"""OrderForTE"""

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
from mastapy._private._internal import conversion, utility

_ORDER_FOR_TE = python_net_import(
    "SMT.MastaAPI.Utility.ModalAnalysis.Gears", "OrderForTE"
)

if TYPE_CHECKING:
    from typing import Any, List, Type, TypeVar

    from mastapy._private._internal.typing import PathLike

    from mastapy._private.utility.modal_analysis.gears import (
        _2026,
        _2027,
        _2029,
        _2030,
        _2032,
        _2033,
        _2034,
        _2035,
        _2036,
    )

    Self = TypeVar("Self", bound="OrderForTE")
    CastSelf = TypeVar("CastSelf", bound="OrderForTE._Cast_OrderForTE")


__docformat__ = "restructuredtext en"
__all__ = ("OrderForTE",)


@extended_dataclass(frozen=True, slots=True, weakref_slot=True)
class _Cast_OrderForTE:
    """Special nested class for casting OrderForTE to subclasses."""

    __parent__: "OrderForTE"

    @property
    def gear_mesh_for_te(self: "CastSelf") -> "_2026.GearMeshForTE":
        from mastapy._private.utility.modal_analysis.gears import _2026

        return self.__parent__._cast(_2026.GearMeshForTE)

    @property
    def gear_order_for_te(self: "CastSelf") -> "_2027.GearOrderForTE":
        from mastapy._private.utility.modal_analysis.gears import _2027

        return self.__parent__._cast(_2027.GearOrderForTE)

    @property
    def harmonic_order_for_te(self: "CastSelf") -> "_2029.HarmonicOrderForTE":
        from mastapy._private.utility.modal_analysis.gears import _2029

        return self.__parent__._cast(_2029.HarmonicOrderForTE)

    @property
    def label_only_order(self: "CastSelf") -> "_2030.LabelOnlyOrder":
        from mastapy._private.utility.modal_analysis.gears import _2030

        return self.__parent__._cast(_2030.LabelOnlyOrder)

    @property
    def order_selector(self: "CastSelf") -> "_2032.OrderSelector":
        from mastapy._private.utility.modal_analysis.gears import _2032

        return self.__parent__._cast(_2032.OrderSelector)

    @property
    def order_with_radius(self: "CastSelf") -> "_2033.OrderWithRadius":
        from mastapy._private.utility.modal_analysis.gears import _2033

        return self.__parent__._cast(_2033.OrderWithRadius)

    @property
    def rolling_bearing_order(self: "CastSelf") -> "_2034.RollingBearingOrder":
        from mastapy._private.utility.modal_analysis.gears import _2034

        return self.__parent__._cast(_2034.RollingBearingOrder)

    @property
    def shaft_order_for_te(self: "CastSelf") -> "_2035.ShaftOrderForTE":
        from mastapy._private.utility.modal_analysis.gears import _2035

        return self.__parent__._cast(_2035.ShaftOrderForTE)

    @property
    def user_defined_order_for_te(self: "CastSelf") -> "_2036.UserDefinedOrderForTE":
        from mastapy._private.utility.modal_analysis.gears import _2036

        return self.__parent__._cast(_2036.UserDefinedOrderForTE)

    @property
    def order_for_te(self: "CastSelf") -> "OrderForTE":
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
class OrderForTE(_0.APIBase):
    """OrderForTE

    This is a mastapy class.
    """

    TYPE: ClassVar["Type"] = _ORDER_FOR_TE

    wrapped: "Any"

    def __post_init__(self: "Self") -> None:
        """Override of the post initialisation magic method."""
        if not hasattr(self.wrapped, "reference_count"):
            self.wrapped.reference_count = 0

        self.wrapped.reference_count += 1

    @property
    @exception_bridge
    def frequency_offset(self: "Self") -> "float":
        """float"""
        temp = pythonnet_property_get(self.wrapped, "FrequencyOffset")

        if temp is None:
            return 0.0

        return temp

    @frequency_offset.setter
    @exception_bridge
    @enforce_parameter_types
    def frequency_offset(self: "Self", value: "float") -> None:
        pythonnet_property_set(
            self.wrapped, "FrequencyOffset", float(value) if value is not None else 0.0
        )

    @property
    @exception_bridge
    def name(self: "Self") -> "str":
        """str

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "Name")

        if temp is None:
            return ""

        return temp

    @property
    @exception_bridge
    def order(self: "Self") -> "float":
        """float

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "Order")

        if temp is None:
            return 0.0

        return temp

    @property
    @exception_bridge
    def children(self: "Self") -> "List[OrderForTE]":
        """List[mastapy.utility.modal_analysis.gears.OrderForTE]

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "Children")

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
    def cast_to(self: "Self") -> "_Cast_OrderForTE":
        """Cast to another type.

        Returns:
            _Cast_OrderForTE
        """
        return _Cast_OrderForTE(self)
