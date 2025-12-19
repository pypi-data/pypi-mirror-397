#!/usr/bin/env python3
"""
Edit distance.
"""

import logging

from pydantic.dataclasses import dataclass
from pypassist.dataclass.decorators import viewer

from .kernels import (
    compute_edit_single_pair,
    compute_edit_single_pair_normalized,
    compute_edit_matrix_chunk,
    compute_edit_matrix_chunk_normalized,
)
from ...base.metric import SequenceMetric
from ...base.settings import BaseSequenceMetricSettings
from .....sequence.base.array import SequenceArray


LOGGER = logging.getLogger(__name__)


@viewer
@dataclass
class EditSequenceMetricSettings(BaseSequenceMetricSettings):
    """
    Configuration settings for Edit Distance sequence metric computation.

    Attributes:
        entity_metric: Metric used for entity-level distance computation.
            String identifier of a EntityMetric in the EntityMetric registry
            (e.g. "hamming") or an instance of EntityMetric. Defaults to "hamming".

        indel_cost: Cost for deletion/insertion operations.
            Defaults to 1.0.

        normalize: Whether to normalize the distance by max sequence length.
            Normalization: distance / max(len_a, len_b). Defaults to False.

        distance_matrix: Options for distance matrix storage and handling.
            Contains options for on-disk storage, data type, and resuming from existing matrices.

    Note: Inherits `entity_metric` and `distance_matrix` from BaseSequenceMetricSettings.
    """

    indel_cost: float = 1.0
    normalize: bool = False


class EditSequenceMetric(SequenceMetric, register_name="edit"):
    """
    Edit Distance

    This similarity measure computes the optimal matching between two sequences
    $x$ and $y$. The optimal matching is defined through matching costs, that are provided by the
    entity metric, and the deletion cost.
    It generates edit distances that are the minimal cost, in terms of insertions, deletions, and
    substitutions, for transforming one sequence into another.

    Uses the Needleman-Wunsch algorithm with Numba JIT compilation for performance.

    Note
    ------
    This is a purely sequential metric. The date of the events are not used.

    References
    ------------
    Levenshtein, V. (1966). Binary codes capable of correcting deletions, insertions, and
    reversals. Soviet Physics Doklady 10, 707-710

    Needleman, S. and C. Wunsch (1970). A general method applicable to the search for
    similarities in the amino acid sequence of two proteins. Journal of Molecular Biology 48,
    443-453
    """

    SETTINGS_DATACLASS = EditSequenceMetricSettings

    def __init__(self, settings=None, *, workenv=None):
        if settings is None:
            settings = EditSequenceMetricSettings()
        super().__init__(settings, workenv=workenv)

    @property
    def _use_normalization(self):
        """Check if normalization is enabled."""
        return self._settings.normalize

    def _compute_single_distance(self, seq_a, seq_b):
        """
        Compute Edit distance between two sequences.

        Args:
            seq_a (Sequence): First sequence.
            seq_b (Sequence): Second sequence.

        Returns:
            float: The Edit distance for the sequence pair.
        """
        entity_features = self._entity_features

        # Extract arrays using SequenceArray
        sa_a = seq_a.get_sequence_array(entity_features)
        sa_b = seq_b.get_sequence_array(entity_features)

        # Combine for encoding (to ensure shared vocabulary)
        combined_sa = SequenceArray.concatenate([sa_a, sa_b])

        # Prepare execution context
        encoded_arrays, context, dist_kernel = self._prepare_execution_context(
            combined_sa
        )

        # Compute with appropriate kernel
        return self._compute_pair(
            encoded_arrays[0],
            encoded_arrays[1],
            sa_a.lengths[0],
            sa_b.lengths[0],
            dist_kernel,
            context,
        )

    def _compute_pair(  # pylint: disable=R0913, R0917
        self, arr_a, arr_b, len_a, len_b, dist_kernel, context
    ):
        """Dispatch to appropriate kernel based on normalization mode."""
        indel_cost = self._settings.indel_cost

        if self._use_normalization:
            return compute_edit_single_pair_normalized(
                arr_a, arr_b, len_a, len_b, dist_kernel, context, indel_cost
            )
        return compute_edit_single_pair(
            arr_a, arr_b, len_a, len_b, dist_kernel, context, indel_cost
        )

    def _compute_distances(self, dm, sequence_pool):
        """
        Compute pairwise Edit distances using Numba-optimized kernels.

        Overrides the default naive loop implementation in SequenceMetric
        with a parallelized, JIT-compiled version for high performance.

        Args:
            dm: DistanceMatrix to fill.
            sequence_pool: Pool of sequences to compare.
        """
        # Extract and prepare data
        sa = sequence_pool.get_sequence_array(self._entity_features)
        encoded_arrays, context, dist_kernel = self._prepare_execution_context(sa)

        # Compute chunks with resume support
        self._compute_matrix_chunks(
            dm,
            encoded_arrays,
            sa.lengths,
            dist_kernel,
            context,
            sequence_pool,
        )

    def _compute_matrix_chunks(  # pylint: disable=R0913, R0914, R0917
        self,
        dm,
        encoded_arrays,
        lengths,
        dist_kernel,
        context,
        sequence_pool,
    ):
        """
        Compute matrix chunks with resume support.

        Args:
            dm: DistanceMatrix to fill.
            encoded_arrays: Encoded sequence data.
            lengths: Array of sequence lengths.
            dist_kernel: Numba distance kernel function.
            context: Context for the distance kernel.
            sequence_pool: Original pool (for progress bar).
        """
        n_sequences = len(encoded_arrays)
        batch_size = 500
        diagonal = dm.get_diagonal_snapshot()

        indel_cost = self._settings.indel_cost
        use_normalization = self._use_normalization

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
                    encoded_arrays,
                    lengths,
                    dist_kernel,
                    context,
                    indel_cost,
                    use_normalization,
                )

                dm.flush()
                dm.mark_chunk_done(diagonal, start, end)
                pbar.update(pairs_count)

    def _compute_chunk(  # pylint: disable=R0913, R0914, R0917
        self,
        data,
        start,
        end,
        encoded_arrays,
        lengths,
        dist_kernel,
        context,
        indel_cost,
        use_normalization,
    ):
        """Dispatch to appropriate kernel based on normalization mode."""
        if use_normalization:
            compute_edit_matrix_chunk_normalized(
                data,
                start,
                end,
                encoded_arrays,
                lengths,
                dist_kernel,
                context,
                indel_cost,
            )
        else:
            compute_edit_matrix_chunk(
                data,
                start,
                end,
                encoded_arrays,
                lengths,
                dist_kernel,
                context,
                indel_cost,
            )

    def _prepare_execution_context(self, sequence_array):
        """
        Prepare data and kernels for Numba execution.

        Args:
            sequence_array: SequenceArray containing the sequences.

        Returns:
            Tuple of (encoded_arrays, context, dist_kernel).
        """
        encoded_arrays, context = self.entity_metric.prepare_computation_data(
            sequence_array
        )
        dist_kernel = self.entity_metric.distance_kernel
        return encoded_arrays, context, dist_kernel
