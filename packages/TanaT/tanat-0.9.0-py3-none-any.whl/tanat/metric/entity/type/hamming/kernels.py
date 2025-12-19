# #!/usr/bin/env python3
"""
Simple and weighted Hamming distance kernels.
"""

from numba import jit


@jit(nopython=True)
def hamming_dist_simple(a, b, context):  # pylint: disable=unused-argument
    """
    Simple Hamming distance kernel.

    Args:
        a: Encoded value (int32 index).
        b: Encoded value (int32 index).
        context: Unused (empty tuple), kept for signature uniformity.

    Returns:
        1.0 if different, 0.0 if equal.
    """
    return 1.0 if a != b else 0.0


@jit(nopython=True)
def hamming_dist_weighted(a, b, context):
    """
    Weighted Hamming distance kernel using cost matrix.

    Args:
        a: Encoded value (int32 index into cost_matrix).
        b: Encoded value (int32 index into cost_matrix).
        context: Tuple containing (cost_matrix,).

    Returns:
        Cost value from matrix.
    """
    cost_matrix = context[0]
    return cost_matrix[a, b]
