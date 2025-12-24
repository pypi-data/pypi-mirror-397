"""StraightBevelDiffGearSetCompoundDynamicAnalysis"""

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
from mastapy._private.system_model.analyses_and_results.dynamic_analyses.compound import (
    _6792,
)

_STRAIGHT_BEVEL_DIFF_GEAR_SET_COMPOUND_DYNAMIC_ANALYSIS = python_net_import(
    "SMT.MastaAPI.SystemModel.AnalysesAndResults.DynamicAnalyses.Compound",
    "StraightBevelDiffGearSetCompoundDynamicAnalysis",
)

if TYPE_CHECKING:
    from typing import Any, List, Type, TypeVar

    from mastapy._private.system_model.analyses_and_results import _2943
    from mastapy._private.system_model.analyses_and_results.analysis_cases import (
        _7939,
        _7942,
    )
    from mastapy._private.system_model.analyses_and_results.dynamic_analyses import (
        _6752,
    )
    from mastapy._private.system_model.analyses_and_results.dynamic_analyses.compound import (
        _6774,
        _6780,
        _6808,
        _6834,
        _6855,
        _6874,
        _6881,
        _6882,
    )
    from mastapy._private.system_model.part_model.gears import _2828

    Self = TypeVar("Self", bound="StraightBevelDiffGearSetCompoundDynamicAnalysis")
    CastSelf = TypeVar(
        "CastSelf",
        bound="StraightBevelDiffGearSetCompoundDynamicAnalysis._Cast_StraightBevelDiffGearSetCompoundDynamicAnalysis",
    )


__docformat__ = "restructuredtext en"
__all__ = ("StraightBevelDiffGearSetCompoundDynamicAnalysis",)


