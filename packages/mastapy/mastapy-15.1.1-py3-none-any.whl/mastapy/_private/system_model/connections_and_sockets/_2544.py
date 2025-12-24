"""OuterShaftSocket"""

from __future__ import annotations

from typing import TYPE_CHECKING, ClassVar

from mastapy._private._internal.dataclasses import extended_dataclass
from mastapy._private._internal.exceptions import CastException
from mastapy._private._internal.python_net import python_net_import

from mastapy._private._internal import utility
from mastapy._private.system_model.connections_and_sockets import _2545

_OUTER_SHAFT_SOCKET = python_net_import(
    "SMT.MastaAPI.SystemModel.ConnectionsAndSockets", "OuterShaftSocket"
)

if TYPE_CHECKING:
    from typing import Any, Type, TypeVar

    from mastapy._private.system_model.connections_and_sockets import (
        _2535,
        _2553,
        _2555,
    )

    Self = TypeVar("Self", bound="OuterShaftSocket")
    CastSelf = TypeVar("CastSelf", bound="OuterShaftSocket._Cast_OuterShaftSocket")


__docformat__ = "restructuredtext en"
__all__ = ("OuterShaftSocket",)


@extended_dataclass(frozen=True, slots=True, weakref_slot=True)
class _Cast_OuterShaftSocket:
    """Special nested class for casting OuterShaftSocket to subclasses."""

    __parent__: "OuterShaftSocket"

    @property
    def outer_shaft_socket_base(self: "CastSelf") -> "_2545.OuterShaftSocketBase":
        return self.__parent__._cast(_2545.OuterShaftSocketBase)

    @property
    def shaft_socket(self: "CastSelf") -> "_2553.ShaftSocket":
        from mastapy._private.system_model.connections_and_sockets import _2553

        return self.__parent__._cast(_2553.ShaftSocket)

    @property
    def cylindrical_socket(self: "CastSelf") -> "_2535.CylindricalSocket":
        from mastapy._private.system_model.connections_and_sockets import _2535

        return self.__parent__._cast(_2535.CylindricalSocket)

    @property
    def socket(self: "CastSelf") -> "_2555.Socket":
        from mastapy._private.system_model.connections_and_sockets import _2555

        return self.__parent__._cast(_2555.Socket)

    @property
    def outer_shaft_socket(self: "CastSelf") -> "OuterShaftSocket":
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
class OuterShaftSocket(_2545.OuterShaftSocketBase):
    """OuterShaftSocket

    This is a mastapy class.
    """

    TYPE: ClassVar["Type"] = _OUTER_SHAFT_SOCKET

    wrapped: "Any"

    def __post_init__(self: "Self") -> None:
        """Override of the post initialisation magic method."""
        if not hasattr(self.wrapped, "reference_count"):
            self.wrapped.reference_count = 0

        self.wrapped.reference_count += 1

    @property
    def cast_to(self: "Self") -> "_Cast_OuterShaftSocket":
        """Cast to another type.

        Returns:
            _Cast_OuterShaftSocket
        """
        return _Cast_OuterShaftSocket(self)
