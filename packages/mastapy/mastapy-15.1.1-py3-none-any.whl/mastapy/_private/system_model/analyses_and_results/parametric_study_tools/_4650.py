"""CouplingConnectionParametricStudyTool"""

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
from mastapy._private.system_model.analyses_and_results.parametric_study_tools import (
    _4685,
)

_COUPLING_CONNECTION_PARAMETRIC_STUDY_TOOL = python_net_import(
    "SMT.MastaAPI.SystemModel.AnalysesAndResults.ParametricStudyTools",
    "CouplingConnectionParametricStudyTool",
)

if TYPE_CHECKING:
    from typing import Any, Type, TypeVar

    from mastapy._private.system_model.analyses_and_results import _2941, _2943, _2945
    from mastapy._private.system_model.analyses_and_results.analysis_cases import _7934
    from mastapy._private.system_model.analyses_and_results.parametric_study_tools import (
        _4634,
        _4639,
        _4648,
        _4714,
        _4736,
        _4751,
    )
    from mastapy._private.system_model.connections_and_sockets.couplings import _2605

    Self = TypeVar("Self", bound="CouplingConnectionParametricStudyTool")
    CastSelf = TypeVar(
        "CastSelf",
        bound="CouplingConnectionParametricStudyTool._Cast_CouplingConnectionParametricStudyTool",
    )


__docformat__ = "restructuredtext en"
__all__ = ("CouplingConnectionParametricStudyTool",)


@extended_dataclass(frozen=True, slots=True, weakref_slot=True)
class _Cast_CouplingConnectionParametricStudyTool:
    """Special nested class for casting CouplingConnectionParametricStudyTool to subclasses."""

    __parent__: "CouplingConnectionParametricStudyTool"

    @property
    def inter_mountable_component_connection_parametric_study_tool(
        self: "CastSelf",
    ) -> "_4685.InterMountableComponentConnectionParametricStudyTool":
        return self.__parent__._cast(
            _4685.InterMountableComponentConnectionParametricStudyTool
        )

    @property
    def connection_parametric_study_tool(
        self: "CastSelf",
    ) -> "_4648.ConnectionParametricStudyTool":
        from mastapy._private.system_model.analyses_and_results.parametric_study_tools import (
            _4648,
        )

        return self.__parent__._cast(_4648.ConnectionParametricStudyTool)

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
    def clutch_connection_parametric_study_tool(
        self: "CastSelf",
    ) -> "_4634.ClutchConnectionParametricStudyTool":
        from mastapy._private.system_model.analyses_and_results.parametric_study_tools import (
            _4634,
        )

        return self.__parent__._cast(_4634.ClutchConnectionParametricStudyTool)

    @property
    def concept_coupling_connection_parametric_study_tool(
        self: "CastSelf",
    ) -> "_4639.ConceptCouplingConnectionParametricStudyTool":
        from mastapy._private.system_model.analyses_and_results.parametric_study_tools import (
            _4639,
        )

        return self.__parent__._cast(_4639.ConceptCouplingConnectionParametricStudyTool)

    @property
    def part_to_part_shear_coupling_connection_parametric_study_tool(
        self: "CastSelf",
    ) -> "_4714.PartToPartShearCouplingConnectionParametricStudyTool":
        from mastapy._private.system_model.analyses_and_results.parametric_study_tools import (
            _4714,
        )

        return self.__parent__._cast(
            _4714.PartToPartShearCouplingConnectionParametricStudyTool
        )

    @property
    def spring_damper_connection_parametric_study_tool(
        self: "CastSelf",
    ) -> "_4736.SpringDamperConnectionParametricStudyTool":
        from mastapy._private.system_model.analyses_and_results.parametric_study_tools import (
            _4736,
        )

        return self.__parent__._cast(_4736.SpringDamperConnectionParametricStudyTool)

    @property
    def torque_converter_connection_parametric_study_tool(
        self: "CastSelf",
    ) -> "_4751.TorqueConverterConnectionParametricStudyTool":
        from mastapy._private.system_model.analyses_and_results.parametric_study_tools import (
            _4751,
        )

        return self.__parent__._cast(_4751.TorqueConverterConnectionParametricStudyTool)

    @property
    def coupling_connection_parametric_study_tool(
        self: "CastSelf",
    ) -> "CouplingConnectionParametricStudyTool":
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
class CouplingConnectionParametricStudyTool(
    _4685.InterMountableComponentConnectionParametricStudyTool
):
    """CouplingConnectionParametricStudyTool

    This is a mastapy class.
    """

    TYPE: ClassVar["Type"] = _COUPLING_CONNECTION_PARAMETRIC_STUDY_TOOL

    wrapped: "Any"

    def __post_init__(self: "Self") -> None:
        """Override of the post initialisation magic method."""
        if not hasattr(self.wrapped, "reference_count"):
            self.wrapped.reference_count = 0

        self.wrapped.reference_count += 1

    @property
    @exception_bridge
    def connection_design(self: "Self") -> "_2605.CouplingConnection":
        """mastapy.system_model.connections_and_sockets.couplings.CouplingConnection

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "ConnectionDesign")

        if temp is None:
            return None

        type_ = temp.GetType()
        return constructor.new(type_.Namespace, type_.Name)(temp)

    @property
    def cast_to(self: "Self") -> "_Cast_CouplingConnectionParametricStudyTool":
        """Cast to another type.

        Returns:
            _Cast_CouplingConnectionParametricStudyTool
        """
        return _Cast_CouplingConnectionParametricStudyTool(self)
