"""AGMAGleasonConicalGearCompoundModalAnalysis"""

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
    _5085,
)

_AGMA_GLEASON_CONICAL_GEAR_COMPOUND_MODAL_ANALYSIS = python_net_import(
    "SMT.MastaAPI.SystemModel.AnalysesAndResults.ModalAnalyses.Compound",
    "AGMAGleasonConicalGearCompoundModalAnalysis",
)

if TYPE_CHECKING:
    from typing import Any, List, Type, TypeVar

    from mastapy._private.system_model.analyses_and_results import _2943
    from mastapy._private.system_model.analyses_and_results.analysis_cases import (
        _7939,
        _7942,
    )
    from mastapy._private.system_model.analyses_and_results.modal_analyses import _4899
    from mastapy._private.system_model.analyses_and_results.modal_analyses.compound import (
        _5064,
        _5067,
        _5068,
        _5069,
        _5078,
        _5111,
        _5115,
        _5132,
        _5134,
        _5154,
        _5160,
        _5163,
        _5166,
        _5167,
        _5181,
    )

    Self = TypeVar("Self", bound="AGMAGleasonConicalGearCompoundModalAnalysis")
    CastSelf = TypeVar(
        "CastSelf",
        bound="AGMAGleasonConicalGearCompoundModalAnalysis._Cast_AGMAGleasonConicalGearCompoundModalAnalysis",
    )


__docformat__ = "restructuredtext en"
__all__ = ("AGMAGleasonConicalGearCompoundModalAnalysis",)


