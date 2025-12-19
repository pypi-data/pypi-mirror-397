#!/usr/bin/env python3
"""
DTW (Dynamic Time Warping) kernels for sequence metric computation.
"""

import numpy as np
from numba import jit, prange


# =============================================================================
# SINGLE PAIR KERNELS
# =============================================================================


@jit(nopython=True)
def compute_dtw_single_pair(  # pylint: disable=R0913, R0914, R0917
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
):
    """
    Compute DTW distance for a single pair of sequences.

    Uses the Sakoe-Chiba algorithm with time constraints.

    Args:
        arr_a: Encoded sequence A (1D int32 array).
        arr_b: Encoded sequence B (1D int32 array).
        len_a: Length of sequence A.
        len_b: Length of sequence B.
        dist_kernel: JIT function (val_a, val_b, context) -> float.
        context: Tuple of context arguments for the kernel.
        ts_a: Timestamps for sequence A (int64 nanoseconds or float64).
        ts_b: Timestamps for sequence B (int64 nanoseconds or float64).
        max_time_diff: Maximum time difference allowed (same type as timestamps, 0 = no constraint).
        window: Sakoe-Chiba band width (-1 = no constraint).

    Returns:
        float: The DTW distance between the two sequences.
    """
    n, m = len_a, len_b

    # Handle empty sequences
    if n == 0 or m == 0:
        return np.inf

    # Compute Sakoe-Chiba band parameters
    if window >= 0:
        sc = min(window, min(n, m) - 1)
        n_sc, m_sc = n - sc, m - sc
    else:
        n_sc, m_sc = n, m

    # Use space-optimized version (2 rows instead of full matrix)
    prev_row = np.full(m + 1, np.inf, dtype=np.float32)
    curr_row = np.full(m + 1, np.inf, dtype=np.float32)
    prev_row[0] = 0.0

    for i in range(1, n + 1):
        curr_row[0] = np.inf

        # Sakoe-Chiba band limits
        j_start = max(1, i - n_sc + 1)
        j_end = min(m, i + m_sc - 1) + 1

        for j in range(j_start, j_end):
            # Check time constraint
            if max_time_diff > 0:
                time_diff = ts_a[i - 1] - ts_b[j - 1]
                if time_diff < 0:
                    time_diff = -time_diff
                if time_diff > max_time_diff:
                    curr_row[j] = np.inf
                    continue

            # Entity distance
            entity_dist = dist_kernel(arr_a[i - 1], arr_b[j - 1], context)

            # DTW recurrence: min of three predecessors + current cost
            curr_row[j] = entity_dist + min(
                prev_row[j],  # insertion
                curr_row[j - 1],  # deletion
                prev_row[j - 1],  # match
            )

        # Swap rows
        prev_row, curr_row = curr_row, prev_row
        curr_row[:] = np.inf

    return prev_row[m]


@jit(nopython=True)
def compute_dtw_single_pair_normalized(  # pylint: disable=R0913, R0914, R0917
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
):
    """
    Compute normalized DTW distance for a single pair of sequences.

    Normalization by warping path length (number of aligned pairs).
    This requires computing the full matrix to backtrack the path.

    Args:
        arr_a: Encoded sequence A (1D int32 array).
        arr_b: Encoded sequence B (1D int32 array).
        len_a: Length of sequence A.
        len_b: Length of sequence B.
        dist_kernel: JIT function (val_a, val_b, context) -> float.
        context: Tuple of context arguments for the kernel.
        ts_a: Timestamps for sequence A.
        ts_b: Timestamps for sequence B.
        max_time_diff: Maximum time difference allowed.
        window: Sakoe-Chiba band width.

    Returns:
        float: The normalized DTW distance (distance / path_length).
    """
    n, m = len_a, len_b

    # Handle empty sequences
    if n == 0 or m == 0:
        return np.inf

    # Compute Sakoe-Chiba band parameters
    if window >= 0:
        sc = min(window, min(n, m) - 1)
        n_sc, m_sc = n - sc, m - sc
    else:
        n_sc, m_sc = n, m

    # Need full matrix for backtracking path length
    dtw = np.full((n + 1, m + 1), np.inf, dtype=np.float32)
    dtw[0, 0] = 0.0

    for i in range(1, n + 1):
        # Sakoe-Chiba band limits
        j_start = max(1, i - n_sc + 1)
        j_end = min(m, i + m_sc - 1) + 1

        for j in range(j_start, j_end):
            # Check time constraint
            if max_time_diff > 0:
                time_diff = ts_a[i - 1] - ts_b[j - 1]
                if time_diff < 0:
                    time_diff = -time_diff
                if time_diff > max_time_diff:
                    continue

            # Entity distance
            entity_dist = dist_kernel(arr_a[i - 1], arr_b[j - 1], context)

            # DTW recurrence
            dtw[i, j] = entity_dist + min(
                dtw[i - 1, j],  # insertion
                dtw[i, j - 1],  # deletion
                dtw[i - 1, j - 1],  # match
            )

    raw_distance = dtw[n, m]

    if raw_distance == np.inf:
        return np.inf

    # Backtrack to compute path length
    path_length = _compute_path_length(dtw, n, m)

    if path_length == 0:
        return 0.0

    return raw_distance / path_length


