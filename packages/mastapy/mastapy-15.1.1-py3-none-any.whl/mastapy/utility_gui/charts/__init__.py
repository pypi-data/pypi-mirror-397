"""Subpackage."""

from typing import TYPE_CHECKING as __tc

if __tc:
    from mastapy._private.utility_gui.charts._2089 import BubbleChartDefinition
    from mastapy._private.utility_gui.charts._2090 import ConstantLine
    from mastapy._private.utility_gui.charts._2091 import CustomLineChart
    from mastapy._private.utility_gui.charts._2092 import CustomTableAndChart
    from mastapy._private.utility_gui.charts._2093 import LegacyChartMathChartDefinition
    from mastapy._private.utility_gui.charts._2094 import MatrixVisualisationDefinition
    from mastapy._private.utility_gui.charts._2095 import ModeConstantLine
    from mastapy._private.utility_gui.charts._2096 import NDChartDefinition
    from mastapy._private.utility_gui.charts._2097 import (
        ParallelCoordinatesChartDefinition,
    )
    from mastapy._private.utility_gui.charts._2098 import PointsForSurface
    from mastapy._private.utility_gui.charts._2099 import ScatterChartDefinition
    from mastapy._private.utility_gui.charts._2100 import Series2D
    from mastapy._private.utility_gui.charts._2101 import SMTAxis
    from mastapy._private.utility_gui.charts._2102 import ThreeDChartDefinition
    from mastapy._private.utility_gui.charts._2103 import ThreeDVectorChartDefinition
    from mastapy._private.utility_gui.charts._2104 import TwoDChartDefinition
else:
    import sys as __sys

    from lazy_imports import LazyImporter as __LazyImporter

    __import_structure = {
        "_private.utility_gui.charts._2089": ["BubbleChartDefinition"],
        "_private.utility_gui.charts._2090": ["ConstantLine"],
        "_private.utility_gui.charts._2091": ["CustomLineChart"],
        "_private.utility_gui.charts._2092": ["CustomTableAndChart"],
        "_private.utility_gui.charts._2093": ["LegacyChartMathChartDefinition"],
        "_private.utility_gui.charts._2094": ["MatrixVisualisationDefinition"],
        "_private.utility_gui.charts._2095": ["ModeConstantLine"],
        "_private.utility_gui.charts._2096": ["NDChartDefinition"],
        "_private.utility_gui.charts._2097": ["ParallelCoordinatesChartDefinition"],
        "_private.utility_gui.charts._2098": ["PointsForSurface"],
        "_private.utility_gui.charts._2099": ["ScatterChartDefinition"],
        "_private.utility_gui.charts._2100": ["Series2D"],
        "_private.utility_gui.charts._2101": ["SMTAxis"],
        "_private.utility_gui.charts._2102": ["ThreeDChartDefinition"],
        "_private.utility_gui.charts._2103": ["ThreeDVectorChartDefinition"],
        "_private.utility_gui.charts._2104": ["TwoDChartDefinition"],
    }

    __sys.modules[__name__] = __LazyImporter(
        "mastapy",
        globals()["__file__"],
        __import_structure,
    )

__all__ = (
    "BubbleChartDefinition",
    "ConstantLine",
    "CustomLineChart",
    "CustomTableAndChart",
    "LegacyChartMathChartDefinition",
    "MatrixVisualisationDefinition",
    "ModeConstantLine",
    "NDChartDefinition",
    "ParallelCoordinatesChartDefinition",
    "PointsForSurface",
    "ScatterChartDefinition",
    "Series2D",
    "SMTAxis",
    "ThreeDChartDefinition",
    "ThreeDVectorChartDefinition",
    "TwoDChartDefinition",
)