@extended_dataclass(frozen=True, slots=True, weakref_slot=True)
class _Cast_AGMAGleasonConicalGearCompoundModalAnalysis:
    """Special nested class for casting AGMAGleasonConicalGearCompoundModalAnalysis to subclasses."""

    __parent__: "AGMAGleasonConicalGearCompoundModalAnalysis"

    @property
    def conical_gear_compound_modal_analysis(
        self: "CastSelf",
    ) -> "_5085.ConicalGearCompoundModalAnalysis":
        return self.__parent__._cast(_5085.ConicalGearCompoundModalAnalysis)

    @property
    def gear_compound_modal_analysis(
        self: "CastSelf",
    ) -> "_5111.GearCompoundModalAnalysis":
        from mastapy._private.system_model.analyses_and_results.modal_analyses.compound import (
            _5111,
        )

        return self.__parent__._cast(_5111.GearCompoundModalAnalysis)

    @property
    def mountable_component_compound_modal_analysis(
        self: "CastSelf",
    ) -> "_5132.MountableComponentCompoundModalAnalysis":
        from mastapy._private.system_model.analyses_and_results.modal_analyses.compound import (
            _5132,
        )

        return self.__parent__._cast(_5132.MountableComponentCompoundModalAnalysis)

    @property
    def component_compound_modal_analysis(
        self: "CastSelf",
    ) -> "_5078.ComponentCompoundModalAnalysis":
        from mastapy._private.system_model.analyses_and_results.modal_analyses.compound import (
            _5078,
        )

        return self.__parent__._cast(_5078.ComponentCompoundModalAnalysis)

    @property
    def part_compound_modal_analysis(
        self: "CastSelf",
    ) -> "_5134.PartCompoundModalAnalysis":
        from mastapy._private.system_model.analyses_and_results.modal_analyses.compound import (
            _5134,
        )

        return self.__parent__._cast(_5134.PartCompoundModalAnalysis)

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
    def bevel_differential_gear_compound_modal_analysis(
        self: "CastSelf",
    ) -> "_5064.BevelDifferentialGearCompoundModalAnalysis":
        from mastapy._private.system_model.analyses_and_results.modal_analyses.compound import (
            _5064,
        )

        return self.__parent__._cast(_5064.BevelDifferentialGearCompoundModalAnalysis)

    @property
    def bevel_differential_planet_gear_compound_modal_analysis(
        self: "CastSelf",
    ) -> "_5067.BevelDifferentialPlanetGearCompoundModalAnalysis":
        from mastapy._private.system_model.analyses_and_results.modal_analyses.compound import (
            _5067,
        )

        return self.__parent__._cast(
            _5067.BevelDifferentialPlanetGearCompoundModalAnalysis
        )

    @property
    def bevel_differential_sun_gear_compound_modal_analysis(
        self: "CastSelf",
    ) -> "_5068.BevelDifferentialSunGearCompoundModalAnalysis":
        from mastapy._private.system_model.analyses_and_results.modal_analyses.compound import (
            _5068,
        )

        return self.__parent__._cast(
            _5068.BevelDifferentialSunGearCompoundModalAnalysis
        )

    @property
    def bevel_gear_compound_modal_analysis(
        self: "CastSelf",
    ) -> "_5069.BevelGearCompoundModalAnalysis":
        from mastapy._private.system_model.analyses_and_results.modal_analyses.compound import (
            _5069,
        )

        return self.__parent__._cast(_5069.BevelGearCompoundModalAnalysis)

    @property
    def hypoid_gear_compound_modal_analysis(
        self: "CastSelf",
    ) -> "_5115.HypoidGearCompoundModalAnalysis":
        from mastapy._private.system_model.analyses_and_results.modal_analyses.compound import (
            _5115,
        )

        return self.__parent__._cast(_5115.HypoidGearCompoundModalAnalysis)

    @property
    def spiral_bevel_gear_compound_modal_analysis(
        self: "CastSelf",
    ) -> "_5154.SpiralBevelGearCompoundModalAnalysis":
        from mastapy._private.system_model.analyses_and_results.modal_analyses.compound import (
            _5154,
        )

        return self.__parent__._cast(_5154.SpiralBevelGearCompoundModalAnalysis)

    @property
    def straight_bevel_diff_gear_compound_modal_analysis(
        self: "CastSelf",
    ) -> "_5160.StraightBevelDiffGearCompoundModalAnalysis":
        from mastapy._private.system_model.analyses_and_results.modal_analyses.compound import (
            _5160,
        )

        return self.__parent__._cast(_5160.StraightBevelDiffGearCompoundModalAnalysis)

    @property
    def straight_bevel_gear_compound_modal_analysis(
        self: "CastSelf",
    ) -> "_5163.StraightBevelGearCompoundModalAnalysis":
        from mastapy._private.system_model.analyses_and_results.modal_analyses.compound import (
            _5163,
        )

        return self.__parent__._cast(_5163.StraightBevelGearCompoundModalAnalysis)

    @property
    def straight_bevel_planet_gear_compound_modal_analysis(
        self: "CastSelf",
    ) -> "_5166.StraightBevelPlanetGearCompoundModalAnalysis":
        from mastapy._private.system_model.analyses_and_results.modal_analyses.compound import (
            _5166,
        )

        return self.__parent__._cast(_5166.StraightBevelPlanetGearCompoundModalAnalysis)

    @property
    def straight_bevel_sun_gear_compound_modal_analysis(
        self: "CastSelf",
    ) -> "_5167.StraightBevelSunGearCompoundModalAnalysis":
        from mastapy._private.system_model.analyses_and_results.modal_analyses.compound import (
            _5167,
        )

        return self.__parent__._cast(_5167.StraightBevelSunGearCompoundModalAnalysis)

    @property
    def zerol_bevel_gear_compound_modal_analysis(
        self: "CastSelf",
    ) -> "_5181.ZerolBevelGearCompoundModalAnalysis":
        from mastapy._private.system_model.analyses_and_results.modal_analyses.compound import (
            _5181,
        )

        return self.__parent__._cast(_5181.ZerolBevelGearCompoundModalAnalysis)

    @property
    def agma_gleason_conical_gear_compound_modal_analysis(
        self: "CastSelf",
    ) -> "AGMAGleasonConicalGearCompoundModalAnalysis":
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
class AGMAGleasonConicalGearCompoundModalAnalysis(
    _5085.ConicalGearCompoundModalAnalysis
):
    """AGMAGleasonConicalGearCompoundModalAnalysis

    This is a mastapy class.
    """

    TYPE: ClassVar["Type"] = _AGMA_GLEASON_CONICAL_GEAR_COMPOUND_MODAL_ANALYSIS

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
    ) -> "List[_4899.AGMAGleasonConicalGearModalAnalysis]":
        """List[mastapy.system_model.analyses_and_results.modal_analyses.AGMAGleasonConicalGearModalAnalysis]

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
    ) -> "List[_4899.AGMAGleasonConicalGearModalAnalysis]":
        """List[mastapy.system_model.analyses_and_results.modal_analyses.AGMAGleasonConicalGearModalAnalysis]

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
    def cast_to(self: "Self") -> "_Cast_AGMAGleasonConicalGearCompoundModalAnalysis":
        """Cast to another type.

        Returns:
            _Cast_AGMAGleasonConicalGearCompoundModalAnalysis
        """
        return _Cast_AGMAGleasonConicalGearCompoundModalAnalysis(self)
