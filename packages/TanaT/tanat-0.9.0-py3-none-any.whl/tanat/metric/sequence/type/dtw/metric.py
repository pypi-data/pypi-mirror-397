#!/usr/bin/env python3
"""
DTW (Dynamic Time Warping) metric.
"""

import logging
from typing import Union, Optional

import numpy as np
from numba.typed import List as NumbaList
from pydantic.dataclasses import dataclass
from pydantic import ConfigDict
from pypassist.dataclass.decorators import viewer

from .kernels import (
    compute_dtw_single_pair,
    compute_dtw_single_pair_normalized,
    compute_dtw_matrix_chunk,
    compute_dtw_matrix_chunk_normalized,
)
from ...base.metric import SequenceMetric
from ...base.settings import BaseSequenceMetricSettings
from .....sequence.base.array import SequenceArray


LOGGER = logging.getLogger(__name__)


@viewer
@dataclass(config=ConfigDict(arbitrary_types_allowed=True))
class DTWSequenceMetricSettings(BaseSequenceMetricSettings):
    """
    Configuration settings for DTW (Dynamic Time Warping) sequence metric computation.

    Attributes:
        entity_metric: Metric used for entity-level distance computation.
            String identifier of a EntityMetric in the EntityMetric registry
            (e.g. "hamming") or an instance of EntityMetric. Defaults to "hamming".

        window: Sakoe-Chiba band width (warping window).
            Restricts the warping path to stay within a band around the diagonal.
            Larger values allow more warping but increase computation time.
            None means no constraint. Optional.

        max_time_diff: Maximum time difference allowed between compared events.
            Events separated by more than this duration are not compared.
            For datetime timestamps: use np.timedelta64 (e.g., np.timedelta64(1, "D")).
            For numeric timestamps: use int or float (e.g., 2 for 2 timesteps).
            None means no constraint. Optional.

        normalize: Whether to normalize the distance by warping path length.
            Normalization: distance / path_length, where path_length is the
            number of aligned pairs in the optimal warping path.
            Defaults to False.

        distance_matrix: Options for distance matrix storage and handling.
            Contains options for on-disk storage, data type, and resuming from existing matrices.

    Note: Inherits `entity_metric` and `distance_matrix` from BaseSequenceMetricSettings.
    """

    window: Optional[int] = None
    max_time_diff: Optional[Union[np.timedelta64, int, float]] = None
    normalize: bool = False


