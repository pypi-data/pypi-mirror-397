"""KlingelnbergCycloPalloidHypoidGearCompoundSteadyStateSynchronousResponseOnAShaft"""

from __future__ import annotations

from typing import TYPE_CHECKING, ClassVar

from mastapy._private._internal.dataclasses import extended_dataclass
from mastapy._private._internal.exception_bridge import exception_bridge
from mastapy._private._internal.exceptions import CastException
from mastapy._private._internal.python_net import (
    python_net_import,
    pythonnet_property_get,
)

from mastapy._private._internal import constructor, conversion, utility
from mastapy._private.system_model.analyses_and_results.steady_state_synchronous_responses_on_a_shaft.compound import (
    _3744,
)

_KLINGELNBERG_CYCLO_PALLOID_HYPOID_GEAR_COMPOUND_STEADY_STATE_SYNCHRONOUS_RESPONSE_ON_A_SHAFT = python_net_import(
    "SMT.MastaAPI.SystemModel.AnalysesAndResults.SteadyStateSynchronousResponsesOnAShaft.Compound",
    "KlingelnbergCycloPalloidHypoidGearCompoundSteadyStateSynchronousResponseOnAShaft",
)

if TYPE_CHECKING:
    from typing import Any, List, Type, TypeVar

    from mastapy._private.system_model.analyses_and_results import _2943
    from mastapy._private.system_model.analyses_and_results.analysis_cases import (
        _7939,
        _7942,
    )
    from mastapy._private.system_model.analyses_and_results.steady_state_synchronous_responses_on_a_shaft import (
        _3617,
    )
    from mastapy._private.system_model.analyses_and_results.steady_state_synchronous_responses_on_a_shaft.compound import (
        _3703,
        _3710,
        _3736,
        _3757,
        _3759,
    )
    from mastapy._private.system_model.part_model.gears import _2819

    Self = TypeVar(
        "Self",
        bound="KlingelnbergCycloPalloidHypoidGearCompoundSteadyStateSynchronousResponseOnAShaft",
    )
    CastSelf = TypeVar(
        "CastSelf",
        bound="KlingelnbergCycloPalloidHypoidGearCompoundSteadyStateSynchronousResponseOnAShaft._Cast_KlingelnbergCycloPalloidHypoidGearCompoundSteadyStateSynchronousResponseOnAShaft",
    )


__docformat__ = "restructuredtext en"
__all__ = (
    "KlingelnbergCycloPalloidHypoidGearCompoundSteadyStateSynchronousResponseOnAShaft",
)


