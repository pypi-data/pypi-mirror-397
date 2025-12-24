"""KlingelnbergCycloPalloidConicalGearSetCompoundSteadyStateSynchronousResponse"""

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
from mastapy._private.system_model.analyses_and_results.steady_state_synchronous_responses.compound import (
    _3449,
)

_KLINGELNBERG_CYCLO_PALLOID_CONICAL_GEAR_SET_COMPOUND_STEADY_STATE_SYNCHRONOUS_RESPONSE = python_net_import(
    "SMT.MastaAPI.SystemModel.AnalysesAndResults.SteadyStateSynchronousResponses.Compound",
    "KlingelnbergCycloPalloidConicalGearSetCompoundSteadyStateSynchronousResponse",
)

if TYPE_CHECKING:
    from typing import Any, List, Type, TypeVar

    from mastapy._private.system_model.analyses_and_results import _2943
    from mastapy._private.system_model.analyses_and_results.analysis_cases import (
        _7939,
        _7942,
    )
    from mastapy._private.system_model.analyses_and_results.steady_state_synchronous_responses import (
        _3348,
    )
    from mastapy._private.system_model.analyses_and_results.steady_state_synchronous_responses.compound import (
        _3415,
        _3475,
        _3486,
        _3489,
        _3496,
        _3515,
    )

    Self = TypeVar(
        "Self",
        bound="KlingelnbergCycloPalloidConicalGearSetCompoundSteadyStateSynchronousResponse",
    )
    CastSelf = TypeVar(
        "CastSelf",
        bound="KlingelnbergCycloPalloidConicalGearSetCompoundSteadyStateSynchronousResponse._Cast_KlingelnbergCycloPalloidConicalGearSetCompoundSteadyStateSynchronousResponse",
    )


__docformat__ = "restructuredtext en"
__all__ = (
    "KlingelnbergCycloPalloidConicalGearSetCompoundSteadyStateSynchronousResponse",
)


