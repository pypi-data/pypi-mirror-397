"""Subpackage."""

from typing import TYPE_CHECKING as __tc

if __tc:
    from mastapy._private.nodal_analysis.system_solvers._112 import (
        BackwardEulerTransientSolver,
    )
    from mastapy._private.nodal_analysis.system_solvers._113 import DenseStiffnessSolver
    from mastapy._private.nodal_analysis.system_solvers._114 import DirkTransientSolver
    from mastapy._private.nodal_analysis.system_solvers._115 import DynamicSolver
    from mastapy._private.nodal_analysis.system_solvers._116 import (
        InternalTransientSolver,
    )
    from mastapy._private.nodal_analysis.system_solvers._117 import (
        LobattoIIICTransientSolver,
    )
    from mastapy._private.nodal_analysis.system_solvers._118 import (
        NewmarkTransientSolver,
    )
    from mastapy._private.nodal_analysis.system_solvers._119 import (
        NewtonRaphsonAnalysis,
    )
    from mastapy._private.nodal_analysis.system_solvers._120 import (
        NewtonRaphsonDegreeOfFreedomError,
    )
    from mastapy._private.nodal_analysis.system_solvers._121 import (
        SimpleVelocityBasedStepHalvingTransientSolver,
    )
    from mastapy._private.nodal_analysis.system_solvers._122 import (
        SingularDegreeOfFreedomAnalysis,
    )
    from mastapy._private.nodal_analysis.system_solvers._123 import (
        SingularValuesAnalysis,
    )
    from mastapy._private.nodal_analysis.system_solvers._124 import (
        SingularVectorAnalysis,
    )
    from mastapy._private.nodal_analysis.system_solvers._125 import Solver
    from mastapy._private.nodal_analysis.system_solvers._126 import (
        StepHalvingTransientSolver,
    )
    from mastapy._private.nodal_analysis.system_solvers._127 import StiffnessSolver
    from mastapy._private.nodal_analysis.system_solvers._128 import ThermalSolver
    from mastapy._private.nodal_analysis.system_solvers._129 import TransientSolver
    from mastapy._private.nodal_analysis.system_solvers._130 import (
        WilsonThetaTransientSolver,
    )
else:
    import sys as __sys

    from lazy_imports import LazyImporter as __LazyImporter

    __import_structure = {
        "_private.nodal_analysis.system_solvers._112": ["BackwardEulerTransientSolver"],
        "_private.nodal_analysis.system_solvers._113": ["DenseStiffnessSolver"],
        "_private.nodal_analysis.system_solvers._114": ["DirkTransientSolver"],
        "_private.nodal_analysis.system_solvers._115": ["DynamicSolver"],
        "_private.nodal_analysis.system_solvers._116": ["InternalTransientSolver"],
        "_private.nodal_analysis.system_solvers._117": ["LobattoIIICTransientSolver"],
        "_private.nodal_analysis.system_solvers._118": ["NewmarkTransientSolver"],
        "_private.nodal_analysis.system_solvers._119": ["NewtonRaphsonAnalysis"],
        "_private.nodal_analysis.system_solvers._120": [
            "NewtonRaphsonDegreeOfFreedomError"
        ],
        "_private.nodal_analysis.system_solvers._121": [
            "SimpleVelocityBasedStepHalvingTransientSolver"
        ],
        "_private.nodal_analysis.system_solvers._122": [
            "SingularDegreeOfFreedomAnalysis"
        ],
        "_private.nodal_analysis.system_solvers._123": ["SingularValuesAnalysis"],
        "_private.nodal_analysis.system_solvers._124": ["SingularVectorAnalysis"],
        "_private.nodal_analysis.system_solvers._125": ["Solver"],
        "_private.nodal_analysis.system_solvers._126": ["StepHalvingTransientSolver"],
        "_private.nodal_analysis.system_solvers._127": ["StiffnessSolver"],
        "_private.nodal_analysis.system_solvers._128": ["ThermalSolver"],
        "_private.nodal_analysis.system_solvers._129": ["TransientSolver"],
        "_private.nodal_analysis.system_solvers._130": ["WilsonThetaTransientSolver"],
    }

    __sys.modules[__name__] = __LazyImporter(
        "mastapy",
        globals()["__file__"],
        __import_structure,
    )

__all__ = (
    "BackwardEulerTransientSolver",
    "DenseStiffnessSolver",
    "DirkTransientSolver",
    "DynamicSolver",
    "InternalTransientSolver",
    "LobattoIIICTransientSolver",
    "NewmarkTransientSolver",
    "NewtonRaphsonAnalysis",
    "NewtonRaphsonDegreeOfFreedomError",
    "SimpleVelocityBasedStepHalvingTransientSolver",
    "SingularDegreeOfFreedomAnalysis",
    "SingularValuesAnalysis",
    "SingularVectorAnalysis",
    "Solver",
    "StepHalvingTransientSolver",
    "StiffnessSolver",
    "ThermalSolver",
    "TransientSolver",
    "WilsonThetaTransientSolver",
)
