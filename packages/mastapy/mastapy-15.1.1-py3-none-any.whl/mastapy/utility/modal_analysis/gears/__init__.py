"""Subpackage."""

from typing import TYPE_CHECKING as __tc

if __tc:
    from mastapy._private.utility.modal_analysis.gears._2026 import GearMeshForTE
    from mastapy._private.utility.modal_analysis.gears._2027 import GearOrderForTE
    from mastapy._private.utility.modal_analysis.gears._2028 import GearPositions
    from mastapy._private.utility.modal_analysis.gears._2029 import HarmonicOrderForTE
    from mastapy._private.utility.modal_analysis.gears._2030 import LabelOnlyOrder
    from mastapy._private.utility.modal_analysis.gears._2031 import OrderForTE
    from mastapy._private.utility.modal_analysis.gears._2032 import OrderSelector
    from mastapy._private.utility.modal_analysis.gears._2033 import OrderWithRadius
    from mastapy._private.utility.modal_analysis.gears._2034 import RollingBearingOrder
    from mastapy._private.utility.modal_analysis.gears._2035 import ShaftOrderForTE
    from mastapy._private.utility.modal_analysis.gears._2036 import (
        UserDefinedOrderForTE,
    )
else:
    import sys as __sys

    from lazy_imports import LazyImporter as __LazyImporter

    __import_structure = {
        "_private.utility.modal_analysis.gears._2026": ["GearMeshForTE"],
        "_private.utility.modal_analysis.gears._2027": ["GearOrderForTE"],
        "_private.utility.modal_analysis.gears._2028": ["GearPositions"],
        "_private.utility.modal_analysis.gears._2029": ["HarmonicOrderForTE"],
        "_private.utility.modal_analysis.gears._2030": ["LabelOnlyOrder"],
        "_private.utility.modal_analysis.gears._2031": ["OrderForTE"],
        "_private.utility.modal_analysis.gears._2032": ["OrderSelector"],
        "_private.utility.modal_analysis.gears._2033": ["OrderWithRadius"],
        "_private.utility.modal_analysis.gears._2034": ["RollingBearingOrder"],
        "_private.utility.modal_analysis.gears._2035": ["ShaftOrderForTE"],
        "_private.utility.modal_analysis.gears._2036": ["UserDefinedOrderForTE"],
    }

    __sys.modules[__name__] = __LazyImporter(
        "mastapy",
        globals()["__file__"],
        __import_structure,
    )

__all__ = (
    "GearMeshForTE",
    "GearOrderForTE",
    "GearPositions",
    "HarmonicOrderForTE",
    "LabelOnlyOrder",
    "OrderForTE",
    "OrderSelector",
    "OrderWithRadius",
    "RollingBearingOrder",
    "ShaftOrderForTE",
    "UserDefinedOrderForTE",
)
