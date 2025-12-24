"""Subpackage."""

from typing import TYPE_CHECKING as __tc

if __tc:
    from mastapy._private.gears.gear_designs.conical._1296 import ActiveConicalFlank
    from mastapy._private.gears.gear_designs.conical._1297 import (
        BacklashDistributionRule,
    )
    from mastapy._private.gears.gear_designs.conical._1298 import ConicalFlanks
    from mastapy._private.gears.gear_designs.conical._1299 import ConicalGearCutter
    from mastapy._private.gears.gear_designs.conical._1300 import ConicalGearDesign
    from mastapy._private.gears.gear_designs.conical._1301 import ConicalGearMeshDesign
    from mastapy._private.gears.gear_designs.conical._1302 import ConicalGearSetDesign
    from mastapy._private.gears.gear_designs.conical._1303 import (
        ConicalMachineSettingCalculationMethods,
    )
    from mastapy._private.gears.gear_designs.conical._1304 import (
        ConicalManufactureMethods,
    )
    from mastapy._private.gears.gear_designs.conical._1305 import (
        ConicalMeshedGearDesign,
    )
    from mastapy._private.gears.gear_designs.conical._1306 import (
        ConicalMeshMisalignments,
    )
    from mastapy._private.gears.gear_designs.conical._1307 import CutterBladeType
    from mastapy._private.gears.gear_designs.conical._1308 import CutterGaugeLengths
    from mastapy._private.gears.gear_designs.conical._1309 import DummyConicalGearCutter
    from mastapy._private.gears.gear_designs.conical._1310 import FrontEndTypes
    from mastapy._private.gears.gear_designs.conical._1311 import (
        GleasonSafetyRequirements,
    )
    from mastapy._private.gears.gear_designs.conical._1312 import (
        KIMoSBevelHypoidSingleLoadCaseResultsData,
    )
    from mastapy._private.gears.gear_designs.conical._1313 import (
        KIMoSBevelHypoidSingleRotationAngleResult,
    )
    from mastapy._private.gears.gear_designs.conical._1314 import (
        KlingelnbergFinishingMethods,
    )
    from mastapy._private.gears.gear_designs.conical._1315 import (
        LoadDistributionFactorMethods,
    )
    from mastapy._private.gears.gear_designs.conical._1316 import TopremEntryType
    from mastapy._private.gears.gear_designs.conical._1317 import TopremLetter
else:
    import sys as __sys

    from lazy_imports import LazyImporter as __LazyImporter

    __import_structure = {
        "_private.gears.gear_designs.conical._1296": ["ActiveConicalFlank"],
        "_private.gears.gear_designs.conical._1297": ["BacklashDistributionRule"],
        "_private.gears.gear_designs.conical._1298": ["ConicalFlanks"],
        "_private.gears.gear_designs.conical._1299": ["ConicalGearCutter"],
        "_private.gears.gear_designs.conical._1300": ["ConicalGearDesign"],
        "_private.gears.gear_designs.conical._1301": ["ConicalGearMeshDesign"],
        "_private.gears.gear_designs.conical._1302": ["ConicalGearSetDesign"],
        "_private.gears.gear_designs.conical._1303": [
            "ConicalMachineSettingCalculationMethods"
        ],
        "_private.gears.gear_designs.conical._1304": ["ConicalManufactureMethods"],
        "_private.gears.gear_designs.conical._1305": ["ConicalMeshedGearDesign"],
        "_private.gears.gear_designs.conical._1306": ["ConicalMeshMisalignments"],
        "_private.gears.gear_designs.conical._1307": ["CutterBladeType"],
        "_private.gears.gear_designs.conical._1308": ["CutterGaugeLengths"],
        "_private.gears.gear_designs.conical._1309": ["DummyConicalGearCutter"],
        "_private.gears.gear_designs.conical._1310": ["FrontEndTypes"],
        "_private.gears.gear_designs.conical._1311": ["GleasonSafetyRequirements"],
        "_private.gears.gear_designs.conical._1312": [
            "KIMoSBevelHypoidSingleLoadCaseResultsData"
        ],
        "_private.gears.gear_designs.conical._1313": [
            "KIMoSBevelHypoidSingleRotationAngleResult"
        ],
        "_private.gears.gear_designs.conical._1314": ["KlingelnbergFinishingMethods"],
        "_private.gears.gear_designs.conical._1315": ["LoadDistributionFactorMethods"],
        "_private.gears.gear_designs.conical._1316": ["TopremEntryType"],
        "_private.gears.gear_designs.conical._1317": ["TopremLetter"],
    }

    __sys.modules[__name__] = __LazyImporter(
        "mastapy",
        globals()["__file__"],
        __import_structure,
    )

__all__ = (
    "ActiveConicalFlank",
    "BacklashDistributionRule",
    "ConicalFlanks",
    "ConicalGearCutter",
    "ConicalGearDesign",
    "ConicalGearMeshDesign",
    "ConicalGearSetDesign",
    "ConicalMachineSettingCalculationMethods",
    "ConicalManufactureMethods",
    "ConicalMeshedGearDesign",
    "ConicalMeshMisalignments",
    "CutterBladeType",
    "CutterGaugeLengths",
    "DummyConicalGearCutter",
    "FrontEndTypes",
    "GleasonSafetyRequirements",
    "KIMoSBevelHypoidSingleLoadCaseResultsData",
    "KIMoSBevelHypoidSingleRotationAngleResult",
    "KlingelnbergFinishingMethods",
    "LoadDistributionFactorMethods",
    "TopremEntryType",
    "TopremLetter",
)
