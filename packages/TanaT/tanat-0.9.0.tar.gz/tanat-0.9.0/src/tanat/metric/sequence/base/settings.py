#!/usr/bin/env python3
"""
Base settings for sequence metrics.
"""

from typing import Union

from pydantic.dataclasses import dataclass, Field

from ...entity.base.metric import EntityMetric
from ...matrix import MatrixStorageOptions


@dataclass
class BaseSequenceMetricSettings:
    """
    Base class for sequence metric settings.

    Attributes:
        entity_metric (Union[str, EntityMetric]):
            Metric used for entity-level distance computation.
            String identifier of a EntityMetric in the EntityMetric registry
            (e.g. "hamming") or an instance of EntityMetric. Defaults to "hamming".
        distance_matrix (MatrixStorageOptions):
            Options for distance matrix storage and handling.
            Contains options for on-disk storage, data type, and resuming from existing matrices.
    """

    entity_metric: Union[str, EntityMetric] = "hamming"
    distance_matrix: MatrixStorageOptions = Field(default_factory=MatrixStorageOptions)
