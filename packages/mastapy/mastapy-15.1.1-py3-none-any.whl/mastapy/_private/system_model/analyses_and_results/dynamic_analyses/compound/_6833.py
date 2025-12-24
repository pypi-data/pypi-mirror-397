"""GearMeshCompoundDynamicAnalysis"""

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
from mastapy._private.system_model.analyses_and_results.dynamic_analyses.compound import (
    _6839,
)

_GEAR_MESH_COMPOUND_DYNAMIC_ANALYSIS = python_net_import(
    "SMT.MastaAPI.SystemModel.AnalysesAndResults.DynamicAnalyses.Compound",
    "GearMeshCompoundDynamicAnalysis",
)

if TYPE_CHECKING:
    from typing import Any, List, Type, TypeVar

    from mastapy._private.system_model.analyses_and_results import _2943
    from mastapy._private.system_model.analyses_and_results.analysis_cases import (
        _7935,
        _7939,
    )
    from mastapy._private.system_model.analyses_and_results.dynamic_analyses import (
        _6702,
    )
    from mastapy._private.system_model.analyses_and_results.dynamic_analyses.compound import (
        _6779,
        _6786,
        _6791,
        _6804,
        _6807,
        _6809,
        _6822,
        _6828,
        _6837,
        _6841,
        _6844,
        _6847,
        _6876,
        _6882,
        _6885,
        _6900,
        _6903,
    )

    Self = TypeVar("Self", bound="GearMeshCompoundDynamicAnalysis")
    CastSelf = TypeVar(
        "CastSelf",
        bound="GearMeshCompoundDynamicAnalysis._Cast_GearMeshCompoundDynamicAnalysis",
    )


__docformat__ = "restructuredtext en"
__all__ = ("GearMeshCompoundDynamicAnalysis",)


