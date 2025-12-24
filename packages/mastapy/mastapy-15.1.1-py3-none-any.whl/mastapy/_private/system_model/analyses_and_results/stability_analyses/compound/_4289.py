"""PartCompoundStabilityAnalysis"""

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
from mastapy._private.system_model.analyses_and_results.analysis_cases import _7942

_PART_COMPOUND_STABILITY_ANALYSIS = python_net_import(
    "SMT.MastaAPI.SystemModel.AnalysesAndResults.StabilityAnalyses.Compound",
    "PartCompoundStabilityAnalysis",
)

if TYPE_CHECKING:
    from typing import Any, List, Type, TypeVar

    from mastapy._private.system_model.analyses_and_results import _2943
    from mastapy._private.system_model.analyses_and_results.analysis_cases import _7939
    from mastapy._private.system_model.analyses_and_results.stability_analyses import (
        _4155,
    )
    from mastapy._private.system_model.analyses_and_results.stability_analyses.compound import (
        _4208,
        _4209,
        _4210,
        _4212,
        _4214,
        _4215,
        _4216,
        _4218,
        _4219,
        _4221,
        _4222,
        _4223,
        _4224,
        _4226,
        _4227,
        _4228,
        _4229,
        _4231,
        _4233,
        _4234,
        _4236,
        _4237,
        _4239,
        _4240,
        _4242,
        _4244,
        _4245,
        _4247,
        _4249,
        _4250,
        _4251,
        _4253,
        _4255,
        _4257,
        _4258,
        _4259,
        _4260,
        _4261,
        _4263,
        _4264,
        _4265,
        _4266,
        _4268,
        _4269,
        _4270,
        _4272,
        _4274,
        _4276,
        _4277,
        _4279,
        _4280,
        _4282,
        _4283,
        _4284,
        _4285,
        _4286,
        _4287,
        _4288,
        _4290,
        _4292,
        _4294,
        _4295,
        _4296,
        _4297,
        _4298,
        _4299,
        _4301,
        _4302,
        _4304,
        _4305,
        _4306,
        _4308,
        _4309,
        _4311,
        _4312,
        _4314,
        _4315,
        _4317,
        _4318,
        _4320,
        _4321,
        _4322,
        _4323,
        _4324,
        _4325,
        _4326,
        _4327,
        _4329,
        _4330,
        _4331,
        _4332,
        _4333,
        _4335,
        _4336,
        _4338,
    )

    Self = TypeVar("Self", bound="PartCompoundStabilityAnalysis")
    CastSelf = TypeVar(
        "CastSelf",
        bound="PartCompoundStabilityAnalysis._Cast_PartCompoundStabilityAnalysis",
    )


__docformat__ = "restructuredtext en"
__all__ = ("PartCompoundStabilityAnalysis",)


