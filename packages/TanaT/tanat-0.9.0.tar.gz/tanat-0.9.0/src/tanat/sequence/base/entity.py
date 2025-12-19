#!/usr/bin/env python3
"""
Entity base class.
"""

from abc import ABC, abstractmethod

from pypassist.mixin.settings import SettingsMixin


class Entity(ABC, SettingsMixin):
    """
    Entity class.
    """

    def __init__(self, data, settings, entity_descriptors=None):
        self._data = data
        self._entity_descriptors = entity_descriptors or {}
        SettingsMixin.__init__(self, settings)

    @property
    def value(self):
        """
        Return the value of the entity using all configured entity features.
        """
        return self.get_value()

    def get_value(self, feature_names=None):
        """
        Return the value of the entity for the specified features.

        Args:
            feature_names: Optional feature name(s) to use (str or list).
                If None, uses all entity_features from settings.

        Returns:
            The entity value - single value if one feature, tuple if multiple.
        """
        features = self._settings.validate_and_filter_entity_features(feature_names)
        data_row = self._data[features]
        if len(features) > 1:
            return tuple(data_row)
        return data_row.item()

    def get_feature_types(self, feature_names=None):
        """
        Return the types of the specified features.

        Args:
            feature_names: Optional feature name(s) to use (str or list).
                If None, uses all entity_features from settings.

        Returns:
            List[str]: Feature types (e.g., ['categorical', 'numerical']).
                Returns None values for features without descriptors.
        """
        features = self._settings.validate_and_filter_entity_features(feature_names)
        types = []
        for feature in features:
            descriptor = self._entity_descriptors.get(feature)
            types.append(descriptor.feature_type if descriptor else None)
        return types

    @property
    def extent(self):
        """
        Return the extent of the entity.
        """
        return self._get_temporal_extent()

    @abstractmethod
    def _get_temporal_extent(self):
        """
        Returns the extent of the entity.
        """

    def __getitem__(self, feature_name):
        if feature_name not in self._settings.get_valid_columns():
            raise ValueError(f"Invalid feature name: {feature_name}")

        return self._data[feature_name]


## -- Temporal extent


class TemporalExtent(ABC):
    """
    Representation of a temporal extent of a temporal entity
    """

    @abstractmethod
    def __repr__(self):
        """
        Return a string representation of the temporal extent.
        """


class InstantExtent(TemporalExtent):
    """
    Representation of an instant in time.
    """

    def __init__(self, date):
        self.date = date

    def __repr__(self):
        return str(self.date)


class PeriodExtent(TemporalExtent):
    """
    Representation of an period in time.
    """

    def __init__(self, start, end):
        self.start = start
        self.end = end

    def duration(self, granularity):
        """
        Duration of the period
        """
        raise NotImplementedError

    def __repr__(self):
        return f"[{self.start}, {self.end}]"
