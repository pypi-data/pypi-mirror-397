#!/usr/bin/env python3
"""
Edit distance kernels for sequence metric computation.
"""

import numpy as np
from numba import jit, prange


# =============================================================================
# SINGLE PAIR KERNELS
# =============================================================================


@jit(nopython=True)
def compute_edit_single_pair(  # pylint: disable=R0913, R0917
    arr_a, arr_b, len_a, len_b, dist_kernel, context, indel_cost
):
    """
    Compute Edit distance for a single pair of sequences.

    Uses the Needleman-Wunsch algorithm with entity-level distances.

    Args:
        arr_a: Encoded sequence A (1D int32 array).
        arr_b: Encoded sequence B (1D int32 array).
        len_a: Length of sequence A.
        len_b: Length of sequence B.
        dist_kernel: JIT function (val_a, val_b, context) -> float.
        context: Tuple of context arguments for the kernel.
        indel_cost: Cost for insertion/deletion operations.

    Returns:
        float: The Edit distance between the two sequences.
    """
    n, m = len_a, len_b

    # Handle empty sequences
    if n == 0:
        return indel_cost * m
    if m == 0:
        return indel_cost * n

    # Initialize distance matrix (n+1 x m+1)
    matrix = np.empty((n + 1, m + 1), dtype=np.float32)

    # Initialize first row and column
    for i in range(n + 1):
        matrix[i, 0] = i * indel_cost
    for j in range(m + 1):
        matrix[0, j] = j * indel_cost

    # Fill the matrix using dynamic programming
    for i in range(1, n + 1):
        for j in range(1, m + 1):
            # Substitution cost using entity metric
            sub_cost = dist_kernel(arr_a[i - 1], arr_b[j - 1], context)

            matrix[i, j] = min(
                matrix[i - 1, j - 1] + sub_cost,  # substitution
                matrix[i - 1, j] + indel_cost,  # deletion
                matrix[i, j - 1] + indel_cost,  # insertion
            )

    return matrix[n, m]


@jit(nopython=True)
def compute_edit_single_pair_normalized(  # pylint: disable=R0913, R0917
    arr_a, arr_b, len_a, len_b, dist_kernel, context, indel_cost
):
    """
    Compute normalized Edit distance for a single pair of sequences.

    Normalization: distance / max(len_a, len_b)

    Args:
        arr_a: Encoded sequence A (1D int32 array).
        arr_b: Encoded sequence B (1D int32 array).
        len_a: Length of sequence A.
        len_b: Length of sequence B.
        dist_kernel: JIT function (val_a, val_b, context) -> float.
        context: Tuple of context arguments for the kernel.
        indel_cost: Cost for insertion/deletion operations.

    Returns:
        float: The normalized Edit distance.
    """
    raw_dist = compute_edit_single_pair(
        arr_a, arr_b, len_a, len_b, dist_kernel, context, indel_cost
    )

    max_len = max(len_a, len_b)
    if max_len == 0:
        return 0.0

    return raw_dist / max_len


# =============================================================================
# MATRIX CHUNK KERNELS
# =============================================================================


@jit(nopython=True, parallel=True)
def compute_edit_matrix_chunk(  # pylint: disable=R0913, R0917
    res, start, end, arrays, lengths, dist_kernel, context, indel_cost
):
    """
    Compute Edit distance matrix chunk.

    Computes upper triangle of distance matrix for rows [start, end).

    Args:
        res: (N, N) float32 array (pre-allocated result).
        start: Start index for the outer loop.
        end: End index for the outer loop.
        arrays: (N, MaxLen) integer array (encoded entities).
        lengths: (N,) integer array (actual lengths).
        dist_kernel: JIT function (val_a, val_b, context) -> float.
        context: Tuple of context arguments for the kernel.
        indel_cost: Cost for insertion/deletion operations.
    """
    n = len(arrays)

    for i in prange(start, end):  # pylint: disable=not-an-iterable
        for j in range(i, n):
            len_i = lengths[i]
            len_j = lengths[j]

            dist = compute_edit_single_pair(
                arrays[i], arrays[j], len_i, len_j, dist_kernel, context, indel_cost
            )

            res[i, j] = dist
            res[j, i] = dist


@jit(nopython=True, parallel=True)
def compute_edit_matrix_chunk_normalized(  # pylint: disable=R0913, R0917
    res, start, end, arrays, lengths, dist_kernel, context, indel_cost
):
    """
    Compute normalized Edit distance matrix chunk.

    Args:
        res: (N, N) float32 array (pre-allocated result).
        start: Start index for the outer loop.
        end: End index for the outer loop.
        arrays: (N, MaxLen) integer array (encoded entities).
        lengths: (N,) integer array (actual lengths).
        dist_kernel: JIT function (val_a, val_b, context) -> float.
        context: Tuple of context arguments for the kernel.
        indel_cost: Cost for insertion/deletion operations.
    """
    n = len(arrays)

    for i in prange(start, end):  # pylint: disable=not-an-iterable
        for j in range(i, n):
            len_i = lengths[i]
            len_j = lengths[j]

            dist = compute_edit_single_pair_normalized(
                arrays[i], arrays[j], len_i, len_j, dist_kernel, context, indel_cost
            )

            res[i, j] = dist
            res[j, i] = dist
