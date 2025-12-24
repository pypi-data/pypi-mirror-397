"""StraightBevelGearHarmonicAnalysis"""

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
from mastapy._private.system_model.analyses_and_results.harmonic_analyses import _6037

_STRAIGHT_BEVEL_GEAR_HARMONIC_ANALYSIS = python_net_import(
    "SMT.MastaAPI.SystemModel.AnalysesAndResults.HarmonicAnalyses",
    "StraightBevelGearHarmonicAnalysis",
)

if TYPE_CHECKING:
    from typing import Any, Type, TypeVar

    from mastapy._private.system_model.analyses_and_results import _2943, _2945, _2949
    from mastapy._private.system_model.analyses_and_results.analysis_cases import (
        _7941,
        _7944,
    )
    from mastapy._private.system_model.analyses_and_results.harmonic_analyses import (
        _6025,
        _6047,
        _6054,
        _6096,
        _6134,
        _6136,
    )
    from mastapy._private.system_model.analyses_and_results.static_loads import _7887
    from mastapy._private.system_model.analyses_and_results.system_deflections import (
        _3112,
    )
    from mastapy._private.system_model.part_model.gears import _2829

    Self = TypeVar("Self", bound="StraightBevelGearHarmonicAnalysis")
    CastSelf = TypeVar(
        "CastSelf",
        bound="StraightBevelGearHarmonicAnalysis._Cast_StraightBevelGearHarmonicAnalysis",
    )


__docformat__ = "restructuredtext en"
__all__ = ("StraightBevelGearHarmonicAnalysis",)


@extended_dataclass(frozen=True, slots=True, weakref_slot=True)
class _Cast_StraightBevelGearHarmonicAnalysis:
    """Special nested class for casting StraightBevelGearHarmonicAnalysis to subclasses."""

    __parent__: "StraightBevelGearHarmonicAnalysis"

    @property
    def bevel_gear_harmonic_analysis(
        self: "CastSelf",
    ) -> "_6037.BevelGearHarmonicAnalysis":
        return self.__parent__._cast(_6037.BevelGearHarmonicAnalysis)

    @property
    def agma_gleason_conical_gear_harmonic_analysis(
        self: "CastSelf",
    ) -> "_6025.AGMAGleasonConicalGearHarmonicAnalysis":
        from mastapy._private.system_model.analyses_and_results.harmonic_analyses import (
            _6025,
        )

        return self.__parent__._cast(_6025.AGMAGleasonConicalGearHarmonicAnalysis)

    @property
    def conical_gear_harmonic_analysis(
        self: "CastSelf",
    ) -> "_6054.ConicalGearHarmonicAnalysis":
        from mastapy._private.system_model.analyses_and_results.harmonic_analyses import (
            _6054,
        )

        return self.__parent__._cast(_6054.ConicalGearHarmonicAnalysis)

    @property
    def gear_harmonic_analysis(self: "CastSelf") -> "_6096.GearHarmonicAnalysis":
        from mastapy._private.system_model.analyses_and_results.harmonic_analyses import (
            _6096,
        )

        return self.__parent__._cast(_6096.GearHarmonicAnalysis)

    @property
    def mountable_component_harmonic_analysis(
        self: "CastSelf",
    ) -> "_6134.MountableComponentHarmonicAnalysis":
        from mastapy._private.system_model.analyses_and_results.harmonic_analyses import (
            _6134,
        )

        return self.__parent__._cast(_6134.MountableComponentHarmonicAnalysis)

    @property
    def component_harmonic_analysis(
        self: "CastSelf",
    ) -> "_6047.ComponentHarmonicAnalysis":
        from mastapy._private.system_model.analyses_and_results.harmonic_analyses import (
            _6047,
        )

        return self.__parent__._cast(_6047.ComponentHarmonicAnalysis)

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
    def straight_bevel_gear_harmonic_analysis(
        self: "CastSelf",
    ) -> "StraightBevelGearHarmonicAnalysis":
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
class StraightBevelGearHarmonicAnalysis(_6037.BevelGearHarmonicAnalysis):
    """StraightBevelGearHarmonicAnalysis

    This is a mastapy class.
    """

    TYPE: ClassVar["Type"] = _STRAIGHT_BEVEL_GEAR_HARMONIC_ANALYSIS

    wrapped: "Any"

    def __post_init__(self: "Self") -> None:
        """Override of the post initialisation magic method."""
        if not hasattr(self.wrapped, "reference_count"):
            self.wrapped.reference_count = 0

        self.wrapped.reference_count += 1

    @property
    @exception_bridge
    def component_design(self: "Self") -> "_2829.StraightBevelGear":
        """mastapy.system_model.part_model.gears.StraightBevelGear

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
    def component_load_case(self: "Self") -> "_7887.StraightBevelGearLoadCase":
        """mastapy.system_model.analyses_and_results.static_loads.StraightBevelGearLoadCase

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "ComponentLoadCase")

        if temp is None:
            return None

        type_ = temp.GetType()
        return constructor.new(type_.Namespace, type_.Name)(temp)

    @property
    @exception_bridge
    def system_deflection_results(
        self: "Self",
    ) -> "_3112.StraightBevelGearSystemDeflection":
        """mastapy.system_model.analyses_and_results.system_deflections.StraightBevelGearSystemDeflection

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "SystemDeflectionResults")

        if temp is None:
            return None

        type_ = temp.GetType()
        return constructor.new(type_.Namespace, type_.Name)(temp)

    @property
    def cast_to(self: "Self") -> "_Cast_StraightBevelGearHarmonicAnalysis":
        """Cast to another type.

        Returns:
            _Cast_StraightBevelGearHarmonicAnalysis
        """
        return _Cast_StraightBevelGearHarmonicAnalysis(self)