@extended_dataclass(frozen=True, slots=True, weakref_slot=True)
class _Cast_KlingelnbergCycloPalloidHypoidGearCompoundSteadyStateSynchronousResponseOnAShaft:
    """Special nested class for casting KlingelnbergCycloPalloidHypoidGearCompoundSteadyStateSynchronousResponseOnAShaft to subclasses."""

    __parent__: "KlingelnbergCycloPalloidHypoidGearCompoundSteadyStateSynchronousResponseOnAShaft"

    @property
    def klingelnberg_cyclo_palloid_conical_gear_compound_steady_state_synchronous_response_on_a_shaft(
        self: "CastSelf",
    ) -> "_3744.KlingelnbergCycloPalloidConicalGearCompoundSteadyStateSynchronousResponseOnAShaft":
        return self.__parent__._cast(
            _3744.KlingelnbergCycloPalloidConicalGearCompoundSteadyStateSynchronousResponseOnAShaft
        )

    @property
    def conical_gear_compound_steady_state_synchronous_response_on_a_shaft(
        self: "CastSelf",
    ) -> "_3710.ConicalGearCompoundSteadyStateSynchronousResponseOnAShaft":
        from mastapy._private.system_model.analyses_and_results.steady_state_synchronous_responses_on_a_shaft.compound import (
            _3710,
        )

        return self.__parent__._cast(
            _3710.ConicalGearCompoundSteadyStateSynchronousResponseOnAShaft
        )

    @property
    def gear_compound_steady_state_synchronous_response_on_a_shaft(
        self: "CastSelf",
    ) -> "_3736.GearCompoundSteadyStateSynchronousResponseOnAShaft":
        from mastapy._private.system_model.analyses_and_results.steady_state_synchronous_responses_on_a_shaft.compound import (
            _3736,
        )

        return self.__parent__._cast(
            _3736.GearCompoundSteadyStateSynchronousResponseOnAShaft
        )

    @property
    def mountable_component_compound_steady_state_synchronous_response_on_a_shaft(
        self: "CastSelf",
    ) -> "_3757.MountableComponentCompoundSteadyStateSynchronousResponseOnAShaft":
        from mastapy._private.system_model.analyses_and_results.steady_state_synchronous_responses_on_a_shaft.compound import (
            _3757,
        )

        return self.__parent__._cast(
            _3757.MountableComponentCompoundSteadyStateSynchronousResponseOnAShaft
        )

    @property
    def component_compound_steady_state_synchronous_response_on_a_shaft(
        self: "CastSelf",
    ) -> "_3703.ComponentCompoundSteadyStateSynchronousResponseOnAShaft":
        from mastapy._private.system_model.analyses_and_results.steady_state_synchronous_responses_on_a_shaft.compound import (
            _3703,
        )

        return self.__parent__._cast(
            _3703.ComponentCompoundSteadyStateSynchronousResponseOnAShaft
        )

    @property
    def part_compound_steady_state_synchronous_response_on_a_shaft(
        self: "CastSelf",
    ) -> "_3759.PartCompoundSteadyStateSynchronousResponseOnAShaft":
        from mastapy._private.system_model.analyses_and_results.steady_state_synchronous_responses_on_a_shaft.compound import (
            _3759,
        )

        return self.__parent__._cast(
            _3759.PartCompoundSteadyStateSynchronousResponseOnAShaft
        )

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
    def klingelnberg_cyclo_palloid_hypoid_gear_compound_steady_state_synchronous_response_on_a_shaft(
        self: "CastSelf",
    ) -> "KlingelnbergCycloPalloidHypoidGearCompoundSteadyStateSynchronousResponseOnAShaft":
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
class KlingelnbergCycloPalloidHypoidGearCompoundSteadyStateSynchronousResponseOnAShaft(
    _3744.KlingelnbergCycloPalloidConicalGearCompoundSteadyStateSynchronousResponseOnAShaft
):
    """KlingelnbergCycloPalloidHypoidGearCompoundSteadyStateSynchronousResponseOnAShaft

    This is a mastapy class.
    """

    TYPE: ClassVar["Type"] = (
        _KLINGELNBERG_CYCLO_PALLOID_HYPOID_GEAR_COMPOUND_STEADY_STATE_SYNCHRONOUS_RESPONSE_ON_A_SHAFT
    )

    wrapped: "Any"

    def __post_init__(self: "Self") -> None:
        """Override of the post initialisation magic method."""
        if not hasattr(self.wrapped, "reference_count"):
            self.wrapped.reference_count = 0

        self.wrapped.reference_count += 1

    @property
    @exception_bridge
    def component_design(self: "Self") -> "_2819.KlingelnbergCycloPalloidHypoidGear":
        """mastapy.system_model.part_model.gears.KlingelnbergCycloPalloidHypoidGear

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
    def component_analysis_cases_ready(
        self: "Self",
    ) -> "List[_3617.KlingelnbergCycloPalloidHypoidGearSteadyStateSynchronousResponseOnAShaft]":
        """List[mastapy.system_model.analyses_and_results.steady_state_synchronous_responses_on_a_shaft.KlingelnbergCycloPalloidHypoidGearSteadyStateSynchronousResponseOnAShaft]

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
    @exception_bridge
    def component_analysis_cases(
        self: "Self",
    ) -> "List[_3617.KlingelnbergCycloPalloidHypoidGearSteadyStateSynchronousResponseOnAShaft]":
        """List[mastapy.system_model.analyses_and_results.steady_state_synchronous_responses_on_a_shaft.KlingelnbergCycloPalloidHypoidGearSteadyStateSynchronousResponseOnAShaft]

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
    def cast_to(
        self: "Self",
    ) -> "_Cast_KlingelnbergCycloPalloidHypoidGearCompoundSteadyStateSynchronousResponseOnAShaft":
        """Cast to another type.

        Returns:
            _Cast_KlingelnbergCycloPalloidHypoidGearCompoundSteadyStateSynchronousResponseOnAShaft
        """
        return _Cast_KlingelnbergCycloPalloidHypoidGearCompoundSteadyStateSynchronousResponseOnAShaft(
            self
        )
