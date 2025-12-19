#!/usr/bin/env python3
"""
Numba-optimized kernels for clustering algorithm.

Note: Kernels adapt to the input distance matrix dtype for consistency.
"""

import numpy as np
from numba import jit, prange


# -----------------------------------------------------------------
#           PAM swap and build phase optimizations
# -----------------------------------------------------------------


@jit(nopython=True)
def compute_min_distances(dist_matrix, unselected, selected):
    """
    Compute minimum and second minimum distances from unselected points to medoids.

    Args:
        dist_matrix: Full distance matrix (n x n)
        unselected: Array of unselected indices
        selected: Array of selected (medoid) indices

    Returns:
        min_dist: Minimum distance to any medoid for each unselected point
        second_min_dist: Second minimum distance for each unselected point
        closest_medoid: Index (in selected array) of closest medoid for each point
    """
    n_unselected = len(unselected)
    n_selected = len(selected)

    # Use same dtype as input matrix
    dtype = dist_matrix.dtype
    min_dist = np.empty(n_unselected, dtype=dtype)
    second_min_dist = np.empty(n_unselected, dtype=dtype)
    closest_medoid = np.empty(n_unselected, dtype=np.int32)

    for j in range(n_unselected):
        u_idx = unselected[j]
        best = np.inf
        second_best = np.inf
        best_idx = 0

        for i in range(n_selected):
            s_idx = selected[i]
            d = dist_matrix[u_idx, s_idx]
            if d < best:
                second_best = best
                best = d
                best_idx = i
            elif d < second_best:
                second_best = d

        min_dist[j] = best
        second_min_dist[j] = second_best
        closest_medoid[j] = best_idx

    return min_dist, second_min_dist, closest_medoid


@jit(nopython=True, parallel=True)
def compute_swap_cost(  # pylint: disable=R0913,R0914
    dist_matrix, unselected, selected, min_dist, second_min_dist, closest_medoid
):
    """
    Compute the cost of swapping each (medoid, non-medoid) pair.

    This is the core of PAM's swap phase, optimized with Numba.

    Args:
        dist_matrix: Full distance matrix (n x n)
        unselected: Array of unselected indices
        selected: Array of selected (medoid) indices
        min_dist: Minimum distance to any medoid for each unselected point
        second_min_dist: Second minimum distance for each unselected point
        closest_medoid: Index of closest medoid for each unselected point

    Returns:
        total_cost: Cost matrix (n_selected x n_unselected) for each possible swap
    """
    n_unselected = len(unselected)
    n_selected = len(selected)

    # Use same dtype as input matrix
    dtype = dist_matrix.dtype
    total_cost = np.zeros((n_selected, n_unselected), dtype=dtype)

    # Parallelize over candidate replacements (h)
    for h in prange(n_unselected):  # pylint: disable=not-an-iterable
        h_idx = unselected[h]

        for i in range(n_selected):
            cost = 0.0

            # For each point j, compute contribution to swap cost
            for j in range(n_unselected):
                j_idx = unselected[j]
                d_j_h = dist_matrix[j_idx, h_idx]  # distance from j to candidate h
                cur_min_dist = min_dist[j]  # current min distance
                cur_second_min_dist = second_min_dist[j]  # second min distance

                if closest_medoid[j] == i:
                    # j's closest medoid is i (being removed)
                    # New distance will be min(d_j_h, cur_second_min_dist)
                    new_dist = min(d_j_h, cur_second_min_dist)
                    cost += new_dist - cur_min_dist
                else:
                    # j's closest medoid is not i
                    # Only matters if h is closer than current min
                    if d_j_h < cur_min_dist:
                        cost += d_j_h - cur_min_dist

            total_cost[i, h] = cost

    return total_cost


@jit(nopython=True)
def find_best_swap(total_cost):
    """
    Find the best swap (lowest negative cost).

    Args:
        total_cost: Cost matrix (n_selected x n_unselected)

    Returns:
        best_i: Index of medoid to remove (-1 if no improvement)
        best_h: Index of candidate to add (-1 if no improvement)
        best_cost: The cost of the best swap
    """
    n_selected, n_unselected = total_cost.shape
    best_cost = 0.0
    best_i = -1
    best_h = -1

    for i in range(n_selected):
        for h in range(n_unselected):
            if total_cost[i, h] < best_cost:
                best_cost = total_cost[i, h]
                best_i = i
                best_h = h

    return best_i, best_h, best_cost


