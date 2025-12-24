"""Subpackage."""

from typing import TYPE_CHECKING as __tc

if __tc:
    from mastapy._private.gears.rating.worm._485 import WormGearDutyCycleRating
    from mastapy._private.gears.rating.worm._486 import WormGearMeshRating
    from mastapy._private.gears.rating.worm._487 import WormGearRating
    from mastapy._private.gears.rating.worm._488 import WormGearSetDutyCycleRating
    from mastapy._private.gears.rating.worm._489 import WormGearSetRating
    from mastapy._private.gears.rating.worm._490 import WormMeshDutyCycleRating
else:
    import sys as __sys

    from lazy_imports import LazyImporter as __LazyImporter

    __import_structure = {
        "_private.gears.rating.worm._485": ["WormGearDutyCycleRating"],
        "_private.gears.rating.worm._486": ["WormGearMeshRating"],
        "_private.gears.rating.worm._487": ["WormGearRating"],
        "_private.gears.rating.worm._488": ["WormGearSetDutyCycleRating"],
        "_private.gears.rating.worm._489": ["WormGearSetRating"],
        "_private.gears.rating.worm._490": ["WormMeshDutyCycleRating"],
    }

    __sys.modules[__name__] = __LazyImporter(
        "mastapy",
        globals()["__file__"],
        __import_structure,
    )

__all__ = (
    "WormGearDutyCycleRating",
    "WormGearMeshRating",
    "WormGearRating",
    "WormGearSetDutyCycleRating",
    "WormGearSetRating",
    "WormMeshDutyCycleRating",
)
