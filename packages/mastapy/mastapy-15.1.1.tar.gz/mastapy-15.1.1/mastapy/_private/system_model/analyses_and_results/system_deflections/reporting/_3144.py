"""ShaftSystemDeflectionSectionsReport"""

from __future__ import annotations

from typing import TYPE_CHECKING, ClassVar

from mastapy._private._internal.dataclasses import extended_dataclass
from mastapy._private._internal.exception_bridge import exception_bridge
from mastapy._private._internal.exceptions import CastException
from mastapy._private._internal.python_net import (
    python_net_import,
    pythonnet_property_get,
    pythonnet_property_set,
)
from mastapy._private._internal.type_enforcement import enforce_parameter_types

from mastapy._private._internal import constructor, conversion, utility
from mastapy._private.utility.report import _1983

_SHAFT_SYSTEM_DEFLECTION_SECTIONS_REPORT = python_net_import(
    "SMT.MastaAPI.SystemModel.AnalysesAndResults.SystemDeflections.Reporting",
    "ShaftSystemDeflectionSectionsReport",
)

if TYPE_CHECKING:
    from typing import Any, Type, TypeVar

    from mastapy._private.utility.enums import _2051
    from mastapy._private.utility.report import _1990, _1996, _1997, _1998

    Self = TypeVar("Self", bound="ShaftSystemDeflectionSectionsReport")
    CastSelf = TypeVar(
        "CastSelf",
        bound="ShaftSystemDeflectionSectionsReport._Cast_ShaftSystemDeflectionSectionsReport",
    )


__docformat__ = "restructuredtext en"
__all__ = ("ShaftSystemDeflectionSectionsReport",)


@extended_dataclass(frozen=True, slots=True, weakref_slot=True)
class _Cast_ShaftSystemDeflectionSectionsReport:
    """Special nested class for casting ShaftSystemDeflectionSectionsReport to subclasses."""

    __parent__: "ShaftSystemDeflectionSectionsReport"

    @property
    def custom_report_chart(self: "CastSelf") -> "_1983.CustomReportChart":
        return self.__parent__._cast(_1983.CustomReportChart)

    @property
    def custom_report_multi_property_item(
        self: "CastSelf",
    ) -> "_1996.CustomReportMultiPropertyItem":
        pass

        from mastapy._private.utility.report import _1996

        return self.__parent__._cast(_1996.CustomReportMultiPropertyItem)

    @property
    def custom_report_multi_property_item_base(
        self: "CastSelf",
    ) -> "_1997.CustomReportMultiPropertyItemBase":
        from mastapy._private.utility.report import _1997

        return self.__parent__._cast(_1997.CustomReportMultiPropertyItemBase)

    @property
    def custom_report_nameable_item(
        self: "CastSelf",
    ) -> "_1998.CustomReportNameableItem":
        from mastapy._private.utility.report import _1998

        return self.__parent__._cast(_1998.CustomReportNameableItem)

    @property
    def custom_report_item(self: "CastSelf") -> "_1990.CustomReportItem":
        from mastapy._private.utility.report import _1990

        return self.__parent__._cast(_1990.CustomReportItem)

    @property
    def shaft_system_deflection_sections_report(
        self: "CastSelf",
    ) -> "ShaftSystemDeflectionSectionsReport":
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
class ShaftSystemDeflectionSectionsReport(_1983.CustomReportChart):
    """ShaftSystemDeflectionSectionsReport

    This is a mastapy class.
    """

    TYPE: ClassVar["Type"] = _SHAFT_SYSTEM_DEFLECTION_SECTIONS_REPORT

    wrapped: "Any"

    def __post_init__(self: "Self") -> None:
        """Override of the post initialisation magic method."""
        if not hasattr(self.wrapped, "reference_count"):
            self.wrapped.reference_count = 0

        self.wrapped.reference_count += 1

    @property
    @exception_bridge
    def display(self: "Self") -> "_2051.TableAndChartOptions":
        """mastapy.utility.enums.TableAndChartOptions"""
        temp = pythonnet_property_get(self.wrapped, "Display")

        if temp is None:
            return None

        value = conversion.pn_to_mp_enum(
            temp, "SMT.MastaAPI.Utility.Enums.TableAndChartOptions"
        )

        if value is None:
            return None

        return constructor.new_from_mastapy(
            "mastapy._private.utility.enums._2051", "TableAndChartOptions"
        )(value)

    @display.setter
    @exception_bridge
    @enforce_parameter_types
    def display(self: "Self", value: "_2051.TableAndChartOptions") -> None:
        value = conversion.mp_to_pn_enum(
            value, "SMT.MastaAPI.Utility.Enums.TableAndChartOptions"
        )
        pythonnet_property_set(self.wrapped, "Display", value)

    @property
    def cast_to(self: "Self") -> "_Cast_ShaftSystemDeflectionSectionsReport":
        """Cast to another type.

        Returns:
            _Cast_ShaftSystemDeflectionSectionsReport
        """
        return _Cast_ShaftSystemDeflectionSectionsReport(self)
