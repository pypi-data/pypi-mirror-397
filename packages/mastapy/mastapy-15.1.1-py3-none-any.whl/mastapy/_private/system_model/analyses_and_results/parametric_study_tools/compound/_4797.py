"""ConicalGearSetCompoundParametricStudyTool"""

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
    _4823,
)

_CONICAL_GEAR_SET_COMPOUND_PARAMETRIC_STUDY_TOOL = python_net_import(
    "SMT.MastaAPI.SystemModel.AnalysesAndResults.ParametricStudyTools.Compound",
    "ConicalGearSetCompoundParametricStudyTool",
)

if TYPE_CHECKING:
    from typing import Any, List, Type, TypeVar

    from mastapy._private.system_model.analyses_and_results import _2943
    from mastapy._private.system_model.analyses_and_results.analysis_cases import (
        _7939,
        _7942,
    )
    from mastapy._private.system_model.analyses_and_results.parametric_study_tools import (
        _4647,
    )
    from mastapy._private.system_model.analyses_and_results.parametric_study_tools.compound import (
        _4763,
        _4769,
        _4776,
        _4781,
        _4827,
        _4831,
        _4834,
        _4837,
        _4844,
        _4863,
        _4866,
        _4872,
        _4875,
        _4893,
    )

    Self = TypeVar("Self", bound="ConicalGearSetCompoundParametricStudyTool")
    CastSelf = TypeVar(
        "CastSelf",
        bound="ConicalGearSetCompoundParametricStudyTool._Cast_ConicalGearSetCompoundParametricStudyTool",
    )


__docformat__ = "restructuredtext en"
__all__ = ("ConicalGearSetCompoundParametricStudyTool",)


