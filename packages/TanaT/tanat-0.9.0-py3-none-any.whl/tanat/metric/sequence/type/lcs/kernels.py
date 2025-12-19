#!/usr/bin/env python3
"""
Longest Common Subsequence kernels for sequence metric computation.
"""

import numpy as np
from numba import jit, prange


# =============================================================================
# SINGLE PAIR KERNELS
# =============================================================================


@jit(nopython=True)
def compute_lcs_single_pair(  # pylint: disable=R0913, R0917
    arr_a, arr_b, len_a, len_b, dist_kernel, context, equality_threshold
):
    """
    Compute Longest Common Subsequence length for a single pair of sequences.

    Uses dynamic programming with space optimization (two rows instead of full matrix).

    Args:
        arr_a: Encoded sequence A (1D int32 array).
        arr_b: Encoded sequence B (1D int32 array).
        len_a: Length of sequence A.
        len_b: Length of sequence B.
        dist_kernel: JIT function (val_a, val_b, context) -> float.
        context: Tuple of context arguments for the kernel.
        equality_threshold: Maximum distance to consider entities as equal.

    Returns:
        float: The LCS length.
    """
    if len_a == 0 or len_b == 0:
        return 0.0

    # Space-optimized DP: only keep two rows
    previous = np.zeros(len_b + 1, dtype=np.float32)
    current = np.zeros(len_b + 1, dtype=np.float32)

    for i in range(len_a):
        for j in range(len_b):
            dist = dist_kernel(arr_a[i], arr_b[j], context)
            # Entities are considered equal if distance <= threshold
            if dist <= equality_threshold:
                current[j + 1] = previous[j] + 1.0
            else:
                current[j + 1] = max(current[j], previous[j + 1])

        # Swap rows
        for k in range(len_b + 1):
            previous[k] = current[k]
            current[k] = 0.0

    return previous[len_b]


@jit(nopython=True)
def compute_lcs_single_pair_as_distance(  # pylint: disable=R0913, R0917
    arr_a, arr_b, len_a, len_b, dist_kernel, context, equality_threshold
):
    """
    Compute LCS-based distance for a single pair of sequences.

    Non-normalized additive distance: d(x,y) = len_a + len_b - 2 * LCS

    Args:
        arr_a: Encoded sequence A (1D int32 array).
        arr_b: Encoded sequence B (1D int32 array).
        len_a: Length of sequence A.
        len_b: Length of sequence B.
        dist_kernel: JIT function (val_a, val_b, context) -> float.
        context: Tuple of context arguments for the kernel.
        equality_threshold: Maximum distance to consider entities as equal.

    Returns:
        float: The LCS-based distance.
    """
    lcs = compute_lcs_single_pair(
        arr_a, arr_b, len_a, len_b, dist_kernel, context, equality_threshold
    )
    return float(len_a + len_b) - 2.0 * lcs


@jit(nopython=True)
def compute_lcs_single_pair_normalized(  # pylint: disable=R0913, R0917
    arr_a, arr_b, len_a, len_b, dist_kernel, context, equality_threshold
):
    """
    Compute normalized LCS-based distance for a single pair of sequences.

    Normalized harmonic distance: d(x,y) = 1 - LCS / sqrt(len_a * len_b)

    Args:
        arr_a: Encoded sequence A (1D int32 array).
        arr_b: Encoded sequence B (1D int32 array).
        len_a: Length of sequence A.
        len_b: Length of sequence B.
        dist_kernel: JIT function (val_a, val_b, context) -> float.
        context: Tuple of context arguments for the kernel.
        equality_threshold: Maximum distance to consider entities as equal.

    Returns:
        float: The normalized LCS-based distance.
    """
    lcs = compute_lcs_single_pair(
        arr_a, arr_b, len_a, len_b, dist_kernel, context, equality_threshold
    )

    if len_a == 0 or len_b == 0:
        return 1.0  # Maximum distance for empty sequences

    return 1.0 - lcs / np.sqrt(float(len_a) * float(len_b))


