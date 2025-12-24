"""Subpackage."""

from typing import TYPE_CHECKING as __tc

if __tc:
    from mastapy._private.gears.gear_designs.spiral_bevel._1095 import (
        SpiralBevelGearDesign,
    )
    from mastapy._private.gears.gear_designs.spiral_bevel._1096 import (
        SpiralBevelGearMeshDesign,
    )
    from mastapy._private.gears.gear_designs.spiral_bevel._1097 import (
        SpiralBevelGearSetDesign,
    )
    from mastapy._private.gears.gear_designs.spiral_bevel._1098 import (
        SpiralBevelMeshedGearDesign,
    )
else:
    import sys as __sys

    from lazy_imports import LazyImporter as __LazyImporter

    __import_structure = {
        "_private.gears.gear_designs.spiral_bevel._1095": ["SpiralBevelGearDesign"],
        "_private.gears.gear_designs.spiral_bevel._1096": ["SpiralBevelGearMeshDesign"],
        "_private.gears.gear_designs.spiral_bevel._1097": ["SpiralBevelGearSetDesign"],
        "_private.gears.gear_designs.spiral_bevel._1098": [
            "SpiralBevelMeshedGearDesign"
        ],
    }

    __sys.modules[__name__] = __LazyImporter(
        "mastapy",
        globals()["__file__"],
        __import_structure,
    )

__all__ = (
    "SpiralBevelGearDesign",
    "SpiralBevelGearMeshDesign",
    "SpiralBevelGearSetDesign",
    "SpiralBevelMeshedGearDesign",
)
