"""ConstraintSwitchingBase"""

from __future__ import annotations

from typing import TYPE_CHECKING, ClassVar, Generic, TypeVar

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

from mastapy._private import _0
from mastapy._private._internal import (
    constructor,
    conversion,
    enum_with_selected_value_runtime,
    utility,
)
from mastapy._private._internal.implicit import enum_with_selected_value, overridable
from mastapy._private.nodal_analysis.varying_input_components import _109

_CONSTRAINT_SWITCHING_BASE = python_net_import(
    "SMT.MastaAPI.NodalAnalysis.VaryingInputComponents", "ConstraintSwitchingBase"
)

if TYPE_CHECKING:
    from typing import Any, Tuple, Type, Union

    from mastapy._private.math_utility import _1715
    from mastapy._private.nodal_analysis.varying_input_components import (
        _100,
        _105,
        _107,
    )

    Self = TypeVar("Self", bound="ConstraintSwitchingBase")
    CastSelf = TypeVar(
        "CastSelf", bound="ConstraintSwitchingBase._Cast_ConstraintSwitchingBase"
    )

TForceInput = TypeVar("TForceInput", bound="_100.AbstractVaryingInputComponent")
TDisplacementInput = TypeVar(
    "TDisplacementInput", bound="_100.AbstractVaryingInputComponent"
)

__docformat__ = "restructuredtext en"
__all__ = ("ConstraintSwitchingBase",)


@extended_dataclass(frozen=True, slots=True, weakref_slot=True)
class _Cast_ConstraintSwitchingBase:
    """Special nested class for casting ConstraintSwitchingBase to subclasses."""

    __parent__: "ConstraintSwitchingBase"

    @property
    def force_or_displacement_input(
        self: "CastSelf",
    ) -> "_105.ForceOrDisplacementInput":
        from mastapy._private.nodal_analysis.varying_input_components import _105

        return self.__parent__._cast(_105.ForceOrDisplacementInput)

    @property
    def moment_or_angle_input(self: "CastSelf") -> "_107.MomentOrAngleInput":
        from mastapy._private.nodal_analysis.varying_input_components import _107

        return self.__parent__._cast(_107.MomentOrAngleInput)

    @property
    def constraint_switching_base(self: "CastSelf") -> "ConstraintSwitchingBase":
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
class ConstraintSwitchingBase(_0.APIBase, Generic[TForceInput, TDisplacementInput]):
    """ConstraintSwitchingBase

    This is a mastapy class.

    Generic Types:
        TForceInput
        TDisplacementInput
    """

    TYPE: ClassVar["Type"] = _CONSTRAINT_SWITCHING_BASE

    wrapped: "Any"

    def __post_init__(self: "Self") -> None:
        """Override of the post initialisation magic method."""
        if not hasattr(self.wrapped, "reference_count"):
            self.wrapped.reference_count = 0

        self.wrapped.reference_count += 1

    @property
    @exception_bridge
    def constraint_axis(self: "Self") -> "_1715.DegreeOfFreedom":
        """mastapy.math_utility.DegreeOfFreedom

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "ConstraintAxis")

        if temp is None:
            return None

        value = conversion.pn_to_mp_enum(
            temp, "SMT.MastaAPI.MathUtility.DegreeOfFreedom"
        )

        if value is None:
            return None

        return constructor.new_from_mastapy(
            "mastapy._private.math_utility._1715", "DegreeOfFreedom"
        )(value)

    @property
    @exception_bridge
    def constraint_type(
        self: "Self",
    ) -> "enum_with_selected_value.EnumWithSelectedValue_ConstraintType":
        """EnumWithSelectedValue[mastapy.nodal_analysis.varying_input_components.ConstraintType]"""
        temp = pythonnet_property_get(self.wrapped, "ConstraintType")

        if temp is None:
            return None

        value = (
            enum_with_selected_value.EnumWithSelectedValue_ConstraintType.wrapped_type()
        )
        return enum_with_selected_value_runtime.create(temp, value)

    @constraint_type.setter
    @exception_bridge
    @enforce_parameter_types
    def constraint_type(self: "Self", value: "_109.ConstraintType") -> None:
        wrapper_type = enum_with_selected_value_runtime.ENUM_WITH_SELECTED_VALUE
        enclosed_type = enum_with_selected_value.EnumWithSelectedValue_ConstraintType.implicit_type()
        value = conversion.mp_to_pn_enum(value, enclosed_type)
        value = wrapper_type[enclosed_type](value)
        pythonnet_property_set(self.wrapped, "ConstraintType", value)

    @property
    @exception_bridge
    def displacement_overridable(self: "Self") -> "overridable.Overridable_float":
        """Overridable[float]"""
        temp = pythonnet_property_get(self.wrapped, "DisplacementOverridable")

        if temp is None:
            return 0.0

        return constructor.new_from_mastapy(
            "mastapy._private._internal.implicit.overridable", "Overridable_float"
        )(temp)

    @displacement_overridable.setter
    @exception_bridge
    @enforce_parameter_types
    def displacement_overridable(
        self: "Self", value: "Union[float, Tuple[float, bool]]"
    ) -> None:
        wrapper_type = overridable.Overridable_float.wrapper_type()
        enclosed_type = overridable.Overridable_float.implicit_type()
        value, is_overridden = _unpack_overridable(value)
        value = wrapper_type[enclosed_type](
            enclosed_type(value) if value is not None else 0.0, is_overridden
        )
        pythonnet_property_set(self.wrapped, "DisplacementOverridable", value)

    @property
    @exception_bridge
    def displacement_or_angle(self: "Self") -> "TDisplacementInput":
        """TDisplacementInput

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "DisplacementOrAngle")

        if temp is None:
            return None

        type_ = temp.GetType()
        return constructor.new(type_.Namespace, type_.Name)(temp)

    @property
    @exception_bridge
    def force_or_moment(self: "Self") -> "TForceInput":
        """TForceInput

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "ForceOrMoment")

        if temp is None:
            return None

        type_ = temp.GetType()
        return constructor.new(type_.Namespace, type_.Name)(temp)

    @property
    def cast_to(self: "Self") -> "_Cast_ConstraintSwitchingBase":
        """Cast to another type.

        Returns:
            _Cast_ConstraintSwitchingBase
        """
        return _Cast_ConstraintSwitchingBase(self)
