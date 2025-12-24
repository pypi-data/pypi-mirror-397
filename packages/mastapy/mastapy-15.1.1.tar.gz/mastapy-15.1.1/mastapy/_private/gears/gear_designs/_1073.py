"""GearDesign"""

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

from mastapy._private._internal import constructor, utility
from mastapy._private.gears.gear_designs import _1074

_GEAR_DESIGN = python_net_import("SMT.MastaAPI.Gears.GearDesigns", "GearDesign")

if TYPE_CHECKING:
    from typing import Any, Type, TypeVar

    from mastapy._private.gears.fe_model import _1343
    from mastapy._private.gears.gear_designs.agma_gleason_conical import _1339
    from mastapy._private.gears.gear_designs.bevel import _1326
    from mastapy._private.gears.gear_designs.concept import _1322
    from mastapy._private.gears.gear_designs.conical import _1300
    from mastapy._private.gears.gear_designs.cylindrical import _1144, _1174
    from mastapy._private.gears.gear_designs.face import _1115, _1120, _1123
    from mastapy._private.gears.gear_designs.hypoid import _1111
    from mastapy._private.gears.gear_designs.klingelnberg_conical import _1107
    from mastapy._private.gears.gear_designs.klingelnberg_hypoid import _1103
    from mastapy._private.gears.gear_designs.klingelnberg_spiral_bevel import _1099
    from mastapy._private.gears.gear_designs.spiral_bevel import _1095
    from mastapy._private.gears.gear_designs.straight_bevel import _1087
    from mastapy._private.gears.gear_designs.straight_bevel_diff import _1091
    from mastapy._private.gears.gear_designs.worm import _1082, _1083, _1086
    from mastapy._private.gears.gear_designs.zerol_bevel import _1078

    Self = TypeVar("Self", bound="GearDesign")
    CastSelf = TypeVar("CastSelf", bound="GearDesign._Cast_GearDesign")


__docformat__ = "restructuredtext en"
__all__ = ("GearDesign",)


