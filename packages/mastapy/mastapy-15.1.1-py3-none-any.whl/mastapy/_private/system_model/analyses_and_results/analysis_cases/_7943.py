"""PartFEAnalysis"""

from __future__ import annotations

from typing import TYPE_CHECKING, ClassVar

from mastapy._private._internal.dataclasses import extended_dataclass
from mastapy._private._internal.exceptions import CastException
from mastapy._private._internal.python_net import python_net_import

from mastapy._private._internal import utility
from mastapy._private.system_model.analyses_and_results.analysis_cases import _7944

_PART_FE_ANALYSIS = python_net_import(
    "SMT.MastaAPI.SystemModel.AnalysesAndResults.AnalysisCases", "PartFEAnalysis"
)

if TYPE_CHECKING:
    from typing import Any, Type, TypeVar

    from mastapy._private.system_model.analyses_and_results import _2943, _2945, _2949
    from mastapy._private.system_model.analyses_and_results.analysis_cases import _7941
    from mastapy._private.system_model.analyses_and_results.dynamic_analyses import (
        _6641,
        _6642,
        _6643,
        _6645,
        _6647,
        _6648,
        _6649,
        _6651,
        _6652,
        _6654,
        _6655,
        _6656,
        _6657,
        _6659,
        _6660,
        _6661,
        _6663,
        _6664,
        _6666,
        _6668,
        _6669,
        _6670,
        _6672,
        _6673,
        _6675,
        _6677,
        _6679,
        _6680,
        _6682,
        _6683,
        _6684,
        _6686,
        _6688,
        _6690,
        _6691,
        _6692,
        _6695,
        _6696,
        _6698,
        _6699,
        _6700,
        _6701,
        _6703,
        _6704,
        _6705,
        _6707,
        _6709,
        _6711,
        _6712,
        _6714,
        _6715,
        _6717,
        _6718,
        _6719,
        _6720,
        _6721,
        _6722,
        _6723,
        _6724,
        _6726,
        _6727,
        _6729,
        _6730,
        _6731,
        _6732,
        _6733,
        _6734,
        _6736,
        _6738,
        _6739,
        _6740,
        _6741,
        _6743,
        _6744,
        _6746,
        _6748,
        _6749,
        _6750,
        _6752,
        _6753,
        _6755,
        _6756,
        _6757,
        _6758,
        _6759,
        _6760,
        _6761,
        _6763,
        _6764,
        _6765,
        _6766,
        _6767,
        _6768,
        _6770,
        _6771,
        _6773,
    )
    from mastapy._private.system_model.analyses_and_results.system_deflections import (
        _2977,
        _2978,
        _2979,
        _2982,
        _2983,
        _2984,
        _2990,
        _2992,
        _2994,
        _2995,
        _2996,
        _2997,
        _2999,
        _3000,
        _3001,
        _3002,
        _3004,
        _3005,
        _3007,
        _3010,
        _3011,
        _3013,
        _3014,
        _3017,
        _3018,
        _3020,
        _3022,
        _3023,
        _3025,
        _3026,
        _3027,
        _3030,
        _3034,
        _3035,
        _3036,
        _3037,
        _3038,
        _3039,
        _3042,
        _3043,
        _3044,
        _3047,
        _3048,
        _3049,
        _3050,
        _3052,
        _3053,
        _3054,
        _3056,
        _3057,
        _3061,
        _3062,
        _3064,
        _3065,
        _3067,
        _3068,
        _3071,
        _3072,
        _3074,
        _3075,
        _3076,
        _3078,
        _3079,
        _3081,
        _3082,
        _3084,
        _3085,
        _3086,
        _3087,
        _3088,
        _3091,
        _3093,
        _3094,
        _3095,
        _3098,
        _3100,
        _3102,
        _3103,
        _3105,
        _3106,
        _3108,
        _3109,
        _3111,
        _3112,
        _3113,
        _3114,
        _3115,
        _3116,
        _3117,
        _3118,
        _3123,
        _3124,
        _3125,
        _3129,
        _3130,
        _3132,
        _3133,
        _3135,
        _3136,
    )

    Self = TypeVar("Self", bound="PartFEAnalysis")
    CastSelf = TypeVar("CastSelf", bound="PartFEAnalysis._Cast_PartFEAnalysis")


__docformat__ = "restructuredtext en"
__all__ = ("PartFEAnalysis",)


