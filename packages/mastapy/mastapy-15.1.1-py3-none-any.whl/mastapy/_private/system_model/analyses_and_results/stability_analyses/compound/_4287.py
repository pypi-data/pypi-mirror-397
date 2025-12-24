"""MountableComponentCompoundStabilityAnalysis"""

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
from mastapy._private.system_model.analyses_and_results.stability_analyses.compound import (
    _4233,
)

_MOUNTABLE_COMPONENT_COMPOUND_STABILITY_ANALYSIS = python_net_import(
    "SMT.MastaAPI.SystemModel.AnalysesAndResults.StabilityAnalyses.Compound",
    "MountableComponentCompoundStabilityAnalysis",
)

if TYPE_CHECKING:
    from typing import Any, List, Type, TypeVar

    from mastapy._private.system_model.analyses_and_results import _2943
    from mastapy._private.system_model.analyses_and_results.analysis_cases import (
        _7939,
        _7942,
    )
    from mastapy._private.system_model.analyses_and_results.stability_analyses import (
        _4153,
    )
    from mastapy._private.system_model.analyses_and_results.stability_analyses.compound import (
        _4212,
        _4216,
        _4219,
        _4222,
        _4223,
        _4224,
        _4231,
        _4236,
        _4237,
        _4240,
        _4244,
        _4247,
        _4250,
        _4255,
        _4258,
        _4261,
        _4266,
        _4270,
        _4274,
        _4277,
        _4280,
        _4283,
        _4284,
        _4288,
        _4289,
        _4292,
        _4295,
        _4296,
        _4297,
        _4298,
        _4299,
        _4302,
        _4306,
        _4309,
        _4314,
        _4315,
        _4318,
        _4321,
        _4322,
        _4324,
        _4325,
        _4326,
        _4329,
        _4330,
        _4331,
        _4332,
        _4333,
        _4336,
    )

    Self = TypeVar("Self", bound="MountableComponentCompoundStabilityAnalysis")
    CastSelf = TypeVar(
        "CastSelf",
        bound="MountableComponentCompoundStabilityAnalysis._Cast_MountableComponentCompoundStabilityAnalysis",
    )


__docformat__ = "restructuredtext en"
__all__ = ("MountableComponentCompoundStabilityAnalysis",)


