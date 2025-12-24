"""BevelGearCompoundModalAnalysisAtAStiffness"""

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
from mastapy._private.system_model.analyses_and_results.modal_analyses_at_a_stiffness.compound import (
    _5321,
)

_BEVEL_GEAR_COMPOUND_MODAL_ANALYSIS_AT_A_STIFFNESS = python_net_import(
    "SMT.MastaAPI.SystemModel.AnalysesAndResults.ModalAnalysesAtAStiffness.Compound",
    "BevelGearCompoundModalAnalysisAtAStiffness",
)

if TYPE_CHECKING:
    from typing import Any, List, Type, TypeVar

    from mastapy._private.system_model.analyses_and_results import _2943
    from mastapy._private.system_model.analyses_and_results.analysis_cases import (
        _7939,
        _7942,
    )
    from mastapy._private.system_model.analyses_and_results.modal_analyses_at_a_stiffness import (
        _5201,
    )
    from mastapy._private.system_model.analyses_and_results.modal_analyses_at_a_stiffness.compound import (
        _5328,
        _5331,
        _5332,
        _5342,
        _5349,
        _5375,
        _5396,
        _5398,
        _5418,
        _5424,
        _5427,
        _5430,
        _5431,
        _5445,
    )

    Self = TypeVar("Self", bound="BevelGearCompoundModalAnalysisAtAStiffness")
    CastSelf = TypeVar(
        "CastSelf",
        bound="BevelGearCompoundModalAnalysisAtAStiffness._Cast_BevelGearCompoundModalAnalysisAtAStiffness",
    )


__docformat__ = "restructuredtext en"
__all__ = ("BevelGearCompoundModalAnalysisAtAStiffness",)


