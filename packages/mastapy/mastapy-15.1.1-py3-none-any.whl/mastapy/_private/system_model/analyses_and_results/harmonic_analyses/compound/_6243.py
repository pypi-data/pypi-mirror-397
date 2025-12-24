"""AGMAGleasonConicalGearSetCompoundHarmonicAnalysis"""

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
from mastapy._private.system_model.analyses_and_results.harmonic_analyses.compound import (
    _6271,
)

_AGMA_GLEASON_CONICAL_GEAR_SET_COMPOUND_HARMONIC_ANALYSIS = python_net_import(
    "SMT.MastaAPI.SystemModel.AnalysesAndResults.HarmonicAnalyses.Compound",
    "AGMAGleasonConicalGearSetCompoundHarmonicAnalysis",
)

if TYPE_CHECKING:
    from typing import Any, List, Type, TypeVar

    from mastapy._private.system_model.analyses_and_results import _2943
    from mastapy._private.system_model.analyses_and_results.analysis_cases import (
        _7939,
        _7942,
    )
    from mastapy._private.system_model.analyses_and_results.harmonic_analyses import (
        _6027,
    )
    from mastapy._private.system_model.analyses_and_results.harmonic_analyses.compound import (
        _6237,
        _6250,
        _6255,
        _6297,
        _6301,
        _6318,
        _6337,
        _6340,
        _6346,
        _6349,
        _6367,
    )

    Self = TypeVar("Self", bound="AGMAGleasonConicalGearSetCompoundHarmonicAnalysis")
    CastSelf = TypeVar(
        "CastSelf",
        bound="AGMAGleasonConicalGearSetCompoundHarmonicAnalysis._Cast_AGMAGleasonConicalGearSetCompoundHarmonicAnalysis",
    )


__docformat__ = "restructuredtext en"
__all__ = ("AGMAGleasonConicalGearSetCompoundHarmonicAnalysis",)


