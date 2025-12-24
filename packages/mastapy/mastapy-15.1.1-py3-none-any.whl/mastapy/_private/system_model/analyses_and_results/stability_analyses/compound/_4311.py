"""SpiralBevelGearSetCompoundStabilityAnalysis"""

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
from mastapy._private.system_model.analyses_and_results.stability_analyses.compound import (
    _4226,
)

_SPIRAL_BEVEL_GEAR_SET_COMPOUND_STABILITY_ANALYSIS = python_net_import(
    "SMT.MastaAPI.SystemModel.AnalysesAndResults.StabilityAnalyses.Compound",
    "SpiralBevelGearSetCompoundStabilityAnalysis",
)

if TYPE_CHECKING:
    from typing import Any, List, Type, TypeVar

    from mastapy._private.system_model.analyses_and_results import _2943
    from mastapy._private.system_model.analyses_and_results.analysis_cases import (
        _7939,
        _7942,
    )
    from mastapy._private.system_model.analyses_and_results.stability_analyses import (
        _4176,
    )
    from mastapy._private.system_model.analyses_and_results.stability_analyses.compound import (
        _4208,
        _4214,
        _4242,
        _4268,
        _4289,
        _4308,
        _4309,
        _4310,
    )
    from mastapy._private.system_model.part_model.gears import _2826

    Self = TypeVar("Self", bound="SpiralBevelGearSetCompoundStabilityAnalysis")
    CastSelf = TypeVar(
        "CastSelf",
        bound="SpiralBevelGearSetCompoundStabilityAnalysis._Cast_SpiralBevelGearSetCompoundStabilityAnalysis",
    )


__docformat__ = "restructuredtext en"
__all__ = ("SpiralBevelGearSetCompoundStabilityAnalysis",)


@extended_dataclass(frozen=True, slots=True, weakref_slot=True)
class _Cast_SpiralBevelGearSetCompoundStabilityAnalysis:
    """Special nested class for casting SpiralBevelGearSetCompoundStabilityAnalysis to subclasses."""

    __parent__: "SpiralBevelGearSetCompoundStabilityAnalysis"

    @property
    def bevel_gear_set_compound_stability_analysis(
        self: "CastSelf",
    ) -> "_4226.BevelGearSetCompoundStabilityAnalysis":
        return self.__parent__._cast(_4226.BevelGearSetCompoundStabilityAnalysis)

    @property
    def agma_gleason_conical_gear_set_compound_stability_analysis(
        self: "CastSelf",
    ) -> "_4214.AGMAGleasonConicalGearSetCompoundStabilityAnalysis":
        from mastapy._private.system_model.analyses_and_results.stability_analyses.compound import (
            _4214,
        )

        return self.__parent__._cast(
            _4214.AGMAGleasonConicalGearSetCompoundStabilityAnalysis
        )

    @property
    def conical_gear_set_compound_stability_analysis(
        self: "CastSelf",
    ) -> "_4242.ConicalGearSetCompoundStabilityAnalysis":
        from mastapy._private.system_model.analyses_and_results.stability_analyses.compound import (
            _4242,
        )

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
    def spiral_bevel_gear_set_compound_stability_analysis(
        self: "CastSelf",
    ) -> "SpiralBevelGearSetCompoundStabilityAnalysis":
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
class SpiralBevelGearSetCompoundStabilityAnalysis(
    _4226.BevelGearSetCompoundStabilityAnalysis
):
    """SpiralBevelGearSetCompoundStabilityAnalysis

    This is a mastapy class.
    """

    TYPE: ClassVar["Type"] = _SPIRAL_BEVEL_GEAR_SET_COMPOUND_STABILITY_ANALYSIS

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
    def assembly_analysis_cases_ready(
        self: "Self",
    ) -> "List[_4176.SpiralBevelGearSetStabilityAnalysis]":
        """List[mastapy.system_model.analyses_and_results.stability_analyses.SpiralBevelGearSetStabilityAnalysis]

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
    def spiral_bevel_gears_compound_stability_analysis(
        self: "Self",
    ) -> "List[_4309.SpiralBevelGearCompoundStabilityAnalysis]":
        """List[mastapy.system_model.analyses_and_results.stability_analyses.compound.SpiralBevelGearCompoundStabilityAnalysis]

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(
            self.wrapped, "SpiralBevelGearsCompoundStabilityAnalysis"
        )

        if temp is None:
            return None

        value = conversion.pn_to_mp_objects_in_list(temp)

        if value is None:
            return None

        return value

    @property
    @exception_bridge
    def spiral_bevel_meshes_compound_stability_analysis(
        self: "Self",
    ) -> "List[_4310.SpiralBevelGearMeshCompoundStabilityAnalysis]":
        """List[mastapy.system_model.analyses_and_results.stability_analyses.compound.SpiralBevelGearMeshCompoundStabilityAnalysis]

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(
            self.wrapped, "SpiralBevelMeshesCompoundStabilityAnalysis"
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
    ) -> "List[_4176.SpiralBevelGearSetStabilityAnalysis]":
        """List[mastapy.system_model.analyses_and_results.stability_analyses.SpiralBevelGearSetStabilityAnalysis]

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
    def cast_to(self: "Self") -> "_Cast_SpiralBevelGearSetCompoundStabilityAnalysis":
        """Cast to another type.

        Returns:
            _Cast_SpiralBevelGearSetCompoundStabilityAnalysis
        """
        return _Cast_SpiralBevelGearSetCompoundStabilityAnalysis(self)
