"""CompoundAnalysis"""

from __future__ import annotations

from typing import TYPE_CHECKING, ClassVar

from mastapy._private._internal.dataclasses import extended_dataclass
from mastapy._private._internal.exception_bridge import exception_bridge
from mastapy._private._internal.exceptions import CastException
from mastapy._private._internal.python_net import (
    python_net_import,
    pythonnet_method_call,
    pythonnet_method_call_overload,
    pythonnet_property_get,
)
from mastapy._private._internal.type_enforcement import enforce_parameter_types

from mastapy._private import _7949
from mastapy._private._internal import conversion, utility

_TASK_PROGRESS = python_net_import("SMT.MastaAPIUtility", "TaskProgress")
_COMPOUND_ANALYSIS = python_net_import(
    "SMT.MastaAPI.SystemModel.AnalysesAndResults", "CompoundAnalysis"
)

if TYPE_CHECKING:
    from typing import Any, Iterable, Type, TypeVar

    from mastapy._private import _7955
    from mastapy._private.system_model import _2451
    from mastapy._private.system_model.analyses_and_results import (
        _2950,
        _2951,
        _2952,
        _2953,
        _2954,
        _2955,
        _2956,
        _2957,
        _2958,
        _2959,
        _2960,
        _2961,
        _2962,
        _2963,
        _2964,
        _2965,
        _2966,
        _2967,
        _2968,
        _2969,
        _2970,
        _2971,
        _2972,
        _2973,
        _2974,
    )
    from mastapy._private.system_model.analyses_and_results.analysis_cases import _7939

    Self = TypeVar("Self", bound="CompoundAnalysis")
    CastSelf = TypeVar("CastSelf", bound="CompoundAnalysis._Cast_CompoundAnalysis")


__docformat__ = "restructuredtext en"
__all__ = ("CompoundAnalysis",)


