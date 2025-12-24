"""BevelGearMeshModalAnalysis"""

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
from mastapy._private.system_model.analyses_and_results.modal_analyses import _4898

_BEVEL_GEAR_MESH_MODAL_ANALYSIS = python_net_import(
    "SMT.MastaAPI.SystemModel.AnalysesAndResults.ModalAnalyses",
    "BevelGearMeshModalAnalysis",
)

if TYPE_CHECKING:
    from typing import Any, Type, TypeVar

    from mastapy._private.system_model.analyses_and_results import _2941, _2943, _2945
    from mastapy._private.system_model.analyses_and_results.analysis_cases import (
        _7934,
        _7937,
    )
    from mastapy._private.system_model.analyses_and_results.modal_analyses import (
        _4905,
        _4926,
        _4929,
        _4957,
        _4964,
        _5008,
        _5014,
        _5017,
        _5038,
    )
    from mastapy._private.system_model.analyses_and_results.system_deflections import (
        _2998,
    )
    from mastapy._private.system_model.connections_and_sockets.gears import _2562

    Self = TypeVar("Self", bound="BevelGearMeshModalAnalysis")
    CastSelf = TypeVar(
        "CastSelf", bound="BevelGearMeshModalAnalysis._Cast_BevelGearMeshModalAnalysis"
    )


__docformat__ = "restructuredtext en"
__all__ = ("BevelGearMeshModalAnalysis",)


@extended_dataclass(frozen=True, slots=True, weakref_slot=True)
class _Cast_BevelGearMeshModalAnalysis:
    """Special nested class for casting BevelGearMeshModalAnalysis to subclasses."""

    __parent__: "BevelGearMeshModalAnalysis"

    @property
    def agma_gleason_conical_gear_mesh_modal_analysis(
        self: "CastSelf",
    ) -> "_4898.AGMAGleasonConicalGearMeshModalAnalysis":
        return self.__parent__._cast(_4898.AGMAGleasonConicalGearMeshModalAnalysis)

    @property
    def conical_gear_mesh_modal_analysis(
        self: "CastSelf",
    ) -> "_4926.ConicalGearMeshModalAnalysis":
        from mastapy._private.system_model.analyses_and_results.modal_analyses import (
            _4926,
        )

        return self.__parent__._cast(_4926.ConicalGearMeshModalAnalysis)

    @property
    def gear_mesh_modal_analysis(self: "CastSelf") -> "_4957.GearMeshModalAnalysis":
        from mastapy._private.system_model.analyses_and_results.modal_analyses import (
            _4957,
        )

        return self.__parent__._cast(_4957.GearMeshModalAnalysis)

    @property
    def inter_mountable_component_connection_modal_analysis(
        self: "CastSelf",
    ) -> "_4964.InterMountableComponentConnectionModalAnalysis":
        from mastapy._private.system_model.analyses_and_results.modal_analyses import (
            _4964,
        )

        return self.__parent__._cast(
            _4964.InterMountableComponentConnectionModalAnalysis
        )

    @property
    def connection_modal_analysis(self: "CastSelf") -> "_4929.ConnectionModalAnalysis":
        from mastapy._private.system_model.analyses_and_results.modal_analyses import (
            _4929,
        )

        return self.__parent__._cast(_4929.ConnectionModalAnalysis)

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
    def bevel_differential_gear_mesh_modal_analysis(
        self: "CastSelf",
    ) -> "_4905.BevelDifferentialGearMeshModalAnalysis":
        from mastapy._private.system_model.analyses_and_results.modal_analyses import (
            _4905,
        )

        return self.__parent__._cast(_4905.BevelDifferentialGearMeshModalAnalysis)

    @property
    def spiral_bevel_gear_mesh_modal_analysis(
        self: "CastSelf",
    ) -> "_5008.SpiralBevelGearMeshModalAnalysis":
        from mastapy._private.system_model.analyses_and_results.modal_analyses import (
            _5008,
        )

        return self.__parent__._cast(_5008.SpiralBevelGearMeshModalAnalysis)

    @property
    def straight_bevel_diff_gear_mesh_modal_analysis(
        self: "CastSelf",
    ) -> "_5014.StraightBevelDiffGearMeshModalAnalysis":
        from mastapy._private.system_model.analyses_and_results.modal_analyses import (
            _5014,
        )

        return self.__parent__._cast(_5014.StraightBevelDiffGearMeshModalAnalysis)

    @property
    def straight_bevel_gear_mesh_modal_analysis(
        self: "CastSelf",
    ) -> "_5017.StraightBevelGearMeshModalAnalysis":
        from mastapy._private.system_model.analyses_and_results.modal_analyses import (
            _5017,
        )

        return self.__parent__._cast(_5017.StraightBevelGearMeshModalAnalysis)

    @property
    def zerol_bevel_gear_mesh_modal_analysis(
        self: "CastSelf",
    ) -> "_5038.ZerolBevelGearMeshModalAnalysis":
        from mastapy._private.system_model.analyses_and_results.modal_analyses import (
            _5038,
        )

        return self.__parent__._cast(_5038.ZerolBevelGearMeshModalAnalysis)

    @property
    def bevel_gear_mesh_modal_analysis(
        self: "CastSelf",
    ) -> "BevelGearMeshModalAnalysis":
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
class BevelGearMeshModalAnalysis(_4898.AGMAGleasonConicalGearMeshModalAnalysis):
    """BevelGearMeshModalAnalysis

    This is a mastapy class.
    """

    TYPE: ClassVar["Type"] = _BEVEL_GEAR_MESH_MODAL_ANALYSIS

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
    @exception_bridge
    def system_deflection_results(
        self: "Self",
    ) -> "_2998.BevelGearMeshSystemDeflection":
        """mastapy.system_model.analyses_and_results.system_deflections.BevelGearMeshSystemDeflection

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "SystemDeflectionResults")

        if temp is None:
            return None

        type_ = temp.GetType()
        return constructor.new(type_.Namespace, type_.Name)(temp)

    @property
    def cast_to(self: "Self") -> "_Cast_BevelGearMeshModalAnalysis":
        """Cast to another type.

        Returns:
            _Cast_BevelGearMeshModalAnalysis
        """
        return _Cast_BevelGearMeshModalAnalysis(self)
