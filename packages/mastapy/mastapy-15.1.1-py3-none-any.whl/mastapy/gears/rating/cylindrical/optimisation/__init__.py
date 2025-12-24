"""Subpackage."""

from typing import TYPE_CHECKING as __tc

if __tc:
    from mastapy._private.gears.rating.cylindrical.optimisation._614 import (
        CylindricalGearSetRatingOptimisationHelper,
    )
    from mastapy._private.gears.rating.cylindrical.optimisation._615 import (
        OptimisationResultsPair,
    )
    from mastapy._private.gears.rating.cylindrical.optimisation._616 import (
        SafetyFactorOptimisationResults,
    )
    from mastapy._private.gears.rating.cylindrical.optimisation._617 import (
        SafetyFactorOptimisationStepResult,
    )
    from mastapy._private.gears.rating.cylindrical.optimisation._618 import (
        SafetyFactorOptimisationStepResultAngle,
    )
    from mastapy._private.gears.rating.cylindrical.optimisation._619 import (
        SafetyFactorOptimisationStepResultNumber,
    )
    from mastapy._private.gears.rating.cylindrical.optimisation._620 import (
        SafetyFactorOptimisationStepResultShortLength,
    )
else:
    import sys as __sys

    from lazy_imports import LazyImporter as __LazyImporter

    __import_structure = {
        "_private.gears.rating.cylindrical.optimisation._614": [
            "CylindricalGearSetRatingOptimisationHelper"
        ],
        "_private.gears.rating.cylindrical.optimisation._615": [
            "OptimisationResultsPair"
        ],
        "_private.gears.rating.cylindrical.optimisation._616": [
            "SafetyFactorOptimisationResults"
        ],
        "_private.gears.rating.cylindrical.optimisation._617": [
            "SafetyFactorOptimisationStepResult"
        ],
        "_private.gears.rating.cylindrical.optimisation._618": [
            "SafetyFactorOptimisationStepResultAngle"
        ],
        "_private.gears.rating.cylindrical.optimisation._619": [
            "SafetyFactorOptimisationStepResultNumber"
        ],
        "_private.gears.rating.cylindrical.optimisation._620": [
            "SafetyFactorOptimisationStepResultShortLength"
        ],
    }

    __sys.modules[__name__] = __LazyImporter(
        "mastapy",
        globals()["__file__"],
        __import_structure,
    )

__all__ = (
    "CylindricalGearSetRatingOptimisationHelper",
    "OptimisationResultsPair",
    "SafetyFactorOptimisationResults",
    "SafetyFactorOptimisationStepResult",
    "SafetyFactorOptimisationStepResultAngle",
    "SafetyFactorOptimisationStepResultNumber",
    "SafetyFactorOptimisationStepResultShortLength",
)
