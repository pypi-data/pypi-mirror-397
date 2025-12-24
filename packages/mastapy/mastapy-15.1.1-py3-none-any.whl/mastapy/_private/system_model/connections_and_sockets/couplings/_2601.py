"""ClutchConnection"""

from __future__ import annotations

from typing import TYPE_CHECKING, ClassVar

from mastapy._private._internal.dataclasses import extended_dataclass
from mastapy._private._internal.exception_bridge import exception_bridge
from mastapy._private._internal.exceptions import CastException
from mastapy._private._internal.python_net import (
    python_net_import,
    pythonnet_property_get,
)

from mastapy._private._internal import utility
from mastapy._private.system_model.connections_and_sockets.couplings import _2605

_CLUTCH_CONNECTION = python_net_import(
    "SMT.MastaAPI.SystemModel.ConnectionsAndSockets.Couplings", "ClutchConnection"
)

if TYPE_CHECKING:
    from typing import Any, Type, TypeVar

    from mastapy._private.system_model import _2451
    from mastapy._private.system_model.connections_and_sockets import _2531, _2540

    Self = TypeVar("Self", bound="ClutchConnection")
    CastSelf = TypeVar("CastSelf", bound="ClutchConnection._Cast_ClutchConnection")


__docformat__ = "restructuredtext en"
__all__ = ("ClutchConnection",)


@extended_dataclass(frozen=True, slots=True, weakref_slot=True)
class _Cast_ClutchConnection:
    """Special nested class for casting ClutchConnection to subclasses."""

    __parent__: "ClutchConnection"

    @property
    def coupling_connection(self: "CastSelf") -> "_2605.CouplingConnection":
        return self.__parent__._cast(_2605.CouplingConnection)

    @property
    def inter_mountable_component_connection(
        self: "CastSelf",
    ) -> "_2540.InterMountableComponentConnection":
        from mastapy._private.system_model.connections_and_sockets import _2540

        return self.__parent__._cast(_2540.InterMountableComponentConnection)

    @property
    def connection(self: "CastSelf") -> "_2531.Connection":
        from mastapy._private.system_model.connections_and_sockets import _2531

        return self.__parent__._cast(_2531.Connection)

    @property
    def design_entity(self: "CastSelf") -> "_2451.DesignEntity":
        from mastapy._private.system_model import _2451

        return self.__parent__._cast(_2451.DesignEntity)

    @property
    def clutch_connection(self: "CastSelf") -> "ClutchConnection":
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
class ClutchConnection(_2605.CouplingConnection):
    """ClutchConnection

    This is a mastapy class.
    """

    TYPE: ClassVar["Type"] = _CLUTCH_CONNECTION

    wrapped: "Any"

    def __post_init__(self: "Self") -> None:
        """Override of the post initialisation magic method."""
        if not hasattr(self.wrapped, "reference_count"):
            self.wrapped.reference_count = 0

        self.wrapped.reference_count += 1

    @property
    @exception_bridge
    def effective_torque_radius(self: "Self") -> "float":
        """float

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "EffectiveTorqueRadius")

        if temp is None:
            return 0.0

        return temp

    @property
    @exception_bridge
    def torque_capacity(self: "Self") -> "float":
        """float

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "TorqueCapacity")

        if temp is None:
            return 0.0

        return temp

    @property
    def cast_to(self: "Self") -> "_Cast_ClutchConnection":
        """Cast to another type.

        Returns:
            _Cast_ClutchConnection
        """
        return _Cast_ClutchConnection(self)
