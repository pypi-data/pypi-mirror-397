#!/usr/bin/env python3
"""
Numba-compiled mean aggregation kernels.
"""

import numpy as np
from numba import jit, prange


# =============================================================================
# Scalar aggregation kernel
# =============================================================================


@jit(nopython=True)
def scalar_mean_kernel(distances):
    """
    Mean aggregation for Numba. Takes a distance vector.

    Args:
        distances: 1D array of distances.

    Returns:
        float: Mean of the distances.
    """
    n = len(distances)
    if n == 0:
        return 0.0
    total = 0.0
    for i in range(n):
        total += distances[i]
    return total / n


# =============================================================================
# Matrix aggregation kernel
# =============================================================================


@jit(nopython=True, parallel=True)
def matrix_mean_kernel(
    output_data,
    matrices,
    weights,
    start,
    end,
    n_sequences,
):
    """
    Aggregate a chunk of distance matrices using weighted mean.
    Writes directly to output_data for memmap support.

    Args:
        output_data: Output matrix to write to (n x n).
        matrices: List of 2D distance matrices (n x n each).
        weights: Array of weights for each matrix.
        start: Start row index.
        end: End row index.
        n_sequences: Total number of sequences.
    """
    n_matrices = len(matrices)
    total_weight = np.sum(weights)

    if total_weight == 0.0:
        return

    # Parallelize over rows in chunk
    for i in prange(start, end):  # pylint: disable=not-an-iterable
        for j in range(i, n_sequences):
            total = 0.0
            for k in range(n_matrices):
                total += weights[k] * matrices[k][i, j]
            value = total / total_weight
            output_data[i, j] = value
            output_data[j, i] = value
