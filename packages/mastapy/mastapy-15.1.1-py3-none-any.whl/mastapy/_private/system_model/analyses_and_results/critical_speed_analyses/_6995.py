"""PartCriticalSpeedAnalysis"""

from __future__ import annotations

from typing import TYPE_CHECKING, ClassVar

from mastapy._private._internal.dataclasses import extended_dataclass
from mastapy._private._internal.exception_bridge import exception_bridge
from mastapy._private._internal.exceptions import CastException
from mastapy._private._internal.python_net import (
    python_net_import,
    pythonnet_method_call,
    pythonnet_property_get,
)

from mastapy._private._internal import constructor, utility
from mastapy._private.system_model.analyses_and_results.analysis_cases import _7944

_PART_CRITICAL_SPEED_ANALYSIS = python_net_import(
    "SMT.MastaAPI.SystemModel.AnalysesAndResults.CriticalSpeedAnalyses",
    "PartCriticalSpeedAnalysis",
)

if TYPE_CHECKING:
    from typing import Any, Type, TypeVar

    from mastapy._private.system_model.analyses_and_results import _2943, _2945, _2949
    from mastapy._private.system_model.analyses_and_results.analysis_cases import _7941
    from mastapy._private.system_model.analyses_and_results.critical_speed_analyses import (
        _6911,
        _6912,
        _6913,
        _6915,
        _6917,
        _6918,
        _6919,
        _6921,
        _6922,
        _6924,
        _6925,
        _6926,
        _6927,
        _6929,
        _6930,
        _6931,
        _6933,
        _6934,
        _6936,
        _6938,
        _6939,
        _6940,
        _6942,
        _6943,
        _6945,
        _6947,
        _6949,
        _6950,
        _6951,
        _6955,
        _6956,
        _6957,
        _6959,
        _6961,
        _6963,
        _6964,
        _6965,
        _6966,
        _6967,
        _6969,
        _6970,
        _6971,
        _6972,
        _6974,
        _6975,
        _6976,
        _6978,
        _6980,
        _6982,
        _6983,
        _6985,
        _6986,
        _6988,
        _6989,
        _6990,
        _6991,
        _6992,
        _6993,
        _6994,
        _6997,
        _6998,
        _7000,
        _7001,
        _7002,
        _7003,
        _7004,
        _7005,
        _7007,
        _7009,
        _7010,
        _7011,
        _7012,
        _7014,
        _7015,
        _7017,
        _7019,
        _7020,
        _7021,
        _7023,
        _7024,
        _7026,
        _7027,
        _7028,
        _7029,
        _7030,
        _7031,
        _7032,
        _7034,
        _7035,
        _7036,
        _7037,
        _7038,
        _7039,
        _7041,
        _7042,
        _7044,
    )
    from mastapy._private.system_model.drawing import _2506
    from mastapy._private.system_model.part_model import _2742

    Self = TypeVar("Self", bound="PartCriticalSpeedAnalysis")
    CastSelf = TypeVar(
        "CastSelf", bound="PartCriticalSpeedAnalysis._Cast_PartCriticalSpeedAnalysis"
    )


__docformat__ = "restructuredtext en"
__all__ = ("PartCriticalSpeedAnalysis",)