@extended_dataclass(frozen=True, slots=True, weakref_slot=True)
class _Cast_PartCompoundStabilityAnalysis:
    """Special nested class for casting PartCompoundStabilityAnalysis to subclasses."""

    __parent__: "PartCompoundStabilityAnalysis"

    @property
    def part_compound_analysis(self: "CastSelf") -> "_7942.PartCompoundAnalysis":
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
    def abstract_assembly_compound_stability_analysis(
        self: "CastSelf",
    ) -> "_4208.AbstractAssemblyCompoundStabilityAnalysis":
        from mastapy._private.system_model.analyses_and_results.stability_analyses.compound import (
            _4208,
        )

        return self.__parent__._cast(_4208.AbstractAssemblyCompoundStabilityAnalysis)

    @property
    def abstract_shaft_compound_stability_analysis(
        self: "CastSelf",
    ) -> "_4209.AbstractShaftCompoundStabilityAnalysis":
        from mastapy._private.system_model.analyses_and_results.stability_analyses.compound import (
            _4209,
        )

        return self.__parent__._cast(_4209.AbstractShaftCompoundStabilityAnalysis)

    @property
    def abstract_shaft_or_housing_compound_stability_analysis(
        self: "CastSelf",
    ) -> "_4210.AbstractShaftOrHousingCompoundStabilityAnalysis":
        from mastapy._private.system_model.analyses_and_results.stability_analyses.compound import (
            _4210,
        )

        return self.__parent__._cast(
            _4210.AbstractShaftOrHousingCompoundStabilityAnalysis
        )

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
    def agma_gleason_conical_gear_set_compound_stability_analysis(
        self: "CastSelf",
    ) -> "_4214.AGMAGleasonConicalGearSetCompoundStabilityAnalysis":
        from mastapy._private.system_model.analyses_and_results.stability_analyses.compound import (
            _4214,
        )

        return self.__parent__._cast(
            _4214.AGMAGleasonConicalGearSetCompoundStabilityAnalysis
        )

    @property
    def assembly_compound_stability_analysis(
        self: "CastSelf",
    ) -> "_4215.AssemblyCompoundStabilityAnalysis":
        from mastapy._private.system_model.analyses_and_results.stability_analyses.compound import (
            _4215,
        )

        return self.__parent__._cast(_4215.AssemblyCompoundStabilityAnalysis)

    @property
    def bearing_compound_stability_analysis(
        self: "CastSelf",
    ) -> "_4216.BearingCompoundStabilityAnalysis":
        from mastapy._private.system_model.analyses_and_results.stability_analyses.compound import (
            _4216,
        )

        return self.__parent__._cast(_4216.BearingCompoundStabilityAnalysis)

    @property
    def belt_drive_compound_stability_analysis(
        self: "CastSelf",
    ) -> "_4218.BeltDriveCompoundStabilityAnalysis":
        from mastapy._private.system_model.analyses_and_results.stability_analyses.compound import (
            _4218,
        )

        return self.__parent__._cast(_4218.BeltDriveCompoundStabilityAnalysis)

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
    def bevel_differential_gear_set_compound_stability_analysis(
        self: "CastSelf",
    ) -> "_4221.BevelDifferentialGearSetCompoundStabilityAnalysis":
        from mastapy._private.system_model.analyses_and_results.stability_analyses.compound import (
            _4221,
        )

        return self.__parent__._cast(
            _4221.BevelDifferentialGearSetCompoundStabilityAnalysis
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
    def bevel_gear_set_compound_stability_analysis(
        self: "CastSelf",
    ) -> "_4226.BevelGearSetCompoundStabilityAnalysis":
        from mastapy._private.system_model.analyses_and_results.stability_analyses.compound import (
            _4226,
        )

        return self.__parent__._cast(_4226.BevelGearSetCompoundStabilityAnalysis)

    @property
    def bolt_compound_stability_analysis(
        self: "CastSelf",
    ) -> "_4227.BoltCompoundStabilityAnalysis":
        from mastapy._private.system_model.analyses_and_results.stability_analyses.compound import (
            _4227,
        )

        return self.__parent__._cast(_4227.BoltCompoundStabilityAnalysis)

    @property
    def bolted_joint_compound_stability_analysis(
        self: "CastSelf",
    ) -> "_4228.BoltedJointCompoundStabilityAnalysis":
        from mastapy._private.system_model.analyses_and_results.stability_analyses.compound import (
            _4228,
        )

        return self.__parent__._cast(_4228.BoltedJointCompoundStabilityAnalysis)

    @property
    def clutch_compound_stability_analysis(
        self: "CastSelf",
    ) -> "_4229.ClutchCompoundStabilityAnalysis":
        from mastapy._private.system_model.analyses_and_results.stability_analyses.compound import (
            _4229,
        )

        return self.__parent__._cast(_4229.ClutchCompoundStabilityAnalysis)

    @property
    def clutch_half_compound_stability_analysis(
        self: "CastSelf",
    ) -> "_4231.ClutchHalfCompoundStabilityAnalysis":
        from mastapy._private.system_model.analyses_and_results.stability_analyses.compound import (
            _4231,
        )

        return self.__parent__._cast(_4231.ClutchHalfCompoundStabilityAnalysis)

    @property
    def component_compound_stability_analysis(
        self: "CastSelf",
    ) -> "_4233.ComponentCompoundStabilityAnalysis":
        from mastapy._private.system_model.analyses_and_results.stability_analyses.compound import (
            _4233,
        )

        return self.__parent__._cast(_4233.ComponentCompoundStabilityAnalysis)

    @property
    def concept_coupling_compound_stability_analysis(
        self: "CastSelf",
    ) -> "_4234.ConceptCouplingCompoundStabilityAnalysis":
        from mastapy._private.system_model.analyses_and_results.stability_analyses.compound import (
            _4234,
        )

        return self.__parent__._cast(_4234.ConceptCouplingCompoundStabilityAnalysis)

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
    def concept_gear_set_compound_stability_analysis(
        self: "CastSelf",
    ) -> "_4239.ConceptGearSetCompoundStabilityAnalysis":
        from mastapy._private.system_model.analyses_and_results.stability_analyses.compound import (
            _4239,
        )

        return self.__parent__._cast(_4239.ConceptGearSetCompoundStabilityAnalysis)

    @property
    def conical_gear_compound_stability_analysis(
        self: "CastSelf",
    ) -> "_4240.ConicalGearCompoundStabilityAnalysis":
        from mastapy._private.system_model.analyses_and_results.stability_analyses.compound import (
            _4240,
        )

        return self.__parent__._cast(_4240.ConicalGearCompoundStabilityAnalysis)

    @property
    def conical_gear_set_compound_stability_analysis(
        self: "CastSelf",
    ) -> "_4242.ConicalGearSetCompoundStabilityAnalysis":
        from mastapy._private.system_model.analyses_and_results.stability_analyses.compound import (
            _4242,
        )

        return self.__parent__._cast(_4242.ConicalGearSetCompoundStabilityAnalysis)

    @property
    def connector_compound_stability_analysis(
        self: "CastSelf",
    ) -> "_4244.ConnectorCompoundStabilityAnalysis":
        from mastapy._private.system_model.analyses_and_results.stability_analyses.compound import (
            _4244,
        )

        return self.__parent__._cast(_4244.ConnectorCompoundStabilityAnalysis)

    @property
    def coupling_compound_stability_analysis(
        self: "CastSelf",
    ) -> "_4245.CouplingCompoundStabilityAnalysis":
        from mastapy._private.system_model.analyses_and_results.stability_analyses.compound import (
            _4245,
        )

        return self.__parent__._cast(_4245.CouplingCompoundStabilityAnalysis)

    @property
    def coupling_half_compound_stability_analysis(
        self: "CastSelf",
    ) -> "_4247.CouplingHalfCompoundStabilityAnalysis":
        from mastapy._private.system_model.analyses_and_results.stability_analyses.compound import (
            _4247,
        )

        return self.__parent__._cast(_4247.CouplingHalfCompoundStabilityAnalysis)

    @property
    def cvt_compound_stability_analysis(
        self: "CastSelf",
    ) -> "_4249.CVTCompoundStabilityAnalysis":
        from mastapy._private.system_model.analyses_and_results.stability_analyses.compound import (
            _4249,
        )

        return self.__parent__._cast(_4249.CVTCompoundStabilityAnalysis)

    @property
    def cvt_pulley_compound_stability_analysis(
        self: "CastSelf",
    ) -> "_4250.CVTPulleyCompoundStabilityAnalysis":
        from mastapy._private.system_model.analyses_and_results.stability_analyses.compound import (
            _4250,
        )

        return self.__parent__._cast(_4250.CVTPulleyCompoundStabilityAnalysis)

    @property
    def cycloidal_assembly_compound_stability_analysis(
        self: "CastSelf",
    ) -> "_4251.CycloidalAssemblyCompoundStabilityAnalysis":
        from mastapy._private.system_model.analyses_and_results.stability_analyses.compound import (
            _4251,
        )

        return self.__parent__._cast(_4251.CycloidalAssemblyCompoundStabilityAnalysis)

    @property
    def cycloidal_disc_compound_stability_analysis(
        self: "CastSelf",
    ) -> "_4253.CycloidalDiscCompoundStabilityAnalysis":
        from mastapy._private.system_model.analyses_and_results.stability_analyses.compound import (
            _4253,
        )

        return self.__parent__._cast(_4253.CycloidalDiscCompoundStabilityAnalysis)

    @property
    def cylindrical_gear_compound_stability_analysis(
        self: "CastSelf",
    ) -> "_4255.CylindricalGearCompoundStabilityAnalysis":
        from mastapy._private.system_model.analyses_and_results.stability_analyses.compound import (
            _4255,
        )

        return self.__parent__._cast(_4255.CylindricalGearCompoundStabilityAnalysis)

    @property
    def cylindrical_gear_set_compound_stability_analysis(
        self: "CastSelf",
    ) -> "_4257.CylindricalGearSetCompoundStabilityAnalysis":
        from mastapy._private.system_model.analyses_and_results.stability_analyses.compound import (
            _4257,
        )

        return self.__parent__._cast(_4257.CylindricalGearSetCompoundStabilityAnalysis)

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
    def datum_compound_stability_analysis(
        self: "CastSelf",
    ) -> "_4259.DatumCompoundStabilityAnalysis":
        from mastapy._private.system_model.analyses_and_results.stability_analyses.compound import (
            _4259,
        )

        return self.__parent__._cast(_4259.DatumCompoundStabilityAnalysis)

    @property
    def external_cad_model_compound_stability_analysis(
        self: "CastSelf",
    ) -> "_4260.ExternalCADModelCompoundStabilityAnalysis":
        from mastapy._private.system_model.analyses_and_results.stability_analyses.compound import (
            _4260,
        )

        return self.__parent__._cast(_4260.ExternalCADModelCompoundStabilityAnalysis)

    @property
    def face_gear_compound_stability_analysis(
        self: "CastSelf",
    ) -> "_4261.FaceGearCompoundStabilityAnalysis":
        from mastapy._private.system_model.analyses_and_results.stability_analyses.compound import (
            _4261,
        )

        return self.__parent__._cast(_4261.FaceGearCompoundStabilityAnalysis)

    @property
    def face_gear_set_compound_stability_analysis(
        self: "CastSelf",
    ) -> "_4263.FaceGearSetCompoundStabilityAnalysis":
        from mastapy._private.system_model.analyses_and_results.stability_analyses.compound import (
            _4263,
        )

        return self.__parent__._cast(_4263.FaceGearSetCompoundStabilityAnalysis)

    @property
    def fe_part_compound_stability_analysis(
        self: "CastSelf",
    ) -> "_4264.FEPartCompoundStabilityAnalysis":
        from mastapy._private.system_model.analyses_and_results.stability_analyses.compound import (
            _4264,
        )

        return self.__parent__._cast(_4264.FEPartCompoundStabilityAnalysis)

    @property
    def flexible_pin_assembly_compound_stability_analysis(
        self: "CastSelf",
    ) -> "_4265.FlexiblePinAssemblyCompoundStabilityAnalysis":
        from mastapy._private.system_model.analyses_and_results.stability_analyses.compound import (
            _4265,
        )

        return self.__parent__._cast(_4265.FlexiblePinAssemblyCompoundStabilityAnalysis)

    @property
    def gear_compound_stability_analysis(
        self: "CastSelf",
    ) -> "_4266.GearCompoundStabilityAnalysis":
        from mastapy._private.system_model.analyses_and_results.stability_analyses.compound import (
            _4266,
        )

        return self.__parent__._cast(_4266.GearCompoundStabilityAnalysis)

    @property
    def gear_set_compound_stability_analysis(
        self: "CastSelf",
    ) -> "_4268.GearSetCompoundStabilityAnalysis":
        from mastapy._private.system_model.analyses_and_results.stability_analyses.compound import (
            _4268,
        )

        return self.__parent__._cast(_4268.GearSetCompoundStabilityAnalysis)

    @property
    def guide_dxf_model_compound_stability_analysis(
        self: "CastSelf",
    ) -> "_4269.GuideDxfModelCompoundStabilityAnalysis":
        from mastapy._private.system_model.analyses_and_results.stability_analyses.compound import (
            _4269,
        )

        return self.__parent__._cast(_4269.GuideDxfModelCompoundStabilityAnalysis)

    @property
    def hypoid_gear_compound_stability_analysis(
        self: "CastSelf",
    ) -> "_4270.HypoidGearCompoundStabilityAnalysis":
        from mastapy._private.system_model.analyses_and_results.stability_analyses.compound import (
            _4270,
        )

        return self.__parent__._cast(_4270.HypoidGearCompoundStabilityAnalysis)

    @property
    def hypoid_gear_set_compound_stability_analysis(
        self: "CastSelf",
    ) -> "_4272.HypoidGearSetCompoundStabilityAnalysis":
        from mastapy._private.system_model.analyses_and_results.stability_analyses.compound import (
            _4272,
        )

        return self.__parent__._cast(_4272.HypoidGearSetCompoundStabilityAnalysis)

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
    def klingelnberg_cyclo_palloid_conical_gear_set_compound_stability_analysis(
        self: "CastSelf",
    ) -> "_4276.KlingelnbergCycloPalloidConicalGearSetCompoundStabilityAnalysis":
        from mastapy._private.system_model.analyses_and_results.stability_analyses.compound import (
            _4276,
        )

        return self.__parent__._cast(
            _4276.KlingelnbergCycloPalloidConicalGearSetCompoundStabilityAnalysis
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
    def klingelnberg_cyclo_palloid_hypoid_gear_set_compound_stability_analysis(
        self: "CastSelf",
    ) -> "_4279.KlingelnbergCycloPalloidHypoidGearSetCompoundStabilityAnalysis":
        from mastapy._private.system_model.analyses_and_results.stability_analyses.compound import (
            _4279,
        )

        return self.__parent__._cast(
            _4279.KlingelnbergCycloPalloidHypoidGearSetCompoundStabilityAnalysis
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
    def klingelnberg_cyclo_palloid_spiral_bevel_gear_set_compound_stability_analysis(
        self: "CastSelf",
    ) -> "_4282.KlingelnbergCycloPalloidSpiralBevelGearSetCompoundStabilityAnalysis":
        from mastapy._private.system_model.analyses_and_results.stability_analyses.compound import (
            _4282,
        )

        return self.__parent__._cast(
            _4282.KlingelnbergCycloPalloidSpiralBevelGearSetCompoundStabilityAnalysis
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
    def microphone_array_compound_stability_analysis(
        self: "CastSelf",
    ) -> "_4285.MicrophoneArrayCompoundStabilityAnalysis":
        from mastapy._private.system_model.analyses_and_results.stability_analyses.compound import (
            _4285,
        )

        return self.__parent__._cast(_4285.MicrophoneArrayCompoundStabilityAnalysis)

    @property
    def microphone_compound_stability_analysis(
        self: "CastSelf",
    ) -> "_4286.MicrophoneCompoundStabilityAnalysis":
        from mastapy._private.system_model.analyses_and_results.stability_analyses.compound import (
            _4286,
        )

        return self.__parent__._cast(_4286.MicrophoneCompoundStabilityAnalysis)

    @property
    def mountable_component_compound_stability_analysis(
        self: "CastSelf",
    ) -> "_4287.MountableComponentCompoundStabilityAnalysis":
        from mastapy._private.system_model.analyses_and_results.stability_analyses.compound import (
            _4287,
        )

        return self.__parent__._cast(_4287.MountableComponentCompoundStabilityAnalysis)

    @property
    def oil_seal_compound_stability_analysis(
        self: "CastSelf",
    ) -> "_4288.OilSealCompoundStabilityAnalysis":
        from mastapy._private.system_model.analyses_and_results.stability_analyses.compound import (
            _4288,
        )

        return self.__parent__._cast(_4288.OilSealCompoundStabilityAnalysis)

    @property
    def part_to_part_shear_coupling_compound_stability_analysis(
        self: "CastSelf",
    ) -> "_4290.PartToPartShearCouplingCompoundStabilityAnalysis":
        from mastapy._private.system_model.analyses_and_results.stability_analyses.compound import (
            _4290,
        )

        return self.__parent__._cast(
            _4290.PartToPartShearCouplingCompoundStabilityAnalysis
        )

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
    def planetary_gear_set_compound_stability_analysis(
        self: "CastSelf",
    ) -> "_4294.PlanetaryGearSetCompoundStabilityAnalysis":
        from mastapy._private.system_model.analyses_and_results.stability_analyses.compound import (
            _4294,
        )

        return self.__parent__._cast(_4294.PlanetaryGearSetCompoundStabilityAnalysis)

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
    def rolling_ring_assembly_compound_stability_analysis(
        self: "CastSelf",
    ) -> "_4301.RollingRingAssemblyCompoundStabilityAnalysis":
        from mastapy._private.system_model.analyses_and_results.stability_analyses.compound import (
            _4301,
        )

        return self.__parent__._cast(_4301.RollingRingAssemblyCompoundStabilityAnalysis)

    @property
    def rolling_ring_compound_stability_analysis(
        self: "CastSelf",
    ) -> "_4302.RollingRingCompoundStabilityAnalysis":
        from mastapy._private.system_model.analyses_and_results.stability_analyses.compound import (
            _4302,
        )

        return self.__parent__._cast(_4302.RollingRingCompoundStabilityAnalysis)

    @property
    def root_assembly_compound_stability_analysis(
        self: "CastSelf",
    ) -> "_4304.RootAssemblyCompoundStabilityAnalysis":
        from mastapy._private.system_model.analyses_and_results.stability_analyses.compound import (
            _4304,
        )

        return self.__parent__._cast(_4304.RootAssemblyCompoundStabilityAnalysis)

    @property
    def shaft_compound_stability_analysis(
        self: "CastSelf",
    ) -> "_4305.ShaftCompoundStabilityAnalysis":
        from mastapy._private.system_model.analyses_and_results.stability_analyses.compound import (
            _4305,
        )

        return self.__parent__._cast(_4305.ShaftCompoundStabilityAnalysis)

    @property
    def shaft_hub_connection_compound_stability_analysis(
        self: "CastSelf",
    ) -> "_4306.ShaftHubConnectionCompoundStabilityAnalysis":
        from mastapy._private.system_model.analyses_and_results.stability_analyses.compound import (
            _4306,
        )

        return self.__parent__._cast(_4306.ShaftHubConnectionCompoundStabilityAnalysis)

    @property
    def specialised_assembly_compound_stability_analysis(
        self: "CastSelf",
    ) -> "_4308.SpecialisedAssemblyCompoundStabilityAnalysis":
        from mastapy._private.system_model.analyses_and_results.stability_analyses.compound import (
            _4308,
        )

        return self.__parent__._cast(_4308.SpecialisedAssemblyCompoundStabilityAnalysis)

    @property
    def spiral_bevel_gear_compound_stability_analysis(
        self: "CastSelf",
    ) -> "_4309.SpiralBevelGearCompoundStabilityAnalysis":
        from mastapy._private.system_model.analyses_and_results.stability_analyses.compound import (
            _4309,
        )

        return self.__parent__._cast(_4309.SpiralBevelGearCompoundStabilityAnalysis)

    @property
    def spiral_bevel_gear_set_compound_stability_analysis(
        self: "CastSelf",
    ) -> "_4311.SpiralBevelGearSetCompoundStabilityAnalysis":
        from mastapy._private.system_model.analyses_and_results.stability_analyses.compound import (
            _4311,
        )

        return self.__parent__._cast(_4311.SpiralBevelGearSetCompoundStabilityAnalysis)

    @property
    def spring_damper_compound_stability_analysis(
        self: "CastSelf",
    ) -> "_4312.SpringDamperCompoundStabilityAnalysis":
        from mastapy._private.system_model.analyses_and_results.stability_analyses.compound import (
            _4312,
        )

        return self.__parent__._cast(_4312.SpringDamperCompoundStabilityAnalysis)

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
    def straight_bevel_diff_gear_set_compound_stability_analysis(
        self: "CastSelf",
    ) -> "_4317.StraightBevelDiffGearSetCompoundStabilityAnalysis":
        from mastapy._private.system_model.analyses_and_results.stability_analyses.compound import (
            _4317,
        )

        return self.__parent__._cast(
            _4317.StraightBevelDiffGearSetCompoundStabilityAnalysis
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
    def straight_bevel_gear_set_compound_stability_analysis(
        self: "CastSelf",
    ) -> "_4320.StraightBevelGearSetCompoundStabilityAnalysis":
        from mastapy._private.system_model.analyses_and_results.stability_analyses.compound import (
            _4320,
        )

        return self.__parent__._cast(
            _4320.StraightBevelGearSetCompoundStabilityAnalysis
        )

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
    def synchroniser_compound_stability_analysis(
        self: "CastSelf",
    ) -> "_4323.SynchroniserCompoundStabilityAnalysis":
        from mastapy._private.system_model.analyses_and_results.stability_analyses.compound import (
            _4323,
        )

        return self.__parent__._cast(_4323.SynchroniserCompoundStabilityAnalysis)

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
    def torque_converter_compound_stability_analysis(
        self: "CastSelf",
    ) -> "_4327.TorqueConverterCompoundStabilityAnalysis":
        from mastapy._private.system_model.analyses_and_results.stability_analyses.compound import (
            _4327,
        )

        return self.__parent__._cast(_4327.TorqueConverterCompoundStabilityAnalysis)

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
    def worm_gear_set_compound_stability_analysis(
        self: "CastSelf",
    ) -> "_4335.WormGearSetCompoundStabilityAnalysis":
        from mastapy._private.system_model.analyses_and_results.stability_analyses.compound import (
            _4335,
        )

        return self.__parent__._cast(_4335.WormGearSetCompoundStabilityAnalysis)

    @property
    def zerol_bevel_gear_compound_stability_analysis(
        self: "CastSelf",
    ) -> "_4336.ZerolBevelGearCompoundStabilityAnalysis":
        from mastapy._private.system_model.analyses_and_results.stability_analyses.compound import (
            _4336,
        )

        return self.__parent__._cast(_4336.ZerolBevelGearCompoundStabilityAnalysis)

    @property
    def zerol_bevel_gear_set_compound_stability_analysis(
        self: "CastSelf",
    ) -> "_4338.ZerolBevelGearSetCompoundStabilityAnalysis":
        from mastapy._private.system_model.analyses_and_results.stability_analyses.compound import (
            _4338,
        )

        return self.__parent__._cast(_4338.ZerolBevelGearSetCompoundStabilityAnalysis)

    @property
    def part_compound_stability_analysis(
        self: "CastSelf",
    ) -> "PartCompoundStabilityAnalysis":
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
class PartCompoundStabilityAnalysis(_7942.PartCompoundAnalysis):
    """PartCompoundStabilityAnalysis

    This is a mastapy class.
    """

    TYPE: ClassVar["Type"] = _PART_COMPOUND_STABILITY_ANALYSIS

    wrapped: "Any"

    def __post_init__(self: "Self") -> None:
        """Override of the post initialisation magic method."""
        if not hasattr(self.wrapped, "reference_count"):
            self.wrapped.reference_count = 0

        self.wrapped.reference_count += 1

    @property
    @exception_bridge
    def component_analysis_cases(self: "Self") -> "List[_4155.PartStabilityAnalysis]":
        """List[mastapy.system_model.analyses_and_results.stability_analyses.PartStabilityAnalysis]

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
    ) -> "List[_4155.PartStabilityAnalysis]":
        """List[mastapy.system_model.analyses_and_results.stability_analyses.PartStabilityAnalysis]

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
    def cast_to(self: "Self") -> "_Cast_PartCompoundStabilityAnalysis":
        """Cast to another type.

        Returns:
            _Cast_PartCompoundStabilityAnalysis
        """
        return _Cast_PartCompoundStabilityAnalysis(self)
