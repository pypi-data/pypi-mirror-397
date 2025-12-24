"""PointLoadLoadCase"""

from __future__ import annotations

from enum import Enum
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

from mastapy._private._internal import (
    constructor,
    conversion,
    enum_with_selected_value_runtime,
    utility,
)
from mastapy._private._internal.implicit import enum_with_selected_value
from mastapy._private.system_model.analyses_and_results.static_loads import _7907

_POINT_LOAD_LOAD_CASE = python_net_import(
    "SMT.MastaAPI.SystemModel.AnalysesAndResults.StaticLoads", "PointLoadLoadCase"
)

if TYPE_CHECKING:
    from typing import Any, Type, TypeVar

    from mastapy._private.nodal_analysis.varying_input_components import _105, _107
    from mastapy._private.system_model.analyses_and_results import _2943, _2945, _2949
    from mastapy._private.system_model.analyses_and_results.static_loads import (
        _7758,
        _7847,
        _7851,
        _7860,
    )
    from mastapy._private.system_model.part_model import _2746

    Self = TypeVar("Self", bound="PointLoadLoadCase")
    CastSelf = TypeVar("CastSelf", bound="PointLoadLoadCase._Cast_PointLoadLoadCase")


__docformat__ = "restructuredtext en"
__all__ = ("PointLoadLoadCase",)


