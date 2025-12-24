"""AGMAGleasonConicalGearMeshSteadyStateSynchronousResponseOnAShaft"""

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
    _3578,
)

_AGMA_GLEASON_CONICAL_GEAR_MESH_STEADY_STATE_SYNCHRONOUS_RESPONSE_ON_A_SHAFT = python_net_import(
    "SMT.MastaAPI.SystemModel.AnalysesAndResults.SteadyStateSynchronousResponsesOnAShaft",
    "AGMAGleasonConicalGearMeshSteadyStateSynchronousResponseOnAShaft",
)

if TYPE_CHECKING:
    from typing import Any, Type, TypeVar

    from mastapy._private.system_model.analyses_and_results import _2941, _2943, _2945
    from mastapy._private.system_model.analyses_and_results.analysis_cases import (
        _7934,
        _7937,
    )
    from mastapy._private.system_model.analyses_and_results.steady_state_synchronous_responses_on_a_shaft import (
        _3557,
        _3562,
        _3581,
        _3604,
        _3608,
        _3611,
        _3647,
        _3654,
        _3657,
        _3675,
    )
    from mastapy._private.system_model.connections_and_sockets.gears import _2558

    Self = TypeVar(
        "Self", bound="AGMAGleasonConicalGearMeshSteadyStateSynchronousResponseOnAShaft"
    )
    CastSelf = TypeVar(
        "CastSelf",
        bound="AGMAGleasonConicalGearMeshSteadyStateSynchronousResponseOnAShaft._Cast_AGMAGleasonConicalGearMeshSteadyStateSynchronousResponseOnAShaft",
    )


__docformat__ = "restructuredtext en"
__all__ = ("AGMAGleasonConicalGearMeshSteadyStateSynchronousResponseOnAShaft",)


