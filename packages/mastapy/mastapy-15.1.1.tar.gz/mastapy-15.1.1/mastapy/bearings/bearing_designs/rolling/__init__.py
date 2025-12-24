"""Subpackage."""

from typing import TYPE_CHECKING as __tc

if __tc:
    from mastapy._private.bearings.bearing_designs.rolling._2382 import (
        AngularContactBallBearing,
    )
    from mastapy._private.bearings.bearing_designs.rolling._2383 import (
        AngularContactThrustBallBearing,
    )
    from mastapy._private.bearings.bearing_designs.rolling._2384 import (
        AsymmetricSphericalRollerBearing,
    )
    from mastapy._private.bearings.bearing_designs.rolling._2385 import (
        AxialThrustCylindricalRollerBearing,
    )
    from mastapy._private.bearings.bearing_designs.rolling._2386 import (
        AxialThrustNeedleRollerBearing,
    )
    from mastapy._private.bearings.bearing_designs.rolling._2387 import BallBearing
    from mastapy._private.bearings.bearing_designs.rolling._2388 import (
        BallBearingShoulderDefinition,
    )
    from mastapy._private.bearings.bearing_designs.rolling._2389 import (
        BarrelRollerBearing,
    )
    from mastapy._private.bearings.bearing_designs.rolling._2390 import (
        BearingProtection,
    )
    from mastapy._private.bearings.bearing_designs.rolling._2391 import (
        BearingProtectionDetailsModifier,
    )
    from mastapy._private.bearings.bearing_designs.rolling._2392 import (
        BearingProtectionLevel,
    )
    from mastapy._private.bearings.bearing_designs.rolling._2393 import (
        BearingTypeExtraInformation,
    )
    from mastapy._private.bearings.bearing_designs.rolling._2394 import CageBridgeShape
    from mastapy._private.bearings.bearing_designs.rolling._2395 import (
        CrossedRollerBearing,
    )
    from mastapy._private.bearings.bearing_designs.rolling._2396 import (
        CylindricalRollerBearing,
    )
    from mastapy._private.bearings.bearing_designs.rolling._2397 import (
        DeepGrooveBallBearing,
    )
    from mastapy._private.bearings.bearing_designs.rolling._2398 import DiameterSeries
    from mastapy._private.bearings.bearing_designs.rolling._2399 import (
        FatigueLoadLimitCalculationMethodEnum,
    )
    from mastapy._private.bearings.bearing_designs.rolling._2400 import (
        FourPointContactAngleDefinition,
    )
    from mastapy._private.bearings.bearing_designs.rolling._2401 import (
        FourPointContactBallBearing,
    )
    from mastapy._private.bearings.bearing_designs.rolling._2402 import (
        GeometricConstants,
    )
    from mastapy._private.bearings.bearing_designs.rolling._2403 import (
        GeometricConstantsForRollingFrictionalMoments,
    )
    from mastapy._private.bearings.bearing_designs.rolling._2404 import (
        GeometricConstantsForSlidingFrictionalMoments,
    )
    from mastapy._private.bearings.bearing_designs.rolling._2405 import HeightSeries
    from mastapy._private.bearings.bearing_designs.rolling._2406 import (
        MultiPointContactBallBearing,
    )
    from mastapy._private.bearings.bearing_designs.rolling._2407 import (
        NeedleRollerBearing,
    )
    from mastapy._private.bearings.bearing_designs.rolling._2408 import (
        NonBarrelRollerBearing,
    )
    from mastapy._private.bearings.bearing_designs.rolling._2409 import RollerBearing
    from mastapy._private.bearings.bearing_designs.rolling._2410 import RollerEndShape
    from mastapy._private.bearings.bearing_designs.rolling._2411 import RollerRibDetail
    from mastapy._private.bearings.bearing_designs.rolling._2412 import RollingBearing
    from mastapy._private.bearings.bearing_designs.rolling._2413 import (
        RollingBearingElement,
    )
    from mastapy._private.bearings.bearing_designs.rolling._2414 import (
        SelfAligningBallBearing,
    )
    from mastapy._private.bearings.bearing_designs.rolling._2415 import (
        SKFSealFrictionalMomentConstants,
    )
    from mastapy._private.bearings.bearing_designs.rolling._2416 import SleeveType
    from mastapy._private.bearings.bearing_designs.rolling._2417 import (
        SphericalRollerBearing,
    )
    from mastapy._private.bearings.bearing_designs.rolling._2418 import (
        SphericalRollerThrustBearing,
    )
    from mastapy._private.bearings.bearing_designs.rolling._2419 import (
        TaperRollerBearing,
    )
    from mastapy._private.bearings.bearing_designs.rolling._2420 import (
        ThreePointContactBallBearing,
    )
    from mastapy._private.bearings.bearing_designs.rolling._2421 import (
        ThrustBallBearing,
    )
    from mastapy._private.bearings.bearing_designs.rolling._2422 import (
        ToroidalRollerBearing,
    )
    from mastapy._private.bearings.bearing_designs.rolling._2423 import WidthSeries
