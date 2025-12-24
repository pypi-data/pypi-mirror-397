"""OilSeal"""

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
from mastapy._private.materials.efficiency import _404
from mastapy._private.system_model.part_model import _2717

_OIL_SEAL = python_net_import("SMT.MastaAPI.SystemModel.PartModel", "OilSeal")

if TYPE_CHECKING:
    from typing import Any, Tuple, Type, TypeVar, Union

    from mastapy._private.bearings.bearing_results import _2200
    from mastapy._private.materials.efficiency import _405, _406
    from mastapy._private.math_utility import _1750
    from mastapy._private.math_utility.measured_data import _1781
    from mastapy._private.system_model import _2451
    from mastapy._private.system_model.part_model import _2714, _2737, _2742

    Self = TypeVar("Self", bound="OilSeal")
    CastSelf = TypeVar("CastSelf", bound="OilSeal._Cast_OilSeal")


__docformat__ = "restructuredtext en"
__all__ = ("OilSeal",)


@extended_dataclass(frozen=True, slots=True, weakref_slot=True)
class _Cast_OilSeal:
    """Special nested class for casting OilSeal to subclasses."""

    __parent__: "OilSeal"

    @property
    def connector(self: "CastSelf") -> "_2717.Connector":
        return self.__parent__._cast(_2717.Connector)

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
    def oil_seal(self: "CastSelf") -> "OilSeal":
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
class OilSeal(_2717.Connector):
    """OilSeal

    This is a mastapy class.
    """

    TYPE: ClassVar["Type"] = _OIL_SEAL

    wrapped: "Any"

    def __post_init__(self: "Self") -> None:
        """Override of the post initialisation magic method."""
        if not hasattr(self.wrapped, "reference_count"):
            self.wrapped.reference_count = 0

        self.wrapped.reference_count += 1

    @property
    @exception_bridge
    def axle_seal_factor(self: "Self") -> "float":
        """float"""
        temp = pythonnet_property_get(self.wrapped, "AxleSealFactor")

        if temp is None:
            return 0.0

        return temp

    @axle_seal_factor.setter
    @exception_bridge
    @enforce_parameter_types
    def axle_seal_factor(self: "Self", value: "float") -> None:
        pythonnet_property_set(
            self.wrapped, "AxleSealFactor", float(value) if value is not None else 0.0
        )

    @property
    @exception_bridge
    def coefficient_of_friction(self: "Self") -> "float":
        """float"""
        temp = pythonnet_property_get(self.wrapped, "CoefficientOfFriction")

        if temp is None:
            return 0.0

        return temp

    @coefficient_of_friction.setter
    @exception_bridge
    @enforce_parameter_types
    def coefficient_of_friction(self: "Self", value: "float") -> None:
        pythonnet_property_set(
            self.wrapped,
            "CoefficientOfFriction",
            float(value) if value is not None else 0.0,
        )

    @property
    @exception_bridge
    def drag_torque_vs_rotational_speed(self: "Self") -> "_1750.Vector2DListAccessor":
        """mastapy.math_utility.Vector2DListAccessor"""
        temp = pythonnet_property_get(self.wrapped, "DragTorqueVsRotationalSpeed")

        if temp is None:
            return None

        type_ = temp.GetType()
        return constructor.new(type_.Namespace, type_.Name)(temp)

    @drag_torque_vs_rotational_speed.setter
    @exception_bridge
    @enforce_parameter_types
    def drag_torque_vs_rotational_speed(
        self: "Self", value: "_1750.Vector2DListAccessor"
    ) -> None:
        pythonnet_property_set(
            self.wrapped, "DragTorqueVsRotationalSpeed", value.wrapped
        )

    @property
    @exception_bridge
    def drag_torque_vs_rotational_speed_and_temperature(
        self: "Self",
    ) -> "_1781.GriddedSurfaceAccessor":
        """mastapy.math_utility.measured_data.GriddedSurfaceAccessor"""
        temp = pythonnet_property_get(
            self.wrapped, "DragTorqueVsRotationalSpeedAndTemperature"
        )

        if temp is None:
            return None

        type_ = temp.GetType()
        return constructor.new(type_.Namespace, type_.Name)(temp)

    @drag_torque_vs_rotational_speed_and_temperature.setter
    @exception_bridge
    @enforce_parameter_types
    def drag_torque_vs_rotational_speed_and_temperature(
        self: "Self", value: "_1781.GriddedSurfaceAccessor"
    ) -> None:
        pythonnet_property_set(
            self.wrapped, "DragTorqueVsRotationalSpeedAndTemperature", value.wrapped
        )

    @property
    @exception_bridge
    def inner_diameter(self: "Self") -> "float":
        """float

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "InnerDiameter")

        if temp is None:
            return 0.0

        return temp

    @property
    @exception_bridge
    def intercept_of_linear_equation_defining_the_effect_of_temperature(
        self: "Self",
    ) -> "float":
        """float"""
        temp = pythonnet_property_get(
            self.wrapped, "InterceptOfLinearEquationDefiningTheEffectOfTemperature"
        )

        if temp is None:
            return 0.0

        return temp

    @intercept_of_linear_equation_defining_the_effect_of_temperature.setter
    @exception_bridge
    @enforce_parameter_types
    def intercept_of_linear_equation_defining_the_effect_of_temperature(
        self: "Self", value: "float"
    ) -> None:
        pythonnet_property_set(
            self.wrapped,
            "InterceptOfLinearEquationDefiningTheEffectOfTemperature",
            float(value) if value is not None else 0.0,
        )

    @property
    @exception_bridge
    def oil_seal_characteristic_life(self: "Self") -> "float":
        """float"""
        temp = pythonnet_property_get(self.wrapped, "OilSealCharacteristicLife")

        if temp is None:
            return 0.0

        return temp

    @oil_seal_characteristic_life.setter
    @exception_bridge
    @enforce_parameter_types
    def oil_seal_characteristic_life(self: "Self", value: "float") -> None:
        pythonnet_property_set(
            self.wrapped,
            "OilSealCharacteristicLife",
            float(value) if value is not None else 0.0,
        )

    @property
    @exception_bridge
    def oil_seal_frictional_torque(self: "Self") -> "float":
        """float

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "OilSealFrictionalTorque")

        if temp is None:
            return 0.0

        return temp

    @property
    @exception_bridge
    def oil_seal_loss_calculation_method(
        self: "Self",
    ) -> "enum_with_selected_value.EnumWithSelectedValue_OilSealLossCalculationMethod":
        """EnumWithSelectedValue[mastapy.materials.efficiency.OilSealLossCalculationMethod]"""
        temp = pythonnet_property_get(self.wrapped, "OilSealLossCalculationMethod")

        if temp is None:
            return None

        value = enum_with_selected_value.EnumWithSelectedValue_OilSealLossCalculationMethod.wrapped_type()
        return enum_with_selected_value_runtime.create(temp, value)

    @oil_seal_loss_calculation_method.setter
    @exception_bridge
    @enforce_parameter_types
    def oil_seal_loss_calculation_method(
        self: "Self", value: "_404.OilSealLossCalculationMethod"
    ) -> None:
        wrapper_type = enum_with_selected_value_runtime.ENUM_WITH_SELECTED_VALUE
        enclosed_type = enum_with_selected_value.EnumWithSelectedValue_OilSealLossCalculationMethod.implicit_type()
        value = conversion.mp_to_pn_enum(value, enclosed_type)
        value = wrapper_type[enclosed_type](value)
        pythonnet_property_set(self.wrapped, "OilSealLossCalculationMethod", value)

    @property
    @exception_bridge
    def oil_seal_material(self: "Self") -> "_405.OilSealMaterialType":
        """mastapy.materials.efficiency.OilSealMaterialType"""
        temp = pythonnet_property_get(self.wrapped, "OilSealMaterial")

        if temp is None:
            return None

        value = conversion.pn_to_mp_enum(
            temp, "SMT.MastaAPI.Materials.Efficiency.OilSealMaterialType"
        )

        if value is None:
            return None

        return constructor.new_from_mastapy(
            "mastapy._private.materials.efficiency._405", "OilSealMaterialType"
        )(value)

    @oil_seal_material.setter
    @exception_bridge
    @enforce_parameter_types
    def oil_seal_material(self: "Self", value: "_405.OilSealMaterialType") -> None:
        value = conversion.mp_to_pn_enum(
            value, "SMT.MastaAPI.Materials.Efficiency.OilSealMaterialType"
        )
        pythonnet_property_set(self.wrapped, "OilSealMaterial", value)

    @property
    @exception_bridge
    def oil_seal_mean_time_before_failure(self: "Self") -> "float":
        """float"""
        temp = pythonnet_property_get(self.wrapped, "OilSealMeanTimeBeforeFailure")

        if temp is None:
            return 0.0

        return temp

    @oil_seal_mean_time_before_failure.setter
    @exception_bridge
    @enforce_parameter_types
    def oil_seal_mean_time_before_failure(self: "Self", value: "float") -> None:
        pythonnet_property_set(
            self.wrapped,
            "OilSealMeanTimeBeforeFailure",
            float(value) if value is not None else 0.0,
        )

    @property
    @exception_bridge
    def oil_seal_orientation(self: "Self") -> "_2200.Orientations":
        """mastapy.bearings.bearing_results.Orientations"""
        temp = pythonnet_property_get(self.wrapped, "OilSealOrientation")

        if temp is None:
            return None

        value = conversion.pn_to_mp_enum(
            temp, "SMT.MastaAPI.Bearings.BearingResults.Orientations"
        )

        if value is None:
            return None

        return constructor.new_from_mastapy(
            "mastapy._private.bearings.bearing_results._2200", "Orientations"
        )(value)

    @oil_seal_orientation.setter
    @exception_bridge
    @enforce_parameter_types
    def oil_seal_orientation(self: "Self", value: "_2200.Orientations") -> None:
        value = conversion.mp_to_pn_enum(
            value, "SMT.MastaAPI.Bearings.BearingResults.Orientations"
        )
        pythonnet_property_set(self.wrapped, "OilSealOrientation", value)

    @property
    @exception_bridge
    def oil_seal_type(self: "Self") -> "_406.OilSealType":
        """mastapy.materials.efficiency.OilSealType"""
        temp = pythonnet_property_get(self.wrapped, "OilSealType")

        if temp is None:
            return None

        value = conversion.pn_to_mp_enum(
            temp, "SMT.MastaAPI.Materials.Efficiency.OilSealType"
        )

        if value is None:
            return None

        return constructor.new_from_mastapy(
            "mastapy._private.materials.efficiency._406", "OilSealType"
        )(value)

    @oil_seal_type.setter
    @exception_bridge
    @enforce_parameter_types
    def oil_seal_type(self: "Self", value: "_406.OilSealType") -> None:
        value = conversion.mp_to_pn_enum(
            value, "SMT.MastaAPI.Materials.Efficiency.OilSealType"
        )
        pythonnet_property_set(self.wrapped, "OilSealType", value)

    @property
    @exception_bridge
    def outer_diameter(self: "Self") -> "float":
        """float

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "OuterDiameter")

        if temp is None:
            return 0.0

        return temp

    @property
    @exception_bridge
    def pressure_at_seal(self: "Self") -> "float":
        """float"""
        temp = pythonnet_property_get(self.wrapped, "PressureAtSeal")

        if temp is None:
            return 0.0

        return temp

    @pressure_at_seal.setter
    @exception_bridge
    @enforce_parameter_types
    def pressure_at_seal(self: "Self", value: "float") -> None:
        pythonnet_property_set(
            self.wrapped, "PressureAtSeal", float(value) if value is not None else 0.0
        )

    @property
    @exception_bridge
    def reference_shaft_diameter(self: "Self") -> "float":
        """float"""
        temp = pythonnet_property_get(self.wrapped, "ReferenceShaftDiameter")

        if temp is None:
            return 0.0

        return temp

    @reference_shaft_diameter.setter
    @exception_bridge
    @enforce_parameter_types
    def reference_shaft_diameter(self: "Self", value: "float") -> None:
        pythonnet_property_set(
            self.wrapped,
            "ReferenceShaftDiameter",
            float(value) if value is not None else 0.0,
        )

    @property
    @exception_bridge
    def slope_of_linear_equation_defining_the_effect_of_temperature(
        self: "Self",
    ) -> "float":
        """float"""
        temp = pythonnet_property_get(
            self.wrapped, "SlopeOfLinearEquationDefiningTheEffectOfTemperature"
        )

        if temp is None:
            return 0.0

        return temp

    @slope_of_linear_equation_defining_the_effect_of_temperature.setter
    @exception_bridge
    @enforce_parameter_types
    def slope_of_linear_equation_defining_the_effect_of_temperature(
        self: "Self", value: "float"
    ) -> None:
        pythonnet_property_set(
            self.wrapped,
            "SlopeOfLinearEquationDefiningTheEffectOfTemperature",
            float(value) if value is not None else 0.0,
        )

    @property
    @exception_bridge
    def thickness_in_radial_direction(self: "Self") -> "float":
        """float"""
        temp = pythonnet_property_get(self.wrapped, "ThicknessInRadialDirection")

        if temp is None:
            return 0.0

        return temp

    @thickness_in_radial_direction.setter
    @exception_bridge
    @enforce_parameter_types
    def thickness_in_radial_direction(self: "Self", value: "float") -> None:
        pythonnet_property_set(
            self.wrapped,
            "ThicknessInRadialDirection",
            float(value) if value is not None else 0.0,
        )

    @property
    @exception_bridge
    def viscosity_ratio(self: "Self") -> "float":
        """float"""
        temp = pythonnet_property_get(self.wrapped, "ViscosityRatio")

        if temp is None:
            return 0.0

        return temp

    @viscosity_ratio.setter
    @exception_bridge
    @enforce_parameter_types
    def viscosity_ratio(self: "Self", value: "float") -> None:
        pythonnet_property_set(
            self.wrapped, "ViscosityRatio", float(value) if value is not None else 0.0
        )

    @property
    @exception_bridge
    def width(self: "Self") -> "overridable.Overridable_float":
        """Overridable[float]"""
        temp = pythonnet_property_get(self.wrapped, "Width")

        if temp is None:
            return 0.0

        return constructor.new_from_mastapy(
            "mastapy._private._internal.implicit.overridable", "Overridable_float"
        )(temp)

    @width.setter
    @exception_bridge
    @enforce_parameter_types
    def width(self: "Self", value: "Union[float, Tuple[float, bool]]") -> None:
        wrapper_type = overridable.Overridable_float.wrapper_type()
        enclosed_type = overridable.Overridable_float.implicit_type()
        value, is_overridden = _unpack_overridable(value)
        value = wrapper_type[enclosed_type](
            enclosed_type(value) if value is not None else 0.0, is_overridden
        )
        pythonnet_property_set(self.wrapped, "Width", value)

    @property
    def cast_to(self: "Self") -> "_Cast_OilSeal":
        """Cast to another type.

        Returns:
            _Cast_OilSeal
        """
        return _Cast_OilSeal(self)
