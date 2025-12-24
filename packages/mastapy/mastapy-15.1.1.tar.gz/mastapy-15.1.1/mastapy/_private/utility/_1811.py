"""IndependentReportablePropertiesBase"""

from __future__ import annotations

from typing import TYPE_CHECKING, ClassVar, Generic, TypeVar

from mastapy._private._internal.dataclasses import extended_dataclass
from mastapy._private._internal.exceptions import CastException
from mastapy._private._internal.python_net import python_net_import

from mastapy._private import _0
from mastapy._private._internal import utility

_INDEPENDENT_REPORTABLE_PROPERTIES_BASE = python_net_import(
    "SMT.MastaAPI.Utility", "IndependentReportablePropertiesBase"
)

if TYPE_CHECKING:
    from typing import Any, Type

    from mastapy._private.bearings.bearing_results import _2185
    from mastapy._private.bearings.bearing_results.rolling import _2217, _2316
    from mastapy._private.bearings.tolerances import _2155
    from mastapy._private.electric_machines import _1411
    from mastapy._private.electric_machines.load_cases_and_analyses import _1588
    from mastapy._private.gears import _458
    from mastapy._private.gears.gear_designs.cylindrical import (
        _1152,
        _1183,
        _1191,
        _1192,
        _1195,
        _1196,
        _1205,
        _1213,
        _1215,
        _1219,
        _1223,
    )
    from mastapy._private.geometry import _415
    from mastapy._private.materials import _389
    from mastapy._private.materials.efficiency import _395, _401
    from mastapy._private.math_utility.measured_data import _1782, _1783, _1784
    from mastapy._private.system_model.analyses_and_results.static_loads import _7731
    from mastapy._private.utility import _1823

    Self = TypeVar("Self", bound="IndependentReportablePropertiesBase")
    CastSelf = TypeVar(
        "CastSelf",
        bound="IndependentReportablePropertiesBase._Cast_IndependentReportablePropertiesBase",
    )

T = TypeVar("T", bound="IndependentReportablePropertiesBase")

__docformat__ = "restructuredtext en"
__all__ = ("IndependentReportablePropertiesBase",)


