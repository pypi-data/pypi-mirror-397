"""GearMeshModalAnalysis"""

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
from mastapy._private.system_model.analyses_and_results.modal_analyses import _4964

_GEAR_MESH_MODAL_ANALYSIS = python_net_import(
    "SMT.MastaAPI.SystemModel.AnalysesAndResults.ModalAnalyses", "GearMeshModalAnalysis"
)

if TYPE_CHECKING:
    from typing import Any, Type, TypeVar

    from mastapy._private.system_model.analyses_and_results import _2941, _2943, _2945
    from mastapy._private.system_model.analyses_and_results.analysis_cases import (
        _7934,
        _7937,
    )
    from mastapy._private.system_model.analyses_and_results.modal_analyses import (
        _4898,
        _4905,
        _4910,
        _4923,
        _4926,
        _4929,
        _4942,
        _4951,
        _4961,
        _4965,
        _4968,
        _4971,
        _5008,
        _5014,
        _5017,
        _5035,
        _5038,
    )
    from mastapy._private.system_model.analyses_and_results.system_deflections import (
        _3051,
    )
    from mastapy._private.system_model.connections_and_sockets.gears import _2572

    Self = TypeVar("Self", bound="GearMeshModalAnalysis")
    CastSelf = TypeVar(
        "CastSelf", bound="GearMeshModalAnalysis._Cast_GearMeshModalAnalysis"
    )


__docformat__ = "restructuredtext en"
__all__ = ("GearMeshModalAnalysis",)


