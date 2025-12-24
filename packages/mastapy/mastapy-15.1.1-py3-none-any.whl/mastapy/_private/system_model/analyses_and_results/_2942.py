"""Context"""

from __future__ import annotations

from typing import TYPE_CHECKING, ClassVar

from mastapy._private._internal.dataclasses import extended_dataclass
from mastapy._private._internal.exception_bridge import exception_bridge
from mastapy._private._internal.exceptions import CastException
from mastapy._private._internal.python_net import (
    python_net_import,
    pythonnet_method_call,
    pythonnet_property_get,
    pythonnet_property_set,
)
from mastapy._private._internal.type_enforcement import enforce_parameter_types

from mastapy._private import _0
from mastapy._private._internal import constructor, conversion, utility

_CONTEXT = python_net_import("SMT.MastaAPI.SystemModel.AnalysesAndResults", "Context")

if TYPE_CHECKING:
    from typing import Any, List, Type, TypeVar

    from mastapy._private._internal.typing import PathLike

    from mastapy._private.system_model import _2448
    from mastapy._private.system_model.analyses_and_results.advanced_system_deflections import (
        _7448,
        _7450,
    )
    from mastapy._private.system_model.analyses_and_results.advanced_time_stepping_analyses_for_modulation import (
        _7180,
    )
    from mastapy._private.system_model.analyses_and_results.analysis_cases import (
        _7931,
        _7933,
        _7940,
        _7946,
        _7947,
    )
    from mastapy._private.system_model.analyses_and_results.critical_speed_analyses import (
        _6951,
    )
    from mastapy._private.system_model.analyses_and_results.dynamic_analyses import (
        _6693,
    )
    from mastapy._private.system_model.analyses_and_results.harmonic_analyses import (
        _6075,
        _6104,
        _6109,
        _6115,
    )
    from mastapy._private.system_model.analyses_and_results.harmonic_analyses.transfer_path_analyses import (
        _6192,
        _6193,
    )
    from mastapy._private.system_model.analyses_and_results.harmonic_analyses_single_excitation import (
        _6430,
        _6448,
    )
    from mastapy._private.system_model.analyses_and_results.mbd_analyses import _5803
    from mastapy._private.system_model.analyses_and_results.modal_analyses import (
        _4947,
        _4978,
    )
    from mastapy._private.system_model.analyses_and_results.modal_analyses_at_a_speed import (
        _5527,
    )
    from mastapy._private.system_model.analyses_and_results.modal_analyses_at_a_stiffness import (
        _5236,
        _5264,
    )
    from mastapy._private.system_model.analyses_and_results.parametric_study_tools import (
        _4706,
        _4707,
    )
    from mastapy._private.system_model.analyses_and_results.power_flows import _4437
    from mastapy._private.system_model.analyses_and_results.stability_analyses import (
        _4125,
        _4181,
    )
    from mastapy._private.system_model.analyses_and_results.static_loads import (
        _7725,
        _7726,
        _7732,
        _7897,
    )
    from mastapy._private.system_model.analyses_and_results.steady_state_synchronous_responses import (
        _3332,
        _3388,
    )
    from mastapy._private.system_model.analyses_and_results.steady_state_synchronous_responses_at_a_speed import (
        _3916,
    )
    from mastapy._private.system_model.analyses_and_results.steady_state_synchronous_responses_on_a_shaft import (
        _3653,
    )
    from mastapy._private.system_model.analyses_and_results.system_deflections import (
        _3119,
        _3126,
    )
    from mastapy._private.utility import _1808

    Self = TypeVar("Self", bound="Context")
    CastSelf = TypeVar("CastSelf", bound="Context._Cast_Context")


__docformat__ = "restructuredtext en"
__all__ = ("Context",)


