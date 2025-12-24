"""Database"""

from __future__ import annotations

from typing import TYPE_CHECKING, ClassVar, Generic, TypeVar

from mastapy._private._internal.dataclasses import extended_dataclass
from mastapy._private._internal.exception_bridge import exception_bridge
from mastapy._private._internal.exceptions import CastException
from mastapy._private._internal.python_net import (
    python_net_import,
    pythonnet_method_call,
    pythonnet_property_get,
)
from mastapy._private._internal.type_enforcement import enforce_parameter_types

from mastapy._private import _0
from mastapy._private._internal import conversion, utility

_DATABASE = python_net_import("SMT.MastaAPI.Utility.Databases", "Database")

if TYPE_CHECKING:
    from typing import Any, List, Type

    from mastapy._private.bearings import _2117, _2130
    from mastapy._private.bearings.bearing_results.rolling import _2216
    from mastapy._private.bolts import _1679, _1681, _1683, _1688
    from mastapy._private.cycloidal import _1669, _1676
    from mastapy._private.electric_machines import _1431, _1445, _1465, _1480
    from mastapy._private.gears import _455
    from mastapy._private.gears.gear_designs import _1066, _1068, _1071
    from mastapy._private.gears.gear_designs.cylindrical import _1147, _1153
    from mastapy._private.gears.gear_set_pareto_optimiser import (
        _1044,
        _1046,
        _1047,
        _1049,
        _1050,
        _1051,
        _1052,
        _1053,
        _1054,
        _1055,
        _1056,
        _1057,
        _1059,
        _1060,
        _1061,
        _1062,
    )
    from mastapy._private.gears.manufacturing.bevel import _926
    from mastapy._private.gears.manufacturing.cylindrical import _736, _741, _752
    from mastapy._private.gears.manufacturing.cylindrical.cutters import (
        _831,
        _837,
        _842,
        _843,
    )
    from mastapy._private.gears.materials import (
        _698,
        _700,
        _702,
        _704,
        _705,
        _707,
        _708,
        _711,
        _722,
        _723,
        _732,
    )
    from mastapy._private.gears.rating.cylindrical import _566, _582
    from mastapy._private.materials import _346, _349, _356, _370, _372, _374
    from mastapy._private.math_utility.optimisation import _1755, _1768
    from mastapy._private.nodal_analysis import _52
    from mastapy._private.shafts import _25, _42
    from mastapy._private.system_model.optimization import _2477, _2486
    from mastapy._private.system_model.optimization.machine_learning import _2494
    from mastapy._private.system_model.part_model.gears.supercharger_rotor_set import (
        _2846,
    )
    from mastapy._private.utility.databases import _2058, _2060, _2064

    Self = TypeVar("Self", bound="Database")
    CastSelf = TypeVar("CastSelf", bound="Database._Cast_Database")

TKey = TypeVar("TKey", bound="_2058.DatabaseKey")
TValue = TypeVar("TValue", bound="_0.APIBase")

__docformat__ = "restructuredtext en"
__all__ = ("Database",)


