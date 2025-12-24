"""AbstractShaftToMountableComponentConnectionModalAnalysisAtAStiffness"""

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
from mastapy._private.system_model.analyses_and_results.modal_analyses_at_a_stiffness import (
    _5219,
)

_ABSTRACT_SHAFT_TO_MOUNTABLE_COMPONENT_CONNECTION_MODAL_ANALYSIS_AT_A_STIFFNESS = (
    python_net_import(
        "SMT.MastaAPI.SystemModel.AnalysesAndResults.ModalAnalysesAtAStiffness",
        "AbstractShaftToMountableComponentConnectionModalAnalysisAtAStiffness",
    )
)

if TYPE_CHECKING:
    from typing import Any, Type, TypeVar

    from mastapy._private.system_model.analyses_and_results import _2941, _2943, _2945
    from mastapy._private.system_model.analyses_and_results.analysis_cases import (
        _7934,
        _7937,
    )
    from mastapy._private.system_model.analyses_and_results.modal_analyses_at_a_stiffness import (
        _5208,
        _5228,
        _5230,
        _5271,
        _5285,
    )
    from mastapy._private.system_model.connections_and_sockets import _2524

    Self = TypeVar(
        "Self",
        bound="AbstractShaftToMountableComponentConnectionModalAnalysisAtAStiffness",
    )
    CastSelf = TypeVar(
        "CastSelf",
        bound="AbstractShaftToMountableComponentConnectionModalAnalysisAtAStiffness._Cast_AbstractShaftToMountableComponentConnectionModalAnalysisAtAStiffness",
    )


__docformat__ = "restructuredtext en"
__all__ = ("AbstractShaftToMountableComponentConnectionModalAnalysisAtAStiffness",)


@extended_dataclass(frozen=True, slots=True, weakref_slot=True)
class _Cast_AbstractShaftToMountableComponentConnectionModalAnalysisAtAStiffness:
    """Special nested class for casting AbstractShaftToMountableComponentConnectionModalAnalysisAtAStiffness to subclasses."""

    __parent__: "AbstractShaftToMountableComponentConnectionModalAnalysisAtAStiffness"

    @property
    def connection_modal_analysis_at_a_stiffness(
        self: "CastSelf",
    ) -> "_5219.ConnectionModalAnalysisAtAStiffness":
        return self.__parent__._cast(_5219.ConnectionModalAnalysisAtAStiffness)

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
    def coaxial_connection_modal_analysis_at_a_stiffness(
        self: "CastSelf",
    ) -> "_5208.CoaxialConnectionModalAnalysisAtAStiffness":
        from mastapy._private.system_model.analyses_and_results.modal_analyses_at_a_stiffness import (
            _5208,
        )

        return self.__parent__._cast(_5208.CoaxialConnectionModalAnalysisAtAStiffness)

    @property
    def cycloidal_disc_central_bearing_connection_modal_analysis_at_a_stiffness(
        self: "CastSelf",
    ) -> "_5228.CycloidalDiscCentralBearingConnectionModalAnalysisAtAStiffness":
        from mastapy._private.system_model.analyses_and_results.modal_analyses_at_a_stiffness import (
            _5228,
        )

        return self.__parent__._cast(
            _5228.CycloidalDiscCentralBearingConnectionModalAnalysisAtAStiffness
        )

    @property
    def cycloidal_disc_planetary_bearing_connection_modal_analysis_at_a_stiffness(
        self: "CastSelf",
    ) -> "_5230.CycloidalDiscPlanetaryBearingConnectionModalAnalysisAtAStiffness":
        from mastapy._private.system_model.analyses_and_results.modal_analyses_at_a_stiffness import (
            _5230,
        )

        return self.__parent__._cast(
            _5230.CycloidalDiscPlanetaryBearingConnectionModalAnalysisAtAStiffness
        )

    @property
    def planetary_connection_modal_analysis_at_a_stiffness(
        self: "CastSelf",
    ) -> "_5271.PlanetaryConnectionModalAnalysisAtAStiffness":
        from mastapy._private.system_model.analyses_and_results.modal_analyses_at_a_stiffness import (
            _5271,
        )

        return self.__parent__._cast(_5271.PlanetaryConnectionModalAnalysisAtAStiffness)

    @property
    def shaft_to_mountable_component_connection_modal_analysis_at_a_stiffness(
        self: "CastSelf",
    ) -> "_5285.ShaftToMountableComponentConnectionModalAnalysisAtAStiffness":
        from mastapy._private.system_model.analyses_and_results.modal_analyses_at_a_stiffness import (
            _5285,
        )

        return self.__parent__._cast(
            _5285.ShaftToMountableComponentConnectionModalAnalysisAtAStiffness
        )

    @property
    def abstract_shaft_to_mountable_component_connection_modal_analysis_at_a_stiffness(
        self: "CastSelf",
    ) -> "AbstractShaftToMountableComponentConnectionModalAnalysisAtAStiffness":
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
class AbstractShaftToMountableComponentConnectionModalAnalysisAtAStiffness(
    _5219.ConnectionModalAnalysisAtAStiffness
):
    """AbstractShaftToMountableComponentConnectionModalAnalysisAtAStiffness

    This is a mastapy class.
    """

    TYPE: ClassVar["Type"] = (
        _ABSTRACT_SHAFT_TO_MOUNTABLE_COMPONENT_CONNECTION_MODAL_ANALYSIS_AT_A_STIFFNESS
    )

    wrapped: "Any"

    def __post_init__(self: "Self") -> None:
        """Override of the post initialisation magic method."""
        if not hasattr(self.wrapped, "reference_count"):
            self.wrapped.reference_count = 0

        self.wrapped.reference_count += 1

    @property
    @exception_bridge
    def connection_design(
        self: "Self",
    ) -> "_2524.AbstractShaftToMountableComponentConnection":
        """mastapy.system_model.connections_and_sockets.AbstractShaftToMountableComponentConnection

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "ConnectionDesign")

        if temp is None:
            return None

        type_ = temp.GetType()
        return constructor.new(type_.Namespace, type_.Name)(temp)

    @property
    def cast_to(
        self: "Self",
    ) -> "_Cast_AbstractShaftToMountableComponentConnectionModalAnalysisAtAStiffness":
        """Cast to another type.

        Returns:
            _Cast_AbstractShaftToMountableComponentConnectionModalAnalysisAtAStiffness
        """
        return (
            _Cast_AbstractShaftToMountableComponentConnectionModalAnalysisAtAStiffness(
                self
            )
        )
