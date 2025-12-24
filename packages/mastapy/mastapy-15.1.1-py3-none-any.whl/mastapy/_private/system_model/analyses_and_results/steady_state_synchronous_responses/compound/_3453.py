"""CouplingConnectionCompoundSteadyStateSynchronousResponse"""

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
    _3480,
)

_COUPLING_CONNECTION_COMPOUND_STEADY_STATE_SYNCHRONOUS_RESPONSE = python_net_import(
    "SMT.MastaAPI.SystemModel.AnalysesAndResults.SteadyStateSynchronousResponses.Compound",
    "CouplingConnectionCompoundSteadyStateSynchronousResponse",
)

if TYPE_CHECKING:
    from typing import Any, List, Type, TypeVar

    from mastapy._private.system_model.analyses_and_results import _2943
    from mastapy._private.system_model.analyses_and_results.analysis_cases import (
        _7935,
        _7939,
    )
    from mastapy._private.system_model.analyses_and_results.steady_state_synchronous_responses import (
        _3317,
    )
    from mastapy._private.system_model.analyses_and_results.steady_state_synchronous_responses.compound import (
        _3437,
        _3442,
        _3450,
        _3498,
        _3520,
        _3535,
    )

    Self = TypeVar(
        "Self", bound="CouplingConnectionCompoundSteadyStateSynchronousResponse"
    )
    CastSelf = TypeVar(
        "CastSelf",
        bound="CouplingConnectionCompoundSteadyStateSynchronousResponse._Cast_CouplingConnectionCompoundSteadyStateSynchronousResponse",
    )


__docformat__ = "restructuredtext en"
__all__ = ("CouplingConnectionCompoundSteadyStateSynchronousResponse",)


