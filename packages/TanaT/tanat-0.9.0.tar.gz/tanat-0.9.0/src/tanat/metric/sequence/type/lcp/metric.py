#!/usr/bin/env python3
"""
Longest Common Prefix.
"""

import logging

import numpy as np
from pydantic import field_validator
from pydantic.dataclasses import dataclass
from pypassist.dataclass.decorators import viewer

from .kernels import (
    compute_lcp_single_pair,
    compute_lcp_single_pair_as_distance,
    compute_lcp_single_pair_normalized,
    compute_lcp_matrix_chunk,
    compute_lcp_matrix_chunk_as_distance,
    compute_lcp_matrix_chunk_normalized,
)
from ...base.metric import SequenceMetric
from ...base.settings import BaseSequenceMetricSettings
from .....sequence.base.array import SequenceArray


LOGGER = logging.getLogger(__name__)


@viewer
@dataclass
class LCPSequenceMetricSettings(BaseSequenceMetricSettings):
    """Settings for LCP (Longest Common Prefix) sequence metric computation.

    Attributes:
        entity_metric: Metric used for entity-level distance computation.
            String identifier of a EntityMetric in the EntityMetric registry
            (e.g. "hamming") or an instance of EntityMetric. Defaults to "hamming".

        equality_threshold: Maximum distance between two entities to consider them equal.
            Entities with distance <= threshold are considered equal.
            Defaults to 0.0 (exact equality).

        as_distance: If True, returns a distance measure instead of raw LCP length.
            Defaults to False (returns LCP length).

        normalize: Normalizes the distance (only when as_distance is True).
            - If False: d(x,y) = len_a + len_b - 2 * LCP
            - If True: d(x,y) = 1 - LCP / sqrt(len_a * len_b)
            Defaults to False.

        distance_matrix: Options for distance matrix storage and handling.
            Contains options for on-disk storage, data type, and resuming from existing matrices.

    Note: Inherits `entity_metric` and `distance_matrix` from BaseSequenceMetricSettings.
    """

    equality_threshold: float = 0.0
    as_distance: bool = False
    normalize: bool = False

    def __post_init__(self):
        """Post-initialization to ensure settings are valid."""
        if self.normalize and not self.as_distance:
            LOGGER.warning(
                "LCPSequenceMetricSettings: 'normalize' is True but 'as_distance' is False. "
                "Normalization will be ignored."
            )

    @field_validator("equality_threshold")
    @classmethod
    def validate_equality_threshold_not_nan(cls, v):
        """Validate that equality_threshold is not NaN."""
        if np.isnan(v):
            raise ValueError("equality_threshold cannot be NaN.")
        return v


class LCPSequenceMetric(SequenceMetric, register_name="lcp"):
    """
    Longest Common Prefix

    This similarity measure computes the length of the longest common prefix
    (LCP) between two sequences $x$ and $y$. A prefix is a contiguous subsequence of entities
    at the beginning of a sequence. They are common between two sequences when all entities are
    similar pairwise. Two entities of the sequences are the same when they have the exact same
    features (whatever their dates).

    The distance derived from the count is obtained in two different manners:

    * normalized harmonic distance: $$d(x,y) = 1 - \\frac{LCP}{\\sqrt{|x| \\times |y|}}$$
    * non-normalized additive distance: $$d(x,y) = |x| + |y| - 2 \\times LCP$$

    Uses Numba JIT compilation for performance.

    Note
    ------
    This is a purely sequential metric. The date of the events are not used.

    Reference
    ------------
    Elzinga, C. H. (2008). Sequence analysis: Metric representations of categorical time
    series. Sociological Methods and Research.
    """

    SETTINGS_DATACLASS = LCPSequenceMetricSettings

    def __init__(self, settings=None, *, workenv=None):
        if settings is None:
            settings = LCPSequenceMetricSettings()
        super().__init__(settings, workenv=workenv)

    @property
    def _output_mode(self):
        """
        Determine output mode based on settings.

        Returns:
            str: 'lcp' for raw LCP length, 'distance' for non-normalized distance,
                 'normalized' for normalized distance.
        """
        if not self._settings.as_distance:
            return "lcp"
        if self._settings.normalize:
            return "normalized"
        return "distance"

    @property
    def _equality_threshold(self):
        """
        Get the equality threshold for entity comparison.

        Returns:
            float: The threshold value.
        """
        return self._settings.equality_threshold

    def _compute_single_distance(self, seq_a, seq_b):
        """
        Compute LCP metric between two sequences.

        Args:
            seq_a (Sequence): First sequence.
            seq_b (Sequence): Second sequence.

        Returns:
            float: The LCP metric value for the sequence pair.
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
        """Dispatch to appropriate kernel based on output mode."""
        mode = self._output_mode
        threshold = self._equality_threshold

        if mode == "normalized":
            return compute_lcp_single_pair_normalized(
                arr_a, arr_b, len_a, len_b, dist_kernel, context, threshold
            )
        if mode == "distance":
            return compute_lcp_single_pair_as_distance(
                arr_a, arr_b, len_a, len_b, dist_kernel, context, threshold
            )
        # Default: raw LCP length
        return compute_lcp_single_pair(
            arr_a, arr_b, len_a, len_b, dist_kernel, context, threshold
        )

    def _compute_distances(self, dm, sequence_pool):
        """
        Compute pairwise LCP metrics using Numba-optimized kernels.

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

        output_mode = self._output_mode
        threshold = self._equality_threshold

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
                    output_mode,
                    threshold,
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
        output_mode,
        threshold,
    ):
        """Dispatch to appropriate kernel based on output mode."""
        if output_mode == "normalized":
            compute_lcp_matrix_chunk_normalized(
                data,
                start,
                end,
                encoded_arrays,
                lengths,
                dist_kernel,
                context,
                threshold,
            )
        elif output_mode == "distance":
            compute_lcp_matrix_chunk_as_distance(
                data,
                start,
                end,
                encoded_arrays,
                lengths,
                dist_kernel,
                context,
                threshold,
            )
        else:
            # Default: raw LCP length
            compute_lcp_matrix_chunk(
                data,
                start,
                end,
                encoded_arrays,
                lengths,
                dist_kernel,
                context,
                threshold,
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
