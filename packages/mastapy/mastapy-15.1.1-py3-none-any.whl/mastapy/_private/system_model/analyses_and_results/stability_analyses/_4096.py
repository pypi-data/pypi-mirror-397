"""CoaxialConnectionStabilityAnalysis"""

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
from mastapy._private.system_model.analyses_and_results.stability_analyses import _4173

_COAXIAL_CONNECTION_STABILITY_ANALYSIS = python_net_import(
    "SMT.MastaAPI.SystemModel.AnalysesAndResults.StabilityAnalyses",
    "CoaxialConnectionStabilityAnalysis",
)

if TYPE_CHECKING:
    from typing import Any, Type, TypeVar

    from mastapy._private.system_model.analyses_and_results import _2941, _2943, _2945
    from mastapy._private.system_model.analyses_and_results.analysis_cases import (
        _7934,
        _7937,
    )
    from mastapy._private.system_model.analyses_and_results.stability_analyses import (
        _4075,
        _4107,
        _4117,
    )
    from mastapy._private.system_model.analyses_and_results.static_loads import _7757
    from mastapy._private.system_model.connections_and_sockets import _2528

    Self = TypeVar("Self", bound="CoaxialConnectionStabilityAnalysis")
    CastSelf = TypeVar(
        "CastSelf",
        bound="CoaxialConnectionStabilityAnalysis._Cast_CoaxialConnectionStabilityAnalysis",
    )


__docformat__ = "restructuredtext en"
__all__ = ("CoaxialConnectionStabilityAnalysis",)


@extended_dataclass(frozen=True, slots=True, weakref_slot=True)
class _Cast_CoaxialConnectionStabilityAnalysis:
    """Special nested class for casting CoaxialConnectionStabilityAnalysis to subclasses."""

    __parent__: "CoaxialConnectionStabilityAnalysis"

    @property
    def shaft_to_mountable_component_connection_stability_analysis(
        self: "CastSelf",
    ) -> "_4173.ShaftToMountableComponentConnectionStabilityAnalysis":
        return self.__parent__._cast(
            _4173.ShaftToMountableComponentConnectionStabilityAnalysis
        )

    @property
    def abstract_shaft_to_mountable_component_connection_stability_analysis(
        self: "CastSelf",
    ) -> "_4075.AbstractShaftToMountableComponentConnectionStabilityAnalysis":
        from mastapy._private.system_model.analyses_and_results.stability_analyses import (
            _4075,
        )

        return self.__parent__._cast(
            _4075.AbstractShaftToMountableComponentConnectionStabilityAnalysis
        )

    @property
    def connection_stability_analysis(
        self: "CastSelf",
    ) -> "_4107.ConnectionStabilityAnalysis":
        from mastapy._private.system_model.analyses_and_results.stability_analyses import (
            _4107,
        )

        return self.__parent__._cast(_4107.ConnectionStabilityAnalysis)

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
    def cycloidal_disc_central_bearing_connection_stability_analysis(
        self: "CastSelf",
    ) -> "_4117.CycloidalDiscCentralBearingConnectionStabilityAnalysis":
        from mastapy._private.system_model.analyses_and_results.stability_analyses import (
            _4117,
        )

        return self.__parent__._cast(
            _4117.CycloidalDiscCentralBearingConnectionStabilityAnalysis
        )

    @property
    def coaxial_connection_stability_analysis(
        self: "CastSelf",
    ) -> "CoaxialConnectionStabilityAnalysis":
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
class CoaxialConnectionStabilityAnalysis(
    _4173.ShaftToMountableComponentConnectionStabilityAnalysis
):
    """CoaxialConnectionStabilityAnalysis

    This is a mastapy class.
    """

    TYPE: ClassVar["Type"] = _COAXIAL_CONNECTION_STABILITY_ANALYSIS

    wrapped: "Any"

    def __post_init__(self: "Self") -> None:
        """Override of the post initialisation magic method."""
        if not hasattr(self.wrapped, "reference_count"):
            self.wrapped.reference_count = 0

        self.wrapped.reference_count += 1

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
    def connection_load_case(self: "Self") -> "_7757.CoaxialConnectionLoadCase":
        """mastapy.system_model.analyses_and_results.static_loads.CoaxialConnectionLoadCase

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "ConnectionLoadCase")

        if temp is None:
            return None

        type_ = temp.GetType()
        return constructor.new(type_.Namespace, type_.Name)(temp)

    @property
    def cast_to(self: "Self") -> "_Cast_CoaxialConnectionStabilityAnalysis":
        """Cast to another type.

        Returns:
            _Cast_CoaxialConnectionStabilityAnalysis
        """
        return _Cast_CoaxialConnectionStabilityAnalysis(self)
