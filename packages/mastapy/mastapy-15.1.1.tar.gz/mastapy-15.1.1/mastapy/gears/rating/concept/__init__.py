"""Subpackage."""

from typing import TYPE_CHECKING as __tc

if __tc:
    from mastapy._private.gears.rating.concept._661 import ConceptGearDutyCycleRating
    from mastapy._private.gears.rating.concept._662 import (
        ConceptGearMeshDutyCycleRating,
    )
    from mastapy._private.gears.rating.concept._663 import ConceptGearMeshRating
    from mastapy._private.gears.rating.concept._664 import ConceptGearRating
    from mastapy._private.gears.rating.concept._665 import ConceptGearSetDutyCycleRating
    from mastapy._private.gears.rating.concept._666 import ConceptGearSetRating
else:
    import sys as __sys

    from lazy_imports import LazyImporter as __LazyImporter

    __import_structure = {
        "_private.gears.rating.concept._661": ["ConceptGearDutyCycleRating"],
        "_private.gears.rating.concept._662": ["ConceptGearMeshDutyCycleRating"],
        "_private.gears.rating.concept._663": ["ConceptGearMeshRating"],
        "_private.gears.rating.concept._664": ["ConceptGearRating"],
        "_private.gears.rating.concept._665": ["ConceptGearSetDutyCycleRating"],
        "_private.gears.rating.concept._666": ["ConceptGearSetRating"],
    }

    __sys.modules[__name__] = __LazyImporter(
        "mastapy",
        globals()["__file__"],
        __import_structure,
    )

__all__ = (
    "ConceptGearDutyCycleRating",
    "ConceptGearMeshDutyCycleRating",
    "ConceptGearMeshRating",
    "ConceptGearRating",
    "ConceptGearSetDutyCycleRating",
    "ConceptGearSetRating",
)
