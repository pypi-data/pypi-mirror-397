"""AGMAGleasonConicalGearSetHarmonicAnalysis"""

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
from mastapy._private.system_model.analyses_and_results.harmonic_analyses import _6056

_AGMA_GLEASON_CONICAL_GEAR_SET_HARMONIC_ANALYSIS = python_net_import(
    "SMT.MastaAPI.SystemModel.AnalysesAndResults.HarmonicAnalyses",
    "AGMAGleasonConicalGearSetHarmonicAnalysis",
)

if TYPE_CHECKING:
    from typing import Any, List, Type, TypeVar

    from mastapy._private.system_model.analyses_and_results import _2943, _2945, _2949
    from mastapy._private.system_model.analyses_and_results.analysis_cases import (
        _7941,
        _7944,
    )
    from mastapy._private.system_model.analyses_and_results.harmonic_analyses import (
        _6020,
        _6025,
        _6026,
        _6034,
        _6039,
        _6101,
        _6118,
        _6136,
        _6158,
        _6162,
        _6169,
        _6172,
        _6191,
    )
    from mastapy._private.system_model.analyses_and_results.system_deflections import (
        _2982,
    )
    from mastapy._private.system_model.part_model.gears import _2795

    Self = TypeVar("Self", bound="AGMAGleasonConicalGearSetHarmonicAnalysis")
    CastSelf = TypeVar(
        "CastSelf",
        bound="AGMAGleasonConicalGearSetHarmonicAnalysis._Cast_AGMAGleasonConicalGearSetHarmonicAnalysis",
    )


__docformat__ = "restructuredtext en"
__all__ = ("AGMAGleasonConicalGearSetHarmonicAnalysis",)


