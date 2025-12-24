"""Subpackage."""

from typing import TYPE_CHECKING as __tc

if __tc:
    from mastapy._private.nodal_analysis.elmer._255 import ContactType
    from mastapy._private.nodal_analysis.elmer._256 import ElectricMachineAnalysisPeriod
    from mastapy._private.nodal_analysis.elmer._257 import ElmerResultEntityType
    from mastapy._private.nodal_analysis.elmer._258 import ElmerResults
    from mastapy._private.nodal_analysis.elmer._259 import ElmerResultsBase
    from mastapy._private.nodal_analysis.elmer._260 import (
        ElmerResultsFromElectromagneticAnalysis,
    )
    from mastapy._private.nodal_analysis.elmer._261 import (
        ElmerResultsFromMechanicalAnalysis,
    )
    from mastapy._private.nodal_analysis.elmer._262 import ElmerResultsViewable
    from mastapy._private.nodal_analysis.elmer._263 import ElmerResultType
    from mastapy._private.nodal_analysis.elmer._265 import (
        MechanicalContactSpecification,
    )
    from mastapy._private.nodal_analysis.elmer._266 import MechanicalSolverType
    from mastapy._private.nodal_analysis.elmer._267 import NodalAverageType
else:
    import sys as __sys

    from lazy_imports import LazyImporter as __LazyImporter

    __import_structure = {
        "_private.nodal_analysis.elmer._255": ["ContactType"],
        "_private.nodal_analysis.elmer._256": ["ElectricMachineAnalysisPeriod"],
        "_private.nodal_analysis.elmer._257": ["ElmerResultEntityType"],
        "_private.nodal_analysis.elmer._258": ["ElmerResults"],
        "_private.nodal_analysis.elmer._259": ["ElmerResultsBase"],
        "_private.nodal_analysis.elmer._260": [
            "ElmerResultsFromElectromagneticAnalysis"
        ],
        "_private.nodal_analysis.elmer._261": ["ElmerResultsFromMechanicalAnalysis"],
        "_private.nodal_analysis.elmer._262": ["ElmerResultsViewable"],
        "_private.nodal_analysis.elmer._263": ["ElmerResultType"],
        "_private.nodal_analysis.elmer._265": ["MechanicalContactSpecification"],
        "_private.nodal_analysis.elmer._266": ["MechanicalSolverType"],
        "_private.nodal_analysis.elmer._267": ["NodalAverageType"],
    }

    __sys.modules[__name__] = __LazyImporter(
        "mastapy",
        globals()["__file__"],
        __import_structure,
    )

__all__ = (
    "ContactType",
    "ElectricMachineAnalysisPeriod",
    "ElmerResultEntityType",
    "ElmerResults",
    "ElmerResultsBase",
    "ElmerResultsFromElectromagneticAnalysis",
    "ElmerResultsFromMechanicalAnalysis",
    "ElmerResultsViewable",
    "ElmerResultType",
    "MechanicalContactSpecification",
    "MechanicalSolverType",
    "NodalAverageType",
)
