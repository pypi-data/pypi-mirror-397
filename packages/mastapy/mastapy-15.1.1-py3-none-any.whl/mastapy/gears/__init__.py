"""Subpackage."""

from typing import TYPE_CHECKING as __tc

if __tc:
    from mastapy._private.gears._420 import AccuracyGrades
    from mastapy._private.gears._421 import AGMAToleranceStandard
    from mastapy._private.gears._422 import BevelHypoidGearDesignSettings
    from mastapy._private.gears._423 import BevelHypoidGearRatingSettings
    from mastapy._private.gears._424 import CentreDistanceChangeMethod
    from mastapy._private.gears._425 import CoefficientOfFrictionCalculationMethod
    from mastapy._private.gears._426 import ConicalGearToothSurface
    from mastapy._private.gears._427 import ContactRatioDataSource
    from mastapy._private.gears._428 import ContactRatioRequirements
    from mastapy._private.gears._429 import CylindricalFlanks
    from mastapy._private.gears._430 import CylindricalMisalignmentDataSource
    from mastapy._private.gears._431 import DeflectionFromBendingOption
    from mastapy._private.gears._432 import DINToleranceStandard
    from mastapy._private.gears._433 import GearFlanks
    from mastapy._private.gears._434 import GearNURBSSurface
    from mastapy._private.gears._435 import GearSetDesignGroup
    from mastapy._private.gears._436 import GearSetModes
    from mastapy._private.gears._437 import GearSetOptimisationResult
    from mastapy._private.gears._438 import GearSetOptimisationResults
    from mastapy._private.gears._439 import GearSetOptimiser
    from mastapy._private.gears._440 import GearWindageAndChurningLossCalculationMethod
    from mastapy._private.gears._441 import Hand
    from mastapy._private.gears._442 import ISOToleranceStandard
    from mastapy._private.gears._443 import LubricationMethodForNoLoadLossesCalc
    from mastapy._private.gears._444 import LubricationMethods
    from mastapy._private.gears._445 import MicroGeometryInputTypes
    from mastapy._private.gears._446 import MicroGeometryModel
    from mastapy._private.gears._447 import (
        MicropittingCoefficientOfFrictionCalculationMethod,
    )
    from mastapy._private.gears._448 import NamedPlanetAngle
    from mastapy._private.gears._449 import GearMeshOilInjectionDirection
    from mastapy._private.gears._450 import OilJetFlowRateSpecificationMethod
    from mastapy._private.gears._451 import OilJetVelocitySpecificationMethod
    from mastapy._private.gears._452 import PlanetaryDetail
    from mastapy._private.gears._453 import PlanetaryRatingLoadSharingOption
    from mastapy._private.gears._454 import PocketingPowerLossCoefficients
    from mastapy._private.gears._455 import PocketingPowerLossCoefficientsDatabase
    from mastapy._private.gears._456 import QualityGradeTypes
    from mastapy._private.gears._457 import SafetyRequirementsAGMA
    from mastapy._private.gears._458 import (
        SpecificationForTheEffectOfOilKinematicViscosity,
    )
    from mastapy._private.gears._459 import SpiralBevelRootLineTilt
    from mastapy._private.gears._460 import SpiralBevelToothTaper
    from mastapy._private.gears._461 import TESpecificationType
    from mastapy._private.gears._462 import WormAddendumFactor
    from mastapy._private.gears._463 import WormType
    from mastapy._private.gears._464 import ZerolBevelGleasonToothTaperOption