@extended_dataclass(frozen=True, slots=True, weakref_slot=True)
class _Cast_Context:
    """Special nested class for casting Context to subclasses."""

    __parent__: "Context"

    @property
    def system_deflection(self: "CastSelf") -> "_3119.SystemDeflection":
        from mastapy._private.system_model.analyses_and_results.system_deflections import (
            _3119,
        )

        return self.__parent__._cast(_3119.SystemDeflection)

    @property
    def torsional_system_deflection(
        self: "CastSelf",
    ) -> "_3126.TorsionalSystemDeflection":
        from mastapy._private.system_model.analyses_and_results.system_deflections import (
            _3126,
        )

        return self.__parent__._cast(_3126.TorsionalSystemDeflection)

    @property
    def dynamic_model_for_steady_state_synchronous_response(
        self: "CastSelf",
    ) -> "_3332.DynamicModelForSteadyStateSynchronousResponse":
        from mastapy._private.system_model.analyses_and_results.steady_state_synchronous_responses import (
            _3332,
        )

        return self.__parent__._cast(
            _3332.DynamicModelForSteadyStateSynchronousResponse
        )

    @property
    def steady_state_synchronous_response(
        self: "CastSelf",
    ) -> "_3388.SteadyStateSynchronousResponse":
        from mastapy._private.system_model.analyses_and_results.steady_state_synchronous_responses import (
            _3388,
        )

        return self.__parent__._cast(_3388.SteadyStateSynchronousResponse)

    @property
    def steady_state_synchronous_response_on_a_shaft(
        self: "CastSelf",
    ) -> "_3653.SteadyStateSynchronousResponseOnAShaft":
        from mastapy._private.system_model.analyses_and_results.steady_state_synchronous_responses_on_a_shaft import (
            _3653,
        )

        return self.__parent__._cast(_3653.SteadyStateSynchronousResponseOnAShaft)

    @property
    def steady_state_synchronous_response_at_a_speed(
        self: "CastSelf",
    ) -> "_3916.SteadyStateSynchronousResponseAtASpeed":
        from mastapy._private.system_model.analyses_and_results.steady_state_synchronous_responses_at_a_speed import (
            _3916,
        )

        return self.__parent__._cast(_3916.SteadyStateSynchronousResponseAtASpeed)

    @property
    def dynamic_model_for_stability_analysis(
        self: "CastSelf",
    ) -> "_4125.DynamicModelForStabilityAnalysis":
        from mastapy._private.system_model.analyses_and_results.stability_analyses import (
            _4125,
        )

        return self.__parent__._cast(_4125.DynamicModelForStabilityAnalysis)

    @property
    def stability_analysis(self: "CastSelf") -> "_4181.StabilityAnalysis":
        from mastapy._private.system_model.analyses_and_results.stability_analyses import (
            _4181,
        )

        return self.__parent__._cast(_4181.StabilityAnalysis)

    @property
    def power_flow(self: "CastSelf") -> "_4437.PowerFlow":
        from mastapy._private.system_model.analyses_and_results.power_flows import _4437

        return self.__parent__._cast(_4437.PowerFlow)

    @property
    def parametric_study_static_load(
        self: "CastSelf",
    ) -> "_4706.ParametricStudyStaticLoad":
        from mastapy._private.system_model.analyses_and_results.parametric_study_tools import (
            _4706,
        )

        return self.__parent__._cast(_4706.ParametricStudyStaticLoad)

    @property
    def parametric_study_tool(self: "CastSelf") -> "_4707.ParametricStudyTool":
        from mastapy._private.system_model.analyses_and_results.parametric_study_tools import (
            _4707,
        )

        return self.__parent__._cast(_4707.ParametricStudyTool)

    @property
    def dynamic_model_for_modal_analysis(
        self: "CastSelf",
    ) -> "_4947.DynamicModelForModalAnalysis":
        from mastapy._private.system_model.analyses_and_results.modal_analyses import (
            _4947,
        )

        return self.__parent__._cast(_4947.DynamicModelForModalAnalysis)

    @property
    def modal_analysis(self: "CastSelf") -> "_4978.ModalAnalysis":
        from mastapy._private.system_model.analyses_and_results.modal_analyses import (
            _4978,
        )

        return self.__parent__._cast(_4978.ModalAnalysis)

    @property
    def dynamic_model_at_a_stiffness(
        self: "CastSelf",
    ) -> "_5236.DynamicModelAtAStiffness":
        from mastapy._private.system_model.analyses_and_results.modal_analyses_at_a_stiffness import (
            _5236,
        )

        return self.__parent__._cast(_5236.DynamicModelAtAStiffness)

    @property
    def modal_analysis_at_a_stiffness(
        self: "CastSelf",
    ) -> "_5264.ModalAnalysisAtAStiffness":
        from mastapy._private.system_model.analyses_and_results.modal_analyses_at_a_stiffness import (
            _5264,
        )

        return self.__parent__._cast(_5264.ModalAnalysisAtAStiffness)

    @property
    def modal_analysis_at_a_speed(self: "CastSelf") -> "_5527.ModalAnalysisAtASpeed":
        from mastapy._private.system_model.analyses_and_results.modal_analyses_at_a_speed import (
            _5527,
        )

        return self.__parent__._cast(_5527.ModalAnalysisAtASpeed)

    @property
    def multibody_dynamics_analysis(
        self: "CastSelf",
    ) -> "_5803.MultibodyDynamicsAnalysis":
        from mastapy._private.system_model.analyses_and_results.mbd_analyses import (
            _5803,
        )

        return self.__parent__._cast(_5803.MultibodyDynamicsAnalysis)

    @property
    def dynamic_model_for_harmonic_analysis(
        self: "CastSelf",
    ) -> "_6075.DynamicModelForHarmonicAnalysis":
        from mastapy._private.system_model.analyses_and_results.harmonic_analyses import (
            _6075,
        )

        return self.__parent__._cast(_6075.DynamicModelForHarmonicAnalysis)

    @property
    def harmonic_analysis(self: "CastSelf") -> "_6104.HarmonicAnalysis":
        from mastapy._private.system_model.analyses_and_results.harmonic_analyses import (
            _6104,
        )

        return self.__parent__._cast(_6104.HarmonicAnalysis)

    @property
    def harmonic_analysis_for_advanced_time_stepping_analysis_for_modulation(
        self: "CastSelf",
    ) -> "_6109.HarmonicAnalysisForAdvancedTimeSteppingAnalysisForModulation":
        from mastapy._private.system_model.analyses_and_results.harmonic_analyses import (
            _6109,
        )

        return self.__parent__._cast(
            _6109.HarmonicAnalysisForAdvancedTimeSteppingAnalysisForModulation
        )

    @property
    def harmonic_analysis_with_varying_stiffness_static_load_case(
        self: "CastSelf",
    ) -> "_6115.HarmonicAnalysisWithVaryingStiffnessStaticLoadCase":
        from mastapy._private.system_model.analyses_and_results.harmonic_analyses import (
            _6115,
        )

        return self.__parent__._cast(
            _6115.HarmonicAnalysisWithVaryingStiffnessStaticLoadCase
        )

    @property
    def dynamic_model_for_transfer_path_analysis(
        self: "CastSelf",
    ) -> "_6192.DynamicModelForTransferPathAnalysis":
        from mastapy._private.system_model.analyses_and_results.harmonic_analyses.transfer_path_analyses import (
            _6192,
        )

        return self.__parent__._cast(_6192.DynamicModelForTransferPathAnalysis)

    @property
    def modal_analysis_for_transfer_path_analysis(
        self: "CastSelf",
    ) -> "_6193.ModalAnalysisForTransferPathAnalysis":
        from mastapy._private.system_model.analyses_and_results.harmonic_analyses.transfer_path_analyses import (
            _6193,
        )

        return self.__parent__._cast(_6193.ModalAnalysisForTransferPathAnalysis)

    @property
    def harmonic_analysis_of_single_excitation(
        self: "CastSelf",
    ) -> "_6430.HarmonicAnalysisOfSingleExcitation":
        from mastapy._private.system_model.analyses_and_results.harmonic_analyses_single_excitation import (
            _6430,
        )

        return self.__parent__._cast(_6430.HarmonicAnalysisOfSingleExcitation)

    @property
    def modal_analysis_for_harmonic_analysis(
        self: "CastSelf",
    ) -> "_6448.ModalAnalysisForHarmonicAnalysis":
        from mastapy._private.system_model.analyses_and_results.harmonic_analyses_single_excitation import (
            _6448,
        )

        return self.__parent__._cast(_6448.ModalAnalysisForHarmonicAnalysis)

    @property
    def dynamic_analysis(self: "CastSelf") -> "_6693.DynamicAnalysis":
        from mastapy._private.system_model.analyses_and_results.dynamic_analyses import (
            _6693,
        )

        return self.__parent__._cast(_6693.DynamicAnalysis)

    @property
    def critical_speed_analysis(self: "CastSelf") -> "_6951.CriticalSpeedAnalysis":
        from mastapy._private.system_model.analyses_and_results.critical_speed_analyses import (
            _6951,
        )

        return self.__parent__._cast(_6951.CriticalSpeedAnalysis)

    @property
    def advanced_time_stepping_analysis_for_modulation(
        self: "CastSelf",
    ) -> "_7180.AdvancedTimeSteppingAnalysisForModulation":
        from mastapy._private.system_model.analyses_and_results.advanced_time_stepping_analyses_for_modulation import (
            _7180,
        )

        return self.__parent__._cast(_7180.AdvancedTimeSteppingAnalysisForModulation)

    @property
    def advanced_system_deflection(
        self: "CastSelf",
    ) -> "_7448.AdvancedSystemDeflection":
        from mastapy._private.system_model.analyses_and_results.advanced_system_deflections import (
            _7448,
        )

        return self.__parent__._cast(_7448.AdvancedSystemDeflection)

    @property
    def advanced_system_deflection_sub_analysis(
        self: "CastSelf",
    ) -> "_7450.AdvancedSystemDeflectionSubAnalysis":
        from mastapy._private.system_model.analyses_and_results.advanced_system_deflections import (
            _7450,
        )

        return self.__parent__._cast(_7450.AdvancedSystemDeflectionSubAnalysis)

    @property
    def load_case(self: "CastSelf") -> "_7725.LoadCase":
        from mastapy._private.system_model.analyses_and_results.static_loads import (
            _7725,
        )

        return self.__parent__._cast(_7725.LoadCase)

    @property
    def static_load_case(self: "CastSelf") -> "_7726.StaticLoadCase":
        from mastapy._private.system_model.analyses_and_results.static_loads import (
            _7726,
        )

        return self.__parent__._cast(_7726.StaticLoadCase)

    @property
    def advanced_time_stepping_analysis_for_modulation_static_load_case(
        self: "CastSelf",
    ) -> "_7732.AdvancedTimeSteppingAnalysisForModulationStaticLoadCase":
        from mastapy._private.system_model.analyses_and_results.static_loads import (
            _7732,
        )

        return self.__parent__._cast(
            _7732.AdvancedTimeSteppingAnalysisForModulationStaticLoadCase
        )

    @property
    def time_series_load_case(self: "CastSelf") -> "_7897.TimeSeriesLoadCase":
        from mastapy._private.system_model.analyses_and_results.static_loads import (
            _7897,
        )

        return self.__parent__._cast(_7897.TimeSeriesLoadCase)

    @property
    def analysis_case(self: "CastSelf") -> "_7931.AnalysisCase":
        from mastapy._private.system_model.analyses_and_results.analysis_cases import (
            _7931,
        )

        return self.__parent__._cast(_7931.AnalysisCase)

    @property
    def compound_analysis_case(self: "CastSelf") -> "_7933.CompoundAnalysisCase":
        from mastapy._private.system_model.analyses_and_results.analysis_cases import (
            _7933,
        )

        return self.__parent__._cast(_7933.CompoundAnalysisCase)

    @property
    def fe_analysis(self: "CastSelf") -> "_7940.FEAnalysis":
        from mastapy._private.system_model.analyses_and_results.analysis_cases import (
            _7940,
        )

        return self.__parent__._cast(_7940.FEAnalysis)

    @property
    def static_load_analysis_case(self: "CastSelf") -> "_7946.StaticLoadAnalysisCase":
        from mastapy._private.system_model.analyses_and_results.analysis_cases import (
            _7946,
        )

        return self.__parent__._cast(_7946.StaticLoadAnalysisCase)

    @property
    def time_series_load_analysis_case(
        self: "CastSelf",
    ) -> "_7947.TimeSeriesLoadAnalysisCase":
        from mastapy._private.system_model.analyses_and_results.analysis_cases import (
            _7947,
        )

        return self.__parent__._cast(_7947.TimeSeriesLoadAnalysisCase)

    @property
    def context(self: "CastSelf") -> "Context":
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
class Context(_0.APIBase):
    """Context

    This is a mastapy class.
    """

    TYPE: ClassVar["Type"] = _CONTEXT

    wrapped: "Any"

    def __post_init__(self: "Self") -> None:
        """Override of the post initialisation magic method."""
        if not hasattr(self.wrapped, "reference_count"):
            self.wrapped.reference_count = 0

        self.wrapped.reference_count += 1

    @property
    @exception_bridge
    def comment(self: "Self") -> "str":
        """str"""
        temp = pythonnet_property_get(self.wrapped, "Comment")

        if temp is None:
            return ""

        return temp

    @comment.setter
    @exception_bridge
    @enforce_parameter_types
    def comment(self: "Self", value: "str") -> None:
        pythonnet_property_set(
            self.wrapped, "Comment", str(value) if value is not None else ""
        )

    @property
    @exception_bridge
    def name(self: "Self") -> "str":
        """str"""
        temp = pythonnet_property_get(self.wrapped, "Name")

        if temp is None:
            return ""

        return temp

    @name.setter
    @exception_bridge
    @enforce_parameter_types
    def name(self: "Self", value: "str") -> None:
        pythonnet_property_set(
            self.wrapped, "Name", str(value) if value is not None else ""
        )

    @property
    @exception_bridge
    def save_history_information(self: "Self") -> "_1808.FileHistoryItem":
        """mastapy.utility.FileHistoryItem

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "SaveHistoryInformation")

        if temp is None:
            return None

        type_ = temp.GetType()
        return constructor.new(type_.Namespace, type_.Name)(temp)

    @property
    @exception_bridge
    def design_properties(self: "Self") -> "_2448.Design":
        """mastapy.system_model.Design

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "DesignProperties")

        if temp is None:
            return None

        type_ = temp.GetType()
        return constructor.new(type_.Namespace, type_.Name)(temp)

    @property
    @exception_bridge
    def report_names(self: "Self") -> "List[str]":
        """List[str]

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "ReportNames")

        if temp is None:
            return None

        value = conversion.pn_to_mp_objects_in_list(temp, str)

        if value is None:
            return None

        return value

    @exception_bridge
    @enforce_parameter_types
    def output_default_report_to(self: "Self", file_path: "PathLike") -> None:
        """Method does not return.

        Args:
            file_path (PathLike)
        """
        file_path = str(file_path)
        pythonnet_method_call(self.wrapped, "OutputDefaultReportTo", file_path)

    @exception_bridge
    def get_default_report_with_encoded_images(self: "Self") -> "str":
        """str"""
        method_result = pythonnet_method_call(
            self.wrapped, "GetDefaultReportWithEncodedImages"
        )
        return method_result

    @exception_bridge
    @enforce_parameter_types
    def output_active_report_to(self: "Self", file_path: "PathLike") -> None:
        """Method does not return.

        Args:
            file_path (PathLike)
        """
        file_path = str(file_path)
        pythonnet_method_call(self.wrapped, "OutputActiveReportTo", file_path)

    @exception_bridge
    @enforce_parameter_types
    def output_active_report_as_text_to(self: "Self", file_path: "PathLike") -> None:
        """Method does not return.

        Args:
            file_path (PathLike)
        """
        file_path = str(file_path)
        pythonnet_method_call(self.wrapped, "OutputActiveReportAsTextTo", file_path)

    @exception_bridge
    def get_active_report_with_encoded_images(self: "Self") -> "str":
        """str"""
        method_result = pythonnet_method_call(
            self.wrapped, "GetActiveReportWithEncodedImages"
        )
        return method_result

    @exception_bridge
    @enforce_parameter_types
    def output_named_report_to(
        self: "Self", report_name: "str", file_path: "PathLike"
    ) -> None:
        """Method does not return.

        Args:
            report_name (str)
            file_path (PathLike)
        """
        report_name = str(report_name)
        file_path = str(file_path)
        pythonnet_method_call(
            self.wrapped,
            "OutputNamedReportTo",
            report_name if report_name else "",
            file_path,
        )

    @exception_bridge
    @enforce_parameter_types
    def output_named_report_as_masta_report(
        self: "Self", report_name: "str", file_path: "PathLike"
    ) -> None:
        """Method does not return.

        Args:
            report_name (str)
            file_path (PathLike)
        """
        report_name = str(report_name)
        file_path = str(file_path)
        pythonnet_method_call(
            self.wrapped,
            "OutputNamedReportAsMastaReport",
            report_name if report_name else "",
            file_path,
        )

    @exception_bridge
    @enforce_parameter_types
    def output_named_report_as_text_to(
        self: "Self", report_name: "str", file_path: "PathLike"
    ) -> None:
        """Method does not return.

        Args:
            report_name (str)
            file_path (PathLike)
        """
        report_name = str(report_name)
        file_path = str(file_path)
        pythonnet_method_call(
            self.wrapped,
            "OutputNamedReportAsTextTo",
            report_name if report_name else "",
            file_path,
        )

    @exception_bridge
    @enforce_parameter_types
    def get_named_report_with_encoded_images(self: "Self", report_name: "str") -> "str":
        """str

        Args:
            report_name (str)
        """
        report_name = str(report_name)
        method_result = pythonnet_method_call(
            self.wrapped,
            "GetNamedReportWithEncodedImages",
            report_name if report_name else "",
        )
        return method_result

    @property
    def cast_to(self: "Self") -> "_Cast_Context":
        """Cast to another type.

        Returns:
            _Cast_Context
        """
        return _Cast_Context(self)
