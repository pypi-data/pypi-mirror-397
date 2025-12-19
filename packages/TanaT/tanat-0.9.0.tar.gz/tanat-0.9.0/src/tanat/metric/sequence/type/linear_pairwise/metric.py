#!/usr/bin/env python3
"""
LinearPairwise sequence metric.
"""

from typing import Union, Optional
import logging

from pydantic.dataclasses import dataclass
from pypassist.dataclass.decorators import viewer

from .kernels import (
    compute_matrix_chunk,
    compute_matrix_chunk_with_padding,
    compute_single_pair,
    compute_single_pair_with_padding,
)
from ...base.metric import SequenceMetric
from ...base.settings import BaseSequenceMetricSettings
from .....sequence.base.array import SequenceArray
from .....function.aggregation.base.function import AggregationFunction

LOGGER = logging.getLogger(__name__)


@viewer
@dataclass
class LinearPairwiseSequenceMetricSettings(BaseSequenceMetricSettings):
    """
    Configuration settings for computing pairwise sequence metrics between sequences.

    Attributes:
        entity_metric: Metric used for entity-level distance computation.
            String identifier of a EntityMetric in the EntityMetric registry
            (e.g. "hamming") or an instance of EntityMetric. Defaults to "hamming".

        agg_fun (Union[str, AggregationFunction]):
            Aggregation function or string identifier for aggregation.
            Defaults to "mean".

        padding_penalty (Optional[float]):
            Penalty applied per position when sequences have different lengths.
            If None, only common positions are compared (shorter sequence defines length).
            If set (e.g., 1.0), missing positions are penalized with this value.
            Defaults to None.

        distance_matrix (Optional[MatrixStorageOptions]):
            Options for distance matrix storage and handling.
            Contains options for on-disk storage, data type, and resuming from existing matrices.

    Note: Inherits `entity_metric` and `distance_matrix` from BaseSequenceMetricSettings.
    """

    agg_fun: Union[str, AggregationFunction] = "mean"
    padding_penalty: Optional[float] = None

    def __snapshot_agg_fun__(self):
        """
        Custom snapshot for the `agg_fun` field.

        Handles AggregationFunction objects by extracting their register name.
        Note: AggregationFunction have no settings.

        Used to detect changes and trigger cache invalidation.
        """
        agg_fun = self.agg_fun
        if isinstance(agg_fun, AggregationFunction):
            return agg_fun.get_registration_name()

        # should be a string identifier to resolve
        return agg_fun


