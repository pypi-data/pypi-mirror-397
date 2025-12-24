"""Subpackage."""

from typing import TYPE_CHECKING as __tc

if __tc:
    from mastapy._private.gears.rating.cylindrical._564 import AGMAScuffingResultsRow
    from mastapy._private.gears.rating.cylindrical._565 import (
        CylindricalGearDesignAndRatingSettings,
    )
    from mastapy._private.gears.rating.cylindrical._566 import (
        CylindricalGearDesignAndRatingSettingsDatabase,
    )
    from mastapy._private.gears.rating.cylindrical._567 import (
        CylindricalGearDesignAndRatingSettingsItem,
    )
    from mastapy._private.gears.rating.cylindrical._568 import (
        CylindricalGearDutyCycleRating,
    )
    from mastapy._private.gears.rating.cylindrical._569 import (
        CylindricalGearFlankDutyCycleRating,
    )
    from mastapy._private.gears.rating.cylindrical._570 import (
        CylindricalGearFlankRating,
    )
    from mastapy._private.gears.rating.cylindrical._571 import CylindricalGearMeshRating
    from mastapy._private.gears.rating.cylindrical._572 import (
        CylindricalGearMicroPittingResults,
    )
    from mastapy._private.gears.rating.cylindrical._573 import CylindricalGearRating
    from mastapy._private.gears.rating.cylindrical._574 import (
        CylindricalGearRatingGeometryDataSource,
    )
    from mastapy._private.gears.rating.cylindrical._575 import (
        CylindricalGearScuffingResults,
    )
    from mastapy._private.gears.rating.cylindrical._576 import (
        CylindricalGearSetDutyCycleRating,
    )
    from mastapy._private.gears.rating.cylindrical._577 import CylindricalGearSetRating
    from mastapy._private.gears.rating.cylindrical._578 import (
        CylindricalGearSingleFlankRating,
    )
    from mastapy._private.gears.rating.cylindrical._579 import (
        CylindricalMeshDutyCycleRating,
    )
    from mastapy._private.gears.rating.cylindrical._580 import (
        CylindricalMeshSingleFlankRating,
    )
    from mastapy._private.gears.rating.cylindrical._581 import (
        CylindricalPlasticGearRatingSettings,
    )
    from mastapy._private.gears.rating.cylindrical._582 import (
        CylindricalPlasticGearRatingSettingsDatabase,
    )
    from mastapy._private.gears.rating.cylindrical._583 import (
        CylindricalPlasticGearRatingSettingsItem,
    )
    from mastapy._private.gears.rating.cylindrical._584 import CylindricalRateableMesh
    from mastapy._private.gears.rating.cylindrical._585 import DynamicFactorMethods
    from mastapy._private.gears.rating.cylindrical._586 import (
        GearBlankFactorCalculationOptions,
    )
    from mastapy._private.gears.rating.cylindrical._587 import ISOScuffingResultsRow
    from mastapy._private.gears.rating.cylindrical._588 import MeshRatingForReports
    from mastapy._private.gears.rating.cylindrical._589 import MicropittingRatingMethod
    from mastapy._private.gears.rating.cylindrical._590 import MicroPittingResultsRow
    from mastapy._private.gears.rating.cylindrical._591 import (
        MisalignmentContactPatternEnhancements,
    )
    from mastapy._private.gears.rating.cylindrical._592 import RatingMethod
    from mastapy._private.gears.rating.cylindrical._593 import (
        ReducedCylindricalGearSetDutyCycleRating,
    )
    from mastapy._private.gears.rating.cylindrical._594 import (
        ScuffingFlashTemperatureRatingMethod,
    )
    from mastapy._private.gears.rating.cylindrical._595 import (
        ScuffingIntegralTemperatureRatingMethod,
    )
    from mastapy._private.gears.rating.cylindrical._596 import ScuffingMethods
    from mastapy._private.gears.rating.cylindrical._597 import ScuffingResultsRow
    from mastapy._private.gears.rating.cylindrical._598 import ScuffingResultsRowGear
    from mastapy._private.gears.rating.cylindrical._599 import TipReliefScuffingOptions
    from mastapy._private.gears.rating.cylindrical._600 import ToothThicknesses
    from mastapy._private.gears.rating.cylindrical._601 import (
        VDI2737SafetyFactorReportingObject,
    )
