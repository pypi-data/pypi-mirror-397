"""AGMAGleasonConicalGearDesign"""

from __future__ import annotations

from typing import TYPE_CHECKING, ClassVar

from mastapy._private._internal.dataclasses import extended_dataclass
from mastapy._private._internal.exception_bridge import exception_bridge
from mastapy._private._internal.exceptions import CastException
from mastapy._private._internal.python_net import (
    python_net_import,
    pythonnet_property_get,
    pythonnet_property_get_with_method,
    pythonnet_property_set,
    pythonnet_property_set_with_method,
)
from mastapy._private._internal.type_enforcement import enforce_parameter_types

from mastapy._private._internal import (
    constructor,
    conversion,
    enum_with_selected_value_runtime,
    utility,
)
from mastapy._private._internal.implicit import enum_with_selected_value
from mastapy._private.gears.gear_designs.conical import _1300, _1303, _1304

_DATABASE_WITH_SELECTED_ITEM = python_net_import(
    "SMT.MastaAPI.UtilityGUI.Databases", "DatabaseWithSelectedItem"
)
_AGMA_GLEASON_CONICAL_GEAR_DESIGN = python_net_import(
    "SMT.MastaAPI.Gears.GearDesigns.AGMAGleasonConical", "AGMAGleasonConicalGearDesign"
)

if TYPE_CHECKING:
    from typing import Any, Type, TypeVar

    from mastapy._private.gears import _420
    from mastapy._private.gears.gear_designs import _1073, _1074
    from mastapy._private.gears.gear_designs.bevel import _1326
    from mastapy._private.gears.gear_designs.conical import _1299, _1310
    from mastapy._private.gears.gear_designs.hypoid import _1111
    from mastapy._private.gears.gear_designs.spiral_bevel import _1095
    from mastapy._private.gears.gear_designs.straight_bevel import _1087
    from mastapy._private.gears.gear_designs.straight_bevel_diff import _1091
    from mastapy._private.gears.gear_designs.zerol_bevel import _1078
    from mastapy._private.gears.materials import _710

    Self = TypeVar("Self", bound="AGMAGleasonConicalGearDesign")
    CastSelf = TypeVar(
        "CastSelf",
        bound="AGMAGleasonConicalGearDesign._Cast_AGMAGleasonConicalGearDesign",
    )


__docformat__ = "restructuredtext en"
__all__ = ("AGMAGleasonConicalGearDesign",)


