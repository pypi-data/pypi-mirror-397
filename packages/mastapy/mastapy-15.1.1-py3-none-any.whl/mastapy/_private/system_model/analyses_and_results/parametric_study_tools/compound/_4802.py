"""CouplingHalfCompoundParametricStudyTool"""

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
    _4842,
)

_COUPLING_HALF_COMPOUND_PARAMETRIC_STUDY_TOOL = python_net_import(
    "SMT.MastaAPI.SystemModel.AnalysesAndResults.ParametricStudyTools.Compound",
    "CouplingHalfCompoundParametricStudyTool",
)

if TYPE_CHECKING:
    from typing import Any, List, Type, TypeVar

    from mastapy._private.system_model.analyses_and_results import _2943
    from mastapy._private.system_model.analyses_and_results.analysis_cases import (
        _7939,
        _7942,
    )
    from mastapy._private.system_model.analyses_and_results.parametric_study_tools import (
        _4651,
    )
    from mastapy._private.system_model.analyses_and_results.parametric_study_tools.compound import (
        _4786,
        _4788,
        _4791,
        _4805,
        _4844,
        _4847,
        _4853,
        _4857,
        _4869,
        _4879,
        _4880,
        _4881,
        _4884,
        _4885,
    )

    Self = TypeVar("Self", bound="CouplingHalfCompoundParametricStudyTool")
    CastSelf = TypeVar(
        "CastSelf",
        bound="CouplingHalfCompoundParametricStudyTool._Cast_CouplingHalfCompoundParametricStudyTool",
    )


__docformat__ = "restructuredtext en"
__all__ = ("CouplingHalfCompoundParametricStudyTool",)


