"""ConicalGearSetDesign"""

from __future__ import annotations

from typing import TYPE_CHECKING, ClassVar

from mastapy._private._internal.dataclasses import extended_dataclass
from mastapy._private._internal.exception_bridge import exception_bridge
from mastapy._private._internal.exceptions import CastException
from mastapy._private._internal.list_with_selected_item import (
    promote_to_list_with_selected_item,
)
from mastapy._private._internal.python_net import (
    python_net_import,
    pythonnet_property_get,
    pythonnet_property_set,
)
from mastapy._private._internal.sentinels import ListWithSelectedItem_None
from mastapy._private._internal.type_enforcement import enforce_parameter_types

from mastapy._private._internal import constructor, conversion, utility
from mastapy._private._internal.implicit import list_with_selected_item
from mastapy._private.gears.gear_designs import _1076

_CONICAL_GEAR_SET_DESIGN = python_net_import(
    "SMT.MastaAPI.Gears.GearDesigns.Conical", "ConicalGearSetDesign"
)

if TYPE_CHECKING:
    from typing import Any, List, Type, TypeVar

    from mastapy._private.gears.gear_designs import _1074
    from mastapy._private.gears.gear_designs.agma_gleason_conical import _1341
    from mastapy._private.gears.gear_designs.bevel import _1328
    from mastapy._private.gears.gear_designs.conical import _1301
    from mastapy._private.gears.gear_designs.hypoid import _1113
    from mastapy._private.gears.gear_designs.klingelnberg_conical import _1109
    from mastapy._private.gears.gear_designs.klingelnberg_hypoid import _1105
    from mastapy._private.gears.gear_designs.klingelnberg_spiral_bevel import _1101
    from mastapy._private.gears.gear_designs.spiral_bevel import _1097
    from mastapy._private.gears.gear_designs.straight_bevel import _1089
    from mastapy._private.gears.gear_designs.straight_bevel_diff import _1093
    from mastapy._private.gears.gear_designs.zerol_bevel import _1080

    Self = TypeVar("Self", bound="ConicalGearSetDesign")
    CastSelf = TypeVar(
        "CastSelf", bound="ConicalGearSetDesign._Cast_ConicalGearSetDesign"
    )


__docformat__ = "restructuredtext en"
__all__ = ("ConicalGearSetDesign",)


