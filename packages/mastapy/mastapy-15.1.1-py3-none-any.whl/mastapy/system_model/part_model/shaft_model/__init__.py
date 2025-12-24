"""Subpackage."""

from typing import TYPE_CHECKING as __tc

if __tc:
    from mastapy._private.system_model.part_model.shaft_model._2758 import Shaft
    from mastapy._private.system_model.part_model.shaft_model._2759 import ShaftBow
    from mastapy._private.system_model.part_model.shaft_model._2760 import (
        WindageLossCalculationOilParameters,
    )
    from mastapy._private.system_model.part_model.shaft_model._2761 import (
        WindageLossCalculationParametersForCurvedSurfaceOfSection,
    )
    from mastapy._private.system_model.part_model.shaft_model._2762 import (
        WindageLossCalculationParametersForEndOfSection,
    )
else:
    import sys as __sys

    from lazy_imports import LazyImporter as __LazyImporter

    __import_structure = {
        "_private.system_model.part_model.shaft_model._2758": ["Shaft"],
        "_private.system_model.part_model.shaft_model._2759": ["ShaftBow"],
        "_private.system_model.part_model.shaft_model._2760": [
            "WindageLossCalculationOilParameters"
        ],
        "_private.system_model.part_model.shaft_model._2761": [
            "WindageLossCalculationParametersForCurvedSurfaceOfSection"
        ],
        "_private.system_model.part_model.shaft_model._2762": [
            "WindageLossCalculationParametersForEndOfSection"
        ],
    }

    __sys.modules[__name__] = __LazyImporter(
        "mastapy",
        globals()["__file__"],
        __import_structure,
    )

__all__ = (
    "Shaft",
    "ShaftBow",
    "WindageLossCalculationOilParameters",
    "WindageLossCalculationParametersForCurvedSurfaceOfSection",
    "WindageLossCalculationParametersForEndOfSection",
)
