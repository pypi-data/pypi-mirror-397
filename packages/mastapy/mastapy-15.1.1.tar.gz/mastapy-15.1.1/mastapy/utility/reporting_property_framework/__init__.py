"""Subpackage."""

from typing import TYPE_CHECKING as __tc

if __tc:
    from mastapy._private.utility.reporting_property_framework._2015 import (
        CellValuePosition,
    )
    from mastapy._private.utility.reporting_property_framework._2016 import (
        CustomChartType,
    )
else:
    import sys as __sys

    from lazy_imports import LazyImporter as __LazyImporter

    __import_structure = {
        "_private.utility.reporting_property_framework._2015": ["CellValuePosition"],
        "_private.utility.reporting_property_framework._2016": ["CustomChartType"],
    }

    __sys.modules[__name__] = __LazyImporter(
        "mastapy",
        globals()["__file__"],
        __import_structure,
    )

__all__ = (
    "CellValuePosition",
    "CustomChartType",
)