@extended_dataclass(frozen=True, slots=True, weakref_slot=True)
class _Cast_BevelGearCompoundModalAnalysisAtAStiffness:
    """Special nested class for casting BevelGearCompoundModalAnalysisAtAStiffness to subclasses."""

    __parent__: "BevelGearCompoundModalAnalysisAtAStiffness"

    @property
    def agma_gleason_conical_gear_compound_modal_analysis_at_a_stiffness(
        self: "CastSelf",
    ) -> "_5321.AGMAGleasonConicalGearCompoundModalAnalysisAtAStiffness":
        return self.__parent__._cast(
            _5321.AGMAGleasonConicalGearCompoundModalAnalysisAtAStiffness
        )

    @property
    def conical_gear_compound_modal_analysis_at_a_stiffness(
        self: "CastSelf",
    ) -> "_5349.ConicalGearCompoundModalAnalysisAtAStiffness":
        from mastapy._private.system_model.analyses_and_results.modal_analyses_at_a_stiffness.compound import (
            _5349,
        )

        return self.__parent__._cast(_5349.ConicalGearCompoundModalAnalysisAtAStiffness)

    @property
    def gear_compound_modal_analysis_at_a_stiffness(
        self: "CastSelf",
    ) -> "_5375.GearCompoundModalAnalysisAtAStiffness":
        from mastapy._private.system_model.analyses_and_results.modal_analyses_at_a_stiffness.compound import (
            _5375,
        )

        return self.__parent__._cast(_5375.GearCompoundModalAnalysisAtAStiffness)

    @property
    def mountable_component_compound_modal_analysis_at_a_stiffness(
        self: "CastSelf",
    ) -> "_5396.MountableComponentCompoundModalAnalysisAtAStiffness":
        from mastapy._private.system_model.analyses_and_results.modal_analyses_at_a_stiffness.compound import (
            _5396,
        )

        return self.__parent__._cast(
            _5396.MountableComponentCompoundModalAnalysisAtAStiffness
        )

    @property
    def component_compound_modal_analysis_at_a_stiffness(
        self: "CastSelf",
    ) -> "_5342.ComponentCompoundModalAnalysisAtAStiffness":
        from mastapy._private.system_model.analyses_and_results.modal_analyses_at_a_stiffness.compound import (
            _5342,
        )

        return self.__parent__._cast(_5342.ComponentCompoundModalAnalysisAtAStiffness)

    @property
    def part_compound_modal_analysis_at_a_stiffness(
        self: "CastSelf",
    ) -> "_5398.PartCompoundModalAnalysisAtAStiffness":
        from mastapy._private.system_model.analyses_and_results.modal_analyses_at_a_stiffness.compound import (
            _5398,
        )

        return self.__parent__._cast(_5398.PartCompoundModalAnalysisAtAStiffness)

    @property
    def part_compound_analysis(self: "CastSelf") -> "_7942.PartCompoundAnalysis":
        from mastapy._private.system_model.analyses_and_results.analysis_cases import (
            _7942,
        )

        return self.__parent__._cast(_7942.PartCompoundAnalysis)

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
    def bevel_differential_gear_compound_modal_analysis_at_a_stiffness(
        self: "CastSelf",
    ) -> "_5328.BevelDifferentialGearCompoundModalAnalysisAtAStiffness":
        from mastapy._private.system_model.analyses_and_results.modal_analyses_at_a_stiffness.compound import (
            _5328,
        )

        return self.__parent__._cast(
            _5328.BevelDifferentialGearCompoundModalAnalysisAtAStiffness
        )

    @property
    def bevel_differential_planet_gear_compound_modal_analysis_at_a_stiffness(
        self: "CastSelf",
    ) -> "_5331.BevelDifferentialPlanetGearCompoundModalAnalysisAtAStiffness":
        from mastapy._private.system_model.analyses_and_results.modal_analyses_at_a_stiffness.compound import (
            _5331,
        )

        return self.__parent__._cast(
            _5331.BevelDifferentialPlanetGearCompoundModalAnalysisAtAStiffness
        )

    @property
    def bevel_differential_sun_gear_compound_modal_analysis_at_a_stiffness(
        self: "CastSelf",
    ) -> "_5332.BevelDifferentialSunGearCompoundModalAnalysisAtAStiffness":
        from mastapy._private.system_model.analyses_and_results.modal_analyses_at_a_stiffness.compound import (
            _5332,
        )

        return self.__parent__._cast(
            _5332.BevelDifferentialSunGearCompoundModalAnalysisAtAStiffness
        )

    @property
    def spiral_bevel_gear_compound_modal_analysis_at_a_stiffness(
        self: "CastSelf",
    ) -> "_5418.SpiralBevelGearCompoundModalAnalysisAtAStiffness":
        from mastapy._private.system_model.analyses_and_results.modal_analyses_at_a_stiffness.compound import (
            _5418,
        )

        return self.__parent__._cast(
            _5418.SpiralBevelGearCompoundModalAnalysisAtAStiffness
        )

    @property
    def straight_bevel_diff_gear_compound_modal_analysis_at_a_stiffness(
        self: "CastSelf",
    ) -> "_5424.StraightBevelDiffGearCompoundModalAnalysisAtAStiffness":
        from mastapy._private.system_model.analyses_and_results.modal_analyses_at_a_stiffness.compound import (
            _5424,
        )

        return self.__parent__._cast(
            _5424.StraightBevelDiffGearCompoundModalAnalysisAtAStiffness
        )

    @property
    def straight_bevel_gear_compound_modal_analysis_at_a_stiffness(
        self: "CastSelf",
    ) -> "_5427.StraightBevelGearCompoundModalAnalysisAtAStiffness":
        from mastapy._private.system_model.analyses_and_results.modal_analyses_at_a_stiffness.compound import (
            _5427,
        )

        return self.__parent__._cast(
            _5427.StraightBevelGearCompoundModalAnalysisAtAStiffness
        )

    @property
    def straight_bevel_planet_gear_compound_modal_analysis_at_a_stiffness(
        self: "CastSelf",
    ) -> "_5430.StraightBevelPlanetGearCompoundModalAnalysisAtAStiffness":
        from mastapy._private.system_model.analyses_and_results.modal_analyses_at_a_stiffness.compound import (
            _5430,
        )

        return self.__parent__._cast(
            _5430.StraightBevelPlanetGearCompoundModalAnalysisAtAStiffness
        )

    @property
    def straight_bevel_sun_gear_compound_modal_analysis_at_a_stiffness(
        self: "CastSelf",
    ) -> "_5431.StraightBevelSunGearCompoundModalAnalysisAtAStiffness":
        from mastapy._private.system_model.analyses_and_results.modal_analyses_at_a_stiffness.compound import (
            _5431,
        )

        return self.__parent__._cast(
            _5431.StraightBevelSunGearCompoundModalAnalysisAtAStiffness
        )

    @property
    def zerol_bevel_gear_compound_modal_analysis_at_a_stiffness(
        self: "CastSelf",
    ) -> "_5445.ZerolBevelGearCompoundModalAnalysisAtAStiffness":
        from mastapy._private.system_model.analyses_and_results.modal_analyses_at_a_stiffness.compound import (
            _5445,
        )

        return self.__parent__._cast(
            _5445.ZerolBevelGearCompoundModalAnalysisAtAStiffness
        )

    @property
    def bevel_gear_compound_modal_analysis_at_a_stiffness(
        self: "CastSelf",
    ) -> "BevelGearCompoundModalAnalysisAtAStiffness":
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
class BevelGearCompoundModalAnalysisAtAStiffness(
    _5321.AGMAGleasonConicalGearCompoundModalAnalysisAtAStiffness
):
    """BevelGearCompoundModalAnalysisAtAStiffness

    This is a mastapy class.
    """

    TYPE: ClassVar["Type"] = _BEVEL_GEAR_COMPOUND_MODAL_ANALYSIS_AT_A_STIFFNESS

    wrapped: "Any"

    def __post_init__(self: "Self") -> None:
        """Override of the post initialisation magic method."""
        if not hasattr(self.wrapped, "reference_count"):
            self.wrapped.reference_count = 0

        self.wrapped.reference_count += 1

    @property
    @exception_bridge
    def component_analysis_cases(
        self: "Self",
    ) -> "List[_5201.BevelGearModalAnalysisAtAStiffness]":
        """List[mastapy.system_model.analyses_and_results.modal_analyses_at_a_stiffness.BevelGearModalAnalysisAtAStiffness]

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "ComponentAnalysisCases")

        if temp is None:
            return None

        value = conversion.pn_to_mp_objects_in_list(temp)

        if value is None:
            return None

        return value

    @property
    @exception_bridge
    def component_analysis_cases_ready(
        self: "Self",
    ) -> "List[_5201.BevelGearModalAnalysisAtAStiffness]":
        """List[mastapy.system_model.analyses_and_results.modal_analyses_at_a_stiffness.BevelGearModalAnalysisAtAStiffness]

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "ComponentAnalysisCasesReady")

        if temp is None:
            return None

        value = conversion.pn_to_mp_objects_in_list(temp)

        if value is None:
            return None

        return value

    @property
    def cast_to(self: "Self") -> "_Cast_BevelGearCompoundModalAnalysisAtAStiffness":
        """Cast to another type.

        Returns:
            _Cast_BevelGearCompoundModalAnalysisAtAStiffness
        """
        return _Cast_BevelGearCompoundModalAnalysisAtAStiffness(self)
