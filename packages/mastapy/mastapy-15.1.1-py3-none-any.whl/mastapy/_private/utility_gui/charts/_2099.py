"""ScatterChartDefinition"""

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
from mastapy._private.utility_gui.charts import _2104

_SCATTER_CHART_DEFINITION = python_net_import(
    "SMT.MastaAPI.UtilityGUI.Charts", "ScatterChartDefinition"
)

if TYPE_CHECKING:
    from typing import Any, List, Type, TypeVar

    from mastapy._private.utility.report import _1975
    from mastapy._private.utility_gui.charts import _2089, _2096

    Self = TypeVar("Self", bound="ScatterChartDefinition")
    CastSelf = TypeVar(
        "CastSelf", bound="ScatterChartDefinition._Cast_ScatterChartDefinition"
    )


__docformat__ = "restructuredtext en"
__all__ = ("ScatterChartDefinition",)


@extended_dataclass(frozen=True, slots=True, weakref_slot=True)
class _Cast_ScatterChartDefinition:
    """Special nested class for casting ScatterChartDefinition to subclasses."""

    __parent__: "ScatterChartDefinition"

    @property
    def two_d_chart_definition(self: "CastSelf") -> "_2104.TwoDChartDefinition":
        return self.__parent__._cast(_2104.TwoDChartDefinition)

    @property
    def nd_chart_definition(self: "CastSelf") -> "_2096.NDChartDefinition":
        from mastapy._private.utility_gui.charts import _2096

        return self.__parent__._cast(_2096.NDChartDefinition)

    @property
    def chart_definition(self: "CastSelf") -> "_1975.ChartDefinition":
        from mastapy._private.utility.report import _1975

        return self.__parent__._cast(_1975.ChartDefinition)

    @property
    def bubble_chart_definition(self: "CastSelf") -> "_2089.BubbleChartDefinition":
        from mastapy._private.utility_gui.charts import _2089

        return self.__parent__._cast(_2089.BubbleChartDefinition)

    @property
    def scatter_chart_definition(self: "CastSelf") -> "ScatterChartDefinition":
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
class ScatterChartDefinition(_2104.TwoDChartDefinition):
    """ScatterChartDefinition

    This is a mastapy class.
    """

    TYPE: ClassVar["Type"] = _SCATTER_CHART_DEFINITION

    wrapped: "Any"

    def __post_init__(self: "Self") -> None:
        """Override of the post initialisation magic method."""
        if not hasattr(self.wrapped, "reference_count"):
            self.wrapped.reference_count = 0

        self.wrapped.reference_count += 1

    @property
    @exception_bridge
    def x_values(self: "Self") -> "List[float]":
        """List[float]

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "XValues")

        if temp is None:
            return None

        value = conversion.to_list_any(temp)

        if value is None:
            return None

        return value

    @property
    @exception_bridge
    def y_values(self: "Self") -> "List[float]":
        """List[float]

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "YValues")

        if temp is None:
            return None

        value = conversion.to_list_any(temp)

        if value is None:
            return None

        return value

    @property
    @exception_bridge
    def z_values(self: "Self") -> "List[float]":
        """List[float]

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "ZValues")

        if temp is None:
            return None

        value = conversion.to_list_any(temp)

        if value is None:
            return None

        return value

    @property
    def cast_to(self: "Self") -> "_Cast_ScatterChartDefinition":
        """Cast to another type.

        Returns:
            _Cast_ScatterChartDefinition
        """
        return _Cast_ScatterChartDefinition(self)
