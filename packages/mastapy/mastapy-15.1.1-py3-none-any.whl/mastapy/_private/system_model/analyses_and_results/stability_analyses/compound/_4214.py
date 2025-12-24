"""AGMAGleasonConicalGearSetCompoundStabilityAnalysis"""

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
from mastapy._private.system_model.analyses_and_results.stability_analyses.compound import (
    _4242,
)

_AGMA_GLEASON_CONICAL_GEAR_SET_COMPOUND_STABILITY_ANALYSIS = python_net_import(
    "SMT.MastaAPI.SystemModel.AnalysesAndResults.StabilityAnalyses.Compound",
    "AGMAGleasonConicalGearSetCompoundStabilityAnalysis",
)

if TYPE_CHECKING:
    from typing import Any, List, Type, TypeVar

    from mastapy._private.system_model.analyses_and_results import _2943
    from mastapy._private.system_model.analyses_and_results.analysis_cases import (
        _7939,
        _7942,
    )
    from mastapy._private.system_model.analyses_and_results.stability_analyses import (
        _4077,
    )
    from mastapy._private.system_model.analyses_and_results.stability_analyses.compound import (
        _4208,
        _4221,
        _4226,
        _4268,
        _4272,
        _4289,
        _4308,
        _4311,
        _4317,
        _4320,
        _4338,
    )

    Self = TypeVar("Self", bound="AGMAGleasonConicalGearSetCompoundStabilityAnalysis")
    CastSelf = TypeVar(
        "CastSelf",
        bound="AGMAGleasonConicalGearSetCompoundStabilityAnalysis._Cast_AGMAGleasonConicalGearSetCompoundStabilityAnalysis",
    )


__docformat__ = "restructuredtext en"
__all__ = ("AGMAGleasonConicalGearSetCompoundStabilityAnalysis",)