@jit(nopython=True, parallel=True)
def compute_build_gain(dist_matrix, unselected, selected):
    """
    Compute the gain for adding each unselected point as a new medoid.
    Used in the BUILD phase of PAM.

    Args:
        dist_matrix: Full distance matrix (n x n)
        unselected: Array of unselected indices
        selected: Array of selected (medoid) indices

    Returns:
        gains: Array of gains for each unselected point
    """
    n_unselected = len(unselected)
    n_selected = len(selected)

    # Use same dtype as input matrix
    dtype = dist_matrix.dtype
    min_dist = np.empty(n_unselected, dtype=dtype)

    # First compute current min distances (sequential, small overhead)
    for j in range(n_unselected):
        u_idx = unselected[j]
        best = np.inf
        for i in range(n_selected):
            s_idx = selected[i]
            d = dist_matrix[u_idx, s_idx]
            if d < best:
                best = d
        min_dist[j] = best

    # Compute gain for each candidate (parallelized)
    gains = np.zeros(n_unselected, dtype=dtype)
    for h in prange(n_unselected):  # pylint: disable=not-an-iterable
        h_idx = unselected[h]
        total_gain = 0.0

        for j in range(n_unselected):
            j_idx = unselected[j]
            d_j_h = dist_matrix[j_idx, h_idx]
            # Gain is reduction in distance (positive = good)
            reduction = min_dist[j] - d_j_h
            if reduction > 0:
                total_gain += reduction

        gains[h] = total_gain

    return gains


def pam_swap_optimized(selected_list, unselected_list, np_dist_matrix):
    """
    Optimized PAM swap phase using Numba kernels.

    Args:
        selected_list: List of selected medoid indices
        unselected_list: List of unselected indices
        np_dist_matrix: Distance matrix as numpy array

    Returns:
        Tuple (i, h) for the best swap, or None if no improvement
    """
    # Convert to sorted numpy arrays for Numba (int32 for indices)
    selected = np.array(sorted(selected_list), dtype=np.int32)
    unselected = np.array(sorted(unselected_list), dtype=np.int32)

    # Compute min distances
    min_dist, second_min_dist, closest_medoid = compute_min_distances(
        np_dist_matrix, unselected, selected
    )

    # Compute swap costs
    total_cost = compute_swap_cost(
        np_dist_matrix, unselected, selected, min_dist, second_min_dist, closest_medoid
    )

    # Find best swap
    best_i, best_h, best_cost = find_best_swap(total_cost)

    if best_i >= 0 and best_cost < 0:  # pylint: disable=chained-comparison
        return (int(selected[best_i]), int(unselected[best_h]))

    return None


def pam_build_optimized(np_dist_matrix, n_clusters):
    """
    Optimized PAM build phase using Numba kernels.

    Args:
        np_dist_matrix: Distance matrix as numpy array
        n_clusters: Number of clusters to form

    Returns:
        selected_list: List of selected medoid indices
        unselected_list: List of unselected indices
    """
    n = len(np_dist_matrix)

    # First medoid: minimize total distance to all others
    total_dist = np.sum(np_dist_matrix, axis=0)
    first_medoid = int(np.argmin(total_dist))

    selected_list = [first_medoid]
    unselected_list = [i for i in range(n) if i != first_medoid]

    # Add remaining medoids one by one
    while len(selected_list) < n_clusters:
        selected = np.array(selected_list, dtype=np.int32)
        unselected = np.array(unselected_list, dtype=np.int32)

        gains = compute_build_gain(np_dist_matrix, unselected, selected)
        best_idx = int(np.argmax(gains))
        best_candidate = unselected_list[best_idx]

        selected_list.append(best_candidate)
        unselected_list.remove(best_candidate)

    return selected_list, unselected_list
