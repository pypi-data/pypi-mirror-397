"""CylindricalSocket"""

from __future__ import annotations

from typing import TYPE_CHECKING, ClassVar

from mastapy._private._internal.dataclasses import extended_dataclass
from mastapy._private._internal.exceptions import CastException
from mastapy._private._internal.python_net import python_net_import

from mastapy._private._internal import utility
from mastapy._private.system_model.connections_and_sockets import _2555

_CYLINDRICAL_SOCKET = python_net_import(
    "SMT.MastaAPI.SystemModel.ConnectionsAndSockets", "CylindricalSocket"
)

if TYPE_CHECKING:
    from typing import Any, Type, TypeVar

    from mastapy._private.system_model.connections_and_sockets import (
        _2525,
        _2526,
        _2533,
        _2538,
        _2539,
        _2541,
        _2542,
        _2543,
        _2544,
        _2545,
        _2547,
        _2548,
        _2549,
        _2552,
        _2553,
    )
    from mastapy._private.system_model.connections_and_sockets.couplings import (
        _2602,
        _2604,
        _2606,
        _2608,
        _2610,
        _2612,
        _2613,
    )
    from mastapy._private.system_model.connections_and_sockets.cycloidal import (
        _2592,
        _2593,
        _2595,
        _2596,
        _2598,
        _2599,
    )
    from mastapy._private.system_model.connections_and_sockets.gears import _2569

    Self = TypeVar("Self", bound="CylindricalSocket")
    CastSelf = TypeVar("CastSelf", bound="CylindricalSocket._Cast_CylindricalSocket")


__docformat__ = "restructuredtext en"
__all__ = ("CylindricalSocket",)


