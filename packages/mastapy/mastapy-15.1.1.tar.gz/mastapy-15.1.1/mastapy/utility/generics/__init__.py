"""Subpackage."""

from typing import TYPE_CHECKING as __tc

if __tc:
    from mastapy._private.utility.generics._2039 import NamedTuple1
    from mastapy._private.utility.generics._2040 import NamedTuple2
    from mastapy._private.utility.generics._2041 import NamedTuple3
    from mastapy._private.utility.generics._2042 import NamedTuple4
    from mastapy._private.utility.generics._2043 import NamedTuple5
    from mastapy._private.utility.generics._2044 import NamedTuple6
    from mastapy._private.utility.generics._2045 import NamedTuple7
else:
    import sys as __sys

    from lazy_imports import LazyImporter as __LazyImporter

    __import_structure = {
        "_private.utility.generics._2039": ["NamedTuple1"],
        "_private.utility.generics._2040": ["NamedTuple2"],
        "_private.utility.generics._2041": ["NamedTuple3"],
        "_private.utility.generics._2042": ["NamedTuple4"],
        "_private.utility.generics._2043": ["NamedTuple5"],
        "_private.utility.generics._2044": ["NamedTuple6"],
        "_private.utility.generics._2045": ["NamedTuple7"],
    }

    __sys.modules[__name__] = __LazyImporter(
        "mastapy",
        globals()["__file__"],
        __import_structure,
    )

__all__ = (
    "NamedTuple1",
    "NamedTuple2",
    "NamedTuple3",
    "NamedTuple4",
    "NamedTuple5",
    "NamedTuple6",
    "NamedTuple7",
)