@extended_dataclass(frozen=True, slots=True, weakref_slot=True)
class _Cast_CouplingConnectionCompoundSteadyStateSynchronousResponse:
    """Special nested class for casting CouplingConnectionCompoundSteadyStateSynchronousResponse to subclasses."""

    __parent__: "CouplingConnectionCompoundSteadyStateSynchronousResponse"

    @property
    def inter_mountable_component_connection_compound_steady_state_synchronous_response(
        self: "CastSelf",
    ) -> (
        "_3480.InterMountableComponentConnectionCompoundSteadyStateSynchronousResponse"
    ):
        return self.__parent__._cast(
            _3480.InterMountableComponentConnectionCompoundSteadyStateSynchronousResponse
        )

    @property
    def connection_compound_steady_state_synchronous_response(
        self: "CastSelf",
    ) -> "_3450.ConnectionCompoundSteadyStateSynchronousResponse":
        from mastapy._private.system_model.analyses_and_results.steady_state_synchronous_responses.compound import (
            _3450,
        )

        return self.__parent__._cast(
            _3450.ConnectionCompoundSteadyStateSynchronousResponse
        )

    @property
    def connection_compound_analysis(
        self: "CastSelf",
    ) -> "_7935.ConnectionCompoundAnalysis":
        from mastapy._private.system_model.analyses_and_results.analysis_cases import (
            _7935,
        )

        return self.__parent__._cast(_7935.ConnectionCompoundAnalysis)

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
    def clutch_connection_compound_steady_state_synchronous_response(
        self: "CastSelf",
    ) -> "_3437.ClutchConnectionCompoundSteadyStateSynchronousResponse":
        from mastapy._private.system_model.analyses_and_results.steady_state_synchronous_responses.compound import (
            _3437,
        )

        return self.__parent__._cast(
            _3437.ClutchConnectionCompoundSteadyStateSynchronousResponse
        )

    @property
    def concept_coupling_connection_compound_steady_state_synchronous_response(
        self: "CastSelf",
    ) -> "_3442.ConceptCouplingConnectionCompoundSteadyStateSynchronousResponse":
        from mastapy._private.system_model.analyses_and_results.steady_state_synchronous_responses.compound import (
            _3442,
        )

        return self.__parent__._cast(
            _3442.ConceptCouplingConnectionCompoundSteadyStateSynchronousResponse
        )

    @property
    def part_to_part_shear_coupling_connection_compound_steady_state_synchronous_response(
        self: "CastSelf",
    ) -> (
        "_3498.PartToPartShearCouplingConnectionCompoundSteadyStateSynchronousResponse"
    ):
        from mastapy._private.system_model.analyses_and_results.steady_state_synchronous_responses.compound import (
            _3498,
        )

        return self.__parent__._cast(
            _3498.PartToPartShearCouplingConnectionCompoundSteadyStateSynchronousResponse
        )

    @property
    def spring_damper_connection_compound_steady_state_synchronous_response(
        self: "CastSelf",
    ) -> "_3520.SpringDamperConnectionCompoundSteadyStateSynchronousResponse":
        from mastapy._private.system_model.analyses_and_results.steady_state_synchronous_responses.compound import (
            _3520,
        )

        return self.__parent__._cast(
            _3520.SpringDamperConnectionCompoundSteadyStateSynchronousResponse
        )

    @property
    def torque_converter_connection_compound_steady_state_synchronous_response(
        self: "CastSelf",
    ) -> "_3535.TorqueConverterConnectionCompoundSteadyStateSynchronousResponse":
        from mastapy._private.system_model.analyses_and_results.steady_state_synchronous_responses.compound import (
            _3535,
        )

        return self.__parent__._cast(
            _3535.TorqueConverterConnectionCompoundSteadyStateSynchronousResponse
        )

    @property
    def coupling_connection_compound_steady_state_synchronous_response(
        self: "CastSelf",
    ) -> "CouplingConnectionCompoundSteadyStateSynchronousResponse":
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
class CouplingConnectionCompoundSteadyStateSynchronousResponse(
    _3480.InterMountableComponentConnectionCompoundSteadyStateSynchronousResponse
):
    """CouplingConnectionCompoundSteadyStateSynchronousResponse

    This is a mastapy class.
    """

    TYPE: ClassVar["Type"] = (
        _COUPLING_CONNECTION_COMPOUND_STEADY_STATE_SYNCHRONOUS_RESPONSE
    )

    wrapped: "Any"

    def __post_init__(self: "Self") -> None:
        """Override of the post initialisation magic method."""
        if not hasattr(self.wrapped, "reference_count"):
            self.wrapped.reference_count = 0

        self.wrapped.reference_count += 1

    @property
    @exception_bridge
    def connection_analysis_cases(
        self: "Self",
    ) -> "List[_3317.CouplingConnectionSteadyStateSynchronousResponse]":
        """List[mastapy.system_model.analyses_and_results.steady_state_synchronous_responses.CouplingConnectionSteadyStateSynchronousResponse]

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "ConnectionAnalysisCases")

        if temp is None:
            return None

        value = conversion.pn_to_mp_objects_in_list(temp)

        if value is None:
            return None

        return value

    @property
    @exception_bridge
    def connection_analysis_cases_ready(
        self: "Self",
    ) -> "List[_3317.CouplingConnectionSteadyStateSynchronousResponse]":
        """List[mastapy.system_model.analyses_and_results.steady_state_synchronous_responses.CouplingConnectionSteadyStateSynchronousResponse]

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "ConnectionAnalysisCasesReady")

        if temp is None:
            return None

        value = conversion.pn_to_mp_objects_in_list(temp)

        if value is None:
            return None

        return value

    @property
    def cast_to(
        self: "Self",
    ) -> "_Cast_CouplingConnectionCompoundSteadyStateSynchronousResponse":
        """Cast to another type.

        Returns:
            _Cast_CouplingConnectionCompoundSteadyStateSynchronousResponse
        """
        return _Cast_CouplingConnectionCompoundSteadyStateSynchronousResponse(self)
