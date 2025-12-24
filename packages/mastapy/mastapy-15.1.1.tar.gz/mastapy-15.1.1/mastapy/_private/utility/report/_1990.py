"""CustomReportItem"""

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
from mastapy._private._internal import utility

_CUSTOM_REPORT_ITEM = python_net_import(
    "SMT.MastaAPI.Utility.Report", "CustomReportItem"
)

if TYPE_CHECKING:
    from typing import Any, Type, TypeVar

    from mastapy._private.bearings.bearing_results import _2186, _2187, _2190, _2198
    from mastapy._private.gears.gear_designs.cylindrical import _1167
    from mastapy._private.shafts import _20
    from mastapy._private.system_model.analyses_and_results.modal_analyses.reporting import (
        _5042,
        _5046,
    )
    from mastapy._private.system_model.analyses_and_results.parametric_study_tools import (
        _4705,
    )
    from mastapy._private.system_model.analyses_and_results.system_deflections.reporting import (
        _3144,
    )
    from mastapy._private.utility.report import (
        _1969,
        _1977,
        _1978,
        _1979,
        _1980,
        _1981,
        _1982,
        _1983,
        _1985,
        _1986,
        _1987,
        _1988,
        _1989,
        _1991,
        _1992,
        _1993,
        _1994,
        _1996,
        _1997,
        _1998,
        _1999,
        _2001,
        _2002,
        _2003,
        _2004,
        _2006,
        _2007,
        _2009,
    )
    from mastapy._private.utility_gui.charts import _2091, _2092

    Self = TypeVar("Self", bound="CustomReportItem")
    CastSelf = TypeVar("CastSelf", bound="CustomReportItem._Cast_CustomReportItem")


__docformat__ = "restructuredtext en"
__all__ = ("CustomReportItem",)


