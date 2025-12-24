"""Subpackage."""

from typing import TYPE_CHECKING as __tc

if __tc:
    from mastapy._private.nodal_analysis.elmer.results._268 import Data
    from mastapy._private.nodal_analysis.elmer.results._269 import Data1D
    from mastapy._private.nodal_analysis.elmer.results._270 import Data3D
    from mastapy._private.nodal_analysis.elmer.results._271 import Element
    from mastapy._private.nodal_analysis.elmer.results._272 import ElementBase
    from mastapy._private.nodal_analysis.elmer.results._273 import (
        ElementFromElectromagneticAnalysis,
    )
    from mastapy._private.nodal_analysis.elmer.results._274 import (
        ElementFromMechanicalAnalysis,
    )
else:
    import sys as __sys

    from lazy_imports import LazyImporter as __LazyImporter

    __import_structure = {
        "_private.nodal_analysis.elmer.results._268": ["Data"],
        "_private.nodal_analysis.elmer.results._269": ["Data1D"],
        "_private.nodal_analysis.elmer.results._270": ["Data3D"],
        "_private.nodal_analysis.elmer.results._271": ["Element"],
        "_private.nodal_analysis.elmer.results._272": ["ElementBase"],
        "_private.nodal_analysis.elmer.results._273": [
            "ElementFromElectromagneticAnalysis"
        ],
        "_private.nodal_analysis.elmer.results._274": ["ElementFromMechanicalAnalysis"],
    }

    __sys.modules[__name__] = __LazyImporter(
        "mastapy",
        globals()["__file__"],
        __import_structure,
    )

__all__ = (
    "Data",
    "Data1D",
    "Data3D",
    "Element",
    "ElementBase",
    "ElementFromElectromagneticAnalysis",
    "ElementFromMechanicalAnalysis",
)
