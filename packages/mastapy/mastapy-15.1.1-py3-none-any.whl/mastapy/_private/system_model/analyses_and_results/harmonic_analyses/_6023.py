"""AbstractShaftOrHousingHarmonicAnalysis"""

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
from mastapy._private.system_model.analyses_and_results.harmonic_analyses import _6047

_ABSTRACT_SHAFT_OR_HOUSING_HARMONIC_ANALYSIS = python_net_import(
    "SMT.MastaAPI.SystemModel.AnalysesAndResults.HarmonicAnalyses",
    "AbstractShaftOrHousingHarmonicAnalysis",
)

if TYPE_CHECKING:
    from typing import Any, Type, TypeVar

    from mastapy._private.system_model.analyses_and_results import _2943, _2945, _2949
    from mastapy._private.system_model.analyses_and_results.analysis_cases import (
        _7941,
        _7944,
    )
    from mastapy._private.system_model.analyses_and_results.harmonic_analyses import (
        _6022,
        _6067,
        _6093,
        _6136,
        _6154,
    )
    from mastapy._private.system_model.analyses_and_results.system_deflections import (
        _2978,
    )
    from mastapy._private.system_model.part_model import _2705

    Self = TypeVar("Self", bound="AbstractShaftOrHousingHarmonicAnalysis")
    CastSelf = TypeVar(
        "CastSelf",
        bound="AbstractShaftOrHousingHarmonicAnalysis._Cast_AbstractShaftOrHousingHarmonicAnalysis",
    )


__docformat__ = "restructuredtext en"
__all__ = ("AbstractShaftOrHousingHarmonicAnalysis",)


@extended_dataclass(frozen=True, slots=True, weakref_slot=True)
class _Cast_AbstractShaftOrHousingHarmonicAnalysis:
    """Special nested class for casting AbstractShaftOrHousingHarmonicAnalysis to subclasses."""

    __parent__: "AbstractShaftOrHousingHarmonicAnalysis"

    @property
    def component_harmonic_analysis(
        self: "CastSelf",
    ) -> "_6047.ComponentHarmonicAnalysis":
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
    def abstract_shaft_harmonic_analysis(
        self: "CastSelf",
    ) -> "_6022.AbstractShaftHarmonicAnalysis":
        from mastapy._private.system_model.analyses_and_results.harmonic_analyses import (
            _6022,
        )

        return self.__parent__._cast(_6022.AbstractShaftHarmonicAnalysis)

    @property
    def cycloidal_disc_harmonic_analysis(
        self: "CastSelf",
    ) -> "_6067.CycloidalDiscHarmonicAnalysis":
        from mastapy._private.system_model.analyses_and_results.harmonic_analyses import (
            _6067,
        )

        return self.__parent__._cast(_6067.CycloidalDiscHarmonicAnalysis)

    @property
    def fe_part_harmonic_analysis(self: "CastSelf") -> "_6093.FEPartHarmonicAnalysis":
        from mastapy._private.system_model.analyses_and_results.harmonic_analyses import (
            _6093,
        )

        return self.__parent__._cast(_6093.FEPartHarmonicAnalysis)

    @property
    def shaft_harmonic_analysis(self: "CastSelf") -> "_6154.ShaftHarmonicAnalysis":
        from mastapy._private.system_model.analyses_and_results.harmonic_analyses import (
            _6154,
        )

        return self.__parent__._cast(_6154.ShaftHarmonicAnalysis)

    @property
    def abstract_shaft_or_housing_harmonic_analysis(
        self: "CastSelf",
    ) -> "AbstractShaftOrHousingHarmonicAnalysis":
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
class AbstractShaftOrHousingHarmonicAnalysis(_6047.ComponentHarmonicAnalysis):
    """AbstractShaftOrHousingHarmonicAnalysis

    This is a mastapy class.
    """

    TYPE: ClassVar["Type"] = _ABSTRACT_SHAFT_OR_HOUSING_HARMONIC_ANALYSIS

    wrapped: "Any"

    def __post_init__(self: "Self") -> None:
        """Override of the post initialisation magic method."""
        if not hasattr(self.wrapped, "reference_count"):
            self.wrapped.reference_count = 0

        self.wrapped.reference_count += 1

    @property
    @exception_bridge
    def component_design(self: "Self") -> "_2705.AbstractShaftOrHousing":
        """mastapy.system_model.part_model.AbstractShaftOrHousing

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
    def system_deflection_results(
        self: "Self",
    ) -> "_2978.AbstractShaftOrHousingSystemDeflection":
        """mastapy.system_model.analyses_and_results.system_deflections.AbstractShaftOrHousingSystemDeflection

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "SystemDeflectionResults")

        if temp is None:
            return None

        type_ = temp.GetType()
        return constructor.new(type_.Namespace, type_.Name)(temp)

    @property
    def cast_to(self: "Self") -> "_Cast_AbstractShaftOrHousingHarmonicAnalysis":
        """Cast to another type.

        Returns:
            _Cast_AbstractShaftOrHousingHarmonicAnalysis
        """
        return _Cast_AbstractShaftOrHousingHarmonicAnalysis(self)
