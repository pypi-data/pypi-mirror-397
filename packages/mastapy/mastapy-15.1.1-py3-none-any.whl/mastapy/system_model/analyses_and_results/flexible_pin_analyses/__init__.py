"""Subpackage."""

from typing import TYPE_CHECKING as __tc

if __tc:
    from mastapy._private.system_model.analyses_and_results.flexible_pin_analyses._6632 import (
        CombinationAnalysis,
    )
    from mastapy._private.system_model.analyses_and_results.flexible_pin_analyses._6633 import (
        FlexiblePinAnalysis,
    )
    from mastapy._private.system_model.analyses_and_results.flexible_pin_analyses._6634 import (
        FlexiblePinAnalysisConceptLevel,
    )
    from mastapy._private.system_model.analyses_and_results.flexible_pin_analyses._6635 import (
        FlexiblePinAnalysisDetailLevelAndPinFatigueOneToothPass,
    )
    from mastapy._private.system_model.analyses_and_results.flexible_pin_analyses._6636 import (
        FlexiblePinAnalysisGearAndBearingRating,
    )
    from mastapy._private.system_model.analyses_and_results.flexible_pin_analyses._6637 import (
        FlexiblePinAnalysisManufactureLevel,
    )
    from mastapy._private.system_model.analyses_and_results.flexible_pin_analyses._6638 import (
        FlexiblePinAnalysisOptions,
    )
    from mastapy._private.system_model.analyses_and_results.flexible_pin_analyses._6639 import (
        FlexiblePinAnalysisStopStartAnalysis,
    )
    from mastapy._private.system_model.analyses_and_results.flexible_pin_analyses._6640 import (
        WindTurbineCertificationReport,
    )
else:
    import sys as __sys

    from lazy_imports import LazyImporter as __LazyImporter

    __import_structure = {
        "_private.system_model.analyses_and_results.flexible_pin_analyses._6632": [
            "CombinationAnalysis"
        ],
        "_private.system_model.analyses_and_results.flexible_pin_analyses._6633": [
            "FlexiblePinAnalysis"
        ],
        "_private.system_model.analyses_and_results.flexible_pin_analyses._6634": [
            "FlexiblePinAnalysisConceptLevel"
        ],
        "_private.system_model.analyses_and_results.flexible_pin_analyses._6635": [
            "FlexiblePinAnalysisDetailLevelAndPinFatigueOneToothPass"
        ],
        "_private.system_model.analyses_and_results.flexible_pin_analyses._6636": [
            "FlexiblePinAnalysisGearAndBearingRating"
        ],
        "_private.system_model.analyses_and_results.flexible_pin_analyses._6637": [
            "FlexiblePinAnalysisManufactureLevel"
        ],
        "_private.system_model.analyses_and_results.flexible_pin_analyses._6638": [
            "FlexiblePinAnalysisOptions"
        ],
        "_private.system_model.analyses_and_results.flexible_pin_analyses._6639": [
            "FlexiblePinAnalysisStopStartAnalysis"
        ],
        "_private.system_model.analyses_and_results.flexible_pin_analyses._6640": [
            "WindTurbineCertificationReport"
        ],
    }

    __sys.modules[__name__] = __LazyImporter(
        "mastapy",
        globals()["__file__"],
        __import_structure,
    )

__all__ = (
    "CombinationAnalysis",
    "FlexiblePinAnalysis",
    "FlexiblePinAnalysisConceptLevel",
    "FlexiblePinAnalysisDetailLevelAndPinFatigueOneToothPass",
    "FlexiblePinAnalysisGearAndBearingRating",
    "FlexiblePinAnalysisManufactureLevel",
    "FlexiblePinAnalysisOptions",
    "FlexiblePinAnalysisStopStartAnalysis",
    "WindTurbineCertificationReport",
)
