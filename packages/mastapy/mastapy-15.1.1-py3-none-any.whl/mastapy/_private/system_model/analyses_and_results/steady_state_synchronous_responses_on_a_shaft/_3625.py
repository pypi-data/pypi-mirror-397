"""MountableComponentSteadyStateSynchronousResponseOnAShaft"""

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
from mastapy._private.system_model.analyses_and_results.steady_state_synchronous_responses_on_a_shaft import (
    _3571,
)

_MOUNTABLE_COMPONENT_STEADY_STATE_SYNCHRONOUS_RESPONSE_ON_A_SHAFT = python_net_import(
    "SMT.MastaAPI.SystemModel.AnalysesAndResults.SteadyStateSynchronousResponsesOnAShaft",
    "MountableComponentSteadyStateSynchronousResponseOnAShaft",
)

if TYPE_CHECKING:
    from typing import Any, Type, TypeVar

    from mastapy._private.system_model.analyses_and_results import _2943, _2945, _2949
    from mastapy._private.system_model.analyses_and_results.analysis_cases import (
        _7941,
        _7944,
    )
    from mastapy._private.system_model.analyses_and_results.steady_state_synchronous_responses_on_a_shaft import (
        _3552,
        _3554,
        _3559,
        _3560,
        _3561,
        _3564,
        _3568,
        _3573,
        _3577,
        _3580,
        _3582,
        _3584,
        _3587,
        _3595,
        _3596,
        _3601,
        _3606,
        _3610,
        _3614,
        _3617,
        _3620,
        _3621,
        _3622,
        _3626,
        _3627,
        _3629,
        _3633,
        _3634,
        _3635,
        _3636,
        _3637,
        _3641,
        _3643,
        _3649,
        _3651,
        _3656,
        _3659,
        _3660,
        _3661,
        _3662,
        _3663,
        _3664,
        _3667,
        _3669,
        _3670,
        _3671,
        _3674,
        _3677,
    )
    from mastapy._private.system_model.part_model import _2737

    Self = TypeVar(
        "Self", bound="MountableComponentSteadyStateSynchronousResponseOnAShaft"
    )
    CastSelf = TypeVar(
        "CastSelf",
        bound="MountableComponentSteadyStateSynchronousResponseOnAShaft._Cast_MountableComponentSteadyStateSynchronousResponseOnAShaft",
    )


__docformat__ = "restructuredtext en"
__all__ = ("MountableComponentSteadyStateSynchronousResponseOnAShaft",)