@extended_dataclass(frozen=True, slots=True, weakref_slot=True)
class _Cast_PartCriticalSpeedAnalysis:
    """Special nested class for casting PartCriticalSpeedAnalysis to subclasses."""

    __parent__: "PartCriticalSpeedAnalysis"

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
    def abstract_assembly_critical_speed_analysis(
        self: "CastSelf",
    ) -> "_6911.AbstractAssemblyCriticalSpeedAnalysis":
        from mastapy._private.system_model.analyses_and_results.critical_speed_analyses import (
            _6911,
        )

        return self.__parent__._cast(_6911.AbstractAssemblyCriticalSpeedAnalysis)

    @property
    def abstract_shaft_critical_speed_analysis(
        self: "CastSelf",
    ) -> "_6912.AbstractShaftCriticalSpeedAnalysis":
        from mastapy._private.system_model.analyses_and_results.critical_speed_analyses import (
            _6912,
        )

        return self.__parent__._cast(_6912.AbstractShaftCriticalSpeedAnalysis)

    @property
    def abstract_shaft_or_housing_critical_speed_analysis(
        self: "CastSelf",
    ) -> "_6913.AbstractShaftOrHousingCriticalSpeedAnalysis":
        from mastapy._private.system_model.analyses_and_results.critical_speed_analyses import (
            _6913,
        )

        return self.__parent__._cast(_6913.AbstractShaftOrHousingCriticalSpeedAnalysis)

    @property
    def agma_gleason_conical_gear_critical_speed_analysis(
        self: "CastSelf",
    ) -> "_6915.AGMAGleasonConicalGearCriticalSpeedAnalysis":
        from mastapy._private.system_model.analyses_and_results.critical_speed_analyses import (
            _6915,
        )

        return self.__parent__._cast(_6915.AGMAGleasonConicalGearCriticalSpeedAnalysis)

    @property
    def agma_gleason_conical_gear_set_critical_speed_analysis(
        self: "CastSelf",
    ) -> "_6917.AGMAGleasonConicalGearSetCriticalSpeedAnalysis":
        from mastapy._private.system_model.analyses_and_results.critical_speed_analyses import (
            _6917,
        )

        return self.__parent__._cast(
            _6917.AGMAGleasonConicalGearSetCriticalSpeedAnalysis
        )

    @property
    def assembly_critical_speed_analysis(
        self: "CastSelf",
    ) -> "_6918.AssemblyCriticalSpeedAnalysis":
        from mastapy._private.system_model.analyses_and_results.critical_speed_analyses import (
            _6918,
        )

        return self.__parent__._cast(_6918.AssemblyCriticalSpeedAnalysis)

    @property
    def bearing_critical_speed_analysis(
        self: "CastSelf",
    ) -> "_6919.BearingCriticalSpeedAnalysis":
        from mastapy._private.system_model.analyses_and_results.critical_speed_analyses import (
            _6919,
        )

        return self.__parent__._cast(_6919.BearingCriticalSpeedAnalysis)

    @property
    def belt_drive_critical_speed_analysis(
        self: "CastSelf",
    ) -> "_6921.BeltDriveCriticalSpeedAnalysis":
        from mastapy._private.system_model.analyses_and_results.critical_speed_analyses import (
            _6921,
        )

        return self.__parent__._cast(_6921.BeltDriveCriticalSpeedAnalysis)

    @property
    def bevel_differential_gear_critical_speed_analysis(
        self: "CastSelf",
    ) -> "_6922.BevelDifferentialGearCriticalSpeedAnalysis":
        from mastapy._private.system_model.analyses_and_results.critical_speed_analyses import (
            _6922,
        )

        return self.__parent__._cast(_6922.BevelDifferentialGearCriticalSpeedAnalysis)

    @property
    def bevel_differential_gear_set_critical_speed_analysis(
        self: "CastSelf",
    ) -> "_6924.BevelDifferentialGearSetCriticalSpeedAnalysis":
        from mastapy._private.system_model.analyses_and_results.critical_speed_analyses import (
            _6924,
        )

        return self.__parent__._cast(
            _6924.BevelDifferentialGearSetCriticalSpeedAnalysis
        )

    @property
    def bevel_differential_planet_gear_critical_speed_analysis(
        self: "CastSelf",
    ) -> "_6925.BevelDifferentialPlanetGearCriticalSpeedAnalysis":
        from mastapy._private.system_model.analyses_and_results.critical_speed_analyses import (
            _6925,
        )

        return self.__parent__._cast(
            _6925.BevelDifferentialPlanetGearCriticalSpeedAnalysis
        )

    @property
    def bevel_differential_sun_gear_critical_speed_analysis(
        self: "CastSelf",
    ) -> "_6926.BevelDifferentialSunGearCriticalSpeedAnalysis":
        from mastapy._private.system_model.analyses_and_results.critical_speed_analyses import (
            _6926,
        )

        return self.__parent__._cast(
            _6926.BevelDifferentialSunGearCriticalSpeedAnalysis
        )

    @property
    def bevel_gear_critical_speed_analysis(
        self: "CastSelf",
    ) -> "_6927.BevelGearCriticalSpeedAnalysis":
        from mastapy._private.system_model.analyses_and_results.critical_speed_analyses import (
            _6927,
        )

        return self.__parent__._cast(_6927.BevelGearCriticalSpeedAnalysis)

    @property
    def bevel_gear_set_critical_speed_analysis(
        self: "CastSelf",
    ) -> "_6929.BevelGearSetCriticalSpeedAnalysis":
        from mastapy._private.system_model.analyses_and_results.critical_speed_analyses import (
            _6929,
        )

        return self.__parent__._cast(_6929.BevelGearSetCriticalSpeedAnalysis)

    @property
    def bolt_critical_speed_analysis(
        self: "CastSelf",
    ) -> "_6930.BoltCriticalSpeedAnalysis":
        from mastapy._private.system_model.analyses_and_results.critical_speed_analyses import (
            _6930,
        )

        return self.__parent__._cast(_6930.BoltCriticalSpeedAnalysis)

    @property
    def bolted_joint_critical_speed_analysis(
        self: "CastSelf",
    ) -> "_6931.BoltedJointCriticalSpeedAnalysis":
        from mastapy._private.system_model.analyses_and_results.critical_speed_analyses import (
            _6931,
        )

        return self.__parent__._cast(_6931.BoltedJointCriticalSpeedAnalysis)

    @property
    def clutch_critical_speed_analysis(
        self: "CastSelf",
    ) -> "_6933.ClutchCriticalSpeedAnalysis":
        from mastapy._private.system_model.analyses_and_results.critical_speed_analyses import (
            _6933,
        )

        return self.__parent__._cast(_6933.ClutchCriticalSpeedAnalysis)

    @property
    def clutch_half_critical_speed_analysis(
        self: "CastSelf",
    ) -> "_6934.ClutchHalfCriticalSpeedAnalysis":
        from mastapy._private.system_model.analyses_and_results.critical_speed_analyses import (
            _6934,
        )

        return self.__parent__._cast(_6934.ClutchHalfCriticalSpeedAnalysis)

    @property
    def component_critical_speed_analysis(
        self: "CastSelf",
    ) -> "_6936.ComponentCriticalSpeedAnalysis":
        from mastapy._private.system_model.analyses_and_results.critical_speed_analyses import (
            _6936,
        )

        return self.__parent__._cast(_6936.ComponentCriticalSpeedAnalysis)

    @property
    def concept_coupling_critical_speed_analysis(
        self: "CastSelf",
    ) -> "_6938.ConceptCouplingCriticalSpeedAnalysis":
        from mastapy._private.system_model.analyses_and_results.critical_speed_analyses import (
            _6938,
        )

        return self.__parent__._cast(_6938.ConceptCouplingCriticalSpeedAnalysis)

    @property
    def concept_coupling_half_critical_speed_analysis(
        self: "CastSelf",
    ) -> "_6939.ConceptCouplingHalfCriticalSpeedAnalysis":
        from mastapy._private.system_model.analyses_and_results.critical_speed_analyses import (
            _6939,
        )

        return self.__parent__._cast(_6939.ConceptCouplingHalfCriticalSpeedAnalysis)

    @property
    def concept_gear_critical_speed_analysis(
        self: "CastSelf",
    ) -> "_6940.ConceptGearCriticalSpeedAnalysis":
        from mastapy._private.system_model.analyses_and_results.critical_speed_analyses import (
            _6940,
        )

        return self.__parent__._cast(_6940.ConceptGearCriticalSpeedAnalysis)

    @property
    def concept_gear_set_critical_speed_analysis(
        self: "CastSelf",
    ) -> "_6942.ConceptGearSetCriticalSpeedAnalysis":
        from mastapy._private.system_model.analyses_and_results.critical_speed_analyses import (
            _6942,
        )

        return self.__parent__._cast(_6942.ConceptGearSetCriticalSpeedAnalysis)

    @property
    def conical_gear_critical_speed_analysis(
        self: "CastSelf",
    ) -> "_6943.ConicalGearCriticalSpeedAnalysis":
        from mastapy._private.system_model.analyses_and_results.critical_speed_analyses import (
            _6943,
        )

        return self.__parent__._cast(_6943.ConicalGearCriticalSpeedAnalysis)

    @property
    def conical_gear_set_critical_speed_analysis(
        self: "CastSelf",
    ) -> "_6945.ConicalGearSetCriticalSpeedAnalysis":
        from mastapy._private.system_model.analyses_and_results.critical_speed_analyses import (
            _6945,
        )

        return self.__parent__._cast(_6945.ConicalGearSetCriticalSpeedAnalysis)

    @property
    def connector_critical_speed_analysis(
        self: "CastSelf",
    ) -> "_6947.ConnectorCriticalSpeedAnalysis":
        from mastapy._private.system_model.analyses_and_results.critical_speed_analyses import (
            _6947,
        )

        return self.__parent__._cast(_6947.ConnectorCriticalSpeedAnalysis)

    @property
    def coupling_critical_speed_analysis(
        self: "CastSelf",
    ) -> "_6949.CouplingCriticalSpeedAnalysis":
        from mastapy._private.system_model.analyses_and_results.critical_speed_analyses import (
            _6949,
        )

        return self.__parent__._cast(_6949.CouplingCriticalSpeedAnalysis)

    @property
    def coupling_half_critical_speed_analysis(
        self: "CastSelf",
    ) -> "_6950.CouplingHalfCriticalSpeedAnalysis":
        from mastapy._private.system_model.analyses_and_results.critical_speed_analyses import (
            _6950,
        )

        return self.__parent__._cast(_6950.CouplingHalfCriticalSpeedAnalysis)

    @property
    def cvt_critical_speed_analysis(
        self: "CastSelf",
    ) -> "_6955.CVTCriticalSpeedAnalysis":
        from mastapy._private.system_model.analyses_and_results.critical_speed_analyses import (
            _6955,
        )

        return self.__parent__._cast(_6955.CVTCriticalSpeedAnalysis)

    @property
    def cvt_pulley_critical_speed_analysis(
        self: "CastSelf",
    ) -> "_6956.CVTPulleyCriticalSpeedAnalysis":
        from mastapy._private.system_model.analyses_and_results.critical_speed_analyses import (
            _6956,
        )

        return self.__parent__._cast(_6956.CVTPulleyCriticalSpeedAnalysis)

    @property
    def cycloidal_assembly_critical_speed_analysis(
        self: "CastSelf",
    ) -> "_6957.CycloidalAssemblyCriticalSpeedAnalysis":
        from mastapy._private.system_model.analyses_and_results.critical_speed_analyses import (
            _6957,
        )

        return self.__parent__._cast(_6957.CycloidalAssemblyCriticalSpeedAnalysis)

    @property
    def cycloidal_disc_critical_speed_analysis(
        self: "CastSelf",
    ) -> "_6959.CycloidalDiscCriticalSpeedAnalysis":
        from mastapy._private.system_model.analyses_and_results.critical_speed_analyses import (
            _6959,
        )

        return self.__parent__._cast(_6959.CycloidalDiscCriticalSpeedAnalysis)

    @property
    def cylindrical_gear_critical_speed_analysis(
        self: "CastSelf",
    ) -> "_6961.CylindricalGearCriticalSpeedAnalysis":
        from mastapy._private.system_model.analyses_and_results.critical_speed_analyses import (
            _6961,
        )

        return self.__parent__._cast(_6961.CylindricalGearCriticalSpeedAnalysis)

    @property
    def cylindrical_gear_set_critical_speed_analysis(
        self: "CastSelf",
    ) -> "_6963.CylindricalGearSetCriticalSpeedAnalysis":
        from mastapy._private.system_model.analyses_and_results.critical_speed_analyses import (
            _6963,
        )

        return self.__parent__._cast(_6963.CylindricalGearSetCriticalSpeedAnalysis)

    @property
    def cylindrical_planet_gear_critical_speed_analysis(
        self: "CastSelf",
    ) -> "_6964.CylindricalPlanetGearCriticalSpeedAnalysis":
        from mastapy._private.system_model.analyses_and_results.critical_speed_analyses import (
            _6964,
        )

        return self.__parent__._cast(_6964.CylindricalPlanetGearCriticalSpeedAnalysis)

    @property
    def datum_critical_speed_analysis(
        self: "CastSelf",
    ) -> "_6965.DatumCriticalSpeedAnalysis":
        from mastapy._private.system_model.analyses_and_results.critical_speed_analyses import (
            _6965,
        )

        return self.__parent__._cast(_6965.DatumCriticalSpeedAnalysis)

    @property
    def external_cad_model_critical_speed_analysis(
        self: "CastSelf",
    ) -> "_6966.ExternalCADModelCriticalSpeedAnalysis":
        from mastapy._private.system_model.analyses_and_results.critical_speed_analyses import (
            _6966,
        )

        return self.__parent__._cast(_6966.ExternalCADModelCriticalSpeedAnalysis)

    @property
    def face_gear_critical_speed_analysis(
        self: "CastSelf",
    ) -> "_6967.FaceGearCriticalSpeedAnalysis":
        from mastapy._private.system_model.analyses_and_results.critical_speed_analyses import (
            _6967,
        )

        return self.__parent__._cast(_6967.FaceGearCriticalSpeedAnalysis)

    @property
    def face_gear_set_critical_speed_analysis(
        self: "CastSelf",
    ) -> "_6969.FaceGearSetCriticalSpeedAnalysis":
        from mastapy._private.system_model.analyses_and_results.critical_speed_analyses import (
            _6969,
        )

        return self.__parent__._cast(_6969.FaceGearSetCriticalSpeedAnalysis)

    @property
    def fe_part_critical_speed_analysis(
        self: "CastSelf",
    ) -> "_6970.FEPartCriticalSpeedAnalysis":
        from mastapy._private.system_model.analyses_and_results.critical_speed_analyses import (
            _6970,
        )

        return self.__parent__._cast(_6970.FEPartCriticalSpeedAnalysis)

    @property
    def flexible_pin_assembly_critical_speed_analysis(
        self: "CastSelf",
    ) -> "_6971.FlexiblePinAssemblyCriticalSpeedAnalysis":
        from mastapy._private.system_model.analyses_and_results.critical_speed_analyses import (
            _6971,
        )

        return self.__parent__._cast(_6971.FlexiblePinAssemblyCriticalSpeedAnalysis)

    @property
    def gear_critical_speed_analysis(
        self: "CastSelf",
    ) -> "_6972.GearCriticalSpeedAnalysis":
        from mastapy._private.system_model.analyses_and_results.critical_speed_analyses import (
            _6972,
        )

        return self.__parent__._cast(_6972.GearCriticalSpeedAnalysis)

    @property
    def gear_set_critical_speed_analysis(
        self: "CastSelf",
    ) -> "_6974.GearSetCriticalSpeedAnalysis":
        from mastapy._private.system_model.analyses_and_results.critical_speed_analyses import (
            _6974,
        )

        return self.__parent__._cast(_6974.GearSetCriticalSpeedAnalysis)

    @property
    def guide_dxf_model_critical_speed_analysis(
        self: "CastSelf",
    ) -> "_6975.GuideDxfModelCriticalSpeedAnalysis":
        from mastapy._private.system_model.analyses_and_results.critical_speed_analyses import (
            _6975,
        )

        return self.__parent__._cast(_6975.GuideDxfModelCriticalSpeedAnalysis)

    @property
    def hypoid_gear_critical_speed_analysis(
        self: "CastSelf",
    ) -> "_6976.HypoidGearCriticalSpeedAnalysis":
        from mastapy._private.system_model.analyses_and_results.critical_speed_analyses import (
            _6976,
        )

        return self.__parent__._cast(_6976.HypoidGearCriticalSpeedAnalysis)

    @property
    def hypoid_gear_set_critical_speed_analysis(
        self: "CastSelf",
    ) -> "_6978.HypoidGearSetCriticalSpeedAnalysis":
        from mastapy._private.system_model.analyses_and_results.critical_speed_analyses import (
            _6978,
        )

        return self.__parent__._cast(_6978.HypoidGearSetCriticalSpeedAnalysis)

    @property
    def klingelnberg_cyclo_palloid_conical_gear_critical_speed_analysis(
        self: "CastSelf",
    ) -> "_6980.KlingelnbergCycloPalloidConicalGearCriticalSpeedAnalysis":
        from mastapy._private.system_model.analyses_and_results.critical_speed_analyses import (
            _6980,
        )

        return self.__parent__._cast(
            _6980.KlingelnbergCycloPalloidConicalGearCriticalSpeedAnalysis
        )

    @property
    def klingelnberg_cyclo_palloid_conical_gear_set_critical_speed_analysis(
        self: "CastSelf",
    ) -> "_6982.KlingelnbergCycloPalloidConicalGearSetCriticalSpeedAnalysis":
        from mastapy._private.system_model.analyses_and_results.critical_speed_analyses import (
            _6982,
        )

        return self.__parent__._cast(
            _6982.KlingelnbergCycloPalloidConicalGearSetCriticalSpeedAnalysis
        )

    @property
    def klingelnberg_cyclo_palloid_hypoid_gear_critical_speed_analysis(
        self: "CastSelf",
    ) -> "_6983.KlingelnbergCycloPalloidHypoidGearCriticalSpeedAnalysis":
        from mastapy._private.system_model.analyses_and_results.critical_speed_analyses import (
            _6983,
        )

        return self.__parent__._cast(
            _6983.KlingelnbergCycloPalloidHypoidGearCriticalSpeedAnalysis
        )

    @property
    def klingelnberg_cyclo_palloid_hypoid_gear_set_critical_speed_analysis(
        self: "CastSelf",
    ) -> "_6985.KlingelnbergCycloPalloidHypoidGearSetCriticalSpeedAnalysis":
        from mastapy._private.system_model.analyses_and_results.critical_speed_analyses import (
            _6985,
        )

        return self.__parent__._cast(
            _6985.KlingelnbergCycloPalloidHypoidGearSetCriticalSpeedAnalysis
        )

    @property
    def klingelnberg_cyclo_palloid_spiral_bevel_gear_critical_speed_analysis(
        self: "CastSelf",
    ) -> "_6986.KlingelnbergCycloPalloidSpiralBevelGearCriticalSpeedAnalysis":
        from mastapy._private.system_model.analyses_and_results.critical_speed_analyses import (
            _6986,
        )

        return self.__parent__._cast(
            _6986.KlingelnbergCycloPalloidSpiralBevelGearCriticalSpeedAnalysis
        )

    @property
    def klingelnberg_cyclo_palloid_spiral_bevel_gear_set_critical_speed_analysis(
        self: "CastSelf",
    ) -> "_6988.KlingelnbergCycloPalloidSpiralBevelGearSetCriticalSpeedAnalysis":
        from mastapy._private.system_model.analyses_and_results.critical_speed_analyses import (
            _6988,
        )

        return self.__parent__._cast(
            _6988.KlingelnbergCycloPalloidSpiralBevelGearSetCriticalSpeedAnalysis
        )

    @property
    def mass_disc_critical_speed_analysis(
        self: "CastSelf",
    ) -> "_6989.MassDiscCriticalSpeedAnalysis":
        from mastapy._private.system_model.analyses_and_results.critical_speed_analyses import (
            _6989,
        )

        return self.__parent__._cast(_6989.MassDiscCriticalSpeedAnalysis)

    @property
    def measurement_component_critical_speed_analysis(
        self: "CastSelf",
    ) -> "_6990.MeasurementComponentCriticalSpeedAnalysis":
        from mastapy._private.system_model.analyses_and_results.critical_speed_analyses import (
            _6990,
        )

        return self.__parent__._cast(_6990.MeasurementComponentCriticalSpeedAnalysis)

    @property
    def microphone_array_critical_speed_analysis(
        self: "CastSelf",
    ) -> "_6991.MicrophoneArrayCriticalSpeedAnalysis":
        from mastapy._private.system_model.analyses_and_results.critical_speed_analyses import (
            _6991,
        )

        return self.__parent__._cast(_6991.MicrophoneArrayCriticalSpeedAnalysis)

    @property
    def microphone_critical_speed_analysis(
        self: "CastSelf",
    ) -> "_6992.MicrophoneCriticalSpeedAnalysis":
        from mastapy._private.system_model.analyses_and_results.critical_speed_analyses import (
            _6992,
        )

        return self.__parent__._cast(_6992.MicrophoneCriticalSpeedAnalysis)

    @property
    def mountable_component_critical_speed_analysis(
        self: "CastSelf",
    ) -> "_6993.MountableComponentCriticalSpeedAnalysis":
        from mastapy._private.system_model.analyses_and_results.critical_speed_analyses import (
            _6993,
        )

        return self.__parent__._cast(_6993.MountableComponentCriticalSpeedAnalysis)

    @property
    def oil_seal_critical_speed_analysis(
        self: "CastSelf",
    ) -> "_6994.OilSealCriticalSpeedAnalysis":
        from mastapy._private.system_model.analyses_and_results.critical_speed_analyses import (
            _6994,
        )

        return self.__parent__._cast(_6994.OilSealCriticalSpeedAnalysis)

    @property
    def part_to_part_shear_coupling_critical_speed_analysis(
        self: "CastSelf",
    ) -> "_6997.PartToPartShearCouplingCriticalSpeedAnalysis":
        from mastapy._private.system_model.analyses_and_results.critical_speed_analyses import (
            _6997,
        )

        return self.__parent__._cast(_6997.PartToPartShearCouplingCriticalSpeedAnalysis)

    @property
    def part_to_part_shear_coupling_half_critical_speed_analysis(
        self: "CastSelf",
    ) -> "_6998.PartToPartShearCouplingHalfCriticalSpeedAnalysis":
        from mastapy._private.system_model.analyses_and_results.critical_speed_analyses import (
            _6998,
        )

        return self.__parent__._cast(
            _6998.PartToPartShearCouplingHalfCriticalSpeedAnalysis
        )

    @property
    def planetary_gear_set_critical_speed_analysis(
        self: "CastSelf",
    ) -> "_7000.PlanetaryGearSetCriticalSpeedAnalysis":
        from mastapy._private.system_model.analyses_and_results.critical_speed_analyses import (
            _7000,
        )

        return self.__parent__._cast(_7000.PlanetaryGearSetCriticalSpeedAnalysis)

    @property
    def planet_carrier_critical_speed_analysis(
        self: "CastSelf",
    ) -> "_7001.PlanetCarrierCriticalSpeedAnalysis":
        from mastapy._private.system_model.analyses_and_results.critical_speed_analyses import (
            _7001,
        )

        return self.__parent__._cast(_7001.PlanetCarrierCriticalSpeedAnalysis)

    @property
    def point_load_critical_speed_analysis(
        self: "CastSelf",
    ) -> "_7002.PointLoadCriticalSpeedAnalysis":
        from mastapy._private.system_model.analyses_and_results.critical_speed_analyses import (
            _7002,
        )

        return self.__parent__._cast(_7002.PointLoadCriticalSpeedAnalysis)

    @property
    def power_load_critical_speed_analysis(
        self: "CastSelf",
    ) -> "_7003.PowerLoadCriticalSpeedAnalysis":
        from mastapy._private.system_model.analyses_and_results.critical_speed_analyses import (
            _7003,
        )

        return self.__parent__._cast(_7003.PowerLoadCriticalSpeedAnalysis)

    @property
    def pulley_critical_speed_analysis(
        self: "CastSelf",
    ) -> "_7004.PulleyCriticalSpeedAnalysis":
        from mastapy._private.system_model.analyses_and_results.critical_speed_analyses import (
            _7004,
        )

        return self.__parent__._cast(_7004.PulleyCriticalSpeedAnalysis)

    @property
    def ring_pins_critical_speed_analysis(
        self: "CastSelf",
    ) -> "_7005.RingPinsCriticalSpeedAnalysis":
        from mastapy._private.system_model.analyses_and_results.critical_speed_analyses import (
            _7005,
        )

        return self.__parent__._cast(_7005.RingPinsCriticalSpeedAnalysis)

    @property
    def rolling_ring_assembly_critical_speed_analysis(
        self: "CastSelf",
    ) -> "_7007.RollingRingAssemblyCriticalSpeedAnalysis":
        from mastapy._private.system_model.analyses_and_results.critical_speed_analyses import (
            _7007,
        )

        return self.__parent__._cast(_7007.RollingRingAssemblyCriticalSpeedAnalysis)

    @property
    def rolling_ring_critical_speed_analysis(
        self: "CastSelf",
    ) -> "_7009.RollingRingCriticalSpeedAnalysis":
        from mastapy._private.system_model.analyses_and_results.critical_speed_analyses import (
            _7009,
        )

        return self.__parent__._cast(_7009.RollingRingCriticalSpeedAnalysis)

    @property
    def root_assembly_critical_speed_analysis(
        self: "CastSelf",
    ) -> "_7010.RootAssemblyCriticalSpeedAnalysis":
        from mastapy._private.system_model.analyses_and_results.critical_speed_analyses import (
            _7010,
        )

        return self.__parent__._cast(_7010.RootAssemblyCriticalSpeedAnalysis)

    @property
    def shaft_critical_speed_analysis(
        self: "CastSelf",
    ) -> "_7011.ShaftCriticalSpeedAnalysis":
        from mastapy._private.system_model.analyses_and_results.critical_speed_analyses import (
            _7011,
        )

        return self.__parent__._cast(_7011.ShaftCriticalSpeedAnalysis)

    @property
    def shaft_hub_connection_critical_speed_analysis(
        self: "CastSelf",
    ) -> "_7012.ShaftHubConnectionCriticalSpeedAnalysis":
        from mastapy._private.system_model.analyses_and_results.critical_speed_analyses import (
            _7012,
        )

        return self.__parent__._cast(_7012.ShaftHubConnectionCriticalSpeedAnalysis)

    @property
    def specialised_assembly_critical_speed_analysis(
        self: "CastSelf",
    ) -> "_7014.SpecialisedAssemblyCriticalSpeedAnalysis":
        from mastapy._private.system_model.analyses_and_results.critical_speed_analyses import (
            _7014,
        )

        return self.__parent__._cast(_7014.SpecialisedAssemblyCriticalSpeedAnalysis)

    @property
    def spiral_bevel_gear_critical_speed_analysis(
        self: "CastSelf",
    ) -> "_7015.SpiralBevelGearCriticalSpeedAnalysis":
        from mastapy._private.system_model.analyses_and_results.critical_speed_analyses import (
            _7015,
        )

        return self.__parent__._cast(_7015.SpiralBevelGearCriticalSpeedAnalysis)

    @property
    def spiral_bevel_gear_set_critical_speed_analysis(
        self: "CastSelf",
    ) -> "_7017.SpiralBevelGearSetCriticalSpeedAnalysis":
        from mastapy._private.system_model.analyses_and_results.critical_speed_analyses import (
            _7017,
        )

        return self.__parent__._cast(_7017.SpiralBevelGearSetCriticalSpeedAnalysis)

    @property
    def spring_damper_critical_speed_analysis(
        self: "CastSelf",
    ) -> "_7019.SpringDamperCriticalSpeedAnalysis":
        from mastapy._private.system_model.analyses_and_results.critical_speed_analyses import (
            _7019,
        )

        return self.__parent__._cast(_7019.SpringDamperCriticalSpeedAnalysis)

    @property
    def spring_damper_half_critical_speed_analysis(
        self: "CastSelf",
    ) -> "_7020.SpringDamperHalfCriticalSpeedAnalysis":
        from mastapy._private.system_model.analyses_and_results.critical_speed_analyses import (
            _7020,
        )

        return self.__parent__._cast(_7020.SpringDamperHalfCriticalSpeedAnalysis)

    @property
    def straight_bevel_diff_gear_critical_speed_analysis(
        self: "CastSelf",
    ) -> "_7021.StraightBevelDiffGearCriticalSpeedAnalysis":
        from mastapy._private.system_model.analyses_and_results.critical_speed_analyses import (
            _7021,
        )

        return self.__parent__._cast(_7021.StraightBevelDiffGearCriticalSpeedAnalysis)

    @property
    def straight_bevel_diff_gear_set_critical_speed_analysis(
        self: "CastSelf",
    ) -> "_7023.StraightBevelDiffGearSetCriticalSpeedAnalysis":
        from mastapy._private.system_model.analyses_and_results.critical_speed_analyses import (
            _7023,
        )

        return self.__parent__._cast(
            _7023.StraightBevelDiffGearSetCriticalSpeedAnalysis
        )

    @property
    def straight_bevel_gear_critical_speed_analysis(
        self: "CastSelf",
    ) -> "_7024.StraightBevelGearCriticalSpeedAnalysis":
        from mastapy._private.system_model.analyses_and_results.critical_speed_analyses import (
            _7024,
        )

        return self.__parent__._cast(_7024.StraightBevelGearCriticalSpeedAnalysis)

    @property
    def straight_bevel_gear_set_critical_speed_analysis(
        self: "CastSelf",
    ) -> "_7026.StraightBevelGearSetCriticalSpeedAnalysis":
        from mastapy._private.system_model.analyses_and_results.critical_speed_analyses import (
            _7026,
        )

        return self.__parent__._cast(_7026.StraightBevelGearSetCriticalSpeedAnalysis)

    @property
    def straight_bevel_planet_gear_critical_speed_analysis(
        self: "CastSelf",
    ) -> "_7027.StraightBevelPlanetGearCriticalSpeedAnalysis":
        from mastapy._private.system_model.analyses_and_results.critical_speed_analyses import (
            _7027,
        )

        return self.__parent__._cast(_7027.StraightBevelPlanetGearCriticalSpeedAnalysis)

    @property
    def straight_bevel_sun_gear_critical_speed_analysis(
        self: "CastSelf",
    ) -> "_7028.StraightBevelSunGearCriticalSpeedAnalysis":
        from mastapy._private.system_model.analyses_and_results.critical_speed_analyses import (
            _7028,
        )

        return self.__parent__._cast(_7028.StraightBevelSunGearCriticalSpeedAnalysis)

    @property
    def synchroniser_critical_speed_analysis(
        self: "CastSelf",
    ) -> "_7029.SynchroniserCriticalSpeedAnalysis":
        from mastapy._private.system_model.analyses_and_results.critical_speed_analyses import (
            _7029,
        )

        return self.__parent__._cast(_7029.SynchroniserCriticalSpeedAnalysis)

    @property
    def synchroniser_half_critical_speed_analysis(
        self: "CastSelf",
    ) -> "_7030.SynchroniserHalfCriticalSpeedAnalysis":
        from mastapy._private.system_model.analyses_and_results.critical_speed_analyses import (
            _7030,
        )

        return self.__parent__._cast(_7030.SynchroniserHalfCriticalSpeedAnalysis)

    @property
    def synchroniser_part_critical_speed_analysis(
        self: "CastSelf",
    ) -> "_7031.SynchroniserPartCriticalSpeedAnalysis":
        from mastapy._private.system_model.analyses_and_results.critical_speed_analyses import (
            _7031,
        )

        return self.__parent__._cast(_7031.SynchroniserPartCriticalSpeedAnalysis)

    @property
    def synchroniser_sleeve_critical_speed_analysis(
        self: "CastSelf",
    ) -> "_7032.SynchroniserSleeveCriticalSpeedAnalysis":
        from mastapy._private.system_model.analyses_and_results.critical_speed_analyses import (
            _7032,
        )

        return self.__parent__._cast(_7032.SynchroniserSleeveCriticalSpeedAnalysis)

    @property
    def torque_converter_critical_speed_analysis(
        self: "CastSelf",
    ) -> "_7034.TorqueConverterCriticalSpeedAnalysis":
        from mastapy._private.system_model.analyses_and_results.critical_speed_analyses import (
            _7034,
        )

        return self.__parent__._cast(_7034.TorqueConverterCriticalSpeedAnalysis)

    @property
    def torque_converter_pump_critical_speed_analysis(
        self: "CastSelf",
    ) -> "_7035.TorqueConverterPumpCriticalSpeedAnalysis":
        from mastapy._private.system_model.analyses_and_results.critical_speed_analyses import (
            _7035,
        )

        return self.__parent__._cast(_7035.TorqueConverterPumpCriticalSpeedAnalysis)

    @property
    def torque_converter_turbine_critical_speed_analysis(
        self: "CastSelf",
    ) -> "_7036.TorqueConverterTurbineCriticalSpeedAnalysis":
        from mastapy._private.system_model.analyses_and_results.critical_speed_analyses import (
            _7036,
        )

        return self.__parent__._cast(_7036.TorqueConverterTurbineCriticalSpeedAnalysis)

    @property
    def unbalanced_mass_critical_speed_analysis(
        self: "CastSelf",
    ) -> "_7037.UnbalancedMassCriticalSpeedAnalysis":
        from mastapy._private.system_model.analyses_and_results.critical_speed_analyses import (
            _7037,
        )

        return self.__parent__._cast(_7037.UnbalancedMassCriticalSpeedAnalysis)

    @property
    def virtual_component_critical_speed_analysis(
        self: "CastSelf",
    ) -> "_7038.VirtualComponentCriticalSpeedAnalysis":
        from mastapy._private.system_model.analyses_and_results.critical_speed_analyses import (
            _7038,
        )

        return self.__parent__._cast(_7038.VirtualComponentCriticalSpeedAnalysis)

    @property
    def worm_gear_critical_speed_analysis(
        self: "CastSelf",
    ) -> "_7039.WormGearCriticalSpeedAnalysis":
        from mastapy._private.system_model.analyses_and_results.critical_speed_analyses import (
            _7039,
        )

        return self.__parent__._cast(_7039.WormGearCriticalSpeedAnalysis)

    @property
    def worm_gear_set_critical_speed_analysis(
        self: "CastSelf",
    ) -> "_7041.WormGearSetCriticalSpeedAnalysis":
        from mastapy._private.system_model.analyses_and_results.critical_speed_analyses import (
            _7041,
        )

        return self.__parent__._cast(_7041.WormGearSetCriticalSpeedAnalysis)

    @property
    def zerol_bevel_gear_critical_speed_analysis(
        self: "CastSelf",
    ) -> "_7042.ZerolBevelGearCriticalSpeedAnalysis":
        from mastapy._private.system_model.analyses_and_results.critical_speed_analyses import (
            _7042,
        )

        return self.__parent__._cast(_7042.ZerolBevelGearCriticalSpeedAnalysis)

    @property
    def zerol_bevel_gear_set_critical_speed_analysis(
        self: "CastSelf",
    ) -> "_7044.ZerolBevelGearSetCriticalSpeedAnalysis":
        from mastapy._private.system_model.analyses_and_results.critical_speed_analyses import (
            _7044,
        )

        return self.__parent__._cast(_7044.ZerolBevelGearSetCriticalSpeedAnalysis)

    @property
    def part_critical_speed_analysis(self: "CastSelf") -> "PartCriticalSpeedAnalysis":
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
class PartCriticalSpeedAnalysis(_7944.PartStaticLoadAnalysisCase):
    """PartCriticalSpeedAnalysis

    This is a mastapy class.
    """

    TYPE: ClassVar["Type"] = _PART_CRITICAL_SPEED_ANALYSIS

    wrapped: "Any"

    def __post_init__(self: "Self") -> None:
        """Override of the post initialisation magic method."""
        if not hasattr(self.wrapped, "reference_count"):
            self.wrapped.reference_count = 0

        self.wrapped.reference_count += 1

    @property
    @exception_bridge
    def component_design(self: "Self") -> "_2742.Part":
        """mastapy.system_model.part_model.Part

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "ComponentDesign")

        if temp is None:
            return None

        type_ = temp.GetType()
        return constructor.new(type_.Namespace, type_.Name)(temp)

    @property
    @exception_bridge
    def critical_speed_analysis(self: "Self") -> "_6951.CriticalSpeedAnalysis":
        """mastapy.system_model.analyses_and_results.critical_speed_analyses.CriticalSpeedAnalysis

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "CriticalSpeedAnalysis")

        if temp is None:
            return None

        type_ = temp.GetType()
        return constructor.new(type_.Namespace, type_.Name)(temp)

    @exception_bridge
    def create_viewable(self: "Self") -> "_2506.CriticalSpeedAnalysisViewable":
        """mastapy.system_model.drawing.CriticalSpeedAnalysisViewable"""
        method_result = pythonnet_method_call(self.wrapped, "CreateViewable")
        type_ = method_result.GetType()
        return (
            constructor.new(type_.Namespace, type_.Name)(method_result)
            if method_result is not None
            else None
        )

    @property
    def cast_to(self: "Self") -> "_Cast_PartCriticalSpeedAnalysis":
        """Cast to another type.

        Returns:
            _Cast_PartCriticalSpeedAnalysis
        """
        return _Cast_PartCriticalSpeedAnalysis(self)
