"""Subpackage."""

from typing import TYPE_CHECKING as __tc

if __tc:
    from mastapy._private.gears.rating.hypoid._551 import HypoidGearMeshRating
    from mastapy._private.gears.rating.hypoid._552 import HypoidGearRating
    from mastapy._private.gears.rating.hypoid._553 import HypoidGearSetRating
    from mastapy._private.gears.rating.hypoid._554 import HypoidRatingMethod
else:
    import sys as __sys

    from lazy_imports import LazyImporter as __LazyImporter

    __import_structure = {
        "_private.gears.rating.hypoid._551": ["HypoidGearMeshRating"],
        "_private.gears.rating.hypoid._552": ["HypoidGearRating"],
        "_private.gears.rating.hypoid._553": ["HypoidGearSetRating"],
        "_private.gears.rating.hypoid._554": ["HypoidRatingMethod"],
    }

    __sys.modules[__name__] = __LazyImporter(
        "mastapy",
        globals()["__file__"],
        __import_structure,
    )

__all__ = (
    "HypoidGearMeshRating",
    "HypoidGearRating",
    "HypoidGearSetRating",
    "HypoidRatingMethod",
)
