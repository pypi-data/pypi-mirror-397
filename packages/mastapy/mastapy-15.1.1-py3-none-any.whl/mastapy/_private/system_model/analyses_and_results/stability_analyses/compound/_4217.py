"""BeltConnectionCompoundStabilityAnalysis"""

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
from mastapy._private.system_model.analyses_and_results.stability_analyses.compound import (
    _4273,
)

_BELT_CONNECTION_COMPOUND_STABILITY_ANALYSIS = python_net_import(
    "SMT.MastaAPI.SystemModel.AnalysesAndResults.StabilityAnalyses.Compound",
    "BeltConnectionCompoundStabilityAnalysis",
)

if TYPE_CHECKING:
    from typing import Any, List, Type, TypeVar

    from mastapy._private.system_model.analyses_and_results import _2943
    from mastapy._private.system_model.analyses_and_results.analysis_cases import (
        _7935,
        _7939,
    )
    from mastapy._private.system_model.analyses_and_results.stability_analyses import (
        _4081,
    )
    from mastapy._private.system_model.analyses_and_results.stability_analyses.compound import (
        _4243,
        _4248,
    )
    from mastapy._private.system_model.connections_and_sockets import _2527

    Self = TypeVar("Self", bound="BeltConnectionCompoundStabilityAnalysis")
    CastSelf = TypeVar(
        "CastSelf",
        bound="BeltConnectionCompoundStabilityAnalysis._Cast_BeltConnectionCompoundStabilityAnalysis",
    )


__docformat__ = "restructuredtext en"
__all__ = ("BeltConnectionCompoundStabilityAnalysis",)


@extended_dataclass(frozen=True, slots=True, weakref_slot=True)
class _Cast_BeltConnectionCompoundStabilityAnalysis:
    """Special nested class for casting BeltConnectionCompoundStabilityAnalysis to subclasses."""

    __parent__: "BeltConnectionCompoundStabilityAnalysis"

    @property
    def inter_mountable_component_connection_compound_stability_analysis(
        self: "CastSelf",
    ) -> "_4273.InterMountableComponentConnectionCompoundStabilityAnalysis":
        return self.__parent__._cast(
            _4273.InterMountableComponentConnectionCompoundStabilityAnalysis
        )

    @property
    def connection_compound_stability_analysis(
        self: "CastSelf",
    ) -> "_4243.ConnectionCompoundStabilityAnalysis":
        from mastapy._private.system_model.analyses_and_results.stability_analyses.compound import (
            _4243,
        )

        return self.__parent__._cast(_4243.ConnectionCompoundStabilityAnalysis)

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
    def cvt_belt_connection_compound_stability_analysis(
        self: "CastSelf",
    ) -> "_4248.CVTBeltConnectionCompoundStabilityAnalysis":
        from mastapy._private.system_model.analyses_and_results.stability_analyses.compound import (
            _4248,
        )

        return self.__parent__._cast(_4248.CVTBeltConnectionCompoundStabilityAnalysis)

    @property
    def belt_connection_compound_stability_analysis(
        self: "CastSelf",
    ) -> "BeltConnectionCompoundStabilityAnalysis":
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
class BeltConnectionCompoundStabilityAnalysis(
    _4273.InterMountableComponentConnectionCompoundStabilityAnalysis
):
    """BeltConnectionCompoundStabilityAnalysis

    This is a mastapy class.
    """

    TYPE: ClassVar["Type"] = _BELT_CONNECTION_COMPOUND_STABILITY_ANALYSIS

    wrapped: "Any"

    def __post_init__(self: "Self") -> None:
        """Override of the post initialisation magic method."""
        if not hasattr(self.wrapped, "reference_count"):
            self.wrapped.reference_count = 0

        self.wrapped.reference_count += 1

    @property
    @exception_bridge
    def component_design(self: "Self") -> "_2527.BeltConnection":
        """mastapy.system_model.connections_and_sockets.BeltConnection

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
    def connection_design(self: "Self") -> "_2527.BeltConnection":
        """mastapy.system_model.connections_and_sockets.BeltConnection

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
    ) -> "List[_4081.BeltConnectionStabilityAnalysis]":
        """List[mastapy.system_model.analyses_and_results.stability_analyses.BeltConnectionStabilityAnalysis]

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
    ) -> "List[_4081.BeltConnectionStabilityAnalysis]":
        """List[mastapy.system_model.analyses_and_results.stability_analyses.BeltConnectionStabilityAnalysis]

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
    def cast_to(self: "Self") -> "_Cast_BeltConnectionCompoundStabilityAnalysis":
        """Cast to another type.

        Returns:
            _Cast_BeltConnectionCompoundStabilityAnalysis
        """
        return _Cast_BeltConnectionCompoundStabilityAnalysis(self)
