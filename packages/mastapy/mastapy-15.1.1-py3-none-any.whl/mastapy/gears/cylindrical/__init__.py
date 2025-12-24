"""Subpackage."""

from typing import TYPE_CHECKING as __tc

if __tc:
    from mastapy._private.gears.cylindrical._1354 import (
        CylindricalGearLTCAContactChartDataAsTextFile,
    )
    from mastapy._private.gears.cylindrical._1355 import (
        CylindricalGearLTCAContactCharts,
    )
    from mastapy._private.gears.cylindrical._1356 import (
        CylindricalGearWorstLTCAContactChartDataAsTextFile,
    )
    from mastapy._private.gears.cylindrical._1357 import (
        CylindricalGearWorstLTCAContactCharts,
    )
    from mastapy._private.gears.cylindrical._1358 import (
        GearLTCAContactChartDataAsTextFile,
    )
    from mastapy._private.gears.cylindrical._1359 import GearLTCAContactCharts
    from mastapy._private.gears.cylindrical._1360 import PointsWithWorstResults
else:
    import sys as __sys

    from lazy_imports import LazyImporter as __LazyImporter

    __import_structure = {
        "_private.gears.cylindrical._1354": [
            "CylindricalGearLTCAContactChartDataAsTextFile"
        ],
        "_private.gears.cylindrical._1355": ["CylindricalGearLTCAContactCharts"],
        "_private.gears.cylindrical._1356": [
            "CylindricalGearWorstLTCAContactChartDataAsTextFile"
        ],
        "_private.gears.cylindrical._1357": ["CylindricalGearWorstLTCAContactCharts"],
        "_private.gears.cylindrical._1358": ["GearLTCAContactChartDataAsTextFile"],
        "_private.gears.cylindrical._1359": ["GearLTCAContactCharts"],
        "_private.gears.cylindrical._1360": ["PointsWithWorstResults"],
    }

    __sys.modules[__name__] = __LazyImporter(
        "mastapy",
        globals()["__file__"],
        __import_structure,
    )

__all__ = (
    "CylindricalGearLTCAContactChartDataAsTextFile",
    "CylindricalGearLTCAContactCharts",
    "CylindricalGearWorstLTCAContactChartDataAsTextFile",
    "CylindricalGearWorstLTCAContactCharts",
    "GearLTCAContactChartDataAsTextFile",
    "GearLTCAContactCharts",
    "PointsWithWorstResults",
)