@extended_dataclass(frozen=True, slots=True, weakref_slot=True)
class _Cast_IndependentReportablePropertiesBase:
    """Special nested class for casting IndependentReportablePropertiesBase to subclasses."""

    __parent__: "IndependentReportablePropertiesBase"

    @property
    def temperature_dependent_property(
        self: "CastSelf",
    ) -> "_389.TemperatureDependentProperty":
        from mastapy._private.materials import _389

        return self.__parent__._cast(_389.TemperatureDependentProperty)

    @property
    def baffle_loss(self: "CastSelf") -> "_395.BaffleLoss":
        from mastapy._private.materials.efficiency import _395

        return self.__parent__._cast(_395.BaffleLoss)

    @property
    def oil_pump_detail(self: "CastSelf") -> "_401.OilPumpDetail":
        from mastapy._private.materials.efficiency import _401

        return self.__parent__._cast(_401.OilPumpDetail)

    @property
    def packaging_limits(self: "CastSelf") -> "_415.PackagingLimits":
        from mastapy._private.geometry import _415

        return self.__parent__._cast(_415.PackagingLimits)

    @property
    def specification_for_the_effect_of_oil_kinematic_viscosity(
        self: "CastSelf",
    ) -> "_458.SpecificationForTheEffectOfOilKinematicViscosity":
        from mastapy._private.gears import _458

        return self.__parent__._cast(
            _458.SpecificationForTheEffectOfOilKinematicViscosity
        )

    @property
    def cylindrical_gear_micro_geometry_settings(
        self: "CastSelf",
    ) -> "_1152.CylindricalGearMicroGeometrySettings":
        from mastapy._private.gears.gear_designs.cylindrical import _1152

        return self.__parent__._cast(_1152.CylindricalGearMicroGeometrySettings)

    @property
    def hardened_material_properties(
        self: "CastSelf",
    ) -> "_1183.HardenedMaterialProperties":
        from mastapy._private.gears.gear_designs.cylindrical import _1183

        return self.__parent__._cast(_1183.HardenedMaterialProperties)

    @property
    def ltca_load_case_modifiable_settings(
        self: "CastSelf",
    ) -> "_1191.LTCALoadCaseModifiableSettings":
        from mastapy._private.gears.gear_designs.cylindrical import _1191

        return self.__parent__._cast(_1191.LTCALoadCaseModifiableSettings)

    @property
    def ltca_settings(self: "CastSelf") -> "_1192.LTCASettings":
        from mastapy._private.gears.gear_designs.cylindrical import _1192

        return self.__parent__._cast(_1192.LTCASettings)

    @property
    def micropitting(self: "CastSelf") -> "_1195.Micropitting":
        from mastapy._private.gears.gear_designs.cylindrical import _1195

        return self.__parent__._cast(_1195.Micropitting)

    @property
    def muller_residual_stress_definition(
        self: "CastSelf",
    ) -> "_1196.MullerResidualStressDefinition":
        from mastapy._private.gears.gear_designs.cylindrical import _1196

        return self.__parent__._cast(_1196.MullerResidualStressDefinition)

    @property
    def scuffing(self: "CastSelf") -> "_1205.Scuffing":
        from mastapy._private.gears.gear_designs.cylindrical import _1205

        return self.__parent__._cast(_1205.Scuffing)

    @property
    def surface_roughness(self: "CastSelf") -> "_1213.SurfaceRoughness":
        from mastapy._private.gears.gear_designs.cylindrical import _1213

        return self.__parent__._cast(_1213.SurfaceRoughness)

    @property
    def tiff_analysis_settings(self: "CastSelf") -> "_1215.TiffAnalysisSettings":
        from mastapy._private.gears.gear_designs.cylindrical import _1215

        return self.__parent__._cast(_1215.TiffAnalysisSettings)

    @property
    def tooth_flank_fracture_analysis_settings(
        self: "CastSelf",
    ) -> "_1219.ToothFlankFractureAnalysisSettings":
        from mastapy._private.gears.gear_designs.cylindrical import _1219

        return self.__parent__._cast(_1219.ToothFlankFractureAnalysisSettings)

    @property
    def usage(self: "CastSelf") -> "_1223.Usage":
        from mastapy._private.gears.gear_designs.cylindrical import _1223

        return self.__parent__._cast(_1223.Usage)

    @property
    def eccentricity(self: "CastSelf") -> "_1411.Eccentricity":
        from mastapy._private.electric_machines import _1411

        return self.__parent__._cast(_1411.Eccentricity)

    @property
    def temperatures(self: "CastSelf") -> "_1588.Temperatures":
        from mastapy._private.electric_machines.load_cases_and_analyses import _1588

        return self.__parent__._cast(_1588.Temperatures)

    @property
    def lookup_table_base(self: "CastSelf") -> "_1782.LookupTableBase":
        from mastapy._private.math_utility.measured_data import _1782

        return self.__parent__._cast(_1782.LookupTableBase)

    @property
    def onedimensional_function_lookup_table(
        self: "CastSelf",
    ) -> "_1783.OnedimensionalFunctionLookupTable":
        from mastapy._private.math_utility.measured_data import _1783

        return self.__parent__._cast(_1783.OnedimensionalFunctionLookupTable)

    @property
    def twodimensional_function_lookup_table(
        self: "CastSelf",
    ) -> "_1784.TwodimensionalFunctionLookupTable":
        from mastapy._private.math_utility.measured_data import _1784

        return self.__parent__._cast(_1784.TwodimensionalFunctionLookupTable)

    @property
    def skf_loss_moment_multipliers(
        self: "CastSelf",
    ) -> "_1823.SKFLossMomentMultipliers":
        from mastapy._private.utility import _1823

        return self.__parent__._cast(_1823.SKFLossMomentMultipliers)

    @property
    def roundness_specification(self: "CastSelf") -> "_2155.RoundnessSpecification":
        from mastapy._private.bearings.tolerances import _2155

        return self.__parent__._cast(_2155.RoundnessSpecification)

    @property
    def equivalent_load_factors(self: "CastSelf") -> "_2185.EquivalentLoadFactors":
        from mastapy._private.bearings.bearing_results import _2185

        return self.__parent__._cast(_2185.EquivalentLoadFactors)

    @property
    def iso14179_settings_per_bearing_type(
        self: "CastSelf",
    ) -> "_2217.ISO14179SettingsPerBearingType":
        from mastapy._private.bearings.bearing_results.rolling import _2217

        return self.__parent__._cast(_2217.ISO14179SettingsPerBearingType)

    @property
    def rolling_bearing_friction_coefficients(
        self: "CastSelf",
    ) -> "_2316.RollingBearingFrictionCoefficients":
        from mastapy._private.bearings.bearing_results.rolling import _2316

        return self.__parent__._cast(_2316.RollingBearingFrictionCoefficients)

    @property
    def additional_acceleration_options(
        self: "CastSelf",
    ) -> "_7731.AdditionalAccelerationOptions":
        from mastapy._private.system_model.analyses_and_results.static_loads import (
            _7731,
        )

        return self.__parent__._cast(_7731.AdditionalAccelerationOptions)

    @property
    def independent_reportable_properties_base(
        self: "CastSelf",
    ) -> "IndependentReportablePropertiesBase":
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
class IndependentReportablePropertiesBase(_0.APIBase, Generic[T]):
    """IndependentReportablePropertiesBase

    This is a mastapy class.

    Generic Types:
        T
    """

    TYPE: ClassVar["Type"] = _INDEPENDENT_REPORTABLE_PROPERTIES_BASE

    wrapped: "Any"

    def __post_init__(self: "Self") -> None:
        """Override of the post initialisation magic method."""
        if not hasattr(self.wrapped, "reference_count"):
            self.wrapped.reference_count = 0

        self.wrapped.reference_count += 1

    @property
    def cast_to(self: "Self") -> "_Cast_IndependentReportablePropertiesBase":
        """Cast to another type.

        Returns:
            _Cast_IndependentReportablePropertiesBase
        """
        return _Cast_IndependentReportablePropertiesBase(self)
