"""PartToPartShearCouplingConnectionHarmonicAnalysis"""

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
from mastapy._private.system_model.analyses_and_results.harmonic_analyses import _6059

_PART_TO_PART_SHEAR_COUPLING_CONNECTION_HARMONIC_ANALYSIS = python_net_import(
    "SMT.MastaAPI.SystemModel.AnalysesAndResults.HarmonicAnalyses",
    "PartToPartShearCouplingConnectionHarmonicAnalysis",
)

if TYPE_CHECKING:
    from typing import Any, Type, TypeVar

    from mastapy._private.system_model.analyses_and_results import _2941, _2943, _2945
    from mastapy._private.system_model.analyses_and_results.analysis_cases import (
        _7934,
        _7937,
    )
    from mastapy._private.system_model.analyses_and_results.harmonic_analyses import (
        _6057,
        _6119,
    )
    from mastapy._private.system_model.analyses_and_results.static_loads import _7852
    from mastapy._private.system_model.analyses_and_results.system_deflections import (
        _3080,
    )
    from mastapy._private.system_model.connections_and_sockets.couplings import _2607

    Self = TypeVar("Self", bound="PartToPartShearCouplingConnectionHarmonicAnalysis")
    CastSelf = TypeVar(
        "CastSelf",
        bound="PartToPartShearCouplingConnectionHarmonicAnalysis._Cast_PartToPartShearCouplingConnectionHarmonicAnalysis",
    )


__docformat__ = "restructuredtext en"
__all__ = ("PartToPartShearCouplingConnectionHarmonicAnalysis",)


@extended_dataclass(frozen=True, slots=True, weakref_slot=True)
class _Cast_PartToPartShearCouplingConnectionHarmonicAnalysis:
    """Special nested class for casting PartToPartShearCouplingConnectionHarmonicAnalysis to subclasses."""

    __parent__: "PartToPartShearCouplingConnectionHarmonicAnalysis"

    @property
    def coupling_connection_harmonic_analysis(
        self: "CastSelf",
    ) -> "_6059.CouplingConnectionHarmonicAnalysis":
        return self.__parent__._cast(_6059.CouplingConnectionHarmonicAnalysis)

    @property
    def inter_mountable_component_connection_harmonic_analysis(
        self: "CastSelf",
    ) -> "_6119.InterMountableComponentConnectionHarmonicAnalysis":
        from mastapy._private.system_model.analyses_and_results.harmonic_analyses import (
            _6119,
        )

        return self.__parent__._cast(
            _6119.InterMountableComponentConnectionHarmonicAnalysis
        )

    @property
    def connection_harmonic_analysis(
        self: "CastSelf",
    ) -> "_6057.ConnectionHarmonicAnalysis":
        from mastapy._private.system_model.analyses_and_results.harmonic_analyses import (
            _6057,
        )

        return self.__parent__._cast(_6057.ConnectionHarmonicAnalysis)

    @property
    def connection_static_load_analysis_case(
        self: "CastSelf",
    ) -> "_7937.ConnectionStaticLoadAnalysisCase":
        from mastapy._private.system_model.analyses_and_results.analysis_cases import (
            _7937,
        )

        return self.__parent__._cast(_7937.ConnectionStaticLoadAnalysisCase)

    @property
    def connection_analysis_case(self: "CastSelf") -> "_7934.ConnectionAnalysisCase":
        from mastapy._private.system_model.analyses_and_results.analysis_cases import (
            _7934,
        )

        return self.__parent__._cast(_7934.ConnectionAnalysisCase)

    @property
    def connection_analysis(self: "CastSelf") -> "_2941.ConnectionAnalysis":
        from mastapy._private.system_model.analyses_and_results import _2941

        return self.__parent__._cast(_2941.ConnectionAnalysis)

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
    def part_to_part_shear_coupling_connection_harmonic_analysis(
        self: "CastSelf",
    ) -> "PartToPartShearCouplingConnectionHarmonicAnalysis":
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
class PartToPartShearCouplingConnectionHarmonicAnalysis(
    _6059.CouplingConnectionHarmonicAnalysis
):
    """PartToPartShearCouplingConnectionHarmonicAnalysis

    This is a mastapy class.
    """

    TYPE: ClassVar["Type"] = _PART_TO_PART_SHEAR_COUPLING_CONNECTION_HARMONIC_ANALYSIS

    wrapped: "Any"

    def __post_init__(self: "Self") -> None:
        """Override of the post initialisation magic method."""
        if not hasattr(self.wrapped, "reference_count"):
            self.wrapped.reference_count = 0

        self.wrapped.reference_count += 1

    @property
    @exception_bridge
    def connection_design(self: "Self") -> "_2607.PartToPartShearCouplingConnection":
        """mastapy.system_model.connections_and_sockets.couplings.PartToPartShearCouplingConnection

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "ConnectionDesign")

        if temp is None:
            return None

        type_ = temp.GetType()
        return constructor.new(type_.Namespace, type_.Name)(temp)

    @property
    @exception_bridge
    def connection_load_case(
        self: "Self",
    ) -> "_7852.PartToPartShearCouplingConnectionLoadCase":
        """mastapy.system_model.analyses_and_results.static_loads.PartToPartShearCouplingConnectionLoadCase

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "ConnectionLoadCase")

        if temp is None:
            return None

        type_ = temp.GetType()
        return constructor.new(type_.Namespace, type_.Name)(temp)

    @property
    @exception_bridge
    def system_deflection_results(
        self: "Self",
    ) -> "_3080.PartToPartShearCouplingConnectionSystemDeflection":
        """mastapy.system_model.analyses_and_results.system_deflections.PartToPartShearCouplingConnectionSystemDeflection

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "SystemDeflectionResults")

        if temp is None:
            return None

        type_ = temp.GetType()
        return constructor.new(type_.Namespace, type_.Name)(temp)

    @property
    def cast_to(
        self: "Self",
    ) -> "_Cast_PartToPartShearCouplingConnectionHarmonicAnalysis":
        """Cast to another type.

        Returns:
            _Cast_PartToPartShearCouplingConnectionHarmonicAnalysis
        """
        return _Cast_PartToPartShearCouplingConnectionHarmonicAnalysis(self)