class DTWSequenceMetric(SequenceMetric, register_name="dtw"):
    """
    DTW Distance

    Dynamic Time Warping measures similarity between two temporal sequences,
    allowing for speed variations. This implementation uses the Sakoe-Chiba
    algorithm with time constraints.

    References
    ----------
    H. Sakoe, S. Chiba, Dynamic programming algorithm optimization for spoken word
    recognition, IEEE Trans. on Acoustics, Speech, and Signal Processing, 26 (1978), 43–49.
    """

    SETTINGS_DATACLASS = DTWSequenceMetricSettings

    def __init__(self, settings=None, *, workenv=None):
        if settings is None:
            settings = DTWSequenceMetricSettings()
        super().__init__(settings, workenv=workenv)

    @property
    def _use_normalization(self):
        """Check if normalization is enabled."""
        return self._settings.normalize

    @property
    def _max_time_diff_ns(self):
        """
        Get time constraint parameter in nanoseconds (for datetime)
        or as-is (for numeric timestamps).

        Returns:
            int: Time constraint in nanoseconds, or 0 if no constraint.
        """
        max_time_diff = self._settings.max_time_diff
        if max_time_diff is None:
            return 0

        # If it's a timedelta64, convert to nanoseconds
        if isinstance(max_time_diff, np.timedelta64):
            return max_time_diff.astype("timedelta64[ns]").astype(np.int64)

        # If numeric, return as-is
        return max_time_diff

    @property
    def _window(self):
        """
        Get Sakoe-Chiba band width parameter.

        Returns:
            int: Band width, or -1 if no constraint.
        """
        window = self._settings.window
        return window if window is not None else -1

    def _compute_single_distance(self, seq_a, seq_b):
        """
        Compute DTW distance between two sequences.

        Args:
            seq_a (Sequence): First sequence.
            seq_b (Sequence): Second sequence.

        Returns:
            float: The DTW distance for the sequence pair.
        """
        entity_features = self._entity_features

        # Extract arrays using SequenceArray with timestamps
        sa_a = seq_a.get_sequence_array(entity_features, include_timestamps=True)
        sa_b = seq_b.get_sequence_array(entity_features, include_timestamps=True)

        # Combine for encoding (to ensure shared vocabulary)
        combined_sa = SequenceArray.concatenate([sa_a, sa_b])

        # Prepare execution context
        encoded_arrays, context, dist_kernel = self._prepare_execution_context(
            combined_sa
        )

        # Prepare timestamps for kernel
        ts_a, ts_b = self._prepare_timestamps(combined_sa.timestamps, 2)

        # Compute with appropriate kernel
        return self._compute_pair(
            encoded_arrays[0],
            encoded_arrays[1],
            sa_a.lengths[0],
            sa_b.lengths[0],
            dist_kernel,
            context,
            ts_a,
            ts_b,
        )

    def _compute_pair(  # pylint: disable=R0913, R0917
        self, arr_a, arr_b, len_a, len_b, dist_kernel, context, ts_a, ts_b
    ):
        """Dispatch to appropriate kernel based on normalization mode."""
        max_time_diff = self._max_time_diff_ns
        window = self._window

        if self._use_normalization:
            return compute_dtw_single_pair_normalized(
                arr_a,
                arr_b,
                len_a,
                len_b,
                dist_kernel,
                context,
                ts_a,
                ts_b,
                max_time_diff,
                window,
            )
        return compute_dtw_single_pair(
            arr_a,
            arr_b,
            len_a,
            len_b,
            dist_kernel,
            context,
            ts_a,
            ts_b,
            max_time_diff,
            window,
        )

    def _compute_distances(self, dm, sequence_pool):
        """
        Compute pairwise DTW distances using Numba-optimized kernels.

        Overrides the default naive loop implementation in SequenceMetric
        with a parallelized, JIT-compiled version for high performance.

        Args:
            dm: DistanceMatrix to fill.
            sequence_pool: Pool of sequences to compare.
        """
        # Extract and prepare data with timestamps
        sa = sequence_pool.get_sequence_array(
            self._entity_features, include_timestamps=True
        )
        encoded_arrays, context, dist_kernel = self._prepare_execution_context(sa)

        # Prepare timestamps for kernel
        timestamps = self._prepare_timestamps(sa.timestamps, len(encoded_arrays))

        # Compute chunks with resume support
        self._compute_matrix_chunks(
            dm,
            encoded_arrays,
            sa.lengths,
            dist_kernel,
            context,
            timestamps,
            sequence_pool,
        )

    def _compute_matrix_chunks(  # pylint: disable=R0913, R0914, R0917
        self,
        dm,
        encoded_arrays,
        lengths,
        dist_kernel,
        context,
        timestamps,
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
            timestamps: List of timestamp arrays.
            sequence_pool: Original pool (for progress bar).
        """
        n_sequences = len(encoded_arrays)
        batch_size = 500
        diagonal = dm.get_diagonal_snapshot()

        max_time_diff = self._max_time_diff_ns
        window = self._window
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
                    timestamps,
                    max_time_diff,
                    window,
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
        timestamps,
        max_time_diff,
        window,
        use_normalization,
    ):
        """Dispatch to appropriate kernel based on normalization mode."""
        if use_normalization:
            compute_dtw_matrix_chunk_normalized(
                data,
                start,
                end,
                encoded_arrays,
                lengths,
                dist_kernel,
                context,
                timestamps,
                max_time_diff,
                window,
            )
        else:
            compute_dtw_matrix_chunk(
                data,
                start,
                end,
                encoded_arrays,
                lengths,
                dist_kernel,
                context,
                timestamps,
                max_time_diff,
                window,
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

    def _prepare_timestamps(self, timestamps, n_sequences):
        """
        Prepare timestamps for Numba kernels.

        Converts datetime64 to int64 nanoseconds for Numba compatibility.
        Numeric timestamps are kept as-is.

        Args:
            timestamps: List of timestamp arrays from SequenceArray.
            n_sequences: Expected number of sequences.

        Returns:
            NumbaList of timestamp arrays ready for Numba.
        """
        result = NumbaList()

        if timestamps is None:
            # No timestamps: create dummy arrays (tc_param should be 0)
            for _ in range(n_sequences):
                result.append(np.zeros(1, dtype=np.int32))
            return result

        # Check first timestamp to determine type
        first_ts = timestamps[0]
        if np.issubdtype(first_ts.dtype, np.datetime64):
            # Convert datetime64 to int64 nanoseconds
            for ts in timestamps:
                result.append(ts.astype("datetime64[ns]").astype(np.int64))
        else:
            # Numeric timestamps
            for ts in timestamps:
                result.append(ts.astype(np.float32))

        return result
