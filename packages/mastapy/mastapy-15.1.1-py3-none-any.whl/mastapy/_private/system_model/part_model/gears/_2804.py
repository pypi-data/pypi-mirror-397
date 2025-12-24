"""ConicalGear"""

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

from mastapy._private._internal import constructor, conversion, utility
from mastapy._private.system_model.part_model.gears import _2811

_CONICAL_GEAR = python_net_import(
    "SMT.MastaAPI.SystemModel.PartModel.Gears", "ConicalGear"
)

if TYPE_CHECKING:
    from typing import Any, Type, TypeVar

    from mastapy._private.gears.gear_designs.conical import _1300
    from mastapy._private.system_model import _2451
    from mastapy._private.system_model.part_model import _2714, _2737, _2742
    from mastapy._private.system_model.part_model.gears import (
        _2794,
        _2796,
        _2798,
        _2799,
        _2800,
        _2812,
        _2815,
        _2817,
        _2819,
        _2821,
        _2825,
        _2827,
        _2829,
        _2831,
        _2832,
        _2835,
    )

    Self = TypeVar("Self", bound="ConicalGear")
    CastSelf = TypeVar("CastSelf", bound="ConicalGear._Cast_ConicalGear")


__docformat__ = "restructuredtext en"
__all__ = ("ConicalGear",)


@extended_dataclass(frozen=True, slots=True, weakref_slot=True)
class _Cast_ConicalGear:
    """Special nested class for casting ConicalGear to subclasses."""

    __parent__: "ConicalGear"

    @property
    def gear(self: "CastSelf") -> "_2811.Gear":
        return self.__parent__._cast(_2811.Gear)

    @property
    def mountable_component(self: "CastSelf") -> "_2737.MountableComponent":
        from mastapy._private.system_model.part_model import _2737

        return self.__parent__._cast(_2737.MountableComponent)

    @property
    def component(self: "CastSelf") -> "_2714.Component":
        from mastapy._private.system_model.part_model import _2714

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
    def zerol_bevel_gear(self: "CastSelf") -> "_2835.ZerolBevelGear":
        from mastapy._private.system_model.part_model.gears import _2835

        return self.__parent__._cast(_2835.ZerolBevelGear)

    @property
    def conical_gear(self: "CastSelf") -> "ConicalGear":
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
class ConicalGear(_2811.Gear):
    """ConicalGear

    This is a mastapy class.
    """

    TYPE: ClassVar["Type"] = _CONICAL_GEAR

    wrapped: "Any"

    def __post_init__(self: "Self") -> None:
        """Override of the post initialisation magic method."""
        if not hasattr(self.wrapped, "reference_count"):
            self.wrapped.reference_count = 0

        self.wrapped.reference_count += 1

    @property
    @exception_bridge
    def length(self: "Self") -> "float":
        """float

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "Length")

        if temp is None:
            return 0.0

        return temp

    @property
    @exception_bridge
    def orientation(self: "Self") -> "_2812.GearOrientations":
        """mastapy.system_model.part_model.gears.GearOrientations"""
        temp = pythonnet_property_get(self.wrapped, "Orientation")

        if temp is None:
            return None

        value = conversion.pn_to_mp_enum(
            temp, "SMT.MastaAPI.SystemModel.PartModel.Gears.GearOrientations"
        )

        if value is None:
            return None

        return constructor.new_from_mastapy(
            "mastapy._private.system_model.part_model.gears._2812", "GearOrientations"
        )(value)

    @orientation.setter
    @exception_bridge
    @enforce_parameter_types
    def orientation(self: "Self", value: "_2812.GearOrientations") -> None:
        value = conversion.mp_to_pn_enum(
            value, "SMT.MastaAPI.SystemModel.PartModel.Gears.GearOrientations"
        )
        pythonnet_property_set(self.wrapped, "Orientation", value)

    @property
    @exception_bridge
    def active_gear_design(self: "Self") -> "_1300.ConicalGearDesign":
        """mastapy.gears.gear_designs.conical.ConicalGearDesign

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "ActiveGearDesign")

        if temp is None:
            return None

        type_ = temp.GetType()
        return constructor.new(type_.Namespace, type_.Name)(temp)

    @property
    @exception_bridge
    def conical_gear_design(self: "Self") -> "_1300.ConicalGearDesign":
        """mastapy.gears.gear_designs.conical.ConicalGearDesign

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "ConicalGearDesign")

        if temp is None:
            return None

        type_ = temp.GetType()
        return constructor.new(type_.Namespace, type_.Name)(temp)

    @property
    def cast_to(self: "Self") -> "_Cast_ConicalGear":
        """Cast to another type.

        Returns:
            _Cast_ConicalGear
        """
        return _Cast_ConicalGear(self)
