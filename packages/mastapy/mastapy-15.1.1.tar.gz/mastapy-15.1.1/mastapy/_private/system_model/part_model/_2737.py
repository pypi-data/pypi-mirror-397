"""MountableComponent"""

from __future__ import annotations

from typing import TYPE_CHECKING, ClassVar

from mastapy._private._internal.dataclasses import extended_dataclass
from mastapy._private._internal.exception_bridge import exception_bridge
from mastapy._private._internal.exceptions import CastException
from mastapy._private._internal.python_net import (
    python_net_import,
    pythonnet_method_call,
    pythonnet_property_get,
    pythonnet_property_set,
)
from mastapy._private._internal.type_enforcement import enforce_parameter_types

from mastapy._private._internal import constructor, utility
from mastapy._private.system_model.part_model import _2714

_MOUNTABLE_COMPONENT = python_net_import(
    "SMT.MastaAPI.SystemModel.PartModel", "MountableComponent"
)

if TYPE_CHECKING:
    from typing import Any, Type, TypeVar

    from mastapy._private.system_model import _2451
    from mastapy._private.system_model.connections_and_sockets import (
        _2528,
        _2531,
        _2535,
    )
    from mastapy._private.system_model.part_model import (
        _2704,
        _2708,
        _2715,
        _2717,
        _2733,
        _2734,
        _2739,
        _2742,
        _2744,
        _2746,
        _2747,
        _2753,
        _2755,
    )
    from mastapy._private.system_model.part_model.couplings import (
        _2862,
        _2865,
        _2868,
        _2871,
        _2873,
        _2875,
        _2882,
        _2884,
        _2891,
        _2894,
        _2895,
        _2896,
        _2898,
        _2900,
    )
    from mastapy._private.system_model.part_model.cycloidal import _2852
    from mastapy._private.system_model.part_model.gears import (
        _2794,
        _2796,
        _2798,
        _2799,
        _2800,
        _2802,
        _2804,
        _2806,
        _2808,
        _2809,
        _2811,
        _2815,
        _2817,
        _2819,
        _2821,
        _2825,
        _2827,
        _2829,
        _2831,
        _2832,
        _2833,
        _2835,
    )

    Self = TypeVar("Self", bound="MountableComponent")
    CastSelf = TypeVar("CastSelf", bound="MountableComponent._Cast_MountableComponent")


__docformat__ = "restructuredtext en"
__all__ = ("MountableComponent",)


