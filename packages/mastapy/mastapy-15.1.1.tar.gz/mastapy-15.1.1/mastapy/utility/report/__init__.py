"""Subpackage."""

from typing import TYPE_CHECKING as __tc

if __tc:
    from mastapy._private.utility.report._1969 import AdHocCustomTable
    from mastapy._private.utility.report._1970 import AxisSettings
    from mastapy._private.utility.report._1971 import BlankRow
    from mastapy._private.utility.report._1972 import CadPageOrientation
    from mastapy._private.utility.report._1973 import CadPageSize
    from mastapy._private.utility.report._1974 import CadTableBorderType
    from mastapy._private.utility.report._1975 import ChartDefinition
    from mastapy._private.utility.report._1976 import SMTChartPointShape
    from mastapy._private.utility.report._1977 import CustomChart
    from mastapy._private.utility.report._1978 import CustomDrawing
    from mastapy._private.utility.report._1979 import CustomGraphic
    from mastapy._private.utility.report._1980 import CustomImage
    from mastapy._private.utility.report._1981 import CustomReport
    from mastapy._private.utility.report._1982 import CustomReportCadDrawing
    from mastapy._private.utility.report._1983 import CustomReportChart
    from mastapy._private.utility.report._1984 import CustomReportChartItem
    from mastapy._private.utility.report._1985 import CustomReportColumn
    from mastapy._private.utility.report._1986 import CustomReportColumns
    from mastapy._private.utility.report._1987 import CustomReportDefinitionItem
    from mastapy._private.utility.report._1988 import CustomReportHorizontalLine
    from mastapy._private.utility.report._1989 import CustomReportHtmlItem
    from mastapy._private.utility.report._1990 import CustomReportItem
    from mastapy._private.utility.report._1991 import CustomReportItemContainer
    from mastapy._private.utility.report._1992 import (
        CustomReportItemContainerCollection,
    )
    from mastapy._private.utility.report._1993 import (
        CustomReportItemContainerCollectionBase,
    )
    from mastapy._private.utility.report._1994 import (
        CustomReportItemContainerCollectionItem,
    )
    from mastapy._private.utility.report._1995 import CustomReportKey
    from mastapy._private.utility.report._1996 import CustomReportMultiPropertyItem
    from mastapy._private.utility.report._1997 import CustomReportMultiPropertyItemBase
    from mastapy._private.utility.report._1998 import CustomReportNameableItem
    from mastapy._private.utility.report._1999 import CustomReportNamedItem
    from mastapy._private.utility.report._2000 import CustomReportPropertyItem
    from mastapy._private.utility.report._2001 import CustomReportStatusItem
    from mastapy._private.utility.report._2002 import CustomReportTab
    from mastapy._private.utility.report._2003 import CustomReportTabs
    from mastapy._private.utility.report._2004 import CustomReportText
    from mastapy._private.utility.report._2005 import CustomRow
    from mastapy._private.utility.report._2006 import CustomSubReport
    from mastapy._private.utility.report._2007 import CustomTable
    from mastapy._private.utility.report._2008 import DefinitionBooleanCheckOptions
    from mastapy._private.utility.report._2009 import DynamicCustomReportItem
    from mastapy._private.utility.report._2010 import FontStyle
    from mastapy._private.utility.report._2011 import FontWeight
    from mastapy._private.utility.report._2012 import HeadingSize
    from mastapy._private.utility.report._2013 import SimpleChartDefinition
    from mastapy._private.utility.report._2014 import UserTextRow
