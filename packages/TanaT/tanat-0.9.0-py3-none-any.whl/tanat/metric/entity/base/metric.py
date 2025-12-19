#!/usr/bin/env python3
"""
Base class for entity metrics.
"""

import logging
from abc import abstractmethod

from .exception import UnregisteredEntityMetricTypeError
from ....sequence.base.entity import Entity
from ...base import Metric

LOGGER = logging.getLogger(__name__)


class EntityMetric(Metric):
    """
    Base class for entity metrics.
    """

    _REGISTER = {}

    def __init__(self, settings=None, *, workenv=None):
        super().__init__(settings, workenv=workenv)

    def __call__(self, ent_a, ent_b, **kwargs):
        """
        Compute the metric for a specific pair of entities.

        Validates inputs and feature types, then delegates to _compute_single_distance.

        Args:
            ent_a (Entity):
                First entity.
            ent_b (Entity):
                Second entity.
            kwargs:
                Optional arguments to override specific settings.

        Returns:
            float: The metric value for the entity pair.

        Example:
            >>> from tanat.metric.entity import EntityMetric
            >>> metric = EntityMetric.get_metric("hamming")
            >>> distance = metric(ent_a, ent_b)
        """
        self._validate_entities(ent_a=ent_a, ent_b=ent_b)
        self._ensure_feature_types_valid(ent_a, ent_b)

        with self.with_tmp_settings(**kwargs):
            return self._compute_single_distance(ent_a, ent_b)

    @abstractmethod
    def _compute_single_distance(self, ent_a, ent_b):
        """
        Compute distance between two entities.

        Subclasses must implement this method with their specific
        computation logic. Settings overrides are already applied
        via with_tmp_settings in __call__.

        Args:
            ent_a (Entity): First entity.
            ent_b (Entity): Second entity.

        Returns:
            float: The metric value for the entity pair.
        """

    @property
    def entity_features(self):
        """
        Get the list of entity features to consider for the metric.

        Returns:
            list or None: List of entity feature names, or None to use all features.
        """
        if not hasattr(self.settings, "entity_features"):
            LOGGER.warning(
                "%s: No entity features configured. "
                "Settings must inherit from BaseEntityMetricSettings with `entity_features` field.",
                self.__class__.__name__,
            )
            return None

        return self.settings.entity_features

    @abstractmethod
    def prepare_computation_data(self, sequence_array):
        """
        Prepare inputs for computation execution (e.g. Numba).

        Args:
            sequence_array (SequenceArray): The input sequence data.

        Returns:
            tuple: (processed_arrays, context)
        """

    @property
    @abstractmethod
    def distance_kernel(self):
        """
        Return the compiled element-wise distance function (e.g. Numba JIT).

        Returns:
            function: JIT-compiled function (val_a, val_b, context) -> float
        """

    @abstractmethod
    def validate_feature_types(self, feature_types):
        """
        Validate feature types compatibility with this metric.

        Called before computation to ensure features are compatible.
        Each EntityMetric subclass must define its constraints or pass silently.

        Args:
            feature_types: List of feature types (e.g. ["categorical", "numerical", "textual"]).

        Raises:
            ValueError: With explanation if features are incompatible.
        """

    def _ensure_feature_types_valid(self, ent_a, ent_b):
        """
        Validate feature types for both entities.

        Checks that each entity's feature types are compatible with this metric.

        Args:
            ent_a: First Entity instance.
            ent_b: Second Entity instance.

        Raises:
            ValueError: If feature types are incompatible with metric.
        """
        for entity in (ent_a, ent_b):
            feature_types = entity.get_feature_types(self.entity_features)
            # Filter out None values (features without descriptors)
            feature_types = [ft for ft in feature_types if ft is not None]
            if feature_types:
                self.validate_feature_types(feature_types)

    def _validate_entities(self, **entities):
        """
        Validate multiple sequences, ensuring they are of the correct type.

        Args:
            entities:
                Dictionary of entities to validate.

        Raises:
            ValueError: If any entity is invalid.
        """
        for key, entity in entities.items():
            if not self._is_valid_entity(entity):
                raise ValueError(
                    f"Invalid sequence '{key}'. Expected Entity, got {type(entity)}."
                )

    def _is_valid_entity(self, entity):
        """
        Check if a given sequence is valid.

        Args:
            entity:
                The entity to validate.

        Returns:
            bool: True if valid, False otherwise.
        """
        return isinstance(entity, Entity)

    @classmethod
    def _unregistered_metric_error(cls, mtype, err):
        """Raise an error for an unregistered entity metric with a custom message."""
        registered = cls.list_registered()
        raise UnregisteredEntityMetricTypeError(
            f"Unknown entity metric: '{mtype}'. " f"Available metrics: {registered}"
        ) from err
