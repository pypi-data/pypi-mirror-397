"""ConnectionFEAnalysis"""

from __future__ import annotations

from typing import TYPE_CHECKING, ClassVar

from mastapy._private._internal.dataclasses import extended_dataclass
from mastapy._private._internal.exceptions import CastException
from mastapy._private._internal.python_net import python_net_import

from mastapy._private._internal import utility
from mastapy._private.system_model.analyses_and_results.analysis_cases import _7937

_CONNECTION_FE_ANALYSIS = python_net_import(
    "SMT.MastaAPI.SystemModel.AnalysesAndResults.AnalysisCases", "ConnectionFEAnalysis"
)

if TYPE_CHECKING:
    from typing import Any, Type, TypeVar

    from mastapy._private.system_model.analyses_and_results import _2941, _2943, _2945
    from mastapy._private.system_model.analyses_and_results.analysis_cases import _7934
    from mastapy._private.system_model.analyses_and_results.dynamic_analyses import (
        _6644,
        _6646,
        _6650,
        _6653,
        _6658,
        _6662,
        _6665,
        _6667,
        _6671,
        _6674,
        _6676,
        _6678,
        _6681,
        _6685,
        _6687,
        _6689,
        _6697,
        _6702,
        _6706,
        _6708,
        _6710,
        _6713,
        _6716,
        _6725,
        _6728,
        _6735,
        _6737,
        _6742,
        _6745,
        _6747,
        _6751,
        _6754,
        _6762,
        _6769,
        _6772,
    )
    from mastapy._private.system_model.analyses_and_results.system_deflections import (
        _2980,
        _2981,
        _2991,
        _2993,
        _2998,
        _3003,
        _3006,
        _3009,
        _3012,
        _3016,
        _3019,
        _3021,
        _3024,
        _3028,
        _3029,
        _3031,
        _3032,
        _3033,
        _3046,
        _3051,
        _3055,
        _3059,
        _3060,
        _3063,
        _3066,
        _3080,
        _3083,
        _3089,
        _3092,
        _3099,
        _3101,
        _3104,
        _3107,
        _3110,
        _3122,
        _3131,
        _3134,
    )

    Self = TypeVar("Self", bound="ConnectionFEAnalysis")
    CastSelf = TypeVar(
        "CastSelf", bound="ConnectionFEAnalysis._Cast_ConnectionFEAnalysis"
    )


__docformat__ = "restructuredtext en"
__all__ = ("ConnectionFEAnalysis",)


