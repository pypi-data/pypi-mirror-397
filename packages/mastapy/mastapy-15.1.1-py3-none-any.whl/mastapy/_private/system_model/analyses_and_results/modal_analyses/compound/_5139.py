"""PlanetaryGearSetCompoundModalAnalysis"""

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
from mastapy._private.system_model.analyses_and_results.modal_analyses.compound import (
    _5102,
)

_PLANETARY_GEAR_SET_COMPOUND_MODAL_ANALYSIS = python_net_import(
    "SMT.MastaAPI.SystemModel.AnalysesAndResults.ModalAnalyses.Compound",
    "PlanetaryGearSetCompoundModalAnalysis",
)

if TYPE_CHECKING:
    from typing import Any, List, Type, TypeVar

    from mastapy._private.system_model.analyses_and_results import _2943
    from mastapy._private.system_model.analyses_and_results.analysis_cases import (
        _7939,
        _7942,
    )
    from mastapy._private.system_model.analyses_and_results.modal_analyses import _4992
    from mastapy._private.system_model.analyses_and_results.modal_analyses.compound import (
        _5053,
        _5113,
        _5134,
        _5153,
    )

    Self = TypeVar("Self", bound="PlanetaryGearSetCompoundModalAnalysis")
    CastSelf = TypeVar(
        "CastSelf",
        bound="PlanetaryGearSetCompoundModalAnalysis._Cast_PlanetaryGearSetCompoundModalAnalysis",
    )


__docformat__ = "restructuredtext en"
__all__ = ("PlanetaryGearSetCompoundModalAnalysis",)


@extended_dataclass(frozen=True, slots=True, weakref_slot=True)
class _Cast_PlanetaryGearSetCompoundModalAnalysis:
    """Special nested class for casting PlanetaryGearSetCompoundModalAnalysis to subclasses."""

    __parent__: "PlanetaryGearSetCompoundModalAnalysis"

    @property
    def cylindrical_gear_set_compound_modal_analysis(
        self: "CastSelf",
    ) -> "_5102.CylindricalGearSetCompoundModalAnalysis":
        return self.__parent__._cast(_5102.CylindricalGearSetCompoundModalAnalysis)

    @property
    def gear_set_compound_modal_analysis(
        self: "CastSelf",
    ) -> "_5113.GearSetCompoundModalAnalysis":
        from mastapy._private.system_model.analyses_and_results.modal_analyses.compound import (
            _5113,
        )

        return self.__parent__._cast(_5113.GearSetCompoundModalAnalysis)

    @property
    def specialised_assembly_compound_modal_analysis(
        self: "CastSelf",
    ) -> "_5153.SpecialisedAssemblyCompoundModalAnalysis":
        from mastapy._private.system_model.analyses_and_results.modal_analyses.compound import (
            _5153,
        )

        return self.__parent__._cast(_5153.SpecialisedAssemblyCompoundModalAnalysis)

    @property
    def abstract_assembly_compound_modal_analysis(
        self: "CastSelf",
    ) -> "_5053.AbstractAssemblyCompoundModalAnalysis":
        from mastapy._private.system_model.analyses_and_results.modal_analyses.compound import (
            _5053,
        )

        return self.__parent__._cast(_5053.AbstractAssemblyCompoundModalAnalysis)

    @property
    def part_compound_modal_analysis(
        self: "CastSelf",
    ) -> "_5134.PartCompoundModalAnalysis":
        from mastapy._private.system_model.analyses_and_results.modal_analyses.compound import (
            _5134,
        )

        return self.__parent__._cast(_5134.PartCompoundModalAnalysis)

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
    def planetary_gear_set_compound_modal_analysis(
        self: "CastSelf",
    ) -> "PlanetaryGearSetCompoundModalAnalysis":
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
class PlanetaryGearSetCompoundModalAnalysis(
    _5102.CylindricalGearSetCompoundModalAnalysis
):
    """PlanetaryGearSetCompoundModalAnalysis

    This is a mastapy class.
    """

    TYPE: ClassVar["Type"] = _PLANETARY_GEAR_SET_COMPOUND_MODAL_ANALYSIS

    wrapped: "Any"

    def __post_init__(self: "Self") -> None:
        """Override of the post initialisation magic method."""
        if not hasattr(self.wrapped, "reference_count"):
            self.wrapped.reference_count = 0

        self.wrapped.reference_count += 1

    @property
    @exception_bridge
    def assembly_analysis_cases_ready(
        self: "Self",
    ) -> "List[_4992.PlanetaryGearSetModalAnalysis]":
        """List[mastapy.system_model.analyses_and_results.modal_analyses.PlanetaryGearSetModalAnalysis]

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
    def assembly_analysis_cases(
        self: "Self",
    ) -> "List[_4992.PlanetaryGearSetModalAnalysis]":
        """List[mastapy.system_model.analyses_and_results.modal_analyses.PlanetaryGearSetModalAnalysis]

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
    def cast_to(self: "Self") -> "_Cast_PlanetaryGearSetCompoundModalAnalysis":
        """Cast to another type.

        Returns:
            _Cast_PlanetaryGearSetCompoundModalAnalysis
        """
        return _Cast_PlanetaryGearSetCompoundModalAnalysis(self)
