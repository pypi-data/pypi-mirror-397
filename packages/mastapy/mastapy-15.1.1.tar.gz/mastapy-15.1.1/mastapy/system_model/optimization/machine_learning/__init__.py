"""Subpackage."""

from typing import TYPE_CHECKING as __tc

if __tc:
    from mastapy._private.system_model.optimization.machine_learning._2492 import (
        CylindricalGearFlankOptimisationParameter,
    )
    from mastapy._private.system_model.optimization.machine_learning._2493 import (
        CylindricalGearFlankOptimisationParameters,
    )
    from mastapy._private.system_model.optimization.machine_learning._2494 import (
        CylindricalGearFlankOptimisationParametersDatabase,
    )
    from mastapy._private.system_model.optimization.machine_learning._2495 import (
        GearFlankParameterSelection,
    )
    from mastapy._private.system_model.optimization.machine_learning._2496 import (
        LoadCaseConstraint,
    )
    from mastapy._private.system_model.optimization.machine_learning._2497 import (
        LoadCaseSettings,
    )
    from mastapy._private.system_model.optimization.machine_learning._2498 import (
        LoadCaseTarget,
    )
    from mastapy._private.system_model.optimization.machine_learning._2499 import (
        ML1MicroGeometryOptimiser,
    )
    from mastapy._private.system_model.optimization.machine_learning._2500 import (
        ML1MicroGeometryOptimiserGroup,
    )
else:
    import sys as __sys

    from lazy_imports import LazyImporter as __LazyImporter

    __import_structure = {
        "_private.system_model.optimization.machine_learning._2492": [
            "CylindricalGearFlankOptimisationParameter"
        ],
        "_private.system_model.optimization.machine_learning._2493": [
            "CylindricalGearFlankOptimisationParameters"
        ],
        "_private.system_model.optimization.machine_learning._2494": [
            "CylindricalGearFlankOptimisationParametersDatabase"
        ],
        "_private.system_model.optimization.machine_learning._2495": [
            "GearFlankParameterSelection"
        ],
        "_private.system_model.optimization.machine_learning._2496": [
            "LoadCaseConstraint"
        ],
        "_private.system_model.optimization.machine_learning._2497": [
            "LoadCaseSettings"
        ],
        "_private.system_model.optimization.machine_learning._2498": ["LoadCaseTarget"],
        "_private.system_model.optimization.machine_learning._2499": [
            "ML1MicroGeometryOptimiser"
        ],
        "_private.system_model.optimization.machine_learning._2500": [
            "ML1MicroGeometryOptimiserGroup"
        ],
    }

    __sys.modules[__name__] = __LazyImporter(
        "mastapy",
        globals()["__file__"],
        __import_structure,
    )

__all__ = (
    "CylindricalGearFlankOptimisationParameter",
    "CylindricalGearFlankOptimisationParameters",
    "CylindricalGearFlankOptimisationParametersDatabase",
    "GearFlankParameterSelection",
    "LoadCaseConstraint",
    "LoadCaseSettings",
    "LoadCaseTarget",
    "ML1MicroGeometryOptimiser",
    "ML1MicroGeometryOptimiserGroup",
)
