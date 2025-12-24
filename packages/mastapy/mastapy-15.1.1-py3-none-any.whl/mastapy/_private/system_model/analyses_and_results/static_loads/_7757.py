"""CoaxialConnectionLoadCase"""

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
from mastapy._private.system_model.analyses_and_results.static_loads import _7876

_COAXIAL_CONNECTION_LOAD_CASE = python_net_import(
    "SMT.MastaAPI.SystemModel.AnalysesAndResults.StaticLoads",
    "CoaxialConnectionLoadCase",
)

if TYPE_CHECKING:
    from typing import Any, Type, TypeVar

    from mastapy._private.system_model.analyses_and_results import _2941, _2943, _2945
    from mastapy._private.system_model.analyses_and_results.static_loads import (
        _7730,
        _7770,
        _7779,
    )
    from mastapy._private.system_model.connections_and_sockets import _2528

    Self = TypeVar("Self", bound="CoaxialConnectionLoadCase")
    CastSelf = TypeVar(
        "CastSelf", bound="CoaxialConnectionLoadCase._Cast_CoaxialConnectionLoadCase"
    )


__docformat__ = "restructuredtext en"
__all__ = ("CoaxialConnectionLoadCase",)


@extended_dataclass(frozen=True, slots=True, weakref_slot=True)
class _Cast_CoaxialConnectionLoadCase:
    """Special nested class for casting CoaxialConnectionLoadCase to subclasses."""

    __parent__: "CoaxialConnectionLoadCase"

    @property
    def shaft_to_mountable_component_connection_load_case(
        self: "CastSelf",
    ) -> "_7876.ShaftToMountableComponentConnectionLoadCase":
        return self.__parent__._cast(_7876.ShaftToMountableComponentConnectionLoadCase)

    @property
    def abstract_shaft_to_mountable_component_connection_load_case(
        self: "CastSelf",
    ) -> "_7730.AbstractShaftToMountableComponentConnectionLoadCase":
        from mastapy._private.system_model.analyses_and_results.static_loads import (
            _7730,
        )

        return self.__parent__._cast(
            _7730.AbstractShaftToMountableComponentConnectionLoadCase
        )

    @property
    def connection_load_case(self: "CastSelf") -> "_7770.ConnectionLoadCase":
        from mastapy._private.system_model.analyses_and_results.static_loads import (
            _7770,
        )

        return self.__parent__._cast(_7770.ConnectionLoadCase)

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
    def cycloidal_disc_central_bearing_connection_load_case(
        self: "CastSelf",
    ) -> "_7779.CycloidalDiscCentralBearingConnectionLoadCase":
        from mastapy._private.system_model.analyses_and_results.static_loads import (
            _7779,
        )

        return self.__parent__._cast(
            _7779.CycloidalDiscCentralBearingConnectionLoadCase
        )

    @property
    def coaxial_connection_load_case(self: "CastSelf") -> "CoaxialConnectionLoadCase":
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
class CoaxialConnectionLoadCase(_7876.ShaftToMountableComponentConnectionLoadCase):
    """CoaxialConnectionLoadCase

    This is a mastapy class.
    """

    TYPE: ClassVar["Type"] = _COAXIAL_CONNECTION_LOAD_CASE

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
    def cast_to(self: "Self") -> "_Cast_CoaxialConnectionLoadCase":
        """Cast to another type.

        Returns:
            _Cast_CoaxialConnectionLoadCase
        """
        return _Cast_CoaxialConnectionLoadCase(self)
