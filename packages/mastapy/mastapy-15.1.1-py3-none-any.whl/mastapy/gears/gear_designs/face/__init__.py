"""Subpackage."""

from typing import TYPE_CHECKING as __tc

if __tc:
    from mastapy._private.gears.gear_designs.face._1115 import FaceGearDesign
    from mastapy._private.gears.gear_designs.face._1116 import (
        FaceGearDiameterFaceWidthSpecificationMethod,
    )
    from mastapy._private.gears.gear_designs.face._1117 import FaceGearMeshDesign
    from mastapy._private.gears.gear_designs.face._1118 import FaceGearMeshMicroGeometry
    from mastapy._private.gears.gear_designs.face._1119 import FaceGearMicroGeometry
    from mastapy._private.gears.gear_designs.face._1120 import FaceGearPinionDesign
    from mastapy._private.gears.gear_designs.face._1121 import FaceGearSetDesign
    from mastapy._private.gears.gear_designs.face._1122 import FaceGearSetMicroGeometry
    from mastapy._private.gears.gear_designs.face._1123 import FaceGearWheelDesign
else:
    import sys as __sys

    from lazy_imports import LazyImporter as __LazyImporter

    __import_structure = {
        "_private.gears.gear_designs.face._1115": ["FaceGearDesign"],
        "_private.gears.gear_designs.face._1116": [
            "FaceGearDiameterFaceWidthSpecificationMethod"
        ],
        "_private.gears.gear_designs.face._1117": ["FaceGearMeshDesign"],
        "_private.gears.gear_designs.face._1118": ["FaceGearMeshMicroGeometry"],
        "_private.gears.gear_designs.face._1119": ["FaceGearMicroGeometry"],
        "_private.gears.gear_designs.face._1120": ["FaceGearPinionDesign"],
        "_private.gears.gear_designs.face._1121": ["FaceGearSetDesign"],
        "_private.gears.gear_designs.face._1122": ["FaceGearSetMicroGeometry"],
        "_private.gears.gear_designs.face._1123": ["FaceGearWheelDesign"],
    }

    __sys.modules[__name__] = __LazyImporter(
        "mastapy",
        globals()["__file__"],
        __import_structure,
    )

__all__ = (
    "FaceGearDesign",
    "FaceGearDiameterFaceWidthSpecificationMethod",
    "FaceGearMeshDesign",
    "FaceGearMeshMicroGeometry",
    "FaceGearMicroGeometry",
    "FaceGearPinionDesign",
    "FaceGearSetDesign",
    "FaceGearSetMicroGeometry",
    "FaceGearWheelDesign",
)
