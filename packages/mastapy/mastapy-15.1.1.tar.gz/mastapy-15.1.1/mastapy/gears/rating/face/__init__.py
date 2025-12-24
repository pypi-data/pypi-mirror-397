"""Subpackage."""

from typing import TYPE_CHECKING as __tc

if __tc:
    from mastapy._private.gears.rating.face._558 import FaceGearDutyCycleRating
    from mastapy._private.gears.rating.face._559 import FaceGearMeshDutyCycleRating
    from mastapy._private.gears.rating.face._560 import FaceGearMeshRating
    from mastapy._private.gears.rating.face._561 import FaceGearRating
    from mastapy._private.gears.rating.face._562 import FaceGearSetDutyCycleRating
    from mastapy._private.gears.rating.face._563 import FaceGearSetRating
else:
    import sys as __sys

    from lazy_imports import LazyImporter as __LazyImporter

    __import_structure = {
        "_private.gears.rating.face._558": ["FaceGearDutyCycleRating"],
        "_private.gears.rating.face._559": ["FaceGearMeshDutyCycleRating"],
        "_private.gears.rating.face._560": ["FaceGearMeshRating"],
        "_private.gears.rating.face._561": ["FaceGearRating"],
        "_private.gears.rating.face._562": ["FaceGearSetDutyCycleRating"],
        "_private.gears.rating.face._563": ["FaceGearSetRating"],
    }

    __sys.modules[__name__] = __LazyImporter(
        "mastapy",
        globals()["__file__"],
        __import_structure,
    )

__all__ = (
    "FaceGearDutyCycleRating",
    "FaceGearMeshDutyCycleRating",
    "FaceGearMeshRating",
    "FaceGearRating",
    "FaceGearSetDutyCycleRating",
    "FaceGearSetRating",
)
