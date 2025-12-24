"""Subpackage."""

from typing import TYPE_CHECKING as __tc

if __tc:
    from mastapy._private.gears.manufacturing.cylindrical.cutter_simulation._857 import (
        CutterSimulationCalc,
    )
    from mastapy._private.gears.manufacturing.cylindrical.cutter_simulation._858 import (
        CylindricalCutterSimulatableGear,
    )
    from mastapy._private.gears.manufacturing.cylindrical.cutter_simulation._859 import (
        CylindricalGearSpecification,
    )
    from mastapy._private.gears.manufacturing.cylindrical.cutter_simulation._860 import (
        CylindricalManufacturedRealGearInMesh,
    )
    from mastapy._private.gears.manufacturing.cylindrical.cutter_simulation._861 import (
        CylindricalManufacturedVirtualGearInMesh,
    )
    from mastapy._private.gears.manufacturing.cylindrical.cutter_simulation._862 import (
        FinishCutterSimulation,
    )
    from mastapy._private.gears.manufacturing.cylindrical.cutter_simulation._863 import (
        FinishStockPoint,
    )
    from mastapy._private.gears.manufacturing.cylindrical.cutter_simulation._864 import (
        FormWheelGrindingSimulationCalculator,
    )
    from mastapy._private.gears.manufacturing.cylindrical.cutter_simulation._865 import (
        GearCutterSimulation,
    )
    from mastapy._private.gears.manufacturing.cylindrical.cutter_simulation._866 import (
        HobSimulationCalculator,
    )
    from mastapy._private.gears.manufacturing.cylindrical.cutter_simulation._867 import (
        ManufacturingOperationConstraints,
    )
    from mastapy._private.gears.manufacturing.cylindrical.cutter_simulation._868 import (
        ManufacturingProcessControls,
    )
    from mastapy._private.gears.manufacturing.cylindrical.cutter_simulation._869 import (
        RackSimulationCalculator,
    )
    from mastapy._private.gears.manufacturing.cylindrical.cutter_simulation._870 import (
        RoughCutterSimulation,
    )
    from mastapy._private.gears.manufacturing.cylindrical.cutter_simulation._871 import (
        ShaperSimulationCalculator,
    )
    from mastapy._private.gears.manufacturing.cylindrical.cutter_simulation._872 import (
        ShavingSimulationCalculator,
    )
    from mastapy._private.gears.manufacturing.cylindrical.cutter_simulation._873 import (
        VirtualSimulationCalculator,
    )
    from mastapy._private.gears.manufacturing.cylindrical.cutter_simulation._874 import (
        WormGrinderSimulationCalculator,
    )
else:
    import sys as __sys

    from lazy_imports import LazyImporter as __LazyImporter

    __import_structure = {
        "_private.gears.manufacturing.cylindrical.cutter_simulation._857": [
            "CutterSimulationCalc"
        ],
        "_private.gears.manufacturing.cylindrical.cutter_simulation._858": [
            "CylindricalCutterSimulatableGear"
        ],
        "_private.gears.manufacturing.cylindrical.cutter_simulation._859": [
            "CylindricalGearSpecification"
        ],
        "_private.gears.manufacturing.cylindrical.cutter_simulation._860": [
            "CylindricalManufacturedRealGearInMesh"
        ],
        "_private.gears.manufacturing.cylindrical.cutter_simulation._861": [
            "CylindricalManufacturedVirtualGearInMesh"
        ],
        "_private.gears.manufacturing.cylindrical.cutter_simulation._862": [
            "FinishCutterSimulation"
        ],
        "_private.gears.manufacturing.cylindrical.cutter_simulation._863": [
            "FinishStockPoint"
        ],
        "_private.gears.manufacturing.cylindrical.cutter_simulation._864": [
            "FormWheelGrindingSimulationCalculator"
        ],
        "_private.gears.manufacturing.cylindrical.cutter_simulation._865": [
            "GearCutterSimulation"
        ],
        "_private.gears.manufacturing.cylindrical.cutter_simulation._866": [
            "HobSimulationCalculator"
        ],
        "_private.gears.manufacturing.cylindrical.cutter_simulation._867": [
            "ManufacturingOperationConstraints"
        ],
        "_private.gears.manufacturing.cylindrical.cutter_simulation._868": [
            "ManufacturingProcessControls"
        ],
        "_private.gears.manufacturing.cylindrical.cutter_simulation._869": [
            "RackSimulationCalculator"
        ],
        "_private.gears.manufacturing.cylindrical.cutter_simulation._870": [
            "RoughCutterSimulation"
        ],
        "_private.gears.manufacturing.cylindrical.cutter_simulation._871": [
            "ShaperSimulationCalculator"
        ],
        "_private.gears.manufacturing.cylindrical.cutter_simulation._872": [
            "ShavingSimulationCalculator"
        ],
        "_private.gears.manufacturing.cylindrical.cutter_simulation._873": [
            "VirtualSimulationCalculator"
        ],
        "_private.gears.manufacturing.cylindrical.cutter_simulation._874": [
            "WormGrinderSimulationCalculator"
        ],
    }

    __sys.modules[__name__] = __LazyImporter(
        "mastapy",
        globals()["__file__"],
        __import_structure,
    )

__all__ = (
    "CutterSimulationCalc",
    "CylindricalCutterSimulatableGear",
    "CylindricalGearSpecification",
    "CylindricalManufacturedRealGearInMesh",
    "CylindricalManufacturedVirtualGearInMesh",
    "FinishCutterSimulation",
    "FinishStockPoint",
    "FormWheelGrindingSimulationCalculator",
    "GearCutterSimulation",
    "HobSimulationCalculator",
    "ManufacturingOperationConstraints",
    "ManufacturingProcessControls",
    "RackSimulationCalculator",
    "RoughCutterSimulation",
    "ShaperSimulationCalculator",
    "ShavingSimulationCalculator",
    "VirtualSimulationCalculator",
    "WormGrinderSimulationCalculator",
)