@extended_dataclass(frozen=True, slots=True, weakref_slot=True)
class _Cast_MountableComponent:
    """Special nested class for casting MountableComponent to subclasses."""

    __parent__: "MountableComponent"

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
    def connector(self: "CastSelf") -> "_2717.Connector":
        from mastapy._private.system_model.part_model import _2717

        return self.__parent__._cast(_2717.Connector)

    @property
    def mass_disc(self: "CastSelf") -> "_2733.MassDisc":
        from mastapy._private.system_model.part_model import _2733

        return self.__parent__._cast(_2733.MassDisc)

    @property
    def measurement_component(self: "CastSelf") -> "_2734.MeasurementComponent":
        from mastapy._private.system_model.part_model import _2734

        return self.__parent__._cast(_2734.MeasurementComponent)

    @property
    def oil_seal(self: "CastSelf") -> "_2739.OilSeal":
        from mastapy._private.system_model.part_model import _2739

        return self.__parent__._cast(_2739.OilSeal)

    @property
    def planet_carrier(self: "CastSelf") -> "_2744.PlanetCarrier":
        from mastapy._private.system_model.part_model import _2744

        return self.__parent__._cast(_2744.PlanetCarrier)

    @property
    def point_load(self: "CastSelf") -> "_2746.PointLoad":
        from mastapy._private.system_model.part_model import _2746

        return self.__parent__._cast(_2746.PointLoad)

    @property
    def power_load(self: "CastSelf") -> "_2747.PowerLoad":
        from mastapy._private.system_model.part_model import _2747

        return self.__parent__._cast(_2747.PowerLoad)

    @property
    def unbalanced_mass(self: "CastSelf") -> "_2753.UnbalancedMass":
        from mastapy._private.system_model.part_model import _2753

        return self.__parent__._cast(_2753.UnbalancedMass)

    @property
    def virtual_component(self: "CastSelf") -> "_2755.VirtualComponent":
        from mastapy._private.system_model.part_model import _2755

        return self.__parent__._cast(_2755.VirtualComponent)

    @property
    def agma_gleason_conical_gear(self: "CastSelf") -> "_2794.AGMAGleasonConicalGear":
        from mastapy._private.system_model.part_model.gears import _2794

        return self.__parent__._cast(_2794.AGMAGleasonConicalGear)

    @property
    def bevel_differential_gear(self: "CastSelf") -> "_2796.BevelDifferentialGear":
        from mastapy._private.system_model.part_model.gears import _2796

        return self.__parent__._cast(_2796.BevelDifferentialGear)

    @property
    def bevel_differential_planet_gear(
        self: "CastSelf",
    ) -> "_2798.BevelDifferentialPlanetGear":
        from mastapy._private.system_model.part_model.gears import _2798

        return self.__parent__._cast(_2798.BevelDifferentialPlanetGear)

    @property
    def bevel_differential_sun_gear(
        self: "CastSelf",
    ) -> "_2799.BevelDifferentialSunGear":
        from mastapy._private.system_model.part_model.gears import _2799

        return self.__parent__._cast(_2799.BevelDifferentialSunGear)

    @property
    def bevel_gear(self: "CastSelf") -> "_2800.BevelGear":
        from mastapy._private.system_model.part_model.gears import _2800

        return self.__parent__._cast(_2800.BevelGear)

    @property
    def concept_gear(self: "CastSelf") -> "_2802.ConceptGear":
        from mastapy._private.system_model.part_model.gears import _2802

        return self.__parent__._cast(_2802.ConceptGear)

    @property
    def conical_gear(self: "CastSelf") -> "_2804.ConicalGear":
        from mastapy._private.system_model.part_model.gears import _2804

        return self.__parent__._cast(_2804.ConicalGear)

    @property
    def cylindrical_gear(self: "CastSelf") -> "_2806.CylindricalGear":
        from mastapy._private.system_model.part_model.gears import _2806

        return self.__parent__._cast(_2806.CylindricalGear)

    @property
    def cylindrical_planet_gear(self: "CastSelf") -> "_2808.CylindricalPlanetGear":
        from mastapy._private.system_model.part_model.gears import _2808

        return self.__parent__._cast(_2808.CylindricalPlanetGear)

    @property
    def face_gear(self: "CastSelf") -> "_2809.FaceGear":
        from mastapy._private.system_model.part_model.gears import _2809

        return self.__parent__._cast(_2809.FaceGear)

    @property
    def gear(self: "CastSelf") -> "_2811.Gear":
        from mastapy._private.system_model.part_model.gears import _2811

        return self.__parent__._cast(_2811.Gear)

    @property
    def hypoid_gear(self: "CastSelf") -> "_2815.HypoidGear":
        from mastapy._private.system_model.part_model.gears import _2815

        return self.__parent__._cast(_2815.HypoidGear)

    @property
    def klingelnberg_cyclo_palloid_conical_gear(
        self: "CastSelf",
    ) -> "_2817.KlingelnbergCycloPalloidConicalGear":
        from mastapy._private.system_model.part_model.gears import _2817

        return self.__parent__._cast(_2817.KlingelnbergCycloPalloidConicalGear)

    @property
    def klingelnberg_cyclo_palloid_hypoid_gear(
        self: "CastSelf",
    ) -> "_2819.KlingelnbergCycloPalloidHypoidGear":
        from mastapy._private.system_model.part_model.gears import _2819

        return self.__parent__._cast(_2819.KlingelnbergCycloPalloidHypoidGear)

    @property
    def klingelnberg_cyclo_palloid_spiral_bevel_gear(
        self: "CastSelf",
    ) -> "_2821.KlingelnbergCycloPalloidSpiralBevelGear":
        from mastapy._private.system_model.part_model.gears import _2821

        return self.__parent__._cast(_2821.KlingelnbergCycloPalloidSpiralBevelGear)

    @property
    def spiral_bevel_gear(self: "CastSelf") -> "_2825.SpiralBevelGear":
        from mastapy._private.system_model.part_model.gears import _2825

        return self.__parent__._cast(_2825.SpiralBevelGear)

    @property
    def straight_bevel_diff_gear(self: "CastSelf") -> "_2827.StraightBevelDiffGear":
        from mastapy._private.system_model.part_model.gears import _2827

        return self.__parent__._cast(_2827.StraightBevelDiffGear)

    @property
    def straight_bevel_gear(self: "CastSelf") -> "_2829.StraightBevelGear":
        from mastapy._private.system_model.part_model.gears import _2829

        return self.__parent__._cast(_2829.StraightBevelGear)

    @property
    def straight_bevel_planet_gear(self: "CastSelf") -> "_2831.StraightBevelPlanetGear":
        from mastapy._private.system_model.part_model.gears import _2831

        return self.__parent__._cast(_2831.StraightBevelPlanetGear)

    @property
    def straight_bevel_sun_gear(self: "CastSelf") -> "_2832.StraightBevelSunGear":
        from mastapy._private.system_model.part_model.gears import _2832

        return self.__parent__._cast(_2832.StraightBevelSunGear)

    @property
    def worm_gear(self: "CastSelf") -> "_2833.WormGear":
        from mastapy._private.system_model.part_model.gears import _2833

        return self.__parent__._cast(_2833.WormGear)

    @property
    def zerol_bevel_gear(self: "CastSelf") -> "_2835.ZerolBevelGear":
        from mastapy._private.system_model.part_model.gears import _2835

        return self.__parent__._cast(_2835.ZerolBevelGear)

    @property
    def ring_pins(self: "CastSelf") -> "_2852.RingPins":
        from mastapy._private.system_model.part_model.cycloidal import _2852

        return self.__parent__._cast(_2852.RingPins)

    @property
    def clutch_half(self: "CastSelf") -> "_2862.ClutchHalf":
        from mastapy._private.system_model.part_model.couplings import _2862

        return self.__parent__._cast(_2862.ClutchHalf)

    @property
    def concept_coupling_half(self: "CastSelf") -> "_2865.ConceptCouplingHalf":
        from mastapy._private.system_model.part_model.couplings import _2865

        return self.__parent__._cast(_2865.ConceptCouplingHalf)

    @property
    def coupling_half(self: "CastSelf") -> "_2868.CouplingHalf":
        from mastapy._private.system_model.part_model.couplings import _2868

        return self.__parent__._cast(_2868.CouplingHalf)

    @property
    def cvt_pulley(self: "CastSelf") -> "_2871.CVTPulley":
        from mastapy._private.system_model.part_model.couplings import _2871

        return self.__parent__._cast(_2871.CVTPulley)

    @property
    def part_to_part_shear_coupling_half(
        self: "CastSelf",
    ) -> "_2873.PartToPartShearCouplingHalf":
        from mastapy._private.system_model.part_model.couplings import _2873

        return self.__parent__._cast(_2873.PartToPartShearCouplingHalf)

    @property
    def pulley(self: "CastSelf") -> "_2875.Pulley":
        from mastapy._private.system_model.part_model.couplings import _2875

        return self.__parent__._cast(_2875.Pulley)

    @property
    def rolling_ring(self: "CastSelf") -> "_2882.RollingRing":
        from mastapy._private.system_model.part_model.couplings import _2882

        return self.__parent__._cast(_2882.RollingRing)

    @property
    def shaft_hub_connection(self: "CastSelf") -> "_2884.ShaftHubConnection":
        from mastapy._private.system_model.part_model.couplings import _2884

        return self.__parent__._cast(_2884.ShaftHubConnection)

    @property
    def spring_damper_half(self: "CastSelf") -> "_2891.SpringDamperHalf":
        from mastapy._private.system_model.part_model.couplings import _2891

        return self.__parent__._cast(_2891.SpringDamperHalf)

    @property
    def synchroniser_half(self: "CastSelf") -> "_2894.SynchroniserHalf":
        from mastapy._private.system_model.part_model.couplings import _2894

        return self.__parent__._cast(_2894.SynchroniserHalf)

    @property
    def synchroniser_part(self: "CastSelf") -> "_2895.SynchroniserPart":
        from mastapy._private.system_model.part_model.couplings import _2895

        return self.__parent__._cast(_2895.SynchroniserPart)

    @property
    def synchroniser_sleeve(self: "CastSelf") -> "_2896.SynchroniserSleeve":
        from mastapy._private.system_model.part_model.couplings import _2896

        return self.__parent__._cast(_2896.SynchroniserSleeve)

    @property
    def torque_converter_pump(self: "CastSelf") -> "_2898.TorqueConverterPump":
        from mastapy._private.system_model.part_model.couplings import _2898

        return self.__parent__._cast(_2898.TorqueConverterPump)

    @property
    def torque_converter_turbine(self: "CastSelf") -> "_2900.TorqueConverterTurbine":
        from mastapy._private.system_model.part_model.couplings import _2900

        return self.__parent__._cast(_2900.TorqueConverterTurbine)

    @property
    def mountable_component(self: "CastSelf") -> "MountableComponent":
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
class MountableComponent(_2714.Component):
    """MountableComponent

    This is a mastapy class.
    """

    TYPE: ClassVar["Type"] = _MOUNTABLE_COMPONENT

    wrapped: "Any"

    def __post_init__(self: "Self") -> None:
        """Override of the post initialisation magic method."""
        if not hasattr(self.wrapped, "reference_count"):
            self.wrapped.reference_count = 0

        self.wrapped.reference_count += 1

    @property
    @exception_bridge
    def rotation_about_axis(self: "Self") -> "float":
        """float"""
        temp = pythonnet_property_get(self.wrapped, "RotationAboutAxis")

        if temp is None:
            return 0.0

        return temp

    @rotation_about_axis.setter
    @exception_bridge
    @enforce_parameter_types
    def rotation_about_axis(self: "Self", value: "float") -> None:
        pythonnet_property_set(
            self.wrapped,
            "RotationAboutAxis",
            float(value) if value is not None else 0.0,
        )

    @property
    @exception_bridge
    def inner_component(self: "Self") -> "_2704.AbstractShaft":
        """mastapy.system_model.part_model.AbstractShaft

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "InnerComponent")

        if temp is None:
            return None

        type_ = temp.GetType()
        return constructor.new(type_.Namespace, type_.Name)(temp)

    @property
    @exception_bridge
    def inner_connection(self: "Self") -> "_2531.Connection":
        """mastapy.system_model.connections_and_sockets.Connection

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "InnerConnection")

        if temp is None:
            return None

        type_ = temp.GetType()
        return constructor.new(type_.Namespace, type_.Name)(temp)

    @property
    @exception_bridge
    def inner_socket(self: "Self") -> "_2535.CylindricalSocket":
        """mastapy.system_model.connections_and_sockets.CylindricalSocket

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "InnerSocket")

        if temp is None:
            return None

        type_ = temp.GetType()
        return constructor.new(type_.Namespace, type_.Name)(temp)

    @property
    @exception_bridge
    def is_mounted(self: "Self") -> "bool":
        """bool

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "IsMounted")

        if temp is None:
            return False

        return temp

    @exception_bridge
    @enforce_parameter_types
    def mount_on(
        self: "Self", shaft: "_2704.AbstractShaft", offset: "float" = float("nan")
    ) -> "_2528.CoaxialConnection":
        """mastapy.system_model.connections_and_sockets.CoaxialConnection

        Args:
            shaft (mastapy.system_model.part_model.AbstractShaft)
            offset (float, optional)
        """
        offset = float(offset)
        method_result = pythonnet_method_call(
            self.wrapped,
            "MountOn",
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
    def try_mount_on(
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
            "TryMountOn",
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
    def cast_to(self: "Self") -> "_Cast_MountableComponent":
        """Cast to another type.

        Returns:
            _Cast_MountableComponent
        """
        return _Cast_MountableComponent(self)
