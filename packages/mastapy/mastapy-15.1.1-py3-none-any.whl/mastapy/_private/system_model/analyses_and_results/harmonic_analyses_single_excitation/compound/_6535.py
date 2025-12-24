"""ConicalGearSetCompoundHarmonicAnalysisOfSingleExcitation"""

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
from mastapy._private.system_model.analyses_and_results.harmonic_analyses_single_excitation.compound import (
    _6561,
)

_CONICAL_GEAR_SET_COMPOUND_HARMONIC_ANALYSIS_OF_SINGLE_EXCITATION = python_net_import(
    "SMT.MastaAPI.SystemModel.AnalysesAndResults.HarmonicAnalysesSingleExcitation.Compound",
    "ConicalGearSetCompoundHarmonicAnalysisOfSingleExcitation",
)

if TYPE_CHECKING:
    from typing import Any, List, Type, TypeVar

    from mastapy._private.system_model.analyses_and_results import _2943
    from mastapy._private.system_model.analyses_and_results.analysis_cases import (
        _7939,
        _7942,
    )
    from mastapy._private.system_model.analyses_and_results.harmonic_analyses_single_excitation import (
        _6402,
    )
    from mastapy._private.system_model.analyses_and_results.harmonic_analyses_single_excitation.compound import (
        _6501,
        _6507,
        _6514,
        _6519,
        _6565,
        _6569,
        _6572,
        _6575,
        _6582,
        _6601,
        _6604,
        _6610,
        _6613,
        _6631,
    )

    Self = TypeVar(
        "Self", bound="ConicalGearSetCompoundHarmonicAnalysisOfSingleExcitation"
    )
    CastSelf = TypeVar(
        "CastSelf",
        bound="ConicalGearSetCompoundHarmonicAnalysisOfSingleExcitation._Cast_ConicalGearSetCompoundHarmonicAnalysisOfSingleExcitation",
    )


__docformat__ = "restructuredtext en"
__all__ = ("ConicalGearSetCompoundHarmonicAnalysisOfSingleExcitation",)


