#!/usr/bin/env python3
"""
Common base class for function.
"""

from abc import ABC, abstractmethod

from pydantic_core import core_schema
from pypassist.mixin.settings import SettingsMixin
from pypassist.mixin.registrable import Registrable, UnregisteredTypeError


class Function(ABC, Registrable, SettingsMixin):
    """
    Common base class for function.
    """

    def __init__(self, settings, *, workenv=None):
        """
        Args:
            settings:
                The metric settings.

            workenv:
                Optional workenv instance.
        """
        SettingsMixin.__init__(self, settings)
        self._workenv = workenv

    @classmethod
    def get_function(cls, ftype, settings=None):
        """
        Retrieve and instantiate a Function.

        Args:
            ftype: Type of function to use, resolved via type registry.
            settings: Function-specific settings dictionary or dataclass.

        Returns:
            An instance of the Function configured
            with the provided settings.
        """
        try:
            function = cls.get_registered(ftype)(settings=settings)
        except UnregisteredTypeError as err:
            cls._unregistered_function_error(ftype, err)

        return function

    @classmethod
    @abstractmethod
    def _unregistered_function_error(cls, ftype, err):
        """Raise an error for an unregistered function with a custom message."""

    @abstractmethod
    def __call__(self, *args, **kwargs):
        """
        Call the function.
        """

    def __get_pydantic_core_schema__(self, handler):  # pylint: disable=unused-argument
        """Pydantic schema override."""
        return core_schema.any_schema()