@extended_dataclass(frozen=True, slots=True, weakref_slot=True)
class _Cast_StraightBevelDiffGearSetCompoundDynamicAnalysis:
    """Special nested class for casting StraightBevelDiffGearSetCompoundDynamicAnalysis to subclasses."""

    __parent__: "StraightBevelDiffGearSetCompoundDynamicAnalysis"

    @property
    def bevel_gear_set_compound_dynamic_analysis(
        self: "CastSelf",
    ) -> "_6792.BevelGearSetCompoundDynamicAnalysis":
        return self.__parent__._cast(_6792.BevelGearSetCompoundDynamicAnalysis)

    @property
    def agma_gleason_conical_gear_set_compound_dynamic_analysis(
        self: "CastSelf",
    ) -> "_6780.AGMAGleasonConicalGearSetCompoundDynamicAnalysis":
        from mastapy._private.system_model.analyses_and_results.dynamic_analyses.compound import (
            _6780,
        )

        return self.__parent__._cast(
            _6780.AGMAGleasonConicalGearSetCompoundDynamicAnalysis
        )

    @property
    def conical_gear_set_compound_dynamic_analysis(
        self: "CastSelf",
    ) -> "_6808.ConicalGearSetCompoundDynamicAnalysis":
        from mastapy._private.system_model.analyses_and_results.dynamic_analyses.compound import (
            _6808,
        )

        return self.__parent__._cast(_6808.ConicalGearSetCompoundDynamicAnalysis)

    @property
    def gear_set_compound_dynamic_analysis(
        self: "CastSelf",
    ) -> "_6834.GearSetCompoundDynamicAnalysis":
        from mastapy._private.system_model.analyses_and_results.dynamic_analyses.compound import (
            _6834,
        )

        return self.__parent__._cast(_6834.GearSetCompoundDynamicAnalysis)

    @property
    def specialised_assembly_compound_dynamic_analysis(
        self: "CastSelf",
    ) -> "_6874.SpecialisedAssemblyCompoundDynamicAnalysis":
        from mastapy._private.system_model.analyses_and_results.dynamic_analyses.compound import (
            _6874,
        )

        return self.__parent__._cast(_6874.SpecialisedAssemblyCompoundDynamicAnalysis)

    @property
    def abstract_assembly_compound_dynamic_analysis(
        self: "CastSelf",
    ) -> "_6774.AbstractAssemblyCompoundDynamicAnalysis":
        from mastapy._private.system_model.analyses_and_results.dynamic_analyses.compound import (
            _6774,
        )

        return self.__parent__._cast(_6774.AbstractAssemblyCompoundDynamicAnalysis)

    @property
    def part_compound_dynamic_analysis(
        self: "CastSelf",
    ) -> "_6855.PartCompoundDynamicAnalysis":
        from mastapy._private.system_model.analyses_and_results.dynamic_analyses.compound import (
            _6855,
        )

        return self.__parent__._cast(_6855.PartCompoundDynamicAnalysis)

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
    def straight_bevel_diff_gear_set_compound_dynamic_analysis(
        self: "CastSelf",
    ) -> "StraightBevelDiffGearSetCompoundDynamicAnalysis":
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
class StraightBevelDiffGearSetCompoundDynamicAnalysis(
    _6792.BevelGearSetCompoundDynamicAnalysis
):
    """StraightBevelDiffGearSetCompoundDynamicAnalysis

    This is a mastapy class.
    """

    TYPE: ClassVar["Type"] = _STRAIGHT_BEVEL_DIFF_GEAR_SET_COMPOUND_DYNAMIC_ANALYSIS

    wrapped: "Any"

    def __post_init__(self: "Self") -> None:
        """Override of the post initialisation magic method."""
        if not hasattr(self.wrapped, "reference_count"):
            self.wrapped.reference_count = 0

        self.wrapped.reference_count += 1

    @property
    @exception_bridge
    def component_design(self: "Self") -> "_2828.StraightBevelDiffGearSet":
        """mastapy.system_model.part_model.gears.StraightBevelDiffGearSet

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
    def assembly_design(self: "Self") -> "_2828.StraightBevelDiffGearSet":
        """mastapy.system_model.part_model.gears.StraightBevelDiffGearSet

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
    def assembly_analysis_cases_ready(
        self: "Self",
    ) -> "List[_6752.StraightBevelDiffGearSetDynamicAnalysis]":
        """List[mastapy.system_model.analyses_and_results.dynamic_analyses.StraightBevelDiffGearSetDynamicAnalysis]

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
    def straight_bevel_diff_gears_compound_dynamic_analysis(
        self: "Self",
    ) -> "List[_6881.StraightBevelDiffGearCompoundDynamicAnalysis]":
        """List[mastapy.system_model.analyses_and_results.dynamic_analyses.compound.StraightBevelDiffGearCompoundDynamicAnalysis]

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(
            self.wrapped, "StraightBevelDiffGearsCompoundDynamicAnalysis"
        )

        if temp is None:
            return None

        value = conversion.pn_to_mp_objects_in_list(temp)

        if value is None:
            return None

        return value

    @property
    @exception_bridge
    def straight_bevel_diff_meshes_compound_dynamic_analysis(
        self: "Self",
    ) -> "List[_6882.StraightBevelDiffGearMeshCompoundDynamicAnalysis]":
        """List[mastapy.system_model.analyses_and_results.dynamic_analyses.compound.StraightBevelDiffGearMeshCompoundDynamicAnalysis]

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(
            self.wrapped, "StraightBevelDiffMeshesCompoundDynamicAnalysis"
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
    ) -> "List[_6752.StraightBevelDiffGearSetDynamicAnalysis]":
        """List[mastapy.system_model.analyses_and_results.dynamic_analyses.StraightBevelDiffGearSetDynamicAnalysis]

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
    def cast_to(
        self: "Self",
    ) -> "_Cast_StraightBevelDiffGearSetCompoundDynamicAnalysis":
        """Cast to another type.

        Returns:
            _Cast_StraightBevelDiffGearSetCompoundDynamicAnalysis
        """
        return _Cast_StraightBevelDiffGearSetCompoundDynamicAnalysis(self)