# =============================================================================
# MATRIX CHUNK KERNELS
# =============================================================================


@jit(nopython=True, parallel=True)
def compute_lcs_matrix_chunk(  # pylint: disable=R0913, R0917
    res, start, end, arrays, lengths, dist_kernel, context, equality_threshold
):
    """
    Compute LCS length matrix chunk.

    Computes upper triangle of LCS matrix for rows [start, end).

    Args:
        res: (N, N) float32 array (pre-allocated result).
        start: Start index for the outer loop.
        end: End index for the outer loop.
        arrays: (N, MaxLen) integer array (encoded entities).
        lengths: (N,) integer array (actual lengths).
        dist_kernel: JIT function (val_a, val_b, context) -> float.
        context: Tuple of context arguments for the kernel.
        equality_threshold: Maximum distance to consider entities as equal.
    """
    n = len(arrays)

    for i in prange(start, end):  # pylint: disable=not-an-iterable
        for j in range(i, n):
            len_i = lengths[i]
            len_j = lengths[j]

            lcs = compute_lcs_single_pair(
                arrays[i],
                arrays[j],
                len_i,
                len_j,
                dist_kernel,
                context,
                equality_threshold,
            )

            res[i, j] = lcs
            res[j, i] = lcs


@jit(nopython=True, parallel=True)
def compute_lcs_matrix_chunk_as_distance(  # pylint: disable=R0913, R0917
    res, start, end, arrays, lengths, dist_kernel, context, equality_threshold
):
    """
    Compute LCS-based distance matrix chunk.

    Non-normalized additive distance: d(x,y) = len_a + len_b - 2 * LCS

    Args:
        res: (N, N) float32 array (pre-allocated result).
        start: Start index for the outer loop.
        end: End index for the outer loop.
        arrays: (N, MaxLen) integer array (encoded entities).
        lengths: (N,) integer array (actual lengths).
        dist_kernel: JIT function (val_a, val_b, context) -> float.
        context: Tuple of context arguments for the kernel.
        equality_threshold: Maximum distance to consider entities as equal.
    """
    n = len(arrays)

    for i in prange(start, end):  # pylint: disable=not-an-iterable
        for j in range(i, n):
            len_i = lengths[i]
            len_j = lengths[j]

            dist = compute_lcs_single_pair_as_distance(
                arrays[i],
                arrays[j],
                len_i,
                len_j,
                dist_kernel,
                context,
                equality_threshold,
            )

            res[i, j] = dist
            res[j, i] = dist


@jit(nopython=True, parallel=True)
def compute_lcs_matrix_chunk_normalized(  # pylint: disable=R0913, R0917
    res, start, end, arrays, lengths, dist_kernel, context, equality_threshold
):
    """
    Compute normalized LCS-based distance matrix chunk.

    Normalized harmonic distance: d(x,y) = 1 - LCS / sqrt(len_a * len_b)

    Args:
        res: (N, N) float32 array (pre-allocated result).
        start: Start index for the outer loop.
        end: End index for the outer loop.
        arrays: (N, MaxLen) integer array (encoded entities).
        lengths: (N,) integer array (actual lengths).
        dist_kernel: JIT function (val_a, val_b, context) -> float.
        context: Tuple of context arguments for the kernel.
        equality_threshold: Maximum distance to consider entities as equal.
    """
    n = len(arrays)

    for i in prange(start, end):  # pylint: disable=not-an-iterable
        for j in range(i, n):
            len_i = lengths[i]
            len_j = lengths[j]

            dist = compute_lcs_single_pair_normalized(
                arrays[i],
                arrays[j],
                len_i,
                len_j,
                dist_kernel,
                context,
                equality_threshold,
            )

            res[i, j] = dist
            res[j, i] = dist
