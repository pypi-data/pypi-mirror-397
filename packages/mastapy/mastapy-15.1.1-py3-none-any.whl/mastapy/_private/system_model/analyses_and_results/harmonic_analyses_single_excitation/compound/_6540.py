"""CouplingHalfCompoundHarmonicAnalysisOfSingleExcitation"""

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
from mastapy._private.system_model.analyses_and_results.harmonic_analyses_single_excitation.compound import (
    _6580,
)

_COUPLING_HALF_COMPOUND_HARMONIC_ANALYSIS_OF_SINGLE_EXCITATION = python_net_import(
    "SMT.MastaAPI.SystemModel.AnalysesAndResults.HarmonicAnalysesSingleExcitation.Compound",
    "CouplingHalfCompoundHarmonicAnalysisOfSingleExcitation",
)

if TYPE_CHECKING:
    from typing import Any, List, Type, TypeVar

    from mastapy._private.system_model.analyses_and_results import _2943
    from mastapy._private.system_model.analyses_and_results.analysis_cases import (
        _7939,
        _7942,
    )
    from mastapy._private.system_model.analyses_and_results.harmonic_analyses_single_excitation import (
        _6406,
    )
    from mastapy._private.system_model.analyses_and_results.harmonic_analyses_single_excitation.compound import (
        _6524,
        _6526,
        _6529,
        _6543,
        _6582,
        _6585,
        _6591,
        _6595,
        _6607,
        _6617,
        _6618,
        _6619,
        _6622,
        _6623,
    )

    Self = TypeVar(
        "Self", bound="CouplingHalfCompoundHarmonicAnalysisOfSingleExcitation"
    )
    CastSelf = TypeVar(
        "CastSelf",
        bound="CouplingHalfCompoundHarmonicAnalysisOfSingleExcitation._Cast_CouplingHalfCompoundHarmonicAnalysisOfSingleExcitation",
    )


__docformat__ = "restructuredtext en"
__all__ = ("CouplingHalfCompoundHarmonicAnalysisOfSingleExcitation",)


