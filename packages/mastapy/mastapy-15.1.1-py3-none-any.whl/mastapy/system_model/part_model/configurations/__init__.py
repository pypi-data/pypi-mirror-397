"""Subpackage."""

from typing import TYPE_CHECKING as __tc

if __tc:
    from mastapy._private.system_model.part_model.configurations._2901 import (
        ActiveFESubstructureSelection,
    )
    from mastapy._private.system_model.part_model.configurations._2902 import (
        ActiveFESubstructureSelectionGroup,
    )
    from mastapy._private.system_model.part_model.configurations._2903 import (
        ActiveShaftDesignSelection,
    )
    from mastapy._private.system_model.part_model.configurations._2904 import (
        ActiveShaftDesignSelectionGroup,
    )
    from mastapy._private.system_model.part_model.configurations._2905 import (
        BearingDetailConfiguration,
    )
    from mastapy._private.system_model.part_model.configurations._2906 import (
        BearingDetailSelection,
    )
    from mastapy._private.system_model.part_model.configurations._2907 import (
        DesignConfiguration,
    )
    from mastapy._private.system_model.part_model.configurations._2908 import (
        PartDetailConfiguration,
    )
    from mastapy._private.system_model.part_model.configurations._2909 import (
        PartDetailSelection,
    )
else:
    import sys as __sys

    from lazy_imports import LazyImporter as __LazyImporter

    __import_structure = {
        "_private.system_model.part_model.configurations._2901": [
            "ActiveFESubstructureSelection"
        ],
        "_private.system_model.part_model.configurations._2902": [
            "ActiveFESubstructureSelectionGroup"
        ],
        "_private.system_model.part_model.configurations._2903": [
            "ActiveShaftDesignSelection"
        ],
        "_private.system_model.part_model.configurations._2904": [
            "ActiveShaftDesignSelectionGroup"
        ],
        "_private.system_model.part_model.configurations._2905": [
            "BearingDetailConfiguration"
        ],
        "_private.system_model.part_model.configurations._2906": [
            "BearingDetailSelection"
        ],
        "_private.system_model.part_model.configurations._2907": [
            "DesignConfiguration"
        ],
        "_private.system_model.part_model.configurations._2908": [
            "PartDetailConfiguration"
        ],
        "_private.system_model.part_model.configurations._2909": [
            "PartDetailSelection"
        ],
    }

    __sys.modules[__name__] = __LazyImporter(
        "mastapy",
        globals()["__file__"],
        __import_structure,
    )

__all__ = (
    "ActiveFESubstructureSelection",
    "ActiveFESubstructureSelectionGroup",
    "ActiveShaftDesignSelection",
    "ActiveShaftDesignSelectionGroup",
    "BearingDetailConfiguration",
    "BearingDetailSelection",
    "DesignConfiguration",
    "PartDetailConfiguration",
    "PartDetailSelection",
)
