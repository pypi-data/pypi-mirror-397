"""WormGearSetHarmonicAnalysisOfSingleExcitation"""

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
from mastapy._private.system_model.analyses_and_results.harmonic_analyses_single_excitation import (
    _6428,
)

_WORM_GEAR_SET_HARMONIC_ANALYSIS_OF_SINGLE_EXCITATION = python_net_import(
    "SMT.MastaAPI.SystemModel.AnalysesAndResults.HarmonicAnalysesSingleExcitation",
    "WormGearSetHarmonicAnalysisOfSingleExcitation",
)

if TYPE_CHECKING:
    from typing import Any, List, Type, TypeVar

    from mastapy._private.system_model.analyses_and_results import _2943, _2945, _2949
    from mastapy._private.system_model.analyses_and_results.analysis_cases import (
        _7941,
        _7944,
    )
    from mastapy._private.system_model.analyses_and_results.harmonic_analyses_single_excitation import (
        _6368,
        _6451,
        _6470,
        _6495,
        _6496,
    )
    from mastapy._private.system_model.analyses_and_results.static_loads import _7910
    from mastapy._private.system_model.part_model.gears import _2834

    Self = TypeVar("Self", bound="WormGearSetHarmonicAnalysisOfSingleExcitation")
    CastSelf = TypeVar(
        "CastSelf",
        bound="WormGearSetHarmonicAnalysisOfSingleExcitation._Cast_WormGearSetHarmonicAnalysisOfSingleExcitation",
    )


__docformat__ = "restructuredtext en"
__all__ = ("WormGearSetHarmonicAnalysisOfSingleExcitation",)


@extended_dataclass(frozen=True, slots=True, weakref_slot=True)
class _Cast_WormGearSetHarmonicAnalysisOfSingleExcitation:
    """Special nested class for casting WormGearSetHarmonicAnalysisOfSingleExcitation to subclasses."""

    __parent__: "WormGearSetHarmonicAnalysisOfSingleExcitation"

    @property
    def gear_set_harmonic_analysis_of_single_excitation(
        self: "CastSelf",
    ) -> "_6428.GearSetHarmonicAnalysisOfSingleExcitation":
        return self.__parent__._cast(_6428.GearSetHarmonicAnalysisOfSingleExcitation)

    @property
    def specialised_assembly_harmonic_analysis_of_single_excitation(
        self: "CastSelf",
    ) -> "_6470.SpecialisedAssemblyHarmonicAnalysisOfSingleExcitation":
        from mastapy._private.system_model.analyses_and_results.harmonic_analyses_single_excitation import (
            _6470,
        )

        return self.__parent__._cast(
            _6470.SpecialisedAssemblyHarmonicAnalysisOfSingleExcitation
        )

    @property
    def abstract_assembly_harmonic_analysis_of_single_excitation(
        self: "CastSelf",
    ) -> "_6368.AbstractAssemblyHarmonicAnalysisOfSingleExcitation":
        from mastapy._private.system_model.analyses_and_results.harmonic_analyses_single_excitation import (
            _6368,
        )

        return self.__parent__._cast(
            _6368.AbstractAssemblyHarmonicAnalysisOfSingleExcitation
        )

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
    def worm_gear_set_harmonic_analysis_of_single_excitation(
        self: "CastSelf",
    ) -> "WormGearSetHarmonicAnalysisOfSingleExcitation":
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
class WormGearSetHarmonicAnalysisOfSingleExcitation(
    _6428.GearSetHarmonicAnalysisOfSingleExcitation
):
    """WormGearSetHarmonicAnalysisOfSingleExcitation

    This is a mastapy class.
    """

    TYPE: ClassVar["Type"] = _WORM_GEAR_SET_HARMONIC_ANALYSIS_OF_SINGLE_EXCITATION

    wrapped: "Any"

    def __post_init__(self: "Self") -> None:
        """Override of the post initialisation magic method."""
        if not hasattr(self.wrapped, "reference_count"):
            self.wrapped.reference_count = 0

        self.wrapped.reference_count += 1

    @property
    @exception_bridge
    def assembly_design(self: "Self") -> "_2834.WormGearSet":
        """mastapy.system_model.part_model.gears.WormGearSet

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "AssemblyDesign")

        if temp is None:
            return None

        type_ = temp.GetType()
        return constructor.new(type_.Namespace, type_.Name)(temp)

    @property
    @exception_bridge
    def assembly_load_case(self: "Self") -> "_7910.WormGearSetLoadCase":
        """mastapy.system_model.analyses_and_results.static_loads.WormGearSetLoadCase

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "AssemblyLoadCase")

        if temp is None:
            return None

        type_ = temp.GetType()
        return constructor.new(type_.Namespace, type_.Name)(temp)

    @property
    @exception_bridge
    def gears_harmonic_analysis_of_single_excitation(
        self: "Self",
    ) -> "List[_6495.WormGearHarmonicAnalysisOfSingleExcitation]":
        """List[mastapy.system_model.analyses_and_results.harmonic_analyses_single_excitation.WormGearHarmonicAnalysisOfSingleExcitation]

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(
            self.wrapped, "GearsHarmonicAnalysisOfSingleExcitation"
        )

        if temp is None:
            return None

        value = conversion.pn_to_mp_objects_in_list(temp)

        if value is None:
            return None

        return value

    @property
    @exception_bridge
    def worm_gears_harmonic_analysis_of_single_excitation(
        self: "Self",
    ) -> "List[_6495.WormGearHarmonicAnalysisOfSingleExcitation]":
        """List[mastapy.system_model.analyses_and_results.harmonic_analyses_single_excitation.WormGearHarmonicAnalysisOfSingleExcitation]

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(
            self.wrapped, "WormGearsHarmonicAnalysisOfSingleExcitation"
        )

        if temp is None:
            return None

        value = conversion.pn_to_mp_objects_in_list(temp)

        if value is None:
            return None

        return value

    @property
    @exception_bridge
    def meshes_harmonic_analysis_of_single_excitation(
        self: "Self",
    ) -> "List[_6496.WormGearMeshHarmonicAnalysisOfSingleExcitation]":
        """List[mastapy.system_model.analyses_and_results.harmonic_analyses_single_excitation.WormGearMeshHarmonicAnalysisOfSingleExcitation]

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(
            self.wrapped, "MeshesHarmonicAnalysisOfSingleExcitation"
        )

        if temp is None:
            return None

        value = conversion.pn_to_mp_objects_in_list(temp)

        if value is None:
            return None

        return value

    @property
    @exception_bridge
    def worm_meshes_harmonic_analysis_of_single_excitation(
        self: "Self",
    ) -> "List[_6496.WormGearMeshHarmonicAnalysisOfSingleExcitation]":
        """List[mastapy.system_model.analyses_and_results.harmonic_analyses_single_excitation.WormGearMeshHarmonicAnalysisOfSingleExcitation]

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(
            self.wrapped, "WormMeshesHarmonicAnalysisOfSingleExcitation"
        )

        if temp is None:
            return None

        value = conversion.pn_to_mp_objects_in_list(temp)

        if value is None:
            return None

        return value

    @property
    def cast_to(self: "Self") -> "_Cast_WormGearSetHarmonicAnalysisOfSingleExcitation":
        """Cast to another type.

        Returns:
            _Cast_WormGearSetHarmonicAnalysisOfSingleExcitation
        """
        return _Cast_WormGearSetHarmonicAnalysisOfSingleExcitation(self)
