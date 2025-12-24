"""Subpackage."""

from typing import TYPE_CHECKING as __tc

if __tc:
    from mastapy._private.materials._336 import (
        AbstractStressCyclesDataForAnSNCurveOfAPlasticMaterial,
    )
    from mastapy._private.materials._337 import AcousticRadiationEfficiency
    from mastapy._private.materials._338 import AcousticRadiationEfficiencyInputType
    from mastapy._private.materials._339 import AGMALubricantType
    from mastapy._private.materials._340 import AGMAMaterialApplications
    from mastapy._private.materials._341 import AGMAMaterialClasses
    from mastapy._private.materials._342 import AGMAMaterialGrade
    from mastapy._private.materials._343 import AirProperties
    from mastapy._private.materials._344 import BearingLubricationCondition
    from mastapy._private.materials._345 import BearingMaterial
    from mastapy._private.materials._346 import BearingMaterialDatabase
    from mastapy._private.materials._347 import BHCurveExtrapolationMethod
    from mastapy._private.materials._348 import BHCurveSpecification
    from mastapy._private.materials._349 import ComponentMaterialDatabase
    from mastapy._private.materials._350 import CompositeFatigueSafetyFactorItem
    from mastapy._private.materials._351 import CylindricalGearRatingMethods
    from mastapy._private.materials._352 import DensitySpecificationMethod
    from mastapy._private.materials._353 import FatigueSafetyFactorItem
    from mastapy._private.materials._354 import FatigueSafetyFactorItemBase
    from mastapy._private.materials._355 import Fluid
    from mastapy._private.materials._356 import FluidDatabase
    from mastapy._private.materials._357 import GearingTypes
    from mastapy._private.materials._358 import GeneralTransmissionProperties
    from mastapy._private.materials._359 import GreaseContaminationOptions
    from mastapy._private.materials._360 import HardnessType
    from mastapy._private.materials._361 import ISO76StaticSafetyFactorLimits
    from mastapy._private.materials._362 import ISOLubricantType
    from mastapy._private.materials._363 import LubricantDefinition
    from mastapy._private.materials._364 import LubricantDelivery
    from mastapy._private.materials._365 import LubricantViscosityClassAGMA
    from mastapy._private.materials._366 import LubricantViscosityClassification
    from mastapy._private.materials._367 import LubricantViscosityClassISO
    from mastapy._private.materials._368 import LubricantViscosityClassSAE
    from mastapy._private.materials._369 import LubricationDetail
    from mastapy._private.materials._370 import LubricationDetailDatabase
    from mastapy._private.materials._371 import Material
    from mastapy._private.materials._372 import MaterialDatabase
    from mastapy._private.materials._373 import MaterialsSettings
    from mastapy._private.materials._374 import MaterialsSettingsDatabase
    from mastapy._private.materials._375 import MaterialsSettingsItem
    from mastapy._private.materials._376 import MaterialStandards
    from mastapy._private.materials._377 import MetalPlasticType
    from mastapy._private.materials._378 import OilFiltrationOptions
    from mastapy._private.materials._379 import PressureViscosityCoefficientMethod
    from mastapy._private.materials._380 import QualityGrade
    from mastapy._private.materials._381 import SafetyFactorGroup
    from mastapy._private.materials._382 import SafetyFactorItem
    from mastapy._private.materials._383 import SNCurve
    from mastapy._private.materials._384 import SNCurvePoint
    from mastapy._private.materials._385 import SoundPressureEnclosure
    from mastapy._private.materials._386 import SoundPressureEnclosureType
    from mastapy._private.materials._387 import (
        StressCyclesDataForTheBendingSNCurveOfAPlasticMaterial,
    )
    from mastapy._private.materials._388 import (
        StressCyclesDataForTheContactSNCurveOfAPlasticMaterial,
    )
    from mastapy._private.materials._389 import TemperatureDependentProperty
    from mastapy._private.materials._390 import TransmissionApplications
    from mastapy._private.materials._391 import VDI2736LubricantType
    from mastapy._private.materials._392 import VehicleDynamicsProperties
    from mastapy._private.materials._393 import WindTurbineStandards
    from mastapy._private.materials._394 import WorkingCharacteristics