@extended_dataclass(frozen=True, slots=True, weakref_slot=True)
class _Cast_AGMAGleasonConicalGearDesign:
    """Special nested class for casting AGMAGleasonConicalGearDesign to subclasses."""

    __parent__: "AGMAGleasonConicalGearDesign"

    @property
    def conical_gear_design(self: "CastSelf") -> "_1300.ConicalGearDesign":
        return self.__parent__._cast(_1300.ConicalGearDesign)

    @property
    def gear_design(self: "CastSelf") -> "_1073.GearDesign":
        from mastapy._private.gears.gear_designs import _1073

        return self.__parent__._cast(_1073.GearDesign)

    @property
    def gear_design_component(self: "CastSelf") -> "_1074.GearDesignComponent":
        from mastapy._private.gears.gear_designs import _1074

        return self.__parent__._cast(_1074.GearDesignComponent)

    @property
    def zerol_bevel_gear_design(self: "CastSelf") -> "_1078.ZerolBevelGearDesign":
        from mastapy._private.gears.gear_designs.zerol_bevel import _1078

        return self.__parent__._cast(_1078.ZerolBevelGearDesign)

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
    def hypoid_gear_design(self: "CastSelf") -> "_1111.HypoidGearDesign":
        from mastapy._private.gears.gear_designs.hypoid import _1111

        return self.__parent__._cast(_1111.HypoidGearDesign)

    @property
    def bevel_gear_design(self: "CastSelf") -> "_1326.BevelGearDesign":
        from mastapy._private.gears.gear_designs.bevel import _1326

        return self.__parent__._cast(_1326.BevelGearDesign)

    @property
    def agma_gleason_conical_gear_design(
        self: "CastSelf",
    ) -> "AGMAGleasonConicalGearDesign":
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
class AGMAGleasonConicalGearDesign(_1300.ConicalGearDesign):
    """AGMAGleasonConicalGearDesign

    This is a mastapy class.
    """

    TYPE: ClassVar["Type"] = _AGMA_GLEASON_CONICAL_GEAR_DESIGN

    wrapped: "Any"

    def __post_init__(self: "Self") -> None:
        """Override of the post initialisation magic method."""
        if not hasattr(self.wrapped, "reference_count"):
            self.wrapped.reference_count = 0

        self.wrapped.reference_count += 1

    @property
    @exception_bridge
    def allowable_bending_stress(self: "Self") -> "float":
        """float

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "AllowableBendingStress")

        if temp is None:
            return 0.0

        return temp

    @property
    @exception_bridge
    def allowable_contact_stress(self: "Self") -> "float":
        """float

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "AllowableContactStress")

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
    def front_end_type(self: "Self") -> "_1310.FrontEndTypes":
        """mastapy.gears.gear_designs.conical.FrontEndTypes"""
        temp = pythonnet_property_get(self.wrapped, "FrontEndType")

        if temp is None:
            return None

        value = conversion.pn_to_mp_enum(
            temp, "SMT.MastaAPI.Gears.GearDesigns.Conical.FrontEndTypes"
        )

        if value is None:
            return None

        return constructor.new_from_mastapy(
            "mastapy._private.gears.gear_designs.conical._1310", "FrontEndTypes"
        )(value)

    @front_end_type.setter
    @exception_bridge
    @enforce_parameter_types
    def front_end_type(self: "Self", value: "_1310.FrontEndTypes") -> None:
        value = conversion.mp_to_pn_enum(
            value, "SMT.MastaAPI.Gears.GearDesigns.Conical.FrontEndTypes"
        )
        pythonnet_property_set(self.wrapped, "FrontEndType", value)

    @property
    @exception_bridge
    def machine_setting_calculation_method(
        self: "Self",
    ) -> "enum_with_selected_value.EnumWithSelectedValue_ConicalMachineSettingCalculationMethods":
        """EnumWithSelectedValue[mastapy.gears.gear_designs.conical.ConicalMachineSettingCalculationMethods]"""
        temp = pythonnet_property_get(self.wrapped, "MachineSettingCalculationMethod")

        if temp is None:
            return None

        value = enum_with_selected_value.EnumWithSelectedValue_ConicalMachineSettingCalculationMethods.wrapped_type()
        return enum_with_selected_value_runtime.create(temp, value)

    @machine_setting_calculation_method.setter
    @exception_bridge
    @enforce_parameter_types
    def machine_setting_calculation_method(
        self: "Self", value: "_1303.ConicalMachineSettingCalculationMethods"
    ) -> None:
        wrapper_type = enum_with_selected_value_runtime.ENUM_WITH_SELECTED_VALUE
        enclosed_type = enum_with_selected_value.EnumWithSelectedValue_ConicalMachineSettingCalculationMethods.implicit_type()
        value = conversion.mp_to_pn_enum(value, enclosed_type)
        value = wrapper_type[enclosed_type](value)
        pythonnet_property_set(self.wrapped, "MachineSettingCalculationMethod", value)

    @property
    @exception_bridge
    def manufacture_method(
        self: "Self",
    ) -> "enum_with_selected_value.EnumWithSelectedValue_ConicalManufactureMethods":
        """EnumWithSelectedValue[mastapy.gears.gear_designs.conical.ConicalManufactureMethods]"""
        temp = pythonnet_property_get(self.wrapped, "ManufactureMethod")

        if temp is None:
            return None

        value = enum_with_selected_value.EnumWithSelectedValue_ConicalManufactureMethods.wrapped_type()
        return enum_with_selected_value_runtime.create(temp, value)

    @manufacture_method.setter
    @exception_bridge
    @enforce_parameter_types
    def manufacture_method(
        self: "Self", value: "_1304.ConicalManufactureMethods"
    ) -> None:
        wrapper_type = enum_with_selected_value_runtime.ENUM_WITH_SELECTED_VALUE
        enclosed_type = enum_with_selected_value.EnumWithSelectedValue_ConicalManufactureMethods.implicit_type()
        value = conversion.mp_to_pn_enum(value, enclosed_type)
        value = wrapper_type[enclosed_type](value)
        pythonnet_property_set(self.wrapped, "ManufactureMethod", value)

    @property
    @exception_bridge
    def material(self: "Self") -> "str":
        """str"""
        temp = pythonnet_property_get_with_method(
            self.wrapped, "Material", "SelectedItemName"
        )

        if temp is None:
            return ""

        return temp

    @material.setter
    @exception_bridge
    @enforce_parameter_types
    def material(self: "Self", value: "str") -> None:
        pythonnet_property_set_with_method(
            self.wrapped,
            "Material",
            "SetSelectedItem",
            str(value) if value is not None else "",
        )

    @property
    @exception_bridge
    def accuracy_grades(self: "Self") -> "_420.AccuracyGrades":
        """mastapy.gears.AccuracyGrades

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "AccuracyGrades")

        if temp is None:
            return None

        type_ = temp.GetType()
        return constructor.new(type_.Namespace, type_.Name)(temp)

    @property
    @exception_bridge
    def bevel_gear_material(self: "Self") -> "_710.GearMaterial":
        """mastapy.gears.materials.GearMaterial

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "BevelGearMaterial")

        if temp is None:
            return None

        type_ = temp.GetType()
        return constructor.new(type_.Namespace, type_.Name)(temp)

    @property
    @exception_bridge
    def cutter(self: "Self") -> "_1299.ConicalGearCutter":
        """mastapy.gears.gear_designs.conical.ConicalGearCutter

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "Cutter")

        if temp is None:
            return None

        type_ = temp.GetType()
        return constructor.new(type_.Namespace, type_.Name)(temp)

    @property
    def cast_to(self: "Self") -> "_Cast_AGMAGleasonConicalGearDesign":
        """Cast to another type.

        Returns:
            _Cast_AGMAGleasonConicalGearDesign
        """
        return _Cast_AGMAGleasonConicalGearDesign(self)
