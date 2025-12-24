"""TorqueConverterTurbineCompoundHarmonicAnalysisOfSingleExcitation"""

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
from mastapy._private.system_model.analyses_and_results.harmonic_analyses_single_excitation.compound import (
    _6540,
)

_TORQUE_CONVERTER_TURBINE_COMPOUND_HARMONIC_ANALYSIS_OF_SINGLE_EXCITATION = python_net_import(
    "SMT.MastaAPI.SystemModel.AnalysesAndResults.HarmonicAnalysesSingleExcitation.Compound",
    "TorqueConverterTurbineCompoundHarmonicAnalysisOfSingleExcitation",
)

if TYPE_CHECKING:
    from typing import Any, List, Type, TypeVar

    from mastapy._private.system_model.analyses_and_results import _2943
    from mastapy._private.system_model.analyses_and_results.analysis_cases import (
        _7939,
        _7942,
    )
    from mastapy._private.system_model.analyses_and_results.harmonic_analyses_single_excitation import (
        _6492,
    )
    from mastapy._private.system_model.analyses_and_results.harmonic_analyses_single_excitation.compound import (
        _6526,
        _6580,
        _6582,
    )
    from mastapy._private.system_model.part_model.couplings import _2900

    Self = TypeVar(
        "Self", bound="TorqueConverterTurbineCompoundHarmonicAnalysisOfSingleExcitation"
    )
    CastSelf = TypeVar(
        "CastSelf",
        bound="TorqueConverterTurbineCompoundHarmonicAnalysisOfSingleExcitation._Cast_TorqueConverterTurbineCompoundHarmonicAnalysisOfSingleExcitation",
    )


__docformat__ = "restructuredtext en"
__all__ = ("TorqueConverterTurbineCompoundHarmonicAnalysisOfSingleExcitation",)


@extended_dataclass(frozen=True, slots=True, weakref_slot=True)
class _Cast_TorqueConverterTurbineCompoundHarmonicAnalysisOfSingleExcitation:
    """Special nested class for casting TorqueConverterTurbineCompoundHarmonicAnalysisOfSingleExcitation to subclasses."""

    __parent__: "TorqueConverterTurbineCompoundHarmonicAnalysisOfSingleExcitation"

    @property
    def coupling_half_compound_harmonic_analysis_of_single_excitation(
        self: "CastSelf",
    ) -> "_6540.CouplingHalfCompoundHarmonicAnalysisOfSingleExcitation":
        return self.__parent__._cast(
            _6540.CouplingHalfCompoundHarmonicAnalysisOfSingleExcitation
        )

    @property
    def mountable_component_compound_harmonic_analysis_of_single_excitation(
        self: "CastSelf",
    ) -> "_6580.MountableComponentCompoundHarmonicAnalysisOfSingleExcitation":
        from mastapy._private.system_model.analyses_and_results.harmonic_analyses_single_excitation.compound import (
            _6580,
        )

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
    def torque_converter_turbine_compound_harmonic_analysis_of_single_excitation(
        self: "CastSelf",
    ) -> "TorqueConverterTurbineCompoundHarmonicAnalysisOfSingleExcitation":
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
class TorqueConverterTurbineCompoundHarmonicAnalysisOfSingleExcitation(
    _6540.CouplingHalfCompoundHarmonicAnalysisOfSingleExcitation
):
    """TorqueConverterTurbineCompoundHarmonicAnalysisOfSingleExcitation

    This is a mastapy class.
    """

    TYPE: ClassVar["Type"] = (
        _TORQUE_CONVERTER_TURBINE_COMPOUND_HARMONIC_ANALYSIS_OF_SINGLE_EXCITATION
    )

    wrapped: "Any"

    def __post_init__(self: "Self") -> None:
        """Override of the post initialisation magic method."""
        if not hasattr(self.wrapped, "reference_count"):
            self.wrapped.reference_count = 0

        self.wrapped.reference_count += 1

    @property
    @exception_bridge
    def component_design(self: "Self") -> "_2900.TorqueConverterTurbine":
        """mastapy.system_model.part_model.couplings.TorqueConverterTurbine

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
    def component_analysis_cases_ready(
        self: "Self",
    ) -> "List[_6492.TorqueConverterTurbineHarmonicAnalysisOfSingleExcitation]":
        """List[mastapy.system_model.analyses_and_results.harmonic_analyses_single_excitation.TorqueConverterTurbineHarmonicAnalysisOfSingleExcitation]

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
    @exception_bridge
    def component_analysis_cases(
        self: "Self",
    ) -> "List[_6492.TorqueConverterTurbineHarmonicAnalysisOfSingleExcitation]":
        """List[mastapy.system_model.analyses_and_results.harmonic_analyses_single_excitation.TorqueConverterTurbineHarmonicAnalysisOfSingleExcitation]

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
    def cast_to(
        self: "Self",
    ) -> "_Cast_TorqueConverterTurbineCompoundHarmonicAnalysisOfSingleExcitation":
        """Cast to another type.

        Returns:
            _Cast_TorqueConverterTurbineCompoundHarmonicAnalysisOfSingleExcitation
        """
        return _Cast_TorqueConverterTurbineCompoundHarmonicAnalysisOfSingleExcitation(
            self
        )
