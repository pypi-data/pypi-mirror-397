"""Subpackage."""

from typing import TYPE_CHECKING as __tc

if __tc:
    from mastapy._private.detailed_rigid_connectors.keyed_joints._1649 import (
        KeyedJointDesign,
    )
    from mastapy._private.detailed_rigid_connectors.keyed_joints._1650 import KeyTypes
    from mastapy._private.detailed_rigid_connectors.keyed_joints._1651 import (
        KeywayJointHalfDesign,
    )
    from mastapy._private.detailed_rigid_connectors.keyed_joints._1652 import (
        NumberOfKeys,
    )
else:
    import sys as __sys

    from lazy_imports import LazyImporter as __LazyImporter

    __import_structure = {
        "_private.detailed_rigid_connectors.keyed_joints._1649": ["KeyedJointDesign"],
        "_private.detailed_rigid_connectors.keyed_joints._1650": ["KeyTypes"],
        "_private.detailed_rigid_connectors.keyed_joints._1651": [
            "KeywayJointHalfDesign"
        ],
        "_private.detailed_rigid_connectors.keyed_joints._1652": ["NumberOfKeys"],
    }

    __sys.modules[__name__] = __LazyImporter(
        "mastapy",
        globals()["__file__"],
        __import_structure,
    )

__all__ = (
    "KeyedJointDesign",
    "KeyTypes",
    "KeywayJointHalfDesign",
    "NumberOfKeys",
)
