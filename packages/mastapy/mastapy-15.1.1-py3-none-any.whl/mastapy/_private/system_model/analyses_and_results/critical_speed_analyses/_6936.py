"""ComponentCriticalSpeedAnalysis"""

from __future__ import annotations

from typing import TYPE_CHECKING, ClassVar

from mastapy._private._internal.dataclasses import extended_dataclass
from mastapy._private._internal.exception_bridge import exception_bridge
from mastapy._private._internal.exceptions import CastException
from mastapy._private._internal.python_net import (
    python_net_import,
    pythonnet_property_get,
)

from mastapy._private._internal import constructor, utility
from mastapy._private.system_model.analyses_and_results.critical_speed_analyses import (
    _6995,
)

_COMPONENT_CRITICAL_SPEED_ANALYSIS = python_net_import(
    "SMT.MastaAPI.SystemModel.AnalysesAndResults.CriticalSpeedAnalyses",
    "ComponentCriticalSpeedAnalysis",
)

if TYPE_CHECKING:
    from typing import Any, Type, TypeVar

    from mastapy._private.system_model.analyses_and_results import _2943, _2945, _2949
    from mastapy._private.system_model.analyses_and_results.analysis_cases import (
        _7941,
        _7944,
    )
    from mastapy._private.system_model.analyses_and_results.critical_speed_analyses import (
        _6912,
        _6913,
        _6915,
        _6919,
        _6922,
        _6925,
        _6926,
        _6927,
        _6930,
        _6934,
        _6939,
        _6940,
        _6943,
        _6947,
        _6950,
        _6956,
        _6959,
        _6961,
        _6964,
        _6965,
        _6966,
        _6967,
        _6970,
        _6972,
        _6975,
        _6976,
        _6980,
        _6983,
        _6986,
        _6989,
        _6990,
        _6992,
        _6993,
        _6994,
        _6998,
        _7001,
        _7002,
        _7003,
        _7004,
        _7005,
        _7009,
        _7011,
        _7012,
        _7015,
        _7020,
        _7021,
        _7024,
        _7027,
        _7028,
        _7030,
        _7031,
        _7032,
        _7035,
        _7036,
        _7037,
        _7038,
        _7039,
        _7042,
    )
    from mastapy._private.system_model.part_model import _2714

    Self = TypeVar("Self", bound="ComponentCriticalSpeedAnalysis")
    CastSelf = TypeVar(
        "CastSelf",
        bound="ComponentCriticalSpeedAnalysis._Cast_ComponentCriticalSpeedAnalysis",
    )


__docformat__ = "restructuredtext en"
__all__ = ("ComponentCriticalSpeedAnalysis",)