else:
    import sys as __sys

    from lazy_imports import LazyImporter as __LazyImporter

    __import_structure = {
        "_private.gears.rating.cylindrical._564": ["AGMAScuffingResultsRow"],
        "_private.gears.rating.cylindrical._565": [
            "CylindricalGearDesignAndRatingSettings"
        ],
        "_private.gears.rating.cylindrical._566": [
            "CylindricalGearDesignAndRatingSettingsDatabase"
        ],
        "_private.gears.rating.cylindrical._567": [
            "CylindricalGearDesignAndRatingSettingsItem"
        ],
        "_private.gears.rating.cylindrical._568": ["CylindricalGearDutyCycleRating"],
        "_private.gears.rating.cylindrical._569": [
            "CylindricalGearFlankDutyCycleRating"
        ],
        "_private.gears.rating.cylindrical._570": ["CylindricalGearFlankRating"],
        "_private.gears.rating.cylindrical._571": ["CylindricalGearMeshRating"],
        "_private.gears.rating.cylindrical._572": [
            "CylindricalGearMicroPittingResults"
        ],
        "_private.gears.rating.cylindrical._573": ["CylindricalGearRating"],
        "_private.gears.rating.cylindrical._574": [
            "CylindricalGearRatingGeometryDataSource"
        ],
        "_private.gears.rating.cylindrical._575": ["CylindricalGearScuffingResults"],
        "_private.gears.rating.cylindrical._576": ["CylindricalGearSetDutyCycleRating"],
        "_private.gears.rating.cylindrical._577": ["CylindricalGearSetRating"],
        "_private.gears.rating.cylindrical._578": ["CylindricalGearSingleFlankRating"],
        "_private.gears.rating.cylindrical._579": ["CylindricalMeshDutyCycleRating"],
        "_private.gears.rating.cylindrical._580": ["CylindricalMeshSingleFlankRating"],
        "_private.gears.rating.cylindrical._581": [
            "CylindricalPlasticGearRatingSettings"
        ],
        "_private.gears.rating.cylindrical._582": [
            "CylindricalPlasticGearRatingSettingsDatabase"
        ],
        "_private.gears.rating.cylindrical._583": [
            "CylindricalPlasticGearRatingSettingsItem"
        ],
        "_private.gears.rating.cylindrical._584": ["CylindricalRateableMesh"],
        "_private.gears.rating.cylindrical._585": ["DynamicFactorMethods"],
        "_private.gears.rating.cylindrical._586": ["GearBlankFactorCalculationOptions"],
        "_private.gears.rating.cylindrical._587": ["ISOScuffingResultsRow"],
        "_private.gears.rating.cylindrical._588": ["MeshRatingForReports"],
        "_private.gears.rating.cylindrical._589": ["MicropittingRatingMethod"],
        "_private.gears.rating.cylindrical._590": ["MicroPittingResultsRow"],
        "_private.gears.rating.cylindrical._591": [
            "MisalignmentContactPatternEnhancements"
        ],
        "_private.gears.rating.cylindrical._592": ["RatingMethod"],
        "_private.gears.rating.cylindrical._593": [
            "ReducedCylindricalGearSetDutyCycleRating"
        ],
        "_private.gears.rating.cylindrical._594": [
            "ScuffingFlashTemperatureRatingMethod"
        ],
        "_private.gears.rating.cylindrical._595": [
            "ScuffingIntegralTemperatureRatingMethod"
        ],
        "_private.gears.rating.cylindrical._596": ["ScuffingMethods"],
        "_private.gears.rating.cylindrical._597": ["ScuffingResultsRow"],
        "_private.gears.rating.cylindrical._598": ["ScuffingResultsRowGear"],
        "_private.gears.rating.cylindrical._599": ["TipReliefScuffingOptions"],
        "_private.gears.rating.cylindrical._600": ["ToothThicknesses"],
        "_private.gears.rating.cylindrical._601": [
            "VDI2737SafetyFactorReportingObject"
        ],
    }

    __sys.modules[__name__] = __LazyImporter(
        "mastapy",
        globals()["__file__"],
        __import_structure,
    )

__all__ = (
    "AGMAScuffingResultsRow",
    "CylindricalGearDesignAndRatingSettings",
    "CylindricalGearDesignAndRatingSettingsDatabase",
    "CylindricalGearDesignAndRatingSettingsItem",
    "CylindricalGearDutyCycleRating",
    "CylindricalGearFlankDutyCycleRating",
    "CylindricalGearFlankRating",
    "CylindricalGearMeshRating",
    "CylindricalGearMicroPittingResults",
    "CylindricalGearRating",
    "CylindricalGearRatingGeometryDataSource",
    "CylindricalGearScuffingResults",
    "CylindricalGearSetDutyCycleRating",
    "CylindricalGearSetRating",
    "CylindricalGearSingleFlankRating",
    "CylindricalMeshDutyCycleRating",
    "CylindricalMeshSingleFlankRating",
    "CylindricalPlasticGearRatingSettings",
    "CylindricalPlasticGearRatingSettingsDatabase",
    "CylindricalPlasticGearRatingSettingsItem",
    "CylindricalRateableMesh",
    "DynamicFactorMethods",
    "GearBlankFactorCalculationOptions",
    "ISOScuffingResultsRow",
    "MeshRatingForReports",
    "MicropittingRatingMethod",
    "MicroPittingResultsRow",
    "MisalignmentContactPatternEnhancements",
    "RatingMethod",
    "ReducedCylindricalGearSetDutyCycleRating",
    "ScuffingFlashTemperatureRatingMethod",
    "ScuffingIntegralTemperatureRatingMethod",
    "ScuffingMethods",
    "ScuffingResultsRow",
    "ScuffingResultsRowGear",
    "TipReliefScuffingOptions",
    "ToothThicknesses",
    "VDI2737SafetyFactorReportingObject",
)