@extended_dataclass(frozen=True, slots=True, weakref_slot=True)
class _Cast_Database:
    """Special nested class for casting Database to subclasses."""

    __parent__: "Database"

    @property
    def shaft_material_database(self: "CastSelf") -> "_25.ShaftMaterialDatabase":
        from mastapy._private.shafts import _25

        return self.__parent__._cast(_25.ShaftMaterialDatabase)

    @property
    def shaft_settings_database(self: "CastSelf") -> "_42.ShaftSettingsDatabase":
        from mastapy._private.shafts import _42

        return self.__parent__._cast(_42.ShaftSettingsDatabase)

    @property
    def analysis_settings_database(self: "CastSelf") -> "_52.AnalysisSettingsDatabase":
        from mastapy._private.nodal_analysis import _52

        return self.__parent__._cast(_52.AnalysisSettingsDatabase)

    @property
    def bearing_material_database(self: "CastSelf") -> "_346.BearingMaterialDatabase":
        from mastapy._private.materials import _346

        return self.__parent__._cast(_346.BearingMaterialDatabase)

    @property
    def component_material_database(
        self: "CastSelf",
    ) -> "_349.ComponentMaterialDatabase":
        from mastapy._private.materials import _349

        return self.__parent__._cast(_349.ComponentMaterialDatabase)

    @property
    def fluid_database(self: "CastSelf") -> "_356.FluidDatabase":
        from mastapy._private.materials import _356

        return self.__parent__._cast(_356.FluidDatabase)

    @property
    def lubrication_detail_database(
        self: "CastSelf",
    ) -> "_370.LubricationDetailDatabase":
        from mastapy._private.materials import _370

        return self.__parent__._cast(_370.LubricationDetailDatabase)

    @property
    def material_database(self: "CastSelf") -> "_372.MaterialDatabase":
        from mastapy._private.materials import _372

        return self.__parent__._cast(_372.MaterialDatabase)

    @property
    def materials_settings_database(
        self: "CastSelf",
    ) -> "_374.MaterialsSettingsDatabase":
        from mastapy._private.materials import _374

        return self.__parent__._cast(_374.MaterialsSettingsDatabase)

    @property
    def pocketing_power_loss_coefficients_database(
        self: "CastSelf",
    ) -> "_455.PocketingPowerLossCoefficientsDatabase":
        from mastapy._private.gears import _455

        return self.__parent__._cast(_455.PocketingPowerLossCoefficientsDatabase)

    @property
    def cylindrical_gear_design_and_rating_settings_database(
        self: "CastSelf",
    ) -> "_566.CylindricalGearDesignAndRatingSettingsDatabase":
        from mastapy._private.gears.rating.cylindrical import _566

        return self.__parent__._cast(
            _566.CylindricalGearDesignAndRatingSettingsDatabase
        )

    @property
    def cylindrical_plastic_gear_rating_settings_database(
        self: "CastSelf",
    ) -> "_582.CylindricalPlasticGearRatingSettingsDatabase":
        from mastapy._private.gears.rating.cylindrical import _582

        return self.__parent__._cast(_582.CylindricalPlasticGearRatingSettingsDatabase)

    @property
    def bevel_gear_abstract_material_database(
        self: "CastSelf",
    ) -> "_698.BevelGearAbstractMaterialDatabase":
        from mastapy._private.gears.materials import _698

        return self.__parent__._cast(_698.BevelGearAbstractMaterialDatabase)

    @property
    def bevel_gear_iso_material_database(
        self: "CastSelf",
    ) -> "_700.BevelGearISOMaterialDatabase":
        from mastapy._private.gears.materials import _700

        return self.__parent__._cast(_700.BevelGearISOMaterialDatabase)

    @property
    def bevel_gear_material_database(
        self: "CastSelf",
    ) -> "_702.BevelGearMaterialDatabase":
        from mastapy._private.gears.materials import _702

        return self.__parent__._cast(_702.BevelGearMaterialDatabase)

    @property
    def cylindrical_gear_agma_material_database(
        self: "CastSelf",
    ) -> "_704.CylindricalGearAGMAMaterialDatabase":
        from mastapy._private.gears.materials import _704

        return self.__parent__._cast(_704.CylindricalGearAGMAMaterialDatabase)

    @property
    def cylindrical_gear_iso_material_database(
        self: "CastSelf",
    ) -> "_705.CylindricalGearISOMaterialDatabase":
        from mastapy._private.gears.materials import _705

        return self.__parent__._cast(_705.CylindricalGearISOMaterialDatabase)

    @property
    def cylindrical_gear_material_database(
        self: "CastSelf",
    ) -> "_707.CylindricalGearMaterialDatabase":
        from mastapy._private.gears.materials import _707

        return self.__parent__._cast(_707.CylindricalGearMaterialDatabase)

    @property
    def cylindrical_gear_plastic_material_database(
        self: "CastSelf",
    ) -> "_708.CylindricalGearPlasticMaterialDatabase":
        from mastapy._private.gears.materials import _708

        return self.__parent__._cast(_708.CylindricalGearPlasticMaterialDatabase)

    @property
    def gear_material_database(self: "CastSelf") -> "_711.GearMaterialDatabase":
        from mastapy._private.gears.materials import _711

        return self.__parent__._cast(_711.GearMaterialDatabase)

    @property
    def isotr1417912001_coefficient_of_friction_constants_database(
        self: "CastSelf",
    ) -> "_722.ISOTR1417912001CoefficientOfFrictionConstantsDatabase":
        from mastapy._private.gears.materials import _722

        return self.__parent__._cast(
            _722.ISOTR1417912001CoefficientOfFrictionConstantsDatabase
        )

    @property
    def klingelnberg_conical_gear_material_database(
        self: "CastSelf",
    ) -> "_723.KlingelnbergConicalGearMaterialDatabase":
        from mastapy._private.gears.materials import _723

        return self.__parent__._cast(_723.KlingelnbergConicalGearMaterialDatabase)

    @property
    def raw_material_database(self: "CastSelf") -> "_732.RawMaterialDatabase":
        from mastapy._private.gears.materials import _732

        return self.__parent__._cast(_732.RawMaterialDatabase)

    @property
    def cylindrical_cutter_database(
        self: "CastSelf",
    ) -> "_736.CylindricalCutterDatabase":
        from mastapy._private.gears.manufacturing.cylindrical import _736

        return self.__parent__._cast(_736.CylindricalCutterDatabase)

    @property
    def cylindrical_hob_database(self: "CastSelf") -> "_741.CylindricalHobDatabase":
        from mastapy._private.gears.manufacturing.cylindrical import _741

        return self.__parent__._cast(_741.CylindricalHobDatabase)

    @property
    def cylindrical_shaper_database(
        self: "CastSelf",
    ) -> "_752.CylindricalShaperDatabase":
        from mastapy._private.gears.manufacturing.cylindrical import _752

        return self.__parent__._cast(_752.CylindricalShaperDatabase)

    @property
    def cylindrical_formed_wheel_grinder_database(
        self: "CastSelf",
    ) -> "_831.CylindricalFormedWheelGrinderDatabase":
        from mastapy._private.gears.manufacturing.cylindrical.cutters import _831

        return self.__parent__._cast(_831.CylindricalFormedWheelGrinderDatabase)

    @property
    def cylindrical_gear_plunge_shaver_database(
        self: "CastSelf",
    ) -> "_837.CylindricalGearPlungeShaverDatabase":
        from mastapy._private.gears.manufacturing.cylindrical.cutters import _837

        return self.__parent__._cast(_837.CylindricalGearPlungeShaverDatabase)

    @property
    def cylindrical_gear_shaver_database(
        self: "CastSelf",
    ) -> "_842.CylindricalGearShaverDatabase":
        from mastapy._private.gears.manufacturing.cylindrical.cutters import _842

        return self.__parent__._cast(_842.CylindricalGearShaverDatabase)

    @property
    def cylindrical_worm_grinder_database(
        self: "CastSelf",
    ) -> "_843.CylindricalWormGrinderDatabase":
        from mastapy._private.gears.manufacturing.cylindrical.cutters import _843

        return self.__parent__._cast(_843.CylindricalWormGrinderDatabase)

    @property
    def manufacturing_machine_database(
        self: "CastSelf",
    ) -> "_926.ManufacturingMachineDatabase":
        from mastapy._private.gears.manufacturing.bevel import _926

        return self.__parent__._cast(_926.ManufacturingMachineDatabase)

    @property
    def micro_geometry_design_space_search_strategy_database(
        self: "CastSelf",
    ) -> "_1044.MicroGeometryDesignSpaceSearchStrategyDatabase":
        from mastapy._private.gears.gear_set_pareto_optimiser import _1044

        return self.__parent__._cast(
            _1044.MicroGeometryDesignSpaceSearchStrategyDatabase
        )

    @property
    def micro_geometry_gear_set_design_space_search_strategy_database(
        self: "CastSelf",
    ) -> "_1046.MicroGeometryGearSetDesignSpaceSearchStrategyDatabase":
        from mastapy._private.gears.gear_set_pareto_optimiser import _1046

        return self.__parent__._cast(
            _1046.MicroGeometryGearSetDesignSpaceSearchStrategyDatabase
        )

    @property
    def micro_geometry_gear_set_duty_cycle_design_space_search_strategy_database(
        self: "CastSelf",
    ) -> "_1047.MicroGeometryGearSetDutyCycleDesignSpaceSearchStrategyDatabase":
        from mastapy._private.gears.gear_set_pareto_optimiser import _1047

        return self.__parent__._cast(
            _1047.MicroGeometryGearSetDutyCycleDesignSpaceSearchStrategyDatabase
        )

    @property
    def pareto_conical_rating_optimisation_strategy_database(
        self: "CastSelf",
    ) -> "_1049.ParetoConicalRatingOptimisationStrategyDatabase":
        from mastapy._private.gears.gear_set_pareto_optimiser import _1049

        return self.__parent__._cast(
            _1049.ParetoConicalRatingOptimisationStrategyDatabase
        )

    @property
    def pareto_cylindrical_gear_set_duty_cycle_optimisation_strategy_database(
        self: "CastSelf",
    ) -> "_1050.ParetoCylindricalGearSetDutyCycleOptimisationStrategyDatabase":
        from mastapy._private.gears.gear_set_pareto_optimiser import _1050

        return self.__parent__._cast(
            _1050.ParetoCylindricalGearSetDutyCycleOptimisationStrategyDatabase
        )

    @property
    def pareto_cylindrical_gear_set_optimisation_strategy_database(
        self: "CastSelf",
    ) -> "_1051.ParetoCylindricalGearSetOptimisationStrategyDatabase":
        from mastapy._private.gears.gear_set_pareto_optimiser import _1051

        return self.__parent__._cast(
            _1051.ParetoCylindricalGearSetOptimisationStrategyDatabase
        )

    @property
    def pareto_cylindrical_rating_optimisation_strategy_database(
        self: "CastSelf",
    ) -> "_1052.ParetoCylindricalRatingOptimisationStrategyDatabase":
        from mastapy._private.gears.gear_set_pareto_optimiser import _1052

        return self.__parent__._cast(
            _1052.ParetoCylindricalRatingOptimisationStrategyDatabase
        )

    @property
    def pareto_face_gear_set_duty_cycle_optimisation_strategy_database(
        self: "CastSelf",
    ) -> "_1053.ParetoFaceGearSetDutyCycleOptimisationStrategyDatabase":
        from mastapy._private.gears.gear_set_pareto_optimiser import _1053

        return self.__parent__._cast(
            _1053.ParetoFaceGearSetDutyCycleOptimisationStrategyDatabase
        )

    @property
    def pareto_face_gear_set_optimisation_strategy_database(
        self: "CastSelf",
    ) -> "_1054.ParetoFaceGearSetOptimisationStrategyDatabase":
        from mastapy._private.gears.gear_set_pareto_optimiser import _1054

        return self.__parent__._cast(
            _1054.ParetoFaceGearSetOptimisationStrategyDatabase
        )

    @property
    def pareto_face_rating_optimisation_strategy_database(
        self: "CastSelf",
    ) -> "_1055.ParetoFaceRatingOptimisationStrategyDatabase":
        from mastapy._private.gears.gear_set_pareto_optimiser import _1055

        return self.__parent__._cast(_1055.ParetoFaceRatingOptimisationStrategyDatabase)

    @property
    def pareto_hypoid_gear_set_duty_cycle_optimisation_strategy_database(
        self: "CastSelf",
    ) -> "_1056.ParetoHypoidGearSetDutyCycleOptimisationStrategyDatabase":
        from mastapy._private.gears.gear_set_pareto_optimiser import _1056

        return self.__parent__._cast(
            _1056.ParetoHypoidGearSetDutyCycleOptimisationStrategyDatabase
        )

    @property
    def pareto_hypoid_gear_set_optimisation_strategy_database(
        self: "CastSelf",
    ) -> "_1057.ParetoHypoidGearSetOptimisationStrategyDatabase":
        from mastapy._private.gears.gear_set_pareto_optimiser import _1057

        return self.__parent__._cast(
            _1057.ParetoHypoidGearSetOptimisationStrategyDatabase
        )

    @property
    def pareto_spiral_bevel_gear_set_duty_cycle_optimisation_strategy_database(
        self: "CastSelf",
    ) -> "_1059.ParetoSpiralBevelGearSetDutyCycleOptimisationStrategyDatabase":
        from mastapy._private.gears.gear_set_pareto_optimiser import _1059

        return self.__parent__._cast(
            _1059.ParetoSpiralBevelGearSetDutyCycleOptimisationStrategyDatabase
        )

    @property
    def pareto_spiral_bevel_gear_set_optimisation_strategy_database(
        self: "CastSelf",
    ) -> "_1060.ParetoSpiralBevelGearSetOptimisationStrategyDatabase":
        from mastapy._private.gears.gear_set_pareto_optimiser import _1060

        return self.__parent__._cast(
            _1060.ParetoSpiralBevelGearSetOptimisationStrategyDatabase
        )

    @property
    def pareto_straight_bevel_gear_set_duty_cycle_optimisation_strategy_database(
        self: "CastSelf",
    ) -> "_1061.ParetoStraightBevelGearSetDutyCycleOptimisationStrategyDatabase":
        from mastapy._private.gears.gear_set_pareto_optimiser import _1061

        return self.__parent__._cast(
            _1061.ParetoStraightBevelGearSetDutyCycleOptimisationStrategyDatabase
        )

    @property
    def pareto_straight_bevel_gear_set_optimisation_strategy_database(
        self: "CastSelf",
    ) -> "_1062.ParetoStraightBevelGearSetOptimisationStrategyDatabase":
        from mastapy._private.gears.gear_set_pareto_optimiser import _1062

        return self.__parent__._cast(
            _1062.ParetoStraightBevelGearSetOptimisationStrategyDatabase
        )

    @property
    def bevel_hypoid_gear_design_settings_database(
        self: "CastSelf",
    ) -> "_1066.BevelHypoidGearDesignSettingsDatabase":
        from mastapy._private.gears.gear_designs import _1066

        return self.__parent__._cast(_1066.BevelHypoidGearDesignSettingsDatabase)

    @property
    def bevel_hypoid_gear_rating_settings_database(
        self: "CastSelf",
    ) -> "_1068.BevelHypoidGearRatingSettingsDatabase":
        from mastapy._private.gears.gear_designs import _1068

        return self.__parent__._cast(_1068.BevelHypoidGearRatingSettingsDatabase)

    @property
    def design_constraint_collection_database(
        self: "CastSelf",
    ) -> "_1071.DesignConstraintCollectionDatabase":
        from mastapy._private.gears.gear_designs import _1071

        return self.__parent__._cast(_1071.DesignConstraintCollectionDatabase)

    @property
    def cylindrical_gear_design_constraints_database(
        self: "CastSelf",
    ) -> "_1147.CylindricalGearDesignConstraintsDatabase":
        from mastapy._private.gears.gear_designs.cylindrical import _1147

        return self.__parent__._cast(_1147.CylindricalGearDesignConstraintsDatabase)

    @property
    def cylindrical_gear_micro_geometry_settings_database(
        self: "CastSelf",
    ) -> "_1153.CylindricalGearMicroGeometrySettingsDatabase":
        from mastapy._private.gears.gear_designs.cylindrical import _1153

        return self.__parent__._cast(_1153.CylindricalGearMicroGeometrySettingsDatabase)

    @property
    def general_electric_machine_material_database(
        self: "CastSelf",
    ) -> "_1431.GeneralElectricMachineMaterialDatabase":
        from mastapy._private.electric_machines import _1431

        return self.__parent__._cast(_1431.GeneralElectricMachineMaterialDatabase)

    @property
    def magnet_material_database(self: "CastSelf") -> "_1445.MagnetMaterialDatabase":
        from mastapy._private.electric_machines import _1445

        return self.__parent__._cast(_1445.MagnetMaterialDatabase)

    @property
    def stator_rotor_material_database(
        self: "CastSelf",
    ) -> "_1465.StatorRotorMaterialDatabase":
        from mastapy._private.electric_machines import _1465

        return self.__parent__._cast(_1465.StatorRotorMaterialDatabase)

    @property
    def winding_material_database(self: "CastSelf") -> "_1480.WindingMaterialDatabase":
        from mastapy._private.electric_machines import _1480

        return self.__parent__._cast(_1480.WindingMaterialDatabase)

    @property
    def cycloidal_disc_material_database(
        self: "CastSelf",
    ) -> "_1669.CycloidalDiscMaterialDatabase":
        from mastapy._private.cycloidal import _1669

        return self.__parent__._cast(_1669.CycloidalDiscMaterialDatabase)

    @property
    def ring_pins_material_database(
        self: "CastSelf",
    ) -> "_1676.RingPinsMaterialDatabase":
        from mastapy._private.cycloidal import _1676

        return self.__parent__._cast(_1676.RingPinsMaterialDatabase)

    @property
    def bolted_joint_material_database(
        self: "CastSelf",
    ) -> "_1679.BoltedJointMaterialDatabase":
        from mastapy._private.bolts import _1679

        return self.__parent__._cast(_1679.BoltedJointMaterialDatabase)

    @property
    def bolt_geometry_database(self: "CastSelf") -> "_1681.BoltGeometryDatabase":
        from mastapy._private.bolts import _1681

        return self.__parent__._cast(_1681.BoltGeometryDatabase)

    @property
    def bolt_material_database(self: "CastSelf") -> "_1683.BoltMaterialDatabase":
        from mastapy._private.bolts import _1683

        return self.__parent__._cast(_1683.BoltMaterialDatabase)

    @property
    def clamped_section_material_database(
        self: "CastSelf",
    ) -> "_1688.ClampedSectionMaterialDatabase":
        from mastapy._private.bolts import _1688

        return self.__parent__._cast(_1688.ClampedSectionMaterialDatabase)

    @property
    def design_space_search_strategy_database(
        self: "CastSelf",
    ) -> "_1755.DesignSpaceSearchStrategyDatabase":
        from mastapy._private.math_utility.optimisation import _1755

        return self.__parent__._cast(_1755.DesignSpaceSearchStrategyDatabase)

    @property
    def pareto_optimisation_strategy_database(
        self: "CastSelf",
    ) -> "_1768.ParetoOptimisationStrategyDatabase":
        from mastapy._private.math_utility.optimisation import _1768

        return self.__parent__._cast(_1768.ParetoOptimisationStrategyDatabase)

    @property
    def named_database(self: "CastSelf") -> "_2060.NamedDatabase":
        from mastapy._private.utility.databases import _2060

        return self.__parent__._cast(_2060.NamedDatabase)

    @property
    def sql_database(self: "CastSelf") -> "_2064.SQLDatabase":
        from mastapy._private.utility.databases import _2064

        return self.__parent__._cast(_2064.SQLDatabase)

    @property
    def bearing_settings_database(self: "CastSelf") -> "_2117.BearingSettingsDatabase":
        from mastapy._private.bearings import _2117

        return self.__parent__._cast(_2117.BearingSettingsDatabase)

    @property
    def rolling_bearing_database(self: "CastSelf") -> "_2130.RollingBearingDatabase":
        from mastapy._private.bearings import _2130

        return self.__parent__._cast(_2130.RollingBearingDatabase)

    @property
    def iso14179_settings_database(
        self: "CastSelf",
    ) -> "_2216.ISO14179SettingsDatabase":
        from mastapy._private.bearings.bearing_results.rolling import _2216

        return self.__parent__._cast(_2216.ISO14179SettingsDatabase)

    @property
    def conical_gear_optimization_strategy_database(
        self: "CastSelf",
    ) -> "_2477.ConicalGearOptimizationStrategyDatabase":
        from mastapy._private.system_model.optimization import _2477

        return self.__parent__._cast(_2477.ConicalGearOptimizationStrategyDatabase)

    @property
    def optimization_strategy_database(
        self: "CastSelf",
    ) -> "_2486.OptimizationStrategyDatabase":
        from mastapy._private.system_model.optimization import _2486

        return self.__parent__._cast(_2486.OptimizationStrategyDatabase)

    @property
    def cylindrical_gear_flank_optimisation_parameters_database(
        self: "CastSelf",
    ) -> "_2494.CylindricalGearFlankOptimisationParametersDatabase":
        from mastapy._private.system_model.optimization.machine_learning import _2494

        return self.__parent__._cast(
            _2494.CylindricalGearFlankOptimisationParametersDatabase
        )

    @property
    def supercharger_rotor_set_database(
        self: "CastSelf",
    ) -> "_2846.SuperchargerRotorSetDatabase":
        from mastapy._private.system_model.part_model.gears.supercharger_rotor_set import (
            _2846,
        )

        return self.__parent__._cast(_2846.SuperchargerRotorSetDatabase)

    @property
    def database(self: "CastSelf") -> "Database":
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
class Database(_0.APIBase, Generic[TKey, TValue]):
    """Database

    This is a mastapy class.

    Generic Types:
        TKey
        TValue
    """

    TYPE: ClassVar["Type"] = _DATABASE

    wrapped: "Any"

    def __post_init__(self: "Self") -> None:
        """Override of the post initialisation magic method."""
        if not hasattr(self.wrapped, "reference_count"):
            self.wrapped.reference_count = 0

        self.wrapped.reference_count += 1

    @property
    @exception_bridge
    def count(self: "Self") -> "int":
        """int

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "Count")

        if temp is None:
            return 0

        return temp

    @exception_bridge
    @enforce_parameter_types
    def can_be_removed(self: "Self", item: "TValue") -> "bool":
        """bool

        Args:
            item (TValue)
        """
        method_result = pythonnet_method_call(self.wrapped, "CanBeRemoved", item)
        return method_result

    @exception_bridge
    def get_all_items(self: "Self") -> "List[TValue]":
        """List[TValue]"""
        return conversion.pn_to_mp_objects_in_list(
            pythonnet_method_call(self.wrapped, "GetAllItems")
        )

    @property
    def cast_to(self: "Self") -> "_Cast_Database":
        """Cast to another type.

        Returns:
            _Cast_Database
        """
        return _Cast_Database(self)