@extended_dataclass(frozen=True, slots=True, weakref_slot=True)
class _Cast_AGMAGleasonConicalGearMeshSteadyStateSynchronousResponseOnAShaft:
    """Special nested class for casting AGMAGleasonConicalGearMeshSteadyStateSynchronousResponseOnAShaft to subclasses."""

    __parent__: "AGMAGleasonConicalGearMeshSteadyStateSynchronousResponseOnAShaft"

    @property
    def conical_gear_mesh_steady_state_synchronous_response_on_a_shaft(
        self: "CastSelf",
    ) -> "_3578.ConicalGearMeshSteadyStateSynchronousResponseOnAShaft":
        return self.__parent__._cast(
            _3578.ConicalGearMeshSteadyStateSynchronousResponseOnAShaft
        )

    @property
    def gear_mesh_steady_state_synchronous_response_on_a_shaft(
        self: "CastSelf",
    ) -> "_3604.GearMeshSteadyStateSynchronousResponseOnAShaft":
        from mastapy._private.system_model.analyses_and_results.steady_state_synchronous_responses_on_a_shaft import (
            _3604,
        )

        return self.__parent__._cast(
            _3604.GearMeshSteadyStateSynchronousResponseOnAShaft
        )

    @property
    def inter_mountable_component_connection_steady_state_synchronous_response_on_a_shaft(
        self: "CastSelf",
    ) -> (
        "_3611.InterMountableComponentConnectionSteadyStateSynchronousResponseOnAShaft"
    ):
        from mastapy._private.system_model.analyses_and_results.steady_state_synchronous_responses_on_a_shaft import (
            _3611,
        )

        return self.__parent__._cast(
            _3611.InterMountableComponentConnectionSteadyStateSynchronousResponseOnAShaft
        )

    @property
    def connection_steady_state_synchronous_response_on_a_shaft(
        self: "CastSelf",
    ) -> "_3581.ConnectionSteadyStateSynchronousResponseOnAShaft":
        from mastapy._private.system_model.analyses_and_results.steady_state_synchronous_responses_on_a_shaft import (
            _3581,
        )

        return self.__parent__._cast(
            _3581.ConnectionSteadyStateSynchronousResponseOnAShaft
        )

    @property
    def connection_static_load_analysis_case(
        self: "CastSelf",
    ) -> "_7937.ConnectionStaticLoadAnalysisCase":
        from mastapy._private.system_model.analyses_and_results.analysis_cases import (
            _7937,
        )

        return self.__parent__._cast(_7937.ConnectionStaticLoadAnalysisCase)

    @property
    def connection_analysis_case(self: "CastSelf") -> "_7934.ConnectionAnalysisCase":
        from mastapy._private.system_model.analyses_and_results.analysis_cases import (
            _7934,
        )

        return self.__parent__._cast(_7934.ConnectionAnalysisCase)

    @property
    def connection_analysis(self: "CastSelf") -> "_2941.ConnectionAnalysis":
        from mastapy._private.system_model.analyses_and_results import _2941

        return self.__parent__._cast(_2941.ConnectionAnalysis)

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
    def bevel_differential_gear_mesh_steady_state_synchronous_response_on_a_shaft(
        self: "CastSelf",
    ) -> "_3557.BevelDifferentialGearMeshSteadyStateSynchronousResponseOnAShaft":
        from mastapy._private.system_model.analyses_and_results.steady_state_synchronous_responses_on_a_shaft import (
            _3557,
        )

        return self.__parent__._cast(
            _3557.BevelDifferentialGearMeshSteadyStateSynchronousResponseOnAShaft
        )

    @property
    def bevel_gear_mesh_steady_state_synchronous_response_on_a_shaft(
        self: "CastSelf",
    ) -> "_3562.BevelGearMeshSteadyStateSynchronousResponseOnAShaft":
        from mastapy._private.system_model.analyses_and_results.steady_state_synchronous_responses_on_a_shaft import (
            _3562,
        )

        return self.__parent__._cast(
            _3562.BevelGearMeshSteadyStateSynchronousResponseOnAShaft
        )

    @property
    def hypoid_gear_mesh_steady_state_synchronous_response_on_a_shaft(
        self: "CastSelf",
    ) -> "_3608.HypoidGearMeshSteadyStateSynchronousResponseOnAShaft":
        from mastapy._private.system_model.analyses_and_results.steady_state_synchronous_responses_on_a_shaft import (
            _3608,
        )

        return self.__parent__._cast(
            _3608.HypoidGearMeshSteadyStateSynchronousResponseOnAShaft
        )

    @property
    def spiral_bevel_gear_mesh_steady_state_synchronous_response_on_a_shaft(
        self: "CastSelf",
    ) -> "_3647.SpiralBevelGearMeshSteadyStateSynchronousResponseOnAShaft":
        from mastapy._private.system_model.analyses_and_results.steady_state_synchronous_responses_on_a_shaft import (
            _3647,
        )

        return self.__parent__._cast(
            _3647.SpiralBevelGearMeshSteadyStateSynchronousResponseOnAShaft
        )

    @property
    def straight_bevel_diff_gear_mesh_steady_state_synchronous_response_on_a_shaft(
        self: "CastSelf",
    ) -> "_3654.StraightBevelDiffGearMeshSteadyStateSynchronousResponseOnAShaft":
        from mastapy._private.system_model.analyses_and_results.steady_state_synchronous_responses_on_a_shaft import (
            _3654,
        )

        return self.__parent__._cast(
            _3654.StraightBevelDiffGearMeshSteadyStateSynchronousResponseOnAShaft
        )

    @property
    def straight_bevel_gear_mesh_steady_state_synchronous_response_on_a_shaft(
        self: "CastSelf",
    ) -> "_3657.StraightBevelGearMeshSteadyStateSynchronousResponseOnAShaft":
        from mastapy._private.system_model.analyses_and_results.steady_state_synchronous_responses_on_a_shaft import (
            _3657,
        )

        return self.__parent__._cast(
            _3657.StraightBevelGearMeshSteadyStateSynchronousResponseOnAShaft
        )

    @property
    def zerol_bevel_gear_mesh_steady_state_synchronous_response_on_a_shaft(
        self: "CastSelf",
    ) -> "_3675.ZerolBevelGearMeshSteadyStateSynchronousResponseOnAShaft":
        from mastapy._private.system_model.analyses_and_results.steady_state_synchronous_responses_on_a_shaft import (
            _3675,
        )

        return self.__parent__._cast(
            _3675.ZerolBevelGearMeshSteadyStateSynchronousResponseOnAShaft
        )

    @property
    def agma_gleason_conical_gear_mesh_steady_state_synchronous_response_on_a_shaft(
        self: "CastSelf",
    ) -> "AGMAGleasonConicalGearMeshSteadyStateSynchronousResponseOnAShaft":
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
class AGMAGleasonConicalGearMeshSteadyStateSynchronousResponseOnAShaft(
    _3578.ConicalGearMeshSteadyStateSynchronousResponseOnAShaft
):
    """AGMAGleasonConicalGearMeshSteadyStateSynchronousResponseOnAShaft

    This is a mastapy class.
    """

    TYPE: ClassVar["Type"] = (
        _AGMA_GLEASON_CONICAL_GEAR_MESH_STEADY_STATE_SYNCHRONOUS_RESPONSE_ON_A_SHAFT
    )

    wrapped: "Any"

    def __post_init__(self: "Self") -> None:
        """Override of the post initialisation magic method."""
        if not hasattr(self.wrapped, "reference_count"):
            self.wrapped.reference_count = 0

        self.wrapped.reference_count += 1

    @property
    @exception_bridge
    def connection_design(self: "Self") -> "_2558.AGMAGleasonConicalGearMesh":
        """mastapy.system_model.connections_and_sockets.gears.AGMAGleasonConicalGearMesh

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "ConnectionDesign")

        if temp is None:
            return None

        type_ = temp.GetType()
        return constructor.new(type_.Namespace, type_.Name)(temp)

    @property
    def cast_to(
        self: "Self",
    ) -> "_Cast_AGMAGleasonConicalGearMeshSteadyStateSynchronousResponseOnAShaft":
        """Cast to another type.

        Returns:
            _Cast_AGMAGleasonConicalGearMeshSteadyStateSynchronousResponseOnAShaft
        """
        return _Cast_AGMAGleasonConicalGearMeshSteadyStateSynchronousResponseOnAShaft(
            self
        )
