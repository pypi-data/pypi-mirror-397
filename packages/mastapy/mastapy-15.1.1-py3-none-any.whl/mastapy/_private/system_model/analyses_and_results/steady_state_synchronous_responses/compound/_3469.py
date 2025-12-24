"""FaceGearMeshCompoundSteadyStateSynchronousResponse"""

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
from mastapy._private.system_model.analyses_and_results.steady_state_synchronous_responses.compound import (
    _3474,
)

_FACE_GEAR_MESH_COMPOUND_STEADY_STATE_SYNCHRONOUS_RESPONSE = python_net_import(
    "SMT.MastaAPI.SystemModel.AnalysesAndResults.SteadyStateSynchronousResponses.Compound",
    "FaceGearMeshCompoundSteadyStateSynchronousResponse",
)

if TYPE_CHECKING:
    from typing import Any, List, Type, TypeVar

    from mastapy._private.system_model.analyses_and_results import _2943
    from mastapy._private.system_model.analyses_and_results.analysis_cases import (
        _7935,
        _7939,
    )
    from mastapy._private.system_model.analyses_and_results.steady_state_synchronous_responses import (
        _3334,
    )
    from mastapy._private.system_model.analyses_and_results.steady_state_synchronous_responses.compound import (
        _3450,
        _3480,
    )
    from mastapy._private.system_model.connections_and_sockets.gears import _2570

    Self = TypeVar("Self", bound="FaceGearMeshCompoundSteadyStateSynchronousResponse")
    CastSelf = TypeVar(
        "CastSelf",
        bound="FaceGearMeshCompoundSteadyStateSynchronousResponse._Cast_FaceGearMeshCompoundSteadyStateSynchronousResponse",
    )


__docformat__ = "restructuredtext en"
__all__ = ("FaceGearMeshCompoundSteadyStateSynchronousResponse",)


@extended_dataclass(frozen=True, slots=True, weakref_slot=True)
class _Cast_FaceGearMeshCompoundSteadyStateSynchronousResponse:
    """Special nested class for casting FaceGearMeshCompoundSteadyStateSynchronousResponse to subclasses."""

    __parent__: "FaceGearMeshCompoundSteadyStateSynchronousResponse"

    @property
    def gear_mesh_compound_steady_state_synchronous_response(
        self: "CastSelf",
    ) -> "_3474.GearMeshCompoundSteadyStateSynchronousResponse":
        return self.__parent__._cast(
            _3474.GearMeshCompoundSteadyStateSynchronousResponse
        )

    @property
    def inter_mountable_component_connection_compound_steady_state_synchronous_response(
        self: "CastSelf",
    ) -> (
        "_3480.InterMountableComponentConnectionCompoundSteadyStateSynchronousResponse"
    ):
        from mastapy._private.system_model.analyses_and_results.steady_state_synchronous_responses.compound import (
            _3480,
        )

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
    def face_gear_mesh_compound_steady_state_synchronous_response(
        self: "CastSelf",
    ) -> "FaceGearMeshCompoundSteadyStateSynchronousResponse":
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
class FaceGearMeshCompoundSteadyStateSynchronousResponse(
    _3474.GearMeshCompoundSteadyStateSynchronousResponse
):
    """FaceGearMeshCompoundSteadyStateSynchronousResponse

    This is a mastapy class.
    """

    TYPE: ClassVar["Type"] = _FACE_GEAR_MESH_COMPOUND_STEADY_STATE_SYNCHRONOUS_RESPONSE

    wrapped: "Any"

    def __post_init__(self: "Self") -> None:
        """Override of the post initialisation magic method."""
        if not hasattr(self.wrapped, "reference_count"):
            self.wrapped.reference_count = 0

        self.wrapped.reference_count += 1

    @property
    @exception_bridge
    def component_design(self: "Self") -> "_2570.FaceGearMesh":
        """mastapy.system_model.connections_and_sockets.gears.FaceGearMesh

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
    def connection_design(self: "Self") -> "_2570.FaceGearMesh":
        """mastapy.system_model.connections_and_sockets.gears.FaceGearMesh

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "ConnectionDesign")

        if temp is None:
            return None

        type_ = temp.GetType()
        return constructor.new(type_.Namespace, type_.Name)(temp)

    @property
    @exception_bridge
    def connection_analysis_cases_ready(
        self: "Self",
    ) -> "List[_3334.FaceGearMeshSteadyStateSynchronousResponse]":
        """List[mastapy.system_model.analyses_and_results.steady_state_synchronous_responses.FaceGearMeshSteadyStateSynchronousResponse]

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
    @exception_bridge
    def connection_analysis_cases(
        self: "Self",
    ) -> "List[_3334.FaceGearMeshSteadyStateSynchronousResponse]":
        """List[mastapy.system_model.analyses_and_results.steady_state_synchronous_responses.FaceGearMeshSteadyStateSynchronousResponse]

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
    def cast_to(
        self: "Self",
    ) -> "_Cast_FaceGearMeshCompoundSteadyStateSynchronousResponse":
        """Cast to another type.

        Returns:
            _Cast_FaceGearMeshCompoundSteadyStateSynchronousResponse
        """
        return _Cast_FaceGearMeshCompoundSteadyStateSynchronousResponse(self)
