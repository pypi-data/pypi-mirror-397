"""CylindricalGearMeshLoadCase"""

from __future__ import annotations

from typing import TYPE_CHECKING, ClassVar

from mastapy._private._internal.dataclasses import extended_dataclass
from mastapy._private._internal.exception_bridge import exception_bridge
from mastapy._private._internal.exceptions import CastException
from mastapy._private._internal.overridable_constructor import _unpack_overridable
from mastapy._private._internal.python_net import (
    python_net_import,
    pythonnet_method_call,
    pythonnet_property_get,
    pythonnet_property_get_with_method,
    pythonnet_property_set,
    pythonnet_property_set_with_method,
)
from mastapy._private._internal.type_enforcement import enforce_parameter_types

from mastapy._private._internal import (
    constructor,
    conversion,
    overridable_enum_runtime,
    utility,
)
from mastapy._private._internal.implicit import overridable
from mastapy._private.gears import _443, _449, _450, _451
from mastapy._private.gears.rating.cylindrical.iso6336 import _623
from mastapy._private.system_model.analyses_and_results.static_loads import _7813

_DATABASE_WITH_SELECTED_ITEM = python_net_import(
    "SMT.MastaAPI.UtilityGUI.Databases", "DatabaseWithSelectedItem"
)
_CYLINDRICAL_GEAR_MESH_LOAD_CASE = python_net_import(
    "SMT.MastaAPI.SystemModel.AnalysesAndResults.StaticLoads",
    "CylindricalGearMeshLoadCase",
)

if TYPE_CHECKING:
    from typing import Any, List, Tuple, Type, TypeVar, Union

    from mastapy._private.gears import _446
    from mastapy._private.gears.materials import _721
    from mastapy._private.system_model.analyses_and_results import _2941, _2943, _2945
    from mastapy._private.system_model.analyses_and_results.static_loads import (
        _7770,
        _7785,
        _7832,
    )
    from mastapy._private.system_model.connections_and_sockets.gears import _2568

    Self = TypeVar("Self", bound="CylindricalGearMeshLoadCase")
    CastSelf = TypeVar(
        "CastSelf",
        bound="CylindricalGearMeshLoadCase._Cast_CylindricalGearMeshLoadCase",
    )


__docformat__ = "restructuredtext en"
__all__ = ("CylindricalGearMeshLoadCase",)


