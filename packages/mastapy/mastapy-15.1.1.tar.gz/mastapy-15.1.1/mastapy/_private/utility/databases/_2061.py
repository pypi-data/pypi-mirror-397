"""NamedDatabaseItem"""

from __future__ import annotations

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

from mastapy._private import _0
from mastapy._private._internal import constructor, conversion, utility

_NAMED_DATABASE_ITEM = python_net_import(
    "SMT.MastaAPI.Utility.Databases", "NamedDatabaseItem"
)

if TYPE_CHECKING:
    from typing import Any, List, Type, TypeVar

    from mastapy._private._internal.typing import PathLike

    from mastapy._private.bearings import _2118
    from mastapy._private.bearings.bearing_results.rolling import _2215
    from mastapy._private.bolts import _1678, _1680, _1682
    from mastapy._private.cycloidal import _1668, _1675
    from mastapy._private.detailed_rigid_connectors.splines import _1628
    from mastapy._private.electric_machines import _1430, _1444, _1464, _1479
    from mastapy._private.gears import _454
    from mastapy._private.gears.gear_designs import _1067, _1069, _1072
    from mastapy._private.gears.gear_designs.cylindrical import _1146, _1154
    from mastapy._private.gears.manufacturing.bevel import _925
    from mastapy._private.gears.manufacturing.cylindrical.cutters import (
        _832,
        _833,
        _834,
        _835,
        _836,
        _838,
        _839,
        _840,
        _841,
        _844,
    )
    from mastapy._private.gears.materials import (
        _696,
        _699,
        _701,
        _706,
        _710,
        _719,
        _721,
        _724,
        _728,
        _731,
    )
    from mastapy._private.gears.rating.cylindrical import _567, _583
    from mastapy._private.materials import _345, _355, _369, _371, _375
    from mastapy._private.math_utility.optimisation import _1765
    from mastapy._private.nodal_analysis import _53
    from mastapy._private.shafts import _24, _43, _46
    from mastapy._private.system_model.optimization import _2475, _2478, _2484, _2485
    from mastapy._private.system_model.optimization.machine_learning import _2493
    from mastapy._private.system_model.part_model.gears.supercharger_rotor_set import (
        _2845,
    )
    from mastapy._private.utility import _1807
    from mastapy._private.utility.databases import _2062

    Self = TypeVar("Self", bound="NamedDatabaseItem")
    CastSelf = TypeVar("CastSelf", bound="NamedDatabaseItem._Cast_NamedDatabaseItem")


__docformat__ = "restructuredtext en"
__all__ = ("NamedDatabaseItem",)