@extended_dataclass(frozen=True, slots=True, weakref_slot=True)
class _Cast_CylindricalSocket:
    """Special nested class for casting CylindricalSocket to subclasses."""

    __parent__: "CylindricalSocket"

    @property
    def socket(self: "CastSelf") -> "_2555.Socket":
        return self.__parent__._cast(_2555.Socket)

    @property
    def bearing_inner_socket(self: "CastSelf") -> "_2525.BearingInnerSocket":
        from mastapy._private.system_model.connections_and_sockets import _2525

        return self.__parent__._cast(_2525.BearingInnerSocket)

    @property
    def bearing_outer_socket(self: "CastSelf") -> "_2526.BearingOuterSocket":
        from mastapy._private.system_model.connections_and_sockets import _2526

        return self.__parent__._cast(_2526.BearingOuterSocket)

    @property
    def cvt_pulley_socket(self: "CastSelf") -> "_2533.CVTPulleySocket":
        from mastapy._private.system_model.connections_and_sockets import _2533

        return self.__parent__._cast(_2533.CVTPulleySocket)

    @property
    def inner_shaft_socket(self: "CastSelf") -> "_2538.InnerShaftSocket":
        from mastapy._private.system_model.connections_and_sockets import _2538

        return self.__parent__._cast(_2538.InnerShaftSocket)

    @property
    def inner_shaft_socket_base(self: "CastSelf") -> "_2539.InnerShaftSocketBase":
        from mastapy._private.system_model.connections_and_sockets import _2539

        return self.__parent__._cast(_2539.InnerShaftSocketBase)

    @property
    def mountable_component_inner_socket(
        self: "CastSelf",
    ) -> "_2541.MountableComponentInnerSocket":
        from mastapy._private.system_model.connections_and_sockets import _2541

        return self.__parent__._cast(_2541.MountableComponentInnerSocket)

    @property
    def mountable_component_outer_socket(
        self: "CastSelf",
    ) -> "_2542.MountableComponentOuterSocket":
        from mastapy._private.system_model.connections_and_sockets import _2542

        return self.__parent__._cast(_2542.MountableComponentOuterSocket)

    @property
    def mountable_component_socket(
        self: "CastSelf",
    ) -> "_2543.MountableComponentSocket":
        from mastapy._private.system_model.connections_and_sockets import _2543

        return self.__parent__._cast(_2543.MountableComponentSocket)

    @property
    def outer_shaft_socket(self: "CastSelf") -> "_2544.OuterShaftSocket":
        from mastapy._private.system_model.connections_and_sockets import _2544

        return self.__parent__._cast(_2544.OuterShaftSocket)

    @property
    def outer_shaft_socket_base(self: "CastSelf") -> "_2545.OuterShaftSocketBase":
        from mastapy._private.system_model.connections_and_sockets import _2545

        return self.__parent__._cast(_2545.OuterShaftSocketBase)

    @property
    def planetary_socket(self: "CastSelf") -> "_2547.PlanetarySocket":
        from mastapy._private.system_model.connections_and_sockets import _2547

        return self.__parent__._cast(_2547.PlanetarySocket)

    @property
    def planetary_socket_base(self: "CastSelf") -> "_2548.PlanetarySocketBase":
        from mastapy._private.system_model.connections_and_sockets import _2548

        return self.__parent__._cast(_2548.PlanetarySocketBase)

    @property
    def pulley_socket(self: "CastSelf") -> "_2549.PulleySocket":
        from mastapy._private.system_model.connections_and_sockets import _2549

        return self.__parent__._cast(_2549.PulleySocket)

    @property
    def rolling_ring_socket(self: "CastSelf") -> "_2552.RollingRingSocket":
        from mastapy._private.system_model.connections_and_sockets import _2552

        return self.__parent__._cast(_2552.RollingRingSocket)

    @property
    def shaft_socket(self: "CastSelf") -> "_2553.ShaftSocket":
        from mastapy._private.system_model.connections_and_sockets import _2553

        return self.__parent__._cast(_2553.ShaftSocket)

    @property
    def cylindrical_gear_teeth_socket(
        self: "CastSelf",
    ) -> "_2569.CylindricalGearTeethSocket":
        from mastapy._private.system_model.connections_and_sockets.gears import _2569

        return self.__parent__._cast(_2569.CylindricalGearTeethSocket)

    @property
    def cycloidal_disc_axial_left_socket(
        self: "CastSelf",
    ) -> "_2592.CycloidalDiscAxialLeftSocket":
        from mastapy._private.system_model.connections_and_sockets.cycloidal import (
            _2592,
        )

        return self.__parent__._cast(_2592.CycloidalDiscAxialLeftSocket)

    @property
    def cycloidal_disc_axial_right_socket(
        self: "CastSelf",
    ) -> "_2593.CycloidalDiscAxialRightSocket":
        from mastapy._private.system_model.connections_and_sockets.cycloidal import (
            _2593,
        )

        return self.__parent__._cast(_2593.CycloidalDiscAxialRightSocket)

    @property
    def cycloidal_disc_inner_socket(
        self: "CastSelf",
    ) -> "_2595.CycloidalDiscInnerSocket":
        from mastapy._private.system_model.connections_and_sockets.cycloidal import (
            _2595,
        )

        return self.__parent__._cast(_2595.CycloidalDiscInnerSocket)

    @property
    def cycloidal_disc_outer_socket(
        self: "CastSelf",
    ) -> "_2596.CycloidalDiscOuterSocket":
        from mastapy._private.system_model.connections_and_sockets.cycloidal import (
            _2596,
        )

        return self.__parent__._cast(_2596.CycloidalDiscOuterSocket)

    @property
    def cycloidal_disc_planetary_bearing_socket(
        self: "CastSelf",
    ) -> "_2598.CycloidalDiscPlanetaryBearingSocket":
        from mastapy._private.system_model.connections_and_sockets.cycloidal import (
            _2598,
        )

        return self.__parent__._cast(_2598.CycloidalDiscPlanetaryBearingSocket)

    @property
    def ring_pins_socket(self: "CastSelf") -> "_2599.RingPinsSocket":
        from mastapy._private.system_model.connections_and_sockets.cycloidal import (
            _2599,
        )

        return self.__parent__._cast(_2599.RingPinsSocket)

    @property
    def clutch_socket(self: "CastSelf") -> "_2602.ClutchSocket":
        from mastapy._private.system_model.connections_and_sockets.couplings import (
            _2602,
        )

        return self.__parent__._cast(_2602.ClutchSocket)

    @property
    def concept_coupling_socket(self: "CastSelf") -> "_2604.ConceptCouplingSocket":
        from mastapy._private.system_model.connections_and_sockets.couplings import (
            _2604,
        )

        return self.__parent__._cast(_2604.ConceptCouplingSocket)

    @property
    def coupling_socket(self: "CastSelf") -> "_2606.CouplingSocket":
        from mastapy._private.system_model.connections_and_sockets.couplings import (
            _2606,
        )

        return self.__parent__._cast(_2606.CouplingSocket)

    @property
    def part_to_part_shear_coupling_socket(
        self: "CastSelf",
    ) -> "_2608.PartToPartShearCouplingSocket":
        from mastapy._private.system_model.connections_and_sockets.couplings import (
            _2608,
        )

        return self.__parent__._cast(_2608.PartToPartShearCouplingSocket)

    @property
    def spring_damper_socket(self: "CastSelf") -> "_2610.SpringDamperSocket":
        from mastapy._private.system_model.connections_and_sockets.couplings import (
            _2610,
        )

        return self.__parent__._cast(_2610.SpringDamperSocket)

    @property
    def torque_converter_pump_socket(
        self: "CastSelf",
    ) -> "_2612.TorqueConverterPumpSocket":
        from mastapy._private.system_model.connections_and_sockets.couplings import (
            _2612,
        )

        return self.__parent__._cast(_2612.TorqueConverterPumpSocket)

    @property
    def torque_converter_turbine_socket(
        self: "CastSelf",
    ) -> "_2613.TorqueConverterTurbineSocket":
        from mastapy._private.system_model.connections_and_sockets.couplings import (
            _2613,
        )

        return self.__parent__._cast(_2613.TorqueConverterTurbineSocket)

    @property
    def cylindrical_socket(self: "CastSelf") -> "CylindricalSocket":
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
class CylindricalSocket(_2555.Socket):
    """CylindricalSocket

    This is a mastapy class.
    """

    TYPE: ClassVar["Type"] = _CYLINDRICAL_SOCKET

    wrapped: "Any"

    def __post_init__(self: "Self") -> None:
        """Override of the post initialisation magic method."""
        if not hasattr(self.wrapped, "reference_count"):
            self.wrapped.reference_count = 0

        self.wrapped.reference_count += 1

    @property
    def cast_to(self: "Self") -> "_Cast_CylindricalSocket":
        """Cast to another type.

        Returns:
            _Cast_CylindricalSocket
        """
        return _Cast_CylindricalSocket(self)
