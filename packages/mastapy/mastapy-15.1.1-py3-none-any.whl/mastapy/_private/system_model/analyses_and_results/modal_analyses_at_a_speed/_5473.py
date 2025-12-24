"""ComponentModalAnalysisAtASpeed"""

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
from mastapy._private.system_model.analyses_and_results.modal_analyses_at_a_speed import (
    _5530,
)

_COMPONENT_MODAL_ANALYSIS_AT_A_SPEED = python_net_import(
    "SMT.MastaAPI.SystemModel.AnalysesAndResults.ModalAnalysesAtASpeed",
    "ComponentModalAnalysisAtASpeed",
)

if TYPE_CHECKING:
    from typing import Any, Type, TypeVar

    from mastapy._private.system_model.analyses_and_results import _2943, _2945, _2949
    from mastapy._private.system_model.analyses_and_results.analysis_cases import (
        _7941,
        _7944,
    )
    from mastapy._private.system_model.analyses_and_results.modal_analyses_at_a_speed import (
        _5449,
        _5450,
        _5453,
        _5456,
        _5460,
        _5462,
        _5463,
        _5465,
        _5468,
        _5470,
        _5475,
        _5478,
        _5481,
        _5484,
        _5486,
        _5490,
        _5493,
        _5496,
        _5498,
        _5499,
        _5500,
        _5502,
        _5504,
        _5507,
        _5509,
        _5511,
        _5515,
        _5518,
        _5521,
        _5523,
        _5524,
        _5526,
        _5528,
        _5529,
        _5532,
        _5536,
        _5537,
        _5538,
        _5539,
        _5540,
        _5544,
        _5546,
        _5547,
        _5551,
        _5554,
        _5557,
        _5560,
        _5562,
        _5563,
        _5564,
        _5566,
        _5567,
        _5570,
        _5571,
        _5572,
        _5573,
        _5575,
        _5578,
    )
    from mastapy._private.system_model.part_model import _2714

    Self = TypeVar("Self", bound="ComponentModalAnalysisAtASpeed")
    CastSelf = TypeVar(
        "CastSelf",
        bound="ComponentModalAnalysisAtASpeed._Cast_ComponentModalAnalysisAtASpeed",
    )


__docformat__ = "restructuredtext en"
__all__ = ("ComponentModalAnalysisAtASpeed",)


