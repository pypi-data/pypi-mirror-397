"""Subpackage."""

from typing import TYPE_CHECKING as __tc

if __tc:
    from mastapy._private.system_model.part_model.part_groups._2765 import (
        ConcentricOrParallelPartGroup,
    )
    from mastapy._private.system_model.part_model.part_groups._2766 import (
        ConcentricPartGroup,
    )
    from mastapy._private.system_model.part_model.part_groups._2767 import (
        ConcentricPartGroupParallelToThis,
    )
    from mastapy._private.system_model.part_model.part_groups._2768 import (
        DesignMeasurements,
    )
    from mastapy._private.system_model.part_model.part_groups._2769 import (
        ParallelPartGroup,
    )
    from mastapy._private.system_model.part_model.part_groups._2770 import (
        ParallelPartGroupSelection,
    )
    from mastapy._private.system_model.part_model.part_groups._2771 import PartGroup
else:
    import sys as __sys

    from lazy_imports import LazyImporter as __LazyImporter

    __import_structure = {
        "_private.system_model.part_model.part_groups._2765": [
            "ConcentricOrParallelPartGroup"
        ],
        "_private.system_model.part_model.part_groups._2766": ["ConcentricPartGroup"],
        "_private.system_model.part_model.part_groups._2767": [
            "ConcentricPartGroupParallelToThis"
        ],
        "_private.system_model.part_model.part_groups._2768": ["DesignMeasurements"],
        "_private.system_model.part_model.part_groups._2769": ["ParallelPartGroup"],
        "_private.system_model.part_model.part_groups._2770": [
            "ParallelPartGroupSelection"
        ],
        "_private.system_model.part_model.part_groups._2771": ["PartGroup"],
    }

    __sys.modules[__name__] = __LazyImporter(
        "mastapy",
        globals()["__file__"],
        __import_structure,
    )

__all__ = (
    "ConcentricOrParallelPartGroup",
    "ConcentricPartGroup",
    "ConcentricPartGroupParallelToThis",
    "DesignMeasurements",
    "ParallelPartGroup",
    "ParallelPartGroupSelection",
    "PartGroup",
)