@extended_dataclass(frozen=True, slots=True, weakref_slot=True)
class _Cast_CylindricalGearMeshLoadCase:
    """Special nested class for casting CylindricalGearMeshLoadCase to subclasses."""

    __parent__: "CylindricalGearMeshLoadCase"

    @property
    def gear_mesh_load_case(self: "CastSelf") -> "_7813.GearMeshLoadCase":
        return self.__parent__._cast(_7813.GearMeshLoadCase)

    @property
    def inter_mountable_component_connection_load_case(
        self: "CastSelf",
    ) -> "_7832.InterMountableComponentConnectionLoadCase":
        from mastapy._private.system_model.analyses_and_results.static_loads import (
            _7832,
        )

        return self.__parent__._cast(_7832.InterMountableComponentConnectionLoadCase)

    @property
    def connection_load_case(self: "CastSelf") -> "_7770.ConnectionLoadCase":
        from mastapy._private.system_model.analyses_and_results.static_loads import (
            _7770,
        )

        return self.__parent__._cast(_7770.ConnectionLoadCase)

    @property
    def connection_analysis(self: "CastSelf") -> "_2941.ConnectionAnalysis":
        from mastapy._private.system_model.analyses_and_results import _2941

        return self.__parent__._cast(_2941.ConnectionAnalysis)

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
    def cylindrical_gear_mesh_load_case(
        self: "CastSelf",
    ) -> "CylindricalGearMeshLoadCase":
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
class CylindricalGearMeshLoadCase(_7813.GearMeshLoadCase):
    """CylindricalGearMeshLoadCase

    This is a mastapy class.
    """

    TYPE: ClassVar["Type"] = _CYLINDRICAL_GEAR_MESH_LOAD_CASE

    wrapped: "Any"

    def __post_init__(self: "Self") -> None:
        """Override of the post initialisation magic method."""
        if not hasattr(self.wrapped, "reference_count"):
            self.wrapped.reference_count = 0

        self.wrapped.reference_count += 1

    @property
    @exception_bridge
    def application_factor(self: "Self") -> "overridable.Overridable_float":
        """Overridable[float]"""
        temp = pythonnet_property_get(self.wrapped, "ApplicationFactor")

        if temp is None:
            return 0.0

        return constructor.new_from_mastapy(
            "mastapy._private._internal.implicit.overridable", "Overridable_float"
        )(temp)

    @application_factor.setter
    @exception_bridge
    @enforce_parameter_types
    def application_factor(
        self: "Self", value: "Union[float, Tuple[float, bool]]"
    ) -> None:
        wrapper_type = overridable.Overridable_float.wrapper_type()
        enclosed_type = overridable.Overridable_float.implicit_type()
        value, is_overridden = _unpack_overridable(value)
        value = wrapper_type[enclosed_type](
            enclosed_type(value) if value is not None else 0.0, is_overridden
        )
        pythonnet_property_set(self.wrapped, "ApplicationFactor", value)

    @property
    @exception_bridge
    def change_in_centre_distance_due_to_housing_thermal_effects(
        self: "Self",
    ) -> "float":
        """float

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(
            self.wrapped, "ChangeInCentreDistanceDueToHousingThermalEffects"
        )

        if temp is None:
            return 0.0

        return temp

    @property
    @exception_bridge
    def do_profile_modifications_compensate_for_the_deflections_at_actual_load(
        self: "Self",
    ) -> "bool":
        """bool"""
        temp = pythonnet_property_get(
            self.wrapped,
            "DoProfileModificationsCompensateForTheDeflectionsAtActualLoad",
        )

        if temp is None:
            return False

        return temp

    @do_profile_modifications_compensate_for_the_deflections_at_actual_load.setter
    @exception_bridge
    @enforce_parameter_types
    def do_profile_modifications_compensate_for_the_deflections_at_actual_load(
        self: "Self", value: "bool"
    ) -> None:
        pythonnet_property_set(
            self.wrapped,
            "DoProfileModificationsCompensateForTheDeflectionsAtActualLoad",
            bool(value) if value is not None else False,
        )

    @property
    @exception_bridge
    def dynamic_factor(self: "Self") -> "overridable.Overridable_float":
        """Overridable[float]"""
        temp = pythonnet_property_get(self.wrapped, "DynamicFactor")

        if temp is None:
            return 0.0

        return constructor.new_from_mastapy(
            "mastapy._private._internal.implicit.overridable", "Overridable_float"
        )(temp)

    @dynamic_factor.setter
    @exception_bridge
    @enforce_parameter_types
    def dynamic_factor(self: "Self", value: "Union[float, Tuple[float, bool]]") -> None:
        wrapper_type = overridable.Overridable_float.wrapper_type()
        enclosed_type = overridable.Overridable_float.implicit_type()
        value, is_overridden = _unpack_overridable(value)
        value = wrapper_type[enclosed_type](
            enclosed_type(value) if value is not None else 0.0, is_overridden
        )
        pythonnet_property_set(self.wrapped, "DynamicFactor", value)

    @property
    @exception_bridge
    def face_load_factor_bending(self: "Self") -> "overridable.Overridable_float":
        """Overridable[float]"""
        temp = pythonnet_property_get(self.wrapped, "FaceLoadFactorBending")

        if temp is None:
            return 0.0

        return constructor.new_from_mastapy(
            "mastapy._private._internal.implicit.overridable", "Overridable_float"
        )(temp)

    @face_load_factor_bending.setter
    @exception_bridge
    @enforce_parameter_types
    def face_load_factor_bending(
        self: "Self", value: "Union[float, Tuple[float, bool]]"
    ) -> None:
        wrapper_type = overridable.Overridable_float.wrapper_type()
        enclosed_type = overridable.Overridable_float.implicit_type()
        value, is_overridden = _unpack_overridable(value)
        value = wrapper_type[enclosed_type](
            enclosed_type(value) if value is not None else 0.0, is_overridden
        )
        pythonnet_property_set(self.wrapped, "FaceLoadFactorBending", value)

    @property
    @exception_bridge
    def face_load_factor_contact(self: "Self") -> "overridable.Overridable_float":
        """Overridable[float]"""
        temp = pythonnet_property_get(self.wrapped, "FaceLoadFactorContact")

        if temp is None:
            return 0.0

        return constructor.new_from_mastapy(
            "mastapy._private._internal.implicit.overridable", "Overridable_float"
        )(temp)

    @face_load_factor_contact.setter
    @exception_bridge
    @enforce_parameter_types
    def face_load_factor_contact(
        self: "Self", value: "Union[float, Tuple[float, bool]]"
    ) -> None:
        wrapper_type = overridable.Overridable_float.wrapper_type()
        enclosed_type = overridable.Overridable_float.implicit_type()
        value, is_overridden = _unpack_overridable(value)
        value = wrapper_type[enclosed_type](
            enclosed_type(value) if value is not None else 0.0, is_overridden
        )
        pythonnet_property_set(self.wrapped, "FaceLoadFactorContact", value)

    @property
    @exception_bridge
    def friction_loss_multiplier(self: "Self") -> "overridable.Overridable_float":
        """Overridable[float]"""
        temp = pythonnet_property_get(self.wrapped, "FrictionLossMultiplier")

        if temp is None:
            return 0.0

        return constructor.new_from_mastapy(
            "mastapy._private._internal.implicit.overridable", "Overridable_float"
        )(temp)

    @friction_loss_multiplier.setter
    @exception_bridge
    @enforce_parameter_types
    def friction_loss_multiplier(
        self: "Self", value: "Union[float, Tuple[float, bool]]"
    ) -> None:
        wrapper_type = overridable.Overridable_float.wrapper_type()
        enclosed_type = overridable.Overridable_float.implicit_type()
        value, is_overridden = _unpack_overridable(value)
        value = wrapper_type[enclosed_type](
            enclosed_type(value) if value is not None else 0.0, is_overridden
        )
        pythonnet_property_set(self.wrapped, "FrictionLossMultiplier", value)

    @property
    @exception_bridge
    def helical_gear_micro_geometry_option(
        self: "Self",
    ) -> "overridable.Overridable_HelicalGearMicroGeometryOption":
        """Overridable[mastapy.gears.rating.cylindrical.iso6336.HelicalGearMicroGeometryOption]"""
        temp = pythonnet_property_get(self.wrapped, "HelicalGearMicroGeometryOption")

        if temp is None:
            return None

        value = overridable.Overridable_HelicalGearMicroGeometryOption.wrapped_type()
        return overridable_enum_runtime.create(temp, value)

    @helical_gear_micro_geometry_option.setter
    @exception_bridge
    @enforce_parameter_types
    def helical_gear_micro_geometry_option(
        self: "Self",
        value: "Union[_623.HelicalGearMicroGeometryOption, Tuple[_623.HelicalGearMicroGeometryOption, bool]]",
    ) -> None:
        wrapper_type = (
            overridable.Overridable_HelicalGearMicroGeometryOption.wrapper_type()
        )
        enclosed_type = (
            overridable.Overridable_HelicalGearMicroGeometryOption.implicit_type()
        )
        value, is_overridden = _unpack_overridable(value)
        value = conversion.mp_to_pn_enum(value, enclosed_type)
        value = wrapper_type[enclosed_type](
            value if value is not None else None, is_overridden
        )
        pythonnet_property_set(self.wrapped, "HelicalGearMicroGeometryOption", value)

    @property
    @exception_bridge
    def iso14179_part_1_coefficient_of_friction_constants_and_exponents_database(
        self: "Self",
    ) -> "str":
        """str"""
        temp = pythonnet_property_get_with_method(
            self.wrapped,
            "ISO14179Part1CoefficientOfFrictionConstantsAndExponentsDatabase",
            "SelectedItemName",
        )

        if temp is None:
            return ""

        return temp

    @iso14179_part_1_coefficient_of_friction_constants_and_exponents_database.setter
    @exception_bridge
    @enforce_parameter_types
    def iso14179_part_1_coefficient_of_friction_constants_and_exponents_database(
        self: "Self", value: "str"
    ) -> None:
        pythonnet_property_set_with_method(
            self.wrapped,
            "ISO14179Part1CoefficientOfFrictionConstantsAndExponentsDatabase",
            "SetSelectedItem",
            str(value) if value is not None else "",
        )

    @property
    @exception_bridge
    def lubrication_method_for_no_load_losses(
        self: "Self",
    ) -> "overridable.Overridable_LubricationMethodForNoLoadLossesCalc":
        """Overridable[mastapy.gears.LubricationMethodForNoLoadLossesCalc]"""
        temp = pythonnet_property_get(self.wrapped, "LubricationMethodForNoLoadLosses")

        if temp is None:
            return None

        value = (
            overridable.Overridable_LubricationMethodForNoLoadLossesCalc.wrapped_type()
        )
        return overridable_enum_runtime.create(temp, value)

    @lubrication_method_for_no_load_losses.setter
    @exception_bridge
    @enforce_parameter_types
    def lubrication_method_for_no_load_losses(
        self: "Self",
        value: "Union[_443.LubricationMethodForNoLoadLossesCalc, Tuple[_443.LubricationMethodForNoLoadLossesCalc, bool]]",
    ) -> None:
        wrapper_type = (
            overridable.Overridable_LubricationMethodForNoLoadLossesCalc.wrapper_type()
        )
        enclosed_type = (
            overridable.Overridable_LubricationMethodForNoLoadLossesCalc.implicit_type()
        )
        value, is_overridden = _unpack_overridable(value)
        value = conversion.mp_to_pn_enum(value, enclosed_type)
        value = wrapper_type[enclosed_type](
            value if value is not None else None, is_overridden
        )
        pythonnet_property_set(self.wrapped, "LubricationMethodForNoLoadLosses", value)

    @property
    @exception_bridge
    def maximum_number_of_times_out_of_contact_before_being_considered_converged(
        self: "Self",
    ) -> "overridable.Overridable_int":
        """Overridable[int]"""
        temp = pythonnet_property_get(
            self.wrapped,
            "MaximumNumberOfTimesOutOfContactBeforeBeingConsideredConverged",
        )

        if temp is None:
            return 0

        return constructor.new_from_mastapy(
            "mastapy._private._internal.implicit.overridable", "Overridable_int"
        )(temp)

    @maximum_number_of_times_out_of_contact_before_being_considered_converged.setter
    @exception_bridge
    @enforce_parameter_types
    def maximum_number_of_times_out_of_contact_before_being_considered_converged(
        self: "Self", value: "Union[int, Tuple[int, bool]]"
    ) -> None:
        wrapper_type = overridable.Overridable_int.wrapper_type()
        enclosed_type = overridable.Overridable_int.implicit_type()
        value, is_overridden = _unpack_overridable(value)
        value = wrapper_type[enclosed_type](
            enclosed_type(value) if value is not None else 0, is_overridden
        )
        pythonnet_property_set(
            self.wrapped,
            "MaximumNumberOfTimesOutOfContactBeforeBeingConsideredConverged",
            value,
        )

    @property
    @exception_bridge
    def micro_geometry_model_for_simple_mesh_stiffness(
        self: "Self",
    ) -> "_446.MicroGeometryModel":
        """mastapy.gears.MicroGeometryModel

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(
            self.wrapped, "MicroGeometryModelForSimpleMeshStiffness"
        )

        if temp is None:
            return None

        value = conversion.pn_to_mp_enum(temp, "SMT.MastaAPI.Gears.MicroGeometryModel")

        if value is None:
            return None

        return constructor.new_from_mastapy(
            "mastapy._private.gears._446", "MicroGeometryModel"
        )(value)

    @property
    @exception_bridge
    def misalignment(self: "Self") -> "overridable.Overridable_float":
        """Overridable[float]"""
        temp = pythonnet_property_get(self.wrapped, "Misalignment")

        if temp is None:
            return 0.0

        return constructor.new_from_mastapy(
            "mastapy._private._internal.implicit.overridable", "Overridable_float"
        )(temp)

    @misalignment.setter
    @exception_bridge
    @enforce_parameter_types
    def misalignment(self: "Self", value: "Union[float, Tuple[float, bool]]") -> None:
        wrapper_type = overridable.Overridable_float.wrapper_type()
        enclosed_type = overridable.Overridable_float.implicit_type()
        value, is_overridden = _unpack_overridable(value)
        value = wrapper_type[enclosed_type](
            enclosed_type(value) if value is not None else 0.0, is_overridden
        )
        pythonnet_property_set(self.wrapped, "Misalignment", value)

    @property
    @exception_bridge
    def misalignment_due_to_manufacturing_tolerances(
        self: "Self",
    ) -> "overridable.Overridable_float":
        """Overridable[float]"""
        temp = pythonnet_property_get(
            self.wrapped, "MisalignmentDueToManufacturingTolerances"
        )

        if temp is None:
            return 0.0

        return constructor.new_from_mastapy(
            "mastapy._private._internal.implicit.overridable", "Overridable_float"
        )(temp)

    @misalignment_due_to_manufacturing_tolerances.setter
    @exception_bridge
    @enforce_parameter_types
    def misalignment_due_to_manufacturing_tolerances(
        self: "Self", value: "Union[float, Tuple[float, bool]]"
    ) -> None:
        wrapper_type = overridable.Overridable_float.wrapper_type()
        enclosed_type = overridable.Overridable_float.implicit_type()
        value, is_overridden = _unpack_overridable(value)
        value = wrapper_type[enclosed_type](
            enclosed_type(value) if value is not None else 0.0, is_overridden
        )
        pythonnet_property_set(
            self.wrapped, "MisalignmentDueToManufacturingTolerances", value
        )

    @property
    @exception_bridge
    def oil_flow_rate_constant(self: "Self") -> "overridable.Overridable_float":
        """Overridable[float]"""
        temp = pythonnet_property_get(self.wrapped, "OilFlowRateConstant")

        if temp is None:
            return 0.0

        return constructor.new_from_mastapy(
            "mastapy._private._internal.implicit.overridable", "Overridable_float"
        )(temp)

    @oil_flow_rate_constant.setter
    @exception_bridge
    @enforce_parameter_types
    def oil_flow_rate_constant(
        self: "Self", value: "Union[float, Tuple[float, bool]]"
    ) -> None:
        wrapper_type = overridable.Overridable_float.wrapper_type()
        enclosed_type = overridable.Overridable_float.implicit_type()
        value, is_overridden = _unpack_overridable(value)
        value = wrapper_type[enclosed_type](
            enclosed_type(value) if value is not None else 0.0, is_overridden
        )
        pythonnet_property_set(self.wrapped, "OilFlowRateConstant", value)

    @property
    @exception_bridge
    def oil_flow_rate_specification_method(
        self: "Self",
    ) -> "overridable.Overridable_OilJetFlowRateSpecificationMethod":
        """Overridable[mastapy.gears.OilJetFlowRateSpecificationMethod]"""
        temp = pythonnet_property_get(self.wrapped, "OilFlowRateSpecificationMethod")

        if temp is None:
            return None

        value = overridable.Overridable_OilJetFlowRateSpecificationMethod.wrapped_type()
        return overridable_enum_runtime.create(temp, value)

    @oil_flow_rate_specification_method.setter
    @exception_bridge
    @enforce_parameter_types
    def oil_flow_rate_specification_method(
        self: "Self",
        value: "Union[_450.OilJetFlowRateSpecificationMethod, Tuple[_450.OilJetFlowRateSpecificationMethod, bool]]",
    ) -> None:
        wrapper_type = (
            overridable.Overridable_OilJetFlowRateSpecificationMethod.wrapper_type()
        )
        enclosed_type = (
            overridable.Overridable_OilJetFlowRateSpecificationMethod.implicit_type()
        )
        value, is_overridden = _unpack_overridable(value)
        value = conversion.mp_to_pn_enum(value, enclosed_type)
        value = wrapper_type[enclosed_type](
            value if value is not None else None, is_overridden
        )
        pythonnet_property_set(self.wrapped, "OilFlowRateSpecificationMethod", value)

    @property
    @exception_bridge
    def oil_injection_direction(
        self: "Self",
    ) -> "overridable.Overridable_GearMeshOilInjectionDirection":
        """Overridable[mastapy.gears.GearMeshOilInjectionDirection]"""
        temp = pythonnet_property_get(self.wrapped, "OilInjectionDirection")

        if temp is None:
            return None

        value = overridable.Overridable_GearMeshOilInjectionDirection.wrapped_type()
        return overridable_enum_runtime.create(temp, value)

    @oil_injection_direction.setter
    @exception_bridge
    @enforce_parameter_types
    def oil_injection_direction(
        self: "Self",
        value: "Union[_449.GearMeshOilInjectionDirection, Tuple[_449.GearMeshOilInjectionDirection, bool]]",
    ) -> None:
        wrapper_type = (
            overridable.Overridable_GearMeshOilInjectionDirection.wrapper_type()
        )
        enclosed_type = (
            overridable.Overridable_GearMeshOilInjectionDirection.implicit_type()
        )
        value, is_overridden = _unpack_overridable(value)
        value = conversion.mp_to_pn_enum(value, enclosed_type)
        value = wrapper_type[enclosed_type](
            value if value is not None else None, is_overridden
        )
        pythonnet_property_set(self.wrapped, "OilInjectionDirection", value)

    @property
    @exception_bridge
    def oil_jet_velocity_constant(self: "Self") -> "overridable.Overridable_float":
        """Overridable[float]"""
        temp = pythonnet_property_get(self.wrapped, "OilJetVelocityConstant")

        if temp is None:
            return 0.0

        return constructor.new_from_mastapy(
            "mastapy._private._internal.implicit.overridable", "Overridable_float"
        )(temp)

    @oil_jet_velocity_constant.setter
    @exception_bridge
    @enforce_parameter_types
    def oil_jet_velocity_constant(
        self: "Self", value: "Union[float, Tuple[float, bool]]"
    ) -> None:
        wrapper_type = overridable.Overridable_float.wrapper_type()
        enclosed_type = overridable.Overridable_float.implicit_type()
        value, is_overridden = _unpack_overridable(value)
        value = wrapper_type[enclosed_type](
            enclosed_type(value) if value is not None else 0.0, is_overridden
        )
        pythonnet_property_set(self.wrapped, "OilJetVelocityConstant", value)

    @property
    @exception_bridge
    def oil_jet_velocity_specification_method(
        self: "Self",
    ) -> "overridable.Overridable_OilJetVelocitySpecificationMethod":
        """Overridable[mastapy.gears.OilJetVelocitySpecificationMethod]"""
        temp = pythonnet_property_get(self.wrapped, "OilJetVelocitySpecificationMethod")

        if temp is None:
            return None

        value = overridable.Overridable_OilJetVelocitySpecificationMethod.wrapped_type()
        return overridable_enum_runtime.create(temp, value)

    @oil_jet_velocity_specification_method.setter
    @exception_bridge
    @enforce_parameter_types
    def oil_jet_velocity_specification_method(
        self: "Self",
        value: "Union[_451.OilJetVelocitySpecificationMethod, Tuple[_451.OilJetVelocitySpecificationMethod, bool]]",
    ) -> None:
        wrapper_type = (
            overridable.Overridable_OilJetVelocitySpecificationMethod.wrapper_type()
        )
        enclosed_type = (
            overridable.Overridable_OilJetVelocitySpecificationMethod.implicit_type()
        )
        value, is_overridden = _unpack_overridable(value)
        value = conversion.mp_to_pn_enum(value, enclosed_type)
        value = wrapper_type[enclosed_type](
            value if value is not None else None, is_overridden
        )
        pythonnet_property_set(self.wrapped, "OilJetVelocitySpecificationMethod", value)

    @property
    @exception_bridge
    def override_misalignment_in_system_deflection_and_ltca(self: "Self") -> "bool":
        """bool"""
        temp = pythonnet_property_get(
            self.wrapped, "OverrideMisalignmentInSystemDeflectionAndLTCA"
        )

        if temp is None:
            return False

        return temp

    @override_misalignment_in_system_deflection_and_ltca.setter
    @exception_bridge
    @enforce_parameter_types
    def override_misalignment_in_system_deflection_and_ltca(
        self: "Self", value: "bool"
    ) -> None:
        pythonnet_property_set(
            self.wrapped,
            "OverrideMisalignmentInSystemDeflectionAndLTCA",
            bool(value) if value is not None else False,
        )

    @property
    @exception_bridge
    def permissible_specific_lubricant_film_thickness(
        self: "Self",
    ) -> "overridable.Overridable_float":
        """Overridable[float]"""
        temp = pythonnet_property_get(
            self.wrapped, "PermissibleSpecificLubricantFilmThickness"
        )

        if temp is None:
            return 0.0

        return constructor.new_from_mastapy(
            "mastapy._private._internal.implicit.overridable", "Overridable_float"
        )(temp)

    @permissible_specific_lubricant_film_thickness.setter
    @exception_bridge
    @enforce_parameter_types
    def permissible_specific_lubricant_film_thickness(
        self: "Self", value: "Union[float, Tuple[float, bool]]"
    ) -> None:
        wrapper_type = overridable.Overridable_float.wrapper_type()
        enclosed_type = overridable.Overridable_float.implicit_type()
        value, is_overridden = _unpack_overridable(value)
        value = wrapper_type[enclosed_type](
            enclosed_type(value) if value is not None else 0.0, is_overridden
        )
        pythonnet_property_set(
            self.wrapped, "PermissibleSpecificLubricantFilmThickness", value
        )

    @property
    @exception_bridge
    def transverse_load_factor_bending(self: "Self") -> "overridable.Overridable_float":
        """Overridable[float]"""
        temp = pythonnet_property_get(self.wrapped, "TransverseLoadFactorBending")

        if temp is None:
            return 0.0

        return constructor.new_from_mastapy(
            "mastapy._private._internal.implicit.overridable", "Overridable_float"
        )(temp)

    @transverse_load_factor_bending.setter
    @exception_bridge
    @enforce_parameter_types
    def transverse_load_factor_bending(
        self: "Self", value: "Union[float, Tuple[float, bool]]"
    ) -> None:
        wrapper_type = overridable.Overridable_float.wrapper_type()
        enclosed_type = overridable.Overridable_float.implicit_type()
        value, is_overridden = _unpack_overridable(value)
        value = wrapper_type[enclosed_type](
            enclosed_type(value) if value is not None else 0.0, is_overridden
        )
        pythonnet_property_set(self.wrapped, "TransverseLoadFactorBending", value)

    @property
    @exception_bridge
    def transverse_load_factor_contact(self: "Self") -> "overridable.Overridable_float":
        """Overridable[float]"""
        temp = pythonnet_property_get(self.wrapped, "TransverseLoadFactorContact")

        if temp is None:
            return 0.0

        return constructor.new_from_mastapy(
            "mastapy._private._internal.implicit.overridable", "Overridable_float"
        )(temp)

    @transverse_load_factor_contact.setter
    @exception_bridge
    @enforce_parameter_types
    def transverse_load_factor_contact(
        self: "Self", value: "Union[float, Tuple[float, bool]]"
    ) -> None:
        wrapper_type = overridable.Overridable_float.wrapper_type()
        enclosed_type = overridable.Overridable_float.implicit_type()
        value, is_overridden = _unpack_overridable(value)
        value = wrapper_type[enclosed_type](
            enclosed_type(value) if value is not None else 0.0, is_overridden
        )
        pythonnet_property_set(self.wrapped, "TransverseLoadFactorContact", value)

    @property
    @exception_bridge
    def use_design_iso14179_part_1_coefficient_of_friction_constants_and_exponents(
        self: "Self",
    ) -> "bool":
        """bool"""
        temp = pythonnet_property_get(
            self.wrapped,
            "UseDesignISO14179Part1CoefficientOfFrictionConstantsAndExponents",
        )

        if temp is None:
            return False

        return temp

    @use_design_iso14179_part_1_coefficient_of_friction_constants_and_exponents.setter
    @exception_bridge
    @enforce_parameter_types
    def use_design_iso14179_part_1_coefficient_of_friction_constants_and_exponents(
        self: "Self", value: "bool"
    ) -> None:
        pythonnet_property_set(
            self.wrapped,
            "UseDesignISO14179Part1CoefficientOfFrictionConstantsAndExponents",
            bool(value) if value is not None else False,
        )

    @property
    @exception_bridge
    def user_specified_coefficient_of_friction(
        self: "Self",
    ) -> "overridable.Overridable_float":
        """Overridable[float]"""
        temp = pythonnet_property_get(
            self.wrapped, "UserSpecifiedCoefficientOfFriction"
        )

        if temp is None:
            return 0.0

        return constructor.new_from_mastapy(
            "mastapy._private._internal.implicit.overridable", "Overridable_float"
        )(temp)

    @user_specified_coefficient_of_friction.setter
    @exception_bridge
    @enforce_parameter_types
    def user_specified_coefficient_of_friction(
        self: "Self", value: "Union[float, Tuple[float, bool]]"
    ) -> None:
        wrapper_type = overridable.Overridable_float.wrapper_type()
        enclosed_type = overridable.Overridable_float.implicit_type()
        value, is_overridden = _unpack_overridable(value)
        value = wrapper_type[enclosed_type](
            enclosed_type(value) if value is not None else 0.0, is_overridden
        )
        pythonnet_property_set(
            self.wrapped, "UserSpecifiedCoefficientOfFriction", value
        )

    @property
    @exception_bridge
    def user_specified_tooth_loss_factor(
        self: "Self",
    ) -> "overridable.Overridable_float":
        """Overridable[float]"""
        temp = pythonnet_property_get(self.wrapped, "UserSpecifiedToothLossFactor")

        if temp is None:
            return 0.0

        return constructor.new_from_mastapy(
            "mastapy._private._internal.implicit.overridable", "Overridable_float"
        )(temp)

    @user_specified_tooth_loss_factor.setter
    @exception_bridge
    @enforce_parameter_types
    def user_specified_tooth_loss_factor(
        self: "Self", value: "Union[float, Tuple[float, bool]]"
    ) -> None:
        wrapper_type = overridable.Overridable_float.wrapper_type()
        enclosed_type = overridable.Overridable_float.implicit_type()
        value, is_overridden = _unpack_overridable(value)
        value = wrapper_type[enclosed_type](
            enclosed_type(value) if value is not None else 0.0, is_overridden
        )
        pythonnet_property_set(self.wrapped, "UserSpecifiedToothLossFactor", value)

    @property
    @exception_bridge
    def volumetric_oil_air_mixture_ratio(self: "Self") -> "float":
        """float

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "VolumetricOilAirMixtureRatio")

        if temp is None:
            return 0.0

        return temp

    @property
    @exception_bridge
    def connection_design(self: "Self") -> "_2568.CylindricalGearMesh":
        """mastapy.system_model.connections_and_sockets.gears.CylindricalGearMesh

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "ConnectionDesign")

        if temp is None:
            return None

        type_ = temp.GetType()
        return constructor.new(type_.Namespace, type_.Name)(temp)

    @property
    @exception_bridge
    def iso14179_coefficient_of_friction_constants_and_exponents(
        self: "Self",
    ) -> "_721.ISOTR1417912001CoefficientOfFrictionConstants":
        """mastapy.gears.materials.ISOTR1417912001CoefficientOfFrictionConstants

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(
            self.wrapped, "ISO14179CoefficientOfFrictionConstantsAndExponents"
        )

        if temp is None:
            return None

        type_ = temp.GetType()
        return constructor.new(type_.Namespace, type_.Name)(temp)

    @property
    @exception_bridge
    def planetaries(self: "Self") -> "List[CylindricalGearMeshLoadCase]":
        """List[mastapy.system_model.analyses_and_results.static_loads.CylindricalGearMeshLoadCase]

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "Planetaries")

        if temp is None:
            return None

        value = conversion.pn_to_mp_objects_in_list(temp)

        if value is None:
            return None

        return value

    @exception_bridge
    def get_harmonic_load_data_for_import(
        self: "Self",
    ) -> "_7785.CylindricalGearSetHarmonicLoadData":
        """mastapy.system_model.analyses_and_results.static_loads.CylindricalGearSetHarmonicLoadData"""
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
    def cast_to(self: "Self") -> "_Cast_CylindricalGearMeshLoadCase":
        """Cast to another type.

        Returns:
            _Cast_CylindricalGearMeshLoadCase
        """
        return _Cast_CylindricalGearMeshLoadCase(self)