@extended_dataclass(frozen=True, slots=True, weakref_slot=True)
class _Cast_ComponentModalAnalysisAtASpeed:
    """Special nested class for casting ComponentModalAnalysisAtASpeed to subclasses."""

    __parent__: "ComponentModalAnalysisAtASpeed"

    @property
    def part_modal_analysis_at_a_speed(
        self: "CastSelf",
    ) -> "_5530.PartModalAnalysisAtASpeed":
        return self.__parent__._cast(_5530.PartModalAnalysisAtASpeed)

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
    def abstract_shaft_modal_analysis_at_a_speed(
        self: "CastSelf",
    ) -> "_5449.AbstractShaftModalAnalysisAtASpeed":
        from mastapy._private.system_model.analyses_and_results.modal_analyses_at_a_speed import (
            _5449,
        )

        return self.__parent__._cast(_5449.AbstractShaftModalAnalysisAtASpeed)

    @property
    def abstract_shaft_or_housing_modal_analysis_at_a_speed(
        self: "CastSelf",
    ) -> "_5450.AbstractShaftOrHousingModalAnalysisAtASpeed":
        from mastapy._private.system_model.analyses_and_results.modal_analyses_at_a_speed import (
            _5450,
        )

        return self.__parent__._cast(_5450.AbstractShaftOrHousingModalAnalysisAtASpeed)

    @property
    def agma_gleason_conical_gear_modal_analysis_at_a_speed(
        self: "CastSelf",
    ) -> "_5453.AGMAGleasonConicalGearModalAnalysisAtASpeed":
        from mastapy._private.system_model.analyses_and_results.modal_analyses_at_a_speed import (
            _5453,
        )

        return self.__parent__._cast(_5453.AGMAGleasonConicalGearModalAnalysisAtASpeed)

    @property
    def bearing_modal_analysis_at_a_speed(
        self: "CastSelf",
    ) -> "_5456.BearingModalAnalysisAtASpeed":
        from mastapy._private.system_model.analyses_and_results.modal_analyses_at_a_speed import (
            _5456,
        )

        return self.__parent__._cast(_5456.BearingModalAnalysisAtASpeed)

    @property
    def bevel_differential_gear_modal_analysis_at_a_speed(
        self: "CastSelf",
    ) -> "_5460.BevelDifferentialGearModalAnalysisAtASpeed":
        from mastapy._private.system_model.analyses_and_results.modal_analyses_at_a_speed import (
            _5460,
        )

        return self.__parent__._cast(_5460.BevelDifferentialGearModalAnalysisAtASpeed)

    @property
    def bevel_differential_planet_gear_modal_analysis_at_a_speed(
        self: "CastSelf",
    ) -> "_5462.BevelDifferentialPlanetGearModalAnalysisAtASpeed":
        from mastapy._private.system_model.analyses_and_results.modal_analyses_at_a_speed import (
            _5462,
        )

        return self.__parent__._cast(
            _5462.BevelDifferentialPlanetGearModalAnalysisAtASpeed
        )

    @property
    def bevel_differential_sun_gear_modal_analysis_at_a_speed(
        self: "CastSelf",
    ) -> "_5463.BevelDifferentialSunGearModalAnalysisAtASpeed":
        from mastapy._private.system_model.analyses_and_results.modal_analyses_at_a_speed import (
            _5463,
        )

        return self.__parent__._cast(
            _5463.BevelDifferentialSunGearModalAnalysisAtASpeed
        )

    @property
    def bevel_gear_modal_analysis_at_a_speed(
        self: "CastSelf",
    ) -> "_5465.BevelGearModalAnalysisAtASpeed":
        from mastapy._private.system_model.analyses_and_results.modal_analyses_at_a_speed import (
            _5465,
        )

        return self.__parent__._cast(_5465.BevelGearModalAnalysisAtASpeed)

    @property
    def bolt_modal_analysis_at_a_speed(
        self: "CastSelf",
    ) -> "_5468.BoltModalAnalysisAtASpeed":
        from mastapy._private.system_model.analyses_and_results.modal_analyses_at_a_speed import (
            _5468,
        )

        return self.__parent__._cast(_5468.BoltModalAnalysisAtASpeed)

    @property
    def clutch_half_modal_analysis_at_a_speed(
        self: "CastSelf",
    ) -> "_5470.ClutchHalfModalAnalysisAtASpeed":
        from mastapy._private.system_model.analyses_and_results.modal_analyses_at_a_speed import (
            _5470,
        )

        return self.__parent__._cast(_5470.ClutchHalfModalAnalysisAtASpeed)

    @property
    def concept_coupling_half_modal_analysis_at_a_speed(
        self: "CastSelf",
    ) -> "_5475.ConceptCouplingHalfModalAnalysisAtASpeed":
        from mastapy._private.system_model.analyses_and_results.modal_analyses_at_a_speed import (
            _5475,
        )

        return self.__parent__._cast(_5475.ConceptCouplingHalfModalAnalysisAtASpeed)

    @property
    def concept_gear_modal_analysis_at_a_speed(
        self: "CastSelf",
    ) -> "_5478.ConceptGearModalAnalysisAtASpeed":
        from mastapy._private.system_model.analyses_and_results.modal_analyses_at_a_speed import (
            _5478,
        )

        return self.__parent__._cast(_5478.ConceptGearModalAnalysisAtASpeed)

    @property
    def conical_gear_modal_analysis_at_a_speed(
        self: "CastSelf",
    ) -> "_5481.ConicalGearModalAnalysisAtASpeed":
        from mastapy._private.system_model.analyses_and_results.modal_analyses_at_a_speed import (
            _5481,
        )

        return self.__parent__._cast(_5481.ConicalGearModalAnalysisAtASpeed)

    @property
    def connector_modal_analysis_at_a_speed(
        self: "CastSelf",
    ) -> "_5484.ConnectorModalAnalysisAtASpeed":
        from mastapy._private.system_model.analyses_and_results.modal_analyses_at_a_speed import (
            _5484,
        )

        return self.__parent__._cast(_5484.ConnectorModalAnalysisAtASpeed)

    @property
    def coupling_half_modal_analysis_at_a_speed(
        self: "CastSelf",
    ) -> "_5486.CouplingHalfModalAnalysisAtASpeed":
        from mastapy._private.system_model.analyses_and_results.modal_analyses_at_a_speed import (
            _5486,
        )

        return self.__parent__._cast(_5486.CouplingHalfModalAnalysisAtASpeed)

    @property
    def cvt_pulley_modal_analysis_at_a_speed(
        self: "CastSelf",
    ) -> "_5490.CVTPulleyModalAnalysisAtASpeed":
        from mastapy._private.system_model.analyses_and_results.modal_analyses_at_a_speed import (
            _5490,
        )

        return self.__parent__._cast(_5490.CVTPulleyModalAnalysisAtASpeed)

    @property
    def cycloidal_disc_modal_analysis_at_a_speed(
        self: "CastSelf",
    ) -> "_5493.CycloidalDiscModalAnalysisAtASpeed":
        from mastapy._private.system_model.analyses_and_results.modal_analyses_at_a_speed import (
            _5493,
        )

        return self.__parent__._cast(_5493.CycloidalDiscModalAnalysisAtASpeed)

    @property
    def cylindrical_gear_modal_analysis_at_a_speed(
        self: "CastSelf",
    ) -> "_5496.CylindricalGearModalAnalysisAtASpeed":
        from mastapy._private.system_model.analyses_and_results.modal_analyses_at_a_speed import (
            _5496,
        )

        return self.__parent__._cast(_5496.CylindricalGearModalAnalysisAtASpeed)

    @property
    def cylindrical_planet_gear_modal_analysis_at_a_speed(
        self: "CastSelf",
    ) -> "_5498.CylindricalPlanetGearModalAnalysisAtASpeed":
        from mastapy._private.system_model.analyses_and_results.modal_analyses_at_a_speed import (
            _5498,
        )

        return self.__parent__._cast(_5498.CylindricalPlanetGearModalAnalysisAtASpeed)

    @property
    def datum_modal_analysis_at_a_speed(
        self: "CastSelf",
    ) -> "_5499.DatumModalAnalysisAtASpeed":
        from mastapy._private.system_model.analyses_and_results.modal_analyses_at_a_speed import (
            _5499,
        )

        return self.__parent__._cast(_5499.DatumModalAnalysisAtASpeed)

    @property
    def external_cad_model_modal_analysis_at_a_speed(
        self: "CastSelf",
    ) -> "_5500.ExternalCADModelModalAnalysisAtASpeed":
        from mastapy._private.system_model.analyses_and_results.modal_analyses_at_a_speed import (
            _5500,
        )

        return self.__parent__._cast(_5500.ExternalCADModelModalAnalysisAtASpeed)

    @property
    def face_gear_modal_analysis_at_a_speed(
        self: "CastSelf",
    ) -> "_5502.FaceGearModalAnalysisAtASpeed":
        from mastapy._private.system_model.analyses_and_results.modal_analyses_at_a_speed import (
            _5502,
        )

        return self.__parent__._cast(_5502.FaceGearModalAnalysisAtASpeed)

    @property
    def fe_part_modal_analysis_at_a_speed(
        self: "CastSelf",
    ) -> "_5504.FEPartModalAnalysisAtASpeed":
        from mastapy._private.system_model.analyses_and_results.modal_analyses_at_a_speed import (
            _5504,
        )

        return self.__parent__._cast(_5504.FEPartModalAnalysisAtASpeed)

    @property
    def gear_modal_analysis_at_a_speed(
        self: "CastSelf",
    ) -> "_5507.GearModalAnalysisAtASpeed":
        from mastapy._private.system_model.analyses_and_results.modal_analyses_at_a_speed import (
            _5507,
        )

        return self.__parent__._cast(_5507.GearModalAnalysisAtASpeed)

    @property
    def guide_dxf_model_modal_analysis_at_a_speed(
        self: "CastSelf",
    ) -> "_5509.GuideDxfModelModalAnalysisAtASpeed":
        from mastapy._private.system_model.analyses_and_results.modal_analyses_at_a_speed import (
            _5509,
        )

        return self.__parent__._cast(_5509.GuideDxfModelModalAnalysisAtASpeed)

    @property
    def hypoid_gear_modal_analysis_at_a_speed(
        self: "CastSelf",
    ) -> "_5511.HypoidGearModalAnalysisAtASpeed":
        from mastapy._private.system_model.analyses_and_results.modal_analyses_at_a_speed import (
            _5511,
        )

        return self.__parent__._cast(_5511.HypoidGearModalAnalysisAtASpeed)

    @property
    def klingelnberg_cyclo_palloid_conical_gear_modal_analysis_at_a_speed(
        self: "CastSelf",
    ) -> "_5515.KlingelnbergCycloPalloidConicalGearModalAnalysisAtASpeed":
        from mastapy._private.system_model.analyses_and_results.modal_analyses_at_a_speed import (
            _5515,
        )

        return self.__parent__._cast(
            _5515.KlingelnbergCycloPalloidConicalGearModalAnalysisAtASpeed
        )

    @property
    def klingelnberg_cyclo_palloid_hypoid_gear_modal_analysis_at_a_speed(
        self: "CastSelf",
    ) -> "_5518.KlingelnbergCycloPalloidHypoidGearModalAnalysisAtASpeed":
        from mastapy._private.system_model.analyses_and_results.modal_analyses_at_a_speed import (
            _5518,
        )

        return self.__parent__._cast(
            _5518.KlingelnbergCycloPalloidHypoidGearModalAnalysisAtASpeed
        )

    @property
    def klingelnberg_cyclo_palloid_spiral_bevel_gear_modal_analysis_at_a_speed(
        self: "CastSelf",
    ) -> "_5521.KlingelnbergCycloPalloidSpiralBevelGearModalAnalysisAtASpeed":
        from mastapy._private.system_model.analyses_and_results.modal_analyses_at_a_speed import (
            _5521,
        )

        return self.__parent__._cast(
            _5521.KlingelnbergCycloPalloidSpiralBevelGearModalAnalysisAtASpeed
        )

    @property
    def mass_disc_modal_analysis_at_a_speed(
        self: "CastSelf",
    ) -> "_5523.MassDiscModalAnalysisAtASpeed":
        from mastapy._private.system_model.analyses_and_results.modal_analyses_at_a_speed import (
            _5523,
        )

        return self.__parent__._cast(_5523.MassDiscModalAnalysisAtASpeed)

    @property
    def measurement_component_modal_analysis_at_a_speed(
        self: "CastSelf",
    ) -> "_5524.MeasurementComponentModalAnalysisAtASpeed":
        from mastapy._private.system_model.analyses_and_results.modal_analyses_at_a_speed import (
            _5524,
        )

        return self.__parent__._cast(_5524.MeasurementComponentModalAnalysisAtASpeed)

    @property
    def microphone_modal_analysis_at_a_speed(
        self: "CastSelf",
    ) -> "_5526.MicrophoneModalAnalysisAtASpeed":
        from mastapy._private.system_model.analyses_and_results.modal_analyses_at_a_speed import (
            _5526,
        )

        return self.__parent__._cast(_5526.MicrophoneModalAnalysisAtASpeed)

    @property
    def mountable_component_modal_analysis_at_a_speed(
        self: "CastSelf",
    ) -> "_5528.MountableComponentModalAnalysisAtASpeed":
        from mastapy._private.system_model.analyses_and_results.modal_analyses_at_a_speed import (
            _5528,
        )

        return self.__parent__._cast(_5528.MountableComponentModalAnalysisAtASpeed)

    @property
    def oil_seal_modal_analysis_at_a_speed(
        self: "CastSelf",
    ) -> "_5529.OilSealModalAnalysisAtASpeed":
        from mastapy._private.system_model.analyses_and_results.modal_analyses_at_a_speed import (
            _5529,
        )

        return self.__parent__._cast(_5529.OilSealModalAnalysisAtASpeed)

    @property
    def part_to_part_shear_coupling_half_modal_analysis_at_a_speed(
        self: "CastSelf",
    ) -> "_5532.PartToPartShearCouplingHalfModalAnalysisAtASpeed":
        from mastapy._private.system_model.analyses_and_results.modal_analyses_at_a_speed import (
            _5532,
        )

        return self.__parent__._cast(
            _5532.PartToPartShearCouplingHalfModalAnalysisAtASpeed
        )

    @property
    def planet_carrier_modal_analysis_at_a_speed(
        self: "CastSelf",
    ) -> "_5536.PlanetCarrierModalAnalysisAtASpeed":
        from mastapy._private.system_model.analyses_and_results.modal_analyses_at_a_speed import (
            _5536,
        )

        return self.__parent__._cast(_5536.PlanetCarrierModalAnalysisAtASpeed)

    @property
    def point_load_modal_analysis_at_a_speed(
        self: "CastSelf",
    ) -> "_5537.PointLoadModalAnalysisAtASpeed":
        from mastapy._private.system_model.analyses_and_results.modal_analyses_at_a_speed import (
            _5537,
        )

        return self.__parent__._cast(_5537.PointLoadModalAnalysisAtASpeed)

    @property
    def power_load_modal_analysis_at_a_speed(
        self: "CastSelf",
    ) -> "_5538.PowerLoadModalAnalysisAtASpeed":
        from mastapy._private.system_model.analyses_and_results.modal_analyses_at_a_speed import (
            _5538,
        )

        return self.__parent__._cast(_5538.PowerLoadModalAnalysisAtASpeed)

    @property
    def pulley_modal_analysis_at_a_speed(
        self: "CastSelf",
    ) -> "_5539.PulleyModalAnalysisAtASpeed":
        from mastapy._private.system_model.analyses_and_results.modal_analyses_at_a_speed import (
            _5539,
        )

        return self.__parent__._cast(_5539.PulleyModalAnalysisAtASpeed)

    @property
    def ring_pins_modal_analysis_at_a_speed(
        self: "CastSelf",
    ) -> "_5540.RingPinsModalAnalysisAtASpeed":
        from mastapy._private.system_model.analyses_and_results.modal_analyses_at_a_speed import (
            _5540,
        )

        return self.__parent__._cast(_5540.RingPinsModalAnalysisAtASpeed)

    @property
    def rolling_ring_modal_analysis_at_a_speed(
        self: "CastSelf",
    ) -> "_5544.RollingRingModalAnalysisAtASpeed":
        from mastapy._private.system_model.analyses_and_results.modal_analyses_at_a_speed import (
            _5544,
        )

        return self.__parent__._cast(_5544.RollingRingModalAnalysisAtASpeed)

    @property
    def shaft_hub_connection_modal_analysis_at_a_speed(
        self: "CastSelf",
    ) -> "_5546.ShaftHubConnectionModalAnalysisAtASpeed":
        from mastapy._private.system_model.analyses_and_results.modal_analyses_at_a_speed import (
            _5546,
        )

        return self.__parent__._cast(_5546.ShaftHubConnectionModalAnalysisAtASpeed)

    @property
    def shaft_modal_analysis_at_a_speed(
        self: "CastSelf",
    ) -> "_5547.ShaftModalAnalysisAtASpeed":
        from mastapy._private.system_model.analyses_and_results.modal_analyses_at_a_speed import (
            _5547,
        )

        return self.__parent__._cast(_5547.ShaftModalAnalysisAtASpeed)

    @property
    def spiral_bevel_gear_modal_analysis_at_a_speed(
        self: "CastSelf",
    ) -> "_5551.SpiralBevelGearModalAnalysisAtASpeed":
        from mastapy._private.system_model.analyses_and_results.modal_analyses_at_a_speed import (
            _5551,
        )

        return self.__parent__._cast(_5551.SpiralBevelGearModalAnalysisAtASpeed)

    @property
    def spring_damper_half_modal_analysis_at_a_speed(
        self: "CastSelf",
    ) -> "_5554.SpringDamperHalfModalAnalysisAtASpeed":
        from mastapy._private.system_model.analyses_and_results.modal_analyses_at_a_speed import (
            _5554,
        )

        return self.__parent__._cast(_5554.SpringDamperHalfModalAnalysisAtASpeed)

    @property
    def straight_bevel_diff_gear_modal_analysis_at_a_speed(
        self: "CastSelf",
    ) -> "_5557.StraightBevelDiffGearModalAnalysisAtASpeed":
        from mastapy._private.system_model.analyses_and_results.modal_analyses_at_a_speed import (
            _5557,
        )

        return self.__parent__._cast(_5557.StraightBevelDiffGearModalAnalysisAtASpeed)

    @property
    def straight_bevel_gear_modal_analysis_at_a_speed(
        self: "CastSelf",
    ) -> "_5560.StraightBevelGearModalAnalysisAtASpeed":
        from mastapy._private.system_model.analyses_and_results.modal_analyses_at_a_speed import (
            _5560,
        )

        return self.__parent__._cast(_5560.StraightBevelGearModalAnalysisAtASpeed)

    @property
    def straight_bevel_planet_gear_modal_analysis_at_a_speed(
        self: "CastSelf",
    ) -> "_5562.StraightBevelPlanetGearModalAnalysisAtASpeed":
        from mastapy._private.system_model.analyses_and_results.modal_analyses_at_a_speed import (
            _5562,
        )

        return self.__parent__._cast(_5562.StraightBevelPlanetGearModalAnalysisAtASpeed)

    @property
    def straight_bevel_sun_gear_modal_analysis_at_a_speed(
        self: "CastSelf",
    ) -> "_5563.StraightBevelSunGearModalAnalysisAtASpeed":
        from mastapy._private.system_model.analyses_and_results.modal_analyses_at_a_speed import (
            _5563,
        )

        return self.__parent__._cast(_5563.StraightBevelSunGearModalAnalysisAtASpeed)

    @property
    def synchroniser_half_modal_analysis_at_a_speed(
        self: "CastSelf",
    ) -> "_5564.SynchroniserHalfModalAnalysisAtASpeed":
        from mastapy._private.system_model.analyses_and_results.modal_analyses_at_a_speed import (
            _5564,
        )

        return self.__parent__._cast(_5564.SynchroniserHalfModalAnalysisAtASpeed)

    @property
    def synchroniser_part_modal_analysis_at_a_speed(
        self: "CastSelf",
    ) -> "_5566.SynchroniserPartModalAnalysisAtASpeed":
        from mastapy._private.system_model.analyses_and_results.modal_analyses_at_a_speed import (
            _5566,
        )

        return self.__parent__._cast(_5566.SynchroniserPartModalAnalysisAtASpeed)

    @property
    def synchroniser_sleeve_modal_analysis_at_a_speed(
        self: "CastSelf",
    ) -> "_5567.SynchroniserSleeveModalAnalysisAtASpeed":
        from mastapy._private.system_model.analyses_and_results.modal_analyses_at_a_speed import (
            _5567,
        )

        return self.__parent__._cast(_5567.SynchroniserSleeveModalAnalysisAtASpeed)

    @property
    def torque_converter_pump_modal_analysis_at_a_speed(
        self: "CastSelf",
    ) -> "_5570.TorqueConverterPumpModalAnalysisAtASpeed":
        from mastapy._private.system_model.analyses_and_results.modal_analyses_at_a_speed import (
            _5570,
        )

        return self.__parent__._cast(_5570.TorqueConverterPumpModalAnalysisAtASpeed)

    @property
    def torque_converter_turbine_modal_analysis_at_a_speed(
        self: "CastSelf",
    ) -> "_5571.TorqueConverterTurbineModalAnalysisAtASpeed":
        from mastapy._private.system_model.analyses_and_results.modal_analyses_at_a_speed import (
            _5571,
        )

        return self.__parent__._cast(_5571.TorqueConverterTurbineModalAnalysisAtASpeed)

    @property
    def unbalanced_mass_modal_analysis_at_a_speed(
        self: "CastSelf",
    ) -> "_5572.UnbalancedMassModalAnalysisAtASpeed":
        from mastapy._private.system_model.analyses_and_results.modal_analyses_at_a_speed import (
            _5572,
        )

        return self.__parent__._cast(_5572.UnbalancedMassModalAnalysisAtASpeed)

    @property
    def virtual_component_modal_analysis_at_a_speed(
        self: "CastSelf",
    ) -> "_5573.VirtualComponentModalAnalysisAtASpeed":
        from mastapy._private.system_model.analyses_and_results.modal_analyses_at_a_speed import (
            _5573,
        )

        return self.__parent__._cast(_5573.VirtualComponentModalAnalysisAtASpeed)

    @property
    def worm_gear_modal_analysis_at_a_speed(
        self: "CastSelf",
    ) -> "_5575.WormGearModalAnalysisAtASpeed":
        from mastapy._private.system_model.analyses_and_results.modal_analyses_at_a_speed import (
            _5575,
        )

        return self.__parent__._cast(_5575.WormGearModalAnalysisAtASpeed)

    @property
    def zerol_bevel_gear_modal_analysis_at_a_speed(
        self: "CastSelf",
    ) -> "_5578.ZerolBevelGearModalAnalysisAtASpeed":
        from mastapy._private.system_model.analyses_and_results.modal_analyses_at_a_speed import (
            _5578,
        )

        return self.__parent__._cast(_5578.ZerolBevelGearModalAnalysisAtASpeed)

    @property
    def component_modal_analysis_at_a_speed(
        self: "CastSelf",
    ) -> "ComponentModalAnalysisAtASpeed":
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
class ComponentModalAnalysisAtASpeed(_5530.PartModalAnalysisAtASpeed):
    """ComponentModalAnalysisAtASpeed

    This is a mastapy class.
    """

    TYPE: ClassVar["Type"] = _COMPONENT_MODAL_ANALYSIS_AT_A_SPEED

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
    def cast_to(self: "Self") -> "_Cast_ComponentModalAnalysisAtASpeed":
        """Cast to another type.

        Returns:
            _Cast_ComponentModalAnalysisAtASpeed
        """
        return _Cast_ComponentModalAnalysisAtASpeed(self)
