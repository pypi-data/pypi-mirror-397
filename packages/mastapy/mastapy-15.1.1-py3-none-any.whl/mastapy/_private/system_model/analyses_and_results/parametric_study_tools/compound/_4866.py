"""SpiralBevelGearSetCompoundParametricStudyTool"""

from __future__ import annotations

from typing import TYPE_CHECKING, ClassVar

from mastapy._private._internal.dataclasses import extended_dataclass
from mastapy._private._internal.exception_bridge import exception_bridge
from mastapy._private._internal.exceptions import CastException
from mastapy._private._internal.python_net import (
    python_net_import,
    pythonnet_property_get,
)

from mastapy._private._internal import constructor, conversion, utility
from mastapy._private.system_model.analyses_and_results.parametric_study_tools.compound import (
    _4781,
)

_SPIRAL_BEVEL_GEAR_SET_COMPOUND_PARAMETRIC_STUDY_TOOL = python_net_import(
    "SMT.MastaAPI.SystemModel.AnalysesAndResults.ParametricStudyTools.Compound",
    "SpiralBevelGearSetCompoundParametricStudyTool",
)

if TYPE_CHECKING:
    from typing import Any, List, Type, TypeVar

    from mastapy._private.system_model.analyses_and_results import _2943
    from mastapy._private.system_model.analyses_and_results.analysis_cases import (
        _7939,
        _7942,
    )
    from mastapy._private.system_model.analyses_and_results.parametric_study_tools import (
        _4735,
    )
    from mastapy._private.system_model.analyses_and_results.parametric_study_tools.compound import (
        _4763,
        _4769,
        _4797,
        _4823,
        _4844,
        _4863,
        _4864,
        _4865,
    )
    from mastapy._private.system_model.analyses_and_results.static_loads import _7880
    from mastapy._private.system_model.part_model.gears import _2826

    Self = TypeVar("Self", bound="SpiralBevelGearSetCompoundParametricStudyTool")
    CastSelf = TypeVar(
        "CastSelf",
        bound="SpiralBevelGearSetCompoundParametricStudyTool._Cast_SpiralBevelGearSetCompoundParametricStudyTool",
    )


__docformat__ = "restructuredtext en"
__all__ = ("SpiralBevelGearSetCompoundParametricStudyTool",)


@extended_dataclass(frozen=True, slots=True, weakref_slot=True)
class _Cast_SpiralBevelGearSetCompoundParametricStudyTool:
    """Special nested class for casting SpiralBevelGearSetCompoundParametricStudyTool to subclasses."""

    __parent__: "SpiralBevelGearSetCompoundParametricStudyTool"

    @property
    def bevel_gear_set_compound_parametric_study_tool(
        self: "CastSelf",
    ) -> "_4781.BevelGearSetCompoundParametricStudyTool":
        return self.__parent__._cast(_4781.BevelGearSetCompoundParametricStudyTool)

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
    def conical_gear_set_compound_parametric_study_tool(
        self: "CastSelf",
    ) -> "_4797.ConicalGearSetCompoundParametricStudyTool":
        from mastapy._private.system_model.analyses_and_results.parametric_study_tools.compound import (
            _4797,
        )

        return self.__parent__._cast(_4797.ConicalGearSetCompoundParametricStudyTool)

    @property
    def gear_set_compound_parametric_study_tool(
        self: "CastSelf",
    ) -> "_4823.GearSetCompoundParametricStudyTool":
        from mastapy._private.system_model.analyses_and_results.parametric_study_tools.compound import (
            _4823,
        )

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
    def spiral_bevel_gear_set_compound_parametric_study_tool(
        self: "CastSelf",
    ) -> "SpiralBevelGearSetCompoundParametricStudyTool":
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
class SpiralBevelGearSetCompoundParametricStudyTool(
    _4781.BevelGearSetCompoundParametricStudyTool
):
    """SpiralBevelGearSetCompoundParametricStudyTool

    This is a mastapy class.
    """

    TYPE: ClassVar["Type"] = _SPIRAL_BEVEL_GEAR_SET_COMPOUND_PARAMETRIC_STUDY_TOOL

    wrapped: "Any"

    def __post_init__(self: "Self") -> None:
        """Override of the post initialisation magic method."""
        if not hasattr(self.wrapped, "reference_count"):
            self.wrapped.reference_count = 0

        self.wrapped.reference_count += 1

    @property
    @exception_bridge
    def component_design(self: "Self") -> "_2826.SpiralBevelGearSet":
        """mastapy.system_model.part_model.gears.SpiralBevelGearSet

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "ComponentDesign")

        if temp is None:
            return None

        type_ = temp.GetType()
        return constructor.new(type_.Namespace, type_.Name)(temp)

    @property
    @exception_bridge
    def assembly_design(self: "Self") -> "_2826.SpiralBevelGearSet":
        """mastapy.system_model.part_model.gears.SpiralBevelGearSet

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "AssemblyDesign")

        if temp is None:
            return None

        type_ = temp.GetType()
        return constructor.new(type_.Namespace, type_.Name)(temp)

    @property
    @exception_bridge
    def properties_changing_all_load_cases(
        self: "Self",
    ) -> "_7880.SpiralBevelGearSetLoadCase":
        """mastapy.system_model.analyses_and_results.static_loads.SpiralBevelGearSetLoadCase

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "PropertiesChangingAllLoadCases")

        if temp is None:
            return None

        type_ = temp.GetType()
        return constructor.new(type_.Namespace, type_.Name)(temp)

    @property
    @exception_bridge
    def assembly_analysis_cases_ready(
        self: "Self",
    ) -> "List[_4735.SpiralBevelGearSetParametricStudyTool]":
        """List[mastapy.system_model.analyses_and_results.parametric_study_tools.SpiralBevelGearSetParametricStudyTool]

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
    @exception_bridge
    def spiral_bevel_gears_compound_parametric_study_tool(
        self: "Self",
    ) -> "List[_4864.SpiralBevelGearCompoundParametricStudyTool]":
        """List[mastapy.system_model.analyses_and_results.parametric_study_tools.compound.SpiralBevelGearCompoundParametricStudyTool]

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(
            self.wrapped, "SpiralBevelGearsCompoundParametricStudyTool"
        )

        if temp is None:
            return None

        value = conversion.pn_to_mp_objects_in_list(temp)

        if value is None:
            return None

        return value

    @property
    @exception_bridge
    def spiral_bevel_meshes_compound_parametric_study_tool(
        self: "Self",
    ) -> "List[_4865.SpiralBevelGearMeshCompoundParametricStudyTool]":
        """List[mastapy.system_model.analyses_and_results.parametric_study_tools.compound.SpiralBevelGearMeshCompoundParametricStudyTool]

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(
            self.wrapped, "SpiralBevelMeshesCompoundParametricStudyTool"
        )

        if temp is None:
            return None

        value = conversion.pn_to_mp_objects_in_list(temp)

        if value is None:
            return None

        return value

    @property
    @exception_bridge
    def assembly_analysis_cases(
        self: "Self",
    ) -> "List[_4735.SpiralBevelGearSetParametricStudyTool]":
        """List[mastapy.system_model.analyses_and_results.parametric_study_tools.SpiralBevelGearSetParametricStudyTool]

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
    def cast_to(self: "Self") -> "_Cast_SpiralBevelGearSetCompoundParametricStudyTool":
        """Cast to another type.

        Returns:
            _Cast_SpiralBevelGearSetCompoundParametricStudyTool
        """
        return _Cast_SpiralBevelGearSetCompoundParametricStudyTool(self)
