#!/usr/bin/env python3
"""
Numba-compiled sum aggregation kernels.
"""

from numba import jit, prange


# =============================================================================
# Scalar aggregation kernel
# =============================================================================


@jit(nopython=True)
def scalar_sum_kernel(distances):
    """
    Sum aggregation for Numba. Takes a distance vector.

    Args:
        distances: 1D array of distances.

    Returns:
        float: Sum of the distances.
    """
    total = 0.0
    for i in range(len(distances)):  # pylint: disable=consider-using-enumerate
        total += distances[i]
    return total


# =============================================================================
# Matrix aggregation kernel
# =============================================================================


@jit(nopython=True, parallel=True)
def matrix_sum_kernel(
    output_data,
    matrices,
    weights,
    start,
    end,
    n_sequences,
):
    """
    Aggregate a chunk of distance matrices using weighted sum.
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

    # Parallelize over rows in chunk
    for i in prange(start, end):  # pylint: disable=not-an-iterable
        for j in range(i, n_sequences):
            total = 0.0
            for k in range(n_matrices):
                total += weights[k] * matrices[k][i, j]
            output_data[i, j] = total
            output_data[j, i] = total
