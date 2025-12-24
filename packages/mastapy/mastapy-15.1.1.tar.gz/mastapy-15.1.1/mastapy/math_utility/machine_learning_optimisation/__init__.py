"""Subpackage."""

from typing import TYPE_CHECKING as __tc

if __tc:
    from mastapy._private.math_utility.machine_learning_optimisation._1788 import (
        ConstraintResult,
    )
    from mastapy._private.math_utility.machine_learning_optimisation._1789 import (
        InputResult,
    )
    from mastapy._private.math_utility.machine_learning_optimisation._1790 import (
        MachineLearningOptimizationVariable,
    )
    from mastapy._private.math_utility.machine_learning_optimisation._1791 import (
        ML1OptimiserSnapshot,
    )
    from mastapy._private.math_utility.machine_learning_optimisation._1792 import (
        ML1OptimizerSettings,
    )
    from mastapy._private.math_utility.machine_learning_optimisation._1793 import (
        OptimizationData,
    )
    from mastapy._private.math_utility.machine_learning_optimisation._1794 import (
        MachineLearningOptimizationResultsStorageOption,
    )
    from mastapy._private.math_utility.machine_learning_optimisation._1795 import (
        OptimizationStage,
    )
else:
    import sys as __sys

    from lazy_imports import LazyImporter as __LazyImporter

    __import_structure = {
        "_private.math_utility.machine_learning_optimisation._1788": [
            "ConstraintResult"
        ],
        "_private.math_utility.machine_learning_optimisation._1789": ["InputResult"],
        "_private.math_utility.machine_learning_optimisation._1790": [
            "MachineLearningOptimizationVariable"
        ],
        "_private.math_utility.machine_learning_optimisation._1791": [
            "ML1OptimiserSnapshot"
        ],
        "_private.math_utility.machine_learning_optimisation._1792": [
            "ML1OptimizerSettings"
        ],
        "_private.math_utility.machine_learning_optimisation._1793": [
            "OptimizationData"
        ],
        "_private.math_utility.machine_learning_optimisation._1794": [
            "MachineLearningOptimizationResultsStorageOption"
        ],
        "_private.math_utility.machine_learning_optimisation._1795": [
            "OptimizationStage"
        ],
    }

    __sys.modules[__name__] = __LazyImporter(
        "mastapy",
        globals()["__file__"],
        __import_structure,
    )

__all__ = (
    "ConstraintResult",
    "InputResult",
    "MachineLearningOptimizationVariable",
    "ML1OptimiserSnapshot",
    "ML1OptimizerSettings",
    "OptimizationData",
    "MachineLearningOptimizationResultsStorageOption",
    "OptimizationStage",
)