@extended_dataclass(frozen=True, slots=True, weakref_slot=True)
class _Cast_AGMAGleasonConicalGearSetHarmonicAnalysis:
    """Special nested class for casting AGMAGleasonConicalGearSetHarmonicAnalysis to subclasses."""

    __parent__: "AGMAGleasonConicalGearSetHarmonicAnalysis"

    @property
    def conical_gear_set_harmonic_analysis(
        self: "CastSelf",
    ) -> "_6056.ConicalGearSetHarmonicAnalysis":
        return self.__parent__._cast(_6056.ConicalGearSetHarmonicAnalysis)

    @property
    def gear_set_harmonic_analysis(self: "CastSelf") -> "_6101.GearSetHarmonicAnalysis":
        from mastapy._private.system_model.analyses_and_results.harmonic_analyses import (
            _6101,
        )

        return self.__parent__._cast(_6101.GearSetHarmonicAnalysis)

    @property
    def specialised_assembly_harmonic_analysis(
        self: "CastSelf",
    ) -> "_6158.SpecialisedAssemblyHarmonicAnalysis":
        from mastapy._private.system_model.analyses_and_results.harmonic_analyses import (
            _6158,
        )

        return self.__parent__._cast(_6158.SpecialisedAssemblyHarmonicAnalysis)

    @property
    def abstract_assembly_harmonic_analysis(
        self: "CastSelf",
    ) -> "_6020.AbstractAssemblyHarmonicAnalysis":
        from mastapy._private.system_model.analyses_and_results.harmonic_analyses import (
            _6020,
        )

        return self.__parent__._cast(_6020.AbstractAssemblyHarmonicAnalysis)

    @property
    def part_harmonic_analysis(self: "CastSelf") -> "_6136.PartHarmonicAnalysis":
        from mastapy._private.system_model.analyses_and_results.harmonic_analyses import (
            _6136,
        )

        return self.__parent__._cast(_6136.PartHarmonicAnalysis)

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
    def bevel_differential_gear_set_harmonic_analysis(
        self: "CastSelf",
    ) -> "_6034.BevelDifferentialGearSetHarmonicAnalysis":
        from mastapy._private.system_model.analyses_and_results.harmonic_analyses import (
            _6034,
        )

        return self.__parent__._cast(_6034.BevelDifferentialGearSetHarmonicAnalysis)

    @property
    def bevel_gear_set_harmonic_analysis(
        self: "CastSelf",
    ) -> "_6039.BevelGearSetHarmonicAnalysis":
        from mastapy._private.system_model.analyses_and_results.harmonic_analyses import (
            _6039,
        )

        return self.__parent__._cast(_6039.BevelGearSetHarmonicAnalysis)

    @property
    def hypoid_gear_set_harmonic_analysis(
        self: "CastSelf",
    ) -> "_6118.HypoidGearSetHarmonicAnalysis":
        from mastapy._private.system_model.analyses_and_results.harmonic_analyses import (
            _6118,
        )

        return self.__parent__._cast(_6118.HypoidGearSetHarmonicAnalysis)

    @property
    def spiral_bevel_gear_set_harmonic_analysis(
        self: "CastSelf",
    ) -> "_6162.SpiralBevelGearSetHarmonicAnalysis":
        from mastapy._private.system_model.analyses_and_results.harmonic_analyses import (
            _6162,
        )

        return self.__parent__._cast(_6162.SpiralBevelGearSetHarmonicAnalysis)

    @property
    def straight_bevel_diff_gear_set_harmonic_analysis(
        self: "CastSelf",
    ) -> "_6169.StraightBevelDiffGearSetHarmonicAnalysis":
        from mastapy._private.system_model.analyses_and_results.harmonic_analyses import (
            _6169,
        )

        return self.__parent__._cast(_6169.StraightBevelDiffGearSetHarmonicAnalysis)

    @property
    def straight_bevel_gear_set_harmonic_analysis(
        self: "CastSelf",
    ) -> "_6172.StraightBevelGearSetHarmonicAnalysis":
        from mastapy._private.system_model.analyses_and_results.harmonic_analyses import (
            _6172,
        )

        return self.__parent__._cast(_6172.StraightBevelGearSetHarmonicAnalysis)

    @property
    def zerol_bevel_gear_set_harmonic_analysis(
        self: "CastSelf",
    ) -> "_6191.ZerolBevelGearSetHarmonicAnalysis":
        from mastapy._private.system_model.analyses_and_results.harmonic_analyses import (
            _6191,
        )

        return self.__parent__._cast(_6191.ZerolBevelGearSetHarmonicAnalysis)

    @property
    def agma_gleason_conical_gear_set_harmonic_analysis(
        self: "CastSelf",
    ) -> "AGMAGleasonConicalGearSetHarmonicAnalysis":
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
class AGMAGleasonConicalGearSetHarmonicAnalysis(_6056.ConicalGearSetHarmonicAnalysis):
    """AGMAGleasonConicalGearSetHarmonicAnalysis

    This is a mastapy class.
    """

    TYPE: ClassVar["Type"] = _AGMA_GLEASON_CONICAL_GEAR_SET_HARMONIC_ANALYSIS

    wrapped: "Any"

    def __post_init__(self: "Self") -> None:
        """Override of the post initialisation magic method."""
        if not hasattr(self.wrapped, "reference_count"):
            self.wrapped.reference_count = 0

        self.wrapped.reference_count += 1

    @property
    @exception_bridge
    def assembly_design(self: "Self") -> "_2795.AGMAGleasonConicalGearSet":
        """mastapy.system_model.part_model.gears.AGMAGleasonConicalGearSet

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
    def conical_gears_harmonic_analysis(
        self: "Self",
    ) -> "List[_6025.AGMAGleasonConicalGearHarmonicAnalysis]":
        """List[mastapy.system_model.analyses_and_results.harmonic_analyses.AGMAGleasonConicalGearHarmonicAnalysis]

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "ConicalGearsHarmonicAnalysis")

        if temp is None:
            return None

        value = conversion.pn_to_mp_objects_in_list(temp)

        if value is None:
            return None

        return value

    @property
    @exception_bridge
    def agma_gleason_conical_gears_harmonic_analysis(
        self: "Self",
    ) -> "List[_6025.AGMAGleasonConicalGearHarmonicAnalysis]":
        """List[mastapy.system_model.analyses_and_results.harmonic_analyses.AGMAGleasonConicalGearHarmonicAnalysis]

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(
            self.wrapped, "AGMAGleasonConicalGearsHarmonicAnalysis"
        )

        if temp is None:
            return None

        value = conversion.pn_to_mp_objects_in_list(temp)

        if value is None:
            return None

        return value

    @property
    @exception_bridge
    def conical_meshes_harmonic_analysis(
        self: "Self",
    ) -> "List[_6026.AGMAGleasonConicalGearMeshHarmonicAnalysis]":
        """List[mastapy.system_model.analyses_and_results.harmonic_analyses.AGMAGleasonConicalGearMeshHarmonicAnalysis]

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "ConicalMeshesHarmonicAnalysis")

        if temp is None:
            return None

        value = conversion.pn_to_mp_objects_in_list(temp)

        if value is None:
            return None

        return value

    @property
    @exception_bridge
    def agma_gleason_conical_meshes_harmonic_analysis(
        self: "Self",
    ) -> "List[_6026.AGMAGleasonConicalGearMeshHarmonicAnalysis]":
        """List[mastapy.system_model.analyses_and_results.harmonic_analyses.AGMAGleasonConicalGearMeshHarmonicAnalysis]

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(
            self.wrapped, "AGMAGleasonConicalMeshesHarmonicAnalysis"
        )

        if temp is None:
            return None

        value = conversion.pn_to_mp_objects_in_list(temp)

        if value is None:
            return None

        return value

    @property
    @exception_bridge
    def system_deflection_results(
        self: "Self",
    ) -> "_2982.AGMAGleasonConicalGearSetSystemDeflection":
        """mastapy.system_model.analyses_and_results.system_deflections.AGMAGleasonConicalGearSetSystemDeflection

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "SystemDeflectionResults")

        if temp is None:
            return None

        type_ = temp.GetType()
        return constructor.new(type_.Namespace, type_.Name)(temp)

    @property
    def cast_to(self: "Self") -> "_Cast_AGMAGleasonConicalGearSetHarmonicAnalysis":
        """Cast to another type.

        Returns:
            _Cast_AGMAGleasonConicalGearSetHarmonicAnalysis
        """
        return _Cast_AGMAGleasonConicalGearSetHarmonicAnalysis(self)
