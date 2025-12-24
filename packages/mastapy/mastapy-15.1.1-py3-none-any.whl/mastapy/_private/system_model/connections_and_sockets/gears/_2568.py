"""CylindricalGearMesh"""

from __future__ import annotations

from typing import TYPE_CHECKING, ClassVar

from mastapy._private._internal.dataclasses import extended_dataclass
from mastapy._private._internal.exception_bridge import exception_bridge
from mastapy._private._internal.exceptions import CastException
from mastapy._private._internal.list_with_selected_item import (
    promote_to_list_with_selected_item,
)
from mastapy._private._internal.overridable_constructor import _unpack_overridable
from mastapy._private._internal.python_net import (
    python_net_import,
    pythonnet_property_get,
    pythonnet_property_get_with_method,
    pythonnet_property_set,
    pythonnet_property_set_with_method,
)
from mastapy._private._internal.sentinels import ListWithSelectedItem_None
from mastapy._private._internal.type_enforcement import enforce_parameter_types

from mastapy._private._internal import (
    constructor,
    conversion,
    enum_with_selected_value_runtime,
    utility,
)
from mastapy._private._internal.implicit import (
    enum_with_selected_value,
    list_with_selected_item,
    overridable,
)
from mastapy._private.gears import _443
from mastapy._private.system_model.connections_and_sockets.gears import _2572
from mastapy._private.system_model.part_model import _2747

_DATABASE_WITH_SELECTED_ITEM = python_net_import(
    "SMT.MastaAPI.UtilityGUI.Databases", "DatabaseWithSelectedItem"
)
_CYLINDRICAL_GEAR_MESH = python_net_import(
    "SMT.MastaAPI.SystemModel.ConnectionsAndSockets.Gears", "CylindricalGearMesh"
)

if TYPE_CHECKING:
    from typing import Any, List, Tuple, Type, TypeVar, Union

    from mastapy._private.gears import _449, _450, _451, _454
    from mastapy._private.gears.gear_designs.cylindrical import _1150
    from mastapy._private.system_model import _2451
    from mastapy._private.system_model.connections_and_sockets import _2531, _2540
    from mastapy._private.system_model.part_model.gears import _2806, _2807

    Self = TypeVar("Self", bound="CylindricalGearMesh")
    CastSelf = TypeVar(
        "CastSelf", bound="CylindricalGearMesh._Cast_CylindricalGearMesh"
    )


__docformat__ = "restructuredtext en"
__all__ = ("CylindricalGearMesh",)


