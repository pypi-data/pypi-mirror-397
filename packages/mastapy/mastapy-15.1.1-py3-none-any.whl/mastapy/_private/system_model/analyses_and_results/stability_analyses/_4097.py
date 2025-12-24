"""ComponentStabilityAnalysis"""

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
from mastapy._private.system_model.analyses_and_results.stability_analyses import _4155

_COMPONENT_STABILITY_ANALYSIS = python_net_import(
    "SMT.MastaAPI.SystemModel.AnalysesAndResults.StabilityAnalyses",
    "ComponentStabilityAnalysis",
)

if TYPE_CHECKING:
    from typing import Any, Type, TypeVar

    from mastapy._private.system_model.analyses_and_results import _2943, _2945, _2949
    from mastapy._private.system_model.analyses_and_results.analysis_cases import (
        _7941,
        _7944,
    )
    from mastapy._private.system_model.analyses_and_results.stability_analyses import (
        _4073,
        _4074,
        _4078,
        _4080,
        _4085,
        _4086,
        _4087,
        _4090,
        _4092,
        _4094,
        _4099,
        _4103,
        _4106,
        _4108,
        _4110,
        _4114,
        _4119,
        _4122,
        _4123,
        _4124,
        _4126,
        _4129,
        _4130,
        _4134,
        _4135,
        _4138,
        _4142,
        _4145,
        _4148,
        _4149,
        _4150,
        _4152,
        _4153,
        _4154,
        _4157,
        _4161,
        _4162,
        _4163,
        _4164,
        _4165,
        _4169,
        _4171,
        _4172,
        _4177,
        _4179,
        _4186,
        _4189,
        _4190,
        _4191,
        _4192,
        _4193,
        _4194,
        _4197,
        _4199,
        _4200,
        _4201,
        _4204,
        _4207,
    )
    from mastapy._private.system_model.part_model import _2714

    Self = TypeVar("Self", bound="ComponentStabilityAnalysis")
    CastSelf = TypeVar(
        "CastSelf", bound="ComponentStabilityAnalysis._Cast_ComponentStabilityAnalysis"
    )


__docformat__ = "restructuredtext en"
__all__ = ("ComponentStabilityAnalysis",)


