"""BevelGearMeshMultibodyDynamicsAnalysis"""

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
from mastapy._private.system_model.analyses_and_results.mbd_analyses import _5715

_BEVEL_GEAR_MESH_MULTIBODY_DYNAMICS_ANALYSIS = python_net_import(
    "SMT.MastaAPI.SystemModel.AnalysesAndResults.MBDAnalyses",
    "BevelGearMeshMultibodyDynamicsAnalysis",
)

if TYPE_CHECKING:
    from typing import Any, Type, TypeVar

    from mastapy._private.system_model.analyses_and_results import _2941, _2943, _2945
    from mastapy._private.system_model.analyses_and_results.analysis_cases import (
        _7934,
        _7938,
    )
    from mastapy._private.system_model.analyses_and_results.mbd_analyses import (
        _5725,
        _5747,
        _5750,
        _5773,
        _5785,
        _5828,
        _5835,
        _5838,
        _5859,
    )
    from mastapy._private.system_model.connections_and_sockets.gears import _2562

    Self = TypeVar("Self", bound="BevelGearMeshMultibodyDynamicsAnalysis")
    CastSelf = TypeVar(
        "CastSelf",
        bound="BevelGearMeshMultibodyDynamicsAnalysis._Cast_BevelGearMeshMultibodyDynamicsAnalysis",
    )


__docformat__ = "restructuredtext en"
__all__ = ("BevelGearMeshMultibodyDynamicsAnalysis",)


