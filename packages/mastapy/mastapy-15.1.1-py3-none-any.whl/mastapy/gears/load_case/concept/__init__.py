"""Subpackage."""

from typing import TYPE_CHECKING as __tc

if __tc:
    from mastapy._private.gears.load_case.concept._1013 import ConceptGearLoadCase
    from mastapy._private.gears.load_case.concept._1014 import ConceptGearSetLoadCase
    from mastapy._private.gears.load_case.concept._1015 import ConceptMeshLoadCase
else:
    import sys as __sys

    from lazy_imports import LazyImporter as __LazyImporter

    __import_structure = {
        "_private.gears.load_case.concept._1013": ["ConceptGearLoadCase"],
        "_private.gears.load_case.concept._1014": ["ConceptGearSetLoadCase"],
        "_private.gears.load_case.concept._1015": ["ConceptMeshLoadCase"],
    }

    __sys.modules[__name__] = __LazyImporter(
        "mastapy",
        globals()["__file__"],
        __import_structure,
    )

__all__ = (
    "ConceptGearLoadCase",
    "ConceptGearSetLoadCase",
    "ConceptMeshLoadCase",
)
