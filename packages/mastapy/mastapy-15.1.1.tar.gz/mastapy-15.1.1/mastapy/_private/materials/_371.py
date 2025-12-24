"""Material"""

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

from mastapy._private._internal import constructor, conversion, utility
from mastapy._private.utility.databases import _2061

_MATERIAL = python_net_import("SMT.MastaAPI.Materials", "Material")

if TYPE_CHECKING:
    from typing import Any, Type, TypeVar

    from mastapy._private.bolts import _1678, _1682
    from mastapy._private.cycloidal import _1668, _1675
    from mastapy._private.detailed_rigid_connectors.splines import _1628
    from mastapy._private.electric_machines import _1430, _1444, _1464, _1479
    from mastapy._private.gears.materials import (
        _696,
        _699,
        _701,
        _706,
        _710,
        _719,
        _724,
        _728,
    )
    from mastapy._private.materials import _345, _360, _376
    from mastapy._private.shafts import _24

    Self = TypeVar("Self", bound="Material")
    CastSelf = TypeVar("CastSelf", bound="Material._Cast_Material")


__docformat__ = "restructuredtext en"
__all__ = ("Material",)


@extended_dataclass(frozen=True, slots=True, weakref_slot=True)
class _Cast_Material:
    """Special nested class for casting Material to subclasses."""

    __parent__: "Material"

    @property
    def named_database_item(self: "CastSelf") -> "_2061.NamedDatabaseItem":
        return self.__parent__._cast(_2061.NamedDatabaseItem)

    @property
    def shaft_material(self: "CastSelf") -> "_24.ShaftMaterial":
        from mastapy._private.shafts import _24

        return self.__parent__._cast(_24.ShaftMaterial)

    @property
    def bearing_material(self: "CastSelf") -> "_345.BearingMaterial":
        from mastapy._private.materials import _345

        return self.__parent__._cast(_345.BearingMaterial)

    @property
    def agma_cylindrical_gear_material(
        self: "CastSelf",
    ) -> "_696.AGMACylindricalGearMaterial":
        from mastapy._private.gears.materials import _696

        return self.__parent__._cast(_696.AGMACylindricalGearMaterial)

    @property
    def bevel_gear_iso_material(self: "CastSelf") -> "_699.BevelGearISOMaterial":
        from mastapy._private.gears.materials import _699

        return self.__parent__._cast(_699.BevelGearISOMaterial)

    @property
    def bevel_gear_material(self: "CastSelf") -> "_701.BevelGearMaterial":
        from mastapy._private.gears.materials import _701

        return self.__parent__._cast(_701.BevelGearMaterial)

    @property
    def cylindrical_gear_material(self: "CastSelf") -> "_706.CylindricalGearMaterial":
        from mastapy._private.gears.materials import _706

        return self.__parent__._cast(_706.CylindricalGearMaterial)

    @property
    def gear_material(self: "CastSelf") -> "_710.GearMaterial":
        from mastapy._private.gears.materials import _710

        return self.__parent__._cast(_710.GearMaterial)

    @property
    def iso_cylindrical_gear_material(
        self: "CastSelf",
    ) -> "_719.ISOCylindricalGearMaterial":
        from mastapy._private.gears.materials import _719

        return self.__parent__._cast(_719.ISOCylindricalGearMaterial)

    @property
    def klingelnberg_cyclo_palloid_conical_gear_material(
        self: "CastSelf",
    ) -> "_724.KlingelnbergCycloPalloidConicalGearMaterial":
        from mastapy._private.gears.materials import _724

        return self.__parent__._cast(_724.KlingelnbergCycloPalloidConicalGearMaterial)

    @property
    def plastic_cylindrical_gear_material(
        self: "CastSelf",
    ) -> "_728.PlasticCylindricalGearMaterial":
        from mastapy._private.gears.materials import _728

        return self.__parent__._cast(_728.PlasticCylindricalGearMaterial)

    @property
    def general_electric_machine_material(
        self: "CastSelf",
    ) -> "_1430.GeneralElectricMachineMaterial":
        from mastapy._private.electric_machines import _1430

        return self.__parent__._cast(_1430.GeneralElectricMachineMaterial)

    @property
    def magnet_material(self: "CastSelf") -> "_1444.MagnetMaterial":
        from mastapy._private.electric_machines import _1444

        return self.__parent__._cast(_1444.MagnetMaterial)

    @property
    def stator_rotor_material(self: "CastSelf") -> "_1464.StatorRotorMaterial":
        from mastapy._private.electric_machines import _1464

        return self.__parent__._cast(_1464.StatorRotorMaterial)

    @property
    def winding_material(self: "CastSelf") -> "_1479.WindingMaterial":
        from mastapy._private.electric_machines import _1479

        return self.__parent__._cast(_1479.WindingMaterial)

    @property
    def spline_material(self: "CastSelf") -> "_1628.SplineMaterial":
        from mastapy._private.detailed_rigid_connectors.splines import _1628

        return self.__parent__._cast(_1628.SplineMaterial)

    @property
    def cycloidal_disc_material(self: "CastSelf") -> "_1668.CycloidalDiscMaterial":
        from mastapy._private.cycloidal import _1668

        return self.__parent__._cast(_1668.CycloidalDiscMaterial)

    @property
    def ring_pins_material(self: "CastSelf") -> "_1675.RingPinsMaterial":
        from mastapy._private.cycloidal import _1675

        return self.__parent__._cast(_1675.RingPinsMaterial)

    @property
    def bolted_joint_material(self: "CastSelf") -> "_1678.BoltedJointMaterial":
        from mastapy._private.bolts import _1678

        return self.__parent__._cast(_1678.BoltedJointMaterial)

    @property
    def bolt_material(self: "CastSelf") -> "_1682.BoltMaterial":
        from mastapy._private.bolts import _1682

        return self.__parent__._cast(_1682.BoltMaterial)

    @property
    def material(self: "CastSelf") -> "Material":
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
class Material(_2061.NamedDatabaseItem):
    """Material

    This is a mastapy class.
    """

    TYPE: ClassVar["Type"] = _MATERIAL

    wrapped: "Any"

    def __post_init__(self: "Self") -> None:
        """Override of the post initialisation magic method."""
        if not hasattr(self.wrapped, "reference_count"):
            self.wrapped.reference_count = 0

        self.wrapped.reference_count += 1

    @property
    @exception_bridge
    def coefficient_of_thermal_expansion(self: "Self") -> "float":
        """float"""
        temp = pythonnet_property_get(self.wrapped, "CoefficientOfThermalExpansion")

        if temp is None:
            return 0.0

        return temp

    @coefficient_of_thermal_expansion.setter
    @exception_bridge
    @enforce_parameter_types
    def coefficient_of_thermal_expansion(self: "Self", value: "float") -> None:
        pythonnet_property_set(
            self.wrapped,
            "CoefficientOfThermalExpansion",
            float(value) if value is not None else 0.0,
        )

    @property
    @exception_bridge
    def cost_per_unit_mass(self: "Self") -> "float":
        """float"""
        temp = pythonnet_property_get(self.wrapped, "CostPerUnitMass")

        if temp is None:
            return 0.0

        return temp

    @cost_per_unit_mass.setter
    @exception_bridge
    @enforce_parameter_types
    def cost_per_unit_mass(self: "Self", value: "float") -> None:
        pythonnet_property_set(
            self.wrapped, "CostPerUnitMass", float(value) if value is not None else 0.0
        )

    @property
    @exception_bridge
    def density(self: "Self") -> "float":
        """float"""
        temp = pythonnet_property_get(self.wrapped, "Density")

        if temp is None:
            return 0.0

        return temp

    @density.setter
    @exception_bridge
    @enforce_parameter_types
    def density(self: "Self", value: "float") -> None:
        pythonnet_property_set(
            self.wrapped, "Density", float(value) if value is not None else 0.0
        )

    @property
    @exception_bridge
    def hardness_type(self: "Self") -> "_360.HardnessType":
        """mastapy.materials.HardnessType"""
        temp = pythonnet_property_get(self.wrapped, "HardnessType")

        if temp is None:
            return None

        value = conversion.pn_to_mp_enum(temp, "SMT.MastaAPI.Materials.HardnessType")

        if value is None:
            return None

        return constructor.new_from_mastapy(
            "mastapy._private.materials._360", "HardnessType"
        )(value)

    @hardness_type.setter
    @exception_bridge
    @enforce_parameter_types
    def hardness_type(self: "Self", value: "_360.HardnessType") -> None:
        value = conversion.mp_to_pn_enum(value, "SMT.MastaAPI.Materials.HardnessType")
        pythonnet_property_set(self.wrapped, "HardnessType", value)

    @property
    @exception_bridge
    def heat_conductivity(self: "Self") -> "float":
        """float"""
        temp = pythonnet_property_get(self.wrapped, "HeatConductivity")

        if temp is None:
            return 0.0

        return temp

    @heat_conductivity.setter
    @exception_bridge
    @enforce_parameter_types
    def heat_conductivity(self: "Self", value: "float") -> None:
        pythonnet_property_set(
            self.wrapped, "HeatConductivity", float(value) if value is not None else 0.0
        )

    @property
    @exception_bridge
    def material_name(self: "Self") -> "str":
        """str

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "MaterialName")

        if temp is None:
            return ""

        return temp

    @property
    @exception_bridge
    def maximum_allowable_temperature(self: "Self") -> "float":
        """float"""
        temp = pythonnet_property_get(self.wrapped, "MaximumAllowableTemperature")

        if temp is None:
            return 0.0

        return temp

    @maximum_allowable_temperature.setter
    @exception_bridge
    @enforce_parameter_types
    def maximum_allowable_temperature(self: "Self", value: "float") -> None:
        pythonnet_property_set(
            self.wrapped,
            "MaximumAllowableTemperature",
            float(value) if value is not None else 0.0,
        )

    @property
    @exception_bridge
    def modulus_of_elasticity(self: "Self") -> "float":
        """float"""
        temp = pythonnet_property_get(self.wrapped, "ModulusOfElasticity")

        if temp is None:
            return 0.0

        return temp

    @modulus_of_elasticity.setter
    @exception_bridge
    @enforce_parameter_types
    def modulus_of_elasticity(self: "Self", value: "float") -> None:
        pythonnet_property_set(
            self.wrapped,
            "ModulusOfElasticity",
            float(value) if value is not None else 0.0,
        )

    @property
    @exception_bridge
    def plane_strain_modulus(self: "Self") -> "float":
        """float

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "PlaneStrainModulus")

        if temp is None:
            return 0.0

        return temp

    @property
    @exception_bridge
    def poissons_ratio(self: "Self") -> "float":
        """float"""
        temp = pythonnet_property_get(self.wrapped, "PoissonsRatio")

        if temp is None:
            return 0.0

        return temp

    @poissons_ratio.setter
    @exception_bridge
    @enforce_parameter_types
    def poissons_ratio(self: "Self", value: "float") -> None:
        pythonnet_property_set(
            self.wrapped, "PoissonsRatio", float(value) if value is not None else 0.0
        )

    @property
    @exception_bridge
    def shear_fatigue_strength(self: "Self") -> "float":
        """float

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "ShearFatigueStrength")

        if temp is None:
            return 0.0

        return temp

    @property
    @exception_bridge
    def shear_modulus(self: "Self") -> "float":
        """float

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "ShearModulus")

        if temp is None:
            return 0.0

        return temp

    @property
    @exception_bridge
    def shear_yield_stress(self: "Self") -> "float":
        """float

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "ShearYieldStress")

        if temp is None:
            return 0.0

        return temp

    @property
    @exception_bridge
    def specific_heat(self: "Self") -> "float":
        """float"""
        temp = pythonnet_property_get(self.wrapped, "SpecificHeat")

        if temp is None:
            return 0.0

        return temp

    @specific_heat.setter
    @exception_bridge
    @enforce_parameter_types
    def specific_heat(self: "Self", value: "float") -> None:
        pythonnet_property_set(
            self.wrapped, "SpecificHeat", float(value) if value is not None else 0.0
        )

    @property
    @exception_bridge
    def standard(self: "Self") -> "_376.MaterialStandards":
        """mastapy.materials.MaterialStandards

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "Standard")

        if temp is None:
            return None

        value = conversion.pn_to_mp_enum(
            temp, "SMT.MastaAPI.Materials.MaterialStandards"
        )

        if value is None:
            return None

        return constructor.new_from_mastapy(
            "mastapy._private.materials._376", "MaterialStandards"
        )(value)

    @property
    @exception_bridge
    def surface_hardness(self: "Self") -> "float":
        """float"""
        temp = pythonnet_property_get(self.wrapped, "SurfaceHardness")

        if temp is None:
            return 0.0

        return temp

    @surface_hardness.setter
    @exception_bridge
    @enforce_parameter_types
    def surface_hardness(self: "Self", value: "float") -> None:
        pythonnet_property_set(
            self.wrapped, "SurfaceHardness", float(value) if value is not None else 0.0
        )

    @property
    @exception_bridge
    def surface_hardness_range_max_in_hb(self: "Self") -> "float":
        """float

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "SurfaceHardnessRangeMaxInHB")

        if temp is None:
            return 0.0

        return temp

    @property
    @exception_bridge
    def surface_hardness_range_max_in_hrc(self: "Self") -> "float":
        """float

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "SurfaceHardnessRangeMaxInHRC")

        if temp is None:
            return 0.0

        return temp

    @property
    @exception_bridge
    def surface_hardness_range_max_in_hv(self: "Self") -> "float":
        """float

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "SurfaceHardnessRangeMaxInHV")

        if temp is None:
            return 0.0

        return temp

    @property
    @exception_bridge
    def surface_hardness_range_min_in_hb(self: "Self") -> "float":
        """float

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "SurfaceHardnessRangeMinInHB")

        if temp is None:
            return 0.0

        return temp

    @property
    @exception_bridge
    def surface_hardness_range_min_in_hrc(self: "Self") -> "float":
        """float

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "SurfaceHardnessRangeMinInHRC")

        if temp is None:
            return 0.0

        return temp

    @property
    @exception_bridge
    def surface_hardness_range_min_in_hv(self: "Self") -> "float":
        """float

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "SurfaceHardnessRangeMinInHV")

        if temp is None:
            return 0.0

        return temp

    @property
    @exception_bridge
    def tensile_yield_strength(self: "Self") -> "float":
        """float"""
        temp = pythonnet_property_get(self.wrapped, "TensileYieldStrength")

        if temp is None:
            return 0.0

        return temp

    @tensile_yield_strength.setter
    @exception_bridge
    @enforce_parameter_types
    def tensile_yield_strength(self: "Self", value: "float") -> None:
        pythonnet_property_set(
            self.wrapped,
            "TensileYieldStrength",
            float(value) if value is not None else 0.0,
        )

    @property
    @exception_bridge
    def ultimate_tensile_strength(self: "Self") -> "float":
        """float"""
        temp = pythonnet_property_get(self.wrapped, "UltimateTensileStrength")

        if temp is None:
            return 0.0

        return temp

    @ultimate_tensile_strength.setter
    @exception_bridge
    @enforce_parameter_types
    def ultimate_tensile_strength(self: "Self", value: "float") -> None:
        pythonnet_property_set(
            self.wrapped,
            "UltimateTensileStrength",
            float(value) if value is not None else 0.0,
        )

    @property
    def cast_to(self: "Self") -> "_Cast_Material":
        """Cast to another type.

        Returns:
            _Cast_Material
        """
        return _Cast_Material(self)