@extended_dataclass(frozen=True, slots=True, weakref_slot=True)
class _Cast_NamedDatabaseItem:
    """Special nested class for casting NamedDatabaseItem to subclasses."""

    __parent__: "NamedDatabaseItem"

    @property
    def shaft_material(self: "CastSelf") -> "_24.ShaftMaterial":
        from mastapy._private.shafts import _24

        return self.__parent__._cast(_24.ShaftMaterial)

    @property
    def shaft_settings_item(self: "CastSelf") -> "_43.ShaftSettingsItem":
        from mastapy._private.shafts import _43

        return self.__parent__._cast(_43.ShaftSettingsItem)

    @property
    def simple_shaft_definition(self: "CastSelf") -> "_46.SimpleShaftDefinition":
        from mastapy._private.shafts import _46

        return self.__parent__._cast(_46.SimpleShaftDefinition)

    @property
    def analysis_settings_item(self: "CastSelf") -> "_53.AnalysisSettingsItem":
        from mastapy._private.nodal_analysis import _53

        return self.__parent__._cast(_53.AnalysisSettingsItem)

    @property
    def bearing_material(self: "CastSelf") -> "_345.BearingMaterial":
        from mastapy._private.materials import _345

        return self.__parent__._cast(_345.BearingMaterial)

    @property
    def fluid(self: "CastSelf") -> "_355.Fluid":
        from mastapy._private.materials import _355

        return self.__parent__._cast(_355.Fluid)

    @property
    def lubrication_detail(self: "CastSelf") -> "_369.LubricationDetail":
        from mastapy._private.materials import _369

        return self.__parent__._cast(_369.LubricationDetail)

    @property
    def material(self: "CastSelf") -> "_371.Material":
        from mastapy._private.materials import _371

        return self.__parent__._cast(_371.Material)

    @property
    def materials_settings_item(self: "CastSelf") -> "_375.MaterialsSettingsItem":
        from mastapy._private.materials import _375

        return self.__parent__._cast(_375.MaterialsSettingsItem)

    @property
    def pocketing_power_loss_coefficients(
        self: "CastSelf",
    ) -> "_454.PocketingPowerLossCoefficients":
        from mastapy._private.gears import _454

        return self.__parent__._cast(_454.PocketingPowerLossCoefficients)

    @property
    def cylindrical_gear_design_and_rating_settings_item(
        self: "CastSelf",
    ) -> "_567.CylindricalGearDesignAndRatingSettingsItem":
        from mastapy._private.gears.rating.cylindrical import _567

        return self.__parent__._cast(_567.CylindricalGearDesignAndRatingSettingsItem)

    @property
    def cylindrical_plastic_gear_rating_settings_item(
        self: "CastSelf",
    ) -> "_583.CylindricalPlasticGearRatingSettingsItem":
        from mastapy._private.gears.rating.cylindrical import _583

        return self.__parent__._cast(_583.CylindricalPlasticGearRatingSettingsItem)

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
    def isotr1417912001_coefficient_of_friction_constants(
        self: "CastSelf",
    ) -> "_721.ISOTR1417912001CoefficientOfFrictionConstants":
        from mastapy._private.gears.materials import _721

        return self.__parent__._cast(_721.ISOTR1417912001CoefficientOfFrictionConstants)

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
    def raw_material(self: "CastSelf") -> "_731.RawMaterial":
        from mastapy._private.gears.materials import _731

        return self.__parent__._cast(_731.RawMaterial)

    @property
    def cylindrical_gear_abstract_cutter_design(
        self: "CastSelf",
    ) -> "_832.CylindricalGearAbstractCutterDesign":
        from mastapy._private.gears.manufacturing.cylindrical.cutters import _832

        return self.__parent__._cast(_832.CylindricalGearAbstractCutterDesign)

    @property
    def cylindrical_gear_form_grinding_wheel(
        self: "CastSelf",
    ) -> "_833.CylindricalGearFormGrindingWheel":
        from mastapy._private.gears.manufacturing.cylindrical.cutters import _833

        return self.__parent__._cast(_833.CylindricalGearFormGrindingWheel)

    @property
    def cylindrical_gear_grinding_worm(
        self: "CastSelf",
    ) -> "_834.CylindricalGearGrindingWorm":
        from mastapy._private.gears.manufacturing.cylindrical.cutters import _834

        return self.__parent__._cast(_834.CylindricalGearGrindingWorm)

    @property
    def cylindrical_gear_hob_design(
        self: "CastSelf",
    ) -> "_835.CylindricalGearHobDesign":
        from mastapy._private.gears.manufacturing.cylindrical.cutters import _835

        return self.__parent__._cast(_835.CylindricalGearHobDesign)

    @property
    def cylindrical_gear_plunge_shaver(
        self: "CastSelf",
    ) -> "_836.CylindricalGearPlungeShaver":
        from mastapy._private.gears.manufacturing.cylindrical.cutters import _836

        return self.__parent__._cast(_836.CylindricalGearPlungeShaver)

    @property
    def cylindrical_gear_rack_design(
        self: "CastSelf",
    ) -> "_838.CylindricalGearRackDesign":
        from mastapy._private.gears.manufacturing.cylindrical.cutters import _838

        return self.__parent__._cast(_838.CylindricalGearRackDesign)

    @property
    def cylindrical_gear_real_cutter_design(
        self: "CastSelf",
    ) -> "_839.CylindricalGearRealCutterDesign":
        from mastapy._private.gears.manufacturing.cylindrical.cutters import _839

        return self.__parent__._cast(_839.CylindricalGearRealCutterDesign)

    @property
    def cylindrical_gear_shaper(self: "CastSelf") -> "_840.CylindricalGearShaper":
        from mastapy._private.gears.manufacturing.cylindrical.cutters import _840

        return self.__parent__._cast(_840.CylindricalGearShaper)

    @property
    def cylindrical_gear_shaver(self: "CastSelf") -> "_841.CylindricalGearShaver":
        from mastapy._private.gears.manufacturing.cylindrical.cutters import _841

        return self.__parent__._cast(_841.CylindricalGearShaver)

    @property
    def involute_cutter_design(self: "CastSelf") -> "_844.InvoluteCutterDesign":
        from mastapy._private.gears.manufacturing.cylindrical.cutters import _844

        return self.__parent__._cast(_844.InvoluteCutterDesign)

    @property
    def manufacturing_machine(self: "CastSelf") -> "_925.ManufacturingMachine":
        from mastapy._private.gears.manufacturing.bevel import _925

        return self.__parent__._cast(_925.ManufacturingMachine)

    @property
    def bevel_hypoid_gear_design_settings_item(
        self: "CastSelf",
    ) -> "_1067.BevelHypoidGearDesignSettingsItem":
        from mastapy._private.gears.gear_designs import _1067

        return self.__parent__._cast(_1067.BevelHypoidGearDesignSettingsItem)

    @property
    def bevel_hypoid_gear_rating_settings_item(
        self: "CastSelf",
    ) -> "_1069.BevelHypoidGearRatingSettingsItem":
        from mastapy._private.gears.gear_designs import _1069

        return self.__parent__._cast(_1069.BevelHypoidGearRatingSettingsItem)

    @property
    def design_constraints_collection(
        self: "CastSelf",
    ) -> "_1072.DesignConstraintsCollection":
        from mastapy._private.gears.gear_designs import _1072

        return self.__parent__._cast(_1072.DesignConstraintsCollection)

    @property
    def cylindrical_gear_design_constraints(
        self: "CastSelf",
    ) -> "_1146.CylindricalGearDesignConstraints":
        from mastapy._private.gears.gear_designs.cylindrical import _1146

        return self.__parent__._cast(_1146.CylindricalGearDesignConstraints)

    @property
    def cylindrical_gear_micro_geometry_settings_item(
        self: "CastSelf",
    ) -> "_1154.CylindricalGearMicroGeometrySettingsItem":
        from mastapy._private.gears.gear_designs.cylindrical import _1154

        return self.__parent__._cast(_1154.CylindricalGearMicroGeometrySettingsItem)

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
    def bolt_geometry(self: "CastSelf") -> "_1680.BoltGeometry":
        from mastapy._private.bolts import _1680

        return self.__parent__._cast(_1680.BoltGeometry)

    @property
    def bolt_material(self: "CastSelf") -> "_1682.BoltMaterial":
        from mastapy._private.bolts import _1682

        return self.__parent__._cast(_1682.BoltMaterial)

    @property
    def pareto_optimisation_strategy(
        self: "CastSelf",
    ) -> "_1765.ParetoOptimisationStrategy":
        from mastapy._private.math_utility.optimisation import _1765

        return self.__parent__._cast(_1765.ParetoOptimisationStrategy)

    @property
    def bearing_settings_item(self: "CastSelf") -> "_2118.BearingSettingsItem":
        from mastapy._private.bearings import _2118

        return self.__parent__._cast(_2118.BearingSettingsItem)

    @property
    def iso14179_settings(self: "CastSelf") -> "_2215.ISO14179Settings":
        from mastapy._private.bearings.bearing_results.rolling import _2215

        return self.__parent__._cast(_2215.ISO14179Settings)

    @property
    def conical_gear_optimisation_strategy(
        self: "CastSelf",
    ) -> "_2475.ConicalGearOptimisationStrategy":
        from mastapy._private.system_model.optimization import _2475

        return self.__parent__._cast(_2475.ConicalGearOptimisationStrategy)

    @property
    def cylindrical_gear_optimisation_strategy(
        self: "CastSelf",
    ) -> "_2478.CylindricalGearOptimisationStrategy":
        from mastapy._private.system_model.optimization import _2478

        return self.__parent__._cast(_2478.CylindricalGearOptimisationStrategy)

    @property
    def optimization_strategy(self: "CastSelf") -> "_2484.OptimizationStrategy":
        from mastapy._private.system_model.optimization import _2484

        return self.__parent__._cast(_2484.OptimizationStrategy)

    @property
    def optimization_strategy_base(
        self: "CastSelf",
    ) -> "_2485.OptimizationStrategyBase":
        from mastapy._private.system_model.optimization import _2485

        return self.__parent__._cast(_2485.OptimizationStrategyBase)

    @property
    def cylindrical_gear_flank_optimisation_parameters(
        self: "CastSelf",
    ) -> "_2493.CylindricalGearFlankOptimisationParameters":
        from mastapy._private.system_model.optimization.machine_learning import _2493

        return self.__parent__._cast(_2493.CylindricalGearFlankOptimisationParameters)

    @property
    def supercharger_rotor_set(self: "CastSelf") -> "_2845.SuperchargerRotorSet":
        from mastapy._private.system_model.part_model.gears.supercharger_rotor_set import (
            _2845,
        )

        return self.__parent__._cast(_2845.SuperchargerRotorSet)

    @property
    def named_database_item(self: "CastSelf") -> "NamedDatabaseItem":
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
class NamedDatabaseItem(_0.APIBase):
    """NamedDatabaseItem

    This is a mastapy class.
    """

    TYPE: ClassVar["Type"] = _NAMED_DATABASE_ITEM

    wrapped: "Any"

    def __post_init__(self: "Self") -> None:
        """Override of the post initialisation magic method."""
        if not hasattr(self.wrapped, "reference_count"):
            self.wrapped.reference_count = 0

        self.wrapped.reference_count += 1

    @property
    @exception_bridge
    def comment(self: "Self") -> "str":
        """str"""
        temp = pythonnet_property_get(self.wrapped, "Comment")

        if temp is None:
            return ""

        return temp

    @comment.setter
    @exception_bridge
    @enforce_parameter_types
    def comment(self: "Self", value: "str") -> None:
        pythonnet_property_set(
            self.wrapped, "Comment", str(value) if value is not None else ""
        )

    @property
    @exception_bridge
    def name(self: "Self") -> "str":
        """str

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "Name")

        if temp is None:
            return ""

        return temp

    @property
    @exception_bridge
    def no_history(self: "Self") -> "str":
        """str

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "NoHistory")

        if temp is None:
            return ""

        return temp

    @property
    @exception_bridge
    def history(self: "Self") -> "_1807.FileHistory":
        """mastapy.utility.FileHistory

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "History")

        if temp is None:
            return None

        type_ = temp.GetType()
        return constructor.new(type_.Namespace, type_.Name)(temp)

    @property
    @exception_bridge
    def database_key(self: "Self") -> "_2062.NamedKey":
        """mastapy.utility.databases.NamedKey"""
        temp = pythonnet_property_get(self.wrapped, "DatabaseKey")

        if temp is None:
            return None

        type_ = temp.GetType()
        return constructor.new(type_.Namespace, type_.Name)(temp)

    @database_key.setter
    @exception_bridge
    @enforce_parameter_types
    def database_key(self: "Self", value: "_2062.NamedKey") -> None:
        pythonnet_property_set(self.wrapped, "DatabaseKey", value.wrapped)

    @property
    @exception_bridge
    def report_names(self: "Self") -> "List[str]":
        """List[str]

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "ReportNames")

        if temp is None:
            return None

        value = conversion.pn_to_mp_objects_in_list(temp, str)

        if value is None:
            return None

        return value

    @exception_bridge
    @enforce_parameter_types
    def output_default_report_to(self: "Self", file_path: "PathLike") -> None:
        """Method does not return.

        Args:
            file_path (PathLike)
        """
        file_path = str(file_path)
        pythonnet_method_call(self.wrapped, "OutputDefaultReportTo", file_path)

    @exception_bridge
    def get_default_report_with_encoded_images(self: "Self") -> "str":
        """str"""
        method_result = pythonnet_method_call(
            self.wrapped, "GetDefaultReportWithEncodedImages"
        )
        return method_result

    @exception_bridge
    @enforce_parameter_types
    def output_active_report_to(self: "Self", file_path: "PathLike") -> None:
        """Method does not return.

        Args:
            file_path (PathLike)
        """
        file_path = str(file_path)
        pythonnet_method_call(self.wrapped, "OutputActiveReportTo", file_path)

    @exception_bridge
    @enforce_parameter_types
    def output_active_report_as_text_to(self: "Self", file_path: "PathLike") -> None:
        """Method does not return.

        Args:
            file_path (PathLike)
        """
        file_path = str(file_path)
        pythonnet_method_call(self.wrapped, "OutputActiveReportAsTextTo", file_path)

    @exception_bridge
    def get_active_report_with_encoded_images(self: "Self") -> "str":
        """str"""
        method_result = pythonnet_method_call(
            self.wrapped, "GetActiveReportWithEncodedImages"
        )
        return method_result

    @exception_bridge
    @enforce_parameter_types
    def output_named_report_to(
        self: "Self", report_name: "str", file_path: "PathLike"
    ) -> None:
        """Method does not return.

        Args:
            report_name (str)
            file_path (PathLike)
        """
        report_name = str(report_name)
        file_path = str(file_path)
        pythonnet_method_call(
            self.wrapped,
            "OutputNamedReportTo",
            report_name if report_name else "",
            file_path,
        )

    @exception_bridge
    @enforce_parameter_types
    def output_named_report_as_masta_report(
        self: "Self", report_name: "str", file_path: "PathLike"
    ) -> None:
        """Method does not return.

        Args:
            report_name (str)
            file_path (PathLike)
        """
        report_name = str(report_name)
        file_path = str(file_path)
        pythonnet_method_call(
            self.wrapped,
            "OutputNamedReportAsMastaReport",
            report_name if report_name else "",
            file_path,
        )

    @exception_bridge
    @enforce_parameter_types
    def output_named_report_as_text_to(
        self: "Self", report_name: "str", file_path: "PathLike"
    ) -> None:
        """Method does not return.

        Args:
            report_name (str)
            file_path (PathLike)
        """
        report_name = str(report_name)
        file_path = str(file_path)
        pythonnet_method_call(
            self.wrapped,
            "OutputNamedReportAsTextTo",
            report_name if report_name else "",
            file_path,
        )

    @exception_bridge
    @enforce_parameter_types
    def get_named_report_with_encoded_images(self: "Self", report_name: "str") -> "str":
        """str

        Args:
            report_name (str)
        """
        report_name = str(report_name)
        method_result = pythonnet_method_call(
            self.wrapped,
            "GetNamedReportWithEncodedImages",
            report_name if report_name else "",
        )
        return method_result

    @property
    def cast_to(self: "Self") -> "_Cast_NamedDatabaseItem":
        """Cast to another type.

        Returns:
            _Cast_NamedDatabaseItem
        """
        return _Cast_NamedDatabaseItem(self)
