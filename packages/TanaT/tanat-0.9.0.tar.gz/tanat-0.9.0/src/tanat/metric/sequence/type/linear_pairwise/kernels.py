#!/usr/bin/env python3
"""
Linear pairwise kernels for sequence metric computation.
"""

import numpy as np
from numba import jit, prange


# =============================================================================
# MATRIX CHUNK KERNELS
# =============================================================================


@jit(nopython=True, parallel=True, cache=False)
def compute_matrix_chunk(  # pylint: disable=R0913, R0914, R0917
    res, start, end, arrays, lengths, dist_kernel, context, aggregator
):
    """
    Compute distance matrix chunk without padding.

    Only compares common positions (min length between sequences).

    Args:
        res: (N, N) float32 array (pre-allocated result).
        start: Start index for the outer loop.
        end: End index for the outer loop.
        arrays: NumbaList of 1D arrays (encoded entities).
        lengths: (N,) integer array (actual lengths).
        dist_kernel: JIT function (val_a, val_b, context) -> float.
        context: Tuple of context arguments for the kernel.
        aggregator: JIT function (distances) -> float.
    """
    n = len(arrays)

    for i in prange(start, end):  # pylint: disable=not-an-iterable
        for j in range(i, n):
            len_i = lengths[i]
            len_j = lengths[j]
            min_len = min(len_i, len_j)

            # Build distance vector for common positions only
            distances = np.empty(min_len, dtype=np.float32)
            for k in range(min_len):
                distances[k] = dist_kernel(arrays[i][k], arrays[j][k], context)

            final_dist = aggregator(distances)
            res[i, j] = final_dist
            res[j, i] = final_dist


@jit(nopython=True, parallel=True, cache=False)
def compute_matrix_chunk_with_padding(  # pylint: disable=R0913, R0914, R0917
    res, start, end, arrays, lengths, dist_kernel, context, aggregator, padding_penalty
):
    """
    Compute distance matrix chunk with padding penalty.

    Compares all positions up to max length, penalizing missing positions.

    Args:
        res: (N, N) float32 array (pre-allocated result).
        start: Start index for the outer loop.
        end: End index for the outer loop.
        arrays: NumbaList of 1D arrays (encoded entities).
        lengths: (N,) integer array (actual lengths).
        dist_kernel: JIT function (val_a, val_b, context) -> float.
        context: Tuple of context arguments for the kernel.
        aggregator: JIT function (distances) -> float.
        padding_penalty: Penalty value for each missing position.
    """
    n = len(arrays)

    for i in prange(start, end):  # pylint: disable=not-an-iterable
        for j in range(i, n):
            len_i = lengths[i]
            len_j = lengths[j]
            min_len = min(len_i, len_j)
            max_len = max(len_i, len_j)

            # Build distance vector for all positions
            distances = np.empty(max_len, dtype=np.float32)

            # Common positions: compute actual distance
            for k in range(min_len):
                distances[k] = dist_kernel(arrays[i][k], arrays[j][k], context)

            # Missing positions: apply penalty
            for k in range(min_len, max_len):
                distances[k] = padding_penalty

            final_dist = aggregator(distances)
            res[i, j] = final_dist
            res[j, i] = final_dist


# =============================================================================
# SINGLE PAIR KERNELS
# =============================================================================


@jit(nopython=True, cache=False)
def compute_single_pair(  # pylint: disable=R0913, R0917
    arr_a, arr_b, len_a, len_b, dist_kernel, context, aggregator
):
    """
    Compute distance for a single pair of sequences without padding.
    """
    min_len = min(len_a, len_b)

    distances = np.empty(min_len, dtype=np.float32)
    for k in range(min_len):
        distances[k] = dist_kernel(arr_a[k], arr_b[k], context)

    return aggregator(distances)


@jit(nopython=True, cache=False)
def compute_single_pair_with_padding(  # pylint: disable=R0913, R0917
    arr_a, arr_b, len_a, len_b, dist_kernel, context, aggregator, padding_penalty
):
    """
    Compute distance for a single pair of sequences with padding penalty.
    """
    min_len = min(len_a, len_b)
    max_len = max(len_a, len_b)

    distances = np.empty(max_len, dtype=np.float32)

    for k in range(min_len):
        distances[k] = dist_kernel(arr_a[k], arr_b[k], context)

    for k in range(min_len, max_len):
        distances[k] = padding_penalty

    return aggregator(distances)