@extended_dataclass(frozen=True, slots=True, weakref_slot=True)
class _Cast_ComponentStabilityAnalysis:
    """Special nested class for casting ComponentStabilityAnalysis to subclasses."""

    __parent__: "ComponentStabilityAnalysis"

    @property
    def part_stability_analysis(self: "CastSelf") -> "_4155.PartStabilityAnalysis":
        return self.__parent__._cast(_4155.PartStabilityAnalysis)

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
    def abstract_shaft_or_housing_stability_analysis(
        self: "CastSelf",
    ) -> "_4073.AbstractShaftOrHousingStabilityAnalysis":
        from mastapy._private.system_model.analyses_and_results.stability_analyses import (
            _4073,
        )

        return self.__parent__._cast(_4073.AbstractShaftOrHousingStabilityAnalysis)

    @property
    def abstract_shaft_stability_analysis(
        self: "CastSelf",
    ) -> "_4074.AbstractShaftStabilityAnalysis":
        from mastapy._private.system_model.analyses_and_results.stability_analyses import (
            _4074,
        )

        return self.__parent__._cast(_4074.AbstractShaftStabilityAnalysis)

    @property
    def agma_gleason_conical_gear_stability_analysis(
        self: "CastSelf",
    ) -> "_4078.AGMAGleasonConicalGearStabilityAnalysis":
        from mastapy._private.system_model.analyses_and_results.stability_analyses import (
            _4078,
        )

        return self.__parent__._cast(_4078.AGMAGleasonConicalGearStabilityAnalysis)

    @property
    def bearing_stability_analysis(
        self: "CastSelf",
    ) -> "_4080.BearingStabilityAnalysis":
        from mastapy._private.system_model.analyses_and_results.stability_analyses import (
            _4080,
        )

        return self.__parent__._cast(_4080.BearingStabilityAnalysis)

    @property
    def bevel_differential_gear_stability_analysis(
        self: "CastSelf",
    ) -> "_4085.BevelDifferentialGearStabilityAnalysis":
        from mastapy._private.system_model.analyses_and_results.stability_analyses import (
            _4085,
        )

        return self.__parent__._cast(_4085.BevelDifferentialGearStabilityAnalysis)

    @property
    def bevel_differential_planet_gear_stability_analysis(
        self: "CastSelf",
    ) -> "_4086.BevelDifferentialPlanetGearStabilityAnalysis":
        from mastapy._private.system_model.analyses_and_results.stability_analyses import (
            _4086,
        )

        return self.__parent__._cast(_4086.BevelDifferentialPlanetGearStabilityAnalysis)

    @property
    def bevel_differential_sun_gear_stability_analysis(
        self: "CastSelf",
    ) -> "_4087.BevelDifferentialSunGearStabilityAnalysis":
        from mastapy._private.system_model.analyses_and_results.stability_analyses import (
            _4087,
        )

        return self.__parent__._cast(_4087.BevelDifferentialSunGearStabilityAnalysis)

    @property
    def bevel_gear_stability_analysis(
        self: "CastSelf",
    ) -> "_4090.BevelGearStabilityAnalysis":
        from mastapy._private.system_model.analyses_and_results.stability_analyses import (
            _4090,
        )

        return self.__parent__._cast(_4090.BevelGearStabilityAnalysis)

    @property
    def bolt_stability_analysis(self: "CastSelf") -> "_4092.BoltStabilityAnalysis":
        from mastapy._private.system_model.analyses_and_results.stability_analyses import (
            _4092,
        )

        return self.__parent__._cast(_4092.BoltStabilityAnalysis)

    @property
    def clutch_half_stability_analysis(
        self: "CastSelf",
    ) -> "_4094.ClutchHalfStabilityAnalysis":
        from mastapy._private.system_model.analyses_and_results.stability_analyses import (
            _4094,
        )

        return self.__parent__._cast(_4094.ClutchHalfStabilityAnalysis)

    @property
    def concept_coupling_half_stability_analysis(
        self: "CastSelf",
    ) -> "_4099.ConceptCouplingHalfStabilityAnalysis":
        from mastapy._private.system_model.analyses_and_results.stability_analyses import (
            _4099,
        )

        return self.__parent__._cast(_4099.ConceptCouplingHalfStabilityAnalysis)

    @property
    def concept_gear_stability_analysis(
        self: "CastSelf",
    ) -> "_4103.ConceptGearStabilityAnalysis":
        from mastapy._private.system_model.analyses_and_results.stability_analyses import (
            _4103,
        )

        return self.__parent__._cast(_4103.ConceptGearStabilityAnalysis)

    @property
    def conical_gear_stability_analysis(
        self: "CastSelf",
    ) -> "_4106.ConicalGearStabilityAnalysis":
        from mastapy._private.system_model.analyses_and_results.stability_analyses import (
            _4106,
        )

        return self.__parent__._cast(_4106.ConicalGearStabilityAnalysis)

    @property
    def connector_stability_analysis(
        self: "CastSelf",
    ) -> "_4108.ConnectorStabilityAnalysis":
        from mastapy._private.system_model.analyses_and_results.stability_analyses import (
            _4108,
        )

        return self.__parent__._cast(_4108.ConnectorStabilityAnalysis)

    @property
    def coupling_half_stability_analysis(
        self: "CastSelf",
    ) -> "_4110.CouplingHalfStabilityAnalysis":
        from mastapy._private.system_model.analyses_and_results.stability_analyses import (
            _4110,
        )

        return self.__parent__._cast(_4110.CouplingHalfStabilityAnalysis)

    @property
    def cvt_pulley_stability_analysis(
        self: "CastSelf",
    ) -> "_4114.CVTPulleyStabilityAnalysis":
        from mastapy._private.system_model.analyses_and_results.stability_analyses import (
            _4114,
        )

        return self.__parent__._cast(_4114.CVTPulleyStabilityAnalysis)

    @property
    def cycloidal_disc_stability_analysis(
        self: "CastSelf",
    ) -> "_4119.CycloidalDiscStabilityAnalysis":
        from mastapy._private.system_model.analyses_and_results.stability_analyses import (
            _4119,
        )

        return self.__parent__._cast(_4119.CycloidalDiscStabilityAnalysis)

    @property
    def cylindrical_gear_stability_analysis(
        self: "CastSelf",
    ) -> "_4122.CylindricalGearStabilityAnalysis":
        from mastapy._private.system_model.analyses_and_results.stability_analyses import (
            _4122,
        )

        return self.__parent__._cast(_4122.CylindricalGearStabilityAnalysis)

    @property
    def cylindrical_planet_gear_stability_analysis(
        self: "CastSelf",
    ) -> "_4123.CylindricalPlanetGearStabilityAnalysis":
        from mastapy._private.system_model.analyses_and_results.stability_analyses import (
            _4123,
        )

        return self.__parent__._cast(_4123.CylindricalPlanetGearStabilityAnalysis)

    @property
    def datum_stability_analysis(self: "CastSelf") -> "_4124.DatumStabilityAnalysis":
        from mastapy._private.system_model.analyses_and_results.stability_analyses import (
            _4124,
        )

        return self.__parent__._cast(_4124.DatumStabilityAnalysis)

    @property
    def external_cad_model_stability_analysis(
        self: "CastSelf",
    ) -> "_4126.ExternalCADModelStabilityAnalysis":
        from mastapy._private.system_model.analyses_and_results.stability_analyses import (
            _4126,
        )

        return self.__parent__._cast(_4126.ExternalCADModelStabilityAnalysis)

    @property
    def face_gear_stability_analysis(
        self: "CastSelf",
    ) -> "_4129.FaceGearStabilityAnalysis":
        from mastapy._private.system_model.analyses_and_results.stability_analyses import (
            _4129,
        )

        return self.__parent__._cast(_4129.FaceGearStabilityAnalysis)

    @property
    def fe_part_stability_analysis(self: "CastSelf") -> "_4130.FEPartStabilityAnalysis":
        from mastapy._private.system_model.analyses_and_results.stability_analyses import (
            _4130,
        )

        return self.__parent__._cast(_4130.FEPartStabilityAnalysis)

    @property
    def gear_stability_analysis(self: "CastSelf") -> "_4134.GearStabilityAnalysis":
        from mastapy._private.system_model.analyses_and_results.stability_analyses import (
            _4134,
        )

        return self.__parent__._cast(_4134.GearStabilityAnalysis)

    @property
    def guide_dxf_model_stability_analysis(
        self: "CastSelf",
    ) -> "_4135.GuideDxfModelStabilityAnalysis":
        from mastapy._private.system_model.analyses_and_results.stability_analyses import (
            _4135,
        )

        return self.__parent__._cast(_4135.GuideDxfModelStabilityAnalysis)

    @property
    def hypoid_gear_stability_analysis(
        self: "CastSelf",
    ) -> "_4138.HypoidGearStabilityAnalysis":
        from mastapy._private.system_model.analyses_and_results.stability_analyses import (
            _4138,
        )

        return self.__parent__._cast(_4138.HypoidGearStabilityAnalysis)

    @property
    def klingelnberg_cyclo_palloid_conical_gear_stability_analysis(
        self: "CastSelf",
    ) -> "_4142.KlingelnbergCycloPalloidConicalGearStabilityAnalysis":
        from mastapy._private.system_model.analyses_and_results.stability_analyses import (
            _4142,
        )

        return self.__parent__._cast(
            _4142.KlingelnbergCycloPalloidConicalGearStabilityAnalysis
        )

    @property
    def klingelnberg_cyclo_palloid_hypoid_gear_stability_analysis(
        self: "CastSelf",
    ) -> "_4145.KlingelnbergCycloPalloidHypoidGearStabilityAnalysis":
        from mastapy._private.system_model.analyses_and_results.stability_analyses import (
            _4145,
        )

        return self.__parent__._cast(
            _4145.KlingelnbergCycloPalloidHypoidGearStabilityAnalysis
        )

    @property
    def klingelnberg_cyclo_palloid_spiral_bevel_gear_stability_analysis(
        self: "CastSelf",
    ) -> "_4148.KlingelnbergCycloPalloidSpiralBevelGearStabilityAnalysis":
        from mastapy._private.system_model.analyses_and_results.stability_analyses import (
            _4148,
        )

        return self.__parent__._cast(
            _4148.KlingelnbergCycloPalloidSpiralBevelGearStabilityAnalysis
        )

    @property
    def mass_disc_stability_analysis(
        self: "CastSelf",
    ) -> "_4149.MassDiscStabilityAnalysis":
        from mastapy._private.system_model.analyses_and_results.stability_analyses import (
            _4149,
        )

        return self.__parent__._cast(_4149.MassDiscStabilityAnalysis)

    @property
    def measurement_component_stability_analysis(
        self: "CastSelf",
    ) -> "_4150.MeasurementComponentStabilityAnalysis":
        from mastapy._private.system_model.analyses_and_results.stability_analyses import (
            _4150,
        )

        return self.__parent__._cast(_4150.MeasurementComponentStabilityAnalysis)

    @property
    def microphone_stability_analysis(
        self: "CastSelf",
    ) -> "_4152.MicrophoneStabilityAnalysis":
        from mastapy._private.system_model.analyses_and_results.stability_analyses import (
            _4152,
        )

        return self.__parent__._cast(_4152.MicrophoneStabilityAnalysis)

    @property
    def mountable_component_stability_analysis(
        self: "CastSelf",
    ) -> "_4153.MountableComponentStabilityAnalysis":
        from mastapy._private.system_model.analyses_and_results.stability_analyses import (
            _4153,
        )

        return self.__parent__._cast(_4153.MountableComponentStabilityAnalysis)

    @property
    def oil_seal_stability_analysis(
        self: "CastSelf",
    ) -> "_4154.OilSealStabilityAnalysis":
        from mastapy._private.system_model.analyses_and_results.stability_analyses import (
            _4154,
        )

        return self.__parent__._cast(_4154.OilSealStabilityAnalysis)

    @property
    def part_to_part_shear_coupling_half_stability_analysis(
        self: "CastSelf",
    ) -> "_4157.PartToPartShearCouplingHalfStabilityAnalysis":
        from mastapy._private.system_model.analyses_and_results.stability_analyses import (
            _4157,
        )

        return self.__parent__._cast(_4157.PartToPartShearCouplingHalfStabilityAnalysis)

    @property
    def planet_carrier_stability_analysis(
        self: "CastSelf",
    ) -> "_4161.PlanetCarrierStabilityAnalysis":
        from mastapy._private.system_model.analyses_and_results.stability_analyses import (
            _4161,
        )

        return self.__parent__._cast(_4161.PlanetCarrierStabilityAnalysis)

    @property
    def point_load_stability_analysis(
        self: "CastSelf",
    ) -> "_4162.PointLoadStabilityAnalysis":
        from mastapy._private.system_model.analyses_and_results.stability_analyses import (
            _4162,
        )

        return self.__parent__._cast(_4162.PointLoadStabilityAnalysis)

    @property
    def power_load_stability_analysis(
        self: "CastSelf",
    ) -> "_4163.PowerLoadStabilityAnalysis":
        from mastapy._private.system_model.analyses_and_results.stability_analyses import (
            _4163,
        )

        return self.__parent__._cast(_4163.PowerLoadStabilityAnalysis)

    @property
    def pulley_stability_analysis(self: "CastSelf") -> "_4164.PulleyStabilityAnalysis":
        from mastapy._private.system_model.analyses_and_results.stability_analyses import (
            _4164,
        )

        return self.__parent__._cast(_4164.PulleyStabilityAnalysis)

    @property
    def ring_pins_stability_analysis(
        self: "CastSelf",
    ) -> "_4165.RingPinsStabilityAnalysis":
        from mastapy._private.system_model.analyses_and_results.stability_analyses import (
            _4165,
        )

        return self.__parent__._cast(_4165.RingPinsStabilityAnalysis)

    @property
    def rolling_ring_stability_analysis(
        self: "CastSelf",
    ) -> "_4169.RollingRingStabilityAnalysis":
        from mastapy._private.system_model.analyses_and_results.stability_analyses import (
            _4169,
        )

        return self.__parent__._cast(_4169.RollingRingStabilityAnalysis)

    @property
    def shaft_hub_connection_stability_analysis(
        self: "CastSelf",
    ) -> "_4171.ShaftHubConnectionStabilityAnalysis":
        from mastapy._private.system_model.analyses_and_results.stability_analyses import (
            _4171,
        )

        return self.__parent__._cast(_4171.ShaftHubConnectionStabilityAnalysis)

    @property
    def shaft_stability_analysis(self: "CastSelf") -> "_4172.ShaftStabilityAnalysis":
        from mastapy._private.system_model.analyses_and_results.stability_analyses import (
            _4172,
        )

        return self.__parent__._cast(_4172.ShaftStabilityAnalysis)

    @property
    def spiral_bevel_gear_stability_analysis(
        self: "CastSelf",
    ) -> "_4177.SpiralBevelGearStabilityAnalysis":
        from mastapy._private.system_model.analyses_and_results.stability_analyses import (
            _4177,
        )

        return self.__parent__._cast(_4177.SpiralBevelGearStabilityAnalysis)

    @property
    def spring_damper_half_stability_analysis(
        self: "CastSelf",
    ) -> "_4179.SpringDamperHalfStabilityAnalysis":
        from mastapy._private.system_model.analyses_and_results.stability_analyses import (
            _4179,
        )

        return self.__parent__._cast(_4179.SpringDamperHalfStabilityAnalysis)

    @property
    def straight_bevel_diff_gear_stability_analysis(
        self: "CastSelf",
    ) -> "_4186.StraightBevelDiffGearStabilityAnalysis":
        from mastapy._private.system_model.analyses_and_results.stability_analyses import (
            _4186,
        )

        return self.__parent__._cast(_4186.StraightBevelDiffGearStabilityAnalysis)

    @property
    def straight_bevel_gear_stability_analysis(
        self: "CastSelf",
    ) -> "_4189.StraightBevelGearStabilityAnalysis":
        from mastapy._private.system_model.analyses_and_results.stability_analyses import (
            _4189,
        )

        return self.__parent__._cast(_4189.StraightBevelGearStabilityAnalysis)

    @property
    def straight_bevel_planet_gear_stability_analysis(
        self: "CastSelf",
    ) -> "_4190.StraightBevelPlanetGearStabilityAnalysis":
        from mastapy._private.system_model.analyses_and_results.stability_analyses import (
            _4190,
        )

        return self.__parent__._cast(_4190.StraightBevelPlanetGearStabilityAnalysis)

    @property
    def straight_bevel_sun_gear_stability_analysis(
        self: "CastSelf",
    ) -> "_4191.StraightBevelSunGearStabilityAnalysis":
        from mastapy._private.system_model.analyses_and_results.stability_analyses import (
            _4191,
        )

        return self.__parent__._cast(_4191.StraightBevelSunGearStabilityAnalysis)

    @property
    def synchroniser_half_stability_analysis(
        self: "CastSelf",
    ) -> "_4192.SynchroniserHalfStabilityAnalysis":
        from mastapy._private.system_model.analyses_and_results.stability_analyses import (
            _4192,
        )

        return self.__parent__._cast(_4192.SynchroniserHalfStabilityAnalysis)

    @property
    def synchroniser_part_stability_analysis(
        self: "CastSelf",
    ) -> "_4193.SynchroniserPartStabilityAnalysis":
        from mastapy._private.system_model.analyses_and_results.stability_analyses import (
            _4193,
        )

        return self.__parent__._cast(_4193.SynchroniserPartStabilityAnalysis)

    @property
    def synchroniser_sleeve_stability_analysis(
        self: "CastSelf",
    ) -> "_4194.SynchroniserSleeveStabilityAnalysis":
        from mastapy._private.system_model.analyses_and_results.stability_analyses import (
            _4194,
        )

        return self.__parent__._cast(_4194.SynchroniserSleeveStabilityAnalysis)

    @property
    def torque_converter_pump_stability_analysis(
        self: "CastSelf",
    ) -> "_4197.TorqueConverterPumpStabilityAnalysis":
        from mastapy._private.system_model.analyses_and_results.stability_analyses import (
            _4197,
        )

        return self.__parent__._cast(_4197.TorqueConverterPumpStabilityAnalysis)

    @property
    def torque_converter_turbine_stability_analysis(
        self: "CastSelf",
    ) -> "_4199.TorqueConverterTurbineStabilityAnalysis":
        from mastapy._private.system_model.analyses_and_results.stability_analyses import (
            _4199,
        )

        return self.__parent__._cast(_4199.TorqueConverterTurbineStabilityAnalysis)

    @property
    def unbalanced_mass_stability_analysis(
        self: "CastSelf",
    ) -> "_4200.UnbalancedMassStabilityAnalysis":
        from mastapy._private.system_model.analyses_and_results.stability_analyses import (
            _4200,
        )

        return self.__parent__._cast(_4200.UnbalancedMassStabilityAnalysis)

    @property
    def virtual_component_stability_analysis(
        self: "CastSelf",
    ) -> "_4201.VirtualComponentStabilityAnalysis":
        from mastapy._private.system_model.analyses_and_results.stability_analyses import (
            _4201,
        )

        return self.__parent__._cast(_4201.VirtualComponentStabilityAnalysis)

    @property
    def worm_gear_stability_analysis(
        self: "CastSelf",
    ) -> "_4204.WormGearStabilityAnalysis":
        from mastapy._private.system_model.analyses_and_results.stability_analyses import (
            _4204,
        )

        return self.__parent__._cast(_4204.WormGearStabilityAnalysis)

    @property
    def zerol_bevel_gear_stability_analysis(
        self: "CastSelf",
    ) -> "_4207.ZerolBevelGearStabilityAnalysis":
        from mastapy._private.system_model.analyses_and_results.stability_analyses import (
            _4207,
        )

        return self.__parent__._cast(_4207.ZerolBevelGearStabilityAnalysis)

    @property
    def component_stability_analysis(self: "CastSelf") -> "ComponentStabilityAnalysis":
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
class ComponentStabilityAnalysis(_4155.PartStabilityAnalysis):
    """ComponentStabilityAnalysis

    This is a mastapy class.
    """

    TYPE: ClassVar["Type"] = _COMPONENT_STABILITY_ANALYSIS

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
    def cast_to(self: "Self") -> "_Cast_ComponentStabilityAnalysis":
        """Cast to another type.

        Returns:
            _Cast_ComponentStabilityAnalysis
        """
        return _Cast_ComponentStabilityAnalysis(self)
