"""SynchroniserPartSteadyStateSynchronousResponse"""

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
from mastapy._private.system_model.analyses_and_results.steady_state_synchronous_responses import (
    _3318,
)

_SYNCHRONISER_PART_STEADY_STATE_SYNCHRONOUS_RESPONSE = python_net_import(
    "SMT.MastaAPI.SystemModel.AnalysesAndResults.SteadyStateSynchronousResponses",
    "SynchroniserPartSteadyStateSynchronousResponse",
)

if TYPE_CHECKING:
    from typing import Any, Type, TypeVar

    from mastapy._private.system_model.analyses_and_results import _2943, _2945, _2949
    from mastapy._private.system_model.analyses_and_results.analysis_cases import (
        _7941,
        _7944,
    )
    from mastapy._private.system_model.analyses_and_results.steady_state_synchronous_responses import (
        _3305,
        _3360,
        _3362,
        _3399,
        _3401,
    )
    from mastapy._private.system_model.part_model.couplings import _2895

    Self = TypeVar("Self", bound="SynchroniserPartSteadyStateSynchronousResponse")
    CastSelf = TypeVar(
        "CastSelf",
        bound="SynchroniserPartSteadyStateSynchronousResponse._Cast_SynchroniserPartSteadyStateSynchronousResponse",
    )


__docformat__ = "restructuredtext en"
__all__ = ("SynchroniserPartSteadyStateSynchronousResponse",)


@extended_dataclass(frozen=True, slots=True, weakref_slot=True)
class _Cast_SynchroniserPartSteadyStateSynchronousResponse:
    """Special nested class for casting SynchroniserPartSteadyStateSynchronousResponse to subclasses."""

    __parent__: "SynchroniserPartSteadyStateSynchronousResponse"

    @property
    def coupling_half_steady_state_synchronous_response(
        self: "CastSelf",
    ) -> "_3318.CouplingHalfSteadyStateSynchronousResponse":
        return self.__parent__._cast(_3318.CouplingHalfSteadyStateSynchronousResponse)

    @property
    def mountable_component_steady_state_synchronous_response(
        self: "CastSelf",
    ) -> "_3360.MountableComponentSteadyStateSynchronousResponse":
        from mastapy._private.system_model.analyses_and_results.steady_state_synchronous_responses import (
            _3360,
        )

        return self.__parent__._cast(
            _3360.MountableComponentSteadyStateSynchronousResponse
        )

    @property
    def component_steady_state_synchronous_response(
        self: "CastSelf",
    ) -> "_3305.ComponentSteadyStateSynchronousResponse":
        from mastapy._private.system_model.analyses_and_results.steady_state_synchronous_responses import (
            _3305,
        )

        return self.__parent__._cast(_3305.ComponentSteadyStateSynchronousResponse)

    @property
    def part_steady_state_synchronous_response(
        self: "CastSelf",
    ) -> "_3362.PartSteadyStateSynchronousResponse":
        from mastapy._private.system_model.analyses_and_results.steady_state_synchronous_responses import (
            _3362,
        )

        return self.__parent__._cast(_3362.PartSteadyStateSynchronousResponse)

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
    def synchroniser_half_steady_state_synchronous_response(
        self: "CastSelf",
    ) -> "_3399.SynchroniserHalfSteadyStateSynchronousResponse":
        from mastapy._private.system_model.analyses_and_results.steady_state_synchronous_responses import (
            _3399,
        )

        return self.__parent__._cast(
            _3399.SynchroniserHalfSteadyStateSynchronousResponse
        )

    @property
    def synchroniser_sleeve_steady_state_synchronous_response(
        self: "CastSelf",
    ) -> "_3401.SynchroniserSleeveSteadyStateSynchronousResponse":
        from mastapy._private.system_model.analyses_and_results.steady_state_synchronous_responses import (
            _3401,
        )

        return self.__parent__._cast(
            _3401.SynchroniserSleeveSteadyStateSynchronousResponse
        )

    @property
    def synchroniser_part_steady_state_synchronous_response(
        self: "CastSelf",
    ) -> "SynchroniserPartSteadyStateSynchronousResponse":
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
class SynchroniserPartSteadyStateSynchronousResponse(
    _3318.CouplingHalfSteadyStateSynchronousResponse
):
    """SynchroniserPartSteadyStateSynchronousResponse

    This is a mastapy class.
    """

    TYPE: ClassVar["Type"] = _SYNCHRONISER_PART_STEADY_STATE_SYNCHRONOUS_RESPONSE

    wrapped: "Any"

    def __post_init__(self: "Self") -> None:
        """Override of the post initialisation magic method."""
        if not hasattr(self.wrapped, "reference_count"):
            self.wrapped.reference_count = 0

        self.wrapped.reference_count += 1

    @property
    @exception_bridge
    def component_design(self: "Self") -> "_2895.SynchroniserPart":
        """mastapy.system_model.part_model.couplings.SynchroniserPart

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "ComponentDesign")

        if temp is None:
            return None

        type_ = temp.GetType()
        return constructor.new(type_.Namespace, type_.Name)(temp)

    @property
    def cast_to(self: "Self") -> "_Cast_SynchroniserPartSteadyStateSynchronousResponse":
        """Cast to another type.

        Returns:
            _Cast_SynchroniserPartSteadyStateSynchronousResponse
        """
        return _Cast_SynchroniserPartSteadyStateSynchronousResponse(self)