class LinearPairwiseSequenceMetric(SequenceMetric, register_name="linearpairwise"):
    """
    Linear pairwise sequence metric.
    """

    SETTINGS_DATACLASS = LinearPairwiseSequenceMetricSettings

    def __init__(self, settings=None, *, workenv=None):
        if settings is None:
            settings = LinearPairwiseSequenceMetricSettings()
        super().__init__(settings, workenv=workenv)

    @property
    def _agg_fun(self):
        """
        Retrieves the aggregation function.
        """
        agg_fun = self._settings.agg_fun
        return self._resolve_agg_fun(agg_fun)

    @property
    def _use_padding(self):
        """Check if padding penalty is enabled."""
        return self._settings.padding_penalty is not None

    def _compute_single_distance(self, seq_a, seq_b):
        """
        Compute distance between two sequences using linear pairwise alignment.

        Args:
            seq_a (Sequence): First sequence.
            seq_b (Sequence): Second sequence.

        Returns:
            float: The aggregated metric value for the sequence pair.
        """
        entity_features = self._entity_features

        # Extract arrays using SequenceArray
        sa_a = seq_a.get_sequence_array(entity_features)
        sa_b = seq_b.get_sequence_array(entity_features)

        # Combine for encoding (to ensure shared vocabulary if needed)
        combined_sa = SequenceArray.concatenate([sa_a, sa_b])

        # Prepare Context
        (
            encoded_arrays,
            context,
            dist_kernel,
            aggregator,
        ) = self._prepare_execution_context(combined_sa)

        # Compute with appropriate kernel
        return self._compute_pair(
            encoded_arrays[0],
            encoded_arrays[1],
            sa_a.lengths[0],
            sa_b.lengths[0],
            dist_kernel,
            context,
            aggregator,
        )

    def _compute_pair(  # pylint: disable=R0913, R0917
        self, arr_a, arr_b, len_a, len_b, dist_kernel, context, aggregator
    ):
        """Dispatch to appropriate kernel based on padding mode."""
        if self._use_padding:
            return compute_single_pair_with_padding(
                arr_a,
                arr_b,
                len_a,
                len_b,
                dist_kernel,
                context,
                aggregator,
                self._settings.padding_penalty,
            )
        return compute_single_pair(
            arr_a,
            arr_b,
            len_a,
            len_b,
            dist_kernel,
            context,
            aggregator,
        )

    def _compute_distances(self, dm, sequence_pool):
        """
        Compute pairwise distances using Numba-optimized linear alignment.

        Overrides the default naive loop implementation in SequenceMetric
        with a parallelized, JIT-compiled version for high performance.

        Args:
            dm: DistanceMatrix to fill.
            sequence_pool: Pool of sequences to compare.
        """
        # Extract and prepare data (returns NumbaList from entity metric)
        sa = sequence_pool.get_sequence_array(self._entity_features)
        numba_arrays, context, dist_kernel, aggregator = (
            self._prepare_execution_context(sa)
        )

        # Compute chunks with resume support
        self._compute_matrix_chunks(
            dm,
            numba_arrays,
            sa.lengths,
            dist_kernel,
            context,
            aggregator,
            sequence_pool,
        )

    def _compute_matrix_chunks(  # pylint: disable=R0913, R0914, R0917
        self,
        dm,
        numba_arrays,
        lengths,
        dist_kernel,
        context,
        aggregator,
        sequence_pool,
    ):
        """
        Compute matrix chunks with resume support.

        Args:
            dm: DistanceMatrix to fill.
            numba_arrays: NumbaList of encoded sequence arrays.
            lengths: Array of sequence lengths.
            dist_kernel: Numba distance kernel function.
            context: Context for the distance kernel.
            aggregator: Numba aggregation function.
            sequence_pool: Original pool (for progress bar).
        """
        n_sequences = len(numba_arrays)
        batch_size = 500
        diagonal = dm.get_diagonal_snapshot()

        # Select kernel based on padding mode
        use_padding = self._use_padding
        padding_penalty = self._settings.padding_penalty

        with self._progress_bar(sequence_pool) as pbar:
            for start in range(0, n_sequences, batch_size):
                end = min(start + batch_size, n_sequences)
                pairs_count = self._count_chunk_pairs(start, end, n_sequences)

                # Skip if already computed (resume mode)
                if dm.is_chunk_computed(diagonal, start):
                    pbar.update(pairs_count)
                    continue

                # Compute chunk
                self._compute_chunk(
                    dm.data,
                    start,
                    end,
                    numba_arrays,
                    lengths,
                    dist_kernel,
                    context,
                    aggregator,
                    use_padding,
                    padding_penalty,
                )

                dm.flush()
                dm.mark_chunk_done(diagonal, start, end)
                pbar.update(pairs_count)

    def _compute_chunk(  # pylint: disable=R0913, R0914, R0917
        self,
        data,
        start,
        end,
        numba_arrays,
        lengths,
        dist_kernel,
        context,
        aggregator,
        use_padding,
        padding_penalty,
    ):
        """Dispatch to appropriate kernel based on padding mode."""
        if use_padding:
            compute_matrix_chunk_with_padding(
                data,
                start,
                end,
                numba_arrays,
                lengths,
                dist_kernel,
                context,
                aggregator,
                padding_penalty,
            )
        else:
            compute_matrix_chunk(
                data,
                start,
                end,
                numba_arrays,
                lengths,
                dist_kernel,
                context,
                aggregator,
            )

    def _prepare_execution_context(self, sequence_array):
        """
        Prepare data and kernels for Numba execution.

        Args:
            sequence_array: SequenceArray containing the sequences.

        Returns:
            Tuple of (encoded_arrays, context, dist_kernel, aggregator).
        """
        encoded_arrays, context = self.entity_metric.prepare_computation_data(
            sequence_array
        )
        dist_kernel = self.entity_metric.distance_kernel
        aggregator = self._agg_fun.scalar_kernel
        return encoded_arrays, context, dist_kernel, aggregator
