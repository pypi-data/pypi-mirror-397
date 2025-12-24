"""Subpackage."""

from typing import TYPE_CHECKING as __tc

if __tc:
    from mastapy._private.gears.manufacturing.cylindrical.cutters._829 import (
        CurveInLinkedList,
    )
    from mastapy._private.gears.manufacturing.cylindrical.cutters._830 import (
        CustomisableEdgeProfile,
    )
    from mastapy._private.gears.manufacturing.cylindrical.cutters._831 import (
        CylindricalFormedWheelGrinderDatabase,
    )
    from mastapy._private.gears.manufacturing.cylindrical.cutters._832 import (
        CylindricalGearAbstractCutterDesign,
    )
    from mastapy._private.gears.manufacturing.cylindrical.cutters._833 import (
        CylindricalGearFormGrindingWheel,
    )
    from mastapy._private.gears.manufacturing.cylindrical.cutters._834 import (
        CylindricalGearGrindingWorm,
    )
    from mastapy._private.gears.manufacturing.cylindrical.cutters._835 import (
        CylindricalGearHobDesign,
    )
    from mastapy._private.gears.manufacturing.cylindrical.cutters._836 import (
        CylindricalGearPlungeShaver,
    )
    from mastapy._private.gears.manufacturing.cylindrical.cutters._837 import (
        CylindricalGearPlungeShaverDatabase,
    )
    from mastapy._private.gears.manufacturing.cylindrical.cutters._838 import (
        CylindricalGearRackDesign,
    )
    from mastapy._private.gears.manufacturing.cylindrical.cutters._839 import (
        CylindricalGearRealCutterDesign,
    )
    from mastapy._private.gears.manufacturing.cylindrical.cutters._840 import (
        CylindricalGearShaper,
    )
    from mastapy._private.gears.manufacturing.cylindrical.cutters._841 import (
        CylindricalGearShaver,
    )
    from mastapy._private.gears.manufacturing.cylindrical.cutters._842 import (
        CylindricalGearShaverDatabase,
    )
    from mastapy._private.gears.manufacturing.cylindrical.cutters._843 import (
        CylindricalWormGrinderDatabase,
    )
    from mastapy._private.gears.manufacturing.cylindrical.cutters._844 import (
        InvoluteCutterDesign,
    )
    from mastapy._private.gears.manufacturing.cylindrical.cutters._845 import (
        MutableCommon,
    )
    from mastapy._private.gears.manufacturing.cylindrical.cutters._846 import (
        MutableCurve,
    )
    from mastapy._private.gears.manufacturing.cylindrical.cutters._847 import (
        MutableFillet,
    )
    from mastapy._private.gears.manufacturing.cylindrical.cutters._848 import (
        RoughCutterCreationSettings,
    )
else:
    import sys as __sys

    from lazy_imports import LazyImporter as __LazyImporter

    __import_structure = {
        "_private.gears.manufacturing.cylindrical.cutters._829": ["CurveInLinkedList"],
        "_private.gears.manufacturing.cylindrical.cutters._830": [
            "CustomisableEdgeProfile"
        ],
        "_private.gears.manufacturing.cylindrical.cutters._831": [
            "CylindricalFormedWheelGrinderDatabase"
        ],
        "_private.gears.manufacturing.cylindrical.cutters._832": [
            "CylindricalGearAbstractCutterDesign"
        ],
        "_private.gears.manufacturing.cylindrical.cutters._833": [
            "CylindricalGearFormGrindingWheel"
        ],
        "_private.gears.manufacturing.cylindrical.cutters._834": [
            "CylindricalGearGrindingWorm"
        ],
        "_private.gears.manufacturing.cylindrical.cutters._835": [
            "CylindricalGearHobDesign"
        ],
        "_private.gears.manufacturing.cylindrical.cutters._836": [
            "CylindricalGearPlungeShaver"
        ],
        "_private.gears.manufacturing.cylindrical.cutters._837": [
            "CylindricalGearPlungeShaverDatabase"
        ],
        "_private.gears.manufacturing.cylindrical.cutters._838": [
            "CylindricalGearRackDesign"
        ],
        "_private.gears.manufacturing.cylindrical.cutters._839": [
            "CylindricalGearRealCutterDesign"
        ],
        "_private.gears.manufacturing.cylindrical.cutters._840": [
            "CylindricalGearShaper"
        ],
        "_private.gears.manufacturing.cylindrical.cutters._841": [
            "CylindricalGearShaver"
        ],
        "_private.gears.manufacturing.cylindrical.cutters._842": [
            "CylindricalGearShaverDatabase"
        ],
        "_private.gears.manufacturing.cylindrical.cutters._843": [
            "CylindricalWormGrinderDatabase"
        ],
        "_private.gears.manufacturing.cylindrical.cutters._844": [
            "InvoluteCutterDesign"
        ],
        "_private.gears.manufacturing.cylindrical.cutters._845": ["MutableCommon"],
        "_private.gears.manufacturing.cylindrical.cutters._846": ["MutableCurve"],
        "_private.gears.manufacturing.cylindrical.cutters._847": ["MutableFillet"],
        "_private.gears.manufacturing.cylindrical.cutters._848": [
            "RoughCutterCreationSettings"
        ],
    }

    __sys.modules[__name__] = __LazyImporter(
        "mastapy",
        globals()["__file__"],
        __import_structure,
    )

__all__ = (
    "CurveInLinkedList",
    "CustomisableEdgeProfile",
    "CylindricalFormedWheelGrinderDatabase",
    "CylindricalGearAbstractCutterDesign",
    "CylindricalGearFormGrindingWheel",
    "CylindricalGearGrindingWorm",
    "CylindricalGearHobDesign",
    "CylindricalGearPlungeShaver",
    "CylindricalGearPlungeShaverDatabase",
    "CylindricalGearRackDesign",
    "CylindricalGearRealCutterDesign",
    "CylindricalGearShaper",
    "CylindricalGearShaver",
    "CylindricalGearShaverDatabase",
    "CylindricalWormGrinderDatabase",
    "InvoluteCutterDesign",
    "MutableCommon",
    "MutableCurve",
    "MutableFillet",
    "RoughCutterCreationSettings",
)
