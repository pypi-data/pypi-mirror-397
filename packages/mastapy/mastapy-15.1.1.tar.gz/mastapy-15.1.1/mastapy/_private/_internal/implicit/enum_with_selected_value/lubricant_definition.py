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
from mastapy._private.materials import _363

_ARRAY = python_net_import("System", "Array")
_ENUM_WITH_SELECTED_VALUE = python_net_import(
    "SMT.MastaAPI.Utility.Property", "EnumWithSelectedValue"
)

if TYPE_CHECKING:
    from typing import Any, List, Type, TypeVar

    Self = TypeVar("Self", bound="EnumWithSelectedValue_LubricantDefinition")


__docformat__ = "restructuredtext en"
__all__ = ("EnumWithSelectedValue_LubricantDefinition",)


class EnumWithSelectedValue_LubricantDefinition(
    mixins.EnumWithSelectedValueMixin, Enum
):
    """EnumWithSelectedValue_LubricantDefinition

    A specific implementation of 'EnumWithSelectedValue' for 'LubricantDefinition' types.
    """

    __qualname__ = "LubricantDefinition"

    @classmethod
    def wrapper_type(cls: "Type[EnumWithSelectedValue_LubricantDefinition]") -> "Any":
        """Pythonnet type of this class.

        Note:
            This property is readonly.

        Returns:
            Any
        """
        return _ENUM_WITH_SELECTED_VALUE

    @classmethod
    def wrapped_type(
        cls: "Type[EnumWithSelectedValue_LubricantDefinition]",
    ) -> "_363.LubricantDefinition":
        """Wrapped Pythonnet type of this class.

        Note:
            This property is readonly

        Returns:
            _363.LubricantDefinition
        """
        return _363.LubricantDefinition

    @classmethod
    def implicit_type(cls: "Type[EnumWithSelectedValue_LubricantDefinition]") -> "Any":
        """Implicit Pythonnet type of this class.

        Note:
            This property is readonly.

        Returns:
            Any
        """
        return _363.LubricantDefinition.type_()

    @property
    @exception_bridge
    def selected_value(self: "Self") -> "_363.LubricantDefinition":
        """mastapy.materials.LubricantDefinition

        Note:
            This property is readonly.
        """
        return None

    @property
    @exception_bridge
    def available_values(self: "Self") -> "List[_363.LubricantDefinition]":
        """List[mastapy.materials.LubricantDefinition]

        Note:
            This property is readonly.
        """
        return None
