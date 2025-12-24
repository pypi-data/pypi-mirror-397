"""ElectricMachineLoadCaseBase"""

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

_ELECTRIC_MACHINE_LOAD_CASE_BASE = python_net_import(
    "SMT.MastaAPI.ElectricMachines.LoadCasesAndAnalyses", "ElectricMachineLoadCaseBase"
)

if TYPE_CHECKING:
    from typing import Any, List, Type, TypeVar

    from mastapy._private._internal.typing import PathLike

    from mastapy._private.electric_machines import _1420
    from mastapy._private.electric_machines.load_cases_and_analyses import (
        _1557,
        _1559,
        _1562,
        _1563,
        _1569,
        _1571,
        _1572,
        _1578,
        _1586,
        _1587,
        _1588,
    )

    Self = TypeVar("Self", bound="ElectricMachineLoadCaseBase")
    CastSelf = TypeVar(
        "CastSelf",
        bound="ElectricMachineLoadCaseBase._Cast_ElectricMachineLoadCaseBase",
    )


__docformat__ = "restructuredtext en"
__all__ = ("ElectricMachineLoadCaseBase",)


@extended_dataclass(frozen=True, slots=True, weakref_slot=True)
class _Cast_ElectricMachineLoadCaseBase:
    """Special nested class for casting ElectricMachineLoadCaseBase to subclasses."""

    __parent__: "ElectricMachineLoadCaseBase"

    @property
    def basic_dynamic_force_load_case(
        self: "CastSelf",
    ) -> "_1557.BasicDynamicForceLoadCase":
        from mastapy._private.electric_machines.load_cases_and_analyses import _1557

        return self.__parent__._cast(_1557.BasicDynamicForceLoadCase)

    @property
    def dynamic_force_load_case(self: "CastSelf") -> "_1559.DynamicForceLoadCase":
        from mastapy._private.electric_machines.load_cases_and_analyses import _1559

        return self.__parent__._cast(_1559.DynamicForceLoadCase)

    @property
    def efficiency_map_load_case(self: "CastSelf") -> "_1562.EfficiencyMapLoadCase":
        from mastapy._private.electric_machines.load_cases_and_analyses import _1562

        return self.__parent__._cast(_1562.EfficiencyMapLoadCase)

    @property
    def electric_machine_load_case(self: "CastSelf") -> "_1569.ElectricMachineLoadCase":
        from mastapy._private.electric_machines.load_cases_and_analyses import _1569

        return self.__parent__._cast(_1569.ElectricMachineLoadCase)

    @property
    def electric_machine_mechanical_load_case(
        self: "CastSelf",
    ) -> "_1572.ElectricMachineMechanicalLoadCase":
        from mastapy._private.electric_machines.load_cases_and_analyses import _1572

        return self.__parent__._cast(_1572.ElectricMachineMechanicalLoadCase)

    @property
    def non_linear_dq_model_multiple_operating_points_load_case(
        self: "CastSelf",
    ) -> "_1578.NonLinearDQModelMultipleOperatingPointsLoadCase":
        from mastapy._private.electric_machines.load_cases_and_analyses import _1578

        return self.__parent__._cast(
            _1578.NonLinearDQModelMultipleOperatingPointsLoadCase
        )

    @property
    def speed_torque_curve_load_case(
        self: "CastSelf",
    ) -> "_1586.SpeedTorqueCurveLoadCase":
        from mastapy._private.electric_machines.load_cases_and_analyses import _1586

        return self.__parent__._cast(_1586.SpeedTorqueCurveLoadCase)

    @property
    def speed_torque_load_case(self: "CastSelf") -> "_1587.SpeedTorqueLoadCase":
        from mastapy._private.electric_machines.load_cases_and_analyses import _1587

        return self.__parent__._cast(_1587.SpeedTorqueLoadCase)

    @property
    def electric_machine_load_case_base(
        self: "CastSelf",
    ) -> "ElectricMachineLoadCaseBase":
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
class ElectricMachineLoadCaseBase(_0.APIBase):
    """ElectricMachineLoadCaseBase

    This is a mastapy class.
    """

    TYPE: ClassVar["Type"] = _ELECTRIC_MACHINE_LOAD_CASE_BASE

    wrapped: "Any"

    def __post_init__(self: "Self") -> None:
        """Override of the post initialisation magic method."""
        if not hasattr(self.wrapped, "reference_count"):
            self.wrapped.reference_count = 0

        self.wrapped.reference_count += 1

    @property
    @exception_bridge
    def folder_path(self: "Self") -> "str":
        """str

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "FolderPath")

        if temp is None:
            return ""

        return temp

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
    def temperatures(self: "Self") -> "_1588.Temperatures":
        """mastapy.electric_machines.load_cases_and_analyses.Temperatures

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "Temperatures")

        if temp is None:
            return None

        type_ = temp.GetType()
        return constructor.new(type_.Namespace, type_.Name)(temp)

    @property
    @exception_bridge
    def analyses(self: "Self") -> "List[_1563.ElectricMachineAnalysis]":
        """List[mastapy.electric_machines.load_cases_and_analyses.ElectricMachineAnalysis]

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "Analyses")

        if temp is None:
            return None

        value = conversion.pn_to_mp_objects_in_list(temp)

        if value is None:
            return None

        return value

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
    def edit_folder_path(self: "Self") -> None:
        """Method does not return."""
        pythonnet_method_call(self.wrapped, "EditFolderPath")

    @exception_bridge
    @enforce_parameter_types
    def analysis_for(
        self: "Self", setup: "_1420.ElectricMachineSetup"
    ) -> "_1563.ElectricMachineAnalysis":
        """mastapy.electric_machines.load_cases_and_analyses.ElectricMachineAnalysis

        Args:
            setup (mastapy.electric_machines.ElectricMachineSetup)
        """
        method_result = pythonnet_method_call(
            self.wrapped, "AnalysisFor", setup.wrapped if setup else None
        )
        type_ = method_result.GetType()
        return (
            constructor.new(type_.Namespace, type_.Name)(method_result)
            if method_result is not None
            else None
        )

    @exception_bridge
    @enforce_parameter_types
    def copy_to(
        self: "Self", another_group: "_1571.ElectricMachineLoadCaseGroup"
    ) -> "ElectricMachineLoadCaseBase":
        """mastapy.electric_machines.load_cases_and_analyses.ElectricMachineLoadCaseBase

        Args:
            another_group (mastapy.electric_machines.load_cases_and_analyses.ElectricMachineLoadCaseGroup)
        """
        method_result = pythonnet_method_call(
            self.wrapped, "CopyTo", another_group.wrapped if another_group else None
        )
        type_ = method_result.GetType()
        return (
            constructor.new(type_.Namespace, type_.Name)(method_result)
            if method_result is not None
            else None
        )

    @exception_bridge
    @enforce_parameter_types
    def remove_analysis(
        self: "Self", electric_machine_analysis: "_1563.ElectricMachineAnalysis"
    ) -> None:
        """Method does not return.

        Args:
            electric_machine_analysis (mastapy.electric_machines.load_cases_and_analyses.ElectricMachineAnalysis)
        """
        pythonnet_method_call(
            self.wrapped,
            "RemoveAnalysis",
            electric_machine_analysis.wrapped if electric_machine_analysis else None,
        )

    @exception_bridge
    @enforce_parameter_types
    def remove_analysis_for(self: "Self", setup: "_1420.ElectricMachineSetup") -> None:
        """Method does not return.

        Args:
            setup (mastapy.electric_machines.ElectricMachineSetup)
        """
        pythonnet_method_call(
            self.wrapped, "RemoveAnalysisFor", setup.wrapped if setup else None
        )

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
    def cast_to(self: "Self") -> "_Cast_ElectricMachineLoadCaseBase":
        """Cast to another type.

        Returns:
            _Cast_ElectricMachineLoadCaseBase
        """
        return _Cast_ElectricMachineLoadCaseBase(self)
