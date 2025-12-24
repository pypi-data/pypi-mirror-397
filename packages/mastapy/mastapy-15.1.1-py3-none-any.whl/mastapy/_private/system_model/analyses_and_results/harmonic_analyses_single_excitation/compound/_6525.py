"""CoaxialConnectionCompoundHarmonicAnalysisOfSingleExcitation"""

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
from mastapy._private.system_model.analyses_and_results.harmonic_analyses_single_excitation.compound import (
    _6600,
)

_COAXIAL_CONNECTION_COMPOUND_HARMONIC_ANALYSIS_OF_SINGLE_EXCITATION = python_net_import(
    "SMT.MastaAPI.SystemModel.AnalysesAndResults.HarmonicAnalysesSingleExcitation.Compound",
    "CoaxialConnectionCompoundHarmonicAnalysisOfSingleExcitation",
)

if TYPE_CHECKING:
    from typing import Any, List, Type, TypeVar

    from mastapy._private.system_model.analyses_and_results import _2943
    from mastapy._private.system_model.analyses_and_results.analysis_cases import (
        _7935,
        _7939,
    )
    from mastapy._private.system_model.analyses_and_results.harmonic_analyses_single_excitation import (
        _6392,
    )
    from mastapy._private.system_model.analyses_and_results.harmonic_analyses_single_excitation.compound import (
        _6504,
        _6536,
        _6545,
    )
    from mastapy._private.system_model.connections_and_sockets import _2528

    Self = TypeVar(
        "Self", bound="CoaxialConnectionCompoundHarmonicAnalysisOfSingleExcitation"
    )
    CastSelf = TypeVar(
        "CastSelf",
        bound="CoaxialConnectionCompoundHarmonicAnalysisOfSingleExcitation._Cast_CoaxialConnectionCompoundHarmonicAnalysisOfSingleExcitation",
    )


__docformat__ = "restructuredtext en"
__all__ = ("CoaxialConnectionCompoundHarmonicAnalysisOfSingleExcitation",)


@extended_dataclass(frozen=True, slots=True, weakref_slot=True)
class _Cast_CoaxialConnectionCompoundHarmonicAnalysisOfSingleExcitation:
    """Special nested class for casting CoaxialConnectionCompoundHarmonicAnalysisOfSingleExcitation to subclasses."""

    __parent__: "CoaxialConnectionCompoundHarmonicAnalysisOfSingleExcitation"

    @property
    def shaft_to_mountable_component_connection_compound_harmonic_analysis_of_single_excitation(
        self: "CastSelf",
    ) -> "_6600.ShaftToMountableComponentConnectionCompoundHarmonicAnalysisOfSingleExcitation":
        return self.__parent__._cast(
            _6600.ShaftToMountableComponentConnectionCompoundHarmonicAnalysisOfSingleExcitation
        )

    @property
    def abstract_shaft_to_mountable_component_connection_compound_harmonic_analysis_of_single_excitation(
        self: "CastSelf",
    ) -> "_6504.AbstractShaftToMountableComponentConnectionCompoundHarmonicAnalysisOfSingleExcitation":
        from mastapy._private.system_model.analyses_and_results.harmonic_analyses_single_excitation.compound import (
            _6504,
        )

        return self.__parent__._cast(
            _6504.AbstractShaftToMountableComponentConnectionCompoundHarmonicAnalysisOfSingleExcitation
        )

    @property
    def connection_compound_harmonic_analysis_of_single_excitation(
        self: "CastSelf",
    ) -> "_6536.ConnectionCompoundHarmonicAnalysisOfSingleExcitation":
        from mastapy._private.system_model.analyses_and_results.harmonic_analyses_single_excitation.compound import (
            _6536,
        )

        return self.__parent__._cast(
            _6536.ConnectionCompoundHarmonicAnalysisOfSingleExcitation
        )

    @property
    def connection_compound_analysis(
        self: "CastSelf",
    ) -> "_7935.ConnectionCompoundAnalysis":
        from mastapy._private.system_model.analyses_and_results.analysis_cases import (
            _7935,
        )

        return self.__parent__._cast(_7935.ConnectionCompoundAnalysis)

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
    def cycloidal_disc_central_bearing_connection_compound_harmonic_analysis_of_single_excitation(
        self: "CastSelf",
    ) -> "_6545.CycloidalDiscCentralBearingConnectionCompoundHarmonicAnalysisOfSingleExcitation":
        from mastapy._private.system_model.analyses_and_results.harmonic_analyses_single_excitation.compound import (
            _6545,
        )

        return self.__parent__._cast(
            _6545.CycloidalDiscCentralBearingConnectionCompoundHarmonicAnalysisOfSingleExcitation
        )

    @property
    def coaxial_connection_compound_harmonic_analysis_of_single_excitation(
        self: "CastSelf",
    ) -> "CoaxialConnectionCompoundHarmonicAnalysisOfSingleExcitation":
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
class CoaxialConnectionCompoundHarmonicAnalysisOfSingleExcitation(
    _6600.ShaftToMountableComponentConnectionCompoundHarmonicAnalysisOfSingleExcitation
):
    """CoaxialConnectionCompoundHarmonicAnalysisOfSingleExcitation

    This is a mastapy class.
    """

    TYPE: ClassVar["Type"] = (
        _COAXIAL_CONNECTION_COMPOUND_HARMONIC_ANALYSIS_OF_SINGLE_EXCITATION
    )

    wrapped: "Any"

    def __post_init__(self: "Self") -> None:
        """Override of the post initialisation magic method."""
        if not hasattr(self.wrapped, "reference_count"):
            self.wrapped.reference_count = 0

        self.wrapped.reference_count += 1

    @property
    @exception_bridge
    def component_design(self: "Self") -> "_2528.CoaxialConnection":
        """mastapy.system_model.connections_and_sockets.CoaxialConnection

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
    def connection_design(self: "Self") -> "_2528.CoaxialConnection":
        """mastapy.system_model.connections_and_sockets.CoaxialConnection

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
    def connection_analysis_cases_ready(
        self: "Self",
    ) -> "List[_6392.CoaxialConnectionHarmonicAnalysisOfSingleExcitation]":
        """List[mastapy.system_model.analyses_and_results.harmonic_analyses_single_excitation.CoaxialConnectionHarmonicAnalysisOfSingleExcitation]

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "ConnectionAnalysisCasesReady")

        if temp is None:
            return None

        value = conversion.pn_to_mp_objects_in_list(temp)

        if value is None:
            return None

        return value

    @property
    @exception_bridge
    def connection_analysis_cases(
        self: "Self",
    ) -> "List[_6392.CoaxialConnectionHarmonicAnalysisOfSingleExcitation]":
        """List[mastapy.system_model.analyses_and_results.harmonic_analyses_single_excitation.CoaxialConnectionHarmonicAnalysisOfSingleExcitation]

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "ConnectionAnalysisCases")

        if temp is None:
            return None

        value = conversion.pn_to_mp_objects_in_list(temp)

        if value is None:
            return None

        return value

    @property
    def cast_to(
        self: "Self",
    ) -> "_Cast_CoaxialConnectionCompoundHarmonicAnalysisOfSingleExcitation":
        """Cast to another type.

        Returns:
            _Cast_CoaxialConnectionCompoundHarmonicAnalysisOfSingleExcitation
        """
        return _Cast_CoaxialConnectionCompoundHarmonicAnalysisOfSingleExcitation(self)
