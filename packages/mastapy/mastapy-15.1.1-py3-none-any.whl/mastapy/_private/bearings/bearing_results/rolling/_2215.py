"""ISO14179Settings"""

from __future__ import annotations

from typing import TYPE_CHECKING, ClassVar

from mastapy._private._internal.dataclasses import extended_dataclass
from mastapy._private._internal.exception_bridge import exception_bridge
from mastapy._private._internal.exceptions import CastException
from mastapy._private._internal.overridable_constructor import _unpack_overridable
from mastapy._private._internal.python_net import (
    python_net_import,
    pythonnet_property_get,
    pythonnet_property_set,
)
from mastapy._private._internal.type_enforcement import enforce_parameter_types

from mastapy._private._internal import constructor, conversion, utility
from mastapy._private._internal.implicit import overridable
from mastapy._private.utility.databases import _2061

_ISO14179_SETTINGS = python_net_import(
    "SMT.MastaAPI.Bearings.BearingResults.Rolling", "ISO14179Settings"
)

if TYPE_CHECKING:
    from typing import Any, Tuple, Type, TypeVar, Union

    from mastapy._private.bearings.bearing_results.rolling import _2308, _2309
    from mastapy._private.math_utility.measured_data import _1783, _1784

    Self = TypeVar("Self", bound="ISO14179Settings")
    CastSelf = TypeVar("CastSelf", bound="ISO14179Settings._Cast_ISO14179Settings")


__docformat__ = "restructuredtext en"
__all__ = ("ISO14179Settings",)


