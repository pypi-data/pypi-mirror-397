"""CycloidalDiscCentralBearingConnectionCompoundModalAnalysis"""

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
from mastapy._private.system_model.analyses_and_results.modal_analyses.compound import (
    _5077,
)

_CYCLOIDAL_DISC_CENTRAL_BEARING_CONNECTION_COMPOUND_MODAL_ANALYSIS = python_net_import(
    "SMT.MastaAPI.SystemModel.AnalysesAndResults.ModalAnalyses.Compound",
    "CycloidalDiscCentralBearingConnectionCompoundModalAnalysis",
)

if TYPE_CHECKING:
    from typing import Any, List, Type, TypeVar

    from mastapy._private.system_model.analyses_and_results import _2943
    from mastapy._private.system_model.analyses_and_results.analysis_cases import (
        _7935,
        _7939,
    )
    from mastapy._private.system_model.analyses_and_results.modal_analyses import _4939
    from mastapy._private.system_model.analyses_and_results.modal_analyses.compound import (
        _5056,
        _5088,
        _5152,
    )

    Self = TypeVar(
        "Self", bound="CycloidalDiscCentralBearingConnectionCompoundModalAnalysis"
    )
    CastSelf = TypeVar(
        "CastSelf",
        bound="CycloidalDiscCentralBearingConnectionCompoundModalAnalysis._Cast_CycloidalDiscCentralBearingConnectionCompoundModalAnalysis",
    )


__docformat__ = "restructuredtext en"
__all__ = ("CycloidalDiscCentralBearingConnectionCompoundModalAnalysis",)


@extended_dataclass(frozen=True, slots=True, weakref_slot=True)
class _Cast_CycloidalDiscCentralBearingConnectionCompoundModalAnalysis:
    """Special nested class for casting CycloidalDiscCentralBearingConnectionCompoundModalAnalysis to subclasses."""

    __parent__: "CycloidalDiscCentralBearingConnectionCompoundModalAnalysis"

    @property
    def coaxial_connection_compound_modal_analysis(
        self: "CastSelf",
    ) -> "_5077.CoaxialConnectionCompoundModalAnalysis":
        return self.__parent__._cast(_5077.CoaxialConnectionCompoundModalAnalysis)

    @property
    def shaft_to_mountable_component_connection_compound_modal_analysis(
        self: "CastSelf",
    ) -> "_5152.ShaftToMountableComponentConnectionCompoundModalAnalysis":
        from mastapy._private.system_model.analyses_and_results.modal_analyses.compound import (
            _5152,
        )

        return self.__parent__._cast(
            _5152.ShaftToMountableComponentConnectionCompoundModalAnalysis
        )

    @property
    def abstract_shaft_to_mountable_component_connection_compound_modal_analysis(
        self: "CastSelf",
    ) -> "_5056.AbstractShaftToMountableComponentConnectionCompoundModalAnalysis":
        from mastapy._private.system_model.analyses_and_results.modal_analyses.compound import (
            _5056,
        )

        return self.__parent__._cast(
            _5056.AbstractShaftToMountableComponentConnectionCompoundModalAnalysis
        )

    @property
    def connection_compound_modal_analysis(
        self: "CastSelf",
    ) -> "_5088.ConnectionCompoundModalAnalysis":
        from mastapy._private.system_model.analyses_and_results.modal_analyses.compound import (
            _5088,
        )

        return self.__parent__._cast(_5088.ConnectionCompoundModalAnalysis)

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
    def cycloidal_disc_central_bearing_connection_compound_modal_analysis(
        self: "CastSelf",
    ) -> "CycloidalDiscCentralBearingConnectionCompoundModalAnalysis":
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
class CycloidalDiscCentralBearingConnectionCompoundModalAnalysis(
    _5077.CoaxialConnectionCompoundModalAnalysis
):
    """CycloidalDiscCentralBearingConnectionCompoundModalAnalysis

    This is a mastapy class.
    """

    TYPE: ClassVar["Type"] = (
        _CYCLOIDAL_DISC_CENTRAL_BEARING_CONNECTION_COMPOUND_MODAL_ANALYSIS
    )

    wrapped: "Any"

    def __post_init__(self: "Self") -> None:
        """Override of the post initialisation magic method."""
        if not hasattr(self.wrapped, "reference_count"):
            self.wrapped.reference_count = 0

        self.wrapped.reference_count += 1

    @property
    @exception_bridge
    def connection_analysis_cases_ready(
        self: "Self",
    ) -> "List[_4939.CycloidalDiscCentralBearingConnectionModalAnalysis]":
        """List[mastapy.system_model.analyses_and_results.modal_analyses.CycloidalDiscCentralBearingConnectionModalAnalysis]

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
    ) -> "List[_4939.CycloidalDiscCentralBearingConnectionModalAnalysis]":
        """List[mastapy.system_model.analyses_and_results.modal_analyses.CycloidalDiscCentralBearingConnectionModalAnalysis]

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
    ) -> "_Cast_CycloidalDiscCentralBearingConnectionCompoundModalAnalysis":
        """Cast to another type.

        Returns:
            _Cast_CycloidalDiscCentralBearingConnectionCompoundModalAnalysis
        """
        return _Cast_CycloidalDiscCentralBearingConnectionCompoundModalAnalysis(self)