@extended_dataclass(frozen=True, slots=True, weakref_slot=True)
class _Cast_ConicalGearSetCompoundParametricStudyTool:
    """Special nested class for casting ConicalGearSetCompoundParametricStudyTool to subclasses."""

    __parent__: "ConicalGearSetCompoundParametricStudyTool"

    @property
    def gear_set_compound_parametric_study_tool(
        self: "CastSelf",
    ) -> "_4823.GearSetCompoundParametricStudyTool":
        return self.__parent__._cast(_4823.GearSetCompoundParametricStudyTool)

    @property
    def specialised_assembly_compound_parametric_study_tool(
        self: "CastSelf",
    ) -> "_4863.SpecialisedAssemblyCompoundParametricStudyTool":
        from mastapy._private.system_model.analyses_and_results.parametric_study_tools.compound import (
            _4863,
        )

        return self.__parent__._cast(
            _4863.SpecialisedAssemblyCompoundParametricStudyTool
        )

    @property
    def abstract_assembly_compound_parametric_study_tool(
        self: "CastSelf",
    ) -> "_4763.AbstractAssemblyCompoundParametricStudyTool":
        from mastapy._private.system_model.analyses_and_results.parametric_study_tools.compound import (
            _4763,
        )

        return self.__parent__._cast(_4763.AbstractAssemblyCompoundParametricStudyTool)

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
    def agma_gleason_conical_gear_set_compound_parametric_study_tool(
        self: "CastSelf",
    ) -> "_4769.AGMAGleasonConicalGearSetCompoundParametricStudyTool":
        from mastapy._private.system_model.analyses_and_results.parametric_study_tools.compound import (
            _4769,
        )

        return self.__parent__._cast(
            _4769.AGMAGleasonConicalGearSetCompoundParametricStudyTool
        )

    @property
    def bevel_differential_gear_set_compound_parametric_study_tool(
        self: "CastSelf",
    ) -> "_4776.BevelDifferentialGearSetCompoundParametricStudyTool":
        from mastapy._private.system_model.analyses_and_results.parametric_study_tools.compound import (
            _4776,
        )

        return self.__parent__._cast(
            _4776.BevelDifferentialGearSetCompoundParametricStudyTool
        )

    @property
    def bevel_gear_set_compound_parametric_study_tool(
        self: "CastSelf",
    ) -> "_4781.BevelGearSetCompoundParametricStudyTool":
        from mastapy._private.system_model.analyses_and_results.parametric_study_tools.compound import (
            _4781,
        )

        return self.__parent__._cast(_4781.BevelGearSetCompoundParametricStudyTool)

    @property
    def hypoid_gear_set_compound_parametric_study_tool(
        self: "CastSelf",
    ) -> "_4827.HypoidGearSetCompoundParametricStudyTool":
        from mastapy._private.system_model.analyses_and_results.parametric_study_tools.compound import (
            _4827,
        )

        return self.__parent__._cast(_4827.HypoidGearSetCompoundParametricStudyTool)

    @property
    def klingelnberg_cyclo_palloid_conical_gear_set_compound_parametric_study_tool(
        self: "CastSelf",
    ) -> "_4831.KlingelnbergCycloPalloidConicalGearSetCompoundParametricStudyTool":
        from mastapy._private.system_model.analyses_and_results.parametric_study_tools.compound import (
            _4831,
        )

        return self.__parent__._cast(
            _4831.KlingelnbergCycloPalloidConicalGearSetCompoundParametricStudyTool
        )

    @property
    def klingelnberg_cyclo_palloid_hypoid_gear_set_compound_parametric_study_tool(
        self: "CastSelf",
    ) -> "_4834.KlingelnbergCycloPalloidHypoidGearSetCompoundParametricStudyTool":
        from mastapy._private.system_model.analyses_and_results.parametric_study_tools.compound import (
            _4834,
        )

        return self.__parent__._cast(
            _4834.KlingelnbergCycloPalloidHypoidGearSetCompoundParametricStudyTool
        )

    @property
    def klingelnberg_cyclo_palloid_spiral_bevel_gear_set_compound_parametric_study_tool(
        self: "CastSelf",
    ) -> "_4837.KlingelnbergCycloPalloidSpiralBevelGearSetCompoundParametricStudyTool":
        from mastapy._private.system_model.analyses_and_results.parametric_study_tools.compound import (
            _4837,
        )

        return self.__parent__._cast(
            _4837.KlingelnbergCycloPalloidSpiralBevelGearSetCompoundParametricStudyTool
        )

    @property
    def spiral_bevel_gear_set_compound_parametric_study_tool(
        self: "CastSelf",
    ) -> "_4866.SpiralBevelGearSetCompoundParametricStudyTool":
        from mastapy._private.system_model.analyses_and_results.parametric_study_tools.compound import (
            _4866,
        )

        return self.__parent__._cast(
            _4866.SpiralBevelGearSetCompoundParametricStudyTool
        )

    @property
    def straight_bevel_diff_gear_set_compound_parametric_study_tool(
        self: "CastSelf",
    ) -> "_4872.StraightBevelDiffGearSetCompoundParametricStudyTool":
        from mastapy._private.system_model.analyses_and_results.parametric_study_tools.compound import (
            _4872,
        )

        return self.__parent__._cast(
            _4872.StraightBevelDiffGearSetCompoundParametricStudyTool
        )

    @property
    def straight_bevel_gear_set_compound_parametric_study_tool(
        self: "CastSelf",
    ) -> "_4875.StraightBevelGearSetCompoundParametricStudyTool":
        from mastapy._private.system_model.analyses_and_results.parametric_study_tools.compound import (
            _4875,
        )

        return self.__parent__._cast(
            _4875.StraightBevelGearSetCompoundParametricStudyTool
        )

    @property
    def zerol_bevel_gear_set_compound_parametric_study_tool(
        self: "CastSelf",
    ) -> "_4893.ZerolBevelGearSetCompoundParametricStudyTool":
        from mastapy._private.system_model.analyses_and_results.parametric_study_tools.compound import (
            _4893,
        )

        return self.__parent__._cast(_4893.ZerolBevelGearSetCompoundParametricStudyTool)

    @property
    def conical_gear_set_compound_parametric_study_tool(
        self: "CastSelf",
    ) -> "ConicalGearSetCompoundParametricStudyTool":
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
class ConicalGearSetCompoundParametricStudyTool(
    _4823.GearSetCompoundParametricStudyTool
):
    """ConicalGearSetCompoundParametricStudyTool

    This is a mastapy class.
    """

    TYPE: ClassVar["Type"] = _CONICAL_GEAR_SET_COMPOUND_PARAMETRIC_STUDY_TOOL

    wrapped: "Any"

    def __post_init__(self: "Self") -> None:
        """Override of the post initialisation magic method."""
        if not hasattr(self.wrapped, "reference_count"):
            self.wrapped.reference_count = 0

        self.wrapped.reference_count += 1

    @property
    @exception_bridge
    def assembly_analysis_cases(
        self: "Self",
    ) -> "List[_4647.ConicalGearSetParametricStudyTool]":
        """List[mastapy.system_model.analyses_and_results.parametric_study_tools.ConicalGearSetParametricStudyTool]

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "AssemblyAnalysisCases")

        if temp is None:
            return None

        value = conversion.pn_to_mp_objects_in_list(temp)

        if value is None:
            return None

        return value

    @property
    @exception_bridge
    def assembly_analysis_cases_ready(
        self: "Self",
    ) -> "List[_4647.ConicalGearSetParametricStudyTool]":
        """List[mastapy.system_model.analyses_and_results.parametric_study_tools.ConicalGearSetParametricStudyTool]

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "AssemblyAnalysisCasesReady")

        if temp is None:
            return None

        value = conversion.pn_to_mp_objects_in_list(temp)

        if value is None:
            return None

        return value

    @property
    def cast_to(self: "Self") -> "_Cast_ConicalGearSetCompoundParametricStudyTool":
        """Cast to another type.

        Returns:
            _Cast_ConicalGearSetCompoundParametricStudyTool
        """
        return _Cast_ConicalGearSetCompoundParametricStudyTool(self)
