"""VirtualComponentParametricStudyTool"""

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
    _4700,
)

_VIRTUAL_COMPONENT_PARAMETRIC_STUDY_TOOL = python_net_import(
    "SMT.MastaAPI.SystemModel.AnalysesAndResults.ParametricStudyTools",
    "VirtualComponentParametricStudyTool",
)

if TYPE_CHECKING:
    from typing import Any, Type, TypeVar

    from mastapy._private.system_model.analyses_and_results import _2943, _2945, _2949
    from mastapy._private.system_model.analyses_and_results.analysis_cases import _7941
    from mastapy._private.system_model.analyses_and_results.parametric_study_tools import (
        _4638,
        _4695,
        _4696,
        _4713,
        _4720,
        _4721,
        _4755,
    )
    from mastapy._private.system_model.part_model import _2755

    Self = TypeVar("Self", bound="VirtualComponentParametricStudyTool")
    CastSelf = TypeVar(
        "CastSelf",
        bound="VirtualComponentParametricStudyTool._Cast_VirtualComponentParametricStudyTool",
    )


__docformat__ = "restructuredtext en"
__all__ = ("VirtualComponentParametricStudyTool",)


@extended_dataclass(frozen=True, slots=True, weakref_slot=True)
class _Cast_VirtualComponentParametricStudyTool:
    """Special nested class for casting VirtualComponentParametricStudyTool to subclasses."""

    __parent__: "VirtualComponentParametricStudyTool"

    @property
    def mountable_component_parametric_study_tool(
        self: "CastSelf",
    ) -> "_4700.MountableComponentParametricStudyTool":
        return self.__parent__._cast(_4700.MountableComponentParametricStudyTool)

    @property
    def component_parametric_study_tool(
        self: "CastSelf",
    ) -> "_4638.ComponentParametricStudyTool":
        from mastapy._private.system_model.analyses_and_results.parametric_study_tools import (
            _4638,
        )

        return self.__parent__._cast(_4638.ComponentParametricStudyTool)

    @property
    def part_parametric_study_tool(self: "CastSelf") -> "_4713.PartParametricStudyTool":
        from mastapy._private.system_model.analyses_and_results.parametric_study_tools import (
            _4713,
        )

        return self.__parent__._cast(_4713.PartParametricStudyTool)

    @property
    def part_analysis_case(self: "CastSelf") -> "_7941.PartAnalysisCase":
        from mastapy._private.system_model.analyses_and_results.analysis_cases import (
            _7941,
        )

        return self.__parent__._cast(_7941.PartAnalysisCase)

    @property
    def part_analysis(self: "CastSelf") -> "_2949.PartAnalysis":
        from mastapy._private.system_model.analyses_and_results import _2949

        return self.__parent__._cast(_2949.PartAnalysis)

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
    def mass_disc_parametric_study_tool(
        self: "CastSelf",
    ) -> "_4695.MassDiscParametricStudyTool":
        from mastapy._private.system_model.analyses_and_results.parametric_study_tools import (
            _4695,
        )

        return self.__parent__._cast(_4695.MassDiscParametricStudyTool)

    @property
    def measurement_component_parametric_study_tool(
        self: "CastSelf",
    ) -> "_4696.MeasurementComponentParametricStudyTool":
        from mastapy._private.system_model.analyses_and_results.parametric_study_tools import (
            _4696,
        )

        return self.__parent__._cast(_4696.MeasurementComponentParametricStudyTool)

    @property
    def point_load_parametric_study_tool(
        self: "CastSelf",
    ) -> "_4720.PointLoadParametricStudyTool":
        from mastapy._private.system_model.analyses_and_results.parametric_study_tools import (
            _4720,
        )

        return self.__parent__._cast(_4720.PointLoadParametricStudyTool)

    @property
    def power_load_parametric_study_tool(
        self: "CastSelf",
    ) -> "_4721.PowerLoadParametricStudyTool":
        from mastapy._private.system_model.analyses_and_results.parametric_study_tools import (
            _4721,
        )

        return self.__parent__._cast(_4721.PowerLoadParametricStudyTool)

    @property
    def unbalanced_mass_parametric_study_tool(
        self: "CastSelf",
    ) -> "_4755.UnbalancedMassParametricStudyTool":
        from mastapy._private.system_model.analyses_and_results.parametric_study_tools import (
            _4755,
        )

        return self.__parent__._cast(_4755.UnbalancedMassParametricStudyTool)

    @property
    def virtual_component_parametric_study_tool(
        self: "CastSelf",
    ) -> "VirtualComponentParametricStudyTool":
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
class VirtualComponentParametricStudyTool(_4700.MountableComponentParametricStudyTool):
    """VirtualComponentParametricStudyTool

    This is a mastapy class.
    """

    TYPE: ClassVar["Type"] = _VIRTUAL_COMPONENT_PARAMETRIC_STUDY_TOOL

    wrapped: "Any"

    def __post_init__(self: "Self") -> None:
        """Override of the post initialisation magic method."""
        if not hasattr(self.wrapped, "reference_count"):
            self.wrapped.reference_count = 0

        self.wrapped.reference_count += 1

    @property
    @exception_bridge
    def component_design(self: "Self") -> "_2755.VirtualComponent":
        """mastapy.system_model.part_model.VirtualComponent

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "ComponentDesign")

        if temp is None:
            return None

        type_ = temp.GetType()
        return constructor.new(type_.Namespace, type_.Name)(temp)

    @property
    def cast_to(self: "Self") -> "_Cast_VirtualComponentParametricStudyTool":
        """Cast to another type.

        Returns:
            _Cast_VirtualComponentParametricStudyTool
        """
        return _Cast_VirtualComponentParametricStudyTool(self)