@extended_dataclass(frozen=True, slots=True, weakref_slot=True)
class _Cast_ComponentCriticalSpeedAnalysis:
    """Special nested class for casting ComponentCriticalSpeedAnalysis to subclasses."""

    __parent__: "ComponentCriticalSpeedAnalysis"

    @property
    def part_critical_speed_analysis(
        self: "CastSelf",
    ) -> "_6995.PartCriticalSpeedAnalysis":
        return self.__parent__._cast(_6995.PartCriticalSpeedAnalysis)

    @property
    def part_static_load_analysis_case(
        self: "CastSelf",
    ) -> "_7944.PartStaticLoadAnalysisCase":
        from mastapy._private.system_model.analyses_and_results.analysis_cases import (
            _7944,
        )

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
    def bearing_critical_speed_analysis(
        self: "CastSelf",
    ) -> "_6919.BearingCriticalSpeedAnalysis":
        from mastapy._private.system_model.analyses_and_results.critical_speed_analyses import (
            _6919,
        )

        return self.__parent__._cast(_6919.BearingCriticalSpeedAnalysis)

    @property
    def bevel_differential_gear_critical_speed_analysis(
        self: "CastSelf",
    ) -> "_6922.BevelDifferentialGearCriticalSpeedAnalysis":
        from mastapy._private.system_model.analyses_and_results.critical_speed_analyses import (
            _6922,
        )

        return self.__parent__._cast(_6922.BevelDifferentialGearCriticalSpeedAnalysis)

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
    def bolt_critical_speed_analysis(
        self: "CastSelf",
    ) -> "_6930.BoltCriticalSpeedAnalysis":
        from mastapy._private.system_model.analyses_and_results.critical_speed_analyses import (
            _6930,
        )

        return self.__parent__._cast(_6930.BoltCriticalSpeedAnalysis)

    @property
    def clutch_half_critical_speed_analysis(
        self: "CastSelf",
    ) -> "_6934.ClutchHalfCriticalSpeedAnalysis":
        from mastapy._private.system_model.analyses_and_results.critical_speed_analyses import (
            _6934,
        )

        return self.__parent__._cast(_6934.ClutchHalfCriticalSpeedAnalysis)

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
    def conical_gear_critical_speed_analysis(
        self: "CastSelf",
    ) -> "_6943.ConicalGearCriticalSpeedAnalysis":
        from mastapy._private.system_model.analyses_and_results.critical_speed_analyses import (
            _6943,
        )

        return self.__parent__._cast(_6943.ConicalGearCriticalSpeedAnalysis)

    @property
    def connector_critical_speed_analysis(
        self: "CastSelf",
    ) -> "_6947.ConnectorCriticalSpeedAnalysis":
        from mastapy._private.system_model.analyses_and_results.critical_speed_analyses import (
            _6947,
        )

        return self.__parent__._cast(_6947.ConnectorCriticalSpeedAnalysis)

    @property
    def coupling_half_critical_speed_analysis(
        self: "CastSelf",
    ) -> "_6950.CouplingHalfCriticalSpeedAnalysis":
        from mastapy._private.system_model.analyses_and_results.critical_speed_analyses import (
            _6950,
        )

        return self.__parent__._cast(_6950.CouplingHalfCriticalSpeedAnalysis)

    @property
    def cvt_pulley_critical_speed_analysis(
        self: "CastSelf",
    ) -> "_6956.CVTPulleyCriticalSpeedAnalysis":
        from mastapy._private.system_model.analyses_and_results.critical_speed_analyses import (
            _6956,
        )

        return self.__parent__._cast(_6956.CVTPulleyCriticalSpeedAnalysis)

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
    def fe_part_critical_speed_analysis(
        self: "CastSelf",
    ) -> "_6970.FEPartCriticalSpeedAnalysis":
        from mastapy._private.system_model.analyses_and_results.critical_speed_analyses import (
            _6970,
        )

        return self.__parent__._cast(_6970.FEPartCriticalSpeedAnalysis)

    @property
    def gear_critical_speed_analysis(
        self: "CastSelf",
    ) -> "_6972.GearCriticalSpeedAnalysis":
        from mastapy._private.system_model.analyses_and_results.critical_speed_analyses import (
            _6972,
        )

        return self.__parent__._cast(_6972.GearCriticalSpeedAnalysis)

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
    def rolling_ring_critical_speed_analysis(
        self: "CastSelf",
    ) -> "_7009.RollingRingCriticalSpeedAnalysis":
        from mastapy._private.system_model.analyses_and_results.critical_speed_analyses import (
            _7009,
        )

        return self.__parent__._cast(_7009.RollingRingCriticalSpeedAnalysis)

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
    def spiral_bevel_gear_critical_speed_analysis(
        self: "CastSelf",
    ) -> "_7015.SpiralBevelGearCriticalSpeedAnalysis":
        from mastapy._private.system_model.analyses_and_results.critical_speed_analyses import (
            _7015,
        )

        return self.__parent__._cast(_7015.SpiralBevelGearCriticalSpeedAnalysis)

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
    def straight_bevel_gear_critical_speed_analysis(
        self: "CastSelf",
    ) -> "_7024.StraightBevelGearCriticalSpeedAnalysis":
        from mastapy._private.system_model.analyses_and_results.critical_speed_analyses import (
            _7024,
        )

        return self.__parent__._cast(_7024.StraightBevelGearCriticalSpeedAnalysis)

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
    def zerol_bevel_gear_critical_speed_analysis(
        self: "CastSelf",
    ) -> "_7042.ZerolBevelGearCriticalSpeedAnalysis":
        from mastapy._private.system_model.analyses_and_results.critical_speed_analyses import (
            _7042,
        )

        return self.__parent__._cast(_7042.ZerolBevelGearCriticalSpeedAnalysis)

    @property
    def component_critical_speed_analysis(
        self: "CastSelf",
    ) -> "ComponentCriticalSpeedAnalysis":
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
class ComponentCriticalSpeedAnalysis(_6995.PartCriticalSpeedAnalysis):
    """ComponentCriticalSpeedAnalysis

    This is a mastapy class.
    """

    TYPE: ClassVar["Type"] = _COMPONENT_CRITICAL_SPEED_ANALYSIS

    wrapped: "Any"

    def __post_init__(self: "Self") -> None:
        """Override of the post initialisation magic method."""
        if not hasattr(self.wrapped, "reference_count"):
            self.wrapped.reference_count = 0

        self.wrapped.reference_count += 1

    @property
    @exception_bridge
    def component_design(self: "Self") -> "_2714.Component":
        """mastapy.system_model.part_model.Component

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "ComponentDesign")

        if temp is None:
            return None

        type_ = temp.GetType()
        return constructor.new(type_.Namespace, type_.Name)(temp)

    @property
    def cast_to(self: "Self") -> "_Cast_ComponentCriticalSpeedAnalysis":
        """Cast to another type.

        Returns:
            _Cast_ComponentCriticalSpeedAnalysis
        """
        return _Cast_ComponentCriticalSpeedAnalysis(self)
