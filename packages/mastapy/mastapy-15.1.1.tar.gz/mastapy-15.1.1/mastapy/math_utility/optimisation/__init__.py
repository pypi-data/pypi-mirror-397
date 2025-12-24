"""Subpackage."""

from typing import TYPE_CHECKING as __tc

if __tc:
    from mastapy._private.math_utility.optimisation._1754 import AbstractOptimisable
    from mastapy._private.math_utility.optimisation._1755 import (
        DesignSpaceSearchStrategyDatabase,
    )
    from mastapy._private.math_utility.optimisation._1756 import InputSetter
    from mastapy._private.math_utility.optimisation._1757 import Optimisable
    from mastapy._private.math_utility.optimisation._1758 import OptimisationHistory
    from mastapy._private.math_utility.optimisation._1759 import OptimizationInput
    from mastapy._private.math_utility.optimisation._1760 import OptimizationProperty
    from mastapy._private.math_utility.optimisation._1761 import OptimizationVariable
    from mastapy._private.math_utility.optimisation._1762 import (
        ParetoOptimisationFilter,
    )
    from mastapy._private.math_utility.optimisation._1763 import ParetoOptimisationInput
    from mastapy._private.math_utility.optimisation._1764 import (
        ParetoOptimisationOutput,
    )
    from mastapy._private.math_utility.optimisation._1765 import (
        ParetoOptimisationStrategy,
    )
    from mastapy._private.math_utility.optimisation._1766 import (
        ParetoOptimisationStrategyBars,
    )
    from mastapy._private.math_utility.optimisation._1767 import (
        ParetoOptimisationStrategyChartInformation,
    )
    from mastapy._private.math_utility.optimisation._1768 import (
        ParetoOptimisationStrategyDatabase,
    )
    from mastapy._private.math_utility.optimisation._1769 import (
        ParetoOptimisationVariable,
    )
    from mastapy._private.math_utility.optimisation._1770 import (
        ParetoOptimisationVariableBase,
    )
    from mastapy._private.math_utility.optimisation._1771 import (
        PropertyTargetForDominantCandidateSearch,
    )
    from mastapy._private.math_utility.optimisation._1772 import (
        ReportingOptimizationInput,
    )
    from mastapy._private.math_utility.optimisation._1773 import (
        SpecifyOptimisationInputAs,
    )
    from mastapy._private.math_utility.optimisation._1774 import TargetingPropertyTo
else:
    import sys as __sys

    from lazy_imports import LazyImporter as __LazyImporter

    __import_structure = {
        "_private.math_utility.optimisation._1754": ["AbstractOptimisable"],
        "_private.math_utility.optimisation._1755": [
            "DesignSpaceSearchStrategyDatabase"
        ],
        "_private.math_utility.optimisation._1756": ["InputSetter"],
        "_private.math_utility.optimisation._1757": ["Optimisable"],
        "_private.math_utility.optimisation._1758": ["OptimisationHistory"],
        "_private.math_utility.optimisation._1759": ["OptimizationInput"],
        "_private.math_utility.optimisation._1760": ["OptimizationProperty"],
        "_private.math_utility.optimisation._1761": ["OptimizationVariable"],
        "_private.math_utility.optimisation._1762": ["ParetoOptimisationFilter"],
        "_private.math_utility.optimisation._1763": ["ParetoOptimisationInput"],
        "_private.math_utility.optimisation._1764": ["ParetoOptimisationOutput"],
        "_private.math_utility.optimisation._1765": ["ParetoOptimisationStrategy"],
        "_private.math_utility.optimisation._1766": ["ParetoOptimisationStrategyBars"],
        "_private.math_utility.optimisation._1767": [
            "ParetoOptimisationStrategyChartInformation"
        ],
        "_private.math_utility.optimisation._1768": [
            "ParetoOptimisationStrategyDatabase"
        ],
        "_private.math_utility.optimisation._1769": ["ParetoOptimisationVariable"],
        "_private.math_utility.optimisation._1770": ["ParetoOptimisationVariableBase"],
        "_private.math_utility.optimisation._1771": [
            "PropertyTargetForDominantCandidateSearch"
        ],
        "_private.math_utility.optimisation._1772": ["ReportingOptimizationInput"],
        "_private.math_utility.optimisation._1773": ["SpecifyOptimisationInputAs"],
        "_private.math_utility.optimisation._1774": ["TargetingPropertyTo"],
    }

    __sys.modules[__name__] = __LazyImporter(
        "mastapy",
        globals()["__file__"],
        __import_structure,
    )

__all__ = (
    "AbstractOptimisable",
    "DesignSpaceSearchStrategyDatabase",
    "InputSetter",
    "Optimisable",
    "OptimisationHistory",
    "OptimizationInput",
    "OptimizationProperty",
    "OptimizationVariable",
    "ParetoOptimisationFilter",
    "ParetoOptimisationInput",
    "ParetoOptimisationOutput",
    "ParetoOptimisationStrategy",
    "ParetoOptimisationStrategyBars",
    "ParetoOptimisationStrategyChartInformation",
    "ParetoOptimisationStrategyDatabase",
    "ParetoOptimisationVariable",
    "ParetoOptimisationVariableBase",
    "PropertyTargetForDominantCandidateSearch",
    "ReportingOptimizationInput",
    "SpecifyOptimisationInputAs",
    "TargetingPropertyTo",
)
