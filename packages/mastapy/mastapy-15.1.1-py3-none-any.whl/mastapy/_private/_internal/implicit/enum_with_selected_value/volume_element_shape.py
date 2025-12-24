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
from mastapy._private.nodal_analysis import _99

_ARRAY = python_net_import("System", "Array")
_ENUM_WITH_SELECTED_VALUE = python_net_import(
    "SMT.MastaAPI.Utility.Property", "EnumWithSelectedValue"
)

if TYPE_CHECKING:
    from typing import Any, List, Type, TypeVar

    Self = TypeVar("Self", bound="EnumWithSelectedValue_VolumeElementShape")


__docformat__ = "restructuredtext en"
__all__ = ("EnumWithSelectedValue_VolumeElementShape",)


class EnumWithSelectedValue_VolumeElementShape(mixins.EnumWithSelectedValueMixin, Enum):
    """EnumWithSelectedValue_VolumeElementShape

    A specific implementation of 'EnumWithSelectedValue' for 'VolumeElementShape' types.
    """

    __qualname__ = "VolumeElementShape"

    @classmethod
    def wrapper_type(cls: "Type[EnumWithSelectedValue_VolumeElementShape]") -> "Any":
        """Pythonnet type of this class.

        Note:
            This property is readonly.

        Returns:
            Any
        """
        return _ENUM_WITH_SELECTED_VALUE

    @classmethod
    def wrapped_type(
        cls: "Type[EnumWithSelectedValue_VolumeElementShape]",
    ) -> "_99.VolumeElementShape":
        """Wrapped Pythonnet type of this class.

        Note:
            This property is readonly

        Returns:
            _99.VolumeElementShape
        """
        return _99.VolumeElementShape

    @classmethod
    def implicit_type(cls: "Type[EnumWithSelectedValue_VolumeElementShape]") -> "Any":
        """Implicit Pythonnet type of this class.

        Note:
            This property is readonly.

        Returns:
            Any
        """
        return _99.VolumeElementShape.type_()

    @property
    @exception_bridge
    def selected_value(self: "Self") -> "_99.VolumeElementShape":
        """mastapy.nodal_analysis.VolumeElementShape

        Note:
            This property is readonly.
        """
        return None

    @property
    @exception_bridge
    def available_values(self: "Self") -> "List[_99.VolumeElementShape]":
        """List[mastapy.nodal_analysis.VolumeElementShape]

        Note:
            This property is readonly.
        """
        return None