@extended_dataclass(frozen=True, slots=True, weakref_slot=True)
class _Cast_AGMAGleasonConicalGearSetCompoundHarmonicAnalysis:
    """Special nested class for casting AGMAGleasonConicalGearSetCompoundHarmonicAnalysis to subclasses."""

    __parent__: "AGMAGleasonConicalGearSetCompoundHarmonicAnalysis"

    @property
    def conical_gear_set_compound_harmonic_analysis(
        self: "CastSelf",
    ) -> "_6271.ConicalGearSetCompoundHarmonicAnalysis":
        return self.__parent__._cast(_6271.ConicalGearSetCompoundHarmonicAnalysis)

    @property
    def gear_set_compound_harmonic_analysis(
        self: "CastSelf",
    ) -> "_6297.GearSetCompoundHarmonicAnalysis":
        from mastapy._private.system_model.analyses_and_results.harmonic_analyses.compound import (
            _6297,
        )

        return self.__parent__._cast(_6297.GearSetCompoundHarmonicAnalysis)

    @property
    def specialised_assembly_compound_harmonic_analysis(
        self: "CastSelf",
    ) -> "_6337.SpecialisedAssemblyCompoundHarmonicAnalysis":
        from mastapy._private.system_model.analyses_and_results.harmonic_analyses.compound import (
            _6337,
        )

        return self.__parent__._cast(_6337.SpecialisedAssemblyCompoundHarmonicAnalysis)

    @property
    def abstract_assembly_compound_harmonic_analysis(
        self: "CastSelf",
    ) -> "_6237.AbstractAssemblyCompoundHarmonicAnalysis":
        from mastapy._private.system_model.analyses_and_results.harmonic_analyses.compound import (
            _6237,
        )

        return self.__parent__._cast(_6237.AbstractAssemblyCompoundHarmonicAnalysis)

    @property
    def part_compound_harmonic_analysis(
        self: "CastSelf",
    ) -> "_6318.PartCompoundHarmonicAnalysis":
        from mastapy._private.system_model.analyses_and_results.harmonic_analyses.compound import (
            _6318,
        )

        return self.__parent__._cast(_6318.PartCompoundHarmonicAnalysis)

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
    def bevel_differential_gear_set_compound_harmonic_analysis(
        self: "CastSelf",
    ) -> "_6250.BevelDifferentialGearSetCompoundHarmonicAnalysis":
        from mastapy._private.system_model.analyses_and_results.harmonic_analyses.compound import (
            _6250,
        )

        return self.__parent__._cast(
            _6250.BevelDifferentialGearSetCompoundHarmonicAnalysis
        )

    @property
    def bevel_gear_set_compound_harmonic_analysis(
        self: "CastSelf",
    ) -> "_6255.BevelGearSetCompoundHarmonicAnalysis":
        from mastapy._private.system_model.analyses_and_results.harmonic_analyses.compound import (
            _6255,
        )

        return self.__parent__._cast(_6255.BevelGearSetCompoundHarmonicAnalysis)

    @property
    def hypoid_gear_set_compound_harmonic_analysis(
        self: "CastSelf",
    ) -> "_6301.HypoidGearSetCompoundHarmonicAnalysis":
        from mastapy._private.system_model.analyses_and_results.harmonic_analyses.compound import (
            _6301,
        )

        return self.__parent__._cast(_6301.HypoidGearSetCompoundHarmonicAnalysis)

    @property
    def spiral_bevel_gear_set_compound_harmonic_analysis(
        self: "CastSelf",
    ) -> "_6340.SpiralBevelGearSetCompoundHarmonicAnalysis":
        from mastapy._private.system_model.analyses_and_results.harmonic_analyses.compound import (
            _6340,
        )

        return self.__parent__._cast(_6340.SpiralBevelGearSetCompoundHarmonicAnalysis)

    @property
    def straight_bevel_diff_gear_set_compound_harmonic_analysis(
        self: "CastSelf",
    ) -> "_6346.StraightBevelDiffGearSetCompoundHarmonicAnalysis":
        from mastapy._private.system_model.analyses_and_results.harmonic_analyses.compound import (
            _6346,
        )

        return self.__parent__._cast(
            _6346.StraightBevelDiffGearSetCompoundHarmonicAnalysis
        )

    @property
    def straight_bevel_gear_set_compound_harmonic_analysis(
        self: "CastSelf",
    ) -> "_6349.StraightBevelGearSetCompoundHarmonicAnalysis":
        from mastapy._private.system_model.analyses_and_results.harmonic_analyses.compound import (
            _6349,
        )

        return self.__parent__._cast(_6349.StraightBevelGearSetCompoundHarmonicAnalysis)

    @property
    def zerol_bevel_gear_set_compound_harmonic_analysis(
        self: "CastSelf",
    ) -> "_6367.ZerolBevelGearSetCompoundHarmonicAnalysis":
        from mastapy._private.system_model.analyses_and_results.harmonic_analyses.compound import (
            _6367,
        )

        return self.__parent__._cast(_6367.ZerolBevelGearSetCompoundHarmonicAnalysis)

    @property
    def agma_gleason_conical_gear_set_compound_harmonic_analysis(
        self: "CastSelf",
    ) -> "AGMAGleasonConicalGearSetCompoundHarmonicAnalysis":
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
class AGMAGleasonConicalGearSetCompoundHarmonicAnalysis(
    _6271.ConicalGearSetCompoundHarmonicAnalysis
):
    """AGMAGleasonConicalGearSetCompoundHarmonicAnalysis

    This is a mastapy class.
    """

    TYPE: ClassVar["Type"] = _AGMA_GLEASON_CONICAL_GEAR_SET_COMPOUND_HARMONIC_ANALYSIS

    wrapped: "Any"

    def __post_init__(self: "Self") -> None:
        """Override of the post initialisation magic method."""
        if not hasattr(self.wrapped, "reference_count"):
            self.wrapped.reference_count = 0

        self.wrapped.reference_count += 1

    @property
    @exception_bridge
    def assembly_analysis_cases(
        self: "Self",
    ) -> "List[_6027.AGMAGleasonConicalGearSetHarmonicAnalysis]":
        """List[mastapy.system_model.analyses_and_results.harmonic_analyses.AGMAGleasonConicalGearSetHarmonicAnalysis]

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "AssemblyAnalysisCases")

        if temp is None:
            return None

        value = conversion.pn_to_mp_objects_in_list(temp)

        if value is None:
            return None

        return value

    @property
    @exception_bridge
    def assembly_analysis_cases_ready(
        self: "Self",
    ) -> "List[_6027.AGMAGleasonConicalGearSetHarmonicAnalysis]":
        """List[mastapy.system_model.analyses_and_results.harmonic_analyses.AGMAGleasonConicalGearSetHarmonicAnalysis]

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "AssemblyAnalysisCasesReady")

        if temp is None:
            return None

        value = conversion.pn_to_mp_objects_in_list(temp)

        if value is None:
            return None

        return value

    @property
    def cast_to(
        self: "Self",
    ) -> "_Cast_AGMAGleasonConicalGearSetCompoundHarmonicAnalysis":
        """Cast to another type.

        Returns:
            _Cast_AGMAGleasonConicalGearSetCompoundHarmonicAnalysis
        """
        return _Cast_AGMAGleasonConicalGearSetCompoundHarmonicAnalysis(self)
