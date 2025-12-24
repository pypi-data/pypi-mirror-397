"""PlanetaryConnectionDynamicAnalysis"""

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
from mastapy._private.system_model.analyses_and_results.dynamic_analyses import _6742

_PLANETARY_CONNECTION_DYNAMIC_ANALYSIS = python_net_import(
    "SMT.MastaAPI.SystemModel.AnalysesAndResults.DynamicAnalyses",
    "PlanetaryConnectionDynamicAnalysis",
)

if TYPE_CHECKING:
    from typing import Any, Type, TypeVar

    from mastapy._private.system_model.analyses_and_results import _2941, _2943, _2945
    from mastapy._private.system_model.analyses_and_results.analysis_cases import (
        _7934,
        _7936,
        _7937,
    )
    from mastapy._private.system_model.analyses_and_results.dynamic_analyses import (
        _6644,
        _6676,
    )
    from mastapy._private.system_model.analyses_and_results.static_loads import _7855
    from mastapy._private.system_model.connections_and_sockets import _2546

    Self = TypeVar("Self", bound="PlanetaryConnectionDynamicAnalysis")
    CastSelf = TypeVar(
        "CastSelf",
        bound="PlanetaryConnectionDynamicAnalysis._Cast_PlanetaryConnectionDynamicAnalysis",
    )


__docformat__ = "restructuredtext en"
__all__ = ("PlanetaryConnectionDynamicAnalysis",)


@extended_dataclass(frozen=True, slots=True, weakref_slot=True)
class _Cast_PlanetaryConnectionDynamicAnalysis:
    """Special nested class for casting PlanetaryConnectionDynamicAnalysis to subclasses."""

    __parent__: "PlanetaryConnectionDynamicAnalysis"

    @property
    def shaft_to_mountable_component_connection_dynamic_analysis(
        self: "CastSelf",
    ) -> "_6742.ShaftToMountableComponentConnectionDynamicAnalysis":
        return self.__parent__._cast(
            _6742.ShaftToMountableComponentConnectionDynamicAnalysis
        )

    @property
    def abstract_shaft_to_mountable_component_connection_dynamic_analysis(
        self: "CastSelf",
    ) -> "_6644.AbstractShaftToMountableComponentConnectionDynamicAnalysis":
        from mastapy._private.system_model.analyses_and_results.dynamic_analyses import (
            _6644,
        )

        return self.__parent__._cast(
            _6644.AbstractShaftToMountableComponentConnectionDynamicAnalysis
        )

    @property
    def connection_dynamic_analysis(
        self: "CastSelf",
    ) -> "_6676.ConnectionDynamicAnalysis":
        from mastapy._private.system_model.analyses_and_results.dynamic_analyses import (
            _6676,
        )

        return self.__parent__._cast(_6676.ConnectionDynamicAnalysis)

    @property
    def connection_fe_analysis(self: "CastSelf") -> "_7936.ConnectionFEAnalysis":
        from mastapy._private.system_model.analyses_and_results.analysis_cases import (
            _7936,
        )

        return self.__parent__._cast(_7936.ConnectionFEAnalysis)

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
    def planetary_connection_dynamic_analysis(
        self: "CastSelf",
    ) -> "PlanetaryConnectionDynamicAnalysis":
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
class PlanetaryConnectionDynamicAnalysis(
    _6742.ShaftToMountableComponentConnectionDynamicAnalysis
):
    """PlanetaryConnectionDynamicAnalysis

    This is a mastapy class.
    """

    TYPE: ClassVar["Type"] = _PLANETARY_CONNECTION_DYNAMIC_ANALYSIS

    wrapped: "Any"

    def __post_init__(self: "Self") -> None:
        """Override of the post initialisation magic method."""
        if not hasattr(self.wrapped, "reference_count"):
            self.wrapped.reference_count = 0

        self.wrapped.reference_count += 1

    @property
    @exception_bridge
    def connection_design(self: "Self") -> "_2546.PlanetaryConnection":
        """mastapy.system_model.connections_and_sockets.PlanetaryConnection

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
    def connection_load_case(self: "Self") -> "_7855.PlanetaryConnectionLoadCase":
        """mastapy.system_model.analyses_and_results.static_loads.PlanetaryConnectionLoadCase

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "ConnectionLoadCase")

        if temp is None:
            return None

        type_ = temp.GetType()
        return constructor.new(type_.Namespace, type_.Name)(temp)

    @property
    def cast_to(self: "Self") -> "_Cast_PlanetaryConnectionDynamicAnalysis":
        """Cast to another type.

        Returns:
            _Cast_PlanetaryConnectionDynamicAnalysis
        """
        return _Cast_PlanetaryConnectionDynamicAnalysis(self)