else:
    import sys as __sys

    from lazy_imports import LazyImporter as __LazyImporter

    __import_structure = {
        "_private.gears._420": ["AccuracyGrades"],
        "_private.gears._421": ["AGMAToleranceStandard"],
        "_private.gears._422": ["BevelHypoidGearDesignSettings"],
        "_private.gears._423": ["BevelHypoidGearRatingSettings"],
        "_private.gears._424": ["CentreDistanceChangeMethod"],
        "_private.gears._425": ["CoefficientOfFrictionCalculationMethod"],
        "_private.gears._426": ["ConicalGearToothSurface"],
        "_private.gears._427": ["ContactRatioDataSource"],
        "_private.gears._428": ["ContactRatioRequirements"],
        "_private.gears._429": ["CylindricalFlanks"],
        "_private.gears._430": ["CylindricalMisalignmentDataSource"],
        "_private.gears._431": ["DeflectionFromBendingOption"],
        "_private.gears._432": ["DINToleranceStandard"],
        "_private.gears._433": ["GearFlanks"],
        "_private.gears._434": ["GearNURBSSurface"],
        "_private.gears._435": ["GearSetDesignGroup"],
        "_private.gears._436": ["GearSetModes"],
        "_private.gears._437": ["GearSetOptimisationResult"],
        "_private.gears._438": ["GearSetOptimisationResults"],
        "_private.gears._439": ["GearSetOptimiser"],
        "_private.gears._440": ["GearWindageAndChurningLossCalculationMethod"],
        "_private.gears._441": ["Hand"],
        "_private.gears._442": ["ISOToleranceStandard"],
        "_private.gears._443": ["LubricationMethodForNoLoadLossesCalc"],
        "_private.gears._444": ["LubricationMethods"],
        "_private.gears._445": ["MicroGeometryInputTypes"],
        "_private.gears._446": ["MicroGeometryModel"],
        "_private.gears._447": ["MicropittingCoefficientOfFrictionCalculationMethod"],
        "_private.gears._448": ["NamedPlanetAngle"],
        "_private.gears._449": ["GearMeshOilInjectionDirection"],
        "_private.gears._450": ["OilJetFlowRateSpecificationMethod"],
        "_private.gears._451": ["OilJetVelocitySpecificationMethod"],
        "_private.gears._452": ["PlanetaryDetail"],
        "_private.gears._453": ["PlanetaryRatingLoadSharingOption"],
        "_private.gears._454": ["PocketingPowerLossCoefficients"],
        "_private.gears._455": ["PocketingPowerLossCoefficientsDatabase"],
        "_private.gears._456": ["QualityGradeTypes"],
        "_private.gears._457": ["SafetyRequirementsAGMA"],
        "_private.gears._458": ["SpecificationForTheEffectOfOilKinematicViscosity"],
        "_private.gears._459": ["SpiralBevelRootLineTilt"],
        "_private.gears._460": ["SpiralBevelToothTaper"],
        "_private.gears._461": ["TESpecificationType"],
        "_private.gears._462": ["WormAddendumFactor"],
        "_private.gears._463": ["WormType"],
        "_private.gears._464": ["ZerolBevelGleasonToothTaperOption"],
    }

    __sys.modules[__name__] = __LazyImporter(
        "mastapy",
        globals()["__file__"],
        __import_structure,
    )

__all__ = (
    "AccuracyGrades",
    "AGMAToleranceStandard",
    "BevelHypoidGearDesignSettings",
    "BevelHypoidGearRatingSettings",
    "CentreDistanceChangeMethod",
    "CoefficientOfFrictionCalculationMethod",
    "ConicalGearToothSurface",
    "ContactRatioDataSource",
    "ContactRatioRequirements",
    "CylindricalFlanks",
    "CylindricalMisalignmentDataSource",
    "DeflectionFromBendingOption",
    "DINToleranceStandard",
    "GearFlanks",
    "GearNURBSSurface",
    "GearSetDesignGroup",
    "GearSetModes",
    "GearSetOptimisationResult",
    "GearSetOptimisationResults",
    "GearSetOptimiser",
    "GearWindageAndChurningLossCalculationMethod",
    "Hand",
    "ISOToleranceStandard",
    "LubricationMethodForNoLoadLossesCalc",
    "LubricationMethods",
    "MicroGeometryInputTypes",
    "MicroGeometryModel",
    "MicropittingCoefficientOfFrictionCalculationMethod",
    "NamedPlanetAngle",
    "GearMeshOilInjectionDirection",
    "OilJetFlowRateSpecificationMethod",
    "OilJetVelocitySpecificationMethod",
    "PlanetaryDetail",
    "PlanetaryRatingLoadSharingOption",
    "PocketingPowerLossCoefficients",
    "PocketingPowerLossCoefficientsDatabase",
    "QualityGradeTypes",
    "SafetyRequirementsAGMA",
    "SpecificationForTheEffectOfOilKinematicViscosity",
    "SpiralBevelRootLineTilt",
    "SpiralBevelToothTaper",
    "TESpecificationType",
    "WormAddendumFactor",
    "WormType",
    "ZerolBevelGleasonToothTaperOption",
)
