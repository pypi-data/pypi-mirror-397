"""Subpackage."""

from typing import TYPE_CHECKING as __tc

if __tc:
    from mastapy._private.gears.manufacturing.cylindrical.cutters.tangibles._849 import (
        CutterShapeDefinition,
    )
    from mastapy._private.gears.manufacturing.cylindrical.cutters.tangibles._850 import (
        CylindricalGearFormedWheelGrinderTangible,
    )
    from mastapy._private.gears.manufacturing.cylindrical.cutters.tangibles._851 import (
        CylindricalGearHobShape,
    )
    from mastapy._private.gears.manufacturing.cylindrical.cutters.tangibles._852 import (
        CylindricalGearShaperTangible,
    )
    from mastapy._private.gears.manufacturing.cylindrical.cutters.tangibles._853 import (
        CylindricalGearShaverTangible,
    )
    from mastapy._private.gears.manufacturing.cylindrical.cutters.tangibles._854 import (
        CylindricalGearWormGrinderShape,
    )
    from mastapy._private.gears.manufacturing.cylindrical.cutters.tangibles._855 import (
        NamedPoint,
    )
    from mastapy._private.gears.manufacturing.cylindrical.cutters.tangibles._856 import (
        RackShape,
    )
else:
    import sys as __sys

    from lazy_imports import LazyImporter as __LazyImporter

    __import_structure = {
        "_private.gears.manufacturing.cylindrical.cutters.tangibles._849": [
            "CutterShapeDefinition"
        ],
        "_private.gears.manufacturing.cylindrical.cutters.tangibles._850": [
            "CylindricalGearFormedWheelGrinderTangible"
        ],
        "_private.gears.manufacturing.cylindrical.cutters.tangibles._851": [
            "CylindricalGearHobShape"
        ],
        "_private.gears.manufacturing.cylindrical.cutters.tangibles._852": [
            "CylindricalGearShaperTangible"
        ],
        "_private.gears.manufacturing.cylindrical.cutters.tangibles._853": [
            "CylindricalGearShaverTangible"
        ],
        "_private.gears.manufacturing.cylindrical.cutters.tangibles._854": [
            "CylindricalGearWormGrinderShape"
        ],
        "_private.gears.manufacturing.cylindrical.cutters.tangibles._855": [
            "NamedPoint"
        ],
        "_private.gears.manufacturing.cylindrical.cutters.tangibles._856": [
            "RackShape"
        ],
    }

    __sys.modules[__name__] = __LazyImporter(
        "mastapy",
        globals()["__file__"],
        __import_structure,
    )

__all__ = (
    "CutterShapeDefinition",
    "CylindricalGearFormedWheelGrinderTangible",
    "CylindricalGearHobShape",
    "CylindricalGearShaperTangible",
    "CylindricalGearShaverTangible",
    "CylindricalGearWormGrinderShape",
    "NamedPoint",
    "RackShape",
)
