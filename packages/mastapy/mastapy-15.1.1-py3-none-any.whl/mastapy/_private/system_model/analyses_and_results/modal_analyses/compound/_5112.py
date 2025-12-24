"""GearMeshCompoundModalAnalysis"""

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
from mastapy._private.system_model.analyses_and_results.modal_analyses.compound import (
    _5118,
)

_GEAR_MESH_COMPOUND_MODAL_ANALYSIS = python_net_import(
    "SMT.MastaAPI.SystemModel.AnalysesAndResults.ModalAnalyses.Compound",
    "GearMeshCompoundModalAnalysis",
)

if TYPE_CHECKING:
    from typing import Any, List, Type, TypeVar

    from mastapy._private.system_model.analyses_and_results import _2943
    from mastapy._private.system_model.analyses_and_results.analysis_cases import (
        _7935,
        _7939,
    )
    from mastapy._private.system_model.analyses_and_results.modal_analyses import _4957
    from mastapy._private.system_model.analyses_and_results.modal_analyses.compound import (
        _5058,
        _5065,
        _5070,
        _5083,
        _5086,
        _5088,
        _5101,
        _5107,
        _5116,
        _5120,
        _5123,
        _5126,
        _5155,
        _5161,
        _5164,
        _5179,
        _5182,
    )

    Self = TypeVar("Self", bound="GearMeshCompoundModalAnalysis")
    CastSelf = TypeVar(
        "CastSelf",
        bound="GearMeshCompoundModalAnalysis._Cast_GearMeshCompoundModalAnalysis",
    )


__docformat__ = "restructuredtext en"
__all__ = ("GearMeshCompoundModalAnalysis",)


