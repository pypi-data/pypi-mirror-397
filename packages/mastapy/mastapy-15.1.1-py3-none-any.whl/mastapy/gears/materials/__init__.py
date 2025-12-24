"""Subpackage."""

from typing import TYPE_CHECKING as __tc

if __tc:
    from mastapy._private.gears.materials._696 import AGMACylindricalGearMaterial
    from mastapy._private.gears.materials._697 import (
        BenedictAndKelleyCoefficientOfFrictionCalculator,
    )
    from mastapy._private.gears.materials._698 import BevelGearAbstractMaterialDatabase
    from mastapy._private.gears.materials._699 import BevelGearISOMaterial
    from mastapy._private.gears.materials._700 import BevelGearISOMaterialDatabase
    from mastapy._private.gears.materials._701 import BevelGearMaterial
    from mastapy._private.gears.materials._702 import BevelGearMaterialDatabase
    from mastapy._private.gears.materials._703 import CoefficientOfFrictionCalculator
    from mastapy._private.gears.materials._704 import (
        CylindricalGearAGMAMaterialDatabase,
    )
    from mastapy._private.gears.materials._705 import CylindricalGearISOMaterialDatabase
    from mastapy._private.gears.materials._706 import CylindricalGearMaterial
    from mastapy._private.gears.materials._707 import CylindricalGearMaterialDatabase
    from mastapy._private.gears.materials._708 import (
        CylindricalGearPlasticMaterialDatabase,
    )
    from mastapy._private.gears.materials._709 import (
        DrozdovAndGavrikovCoefficientOfFrictionCalculator,
    )
    from mastapy._private.gears.materials._710 import GearMaterial
    from mastapy._private.gears.materials._711 import GearMaterialDatabase
    from mastapy._private.gears.materials._712 import (
        GearMaterialExpertSystemFactorSettings,
    )
    from mastapy._private.gears.materials._713 import (
        InstantaneousCoefficientOfFrictionCalculator,
    )
    from mastapy._private.gears.materials._714 import (
        ISO14179Part1CoefficientOfFrictionCalculator,
    )
    from mastapy._private.gears.materials._715 import (
        ISO14179Part1ConstantC1SpecificationMethod,
    )
    from mastapy._private.gears.materials._716 import (
        ISO14179Part2CoefficientOfFrictionCalculator,
    )
    from mastapy._private.gears.materials._717 import (
        ISO14179Part2CoefficientOfFrictionCalculatorBase,
    )
    from mastapy._private.gears.materials._718 import (
        ISO14179Part2CoefficientOfFrictionCalculatorWithMartinsModification,
    )
    from mastapy._private.gears.materials._719 import ISOCylindricalGearMaterial
    from mastapy._private.gears.materials._720 import (
        ISOTC60CoefficientOfFrictionCalculator,
    )
    from mastapy._private.gears.materials._721 import (
        ISOTR1417912001CoefficientOfFrictionConstants,
    )
    from mastapy._private.gears.materials._722 import (
        ISOTR1417912001CoefficientOfFrictionConstantsDatabase,
    )
    from mastapy._private.gears.materials._723 import (
        KlingelnbergConicalGearMaterialDatabase,
    )
    from mastapy._private.gears.materials._724 import (
        KlingelnbergCycloPalloidConicalGearMaterial,
    )
    from mastapy._private.gears.materials._725 import ManufactureRating
    from mastapy._private.gears.materials._726 import (
        MisharinCoefficientOfFrictionCalculator,
    )
    from mastapy._private.gears.materials._727 import (
        ODonoghueAndCameronCoefficientOfFrictionCalculator,
    )
    from mastapy._private.gears.materials._728 import PlasticCylindricalGearMaterial
    from mastapy._private.gears.materials._729 import PlasticSNCurve
    from mastapy._private.gears.materials._730 import RatingMethods
    from mastapy._private.gears.materials._731 import RawMaterial
    from mastapy._private.gears.materials._732 import RawMaterialDatabase
    from mastapy._private.gears.materials._733 import (
        ScriptCoefficientOfFrictionCalculator,
    )
    from mastapy._private.gears.materials._734 import SNCurveDefinition