@extended_dataclass(frozen=True, slots=True, weakref_slot=True)
class _Cast_CouplingHalfCompoundParametricStudyTool:
    """Special nested class for casting CouplingHalfCompoundParametricStudyTool to subclasses."""

    __parent__: "CouplingHalfCompoundParametricStudyTool"

    @property
    def mountable_component_compound_parametric_study_tool(
        self: "CastSelf",
    ) -> "_4842.MountableComponentCompoundParametricStudyTool":
        return self.__parent__._cast(
            _4842.MountableComponentCompoundParametricStudyTool
        )

    @property
    def component_compound_parametric_study_tool(
        self: "CastSelf",
    ) -> "_4788.ComponentCompoundParametricStudyTool":
        from mastapy._private.system_model.analyses_and_results.parametric_study_tools.compound import (
            _4788,
        )

        return self.__parent__._cast(_4788.ComponentCompoundParametricStudyTool)

    @property
    def part_compound_parametric_study_tool(
        self: "CastSelf",
    ) -> "_4844.PartCompoundParametricStudyTool":
        from mastapy._private.system_model.analyses_and_results.parametric_study_tools.compound import (
            _4844,
        )

        return self.__parent__._cast(_4844.PartCompoundParametricStudyTool)

    @property
    def part_compound_analysis(self: "CastSelf") -> "_7942.PartCompoundAnalysis":
        from mastapy._private.system_model.analyses_and_results.analysis_cases import (
            _7942,
        )

        return self.__parent__._cast(_7942.PartCompoundAnalysis)

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
    def clutch_half_compound_parametric_study_tool(
        self: "CastSelf",
    ) -> "_4786.ClutchHalfCompoundParametricStudyTool":
        from mastapy._private.system_model.analyses_and_results.parametric_study_tools.compound import (
            _4786,
        )

        return self.__parent__._cast(_4786.ClutchHalfCompoundParametricStudyTool)

    @property
    def concept_coupling_half_compound_parametric_study_tool(
        self: "CastSelf",
    ) -> "_4791.ConceptCouplingHalfCompoundParametricStudyTool":
        from mastapy._private.system_model.analyses_and_results.parametric_study_tools.compound import (
            _4791,
        )

        return self.__parent__._cast(
            _4791.ConceptCouplingHalfCompoundParametricStudyTool
        )

    @property
    def cvt_pulley_compound_parametric_study_tool(
        self: "CastSelf",
    ) -> "_4805.CVTPulleyCompoundParametricStudyTool":
        from mastapy._private.system_model.analyses_and_results.parametric_study_tools.compound import (
            _4805,
        )

        return self.__parent__._cast(_4805.CVTPulleyCompoundParametricStudyTool)

    @property
    def part_to_part_shear_coupling_half_compound_parametric_study_tool(
        self: "CastSelf",
    ) -> "_4847.PartToPartShearCouplingHalfCompoundParametricStudyTool":
        from mastapy._private.system_model.analyses_and_results.parametric_study_tools.compound import (
            _4847,
        )

        return self.__parent__._cast(
            _4847.PartToPartShearCouplingHalfCompoundParametricStudyTool
        )

    @property
    def pulley_compound_parametric_study_tool(
        self: "CastSelf",
    ) -> "_4853.PulleyCompoundParametricStudyTool":
        from mastapy._private.system_model.analyses_and_results.parametric_study_tools.compound import (
            _4853,
        )

        return self.__parent__._cast(_4853.PulleyCompoundParametricStudyTool)

    @property
    def rolling_ring_compound_parametric_study_tool(
        self: "CastSelf",
    ) -> "_4857.RollingRingCompoundParametricStudyTool":
        from mastapy._private.system_model.analyses_and_results.parametric_study_tools.compound import (
            _4857,
        )

        return self.__parent__._cast(_4857.RollingRingCompoundParametricStudyTool)

    @property
    def spring_damper_half_compound_parametric_study_tool(
        self: "CastSelf",
    ) -> "_4869.SpringDamperHalfCompoundParametricStudyTool":
        from mastapy._private.system_model.analyses_and_results.parametric_study_tools.compound import (
            _4869,
        )

        return self.__parent__._cast(_4869.SpringDamperHalfCompoundParametricStudyTool)

    @property
    def synchroniser_half_compound_parametric_study_tool(
        self: "CastSelf",
    ) -> "_4879.SynchroniserHalfCompoundParametricStudyTool":
        from mastapy._private.system_model.analyses_and_results.parametric_study_tools.compound import (
            _4879,
        )

        return self.__parent__._cast(_4879.SynchroniserHalfCompoundParametricStudyTool)

    @property
    def synchroniser_part_compound_parametric_study_tool(
        self: "CastSelf",
    ) -> "_4880.SynchroniserPartCompoundParametricStudyTool":
        from mastapy._private.system_model.analyses_and_results.parametric_study_tools.compound import (
            _4880,
        )

        return self.__parent__._cast(_4880.SynchroniserPartCompoundParametricStudyTool)

    @property
    def synchroniser_sleeve_compound_parametric_study_tool(
        self: "CastSelf",
    ) -> "_4881.SynchroniserSleeveCompoundParametricStudyTool":
        from mastapy._private.system_model.analyses_and_results.parametric_study_tools.compound import (
            _4881,
        )

        return self.__parent__._cast(
            _4881.SynchroniserSleeveCompoundParametricStudyTool
        )

    @property
    def torque_converter_pump_compound_parametric_study_tool(
        self: "CastSelf",
    ) -> "_4884.TorqueConverterPumpCompoundParametricStudyTool":
        from mastapy._private.system_model.analyses_and_results.parametric_study_tools.compound import (
            _4884,
        )

        return self.__parent__._cast(
            _4884.TorqueConverterPumpCompoundParametricStudyTool
        )

    @property
    def torque_converter_turbine_compound_parametric_study_tool(
        self: "CastSelf",
    ) -> "_4885.TorqueConverterTurbineCompoundParametricStudyTool":
        from mastapy._private.system_model.analyses_and_results.parametric_study_tools.compound import (
            _4885,
        )

        return self.__parent__._cast(
            _4885.TorqueConverterTurbineCompoundParametricStudyTool
        )

    @property
    def coupling_half_compound_parametric_study_tool(
        self: "CastSelf",
    ) -> "CouplingHalfCompoundParametricStudyTool":
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
class CouplingHalfCompoundParametricStudyTool(
    _4842.MountableComponentCompoundParametricStudyTool
):
    """CouplingHalfCompoundParametricStudyTool

    This is a mastapy class.
    """

    TYPE: ClassVar["Type"] = _COUPLING_HALF_COMPOUND_PARAMETRIC_STUDY_TOOL

    wrapped: "Any"

    def __post_init__(self: "Self") -> None:
        """Override of the post initialisation magic method."""
        if not hasattr(self.wrapped, "reference_count"):
            self.wrapped.reference_count = 0

        self.wrapped.reference_count += 1

    @property
    @exception_bridge
    def component_analysis_cases(
        self: "Self",
    ) -> "List[_4651.CouplingHalfParametricStudyTool]":
        """List[mastapy.system_model.analyses_and_results.parametric_study_tools.CouplingHalfParametricStudyTool]

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "ComponentAnalysisCases")

        if temp is None:
            return None

        value = conversion.pn_to_mp_objects_in_list(temp)

        if value is None:
            return None

        return value

    @property
    @exception_bridge
    def component_analysis_cases_ready(
        self: "Self",
    ) -> "List[_4651.CouplingHalfParametricStudyTool]":
        """List[mastapy.system_model.analyses_and_results.parametric_study_tools.CouplingHalfParametricStudyTool]

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "ComponentAnalysisCasesReady")

        if temp is None:
            return None

        value = conversion.pn_to_mp_objects_in_list(temp)

        if value is None:
            return None

        return value

    @property
    def cast_to(self: "Self") -> "_Cast_CouplingHalfCompoundParametricStudyTool":
        """Cast to another type.

        Returns:
            _Cast_CouplingHalfCompoundParametricStudyTool
        """
        return _Cast_CouplingHalfCompoundParametricStudyTool(self)