@extended_dataclass(frozen=True, slots=True, weakref_slot=True)
class _Cast_CustomReportItem:
    """Special nested class for casting CustomReportItem to subclasses."""

    __parent__: "CustomReportItem"

    @property
    def shaft_damage_results_table_and_chart(
        self: "CastSelf",
    ) -> "_20.ShaftDamageResultsTableAndChart":
        from mastapy._private.shafts import _20

        return self.__parent__._cast(_20.ShaftDamageResultsTableAndChart)

    @property
    def cylindrical_gear_table_with_mg_charts(
        self: "CastSelf",
    ) -> "_1167.CylindricalGearTableWithMGCharts":
        from mastapy._private.gears.gear_designs.cylindrical import _1167

        return self.__parent__._cast(_1167.CylindricalGearTableWithMGCharts)

    @property
    def ad_hoc_custom_table(self: "CastSelf") -> "_1969.AdHocCustomTable":
        from mastapy._private.utility.report import _1969

        return self.__parent__._cast(_1969.AdHocCustomTable)

    @property
    def custom_chart(self: "CastSelf") -> "_1977.CustomChart":
        from mastapy._private.utility.report import _1977

        return self.__parent__._cast(_1977.CustomChart)

    @property
    def custom_drawing(self: "CastSelf") -> "_1978.CustomDrawing":
        from mastapy._private.utility.report import _1978

        return self.__parent__._cast(_1978.CustomDrawing)

    @property
    def custom_graphic(self: "CastSelf") -> "_1979.CustomGraphic":
        from mastapy._private.utility.report import _1979

        return self.__parent__._cast(_1979.CustomGraphic)

    @property
    def custom_image(self: "CastSelf") -> "_1980.CustomImage":
        from mastapy._private.utility.report import _1980

        return self.__parent__._cast(_1980.CustomImage)

    @property
    def custom_report(self: "CastSelf") -> "_1981.CustomReport":
        from mastapy._private.utility.report import _1981

        return self.__parent__._cast(_1981.CustomReport)

    @property
    def custom_report_cad_drawing(self: "CastSelf") -> "_1982.CustomReportCadDrawing":
        from mastapy._private.utility.report import _1982

        return self.__parent__._cast(_1982.CustomReportCadDrawing)

    @property
    def custom_report_chart(self: "CastSelf") -> "_1983.CustomReportChart":
        from mastapy._private.utility.report import _1983

        return self.__parent__._cast(_1983.CustomReportChart)

    @property
    def custom_report_column(self: "CastSelf") -> "_1985.CustomReportColumn":
        from mastapy._private.utility.report import _1985

        return self.__parent__._cast(_1985.CustomReportColumn)

    @property
    def custom_report_columns(self: "CastSelf") -> "_1986.CustomReportColumns":
        from mastapy._private.utility.report import _1986

        return self.__parent__._cast(_1986.CustomReportColumns)

    @property
    def custom_report_definition_item(
        self: "CastSelf",
    ) -> "_1987.CustomReportDefinitionItem":
        from mastapy._private.utility.report import _1987

        return self.__parent__._cast(_1987.CustomReportDefinitionItem)

    @property
    def custom_report_horizontal_line(
        self: "CastSelf",
    ) -> "_1988.CustomReportHorizontalLine":
        from mastapy._private.utility.report import _1988

        return self.__parent__._cast(_1988.CustomReportHorizontalLine)

    @property
    def custom_report_html_item(self: "CastSelf") -> "_1989.CustomReportHtmlItem":
        from mastapy._private.utility.report import _1989

        return self.__parent__._cast(_1989.CustomReportHtmlItem)

    @property
    def custom_report_item_container(
        self: "CastSelf",
    ) -> "_1991.CustomReportItemContainer":
        from mastapy._private.utility.report import _1991

        return self.__parent__._cast(_1991.CustomReportItemContainer)

    @property
    def custom_report_item_container_collection(
        self: "CastSelf",
    ) -> "_1992.CustomReportItemContainerCollection":
        from mastapy._private.utility.report import _1992

        return self.__parent__._cast(_1992.CustomReportItemContainerCollection)

    @property
    def custom_report_item_container_collection_base(
        self: "CastSelf",
    ) -> "_1993.CustomReportItemContainerCollectionBase":
        from mastapy._private.utility.report import _1993

        return self.__parent__._cast(_1993.CustomReportItemContainerCollectionBase)

    @property
    def custom_report_item_container_collection_item(
        self: "CastSelf",
    ) -> "_1994.CustomReportItemContainerCollectionItem":
        from mastapy._private.utility.report import _1994

        return self.__parent__._cast(_1994.CustomReportItemContainerCollectionItem)

    @property
    def custom_report_multi_property_item(
        self: "CastSelf",
    ) -> "_1996.CustomReportMultiPropertyItem":
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
    def custom_report_named_item(self: "CastSelf") -> "_1999.CustomReportNamedItem":
        from mastapy._private.utility.report import _1999

        return self.__parent__._cast(_1999.CustomReportNamedItem)

    @property
    def custom_report_status_item(self: "CastSelf") -> "_2001.CustomReportStatusItem":
        from mastapy._private.utility.report import _2001

        return self.__parent__._cast(_2001.CustomReportStatusItem)

    @property
    def custom_report_tab(self: "CastSelf") -> "_2002.CustomReportTab":
        from mastapy._private.utility.report import _2002

        return self.__parent__._cast(_2002.CustomReportTab)

    @property
    def custom_report_tabs(self: "CastSelf") -> "_2003.CustomReportTabs":
        from mastapy._private.utility.report import _2003

        return self.__parent__._cast(_2003.CustomReportTabs)

    @property
    def custom_report_text(self: "CastSelf") -> "_2004.CustomReportText":
        from mastapy._private.utility.report import _2004

        return self.__parent__._cast(_2004.CustomReportText)

    @property
    def custom_sub_report(self: "CastSelf") -> "_2006.CustomSubReport":
        from mastapy._private.utility.report import _2006

        return self.__parent__._cast(_2006.CustomSubReport)

    @property
    def custom_table(self: "CastSelf") -> "_2007.CustomTable":
        from mastapy._private.utility.report import _2007

        return self.__parent__._cast(_2007.CustomTable)

    @property
    def dynamic_custom_report_item(self: "CastSelf") -> "_2009.DynamicCustomReportItem":
        from mastapy._private.utility.report import _2009

        return self.__parent__._cast(_2009.DynamicCustomReportItem)

    @property
    def custom_line_chart(self: "CastSelf") -> "_2091.CustomLineChart":
        from mastapy._private.utility_gui.charts import _2091

        return self.__parent__._cast(_2091.CustomLineChart)

    @property
    def custom_table_and_chart(self: "CastSelf") -> "_2092.CustomTableAndChart":
        from mastapy._private.utility_gui.charts import _2092

        return self.__parent__._cast(_2092.CustomTableAndChart)

    @property
    def loaded_ball_element_chart_reporter(
        self: "CastSelf",
    ) -> "_2186.LoadedBallElementChartReporter":
        from mastapy._private.bearings.bearing_results import _2186

        return self.__parent__._cast(_2186.LoadedBallElementChartReporter)

    @property
    def loaded_bearing_chart_reporter(
        self: "CastSelf",
    ) -> "_2187.LoadedBearingChartReporter":
        from mastapy._private.bearings.bearing_results import _2187

        return self.__parent__._cast(_2187.LoadedBearingChartReporter)

    @property
    def loaded_bearing_temperature_chart(
        self: "CastSelf",
    ) -> "_2190.LoadedBearingTemperatureChart":
        from mastapy._private.bearings.bearing_results import _2190

        return self.__parent__._cast(_2190.LoadedBearingTemperatureChart)

    @property
    def loaded_roller_element_chart_reporter(
        self: "CastSelf",
    ) -> "_2198.LoadedRollerElementChartReporter":
        from mastapy._private.bearings.bearing_results import _2198

        return self.__parent__._cast(_2198.LoadedRollerElementChartReporter)

    @property
    def shaft_system_deflection_sections_report(
        self: "CastSelf",
    ) -> "_3144.ShaftSystemDeflectionSectionsReport":
        from mastapy._private.system_model.analyses_and_results.system_deflections.reporting import (
            _3144,
        )

        return self.__parent__._cast(_3144.ShaftSystemDeflectionSectionsReport)

    @property
    def parametric_study_histogram(
        self: "CastSelf",
    ) -> "_4705.ParametricStudyHistogram":
        from mastapy._private.system_model.analyses_and_results.parametric_study_tools import (
            _4705,
        )

        return self.__parent__._cast(_4705.ParametricStudyHistogram)

    @property
    def campbell_diagram_report(self: "CastSelf") -> "_5042.CampbellDiagramReport":
        from mastapy._private.system_model.analyses_and_results.modal_analyses.reporting import (
            _5042,
        )

        return self.__parent__._cast(_5042.CampbellDiagramReport)

    @property
    def per_mode_results_report(self: "CastSelf") -> "_5046.PerModeResultsReport":
        from mastapy._private.system_model.analyses_and_results.modal_analyses.reporting import (
            _5046,
        )

        return self.__parent__._cast(_5046.PerModeResultsReport)

    @property
    def custom_report_item(self: "CastSelf") -> "CustomReportItem":
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
class CustomReportItem(_0.APIBase):
    """CustomReportItem

    This is a mastapy class.
    """

    TYPE: ClassVar["Type"] = _CUSTOM_REPORT_ITEM

    wrapped: "Any"

    def __post_init__(self: "Self") -> None:
        """Override of the post initialisation magic method."""
        if not hasattr(self.wrapped, "reference_count"):
            self.wrapped.reference_count = 0

        self.wrapped.reference_count += 1

    @property
    @exception_bridge
    def is_main_report_item(self: "Self") -> "bool":
        """bool"""
        temp = pythonnet_property_get(self.wrapped, "IsMainReportItem")

        if temp is None:
            return False

        return temp

    @is_main_report_item.setter
    @exception_bridge
    @enforce_parameter_types
    def is_main_report_item(self: "Self", value: "bool") -> None:
        pythonnet_property_set(
            self.wrapped,
            "IsMainReportItem",
            bool(value) if value is not None else False,
        )

    @property
    @exception_bridge
    def item_type(self: "Self") -> "str":
        """str

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "ItemType")

        if temp is None:
            return ""

        return temp

    @exception_bridge
    def add_condition(self: "Self") -> None:
        """Method does not return."""
        pythonnet_method_call(self.wrapped, "AddCondition")

    @property
    def cast_to(self: "Self") -> "_Cast_CustomReportItem":
        """Cast to another type.

        Returns:
            _Cast_CustomReportItem
        """
        return _Cast_CustomReportItem(self)
