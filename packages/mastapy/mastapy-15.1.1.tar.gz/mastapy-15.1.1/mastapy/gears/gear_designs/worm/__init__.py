"""Subpackage."""

from typing import TYPE_CHECKING as __tc

if __tc:
    from mastapy._private.gears.gear_designs.worm._1082 import WormDesign
    from mastapy._private.gears.gear_designs.worm._1083 import WormGearDesign
    from mastapy._private.gears.gear_designs.worm._1084 import WormGearMeshDesign
    from mastapy._private.gears.gear_designs.worm._1085 import WormGearSetDesign
    from mastapy._private.gears.gear_designs.worm._1086 import WormWheelDesign
else:
    import sys as __sys

    from lazy_imports import LazyImporter as __LazyImporter

    __import_structure = {
        "_private.gears.gear_designs.worm._1082": ["WormDesign"],
        "_private.gears.gear_designs.worm._1083": ["WormGearDesign"],
        "_private.gears.gear_designs.worm._1084": ["WormGearMeshDesign"],
        "_private.gears.gear_designs.worm._1085": ["WormGearSetDesign"],
        "_private.gears.gear_designs.worm._1086": ["WormWheelDesign"],
    }

    __sys.modules[__name__] = __LazyImporter(
        "mastapy",
        globals()["__file__"],
        __import_structure,
    )

__all__ = (
    "WormDesign",
    "WormGearDesign",
    "WormGearMeshDesign",
    "WormGearSetDesign",
    "WormWheelDesign",
)