@jit(nopython=True)
def _compute_path_length(dtw, n, m):
    """
    Compute the length of the optimal warping path by backtracking.

    Args:
        dtw: The DTW cost matrix.
        n: Length of sequence A.
        m: Length of sequence B.

    Returns:
        int: The number of aligned pairs in the optimal path.
    """
    i, j = n, m
    path_length = 0

    while i > 0 and j > 0:
        path_length += 1

        # Find which predecessor was used
        diag = dtw[i - 1, j - 1]
        left = dtw[i, j - 1]
        up = dtw[i - 1, j]

        if diag <= left and diag <= up:
            # Diagonal move (match)
            i -= 1
            j -= 1
        elif left <= up:
            # Left move (insertion in B)
            j -= 1
        else:
            # Up move (insertion in A)
            i -= 1

    # Count remaining moves if one sequence not exhausted
    path_length += i + j

    return path_length


# =============================================================================
# MATRIX CHUNK KERNELS
# =============================================================================


@jit(nopython=True, parallel=True)
def compute_dtw_matrix_chunk(  # pylint: disable=R0913, R0914, R0917
    result_matrix,
    start,
    end,
    encoded_arrays,
    lengths,
    dist_kernel,
    context,
    timestamps,
    max_time_diff,
    window,
):
    """
    Compute DTW distances for a chunk of the distance matrix.

    Parallelized over rows using prange.

    Args:
        result_matrix: Output distance matrix (modified in-place).
        start: Start row index for this chunk.
        end: End row index for this chunk.
        encoded_arrays: List of encoded sequence arrays.
        lengths: Array of sequence lengths.
        dist_kernel: JIT function for entity distance.
        context: Context tuple for the distance kernel.
        timestamps: List of timestamp arrays.
        max_time_diff: Maximum time difference allowed.
        window: Sakoe-Chiba band width.
    """
    n_sequences = len(encoded_arrays)

    for i in prange(start, end):  # pylint: disable=not-an-iterable
        arr_a = encoded_arrays[i]
        len_a = lengths[i]
        ts_a = timestamps[i]

        for j in range(i, n_sequences):
            arr_b = encoded_arrays[j]
            len_b = lengths[j]
            ts_b = timestamps[j]

            dist = compute_dtw_single_pair(
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

            # Fill symmetric matrix
            result_matrix[i, j] = dist
            result_matrix[j, i] = dist


@jit(nopython=True, parallel=True)
def compute_dtw_matrix_chunk_normalized(  # pylint: disable=R0913, R0914, R0917
    result_matrix,
    start,
    end,
    encoded_arrays,
    lengths,
    dist_kernel,
    context,
    timestamps,
    max_time_diff,
    window,
):
    """
    Compute normalized DTW distances for a chunk of the distance matrix.

    Normalization by warping path length (number of aligned pairs).
    Parallelized over rows using prange.

    Args:
        result_matrix: Output distance matrix (modified in-place).
        start: Start row index for this chunk.
        end: End row index for this chunk.
        encoded_arrays: List of encoded sequence arrays.
        lengths: Array of sequence lengths.
        dist_kernel: JIT function for entity distance.
        context: Context tuple for the distance kernel.
        timestamps: List of timestamp arrays.
        max_time_diff: Maximum time difference allowed.
        window: Sakoe-Chiba band width.
    """
    n_sequences = len(encoded_arrays)

    for i in prange(start, end):  # pylint: disable=not-an-iterable
        arr_a = encoded_arrays[i]
        len_a = lengths[i]
        ts_a = timestamps[i]

        for j in range(i, n_sequences):
            arr_b = encoded_arrays[j]
            len_b = lengths[j]
            ts_b = timestamps[j]

            dist = compute_dtw_single_pair_normalized(
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

            # Fill symmetric matrix
            result_matrix[i, j] = dist
            result_matrix[j, i] = dist