else:
    import sys as __sys

    from lazy_imports import LazyImporter as __LazyImporter

    __import_structure = {
        "_private.gears.materials._696": ["AGMACylindricalGearMaterial"],
        "_private.gears.materials._697": [
            "BenedictAndKelleyCoefficientOfFrictionCalculator"
        ],
        "_private.gears.materials._698": ["BevelGearAbstractMaterialDatabase"],
        "_private.gears.materials._699": ["BevelGearISOMaterial"],
        "_private.gears.materials._700": ["BevelGearISOMaterialDatabase"],
        "_private.gears.materials._701": ["BevelGearMaterial"],
        "_private.gears.materials._702": ["BevelGearMaterialDatabase"],
        "_private.gears.materials._703": ["CoefficientOfFrictionCalculator"],
        "_private.gears.materials._704": ["CylindricalGearAGMAMaterialDatabase"],
        "_private.gears.materials._705": ["CylindricalGearISOMaterialDatabase"],
        "_private.gears.materials._706": ["CylindricalGearMaterial"],
        "_private.gears.materials._707": ["CylindricalGearMaterialDatabase"],
        "_private.gears.materials._708": ["CylindricalGearPlasticMaterialDatabase"],
        "_private.gears.materials._709": [
            "DrozdovAndGavrikovCoefficientOfFrictionCalculator"
        ],
        "_private.gears.materials._710": ["GearMaterial"],
        "_private.gears.materials._711": ["GearMaterialDatabase"],
        "_private.gears.materials._712": ["GearMaterialExpertSystemFactorSettings"],
        "_private.gears.materials._713": [
            "InstantaneousCoefficientOfFrictionCalculator"
        ],
        "_private.gears.materials._714": [
            "ISO14179Part1CoefficientOfFrictionCalculator"
        ],
        "_private.gears.materials._715": ["ISO14179Part1ConstantC1SpecificationMethod"],
        "_private.gears.materials._716": [
            "ISO14179Part2CoefficientOfFrictionCalculator"
        ],
        "_private.gears.materials._717": [
            "ISO14179Part2CoefficientOfFrictionCalculatorBase"
        ],
        "_private.gears.materials._718": [
            "ISO14179Part2CoefficientOfFrictionCalculatorWithMartinsModification"
        ],
        "_private.gears.materials._719": ["ISOCylindricalGearMaterial"],
        "_private.gears.materials._720": ["ISOTC60CoefficientOfFrictionCalculator"],
        "_private.gears.materials._721": [
            "ISOTR1417912001CoefficientOfFrictionConstants"
        ],
        "_private.gears.materials._722": [
            "ISOTR1417912001CoefficientOfFrictionConstantsDatabase"
        ],
        "_private.gears.materials._723": ["KlingelnbergConicalGearMaterialDatabase"],
        "_private.gears.materials._724": [
            "KlingelnbergCycloPalloidConicalGearMaterial"
        ],
        "_private.gears.materials._725": ["ManufactureRating"],
        "_private.gears.materials._726": ["MisharinCoefficientOfFrictionCalculator"],
        "_private.gears.materials._727": [
            "ODonoghueAndCameronCoefficientOfFrictionCalculator"
        ],
        "_private.gears.materials._728": ["PlasticCylindricalGearMaterial"],
        "_private.gears.materials._729": ["PlasticSNCurve"],
        "_private.gears.materials._730": ["RatingMethods"],
        "_private.gears.materials._731": ["RawMaterial"],
        "_private.gears.materials._732": ["RawMaterialDatabase"],
        "_private.gears.materials._733": ["ScriptCoefficientOfFrictionCalculator"],
        "_private.gears.materials._734": ["SNCurveDefinition"],
    }

    __sys.modules[__name__] = __LazyImporter(
        "mastapy",
        globals()["__file__"],
        __import_structure,
    )

__all__ = (
    "AGMACylindricalGearMaterial",
    "BenedictAndKelleyCoefficientOfFrictionCalculator",
    "BevelGearAbstractMaterialDatabase",
    "BevelGearISOMaterial",
    "BevelGearISOMaterialDatabase",
    "BevelGearMaterial",
    "BevelGearMaterialDatabase",
    "CoefficientOfFrictionCalculator",
    "CylindricalGearAGMAMaterialDatabase",
    "CylindricalGearISOMaterialDatabase",
    "CylindricalGearMaterial",
    "CylindricalGearMaterialDatabase",
    "CylindricalGearPlasticMaterialDatabase",
    "DrozdovAndGavrikovCoefficientOfFrictionCalculator",
    "GearMaterial",
    "GearMaterialDatabase",
    "GearMaterialExpertSystemFactorSettings",
    "InstantaneousCoefficientOfFrictionCalculator",
    "ISO14179Part1CoefficientOfFrictionCalculator",
    "ISO14179Part1ConstantC1SpecificationMethod",
    "ISO14179Part2CoefficientOfFrictionCalculator",
    "ISO14179Part2CoefficientOfFrictionCalculatorBase",
    "ISO14179Part2CoefficientOfFrictionCalculatorWithMartinsModification",
    "ISOCylindricalGearMaterial",
    "ISOTC60CoefficientOfFrictionCalculator",
    "ISOTR1417912001CoefficientOfFrictionConstants",
    "ISOTR1417912001CoefficientOfFrictionConstantsDatabase",
    "KlingelnbergConicalGearMaterialDatabase",
    "KlingelnbergCycloPalloidConicalGearMaterial",
    "ManufactureRating",
    "MisharinCoefficientOfFrictionCalculator",
    "ODonoghueAndCameronCoefficientOfFrictionCalculator",
    "PlasticCylindricalGearMaterial",
    "PlasticSNCurve",
    "RatingMethods",
    "RawMaterial",
    "RawMaterialDatabase",
    "ScriptCoefficientOfFrictionCalculator",
    "SNCurveDefinition",
)
