"""BaffleLoss"""

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

from mastapy._private._internal import conversion, utility
from mastapy._private.utility import _1811

_BAFFLE_LOSS = python_net_import("SMT.MastaAPI.Materials.Efficiency", "BaffleLoss")

if TYPE_CHECKING:
    from typing import Any, List, Type, TypeVar

    from mastapy._private._internal.typing import PathLike

    Self = TypeVar("Self", bound="BaffleLoss")
    CastSelf = TypeVar("CastSelf", bound="BaffleLoss._Cast_BaffleLoss")


__docformat__ = "restructuredtext en"
__all__ = ("BaffleLoss",)


@extended_dataclass(frozen=True, slots=True, weakref_slot=True)
class _Cast_BaffleLoss:
    """Special nested class for casting BaffleLoss to subclasses."""

    __parent__: "BaffleLoss"

    @property
    def independent_reportable_properties_base(
        self: "CastSelf",
    ) -> "_1811.IndependentReportablePropertiesBase":
        pass

        return self.__parent__._cast(_1811.IndependentReportablePropertiesBase)

    @property
    def baffle_loss(self: "CastSelf") -> "BaffleLoss":
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
class BaffleLoss(_1811.IndependentReportablePropertiesBase["BaffleLoss"]):
    """BaffleLoss

    This is a mastapy class.
    """

    TYPE: ClassVar["Type"] = _BAFFLE_LOSS

    wrapped: "Any"

    def __post_init__(self: "Self") -> None:
        """Override of the post initialisation magic method."""
        if not hasattr(self.wrapped, "reference_count"):
            self.wrapped.reference_count = 0

        self.wrapped.reference_count += 1

    @property
    @exception_bridge
    def baffle_loss_factor(self: "Self") -> "float":
        """float"""
        temp = pythonnet_property_get(self.wrapped, "BaffleLossFactor")

        if temp is None:
            return 0.0

        return temp

    @baffle_loss_factor.setter
    @exception_bridge
    @enforce_parameter_types
    def baffle_loss_factor(self: "Self", value: "float") -> None:
        pythonnet_property_set(
            self.wrapped, "BaffleLossFactor", float(value) if value is not None else 0.0
        )

    @property
    @exception_bridge
    def baffle_type(self: "Self") -> "str":
        """str"""
        temp = pythonnet_property_get(self.wrapped, "BaffleType")

        if temp is None:
            return ""

        return temp

    @baffle_type.setter
    @exception_bridge
    @enforce_parameter_types
    def baffle_type(self: "Self", value: "str") -> None:
        pythonnet_property_set(
            self.wrapped, "BaffleType", str(value) if value is not None else ""
        )

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
    def cast_to(self: "Self") -> "_Cast_BaffleLoss":
        """Cast to another type.

        Returns:
            _Cast_BaffleLoss
        """
        return _Cast_BaffleLoss(self)
