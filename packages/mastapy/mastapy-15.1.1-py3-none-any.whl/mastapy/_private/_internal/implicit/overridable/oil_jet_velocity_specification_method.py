"""Implementations of 'Overridable' in Python.

As Python does not have an implicit operator, this is the next
best solution for implementing these types properly.
"""

from __future__ import annotations

from enum import Enum
from typing import TYPE_CHECKING

from mastapy._private._internal import mixins
from mastapy._private._internal.exception_bridge import exception_bridge
from mastapy._private._internal.python_net import python_net_import
from mastapy._private.gears import _451

_OVERRIDABLE = python_net_import("SMT.MastaAPI.Utility.Property", "Overridable")

if TYPE_CHECKING:
    from typing import Any, Type, TypeVar

    Self = TypeVar("Self", bound="Overridable_OilJetVelocitySpecificationMethod")


__docformat__ = "restructuredtext en"
__all__ = ("Overridable_OilJetVelocitySpecificationMethod",)


class Overridable_OilJetVelocitySpecificationMethod(mixins.OverridableMixin, Enum):
    """Overridable_OilJetVelocitySpecificationMethod

    A specific implementation of 'Overridable' for 'OilJetVelocitySpecificationMethod' types.
    """

    __qualname__ = "OilJetVelocitySpecificationMethod"

    @classmethod
    def wrapper_type(
        cls: "Type[Overridable_OilJetVelocitySpecificationMethod]",
    ) -> "Any":
        """Pythonnet type of this class.

        Note:
            This property is readonly.

        Returns:
            Any
        """
        return _OVERRIDABLE

    @classmethod
    def wrapped_type(
        cls: "Type[Overridable_OilJetVelocitySpecificationMethod]",
    ) -> "_451.OilJetVelocitySpecificationMethod":
        """Wrapped Pythonnet type of this class.

        Note:
            This property is readonly

        Returns:
            _451.OilJetVelocitySpecificationMethod
        """
        return _451.OilJetVelocitySpecificationMethod

    @classmethod
    def implicit_type(
        cls: "Type[Overridable_OilJetVelocitySpecificationMethod]",
    ) -> "Any":
        """Implicit Pythonnet type of this class.

        Note:
            This property is readonly.

        Returns:
            Any
        """
        return _451.OilJetVelocitySpecificationMethod.type_()

    @property
    @exception_bridge
    def value(self: "Self") -> "_451.OilJetVelocitySpecificationMethod":
        """mastapy.gears.OilJetVelocitySpecificationMethod

        Note:
            This property is readonly.
        """
        return None

    @property
    @exception_bridge
    def overridden(self: "Self") -> "bool":
        """bool

        Note:
            This property is readonly.
        """
        return None

    @property
    @exception_bridge
    def override_value(self: "Self") -> "_451.OilJetVelocitySpecificationMethod":
        """mastapy.gears.OilJetVelocitySpecificationMethod

        Note:
            This property is readonly.
        """
        return None

    @property
    @exception_bridge
    def calculated_value(self: "Self") -> "_451.OilJetVelocitySpecificationMethod":
        """mastapy.gears.OilJetVelocitySpecificationMethod

        Note:
            This property is readonly.
        """
        return None
