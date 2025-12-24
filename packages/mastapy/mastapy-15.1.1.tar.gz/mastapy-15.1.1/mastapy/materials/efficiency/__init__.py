"""Subpackage."""

from typing import TYPE_CHECKING as __tc

if __tc:
    from mastapy._private.materials.efficiency._395 import BaffleLoss
    from mastapy._private.materials.efficiency._396 import BearingEfficiencyRatingMethod
    from mastapy._private.materials.efficiency._397 import CombinedResistiveTorque
    from mastapy._private.materials.efficiency._398 import IndependentPowerLoss
    from mastapy._private.materials.efficiency._399 import IndependentResistiveTorque
    from mastapy._private.materials.efficiency._400 import LoadAndSpeedCombinedPowerLoss
    from mastapy._private.materials.efficiency._401 import OilPumpDetail
    from mastapy._private.materials.efficiency._402 import OilPumpDriveType
    from mastapy._private.materials.efficiency._403 import OilPumpLossCalculationMethod
    from mastapy._private.materials.efficiency._404 import OilSealLossCalculationMethod
    from mastapy._private.materials.efficiency._405 import OilSealMaterialType
    from mastapy._private.materials.efficiency._406 import OilSealType
    from mastapy._private.materials.efficiency._407 import PowerLoss
    from mastapy._private.materials.efficiency._408 import ResistiveTorque
    from mastapy._private.materials.efficiency._409 import (
        WetClutchLossCalculationMethod,
    )
else:
    import sys as __sys

    from lazy_imports import LazyImporter as __LazyImporter

    __import_structure = {
        "_private.materials.efficiency._395": ["BaffleLoss"],
        "_private.materials.efficiency._396": ["BearingEfficiencyRatingMethod"],
        "_private.materials.efficiency._397": ["CombinedResistiveTorque"],
        "_private.materials.efficiency._398": ["IndependentPowerLoss"],
        "_private.materials.efficiency._399": ["IndependentResistiveTorque"],
        "_private.materials.efficiency._400": ["LoadAndSpeedCombinedPowerLoss"],
        "_private.materials.efficiency._401": ["OilPumpDetail"],
        "_private.materials.efficiency._402": ["OilPumpDriveType"],
        "_private.materials.efficiency._403": ["OilPumpLossCalculationMethod"],
        "_private.materials.efficiency._404": ["OilSealLossCalculationMethod"],
        "_private.materials.efficiency._405": ["OilSealMaterialType"],
        "_private.materials.efficiency._406": ["OilSealType"],
        "_private.materials.efficiency._407": ["PowerLoss"],
        "_private.materials.efficiency._408": ["ResistiveTorque"],
        "_private.materials.efficiency._409": ["WetClutchLossCalculationMethod"],
    }

    __sys.modules[__name__] = __LazyImporter(
        "mastapy",
        globals()["__file__"],
        __import_structure,
    )

__all__ = (
    "BaffleLoss",
    "BearingEfficiencyRatingMethod",
    "CombinedResistiveTorque",
    "IndependentPowerLoss",
    "IndependentResistiveTorque",
    "LoadAndSpeedCombinedPowerLoss",
    "OilPumpDetail",
    "OilPumpDriveType",
    "OilPumpLossCalculationMethod",
    "OilSealLossCalculationMethod",
    "OilSealMaterialType",
    "OilSealType",
    "PowerLoss",
    "ResistiveTorque",
    "WetClutchLossCalculationMethod",
)