@extended_dataclass(frozen=True, slots=True, weakref_slot=True)
class _Cast_GearMeshModalAnalysis:
    """Special nested class for casting GearMeshModalAnalysis to subclasses."""

    __parent__: "GearMeshModalAnalysis"

    @property
    def inter_mountable_component_connection_modal_analysis(
        self: "CastSelf",
    ) -> "_4964.InterMountableComponentConnectionModalAnalysis":
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
    def agma_gleason_conical_gear_mesh_modal_analysis(
        self: "CastSelf",
    ) -> "_4898.AGMAGleasonConicalGearMeshModalAnalysis":
        from mastapy._private.system_model.analyses_and_results.modal_analyses import (
            _4898,
        )

        return self.__parent__._cast(_4898.AGMAGleasonConicalGearMeshModalAnalysis)

    @property
    def bevel_differential_gear_mesh_modal_analysis(
        self: "CastSelf",
    ) -> "_4905.BevelDifferentialGearMeshModalAnalysis":
        from mastapy._private.system_model.analyses_and_results.modal_analyses import (
            _4905,
        )

        return self.__parent__._cast(_4905.BevelDifferentialGearMeshModalAnalysis)

    @property
    def bevel_gear_mesh_modal_analysis(
        self: "CastSelf",
    ) -> "_4910.BevelGearMeshModalAnalysis":
        from mastapy._private.system_model.analyses_and_results.modal_analyses import (
            _4910,
        )

        return self.__parent__._cast(_4910.BevelGearMeshModalAnalysis)

    @property
    def concept_gear_mesh_modal_analysis(
        self: "CastSelf",
    ) -> "_4923.ConceptGearMeshModalAnalysis":
        from mastapy._private.system_model.analyses_and_results.modal_analyses import (
            _4923,
        )

        return self.__parent__._cast(_4923.ConceptGearMeshModalAnalysis)

    @property
    def conical_gear_mesh_modal_analysis(
        self: "CastSelf",
    ) -> "_4926.ConicalGearMeshModalAnalysis":
        from mastapy._private.system_model.analyses_and_results.modal_analyses import (
            _4926,
        )

        return self.__parent__._cast(_4926.ConicalGearMeshModalAnalysis)

    @property
    def cylindrical_gear_mesh_modal_analysis(
        self: "CastSelf",
    ) -> "_4942.CylindricalGearMeshModalAnalysis":
        from mastapy._private.system_model.analyses_and_results.modal_analyses import (
            _4942,
        )

        return self.__parent__._cast(_4942.CylindricalGearMeshModalAnalysis)

    @property
    def face_gear_mesh_modal_analysis(
        self: "CastSelf",
    ) -> "_4951.FaceGearMeshModalAnalysis":
        from mastapy._private.system_model.analyses_and_results.modal_analyses import (
            _4951,
        )

        return self.__parent__._cast(_4951.FaceGearMeshModalAnalysis)

    @property
    def hypoid_gear_mesh_modal_analysis(
        self: "CastSelf",
    ) -> "_4961.HypoidGearMeshModalAnalysis":
        from mastapy._private.system_model.analyses_and_results.modal_analyses import (
            _4961,
        )

        return self.__parent__._cast(_4961.HypoidGearMeshModalAnalysis)

    @property
    def klingelnberg_cyclo_palloid_conical_gear_mesh_modal_analysis(
        self: "CastSelf",
    ) -> "_4965.KlingelnbergCycloPalloidConicalGearMeshModalAnalysis":
        from mastapy._private.system_model.analyses_and_results.modal_analyses import (
            _4965,
        )

        return self.__parent__._cast(
            _4965.KlingelnbergCycloPalloidConicalGearMeshModalAnalysis
        )

    @property
    def klingelnberg_cyclo_palloid_hypoid_gear_mesh_modal_analysis(
        self: "CastSelf",
    ) -> "_4968.KlingelnbergCycloPalloidHypoidGearMeshModalAnalysis":
        from mastapy._private.system_model.analyses_and_results.modal_analyses import (
            _4968,
        )

        return self.__parent__._cast(
            _4968.KlingelnbergCycloPalloidHypoidGearMeshModalAnalysis
        )

    @property
    def klingelnberg_cyclo_palloid_spiral_bevel_gear_mesh_modal_analysis(
        self: "CastSelf",
    ) -> "_4971.KlingelnbergCycloPalloidSpiralBevelGearMeshModalAnalysis":
        from mastapy._private.system_model.analyses_and_results.modal_analyses import (
            _4971,
        )

        return self.__parent__._cast(
            _4971.KlingelnbergCycloPalloidSpiralBevelGearMeshModalAnalysis
        )

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
    def worm_gear_mesh_modal_analysis(
        self: "CastSelf",
    ) -> "_5035.WormGearMeshModalAnalysis":
        from mastapy._private.system_model.analyses_and_results.modal_analyses import (
            _5035,
        )

        return self.__parent__._cast(_5035.WormGearMeshModalAnalysis)

    @property
    def zerol_bevel_gear_mesh_modal_analysis(
        self: "CastSelf",
    ) -> "_5038.ZerolBevelGearMeshModalAnalysis":
        from mastapy._private.system_model.analyses_and_results.modal_analyses import (
            _5038,
        )

        return self.__parent__._cast(_5038.ZerolBevelGearMeshModalAnalysis)

    @property
    def gear_mesh_modal_analysis(self: "CastSelf") -> "GearMeshModalAnalysis":
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
class GearMeshModalAnalysis(_4964.InterMountableComponentConnectionModalAnalysis):
    """GearMeshModalAnalysis

    This is a mastapy class.
    """

    TYPE: ClassVar["Type"] = _GEAR_MESH_MODAL_ANALYSIS

    wrapped: "Any"

    def __post_init__(self: "Self") -> None:
        """Override of the post initialisation magic method."""
        if not hasattr(self.wrapped, "reference_count"):
            self.wrapped.reference_count = 0

        self.wrapped.reference_count += 1

    @property
    @exception_bridge
    def connection_design(self: "Self") -> "_2572.GearMesh":
        """mastapy.system_model.connections_and_sockets.gears.GearMesh

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
    def system_deflection_results(self: "Self") -> "_3051.GearMeshSystemDeflection":
        """mastapy.system_model.analyses_and_results.system_deflections.GearMeshSystemDeflection

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "SystemDeflectionResults")

        if temp is None:
            return None

        type_ = temp.GetType()
        return constructor.new(type_.Namespace, type_.Name)(temp)

    @property
    def cast_to(self: "Self") -> "_Cast_GearMeshModalAnalysis":
        """Cast to another type.

        Returns:
            _Cast_GearMeshModalAnalysis
        """
        return _Cast_GearMeshModalAnalysis(self)