@extended_dataclass(frozen=True, slots=True, weakref_slot=True)
class _Cast_GearDesign:
    """Special nested class for casting GearDesign to subclasses."""

    __parent__: "GearDesign"

    @property
    def gear_design_component(self: "CastSelf") -> "_1074.GearDesignComponent":
        return self.__parent__._cast(_1074.GearDesignComponent)

    @property
    def zerol_bevel_gear_design(self: "CastSelf") -> "_1078.ZerolBevelGearDesign":
        from mastapy._private.gears.gear_designs.zerol_bevel import _1078

        return self.__parent__._cast(_1078.ZerolBevelGearDesign)

    @property
    def worm_design(self: "CastSelf") -> "_1082.WormDesign":
        from mastapy._private.gears.gear_designs.worm import _1082

        return self.__parent__._cast(_1082.WormDesign)

    @property
    def worm_gear_design(self: "CastSelf") -> "_1083.WormGearDesign":
        from mastapy._private.gears.gear_designs.worm import _1083

        return self.__parent__._cast(_1083.WormGearDesign)

    @property
    def worm_wheel_design(self: "CastSelf") -> "_1086.WormWheelDesign":
        from mastapy._private.gears.gear_designs.worm import _1086

        return self.__parent__._cast(_1086.WormWheelDesign)

    @property
    def straight_bevel_gear_design(self: "CastSelf") -> "_1087.StraightBevelGearDesign":
        from mastapy._private.gears.gear_designs.straight_bevel import _1087

        return self.__parent__._cast(_1087.StraightBevelGearDesign)

    @property
    def straight_bevel_diff_gear_design(
        self: "CastSelf",
    ) -> "_1091.StraightBevelDiffGearDesign":
        from mastapy._private.gears.gear_designs.straight_bevel_diff import _1091

        return self.__parent__._cast(_1091.StraightBevelDiffGearDesign)

    @property
    def spiral_bevel_gear_design(self: "CastSelf") -> "_1095.SpiralBevelGearDesign":
        from mastapy._private.gears.gear_designs.spiral_bevel import _1095

        return self.__parent__._cast(_1095.SpiralBevelGearDesign)

    @property
    def klingelnberg_cyclo_palloid_spiral_bevel_gear_design(
        self: "CastSelf",
    ) -> "_1099.KlingelnbergCycloPalloidSpiralBevelGearDesign":
        from mastapy._private.gears.gear_designs.klingelnberg_spiral_bevel import _1099

        return self.__parent__._cast(
            _1099.KlingelnbergCycloPalloidSpiralBevelGearDesign
        )

    @property
    def klingelnberg_cyclo_palloid_hypoid_gear_design(
        self: "CastSelf",
    ) -> "_1103.KlingelnbergCycloPalloidHypoidGearDesign":
        from mastapy._private.gears.gear_designs.klingelnberg_hypoid import _1103

        return self.__parent__._cast(_1103.KlingelnbergCycloPalloidHypoidGearDesign)

    @property
    def klingelnberg_conical_gear_design(
        self: "CastSelf",
    ) -> "_1107.KlingelnbergConicalGearDesign":
        from mastapy._private.gears.gear_designs.klingelnberg_conical import _1107

        return self.__parent__._cast(_1107.KlingelnbergConicalGearDesign)

    @property
    def hypoid_gear_design(self: "CastSelf") -> "_1111.HypoidGearDesign":
        from mastapy._private.gears.gear_designs.hypoid import _1111

        return self.__parent__._cast(_1111.HypoidGearDesign)

    @property
    def face_gear_design(self: "CastSelf") -> "_1115.FaceGearDesign":
        from mastapy._private.gears.gear_designs.face import _1115

        return self.__parent__._cast(_1115.FaceGearDesign)

    @property
    def face_gear_pinion_design(self: "CastSelf") -> "_1120.FaceGearPinionDesign":
        from mastapy._private.gears.gear_designs.face import _1120

        return self.__parent__._cast(_1120.FaceGearPinionDesign)

    @property
    def face_gear_wheel_design(self: "CastSelf") -> "_1123.FaceGearWheelDesign":
        from mastapy._private.gears.gear_designs.face import _1123

        return self.__parent__._cast(_1123.FaceGearWheelDesign)

    @property
    def cylindrical_gear_design(self: "CastSelf") -> "_1144.CylindricalGearDesign":
        from mastapy._private.gears.gear_designs.cylindrical import _1144

        return self.__parent__._cast(_1144.CylindricalGearDesign)

    @property
    def cylindrical_planet_gear_design(
        self: "CastSelf",
    ) -> "_1174.CylindricalPlanetGearDesign":
        from mastapy._private.gears.gear_designs.cylindrical import _1174

        return self.__parent__._cast(_1174.CylindricalPlanetGearDesign)

    @property
    def conical_gear_design(self: "CastSelf") -> "_1300.ConicalGearDesign":
        from mastapy._private.gears.gear_designs.conical import _1300

        return self.__parent__._cast(_1300.ConicalGearDesign)

    @property
    def concept_gear_design(self: "CastSelf") -> "_1322.ConceptGearDesign":
        from mastapy._private.gears.gear_designs.concept import _1322

        return self.__parent__._cast(_1322.ConceptGearDesign)

    @property
    def bevel_gear_design(self: "CastSelf") -> "_1326.BevelGearDesign":
        from mastapy._private.gears.gear_designs.bevel import _1326

        return self.__parent__._cast(_1326.BevelGearDesign)

    @property
    def agma_gleason_conical_gear_design(
        self: "CastSelf",
    ) -> "_1339.AGMAGleasonConicalGearDesign":
        from mastapy._private.gears.gear_designs.agma_gleason_conical import _1339

        return self.__parent__._cast(_1339.AGMAGleasonConicalGearDesign)

    @property
    def gear_design(self: "CastSelf") -> "GearDesign":
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
class GearDesign(_1074.GearDesignComponent):
    """GearDesign

    This is a mastapy class.
    """

    TYPE: ClassVar["Type"] = _GEAR_DESIGN

    wrapped: "Any"

    def __post_init__(self: "Self") -> None:
        """Override of the post initialisation magic method."""
        if not hasattr(self.wrapped, "reference_count"):
            self.wrapped.reference_count = 0

        self.wrapped.reference_count += 1

    @property
    @exception_bridge
    def absolute_shaft_inner_diameter(self: "Self") -> "float":
        """float

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "AbsoluteShaftInnerDiameter")

        if temp is None:
            return 0.0

        return temp

    @property
    @exception_bridge
    def face_width(self: "Self") -> "float":
        """float"""
        temp = pythonnet_property_get(self.wrapped, "FaceWidth")

        if temp is None:
            return 0.0

        return temp

    @face_width.setter
    @exception_bridge
    @enforce_parameter_types
    def face_width(self: "Self", value: "float") -> None:
        pythonnet_property_set(
            self.wrapped, "FaceWidth", float(value) if value is not None else 0.0
        )

    @property
    @exception_bridge
    def mass(self: "Self") -> "float":
        """float

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "Mass")

        if temp is None:
            return 0.0

        return temp

    @property
    @exception_bridge
    def name(self: "Self") -> "str":
        """str

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "Name")

        if temp is None:
            return ""

        return temp

    @property
    @exception_bridge
    def names_of_meshing_gears(self: "Self") -> "str":
        """str

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "NamesOfMeshingGears")

        if temp is None:
            return ""

        return temp

    @property
    @exception_bridge
    def number_of_teeth(self: "Self") -> "int":
        """int"""
        temp = pythonnet_property_get(self.wrapped, "NumberOfTeeth")

        if temp is None:
            return 0

        return temp

    @number_of_teeth.setter
    @exception_bridge
    @enforce_parameter_types
    def number_of_teeth(self: "Self", value: "int") -> None:
        pythonnet_property_set(
            self.wrapped, "NumberOfTeeth", int(value) if value is not None else 0
        )

    @property
    @exception_bridge
    def number_of_teeth_maintaining_ratio(self: "Self") -> "int":
        """int"""
        temp = pythonnet_property_get(self.wrapped, "NumberOfTeethMaintainingRatio")

        if temp is None:
            return 0

        return temp

    @number_of_teeth_maintaining_ratio.setter
    @exception_bridge
    @enforce_parameter_types
    def number_of_teeth_maintaining_ratio(self: "Self", value: "int") -> None:
        pythonnet_property_set(
            self.wrapped,
            "NumberOfTeethMaintainingRatio",
            int(value) if value is not None else 0,
        )

    @property
    @exception_bridge
    def shaft_inner_diameter(self: "Self") -> "float":
        """float

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "ShaftInnerDiameter")

        if temp is None:
            return 0.0

        return temp

    @property
    @exception_bridge
    def shaft_outer_diameter(self: "Self") -> "float":
        """float

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "ShaftOuterDiameter")

        if temp is None:
            return 0.0

        return temp

    @property
    @exception_bridge
    def tifffe_model(self: "Self") -> "_1343.GearFEModel":
        """mastapy.gears.fe_model.GearFEModel

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "TIFFFEModel")

        if temp is None:
            return None

        type_ = temp.GetType()
        return constructor.new(type_.Namespace, type_.Name)(temp)

    @property
    def cast_to(self: "Self") -> "_Cast_GearDesign":
        """Cast to another type.

        Returns:
            _Cast_GearDesign
        """
        return _Cast_GearDesign(self)
