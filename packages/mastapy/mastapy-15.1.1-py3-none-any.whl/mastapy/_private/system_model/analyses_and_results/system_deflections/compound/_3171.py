"""ComponentCompoundSystemDeflection"""

from __future__ import annotations

from typing import TYPE_CHECKING, ClassVar

from mastapy._private._internal.dataclasses import extended_dataclass
from mastapy._private._internal.exception_bridge import exception_bridge
from mastapy._private._internal.exceptions import CastException
from mastapy._private._internal.python_net import (
    python_net_import,
    pythonnet_property_get,
)

from mastapy._private._internal import conversion, utility
from mastapy._private.system_model.analyses_and_results.system_deflections.compound import (
    _3228,
)

_COMPONENT_COMPOUND_SYSTEM_DEFLECTION = python_net_import(
    "SMT.MastaAPI.SystemModel.AnalysesAndResults.SystemDeflections.Compound",
    "ComponentCompoundSystemDeflection",
)

if TYPE_CHECKING:
    from typing import Any, List, Type, TypeVar

    from mastapy._private.system_model.analyses_and_results import _2943
    from mastapy._private.system_model.analyses_and_results.analysis_cases import (
        _7939,
        _7942,
    )
    from mastapy._private.system_model.analyses_and_results.system_deflections import (
        _3007,
    )
    from mastapy._private.system_model.analyses_and_results.system_deflections.compound import (
        _3147,
        _3148,
        _3150,
        _3154,
        _3157,
        _3160,
        _3161,
        _3162,
        _3165,
        _3169,
        _3174,
        _3175,
        _3178,
        _3182,
        _3185,
        _3188,
        _3191,
        _3193,
        _3196,
        _3197,
        _3199,
        _3200,
        _3203,
        _3205,
        _3208,
        _3209,
        _3213,
        _3216,
        _3219,
        _3222,
        _3223,
        _3225,
        _3226,
        _3227,
        _3231,
        _3234,
        _3235,
        _3236,
        _3237,
        _3238,
        _3241,
        _3244,
        _3246,
        _3249,
        _3254,
        _3255,
        _3258,
        _3261,
        _3262,
        _3264,
        _3265,
        _3266,
        _3269,
        _3270,
        _3271,
        _3272,
        _3273,
        _3276,
    )

    Self = TypeVar("Self", bound="ComponentCompoundSystemDeflection")
    CastSelf = TypeVar(
        "CastSelf",
        bound="ComponentCompoundSystemDeflection._Cast_ComponentCompoundSystemDeflection",
    )


__docformat__ = "restructuredtext en"
__all__ = ("ComponentCompoundSystemDeflection",)