@extended_dataclass(frozen=True, slots=True, weakref_slot=True)
class _Cast_ConnectionFEAnalysis:
    """Special nested class for casting ConnectionFEAnalysis to subclasses."""

    __parent__: "ConnectionFEAnalysis"

    @property
    def connection_static_load_analysis_case(
        self: "CastSelf",
    ) -> "_7937.ConnectionStaticLoadAnalysisCase":
        return self.__parent__._cast(_7937.ConnectionStaticLoadAnalysisCase)

    @property
    def connection_analysis_case(self: "CastSelf") -> "_7934.ConnectionAnalysisCase":
        from mastapy._private.system_model.analyses_and_results.analysis_cases import (
            _7934,
        )

        return self.__parent__._cast(_7934.ConnectionAnalysisCase)

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
    def abstract_shaft_to_mountable_component_connection_system_deflection(
        self: "CastSelf",
    ) -> "_2980.AbstractShaftToMountableComponentConnectionSystemDeflection":
        from mastapy._private.system_model.analyses_and_results.system_deflections import (
            _2980,
        )

        return self.__parent__._cast(
            _2980.AbstractShaftToMountableComponentConnectionSystemDeflection
        )

    @property
    def agma_gleason_conical_gear_mesh_system_deflection(
        self: "CastSelf",
    ) -> "_2981.AGMAGleasonConicalGearMeshSystemDeflection":
        from mastapy._private.system_model.analyses_and_results.system_deflections import (
            _2981,
        )

        return self.__parent__._cast(_2981.AGMAGleasonConicalGearMeshSystemDeflection)

    @property
    def belt_connection_system_deflection(
        self: "CastSelf",
    ) -> "_2991.BeltConnectionSystemDeflection":
        from mastapy._private.system_model.analyses_and_results.system_deflections import (
            _2991,
        )

        return self.__parent__._cast(_2991.BeltConnectionSystemDeflection)

    @property
    def bevel_differential_gear_mesh_system_deflection(
        self: "CastSelf",
    ) -> "_2993.BevelDifferentialGearMeshSystemDeflection":
        from mastapy._private.system_model.analyses_and_results.system_deflections import (
            _2993,
        )

        return self.__parent__._cast(_2993.BevelDifferentialGearMeshSystemDeflection)

    @property
    def bevel_gear_mesh_system_deflection(
        self: "CastSelf",
    ) -> "_2998.BevelGearMeshSystemDeflection":
        from mastapy._private.system_model.analyses_and_results.system_deflections import (
            _2998,
        )

        return self.__parent__._cast(_2998.BevelGearMeshSystemDeflection)

    @property
    def clutch_connection_system_deflection(
        self: "CastSelf",
    ) -> "_3003.ClutchConnectionSystemDeflection":
        from mastapy._private.system_model.analyses_and_results.system_deflections import (
            _3003,
        )

        return self.__parent__._cast(_3003.ClutchConnectionSystemDeflection)

    @property
    def coaxial_connection_system_deflection(
        self: "CastSelf",
    ) -> "_3006.CoaxialConnectionSystemDeflection":
        from mastapy._private.system_model.analyses_and_results.system_deflections import (
            _3006,
        )

        return self.__parent__._cast(_3006.CoaxialConnectionSystemDeflection)

    @property
    def concept_coupling_connection_system_deflection(
        self: "CastSelf",
    ) -> "_3009.ConceptCouplingConnectionSystemDeflection":
        from mastapy._private.system_model.analyses_and_results.system_deflections import (
            _3009,
        )

        return self.__parent__._cast(_3009.ConceptCouplingConnectionSystemDeflection)

    @property
    def concept_gear_mesh_system_deflection(
        self: "CastSelf",
    ) -> "_3012.ConceptGearMeshSystemDeflection":
        from mastapy._private.system_model.analyses_and_results.system_deflections import (
            _3012,
        )

        return self.__parent__._cast(_3012.ConceptGearMeshSystemDeflection)

    @property
    def conical_gear_mesh_system_deflection(
        self: "CastSelf",
    ) -> "_3016.ConicalGearMeshSystemDeflection":
        from mastapy._private.system_model.analyses_and_results.system_deflections import (
            _3016,
        )

        return self.__parent__._cast(_3016.ConicalGearMeshSystemDeflection)

    @property
    def connection_system_deflection(
        self: "CastSelf",
    ) -> "_3019.ConnectionSystemDeflection":
        from mastapy._private.system_model.analyses_and_results.system_deflections import (
            _3019,
        )

        return self.__parent__._cast(_3019.ConnectionSystemDeflection)

    @property
    def coupling_connection_system_deflection(
        self: "CastSelf",
    ) -> "_3021.CouplingConnectionSystemDeflection":
        from mastapy._private.system_model.analyses_and_results.system_deflections import (
            _3021,
        )

        return self.__parent__._cast(_3021.CouplingConnectionSystemDeflection)

    @property
    def cvt_belt_connection_system_deflection(
        self: "CastSelf",
    ) -> "_3024.CVTBeltConnectionSystemDeflection":
        from mastapy._private.system_model.analyses_and_results.system_deflections import (
            _3024,
        )

        return self.__parent__._cast(_3024.CVTBeltConnectionSystemDeflection)

    @property
    def cycloidal_disc_central_bearing_connection_system_deflection(
        self: "CastSelf",
    ) -> "_3028.CycloidalDiscCentralBearingConnectionSystemDeflection":
        from mastapy._private.system_model.analyses_and_results.system_deflections import (
            _3028,
        )

        return self.__parent__._cast(
            _3028.CycloidalDiscCentralBearingConnectionSystemDeflection
        )

    @property
    def cycloidal_disc_planetary_bearing_connection_system_deflection(
        self: "CastSelf",
    ) -> "_3029.CycloidalDiscPlanetaryBearingConnectionSystemDeflection":
        from mastapy._private.system_model.analyses_and_results.system_deflections import (
            _3029,
        )

        return self.__parent__._cast(
            _3029.CycloidalDiscPlanetaryBearingConnectionSystemDeflection
        )

    @property
    def cylindrical_gear_mesh_system_deflection(
        self: "CastSelf",
    ) -> "_3031.CylindricalGearMeshSystemDeflection":
        from mastapy._private.system_model.analyses_and_results.system_deflections import (
            _3031,
        )

        return self.__parent__._cast(_3031.CylindricalGearMeshSystemDeflection)

    @property
    def cylindrical_gear_mesh_system_deflection_timestep(
        self: "CastSelf",
    ) -> "_3032.CylindricalGearMeshSystemDeflectionTimestep":
        from mastapy._private.system_model.analyses_and_results.system_deflections import (
            _3032,
        )

        return self.__parent__._cast(_3032.CylindricalGearMeshSystemDeflectionTimestep)

    @property
    def cylindrical_gear_mesh_system_deflection_with_ltca_results(
        self: "CastSelf",
    ) -> "_3033.CylindricalGearMeshSystemDeflectionWithLTCAResults":
        from mastapy._private.system_model.analyses_and_results.system_deflections import (
            _3033,
        )

        return self.__parent__._cast(
            _3033.CylindricalGearMeshSystemDeflectionWithLTCAResults
        )

    @property
    def face_gear_mesh_system_deflection(
        self: "CastSelf",
    ) -> "_3046.FaceGearMeshSystemDeflection":
        from mastapy._private.system_model.analyses_and_results.system_deflections import (
            _3046,
        )

        return self.__parent__._cast(_3046.FaceGearMeshSystemDeflection)

    @property
    def gear_mesh_system_deflection(
        self: "CastSelf",
    ) -> "_3051.GearMeshSystemDeflection":
        from mastapy._private.system_model.analyses_and_results.system_deflections import (
            _3051,
        )

        return self.__parent__._cast(_3051.GearMeshSystemDeflection)

    @property
    def hypoid_gear_mesh_system_deflection(
        self: "CastSelf",
    ) -> "_3055.HypoidGearMeshSystemDeflection":
        from mastapy._private.system_model.analyses_and_results.system_deflections import (
            _3055,
        )

        return self.__parent__._cast(_3055.HypoidGearMeshSystemDeflection)

    @property
    def inter_mountable_component_connection_system_deflection(
        self: "CastSelf",
    ) -> "_3059.InterMountableComponentConnectionSystemDeflection":
        from mastapy._private.system_model.analyses_and_results.system_deflections import (
            _3059,
        )

        return self.__parent__._cast(
            _3059.InterMountableComponentConnectionSystemDeflection
        )

    @property
    def klingelnberg_cyclo_palloid_conical_gear_mesh_system_deflection(
        self: "CastSelf",
    ) -> "_3060.KlingelnbergCycloPalloidConicalGearMeshSystemDeflection":
        from mastapy._private.system_model.analyses_and_results.system_deflections import (
            _3060,
        )

        return self.__parent__._cast(
            _3060.KlingelnbergCycloPalloidConicalGearMeshSystemDeflection
        )

    @property
    def klingelnberg_cyclo_palloid_hypoid_gear_mesh_system_deflection(
        self: "CastSelf",
    ) -> "_3063.KlingelnbergCycloPalloidHypoidGearMeshSystemDeflection":
        from mastapy._private.system_model.analyses_and_results.system_deflections import (
            _3063,
        )

        return self.__parent__._cast(
            _3063.KlingelnbergCycloPalloidHypoidGearMeshSystemDeflection
        )

    @property
    def klingelnberg_cyclo_palloid_spiral_bevel_gear_mesh_system_deflection(
        self: "CastSelf",
    ) -> "_3066.KlingelnbergCycloPalloidSpiralBevelGearMeshSystemDeflection":
        from mastapy._private.system_model.analyses_and_results.system_deflections import (
            _3066,
        )

        return self.__parent__._cast(
            _3066.KlingelnbergCycloPalloidSpiralBevelGearMeshSystemDeflection
        )

    @property
    def part_to_part_shear_coupling_connection_system_deflection(
        self: "CastSelf",
    ) -> "_3080.PartToPartShearCouplingConnectionSystemDeflection":
        from mastapy._private.system_model.analyses_and_results.system_deflections import (
            _3080,
        )

        return self.__parent__._cast(
            _3080.PartToPartShearCouplingConnectionSystemDeflection
        )

    @property
    def planetary_connection_system_deflection(
        self: "CastSelf",
    ) -> "_3083.PlanetaryConnectionSystemDeflection":
        from mastapy._private.system_model.analyses_and_results.system_deflections import (
            _3083,
        )

        return self.__parent__._cast(_3083.PlanetaryConnectionSystemDeflection)

    @property
    def ring_pins_to_disc_connection_system_deflection(
        self: "CastSelf",
    ) -> "_3089.RingPinsToDiscConnectionSystemDeflection":
        from mastapy._private.system_model.analyses_and_results.system_deflections import (
            _3089,
        )

        return self.__parent__._cast(_3089.RingPinsToDiscConnectionSystemDeflection)

    @property
    def rolling_ring_connection_system_deflection(
        self: "CastSelf",
    ) -> "_3092.RollingRingConnectionSystemDeflection":
        from mastapy._private.system_model.analyses_and_results.system_deflections import (
            _3092,
        )

        return self.__parent__._cast(_3092.RollingRingConnectionSystemDeflection)

    @property
    def shaft_to_mountable_component_connection_system_deflection(
        self: "CastSelf",
    ) -> "_3099.ShaftToMountableComponentConnectionSystemDeflection":
        from mastapy._private.system_model.analyses_and_results.system_deflections import (
            _3099,
        )

        return self.__parent__._cast(
            _3099.ShaftToMountableComponentConnectionSystemDeflection
        )

    @property
    def spiral_bevel_gear_mesh_system_deflection(
        self: "CastSelf",
    ) -> "_3101.SpiralBevelGearMeshSystemDeflection":
        from mastapy._private.system_model.analyses_and_results.system_deflections import (
            _3101,
        )

        return self.__parent__._cast(_3101.SpiralBevelGearMeshSystemDeflection)

    @property
    def spring_damper_connection_system_deflection(
        self: "CastSelf",
    ) -> "_3104.SpringDamperConnectionSystemDeflection":
        from mastapy._private.system_model.analyses_and_results.system_deflections import (
            _3104,
        )

        return self.__parent__._cast(_3104.SpringDamperConnectionSystemDeflection)

    @property
    def straight_bevel_diff_gear_mesh_system_deflection(
        self: "CastSelf",
    ) -> "_3107.StraightBevelDiffGearMeshSystemDeflection":
        from mastapy._private.system_model.analyses_and_results.system_deflections import (
            _3107,
        )

        return self.__parent__._cast(_3107.StraightBevelDiffGearMeshSystemDeflection)

    @property
    def straight_bevel_gear_mesh_system_deflection(
        self: "CastSelf",
    ) -> "_3110.StraightBevelGearMeshSystemDeflection":
        from mastapy._private.system_model.analyses_and_results.system_deflections import (
            _3110,
        )

        return self.__parent__._cast(_3110.StraightBevelGearMeshSystemDeflection)

    @property
    def torque_converter_connection_system_deflection(
        self: "CastSelf",
    ) -> "_3122.TorqueConverterConnectionSystemDeflection":
        from mastapy._private.system_model.analyses_and_results.system_deflections import (
            _3122,
        )

        return self.__parent__._cast(_3122.TorqueConverterConnectionSystemDeflection)

    @property
    def worm_gear_mesh_system_deflection(
        self: "CastSelf",
    ) -> "_3131.WormGearMeshSystemDeflection":
        from mastapy._private.system_model.analyses_and_results.system_deflections import (
            _3131,
        )

        return self.__parent__._cast(_3131.WormGearMeshSystemDeflection)

    @property
    def zerol_bevel_gear_mesh_system_deflection(
        self: "CastSelf",
    ) -> "_3134.ZerolBevelGearMeshSystemDeflection":
        from mastapy._private.system_model.analyses_and_results.system_deflections import (
            _3134,
        )

        return self.__parent__._cast(_3134.ZerolBevelGearMeshSystemDeflection)

    @property
    def abstract_shaft_to_mountable_component_connection_dynamic_analysis(
        self: "CastSelf",
    ) -> "_6644.AbstractShaftToMountableComponentConnectionDynamicAnalysis":
        from mastapy._private.system_model.analyses_and_results.dynamic_analyses import (
            _6644,
        )

        return self.__parent__._cast(
            _6644.AbstractShaftToMountableComponentConnectionDynamicAnalysis
        )

    @property
    def agma_gleason_conical_gear_mesh_dynamic_analysis(
        self: "CastSelf",
    ) -> "_6646.AGMAGleasonConicalGearMeshDynamicAnalysis":
        from mastapy._private.system_model.analyses_and_results.dynamic_analyses import (
            _6646,
        )

        return self.__parent__._cast(_6646.AGMAGleasonConicalGearMeshDynamicAnalysis)

    @property
    def belt_connection_dynamic_analysis(
        self: "CastSelf",
    ) -> "_6650.BeltConnectionDynamicAnalysis":
        from mastapy._private.system_model.analyses_and_results.dynamic_analyses import (
            _6650,
        )

        return self.__parent__._cast(_6650.BeltConnectionDynamicAnalysis)

    @property
    def bevel_differential_gear_mesh_dynamic_analysis(
        self: "CastSelf",
    ) -> "_6653.BevelDifferentialGearMeshDynamicAnalysis":
        from mastapy._private.system_model.analyses_and_results.dynamic_analyses import (
            _6653,
        )

        return self.__parent__._cast(_6653.BevelDifferentialGearMeshDynamicAnalysis)

    @property
    def bevel_gear_mesh_dynamic_analysis(
        self: "CastSelf",
    ) -> "_6658.BevelGearMeshDynamicAnalysis":
        from mastapy._private.system_model.analyses_and_results.dynamic_analyses import (
            _6658,
        )

        return self.__parent__._cast(_6658.BevelGearMeshDynamicAnalysis)

    @property
    def clutch_connection_dynamic_analysis(
        self: "CastSelf",
    ) -> "_6662.ClutchConnectionDynamicAnalysis":
        from mastapy._private.system_model.analyses_and_results.dynamic_analyses import (
            _6662,
        )

        return self.__parent__._cast(_6662.ClutchConnectionDynamicAnalysis)

    @property
    def coaxial_connection_dynamic_analysis(
        self: "CastSelf",
    ) -> "_6665.CoaxialConnectionDynamicAnalysis":
        from mastapy._private.system_model.analyses_and_results.dynamic_analyses import (
            _6665,
        )

        return self.__parent__._cast(_6665.CoaxialConnectionDynamicAnalysis)

    @property
    def concept_coupling_connection_dynamic_analysis(
        self: "CastSelf",
    ) -> "_6667.ConceptCouplingConnectionDynamicAnalysis":
        from mastapy._private.system_model.analyses_and_results.dynamic_analyses import (
            _6667,
        )

        return self.__parent__._cast(_6667.ConceptCouplingConnectionDynamicAnalysis)

    @property
    def concept_gear_mesh_dynamic_analysis(
        self: "CastSelf",
    ) -> "_6671.ConceptGearMeshDynamicAnalysis":
        from mastapy._private.system_model.analyses_and_results.dynamic_analyses import (
            _6671,
        )

        return self.__parent__._cast(_6671.ConceptGearMeshDynamicAnalysis)

    @property
    def conical_gear_mesh_dynamic_analysis(
        self: "CastSelf",
    ) -> "_6674.ConicalGearMeshDynamicAnalysis":
        from mastapy._private.system_model.analyses_and_results.dynamic_analyses import (
            _6674,
        )

        return self.__parent__._cast(_6674.ConicalGearMeshDynamicAnalysis)

    @property
    def connection_dynamic_analysis(
        self: "CastSelf",
    ) -> "_6676.ConnectionDynamicAnalysis":
        from mastapy._private.system_model.analyses_and_results.dynamic_analyses import (
            _6676,
        )

        return self.__parent__._cast(_6676.ConnectionDynamicAnalysis)

    @property
    def coupling_connection_dynamic_analysis(
        self: "CastSelf",
    ) -> "_6678.CouplingConnectionDynamicAnalysis":
        from mastapy._private.system_model.analyses_and_results.dynamic_analyses import (
            _6678,
        )

        return self.__parent__._cast(_6678.CouplingConnectionDynamicAnalysis)

    @property
    def cvt_belt_connection_dynamic_analysis(
        self: "CastSelf",
    ) -> "_6681.CVTBeltConnectionDynamicAnalysis":
        from mastapy._private.system_model.analyses_and_results.dynamic_analyses import (
            _6681,
        )

        return self.__parent__._cast(_6681.CVTBeltConnectionDynamicAnalysis)

    @property
    def cycloidal_disc_central_bearing_connection_dynamic_analysis(
        self: "CastSelf",
    ) -> "_6685.CycloidalDiscCentralBearingConnectionDynamicAnalysis":
        from mastapy._private.system_model.analyses_and_results.dynamic_analyses import (
            _6685,
        )

        return self.__parent__._cast(
            _6685.CycloidalDiscCentralBearingConnectionDynamicAnalysis
        )

    @property
    def cycloidal_disc_planetary_bearing_connection_dynamic_analysis(
        self: "CastSelf",
    ) -> "_6687.CycloidalDiscPlanetaryBearingConnectionDynamicAnalysis":
        from mastapy._private.system_model.analyses_and_results.dynamic_analyses import (
            _6687,
        )

        return self.__parent__._cast(
            _6687.CycloidalDiscPlanetaryBearingConnectionDynamicAnalysis
        )

    @property
    def cylindrical_gear_mesh_dynamic_analysis(
        self: "CastSelf",
    ) -> "_6689.CylindricalGearMeshDynamicAnalysis":
        from mastapy._private.system_model.analyses_and_results.dynamic_analyses import (
            _6689,
        )

        return self.__parent__._cast(_6689.CylindricalGearMeshDynamicAnalysis)

    @property
    def face_gear_mesh_dynamic_analysis(
        self: "CastSelf",
    ) -> "_6697.FaceGearMeshDynamicAnalysis":
        from mastapy._private.system_model.analyses_and_results.dynamic_analyses import (
            _6697,
        )

        return self.__parent__._cast(_6697.FaceGearMeshDynamicAnalysis)

    @property
    def gear_mesh_dynamic_analysis(self: "CastSelf") -> "_6702.GearMeshDynamicAnalysis":
        from mastapy._private.system_model.analyses_and_results.dynamic_analyses import (
            _6702,
        )

        return self.__parent__._cast(_6702.GearMeshDynamicAnalysis)

    @property
    def hypoid_gear_mesh_dynamic_analysis(
        self: "CastSelf",
    ) -> "_6706.HypoidGearMeshDynamicAnalysis":
        from mastapy._private.system_model.analyses_and_results.dynamic_analyses import (
            _6706,
        )

        return self.__parent__._cast(_6706.HypoidGearMeshDynamicAnalysis)

    @property
    def inter_mountable_component_connection_dynamic_analysis(
        self: "CastSelf",
    ) -> "_6708.InterMountableComponentConnectionDynamicAnalysis":
        from mastapy._private.system_model.analyses_and_results.dynamic_analyses import (
            _6708,
        )

        return self.__parent__._cast(
            _6708.InterMountableComponentConnectionDynamicAnalysis
        )

    @property
    def klingelnberg_cyclo_palloid_conical_gear_mesh_dynamic_analysis(
        self: "CastSelf",
    ) -> "_6710.KlingelnbergCycloPalloidConicalGearMeshDynamicAnalysis":
        from mastapy._private.system_model.analyses_and_results.dynamic_analyses import (
            _6710,
        )

        return self.__parent__._cast(
            _6710.KlingelnbergCycloPalloidConicalGearMeshDynamicAnalysis
        )

    @property
    def klingelnberg_cyclo_palloid_hypoid_gear_mesh_dynamic_analysis(
        self: "CastSelf",
    ) -> "_6713.KlingelnbergCycloPalloidHypoidGearMeshDynamicAnalysis":
        from mastapy._private.system_model.analyses_and_results.dynamic_analyses import (
            _6713,
        )

        return self.__parent__._cast(
            _6713.KlingelnbergCycloPalloidHypoidGearMeshDynamicAnalysis
        )

    @property
    def klingelnberg_cyclo_palloid_spiral_bevel_gear_mesh_dynamic_analysis(
        self: "CastSelf",
    ) -> "_6716.KlingelnbergCycloPalloidSpiralBevelGearMeshDynamicAnalysis":
        from mastapy._private.system_model.analyses_and_results.dynamic_analyses import (
            _6716,
        )

        return self.__parent__._cast(
            _6716.KlingelnbergCycloPalloidSpiralBevelGearMeshDynamicAnalysis
        )

    @property
    def part_to_part_shear_coupling_connection_dynamic_analysis(
        self: "CastSelf",
    ) -> "_6725.PartToPartShearCouplingConnectionDynamicAnalysis":
        from mastapy._private.system_model.analyses_and_results.dynamic_analyses import (
            _6725,
        )

        return self.__parent__._cast(
            _6725.PartToPartShearCouplingConnectionDynamicAnalysis
        )

    @property
    def planetary_connection_dynamic_analysis(
        self: "CastSelf",
    ) -> "_6728.PlanetaryConnectionDynamicAnalysis":
        from mastapy._private.system_model.analyses_and_results.dynamic_analyses import (
            _6728,
        )

        return self.__parent__._cast(_6728.PlanetaryConnectionDynamicAnalysis)

    @property
    def ring_pins_to_disc_connection_dynamic_analysis(
        self: "CastSelf",
    ) -> "_6735.RingPinsToDiscConnectionDynamicAnalysis":
        from mastapy._private.system_model.analyses_and_results.dynamic_analyses import (
            _6735,
        )

        return self.__parent__._cast(_6735.RingPinsToDiscConnectionDynamicAnalysis)

    @property
    def rolling_ring_connection_dynamic_analysis(
        self: "CastSelf",
    ) -> "_6737.RollingRingConnectionDynamicAnalysis":
        from mastapy._private.system_model.analyses_and_results.dynamic_analyses import (
            _6737,
        )

        return self.__parent__._cast(_6737.RollingRingConnectionDynamicAnalysis)

    @property
    def shaft_to_mountable_component_connection_dynamic_analysis(
        self: "CastSelf",
    ) -> "_6742.ShaftToMountableComponentConnectionDynamicAnalysis":
        from mastapy._private.system_model.analyses_and_results.dynamic_analyses import (
            _6742,
        )

        return self.__parent__._cast(
            _6742.ShaftToMountableComponentConnectionDynamicAnalysis
        )

    @property
    def spiral_bevel_gear_mesh_dynamic_analysis(
        self: "CastSelf",
    ) -> "_6745.SpiralBevelGearMeshDynamicAnalysis":
        from mastapy._private.system_model.analyses_and_results.dynamic_analyses import (
            _6745,
        )

        return self.__parent__._cast(_6745.SpiralBevelGearMeshDynamicAnalysis)

    @property
    def spring_damper_connection_dynamic_analysis(
        self: "CastSelf",
    ) -> "_6747.SpringDamperConnectionDynamicAnalysis":
        from mastapy._private.system_model.analyses_and_results.dynamic_analyses import (
            _6747,
        )

        return self.__parent__._cast(_6747.SpringDamperConnectionDynamicAnalysis)

    @property
    def straight_bevel_diff_gear_mesh_dynamic_analysis(
        self: "CastSelf",
    ) -> "_6751.StraightBevelDiffGearMeshDynamicAnalysis":
        from mastapy._private.system_model.analyses_and_results.dynamic_analyses import (
            _6751,
        )

        return self.__parent__._cast(_6751.StraightBevelDiffGearMeshDynamicAnalysis)

    @property
    def straight_bevel_gear_mesh_dynamic_analysis(
        self: "CastSelf",
    ) -> "_6754.StraightBevelGearMeshDynamicAnalysis":
        from mastapy._private.system_model.analyses_and_results.dynamic_analyses import (
            _6754,
        )

        return self.__parent__._cast(_6754.StraightBevelGearMeshDynamicAnalysis)

    @property
    def torque_converter_connection_dynamic_analysis(
        self: "CastSelf",
    ) -> "_6762.TorqueConverterConnectionDynamicAnalysis":
        from mastapy._private.system_model.analyses_and_results.dynamic_analyses import (
            _6762,
        )

        return self.__parent__._cast(_6762.TorqueConverterConnectionDynamicAnalysis)

    @property
    def worm_gear_mesh_dynamic_analysis(
        self: "CastSelf",
    ) -> "_6769.WormGearMeshDynamicAnalysis":
        from mastapy._private.system_model.analyses_and_results.dynamic_analyses import (
            _6769,
        )

        return self.__parent__._cast(_6769.WormGearMeshDynamicAnalysis)

    @property
    def zerol_bevel_gear_mesh_dynamic_analysis(
        self: "CastSelf",
    ) -> "_6772.ZerolBevelGearMeshDynamicAnalysis":
        from mastapy._private.system_model.analyses_and_results.dynamic_analyses import (
            _6772,
        )

        return self.__parent__._cast(_6772.ZerolBevelGearMeshDynamicAnalysis)

    @property
    def connection_fe_analysis(self: "CastSelf") -> "ConnectionFEAnalysis":
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
class ConnectionFEAnalysis(_7937.ConnectionStaticLoadAnalysisCase):
    """ConnectionFEAnalysis

    This is a mastapy class.
    """

    TYPE: ClassVar["Type"] = _CONNECTION_FE_ANALYSIS

    wrapped: "Any"

    def __post_init__(self: "Self") -> None:
        """Override of the post initialisation magic method."""
        if not hasattr(self.wrapped, "reference_count"):
            self.wrapped.reference_count = 0

        self.wrapped.reference_count += 1

    @property
    def cast_to(self: "Self") -> "_Cast_ConnectionFEAnalysis":
        """Cast to another type.

        Returns:
            _Cast_ConnectionFEAnalysis
        """
        return _Cast_ConnectionFEAnalysis(self)
