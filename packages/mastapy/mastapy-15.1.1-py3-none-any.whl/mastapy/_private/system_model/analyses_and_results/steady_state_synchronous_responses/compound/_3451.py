"""ConnectorCompoundSteadyStateSynchronousResponse"""

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
    _3494,
)

_CONNECTOR_COMPOUND_STEADY_STATE_SYNCHRONOUS_RESPONSE = python_net_import(
    "SMT.MastaAPI.SystemModel.AnalysesAndResults.SteadyStateSynchronousResponses.Compound",
    "ConnectorCompoundSteadyStateSynchronousResponse",
)

if TYPE_CHECKING:
    from typing import Any, List, Type, TypeVar

    from mastapy._private.system_model.analyses_and_results import _2943
    from mastapy._private.system_model.analyses_and_results.analysis_cases import (
        _7939,
        _7942,
    )
    from mastapy._private.system_model.analyses_and_results.steady_state_synchronous_responses import (
        _3316,
    )
    from mastapy._private.system_model.analyses_and_results.steady_state_synchronous_responses.compound import (
        _3423,
        _3440,
        _3495,
        _3496,
        _3513,
    )

    Self = TypeVar("Self", bound="ConnectorCompoundSteadyStateSynchronousResponse")
    CastSelf = TypeVar(
        "CastSelf",
        bound="ConnectorCompoundSteadyStateSynchronousResponse._Cast_ConnectorCompoundSteadyStateSynchronousResponse",
    )


__docformat__ = "restructuredtext en"
__all__ = ("ConnectorCompoundSteadyStateSynchronousResponse",)


@extended_dataclass(frozen=True, slots=True, weakref_slot=True)
class _Cast_ConnectorCompoundSteadyStateSynchronousResponse:
    """Special nested class for casting ConnectorCompoundSteadyStateSynchronousResponse to subclasses."""

    __parent__: "ConnectorCompoundSteadyStateSynchronousResponse"

    @property
    def mountable_component_compound_steady_state_synchronous_response(
        self: "CastSelf",
    ) -> "_3494.MountableComponentCompoundSteadyStateSynchronousResponse":
        return self.__parent__._cast(
            _3494.MountableComponentCompoundSteadyStateSynchronousResponse
        )

    @property
    def component_compound_steady_state_synchronous_response(
        self: "CastSelf",
    ) -> "_3440.ComponentCompoundSteadyStateSynchronousResponse":
        from mastapy._private.system_model.analyses_and_results.steady_state_synchronous_responses.compound import (
            _3440,
        )

        return self.__parent__._cast(
            _3440.ComponentCompoundSteadyStateSynchronousResponse
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
    def bearing_compound_steady_state_synchronous_response(
        self: "CastSelf",
    ) -> "_3423.BearingCompoundSteadyStateSynchronousResponse":
        from mastapy._private.system_model.analyses_and_results.steady_state_synchronous_responses.compound import (
            _3423,
        )

        return self.__parent__._cast(
            _3423.BearingCompoundSteadyStateSynchronousResponse
        )

    @property
    def oil_seal_compound_steady_state_synchronous_response(
        self: "CastSelf",
    ) -> "_3495.OilSealCompoundSteadyStateSynchronousResponse":
        from mastapy._private.system_model.analyses_and_results.steady_state_synchronous_responses.compound import (
            _3495,
        )

        return self.__parent__._cast(
            _3495.OilSealCompoundSteadyStateSynchronousResponse
        )

    @property
    def shaft_hub_connection_compound_steady_state_synchronous_response(
        self: "CastSelf",
    ) -> "_3513.ShaftHubConnectionCompoundSteadyStateSynchronousResponse":
        from mastapy._private.system_model.analyses_and_results.steady_state_synchronous_responses.compound import (
            _3513,
        )

        return self.__parent__._cast(
            _3513.ShaftHubConnectionCompoundSteadyStateSynchronousResponse
        )

    @property
    def connector_compound_steady_state_synchronous_response(
        self: "CastSelf",
    ) -> "ConnectorCompoundSteadyStateSynchronousResponse":
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
class ConnectorCompoundSteadyStateSynchronousResponse(
    _3494.MountableComponentCompoundSteadyStateSynchronousResponse
):
    """ConnectorCompoundSteadyStateSynchronousResponse

    This is a mastapy class.
    """

    TYPE: ClassVar["Type"] = _CONNECTOR_COMPOUND_STEADY_STATE_SYNCHRONOUS_RESPONSE

    wrapped: "Any"

    def __post_init__(self: "Self") -> None:
        """Override of the post initialisation magic method."""
        if not hasattr(self.wrapped, "reference_count"):
            self.wrapped.reference_count = 0

        self.wrapped.reference_count += 1

    @property
    @exception_bridge
    def component_analysis_cases(
        self: "Self",
    ) -> "List[_3316.ConnectorSteadyStateSynchronousResponse]":
        """List[mastapy.system_model.analyses_and_results.steady_state_synchronous_responses.ConnectorSteadyStateSynchronousResponse]

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
    @exception_bridge
    def component_analysis_cases_ready(
        self: "Self",
    ) -> "List[_3316.ConnectorSteadyStateSynchronousResponse]":
        """List[mastapy.system_model.analyses_and_results.steady_state_synchronous_responses.ConnectorSteadyStateSynchronousResponse]

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
    def cast_to(
        self: "Self",
    ) -> "_Cast_ConnectorCompoundSteadyStateSynchronousResponse":
        """Cast to another type.

        Returns:
            _Cast_ConnectorCompoundSteadyStateSynchronousResponse
        """
        return _Cast_ConnectorCompoundSteadyStateSynchronousResponse(self)
