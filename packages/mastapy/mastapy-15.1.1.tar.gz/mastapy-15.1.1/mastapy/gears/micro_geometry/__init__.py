"""Subpackage."""

from typing import TYPE_CHECKING as __tc

if __tc:
    from mastapy._private.gears.micro_geometry._682 import BiasModification
    from mastapy._private.gears.micro_geometry._683 import FlankMicroGeometry
    from mastapy._private.gears.micro_geometry._684 import FlankSide
    from mastapy._private.gears.micro_geometry._685 import LeadModification
    from mastapy._private.gears.micro_geometry._686 import (
        LocationOfEvaluationLowerLimit,
    )
    from mastapy._private.gears.micro_geometry._687 import (
        LocationOfEvaluationUpperLimit,
    )
    from mastapy._private.gears.micro_geometry._688 import (
        LocationOfRootReliefEvaluation,
    )
    from mastapy._private.gears.micro_geometry._689 import LocationOfTipReliefEvaluation
    from mastapy._private.gears.micro_geometry._690 import (
        MainProfileReliefEndsAtTheStartOfRootReliefOption,
    )
    from mastapy._private.gears.micro_geometry._691 import (
        MainProfileReliefEndsAtTheStartOfTipReliefOption,
    )
    from mastapy._private.gears.micro_geometry._692 import Modification
    from mastapy._private.gears.micro_geometry._693 import (
        ParabolicRootReliefStartsTangentToMainProfileRelief,
    )
    from mastapy._private.gears.micro_geometry._694 import (
        ParabolicTipReliefStartsTangentToMainProfileRelief,
    )
    from mastapy._private.gears.micro_geometry._695 import ProfileModification
else:
    import sys as __sys

    from lazy_imports import LazyImporter as __LazyImporter

    __import_structure = {
        "_private.gears.micro_geometry._682": ["BiasModification"],
        "_private.gears.micro_geometry._683": ["FlankMicroGeometry"],
        "_private.gears.micro_geometry._684": ["FlankSide"],
        "_private.gears.micro_geometry._685": ["LeadModification"],
        "_private.gears.micro_geometry._686": ["LocationOfEvaluationLowerLimit"],
        "_private.gears.micro_geometry._687": ["LocationOfEvaluationUpperLimit"],
        "_private.gears.micro_geometry._688": ["LocationOfRootReliefEvaluation"],
        "_private.gears.micro_geometry._689": ["LocationOfTipReliefEvaluation"],
        "_private.gears.micro_geometry._690": [
            "MainProfileReliefEndsAtTheStartOfRootReliefOption"
        ],
        "_private.gears.micro_geometry._691": [
            "MainProfileReliefEndsAtTheStartOfTipReliefOption"
        ],
        "_private.gears.micro_geometry._692": ["Modification"],
        "_private.gears.micro_geometry._693": [
            "ParabolicRootReliefStartsTangentToMainProfileRelief"
        ],
        "_private.gears.micro_geometry._694": [
            "ParabolicTipReliefStartsTangentToMainProfileRelief"
        ],
        "_private.gears.micro_geometry._695": ["ProfileModification"],
    }

    __sys.modules[__name__] = __LazyImporter(
        "mastapy",
        globals()["__file__"],
        __import_structure,
    )

__all__ = (
    "BiasModification",
    "FlankMicroGeometry",
    "FlankSide",
    "LeadModification",
    "LocationOfEvaluationLowerLimit",
    "LocationOfEvaluationUpperLimit",
    "LocationOfRootReliefEvaluation",
    "LocationOfTipReliefEvaluation",
    "MainProfileReliefEndsAtTheStartOfRootReliefOption",
    "MainProfileReliefEndsAtTheStartOfTipReliefOption",
    "Modification",
    "ParabolicRootReliefStartsTangentToMainProfileRelief",
    "ParabolicTipReliefStartsTangentToMainProfileRelief",
    "ProfileModification",
)
