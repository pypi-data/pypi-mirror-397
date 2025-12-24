"""ProcessCalculation"""

from __future__ import annotations

from typing import TYPE_CHECKING, ClassVar

from mastapy._private._internal.dataclasses import extended_dataclass
from mastapy._private._internal.exception_bridge import exception_bridge
from mastapy._private._internal.exceptions import CastException
from mastapy._private._internal.python_net import (
    python_net_import,
    pythonnet_method_call,
    pythonnet_property_get,
)
from mastapy._private._internal.type_enforcement import enforce_parameter_types

from mastapy._private import _0
from mastapy._private._internal import constructor, conversion, utility

_PROCESS_CALCULATION = python_net_import(
    "SMT.MastaAPI.Gears.Manufacturing.Cylindrical.HobbingProcessSimulationNew",
    "ProcessCalculation",
)

if TYPE_CHECKING:
    from typing import Any, List, Type, TypeVar

    from mastapy._private._internal.typing import PathLike

    from mastapy._private.gears.manufacturing.cylindrical.hobbing_process_simulation_new import (
        _792,
        _793,
        _794,
        _795,
        _796,
        _797,
        _801,
        _811,
        _818,
        _819,
        _820,
        _821,
        _822,
        _823,
        _824,
        _828,
    )

    Self = TypeVar("Self", bound="ProcessCalculation")
    CastSelf = TypeVar("CastSelf", bound="ProcessCalculation._Cast_ProcessCalculation")


__docformat__ = "restructuredtext en"
__all__ = ("ProcessCalculation",)


