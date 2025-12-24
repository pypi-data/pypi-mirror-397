"""ConicalGearMeshStabilityAnalysis"""

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
from mastapy._private.system_model.analyses_and_results.stability_analyses import _4132

_CONICAL_GEAR_MESH_STABILITY_ANALYSIS = python_net_import(
    "SMT.MastaAPI.SystemModel.AnalysesAndResults.StabilityAnalyses",
    "ConicalGearMeshStabilityAnalysis",
)

if TYPE_CHECKING:
    from typing import Any, List, Type, TypeVar

    from mastapy._private.system_model.analyses_and_results import _2941, _2943, _2945
    from mastapy._private.system_model.analyses_and_results.analysis_cases import (
        _7934,
        _7937,
    )
    from mastapy._private.system_model.analyses_and_results.stability_analyses import (
        _4076,
        _4083,
        _4088,
        _4107,
        _4136,
        _4139,
        _4140,
        _4143,
        _4146,
        _4175,
        _4184,
        _4187,
        _4205,
    )
    from mastapy._private.system_model.connections_and_sockets.gears import _2566

    Self = TypeVar("Self", bound="ConicalGearMeshStabilityAnalysis")
    CastSelf = TypeVar(
        "CastSelf",
        bound="ConicalGearMeshStabilityAnalysis._Cast_ConicalGearMeshStabilityAnalysis",
    )


__docformat__ = "restructuredtext en"
__all__ = ("ConicalGearMeshStabilityAnalysis",)


