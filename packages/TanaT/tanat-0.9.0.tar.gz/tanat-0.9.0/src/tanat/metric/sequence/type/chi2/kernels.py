#!/usr/bin/env python3
"""
Chi2 distance kernels for sequence metric computation.
"""

import numpy as np
from numba import jit, prange


# =============================================================================
# HISTOGRAM COMPUTATION
# =============================================================================


@jit(nopython=True)
def _compute_histogram(encoded_arr, length, durations, n_categories):
    """
    Compute histogram (sum of durations per category).

    Args:
        encoded_arr: Encoded sequence (1D int32 array).
        length: Length of the sequence.
        durations: Duration for each element (1D float64 array).
        n_categories: Total number of categories in vocabulary.

    Returns:
        np.ndarray: Histogram of shape (n_categories,) with duration sums.
    """
    hist = np.zeros(n_categories, dtype=np.float64)
    for i in range(length):
        cat = encoded_arr[i]
        hist[cat] += durations[i]
    return hist


# =============================================================================
# CHI2 DISTANCE COMPUTATION
# =============================================================================


@jit(nopython=True)
def _chi2_from_histograms(hist_a, hist_b):
    """
    Compute Chi2 distance from two histograms.

    Formula: sqrt(sum((h_a[i] - h_b[i])^2 / (h_a[i] + h_b[i])))

    Args:
        hist_a: Histogram for sequence A.
        hist_b: Histogram for sequence B.

    Returns:
        float: Chi2 distance.
    """
    chi2 = 0.0
    n = len(hist_a)
    for i in range(n):
        total = hist_a[i] + hist_b[i]
        if total > 0:
            diff = hist_a[i] - hist_b[i]
            chi2 += (diff * diff) / total
    return np.sqrt(chi2)


# =============================================================================
# SINGLE PAIR KERNELS
# =============================================================================


@jit(nopython=True)
def compute_chi2_single_pair(
    arr_a,
    arr_b,
    len_a,
    len_b,
    durations_a,
    durations_b,
    n_categories,
):
    """
    Compute Chi2 distance for a single pair of sequences.

    Args:
        arr_a: Encoded sequence A (1D int32 array).
        arr_b: Encoded sequence B (1D int32 array).
        len_a: Length of sequence A.
        len_b: Length of sequence B.
        durations_a: Durations for sequence A (1D float64 array).
        durations_b: Durations for sequence B (1D float64 array).
        n_categories: Total number of categories in vocabulary.

    Returns:
        float: The Chi2 distance between the two sequences.
    """
    # Handle empty sequences
    if len_a == 0 or len_b == 0:
        return np.inf

    # Compute histograms
    hist_a = _compute_histogram(arr_a, len_a, durations_a, n_categories)
    hist_b = _compute_histogram(arr_b, len_b, durations_b, n_categories)

    # Compute Chi2 distance
    return _chi2_from_histograms(hist_a, hist_b)


# =============================================================================
# MATRIX CHUNK KERNELS
# =============================================================================


@jit(nopython=True, parallel=True)
def compute_chi2_matrix_chunk(
    result_matrix,
    start,
    end,
    encoded_arrays,
    lengths,
    durations_list,
    n_categories,
):
    """
    Compute Chi2 distances for a chunk of the distance matrix.

    Parallelized over rows using prange.

    Args:
        result_matrix: Output distance matrix (modified in-place).
        start: Start row index for this chunk.
        end: End row index for this chunk.
        encoded_arrays: List of encoded sequence arrays.
        lengths: Array of sequence lengths.
        durations_list: List of duration arrays.
        n_categories: Total number of categories in vocabulary.
    """
    n_sequences = len(encoded_arrays)

    for i in prange(start, end):  # pylint: disable=not-an-iterable
        arr_a = encoded_arrays[i]
        len_a = lengths[i]
        dur_a = durations_list[i]

        for j in range(i, n_sequences):
            arr_b = encoded_arrays[j]
            len_b = lengths[j]
            dur_b = durations_list[j]

            dist = compute_chi2_single_pair(
                arr_a,
                arr_b,
                len_a,
                len_b,
                dur_a,
                dur_b,
                n_categories,
            )

            # Fill symmetric matrix
            result_matrix[i, j] = dist
            result_matrix[j, i] = dist
