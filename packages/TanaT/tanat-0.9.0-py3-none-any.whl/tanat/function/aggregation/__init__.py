#!/usr/bin/env python3
"""
Aggregation function types.
"""

from .type.mean.function import (
    MeanAggregationFunction,
)
from .type.sum.function import (
    SumAggregationFunction,
)


__all__ = [
    "MeanAggregationFunction",
    "SumAggregationFunction",
]