else:
    import sys as __sys

    from lazy_imports import LazyImporter as __LazyImporter

    __import_structure = {
        "_private.bearings.bearing_designs.rolling._2382": [
            "AngularContactBallBearing"
        ],
        "_private.bearings.bearing_designs.rolling._2383": [
            "AngularContactThrustBallBearing"
        ],
        "_private.bearings.bearing_designs.rolling._2384": [
            "AsymmetricSphericalRollerBearing"
        ],
        "_private.bearings.bearing_designs.rolling._2385": [
            "AxialThrustCylindricalRollerBearing"
        ],
        "_private.bearings.bearing_designs.rolling._2386": [
            "AxialThrustNeedleRollerBearing"
        ],
        "_private.bearings.bearing_designs.rolling._2387": ["BallBearing"],
        "_private.bearings.bearing_designs.rolling._2388": [
            "BallBearingShoulderDefinition"
        ],
        "_private.bearings.bearing_designs.rolling._2389": ["BarrelRollerBearing"],
        "_private.bearings.bearing_designs.rolling._2390": ["BearingProtection"],
        "_private.bearings.bearing_designs.rolling._2391": [
            "BearingProtectionDetailsModifier"
        ],
        "_private.bearings.bearing_designs.rolling._2392": ["BearingProtectionLevel"],
        "_private.bearings.bearing_designs.rolling._2393": [
            "BearingTypeExtraInformation"
        ],
        "_private.bearings.bearing_designs.rolling._2394": ["CageBridgeShape"],
        "_private.bearings.bearing_designs.rolling._2395": ["CrossedRollerBearing"],
        "_private.bearings.bearing_designs.rolling._2396": ["CylindricalRollerBearing"],
        "_private.bearings.bearing_designs.rolling._2397": ["DeepGrooveBallBearing"],
        "_private.bearings.bearing_designs.rolling._2398": ["DiameterSeries"],
        "_private.bearings.bearing_designs.rolling._2399": [
            "FatigueLoadLimitCalculationMethodEnum"
        ],
        "_private.bearings.bearing_designs.rolling._2400": [
            "FourPointContactAngleDefinition"
        ],
        "_private.bearings.bearing_designs.rolling._2401": [
            "FourPointContactBallBearing"
        ],
        "_private.bearings.bearing_designs.rolling._2402": ["GeometricConstants"],
        "_private.bearings.bearing_designs.rolling._2403": [
            "GeometricConstantsForRollingFrictionalMoments"
        ],
        "_private.bearings.bearing_designs.rolling._2404": [
            "GeometricConstantsForSlidingFrictionalMoments"
        ],
        "_private.bearings.bearing_designs.rolling._2405": ["HeightSeries"],
        "_private.bearings.bearing_designs.rolling._2406": [
            "MultiPointContactBallBearing"
        ],
        "_private.bearings.bearing_designs.rolling._2407": ["NeedleRollerBearing"],
        "_private.bearings.bearing_designs.rolling._2408": ["NonBarrelRollerBearing"],
        "_private.bearings.bearing_designs.rolling._2409": ["RollerBearing"],
        "_private.bearings.bearing_designs.rolling._2410": ["RollerEndShape"],
        "_private.bearings.bearing_designs.rolling._2411": ["RollerRibDetail"],
        "_private.bearings.bearing_designs.rolling._2412": ["RollingBearing"],
        "_private.bearings.bearing_designs.rolling._2413": ["RollingBearingElement"],
        "_private.bearings.bearing_designs.rolling._2414": ["SelfAligningBallBearing"],
        "_private.bearings.bearing_designs.rolling._2415": [
            "SKFSealFrictionalMomentConstants"
        ],
        "_private.bearings.bearing_designs.rolling._2416": ["SleeveType"],
        "_private.bearings.bearing_designs.rolling._2417": ["SphericalRollerBearing"],
        "_private.bearings.bearing_designs.rolling._2418": [
            "SphericalRollerThrustBearing"
        ],
        "_private.bearings.bearing_designs.rolling._2419": ["TaperRollerBearing"],
        "_private.bearings.bearing_designs.rolling._2420": [
            "ThreePointContactBallBearing"
        ],
        "_private.bearings.bearing_designs.rolling._2421": ["ThrustBallBearing"],
        "_private.bearings.bearing_designs.rolling._2422": ["ToroidalRollerBearing"],
        "_private.bearings.bearing_designs.rolling._2423": ["WidthSeries"],
    }

    __sys.modules[__name__] = __LazyImporter(
        "mastapy",
        globals()["__file__"],
        __import_structure,
    )

__all__ = (
    "AngularContactBallBearing",
    "AngularContactThrustBallBearing",
    "AsymmetricSphericalRollerBearing",
    "AxialThrustCylindricalRollerBearing",
    "AxialThrustNeedleRollerBearing",
    "BallBearing",
    "BallBearingShoulderDefinition",
    "BarrelRollerBearing",
    "BearingProtection",
    "BearingProtectionDetailsModifier",
    "BearingProtectionLevel",
    "BearingTypeExtraInformation",
    "CageBridgeShape",
    "CrossedRollerBearing",
    "CylindricalRollerBearing",
    "DeepGrooveBallBearing",
    "DiameterSeries",
    "FatigueLoadLimitCalculationMethodEnum",
    "FourPointContactAngleDefinition",
    "FourPointContactBallBearing",
    "GeometricConstants",
    "GeometricConstantsForRollingFrictionalMoments",
    "GeometricConstantsForSlidingFrictionalMoments",
    "HeightSeries",
    "MultiPointContactBallBearing",
    "NeedleRollerBearing",
    "NonBarrelRollerBearing",
    "RollerBearing",
    "RollerEndShape",
    "RollerRibDetail",
    "RollingBearing",
    "RollingBearingElement",
    "SelfAligningBallBearing",
    "SKFSealFrictionalMomentConstants",
    "SleeveType",
    "SphericalRollerBearing",
    "SphericalRollerThrustBearing",
    "TaperRollerBearing",
    "ThreePointContactBallBearing",
    "ThrustBallBearing",
    "ToroidalRollerBearing",
    "WidthSeries",
)
