"""Subpackage."""

from typing import TYPE_CHECKING as __tc

if __tc:
    from mastapy._private.utility.units_and_measurements._1826 import (
        DegreesMinutesSeconds,
    )
    from mastapy._private.utility.units_and_measurements._1827 import EnumUnit
    from mastapy._private.utility.units_and_measurements._1828 import InverseUnit
    from mastapy._private.utility.units_and_measurements._1829 import MeasurementBase
    from mastapy._private.utility.units_and_measurements._1830 import (
        MeasurementSettings,
    )
    from mastapy._private.utility.units_and_measurements._1831 import MeasurementSystem
    from mastapy._private.utility.units_and_measurements._1832 import SafetyFactorUnit
    from mastapy._private.utility.units_and_measurements._1833 import TimeUnit
    from mastapy._private.utility.units_and_measurements._1834 import Unit
    from mastapy._private.utility.units_and_measurements._1835 import UnitGradient
else:
    import sys as __sys

    from lazy_imports import LazyImporter as __LazyImporter

    __import_structure = {
        "_private.utility.units_and_measurements._1826": ["DegreesMinutesSeconds"],
        "_private.utility.units_and_measurements._1827": ["EnumUnit"],
        "_private.utility.units_and_measurements._1828": ["InverseUnit"],
        "_private.utility.units_and_measurements._1829": ["MeasurementBase"],
        "_private.utility.units_and_measurements._1830": ["MeasurementSettings"],
        "_private.utility.units_and_measurements._1831": ["MeasurementSystem"],
        "_private.utility.units_and_measurements._1832": ["SafetyFactorUnit"],
        "_private.utility.units_and_measurements._1833": ["TimeUnit"],
        "_private.utility.units_and_measurements._1834": ["Unit"],
        "_private.utility.units_and_measurements._1835": ["UnitGradient"],
    }

    __sys.modules[__name__] = __LazyImporter(
        "mastapy",
        globals()["__file__"],
        __import_structure,
    )

__all__ = (
    "DegreesMinutesSeconds",
    "EnumUnit",
    "InverseUnit",
    "MeasurementBase",
    "MeasurementSettings",
    "MeasurementSystem",
    "SafetyFactorUnit",
    "TimeUnit",
    "Unit",
    "UnitGradient",
)