@extended_dataclass(frozen=True, slots=True, weakref_slot=True)
class _Cast_CompoundAnalysis:
    """Special nested class for casting CompoundAnalysis to subclasses."""

    __parent__: "CompoundAnalysis"

    @property
    def marshal_by_ref_object_permanent(
        self: "CastSelf",
    ) -> "_7949.MarshalByRefObjectPermanent":
        return self.__parent__._cast(_7949.MarshalByRefObjectPermanent)

    @property
    def compound_advanced_system_deflection(
        self: "CastSelf",
    ) -> "_2950.CompoundAdvancedSystemDeflection":
        from mastapy._private.system_model.analyses_and_results import _2950

        return self.__parent__._cast(_2950.CompoundAdvancedSystemDeflection)

    @property
    def compound_advanced_system_deflection_sub_analysis(
        self: "CastSelf",
    ) -> "_2951.CompoundAdvancedSystemDeflectionSubAnalysis":
        from mastapy._private.system_model.analyses_and_results import _2951

        return self.__parent__._cast(_2951.CompoundAdvancedSystemDeflectionSubAnalysis)

    @property
    def compound_advanced_time_stepping_analysis_for_modulation(
        self: "CastSelf",
    ) -> "_2952.CompoundAdvancedTimeSteppingAnalysisForModulation":
        from mastapy._private.system_model.analyses_and_results import _2952

        return self.__parent__._cast(
            _2952.CompoundAdvancedTimeSteppingAnalysisForModulation
        )

    @property
    def compound_critical_speed_analysis(
        self: "CastSelf",
    ) -> "_2953.CompoundCriticalSpeedAnalysis":
        from mastapy._private.system_model.analyses_and_results import _2953

        return self.__parent__._cast(_2953.CompoundCriticalSpeedAnalysis)

    @property
    def compound_dynamic_analysis(self: "CastSelf") -> "_2954.CompoundDynamicAnalysis":
        from mastapy._private.system_model.analyses_and_results import _2954

        return self.__parent__._cast(_2954.CompoundDynamicAnalysis)

    @property
    def compound_dynamic_model_at_a_stiffness(
        self: "CastSelf",
    ) -> "_2955.CompoundDynamicModelAtAStiffness":
        from mastapy._private.system_model.analyses_and_results import _2955

        return self.__parent__._cast(_2955.CompoundDynamicModelAtAStiffness)

    @property
    def compound_dynamic_model_for_harmonic_analysis(
        self: "CastSelf",
    ) -> "_2956.CompoundDynamicModelForHarmonicAnalysis":
        from mastapy._private.system_model.analyses_and_results import _2956

        return self.__parent__._cast(_2956.CompoundDynamicModelForHarmonicAnalysis)

    @property
    def compound_dynamic_model_for_modal_analysis(
        self: "CastSelf",
    ) -> "_2957.CompoundDynamicModelForModalAnalysis":
        from mastapy._private.system_model.analyses_and_results import _2957

        return self.__parent__._cast(_2957.CompoundDynamicModelForModalAnalysis)

    @property
    def compound_dynamic_model_for_stability_analysis(
        self: "CastSelf",
    ) -> "_2958.CompoundDynamicModelForStabilityAnalysis":
        from mastapy._private.system_model.analyses_and_results import _2958

        return self.__parent__._cast(_2958.CompoundDynamicModelForStabilityAnalysis)

    @property
    def compound_dynamic_model_for_steady_state_synchronous_response(
        self: "CastSelf",
    ) -> "_2959.CompoundDynamicModelForSteadyStateSynchronousResponse":
        from mastapy._private.system_model.analyses_and_results import _2959

        return self.__parent__._cast(
            _2959.CompoundDynamicModelForSteadyStateSynchronousResponse
        )

    @property
    def compound_harmonic_analysis(
        self: "CastSelf",
    ) -> "_2960.CompoundHarmonicAnalysis":
        from mastapy._private.system_model.analyses_and_results import _2960

        return self.__parent__._cast(_2960.CompoundHarmonicAnalysis)

    @property
    def compound_harmonic_analysis_for_advanced_time_stepping_analysis_for_modulation(
        self: "CastSelf",
    ) -> "_2961.CompoundHarmonicAnalysisForAdvancedTimeSteppingAnalysisForModulation":
        from mastapy._private.system_model.analyses_and_results import _2961

        return self.__parent__._cast(
            _2961.CompoundHarmonicAnalysisForAdvancedTimeSteppingAnalysisForModulation
        )

    @property
    def compound_harmonic_analysis_of_single_excitation(
        self: "CastSelf",
    ) -> "_2962.CompoundHarmonicAnalysisOfSingleExcitation":
        from mastapy._private.system_model.analyses_and_results import _2962

        return self.__parent__._cast(_2962.CompoundHarmonicAnalysisOfSingleExcitation)

    @property
    def compound_modal_analysis(self: "CastSelf") -> "_2963.CompoundModalAnalysis":
        from mastapy._private.system_model.analyses_and_results import _2963

        return self.__parent__._cast(_2963.CompoundModalAnalysis)

    @property
    def compound_modal_analysis_at_a_speed(
        self: "CastSelf",
    ) -> "_2964.CompoundModalAnalysisAtASpeed":
        from mastapy._private.system_model.analyses_and_results import _2964

        return self.__parent__._cast(_2964.CompoundModalAnalysisAtASpeed)

    @property
    def compound_modal_analysis_at_a_stiffness(
        self: "CastSelf",
    ) -> "_2965.CompoundModalAnalysisAtAStiffness":
        from mastapy._private.system_model.analyses_and_results import _2965

        return self.__parent__._cast(_2965.CompoundModalAnalysisAtAStiffness)

    @property
    def compound_modal_analysis_for_harmonic_analysis(
        self: "CastSelf",
    ) -> "_2966.CompoundModalAnalysisForHarmonicAnalysis":
        from mastapy._private.system_model.analyses_and_results import _2966

        return self.__parent__._cast(_2966.CompoundModalAnalysisForHarmonicAnalysis)

    @property
    def compound_multibody_dynamics_analysis(
        self: "CastSelf",
    ) -> "_2967.CompoundMultibodyDynamicsAnalysis":
        from mastapy._private.system_model.analyses_and_results import _2967

        return self.__parent__._cast(_2967.CompoundMultibodyDynamicsAnalysis)

    @property
    def compound_power_flow(self: "CastSelf") -> "_2968.CompoundPowerFlow":
        from mastapy._private.system_model.analyses_and_results import _2968

        return self.__parent__._cast(_2968.CompoundPowerFlow)

    @property
    def compound_stability_analysis(
        self: "CastSelf",
    ) -> "_2969.CompoundStabilityAnalysis":
        from mastapy._private.system_model.analyses_and_results import _2969

        return self.__parent__._cast(_2969.CompoundStabilityAnalysis)

    @property
    def compound_steady_state_synchronous_response(
        self: "CastSelf",
    ) -> "_2970.CompoundSteadyStateSynchronousResponse":
        from mastapy._private.system_model.analyses_and_results import _2970

        return self.__parent__._cast(_2970.CompoundSteadyStateSynchronousResponse)

    @property
    def compound_steady_state_synchronous_response_at_a_speed(
        self: "CastSelf",
    ) -> "_2971.CompoundSteadyStateSynchronousResponseAtASpeed":
        from mastapy._private.system_model.analyses_and_results import _2971

        return self.__parent__._cast(
            _2971.CompoundSteadyStateSynchronousResponseAtASpeed
        )

    @property
    def compound_steady_state_synchronous_response_on_a_shaft(
        self: "CastSelf",
    ) -> "_2972.CompoundSteadyStateSynchronousResponseOnAShaft":
        from mastapy._private.system_model.analyses_and_results import _2972

        return self.__parent__._cast(
            _2972.CompoundSteadyStateSynchronousResponseOnAShaft
        )

    @property
    def compound_system_deflection(
        self: "CastSelf",
    ) -> "_2973.CompoundSystemDeflection":
        from mastapy._private.system_model.analyses_and_results import _2973

        return self.__parent__._cast(_2973.CompoundSystemDeflection)

    @property
    def compound_torsional_system_deflection(
        self: "CastSelf",
    ) -> "_2974.CompoundTorsionalSystemDeflection":
        from mastapy._private.system_model.analyses_and_results import _2974

        return self.__parent__._cast(_2974.CompoundTorsionalSystemDeflection)

    @property
    def compound_analysis(self: "CastSelf") -> "CompoundAnalysis":
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
class CompoundAnalysis(_7949.MarshalByRefObjectPermanent):
    """CompoundAnalysis

    This is a mastapy class.
    """

    TYPE: ClassVar["Type"] = _COMPOUND_ANALYSIS

    wrapped: "Any"

    def __post_init__(self: "Self") -> None:
        """Override of the post initialisation magic method."""
        if not hasattr(self.wrapped, "reference_count"):
            self.wrapped.reference_count = 0

        self.wrapped.reference_count += 1

    @property
    @exception_bridge
    def results_ready(self: "Self") -> "bool":
        """bool

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "ResultsReady")

        if temp is None:
            return False

        return temp

    @exception_bridge
    def perform_analysis(self: "Self") -> None:
        """Method does not return."""
        pythonnet_method_call(self.wrapped, "PerformAnalysis")

    @exception_bridge
    @enforce_parameter_types
    def perform_analysis_with_progress(
        self: "Self", progress: "_7955.TaskProgress"
    ) -> None:
        """Method does not return.

        Args:
            progress (mastapy.TaskProgress)
        """
        pythonnet_method_call_overload(
            self.wrapped,
            "PerformAnalysis",
            [_TASK_PROGRESS],
            progress.wrapped if progress else None,
        )

    @exception_bridge
    @enforce_parameter_types
    def results_for(
        self: "Self", design_entity: "_2451.DesignEntity"
    ) -> "Iterable[_7939.DesignEntityCompoundAnalysis]":
        """Iterable[mastapy.system_model.analyses_and_results.analysis_cases.DesignEntityCompoundAnalysis]

        Args:
            design_entity (mastapy.system_model.DesignEntity)
        """
        return conversion.pn_to_mp_objects_in_iterable(
            pythonnet_method_call(
                self.wrapped,
                "ResultsFor",
                design_entity.wrapped if design_entity else None,
            )
        )

    @property
    def cast_to(self: "Self") -> "_Cast_CompoundAnalysis":
        """Cast to another type.

        Returns:
            _Cast_CompoundAnalysis
        """
        return _Cast_CompoundAnalysis(self)
