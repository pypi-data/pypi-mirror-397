"""InterMountableComponentConnection"""

from __future__ import annotations

from typing import TYPE_CHECKING, ClassVar

from mastapy._private._internal.dataclasses import extended_dataclass
from mastapy._private._internal.exception_bridge import exception_bridge
from mastapy._private._internal.exceptions import CastException
from mastapy._private._internal.python_net import (
    python_net_import,
    pythonnet_property_get,
    pythonnet_property_set,
)
from mastapy._private._internal.type_enforcement import enforce_parameter_types

from mastapy._private._internal import utility
from mastapy._private.system_model.connections_and_sockets import _2531

_INTER_MOUNTABLE_COMPONENT_CONNECTION = python_net_import(
    "SMT.MastaAPI.SystemModel.ConnectionsAndSockets",
    "InterMountableComponentConnection",
)

if TYPE_CHECKING:
    from typing import Any, Type, TypeVar

    from mastapy._private.system_model import _2451
    from mastapy._private.system_model.connections_and_sockets import (
        _2527,
        _2532,
        _2551,
    )
    from mastapy._private.system_model.connections_and_sockets.couplings import (
        _2601,
        _2603,
        _2605,
        _2607,
        _2609,
        _2611,
    )
    from mastapy._private.system_model.connections_and_sockets.cycloidal import _2600
    from mastapy._private.system_model.connections_and_sockets.gears import (
        _2558,
        _2560,
        _2562,
        _2564,
        _2566,
        _2568,
        _2570,
        _2572,
        _2574,
        _2577,
        _2578,
        _2579,
        _2582,
        _2584,
        _2586,
        _2588,
        _2590,
    )

    Self = TypeVar("Self", bound="InterMountableComponentConnection")
    CastSelf = TypeVar(
        "CastSelf",
        bound="InterMountableComponentConnection._Cast_InterMountableComponentConnection",
    )


__docformat__ = "restructuredtext en"
__all__ = ("InterMountableComponentConnection",)