@extended_dataclass(frozen=True, slots=True, weakref_slot=True)
class _Cast_GearMeshCompoundModalAnalysis:
    """Special nested class for casting GearMeshCompoundModalAnalysis to subclasses."""

    __parent__: "GearMeshCompoundModalAnalysis"

    @property
    def inter_mountable_component_connection_compound_modal_analysis(
        self: "CastSelf",
    ) -> "_5118.InterMountableComponentConnectionCompoundModalAnalysis":
        return self.__parent__._cast(
            _5118.InterMountableComponentConnectionCompoundModalAnalysis
        )

    @property
    def connection_compound_modal_analysis(
        self: "CastSelf",
    ) -> "_5088.ConnectionCompoundModalAnalysis":
        from mastapy._private.system_model.analyses_and_results.modal_analyses.compound import (
            _5088,
        )

        return self.__parent__._cast(_5088.ConnectionCompoundModalAnalysis)

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
    def agma_gleason_conical_gear_mesh_compound_modal_analysis(
        self: "CastSelf",
    ) -> "_5058.AGMAGleasonConicalGearMeshCompoundModalAnalysis":
        from mastapy._private.system_model.analyses_and_results.modal_analyses.compound import (
            _5058,
        )

        return self.__parent__._cast(
            _5058.AGMAGleasonConicalGearMeshCompoundModalAnalysis
        )

    @property
    def bevel_differential_gear_mesh_compound_modal_analysis(
        self: "CastSelf",
    ) -> "_5065.BevelDifferentialGearMeshCompoundModalAnalysis":
        from mastapy._private.system_model.analyses_and_results.modal_analyses.compound import (
            _5065,
        )

        return self.__parent__._cast(
            _5065.BevelDifferentialGearMeshCompoundModalAnalysis
        )

    @property
    def bevel_gear_mesh_compound_modal_analysis(
        self: "CastSelf",
    ) -> "_5070.BevelGearMeshCompoundModalAnalysis":
        from mastapy._private.system_model.analyses_and_results.modal_analyses.compound import (
            _5070,
        )

        return self.__parent__._cast(_5070.BevelGearMeshCompoundModalAnalysis)

    @property
    def concept_gear_mesh_compound_modal_analysis(
        self: "CastSelf",
    ) -> "_5083.ConceptGearMeshCompoundModalAnalysis":
        from mastapy._private.system_model.analyses_and_results.modal_analyses.compound import (
            _5083,
        )

        return self.__parent__._cast(_5083.ConceptGearMeshCompoundModalAnalysis)

    @property
    def conical_gear_mesh_compound_modal_analysis(
        self: "CastSelf",
    ) -> "_5086.ConicalGearMeshCompoundModalAnalysis":
        from mastapy._private.system_model.analyses_and_results.modal_analyses.compound import (
            _5086,
        )

        return self.__parent__._cast(_5086.ConicalGearMeshCompoundModalAnalysis)

    @property
    def cylindrical_gear_mesh_compound_modal_analysis(
        self: "CastSelf",
    ) -> "_5101.CylindricalGearMeshCompoundModalAnalysis":
        from mastapy._private.system_model.analyses_and_results.modal_analyses.compound import (
            _5101,
        )

        return self.__parent__._cast(_5101.CylindricalGearMeshCompoundModalAnalysis)

    @property
    def face_gear_mesh_compound_modal_analysis(
        self: "CastSelf",
    ) -> "_5107.FaceGearMeshCompoundModalAnalysis":
        from mastapy._private.system_model.analyses_and_results.modal_analyses.compound import (
            _5107,
        )

        return self.__parent__._cast(_5107.FaceGearMeshCompoundModalAnalysis)

    @property
    def hypoid_gear_mesh_compound_modal_analysis(
        self: "CastSelf",
    ) -> "_5116.HypoidGearMeshCompoundModalAnalysis":
        from mastapy._private.system_model.analyses_and_results.modal_analyses.compound import (
            _5116,
        )

        return self.__parent__._cast(_5116.HypoidGearMeshCompoundModalAnalysis)

    @property
    def klingelnberg_cyclo_palloid_conical_gear_mesh_compound_modal_analysis(
        self: "CastSelf",
    ) -> "_5120.KlingelnbergCycloPalloidConicalGearMeshCompoundModalAnalysis":
        from mastapy._private.system_model.analyses_and_results.modal_analyses.compound import (
            _5120,
        )

        return self.__parent__._cast(
            _5120.KlingelnbergCycloPalloidConicalGearMeshCompoundModalAnalysis
        )

    @property
    def klingelnberg_cyclo_palloid_hypoid_gear_mesh_compound_modal_analysis(
        self: "CastSelf",
    ) -> "_5123.KlingelnbergCycloPalloidHypoidGearMeshCompoundModalAnalysis":
        from mastapy._private.system_model.analyses_and_results.modal_analyses.compound import (
            _5123,
        )

        return self.__parent__._cast(
            _5123.KlingelnbergCycloPalloidHypoidGearMeshCompoundModalAnalysis
        )

    @property
    def klingelnberg_cyclo_palloid_spiral_bevel_gear_mesh_compound_modal_analysis(
        self: "CastSelf",
    ) -> "_5126.KlingelnbergCycloPalloidSpiralBevelGearMeshCompoundModalAnalysis":
        from mastapy._private.system_model.analyses_and_results.modal_analyses.compound import (
            _5126,
        )

        return self.__parent__._cast(
            _5126.KlingelnbergCycloPalloidSpiralBevelGearMeshCompoundModalAnalysis
        )

    @property
    def spiral_bevel_gear_mesh_compound_modal_analysis(
        self: "CastSelf",
    ) -> "_5155.SpiralBevelGearMeshCompoundModalAnalysis":
        from mastapy._private.system_model.analyses_and_results.modal_analyses.compound import (
            _5155,
        )

        return self.__parent__._cast(_5155.SpiralBevelGearMeshCompoundModalAnalysis)

    @property
    def straight_bevel_diff_gear_mesh_compound_modal_analysis(
        self: "CastSelf",
    ) -> "_5161.StraightBevelDiffGearMeshCompoundModalAnalysis":
        from mastapy._private.system_model.analyses_and_results.modal_analyses.compound import (
            _5161,
        )

        return self.__parent__._cast(
            _5161.StraightBevelDiffGearMeshCompoundModalAnalysis
        )

    @property
    def straight_bevel_gear_mesh_compound_modal_analysis(
        self: "CastSelf",
    ) -> "_5164.StraightBevelGearMeshCompoundModalAnalysis":
        from mastapy._private.system_model.analyses_and_results.modal_analyses.compound import (
            _5164,
        )

        return self.__parent__._cast(_5164.StraightBevelGearMeshCompoundModalAnalysis)

    @property
    def worm_gear_mesh_compound_modal_analysis(
        self: "CastSelf",
    ) -> "_5179.WormGearMeshCompoundModalAnalysis":
        from mastapy._private.system_model.analyses_and_results.modal_analyses.compound import (
            _5179,
        )

        return self.__parent__._cast(_5179.WormGearMeshCompoundModalAnalysis)

    @property
    def zerol_bevel_gear_mesh_compound_modal_analysis(
        self: "CastSelf",
    ) -> "_5182.ZerolBevelGearMeshCompoundModalAnalysis":
        from mastapy._private.system_model.analyses_and_results.modal_analyses.compound import (
            _5182,
        )

        return self.__parent__._cast(_5182.ZerolBevelGearMeshCompoundModalAnalysis)

    @property
    def gear_mesh_compound_modal_analysis(
        self: "CastSelf",
    ) -> "GearMeshCompoundModalAnalysis":
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
class GearMeshCompoundModalAnalysis(
    _5118.InterMountableComponentConnectionCompoundModalAnalysis
):
    """GearMeshCompoundModalAnalysis

    This is a mastapy class.
    """

    TYPE: ClassVar["Type"] = _GEAR_MESH_COMPOUND_MODAL_ANALYSIS

    wrapped: "Any"

    def __post_init__(self: "Self") -> None:
        """Override of the post initialisation magic method."""
        if not hasattr(self.wrapped, "reference_count"):
            self.wrapped.reference_count = 0

        self.wrapped.reference_count += 1

    @property
    @exception_bridge
    def connection_analysis_cases(self: "Self") -> "List[_4957.GearMeshModalAnalysis]":
        """List[mastapy.system_model.analyses_and_results.modal_analyses.GearMeshModalAnalysis]

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
    ) -> "List[_4957.GearMeshModalAnalysis]":
        """List[mastapy.system_model.analyses_and_results.modal_analyses.GearMeshModalAnalysis]

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
    def cast_to(self: "Self") -> "_Cast_GearMeshCompoundModalAnalysis":
        """Cast to another type.

        Returns:
            _Cast_GearMeshCompoundModalAnalysis
        """
        return _Cast_GearMeshCompoundModalAnalysis(self)
