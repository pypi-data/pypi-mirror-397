"""NodesForPlanetarySocket"""

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

_NODES_FOR_PLANETARY_SOCKET = python_net_import(
    "SMT.MastaAPI.SystemModel.FE", "NodesForPlanetarySocket"
)

if TYPE_CHECKING:
    from typing import Any, List, Type, TypeVar

    from mastapy._private.system_model.fe import _2670

    Self = TypeVar("Self", bound="NodesForPlanetarySocket")
    CastSelf = TypeVar(
        "CastSelf", bound="NodesForPlanetarySocket._Cast_NodesForPlanetarySocket"
    )


__docformat__ = "restructuredtext en"
__all__ = ("NodesForPlanetarySocket",)


@extended_dataclass(frozen=True, slots=True, weakref_slot=True)
class _Cast_NodesForPlanetarySocket:
    """Special nested class for casting NodesForPlanetarySocket to subclasses."""

    __parent__: "NodesForPlanetarySocket"

    @property
    def nodes_for_planetary_socket(self: "CastSelf") -> "NodesForPlanetarySocket":
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
class NodesForPlanetarySocket(_0.APIBase):
    """NodesForPlanetarySocket

    This is a mastapy class.
    """

    TYPE: ClassVar["Type"] = _NODES_FOR_PLANETARY_SOCKET

    wrapped: "Any"

    def __post_init__(self: "Self") -> None:
        """Override of the post initialisation magic method."""
        if not hasattr(self.wrapped, "reference_count"):
            self.wrapped.reference_count = 0

        self.wrapped.reference_count += 1

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
    @exception_bridge
    def nodes_for_sockets(self: "Self") -> "List[_2670.NodesForPlanetInSocket]":
        """List[mastapy.system_model.fe.NodesForPlanetInSocket]

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "NodesForSockets")

        if temp is None:
            return None

        value = conversion.pn_to_mp_objects_in_list(temp)

        if value is None:
            return None

        return value

    @property
    def cast_to(self: "Self") -> "_Cast_NodesForPlanetarySocket":
        """Cast to another type.

        Returns:
            _Cast_NodesForPlanetarySocket
        """
        return _Cast_NodesForPlanetarySocket(self)