@extended_dataclass(frozen=True, slots=True, weakref_slot=True)
class _Cast_ConicalGearSetDesign:
    """Special nested class for casting ConicalGearSetDesign to subclasses."""

    __parent__: "ConicalGearSetDesign"

    @property
    def gear_set_design(self: "CastSelf") -> "_1076.GearSetDesign":
        return self.__parent__._cast(_1076.GearSetDesign)

    @property
    def gear_design_component(self: "CastSelf") -> "_1074.GearDesignComponent":
        from mastapy._private.gears.gear_designs import _1074

        return self.__parent__._cast(_1074.GearDesignComponent)

    @property
    def zerol_bevel_gear_set_design(
        self: "CastSelf",
    ) -> "_1080.ZerolBevelGearSetDesign":
        from mastapy._private.gears.gear_designs.zerol_bevel import _1080

        return self.__parent__._cast(_1080.ZerolBevelGearSetDesign)

    @property
    def straight_bevel_gear_set_design(
        self: "CastSelf",
    ) -> "_1089.StraightBevelGearSetDesign":
        from mastapy._private.gears.gear_designs.straight_bevel import _1089

        return self.__parent__._cast(_1089.StraightBevelGearSetDesign)

    @property
    def straight_bevel_diff_gear_set_design(
        self: "CastSelf",
    ) -> "_1093.StraightBevelDiffGearSetDesign":
        from mastapy._private.gears.gear_designs.straight_bevel_diff import _1093

        return self.__parent__._cast(_1093.StraightBevelDiffGearSetDesign)

    @property
    def spiral_bevel_gear_set_design(
        self: "CastSelf",
    ) -> "_1097.SpiralBevelGearSetDesign":
        from mastapy._private.gears.gear_designs.spiral_bevel import _1097

        return self.__parent__._cast(_1097.SpiralBevelGearSetDesign)

    @property
    def klingelnberg_cyclo_palloid_spiral_bevel_gear_set_design(
        self: "CastSelf",
    ) -> "_1101.KlingelnbergCycloPalloidSpiralBevelGearSetDesign":
        from mastapy._private.gears.gear_designs.klingelnberg_spiral_bevel import _1101

        return self.__parent__._cast(
            _1101.KlingelnbergCycloPalloidSpiralBevelGearSetDesign
        )

    @property
    def klingelnberg_cyclo_palloid_hypoid_gear_set_design(
        self: "CastSelf",
    ) -> "_1105.KlingelnbergCycloPalloidHypoidGearSetDesign":
        from mastapy._private.gears.gear_designs.klingelnberg_hypoid import _1105

        return self.__parent__._cast(_1105.KlingelnbergCycloPalloidHypoidGearSetDesign)

    @property
    def klingelnberg_conical_gear_set_design(
        self: "CastSelf",
    ) -> "_1109.KlingelnbergConicalGearSetDesign":
        from mastapy._private.gears.gear_designs.klingelnberg_conical import _1109

        return self.__parent__._cast(_1109.KlingelnbergConicalGearSetDesign)

    @property
    def hypoid_gear_set_design(self: "CastSelf") -> "_1113.HypoidGearSetDesign":
        from mastapy._private.gears.gear_designs.hypoid import _1113

        return self.__parent__._cast(_1113.HypoidGearSetDesign)

    @property
    def bevel_gear_set_design(self: "CastSelf") -> "_1328.BevelGearSetDesign":
        from mastapy._private.gears.gear_designs.bevel import _1328

        return self.__parent__._cast(_1328.BevelGearSetDesign)

    @property
    def agma_gleason_conical_gear_set_design(
        self: "CastSelf",
    ) -> "_1341.AGMAGleasonConicalGearSetDesign":
        from mastapy._private.gears.gear_designs.agma_gleason_conical import _1341

        return self.__parent__._cast(_1341.AGMAGleasonConicalGearSetDesign)

    @property
    def conical_gear_set_design(self: "CastSelf") -> "ConicalGearSetDesign":
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
class ConicalGearSetDesign(_1076.GearSetDesign):
    """ConicalGearSetDesign

    This is a mastapy class.
    """

    TYPE: ClassVar["Type"] = _CONICAL_GEAR_SET_DESIGN

    wrapped: "Any"

    def __post_init__(self: "Self") -> None:
        """Override of the post initialisation magic method."""
        if not hasattr(self.wrapped, "reference_count"):
            self.wrapped.reference_count = 0

        self.wrapped.reference_count += 1

    @property
    @exception_bridge
    def circular_pitch(self: "Self") -> "float":
        """float

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "CircularPitch")

        if temp is None:
            return 0.0

        return temp

    @property
    @exception_bridge
    def cutter_radius(self: "Self") -> "float":
        """float

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "CutterRadius")

        if temp is None:
            return 0.0

        return temp

    @property
    @exception_bridge
    def dominant_pinion(
        self: "Self",
    ) -> "list_with_selected_item.ListWithSelectedItem_str":
        """ListWithSelectedItem[str]"""
        temp = pythonnet_property_get(self.wrapped, "DominantPinion")

        if temp is None:
            return ""

        selected_value = temp.SelectedValue

        if selected_value is None:
            return ListWithSelectedItem_None(temp)

        return constructor.new_from_mastapy(
            "mastapy._private._internal.implicit.list_with_selected_item",
            "ListWithSelectedItem_str",
        )(temp)

    @dominant_pinion.setter
    @exception_bridge
    @enforce_parameter_types
    def dominant_pinion(self: "Self", value: "str") -> None:
        generic_type = list_with_selected_item.ListWithSelectedItem_str.implicit_type()
        value = promote_to_list_with_selected_item(value)
        value = conversion.mp_to_pn_smt_list_with_selected_item(
            self, value, generic_type
        )
        pythonnet_property_set(self.wrapped, "DominantPinion", value)

    @property
    @exception_bridge
    def imported_xml_file_name(self: "Self") -> "str":
        """str

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "ImportedXMLFileName")

        if temp is None:
            return ""

        return temp

    @property
    @exception_bridge
    def mean_normal_module(self: "Self") -> "float":
        """float"""
        temp = pythonnet_property_get(self.wrapped, "MeanNormalModule")

        if temp is None:
            return 0.0

        return temp

    @mean_normal_module.setter
    @exception_bridge
    @enforce_parameter_types
    def mean_normal_module(self: "Self", value: "float") -> None:
        pythonnet_property_set(
            self.wrapped, "MeanNormalModule", float(value) if value is not None else 0.0
        )

    @property
    @exception_bridge
    def module(self: "Self") -> "float":
        """float"""
        temp = pythonnet_property_get(self.wrapped, "Module")

        if temp is None:
            return 0.0

        return temp

    @module.setter
    @exception_bridge
    @enforce_parameter_types
    def module(self: "Self", value: "float") -> None:
        pythonnet_property_set(
            self.wrapped, "Module", float(value) if value is not None else 0.0
        )

    @property
    @exception_bridge
    def wheel_finish_cutter_point_width(self: "Self") -> "float":
        """float"""
        temp = pythonnet_property_get(self.wrapped, "WheelFinishCutterPointWidth")

        if temp is None:
            return 0.0

        return temp

    @wheel_finish_cutter_point_width.setter
    @exception_bridge
    @enforce_parameter_types
    def wheel_finish_cutter_point_width(self: "Self", value: "float") -> None:
        pythonnet_property_set(
            self.wrapped,
            "WheelFinishCutterPointWidth",
            float(value) if value is not None else 0.0,
        )

    @property
    @exception_bridge
    def wheel_mean_cone_distance(self: "Self") -> "float":
        """float

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "WheelMeanConeDistance")

        if temp is None:
            return 0.0

        return temp

    @property
    @exception_bridge
    def wheel_outer_cone_distance(self: "Self") -> "float":
        """float

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "WheelOuterConeDistance")

        if temp is None:
            return 0.0

        return temp

    @property
    @exception_bridge
    def wheel_pitch_diameter(self: "Self") -> "float":
        """float"""
        temp = pythonnet_property_get(self.wrapped, "WheelPitchDiameter")

        if temp is None:
            return 0.0

        return temp

    @wheel_pitch_diameter.setter
    @exception_bridge
    @enforce_parameter_types
    def wheel_pitch_diameter(self: "Self", value: "float") -> None:
        pythonnet_property_set(
            self.wrapped,
            "WheelPitchDiameter",
            float(value) if value is not None else 0.0,
        )

    @property
    @exception_bridge
    def conical_meshes(self: "Self") -> "List[_1301.ConicalGearMeshDesign]":
        """List[mastapy.gears.gear_designs.conical.ConicalGearMeshDesign]

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "ConicalMeshes")

        if temp is None:
            return None

        value = conversion.pn_to_mp_objects_in_list(temp)

        if value is None:
            return None

        return value

    @property
    def cast_to(self: "Self") -> "_Cast_ConicalGearSetDesign":
        """Cast to another type.

        Returns:
            _Cast_ConicalGearSetDesign
        """
        return _Cast_ConicalGearSetDesign(self)
