"""Subpackage."""

from typing import TYPE_CHECKING as __tc

if __tc:
    from mastapy._private.gears.load_case.conical._1010 import ConicalGearLoadCase
    from mastapy._private.gears.load_case.conical._1011 import ConicalGearSetLoadCase
    from mastapy._private.gears.load_case.conical._1012 import ConicalMeshLoadCase
else:
    import sys as __sys

    from lazy_imports import LazyImporter as __LazyImporter

    __import_structure = {
        "_private.gears.load_case.conical._1010": ["ConicalGearLoadCase"],
        "_private.gears.load_case.conical._1011": ["ConicalGearSetLoadCase"],
        "_private.gears.load_case.conical._1012": ["ConicalMeshLoadCase"],
    }

    __sys.modules[__name__] = __LazyImporter(
        "mastapy",
        globals()["__file__"],
        __import_structure,
    )

__all__ = (
    "ConicalGearLoadCase",
    "ConicalGearSetLoadCase",
    "ConicalMeshLoadCase",
)
