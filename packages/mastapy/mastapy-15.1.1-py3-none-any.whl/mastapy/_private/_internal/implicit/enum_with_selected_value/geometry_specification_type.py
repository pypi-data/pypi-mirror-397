"""Implementations of 'EnumWithSelectedValue' in Python.

As Python does not have an implicit operator, this is the next
best solution for implementing these types properly.
"""

from __future__ import annotations

from enum import Enum
from typing import TYPE_CHECKING

from mastapy._private._internal import mixins
from mastapy._private._internal.exception_bridge import exception_bridge
from mastapy._private._internal.python_net import python_net_import
from mastapy._private.gears.gear_designs.cylindrical import _1182

_ARRAY = python_net_import("System", "Array")
_ENUM_WITH_SELECTED_VALUE = python_net_import(
    "SMT.MastaAPI.Utility.Property", "EnumWithSelectedValue"
)

if TYPE_CHECKING:
    from typing import Any, List, Type, TypeVar

    Self = TypeVar("Self", bound="EnumWithSelectedValue_GeometrySpecificationType")


__docformat__ = "restructuredtext en"
__all__ = ("EnumWithSelectedValue_GeometrySpecificationType",)


class EnumWithSelectedValue_GeometrySpecificationType(
    mixins.EnumWithSelectedValueMixin, Enum
):
    """EnumWithSelectedValue_GeometrySpecificationType

    A specific implementation of 'EnumWithSelectedValue' for 'GeometrySpecificationType' types.
    """

    __qualname__ = "GeometrySpecificationType"

    @classmethod
    def wrapper_type(
        cls: "Type[EnumWithSelectedValue_GeometrySpecificationType]",
    ) -> "Any":
        """Pythonnet type of this class.

        Note:
            This property is readonly.

        Returns:
            Any
        """
        return _ENUM_WITH_SELECTED_VALUE

    @classmethod
    def wrapped_type(
        cls: "Type[EnumWithSelectedValue_GeometrySpecificationType]",
    ) -> "_1182.GeometrySpecificationType":
        """Wrapped Pythonnet type of this class.

        Note:
            This property is readonly

        Returns:
            _1182.GeometrySpecificationType
        """
        return _1182.GeometrySpecificationType

    @classmethod
    def implicit_type(
        cls: "Type[EnumWithSelectedValue_GeometrySpecificationType]",
    ) -> "Any":
        """Implicit Pythonnet type of this class.

        Note:
            This property is readonly.

        Returns:
            Any
        """
        return _1182.GeometrySpecificationType.type_()

    @property
    @exception_bridge
    def selected_value(self: "Self") -> "_1182.GeometrySpecificationType":
        """mastapy.gears.gear_designs.cylindrical.GeometrySpecificationType

        Note:
            This property is readonly.
        """
        return None

    @property
    @exception_bridge
    def available_values(self: "Self") -> "List[_1182.GeometrySpecificationType]":
        """List[mastapy.gears.gear_designs.cylindrical.GeometrySpecificationType]

        Note:
            This property is readonly.
        """
        return None