@extended_dataclass(frozen=True, slots=True, weakref_slot=True)
class _Cast_ConicalGearMeshStabilityAnalysis:
    """Special nested class for casting ConicalGearMeshStabilityAnalysis to subclasses."""

    __parent__: "ConicalGearMeshStabilityAnalysis"

    @property
    def gear_mesh_stability_analysis(
        self: "CastSelf",
    ) -> "_4132.GearMeshStabilityAnalysis":
        return self.__parent__._cast(_4132.GearMeshStabilityAnalysis)

    @property
    def inter_mountable_component_connection_stability_analysis(
        self: "CastSelf",
    ) -> "_4139.InterMountableComponentConnectionStabilityAnalysis":
        from mastapy._private.system_model.analyses_and_results.stability_analyses import (
            _4139,
        )

        return self.__parent__._cast(
            _4139.InterMountableComponentConnectionStabilityAnalysis
        )

    @property
    def connection_stability_analysis(
        self: "CastSelf",
    ) -> "_4107.ConnectionStabilityAnalysis":
        from mastapy._private.system_model.analyses_and_results.stability_analyses import (
            _4107,
        )

        return self.__parent__._cast(_4107.ConnectionStabilityAnalysis)

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
    def agma_gleason_conical_gear_mesh_stability_analysis(
        self: "CastSelf",
    ) -> "_4076.AGMAGleasonConicalGearMeshStabilityAnalysis":
        from mastapy._private.system_model.analyses_and_results.stability_analyses import (
            _4076,
        )

        return self.__parent__._cast(_4076.AGMAGleasonConicalGearMeshStabilityAnalysis)

    @property
    def bevel_differential_gear_mesh_stability_analysis(
        self: "CastSelf",
    ) -> "_4083.BevelDifferentialGearMeshStabilityAnalysis":
        from mastapy._private.system_model.analyses_and_results.stability_analyses import (
            _4083,
        )

        return self.__parent__._cast(_4083.BevelDifferentialGearMeshStabilityAnalysis)

    @property
    def bevel_gear_mesh_stability_analysis(
        self: "CastSelf",
    ) -> "_4088.BevelGearMeshStabilityAnalysis":
        from mastapy._private.system_model.analyses_and_results.stability_analyses import (
            _4088,
        )

        return self.__parent__._cast(_4088.BevelGearMeshStabilityAnalysis)

    @property
    def hypoid_gear_mesh_stability_analysis(
        self: "CastSelf",
    ) -> "_4136.HypoidGearMeshStabilityAnalysis":
        from mastapy._private.system_model.analyses_and_results.stability_analyses import (
            _4136,
        )

        return self.__parent__._cast(_4136.HypoidGearMeshStabilityAnalysis)

    @property
    def klingelnberg_cyclo_palloid_conical_gear_mesh_stability_analysis(
        self: "CastSelf",
    ) -> "_4140.KlingelnbergCycloPalloidConicalGearMeshStabilityAnalysis":
        from mastapy._private.system_model.analyses_and_results.stability_analyses import (
            _4140,
        )

        return self.__parent__._cast(
            _4140.KlingelnbergCycloPalloidConicalGearMeshStabilityAnalysis
        )

    @property
    def klingelnberg_cyclo_palloid_hypoid_gear_mesh_stability_analysis(
        self: "CastSelf",
    ) -> "_4143.KlingelnbergCycloPalloidHypoidGearMeshStabilityAnalysis":
        from mastapy._private.system_model.analyses_and_results.stability_analyses import (
            _4143,
        )

        return self.__parent__._cast(
            _4143.KlingelnbergCycloPalloidHypoidGearMeshStabilityAnalysis
        )

    @property
    def klingelnberg_cyclo_palloid_spiral_bevel_gear_mesh_stability_analysis(
        self: "CastSelf",
    ) -> "_4146.KlingelnbergCycloPalloidSpiralBevelGearMeshStabilityAnalysis":
        from mastapy._private.system_model.analyses_and_results.stability_analyses import (
            _4146,
        )

        return self.__parent__._cast(
            _4146.KlingelnbergCycloPalloidSpiralBevelGearMeshStabilityAnalysis
        )

    @property
    def spiral_bevel_gear_mesh_stability_analysis(
        self: "CastSelf",
    ) -> "_4175.SpiralBevelGearMeshStabilityAnalysis":
        from mastapy._private.system_model.analyses_and_results.stability_analyses import (
            _4175,
        )

        return self.__parent__._cast(_4175.SpiralBevelGearMeshStabilityAnalysis)

    @property
    def straight_bevel_diff_gear_mesh_stability_analysis(
        self: "CastSelf",
    ) -> "_4184.StraightBevelDiffGearMeshStabilityAnalysis":
        from mastapy._private.system_model.analyses_and_results.stability_analyses import (
            _4184,
        )

        return self.__parent__._cast(_4184.StraightBevelDiffGearMeshStabilityAnalysis)

    @property
    def straight_bevel_gear_mesh_stability_analysis(
        self: "CastSelf",
    ) -> "_4187.StraightBevelGearMeshStabilityAnalysis":
        from mastapy._private.system_model.analyses_and_results.stability_analyses import (
            _4187,
        )

        return self.__parent__._cast(_4187.StraightBevelGearMeshStabilityAnalysis)

    @property
    def zerol_bevel_gear_mesh_stability_analysis(
        self: "CastSelf",
    ) -> "_4205.ZerolBevelGearMeshStabilityAnalysis":
        from mastapy._private.system_model.analyses_and_results.stability_analyses import (
            _4205,
        )

        return self.__parent__._cast(_4205.ZerolBevelGearMeshStabilityAnalysis)

    @property
    def conical_gear_mesh_stability_analysis(
        self: "CastSelf",
    ) -> "ConicalGearMeshStabilityAnalysis":
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
class ConicalGearMeshStabilityAnalysis(_4132.GearMeshStabilityAnalysis):
    """ConicalGearMeshStabilityAnalysis

    This is a mastapy class.
    """

    TYPE: ClassVar["Type"] = _CONICAL_GEAR_MESH_STABILITY_ANALYSIS

    wrapped: "Any"

    def __post_init__(self: "Self") -> None:
        """Override of the post initialisation magic method."""
        if not hasattr(self.wrapped, "reference_count"):
            self.wrapped.reference_count = 0

        self.wrapped.reference_count += 1

    @property
    @exception_bridge
    def connection_design(self: "Self") -> "_2566.ConicalGearMesh":
        """mastapy.system_model.connections_and_sockets.gears.ConicalGearMesh

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
    def planetaries(self: "Self") -> "List[ConicalGearMeshStabilityAnalysis]":
        """List[mastapy.system_model.analyses_and_results.stability_analyses.ConicalGearMeshStabilityAnalysis]

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "Planetaries")

        if temp is None:
            return None

        value = conversion.pn_to_mp_objects_in_list(temp)

        if value is None:
            return None

        return value

    @property
    def cast_to(self: "Self") -> "_Cast_ConicalGearMeshStabilityAnalysis":
        """Cast to another type.

        Returns:
            _Cast_ConicalGearMeshStabilityAnalysis
        """
        return _Cast_ConicalGearMeshStabilityAnalysis(self)