@extended_dataclass(frozen=True, slots=True, weakref_slot=True)
class _Cast_ProcessCalculation:
    """Special nested class for casting ProcessCalculation to subclasses."""

    __parent__: "ProcessCalculation"

    @property
    def hobbing_process_calculation(
        self: "CastSelf",
    ) -> "_792.HobbingProcessCalculation":
        from mastapy._private.gears.manufacturing.cylindrical.hobbing_process_simulation_new import (
            _792,
        )

        return self.__parent__._cast(_792.HobbingProcessCalculation)

    @property
    def hobbing_process_gear_shape(self: "CastSelf") -> "_793.HobbingProcessGearShape":
        from mastapy._private.gears.manufacturing.cylindrical.hobbing_process_simulation_new import (
            _793,
        )

        return self.__parent__._cast(_793.HobbingProcessGearShape)

    @property
    def hobbing_process_lead_calculation(
        self: "CastSelf",
    ) -> "_794.HobbingProcessLeadCalculation":
        from mastapy._private.gears.manufacturing.cylindrical.hobbing_process_simulation_new import (
            _794,
        )

        return self.__parent__._cast(_794.HobbingProcessLeadCalculation)

    @property
    def hobbing_process_mark_on_shaft(
        self: "CastSelf",
    ) -> "_795.HobbingProcessMarkOnShaft":
        from mastapy._private.gears.manufacturing.cylindrical.hobbing_process_simulation_new import (
            _795,
        )

        return self.__parent__._cast(_795.HobbingProcessMarkOnShaft)

    @property
    def hobbing_process_pitch_calculation(
        self: "CastSelf",
    ) -> "_796.HobbingProcessPitchCalculation":
        from mastapy._private.gears.manufacturing.cylindrical.hobbing_process_simulation_new import (
            _796,
        )

        return self.__parent__._cast(_796.HobbingProcessPitchCalculation)

    @property
    def hobbing_process_profile_calculation(
        self: "CastSelf",
    ) -> "_797.HobbingProcessProfileCalculation":
        from mastapy._private.gears.manufacturing.cylindrical.hobbing_process_simulation_new import (
            _797,
        )

        return self.__parent__._cast(_797.HobbingProcessProfileCalculation)

    @property
    def hobbing_process_total_modification_calculation(
        self: "CastSelf",
    ) -> "_801.HobbingProcessTotalModificationCalculation":
        from mastapy._private.gears.manufacturing.cylindrical.hobbing_process_simulation_new import (
            _801,
        )

        return self.__parent__._cast(_801.HobbingProcessTotalModificationCalculation)

    @property
    def worm_grinding_cutter_calculation(
        self: "CastSelf",
    ) -> "_818.WormGrindingCutterCalculation":
        from mastapy._private.gears.manufacturing.cylindrical.hobbing_process_simulation_new import (
            _818,
        )

        return self.__parent__._cast(_818.WormGrindingCutterCalculation)

    @property
    def worm_grinding_lead_calculation(
        self: "CastSelf",
    ) -> "_819.WormGrindingLeadCalculation":
        from mastapy._private.gears.manufacturing.cylindrical.hobbing_process_simulation_new import (
            _819,
        )

        return self.__parent__._cast(_819.WormGrindingLeadCalculation)

    @property
    def worm_grinding_process_calculation(
        self: "CastSelf",
    ) -> "_820.WormGrindingProcessCalculation":
        from mastapy._private.gears.manufacturing.cylindrical.hobbing_process_simulation_new import (
            _820,
        )

        return self.__parent__._cast(_820.WormGrindingProcessCalculation)

    @property
    def worm_grinding_process_gear_shape(
        self: "CastSelf",
    ) -> "_821.WormGrindingProcessGearShape":
        from mastapy._private.gears.manufacturing.cylindrical.hobbing_process_simulation_new import (
            _821,
        )

        return self.__parent__._cast(_821.WormGrindingProcessGearShape)

    @property
    def worm_grinding_process_mark_on_shaft(
        self: "CastSelf",
    ) -> "_822.WormGrindingProcessMarkOnShaft":
        from mastapy._private.gears.manufacturing.cylindrical.hobbing_process_simulation_new import (
            _822,
        )

        return self.__parent__._cast(_822.WormGrindingProcessMarkOnShaft)

    @property
    def worm_grinding_process_pitch_calculation(
        self: "CastSelf",
    ) -> "_823.WormGrindingProcessPitchCalculation":
        from mastapy._private.gears.manufacturing.cylindrical.hobbing_process_simulation_new import (
            _823,
        )

        return self.__parent__._cast(_823.WormGrindingProcessPitchCalculation)

    @property
    def worm_grinding_process_profile_calculation(
        self: "CastSelf",
    ) -> "_824.WormGrindingProcessProfileCalculation":
        from mastapy._private.gears.manufacturing.cylindrical.hobbing_process_simulation_new import (
            _824,
        )

        return self.__parent__._cast(_824.WormGrindingProcessProfileCalculation)

    @property
    def worm_grinding_process_total_modification_calculation(
        self: "CastSelf",
    ) -> "_828.WormGrindingProcessTotalModificationCalculation":
        from mastapy._private.gears.manufacturing.cylindrical.hobbing_process_simulation_new import (
            _828,
        )

        return self.__parent__._cast(
            _828.WormGrindingProcessTotalModificationCalculation
        )

    @property
    def process_calculation(self: "CastSelf") -> "ProcessCalculation":
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
class ProcessCalculation(_0.APIBase):
    """ProcessCalculation

    This is a mastapy class.
    """

    TYPE: ClassVar["Type"] = _PROCESS_CALCULATION

    wrapped: "Any"

    def __post_init__(self: "Self") -> None:
        """Override of the post initialisation magic method."""
        if not hasattr(self.wrapped, "reference_count"):
            self.wrapped.reference_count = 0

        self.wrapped.reference_count += 1

    @property
    @exception_bridge
    def centre_distance(self: "Self") -> "float":
        """float

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "CentreDistance")

        if temp is None:
            return 0.0

        return temp

    @property
    @exception_bridge
    def centre_distance_parabolic_parameter(self: "Self") -> "float":
        """float

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "CentreDistanceParabolicParameter")

        if temp is None:
            return 0.0

        return temp

    @property
    @exception_bridge
    def cutter_gear_rotation_ratio(self: "Self") -> "float":
        """float

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "CutterGearRotationRatio")

        if temp is None:
            return 0.0

        return temp

    @property
    @exception_bridge
    def cutter_minimum_effective_length(self: "Self") -> "float":
        """float

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "CutterMinimumEffectiveLength")

        if temp is None:
            return 0.0

        return temp

    @property
    @exception_bridge
    def idle_distance(self: "Self") -> "float":
        """float

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "IdleDistance")

        if temp is None:
            return 0.0

        return temp

    @property
    @exception_bridge
    def minimum_allowable_neck_width(self: "Self") -> "float":
        """float

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "MinimumAllowableNeckWidth")

        if temp is None:
            return 0.0

        return temp

    @property
    @exception_bridge
    def neck_width(self: "Self") -> "float":
        """float

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "NeckWidth")

        if temp is None:
            return 0.0

        return temp

    @property
    @exception_bridge
    def setting_angle(self: "Self") -> "float":
        """float

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "SettingAngle")

        if temp is None:
            return 0.0

        return temp

    @property
    @exception_bridge
    def shaft_angle(self: "Self") -> "float":
        """float

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "ShaftAngle")

        if temp is None:
            return 0.0

        return temp

    @property
    @exception_bridge
    def shaft_mark_length(self: "Self") -> "float":
        """float

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "ShaftMarkLength")

        if temp is None:
            return 0.0

        return temp

    @property
    @exception_bridge
    def inputs(self: "Self") -> "_811.ProcessSimulationInput":
        """mastapy.gears.manufacturing.cylindrical.hobbing_process_simulation_new.ProcessSimulationInput

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "Inputs")

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
    def calculate_idle_distance(self: "Self") -> None:
        """Method does not return."""
        pythonnet_method_call(self.wrapped, "CalculateIdleDistance")

    @exception_bridge
    def calculate_left_modifications(self: "Self") -> None:
        """Method does not return."""
        pythonnet_method_call(self.wrapped, "CalculateLeftModifications")

    @exception_bridge
    def calculate_left_total_modifications(self: "Self") -> None:
        """Method does not return."""
        pythonnet_method_call(self.wrapped, "CalculateLeftTotalModifications")

    @exception_bridge
    def calculate_maximum_shaft_mark_length(self: "Self") -> None:
        """Method does not return."""
        pythonnet_method_call(self.wrapped, "CalculateMaximumShaftMarkLength")

    @exception_bridge
    def calculate_modifications(self: "Self") -> None:
        """Method does not return."""
        pythonnet_method_call(self.wrapped, "CalculateModifications")

    @exception_bridge
    def calculate_right_modifications(self: "Self") -> None:
        """Method does not return."""
        pythonnet_method_call(self.wrapped, "CalculateRightModifications")

    @exception_bridge
    def calculate_right_total_modifications(self: "Self") -> None:
        """Method does not return."""
        pythonnet_method_call(self.wrapped, "CalculateRightTotalModifications")

    @exception_bridge
    def calculate_shaft_mark(self: "Self") -> None:
        """Method does not return."""
        pythonnet_method_call(self.wrapped, "CalculateShaftMark")

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
    def cast_to(self: "Self") -> "_Cast_ProcessCalculation":
        """Cast to another type.

        Returns:
            _Cast_ProcessCalculation
        """
        return _Cast_ProcessCalculation(self)
