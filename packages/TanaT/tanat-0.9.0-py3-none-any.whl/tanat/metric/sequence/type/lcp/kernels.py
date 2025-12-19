#!/usr/bin/env python3
"""
Longest Common Prefix kernels for sequence metric computation.
"""

import numpy as np
from numba import jit, prange


# =============================================================================
# SINGLE PAIR KERNELS
# =============================================================================


@jit(nopython=True)
def compute_lcp_single_pair(  # pylint: disable=R0913, R0917
    arr_a, arr_b, len_a, len_b, dist_kernel, context, equality_threshold
):
    """
    Compute Longest Common Prefix length for a single pair of sequences.

    The LCP is the length of the longest contiguous sequence of matching
    entities starting from the beginning of both sequences.

    Args:
        arr_a: Encoded sequence A (1D int32 array).
        arr_b: Encoded sequence B (1D int32 array).
        len_a: Length of sequence A.
        len_b: Length of sequence B.
        dist_kernel: JIT function (val_a, val_b, context) -> float.
        context: Tuple of context arguments for the kernel.
        equality_threshold: Maximum distance to consider entities as equal.

    Returns:
        float: The LCP length (as float for consistency with other metrics).
    """
    min_len = min(len_a, len_b)

    for idx in range(min_len):
        dist = dist_kernel(arr_a[idx], arr_b[idx], context)
        # Entities are considered different if distance > threshold
        if dist > equality_threshold:
            return float(idx)

    return float(min_len)


@jit(nopython=True)
def compute_lcp_single_pair_as_distance(  # pylint: disable=R0913, R0917
    arr_a, arr_b, len_a, len_b, dist_kernel, context, equality_threshold
):
    """
    Compute LCP-based distance for a single pair of sequences.

    Non-normalized additive distance: d(x,y) = len_a + len_b - 2 * LCP

    Args:
        arr_a: Encoded sequence A (1D int32 array).
        arr_b: Encoded sequence B (1D int32 array).
        len_a: Length of sequence A.
        len_b: Length of sequence B.
        dist_kernel: JIT function (val_a, val_b, context) -> float.
        context: Tuple of context arguments for the kernel.
        equality_threshold: Maximum distance to consider entities as equal.

    Returns:
        float: The LCP-based distance.
    """
    lcp = compute_lcp_single_pair(
        arr_a, arr_b, len_a, len_b, dist_kernel, context, equality_threshold
    )
    return float(len_a + len_b) - 2.0 * lcp


@jit(nopython=True)
def compute_lcp_single_pair_normalized(  # pylint: disable=R0913, R0917
    arr_a, arr_b, len_a, len_b, dist_kernel, context, equality_threshold
):
    """
    Compute normalized LCP-based distance for a single pair of sequences.

    Normalized harmonic distance: d(x,y) = 1 - LCP / sqrt(len_a * len_b)

    Args:
        arr_a: Encoded sequence A (1D int32 array).
        arr_b: Encoded sequence B (1D int32 array).
        len_a: Length of sequence A.
        len_b: Length of sequence B.
        dist_kernel: JIT function (val_a, val_b, context) -> float.
        context: Tuple of context arguments for the kernel.
        equality_threshold: Maximum distance to consider entities as equal.

    Returns:
        float: The normalized LCP-based distance.
    """
    lcp = compute_lcp_single_pair(
        arr_a, arr_b, len_a, len_b, dist_kernel, context, equality_threshold
    )

    if len_a == 0 or len_b == 0:
        return 1.0  # Maximum distance for empty sequences

    return 1.0 - lcp / np.sqrt(float(len_a) * float(len_b))


# =============================================================================
# MATRIX CHUNK KERNELS
# =============================================================================


@jit(nopython=True, parallel=True)
def compute_lcp_matrix_chunk(  # pylint: disable=R0913, R0917
    res, start, end, arrays, lengths, dist_kernel, context, equality_threshold
):
    """
    Compute LCP length matrix chunk.

    Computes upper triangle of LCP matrix for rows [start, end).

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

            lcp = compute_lcp_single_pair(
                arrays[i],
                arrays[j],
                len_i,
                len_j,
                dist_kernel,
                context,
                equality_threshold,
            )

            res[i, j] = lcp
            res[j, i] = lcp


@jit(nopython=True, parallel=True)
def compute_lcp_matrix_chunk_as_distance(  # pylint: disable=R0913, R0917
    res, start, end, arrays, lengths, dist_kernel, context, equality_threshold
):
    """
    Compute LCP-based distance matrix chunk.

    Non-normalized additive distance: d(x,y) = len_a + len_b - 2 * LCP

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

            dist = compute_lcp_single_pair_as_distance(
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
def compute_lcp_matrix_chunk_normalized(  # pylint: disable=R0913, R0917
    res, start, end, arrays, lengths, dist_kernel, context, equality_threshold
):
    """
    Compute normalized LCP-based distance matrix chunk.

    Normalized harmonic distance: d(x,y) = 1 - LCP / sqrt(len_a * len_b)

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

            dist = compute_lcp_single_pair_normalized(
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
