"""SplineJointDesign"""

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

from mastapy._private._internal import (
    constructor,
    conversion,
    enum_with_selected_value_runtime,
    utility,
)
from mastapy._private._internal.implicit import enum_with_selected_value, overridable
from mastapy._private.detailed_rigid_connectors import _1599
from mastapy._private.detailed_rigid_connectors.splines import _1606, _1629

_SPLINE_JOINT_DESIGN = python_net_import(
    "SMT.MastaAPI.DetailedRigidConnectors.Splines", "SplineJointDesign"
)

if TYPE_CHECKING:
    from typing import Any, Tuple, Type, TypeVar, Union

    from mastapy._private.detailed_rigid_connectors.splines import (
        _1602,
        _1605,
        _1609,
        _1612,
        _1613,
        _1617,
        _1618,
        _1620,
        _1621,
        _1625,
        _1626,
        _1632,
    )

    Self = TypeVar("Self", bound="SplineJointDesign")
    CastSelf = TypeVar("CastSelf", bound="SplineJointDesign._Cast_SplineJointDesign")


__docformat__ = "restructuredtext en"
__all__ = ("SplineJointDesign",)


@extended_dataclass(frozen=True, slots=True, weakref_slot=True)
class _Cast_SplineJointDesign:
    """Special nested class for casting SplineJointDesign to subclasses."""

    __parent__: "SplineJointDesign"

    @property
    def detailed_rigid_connector_design(
        self: "CastSelf",
    ) -> "_1599.DetailedRigidConnectorDesign":
        return self.__parent__._cast(_1599.DetailedRigidConnectorDesign)

    @property
    def custom_spline_joint_design(self: "CastSelf") -> "_1602.CustomSplineJointDesign":
        from mastapy._private.detailed_rigid_connectors.splines import _1602

        return self.__parent__._cast(_1602.CustomSplineJointDesign)

    @property
    def din5480_spline_joint_design(
        self: "CastSelf",
    ) -> "_1605.DIN5480SplineJointDesign":
        from mastapy._private.detailed_rigid_connectors.splines import _1605

        return self.__parent__._cast(_1605.DIN5480SplineJointDesign)

    @property
    def gbt3478_spline_joint_design(
        self: "CastSelf",
    ) -> "_1609.GBT3478SplineJointDesign":
        from mastapy._private.detailed_rigid_connectors.splines import _1609

        return self.__parent__._cast(_1609.GBT3478SplineJointDesign)

    @property
    def iso4156_spline_joint_design(
        self: "CastSelf",
    ) -> "_1612.ISO4156SplineJointDesign":
        from mastapy._private.detailed_rigid_connectors.splines import _1612

        return self.__parent__._cast(_1612.ISO4156SplineJointDesign)

    @property
    def jisb1603_spline_joint_design(
        self: "CastSelf",
    ) -> "_1613.JISB1603SplineJointDesign":
        from mastapy._private.detailed_rigid_connectors.splines import _1613

        return self.__parent__._cast(_1613.JISB1603SplineJointDesign)

    @property
    def sae_spline_joint_design(self: "CastSelf") -> "_1620.SAESplineJointDesign":
        from mastapy._private.detailed_rigid_connectors.splines import _1620

        return self.__parent__._cast(_1620.SAESplineJointDesign)

    @property
    def standard_spline_joint_design(
        self: "CastSelf",
    ) -> "_1632.StandardSplineJointDesign":
        from mastapy._private.detailed_rigid_connectors.splines import _1632

        return self.__parent__._cast(_1632.StandardSplineJointDesign)

    @property
    def spline_joint_design(self: "CastSelf") -> "SplineJointDesign":
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
class SplineJointDesign(_1599.DetailedRigidConnectorDesign):
    """SplineJointDesign

    This is a mastapy class.
    """

    TYPE: ClassVar["Type"] = _SPLINE_JOINT_DESIGN

    wrapped: "Any"

    def __post_init__(self: "Self") -> None:
        """Override of the post initialisation magic method."""
        if not hasattr(self.wrapped, "reference_count"):
            self.wrapped.reference_count = 0

        self.wrapped.reference_count += 1

    @property
    @exception_bridge
    def base_diameter(self: "Self") -> "float":
        """float

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "BaseDiameter")

        if temp is None:
            return 0.0

        return temp

    @property
    @exception_bridge
    def base_pitch(self: "Self") -> "float":
        """float

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "BasePitch")

        if temp is None:
            return 0.0

        return temp

    @property
    @exception_bridge
    def base_radius(self: "Self") -> "float":
        """float

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "BaseRadius")

        if temp is None:
            return 0.0

        return temp

    @property
    @exception_bridge
    def basic_space_width(self: "Self") -> "float":
        """float

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "BasicSpaceWidth")

        if temp is None:
            return 0.0

        return temp

    @property
    @exception_bridge
    def basic_tooth_thickness(self: "Self") -> "float":
        """float

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "BasicToothThickness")

        if temp is None:
            return 0.0

        return temp

    @property
    @exception_bridge
    def before_running_in(self: "Self") -> "bool":
        """bool"""
        temp = pythonnet_property_get(self.wrapped, "BeforeRunningIn")

        if temp is None:
            return False

        return temp

    @before_running_in.setter
    @exception_bridge
    @enforce_parameter_types
    def before_running_in(self: "Self", value: "bool") -> None:
        pythonnet_property_set(
            self.wrapped, "BeforeRunningIn", bool(value) if value is not None else False
        )

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
    def designation(self: "Self") -> "str":
        """str

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "Designation")

        if temp is None:
            return ""

        return temp

    @property
    @exception_bridge
    def diametral_pitch(self: "Self") -> "float":
        """float"""
        temp = pythonnet_property_get(self.wrapped, "DiametralPitch")

        if temp is None:
            return 0.0

        return temp

    @diametral_pitch.setter
    @exception_bridge
    @enforce_parameter_types
    def diametral_pitch(self: "Self", value: "float") -> None:
        pythonnet_property_set(
            self.wrapped, "DiametralPitch", float(value) if value is not None else 0.0
        )

    @property
    @exception_bridge
    def dudley_maximum_effective_length(self: "Self") -> "float":
        """float

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "DudleyMaximumEffectiveLength")

        if temp is None:
            return 0.0

        return temp

    @property
    @exception_bridge
    def dudley_maximum_effective_length_option(
        self: "Self",
    ) -> "enum_with_selected_value.EnumWithSelectedValue_DudleyEffectiveLengthApproximationOption":
        """EnumWithSelectedValue[mastapy.detailed_rigid_connectors.splines.DudleyEffectiveLengthApproximationOption]"""
        temp = pythonnet_property_get(
            self.wrapped, "DudleyMaximumEffectiveLengthOption"
        )

        if temp is None:
            return None

        value = enum_with_selected_value.EnumWithSelectedValue_DudleyEffectiveLengthApproximationOption.wrapped_type()
        return enum_with_selected_value_runtime.create(temp, value)

    @dudley_maximum_effective_length_option.setter
    @exception_bridge
    @enforce_parameter_types
    def dudley_maximum_effective_length_option(
        self: "Self", value: "_1606.DudleyEffectiveLengthApproximationOption"
    ) -> None:
        wrapper_type = enum_with_selected_value_runtime.ENUM_WITH_SELECTED_VALUE
        enclosed_type = enum_with_selected_value.EnumWithSelectedValue_DudleyEffectiveLengthApproximationOption.implicit_type()
        value = conversion.mp_to_pn_enum(value, enclosed_type)
        value = wrapper_type[enclosed_type](value)
        pythonnet_property_set(
            self.wrapped, "DudleyMaximumEffectiveLengthOption", value
        )

    @property
    @exception_bridge
    def fatigue_life_factor_type(self: "Self") -> "_1618.SAEFatigueLifeFactorTypes":
        """mastapy.detailed_rigid_connectors.splines.SAEFatigueLifeFactorTypes"""
        temp = pythonnet_property_get(self.wrapped, "FatigueLifeFactorType")

        if temp is None:
            return None

        value = conversion.pn_to_mp_enum(
            temp,
            "SMT.MastaAPI.DetailedRigidConnectors.Splines.SAEFatigueLifeFactorTypes",
        )

        if value is None:
            return None

        return constructor.new_from_mastapy(
            "mastapy._private.detailed_rigid_connectors.splines._1618",
            "SAEFatigueLifeFactorTypes",
        )(value)

    @fatigue_life_factor_type.setter
    @exception_bridge
    @enforce_parameter_types
    def fatigue_life_factor_type(
        self: "Self", value: "_1618.SAEFatigueLifeFactorTypes"
    ) -> None:
        value = conversion.mp_to_pn_enum(
            value,
            "SMT.MastaAPI.DetailedRigidConnectors.Splines.SAEFatigueLifeFactorTypes",
        )
        pythonnet_property_set(self.wrapped, "FatigueLifeFactorType", value)

    @property
    @exception_bridge
    def minimum_effective_clearance(self: "Self") -> "float":
        """float

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "MinimumEffectiveClearance")

        if temp is None:
            return 0.0

        return temp

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
    def number_of_teeth_in_contact(self: "Self") -> "overridable.Overridable_float":
        """Overridable[float]"""
        temp = pythonnet_property_get(self.wrapped, "NumberOfTeethInContact")

        if temp is None:
            return 0.0

        return constructor.new_from_mastapy(
            "mastapy._private._internal.implicit.overridable", "Overridable_float"
        )(temp)

    @number_of_teeth_in_contact.setter
    @exception_bridge
    @enforce_parameter_types
    def number_of_teeth_in_contact(
        self: "Self", value: "Union[float, Tuple[float, bool]]"
    ) -> None:
        wrapper_type = overridable.Overridable_float.wrapper_type()
        enclosed_type = overridable.Overridable_float.implicit_type()
        value, is_overridden = _unpack_overridable(value)
        value = wrapper_type[enclosed_type](
            enclosed_type(value) if value is not None else 0.0, is_overridden
        )
        pythonnet_property_set(self.wrapped, "NumberOfTeethInContact", value)

    @property
    @exception_bridge
    def pitch_diameter(self: "Self") -> "float":
        """float

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "PitchDiameter")

        if temp is None:
            return 0.0

        return temp

    @property
    @exception_bridge
    def pressure_angle(self: "Self") -> "float":
        """float"""
        temp = pythonnet_property_get(self.wrapped, "PressureAngle")

        if temp is None:
            return 0.0

        return temp

    @pressure_angle.setter
    @exception_bridge
    @enforce_parameter_types
    def pressure_angle(self: "Self", value: "float") -> None:
        pythonnet_property_set(
            self.wrapped, "PressureAngle", float(value) if value is not None else 0.0
        )

    @property
    @exception_bridge
    def root_type(self: "Self") -> "_1617.RootTypes":
        """mastapy.detailed_rigid_connectors.splines.RootTypes"""
        temp = pythonnet_property_get(self.wrapped, "RootType")

        if temp is None:
            return None

        value = conversion.pn_to_mp_enum(
            temp, "SMT.MastaAPI.DetailedRigidConnectors.Splines.RootTypes"
        )

        if value is None:
            return None

        return constructor.new_from_mastapy(
            "mastapy._private.detailed_rigid_connectors.splines._1617", "RootTypes"
        )(value)

    @root_type.setter
    @exception_bridge
    @enforce_parameter_types
    def root_type(self: "Self", value: "_1617.RootTypes") -> None:
        value = conversion.mp_to_pn_enum(
            value, "SMT.MastaAPI.DetailedRigidConnectors.Splines.RootTypes"
        )
        pythonnet_property_set(self.wrapped, "RootType", value)

    @property
    @exception_bridge
    def spline_fixture_type(self: "Self") -> "_1625.SplineFixtureTypes":
        """mastapy.detailed_rigid_connectors.splines.SplineFixtureTypes"""
        temp = pythonnet_property_get(self.wrapped, "SplineFixtureType")

        if temp is None:
            return None

        value = conversion.pn_to_mp_enum(
            temp, "SMT.MastaAPI.DetailedRigidConnectors.Splines.SplineFixtureTypes"
        )

        if value is None:
            return None

        return constructor.new_from_mastapy(
            "mastapy._private.detailed_rigid_connectors.splines._1625",
            "SplineFixtureTypes",
        )(value)

    @spline_fixture_type.setter
    @exception_bridge
    @enforce_parameter_types
    def spline_fixture_type(self: "Self", value: "_1625.SplineFixtureTypes") -> None:
        value = conversion.mp_to_pn_enum(
            value, "SMT.MastaAPI.DetailedRigidConnectors.Splines.SplineFixtureTypes"
        )
        pythonnet_property_set(self.wrapped, "SplineFixtureType", value)

    @property
    @exception_bridge
    def spline_rating_type(
        self: "Self",
    ) -> "enum_with_selected_value.EnumWithSelectedValue_SplineRatingTypes":
        """EnumWithSelectedValue[mastapy.detailed_rigid_connectors.splines.SplineRatingTypes]"""
        temp = pythonnet_property_get(self.wrapped, "SplineRatingType")

        if temp is None:
            return None

        value = enum_with_selected_value.EnumWithSelectedValue_SplineRatingTypes.wrapped_type()
        return enum_with_selected_value_runtime.create(temp, value)

    @spline_rating_type.setter
    @exception_bridge
    @enforce_parameter_types
    def spline_rating_type(self: "Self", value: "_1629.SplineRatingTypes") -> None:
        wrapper_type = enum_with_selected_value_runtime.ENUM_WITH_SELECTED_VALUE
        enclosed_type = enum_with_selected_value.EnumWithSelectedValue_SplineRatingTypes.implicit_type()
        value = conversion.mp_to_pn_enum(value, enclosed_type)
        value = wrapper_type[enclosed_type](value)
        pythonnet_property_set(self.wrapped, "SplineRatingType", value)

    @property
    @exception_bridge
    def torque_cycles(self: "Self") -> "_1621.SAETorqueCycles":
        """mastapy.detailed_rigid_connectors.splines.SAETorqueCycles"""
        temp = pythonnet_property_get(self.wrapped, "TorqueCycles")

        if temp is None:
            return None

        value = conversion.pn_to_mp_enum(
            temp, "SMT.MastaAPI.DetailedRigidConnectors.Splines.SAETorqueCycles"
        )

        if value is None:
            return None

        return constructor.new_from_mastapy(
            "mastapy._private.detailed_rigid_connectors.splines._1621",
            "SAETorqueCycles",
        )(value)

    @torque_cycles.setter
    @exception_bridge
    @enforce_parameter_types
    def torque_cycles(self: "Self", value: "_1621.SAETorqueCycles") -> None:
        value = conversion.mp_to_pn_enum(
            value, "SMT.MastaAPI.DetailedRigidConnectors.Splines.SAETorqueCycles"
        )
        pythonnet_property_set(self.wrapped, "TorqueCycles", value)

    @property
    @exception_bridge
    def total_crowning(self: "Self") -> "float":
        """float"""
        temp = pythonnet_property_get(self.wrapped, "TotalCrowning")

        if temp is None:
            return 0.0

        return temp

    @total_crowning.setter
    @exception_bridge
    @enforce_parameter_types
    def total_crowning(self: "Self", value: "float") -> None:
        pythonnet_property_set(
            self.wrapped, "TotalCrowning", float(value) if value is not None else 0.0
        )

    @property
    @exception_bridge
    def use_sae_stress_concentration_factor(self: "Self") -> "bool":
        """bool"""
        temp = pythonnet_property_get(self.wrapped, "UseSAEStressConcentrationFactor")

        if temp is None:
            return False

        return temp

    @use_sae_stress_concentration_factor.setter
    @exception_bridge
    @enforce_parameter_types
    def use_sae_stress_concentration_factor(self: "Self", value: "bool") -> None:
        pythonnet_property_set(
            self.wrapped,
            "UseSAEStressConcentrationFactor",
            bool(value) if value is not None else False,
        )

    @property
    @exception_bridge
    def use_user_input_allowable_stresses(self: "Self") -> "bool":
        """bool"""
        temp = pythonnet_property_get(self.wrapped, "UseUserInputAllowableStresses")

        if temp is None:
            return False

        return temp

    @use_user_input_allowable_stresses.setter
    @exception_bridge
    @enforce_parameter_types
    def use_user_input_allowable_stresses(self: "Self", value: "bool") -> None:
        pythonnet_property_set(
            self.wrapped,
            "UseUserInputAllowableStresses",
            bool(value) if value is not None else False,
        )

    @property
    @exception_bridge
    def user_specified_external_teeth_stress_concentration_factor(
        self: "Self",
    ) -> "float":
        """float"""
        temp = pythonnet_property_get(
            self.wrapped, "UserSpecifiedExternalTeethStressConcentrationFactor"
        )

        if temp is None:
            return 0.0

        return temp

    @user_specified_external_teeth_stress_concentration_factor.setter
    @exception_bridge
    @enforce_parameter_types
    def user_specified_external_teeth_stress_concentration_factor(
        self: "Self", value: "float"
    ) -> None:
        pythonnet_property_set(
            self.wrapped,
            "UserSpecifiedExternalTeethStressConcentrationFactor",
            float(value) if value is not None else 0.0,
        )

    @property
    @exception_bridge
    def user_specified_internal_teeth_stress_concentration_factor(
        self: "Self",
    ) -> "float":
        """float"""
        temp = pythonnet_property_get(
            self.wrapped, "UserSpecifiedInternalTeethStressConcentrationFactor"
        )

        if temp is None:
            return 0.0

        return temp

    @user_specified_internal_teeth_stress_concentration_factor.setter
    @exception_bridge
    @enforce_parameter_types
    def user_specified_internal_teeth_stress_concentration_factor(
        self: "Self", value: "float"
    ) -> None:
        pythonnet_property_set(
            self.wrapped,
            "UserSpecifiedInternalTeethStressConcentrationFactor",
            float(value) if value is not None else 0.0,
        )

    @property
    @exception_bridge
    def wall_thickness(self: "Self") -> "float":
        """float

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "WallThickness")

        if temp is None:
            return 0.0

        return temp

    @property
    @exception_bridge
    def with_crown(self: "Self") -> "bool":
        """bool"""
        temp = pythonnet_property_get(self.wrapped, "WithCrown")

        if temp is None:
            return False

        return temp

    @with_crown.setter
    @exception_bridge
    @enforce_parameter_types
    def with_crown(self: "Self", value: "bool") -> None:
        pythonnet_property_set(
            self.wrapped, "WithCrown", bool(value) if value is not None else False
        )

    @property
    @exception_bridge
    def external_half(self: "Self") -> "_1626.SplineHalfDesign":
        """mastapy.detailed_rigid_connectors.splines.SplineHalfDesign

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "ExternalHalf")

        if temp is None:
            return None

        type_ = temp.GetType()
        return constructor.new(type_.Namespace, type_.Name)(temp)

    @property
    @exception_bridge
    def internal_half(self: "Self") -> "_1626.SplineHalfDesign":
        """mastapy.detailed_rigid_connectors.splines.SplineHalfDesign

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "InternalHalf")

        if temp is None:
            return None

        type_ = temp.GetType()
        return constructor.new(type_.Namespace, type_.Name)(temp)

    @property
    def cast_to(self: "Self") -> "_Cast_SplineJointDesign":
        """Cast to another type.

        Returns:
            _Cast_SplineJointDesign
        """
        return _Cast_SplineJointDesign(self)
