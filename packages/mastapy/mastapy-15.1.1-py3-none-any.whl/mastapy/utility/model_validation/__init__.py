"""Subpackage."""

from typing import TYPE_CHECKING as __tc

if __tc:
    from mastapy._private.utility.model_validation._2018 import Fix
    from mastapy._private.utility.model_validation._2019 import Severity
    from mastapy._private.utility.model_validation._2020 import Status
    from mastapy._private.utility.model_validation._2021 import StatusItem
    from mastapy._private.utility.model_validation._2022 import StatusItemSeverity
    from mastapy._private.utility.model_validation._2023 import StatusItemWrapper
    from mastapy._private.utility.model_validation._2024 import StatusWrapper
else:
    import sys as __sys

    from lazy_imports import LazyImporter as __LazyImporter

    __import_structure = {
        "_private.utility.model_validation._2018": ["Fix"],
        "_private.utility.model_validation._2019": ["Severity"],
        "_private.utility.model_validation._2020": ["Status"],
        "_private.utility.model_validation._2021": ["StatusItem"],
        "_private.utility.model_validation._2022": ["StatusItemSeverity"],
        "_private.utility.model_validation._2023": ["StatusItemWrapper"],
        "_private.utility.model_validation._2024": ["StatusWrapper"],
    }

    __sys.modules[__name__] = __LazyImporter(
        "mastapy",
        globals()["__file__"],
        __import_structure,
    )

__all__ = (
    "Fix",
    "Severity",
    "Status",
    "StatusItem",
    "StatusItemSeverity",
    "StatusItemWrapper",
    "StatusWrapper",
)
