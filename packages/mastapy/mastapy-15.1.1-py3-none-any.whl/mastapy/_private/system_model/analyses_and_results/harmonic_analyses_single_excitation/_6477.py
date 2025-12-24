"""StraightBevelDiffGearHarmonicAnalysisOfSingleExcitation"""

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
from mastapy._private.system_model.analyses_and_results.harmonic_analyses_single_excitation import (
    _6384,
)

_STRAIGHT_BEVEL_DIFF_GEAR_HARMONIC_ANALYSIS_OF_SINGLE_EXCITATION = python_net_import(
    "SMT.MastaAPI.SystemModel.AnalysesAndResults.HarmonicAnalysesSingleExcitation",
    "StraightBevelDiffGearHarmonicAnalysisOfSingleExcitation",
)

if TYPE_CHECKING:
    from typing import Any, Type, TypeVar

    from mastapy._private.system_model.analyses_and_results import _2943, _2945, _2949
    from mastapy._private.system_model.analyses_and_results.analysis_cases import (
        _7941,
        _7944,
    )
    from mastapy._private.system_model.analyses_and_results.harmonic_analyses_single_excitation import (
        _6372,
        _6393,
        _6400,
        _6426,
        _6449,
        _6451,
        _6483,
        _6484,
    )
    from mastapy._private.system_model.analyses_and_results.static_loads import _7884
    from mastapy._private.system_model.part_model.gears import _2827

    Self = TypeVar(
        "Self", bound="StraightBevelDiffGearHarmonicAnalysisOfSingleExcitation"
    )
    CastSelf = TypeVar(
        "CastSelf",
        bound="StraightBevelDiffGearHarmonicAnalysisOfSingleExcitation._Cast_StraightBevelDiffGearHarmonicAnalysisOfSingleExcitation",
    )


__docformat__ = "restructuredtext en"
__all__ = ("StraightBevelDiffGearHarmonicAnalysisOfSingleExcitation",)