@extended_dataclass(frozen=True, slots=True, weakref_slot=True)
class _Cast_AGMAGleasonConicalGearSetCompoundStabilityAnalysis:
    """Special nested class for casting AGMAGleasonConicalGearSetCompoundStabilityAnalysis to subclasses."""

    __parent__: "AGMAGleasonConicalGearSetCompoundStabilityAnalysis"

    @property
    def conical_gear_set_compound_stability_analysis(
        self: "CastSelf",
    ) -> "_4242.ConicalGearSetCompoundStabilityAnalysis":
        return self.__parent__._cast(_4242.ConicalGearSetCompoundStabilityAnalysis)

    @property
    def gear_set_compound_stability_analysis(
        self: "CastSelf",
    ) -> "_4268.GearSetCompoundStabilityAnalysis":
        from mastapy._private.system_model.analyses_and_results.stability_analyses.compound import (
            _4268,
        )

        return self.__parent__._cast(_4268.GearSetCompoundStabilityAnalysis)

    @property
    def specialised_assembly_compound_stability_analysis(
        self: "CastSelf",
    ) -> "_4308.SpecialisedAssemblyCompoundStabilityAnalysis":
        from mastapy._private.system_model.analyses_and_results.stability_analyses.compound import (
            _4308,
        )

        return self.__parent__._cast(_4308.SpecialisedAssemblyCompoundStabilityAnalysis)

    @property
    def abstract_assembly_compound_stability_analysis(
        self: "CastSelf",
    ) -> "_4208.AbstractAssemblyCompoundStabilityAnalysis":
        from mastapy._private.system_model.analyses_and_results.stability_analyses.compound import (
            _4208,
        )

        return self.__parent__._cast(_4208.AbstractAssemblyCompoundStabilityAnalysis)

    @property
    def part_compound_stability_analysis(
        self: "CastSelf",
    ) -> "_4289.PartCompoundStabilityAnalysis":
        from mastapy._private.system_model.analyses_and_results.stability_analyses.compound import (
            _4289,
        )

        return self.__parent__._cast(_4289.PartCompoundStabilityAnalysis)

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
    def bevel_differential_gear_set_compound_stability_analysis(
        self: "CastSelf",
    ) -> "_4221.BevelDifferentialGearSetCompoundStabilityAnalysis":
        from mastapy._private.system_model.analyses_and_results.stability_analyses.compound import (
            _4221,
        )

        return self.__parent__._cast(
            _4221.BevelDifferentialGearSetCompoundStabilityAnalysis
        )

    @property
    def bevel_gear_set_compound_stability_analysis(
        self: "CastSelf",
    ) -> "_4226.BevelGearSetCompoundStabilityAnalysis":
        from mastapy._private.system_model.analyses_and_results.stability_analyses.compound import (
            _4226,
        )

        return self.__parent__._cast(_4226.BevelGearSetCompoundStabilityAnalysis)

    @property
    def hypoid_gear_set_compound_stability_analysis(
        self: "CastSelf",
    ) -> "_4272.HypoidGearSetCompoundStabilityAnalysis":
        from mastapy._private.system_model.analyses_and_results.stability_analyses.compound import (
            _4272,
        )

        return self.__parent__._cast(_4272.HypoidGearSetCompoundStabilityAnalysis)

    @property
    def spiral_bevel_gear_set_compound_stability_analysis(
        self: "CastSelf",
    ) -> "_4311.SpiralBevelGearSetCompoundStabilityAnalysis":
        from mastapy._private.system_model.analyses_and_results.stability_analyses.compound import (
            _4311,
        )

        return self.__parent__._cast(_4311.SpiralBevelGearSetCompoundStabilityAnalysis)

    @property
    def straight_bevel_diff_gear_set_compound_stability_analysis(
        self: "CastSelf",
    ) -> "_4317.StraightBevelDiffGearSetCompoundStabilityAnalysis":
        from mastapy._private.system_model.analyses_and_results.stability_analyses.compound import (
            _4317,
        )

        return self.__parent__._cast(
            _4317.StraightBevelDiffGearSetCompoundStabilityAnalysis
        )

    @property
    def straight_bevel_gear_set_compound_stability_analysis(
        self: "CastSelf",
    ) -> "_4320.StraightBevelGearSetCompoundStabilityAnalysis":
        from mastapy._private.system_model.analyses_and_results.stability_analyses.compound import (
            _4320,
        )

        return self.__parent__._cast(
            _4320.StraightBevelGearSetCompoundStabilityAnalysis
        )

    @property
    def zerol_bevel_gear_set_compound_stability_analysis(
        self: "CastSelf",
    ) -> "_4338.ZerolBevelGearSetCompoundStabilityAnalysis":
        from mastapy._private.system_model.analyses_and_results.stability_analyses.compound import (
            _4338,
        )

        return self.__parent__._cast(_4338.ZerolBevelGearSetCompoundStabilityAnalysis)

    @property
    def agma_gleason_conical_gear_set_compound_stability_analysis(
        self: "CastSelf",
    ) -> "AGMAGleasonConicalGearSetCompoundStabilityAnalysis":
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
class AGMAGleasonConicalGearSetCompoundStabilityAnalysis(
    _4242.ConicalGearSetCompoundStabilityAnalysis
):
    """AGMAGleasonConicalGearSetCompoundStabilityAnalysis

    This is a mastapy class.
    """

    TYPE: ClassVar["Type"] = _AGMA_GLEASON_CONICAL_GEAR_SET_COMPOUND_STABILITY_ANALYSIS

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
    ) -> "List[_4077.AGMAGleasonConicalGearSetStabilityAnalysis]":
        """List[mastapy.system_model.analyses_and_results.stability_analyses.AGMAGleasonConicalGearSetStabilityAnalysis]

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
    ) -> "List[_4077.AGMAGleasonConicalGearSetStabilityAnalysis]":
        """List[mastapy.system_model.analyses_and_results.stability_analyses.AGMAGleasonConicalGearSetStabilityAnalysis]

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
    def cast_to(
        self: "Self",
    ) -> "_Cast_AGMAGleasonConicalGearSetCompoundStabilityAnalysis":
        """Cast to another type.

        Returns:
            _Cast_AGMAGleasonConicalGearSetCompoundStabilityAnalysis
        """
        return _Cast_AGMAGleasonConicalGearSetCompoundStabilityAnalysis(self)
