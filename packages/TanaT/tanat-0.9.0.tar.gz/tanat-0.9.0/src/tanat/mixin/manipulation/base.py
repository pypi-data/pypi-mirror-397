#!/usr/bin/env python3
"""
Base manipulation mixin for sequence and trajectory containers.
"""

import copy
from abc import ABC, abstractmethod

from pydantic import ValidationError

from pypassist.mixin.cachable import Cachable

from ...zeroing.setter import ZeroSetter


class BaseManipulationMixin(ABC):
    """
    Base mixin providing common manipulation methods.

    Reduces code duplication between sequence & trajectory modules
    by implementing shared logic with specialized abstract hooks.
    """

    def __init__(self):
        self._t_zero = None
        self._zeroing_base_class = ZeroSetter

    @property
    def _is_pool(self):
        """
        Internal property to determine if the object is a Pool or not.
        Usefull to avoid circular import and allows treatment of both.
        """
        return getattr(self, "_IS_POOL", False)

    @property
    def _container_type(self):
        """
        Internal property to determine the container type.
        Returns: 'sequence' or 'trajectory'
        """
        return getattr(self, "_CONTAINER_TYPE", None)

    def copy(self, deep=True):
        """
        Create shallow or deep copy of container.

        Args:
            deep: If True, create deep copy. Default True.

        Returns:
            Copy of the container instance.
        """
        copy_data = self._get_copy_data(deep)
        return self._create_copy_instance(copy_data)

    @abstractmethod
    def _get_copy_data(self, deep):
        """Extract data for copy operation."""

    @abstractmethod
    def _create_copy_instance(self, copy_data):
        """Create new instance with copied data."""

    # Common copy methods for all containers
    def _copy_settings(self, deep):
        """Create a copy of dataclass settings."""
        if deep:
            return copy.deepcopy(self.settings)
        return copy.copy(self.settings)

    def _copy_metadata(self, deep):
        """Create a copy of metadata if it exists."""
        if self.metadata is None:
            return None
        if deep:
            return copy.deepcopy(self.metadata)
        return copy.copy(self.metadata)

    def _copy_static_data(self, deep):
        """Create a copy of static data if it exists."""
        if self.static_data is None:
            return None
        return self.static_data.copy(deep=deep)

    ## ----- ZEROING ----- ##

    @Cachable.caching_property
    def t_zero(self):  # pylint: disable=E0202
        """
        The index date(s) used to calculate elapsed time.

        For pools with dict-based t_zero, automatically filters to keep
        only IDs that exist in the current pool.

        Cached to avoid repeated filtering on each access.
        """
        if self._t_zero is None:
            self._default_zero_setter()

        # For dict, return filtered version (without modifying _t_zero)
        if isinstance(self._t_zero, dict):
            # getattr(unique_ids) is None => single sequence
            valid_ids = getattr(self, "unique_ids", None) or [self.id_value]
            return {k: v for k, v in self._t_zero.items() if k in valid_ids}

        return self._t_zero

    @property
    def t0(self):
        """
        Alias for t_zero.
        """
        return self.t_zero

    @t_zero.setter
    def t_zero(self, value):
        """
        Set the index date(s).
        """
        settings_dict = {"value": value}
        try:
            indexer = self._zeroing_base_class.init(
                settings=settings_dict, zero_setter_type="direct"
            )
        except (TypeError, ValidationError) as err:
            raise ValueError(
                f"Invalid t_zero value: {value!r}. Expected a datetime or a dict."
            ) from err

        indexer.assign(self)  # Will clear cache via _clear_cache_and_return

    @t0.setter
    def t0(self, value):
        """
        Alias for t_zero setter.
        """
        self.t_zero = value

    def _default_zero_setter(self):
        """
        Default setter method if no t_zero is set.
        By default, position setter is used (with default settings).
        """
        self.zero_from_position()

    def _propagate_t_zero(self, child, id_value=None):
        """
        Propagate t_zero to child container.

        For pools, the child's t_zero property will automatically filter
        invalid IDs when accessed.

        Args:
            child: Child container to receive t_zero.
            id_value: Specific ID for dict-based t_zero (single sequence). Optional.
        """
        # Use property to ensure t_zero is computed if not already set
        t_zero = self.t_zero

        if isinstance(t_zero, dict) and id_value is not None:
            # Single sequence extraction
            child._t_zero = t_zero.get(id_value, None)
        else:
            # Copy as-is (dict or scalar) - filtering done by property getter
            child._t_zero = t_zero.copy() if isinstance(t_zero, dict) else t_zero