@extended_dataclass(frozen=True, slots=True, weakref_slot=True)
class _Cast_ConicalGearSetCompoundHarmonicAnalysisOfSingleExcitation:
    """Special nested class for casting ConicalGearSetCompoundHarmonicAnalysisOfSingleExcitation to subclasses."""

    __parent__: "ConicalGearSetCompoundHarmonicAnalysisOfSingleExcitation"

    @property
    def gear_set_compound_harmonic_analysis_of_single_excitation(
        self: "CastSelf",
    ) -> "_6561.GearSetCompoundHarmonicAnalysisOfSingleExcitation":
        return self.__parent__._cast(
            _6561.GearSetCompoundHarmonicAnalysisOfSingleExcitation
        )

    @property
    def specialised_assembly_compound_harmonic_analysis_of_single_excitation(
        self: "CastSelf",
    ) -> "_6601.SpecialisedAssemblyCompoundHarmonicAnalysisOfSingleExcitation":
        from mastapy._private.system_model.analyses_and_results.harmonic_analyses_single_excitation.compound import (
            _6601,
        )

        return self.__parent__._cast(
            _6601.SpecialisedAssemblyCompoundHarmonicAnalysisOfSingleExcitation
        )

    @property
    def abstract_assembly_compound_harmonic_analysis_of_single_excitation(
        self: "CastSelf",
    ) -> "_6501.AbstractAssemblyCompoundHarmonicAnalysisOfSingleExcitation":
        from mastapy._private.system_model.analyses_and_results.harmonic_analyses_single_excitation.compound import (
            _6501,
        )

        return self.__parent__._cast(
            _6501.AbstractAssemblyCompoundHarmonicAnalysisOfSingleExcitation
        )

    @property
    def part_compound_harmonic_analysis_of_single_excitation(
        self: "CastSelf",
    ) -> "_6582.PartCompoundHarmonicAnalysisOfSingleExcitation":
        from mastapy._private.system_model.analyses_and_results.harmonic_analyses_single_excitation.compound import (
            _6582,
        )

        return self.__parent__._cast(
            _6582.PartCompoundHarmonicAnalysisOfSingleExcitation
        )

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
    def agma_gleason_conical_gear_set_compound_harmonic_analysis_of_single_excitation(
        self: "CastSelf",
    ) -> "_6507.AGMAGleasonConicalGearSetCompoundHarmonicAnalysisOfSingleExcitation":
        from mastapy._private.system_model.analyses_and_results.harmonic_analyses_single_excitation.compound import (
            _6507,
        )

        return self.__parent__._cast(
            _6507.AGMAGleasonConicalGearSetCompoundHarmonicAnalysisOfSingleExcitation
        )

    @property
    def bevel_differential_gear_set_compound_harmonic_analysis_of_single_excitation(
        self: "CastSelf",
    ) -> "_6514.BevelDifferentialGearSetCompoundHarmonicAnalysisOfSingleExcitation":
        from mastapy._private.system_model.analyses_and_results.harmonic_analyses_single_excitation.compound import (
            _6514,
        )

        return self.__parent__._cast(
            _6514.BevelDifferentialGearSetCompoundHarmonicAnalysisOfSingleExcitation
        )

    @property
    def bevel_gear_set_compound_harmonic_analysis_of_single_excitation(
        self: "CastSelf",
    ) -> "_6519.BevelGearSetCompoundHarmonicAnalysisOfSingleExcitation":
        from mastapy._private.system_model.analyses_and_results.harmonic_analyses_single_excitation.compound import (
            _6519,
        )

        return self.__parent__._cast(
            _6519.BevelGearSetCompoundHarmonicAnalysisOfSingleExcitation
        )

    @property
    def hypoid_gear_set_compound_harmonic_analysis_of_single_excitation(
        self: "CastSelf",
    ) -> "_6565.HypoidGearSetCompoundHarmonicAnalysisOfSingleExcitation":
        from mastapy._private.system_model.analyses_and_results.harmonic_analyses_single_excitation.compound import (
            _6565,
        )

        return self.__parent__._cast(
            _6565.HypoidGearSetCompoundHarmonicAnalysisOfSingleExcitation
        )

    @property
    def klingelnberg_cyclo_palloid_conical_gear_set_compound_harmonic_analysis_of_single_excitation(
        self: "CastSelf",
    ) -> "_6569.KlingelnbergCycloPalloidConicalGearSetCompoundHarmonicAnalysisOfSingleExcitation":
        from mastapy._private.system_model.analyses_and_results.harmonic_analyses_single_excitation.compound import (
            _6569,
        )

        return self.__parent__._cast(
            _6569.KlingelnbergCycloPalloidConicalGearSetCompoundHarmonicAnalysisOfSingleExcitation
        )

    @property
    def klingelnberg_cyclo_palloid_hypoid_gear_set_compound_harmonic_analysis_of_single_excitation(
        self: "CastSelf",
    ) -> "_6572.KlingelnbergCycloPalloidHypoidGearSetCompoundHarmonicAnalysisOfSingleExcitation":
        from mastapy._private.system_model.analyses_and_results.harmonic_analyses_single_excitation.compound import (
            _6572,
        )

        return self.__parent__._cast(
            _6572.KlingelnbergCycloPalloidHypoidGearSetCompoundHarmonicAnalysisOfSingleExcitation
        )

    @property
    def klingelnberg_cyclo_palloid_spiral_bevel_gear_set_compound_harmonic_analysis_of_single_excitation(
        self: "CastSelf",
    ) -> "_6575.KlingelnbergCycloPalloidSpiralBevelGearSetCompoundHarmonicAnalysisOfSingleExcitation":
        from mastapy._private.system_model.analyses_and_results.harmonic_analyses_single_excitation.compound import (
            _6575,
        )

        return self.__parent__._cast(
            _6575.KlingelnbergCycloPalloidSpiralBevelGearSetCompoundHarmonicAnalysisOfSingleExcitation
        )

    @property
    def spiral_bevel_gear_set_compound_harmonic_analysis_of_single_excitation(
        self: "CastSelf",
    ) -> "_6604.SpiralBevelGearSetCompoundHarmonicAnalysisOfSingleExcitation":
        from mastapy._private.system_model.analyses_and_results.harmonic_analyses_single_excitation.compound import (
            _6604,
        )

        return self.__parent__._cast(
            _6604.SpiralBevelGearSetCompoundHarmonicAnalysisOfSingleExcitation
        )

    @property
    def straight_bevel_diff_gear_set_compound_harmonic_analysis_of_single_excitation(
        self: "CastSelf",
    ) -> "_6610.StraightBevelDiffGearSetCompoundHarmonicAnalysisOfSingleExcitation":
        from mastapy._private.system_model.analyses_and_results.harmonic_analyses_single_excitation.compound import (
            _6610,
        )

        return self.__parent__._cast(
            _6610.StraightBevelDiffGearSetCompoundHarmonicAnalysisOfSingleExcitation
        )

    @property
    def straight_bevel_gear_set_compound_harmonic_analysis_of_single_excitation(
        self: "CastSelf",
    ) -> "_6613.StraightBevelGearSetCompoundHarmonicAnalysisOfSingleExcitation":
        from mastapy._private.system_model.analyses_and_results.harmonic_analyses_single_excitation.compound import (
            _6613,
        )

        return self.__parent__._cast(
            _6613.StraightBevelGearSetCompoundHarmonicAnalysisOfSingleExcitation
        )

    @property
    def zerol_bevel_gear_set_compound_harmonic_analysis_of_single_excitation(
        self: "CastSelf",
    ) -> "_6631.ZerolBevelGearSetCompoundHarmonicAnalysisOfSingleExcitation":
        from mastapy._private.system_model.analyses_and_results.harmonic_analyses_single_excitation.compound import (
            _6631,
        )

        return self.__parent__._cast(
            _6631.ZerolBevelGearSetCompoundHarmonicAnalysisOfSingleExcitation
        )

    @property
    def conical_gear_set_compound_harmonic_analysis_of_single_excitation(
        self: "CastSelf",
    ) -> "ConicalGearSetCompoundHarmonicAnalysisOfSingleExcitation":
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
class ConicalGearSetCompoundHarmonicAnalysisOfSingleExcitation(
    _6561.GearSetCompoundHarmonicAnalysisOfSingleExcitation
):
    """ConicalGearSetCompoundHarmonicAnalysisOfSingleExcitation

    This is a mastapy class.
    """

    TYPE: ClassVar["Type"] = (
        _CONICAL_GEAR_SET_COMPOUND_HARMONIC_ANALYSIS_OF_SINGLE_EXCITATION
    )

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
    ) -> "List[_6402.ConicalGearSetHarmonicAnalysisOfSingleExcitation]":
        """List[mastapy.system_model.analyses_and_results.harmonic_analyses_single_excitation.ConicalGearSetHarmonicAnalysisOfSingleExcitation]

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
    ) -> "List[_6402.ConicalGearSetHarmonicAnalysisOfSingleExcitation]":
        """List[mastapy.system_model.analyses_and_results.harmonic_analyses_single_excitation.ConicalGearSetHarmonicAnalysisOfSingleExcitation]

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
    ) -> "_Cast_ConicalGearSetCompoundHarmonicAnalysisOfSingleExcitation":
        """Cast to another type.

        Returns:
            _Cast_ConicalGearSetCompoundHarmonicAnalysisOfSingleExcitation
        """
        return _Cast_ConicalGearSetCompoundHarmonicAnalysisOfSingleExcitation(self)
