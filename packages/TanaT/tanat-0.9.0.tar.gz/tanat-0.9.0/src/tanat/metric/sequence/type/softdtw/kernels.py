#!/usr/bin/env python3
"""
SoftDTW (Soft Dynamic Time Warping) kernels for sequence metric computation.
"""

import numpy as np
from numba import jit, prange


# =============================================================================
# SOFTMIN HELPER
# =============================================================================


@jit(nopython=True)
def _softmin3(a, b, c, gamma):
    """
    Compute softmin of 3 input variables with parameter gamma.

    Uses the log-sum-exp trick for numerical stability.
    In the limit case gamma → 0, reduces to hard-min operator.

    Args:
        a: First input variable.
        b: Second input variable.
        c: Third input variable.
        gamma: Regularization parameter (must be positive).

    Returns:
        float: Softmin value.
    """
    # Log-sum-exp trick for numerical stability
    neg_gamma = -gamma
    vals = np.array([a / neg_gamma, b / neg_gamma, c / neg_gamma])
    max_val = np.max(vals)
    return neg_gamma * (np.log(np.sum(np.exp(vals - max_val))) + max_val)


# =============================================================================
# SINGLE PAIR KERNELS
# =============================================================================


@jit(nopython=True)
def compute_softdtw_single_pair(  # pylint: disable=R0913, R0914
    arr_a,
    arr_b,
    len_a,
    len_b,
    dist_kernel,
    context,
    gamma,
):
    """
    Compute SoftDTW distance for a single pair of sequences.

    Args:
        arr_a: Encoded sequence A (1D int32 array).
        arr_b: Encoded sequence B (1D int32 array).
        len_a: Length of sequence A.
        len_b: Length of sequence B.
        dist_kernel: JIT function (val_a, val_b, context) -> float.
        context: Tuple of context arguments for the kernel.
        gamma: Regularization parameter for soft-min function.

    Returns:
        float: The SoftDTW distance between the two sequences.
    """
    n, m = len_a, len_b

    # Handle empty sequences
    if n == 0 or m == 0:
        return np.inf

    # Initialize R matrix
    # Use (n+2, m+2) with proper boundary conditions
    # R[0,0] = 0, borders = +inf (except last row/col which are unused)
    inf_val = np.finfo(np.float64).max
    r_matrix = np.zeros((n + 2, m + 2), dtype=np.float64)

    # Set boundary conditions: first row and column to +inf (except [0,0])
    for i in range(n + 1):
        r_matrix[i, 0] = inf_val
    for j in range(m + 1):
        r_matrix[0, j] = inf_val
    r_matrix[0, 0] = 0.0

    # DP recursion
    for i in range(1, n + 1):
        for j in range(1, m + 1):
            # Entity distance
            entity_dist = dist_kernel(arr_a[i - 1], arr_b[j - 1], context)

            # SoftDTW recurrence: softmin of three predecessors + current cost
            r_matrix[i, j] = entity_dist + _softmin3(
                r_matrix[i - 1, j],  # insertion
                r_matrix[i - 1, j - 1],  # match
                r_matrix[i, j - 1],  # deletion
                gamma,
            )

    return r_matrix[n, m]


# =============================================================================
# MATRIX CHUNK KERNELS
# =============================================================================


@jit(nopython=True, parallel=True)
def compute_softdtw_matrix_chunk(  # pylint: disable=R0913, R0914
    result_matrix,
    start,
    end,
    encoded_arrays,
    lengths,
    dist_kernel,
    context,
    gamma,
):
    """
    Compute SoftDTW distances for a chunk of the distance matrix.

    Parallelized over rows using prange.

    Args:
        result_matrix: Output distance matrix (modified in-place).
        start: Start row index for this chunk.
        end: End row index for this chunk.
        encoded_arrays: List of encoded sequence arrays.
        lengths: Array of sequence lengths.
        dist_kernel: JIT function for entity distance.
        context: Context tuple for the distance kernel.
        gamma: Regularization parameter for soft-min function.
    """
    n_sequences = len(encoded_arrays)

    for i in prange(start, end):  # pylint: disable=not-an-iterable
        arr_a = encoded_arrays[i]
        len_a = lengths[i]

        for j in range(i, n_sequences):
            arr_b = encoded_arrays[j]
            len_b = lengths[j]

            dist = compute_softdtw_single_pair(
                arr_a,
                arr_b,
                len_a,
                len_b,
                dist_kernel,
                context,
                gamma,
            )

            # Fill symmetric matrix
            result_matrix[i, j] = dist
            result_matrix[j, i] = dist