@extended_dataclass(frozen=True, slots=True, weakref_slot=True)
class _Cast_GearMeshCompoundDynamicAnalysis:
    """Special nested class for casting GearMeshCompoundDynamicAnalysis to subclasses."""

    __parent__: "GearMeshCompoundDynamicAnalysis"

    @property
    def inter_mountable_component_connection_compound_dynamic_analysis(
        self: "CastSelf",
    ) -> "_6839.InterMountableComponentConnectionCompoundDynamicAnalysis":
        return self.__parent__._cast(
            _6839.InterMountableComponentConnectionCompoundDynamicAnalysis
        )

    @property
    def connection_compound_dynamic_analysis(
        self: "CastSelf",
    ) -> "_6809.ConnectionCompoundDynamicAnalysis":
        from mastapy._private.system_model.analyses_and_results.dynamic_analyses.compound import (
            _6809,
        )

        return self.__parent__._cast(_6809.ConnectionCompoundDynamicAnalysis)

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
    def agma_gleason_conical_gear_mesh_compound_dynamic_analysis(
        self: "CastSelf",
    ) -> "_6779.AGMAGleasonConicalGearMeshCompoundDynamicAnalysis":
        from mastapy._private.system_model.analyses_and_results.dynamic_analyses.compound import (
            _6779,
        )

        return self.__parent__._cast(
            _6779.AGMAGleasonConicalGearMeshCompoundDynamicAnalysis
        )

    @property
    def bevel_differential_gear_mesh_compound_dynamic_analysis(
        self: "CastSelf",
    ) -> "_6786.BevelDifferentialGearMeshCompoundDynamicAnalysis":
        from mastapy._private.system_model.analyses_and_results.dynamic_analyses.compound import (
            _6786,
        )

        return self.__parent__._cast(
            _6786.BevelDifferentialGearMeshCompoundDynamicAnalysis
        )

    @property
    def bevel_gear_mesh_compound_dynamic_analysis(
        self: "CastSelf",
    ) -> "_6791.BevelGearMeshCompoundDynamicAnalysis":
        from mastapy._private.system_model.analyses_and_results.dynamic_analyses.compound import (
            _6791,
        )

        return self.__parent__._cast(_6791.BevelGearMeshCompoundDynamicAnalysis)

    @property
    def concept_gear_mesh_compound_dynamic_analysis(
        self: "CastSelf",
    ) -> "_6804.ConceptGearMeshCompoundDynamicAnalysis":
        from mastapy._private.system_model.analyses_and_results.dynamic_analyses.compound import (
            _6804,
        )

        return self.__parent__._cast(_6804.ConceptGearMeshCompoundDynamicAnalysis)

    @property
    def conical_gear_mesh_compound_dynamic_analysis(
        self: "CastSelf",
    ) -> "_6807.ConicalGearMeshCompoundDynamicAnalysis":
        from mastapy._private.system_model.analyses_and_results.dynamic_analyses.compound import (
            _6807,
        )

        return self.__parent__._cast(_6807.ConicalGearMeshCompoundDynamicAnalysis)

    @property
    def cylindrical_gear_mesh_compound_dynamic_analysis(
        self: "CastSelf",
    ) -> "_6822.CylindricalGearMeshCompoundDynamicAnalysis":
        from mastapy._private.system_model.analyses_and_results.dynamic_analyses.compound import (
            _6822,
        )

        return self.__parent__._cast(_6822.CylindricalGearMeshCompoundDynamicAnalysis)

    @property
    def face_gear_mesh_compound_dynamic_analysis(
        self: "CastSelf",
    ) -> "_6828.FaceGearMeshCompoundDynamicAnalysis":
        from mastapy._private.system_model.analyses_and_results.dynamic_analyses.compound import (
            _6828,
        )

        return self.__parent__._cast(_6828.FaceGearMeshCompoundDynamicAnalysis)

    @property
    def hypoid_gear_mesh_compound_dynamic_analysis(
        self: "CastSelf",
    ) -> "_6837.HypoidGearMeshCompoundDynamicAnalysis":
        from mastapy._private.system_model.analyses_and_results.dynamic_analyses.compound import (
            _6837,
        )

        return self.__parent__._cast(_6837.HypoidGearMeshCompoundDynamicAnalysis)

    @property
    def klingelnberg_cyclo_palloid_conical_gear_mesh_compound_dynamic_analysis(
        self: "CastSelf",
    ) -> "_6841.KlingelnbergCycloPalloidConicalGearMeshCompoundDynamicAnalysis":
        from mastapy._private.system_model.analyses_and_results.dynamic_analyses.compound import (
            _6841,
        )

        return self.__parent__._cast(
            _6841.KlingelnbergCycloPalloidConicalGearMeshCompoundDynamicAnalysis
        )

    @property
    def klingelnberg_cyclo_palloid_hypoid_gear_mesh_compound_dynamic_analysis(
        self: "CastSelf",
    ) -> "_6844.KlingelnbergCycloPalloidHypoidGearMeshCompoundDynamicAnalysis":
        from mastapy._private.system_model.analyses_and_results.dynamic_analyses.compound import (
            _6844,
        )

        return self.__parent__._cast(
            _6844.KlingelnbergCycloPalloidHypoidGearMeshCompoundDynamicAnalysis
        )

    @property
    def klingelnberg_cyclo_palloid_spiral_bevel_gear_mesh_compound_dynamic_analysis(
        self: "CastSelf",
    ) -> "_6847.KlingelnbergCycloPalloidSpiralBevelGearMeshCompoundDynamicAnalysis":
        from mastapy._private.system_model.analyses_and_results.dynamic_analyses.compound import (
            _6847,
        )

        return self.__parent__._cast(
            _6847.KlingelnbergCycloPalloidSpiralBevelGearMeshCompoundDynamicAnalysis
        )

    @property
    def spiral_bevel_gear_mesh_compound_dynamic_analysis(
        self: "CastSelf",
    ) -> "_6876.SpiralBevelGearMeshCompoundDynamicAnalysis":
        from mastapy._private.system_model.analyses_and_results.dynamic_analyses.compound import (
            _6876,
        )

        return self.__parent__._cast(_6876.SpiralBevelGearMeshCompoundDynamicAnalysis)

    @property
    def straight_bevel_diff_gear_mesh_compound_dynamic_analysis(
        self: "CastSelf",
    ) -> "_6882.StraightBevelDiffGearMeshCompoundDynamicAnalysis":
        from mastapy._private.system_model.analyses_and_results.dynamic_analyses.compound import (
            _6882,
        )

        return self.__parent__._cast(
            _6882.StraightBevelDiffGearMeshCompoundDynamicAnalysis
        )

    @property
    def straight_bevel_gear_mesh_compound_dynamic_analysis(
        self: "CastSelf",
    ) -> "_6885.StraightBevelGearMeshCompoundDynamicAnalysis":
        from mastapy._private.system_model.analyses_and_results.dynamic_analyses.compound import (
            _6885,
        )

        return self.__parent__._cast(_6885.StraightBevelGearMeshCompoundDynamicAnalysis)

    @property
    def worm_gear_mesh_compound_dynamic_analysis(
        self: "CastSelf",
    ) -> "_6900.WormGearMeshCompoundDynamicAnalysis":
        from mastapy._private.system_model.analyses_and_results.dynamic_analyses.compound import (
            _6900,
        )

        return self.__parent__._cast(_6900.WormGearMeshCompoundDynamicAnalysis)

    @property
    def zerol_bevel_gear_mesh_compound_dynamic_analysis(
        self: "CastSelf",
    ) -> "_6903.ZerolBevelGearMeshCompoundDynamicAnalysis":
        from mastapy._private.system_model.analyses_and_results.dynamic_analyses.compound import (
            _6903,
        )

        return self.__parent__._cast(_6903.ZerolBevelGearMeshCompoundDynamicAnalysis)

    @property
    def gear_mesh_compound_dynamic_analysis(
        self: "CastSelf",
    ) -> "GearMeshCompoundDynamicAnalysis":
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
class GearMeshCompoundDynamicAnalysis(
    _6839.InterMountableComponentConnectionCompoundDynamicAnalysis
):
    """GearMeshCompoundDynamicAnalysis

    This is a mastapy class.
    """

    TYPE: ClassVar["Type"] = _GEAR_MESH_COMPOUND_DYNAMIC_ANALYSIS

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
    ) -> "List[_6702.GearMeshDynamicAnalysis]":
        """List[mastapy.system_model.analyses_and_results.dynamic_analyses.GearMeshDynamicAnalysis]

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
    ) -> "List[_6702.GearMeshDynamicAnalysis]":
        """List[mastapy.system_model.analyses_and_results.dynamic_analyses.GearMeshDynamicAnalysis]

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
    def cast_to(self: "Self") -> "_Cast_GearMeshCompoundDynamicAnalysis":
        """Cast to another type.

        Returns:
            _Cast_GearMeshCompoundDynamicAnalysis
        """
        return _Cast_GearMeshCompoundDynamicAnalysis(self)
