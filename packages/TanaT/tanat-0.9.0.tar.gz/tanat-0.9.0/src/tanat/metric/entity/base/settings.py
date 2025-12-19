#!/usr/bin/env python3
"""
Base class for entity metric settings.
"""

from typing import Optional

from pydantic import field_validator
from pydantic.dataclasses import dataclass
from pypassist.fallback.typing import List


@dataclass
class BaseEntityMetricSettings:
    """
    Base class for entity metric settings.

    Attributes:
        entity_features (Optional[List[str]]):
            Column names for entity features to include in the metric.
            If None, all entity features will be used.
    """

    entity_features: Optional[List[str]] = None

    @field_validator("entity_features", mode="before")
    @classmethod
    def normalize_entity_features(cls, v):
        """
        Convert single string to list for user convenience.

        Allows users to pass a simple string when they have only one entity
        feature, instead of requiring a list. Pydantic then handles all native
        validation (type checking, etc.).

        Args:
            v: Entity feature(s) as string or list

        Returns:
            List: The value as a list (Pydantic will validate List[str] after)
        """
        if v is None:
            return v
        if isinstance(v, str):
            return [v]
        return v