else:
    import sys as __sys

    from lazy_imports import LazyImporter as __LazyImporter

    __import_structure = {
        "_private.materials._336": [
            "AbstractStressCyclesDataForAnSNCurveOfAPlasticMaterial"
        ],
        "_private.materials._337": ["AcousticRadiationEfficiency"],
        "_private.materials._338": ["AcousticRadiationEfficiencyInputType"],
        "_private.materials._339": ["AGMALubricantType"],
        "_private.materials._340": ["AGMAMaterialApplications"],
        "_private.materials._341": ["AGMAMaterialClasses"],
        "_private.materials._342": ["AGMAMaterialGrade"],
        "_private.materials._343": ["AirProperties"],
        "_private.materials._344": ["BearingLubricationCondition"],
        "_private.materials._345": ["BearingMaterial"],
        "_private.materials._346": ["BearingMaterialDatabase"],
        "_private.materials._347": ["BHCurveExtrapolationMethod"],
        "_private.materials._348": ["BHCurveSpecification"],
        "_private.materials._349": ["ComponentMaterialDatabase"],
        "_private.materials._350": ["CompositeFatigueSafetyFactorItem"],
        "_private.materials._351": ["CylindricalGearRatingMethods"],
        "_private.materials._352": ["DensitySpecificationMethod"],
        "_private.materials._353": ["FatigueSafetyFactorItem"],
        "_private.materials._354": ["FatigueSafetyFactorItemBase"],
        "_private.materials._355": ["Fluid"],
        "_private.materials._356": ["FluidDatabase"],
        "_private.materials._357": ["GearingTypes"],
        "_private.materials._358": ["GeneralTransmissionProperties"],
        "_private.materials._359": ["GreaseContaminationOptions"],
        "_private.materials._360": ["HardnessType"],
        "_private.materials._361": ["ISO76StaticSafetyFactorLimits"],
        "_private.materials._362": ["ISOLubricantType"],
        "_private.materials._363": ["LubricantDefinition"],
        "_private.materials._364": ["LubricantDelivery"],
        "_private.materials._365": ["LubricantViscosityClassAGMA"],
        "_private.materials._366": ["LubricantViscosityClassification"],
        "_private.materials._367": ["LubricantViscosityClassISO"],
        "_private.materials._368": ["LubricantViscosityClassSAE"],
        "_private.materials._369": ["LubricationDetail"],
        "_private.materials._370": ["LubricationDetailDatabase"],
        "_private.materials._371": ["Material"],
        "_private.materials._372": ["MaterialDatabase"],
        "_private.materials._373": ["MaterialsSettings"],
        "_private.materials._374": ["MaterialsSettingsDatabase"],
        "_private.materials._375": ["MaterialsSettingsItem"],
        "_private.materials._376": ["MaterialStandards"],
        "_private.materials._377": ["MetalPlasticType"],
        "_private.materials._378": ["OilFiltrationOptions"],
        "_private.materials._379": ["PressureViscosityCoefficientMethod"],
        "_private.materials._380": ["QualityGrade"],
        "_private.materials._381": ["SafetyFactorGroup"],
        "_private.materials._382": ["SafetyFactorItem"],
        "_private.materials._383": ["SNCurve"],
        "_private.materials._384": ["SNCurvePoint"],
        "_private.materials._385": ["SoundPressureEnclosure"],
        "_private.materials._386": ["SoundPressureEnclosureType"],
        "_private.materials._387": [
            "StressCyclesDataForTheBendingSNCurveOfAPlasticMaterial"
        ],
        "_private.materials._388": [
            "StressCyclesDataForTheContactSNCurveOfAPlasticMaterial"
        ],
        "_private.materials._389": ["TemperatureDependentProperty"],
        "_private.materials._390": ["TransmissionApplications"],
        "_private.materials._391": ["VDI2736LubricantType"],
        "_private.materials._392": ["VehicleDynamicsProperties"],
        "_private.materials._393": ["WindTurbineStandards"],
        "_private.materials._394": ["WorkingCharacteristics"],
    }

    __sys.modules[__name__] = __LazyImporter(
        "mastapy",
        globals()["__file__"],
        __import_structure,
    )

__all__ = (
    "AbstractStressCyclesDataForAnSNCurveOfAPlasticMaterial",
    "AcousticRadiationEfficiency",
    "AcousticRadiationEfficiencyInputType",
    "AGMALubricantType",
    "AGMAMaterialApplications",
    "AGMAMaterialClasses",
    "AGMAMaterialGrade",
    "AirProperties",
    "BearingLubricationCondition",
    "BearingMaterial",
    "BearingMaterialDatabase",
    "BHCurveExtrapolationMethod",
    "BHCurveSpecification",
    "ComponentMaterialDatabase",
    "CompositeFatigueSafetyFactorItem",
    "CylindricalGearRatingMethods",
    "DensitySpecificationMethod",
    "FatigueSafetyFactorItem",
    "FatigueSafetyFactorItemBase",
    "Fluid",
    "FluidDatabase",
    "GearingTypes",
    "GeneralTransmissionProperties",
    "GreaseContaminationOptions",
    "HardnessType",
    "ISO76StaticSafetyFactorLimits",
    "ISOLubricantType",
    "LubricantDefinition",
    "LubricantDelivery",
    "LubricantViscosityClassAGMA",
    "LubricantViscosityClassification",
    "LubricantViscosityClassISO",
    "LubricantViscosityClassSAE",
    "LubricationDetail",
    "LubricationDetailDatabase",
    "Material",
    "MaterialDatabase",
    "MaterialsSettings",
    "MaterialsSettingsDatabase",
    "MaterialsSettingsItem",
    "MaterialStandards",
    "MetalPlasticType",
    "OilFiltrationOptions",
    "PressureViscosityCoefficientMethod",
    "QualityGrade",
    "SafetyFactorGroup",
    "SafetyFactorItem",
    "SNCurve",
    "SNCurvePoint",
    "SoundPressureEnclosure",
    "SoundPressureEnclosureType",
    "StressCyclesDataForTheBendingSNCurveOfAPlasticMaterial",
    "StressCyclesDataForTheContactSNCurveOfAPlasticMaterial",
    "TemperatureDependentProperty",
    "TransmissionApplications",
    "VDI2736LubricantType",
    "VehicleDynamicsProperties",
    "WindTurbineStandards",
    "WorkingCharacteristics",
)
