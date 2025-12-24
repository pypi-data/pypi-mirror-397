"""Subpackage."""

from typing import TYPE_CHECKING as __tc

if __tc:
    from mastapy._private.gears.manufacturing.bevel.cutters._939 import (
        PinionFinishCutter,
    )
    from mastapy._private.gears.manufacturing.bevel.cutters._940 import (
        PinionRoughCutter,
    )
    from mastapy._private.gears.manufacturing.bevel.cutters._941 import (
        WheelFinishCutter,
    )
    from mastapy._private.gears.manufacturing.bevel.cutters._942 import WheelRoughCutter
else:
    import sys as __sys

    from lazy_imports import LazyImporter as __LazyImporter

    __import_structure = {
        "_private.gears.manufacturing.bevel.cutters._939": ["PinionFinishCutter"],
        "_private.gears.manufacturing.bevel.cutters._940": ["PinionRoughCutter"],
        "_private.gears.manufacturing.bevel.cutters._941": ["WheelFinishCutter"],
        "_private.gears.manufacturing.bevel.cutters._942": ["WheelRoughCutter"],
    }

    __sys.modules[__name__] = __LazyImporter(
        "mastapy",
        globals()["__file__"],
        __import_structure,
    )

__all__ = (
    "PinionFinishCutter",
    "PinionRoughCutter",
    "WheelFinishCutter",
    "WheelRoughCutter",
)