@extended_dataclass(frozen=True, slots=True, weakref_slot=True)
class _Cast_StraightBevelDiffGearHarmonicAnalysisOfSingleExcitation:
    """Special nested class for casting StraightBevelDiffGearHarmonicAnalysisOfSingleExcitation to subclasses."""

    __parent__: "StraightBevelDiffGearHarmonicAnalysisOfSingleExcitation"

    @property
    def bevel_gear_harmonic_analysis_of_single_excitation(
        self: "CastSelf",
    ) -> "_6384.BevelGearHarmonicAnalysisOfSingleExcitation":
        return self.__parent__._cast(_6384.BevelGearHarmonicAnalysisOfSingleExcitation)

    @property
    def agma_gleason_conical_gear_harmonic_analysis_of_single_excitation(
        self: "CastSelf",
    ) -> "_6372.AGMAGleasonConicalGearHarmonicAnalysisOfSingleExcitation":
        from mastapy._private.system_model.analyses_and_results.harmonic_analyses_single_excitation import (
            _6372,
        )

        return self.__parent__._cast(
            _6372.AGMAGleasonConicalGearHarmonicAnalysisOfSingleExcitation
        )

    @property
    def conical_gear_harmonic_analysis_of_single_excitation(
        self: "CastSelf",
    ) -> "_6400.ConicalGearHarmonicAnalysisOfSingleExcitation":
        from mastapy._private.system_model.analyses_and_results.harmonic_analyses_single_excitation import (
            _6400,
        )

        return self.__parent__._cast(
            _6400.ConicalGearHarmonicAnalysisOfSingleExcitation
        )

    @property
    def gear_harmonic_analysis_of_single_excitation(
        self: "CastSelf",
    ) -> "_6426.GearHarmonicAnalysisOfSingleExcitation":
        from mastapy._private.system_model.analyses_and_results.harmonic_analyses_single_excitation import (
            _6426,
        )

        return self.__parent__._cast(_6426.GearHarmonicAnalysisOfSingleExcitation)

    @property
    def mountable_component_harmonic_analysis_of_single_excitation(
        self: "CastSelf",
    ) -> "_6449.MountableComponentHarmonicAnalysisOfSingleExcitation":
        from mastapy._private.system_model.analyses_and_results.harmonic_analyses_single_excitation import (
            _6449,
        )

        return self.__parent__._cast(
            _6449.MountableComponentHarmonicAnalysisOfSingleExcitation
        )

    @property
    def component_harmonic_analysis_of_single_excitation(
        self: "CastSelf",
    ) -> "_6393.ComponentHarmonicAnalysisOfSingleExcitation":
        from mastapy._private.system_model.analyses_and_results.harmonic_analyses_single_excitation import (
            _6393,
        )

        return self.__parent__._cast(_6393.ComponentHarmonicAnalysisOfSingleExcitation)

    @property
    def part_harmonic_analysis_of_single_excitation(
        self: "CastSelf",
    ) -> "_6451.PartHarmonicAnalysisOfSingleExcitation":
        from mastapy._private.system_model.analyses_and_results.harmonic_analyses_single_excitation import (
            _6451,
        )

        return self.__parent__._cast(_6451.PartHarmonicAnalysisOfSingleExcitation)

    @property
    def part_static_load_analysis_case(
        self: "CastSelf",
    ) -> "_7944.PartStaticLoadAnalysisCase":
        from mastapy._private.system_model.analyses_and_results.analysis_cases import (
            _7944,
        )

        return self.__parent__._cast(_7944.PartStaticLoadAnalysisCase)

    @property
    def part_analysis_case(self: "CastSelf") -> "_7941.PartAnalysisCase":
        from mastapy._private.system_model.analyses_and_results.analysis_cases import (
            _7941,
        )

        return self.__parent__._cast(_7941.PartAnalysisCase)

    @property
    def part_analysis(self: "CastSelf") -> "_2949.PartAnalysis":
        from mastapy._private.system_model.analyses_and_results import _2949

        return self.__parent__._cast(_2949.PartAnalysis)

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
    def straight_bevel_planet_gear_harmonic_analysis_of_single_excitation(
        self: "CastSelf",
    ) -> "_6483.StraightBevelPlanetGearHarmonicAnalysisOfSingleExcitation":
        from mastapy._private.system_model.analyses_and_results.harmonic_analyses_single_excitation import (
            _6483,
        )

        return self.__parent__._cast(
            _6483.StraightBevelPlanetGearHarmonicAnalysisOfSingleExcitation
        )

    @property
    def straight_bevel_sun_gear_harmonic_analysis_of_single_excitation(
        self: "CastSelf",
    ) -> "_6484.StraightBevelSunGearHarmonicAnalysisOfSingleExcitation":
        from mastapy._private.system_model.analyses_and_results.harmonic_analyses_single_excitation import (
            _6484,
        )

        return self.__parent__._cast(
            _6484.StraightBevelSunGearHarmonicAnalysisOfSingleExcitation
        )

    @property
    def straight_bevel_diff_gear_harmonic_analysis_of_single_excitation(
        self: "CastSelf",
    ) -> "StraightBevelDiffGearHarmonicAnalysisOfSingleExcitation":
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
class StraightBevelDiffGearHarmonicAnalysisOfSingleExcitation(
    _6384.BevelGearHarmonicAnalysisOfSingleExcitation
):
    """StraightBevelDiffGearHarmonicAnalysisOfSingleExcitation

    This is a mastapy class.
    """

    TYPE: ClassVar["Type"] = (
        _STRAIGHT_BEVEL_DIFF_GEAR_HARMONIC_ANALYSIS_OF_SINGLE_EXCITATION
    )

    wrapped: "Any"

    def __post_init__(self: "Self") -> None:
        """Override of the post initialisation magic method."""
        if not hasattr(self.wrapped, "reference_count"):
            self.wrapped.reference_count = 0

        self.wrapped.reference_count += 1

    @property
    @exception_bridge
    def component_design(self: "Self") -> "_2827.StraightBevelDiffGear":
        """mastapy.system_model.part_model.gears.StraightBevelDiffGear

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "ComponentDesign")

        if temp is None:
            return None

        type_ = temp.GetType()
        return constructor.new(type_.Namespace, type_.Name)(temp)

    @property
    @exception_bridge
    def component_load_case(self: "Self") -> "_7884.StraightBevelDiffGearLoadCase":
        """mastapy.system_model.analyses_and_results.static_loads.StraightBevelDiffGearLoadCase

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "ComponentLoadCase")

        if temp is None:
            return None

        type_ = temp.GetType()
        return constructor.new(type_.Namespace, type_.Name)(temp)

    @property
    def cast_to(
        self: "Self",
    ) -> "_Cast_StraightBevelDiffGearHarmonicAnalysisOfSingleExcitation":
        """Cast to another type.

        Returns:
            _Cast_StraightBevelDiffGearHarmonicAnalysisOfSingleExcitation
        """
        return _Cast_StraightBevelDiffGearHarmonicAnalysisOfSingleExcitation(self)
