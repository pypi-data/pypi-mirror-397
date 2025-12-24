"""DynamicModelForHarmonicAnalysis"""

from __future__ import annotations

from typing import TYPE_CHECKING, ClassVar

from mastapy._private._internal.dataclasses import extended_dataclass
from mastapy._private._internal.exceptions import CastException
from mastapy._private._internal.python_net import python_net_import

from mastapy._private._internal import utility
from mastapy._private.system_model.analyses_and_results.dynamic_analyses import _6693

_DYNAMIC_MODEL_FOR_HARMONIC_ANALYSIS = python_net_import(
    "SMT.MastaAPI.SystemModel.AnalysesAndResults.HarmonicAnalyses",
    "DynamicModelForHarmonicAnalysis",
)

if TYPE_CHECKING:
    from typing import Any, Type, TypeVar

    from mastapy._private.system_model.analyses_and_results import _2942
    from mastapy._private.system_model.analyses_and_results.analysis_cases import (
        _7931,
        _7940,
        _7946,
    )
    from mastapy._private.system_model.analyses_and_results.harmonic_analyses.transfer_path_analyses import (
        _6192,
    )

    Self = TypeVar("Self", bound="DynamicModelForHarmonicAnalysis")
    CastSelf = TypeVar(
        "CastSelf",
        bound="DynamicModelForHarmonicAnalysis._Cast_DynamicModelForHarmonicAnalysis",
    )


__docformat__ = "restructuredtext en"
__all__ = ("DynamicModelForHarmonicAnalysis",)


@extended_dataclass(frozen=True, slots=True, weakref_slot=True)
class _Cast_DynamicModelForHarmonicAnalysis:
    """Special nested class for casting DynamicModelForHarmonicAnalysis to subclasses."""

    __parent__: "DynamicModelForHarmonicAnalysis"

    @property
    def dynamic_analysis(self: "CastSelf") -> "_6693.DynamicAnalysis":
        return self.__parent__._cast(_6693.DynamicAnalysis)

    @property
    def fe_analysis(self: "CastSelf") -> "_7940.FEAnalysis":
        from mastapy._private.system_model.analyses_and_results.analysis_cases import (
            _7940,
        )

        return self.__parent__._cast(_7940.FEAnalysis)

    @property
    def static_load_analysis_case(self: "CastSelf") -> "_7946.StaticLoadAnalysisCase":
        from mastapy._private.system_model.analyses_and_results.analysis_cases import (
            _7946,
        )

        return self.__parent__._cast(_7946.StaticLoadAnalysisCase)

    @property
    def analysis_case(self: "CastSelf") -> "_7931.AnalysisCase":
        from mastapy._private.system_model.analyses_and_results.analysis_cases import (
            _7931,
        )

        return self.__parent__._cast(_7931.AnalysisCase)

    @property
    def context(self: "CastSelf") -> "_2942.Context":
        from mastapy._private.system_model.analyses_and_results import _2942

        return self.__parent__._cast(_2942.Context)

    @property
    def dynamic_model_for_transfer_path_analysis(
        self: "CastSelf",
    ) -> "_6192.DynamicModelForTransferPathAnalysis":
        from mastapy._private.system_model.analyses_and_results.harmonic_analyses.transfer_path_analyses import (
            _6192,
        )

        return self.__parent__._cast(_6192.DynamicModelForTransferPathAnalysis)

    @property
    def dynamic_model_for_harmonic_analysis(
        self: "CastSelf",
    ) -> "DynamicModelForHarmonicAnalysis":
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
class DynamicModelForHarmonicAnalysis(_6693.DynamicAnalysis):
    """DynamicModelForHarmonicAnalysis

    This is a mastapy class.
    """

    TYPE: ClassVar["Type"] = _DYNAMIC_MODEL_FOR_HARMONIC_ANALYSIS

    wrapped: "Any"

    def __post_init__(self: "Self") -> None:
        """Override of the post initialisation magic method."""
        if not hasattr(self.wrapped, "reference_count"):
            self.wrapped.reference_count = 0

        self.wrapped.reference_count += 1

    @property
    def cast_to(self: "Self") -> "_Cast_DynamicModelForHarmonicAnalysis":
        """Cast to another type.

        Returns:
            _Cast_DynamicModelForHarmonicAnalysis
        """
        return _Cast_DynamicModelForHarmonicAnalysis(self)