@extended_dataclass(frozen=True, slots=True, weakref_slot=True)
class _Cast_CylindricalGearMesh:
    """Special nested class for casting CylindricalGearMesh to subclasses."""

    __parent__: "CylindricalGearMesh"

    @property
    def gear_mesh(self: "CastSelf") -> "_2572.GearMesh":
        return self.__parent__._cast(_2572.GearMesh)

    @property
    def inter_mountable_component_connection(
        self: "CastSelf",
    ) -> "_2540.InterMountableComponentConnection":
        from mastapy._private.system_model.connections_and_sockets import _2540

        return self.__parent__._cast(_2540.InterMountableComponentConnection)

    @property
    def connection(self: "CastSelf") -> "_2531.Connection":
        from mastapy._private.system_model.connections_and_sockets import _2531

        return self.__parent__._cast(_2531.Connection)

    @property
    def design_entity(self: "CastSelf") -> "_2451.DesignEntity":
        from mastapy._private.system_model import _2451

        return self.__parent__._cast(_2451.DesignEntity)

    @property
    def cylindrical_gear_mesh(self: "CastSelf") -> "CylindricalGearMesh":
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
class CylindricalGearMesh(_2572.GearMesh):
    """CylindricalGearMesh

    This is a mastapy class.
    """

    TYPE: ClassVar["Type"] = _CYLINDRICAL_GEAR_MESH

    wrapped: "Any"

    def __post_init__(self: "Self") -> None:
        """Override of the post initialisation magic method."""
        if not hasattr(self.wrapped, "reference_count"):
            self.wrapped.reference_count = 0

        self.wrapped.reference_count += 1

    @property
    @exception_bridge
    def centre_distance(self: "Self") -> "float":
        """float"""
        temp = pythonnet_property_get(self.wrapped, "CentreDistance")

        if temp is None:
            return 0.0

        return temp

    @centre_distance.setter
    @exception_bridge
    @enforce_parameter_types
    def centre_distance(self: "Self", value: "float") -> None:
        pythonnet_property_set(
            self.wrapped, "CentreDistance", float(value) if value is not None else 0.0
        )

    @property
    @exception_bridge
    def centre_distance_range(self: "Self") -> "Tuple[float, float]":
        """Tuple[float, float]

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "CentreDistanceRange")

        if temp is None:
            return None

        value = conversion.pn_to_mp_range(temp)

        if value is None:
            return None

        return value

    @property
    @exception_bridge
    def centre_distance_with_normal_module_adjustment_by_scaling_entire_model(
        self: "Self",
    ) -> "float":
        """float"""
        temp = pythonnet_property_get(
            self.wrapped, "CentreDistanceWithNormalModuleAdjustmentByScalingEntireModel"
        )

        if temp is None:
            return 0.0

        return temp

    @centre_distance_with_normal_module_adjustment_by_scaling_entire_model.setter
    @exception_bridge
    @enforce_parameter_types
    def centre_distance_with_normal_module_adjustment_by_scaling_entire_model(
        self: "Self", value: "float"
    ) -> None:
        pythonnet_property_set(
            self.wrapped,
            "CentreDistanceWithNormalModuleAdjustmentByScalingEntireModel",
            float(value) if value is not None else 0.0,
        )

    @property
    @exception_bridge
    def effect_of_pocket_dimension(self: "Self") -> "overridable.Overridable_float":
        """Overridable[float]"""
        temp = pythonnet_property_get(self.wrapped, "EffectOfPocketDimension")

        if temp is None:
            return 0.0

        return constructor.new_from_mastapy(
            "mastapy._private._internal.implicit.overridable", "Overridable_float"
        )(temp)

    @effect_of_pocket_dimension.setter
    @exception_bridge
    @enforce_parameter_types
    def effect_of_pocket_dimension(
        self: "Self", value: "Union[float, Tuple[float, bool]]"
    ) -> None:
        wrapper_type = overridable.Overridable_float.wrapper_type()
        enclosed_type = overridable.Overridable_float.implicit_type()
        value, is_overridden = _unpack_overridable(value)
        value = wrapper_type[enclosed_type](
            enclosed_type(value) if value is not None else 0.0, is_overridden
        )
        pythonnet_property_set(self.wrapped, "EffectOfPocketDimension", value)

    @property
    @exception_bridge
    def hydraulic_length(self: "Self") -> "overridable.Overridable_float":
        """Overridable[float]"""
        temp = pythonnet_property_get(self.wrapped, "HydraulicLength")

        if temp is None:
            return 0.0

        return constructor.new_from_mastapy(
            "mastapy._private._internal.implicit.overridable", "Overridable_float"
        )(temp)

    @hydraulic_length.setter
    @exception_bridge
    @enforce_parameter_types
    def hydraulic_length(
        self: "Self", value: "Union[float, Tuple[float, bool]]"
    ) -> None:
        wrapper_type = overridable.Overridable_float.wrapper_type()
        enclosed_type = overridable.Overridable_float.implicit_type()
        value, is_overridden = _unpack_overridable(value)
        value = wrapper_type[enclosed_type](
            enclosed_type(value) if value is not None else 0.0, is_overridden
        )
        pythonnet_property_set(self.wrapped, "HydraulicLength", value)

    @property
    @exception_bridge
    def include_iso141792_no_load_gear_mesh_losses(self: "Self") -> "bool":
        """bool"""
        temp = pythonnet_property_get(
            self.wrapped, "IncludeISO141792NoLoadGearMeshLosses"
        )

        if temp is None:
            return False

        return temp

    @include_iso141792_no_load_gear_mesh_losses.setter
    @exception_bridge
    @enforce_parameter_types
    def include_iso141792_no_load_gear_mesh_losses(self: "Self", value: "bool") -> None:
        pythonnet_property_set(
            self.wrapped,
            "IncludeISO141792NoLoadGearMeshLosses",
            bool(value) if value is not None else False,
        )

    @property
    @exception_bridge
    def is_centre_distance_ready_to_change(self: "Self") -> "bool":
        """bool

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "IsCentreDistanceReadyToChange")

        if temp is None:
            return False

        return temp

    @property
    @exception_bridge
    def lubrication_method_for_no_load_losses(
        self: "Self",
    ) -> "enum_with_selected_value.EnumWithSelectedValue_LubricationMethodForNoLoadLossesCalc":
        """EnumWithSelectedValue[mastapy.gears.LubricationMethodForNoLoadLossesCalc]"""
        temp = pythonnet_property_get(self.wrapped, "LubricationMethodForNoLoadLosses")

        if temp is None:
            return None

        value = enum_with_selected_value.EnumWithSelectedValue_LubricationMethodForNoLoadLossesCalc.wrapped_type()
        return enum_with_selected_value_runtime.create(temp, value)

    @lubrication_method_for_no_load_losses.setter
    @exception_bridge
    @enforce_parameter_types
    def lubrication_method_for_no_load_losses(
        self: "Self", value: "_443.LubricationMethodForNoLoadLossesCalc"
    ) -> None:
        wrapper_type = enum_with_selected_value_runtime.ENUM_WITH_SELECTED_VALUE
        enclosed_type = enum_with_selected_value.EnumWithSelectedValue_LubricationMethodForNoLoadLossesCalc.implicit_type()
        value = conversion.mp_to_pn_enum(value, enclosed_type)
        value = wrapper_type[enclosed_type](value)
        pythonnet_property_set(self.wrapped, "LubricationMethodForNoLoadLosses", value)

    @property
    @exception_bridge
    def oil_flow_rate_constant(self: "Self") -> "float":
        """float"""
        temp = pythonnet_property_get(self.wrapped, "OilFlowRateConstant")

        if temp is None:
            return 0.0

        return temp

    @oil_flow_rate_constant.setter
    @exception_bridge
    @enforce_parameter_types
    def oil_flow_rate_constant(self: "Self", value: "float") -> None:
        pythonnet_property_set(
            self.wrapped,
            "OilFlowRateConstant",
            float(value) if value is not None else 0.0,
        )

    @property
    @exception_bridge
    def oil_flow_rate_specification_method(
        self: "Self",
    ) -> "_450.OilJetFlowRateSpecificationMethod":
        """mastapy.gears.OilJetFlowRateSpecificationMethod"""
        temp = pythonnet_property_get(self.wrapped, "OilFlowRateSpecificationMethod")

        if temp is None:
            return None

        value = conversion.pn_to_mp_enum(
            temp, "SMT.MastaAPI.Gears.OilJetFlowRateSpecificationMethod"
        )

        if value is None:
            return None

        return constructor.new_from_mastapy(
            "mastapy._private.gears._450", "OilJetFlowRateSpecificationMethod"
        )(value)

    @oil_flow_rate_specification_method.setter
    @exception_bridge
    @enforce_parameter_types
    def oil_flow_rate_specification_method(
        self: "Self", value: "_450.OilJetFlowRateSpecificationMethod"
    ) -> None:
        value = conversion.mp_to_pn_enum(
            value, "SMT.MastaAPI.Gears.OilJetFlowRateSpecificationMethod"
        )
        pythonnet_property_set(self.wrapped, "OilFlowRateSpecificationMethod", value)

    @property
    @exception_bridge
    def oil_injection_direction(self: "Self") -> "_449.GearMeshOilInjectionDirection":
        """mastapy.gears.GearMeshOilInjectionDirection"""
        temp = pythonnet_property_get(self.wrapped, "OilInjectionDirection")

        if temp is None:
            return None

        value = conversion.pn_to_mp_enum(
            temp, "SMT.MastaAPI.Gears.GearMeshOilInjectionDirection"
        )

        if value is None:
            return None

        return constructor.new_from_mastapy(
            "mastapy._private.gears._449", "GearMeshOilInjectionDirection"
        )(value)

    @oil_injection_direction.setter
    @exception_bridge
    @enforce_parameter_types
    def oil_injection_direction(
        self: "Self", value: "_449.GearMeshOilInjectionDirection"
    ) -> None:
        value = conversion.mp_to_pn_enum(
            value, "SMT.MastaAPI.Gears.GearMeshOilInjectionDirection"
        )
        pythonnet_property_set(self.wrapped, "OilInjectionDirection", value)

    @property
    @exception_bridge
    def oil_jet_velocity_constant(self: "Self") -> "float":
        """float"""
        temp = pythonnet_property_get(self.wrapped, "OilJetVelocityConstant")

        if temp is None:
            return 0.0

        return temp

    @oil_jet_velocity_constant.setter
    @exception_bridge
    @enforce_parameter_types
    def oil_jet_velocity_constant(self: "Self", value: "float") -> None:
        pythonnet_property_set(
            self.wrapped,
            "OilJetVelocityConstant",
            float(value) if value is not None else 0.0,
        )

    @property
    @exception_bridge
    def oil_jet_velocity_specification_method(
        self: "Self",
    ) -> "_451.OilJetVelocitySpecificationMethod":
        """mastapy.gears.OilJetVelocitySpecificationMethod"""
        temp = pythonnet_property_get(self.wrapped, "OilJetVelocitySpecificationMethod")

        if temp is None:
            return None

        value = conversion.pn_to_mp_enum(
            temp, "SMT.MastaAPI.Gears.OilJetVelocitySpecificationMethod"
        )

        if value is None:
            return None

        return constructor.new_from_mastapy(
            "mastapy._private.gears._451", "OilJetVelocitySpecificationMethod"
        )(value)

    @oil_jet_velocity_specification_method.setter
    @exception_bridge
    @enforce_parameter_types
    def oil_jet_velocity_specification_method(
        self: "Self", value: "_451.OilJetVelocitySpecificationMethod"
    ) -> None:
        value = conversion.mp_to_pn_enum(
            value, "SMT.MastaAPI.Gears.OilJetVelocitySpecificationMethod"
        )
        pythonnet_property_set(self.wrapped, "OilJetVelocitySpecificationMethod", value)

    @property
    @exception_bridge
    def override_design_pocketing_power_loss_coefficients(self: "Self") -> "bool":
        """bool"""
        temp = pythonnet_property_get(
            self.wrapped, "OverrideDesignPocketingPowerLossCoefficients"
        )

        if temp is None:
            return False

        return temp

    @override_design_pocketing_power_loss_coefficients.setter
    @exception_bridge
    @enforce_parameter_types
    def override_design_pocketing_power_loss_coefficients(
        self: "Self", value: "bool"
    ) -> None:
        pythonnet_property_set(
            self.wrapped,
            "OverrideDesignPocketingPowerLossCoefficients",
            bool(value) if value is not None else False,
        )

    @property
    @exception_bridge
    def pocket_dimension(self: "Self") -> "float":
        """float

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "PocketDimension")

        if temp is None:
            return 0.0

        return temp

    @property
    @exception_bridge
    def pocketing_power_loss_coefficients_database(self: "Self") -> "str":
        """str"""
        temp = pythonnet_property_get_with_method(
            self.wrapped, "PocketingPowerLossCoefficientsDatabase", "SelectedItemName"
        )

        if temp is None:
            return ""

        return temp

    @pocketing_power_loss_coefficients_database.setter
    @exception_bridge
    @enforce_parameter_types
    def pocketing_power_loss_coefficients_database(self: "Self", value: "str") -> None:
        pythonnet_property_set_with_method(
            self.wrapped,
            "PocketingPowerLossCoefficientsDatabase",
            "SetSelectedItem",
            str(value) if value is not None else "",
        )

    @property
    @exception_bridge
    def pocketing_power_loss_correlation_factor(
        self: "Self",
    ) -> "overridable.Overridable_float":
        """Overridable[float]"""
        temp = pythonnet_property_get(
            self.wrapped, "PocketingPowerLossCorrelationFactor"
        )

        if temp is None:
            return 0.0

        return constructor.new_from_mastapy(
            "mastapy._private._internal.implicit.overridable", "Overridable_float"
        )(temp)

    @pocketing_power_loss_correlation_factor.setter
    @exception_bridge
    @enforce_parameter_types
    def pocketing_power_loss_correlation_factor(
        self: "Self", value: "Union[float, Tuple[float, bool]]"
    ) -> None:
        wrapper_type = overridable.Overridable_float.wrapper_type()
        enclosed_type = overridable.Overridable_float.implicit_type()
        value, is_overridden = _unpack_overridable(value)
        value = wrapper_type[enclosed_type](
            enclosed_type(value) if value is not None else 0.0, is_overridden
        )
        pythonnet_property_set(
            self.wrapped, "PocketingPowerLossCorrelationFactor", value
        )

    @property
    @exception_bridge
    def power_load_for_injection_loss_scripts(
        self: "Self",
    ) -> "list_with_selected_item.ListWithSelectedItem_PowerLoad":
        """ListWithSelectedItem[mastapy.system_model.part_model.PowerLoad]"""
        temp = pythonnet_property_get(self.wrapped, "PowerLoadForInjectionLossScripts")

        if temp is None:
            return None

        selected_value = temp.SelectedValue

        if selected_value is None:
            return ListWithSelectedItem_None(temp)

        return constructor.new_from_mastapy(
            "mastapy._private._internal.implicit.list_with_selected_item",
            "ListWithSelectedItem_PowerLoad",
        )(temp)

    @power_load_for_injection_loss_scripts.setter
    @exception_bridge
    @enforce_parameter_types
    def power_load_for_injection_loss_scripts(
        self: "Self", value: "_2747.PowerLoad"
    ) -> None:
        generic_type = (
            list_with_selected_item.ListWithSelectedItem_PowerLoad.implicit_type()
        )
        value = promote_to_list_with_selected_item(value)
        value = conversion.mp_to_pn_smt_list_with_selected_item(
            self, value, generic_type
        )
        pythonnet_property_set(self.wrapped, "PowerLoadForInjectionLossScripts", value)

    @property
    @exception_bridge
    def volumetric_oil_air_mixture_ratio(
        self: "Self",
    ) -> "overridable.Overridable_float":
        """Overridable[float]"""
        temp = pythonnet_property_get(self.wrapped, "VolumetricOilAirMixtureRatio")

        if temp is None:
            return 0.0

        return constructor.new_from_mastapy(
            "mastapy._private._internal.implicit.overridable", "Overridable_float"
        )(temp)

    @volumetric_oil_air_mixture_ratio.setter
    @exception_bridge
    @enforce_parameter_types
    def volumetric_oil_air_mixture_ratio(
        self: "Self", value: "Union[float, Tuple[float, bool]]"
    ) -> None:
        wrapper_type = overridable.Overridable_float.wrapper_type()
        enclosed_type = overridable.Overridable_float.implicit_type()
        value, is_overridden = _unpack_overridable(value)
        value = wrapper_type[enclosed_type](
            enclosed_type(value) if value is not None else 0.0, is_overridden
        )
        pythonnet_property_set(self.wrapped, "VolumetricOilAirMixtureRatio", value)

    @property
    @exception_bridge
    def active_gear_mesh_design(self: "Self") -> "_1150.CylindricalGearMeshDesign":
        """mastapy.gears.gear_designs.cylindrical.CylindricalGearMeshDesign

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "ActiveGearMeshDesign")

        if temp is None:
            return None

        type_ = temp.GetType()
        return constructor.new(type_.Namespace, type_.Name)(temp)

    @property
    @exception_bridge
    def cylindrical_gear_mesh_design(self: "Self") -> "_1150.CylindricalGearMeshDesign":
        """mastapy.gears.gear_designs.cylindrical.CylindricalGearMeshDesign

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "CylindricalGearMeshDesign")

        if temp is None:
            return None

        type_ = temp.GetType()
        return constructor.new(type_.Namespace, type_.Name)(temp)

    @property
    @exception_bridge
    def cylindrical_gear_set(self: "Self") -> "_2807.CylindricalGearSet":
        """mastapy.system_model.part_model.gears.CylindricalGearSet

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "CylindricalGearSet")

        if temp is None:
            return None

        type_ = temp.GetType()
        return constructor.new(type_.Namespace, type_.Name)(temp)

    @property
    @exception_bridge
    def pocketing_power_loss_coefficients(
        self: "Self",
    ) -> "_454.PocketingPowerLossCoefficients":
        """mastapy.gears.PocketingPowerLossCoefficients

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "PocketingPowerLossCoefficients")

        if temp is None:
            return None

        type_ = temp.GetType()
        return constructor.new(type_.Namespace, type_.Name)(temp)

    @property
    @exception_bridge
    def cylindrical_gears(self: "Self") -> "List[_2806.CylindricalGear]":
        """List[mastapy.system_model.part_model.gears.CylindricalGear]

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "CylindricalGears")

        if temp is None:
            return None

        value = conversion.pn_to_mp_objects_in_list(temp)

        if value is None:
            return None

        return value

    @property
    def cast_to(self: "Self") -> "_Cast_CylindricalGearMesh":
        """Cast to another type.

        Returns:
            _Cast_CylindricalGearMesh
        """
        return _Cast_CylindricalGearMesh(self)