@extended_dataclass(frozen=True, slots=True, weakref_slot=True)
class _Cast_CouplingHalfCompoundHarmonicAnalysisOfSingleExcitation:
    """Special nested class for casting CouplingHalfCompoundHarmonicAnalysisOfSingleExcitation to subclasses."""

    __parent__: "CouplingHalfCompoundHarmonicAnalysisOfSingleExcitation"

    @property
    def mountable_component_compound_harmonic_analysis_of_single_excitation(
        self: "CastSelf",
    ) -> "_6580.MountableComponentCompoundHarmonicAnalysisOfSingleExcitation":
        return self.__parent__._cast(
            _6580.MountableComponentCompoundHarmonicAnalysisOfSingleExcitation
        )

    @property
    def component_compound_harmonic_analysis_of_single_excitation(
        self: "CastSelf",
    ) -> "_6526.ComponentCompoundHarmonicAnalysisOfSingleExcitation":
        from mastapy._private.system_model.analyses_and_results.harmonic_analyses_single_excitation.compound import (
            _6526,
        )

        return self.__parent__._cast(
            _6526.ComponentCompoundHarmonicAnalysisOfSingleExcitation
        )

    @property
    def part_compound_harmonic_analysis_of_single_excitation(
        self: "CastSelf",
    ) -> "_6582.PartCompoundHarmonicAnalysisOfSingleExcitation":
        from mastapy._private.system_model.analyses_and_results.harmonic_analyses_single_excitation.compound import (
            _6582,
        )

        return self.__parent__._cast(
            _6582.PartCompoundHarmonicAnalysisOfSingleExcitation
        )

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
    def clutch_half_compound_harmonic_analysis_of_single_excitation(
        self: "CastSelf",
    ) -> "_6524.ClutchHalfCompoundHarmonicAnalysisOfSingleExcitation":
        from mastapy._private.system_model.analyses_and_results.harmonic_analyses_single_excitation.compound import (
            _6524,
        )

        return self.__parent__._cast(
            _6524.ClutchHalfCompoundHarmonicAnalysisOfSingleExcitation
        )

    @property
    def concept_coupling_half_compound_harmonic_analysis_of_single_excitation(
        self: "CastSelf",
    ) -> "_6529.ConceptCouplingHalfCompoundHarmonicAnalysisOfSingleExcitation":
        from mastapy._private.system_model.analyses_and_results.harmonic_analyses_single_excitation.compound import (
            _6529,
        )

        return self.__parent__._cast(
            _6529.ConceptCouplingHalfCompoundHarmonicAnalysisOfSingleExcitation
        )

    @property
    def cvt_pulley_compound_harmonic_analysis_of_single_excitation(
        self: "CastSelf",
    ) -> "_6543.CVTPulleyCompoundHarmonicAnalysisOfSingleExcitation":
        from mastapy._private.system_model.analyses_and_results.harmonic_analyses_single_excitation.compound import (
            _6543,
        )

        return self.__parent__._cast(
            _6543.CVTPulleyCompoundHarmonicAnalysisOfSingleExcitation
        )

    @property
    def part_to_part_shear_coupling_half_compound_harmonic_analysis_of_single_excitation(
        self: "CastSelf",
    ) -> "_6585.PartToPartShearCouplingHalfCompoundHarmonicAnalysisOfSingleExcitation":
        from mastapy._private.system_model.analyses_and_results.harmonic_analyses_single_excitation.compound import (
            _6585,
        )

        return self.__parent__._cast(
            _6585.PartToPartShearCouplingHalfCompoundHarmonicAnalysisOfSingleExcitation
        )

    @property
    def pulley_compound_harmonic_analysis_of_single_excitation(
        self: "CastSelf",
    ) -> "_6591.PulleyCompoundHarmonicAnalysisOfSingleExcitation":
        from mastapy._private.system_model.analyses_and_results.harmonic_analyses_single_excitation.compound import (
            _6591,
        )

        return self.__parent__._cast(
            _6591.PulleyCompoundHarmonicAnalysisOfSingleExcitation
        )

    @property
    def rolling_ring_compound_harmonic_analysis_of_single_excitation(
        self: "CastSelf",
    ) -> "_6595.RollingRingCompoundHarmonicAnalysisOfSingleExcitation":
        from mastapy._private.system_model.analyses_and_results.harmonic_analyses_single_excitation.compound import (
            _6595,
        )

        return self.__parent__._cast(
            _6595.RollingRingCompoundHarmonicAnalysisOfSingleExcitation
        )

    @property
    def spring_damper_half_compound_harmonic_analysis_of_single_excitation(
        self: "CastSelf",
    ) -> "_6607.SpringDamperHalfCompoundHarmonicAnalysisOfSingleExcitation":
        from mastapy._private.system_model.analyses_and_results.harmonic_analyses_single_excitation.compound import (
            _6607,
        )

        return self.__parent__._cast(
            _6607.SpringDamperHalfCompoundHarmonicAnalysisOfSingleExcitation
        )

    @property
    def synchroniser_half_compound_harmonic_analysis_of_single_excitation(
        self: "CastSelf",
    ) -> "_6617.SynchroniserHalfCompoundHarmonicAnalysisOfSingleExcitation":
        from mastapy._private.system_model.analyses_and_results.harmonic_analyses_single_excitation.compound import (
            _6617,
        )

        return self.__parent__._cast(
            _6617.SynchroniserHalfCompoundHarmonicAnalysisOfSingleExcitation
        )

    @property
    def synchroniser_part_compound_harmonic_analysis_of_single_excitation(
        self: "CastSelf",
    ) -> "_6618.SynchroniserPartCompoundHarmonicAnalysisOfSingleExcitation":
        from mastapy._private.system_model.analyses_and_results.harmonic_analyses_single_excitation.compound import (
            _6618,
        )

        return self.__parent__._cast(
            _6618.SynchroniserPartCompoundHarmonicAnalysisOfSingleExcitation
        )

    @property
    def synchroniser_sleeve_compound_harmonic_analysis_of_single_excitation(
        self: "CastSelf",
    ) -> "_6619.SynchroniserSleeveCompoundHarmonicAnalysisOfSingleExcitation":
        from mastapy._private.system_model.analyses_and_results.harmonic_analyses_single_excitation.compound import (
            _6619,
        )

        return self.__parent__._cast(
            _6619.SynchroniserSleeveCompoundHarmonicAnalysisOfSingleExcitation
        )

    @property
    def torque_converter_pump_compound_harmonic_analysis_of_single_excitation(
        self: "CastSelf",
    ) -> "_6622.TorqueConverterPumpCompoundHarmonicAnalysisOfSingleExcitation":
        from mastapy._private.system_model.analyses_and_results.harmonic_analyses_single_excitation.compound import (
            _6622,
        )

        return self.__parent__._cast(
            _6622.TorqueConverterPumpCompoundHarmonicAnalysisOfSingleExcitation
        )

    @property
    def torque_converter_turbine_compound_harmonic_analysis_of_single_excitation(
        self: "CastSelf",
    ) -> "_6623.TorqueConverterTurbineCompoundHarmonicAnalysisOfSingleExcitation":
        from mastapy._private.system_model.analyses_and_results.harmonic_analyses_single_excitation.compound import (
            _6623,
        )

        return self.__parent__._cast(
            _6623.TorqueConverterTurbineCompoundHarmonicAnalysisOfSingleExcitation
        )

    @property
    def coupling_half_compound_harmonic_analysis_of_single_excitation(
        self: "CastSelf",
    ) -> "CouplingHalfCompoundHarmonicAnalysisOfSingleExcitation":
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
class CouplingHalfCompoundHarmonicAnalysisOfSingleExcitation(
    _6580.MountableComponentCompoundHarmonicAnalysisOfSingleExcitation
):
    """CouplingHalfCompoundHarmonicAnalysisOfSingleExcitation

    This is a mastapy class.
    """

    TYPE: ClassVar["Type"] = (
        _COUPLING_HALF_COMPOUND_HARMONIC_ANALYSIS_OF_SINGLE_EXCITATION
    )

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
    ) -> "List[_6406.CouplingHalfHarmonicAnalysisOfSingleExcitation]":
        """List[mastapy.system_model.analyses_and_results.harmonic_analyses_single_excitation.CouplingHalfHarmonicAnalysisOfSingleExcitation]

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
    ) -> "List[_6406.CouplingHalfHarmonicAnalysisOfSingleExcitation]":
        """List[mastapy.system_model.analyses_and_results.harmonic_analyses_single_excitation.CouplingHalfHarmonicAnalysisOfSingleExcitation]

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
    def cast_to(
        self: "Self",
    ) -> "_Cast_CouplingHalfCompoundHarmonicAnalysisOfSingleExcitation":
        """Cast to another type.

        Returns:
            _Cast_CouplingHalfCompoundHarmonicAnalysisOfSingleExcitation
        """
        return _Cast_CouplingHalfCompoundHarmonicAnalysisOfSingleExcitation(self)
