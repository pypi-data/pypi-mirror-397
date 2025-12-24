"""EdgeNamedSelectionDetails"""

from __future__ import annotations

from typing import TYPE_CHECKING, ClassVar

from mastapy._private._internal.dataclasses import extended_dataclass
from mastapy._private._internal.exception_bridge import exception_bridge
from mastapy._private._internal.exceptions import CastException
from mastapy._private._internal.python_net import (
    python_net_import,
    pythonnet_property_get,
)

from mastapy._private import _0
from mastapy._private._internal import utility

_EDGE_NAMED_SELECTION_DETAILS = python_net_import(
    "SMT.MastaAPI.MathUtility", "EdgeNamedSelectionDetails"
)

if TYPE_CHECKING:
    from typing import Any, Type, TypeVar

    Self = TypeVar("Self", bound="EdgeNamedSelectionDetails")
    CastSelf = TypeVar(
        "CastSelf", bound="EdgeNamedSelectionDetails._Cast_EdgeNamedSelectionDetails"
    )


__docformat__ = "restructuredtext en"
__all__ = ("EdgeNamedSelectionDetails",)


@extended_dataclass(frozen=True, slots=True, weakref_slot=True)
class _Cast_EdgeNamedSelectionDetails:
    """Special nested class for casting EdgeNamedSelectionDetails to subclasses."""

    __parent__: "EdgeNamedSelectionDetails"

    @property
    def edge_named_selection_details(self: "CastSelf") -> "EdgeNamedSelectionDetails":
        return self.__parent__

    def __getattr__(self: "CastSelf", name: str) -> "Any":
        try:
            return self.__getattribute__(name)
        except AttributeError:
            class_name = utility.camel(name)
            raise CastException(
                f'Detected an invalid cast. Cannot cast to type "{class_name}"'
            ) from None


@extended_dataclass(frozen=True, slots=True, weakref_slot=True, eq=False)
class EdgeNamedSelectionDetails(_0.APIBase):
    """EdgeNamedSelectionDetails

    This is a mastapy class.
    """

    TYPE: ClassVar["Type"] = _EDGE_NAMED_SELECTION_DETAILS

    wrapped: "Any"

    def __post_init__(self: "Self") -> None:
        """Override of the post initialisation magic method."""
        if not hasattr(self.wrapped, "reference_count"):
            self.wrapped.reference_count = 0

        self.wrapped.reference_count += 1

    @property
    @exception_bridge
    def name(self: "Self") -> "str":
        """str

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "Name")

        if temp is None:
            return ""

        return temp

    @property
    def cast_to(self: "Self") -> "_Cast_EdgeNamedSelectionDetails":
        """Cast to another type.

        Returns:
            _Cast_EdgeNamedSelectionDetails
        """
        return _Cast_EdgeNamedSelectionDetails(self)