else:
    import sys as __sys

    from lazy_imports import LazyImporter as __LazyImporter

    __import_structure = {
        "_private.utility.report._1969": ["AdHocCustomTable"],
        "_private.utility.report._1970": ["AxisSettings"],
        "_private.utility.report._1971": ["BlankRow"],
        "_private.utility.report._1972": ["CadPageOrientation"],
        "_private.utility.report._1973": ["CadPageSize"],
        "_private.utility.report._1974": ["CadTableBorderType"],
        "_private.utility.report._1975": ["ChartDefinition"],
        "_private.utility.report._1976": ["SMTChartPointShape"],
        "_private.utility.report._1977": ["CustomChart"],
        "_private.utility.report._1978": ["CustomDrawing"],
        "_private.utility.report._1979": ["CustomGraphic"],
        "_private.utility.report._1980": ["CustomImage"],
        "_private.utility.report._1981": ["CustomReport"],
        "_private.utility.report._1982": ["CustomReportCadDrawing"],
        "_private.utility.report._1983": ["CustomReportChart"],
        "_private.utility.report._1984": ["CustomReportChartItem"],
        "_private.utility.report._1985": ["CustomReportColumn"],
        "_private.utility.report._1986": ["CustomReportColumns"],
        "_private.utility.report._1987": ["CustomReportDefinitionItem"],
        "_private.utility.report._1988": ["CustomReportHorizontalLine"],
        "_private.utility.report._1989": ["CustomReportHtmlItem"],
        "_private.utility.report._1990": ["CustomReportItem"],
        "_private.utility.report._1991": ["CustomReportItemContainer"],
        "_private.utility.report._1992": ["CustomReportItemContainerCollection"],
        "_private.utility.report._1993": ["CustomReportItemContainerCollectionBase"],
        "_private.utility.report._1994": ["CustomReportItemContainerCollectionItem"],
        "_private.utility.report._1995": ["CustomReportKey"],
        "_private.utility.report._1996": ["CustomReportMultiPropertyItem"],
        "_private.utility.report._1997": ["CustomReportMultiPropertyItemBase"],
        "_private.utility.report._1998": ["CustomReportNameableItem"],
        "_private.utility.report._1999": ["CustomReportNamedItem"],
        "_private.utility.report._2000": ["CustomReportPropertyItem"],
        "_private.utility.report._2001": ["CustomReportStatusItem"],
        "_private.utility.report._2002": ["CustomReportTab"],
        "_private.utility.report._2003": ["CustomReportTabs"],
        "_private.utility.report._2004": ["CustomReportText"],
        "_private.utility.report._2005": ["CustomRow"],
        "_private.utility.report._2006": ["CustomSubReport"],
        "_private.utility.report._2007": ["CustomTable"],
        "_private.utility.report._2008": ["DefinitionBooleanCheckOptions"],
        "_private.utility.report._2009": ["DynamicCustomReportItem"],
        "_private.utility.report._2010": ["FontStyle"],
        "_private.utility.report._2011": ["FontWeight"],
        "_private.utility.report._2012": ["HeadingSize"],
        "_private.utility.report._2013": ["SimpleChartDefinition"],
        "_private.utility.report._2014": ["UserTextRow"],
    }

    __sys.modules[__name__] = __LazyImporter(
        "mastapy",
        globals()["__file__"],
        __import_structure,
    )

__all__ = (
    "AdHocCustomTable",
    "AxisSettings",
    "BlankRow",
    "CadPageOrientation",
    "CadPageSize",
    "CadTableBorderType",
    "ChartDefinition",
    "SMTChartPointShape",
    "CustomChart",
    "CustomDrawing",
    "CustomGraphic",
    "CustomImage",
    "CustomReport",
    "CustomReportCadDrawing",
    "CustomReportChart",
    "CustomReportChartItem",
    "CustomReportColumn",
    "CustomReportColumns",
    "CustomReportDefinitionItem",
    "CustomReportHorizontalLine",
    "CustomReportHtmlItem",
    "CustomReportItem",
    "CustomReportItemContainer",
    "CustomReportItemContainerCollection",
    "CustomReportItemContainerCollectionBase",
    "CustomReportItemContainerCollectionItem",
    "CustomReportKey",
    "CustomReportMultiPropertyItem",
    "CustomReportMultiPropertyItemBase",
    "CustomReportNameableItem",
    "CustomReportNamedItem",
    "CustomReportPropertyItem",
    "CustomReportStatusItem",
    "CustomReportTab",
    "CustomReportTabs",
    "CustomReportText",
    "CustomRow",
    "CustomSubReport",
    "CustomTable",
    "DefinitionBooleanCheckOptions",
    "DynamicCustomReportItem",
    "FontStyle",
    "FontWeight",
    "HeadingSize",
    "SimpleChartDefinition",
    "UserTextRow",
)
