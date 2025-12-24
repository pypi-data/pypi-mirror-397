"""Subpackage."""

from typing import TYPE_CHECKING as __tc

if __tc:
    from mastapy._private.gears.gear_designs.bevel._1325 import (
        AGMAGleasonConicalGearGeometryMethods,
    )
    from mastapy._private.gears.gear_designs.bevel._1326 import BevelGearDesign
    from mastapy._private.gears.gear_designs.bevel._1327 import BevelGearMeshDesign
    from mastapy._private.gears.gear_designs.bevel._1328 import BevelGearSetDesign
    from mastapy._private.gears.gear_designs.bevel._1329 import BevelMeshedGearDesign
    from mastapy._private.gears.gear_designs.bevel._1330 import (
        DrivenMachineCharacteristicGleason,
    )
    from mastapy._private.gears.gear_designs.bevel._1331 import EdgeRadiusType
    from mastapy._private.gears.gear_designs.bevel._1332 import FinishingMethods
    from mastapy._private.gears.gear_designs.bevel._1333 import (
        MachineCharacteristicAGMAKlingelnberg,
    )
    from mastapy._private.gears.gear_designs.bevel._1334 import (
        PrimeMoverCharacteristicGleason,
    )
    from mastapy._private.gears.gear_designs.bevel._1335 import (
        ToothProportionsInputMethod,
    )
    from mastapy._private.gears.gear_designs.bevel._1336 import (
        ToothThicknessSpecificationMethod,
    )
    from mastapy._private.gears.gear_designs.bevel._1337 import (
        WheelFinishCutterPointWidthRestrictionMethod,
    )
else:
    import sys as __sys

    from lazy_imports import LazyImporter as __LazyImporter

    __import_structure = {
        "_private.gears.gear_designs.bevel._1325": [
            "AGMAGleasonConicalGearGeometryMethods"
        ],
        "_private.gears.gear_designs.bevel._1326": ["BevelGearDesign"],
        "_private.gears.gear_designs.bevel._1327": ["BevelGearMeshDesign"],
        "_private.gears.gear_designs.bevel._1328": ["BevelGearSetDesign"],
        "_private.gears.gear_designs.bevel._1329": ["BevelMeshedGearDesign"],
        "_private.gears.gear_designs.bevel._1330": [
            "DrivenMachineCharacteristicGleason"
        ],
        "_private.gears.gear_designs.bevel._1331": ["EdgeRadiusType"],
        "_private.gears.gear_designs.bevel._1332": ["FinishingMethods"],
        "_private.gears.gear_designs.bevel._1333": [
            "MachineCharacteristicAGMAKlingelnberg"
        ],
        "_private.gears.gear_designs.bevel._1334": ["PrimeMoverCharacteristicGleason"],
        "_private.gears.gear_designs.bevel._1335": ["ToothProportionsInputMethod"],
        "_private.gears.gear_designs.bevel._1336": [
            "ToothThicknessSpecificationMethod"
        ],
        "_private.gears.gear_designs.bevel._1337": [
            "WheelFinishCutterPointWidthRestrictionMethod"
        ],
    }

    __sys.modules[__name__] = __LazyImporter(
        "mastapy",
        globals()["__file__"],
        __import_structure,
    )

__all__ = (
    "AGMAGleasonConicalGearGeometryMethods",
    "BevelGearDesign",
    "BevelGearMeshDesign",
    "BevelGearSetDesign",
    "BevelMeshedGearDesign",
    "DrivenMachineCharacteristicGleason",
    "EdgeRadiusType",
    "FinishingMethods",
    "MachineCharacteristicAGMAKlingelnberg",
    "PrimeMoverCharacteristicGleason",
    "ToothProportionsInputMethod",
    "ToothThicknessSpecificationMethod",
    "WheelFinishCutterPointWidthRestrictionMethod",
)