@extended_dataclass(frozen=True, slots=True, weakref_slot=True)
class _Cast_PartFEAnalysis:
    """Special nested class for casting PartFEAnalysis to subclasses."""

    __parent__: "PartFEAnalysis"

    @property
    def part_static_load_analysis_case(
        self: "CastSelf",
    ) -> "_7944.PartStaticLoadAnalysisCase":
        return self.__parent__._cast(_7944.PartStaticLoadAnalysisCase)

    @property
    def part_analysis_case(self: "CastSelf") -> "_7941.PartAnalysisCase":
        from mastapy._private.system_model.analyses_and_results.analysis_cases import (
            _7941,
        )

        return self.__parent__._cast(_7941.PartAnalysisCase)

    @property
    def part_analysis(self: "CastSelf") -> "_2949.PartAnalysis":
        from mastapy._private.system_model.analyses_and_results import _2949

        return self.__parent__._cast(_2949.PartAnalysis)

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
    def abstract_assembly_system_deflection(
        self: "CastSelf",
    ) -> "_2977.AbstractAssemblySystemDeflection":
        from mastapy._private.system_model.analyses_and_results.system_deflections import (
            _2977,
        )

        return self.__parent__._cast(_2977.AbstractAssemblySystemDeflection)

    @property
    def abstract_shaft_or_housing_system_deflection(
        self: "CastSelf",
    ) -> "_2978.AbstractShaftOrHousingSystemDeflection":
        from mastapy._private.system_model.analyses_and_results.system_deflections import (
            _2978,
        )

        return self.__parent__._cast(_2978.AbstractShaftOrHousingSystemDeflection)

    @property
    def abstract_shaft_system_deflection(
        self: "CastSelf",
    ) -> "_2979.AbstractShaftSystemDeflection":
        from mastapy._private.system_model.analyses_and_results.system_deflections import (
            _2979,
        )

        return self.__parent__._cast(_2979.AbstractShaftSystemDeflection)

    @property
    def agma_gleason_conical_gear_set_system_deflection(
        self: "CastSelf",
    ) -> "_2982.AGMAGleasonConicalGearSetSystemDeflection":
        from mastapy._private.system_model.analyses_and_results.system_deflections import (
            _2982,
        )

        return self.__parent__._cast(_2982.AGMAGleasonConicalGearSetSystemDeflection)

    @property
    def agma_gleason_conical_gear_system_deflection(
        self: "CastSelf",
    ) -> "_2983.AGMAGleasonConicalGearSystemDeflection":
        from mastapy._private.system_model.analyses_and_results.system_deflections import (
            _2983,
        )

        return self.__parent__._cast(_2983.AGMAGleasonConicalGearSystemDeflection)

    @property
    def assembly_system_deflection(
        self: "CastSelf",
    ) -> "_2984.AssemblySystemDeflection":
        from mastapy._private.system_model.analyses_and_results.system_deflections import (
            _2984,
        )

        return self.__parent__._cast(_2984.AssemblySystemDeflection)

    @property
    def bearing_system_deflection(self: "CastSelf") -> "_2990.BearingSystemDeflection":
        from mastapy._private.system_model.analyses_and_results.system_deflections import (
            _2990,
        )

        return self.__parent__._cast(_2990.BearingSystemDeflection)

    @property
    def belt_drive_system_deflection(
        self: "CastSelf",
    ) -> "_2992.BeltDriveSystemDeflection":
        from mastapy._private.system_model.analyses_and_results.system_deflections import (
            _2992,
        )

        return self.__parent__._cast(_2992.BeltDriveSystemDeflection)

    @property
    def bevel_differential_gear_set_system_deflection(
        self: "CastSelf",
    ) -> "_2994.BevelDifferentialGearSetSystemDeflection":
        from mastapy._private.system_model.analyses_and_results.system_deflections import (
            _2994,
        )

        return self.__parent__._cast(_2994.BevelDifferentialGearSetSystemDeflection)

    @property
    def bevel_differential_gear_system_deflection(
        self: "CastSelf",
    ) -> "_2995.BevelDifferentialGearSystemDeflection":
        from mastapy._private.system_model.analyses_and_results.system_deflections import (
            _2995,
        )

        return self.__parent__._cast(_2995.BevelDifferentialGearSystemDeflection)

    @property
    def bevel_differential_planet_gear_system_deflection(
        self: "CastSelf",
    ) -> "_2996.BevelDifferentialPlanetGearSystemDeflection":
        from mastapy._private.system_model.analyses_and_results.system_deflections import (
            _2996,
        )

        return self.__parent__._cast(_2996.BevelDifferentialPlanetGearSystemDeflection)

    @property
    def bevel_differential_sun_gear_system_deflection(
        self: "CastSelf",
    ) -> "_2997.BevelDifferentialSunGearSystemDeflection":
        from mastapy._private.system_model.analyses_and_results.system_deflections import (
            _2997,
        )

        return self.__parent__._cast(_2997.BevelDifferentialSunGearSystemDeflection)

    @property
    def bevel_gear_set_system_deflection(
        self: "CastSelf",
    ) -> "_2999.BevelGearSetSystemDeflection":
        from mastapy._private.system_model.analyses_and_results.system_deflections import (
            _2999,
        )

        return self.__parent__._cast(_2999.BevelGearSetSystemDeflection)

    @property
    def bevel_gear_system_deflection(
        self: "CastSelf",
    ) -> "_3000.BevelGearSystemDeflection":
        from mastapy._private.system_model.analyses_and_results.system_deflections import (
            _3000,
        )

        return self.__parent__._cast(_3000.BevelGearSystemDeflection)

    @property
    def bolted_joint_system_deflection(
        self: "CastSelf",
    ) -> "_3001.BoltedJointSystemDeflection":
        from mastapy._private.system_model.analyses_and_results.system_deflections import (
            _3001,
        )

        return self.__parent__._cast(_3001.BoltedJointSystemDeflection)

    @property
    def bolt_system_deflection(self: "CastSelf") -> "_3002.BoltSystemDeflection":
        from mastapy._private.system_model.analyses_and_results.system_deflections import (
            _3002,
        )

        return self.__parent__._cast(_3002.BoltSystemDeflection)

    @property
    def clutch_half_system_deflection(
        self: "CastSelf",
    ) -> "_3004.ClutchHalfSystemDeflection":
        from mastapy._private.system_model.analyses_and_results.system_deflections import (
            _3004,
        )

        return self.__parent__._cast(_3004.ClutchHalfSystemDeflection)

    @property
    def clutch_system_deflection(self: "CastSelf") -> "_3005.ClutchSystemDeflection":
        from mastapy._private.system_model.analyses_and_results.system_deflections import (
            _3005,
        )

        return self.__parent__._cast(_3005.ClutchSystemDeflection)

    @property
    def component_system_deflection(
        self: "CastSelf",
    ) -> "_3007.ComponentSystemDeflection":
        from mastapy._private.system_model.analyses_and_results.system_deflections import (
            _3007,
        )

        return self.__parent__._cast(_3007.ComponentSystemDeflection)

    @property
    def concept_coupling_half_system_deflection(
        self: "CastSelf",
    ) -> "_3010.ConceptCouplingHalfSystemDeflection":
        from mastapy._private.system_model.analyses_and_results.system_deflections import (
            _3010,
        )

        return self.__parent__._cast(_3010.ConceptCouplingHalfSystemDeflection)

    @property
    def concept_coupling_system_deflection(
        self: "CastSelf",
    ) -> "_3011.ConceptCouplingSystemDeflection":
        from mastapy._private.system_model.analyses_and_results.system_deflections import (
            _3011,
        )

        return self.__parent__._cast(_3011.ConceptCouplingSystemDeflection)

    @property
    def concept_gear_set_system_deflection(
        self: "CastSelf",
    ) -> "_3013.ConceptGearSetSystemDeflection":
        from mastapy._private.system_model.analyses_and_results.system_deflections import (
            _3013,
        )

        return self.__parent__._cast(_3013.ConceptGearSetSystemDeflection)

    @property
    def concept_gear_system_deflection(
        self: "CastSelf",
    ) -> "_3014.ConceptGearSystemDeflection":
        from mastapy._private.system_model.analyses_and_results.system_deflections import (
            _3014,
        )

        return self.__parent__._cast(_3014.ConceptGearSystemDeflection)

    @property
    def conical_gear_set_system_deflection(
        self: "CastSelf",
    ) -> "_3017.ConicalGearSetSystemDeflection":
        from mastapy._private.system_model.analyses_and_results.system_deflections import (
            _3017,
        )

        return self.__parent__._cast(_3017.ConicalGearSetSystemDeflection)

    @property
    def conical_gear_system_deflection(
        self: "CastSelf",
    ) -> "_3018.ConicalGearSystemDeflection":
        from mastapy._private.system_model.analyses_and_results.system_deflections import (
            _3018,
        )

        return self.__parent__._cast(_3018.ConicalGearSystemDeflection)

    @property
    def connector_system_deflection(
        self: "CastSelf",
    ) -> "_3020.ConnectorSystemDeflection":
        from mastapy._private.system_model.analyses_and_results.system_deflections import (
            _3020,
        )

        return self.__parent__._cast(_3020.ConnectorSystemDeflection)

    @property
    def coupling_half_system_deflection(
        self: "CastSelf",
    ) -> "_3022.CouplingHalfSystemDeflection":
        from mastapy._private.system_model.analyses_and_results.system_deflections import (
            _3022,
        )

        return self.__parent__._cast(_3022.CouplingHalfSystemDeflection)

    @property
    def coupling_system_deflection(
        self: "CastSelf",
    ) -> "_3023.CouplingSystemDeflection":
        from mastapy._private.system_model.analyses_and_results.system_deflections import (
            _3023,
        )

        return self.__parent__._cast(_3023.CouplingSystemDeflection)

    @property
    def cvt_pulley_system_deflection(
        self: "CastSelf",
    ) -> "_3025.CVTPulleySystemDeflection":
        from mastapy._private.system_model.analyses_and_results.system_deflections import (
            _3025,
        )

        return self.__parent__._cast(_3025.CVTPulleySystemDeflection)

    @property
    def cvt_system_deflection(self: "CastSelf") -> "_3026.CVTSystemDeflection":
        from mastapy._private.system_model.analyses_and_results.system_deflections import (
            _3026,
        )

        return self.__parent__._cast(_3026.CVTSystemDeflection)

    @property
    def cycloidal_assembly_system_deflection(
        self: "CastSelf",
    ) -> "_3027.CycloidalAssemblySystemDeflection":
        from mastapy._private.system_model.analyses_and_results.system_deflections import (
            _3027,
        )

        return self.__parent__._cast(_3027.CycloidalAssemblySystemDeflection)

    @property
    def cycloidal_disc_system_deflection(
        self: "CastSelf",
    ) -> "_3030.CycloidalDiscSystemDeflection":
        from mastapy._private.system_model.analyses_and_results.system_deflections import (
            _3030,
        )

        return self.__parent__._cast(_3030.CycloidalDiscSystemDeflection)

    @property
    def cylindrical_gear_set_system_deflection(
        self: "CastSelf",
    ) -> "_3034.CylindricalGearSetSystemDeflection":
        from mastapy._private.system_model.analyses_and_results.system_deflections import (
            _3034,
        )

        return self.__parent__._cast(_3034.CylindricalGearSetSystemDeflection)

    @property
    def cylindrical_gear_set_system_deflection_timestep(
        self: "CastSelf",
    ) -> "_3035.CylindricalGearSetSystemDeflectionTimestep":
        from mastapy._private.system_model.analyses_and_results.system_deflections import (
            _3035,
        )

        return self.__parent__._cast(_3035.CylindricalGearSetSystemDeflectionTimestep)

    @property
    def cylindrical_gear_set_system_deflection_with_ltca_results(
        self: "CastSelf",
    ) -> "_3036.CylindricalGearSetSystemDeflectionWithLTCAResults":
        from mastapy._private.system_model.analyses_and_results.system_deflections import (
            _3036,
        )

        return self.__parent__._cast(
            _3036.CylindricalGearSetSystemDeflectionWithLTCAResults
        )

    @property
    def cylindrical_gear_system_deflection(
        self: "CastSelf",
    ) -> "_3037.CylindricalGearSystemDeflection":
        from mastapy._private.system_model.analyses_and_results.system_deflections import (
            _3037,
        )

        return self.__parent__._cast(_3037.CylindricalGearSystemDeflection)

    @property
    def cylindrical_gear_system_deflection_timestep(
        self: "CastSelf",
    ) -> "_3038.CylindricalGearSystemDeflectionTimestep":
        from mastapy._private.system_model.analyses_and_results.system_deflections import (
            _3038,
        )

        return self.__parent__._cast(_3038.CylindricalGearSystemDeflectionTimestep)

    @property
    def cylindrical_gear_system_deflection_with_ltca_results(
        self: "CastSelf",
    ) -> "_3039.CylindricalGearSystemDeflectionWithLTCAResults":
        from mastapy._private.system_model.analyses_and_results.system_deflections import (
            _3039,
        )

        return self.__parent__._cast(
            _3039.CylindricalGearSystemDeflectionWithLTCAResults
        )

    @property
    def cylindrical_planet_gear_system_deflection(
        self: "CastSelf",
    ) -> "_3042.CylindricalPlanetGearSystemDeflection":
        from mastapy._private.system_model.analyses_and_results.system_deflections import (
            _3042,
        )

        return self.__parent__._cast(_3042.CylindricalPlanetGearSystemDeflection)

    @property
    def datum_system_deflection(self: "CastSelf") -> "_3043.DatumSystemDeflection":
        from mastapy._private.system_model.analyses_and_results.system_deflections import (
            _3043,
        )

        return self.__parent__._cast(_3043.DatumSystemDeflection)

    @property
    def external_cad_model_system_deflection(
        self: "CastSelf",
    ) -> "_3044.ExternalCADModelSystemDeflection":
        from mastapy._private.system_model.analyses_and_results.system_deflections import (
            _3044,
        )

        return self.__parent__._cast(_3044.ExternalCADModelSystemDeflection)

    @property
    def face_gear_set_system_deflection(
        self: "CastSelf",
    ) -> "_3047.FaceGearSetSystemDeflection":
        from mastapy._private.system_model.analyses_and_results.system_deflections import (
            _3047,
        )

        return self.__parent__._cast(_3047.FaceGearSetSystemDeflection)

    @property
    def face_gear_system_deflection(
        self: "CastSelf",
    ) -> "_3048.FaceGearSystemDeflection":
        from mastapy._private.system_model.analyses_and_results.system_deflections import (
            _3048,
        )

        return self.__parent__._cast(_3048.FaceGearSystemDeflection)

    @property
    def fe_part_system_deflection(self: "CastSelf") -> "_3049.FEPartSystemDeflection":
        from mastapy._private.system_model.analyses_and_results.system_deflections import (
            _3049,
        )

        return self.__parent__._cast(_3049.FEPartSystemDeflection)

    @property
    def flexible_pin_assembly_system_deflection(
        self: "CastSelf",
    ) -> "_3050.FlexiblePinAssemblySystemDeflection":
        from mastapy._private.system_model.analyses_and_results.system_deflections import (
            _3050,
        )

        return self.__parent__._cast(_3050.FlexiblePinAssemblySystemDeflection)

    @property
    def gear_set_system_deflection(self: "CastSelf") -> "_3052.GearSetSystemDeflection":
        from mastapy._private.system_model.analyses_and_results.system_deflections import (
            _3052,
        )

        return self.__parent__._cast(_3052.GearSetSystemDeflection)

    @property
    def gear_system_deflection(self: "CastSelf") -> "_3053.GearSystemDeflection":
        from mastapy._private.system_model.analyses_and_results.system_deflections import (
            _3053,
        )

        return self.__parent__._cast(_3053.GearSystemDeflection)

    @property
    def guide_dxf_model_system_deflection(
        self: "CastSelf",
    ) -> "_3054.GuideDxfModelSystemDeflection":
        from mastapy._private.system_model.analyses_and_results.system_deflections import (
            _3054,
        )

        return self.__parent__._cast(_3054.GuideDxfModelSystemDeflection)

    @property
    def hypoid_gear_set_system_deflection(
        self: "CastSelf",
    ) -> "_3056.HypoidGearSetSystemDeflection":
        from mastapy._private.system_model.analyses_and_results.system_deflections import (
            _3056,
        )

        return self.__parent__._cast(_3056.HypoidGearSetSystemDeflection)

    @property
    def hypoid_gear_system_deflection(
        self: "CastSelf",
    ) -> "_3057.HypoidGearSystemDeflection":
        from mastapy._private.system_model.analyses_and_results.system_deflections import (
            _3057,
        )

        return self.__parent__._cast(_3057.HypoidGearSystemDeflection)

    @property
    def klingelnberg_cyclo_palloid_conical_gear_set_system_deflection(
        self: "CastSelf",
    ) -> "_3061.KlingelnbergCycloPalloidConicalGearSetSystemDeflection":
        from mastapy._private.system_model.analyses_and_results.system_deflections import (
            _3061,
        )

        return self.__parent__._cast(
            _3061.KlingelnbergCycloPalloidConicalGearSetSystemDeflection
        )

    @property
    def klingelnberg_cyclo_palloid_conical_gear_system_deflection(
        self: "CastSelf",
    ) -> "_3062.KlingelnbergCycloPalloidConicalGearSystemDeflection":
        from mastapy._private.system_model.analyses_and_results.system_deflections import (
            _3062,
        )

        return self.__parent__._cast(
            _3062.KlingelnbergCycloPalloidConicalGearSystemDeflection
        )

    @property
    def klingelnberg_cyclo_palloid_hypoid_gear_set_system_deflection(
        self: "CastSelf",
    ) -> "_3064.KlingelnbergCycloPalloidHypoidGearSetSystemDeflection":
        from mastapy._private.system_model.analyses_and_results.system_deflections import (
            _3064,
        )

        return self.__parent__._cast(
            _3064.KlingelnbergCycloPalloidHypoidGearSetSystemDeflection
        )

    @property
    def klingelnberg_cyclo_palloid_hypoid_gear_system_deflection(
        self: "CastSelf",
    ) -> "_3065.KlingelnbergCycloPalloidHypoidGearSystemDeflection":
        from mastapy._private.system_model.analyses_and_results.system_deflections import (
            _3065,
        )

        return self.__parent__._cast(
            _3065.KlingelnbergCycloPalloidHypoidGearSystemDeflection
        )

    @property
    def klingelnberg_cyclo_palloid_spiral_bevel_gear_set_system_deflection(
        self: "CastSelf",
    ) -> "_3067.KlingelnbergCycloPalloidSpiralBevelGearSetSystemDeflection":
        from mastapy._private.system_model.analyses_and_results.system_deflections import (
            _3067,
        )

        return self.__parent__._cast(
            _3067.KlingelnbergCycloPalloidSpiralBevelGearSetSystemDeflection
        )

    @property
    def klingelnberg_cyclo_palloid_spiral_bevel_gear_system_deflection(
        self: "CastSelf",
    ) -> "_3068.KlingelnbergCycloPalloidSpiralBevelGearSystemDeflection":
        from mastapy._private.system_model.analyses_and_results.system_deflections import (
            _3068,
        )

        return self.__parent__._cast(
            _3068.KlingelnbergCycloPalloidSpiralBevelGearSystemDeflection
        )

    @property
    def mass_disc_system_deflection(
        self: "CastSelf",
    ) -> "_3071.MassDiscSystemDeflection":
        from mastapy._private.system_model.analyses_and_results.system_deflections import (
            _3071,
        )

        return self.__parent__._cast(_3071.MassDiscSystemDeflection)

    @property
    def measurement_component_system_deflection(
        self: "CastSelf",
    ) -> "_3072.MeasurementComponentSystemDeflection":
        from mastapy._private.system_model.analyses_and_results.system_deflections import (
            _3072,
        )

        return self.__parent__._cast(_3072.MeasurementComponentSystemDeflection)

    @property
    def microphone_array_system_deflection(
        self: "CastSelf",
    ) -> "_3074.MicrophoneArraySystemDeflection":
        from mastapy._private.system_model.analyses_and_results.system_deflections import (
            _3074,
        )

        return self.__parent__._cast(_3074.MicrophoneArraySystemDeflection)

    @property
    def microphone_system_deflection(
        self: "CastSelf",
    ) -> "_3075.MicrophoneSystemDeflection":
        from mastapy._private.system_model.analyses_and_results.system_deflections import (
            _3075,
        )

        return self.__parent__._cast(_3075.MicrophoneSystemDeflection)

    @property
    def mountable_component_system_deflection(
        self: "CastSelf",
    ) -> "_3076.MountableComponentSystemDeflection":
        from mastapy._private.system_model.analyses_and_results.system_deflections import (
            _3076,
        )

        return self.__parent__._cast(_3076.MountableComponentSystemDeflection)

    @property
    def oil_seal_system_deflection(self: "CastSelf") -> "_3078.OilSealSystemDeflection":
        from mastapy._private.system_model.analyses_and_results.system_deflections import (
            _3078,
        )

        return self.__parent__._cast(_3078.OilSealSystemDeflection)

    @property
    def part_system_deflection(self: "CastSelf") -> "_3079.PartSystemDeflection":
        from mastapy._private.system_model.analyses_and_results.system_deflections import (
            _3079,
        )

        return self.__parent__._cast(_3079.PartSystemDeflection)

    @property
    def part_to_part_shear_coupling_half_system_deflection(
        self: "CastSelf",
    ) -> "_3081.PartToPartShearCouplingHalfSystemDeflection":
        from mastapy._private.system_model.analyses_and_results.system_deflections import (
            _3081,
        )

        return self.__parent__._cast(_3081.PartToPartShearCouplingHalfSystemDeflection)

    @property
    def part_to_part_shear_coupling_system_deflection(
        self: "CastSelf",
    ) -> "_3082.PartToPartShearCouplingSystemDeflection":
        from mastapy._private.system_model.analyses_and_results.system_deflections import (
            _3082,
        )

        return self.__parent__._cast(_3082.PartToPartShearCouplingSystemDeflection)

    @property
    def planet_carrier_system_deflection(
        self: "CastSelf",
    ) -> "_3084.PlanetCarrierSystemDeflection":
        from mastapy._private.system_model.analyses_and_results.system_deflections import (
            _3084,
        )

        return self.__parent__._cast(_3084.PlanetCarrierSystemDeflection)

    @property
    def point_load_system_deflection(
        self: "CastSelf",
    ) -> "_3085.PointLoadSystemDeflection":
        from mastapy._private.system_model.analyses_and_results.system_deflections import (
            _3085,
        )

        return self.__parent__._cast(_3085.PointLoadSystemDeflection)

    @property
    def power_load_system_deflection(
        self: "CastSelf",
    ) -> "_3086.PowerLoadSystemDeflection":
        from mastapy._private.system_model.analyses_and_results.system_deflections import (
            _3086,
        )

        return self.__parent__._cast(_3086.PowerLoadSystemDeflection)

    @property
    def pulley_system_deflection(self: "CastSelf") -> "_3087.PulleySystemDeflection":
        from mastapy._private.system_model.analyses_and_results.system_deflections import (
            _3087,
        )

        return self.__parent__._cast(_3087.PulleySystemDeflection)

    @property
    def ring_pins_system_deflection(
        self: "CastSelf",
    ) -> "_3088.RingPinsSystemDeflection":
        from mastapy._private.system_model.analyses_and_results.system_deflections import (
            _3088,
        )

        return self.__parent__._cast(_3088.RingPinsSystemDeflection)

    @property
    def rolling_ring_assembly_system_deflection(
        self: "CastSelf",
    ) -> "_3091.RollingRingAssemblySystemDeflection":
        from mastapy._private.system_model.analyses_and_results.system_deflections import (
            _3091,
        )

        return self.__parent__._cast(_3091.RollingRingAssemblySystemDeflection)

    @property
    def rolling_ring_system_deflection(
        self: "CastSelf",
    ) -> "_3093.RollingRingSystemDeflection":
        from mastapy._private.system_model.analyses_and_results.system_deflections import (
            _3093,
        )

        return self.__parent__._cast(_3093.RollingRingSystemDeflection)

    @property
    def root_assembly_system_deflection(
        self: "CastSelf",
    ) -> "_3094.RootAssemblySystemDeflection":
        from mastapy._private.system_model.analyses_and_results.system_deflections import (
            _3094,
        )

        return self.__parent__._cast(_3094.RootAssemblySystemDeflection)

    @property
    def shaft_hub_connection_system_deflection(
        self: "CastSelf",
    ) -> "_3095.ShaftHubConnectionSystemDeflection":
        from mastapy._private.system_model.analyses_and_results.system_deflections import (
            _3095,
        )

        return self.__parent__._cast(_3095.ShaftHubConnectionSystemDeflection)

    @property
    def shaft_system_deflection(self: "CastSelf") -> "_3098.ShaftSystemDeflection":
        from mastapy._private.system_model.analyses_and_results.system_deflections import (
            _3098,
        )

        return self.__parent__._cast(_3098.ShaftSystemDeflection)

    @property
    def specialised_assembly_system_deflection(
        self: "CastSelf",
    ) -> "_3100.SpecialisedAssemblySystemDeflection":
        from mastapy._private.system_model.analyses_and_results.system_deflections import (
            _3100,
        )

        return self.__parent__._cast(_3100.SpecialisedAssemblySystemDeflection)

    @property
    def spiral_bevel_gear_set_system_deflection(
        self: "CastSelf",
    ) -> "_3102.SpiralBevelGearSetSystemDeflection":
        from mastapy._private.system_model.analyses_and_results.system_deflections import (
            _3102,
        )

        return self.__parent__._cast(_3102.SpiralBevelGearSetSystemDeflection)

    @property
    def spiral_bevel_gear_system_deflection(
        self: "CastSelf",
    ) -> "_3103.SpiralBevelGearSystemDeflection":
        from mastapy._private.system_model.analyses_and_results.system_deflections import (
            _3103,
        )

        return self.__parent__._cast(_3103.SpiralBevelGearSystemDeflection)

    @property
    def spring_damper_half_system_deflection(
        self: "CastSelf",
    ) -> "_3105.SpringDamperHalfSystemDeflection":
        from mastapy._private.system_model.analyses_and_results.system_deflections import (
            _3105,
        )

        return self.__parent__._cast(_3105.SpringDamperHalfSystemDeflection)

    @property
    def spring_damper_system_deflection(
        self: "CastSelf",
    ) -> "_3106.SpringDamperSystemDeflection":
        from mastapy._private.system_model.analyses_and_results.system_deflections import (
            _3106,
        )

        return self.__parent__._cast(_3106.SpringDamperSystemDeflection)

    @property
    def straight_bevel_diff_gear_set_system_deflection(
        self: "CastSelf",
    ) -> "_3108.StraightBevelDiffGearSetSystemDeflection":
        from mastapy._private.system_model.analyses_and_results.system_deflections import (
            _3108,
        )

        return self.__parent__._cast(_3108.StraightBevelDiffGearSetSystemDeflection)

    @property
    def straight_bevel_diff_gear_system_deflection(
        self: "CastSelf",
    ) -> "_3109.StraightBevelDiffGearSystemDeflection":
        from mastapy._private.system_model.analyses_and_results.system_deflections import (
            _3109,
        )

        return self.__parent__._cast(_3109.StraightBevelDiffGearSystemDeflection)

    @property
    def straight_bevel_gear_set_system_deflection(
        self: "CastSelf",
    ) -> "_3111.StraightBevelGearSetSystemDeflection":
        from mastapy._private.system_model.analyses_and_results.system_deflections import (
            _3111,
        )

        return self.__parent__._cast(_3111.StraightBevelGearSetSystemDeflection)

    @property
    def straight_bevel_gear_system_deflection(
        self: "CastSelf",
    ) -> "_3112.StraightBevelGearSystemDeflection":
        from mastapy._private.system_model.analyses_and_results.system_deflections import (
            _3112,
        )

        return self.__parent__._cast(_3112.StraightBevelGearSystemDeflection)

    @property
    def straight_bevel_planet_gear_system_deflection(
        self: "CastSelf",
    ) -> "_3113.StraightBevelPlanetGearSystemDeflection":
        from mastapy._private.system_model.analyses_and_results.system_deflections import (
            _3113,
        )

        return self.__parent__._cast(_3113.StraightBevelPlanetGearSystemDeflection)

    @property
    def straight_bevel_sun_gear_system_deflection(
        self: "CastSelf",
    ) -> "_3114.StraightBevelSunGearSystemDeflection":
        from mastapy._private.system_model.analyses_and_results.system_deflections import (
            _3114,
        )

        return self.__parent__._cast(_3114.StraightBevelSunGearSystemDeflection)

    @property
    def synchroniser_half_system_deflection(
        self: "CastSelf",
    ) -> "_3115.SynchroniserHalfSystemDeflection":
        from mastapy._private.system_model.analyses_and_results.system_deflections import (
            _3115,
        )

        return self.__parent__._cast(_3115.SynchroniserHalfSystemDeflection)

    @property
    def synchroniser_part_system_deflection(
        self: "CastSelf",
    ) -> "_3116.SynchroniserPartSystemDeflection":
        from mastapy._private.system_model.analyses_and_results.system_deflections import (
            _3116,
        )

        return self.__parent__._cast(_3116.SynchroniserPartSystemDeflection)

    @property
    def synchroniser_sleeve_system_deflection(
        self: "CastSelf",
    ) -> "_3117.SynchroniserSleeveSystemDeflection":
        from mastapy._private.system_model.analyses_and_results.system_deflections import (
            _3117,
        )

        return self.__parent__._cast(_3117.SynchroniserSleeveSystemDeflection)

    @property
    def synchroniser_system_deflection(
        self: "CastSelf",
    ) -> "_3118.SynchroniserSystemDeflection":
        from mastapy._private.system_model.analyses_and_results.system_deflections import (
            _3118,
        )

        return self.__parent__._cast(_3118.SynchroniserSystemDeflection)

    @property
    def torque_converter_pump_system_deflection(
        self: "CastSelf",
    ) -> "_3123.TorqueConverterPumpSystemDeflection":
        from mastapy._private.system_model.analyses_and_results.system_deflections import (
            _3123,
        )

        return self.__parent__._cast(_3123.TorqueConverterPumpSystemDeflection)

    @property
    def torque_converter_system_deflection(
        self: "CastSelf",
    ) -> "_3124.TorqueConverterSystemDeflection":
        from mastapy._private.system_model.analyses_and_results.system_deflections import (
            _3124,
        )

        return self.__parent__._cast(_3124.TorqueConverterSystemDeflection)

    @property
    def torque_converter_turbine_system_deflection(
        self: "CastSelf",
    ) -> "_3125.TorqueConverterTurbineSystemDeflection":
        from mastapy._private.system_model.analyses_and_results.system_deflections import (
            _3125,
        )

        return self.__parent__._cast(_3125.TorqueConverterTurbineSystemDeflection)

    @property
    def unbalanced_mass_system_deflection(
        self: "CastSelf",
    ) -> "_3129.UnbalancedMassSystemDeflection":
        from mastapy._private.system_model.analyses_and_results.system_deflections import (
            _3129,
        )

        return self.__parent__._cast(_3129.UnbalancedMassSystemDeflection)

    @property
    def virtual_component_system_deflection(
        self: "CastSelf",
    ) -> "_3130.VirtualComponentSystemDeflection":
        from mastapy._private.system_model.analyses_and_results.system_deflections import (
            _3130,
        )

        return self.__parent__._cast(_3130.VirtualComponentSystemDeflection)

    @property
    def worm_gear_set_system_deflection(
        self: "CastSelf",
    ) -> "_3132.WormGearSetSystemDeflection":
        from mastapy._private.system_model.analyses_and_results.system_deflections import (
            _3132,
        )

        return self.__parent__._cast(_3132.WormGearSetSystemDeflection)

    @property
    def worm_gear_system_deflection(
        self: "CastSelf",
    ) -> "_3133.WormGearSystemDeflection":
        from mastapy._private.system_model.analyses_and_results.system_deflections import (
            _3133,
        )

        return self.__parent__._cast(_3133.WormGearSystemDeflection)

    @property
    def zerol_bevel_gear_set_system_deflection(
        self: "CastSelf",
    ) -> "_3135.ZerolBevelGearSetSystemDeflection":
        from mastapy._private.system_model.analyses_and_results.system_deflections import (
            _3135,
        )

        return self.__parent__._cast(_3135.ZerolBevelGearSetSystemDeflection)

    @property
    def zerol_bevel_gear_system_deflection(
        self: "CastSelf",
    ) -> "_3136.ZerolBevelGearSystemDeflection":
        from mastapy._private.system_model.analyses_and_results.system_deflections import (
            _3136,
        )

        return self.__parent__._cast(_3136.ZerolBevelGearSystemDeflection)

    @property
    def abstract_assembly_dynamic_analysis(
        self: "CastSelf",
    ) -> "_6641.AbstractAssemblyDynamicAnalysis":
        from mastapy._private.system_model.analyses_and_results.dynamic_analyses import (
            _6641,
        )

        return self.__parent__._cast(_6641.AbstractAssemblyDynamicAnalysis)

    @property
    def abstract_shaft_dynamic_analysis(
        self: "CastSelf",
    ) -> "_6642.AbstractShaftDynamicAnalysis":
        from mastapy._private.system_model.analyses_and_results.dynamic_analyses import (
            _6642,
        )

        return self.__parent__._cast(_6642.AbstractShaftDynamicAnalysis)

    @property
    def abstract_shaft_or_housing_dynamic_analysis(
        self: "CastSelf",
    ) -> "_6643.AbstractShaftOrHousingDynamicAnalysis":
        from mastapy._private.system_model.analyses_and_results.dynamic_analyses import (
            _6643,
        )

        return self.__parent__._cast(_6643.AbstractShaftOrHousingDynamicAnalysis)

    @property
    def agma_gleason_conical_gear_dynamic_analysis(
        self: "CastSelf",
    ) -> "_6645.AGMAGleasonConicalGearDynamicAnalysis":
        from mastapy._private.system_model.analyses_and_results.dynamic_analyses import (
            _6645,
        )

        return self.__parent__._cast(_6645.AGMAGleasonConicalGearDynamicAnalysis)

    @property
    def agma_gleason_conical_gear_set_dynamic_analysis(
        self: "CastSelf",
    ) -> "_6647.AGMAGleasonConicalGearSetDynamicAnalysis":
        from mastapy._private.system_model.analyses_and_results.dynamic_analyses import (
            _6647,
        )

        return self.__parent__._cast(_6647.AGMAGleasonConicalGearSetDynamicAnalysis)

    @property
    def assembly_dynamic_analysis(self: "CastSelf") -> "_6648.AssemblyDynamicAnalysis":
        from mastapy._private.system_model.analyses_and_results.dynamic_analyses import (
            _6648,
        )

        return self.__parent__._cast(_6648.AssemblyDynamicAnalysis)

    @property
    def bearing_dynamic_analysis(self: "CastSelf") -> "_6649.BearingDynamicAnalysis":
        from mastapy._private.system_model.analyses_and_results.dynamic_analyses import (
            _6649,
        )

        return self.__parent__._cast(_6649.BearingDynamicAnalysis)

    @property
    def belt_drive_dynamic_analysis(
        self: "CastSelf",
    ) -> "_6651.BeltDriveDynamicAnalysis":
        from mastapy._private.system_model.analyses_and_results.dynamic_analyses import (
            _6651,
        )

        return self.__parent__._cast(_6651.BeltDriveDynamicAnalysis)

    @property
    def bevel_differential_gear_dynamic_analysis(
        self: "CastSelf",
    ) -> "_6652.BevelDifferentialGearDynamicAnalysis":
        from mastapy._private.system_model.analyses_and_results.dynamic_analyses import (
            _6652,
        )

        return self.__parent__._cast(_6652.BevelDifferentialGearDynamicAnalysis)

    @property
    def bevel_differential_gear_set_dynamic_analysis(
        self: "CastSelf",
    ) -> "_6654.BevelDifferentialGearSetDynamicAnalysis":
        from mastapy._private.system_model.analyses_and_results.dynamic_analyses import (
            _6654,
        )

        return self.__parent__._cast(_6654.BevelDifferentialGearSetDynamicAnalysis)

    @property
    def bevel_differential_planet_gear_dynamic_analysis(
        self: "CastSelf",
    ) -> "_6655.BevelDifferentialPlanetGearDynamicAnalysis":
        from mastapy._private.system_model.analyses_and_results.dynamic_analyses import (
            _6655,
        )

        return self.__parent__._cast(_6655.BevelDifferentialPlanetGearDynamicAnalysis)

    @property
    def bevel_differential_sun_gear_dynamic_analysis(
        self: "CastSelf",
    ) -> "_6656.BevelDifferentialSunGearDynamicAnalysis":
        from mastapy._private.system_model.analyses_and_results.dynamic_analyses import (
            _6656,
        )

        return self.__parent__._cast(_6656.BevelDifferentialSunGearDynamicAnalysis)

    @property
    def bevel_gear_dynamic_analysis(
        self: "CastSelf",
    ) -> "_6657.BevelGearDynamicAnalysis":
        from mastapy._private.system_model.analyses_and_results.dynamic_analyses import (
            _6657,
        )

        return self.__parent__._cast(_6657.BevelGearDynamicAnalysis)

    @property
    def bevel_gear_set_dynamic_analysis(
        self: "CastSelf",
    ) -> "_6659.BevelGearSetDynamicAnalysis":
        from mastapy._private.system_model.analyses_and_results.dynamic_analyses import (
            _6659,
        )

        return self.__parent__._cast(_6659.BevelGearSetDynamicAnalysis)

    @property
    def bolt_dynamic_analysis(self: "CastSelf") -> "_6660.BoltDynamicAnalysis":
        from mastapy._private.system_model.analyses_and_results.dynamic_analyses import (
            _6660,
        )

        return self.__parent__._cast(_6660.BoltDynamicAnalysis)

    @property
    def bolted_joint_dynamic_analysis(
        self: "CastSelf",
    ) -> "_6661.BoltedJointDynamicAnalysis":
        from mastapy._private.system_model.analyses_and_results.dynamic_analyses import (
            _6661,
        )

        return self.__parent__._cast(_6661.BoltedJointDynamicAnalysis)

    @property
    def clutch_dynamic_analysis(self: "CastSelf") -> "_6663.ClutchDynamicAnalysis":
        from mastapy._private.system_model.analyses_and_results.dynamic_analyses import (
            _6663,
        )

        return self.__parent__._cast(_6663.ClutchDynamicAnalysis)

    @property
    def clutch_half_dynamic_analysis(
        self: "CastSelf",
    ) -> "_6664.ClutchHalfDynamicAnalysis":
        from mastapy._private.system_model.analyses_and_results.dynamic_analyses import (
            _6664,
        )

        return self.__parent__._cast(_6664.ClutchHalfDynamicAnalysis)

    @property
    def component_dynamic_analysis(
        self: "CastSelf",
    ) -> "_6666.ComponentDynamicAnalysis":
        from mastapy._private.system_model.analyses_and_results.dynamic_analyses import (
            _6666,
        )

        return self.__parent__._cast(_6666.ComponentDynamicAnalysis)

    @property
    def concept_coupling_dynamic_analysis(
        self: "CastSelf",
    ) -> "_6668.ConceptCouplingDynamicAnalysis":
        from mastapy._private.system_model.analyses_and_results.dynamic_analyses import (
            _6668,
        )

        return self.__parent__._cast(_6668.ConceptCouplingDynamicAnalysis)

    @property
    def concept_coupling_half_dynamic_analysis(
        self: "CastSelf",
    ) -> "_6669.ConceptCouplingHalfDynamicAnalysis":
        from mastapy._private.system_model.analyses_and_results.dynamic_analyses import (
            _6669,
        )

        return self.__parent__._cast(_6669.ConceptCouplingHalfDynamicAnalysis)

    @property
    def concept_gear_dynamic_analysis(
        self: "CastSelf",
    ) -> "_6670.ConceptGearDynamicAnalysis":
        from mastapy._private.system_model.analyses_and_results.dynamic_analyses import (
            _6670,
        )

        return self.__parent__._cast(_6670.ConceptGearDynamicAnalysis)

    @property
    def concept_gear_set_dynamic_analysis(
        self: "CastSelf",
    ) -> "_6672.ConceptGearSetDynamicAnalysis":
        from mastapy._private.system_model.analyses_and_results.dynamic_analyses import (
            _6672,
        )

        return self.__parent__._cast(_6672.ConceptGearSetDynamicAnalysis)

    @property
    def conical_gear_dynamic_analysis(
        self: "CastSelf",
    ) -> "_6673.ConicalGearDynamicAnalysis":
        from mastapy._private.system_model.analyses_and_results.dynamic_analyses import (
            _6673,
        )

        return self.__parent__._cast(_6673.ConicalGearDynamicAnalysis)

    @property
    def conical_gear_set_dynamic_analysis(
        self: "CastSelf",
    ) -> "_6675.ConicalGearSetDynamicAnalysis":
        from mastapy._private.system_model.analyses_and_results.dynamic_analyses import (
            _6675,
        )

        return self.__parent__._cast(_6675.ConicalGearSetDynamicAnalysis)

    @property
    def connector_dynamic_analysis(
        self: "CastSelf",
    ) -> "_6677.ConnectorDynamicAnalysis":
        from mastapy._private.system_model.analyses_and_results.dynamic_analyses import (
            _6677,
        )

        return self.__parent__._cast(_6677.ConnectorDynamicAnalysis)

    @property
    def coupling_dynamic_analysis(self: "CastSelf") -> "_6679.CouplingDynamicAnalysis":
        from mastapy._private.system_model.analyses_and_results.dynamic_analyses import (
            _6679,
        )

        return self.__parent__._cast(_6679.CouplingDynamicAnalysis)

    @property
    def coupling_half_dynamic_analysis(
        self: "CastSelf",
    ) -> "_6680.CouplingHalfDynamicAnalysis":
        from mastapy._private.system_model.analyses_and_results.dynamic_analyses import (
            _6680,
        )

        return self.__parent__._cast(_6680.CouplingHalfDynamicAnalysis)

    @property
    def cvt_dynamic_analysis(self: "CastSelf") -> "_6682.CVTDynamicAnalysis":
        from mastapy._private.system_model.analyses_and_results.dynamic_analyses import (
            _6682,
        )

        return self.__parent__._cast(_6682.CVTDynamicAnalysis)

    @property
    def cvt_pulley_dynamic_analysis(
        self: "CastSelf",
    ) -> "_6683.CVTPulleyDynamicAnalysis":
        from mastapy._private.system_model.analyses_and_results.dynamic_analyses import (
            _6683,
        )

        return self.__parent__._cast(_6683.CVTPulleyDynamicAnalysis)

    @property
    def cycloidal_assembly_dynamic_analysis(
        self: "CastSelf",
    ) -> "_6684.CycloidalAssemblyDynamicAnalysis":
        from mastapy._private.system_model.analyses_and_results.dynamic_analyses import (
            _6684,
        )

        return self.__parent__._cast(_6684.CycloidalAssemblyDynamicAnalysis)

    @property
    def cycloidal_disc_dynamic_analysis(
        self: "CastSelf",
    ) -> "_6686.CycloidalDiscDynamicAnalysis":
        from mastapy._private.system_model.analyses_and_results.dynamic_analyses import (
            _6686,
        )

        return self.__parent__._cast(_6686.CycloidalDiscDynamicAnalysis)

    @property
    def cylindrical_gear_dynamic_analysis(
        self: "CastSelf",
    ) -> "_6688.CylindricalGearDynamicAnalysis":
        from mastapy._private.system_model.analyses_and_results.dynamic_analyses import (
            _6688,
        )

        return self.__parent__._cast(_6688.CylindricalGearDynamicAnalysis)

    @property
    def cylindrical_gear_set_dynamic_analysis(
        self: "CastSelf",
    ) -> "_6690.CylindricalGearSetDynamicAnalysis":
        from mastapy._private.system_model.analyses_and_results.dynamic_analyses import (
            _6690,
        )

        return self.__parent__._cast(_6690.CylindricalGearSetDynamicAnalysis)

    @property
    def cylindrical_planet_gear_dynamic_analysis(
        self: "CastSelf",
    ) -> "_6691.CylindricalPlanetGearDynamicAnalysis":
        from mastapy._private.system_model.analyses_and_results.dynamic_analyses import (
            _6691,
        )

        return self.__parent__._cast(_6691.CylindricalPlanetGearDynamicAnalysis)

    @property
    def datum_dynamic_analysis(self: "CastSelf") -> "_6692.DatumDynamicAnalysis":
        from mastapy._private.system_model.analyses_and_results.dynamic_analyses import (
            _6692,
        )

        return self.__parent__._cast(_6692.DatumDynamicAnalysis)

    @property
    def external_cad_model_dynamic_analysis(
        self: "CastSelf",
    ) -> "_6695.ExternalCADModelDynamicAnalysis":
        from mastapy._private.system_model.analyses_and_results.dynamic_analyses import (
            _6695,
        )

        return self.__parent__._cast(_6695.ExternalCADModelDynamicAnalysis)

    @property
    def face_gear_dynamic_analysis(self: "CastSelf") -> "_6696.FaceGearDynamicAnalysis":
        from mastapy._private.system_model.analyses_and_results.dynamic_analyses import (
            _6696,
        )

        return self.__parent__._cast(_6696.FaceGearDynamicAnalysis)

    @property
    def face_gear_set_dynamic_analysis(
        self: "CastSelf",
    ) -> "_6698.FaceGearSetDynamicAnalysis":
        from mastapy._private.system_model.analyses_and_results.dynamic_analyses import (
            _6698,
        )

        return self.__parent__._cast(_6698.FaceGearSetDynamicAnalysis)

    @property
    def fe_part_dynamic_analysis(self: "CastSelf") -> "_6699.FEPartDynamicAnalysis":
        from mastapy._private.system_model.analyses_and_results.dynamic_analyses import (
            _6699,
        )

        return self.__parent__._cast(_6699.FEPartDynamicAnalysis)

    @property
    def flexible_pin_assembly_dynamic_analysis(
        self: "CastSelf",
    ) -> "_6700.FlexiblePinAssemblyDynamicAnalysis":
        from mastapy._private.system_model.analyses_and_results.dynamic_analyses import (
            _6700,
        )

        return self.__parent__._cast(_6700.FlexiblePinAssemblyDynamicAnalysis)

    @property
    def gear_dynamic_analysis(self: "CastSelf") -> "_6701.GearDynamicAnalysis":
        from mastapy._private.system_model.analyses_and_results.dynamic_analyses import (
            _6701,
        )

        return self.__parent__._cast(_6701.GearDynamicAnalysis)

    @property
    def gear_set_dynamic_analysis(self: "CastSelf") -> "_6703.GearSetDynamicAnalysis":
        from mastapy._private.system_model.analyses_and_results.dynamic_analyses import (
            _6703,
        )

        return self.__parent__._cast(_6703.GearSetDynamicAnalysis)

    @property
    def guide_dxf_model_dynamic_analysis(
        self: "CastSelf",
    ) -> "_6704.GuideDxfModelDynamicAnalysis":
        from mastapy._private.system_model.analyses_and_results.dynamic_analyses import (
            _6704,
        )

        return self.__parent__._cast(_6704.GuideDxfModelDynamicAnalysis)

    @property
    def hypoid_gear_dynamic_analysis(
        self: "CastSelf",
    ) -> "_6705.HypoidGearDynamicAnalysis":
        from mastapy._private.system_model.analyses_and_results.dynamic_analyses import (
            _6705,
        )

        return self.__parent__._cast(_6705.HypoidGearDynamicAnalysis)

    @property
    def hypoid_gear_set_dynamic_analysis(
        self: "CastSelf",
    ) -> "_6707.HypoidGearSetDynamicAnalysis":
        from mastapy._private.system_model.analyses_and_results.dynamic_analyses import (
            _6707,
        )

        return self.__parent__._cast(_6707.HypoidGearSetDynamicAnalysis)

    @property
    def klingelnberg_cyclo_palloid_conical_gear_dynamic_analysis(
        self: "CastSelf",
    ) -> "_6709.KlingelnbergCycloPalloidConicalGearDynamicAnalysis":
        from mastapy._private.system_model.analyses_and_results.dynamic_analyses import (
            _6709,
        )

        return self.__parent__._cast(
            _6709.KlingelnbergCycloPalloidConicalGearDynamicAnalysis
        )

    @property
    def klingelnberg_cyclo_palloid_conical_gear_set_dynamic_analysis(
        self: "CastSelf",
    ) -> "_6711.KlingelnbergCycloPalloidConicalGearSetDynamicAnalysis":
        from mastapy._private.system_model.analyses_and_results.dynamic_analyses import (
            _6711,
        )

        return self.__parent__._cast(
            _6711.KlingelnbergCycloPalloidConicalGearSetDynamicAnalysis
        )

    @property
    def klingelnberg_cyclo_palloid_hypoid_gear_dynamic_analysis(
        self: "CastSelf",
    ) -> "_6712.KlingelnbergCycloPalloidHypoidGearDynamicAnalysis":
        from mastapy._private.system_model.analyses_and_results.dynamic_analyses import (
            _6712,
        )

        return self.__parent__._cast(
            _6712.KlingelnbergCycloPalloidHypoidGearDynamicAnalysis
        )

    @property
    def klingelnberg_cyclo_palloid_hypoid_gear_set_dynamic_analysis(
        self: "CastSelf",
    ) -> "_6714.KlingelnbergCycloPalloidHypoidGearSetDynamicAnalysis":
        from mastapy._private.system_model.analyses_and_results.dynamic_analyses import (
            _6714,
        )

        return self.__parent__._cast(
            _6714.KlingelnbergCycloPalloidHypoidGearSetDynamicAnalysis
        )

    @property
    def klingelnberg_cyclo_palloid_spiral_bevel_gear_dynamic_analysis(
        self: "CastSelf",
    ) -> "_6715.KlingelnbergCycloPalloidSpiralBevelGearDynamicAnalysis":
        from mastapy._private.system_model.analyses_and_results.dynamic_analyses import (
            _6715,
        )

        return self.__parent__._cast(
            _6715.KlingelnbergCycloPalloidSpiralBevelGearDynamicAnalysis
        )

    @property
    def klingelnberg_cyclo_palloid_spiral_bevel_gear_set_dynamic_analysis(
        self: "CastSelf",
    ) -> "_6717.KlingelnbergCycloPalloidSpiralBevelGearSetDynamicAnalysis":
        from mastapy._private.system_model.analyses_and_results.dynamic_analyses import (
            _6717,
        )

        return self.__parent__._cast(
            _6717.KlingelnbergCycloPalloidSpiralBevelGearSetDynamicAnalysis
        )

    @property
    def mass_disc_dynamic_analysis(self: "CastSelf") -> "_6718.MassDiscDynamicAnalysis":
        from mastapy._private.system_model.analyses_and_results.dynamic_analyses import (
            _6718,
        )

        return self.__parent__._cast(_6718.MassDiscDynamicAnalysis)

    @property
    def measurement_component_dynamic_analysis(
        self: "CastSelf",
    ) -> "_6719.MeasurementComponentDynamicAnalysis":
        from mastapy._private.system_model.analyses_and_results.dynamic_analyses import (
            _6719,
        )

        return self.__parent__._cast(_6719.MeasurementComponentDynamicAnalysis)

    @property
    def microphone_array_dynamic_analysis(
        self: "CastSelf",
    ) -> "_6720.MicrophoneArrayDynamicAnalysis":
        from mastapy._private.system_model.analyses_and_results.dynamic_analyses import (
            _6720,
        )

        return self.__parent__._cast(_6720.MicrophoneArrayDynamicAnalysis)

    @property
    def microphone_dynamic_analysis(
        self: "CastSelf",
    ) -> "_6721.MicrophoneDynamicAnalysis":
        from mastapy._private.system_model.analyses_and_results.dynamic_analyses import (
            _6721,
        )

        return self.__parent__._cast(_6721.MicrophoneDynamicAnalysis)

    @property
    def mountable_component_dynamic_analysis(
        self: "CastSelf",
    ) -> "_6722.MountableComponentDynamicAnalysis":
        from mastapy._private.system_model.analyses_and_results.dynamic_analyses import (
            _6722,
        )

        return self.__parent__._cast(_6722.MountableComponentDynamicAnalysis)

    @property
    def oil_seal_dynamic_analysis(self: "CastSelf") -> "_6723.OilSealDynamicAnalysis":
        from mastapy._private.system_model.analyses_and_results.dynamic_analyses import (
            _6723,
        )

        return self.__parent__._cast(_6723.OilSealDynamicAnalysis)

    @property
    def part_dynamic_analysis(self: "CastSelf") -> "_6724.PartDynamicAnalysis":
        from mastapy._private.system_model.analyses_and_results.dynamic_analyses import (
            _6724,
        )

        return self.__parent__._cast(_6724.PartDynamicAnalysis)

    @property
    def part_to_part_shear_coupling_dynamic_analysis(
        self: "CastSelf",
    ) -> "_6726.PartToPartShearCouplingDynamicAnalysis":
        from mastapy._private.system_model.analyses_and_results.dynamic_analyses import (
            _6726,
        )

        return self.__parent__._cast(_6726.PartToPartShearCouplingDynamicAnalysis)

    @property
    def part_to_part_shear_coupling_half_dynamic_analysis(
        self: "CastSelf",
    ) -> "_6727.PartToPartShearCouplingHalfDynamicAnalysis":
        from mastapy._private.system_model.analyses_and_results.dynamic_analyses import (
            _6727,
        )

        return self.__parent__._cast(_6727.PartToPartShearCouplingHalfDynamicAnalysis)

    @property
    def planetary_gear_set_dynamic_analysis(
        self: "CastSelf",
    ) -> "_6729.PlanetaryGearSetDynamicAnalysis":
        from mastapy._private.system_model.analyses_and_results.dynamic_analyses import (
            _6729,
        )

        return self.__parent__._cast(_6729.PlanetaryGearSetDynamicAnalysis)

    @property
    def planet_carrier_dynamic_analysis(
        self: "CastSelf",
    ) -> "_6730.PlanetCarrierDynamicAnalysis":
        from mastapy._private.system_model.analyses_and_results.dynamic_analyses import (
            _6730,
        )

        return self.__parent__._cast(_6730.PlanetCarrierDynamicAnalysis)

    @property
    def point_load_dynamic_analysis(
        self: "CastSelf",
    ) -> "_6731.PointLoadDynamicAnalysis":
        from mastapy._private.system_model.analyses_and_results.dynamic_analyses import (
            _6731,
        )

        return self.__parent__._cast(_6731.PointLoadDynamicAnalysis)

    @property
    def power_load_dynamic_analysis(
        self: "CastSelf",
    ) -> "_6732.PowerLoadDynamicAnalysis":
        from mastapy._private.system_model.analyses_and_results.dynamic_analyses import (
            _6732,
        )

        return self.__parent__._cast(_6732.PowerLoadDynamicAnalysis)

    @property
    def pulley_dynamic_analysis(self: "CastSelf") -> "_6733.PulleyDynamicAnalysis":
        from mastapy._private.system_model.analyses_and_results.dynamic_analyses import (
            _6733,
        )

        return self.__parent__._cast(_6733.PulleyDynamicAnalysis)

    @property
    def ring_pins_dynamic_analysis(self: "CastSelf") -> "_6734.RingPinsDynamicAnalysis":
        from mastapy._private.system_model.analyses_and_results.dynamic_analyses import (
            _6734,
        )

        return self.__parent__._cast(_6734.RingPinsDynamicAnalysis)

    @property
    def rolling_ring_assembly_dynamic_analysis(
        self: "CastSelf",
    ) -> "_6736.RollingRingAssemblyDynamicAnalysis":
        from mastapy._private.system_model.analyses_and_results.dynamic_analyses import (
            _6736,
        )

        return self.__parent__._cast(_6736.RollingRingAssemblyDynamicAnalysis)

    @property
    def rolling_ring_dynamic_analysis(
        self: "CastSelf",
    ) -> "_6738.RollingRingDynamicAnalysis":
        from mastapy._private.system_model.analyses_and_results.dynamic_analyses import (
            _6738,
        )

        return self.__parent__._cast(_6738.RollingRingDynamicAnalysis)

    @property
    def root_assembly_dynamic_analysis(
        self: "CastSelf",
    ) -> "_6739.RootAssemblyDynamicAnalysis":
        from mastapy._private.system_model.analyses_and_results.dynamic_analyses import (
            _6739,
        )

        return self.__parent__._cast(_6739.RootAssemblyDynamicAnalysis)

    @property
    def shaft_dynamic_analysis(self: "CastSelf") -> "_6740.ShaftDynamicAnalysis":
        from mastapy._private.system_model.analyses_and_results.dynamic_analyses import (
            _6740,
        )

        return self.__parent__._cast(_6740.ShaftDynamicAnalysis)

    @property
    def shaft_hub_connection_dynamic_analysis(
        self: "CastSelf",
    ) -> "_6741.ShaftHubConnectionDynamicAnalysis":
        from mastapy._private.system_model.analyses_and_results.dynamic_analyses import (
            _6741,
        )

        return self.__parent__._cast(_6741.ShaftHubConnectionDynamicAnalysis)

    @property
    def specialised_assembly_dynamic_analysis(
        self: "CastSelf",
    ) -> "_6743.SpecialisedAssemblyDynamicAnalysis":
        from mastapy._private.system_model.analyses_and_results.dynamic_analyses import (
            _6743,
        )

        return self.__parent__._cast(_6743.SpecialisedAssemblyDynamicAnalysis)

    @property
    def spiral_bevel_gear_dynamic_analysis(
        self: "CastSelf",
    ) -> "_6744.SpiralBevelGearDynamicAnalysis":
        from mastapy._private.system_model.analyses_and_results.dynamic_analyses import (
            _6744,
        )

        return self.__parent__._cast(_6744.SpiralBevelGearDynamicAnalysis)

    @property
    def spiral_bevel_gear_set_dynamic_analysis(
        self: "CastSelf",
    ) -> "_6746.SpiralBevelGearSetDynamicAnalysis":
        from mastapy._private.system_model.analyses_and_results.dynamic_analyses import (
            _6746,
        )

        return self.__parent__._cast(_6746.SpiralBevelGearSetDynamicAnalysis)

    @property
    def spring_damper_dynamic_analysis(
        self: "CastSelf",
    ) -> "_6748.SpringDamperDynamicAnalysis":
        from mastapy._private.system_model.analyses_and_results.dynamic_analyses import (
            _6748,
        )

        return self.__parent__._cast(_6748.SpringDamperDynamicAnalysis)

    @property
    def spring_damper_half_dynamic_analysis(
        self: "CastSelf",
    ) -> "_6749.SpringDamperHalfDynamicAnalysis":
        from mastapy._private.system_model.analyses_and_results.dynamic_analyses import (
            _6749,
        )

        return self.__parent__._cast(_6749.SpringDamperHalfDynamicAnalysis)

    @property
    def straight_bevel_diff_gear_dynamic_analysis(
        self: "CastSelf",
    ) -> "_6750.StraightBevelDiffGearDynamicAnalysis":
        from mastapy._private.system_model.analyses_and_results.dynamic_analyses import (
            _6750,
        )

        return self.__parent__._cast(_6750.StraightBevelDiffGearDynamicAnalysis)

    @property
    def straight_bevel_diff_gear_set_dynamic_analysis(
        self: "CastSelf",
    ) -> "_6752.StraightBevelDiffGearSetDynamicAnalysis":
        from mastapy._private.system_model.analyses_and_results.dynamic_analyses import (
            _6752,
        )

        return self.__parent__._cast(_6752.StraightBevelDiffGearSetDynamicAnalysis)

    @property
    def straight_bevel_gear_dynamic_analysis(
        self: "CastSelf",
    ) -> "_6753.StraightBevelGearDynamicAnalysis":
        from mastapy._private.system_model.analyses_and_results.dynamic_analyses import (
            _6753,
        )

        return self.__parent__._cast(_6753.StraightBevelGearDynamicAnalysis)

    @property
    def straight_bevel_gear_set_dynamic_analysis(
        self: "CastSelf",
    ) -> "_6755.StraightBevelGearSetDynamicAnalysis":
        from mastapy._private.system_model.analyses_and_results.dynamic_analyses import (
            _6755,
        )

        return self.__parent__._cast(_6755.StraightBevelGearSetDynamicAnalysis)

    @property
    def straight_bevel_planet_gear_dynamic_analysis(
        self: "CastSelf",
    ) -> "_6756.StraightBevelPlanetGearDynamicAnalysis":
        from mastapy._private.system_model.analyses_and_results.dynamic_analyses import (
            _6756,
        )

        return self.__parent__._cast(_6756.StraightBevelPlanetGearDynamicAnalysis)

    @property
    def straight_bevel_sun_gear_dynamic_analysis(
        self: "CastSelf",
    ) -> "_6757.StraightBevelSunGearDynamicAnalysis":
        from mastapy._private.system_model.analyses_and_results.dynamic_analyses import (
            _6757,
        )

        return self.__parent__._cast(_6757.StraightBevelSunGearDynamicAnalysis)

    @property
    def synchroniser_dynamic_analysis(
        self: "CastSelf",
    ) -> "_6758.SynchroniserDynamicAnalysis":
        from mastapy._private.system_model.analyses_and_results.dynamic_analyses import (
            _6758,
        )

        return self.__parent__._cast(_6758.SynchroniserDynamicAnalysis)

    @property
    def synchroniser_half_dynamic_analysis(
        self: "CastSelf",
    ) -> "_6759.SynchroniserHalfDynamicAnalysis":
        from mastapy._private.system_model.analyses_and_results.dynamic_analyses import (
            _6759,
        )

        return self.__parent__._cast(_6759.SynchroniserHalfDynamicAnalysis)

    @property
    def synchroniser_part_dynamic_analysis(
        self: "CastSelf",
    ) -> "_6760.SynchroniserPartDynamicAnalysis":
        from mastapy._private.system_model.analyses_and_results.dynamic_analyses import (
            _6760,
        )

        return self.__parent__._cast(_6760.SynchroniserPartDynamicAnalysis)

    @property
    def synchroniser_sleeve_dynamic_analysis(
        self: "CastSelf",
    ) -> "_6761.SynchroniserSleeveDynamicAnalysis":
        from mastapy._private.system_model.analyses_and_results.dynamic_analyses import (
            _6761,
        )

        return self.__parent__._cast(_6761.SynchroniserSleeveDynamicAnalysis)

    @property
    def torque_converter_dynamic_analysis(
        self: "CastSelf",
    ) -> "_6763.TorqueConverterDynamicAnalysis":
        from mastapy._private.system_model.analyses_and_results.dynamic_analyses import (
            _6763,
        )

        return self.__parent__._cast(_6763.TorqueConverterDynamicAnalysis)

    @property
    def torque_converter_pump_dynamic_analysis(
        self: "CastSelf",
    ) -> "_6764.TorqueConverterPumpDynamicAnalysis":
        from mastapy._private.system_model.analyses_and_results.dynamic_analyses import (
            _6764,
        )

        return self.__parent__._cast(_6764.TorqueConverterPumpDynamicAnalysis)

    @property
    def torque_converter_turbine_dynamic_analysis(
        self: "CastSelf",
    ) -> "_6765.TorqueConverterTurbineDynamicAnalysis":
        from mastapy._private.system_model.analyses_and_results.dynamic_analyses import (
            _6765,
        )

        return self.__parent__._cast(_6765.TorqueConverterTurbineDynamicAnalysis)

    @property
    def unbalanced_mass_dynamic_analysis(
        self: "CastSelf",
    ) -> "_6766.UnbalancedMassDynamicAnalysis":
        from mastapy._private.system_model.analyses_and_results.dynamic_analyses import (
            _6766,
        )

        return self.__parent__._cast(_6766.UnbalancedMassDynamicAnalysis)

    @property
    def virtual_component_dynamic_analysis(
        self: "CastSelf",
    ) -> "_6767.VirtualComponentDynamicAnalysis":
        from mastapy._private.system_model.analyses_and_results.dynamic_analyses import (
            _6767,
        )

        return self.__parent__._cast(_6767.VirtualComponentDynamicAnalysis)

    @property
    def worm_gear_dynamic_analysis(self: "CastSelf") -> "_6768.WormGearDynamicAnalysis":
        from mastapy._private.system_model.analyses_and_results.dynamic_analyses import (
            _6768,
        )

        return self.__parent__._cast(_6768.WormGearDynamicAnalysis)

    @property
    def worm_gear_set_dynamic_analysis(
        self: "CastSelf",
    ) -> "_6770.WormGearSetDynamicAnalysis":
        from mastapy._private.system_model.analyses_and_results.dynamic_analyses import (
            _6770,
        )

        return self.__parent__._cast(_6770.WormGearSetDynamicAnalysis)

    @property
    def zerol_bevel_gear_dynamic_analysis(
        self: "CastSelf",
    ) -> "_6771.ZerolBevelGearDynamicAnalysis":
        from mastapy._private.system_model.analyses_and_results.dynamic_analyses import (
            _6771,
        )

        return self.__parent__._cast(_6771.ZerolBevelGearDynamicAnalysis)

    @property
    def zerol_bevel_gear_set_dynamic_analysis(
        self: "CastSelf",
    ) -> "_6773.ZerolBevelGearSetDynamicAnalysis":
        from mastapy._private.system_model.analyses_and_results.dynamic_analyses import (
            _6773,
        )

        return self.__parent__._cast(_6773.ZerolBevelGearSetDynamicAnalysis)

    @property
    def part_fe_analysis(self: "CastSelf") -> "PartFEAnalysis":
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
class PartFEAnalysis(_7944.PartStaticLoadAnalysisCase):
    """PartFEAnalysis

    This is a mastapy class.
    """

    TYPE: ClassVar["Type"] = _PART_FE_ANALYSIS

    wrapped: "Any"

    def __post_init__(self: "Self") -> None:
        """Override of the post initialisation magic method."""
        if not hasattr(self.wrapped, "reference_count"):
            self.wrapped.reference_count = 0

        self.wrapped.reference_count += 1

    @property
    def cast_to(self: "Self") -> "_Cast_PartFEAnalysis":
        """Cast to another type.

        Returns:
            _Cast_PartFEAnalysis
        """
        return _Cast_PartFEAnalysis(self)