@extended_dataclass(frozen=True, slots=True, weakref_slot=True)
class _Cast_MountableComponentCompoundStabilityAnalysis:
    """Special nested class for casting MountableComponentCompoundStabilityAnalysis to subclasses."""

    __parent__: "MountableComponentCompoundStabilityAnalysis"

    @property
    def component_compound_stability_analysis(
        self: "CastSelf",
    ) -> "_4233.ComponentCompoundStabilityAnalysis":
        return self.__parent__._cast(_4233.ComponentCompoundStabilityAnalysis)

    @property
    def part_compound_stability_analysis(
        self: "CastSelf",
    ) -> "_4289.PartCompoundStabilityAnalysis":
        from mastapy._private.system_model.analyses_and_results.stability_analyses.compound import (
            _4289,
        )

        return self.__parent__._cast(_4289.PartCompoundStabilityAnalysis)

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
    def agma_gleason_conical_gear_compound_stability_analysis(
        self: "CastSelf",
    ) -> "_4212.AGMAGleasonConicalGearCompoundStabilityAnalysis":
        from mastapy._private.system_model.analyses_and_results.stability_analyses.compound import (
            _4212,
        )

        return self.__parent__._cast(
            _4212.AGMAGleasonConicalGearCompoundStabilityAnalysis
        )

    @property
    def bearing_compound_stability_analysis(
        self: "CastSelf",
    ) -> "_4216.BearingCompoundStabilityAnalysis":
        from mastapy._private.system_model.analyses_and_results.stability_analyses.compound import (
            _4216,
        )

        return self.__parent__._cast(_4216.BearingCompoundStabilityAnalysis)

    @property
    def bevel_differential_gear_compound_stability_analysis(
        self: "CastSelf",
    ) -> "_4219.BevelDifferentialGearCompoundStabilityAnalysis":
        from mastapy._private.system_model.analyses_and_results.stability_analyses.compound import (
            _4219,
        )

        return self.__parent__._cast(
            _4219.BevelDifferentialGearCompoundStabilityAnalysis
        )

    @property
    def bevel_differential_planet_gear_compound_stability_analysis(
        self: "CastSelf",
    ) -> "_4222.BevelDifferentialPlanetGearCompoundStabilityAnalysis":
        from mastapy._private.system_model.analyses_and_results.stability_analyses.compound import (
            _4222,
        )

        return self.__parent__._cast(
            _4222.BevelDifferentialPlanetGearCompoundStabilityAnalysis
        )

    @property
    def bevel_differential_sun_gear_compound_stability_analysis(
        self: "CastSelf",
    ) -> "_4223.BevelDifferentialSunGearCompoundStabilityAnalysis":
        from mastapy._private.system_model.analyses_and_results.stability_analyses.compound import (
            _4223,
        )

        return self.__parent__._cast(
            _4223.BevelDifferentialSunGearCompoundStabilityAnalysis
        )

    @property
    def bevel_gear_compound_stability_analysis(
        self: "CastSelf",
    ) -> "_4224.BevelGearCompoundStabilityAnalysis":
        from mastapy._private.system_model.analyses_and_results.stability_analyses.compound import (
            _4224,
        )

        return self.__parent__._cast(_4224.BevelGearCompoundStabilityAnalysis)

    @property
    def clutch_half_compound_stability_analysis(
        self: "CastSelf",
    ) -> "_4231.ClutchHalfCompoundStabilityAnalysis":
        from mastapy._private.system_model.analyses_and_results.stability_analyses.compound import (
            _4231,
        )

        return self.__parent__._cast(_4231.ClutchHalfCompoundStabilityAnalysis)

    @property
    def concept_coupling_half_compound_stability_analysis(
        self: "CastSelf",
    ) -> "_4236.ConceptCouplingHalfCompoundStabilityAnalysis":
        from mastapy._private.system_model.analyses_and_results.stability_analyses.compound import (
            _4236,
        )

        return self.__parent__._cast(_4236.ConceptCouplingHalfCompoundStabilityAnalysis)

    @property
    def concept_gear_compound_stability_analysis(
        self: "CastSelf",
    ) -> "_4237.ConceptGearCompoundStabilityAnalysis":
        from mastapy._private.system_model.analyses_and_results.stability_analyses.compound import (
            _4237,
        )

        return self.__parent__._cast(_4237.ConceptGearCompoundStabilityAnalysis)

    @property
    def conical_gear_compound_stability_analysis(
        self: "CastSelf",
    ) -> "_4240.ConicalGearCompoundStabilityAnalysis":
        from mastapy._private.system_model.analyses_and_results.stability_analyses.compound import (
            _4240,
        )

        return self.__parent__._cast(_4240.ConicalGearCompoundStabilityAnalysis)

    @property
    def connector_compound_stability_analysis(
        self: "CastSelf",
    ) -> "_4244.ConnectorCompoundStabilityAnalysis":
        from mastapy._private.system_model.analyses_and_results.stability_analyses.compound import (
            _4244,
        )

        return self.__parent__._cast(_4244.ConnectorCompoundStabilityAnalysis)

    @property
    def coupling_half_compound_stability_analysis(
        self: "CastSelf",
    ) -> "_4247.CouplingHalfCompoundStabilityAnalysis":
        from mastapy._private.system_model.analyses_and_results.stability_analyses.compound import (
            _4247,
        )

        return self.__parent__._cast(_4247.CouplingHalfCompoundStabilityAnalysis)

    @property
    def cvt_pulley_compound_stability_analysis(
        self: "CastSelf",
    ) -> "_4250.CVTPulleyCompoundStabilityAnalysis":
        from mastapy._private.system_model.analyses_and_results.stability_analyses.compound import (
            _4250,
        )

        return self.__parent__._cast(_4250.CVTPulleyCompoundStabilityAnalysis)

    @property
    def cylindrical_gear_compound_stability_analysis(
        self: "CastSelf",
    ) -> "_4255.CylindricalGearCompoundStabilityAnalysis":
        from mastapy._private.system_model.analyses_and_results.stability_analyses.compound import (
            _4255,
        )

        return self.__parent__._cast(_4255.CylindricalGearCompoundStabilityAnalysis)

    @property
    def cylindrical_planet_gear_compound_stability_analysis(
        self: "CastSelf",
    ) -> "_4258.CylindricalPlanetGearCompoundStabilityAnalysis":
        from mastapy._private.system_model.analyses_and_results.stability_analyses.compound import (
            _4258,
        )

        return self.__parent__._cast(
            _4258.CylindricalPlanetGearCompoundStabilityAnalysis
        )

    @property
    def face_gear_compound_stability_analysis(
        self: "CastSelf",
    ) -> "_4261.FaceGearCompoundStabilityAnalysis":
        from mastapy._private.system_model.analyses_and_results.stability_analyses.compound import (
            _4261,
        )

        return self.__parent__._cast(_4261.FaceGearCompoundStabilityAnalysis)

    @property
    def gear_compound_stability_analysis(
        self: "CastSelf",
    ) -> "_4266.GearCompoundStabilityAnalysis":
        from mastapy._private.system_model.analyses_and_results.stability_analyses.compound import (
            _4266,
        )

        return self.__parent__._cast(_4266.GearCompoundStabilityAnalysis)

    @property
    def hypoid_gear_compound_stability_analysis(
        self: "CastSelf",
    ) -> "_4270.HypoidGearCompoundStabilityAnalysis":
        from mastapy._private.system_model.analyses_and_results.stability_analyses.compound import (
            _4270,
        )

        return self.__parent__._cast(_4270.HypoidGearCompoundStabilityAnalysis)

    @property
    def klingelnberg_cyclo_palloid_conical_gear_compound_stability_analysis(
        self: "CastSelf",
    ) -> "_4274.KlingelnbergCycloPalloidConicalGearCompoundStabilityAnalysis":
        from mastapy._private.system_model.analyses_and_results.stability_analyses.compound import (
            _4274,
        )

        return self.__parent__._cast(
            _4274.KlingelnbergCycloPalloidConicalGearCompoundStabilityAnalysis
        )

    @property
    def klingelnberg_cyclo_palloid_hypoid_gear_compound_stability_analysis(
        self: "CastSelf",
    ) -> "_4277.KlingelnbergCycloPalloidHypoidGearCompoundStabilityAnalysis":
        from mastapy._private.system_model.analyses_and_results.stability_analyses.compound import (
            _4277,
        )

        return self.__parent__._cast(
            _4277.KlingelnbergCycloPalloidHypoidGearCompoundStabilityAnalysis
        )

    @property
    def klingelnberg_cyclo_palloid_spiral_bevel_gear_compound_stability_analysis(
        self: "CastSelf",
    ) -> "_4280.KlingelnbergCycloPalloidSpiralBevelGearCompoundStabilityAnalysis":
        from mastapy._private.system_model.analyses_and_results.stability_analyses.compound import (
            _4280,
        )

        return self.__parent__._cast(
            _4280.KlingelnbergCycloPalloidSpiralBevelGearCompoundStabilityAnalysis
        )

    @property
    def mass_disc_compound_stability_analysis(
        self: "CastSelf",
    ) -> "_4283.MassDiscCompoundStabilityAnalysis":
        from mastapy._private.system_model.analyses_and_results.stability_analyses.compound import (
            _4283,
        )

        return self.__parent__._cast(_4283.MassDiscCompoundStabilityAnalysis)

    @property
    def measurement_component_compound_stability_analysis(
        self: "CastSelf",
    ) -> "_4284.MeasurementComponentCompoundStabilityAnalysis":
        from mastapy._private.system_model.analyses_and_results.stability_analyses.compound import (
            _4284,
        )

        return self.__parent__._cast(
            _4284.MeasurementComponentCompoundStabilityAnalysis
        )

    @property
    def oil_seal_compound_stability_analysis(
        self: "CastSelf",
    ) -> "_4288.OilSealCompoundStabilityAnalysis":
        from mastapy._private.system_model.analyses_and_results.stability_analyses.compound import (
            _4288,
        )

        return self.__parent__._cast(_4288.OilSealCompoundStabilityAnalysis)

    @property
    def part_to_part_shear_coupling_half_compound_stability_analysis(
        self: "CastSelf",
    ) -> "_4292.PartToPartShearCouplingHalfCompoundStabilityAnalysis":
        from mastapy._private.system_model.analyses_and_results.stability_analyses.compound import (
            _4292,
        )

        return self.__parent__._cast(
            _4292.PartToPartShearCouplingHalfCompoundStabilityAnalysis
        )

    @property
    def planet_carrier_compound_stability_analysis(
        self: "CastSelf",
    ) -> "_4295.PlanetCarrierCompoundStabilityAnalysis":
        from mastapy._private.system_model.analyses_and_results.stability_analyses.compound import (
            _4295,
        )

        return self.__parent__._cast(_4295.PlanetCarrierCompoundStabilityAnalysis)

    @property
    def point_load_compound_stability_analysis(
        self: "CastSelf",
    ) -> "_4296.PointLoadCompoundStabilityAnalysis":
        from mastapy._private.system_model.analyses_and_results.stability_analyses.compound import (
            _4296,
        )

        return self.__parent__._cast(_4296.PointLoadCompoundStabilityAnalysis)

    @property
    def power_load_compound_stability_analysis(
        self: "CastSelf",
    ) -> "_4297.PowerLoadCompoundStabilityAnalysis":
        from mastapy._private.system_model.analyses_and_results.stability_analyses.compound import (
            _4297,
        )

        return self.__parent__._cast(_4297.PowerLoadCompoundStabilityAnalysis)

    @property
    def pulley_compound_stability_analysis(
        self: "CastSelf",
    ) -> "_4298.PulleyCompoundStabilityAnalysis":
        from mastapy._private.system_model.analyses_and_results.stability_analyses.compound import (
            _4298,
        )

        return self.__parent__._cast(_4298.PulleyCompoundStabilityAnalysis)

    @property
    def ring_pins_compound_stability_analysis(
        self: "CastSelf",
    ) -> "_4299.RingPinsCompoundStabilityAnalysis":
        from mastapy._private.system_model.analyses_and_results.stability_analyses.compound import (
            _4299,
        )

        return self.__parent__._cast(_4299.RingPinsCompoundStabilityAnalysis)

    @property
    def rolling_ring_compound_stability_analysis(
        self: "CastSelf",
    ) -> "_4302.RollingRingCompoundStabilityAnalysis":
        from mastapy._private.system_model.analyses_and_results.stability_analyses.compound import (
            _4302,
        )

        return self.__parent__._cast(_4302.RollingRingCompoundStabilityAnalysis)

    @property
    def shaft_hub_connection_compound_stability_analysis(
        self: "CastSelf",
    ) -> "_4306.ShaftHubConnectionCompoundStabilityAnalysis":
        from mastapy._private.system_model.analyses_and_results.stability_analyses.compound import (
            _4306,
        )

        return self.__parent__._cast(_4306.ShaftHubConnectionCompoundStabilityAnalysis)

    @property
    def spiral_bevel_gear_compound_stability_analysis(
        self: "CastSelf",
    ) -> "_4309.SpiralBevelGearCompoundStabilityAnalysis":
        from mastapy._private.system_model.analyses_and_results.stability_analyses.compound import (
            _4309,
        )

        return self.__parent__._cast(_4309.SpiralBevelGearCompoundStabilityAnalysis)

    @property
    def spring_damper_half_compound_stability_analysis(
        self: "CastSelf",
    ) -> "_4314.SpringDamperHalfCompoundStabilityAnalysis":
        from mastapy._private.system_model.analyses_and_results.stability_analyses.compound import (
            _4314,
        )

        return self.__parent__._cast(_4314.SpringDamperHalfCompoundStabilityAnalysis)

    @property
    def straight_bevel_diff_gear_compound_stability_analysis(
        self: "CastSelf",
    ) -> "_4315.StraightBevelDiffGearCompoundStabilityAnalysis":
        from mastapy._private.system_model.analyses_and_results.stability_analyses.compound import (
            _4315,
        )

        return self.__parent__._cast(
            _4315.StraightBevelDiffGearCompoundStabilityAnalysis
        )

    @property
    def straight_bevel_gear_compound_stability_analysis(
        self: "CastSelf",
    ) -> "_4318.StraightBevelGearCompoundStabilityAnalysis":
        from mastapy._private.system_model.analyses_and_results.stability_analyses.compound import (
            _4318,
        )

        return self.__parent__._cast(_4318.StraightBevelGearCompoundStabilityAnalysis)

    @property
    def straight_bevel_planet_gear_compound_stability_analysis(
        self: "CastSelf",
    ) -> "_4321.StraightBevelPlanetGearCompoundStabilityAnalysis":
        from mastapy._private.system_model.analyses_and_results.stability_analyses.compound import (
            _4321,
        )

        return self.__parent__._cast(
            _4321.StraightBevelPlanetGearCompoundStabilityAnalysis
        )

    @property
    def straight_bevel_sun_gear_compound_stability_analysis(
        self: "CastSelf",
    ) -> "_4322.StraightBevelSunGearCompoundStabilityAnalysis":
        from mastapy._private.system_model.analyses_and_results.stability_analyses.compound import (
            _4322,
        )

        return self.__parent__._cast(
            _4322.StraightBevelSunGearCompoundStabilityAnalysis
        )

    @property
    def synchroniser_half_compound_stability_analysis(
        self: "CastSelf",
    ) -> "_4324.SynchroniserHalfCompoundStabilityAnalysis":
        from mastapy._private.system_model.analyses_and_results.stability_analyses.compound import (
            _4324,
        )

        return self.__parent__._cast(_4324.SynchroniserHalfCompoundStabilityAnalysis)

    @property
    def synchroniser_part_compound_stability_analysis(
        self: "CastSelf",
    ) -> "_4325.SynchroniserPartCompoundStabilityAnalysis":
        from mastapy._private.system_model.analyses_and_results.stability_analyses.compound import (
            _4325,
        )

        return self.__parent__._cast(_4325.SynchroniserPartCompoundStabilityAnalysis)

    @property
    def synchroniser_sleeve_compound_stability_analysis(
        self: "CastSelf",
    ) -> "_4326.SynchroniserSleeveCompoundStabilityAnalysis":
        from mastapy._private.system_model.analyses_and_results.stability_analyses.compound import (
            _4326,
        )

        return self.__parent__._cast(_4326.SynchroniserSleeveCompoundStabilityAnalysis)

    @property
    def torque_converter_pump_compound_stability_analysis(
        self: "CastSelf",
    ) -> "_4329.TorqueConverterPumpCompoundStabilityAnalysis":
        from mastapy._private.system_model.analyses_and_results.stability_analyses.compound import (
            _4329,
        )

        return self.__parent__._cast(_4329.TorqueConverterPumpCompoundStabilityAnalysis)

    @property
    def torque_converter_turbine_compound_stability_analysis(
        self: "CastSelf",
    ) -> "_4330.TorqueConverterTurbineCompoundStabilityAnalysis":
        from mastapy._private.system_model.analyses_and_results.stability_analyses.compound import (
            _4330,
        )

        return self.__parent__._cast(
            _4330.TorqueConverterTurbineCompoundStabilityAnalysis
        )

    @property
    def unbalanced_mass_compound_stability_analysis(
        self: "CastSelf",
    ) -> "_4331.UnbalancedMassCompoundStabilityAnalysis":
        from mastapy._private.system_model.analyses_and_results.stability_analyses.compound import (
            _4331,
        )

        return self.__parent__._cast(_4331.UnbalancedMassCompoundStabilityAnalysis)

    @property
    def virtual_component_compound_stability_analysis(
        self: "CastSelf",
    ) -> "_4332.VirtualComponentCompoundStabilityAnalysis":
        from mastapy._private.system_model.analyses_and_results.stability_analyses.compound import (
            _4332,
        )

        return self.__parent__._cast(_4332.VirtualComponentCompoundStabilityAnalysis)

    @property
    def worm_gear_compound_stability_analysis(
        self: "CastSelf",
    ) -> "_4333.WormGearCompoundStabilityAnalysis":
        from mastapy._private.system_model.analyses_and_results.stability_analyses.compound import (
            _4333,
        )

        return self.__parent__._cast(_4333.WormGearCompoundStabilityAnalysis)

    @property
    def zerol_bevel_gear_compound_stability_analysis(
        self: "CastSelf",
    ) -> "_4336.ZerolBevelGearCompoundStabilityAnalysis":
        from mastapy._private.system_model.analyses_and_results.stability_analyses.compound import (
            _4336,
        )

        return self.__parent__._cast(_4336.ZerolBevelGearCompoundStabilityAnalysis)

    @property
    def mountable_component_compound_stability_analysis(
        self: "CastSelf",
    ) -> "MountableComponentCompoundStabilityAnalysis":
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
class MountableComponentCompoundStabilityAnalysis(
    _4233.ComponentCompoundStabilityAnalysis
):
    """MountableComponentCompoundStabilityAnalysis

    This is a mastapy class.
    """

    TYPE: ClassVar["Type"] = _MOUNTABLE_COMPONENT_COMPOUND_STABILITY_ANALYSIS

    wrapped: "Any"

    def __post_init__(self: "Self") -> None:
        """Override of the post initialisation magic method."""
        if not hasattr(self.wrapped, "reference_count"):
            self.wrapped.reference_count = 0

        self.wrapped.reference_count += 1

    @property
    @exception_bridge
    def component_analysis_cases(
        self: "Self",
    ) -> "List[_4153.MountableComponentStabilityAnalysis]":
        """List[mastapy.system_model.analyses_and_results.stability_analyses.MountableComponentStabilityAnalysis]

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
    ) -> "List[_4153.MountableComponentStabilityAnalysis]":
        """List[mastapy.system_model.analyses_and_results.stability_analyses.MountableComponentStabilityAnalysis]

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
    def cast_to(self: "Self") -> "_Cast_MountableComponentCompoundStabilityAnalysis":
        """Cast to another type.

        Returns:
            _Cast_MountableComponentCompoundStabilityAnalysis
        """
        return _Cast_MountableComponentCompoundStabilityAnalysis(self)
