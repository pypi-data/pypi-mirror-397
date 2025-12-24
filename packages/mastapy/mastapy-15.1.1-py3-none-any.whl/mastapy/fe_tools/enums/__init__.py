"""Subpackage."""

from typing import TYPE_CHECKING as __tc

if __tc:
    from mastapy._private.fe_tools.enums._1389 import ElementPropertyClass
    from mastapy._private.fe_tools.enums._1390 import MaterialPropertyClass
else:
    import sys as __sys

    from lazy_imports import LazyImporter as __LazyImporter

    __import_structure = {
        "_private.fe_tools.enums._1389": ["ElementPropertyClass"],
        "_private.fe_tools.enums._1390": ["MaterialPropertyClass"],
    }

    __sys.modules[__name__] = __LazyImporter(
        "mastapy",
        globals()["__file__"],
        __import_structure,
    )

__all__ = (
    "ElementPropertyClass",
    "MaterialPropertyClass",
)