@extended_dataclass(frozen=True, slots=True, weakref_slot=True)
class _Cast_InterMountableComponentConnection:
    """Special nested class for casting InterMountableComponentConnection to subclasses."""

    __parent__: "InterMountableComponentConnection"

    @property
    def connection(self: "CastSelf") -> "_2531.Connection":
        return self.__parent__._cast(_2531.Connection)

    @property
    def design_entity(self: "CastSelf") -> "_2451.DesignEntity":
        from mastapy._private.system_model import _2451

        return self.__parent__._cast(_2451.DesignEntity)

    @property
    def belt_connection(self: "CastSelf") -> "_2527.BeltConnection":
        from mastapy._private.system_model.connections_and_sockets import _2527

        return self.__parent__._cast(_2527.BeltConnection)

    @property
    def cvt_belt_connection(self: "CastSelf") -> "_2532.CVTBeltConnection":
        from mastapy._private.system_model.connections_and_sockets import _2532

        return self.__parent__._cast(_2532.CVTBeltConnection)

    @property
    def rolling_ring_connection(self: "CastSelf") -> "_2551.RollingRingConnection":
        from mastapy._private.system_model.connections_and_sockets import _2551

        return self.__parent__._cast(_2551.RollingRingConnection)

    @property
    def agma_gleason_conical_gear_mesh(
        self: "CastSelf",
    ) -> "_2558.AGMAGleasonConicalGearMesh":
        from mastapy._private.system_model.connections_and_sockets.gears import _2558

        return self.__parent__._cast(_2558.AGMAGleasonConicalGearMesh)

    @property
    def bevel_differential_gear_mesh(
        self: "CastSelf",
    ) -> "_2560.BevelDifferentialGearMesh":
        from mastapy._private.system_model.connections_and_sockets.gears import _2560

        return self.__parent__._cast(_2560.BevelDifferentialGearMesh)

    @property
    def bevel_gear_mesh(self: "CastSelf") -> "_2562.BevelGearMesh":
        from mastapy._private.system_model.connections_and_sockets.gears import _2562

        return self.__parent__._cast(_2562.BevelGearMesh)

    @property
    def concept_gear_mesh(self: "CastSelf") -> "_2564.ConceptGearMesh":
        from mastapy._private.system_model.connections_and_sockets.gears import _2564

        return self.__parent__._cast(_2564.ConceptGearMesh)

    @property
    def conical_gear_mesh(self: "CastSelf") -> "_2566.ConicalGearMesh":
        from mastapy._private.system_model.connections_and_sockets.gears import _2566

        return self.__parent__._cast(_2566.ConicalGearMesh)

    @property
    def cylindrical_gear_mesh(self: "CastSelf") -> "_2568.CylindricalGearMesh":
        from mastapy._private.system_model.connections_and_sockets.gears import _2568

        return self.__parent__._cast(_2568.CylindricalGearMesh)

    @property
    def face_gear_mesh(self: "CastSelf") -> "_2570.FaceGearMesh":
        from mastapy._private.system_model.connections_and_sockets.gears import _2570

        return self.__parent__._cast(_2570.FaceGearMesh)

    @property
    def gear_mesh(self: "CastSelf") -> "_2572.GearMesh":
        from mastapy._private.system_model.connections_and_sockets.gears import _2572

        return self.__parent__._cast(_2572.GearMesh)

    @property
    def hypoid_gear_mesh(self: "CastSelf") -> "_2574.HypoidGearMesh":
        from mastapy._private.system_model.connections_and_sockets.gears import _2574

        return self.__parent__._cast(_2574.HypoidGearMesh)

    @property
    def klingelnberg_cyclo_palloid_conical_gear_mesh(
        self: "CastSelf",
    ) -> "_2577.KlingelnbergCycloPalloidConicalGearMesh":
        from mastapy._private.system_model.connections_and_sockets.gears import _2577

        return self.__parent__._cast(_2577.KlingelnbergCycloPalloidConicalGearMesh)

    @property
    def klingelnberg_cyclo_palloid_hypoid_gear_mesh(
        self: "CastSelf",
    ) -> "_2578.KlingelnbergCycloPalloidHypoidGearMesh":
        from mastapy._private.system_model.connections_and_sockets.gears import _2578

        return self.__parent__._cast(_2578.KlingelnbergCycloPalloidHypoidGearMesh)

    @property
    def klingelnberg_cyclo_palloid_spiral_bevel_gear_mesh(
        self: "CastSelf",
    ) -> "_2579.KlingelnbergCycloPalloidSpiralBevelGearMesh":
        from mastapy._private.system_model.connections_and_sockets.gears import _2579

        return self.__parent__._cast(_2579.KlingelnbergCycloPalloidSpiralBevelGearMesh)

    @property
    def spiral_bevel_gear_mesh(self: "CastSelf") -> "_2582.SpiralBevelGearMesh":
        from mastapy._private.system_model.connections_and_sockets.gears import _2582

        return self.__parent__._cast(_2582.SpiralBevelGearMesh)

    @property
    def straight_bevel_diff_gear_mesh(
        self: "CastSelf",
    ) -> "_2584.StraightBevelDiffGearMesh":
        from mastapy._private.system_model.connections_and_sockets.gears import _2584

        return self.__parent__._cast(_2584.StraightBevelDiffGearMesh)

    @property
    def straight_bevel_gear_mesh(self: "CastSelf") -> "_2586.StraightBevelGearMesh":
        from mastapy._private.system_model.connections_and_sockets.gears import _2586

        return self.__parent__._cast(_2586.StraightBevelGearMesh)

    @property
    def worm_gear_mesh(self: "CastSelf") -> "_2588.WormGearMesh":
        from mastapy._private.system_model.connections_and_sockets.gears import _2588

        return self.__parent__._cast(_2588.WormGearMesh)

    @property
    def zerol_bevel_gear_mesh(self: "CastSelf") -> "_2590.ZerolBevelGearMesh":
        from mastapy._private.system_model.connections_and_sockets.gears import _2590

        return self.__parent__._cast(_2590.ZerolBevelGearMesh)

    @property
    def ring_pins_to_disc_connection(
        self: "CastSelf",
    ) -> "_2600.RingPinsToDiscConnection":
        from mastapy._private.system_model.connections_and_sockets.cycloidal import (
            _2600,
        )

        return self.__parent__._cast(_2600.RingPinsToDiscConnection)

    @property
    def clutch_connection(self: "CastSelf") -> "_2601.ClutchConnection":
        from mastapy._private.system_model.connections_and_sockets.couplings import (
            _2601,
        )

        return self.__parent__._cast(_2601.ClutchConnection)

    @property
    def concept_coupling_connection(
        self: "CastSelf",
    ) -> "_2603.ConceptCouplingConnection":
        from mastapy._private.system_model.connections_and_sockets.couplings import (
            _2603,
        )

        return self.__parent__._cast(_2603.ConceptCouplingConnection)

    @property
    def coupling_connection(self: "CastSelf") -> "_2605.CouplingConnection":
        from mastapy._private.system_model.connections_and_sockets.couplings import (
            _2605,
        )

        return self.__parent__._cast(_2605.CouplingConnection)

    @property
    def part_to_part_shear_coupling_connection(
        self: "CastSelf",
    ) -> "_2607.PartToPartShearCouplingConnection":
        from mastapy._private.system_model.connections_and_sockets.couplings import (
            _2607,
        )

        return self.__parent__._cast(_2607.PartToPartShearCouplingConnection)

    @property
    def spring_damper_connection(self: "CastSelf") -> "_2609.SpringDamperConnection":
        from mastapy._private.system_model.connections_and_sockets.couplings import (
            _2609,
        )

        return self.__parent__._cast(_2609.SpringDamperConnection)

    @property
    def torque_converter_connection(
        self: "CastSelf",
    ) -> "_2611.TorqueConverterConnection":
        from mastapy._private.system_model.connections_and_sockets.couplings import (
            _2611,
        )

        return self.__parent__._cast(_2611.TorqueConverterConnection)

    @property
    def inter_mountable_component_connection(
        self: "CastSelf",
    ) -> "InterMountableComponentConnection":
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
class InterMountableComponentConnection(_2531.Connection):
    """InterMountableComponentConnection

    This is a mastapy class.
    """

    TYPE: ClassVar["Type"] = _INTER_MOUNTABLE_COMPONENT_CONNECTION

    wrapped: "Any"

    def __post_init__(self: "Self") -> None:
        """Override of the post initialisation magic method."""
        if not hasattr(self.wrapped, "reference_count"):
            self.wrapped.reference_count = 0

        self.wrapped.reference_count += 1

    @property
    @exception_bridge
    def additional_modal_damping_ratio(self: "Self") -> "float":
        """float"""
        temp = pythonnet_property_get(self.wrapped, "AdditionalModalDampingRatio")

        if temp is None:
            return 0.0

        return temp

    @additional_modal_damping_ratio.setter
    @exception_bridge
    @enforce_parameter_types
    def additional_modal_damping_ratio(self: "Self", value: "float") -> None:
        pythonnet_property_set(
            self.wrapped,
            "AdditionalModalDampingRatio",
            float(value) if value is not None else 0.0,
        )

    @property
    def cast_to(self: "Self") -> "_Cast_InterMountableComponentConnection":
        """Cast to another type.

        Returns:
            _Cast_InterMountableComponentConnection
        """
        return _Cast_InterMountableComponentConnection(self)
