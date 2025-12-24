"""Connector"""

from __future__ import annotations

from typing import TYPE_CHECKING, ClassVar

from mastapy._private._internal.dataclasses import extended_dataclass
from mastapy._private._internal.exception_bridge import exception_bridge
from mastapy._private._internal.exceptions import CastException
from mastapy._private._internal.python_net import (
    python_net_import,
    pythonnet_method_call,
    pythonnet_property_get,
)
from mastapy._private._internal.type_enforcement import enforce_parameter_types

from mastapy._private._internal import constructor, utility
from mastapy._private.system_model.part_model import _2737

_CONNECTOR = python_net_import("SMT.MastaAPI.SystemModel.PartModel", "Connector")

if TYPE_CHECKING:
    from typing import Any, Type, TypeVar

    from mastapy._private.system_model import _2451
    from mastapy._private.system_model.connections_and_sockets import _2531, _2535
    from mastapy._private.system_model.part_model import (
        _2704,
        _2708,
        _2714,
        _2715,
        _2739,
        _2742,
    )
    from mastapy._private.system_model.part_model.couplings import _2884

    Self = TypeVar("Self", bound="Connector")
    CastSelf = TypeVar("CastSelf", bound="Connector._Cast_Connector")


__docformat__ = "restructuredtext en"
__all__ = ("Connector",)


@extended_dataclass(frozen=True, slots=True, weakref_slot=True)
class _Cast_Connector:
    """Special nested class for casting Connector to subclasses."""

    __parent__: "Connector"

    @property
    def mountable_component(self: "CastSelf") -> "_2737.MountableComponent":
        return self.__parent__._cast(_2737.MountableComponent)

    @property
    def component(self: "CastSelf") -> "_2714.Component":
        return self.__parent__._cast(_2714.Component)

    @property
    def part(self: "CastSelf") -> "_2742.Part":
        from mastapy._private.system_model.part_model import _2742

        return self.__parent__._cast(_2742.Part)

    @property
    def design_entity(self: "CastSelf") -> "_2451.DesignEntity":
        from mastapy._private.system_model import _2451

        return self.__parent__._cast(_2451.DesignEntity)

    @property
    def bearing(self: "CastSelf") -> "_2708.Bearing":
        from mastapy._private.system_model.part_model import _2708

        return self.__parent__._cast(_2708.Bearing)

    @property
    def oil_seal(self: "CastSelf") -> "_2739.OilSeal":
        from mastapy._private.system_model.part_model import _2739

        return self.__parent__._cast(_2739.OilSeal)

    @property
    def shaft_hub_connection(self: "CastSelf") -> "_2884.ShaftHubConnection":
        from mastapy._private.system_model.part_model.couplings import _2884

        return self.__parent__._cast(_2884.ShaftHubConnection)

    @property
    def connector(self: "CastSelf") -> "Connector":
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
class Connector(_2737.MountableComponent):
    """Connector

    This is a mastapy class.
    """

    TYPE: ClassVar["Type"] = _CONNECTOR

    wrapped: "Any"

    def __post_init__(self: "Self") -> None:
        """Override of the post initialisation magic method."""
        if not hasattr(self.wrapped, "reference_count"):
            self.wrapped.reference_count = 0

        self.wrapped.reference_count += 1

    @property
    @exception_bridge
    def outer_component(self: "Self") -> "_2704.AbstractShaft":
        """mastapy.system_model.part_model.AbstractShaft

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "OuterComponent")

        if temp is None:
            return None

        type_ = temp.GetType()
        return constructor.new(type_.Namespace, type_.Name)(temp)

    @property
    @exception_bridge
    def outer_connection(self: "Self") -> "_2531.Connection":
        """mastapy.system_model.connections_and_sockets.Connection

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "OuterConnection")

        if temp is None:
            return None

        type_ = temp.GetType()
        return constructor.new(type_.Namespace, type_.Name)(temp)

    @property
    @exception_bridge
    def outer_socket(self: "Self") -> "_2535.CylindricalSocket":
        """mastapy.system_model.connections_and_sockets.CylindricalSocket

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "OuterSocket")

        if temp is None:
            return None

        type_ = temp.GetType()
        return constructor.new(type_.Namespace, type_.Name)(temp)

    @exception_bridge
    @enforce_parameter_types
    def house_in(
        self: "Self", shaft: "_2704.AbstractShaft", offset: "float" = float("nan")
    ) -> "_2531.Connection":
        """mastapy.system_model.connections_and_sockets.Connection

        Args:
            shaft (mastapy.system_model.part_model.AbstractShaft)
            offset (float, optional)
        """
        offset = float(offset)
        method_result = pythonnet_method_call(
            self.wrapped,
            "HouseIn",
            shaft.wrapped if shaft else None,
            offset if offset else 0.0,
        )
        type_ = method_result.GetType()
        return (
            constructor.new(type_.Namespace, type_.Name)(method_result)
            if method_result is not None
            else None
        )

    @exception_bridge
    @enforce_parameter_types
    def other_component(
        self: "Self", component: "_2714.Component"
    ) -> "_2704.AbstractShaft":
        """mastapy.system_model.part_model.AbstractShaft

        Args:
            component (mastapy.system_model.part_model.Component)
        """
        method_result = pythonnet_method_call(
            self.wrapped, "OtherComponent", component.wrapped if component else None
        )
        type_ = method_result.GetType()
        return (
            constructor.new(type_.Namespace, type_.Name)(method_result)
            if method_result is not None
            else None
        )

    @exception_bridge
    @enforce_parameter_types
    def try_house_in(
        self: "Self", shaft: "_2704.AbstractShaft", offset: "float" = float("nan")
    ) -> "_2715.ComponentsConnectedResult":
        """mastapy.system_model.part_model.ComponentsConnectedResult

        Args:
            shaft (mastapy.system_model.part_model.AbstractShaft)
            offset (float, optional)
        """
        offset = float(offset)
        method_result = pythonnet_method_call(
            self.wrapped,
            "TryHouseIn",
            shaft.wrapped if shaft else None,
            offset if offset else 0.0,
        )
        type_ = method_result.GetType()
        return (
            constructor.new(type_.Namespace, type_.Name)(method_result)
            if method_result is not None
            else None
        )

    @property
    def cast_to(self: "Self") -> "_Cast_Connector":
        """Cast to another type.

        Returns:
            _Cast_Connector
        """
        return _Cast_Connector(self)
