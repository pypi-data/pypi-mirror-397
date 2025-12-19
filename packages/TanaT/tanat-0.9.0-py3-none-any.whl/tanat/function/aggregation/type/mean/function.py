#!/usr/bin/env python3
"""
Mean aggregation function.
"""

import logging

from numpy import nanmean as np_nanmean

from ...base.function import AggregationFunction
from .kernel import scalar_mean_kernel, matrix_mean_kernel


LOGGER = logging.getLogger(__name__)


class MeanAggregationFunction(AggregationFunction, register_name="mean"):
    """
    Mean aggregation function.
    """

    def __init__(self, settings=None):
        if settings is not None:
            LOGGER.warning(
                "MeanAggregationFunction does not support settings. Ignoring."
            )
            settings = None
        super().__init__(settings)

    def __call__(self, values):
        """
        Mean the values.

        Args:
            values (list):
                List of values to mean.

        Returns:
            float: The mean of the values.
        """
        return np_nanmean(values)

    @property
    def scalar_kernel(self):
        """Return the Numba-compiled scalar aggregation kernel."""
        return scalar_mean_kernel

    @property
    def matrix_kernel(self):
        """Return the Numba-compiled matrix aggregation kernel."""
        return matrix_mean_kernel