@extended_dataclass(frozen=True, slots=True, weakref_slot=True)
class _Cast_BevelGearMeshMultibodyDynamicsAnalysis:
    """Special nested class for casting BevelGearMeshMultibodyDynamicsAnalysis to subclasses."""

    __parent__: "BevelGearMeshMultibodyDynamicsAnalysis"

    @property
    def agma_gleason_conical_gear_mesh_multibody_dynamics_analysis(
        self: "CastSelf",
    ) -> "_5715.AGMAGleasonConicalGearMeshMultibodyDynamicsAnalysis":
        return self.__parent__._cast(
            _5715.AGMAGleasonConicalGearMeshMultibodyDynamicsAnalysis
        )

    @property
    def conical_gear_mesh_multibody_dynamics_analysis(
        self: "CastSelf",
    ) -> "_5747.ConicalGearMeshMultibodyDynamicsAnalysis":
        from mastapy._private.system_model.analyses_and_results.mbd_analyses import (
            _5747,
        )

        return self.__parent__._cast(_5747.ConicalGearMeshMultibodyDynamicsAnalysis)

    @property
    def gear_mesh_multibody_dynamics_analysis(
        self: "CastSelf",
    ) -> "_5773.GearMeshMultibodyDynamicsAnalysis":
        from mastapy._private.system_model.analyses_and_results.mbd_analyses import (
            _5773,
        )

        return self.__parent__._cast(_5773.GearMeshMultibodyDynamicsAnalysis)

    @property
    def inter_mountable_component_connection_multibody_dynamics_analysis(
        self: "CastSelf",
    ) -> "_5785.InterMountableComponentConnectionMultibodyDynamicsAnalysis":
        from mastapy._private.system_model.analyses_and_results.mbd_analyses import (
            _5785,
        )

        return self.__parent__._cast(
            _5785.InterMountableComponentConnectionMultibodyDynamicsAnalysis
        )

    @property
    def connection_multibody_dynamics_analysis(
        self: "CastSelf",
    ) -> "_5750.ConnectionMultibodyDynamicsAnalysis":
        from mastapy._private.system_model.analyses_and_results.mbd_analyses import (
            _5750,
        )

        return self.__parent__._cast(_5750.ConnectionMultibodyDynamicsAnalysis)

    @property
    def connection_time_series_load_analysis_case(
        self: "CastSelf",
    ) -> "_7938.ConnectionTimeSeriesLoadAnalysisCase":
        from mastapy._private.system_model.analyses_and_results.analysis_cases import (
            _7938,
        )

        return self.__parent__._cast(_7938.ConnectionTimeSeriesLoadAnalysisCase)

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
    def bevel_differential_gear_mesh_multibody_dynamics_analysis(
        self: "CastSelf",
    ) -> "_5725.BevelDifferentialGearMeshMultibodyDynamicsAnalysis":
        from mastapy._private.system_model.analyses_and_results.mbd_analyses import (
            _5725,
        )

        return self.__parent__._cast(
            _5725.BevelDifferentialGearMeshMultibodyDynamicsAnalysis
        )

    @property
    def spiral_bevel_gear_mesh_multibody_dynamics_analysis(
        self: "CastSelf",
    ) -> "_5828.SpiralBevelGearMeshMultibodyDynamicsAnalysis":
        from mastapy._private.system_model.analyses_and_results.mbd_analyses import (
            _5828,
        )

        return self.__parent__._cast(_5828.SpiralBevelGearMeshMultibodyDynamicsAnalysis)

    @property
    def straight_bevel_diff_gear_mesh_multibody_dynamics_analysis(
        self: "CastSelf",
    ) -> "_5835.StraightBevelDiffGearMeshMultibodyDynamicsAnalysis":
        from mastapy._private.system_model.analyses_and_results.mbd_analyses import (
            _5835,
        )

        return self.__parent__._cast(
            _5835.StraightBevelDiffGearMeshMultibodyDynamicsAnalysis
        )

    @property
    def straight_bevel_gear_mesh_multibody_dynamics_analysis(
        self: "CastSelf",
    ) -> "_5838.StraightBevelGearMeshMultibodyDynamicsAnalysis":
        from mastapy._private.system_model.analyses_and_results.mbd_analyses import (
            _5838,
        )

        return self.__parent__._cast(
            _5838.StraightBevelGearMeshMultibodyDynamicsAnalysis
        )

    @property
    def zerol_bevel_gear_mesh_multibody_dynamics_analysis(
        self: "CastSelf",
    ) -> "_5859.ZerolBevelGearMeshMultibodyDynamicsAnalysis":
        from mastapy._private.system_model.analyses_and_results.mbd_analyses import (
            _5859,
        )

        return self.__parent__._cast(_5859.ZerolBevelGearMeshMultibodyDynamicsAnalysis)

    @property
    def bevel_gear_mesh_multibody_dynamics_analysis(
        self: "CastSelf",
    ) -> "BevelGearMeshMultibodyDynamicsAnalysis":
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
class BevelGearMeshMultibodyDynamicsAnalysis(
    _5715.AGMAGleasonConicalGearMeshMultibodyDynamicsAnalysis
):
    """BevelGearMeshMultibodyDynamicsAnalysis

    This is a mastapy class.
    """

    TYPE: ClassVar["Type"] = _BEVEL_GEAR_MESH_MULTIBODY_DYNAMICS_ANALYSIS

    wrapped: "Any"

    def __post_init__(self: "Self") -> None:
        """Override of the post initialisation magic method."""
        if not hasattr(self.wrapped, "reference_count"):
            self.wrapped.reference_count = 0

        self.wrapped.reference_count += 1

    @property
    @exception_bridge
    def connection_design(self: "Self") -> "_2562.BevelGearMesh":
        """mastapy.system_model.connections_and_sockets.gears.BevelGearMesh

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "ConnectionDesign")

        if temp is None:
            return None

        type_ = temp.GetType()
        return constructor.new(type_.Namespace, type_.Name)(temp)

    @property
    def cast_to(self: "Self") -> "_Cast_BevelGearMeshMultibodyDynamicsAnalysis":
        """Cast to another type.

        Returns:
            _Cast_BevelGearMeshMultibodyDynamicsAnalysis
        """
        return _Cast_BevelGearMeshMultibodyDynamicsAnalysis(self)
