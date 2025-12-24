"""UnavailableSocketForWindup"""

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
from mastapy._private._internal import conversion, utility

_UNAVAILABLE_SOCKET_FOR_WINDUP = python_net_import(
    "SMT.MastaAPI.SystemModel.AnalysesAndResults.SystemDeflections",
    "UnavailableSocketForWindup",
)

if TYPE_CHECKING:
    from typing import Any, List, Type, TypeVar

    Self = TypeVar("Self", bound="UnavailableSocketForWindup")
    CastSelf = TypeVar(
        "CastSelf", bound="UnavailableSocketForWindup._Cast_UnavailableSocketForWindup"
    )


__docformat__ = "restructuredtext en"
__all__ = ("UnavailableSocketForWindup",)


@extended_dataclass(frozen=True, slots=True, weakref_slot=True)
class _Cast_UnavailableSocketForWindup:
    """Special nested class for casting UnavailableSocketForWindup to subclasses."""

    __parent__: "UnavailableSocketForWindup"

    @property
    def unavailable_socket_for_windup(self: "CastSelf") -> "UnavailableSocketForWindup":
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
class UnavailableSocketForWindup(_0.APIBase):
    """UnavailableSocketForWindup

    This is a mastapy class.
    """

    TYPE: ClassVar["Type"] = _UNAVAILABLE_SOCKET_FOR_WINDUP

    wrapped: "Any"

    def __post_init__(self: "Self") -> None:
        """Override of the post initialisation magic method."""
        if not hasattr(self.wrapped, "reference_count"):
            self.wrapped.reference_count = 0

        self.wrapped.reference_count += 1

    @property
    @exception_bridge
    def required_angles(self: "Self") -> "List[float]":
        """List[float]

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "RequiredAngles")

        if temp is None:
            return None

        value = conversion.pn_to_mp_objects_in_list(temp, float)

        if value is None:
            return None

        return value

    @property
    @exception_bridge
    def selected_node_angles(self: "Self") -> "List[float]":
        """List[float]

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "SelectedNodeAngles")

        if temp is None:
            return None

        value = conversion.pn_to_mp_objects_in_list(temp, float)

        if value is None:
            return None

        return value

    @property
    @exception_bridge
    def socket(self: "Self") -> "str":
        """str

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "Socket")

        if temp is None:
            return ""

        return temp

    @property
    def cast_to(self: "Self") -> "_Cast_UnavailableSocketForWindup":
        """Cast to another type.

        Returns:
            _Cast_UnavailableSocketForWindup
        """
        return _Cast_UnavailableSocketForWindup(self)