@extended_dataclass(frozen=True, slots=True, weakref_slot=True)
class _Cast_KlingelnbergCycloPalloidConicalGearSetCompoundSteadyStateSynchronousResponse:
    """Special nested class for casting KlingelnbergCycloPalloidConicalGearSetCompoundSteadyStateSynchronousResponse to subclasses."""

    __parent__: (
        "KlingelnbergCycloPalloidConicalGearSetCompoundSteadyStateSynchronousResponse"
    )

    @property
    def conical_gear_set_compound_steady_state_synchronous_response(
        self: "CastSelf",
    ) -> "_3449.ConicalGearSetCompoundSteadyStateSynchronousResponse":
        return self.__parent__._cast(
            _3449.ConicalGearSetCompoundSteadyStateSynchronousResponse
        )

    @property
    def gear_set_compound_steady_state_synchronous_response(
        self: "CastSelf",
    ) -> "_3475.GearSetCompoundSteadyStateSynchronousResponse":
        from mastapy._private.system_model.analyses_and_results.steady_state_synchronous_responses.compound import (
            _3475,
        )

        return self.__parent__._cast(
            _3475.GearSetCompoundSteadyStateSynchronousResponse
        )

    @property
    def specialised_assembly_compound_steady_state_synchronous_response(
        self: "CastSelf",
    ) -> "_3515.SpecialisedAssemblyCompoundSteadyStateSynchronousResponse":
        from mastapy._private.system_model.analyses_and_results.steady_state_synchronous_responses.compound import (
            _3515,
        )

        return self.__parent__._cast(
            _3515.SpecialisedAssemblyCompoundSteadyStateSynchronousResponse
        )

    @property
    def abstract_assembly_compound_steady_state_synchronous_response(
        self: "CastSelf",
    ) -> "_3415.AbstractAssemblyCompoundSteadyStateSynchronousResponse":
        from mastapy._private.system_model.analyses_and_results.steady_state_synchronous_responses.compound import (
            _3415,
        )

        return self.__parent__._cast(
            _3415.AbstractAssemblyCompoundSteadyStateSynchronousResponse
        )

    @property
    def part_compound_steady_state_synchronous_response(
        self: "CastSelf",
    ) -> "_3496.PartCompoundSteadyStateSynchronousResponse":
        from mastapy._private.system_model.analyses_and_results.steady_state_synchronous_responses.compound import (
            _3496,
        )

        return self.__parent__._cast(_3496.PartCompoundSteadyStateSynchronousResponse)

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
    def klingelnberg_cyclo_palloid_hypoid_gear_set_compound_steady_state_synchronous_response(
        self: "CastSelf",
    ) -> "_3486.KlingelnbergCycloPalloidHypoidGearSetCompoundSteadyStateSynchronousResponse":
        from mastapy._private.system_model.analyses_and_results.steady_state_synchronous_responses.compound import (
            _3486,
        )

        return self.__parent__._cast(
            _3486.KlingelnbergCycloPalloidHypoidGearSetCompoundSteadyStateSynchronousResponse
        )

    @property
    def klingelnberg_cyclo_palloid_spiral_bevel_gear_set_compound_steady_state_synchronous_response(
        self: "CastSelf",
    ) -> "_3489.KlingelnbergCycloPalloidSpiralBevelGearSetCompoundSteadyStateSynchronousResponse":
        from mastapy._private.system_model.analyses_and_results.steady_state_synchronous_responses.compound import (
            _3489,
        )

        return self.__parent__._cast(
            _3489.KlingelnbergCycloPalloidSpiralBevelGearSetCompoundSteadyStateSynchronousResponse
        )

    @property
    def klingelnberg_cyclo_palloid_conical_gear_set_compound_steady_state_synchronous_response(
        self: "CastSelf",
    ) -> "KlingelnbergCycloPalloidConicalGearSetCompoundSteadyStateSynchronousResponse":
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
class KlingelnbergCycloPalloidConicalGearSetCompoundSteadyStateSynchronousResponse(
    _3449.ConicalGearSetCompoundSteadyStateSynchronousResponse
):
    """KlingelnbergCycloPalloidConicalGearSetCompoundSteadyStateSynchronousResponse

    This is a mastapy class.
    """

    TYPE: ClassVar["Type"] = (
        _KLINGELNBERG_CYCLO_PALLOID_CONICAL_GEAR_SET_COMPOUND_STEADY_STATE_SYNCHRONOUS_RESPONSE
    )

    wrapped: "Any"

    def __post_init__(self: "Self") -> None:
        """Override of the post initialisation magic method."""
        if not hasattr(self.wrapped, "reference_count"):
            self.wrapped.reference_count = 0

        self.wrapped.reference_count += 1

    @property
    @exception_bridge
    def assembly_analysis_cases(
        self: "Self",
    ) -> "List[_3348.KlingelnbergCycloPalloidConicalGearSetSteadyStateSynchronousResponse]":
        """List[mastapy.system_model.analyses_and_results.steady_state_synchronous_responses.KlingelnbergCycloPalloidConicalGearSetSteadyStateSynchronousResponse]

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "AssemblyAnalysisCases")

        if temp is None:
            return None

        value = conversion.pn_to_mp_objects_in_list(temp)

        if value is None:
            return None

        return value

    @property
    @exception_bridge
    def assembly_analysis_cases_ready(
        self: "Self",
    ) -> "List[_3348.KlingelnbergCycloPalloidConicalGearSetSteadyStateSynchronousResponse]":
        """List[mastapy.system_model.analyses_and_results.steady_state_synchronous_responses.KlingelnbergCycloPalloidConicalGearSetSteadyStateSynchronousResponse]

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "AssemblyAnalysisCasesReady")

        if temp is None:
            return None

        value = conversion.pn_to_mp_objects_in_list(temp)

        if value is None:
            return None

        return value

    @property
    def cast_to(
        self: "Self",
    ) -> "_Cast_KlingelnbergCycloPalloidConicalGearSetCompoundSteadyStateSynchronousResponse":
        """Cast to another type.

        Returns:
            _Cast_KlingelnbergCycloPalloidConicalGearSetCompoundSteadyStateSynchronousResponse
        """
        return _Cast_KlingelnbergCycloPalloidConicalGearSetCompoundSteadyStateSynchronousResponse(
            self
        )
