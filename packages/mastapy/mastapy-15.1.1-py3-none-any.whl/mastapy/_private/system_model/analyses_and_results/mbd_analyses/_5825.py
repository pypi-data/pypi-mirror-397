"""ShaftToMountableComponentConnectionMultibodyDynamicsAnalysis"""

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
from mastapy._private.system_model.analyses_and_results.mbd_analyses import _5714

_SHAFT_TO_MOUNTABLE_COMPONENT_CONNECTION_MULTIBODY_DYNAMICS_ANALYSIS = (
    python_net_import(
        "SMT.MastaAPI.SystemModel.AnalysesAndResults.MBDAnalyses",
        "ShaftToMountableComponentConnectionMultibodyDynamicsAnalysis",
    )
)

if TYPE_CHECKING:
    from typing import Any, Type, TypeVar

    from mastapy._private.system_model.analyses_and_results import _2941, _2943, _2945
    from mastapy._private.system_model.analyses_and_results.analysis_cases import (
        _7934,
        _7938,
    )
    from mastapy._private.system_model.analyses_and_results.mbd_analyses import (
        _5739,
        _5750,
        _5759,
        _5809,
    )
    from mastapy._private.system_model.connections_and_sockets import _2554

    Self = TypeVar(
        "Self", bound="ShaftToMountableComponentConnectionMultibodyDynamicsAnalysis"
    )
    CastSelf = TypeVar(
        "CastSelf",
        bound="ShaftToMountableComponentConnectionMultibodyDynamicsAnalysis._Cast_ShaftToMountableComponentConnectionMultibodyDynamicsAnalysis",
    )


__docformat__ = "restructuredtext en"
__all__ = ("ShaftToMountableComponentConnectionMultibodyDynamicsAnalysis",)


@extended_dataclass(frozen=True, slots=True, weakref_slot=True)
class _Cast_ShaftToMountableComponentConnectionMultibodyDynamicsAnalysis:
    """Special nested class for casting ShaftToMountableComponentConnectionMultibodyDynamicsAnalysis to subclasses."""

    __parent__: "ShaftToMountableComponentConnectionMultibodyDynamicsAnalysis"

    @property
    def abstract_shaft_to_mountable_component_connection_multibody_dynamics_analysis(
        self: "CastSelf",
    ) -> "_5714.AbstractShaftToMountableComponentConnectionMultibodyDynamicsAnalysis":
        return self.__parent__._cast(
            _5714.AbstractShaftToMountableComponentConnectionMultibodyDynamicsAnalysis
        )

    @property
    def connection_multibody_dynamics_analysis(
        self: "CastSelf",
    ) -> "_5750.ConnectionMultibodyDynamicsAnalysis":
        from mastapy._private.system_model.analyses_and_results.mbd_analyses import (
            _5750,
        )

        return self.__parent__._cast(_5750.ConnectionMultibodyDynamicsAnalysis)

    @property
    def connection_time_series_load_analysis_case(
        self: "CastSelf",
    ) -> "_7938.ConnectionTimeSeriesLoadAnalysisCase":
        from mastapy._private.system_model.analyses_and_results.analysis_cases import (
            _7938,
        )

        return self.__parent__._cast(_7938.ConnectionTimeSeriesLoadAnalysisCase)

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
    def coaxial_connection_multibody_dynamics_analysis(
        self: "CastSelf",
    ) -> "_5739.CoaxialConnectionMultibodyDynamicsAnalysis":
        from mastapy._private.system_model.analyses_and_results.mbd_analyses import (
            _5739,
        )

        return self.__parent__._cast(_5739.CoaxialConnectionMultibodyDynamicsAnalysis)

    @property
    def cycloidal_disc_central_bearing_connection_multibody_dynamics_analysis(
        self: "CastSelf",
    ) -> "_5759.CycloidalDiscCentralBearingConnectionMultibodyDynamicsAnalysis":
        from mastapy._private.system_model.analyses_and_results.mbd_analyses import (
            _5759,
        )

        return self.__parent__._cast(
            _5759.CycloidalDiscCentralBearingConnectionMultibodyDynamicsAnalysis
        )

    @property
    def planetary_connection_multibody_dynamics_analysis(
        self: "CastSelf",
    ) -> "_5809.PlanetaryConnectionMultibodyDynamicsAnalysis":
        from mastapy._private.system_model.analyses_and_results.mbd_analyses import (
            _5809,
        )

        return self.__parent__._cast(_5809.PlanetaryConnectionMultibodyDynamicsAnalysis)

    @property
    def shaft_to_mountable_component_connection_multibody_dynamics_analysis(
        self: "CastSelf",
    ) -> "ShaftToMountableComponentConnectionMultibodyDynamicsAnalysis":
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
class ShaftToMountableComponentConnectionMultibodyDynamicsAnalysis(
    _5714.AbstractShaftToMountableComponentConnectionMultibodyDynamicsAnalysis
):
    """ShaftToMountableComponentConnectionMultibodyDynamicsAnalysis

    This is a mastapy class.
    """

    TYPE: ClassVar["Type"] = (
        _SHAFT_TO_MOUNTABLE_COMPONENT_CONNECTION_MULTIBODY_DYNAMICS_ANALYSIS
    )

    wrapped: "Any"

    def __post_init__(self: "Self") -> None:
        """Override of the post initialisation magic method."""
        if not hasattr(self.wrapped, "reference_count"):
            self.wrapped.reference_count = 0

        self.wrapped.reference_count += 1

    @property
    @exception_bridge
    def connection_design(self: "Self") -> "_2554.ShaftToMountableComponentConnection":
        """mastapy.system_model.connections_and_sockets.ShaftToMountableComponentConnection

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
    ) -> "_Cast_ShaftToMountableComponentConnectionMultibodyDynamicsAnalysis":
        """Cast to another type.

        Returns:
            _Cast_ShaftToMountableComponentConnectionMultibodyDynamicsAnalysis
        """
        return _Cast_ShaftToMountableComponentConnectionMultibodyDynamicsAnalysis(self)