@extended_dataclass(frozen=True, slots=True, weakref_slot=True)
class _Cast_MountableComponentSteadyStateSynchronousResponseOnAShaft:
    """Special nested class for casting MountableComponentSteadyStateSynchronousResponseOnAShaft to subclasses."""

    __parent__: "MountableComponentSteadyStateSynchronousResponseOnAShaft"

    @property
    def component_steady_state_synchronous_response_on_a_shaft(
        self: "CastSelf",
    ) -> "_3571.ComponentSteadyStateSynchronousResponseOnAShaft":
        return self.__parent__._cast(
            _3571.ComponentSteadyStateSynchronousResponseOnAShaft
        )

    @property
    def part_steady_state_synchronous_response_on_a_shaft(
        self: "CastSelf",
    ) -> "_3627.PartSteadyStateSynchronousResponseOnAShaft":
        from mastapy._private.system_model.analyses_and_results.steady_state_synchronous_responses_on_a_shaft import (
            _3627,
        )

        return self.__parent__._cast(_3627.PartSteadyStateSynchronousResponseOnAShaft)

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
    def agma_gleason_conical_gear_steady_state_synchronous_response_on_a_shaft(
        self: "CastSelf",
    ) -> "_3552.AGMAGleasonConicalGearSteadyStateSynchronousResponseOnAShaft":
        from mastapy._private.system_model.analyses_and_results.steady_state_synchronous_responses_on_a_shaft import (
            _3552,
        )

        return self.__parent__._cast(
            _3552.AGMAGleasonConicalGearSteadyStateSynchronousResponseOnAShaft
        )

    @property
    def bearing_steady_state_synchronous_response_on_a_shaft(
        self: "CastSelf",
    ) -> "_3554.BearingSteadyStateSynchronousResponseOnAShaft":
        from mastapy._private.system_model.analyses_and_results.steady_state_synchronous_responses_on_a_shaft import (
            _3554,
        )

        return self.__parent__._cast(
            _3554.BearingSteadyStateSynchronousResponseOnAShaft
        )

    @property
    def bevel_differential_gear_steady_state_synchronous_response_on_a_shaft(
        self: "CastSelf",
    ) -> "_3559.BevelDifferentialGearSteadyStateSynchronousResponseOnAShaft":
        from mastapy._private.system_model.analyses_and_results.steady_state_synchronous_responses_on_a_shaft import (
            _3559,
        )

        return self.__parent__._cast(
            _3559.BevelDifferentialGearSteadyStateSynchronousResponseOnAShaft
        )

    @property
    def bevel_differential_planet_gear_steady_state_synchronous_response_on_a_shaft(
        self: "CastSelf",
    ) -> "_3560.BevelDifferentialPlanetGearSteadyStateSynchronousResponseOnAShaft":
        from mastapy._private.system_model.analyses_and_results.steady_state_synchronous_responses_on_a_shaft import (
            _3560,
        )

        return self.__parent__._cast(
            _3560.BevelDifferentialPlanetGearSteadyStateSynchronousResponseOnAShaft
        )

    @property
    def bevel_differential_sun_gear_steady_state_synchronous_response_on_a_shaft(
        self: "CastSelf",
    ) -> "_3561.BevelDifferentialSunGearSteadyStateSynchronousResponseOnAShaft":
        from mastapy._private.system_model.analyses_and_results.steady_state_synchronous_responses_on_a_shaft import (
            _3561,
        )

        return self.__parent__._cast(
            _3561.BevelDifferentialSunGearSteadyStateSynchronousResponseOnAShaft
        )

    @property
    def bevel_gear_steady_state_synchronous_response_on_a_shaft(
        self: "CastSelf",
    ) -> "_3564.BevelGearSteadyStateSynchronousResponseOnAShaft":
        from mastapy._private.system_model.analyses_and_results.steady_state_synchronous_responses_on_a_shaft import (
            _3564,
        )

        return self.__parent__._cast(
            _3564.BevelGearSteadyStateSynchronousResponseOnAShaft
        )

    @property
    def clutch_half_steady_state_synchronous_response_on_a_shaft(
        self: "CastSelf",
    ) -> "_3568.ClutchHalfSteadyStateSynchronousResponseOnAShaft":
        from mastapy._private.system_model.analyses_and_results.steady_state_synchronous_responses_on_a_shaft import (
            _3568,
        )

        return self.__parent__._cast(
            _3568.ClutchHalfSteadyStateSynchronousResponseOnAShaft
        )

    @property
    def concept_coupling_half_steady_state_synchronous_response_on_a_shaft(
        self: "CastSelf",
    ) -> "_3573.ConceptCouplingHalfSteadyStateSynchronousResponseOnAShaft":
        from mastapy._private.system_model.analyses_and_results.steady_state_synchronous_responses_on_a_shaft import (
            _3573,
        )

        return self.__parent__._cast(
            _3573.ConceptCouplingHalfSteadyStateSynchronousResponseOnAShaft
        )

    @property
    def concept_gear_steady_state_synchronous_response_on_a_shaft(
        self: "CastSelf",
    ) -> "_3577.ConceptGearSteadyStateSynchronousResponseOnAShaft":
        from mastapy._private.system_model.analyses_and_results.steady_state_synchronous_responses_on_a_shaft import (
            _3577,
        )

        return self.__parent__._cast(
            _3577.ConceptGearSteadyStateSynchronousResponseOnAShaft
        )

    @property
    def conical_gear_steady_state_synchronous_response_on_a_shaft(
        self: "CastSelf",
    ) -> "_3580.ConicalGearSteadyStateSynchronousResponseOnAShaft":
        from mastapy._private.system_model.analyses_and_results.steady_state_synchronous_responses_on_a_shaft import (
            _3580,
        )

        return self.__parent__._cast(
            _3580.ConicalGearSteadyStateSynchronousResponseOnAShaft
        )

    @property
    def connector_steady_state_synchronous_response_on_a_shaft(
        self: "CastSelf",
    ) -> "_3582.ConnectorSteadyStateSynchronousResponseOnAShaft":
        from mastapy._private.system_model.analyses_and_results.steady_state_synchronous_responses_on_a_shaft import (
            _3582,
        )

        return self.__parent__._cast(
            _3582.ConnectorSteadyStateSynchronousResponseOnAShaft
        )

    @property
    def coupling_half_steady_state_synchronous_response_on_a_shaft(
        self: "CastSelf",
    ) -> "_3584.CouplingHalfSteadyStateSynchronousResponseOnAShaft":
        from mastapy._private.system_model.analyses_and_results.steady_state_synchronous_responses_on_a_shaft import (
            _3584,
        )

        return self.__parent__._cast(
            _3584.CouplingHalfSteadyStateSynchronousResponseOnAShaft
        )

    @property
    def cvt_pulley_steady_state_synchronous_response_on_a_shaft(
        self: "CastSelf",
    ) -> "_3587.CVTPulleySteadyStateSynchronousResponseOnAShaft":
        from mastapy._private.system_model.analyses_and_results.steady_state_synchronous_responses_on_a_shaft import (
            _3587,
        )

        return self.__parent__._cast(
            _3587.CVTPulleySteadyStateSynchronousResponseOnAShaft
        )

    @property
    def cylindrical_gear_steady_state_synchronous_response_on_a_shaft(
        self: "CastSelf",
    ) -> "_3595.CylindricalGearSteadyStateSynchronousResponseOnAShaft":
        from mastapy._private.system_model.analyses_and_results.steady_state_synchronous_responses_on_a_shaft import (
            _3595,
        )

        return self.__parent__._cast(
            _3595.CylindricalGearSteadyStateSynchronousResponseOnAShaft
        )

    @property
    def cylindrical_planet_gear_steady_state_synchronous_response_on_a_shaft(
        self: "CastSelf",
    ) -> "_3596.CylindricalPlanetGearSteadyStateSynchronousResponseOnAShaft":
        from mastapy._private.system_model.analyses_and_results.steady_state_synchronous_responses_on_a_shaft import (
            _3596,
        )

        return self.__parent__._cast(
            _3596.CylindricalPlanetGearSteadyStateSynchronousResponseOnAShaft
        )

    @property
    def face_gear_steady_state_synchronous_response_on_a_shaft(
        self: "CastSelf",
    ) -> "_3601.FaceGearSteadyStateSynchronousResponseOnAShaft":
        from mastapy._private.system_model.analyses_and_results.steady_state_synchronous_responses_on_a_shaft import (
            _3601,
        )

        return self.__parent__._cast(
            _3601.FaceGearSteadyStateSynchronousResponseOnAShaft
        )

    @property
    def gear_steady_state_synchronous_response_on_a_shaft(
        self: "CastSelf",
    ) -> "_3606.GearSteadyStateSynchronousResponseOnAShaft":
        from mastapy._private.system_model.analyses_and_results.steady_state_synchronous_responses_on_a_shaft import (
            _3606,
        )

        return self.__parent__._cast(_3606.GearSteadyStateSynchronousResponseOnAShaft)

    @property
    def hypoid_gear_steady_state_synchronous_response_on_a_shaft(
        self: "CastSelf",
    ) -> "_3610.HypoidGearSteadyStateSynchronousResponseOnAShaft":
        from mastapy._private.system_model.analyses_and_results.steady_state_synchronous_responses_on_a_shaft import (
            _3610,
        )

        return self.__parent__._cast(
            _3610.HypoidGearSteadyStateSynchronousResponseOnAShaft
        )

    @property
    def klingelnberg_cyclo_palloid_conical_gear_steady_state_synchronous_response_on_a_shaft(
        self: "CastSelf",
    ) -> "_3614.KlingelnbergCycloPalloidConicalGearSteadyStateSynchronousResponseOnAShaft":
        from mastapy._private.system_model.analyses_and_results.steady_state_synchronous_responses_on_a_shaft import (
            _3614,
        )

        return self.__parent__._cast(
            _3614.KlingelnbergCycloPalloidConicalGearSteadyStateSynchronousResponseOnAShaft
        )

    @property
    def klingelnberg_cyclo_palloid_hypoid_gear_steady_state_synchronous_response_on_a_shaft(
        self: "CastSelf",
    ) -> (
        "_3617.KlingelnbergCycloPalloidHypoidGearSteadyStateSynchronousResponseOnAShaft"
    ):
        from mastapy._private.system_model.analyses_and_results.steady_state_synchronous_responses_on_a_shaft import (
            _3617,
        )

        return self.__parent__._cast(
            _3617.KlingelnbergCycloPalloidHypoidGearSteadyStateSynchronousResponseOnAShaft
        )

    @property
    def klingelnberg_cyclo_palloid_spiral_bevel_gear_steady_state_synchronous_response_on_a_shaft(
        self: "CastSelf",
    ) -> "_3620.KlingelnbergCycloPalloidSpiralBevelGearSteadyStateSynchronousResponseOnAShaft":
        from mastapy._private.system_model.analyses_and_results.steady_state_synchronous_responses_on_a_shaft import (
            _3620,
        )

        return self.__parent__._cast(
            _3620.KlingelnbergCycloPalloidSpiralBevelGearSteadyStateSynchronousResponseOnAShaft
        )

    @property
    def mass_disc_steady_state_synchronous_response_on_a_shaft(
        self: "CastSelf",
    ) -> "_3621.MassDiscSteadyStateSynchronousResponseOnAShaft":
        from mastapy._private.system_model.analyses_and_results.steady_state_synchronous_responses_on_a_shaft import (
            _3621,
        )

        return self.__parent__._cast(
            _3621.MassDiscSteadyStateSynchronousResponseOnAShaft
        )

    @property
    def measurement_component_steady_state_synchronous_response_on_a_shaft(
        self: "CastSelf",
    ) -> "_3622.MeasurementComponentSteadyStateSynchronousResponseOnAShaft":
        from mastapy._private.system_model.analyses_and_results.steady_state_synchronous_responses_on_a_shaft import (
            _3622,
        )

        return self.__parent__._cast(
            _3622.MeasurementComponentSteadyStateSynchronousResponseOnAShaft
        )

    @property
    def oil_seal_steady_state_synchronous_response_on_a_shaft(
        self: "CastSelf",
    ) -> "_3626.OilSealSteadyStateSynchronousResponseOnAShaft":
        from mastapy._private.system_model.analyses_and_results.steady_state_synchronous_responses_on_a_shaft import (
            _3626,
        )

        return self.__parent__._cast(
            _3626.OilSealSteadyStateSynchronousResponseOnAShaft
        )

    @property
    def part_to_part_shear_coupling_half_steady_state_synchronous_response_on_a_shaft(
        self: "CastSelf",
    ) -> "_3629.PartToPartShearCouplingHalfSteadyStateSynchronousResponseOnAShaft":
        from mastapy._private.system_model.analyses_and_results.steady_state_synchronous_responses_on_a_shaft import (
            _3629,
        )

        return self.__parent__._cast(
            _3629.PartToPartShearCouplingHalfSteadyStateSynchronousResponseOnAShaft
        )

    @property
    def planet_carrier_steady_state_synchronous_response_on_a_shaft(
        self: "CastSelf",
    ) -> "_3633.PlanetCarrierSteadyStateSynchronousResponseOnAShaft":
        from mastapy._private.system_model.analyses_and_results.steady_state_synchronous_responses_on_a_shaft import (
            _3633,
        )

        return self.__parent__._cast(
            _3633.PlanetCarrierSteadyStateSynchronousResponseOnAShaft
        )

    @property
    def point_load_steady_state_synchronous_response_on_a_shaft(
        self: "CastSelf",
    ) -> "_3634.PointLoadSteadyStateSynchronousResponseOnAShaft":
        from mastapy._private.system_model.analyses_and_results.steady_state_synchronous_responses_on_a_shaft import (
            _3634,
        )

        return self.__parent__._cast(
            _3634.PointLoadSteadyStateSynchronousResponseOnAShaft
        )

    @property
    def power_load_steady_state_synchronous_response_on_a_shaft(
        self: "CastSelf",
    ) -> "_3635.PowerLoadSteadyStateSynchronousResponseOnAShaft":
        from mastapy._private.system_model.analyses_and_results.steady_state_synchronous_responses_on_a_shaft import (
            _3635,
        )

        return self.__parent__._cast(
            _3635.PowerLoadSteadyStateSynchronousResponseOnAShaft
        )

    @property
    def pulley_steady_state_synchronous_response_on_a_shaft(
        self: "CastSelf",
    ) -> "_3636.PulleySteadyStateSynchronousResponseOnAShaft":
        from mastapy._private.system_model.analyses_and_results.steady_state_synchronous_responses_on_a_shaft import (
            _3636,
        )

        return self.__parent__._cast(_3636.PulleySteadyStateSynchronousResponseOnAShaft)

    @property
    def ring_pins_steady_state_synchronous_response_on_a_shaft(
        self: "CastSelf",
    ) -> "_3637.RingPinsSteadyStateSynchronousResponseOnAShaft":
        from mastapy._private.system_model.analyses_and_results.steady_state_synchronous_responses_on_a_shaft import (
            _3637,
        )

        return self.__parent__._cast(
            _3637.RingPinsSteadyStateSynchronousResponseOnAShaft
        )

    @property
    def rolling_ring_steady_state_synchronous_response_on_a_shaft(
        self: "CastSelf",
    ) -> "_3641.RollingRingSteadyStateSynchronousResponseOnAShaft":
        from mastapy._private.system_model.analyses_and_results.steady_state_synchronous_responses_on_a_shaft import (
            _3641,
        )

        return self.__parent__._cast(
            _3641.RollingRingSteadyStateSynchronousResponseOnAShaft
        )

    @property
    def shaft_hub_connection_steady_state_synchronous_response_on_a_shaft(
        self: "CastSelf",
    ) -> "_3643.ShaftHubConnectionSteadyStateSynchronousResponseOnAShaft":
        from mastapy._private.system_model.analyses_and_results.steady_state_synchronous_responses_on_a_shaft import (
            _3643,
        )

        return self.__parent__._cast(
            _3643.ShaftHubConnectionSteadyStateSynchronousResponseOnAShaft
        )

    @property
    def spiral_bevel_gear_steady_state_synchronous_response_on_a_shaft(
        self: "CastSelf",
    ) -> "_3649.SpiralBevelGearSteadyStateSynchronousResponseOnAShaft":
        from mastapy._private.system_model.analyses_and_results.steady_state_synchronous_responses_on_a_shaft import (
            _3649,
        )

        return self.__parent__._cast(
            _3649.SpiralBevelGearSteadyStateSynchronousResponseOnAShaft
        )

    @property
    def spring_damper_half_steady_state_synchronous_response_on_a_shaft(
        self: "CastSelf",
    ) -> "_3651.SpringDamperHalfSteadyStateSynchronousResponseOnAShaft":
        from mastapy._private.system_model.analyses_and_results.steady_state_synchronous_responses_on_a_shaft import (
            _3651,
        )

        return self.__parent__._cast(
            _3651.SpringDamperHalfSteadyStateSynchronousResponseOnAShaft
        )

    @property
    def straight_bevel_diff_gear_steady_state_synchronous_response_on_a_shaft(
        self: "CastSelf",
    ) -> "_3656.StraightBevelDiffGearSteadyStateSynchronousResponseOnAShaft":
        from mastapy._private.system_model.analyses_and_results.steady_state_synchronous_responses_on_a_shaft import (
            _3656,
        )

        return self.__parent__._cast(
            _3656.StraightBevelDiffGearSteadyStateSynchronousResponseOnAShaft
        )

    @property
    def straight_bevel_gear_steady_state_synchronous_response_on_a_shaft(
        self: "CastSelf",
    ) -> "_3659.StraightBevelGearSteadyStateSynchronousResponseOnAShaft":
        from mastapy._private.system_model.analyses_and_results.steady_state_synchronous_responses_on_a_shaft import (
            _3659,
        )

        return self.__parent__._cast(
            _3659.StraightBevelGearSteadyStateSynchronousResponseOnAShaft
        )

    @property
    def straight_bevel_planet_gear_steady_state_synchronous_response_on_a_shaft(
        self: "CastSelf",
    ) -> "_3660.StraightBevelPlanetGearSteadyStateSynchronousResponseOnAShaft":
        from mastapy._private.system_model.analyses_and_results.steady_state_synchronous_responses_on_a_shaft import (
            _3660,
        )

        return self.__parent__._cast(
            _3660.StraightBevelPlanetGearSteadyStateSynchronousResponseOnAShaft
        )

    @property
    def straight_bevel_sun_gear_steady_state_synchronous_response_on_a_shaft(
        self: "CastSelf",
    ) -> "_3661.StraightBevelSunGearSteadyStateSynchronousResponseOnAShaft":
        from mastapy._private.system_model.analyses_and_results.steady_state_synchronous_responses_on_a_shaft import (
            _3661,
        )

        return self.__parent__._cast(
            _3661.StraightBevelSunGearSteadyStateSynchronousResponseOnAShaft
        )

    @property
    def synchroniser_half_steady_state_synchronous_response_on_a_shaft(
        self: "CastSelf",
    ) -> "_3662.SynchroniserHalfSteadyStateSynchronousResponseOnAShaft":
        from mastapy._private.system_model.analyses_and_results.steady_state_synchronous_responses_on_a_shaft import (
            _3662,
        )

        return self.__parent__._cast(
            _3662.SynchroniserHalfSteadyStateSynchronousResponseOnAShaft
        )

    @property
    def synchroniser_part_steady_state_synchronous_response_on_a_shaft(
        self: "CastSelf",
    ) -> "_3663.SynchroniserPartSteadyStateSynchronousResponseOnAShaft":
        from mastapy._private.system_model.analyses_and_results.steady_state_synchronous_responses_on_a_shaft import (
            _3663,
        )

        return self.__parent__._cast(
            _3663.SynchroniserPartSteadyStateSynchronousResponseOnAShaft
        )

    @property
    def synchroniser_sleeve_steady_state_synchronous_response_on_a_shaft(
        self: "CastSelf",
    ) -> "_3664.SynchroniserSleeveSteadyStateSynchronousResponseOnAShaft":
        from mastapy._private.system_model.analyses_and_results.steady_state_synchronous_responses_on_a_shaft import (
            _3664,
        )

        return self.__parent__._cast(
            _3664.SynchroniserSleeveSteadyStateSynchronousResponseOnAShaft
        )

    @property
    def torque_converter_pump_steady_state_synchronous_response_on_a_shaft(
        self: "CastSelf",
    ) -> "_3667.TorqueConverterPumpSteadyStateSynchronousResponseOnAShaft":
        from mastapy._private.system_model.analyses_and_results.steady_state_synchronous_responses_on_a_shaft import (
            _3667,
        )

        return self.__parent__._cast(
            _3667.TorqueConverterPumpSteadyStateSynchronousResponseOnAShaft
        )

    @property
    def torque_converter_turbine_steady_state_synchronous_response_on_a_shaft(
        self: "CastSelf",
    ) -> "_3669.TorqueConverterTurbineSteadyStateSynchronousResponseOnAShaft":
        from mastapy._private.system_model.analyses_and_results.steady_state_synchronous_responses_on_a_shaft import (
            _3669,
        )

        return self.__parent__._cast(
            _3669.TorqueConverterTurbineSteadyStateSynchronousResponseOnAShaft
        )

    @property
    def unbalanced_mass_steady_state_synchronous_response_on_a_shaft(
        self: "CastSelf",
    ) -> "_3670.UnbalancedMassSteadyStateSynchronousResponseOnAShaft":
        from mastapy._private.system_model.analyses_and_results.steady_state_synchronous_responses_on_a_shaft import (
            _3670,
        )

        return self.__parent__._cast(
            _3670.UnbalancedMassSteadyStateSynchronousResponseOnAShaft
        )

    @property
    def virtual_component_steady_state_synchronous_response_on_a_shaft(
        self: "CastSelf",
    ) -> "_3671.VirtualComponentSteadyStateSynchronousResponseOnAShaft":
        from mastapy._private.system_model.analyses_and_results.steady_state_synchronous_responses_on_a_shaft import (
            _3671,
        )

        return self.__parent__._cast(
            _3671.VirtualComponentSteadyStateSynchronousResponseOnAShaft
        )

    @property
    def worm_gear_steady_state_synchronous_response_on_a_shaft(
        self: "CastSelf",
    ) -> "_3674.WormGearSteadyStateSynchronousResponseOnAShaft":
        from mastapy._private.system_model.analyses_and_results.steady_state_synchronous_responses_on_a_shaft import (
            _3674,
        )

        return self.__parent__._cast(
            _3674.WormGearSteadyStateSynchronousResponseOnAShaft
        )

    @property
    def zerol_bevel_gear_steady_state_synchronous_response_on_a_shaft(
        self: "CastSelf",
    ) -> "_3677.ZerolBevelGearSteadyStateSynchronousResponseOnAShaft":
        from mastapy._private.system_model.analyses_and_results.steady_state_synchronous_responses_on_a_shaft import (
            _3677,
        )

        return self.__parent__._cast(
            _3677.ZerolBevelGearSteadyStateSynchronousResponseOnAShaft
        )

    @property
    def mountable_component_steady_state_synchronous_response_on_a_shaft(
        self: "CastSelf",
    ) -> "MountableComponentSteadyStateSynchronousResponseOnAShaft":
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
class MountableComponentSteadyStateSynchronousResponseOnAShaft(
    _3571.ComponentSteadyStateSynchronousResponseOnAShaft
):
    """MountableComponentSteadyStateSynchronousResponseOnAShaft

    This is a mastapy class.
    """

    TYPE: ClassVar["Type"] = (
        _MOUNTABLE_COMPONENT_STEADY_STATE_SYNCHRONOUS_RESPONSE_ON_A_SHAFT
    )

    wrapped: "Any"

    def __post_init__(self: "Self") -> None:
        """Override of the post initialisation magic method."""
        if not hasattr(self.wrapped, "reference_count"):
            self.wrapped.reference_count = 0

        self.wrapped.reference_count += 1

    @property
    @exception_bridge
    def component_design(self: "Self") -> "_2737.MountableComponent":
        """mastapy.system_model.part_model.MountableComponent

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "ComponentDesign")

        if temp is None:
            return None

        type_ = temp.GetType()
        return constructor.new(type_.Namespace, type_.Name)(temp)

    @property
    def cast_to(
        self: "Self",
    ) -> "_Cast_MountableComponentSteadyStateSynchronousResponseOnAShaft":
        """Cast to another type.

        Returns:
            _Cast_MountableComponentSteadyStateSynchronousResponseOnAShaft
        """
        return _Cast_MountableComponentSteadyStateSynchronousResponseOnAShaft(self)
