"""AGMAGleasonConicalGearMeshCriticalSpeedAnalysis"""

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
from mastapy._private.system_model.analyses_and_results.critical_speed_analyses import (
    _6944,
)

_AGMA_GLEASON_CONICAL_GEAR_MESH_CRITICAL_SPEED_ANALYSIS = python_net_import(
    "SMT.MastaAPI.SystemModel.AnalysesAndResults.CriticalSpeedAnalyses",
    "AGMAGleasonConicalGearMeshCriticalSpeedAnalysis",
)

if TYPE_CHECKING:
    from typing import Any, Type, TypeVar

    from mastapy._private.system_model.analyses_and_results import _2941, _2943, _2945
    from mastapy._private.system_model.analyses_and_results.analysis_cases import (
        _7934,
        _7937,
    )
    from mastapy._private.system_model.analyses_and_results.critical_speed_analyses import (
        _6923,
        _6928,
        _6946,
        _6973,
        _6977,
        _6979,
        _7016,
        _7022,
        _7025,
        _7043,
    )
    from mastapy._private.system_model.connections_and_sockets.gears import _2558

    Self = TypeVar("Self", bound="AGMAGleasonConicalGearMeshCriticalSpeedAnalysis")
    CastSelf = TypeVar(
        "CastSelf",
        bound="AGMAGleasonConicalGearMeshCriticalSpeedAnalysis._Cast_AGMAGleasonConicalGearMeshCriticalSpeedAnalysis",
    )


__docformat__ = "restructuredtext en"
__all__ = ("AGMAGleasonConicalGearMeshCriticalSpeedAnalysis",)


@extended_dataclass(frozen=True, slots=True, weakref_slot=True)
class _Cast_AGMAGleasonConicalGearMeshCriticalSpeedAnalysis:
    """Special nested class for casting AGMAGleasonConicalGearMeshCriticalSpeedAnalysis to subclasses."""

    __parent__: "AGMAGleasonConicalGearMeshCriticalSpeedAnalysis"

    @property
    def conical_gear_mesh_critical_speed_analysis(
        self: "CastSelf",
    ) -> "_6944.ConicalGearMeshCriticalSpeedAnalysis":
        return self.__parent__._cast(_6944.ConicalGearMeshCriticalSpeedAnalysis)

    @property
    def gear_mesh_critical_speed_analysis(
        self: "CastSelf",
    ) -> "_6973.GearMeshCriticalSpeedAnalysis":
        from mastapy._private.system_model.analyses_and_results.critical_speed_analyses import (
            _6973,
        )

        return self.__parent__._cast(_6973.GearMeshCriticalSpeedAnalysis)

    @property
    def inter_mountable_component_connection_critical_speed_analysis(
        self: "CastSelf",
    ) -> "_6979.InterMountableComponentConnectionCriticalSpeedAnalysis":
        from mastapy._private.system_model.analyses_and_results.critical_speed_analyses import (
            _6979,
        )

        return self.__parent__._cast(
            _6979.InterMountableComponentConnectionCriticalSpeedAnalysis
        )

    @property
    def connection_critical_speed_analysis(
        self: "CastSelf",
    ) -> "_6946.ConnectionCriticalSpeedAnalysis":
        from mastapy._private.system_model.analyses_and_results.critical_speed_analyses import (
            _6946,
        )

        return self.__parent__._cast(_6946.ConnectionCriticalSpeedAnalysis)

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
    def bevel_differential_gear_mesh_critical_speed_analysis(
        self: "CastSelf",
    ) -> "_6923.BevelDifferentialGearMeshCriticalSpeedAnalysis":
        from mastapy._private.system_model.analyses_and_results.critical_speed_analyses import (
            _6923,
        )

        return self.__parent__._cast(
            _6923.BevelDifferentialGearMeshCriticalSpeedAnalysis
        )

    @property
    def bevel_gear_mesh_critical_speed_analysis(
        self: "CastSelf",
    ) -> "_6928.BevelGearMeshCriticalSpeedAnalysis":
        from mastapy._private.system_model.analyses_and_results.critical_speed_analyses import (
            _6928,
        )

        return self.__parent__._cast(_6928.BevelGearMeshCriticalSpeedAnalysis)

    @property
    def hypoid_gear_mesh_critical_speed_analysis(
        self: "CastSelf",
    ) -> "_6977.HypoidGearMeshCriticalSpeedAnalysis":
        from mastapy._private.system_model.analyses_and_results.critical_speed_analyses import (
            _6977,
        )

        return self.__parent__._cast(_6977.HypoidGearMeshCriticalSpeedAnalysis)

    @property
    def spiral_bevel_gear_mesh_critical_speed_analysis(
        self: "CastSelf",
    ) -> "_7016.SpiralBevelGearMeshCriticalSpeedAnalysis":
        from mastapy._private.system_model.analyses_and_results.critical_speed_analyses import (
            _7016,
        )

        return self.__parent__._cast(_7016.SpiralBevelGearMeshCriticalSpeedAnalysis)

    @property
    def straight_bevel_diff_gear_mesh_critical_speed_analysis(
        self: "CastSelf",
    ) -> "_7022.StraightBevelDiffGearMeshCriticalSpeedAnalysis":
        from mastapy._private.system_model.analyses_and_results.critical_speed_analyses import (
            _7022,
        )

        return self.__parent__._cast(
            _7022.StraightBevelDiffGearMeshCriticalSpeedAnalysis
        )

    @property
    def straight_bevel_gear_mesh_critical_speed_analysis(
        self: "CastSelf",
    ) -> "_7025.StraightBevelGearMeshCriticalSpeedAnalysis":
        from mastapy._private.system_model.analyses_and_results.critical_speed_analyses import (
            _7025,
        )

        return self.__parent__._cast(_7025.StraightBevelGearMeshCriticalSpeedAnalysis)

    @property
    def zerol_bevel_gear_mesh_critical_speed_analysis(
        self: "CastSelf",
    ) -> "_7043.ZerolBevelGearMeshCriticalSpeedAnalysis":
        from mastapy._private.system_model.analyses_and_results.critical_speed_analyses import (
            _7043,
        )

        return self.__parent__._cast(_7043.ZerolBevelGearMeshCriticalSpeedAnalysis)

    @property
    def agma_gleason_conical_gear_mesh_critical_speed_analysis(
        self: "CastSelf",
    ) -> "AGMAGleasonConicalGearMeshCriticalSpeedAnalysis":
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
class AGMAGleasonConicalGearMeshCriticalSpeedAnalysis(
    _6944.ConicalGearMeshCriticalSpeedAnalysis
):
    """AGMAGleasonConicalGearMeshCriticalSpeedAnalysis

    This is a mastapy class.
    """

    TYPE: ClassVar["Type"] = _AGMA_GLEASON_CONICAL_GEAR_MESH_CRITICAL_SPEED_ANALYSIS

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
    ) -> "_Cast_AGMAGleasonConicalGearMeshCriticalSpeedAnalysis":
        """Cast to another type.

        Returns:
            _Cast_AGMAGleasonConicalGearMeshCriticalSpeedAnalysis
        """
        return _Cast_AGMAGleasonConicalGearMeshCriticalSpeedAnalysis(self)