@extended_dataclass(frozen=True, slots=True, weakref_slot=True)
class _Cast_ISO14179Settings:
    """Special nested class for casting ISO14179Settings to subclasses."""

    __parent__: "ISO14179Settings"

    @property
    def named_database_item(self: "CastSelf") -> "_2061.NamedDatabaseItem":
        return self.__parent__._cast(_2061.NamedDatabaseItem)

    @property
    def iso14179_settings(self: "CastSelf") -> "ISO14179Settings":
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
class ISO14179Settings(_2061.NamedDatabaseItem):
    """ISO14179Settings

    This is a mastapy class.
    """

    TYPE: ClassVar["Type"] = _ISO14179_SETTINGS

    wrapped: "Any"

    def __post_init__(self: "Self") -> None:
        """Override of the post initialisation magic method."""
        if not hasattr(self.wrapped, "reference_count"):
            self.wrapped.reference_count = 0

        self.wrapped.reference_count += 1

    @property
    @exception_bridge
    def base_f0(self: "Self") -> "overridable.Overridable_float":
        """Overridable[float]"""
        temp = pythonnet_property_get(self.wrapped, "BaseF0")

        if temp is None:
            return 0.0

        return constructor.new_from_mastapy(
            "mastapy._private._internal.implicit.overridable", "Overridable_float"
        )(temp)

    @base_f0.setter
    @exception_bridge
    @enforce_parameter_types
    def base_f0(self: "Self", value: "Union[float, Tuple[float, bool]]") -> None:
        wrapper_type = overridable.Overridable_float.wrapper_type()
        enclosed_type = overridable.Overridable_float.implicit_type()
        value, is_overridden = _unpack_overridable(value)
        value = wrapper_type[enclosed_type](
            enclosed_type(value) if value is not None else 0.0, is_overridden
        )
        pythonnet_property_set(self.wrapped, "BaseF0", value)

    @property
    @exception_bridge
    def bore_factor_for_f0_calculation(self: "Self") -> "float":
        """float"""
        temp = pythonnet_property_get(self.wrapped, "BoreFactorForF0Calculation")

        if temp is None:
            return 0.0

        return temp

    @bore_factor_for_f0_calculation.setter
    @exception_bridge
    @enforce_parameter_types
    def bore_factor_for_f0_calculation(self: "Self", value: "float") -> None:
        pythonnet_property_set(
            self.wrapped,
            "BoreFactorForF0Calculation",
            float(value) if value is not None else 0.0,
        )

    @property
    @exception_bridge
    def cage_type_factor(self: "Self") -> "overridable.Overridable_float":
        """Overridable[float]"""
        temp = pythonnet_property_get(self.wrapped, "CageTypeFactor")

        if temp is None:
            return 0.0

        return constructor.new_from_mastapy(
            "mastapy._private._internal.implicit.overridable", "Overridable_float"
        )(temp)

    @cage_type_factor.setter
    @exception_bridge
    @enforce_parameter_types
    def cage_type_factor(
        self: "Self", value: "Union[float, Tuple[float, bool]]"
    ) -> None:
        wrapper_type = overridable.Overridable_float.wrapper_type()
        enclosed_type = overridable.Overridable_float.implicit_type()
        value, is_overridden = _unpack_overridable(value)
        value = wrapper_type[enclosed_type](
            enclosed_type(value) if value is not None else 0.0, is_overridden
        )
        pythonnet_property_set(self.wrapped, "CageTypeFactor", value)

    @property
    @exception_bridge
    def calculate_base_f0_using_bearing_width_and_bore(self: "Self") -> "bool":
        """bool"""
        temp = pythonnet_property_get(
            self.wrapped, "CalculateBaseF0UsingBearingWidthAndBore"
        )

        if temp is None:
            return False

        return temp

    @calculate_base_f0_using_bearing_width_and_bore.setter
    @exception_bridge
    @enforce_parameter_types
    def calculate_base_f0_using_bearing_width_and_bore(
        self: "Self", value: "bool"
    ) -> None:
        pythonnet_property_set(
            self.wrapped,
            "CalculateBaseF0UsingBearingWidthAndBore",
            bool(value) if value is not None else False,
        )

    @property
    @exception_bridge
    def cross_flow_factor(self: "Self") -> "overridable.Overridable_float":
        """Overridable[float]"""
        temp = pythonnet_property_get(self.wrapped, "CrossFlowFactor")

        if temp is None:
            return 0.0

        return constructor.new_from_mastapy(
            "mastapy._private._internal.implicit.overridable", "Overridable_float"
        )(temp)

    @cross_flow_factor.setter
    @exception_bridge
    @enforce_parameter_types
    def cross_flow_factor(
        self: "Self", value: "Union[float, Tuple[float, bool]]"
    ) -> None:
        wrapper_type = overridable.Overridable_float.wrapper_type()
        enclosed_type = overridable.Overridable_float.implicit_type()
        value, is_overridden = _unpack_overridable(value)
        value = wrapper_type[enclosed_type](
            enclosed_type(value) if value is not None else 0.0, is_overridden
        )
        pythonnet_property_set(self.wrapped, "CrossFlowFactor", value)

    @property
    @exception_bridge
    def exponent_of_static_equivalent_load_to_capacity_ratio(
        self: "Self",
    ) -> "overridable.Overridable_float":
        """Overridable[float]"""
        temp = pythonnet_property_get(
            self.wrapped, "ExponentOfStaticEquivalentLoadToCapacityRatio"
        )

        if temp is None:
            return 0.0

        return constructor.new_from_mastapy(
            "mastapy._private._internal.implicit.overridable", "Overridable_float"
        )(temp)

    @exponent_of_static_equivalent_load_to_capacity_ratio.setter
    @exception_bridge
    @enforce_parameter_types
    def exponent_of_static_equivalent_load_to_capacity_ratio(
        self: "Self", value: "Union[float, Tuple[float, bool]]"
    ) -> None:
        wrapper_type = overridable.Overridable_float.wrapper_type()
        enclosed_type = overridable.Overridable_float.implicit_type()
        value, is_overridden = _unpack_overridable(value)
        value = wrapper_type[enclosed_type](
            enclosed_type(value) if value is not None else 0.0, is_overridden
        )
        pythonnet_property_set(
            self.wrapped, "ExponentOfStaticEquivalentLoadToCapacityRatio", value
        )

    @property
    @exception_bridge
    def ina_lubrication_flooding_correction_factor(
        self: "Self",
    ) -> "overridable.Overridable_float":
        """Overridable[float]"""
        temp = pythonnet_property_get(
            self.wrapped, "INALubricationFloodingCorrectionFactor"
        )

        if temp is None:
            return 0.0

        return constructor.new_from_mastapy(
            "mastapy._private._internal.implicit.overridable", "Overridable_float"
        )(temp)

    @ina_lubrication_flooding_correction_factor.setter
    @exception_bridge
    @enforce_parameter_types
    def ina_lubrication_flooding_correction_factor(
        self: "Self", value: "Union[float, Tuple[float, bool]]"
    ) -> None:
        wrapper_type = overridable.Overridable_float.wrapper_type()
        enclosed_type = overridable.Overridable_float.implicit_type()
        value, is_overridden = _unpack_overridable(value)
        value = wrapper_type[enclosed_type](
            enclosed_type(value) if value is not None else 0.0, is_overridden
        )
        pythonnet_property_set(
            self.wrapped, "INALubricationFloodingCorrectionFactor", value
        )

    @property
    @exception_bridge
    def isotr141792001f1_specification_method(
        self: "Self",
    ) -> "_2308.PowerRatingF1EstimationMethod":
        """mastapy.bearings.bearing_results.rolling.PowerRatingF1EstimationMethod"""
        temp = pythonnet_property_get(
            self.wrapped, "ISOTR141792001F1SpecificationMethod"
        )

        if temp is None:
            return None

        value = conversion.pn_to_mp_enum(
            temp,
            "SMT.MastaAPI.Bearings.BearingResults.Rolling.PowerRatingF1EstimationMethod",
        )

        if value is None:
            return None

        return constructor.new_from_mastapy(
            "mastapy._private.bearings.bearing_results.rolling._2308",
            "PowerRatingF1EstimationMethod",
        )(value)

    @isotr141792001f1_specification_method.setter
    @exception_bridge
    @enforce_parameter_types
    def isotr141792001f1_specification_method(
        self: "Self", value: "_2308.PowerRatingF1EstimationMethod"
    ) -> None:
        value = conversion.mp_to_pn_enum(
            value,
            "SMT.MastaAPI.Bearings.BearingResults.Rolling.PowerRatingF1EstimationMethod",
        )
        pythonnet_property_set(
            self.wrapped, "ISOTR141792001F1SpecificationMethod", value
        )

    @property
    @exception_bridge
    def power_rating_f0_additional_adjustment_factor(
        self: "Self",
    ) -> "overridable.Overridable_float":
        """Overridable[float]"""
        temp = pythonnet_property_get(
            self.wrapped, "PowerRatingF0AdditionalAdjustmentFactor"
        )

        if temp is None:
            return 0.0

        return constructor.new_from_mastapy(
            "mastapy._private._internal.implicit.overridable", "Overridable_float"
        )(temp)

    @power_rating_f0_additional_adjustment_factor.setter
    @exception_bridge
    @enforce_parameter_types
    def power_rating_f0_additional_adjustment_factor(
        self: "Self", value: "Union[float, Tuple[float, bool]]"
    ) -> None:
        wrapper_type = overridable.Overridable_float.wrapper_type()
        enclosed_type = overridable.Overridable_float.implicit_type()
        value, is_overridden = _unpack_overridable(value)
        value = wrapper_type[enclosed_type](
            enclosed_type(value) if value is not None else 0.0, is_overridden
        )
        pythonnet_property_set(
            self.wrapped, "PowerRatingF0AdditionalAdjustmentFactor", value
        )

    @property
    @exception_bridge
    def power_rating_f0_scaling_factor(self: "Self") -> "overridable.Overridable_float":
        """Overridable[float]"""
        temp = pythonnet_property_get(self.wrapped, "PowerRatingF0ScalingFactor")

        if temp is None:
            return 0.0

        return constructor.new_from_mastapy(
            "mastapy._private._internal.implicit.overridable", "Overridable_float"
        )(temp)

    @power_rating_f0_scaling_factor.setter
    @exception_bridge
    @enforce_parameter_types
    def power_rating_f0_scaling_factor(
        self: "Self", value: "Union[float, Tuple[float, bool]]"
    ) -> None:
        wrapper_type = overridable.Overridable_float.wrapper_type()
        enclosed_type = overridable.Overridable_float.implicit_type()
        value, is_overridden = _unpack_overridable(value)
        value = wrapper_type[enclosed_type](
            enclosed_type(value) if value is not None else 0.0, is_overridden
        )
        pythonnet_property_set(self.wrapped, "PowerRatingF0ScalingFactor", value)

    @property
    @exception_bridge
    def power_rating_f0_scaling_method(
        self: "Self",
    ) -> "_2309.PowerRatingFactorScalingMethod":
        """mastapy.bearings.bearing_results.rolling.PowerRatingFactorScalingMethod"""
        temp = pythonnet_property_get(self.wrapped, "PowerRatingF0ScalingMethod")

        if temp is None:
            return None

        value = conversion.pn_to_mp_enum(
            temp,
            "SMT.MastaAPI.Bearings.BearingResults.Rolling.PowerRatingFactorScalingMethod",
        )

        if value is None:
            return None

        return constructor.new_from_mastapy(
            "mastapy._private.bearings.bearing_results.rolling._2309",
            "PowerRatingFactorScalingMethod",
        )(value)

    @power_rating_f0_scaling_method.setter
    @exception_bridge
    @enforce_parameter_types
    def power_rating_f0_scaling_method(
        self: "Self", value: "_2309.PowerRatingFactorScalingMethod"
    ) -> None:
        value = conversion.mp_to_pn_enum(
            value,
            "SMT.MastaAPI.Bearings.BearingResults.Rolling.PowerRatingFactorScalingMethod",
        )
        pythonnet_property_set(self.wrapped, "PowerRatingF0ScalingMethod", value)

    @property
    @exception_bridge
    def power_rating_f1_scaling_factor(self: "Self") -> "overridable.Overridable_float":
        """Overridable[float]"""
        temp = pythonnet_property_get(self.wrapped, "PowerRatingF1ScalingFactor")

        if temp is None:
            return 0.0

        return constructor.new_from_mastapy(
            "mastapy._private._internal.implicit.overridable", "Overridable_float"
        )(temp)

    @power_rating_f1_scaling_factor.setter
    @exception_bridge
    @enforce_parameter_types
    def power_rating_f1_scaling_factor(
        self: "Self", value: "Union[float, Tuple[float, bool]]"
    ) -> None:
        wrapper_type = overridable.Overridable_float.wrapper_type()
        enclosed_type = overridable.Overridable_float.implicit_type()
        value, is_overridden = _unpack_overridable(value)
        value = wrapper_type[enclosed_type](
            enclosed_type(value) if value is not None else 0.0, is_overridden
        )
        pythonnet_property_set(self.wrapped, "PowerRatingF1ScalingFactor", value)

    @property
    @exception_bridge
    def power_rating_f1_scaling_method(
        self: "Self",
    ) -> "_2309.PowerRatingFactorScalingMethod":
        """mastapy.bearings.bearing_results.rolling.PowerRatingFactorScalingMethod"""
        temp = pythonnet_property_get(self.wrapped, "PowerRatingF1ScalingMethod")

        if temp is None:
            return None

        value = conversion.pn_to_mp_enum(
            temp,
            "SMT.MastaAPI.Bearings.BearingResults.Rolling.PowerRatingFactorScalingMethod",
        )

        if value is None:
            return None

        return constructor.new_from_mastapy(
            "mastapy._private.bearings.bearing_results.rolling._2309",
            "PowerRatingFactorScalingMethod",
        )(value)

    @power_rating_f1_scaling_method.setter
    @exception_bridge
    @enforce_parameter_types
    def power_rating_f1_scaling_method(
        self: "Self", value: "_2309.PowerRatingFactorScalingMethod"
    ) -> None:
        value = conversion.mp_to_pn_enum(
            value,
            "SMT.MastaAPI.Bearings.BearingResults.Rolling.PowerRatingFactorScalingMethod",
        )
        pythonnet_property_set(self.wrapped, "PowerRatingF1ScalingMethod", value)

    @property
    @exception_bridge
    def user_specified_f1_for_isotr141792001(self: "Self") -> "float":
        """float"""
        temp = pythonnet_property_get(self.wrapped, "UserSpecifiedF1ForISOTR141792001")

        if temp is None:
            return 0.0

        return temp

    @user_specified_f1_for_isotr141792001.setter
    @exception_bridge
    @enforce_parameter_types
    def user_specified_f1_for_isotr141792001(self: "Self", value: "float") -> None:
        pythonnet_property_set(
            self.wrapped,
            "UserSpecifiedF1ForISOTR141792001",
            float(value) if value is not None else 0.0,
        )

    @property
    @exception_bridge
    def width_factor_for_f0_calculation(self: "Self") -> "float":
        """float"""
        temp = pythonnet_property_get(self.wrapped, "WidthFactorForF0Calculation")

        if temp is None:
            return 0.0

        return temp

    @width_factor_for_f0_calculation.setter
    @exception_bridge
    @enforce_parameter_types
    def width_factor_for_f0_calculation(self: "Self", value: "float") -> None:
        pythonnet_property_set(
            self.wrapped,
            "WidthFactorForF0Calculation",
            float(value) if value is not None else 0.0,
        )

    @property
    @exception_bridge
    def power_rating_f0_scaling_factor_one_dimensional_lookup_table(
        self: "Self",
    ) -> "_1783.OnedimensionalFunctionLookupTable":
        """mastapy.math_utility.measured_data.OnedimensionalFunctionLookupTable

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(
            self.wrapped, "PowerRatingF0ScalingFactorOneDimensionalLookupTable"
        )

        if temp is None:
            return None

        type_ = temp.GetType()
        return constructor.new(type_.Namespace, type_.Name)(temp)

    @property
    @exception_bridge
    def power_rating_f1_one_dimensional_lookup_table(
        self: "Self",
    ) -> "_1783.OnedimensionalFunctionLookupTable":
        """mastapy.math_utility.measured_data.OnedimensionalFunctionLookupTable

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(
            self.wrapped, "PowerRatingF1OneDimensionalLookupTable"
        )

        if temp is None:
            return None

        type_ = temp.GetType()
        return constructor.new(type_.Namespace, type_.Name)(temp)

    @property
    @exception_bridge
    def power_rating_f1_scaling_factor_one_dimensional_lookup_table(
        self: "Self",
    ) -> "_1783.OnedimensionalFunctionLookupTable":
        """mastapy.math_utility.measured_data.OnedimensionalFunctionLookupTable

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(
            self.wrapped, "PowerRatingF1ScalingFactorOneDimensionalLookupTable"
        )

        if temp is None:
            return None

        type_ = temp.GetType()
        return constructor.new(type_.Namespace, type_.Name)(temp)

    @property
    @exception_bridge
    def power_rating_f1_two_dimensional_lookup_table(
        self: "Self",
    ) -> "_1784.TwodimensionalFunctionLookupTable":
        """mastapy.math_utility.measured_data.TwodimensionalFunctionLookupTable

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(
            self.wrapped, "PowerRatingF1TwoDimensionalLookupTable"
        )

        if temp is None:
            return None

        type_ = temp.GetType()
        return constructor.new(type_.Namespace, type_.Name)(temp)

    @property
    def cast_to(self: "Self") -> "_Cast_ISO14179Settings":
        """Cast to another type.

        Returns:
            _Cast_ISO14179Settings
        """
        return _Cast_ISO14179Settings(self)