@extended_dataclass(frozen=True, slots=True, weakref_slot=True)
class _Cast_PointLoadLoadCase:
    """Special nested class for casting PointLoadLoadCase to subclasses."""

    __parent__: "PointLoadLoadCase"

    @property
    def virtual_component_load_case(
        self: "CastSelf",
    ) -> "_7907.VirtualComponentLoadCase":
        return self.__parent__._cast(_7907.VirtualComponentLoadCase)

    @property
    def mountable_component_load_case(
        self: "CastSelf",
    ) -> "_7847.MountableComponentLoadCase":
        from mastapy._private.system_model.analyses_and_results.static_loads import (
            _7847,
        )

        return self.__parent__._cast(_7847.MountableComponentLoadCase)

    @property
    def component_load_case(self: "CastSelf") -> "_7758.ComponentLoadCase":
        from mastapy._private.system_model.analyses_and_results.static_loads import (
            _7758,
        )

        return self.__parent__._cast(_7758.ComponentLoadCase)

    @property
    def part_load_case(self: "CastSelf") -> "_7851.PartLoadCase":
        from mastapy._private.system_model.analyses_and_results.static_loads import (
            _7851,
        )

        return self.__parent__._cast(_7851.PartLoadCase)

    @property
    def part_analysis(self: "CastSelf") -> "_2949.PartAnalysis":
        from mastapy._private.system_model.analyses_and_results import _2949

        return self.__parent__._cast(_2949.PartAnalysis)

    @property
    def design_entity_single_context_analysis(
        self: "CastSelf",
    ) -> "_2945.DesignEntitySingleContextAnalysis":
        from mastapy._private.system_model.analyses_and_results import _2945

        return self.__parent__._cast(_2945.DesignEntitySingleContextAnalysis)

    @property
    def design_entity_analysis(self: "CastSelf") -> "_2943.DesignEntityAnalysis":
        from mastapy._private.system_model.analyses_and_results import _2943

        return self.__parent__._cast(_2943.DesignEntityAnalysis)

    @property
    def point_load_load_case(self: "CastSelf") -> "PointLoadLoadCase":
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
class PointLoadLoadCase(_7907.VirtualComponentLoadCase):
    """PointLoadLoadCase

    This is a mastapy class.
    """

    TYPE: ClassVar["Type"] = _POINT_LOAD_LOAD_CASE

    class ForceSpecification(Enum):
        """ForceSpecification is a nested enum."""

        @classmethod
        def type_(cls) -> "Type":
            return _POINT_LOAD_LOAD_CASE.ForceSpecification

        RADIAL_TANGENTIAL = 0
        FORCE_X_FORCE_Y = 1

    def __enum_setattr(self: "Self", attr: str, value: "Any") -> None:
        raise AttributeError("Cannot set the attributes of an Enum.") from None

    def __enum_delattr(self: "Self", attr: str) -> None:
        raise AttributeError("Cannot delete the attributes of an Enum.") from None

    ForceSpecification.__setattr__ = __enum_setattr
    ForceSpecification.__delattr__ = __enum_delattr

    wrapped: "Any"

    def __post_init__(self: "Self") -> None:
        """Override of the post initialisation magic method."""
        if not hasattr(self.wrapped, "reference_count"):
            self.wrapped.reference_count = 0

        self.wrapped.reference_count += 1

    @property
    @exception_bridge
    def angle_of_radial_force(self: "Self") -> "float":
        """float"""
        temp = pythonnet_property_get(self.wrapped, "AngleOfRadialForce")

        if temp is None:
            return 0.0

        return temp

    @angle_of_radial_force.setter
    @exception_bridge
    @enforce_parameter_types
    def angle_of_radial_force(self: "Self", value: "float") -> None:
        pythonnet_property_set(
            self.wrapped,
            "AngleOfRadialForce",
            float(value) if value is not None else 0.0,
        )

    @property
    @exception_bridge
    def force_specification_options(
        self: "Self",
    ) -> "enum_with_selected_value.EnumWithSelectedValue_PointLoadLoadCase_ForceSpecification":
        """EnumWithSelectedValue[mastapy.system_model.analyses_and_results.static_loads.PointLoadLoadCase.ForceSpecification]"""
        temp = pythonnet_property_get(self.wrapped, "ForceSpecificationOptions")

        if temp is None:
            return None

        value = enum_with_selected_value.EnumWithSelectedValue_PointLoadLoadCase_ForceSpecification.wrapped_type()
        return enum_with_selected_value_runtime.create(temp, value)

    @force_specification_options.setter
    @exception_bridge
    @enforce_parameter_types
    def force_specification_options(
        self: "Self", value: "PointLoadLoadCase.ForceSpecification"
    ) -> None:
        wrapper_type = enum_with_selected_value_runtime.ENUM_WITH_SELECTED_VALUE
        enclosed_type = enum_with_selected_value.EnumWithSelectedValue_PointLoadLoadCase_ForceSpecification.implicit_type()
        value = conversion.mp_to_pn_enum(value, enclosed_type)
        value = wrapper_type[enclosed_type](value)
        pythonnet_property_set(self.wrapped, "ForceSpecificationOptions", value)

    @property
    @exception_bridge
    def magnitude_radial_force(self: "Self") -> "float":
        """float"""
        temp = pythonnet_property_get(self.wrapped, "MagnitudeRadialForce")

        if temp is None:
            return 0.0

        return temp

    @magnitude_radial_force.setter
    @exception_bridge
    @enforce_parameter_types
    def magnitude_radial_force(self: "Self", value: "float") -> None:
        pythonnet_property_set(
            self.wrapped,
            "MagnitudeRadialForce",
            float(value) if value is not None else 0.0,
        )

    @property
    @exception_bridge
    def radial_load(self: "Self") -> "float":
        """float"""
        temp = pythonnet_property_get(self.wrapped, "RadialLoad")

        if temp is None:
            return 0.0

        return temp

    @radial_load.setter
    @exception_bridge
    @enforce_parameter_types
    def radial_load(self: "Self", value: "float") -> None:
        pythonnet_property_set(
            self.wrapped, "RadialLoad", float(value) if value is not None else 0.0
        )

    @property
    @exception_bridge
    def tangential_load(self: "Self") -> "float":
        """float"""
        temp = pythonnet_property_get(self.wrapped, "TangentialLoad")

        if temp is None:
            return 0.0

        return temp

    @tangential_load.setter
    @exception_bridge
    @enforce_parameter_types
    def tangential_load(self: "Self", value: "float") -> None:
        pythonnet_property_set(
            self.wrapped, "TangentialLoad", float(value) if value is not None else 0.0
        )

    @property
    @exception_bridge
    def component_design(self: "Self") -> "_2746.PointLoad":
        """mastapy.system_model.part_model.PointLoad

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "ComponentDesign")

        if temp is None:
            return None

        type_ = temp.GetType()
        return constructor.new(type_.Namespace, type_.Name)(temp)

    @property
    @exception_bridge
    def constraint_theta_x(self: "Self") -> "_107.MomentOrAngleInput":
        """mastapy.nodal_analysis.varying_input_components.MomentOrAngleInput

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "ConstraintThetaX")

        if temp is None:
            return None

        type_ = temp.GetType()
        return constructor.new(type_.Namespace, type_.Name)(temp)

    @property
    @exception_bridge
    def constraint_theta_y(self: "Self") -> "_107.MomentOrAngleInput":
        """mastapy.nodal_analysis.varying_input_components.MomentOrAngleInput

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "ConstraintThetaY")

        if temp is None:
            return None

        type_ = temp.GetType()
        return constructor.new(type_.Namespace, type_.Name)(temp)

    @property
    @exception_bridge
    def constraint_theta_z(self: "Self") -> "_107.MomentOrAngleInput":
        """mastapy.nodal_analysis.varying_input_components.MomentOrAngleInput

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "ConstraintThetaZ")

        if temp is None:
            return None

        type_ = temp.GetType()
        return constructor.new(type_.Namespace, type_.Name)(temp)

    @property
    @exception_bridge
    def constraint_x(self: "Self") -> "_105.ForceOrDisplacementInput":
        """mastapy.nodal_analysis.varying_input_components.ForceOrDisplacementInput

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "ConstraintX")

        if temp is None:
            return None

        type_ = temp.GetType()
        return constructor.new(type_.Namespace, type_.Name)(temp)

    @property
    @exception_bridge
    def constraint_y(self: "Self") -> "_105.ForceOrDisplacementInput":
        """mastapy.nodal_analysis.varying_input_components.ForceOrDisplacementInput

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "ConstraintY")

        if temp is None:
            return None

        type_ = temp.GetType()
        return constructor.new(type_.Namespace, type_.Name)(temp)

    @property
    @exception_bridge
    def constraint_z(self: "Self") -> "_105.ForceOrDisplacementInput":
        """mastapy.nodal_analysis.varying_input_components.ForceOrDisplacementInput

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "ConstraintZ")

        if temp is None:
            return None

        type_ = temp.GetType()
        return constructor.new(type_.Namespace, type_.Name)(temp)

    @exception_bridge
    def get_harmonic_load_data_for_import(
        self: "Self",
    ) -> "_7860.PointLoadHarmonicLoadData":
        """mastapy.system_model.analyses_and_results.static_loads.PointLoadHarmonicLoadData"""
        method_result = pythonnet_method_call(
            self.wrapped, "GetHarmonicLoadDataForImport"
        )
        type_ = method_result.GetType()
        return (
            constructor.new(type_.Namespace, type_.Name)(method_result)
            if method_result is not None
            else None
        )

    @property
    def cast_to(self: "Self") -> "_Cast_PointLoadLoadCase":
        """Cast to another type.

        Returns:
            _Cast_PointLoadLoadCase
        """
        return _Cast_PointLoadLoadCase(self)
