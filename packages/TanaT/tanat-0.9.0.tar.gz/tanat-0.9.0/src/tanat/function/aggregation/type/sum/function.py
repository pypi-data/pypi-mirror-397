#!/usr/bin/env python3
"""
Sum aggregation function.
"""

import logging

from numpy import nansum as np_nansum

from ...base.function import AggregationFunction
from .kernel import scalar_sum_kernel, matrix_sum_kernel


LOGGER = logging.getLogger(__name__)


class SumAggregationFunction(AggregationFunction, register_name="sum"):
    """
    Sum aggregation function.
    """

    def __init__(self, settings=None):
        if settings is not None:
            LOGGER.warning(
                "SumAggregationFunction does not support settings. Ignoring."
            )
            settings = None
        super().__init__(settings)

    def __call__(self, values):
        """
        Sum the values.

        Args:
            values (list):
                List of values to sum.

        Returns:
            float: The sum of the values.
        """
        return np_nansum(values)

    @property
    def scalar_kernel(self):
        """Return the Numba-compiled scalar aggregation kernel."""
        return scalar_sum_kernel

    @property
    def matrix_kernel(self):
        """Return the Numba-compiled matrix aggregation kernel."""
        return matrix_sum_kernel
