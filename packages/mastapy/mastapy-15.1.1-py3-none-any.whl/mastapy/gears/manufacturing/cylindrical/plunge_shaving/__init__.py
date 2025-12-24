"""Subpackage."""

from typing import TYPE_CHECKING as __tc

if __tc:
    from mastapy._private.gears.manufacturing.cylindrical.plunge_shaving._768 import (
        CalculationError,
    )
    from mastapy._private.gears.manufacturing.cylindrical.plunge_shaving._769 import (
        ChartType,
    )
    from mastapy._private.gears.manufacturing.cylindrical.plunge_shaving._770 import (
        GearPointCalculationError,
    )
    from mastapy._private.gears.manufacturing.cylindrical.plunge_shaving._771 import (
        MicroGeometryDefinitionMethod,
    )
    from mastapy._private.gears.manufacturing.cylindrical.plunge_shaving._772 import (
        MicroGeometryDefinitionType,
    )
    from mastapy._private.gears.manufacturing.cylindrical.plunge_shaving._773 import (
        PlungeShaverCalculation,
    )
    from mastapy._private.gears.manufacturing.cylindrical.plunge_shaving._774 import (
        PlungeShaverCalculationInputs,
    )
    from mastapy._private.gears.manufacturing.cylindrical.plunge_shaving._775 import (
        PlungeShaverGeneration,
    )
    from mastapy._private.gears.manufacturing.cylindrical.plunge_shaving._776 import (
        PlungeShaverInputsAndMicroGeometry,
    )
    from mastapy._private.gears.manufacturing.cylindrical.plunge_shaving._777 import (
        PlungeShaverOutputs,
    )
    from mastapy._private.gears.manufacturing.cylindrical.plunge_shaving._778 import (
        PlungeShaverSettings,
    )
    from mastapy._private.gears.manufacturing.cylindrical.plunge_shaving._779 import (
        PointOfInterest,
    )
    from mastapy._private.gears.manufacturing.cylindrical.plunge_shaving._780 import (
        RealPlungeShaverOutputs,
    )
    from mastapy._private.gears.manufacturing.cylindrical.plunge_shaving._781 import (
        ShaverPointCalculationError,
    )
    from mastapy._private.gears.manufacturing.cylindrical.plunge_shaving._782 import (
        ShaverPointOfInterest,
    )
    from mastapy._private.gears.manufacturing.cylindrical.plunge_shaving._783 import (
        VirtualPlungeShaverOutputs,
    )
else:
    import sys as __sys

    from lazy_imports import LazyImporter as __LazyImporter

    __import_structure = {
        "_private.gears.manufacturing.cylindrical.plunge_shaving._768": [
            "CalculationError"
        ],
        "_private.gears.manufacturing.cylindrical.plunge_shaving._769": ["ChartType"],
        "_private.gears.manufacturing.cylindrical.plunge_shaving._770": [
            "GearPointCalculationError"
        ],
        "_private.gears.manufacturing.cylindrical.plunge_shaving._771": [
            "MicroGeometryDefinitionMethod"
        ],
        "_private.gears.manufacturing.cylindrical.plunge_shaving._772": [
            "MicroGeometryDefinitionType"
        ],
        "_private.gears.manufacturing.cylindrical.plunge_shaving._773": [
            "PlungeShaverCalculation"
        ],
        "_private.gears.manufacturing.cylindrical.plunge_shaving._774": [
            "PlungeShaverCalculationInputs"
        ],
        "_private.gears.manufacturing.cylindrical.plunge_shaving._775": [
            "PlungeShaverGeneration"
        ],
        "_private.gears.manufacturing.cylindrical.plunge_shaving._776": [
            "PlungeShaverInputsAndMicroGeometry"
        ],
        "_private.gears.manufacturing.cylindrical.plunge_shaving._777": [
            "PlungeShaverOutputs"
        ],
        "_private.gears.manufacturing.cylindrical.plunge_shaving._778": [
            "PlungeShaverSettings"
        ],
        "_private.gears.manufacturing.cylindrical.plunge_shaving._779": [
            "PointOfInterest"
        ],
        "_private.gears.manufacturing.cylindrical.plunge_shaving._780": [
            "RealPlungeShaverOutputs"
        ],
        "_private.gears.manufacturing.cylindrical.plunge_shaving._781": [
            "ShaverPointCalculationError"
        ],
        "_private.gears.manufacturing.cylindrical.plunge_shaving._782": [
            "ShaverPointOfInterest"
        ],
        "_private.gears.manufacturing.cylindrical.plunge_shaving._783": [
            "VirtualPlungeShaverOutputs"
        ],
    }

    __sys.modules[__name__] = __LazyImporter(
        "mastapy",
        globals()["__file__"],
        __import_structure,
    )

__all__ = (
    "CalculationError",
    "ChartType",
    "GearPointCalculationError",
    "MicroGeometryDefinitionMethod",
    "MicroGeometryDefinitionType",
    "PlungeShaverCalculation",
    "PlungeShaverCalculationInputs",
    "PlungeShaverGeneration",
    "PlungeShaverInputsAndMicroGeometry",
    "PlungeShaverOutputs",
    "PlungeShaverSettings",
    "PointOfInterest",
    "RealPlungeShaverOutputs",
    "ShaverPointCalculationError",
    "ShaverPointOfInterest",
    "VirtualPlungeShaverOutputs",
)
