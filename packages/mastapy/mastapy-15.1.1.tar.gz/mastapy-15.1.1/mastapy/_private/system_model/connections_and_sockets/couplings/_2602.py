"""ClutchSocket"""

from __future__ import annotations

from typing import TYPE_CHECKING, ClassVar

from mastapy._private._internal.dataclasses import extended_dataclass
from mastapy._private._internal.exceptions import CastException
from mastapy._private._internal.python_net import python_net_import

from mastapy._private._internal import utility
from mastapy._private.system_model.connections_and_sockets.couplings import _2606

_CLUTCH_SOCKET = python_net_import(
    "SMT.MastaAPI.SystemModel.ConnectionsAndSockets.Couplings", "ClutchSocket"
)

if TYPE_CHECKING:
    from typing import Any, Type, TypeVar

    from mastapy._private.system_model.connections_and_sockets import _2535, _2555

    Self = TypeVar("Self", bound="ClutchSocket")
    CastSelf = TypeVar("CastSelf", bound="ClutchSocket._Cast_ClutchSocket")


__docformat__ = "restructuredtext en"
__all__ = ("ClutchSocket",)


@extended_dataclass(frozen=True, slots=True, weakref_slot=True)
class _Cast_ClutchSocket:
    """Special nested class for casting ClutchSocket to subclasses."""

    __parent__: "ClutchSocket"

    @property
    def coupling_socket(self: "CastSelf") -> "_2606.CouplingSocket":
        return self.__parent__._cast(_2606.CouplingSocket)

    @property
    def cylindrical_socket(self: "CastSelf") -> "_2535.CylindricalSocket":
        from mastapy._private.system_model.connections_and_sockets import _2535

        return self.__parent__._cast(_2535.CylindricalSocket)

    @property
    def socket(self: "CastSelf") -> "_2555.Socket":
        from mastapy._private.system_model.connections_and_sockets import _2555

        return self.__parent__._cast(_2555.Socket)

    @property
    def clutch_socket(self: "CastSelf") -> "ClutchSocket":
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
class ClutchSocket(_2606.CouplingSocket):
    """ClutchSocket

    This is a mastapy class.
    """

    TYPE: ClassVar["Type"] = _CLUTCH_SOCKET

    wrapped: "Any"

    def __post_init__(self: "Self") -> None:
        """Override of the post initialisation magic method."""
        if not hasattr(self.wrapped, "reference_count"):
            self.wrapped.reference_count = 0

        self.wrapped.reference_count += 1

    @property
    def cast_to(self: "Self") -> "_Cast_ClutchSocket":
        """Cast to another type.

        Returns:
            _Cast_ClutchSocket
        """
        return _Cast_ClutchSocket(self)