@extended_dataclass(frozen=True, slots=True, weakref_slot=True)
class _Cast_ComponentCompoundSystemDeflection:
    """Special nested class for casting ComponentCompoundSystemDeflection to subclasses."""

    __parent__: "ComponentCompoundSystemDeflection"

    @property
    def part_compound_system_deflection(
        self: "CastSelf",
    ) -> "_3228.PartCompoundSystemDeflection":
        return self.__parent__._cast(_3228.PartCompoundSystemDeflection)

    @property
    def part_compound_analysis(self: "CastSelf") -> "_7942.PartCompoundAnalysis":
        from mastapy._private.system_model.analyses_and_results.analysis_cases import (
            _7942,
        )

        return self.__parent__._cast(_7942.PartCompoundAnalysis)

    @property
    def design_entity_compound_analysis(
        self: "CastSelf",
    ) -> "_7939.DesignEntityCompoundAnalysis":
        from mastapy._private.system_model.analyses_and_results.analysis_cases import (
            _7939,
        )

        return self.__parent__._cast(_7939.DesignEntityCompoundAnalysis)

    @property
    def design_entity_analysis(self: "CastSelf") -> "_2943.DesignEntityAnalysis":
        from mastapy._private.system_model.analyses_and_results import _2943

        return self.__parent__._cast(_2943.DesignEntityAnalysis)

    @property
    def abstract_shaft_compound_system_deflection(
        self: "CastSelf",
    ) -> "_3147.AbstractShaftCompoundSystemDeflection":
        from mastapy._private.system_model.analyses_and_results.system_deflections.compound import (
            _3147,
        )

        return self.__parent__._cast(_3147.AbstractShaftCompoundSystemDeflection)

    @property
    def abstract_shaft_or_housing_compound_system_deflection(
        self: "CastSelf",
    ) -> "_3148.AbstractShaftOrHousingCompoundSystemDeflection":
        from mastapy._private.system_model.analyses_and_results.system_deflections.compound import (
            _3148,
        )

        return self.__parent__._cast(
            _3148.AbstractShaftOrHousingCompoundSystemDeflection
        )

    @property
    def agma_gleason_conical_gear_compound_system_deflection(
        self: "CastSelf",
    ) -> "_3150.AGMAGleasonConicalGearCompoundSystemDeflection":
        from mastapy._private.system_model.analyses_and_results.system_deflections.compound import (
            _3150,
        )

        return self.__parent__._cast(
            _3150.AGMAGleasonConicalGearCompoundSystemDeflection
        )

    @property
    def bearing_compound_system_deflection(
        self: "CastSelf",
    ) -> "_3154.BearingCompoundSystemDeflection":
        from mastapy._private.system_model.analyses_and_results.system_deflections.compound import (
            _3154,
        )

        return self.__parent__._cast(_3154.BearingCompoundSystemDeflection)

    @property
    def bevel_differential_gear_compound_system_deflection(
        self: "CastSelf",
    ) -> "_3157.BevelDifferentialGearCompoundSystemDeflection":
        from mastapy._private.system_model.analyses_and_results.system_deflections.compound import (
            _3157,
        )

        return self.__parent__._cast(
            _3157.BevelDifferentialGearCompoundSystemDeflection
        )

    @property
    def bevel_differential_planet_gear_compound_system_deflection(
        self: "CastSelf",
    ) -> "_3160.BevelDifferentialPlanetGearCompoundSystemDeflection":
        from mastapy._private.system_model.analyses_and_results.system_deflections.compound import (
            _3160,
        )

        return self.__parent__._cast(
            _3160.BevelDifferentialPlanetGearCompoundSystemDeflection
        )

    @property
    def bevel_differential_sun_gear_compound_system_deflection(
        self: "CastSelf",
    ) -> "_3161.BevelDifferentialSunGearCompoundSystemDeflection":
        from mastapy._private.system_model.analyses_and_results.system_deflections.compound import (
            _3161,
        )

        return self.__parent__._cast(
            _3161.BevelDifferentialSunGearCompoundSystemDeflection
        )

    @property
    def bevel_gear_compound_system_deflection(
        self: "CastSelf",
    ) -> "_3162.BevelGearCompoundSystemDeflection":
        from mastapy._private.system_model.analyses_and_results.system_deflections.compound import (
            _3162,
        )

        return self.__parent__._cast(_3162.BevelGearCompoundSystemDeflection)

    @property
    def bolt_compound_system_deflection(
        self: "CastSelf",
    ) -> "_3165.BoltCompoundSystemDeflection":
        from mastapy._private.system_model.analyses_and_results.system_deflections.compound import (
            _3165,
        )

        return self.__parent__._cast(_3165.BoltCompoundSystemDeflection)

    @property
    def clutch_half_compound_system_deflection(
        self: "CastSelf",
    ) -> "_3169.ClutchHalfCompoundSystemDeflection":
        from mastapy._private.system_model.analyses_and_results.system_deflections.compound import (
            _3169,
        )

        return self.__parent__._cast(_3169.ClutchHalfCompoundSystemDeflection)

    @property
    def concept_coupling_half_compound_system_deflection(
        self: "CastSelf",
    ) -> "_3174.ConceptCouplingHalfCompoundSystemDeflection":
        from mastapy._private.system_model.analyses_and_results.system_deflections.compound import (
            _3174,
        )

        return self.__parent__._cast(_3174.ConceptCouplingHalfCompoundSystemDeflection)

    @property
    def concept_gear_compound_system_deflection(
        self: "CastSelf",
    ) -> "_3175.ConceptGearCompoundSystemDeflection":
        from mastapy._private.system_model.analyses_and_results.system_deflections.compound import (
            _3175,
        )

        return self.__parent__._cast(_3175.ConceptGearCompoundSystemDeflection)

    @property
    def conical_gear_compound_system_deflection(
        self: "CastSelf",
    ) -> "_3178.ConicalGearCompoundSystemDeflection":
        from mastapy._private.system_model.analyses_and_results.system_deflections.compound import (
            _3178,
        )

        return self.__parent__._cast(_3178.ConicalGearCompoundSystemDeflection)

    @property
    def connector_compound_system_deflection(
        self: "CastSelf",
    ) -> "_3182.ConnectorCompoundSystemDeflection":
        from mastapy._private.system_model.analyses_and_results.system_deflections.compound import (
            _3182,
        )

        return self.__parent__._cast(_3182.ConnectorCompoundSystemDeflection)

    @property
    def coupling_half_compound_system_deflection(
        self: "CastSelf",
    ) -> "_3185.CouplingHalfCompoundSystemDeflection":
        from mastapy._private.system_model.analyses_and_results.system_deflections.compound import (
            _3185,
        )

        return self.__parent__._cast(_3185.CouplingHalfCompoundSystemDeflection)

    @property
    def cvt_pulley_compound_system_deflection(
        self: "CastSelf",
    ) -> "_3188.CVTPulleyCompoundSystemDeflection":
        from mastapy._private.system_model.analyses_and_results.system_deflections.compound import (
            _3188,
        )

        return self.__parent__._cast(_3188.CVTPulleyCompoundSystemDeflection)

    @property
    def cycloidal_disc_compound_system_deflection(
        self: "CastSelf",
    ) -> "_3191.CycloidalDiscCompoundSystemDeflection":
        from mastapy._private.system_model.analyses_and_results.system_deflections.compound import (
            _3191,
        )

        return self.__parent__._cast(_3191.CycloidalDiscCompoundSystemDeflection)

    @property
    def cylindrical_gear_compound_system_deflection(
        self: "CastSelf",
    ) -> "_3193.CylindricalGearCompoundSystemDeflection":
        from mastapy._private.system_model.analyses_and_results.system_deflections.compound import (
            _3193,
        )

        return self.__parent__._cast(_3193.CylindricalGearCompoundSystemDeflection)

    @property
    def cylindrical_planet_gear_compound_system_deflection(
        self: "CastSelf",
    ) -> "_3196.CylindricalPlanetGearCompoundSystemDeflection":
        from mastapy._private.system_model.analyses_and_results.system_deflections.compound import (
            _3196,
        )

        return self.__parent__._cast(
            _3196.CylindricalPlanetGearCompoundSystemDeflection
        )

    @property
    def datum_compound_system_deflection(
        self: "CastSelf",
    ) -> "_3197.DatumCompoundSystemDeflection":
        from mastapy._private.system_model.analyses_and_results.system_deflections.compound import (
            _3197,
        )

        return self.__parent__._cast(_3197.DatumCompoundSystemDeflection)

    @property
    def external_cad_model_compound_system_deflection(
        self: "CastSelf",
    ) -> "_3199.ExternalCADModelCompoundSystemDeflection":
        from mastapy._private.system_model.analyses_and_results.system_deflections.compound import (
            _3199,
        )

        return self.__parent__._cast(_3199.ExternalCADModelCompoundSystemDeflection)

    @property
    def face_gear_compound_system_deflection(
        self: "CastSelf",
    ) -> "_3200.FaceGearCompoundSystemDeflection":
        from mastapy._private.system_model.analyses_and_results.system_deflections.compound import (
            _3200,
        )

        return self.__parent__._cast(_3200.FaceGearCompoundSystemDeflection)

    @property
    def fe_part_compound_system_deflection(
        self: "CastSelf",
    ) -> "_3203.FEPartCompoundSystemDeflection":
        from mastapy._private.system_model.analyses_and_results.system_deflections.compound import (
            _3203,
        )

        return self.__parent__._cast(_3203.FEPartCompoundSystemDeflection)

    @property
    def gear_compound_system_deflection(
        self: "CastSelf",
    ) -> "_3205.GearCompoundSystemDeflection":
        from mastapy._private.system_model.analyses_and_results.system_deflections.compound import (
            _3205,
        )

        return self.__parent__._cast(_3205.GearCompoundSystemDeflection)

    @property
    def guide_dxf_model_compound_system_deflection(
        self: "CastSelf",
    ) -> "_3208.GuideDxfModelCompoundSystemDeflection":
        from mastapy._private.system_model.analyses_and_results.system_deflections.compound import (
            _3208,
        )

        return self.__parent__._cast(_3208.GuideDxfModelCompoundSystemDeflection)

    @property
    def hypoid_gear_compound_system_deflection(
        self: "CastSelf",
    ) -> "_3209.HypoidGearCompoundSystemDeflection":
        from mastapy._private.system_model.analyses_and_results.system_deflections.compound import (
            _3209,
        )

        return self.__parent__._cast(_3209.HypoidGearCompoundSystemDeflection)

    @property
    def klingelnberg_cyclo_palloid_conical_gear_compound_system_deflection(
        self: "CastSelf",
    ) -> "_3213.KlingelnbergCycloPalloidConicalGearCompoundSystemDeflection":
        from mastapy._private.system_model.analyses_and_results.system_deflections.compound import (
            _3213,
        )

        return self.__parent__._cast(
            _3213.KlingelnbergCycloPalloidConicalGearCompoundSystemDeflection
        )

    @property
    def klingelnberg_cyclo_palloid_hypoid_gear_compound_system_deflection(
        self: "CastSelf",
    ) -> "_3216.KlingelnbergCycloPalloidHypoidGearCompoundSystemDeflection":
        from mastapy._private.system_model.analyses_and_results.system_deflections.compound import (
            _3216,
        )

        return self.__parent__._cast(
            _3216.KlingelnbergCycloPalloidHypoidGearCompoundSystemDeflection
        )

    @property
    def klingelnberg_cyclo_palloid_spiral_bevel_gear_compound_system_deflection(
        self: "CastSelf",
    ) -> "_3219.KlingelnbergCycloPalloidSpiralBevelGearCompoundSystemDeflection":
        from mastapy._private.system_model.analyses_and_results.system_deflections.compound import (
            _3219,
        )

        return self.__parent__._cast(
            _3219.KlingelnbergCycloPalloidSpiralBevelGearCompoundSystemDeflection
        )

    @property
    def mass_disc_compound_system_deflection(
        self: "CastSelf",
    ) -> "_3222.MassDiscCompoundSystemDeflection":
        from mastapy._private.system_model.analyses_and_results.system_deflections.compound import (
            _3222,
        )

        return self.__parent__._cast(_3222.MassDiscCompoundSystemDeflection)

    @property
    def measurement_component_compound_system_deflection(
        self: "CastSelf",
    ) -> "_3223.MeasurementComponentCompoundSystemDeflection":
        from mastapy._private.system_model.analyses_and_results.system_deflections.compound import (
            _3223,
        )

        return self.__parent__._cast(_3223.MeasurementComponentCompoundSystemDeflection)

    @property
    def microphone_compound_system_deflection(
        self: "CastSelf",
    ) -> "_3225.MicrophoneCompoundSystemDeflection":
        from mastapy._private.system_model.analyses_and_results.system_deflections.compound import (
            _3225,
        )

        return self.__parent__._cast(_3225.MicrophoneCompoundSystemDeflection)

    @property
    def mountable_component_compound_system_deflection(
        self: "CastSelf",
    ) -> "_3226.MountableComponentCompoundSystemDeflection":
        from mastapy._private.system_model.analyses_and_results.system_deflections.compound import (
            _3226,
        )

        return self.__parent__._cast(_3226.MountableComponentCompoundSystemDeflection)

    @property
    def oil_seal_compound_system_deflection(
        self: "CastSelf",
    ) -> "_3227.OilSealCompoundSystemDeflection":
        from mastapy._private.system_model.analyses_and_results.system_deflections.compound import (
            _3227,
        )

        return self.__parent__._cast(_3227.OilSealCompoundSystemDeflection)

    @property
    def part_to_part_shear_coupling_half_compound_system_deflection(
        self: "CastSelf",
    ) -> "_3231.PartToPartShearCouplingHalfCompoundSystemDeflection":
        from mastapy._private.system_model.analyses_and_results.system_deflections.compound import (
            _3231,
        )

        return self.__parent__._cast(
            _3231.PartToPartShearCouplingHalfCompoundSystemDeflection
        )

    @property
    def planet_carrier_compound_system_deflection(
        self: "CastSelf",
    ) -> "_3234.PlanetCarrierCompoundSystemDeflection":
        from mastapy._private.system_model.analyses_and_results.system_deflections.compound import (
            _3234,
        )

        return self.__parent__._cast(_3234.PlanetCarrierCompoundSystemDeflection)

    @property
    def point_load_compound_system_deflection(
        self: "CastSelf",
    ) -> "_3235.PointLoadCompoundSystemDeflection":
        from mastapy._private.system_model.analyses_and_results.system_deflections.compound import (
            _3235,
        )

        return self.__parent__._cast(_3235.PointLoadCompoundSystemDeflection)

    @property
    def power_load_compound_system_deflection(
        self: "CastSelf",
    ) -> "_3236.PowerLoadCompoundSystemDeflection":
        from mastapy._private.system_model.analyses_and_results.system_deflections.compound import (
            _3236,
        )

        return self.__parent__._cast(_3236.PowerLoadCompoundSystemDeflection)

    @property
    def pulley_compound_system_deflection(
        self: "CastSelf",
    ) -> "_3237.PulleyCompoundSystemDeflection":
        from mastapy._private.system_model.analyses_and_results.system_deflections.compound import (
            _3237,
        )

        return self.__parent__._cast(_3237.PulleyCompoundSystemDeflection)

    @property
    def ring_pins_compound_system_deflection(
        self: "CastSelf",
    ) -> "_3238.RingPinsCompoundSystemDeflection":
        from mastapy._private.system_model.analyses_and_results.system_deflections.compound import (
            _3238,
        )

        return self.__parent__._cast(_3238.RingPinsCompoundSystemDeflection)

    @property
    def rolling_ring_compound_system_deflection(
        self: "CastSelf",
    ) -> "_3241.RollingRingCompoundSystemDeflection":
        from mastapy._private.system_model.analyses_and_results.system_deflections.compound import (
            _3241,
        )

        return self.__parent__._cast(_3241.RollingRingCompoundSystemDeflection)

    @property
    def shaft_compound_system_deflection(
        self: "CastSelf",
    ) -> "_3244.ShaftCompoundSystemDeflection":
        from mastapy._private.system_model.analyses_and_results.system_deflections.compound import (
            _3244,
        )

        return self.__parent__._cast(_3244.ShaftCompoundSystemDeflection)

    @property
    def shaft_hub_connection_compound_system_deflection(
        self: "CastSelf",
    ) -> "_3246.ShaftHubConnectionCompoundSystemDeflection":
        from mastapy._private.system_model.analyses_and_results.system_deflections.compound import (
            _3246,
        )

        return self.__parent__._cast(_3246.ShaftHubConnectionCompoundSystemDeflection)

    @property
    def spiral_bevel_gear_compound_system_deflection(
        self: "CastSelf",
    ) -> "_3249.SpiralBevelGearCompoundSystemDeflection":
        from mastapy._private.system_model.analyses_and_results.system_deflections.compound import (
            _3249,
        )

        return self.__parent__._cast(_3249.SpiralBevelGearCompoundSystemDeflection)

    @property
    def spring_damper_half_compound_system_deflection(
        self: "CastSelf",
    ) -> "_3254.SpringDamperHalfCompoundSystemDeflection":
        from mastapy._private.system_model.analyses_and_results.system_deflections.compound import (
            _3254,
        )

        return self.__parent__._cast(_3254.SpringDamperHalfCompoundSystemDeflection)

    @property
    def straight_bevel_diff_gear_compound_system_deflection(
        self: "CastSelf",
    ) -> "_3255.StraightBevelDiffGearCompoundSystemDeflection":
        from mastapy._private.system_model.analyses_and_results.system_deflections.compound import (
            _3255,
        )

        return self.__parent__._cast(
            _3255.StraightBevelDiffGearCompoundSystemDeflection
        )

    @property
    def straight_bevel_gear_compound_system_deflection(
        self: "CastSelf",
    ) -> "_3258.StraightBevelGearCompoundSystemDeflection":
        from mastapy._private.system_model.analyses_and_results.system_deflections.compound import (
            _3258,
        )

        return self.__parent__._cast(_3258.StraightBevelGearCompoundSystemDeflection)

    @property
    def straight_bevel_planet_gear_compound_system_deflection(
        self: "CastSelf",
    ) -> "_3261.StraightBevelPlanetGearCompoundSystemDeflection":
        from mastapy._private.system_model.analyses_and_results.system_deflections.compound import (
            _3261,
        )

        return self.__parent__._cast(
            _3261.StraightBevelPlanetGearCompoundSystemDeflection
        )

    @property
    def straight_bevel_sun_gear_compound_system_deflection(
        self: "CastSelf",
    ) -> "_3262.StraightBevelSunGearCompoundSystemDeflection":
        from mastapy._private.system_model.analyses_and_results.system_deflections.compound import (
            _3262,
        )

        return self.__parent__._cast(_3262.StraightBevelSunGearCompoundSystemDeflection)

    @property
    def synchroniser_half_compound_system_deflection(
        self: "CastSelf",
    ) -> "_3264.SynchroniserHalfCompoundSystemDeflection":
        from mastapy._private.system_model.analyses_and_results.system_deflections.compound import (
            _3264,
        )

        return self.__parent__._cast(_3264.SynchroniserHalfCompoundSystemDeflection)

    @property
    def synchroniser_part_compound_system_deflection(
        self: "CastSelf",
    ) -> "_3265.SynchroniserPartCompoundSystemDeflection":
        from mastapy._private.system_model.analyses_and_results.system_deflections.compound import (
            _3265,
        )

        return self.__parent__._cast(_3265.SynchroniserPartCompoundSystemDeflection)

    @property
    def synchroniser_sleeve_compound_system_deflection(
        self: "CastSelf",
    ) -> "_3266.SynchroniserSleeveCompoundSystemDeflection":
        from mastapy._private.system_model.analyses_and_results.system_deflections.compound import (
            _3266,
        )

        return self.__parent__._cast(_3266.SynchroniserSleeveCompoundSystemDeflection)

    @property
    def torque_converter_pump_compound_system_deflection(
        self: "CastSelf",
    ) -> "_3269.TorqueConverterPumpCompoundSystemDeflection":
        from mastapy._private.system_model.analyses_and_results.system_deflections.compound import (
            _3269,
        )

        return self.__parent__._cast(_3269.TorqueConverterPumpCompoundSystemDeflection)

    @property
    def torque_converter_turbine_compound_system_deflection(
        self: "CastSelf",
    ) -> "_3270.TorqueConverterTurbineCompoundSystemDeflection":
        from mastapy._private.system_model.analyses_and_results.system_deflections.compound import (
            _3270,
        )

        return self.__parent__._cast(
            _3270.TorqueConverterTurbineCompoundSystemDeflection
        )

    @property
    def unbalanced_mass_compound_system_deflection(
        self: "CastSelf",
    ) -> "_3271.UnbalancedMassCompoundSystemDeflection":
        from mastapy._private.system_model.analyses_and_results.system_deflections.compound import (
            _3271,
        )

        return self.__parent__._cast(_3271.UnbalancedMassCompoundSystemDeflection)

    @property
    def virtual_component_compound_system_deflection(
        self: "CastSelf",
    ) -> "_3272.VirtualComponentCompoundSystemDeflection":
        from mastapy._private.system_model.analyses_and_results.system_deflections.compound import (
            _3272,
        )

        return self.__parent__._cast(_3272.VirtualComponentCompoundSystemDeflection)

    @property
    def worm_gear_compound_system_deflection(
        self: "CastSelf",
    ) -> "_3273.WormGearCompoundSystemDeflection":
        from mastapy._private.system_model.analyses_and_results.system_deflections.compound import (
            _3273,
        )

        return self.__parent__._cast(_3273.WormGearCompoundSystemDeflection)

    @property
    def zerol_bevel_gear_compound_system_deflection(
        self: "CastSelf",
    ) -> "_3276.ZerolBevelGearCompoundSystemDeflection":
        from mastapy._private.system_model.analyses_and_results.system_deflections.compound import (
            _3276,
        )

        return self.__parent__._cast(_3276.ZerolBevelGearCompoundSystemDeflection)

    @property
    def component_compound_system_deflection(
        self: "CastSelf",
    ) -> "ComponentCompoundSystemDeflection":
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
class ComponentCompoundSystemDeflection(_3228.PartCompoundSystemDeflection):
    """ComponentCompoundSystemDeflection

    This is a mastapy class.
    """

    TYPE: ClassVar["Type"] = _COMPONENT_COMPOUND_SYSTEM_DEFLECTION

    wrapped: "Any"

    def __post_init__(self: "Self") -> None:
        """Override of the post initialisation magic method."""
        if not hasattr(self.wrapped, "reference_count"):
            self.wrapped.reference_count = 0

        self.wrapped.reference_count += 1

    @property
    @exception_bridge
    def energy_lost(self: "Self") -> "float":
        """float

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "EnergyLost")

        if temp is None:
            return 0.0

        return temp

    @property
    @exception_bridge
    def energy_lost_contribution(self: "Self") -> "float":
        """float

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "EnergyLostContribution")

        if temp is None:
            return 0.0

        return temp

    @property
    @exception_bridge
    def component_analysis_cases(
        self: "Self",
    ) -> "List[_3007.ComponentSystemDeflection]":
        """List[mastapy.system_model.analyses_and_results.system_deflections.ComponentSystemDeflection]

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "ComponentAnalysisCases")

        if temp is None:
            return None

        value = conversion.pn_to_mp_objects_in_list(temp)

        if value is None:
            return None

        return value

    @property
    @exception_bridge
    def component_analysis_cases_ready(
        self: "Self",
    ) -> "List[_3007.ComponentSystemDeflection]":
        """List[mastapy.system_model.analyses_and_results.system_deflections.ComponentSystemDeflection]

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "ComponentAnalysisCasesReady")

        if temp is None:
            return None

        value = conversion.pn_to_mp_objects_in_list(temp)

        if value is None:
            return None

        return value

    @property
    def cast_to(self: "Self") -> "_Cast_ComponentCompoundSystemDeflection":
        """Cast to another type.

        Returns:
            _Cast_ComponentCompoundSystemDeflection
        """
        return _Cast_ComponentCompoundSystemDeflection(self)
