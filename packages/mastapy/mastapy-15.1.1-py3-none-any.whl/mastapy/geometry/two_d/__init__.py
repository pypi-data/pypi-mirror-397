"""Subpackage."""

from typing import TYPE_CHECKING as __tc

if __tc:
    from mastapy._private.geometry.two_d._416 import CADFace
    from mastapy._private.geometry.two_d._417 import CADFaceGroup
    from mastapy._private.geometry.two_d._418 import InternalExternalType
else:
    import sys as __sys

    from lazy_imports import LazyImporter as __LazyImporter

    __import_structure = {
        "_private.geometry.two_d._416": ["CADFace"],
        "_private.geometry.two_d._417": ["CADFaceGroup"],
        "_private.geometry.two_d._418": ["InternalExternalType"],
    }

    __sys.modules[__name__] = __LazyImporter(
        "mastapy",
        globals()["__file__"],
        __import_structure,
    )

__all__ = (
    "CADFace",
    "CADFaceGroup",
    "InternalExternalType",
)
