"""ShaftToMountableComponentConnectionCompoundParametricStudyTool"""

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
from mastapy._private.system_model.analyses_and_results.parametric_study_tools.compound import (
    _4766,
)

_SHAFT_TO_MOUNTABLE_COMPONENT_CONNECTION_COMPOUND_PARAMETRIC_STUDY_TOOL = (
    python_net_import(
        "SMT.MastaAPI.SystemModel.AnalysesAndResults.ParametricStudyTools.Compound",
        "ShaftToMountableComponentConnectionCompoundParametricStudyTool",
    )
)

if TYPE_CHECKING:
    from typing import Any, List, Type, TypeVar

    from mastapy._private.system_model.analyses_and_results import _2943
    from mastapy._private.system_model.analyses_and_results.analysis_cases import (
        _7935,
        _7939,
    )
    from mastapy._private.system_model.analyses_and_results.parametric_study_tools import (
        _4731,
    )
    from mastapy._private.system_model.analyses_and_results.parametric_study_tools.compound import (
        _4787,
        _4798,
        _4807,
        _4848,
    )

    Self = TypeVar(
        "Self", bound="ShaftToMountableComponentConnectionCompoundParametricStudyTool"
    )
    CastSelf = TypeVar(
        "CastSelf",
        bound="ShaftToMountableComponentConnectionCompoundParametricStudyTool._Cast_ShaftToMountableComponentConnectionCompoundParametricStudyTool",
    )


__docformat__ = "restructuredtext en"
__all__ = ("ShaftToMountableComponentConnectionCompoundParametricStudyTool",)


@extended_dataclass(frozen=True, slots=True, weakref_slot=True)
class _Cast_ShaftToMountableComponentConnectionCompoundParametricStudyTool:
    """Special nested class for casting ShaftToMountableComponentConnectionCompoundParametricStudyTool to subclasses."""

    __parent__: "ShaftToMountableComponentConnectionCompoundParametricStudyTool"

    @property
    def abstract_shaft_to_mountable_component_connection_compound_parametric_study_tool(
        self: "CastSelf",
    ) -> "_4766.AbstractShaftToMountableComponentConnectionCompoundParametricStudyTool":
        return self.__parent__._cast(
            _4766.AbstractShaftToMountableComponentConnectionCompoundParametricStudyTool
        )

    @property
    def connection_compound_parametric_study_tool(
        self: "CastSelf",
    ) -> "_4798.ConnectionCompoundParametricStudyTool":
        from mastapy._private.system_model.analyses_and_results.parametric_study_tools.compound import (
            _4798,
        )

        return self.__parent__._cast(_4798.ConnectionCompoundParametricStudyTool)

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
    def coaxial_connection_compound_parametric_study_tool(
        self: "CastSelf",
    ) -> "_4787.CoaxialConnectionCompoundParametricStudyTool":
        from mastapy._private.system_model.analyses_and_results.parametric_study_tools.compound import (
            _4787,
        )

        return self.__parent__._cast(_4787.CoaxialConnectionCompoundParametricStudyTool)

    @property
    def cycloidal_disc_central_bearing_connection_compound_parametric_study_tool(
        self: "CastSelf",
    ) -> "_4807.CycloidalDiscCentralBearingConnectionCompoundParametricStudyTool":
        from mastapy._private.system_model.analyses_and_results.parametric_study_tools.compound import (
            _4807,
        )

        return self.__parent__._cast(
            _4807.CycloidalDiscCentralBearingConnectionCompoundParametricStudyTool
        )

    @property
    def planetary_connection_compound_parametric_study_tool(
        self: "CastSelf",
    ) -> "_4848.PlanetaryConnectionCompoundParametricStudyTool":
        from mastapy._private.system_model.analyses_and_results.parametric_study_tools.compound import (
            _4848,
        )

        return self.__parent__._cast(
            _4848.PlanetaryConnectionCompoundParametricStudyTool
        )

    @property
    def shaft_to_mountable_component_connection_compound_parametric_study_tool(
        self: "CastSelf",
    ) -> "ShaftToMountableComponentConnectionCompoundParametricStudyTool":
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
class ShaftToMountableComponentConnectionCompoundParametricStudyTool(
    _4766.AbstractShaftToMountableComponentConnectionCompoundParametricStudyTool
):
    """ShaftToMountableComponentConnectionCompoundParametricStudyTool

    This is a mastapy class.
    """

    TYPE: ClassVar["Type"] = (
        _SHAFT_TO_MOUNTABLE_COMPONENT_CONNECTION_COMPOUND_PARAMETRIC_STUDY_TOOL
    )

    wrapped: "Any"

    def __post_init__(self: "Self") -> None:
        """Override of the post initialisation magic method."""
        if not hasattr(self.wrapped, "reference_count"):
            self.wrapped.reference_count = 0

        self.wrapped.reference_count += 1

    @property
    @exception_bridge
    def connection_analysis_cases(
        self: "Self",
    ) -> "List[_4731.ShaftToMountableComponentConnectionParametricStudyTool]":
        """List[mastapy.system_model.analyses_and_results.parametric_study_tools.ShaftToMountableComponentConnectionParametricStudyTool]

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
    @exception_bridge
    def connection_analysis_cases_ready(
        self: "Self",
    ) -> "List[_4731.ShaftToMountableComponentConnectionParametricStudyTool]":
        """List[mastapy.system_model.analyses_and_results.parametric_study_tools.ShaftToMountableComponentConnectionParametricStudyTool]

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
    def cast_to(
        self: "Self",
    ) -> "_Cast_ShaftToMountableComponentConnectionCompoundParametricStudyTool":
        """Cast to another type.

        Returns:
            _Cast_ShaftToMountableComponentConnectionCompoundParametricStudyTool
        """
        return _Cast_ShaftToMountableComponentConnectionCompoundParametricStudyTool(
            self
        )
