"""Subpackage."""

from typing import TYPE_CHECKING as __tc

if __tc:
    from mastapy._private.gears.gear_designs.cylindrical.accuracy_and_tolerances._1273 import (
        AGMA2000A88AccuracyGrader,
    )
    from mastapy._private.gears.gear_designs.cylindrical.accuracy_and_tolerances._1274 import (
        AGMA20151A01AccuracyGrader,
    )
    from mastapy._private.gears.gear_designs.cylindrical.accuracy_and_tolerances._1275 import (
        AGMA20151AccuracyGrades,
    )
    from mastapy._private.gears.gear_designs.cylindrical.accuracy_and_tolerances._1276 import (
        AGMAISO13281B14AccuracyGrader,
    )
    from mastapy._private.gears.gear_designs.cylindrical.accuracy_and_tolerances._1277 import (
        Customer102AGMA2000AccuracyGrader,
    )
    from mastapy._private.gears.gear_designs.cylindrical.accuracy_and_tolerances._1278 import (
        CylindricalAccuracyGrader,
    )
    from mastapy._private.gears.gear_designs.cylindrical.accuracy_and_tolerances._1279 import (
        CylindricalAccuracyGraderBase,
    )
    from mastapy._private.gears.gear_designs.cylindrical.accuracy_and_tolerances._1280 import (
        CylindricalAccuracyGraderWithProfileFormAndSlope,
    )
    from mastapy._private.gears.gear_designs.cylindrical.accuracy_and_tolerances._1281 import (
        CylindricalAccuracyGrades,
    )
    from mastapy._private.gears.gear_designs.cylindrical.accuracy_and_tolerances._1282 import (
        CylindricalGearAccuracyTolerances,
    )
    from mastapy._private.gears.gear_designs.cylindrical.accuracy_and_tolerances._1283 import (
        DIN3962AccuracyGrader,
    )
    from mastapy._private.gears.gear_designs.cylindrical.accuracy_and_tolerances._1284 import (
        DIN3962AccuracyGrades,
    )
    from mastapy._private.gears.gear_designs.cylindrical.accuracy_and_tolerances._1285 import (
        DIN3967SystemOfGearFits,
    )
    from mastapy._private.gears.gear_designs.cylindrical.accuracy_and_tolerances._1286 import (
        ISO132811995AccuracyGrader,
    )
    from mastapy._private.gears.gear_designs.cylindrical.accuracy_and_tolerances._1287 import (
        ISO132812013AccuracyGrader,
    )
    from mastapy._private.gears.gear_designs.cylindrical.accuracy_and_tolerances._1288 import (
        ISO1328AccuracyGraderCommon,
    )
    from mastapy._private.gears.gear_designs.cylindrical.accuracy_and_tolerances._1289 import (
        ISO1328AccuracyGrades,
    )
    from mastapy._private.gears.gear_designs.cylindrical.accuracy_and_tolerances._1290 import (
        OverridableTolerance,
    )
else:
    import sys as __sys

    from lazy_imports import LazyImporter as __LazyImporter

    __import_structure = {
        "_private.gears.gear_designs.cylindrical.accuracy_and_tolerances._1273": [
            "AGMA2000A88AccuracyGrader"
        ],
        "_private.gears.gear_designs.cylindrical.accuracy_and_tolerances._1274": [
            "AGMA20151A01AccuracyGrader"
        ],
        "_private.gears.gear_designs.cylindrical.accuracy_and_tolerances._1275": [
            "AGMA20151AccuracyGrades"
        ],
        "_private.gears.gear_designs.cylindrical.accuracy_and_tolerances._1276": [
            "AGMAISO13281B14AccuracyGrader"
        ],
        "_private.gears.gear_designs.cylindrical.accuracy_and_tolerances._1277": [
            "Customer102AGMA2000AccuracyGrader"
        ],
        "_private.gears.gear_designs.cylindrical.accuracy_and_tolerances._1278": [
            "CylindricalAccuracyGrader"
        ],
        "_private.gears.gear_designs.cylindrical.accuracy_and_tolerances._1279": [
            "CylindricalAccuracyGraderBase"
        ],
        "_private.gears.gear_designs.cylindrical.accuracy_and_tolerances._1280": [
            "CylindricalAccuracyGraderWithProfileFormAndSlope"
        ],
        "_private.gears.gear_designs.cylindrical.accuracy_and_tolerances._1281": [
            "CylindricalAccuracyGrades"
        ],
        "_private.gears.gear_designs.cylindrical.accuracy_and_tolerances._1282": [
            "CylindricalGearAccuracyTolerances"
        ],
        "_private.gears.gear_designs.cylindrical.accuracy_and_tolerances._1283": [
            "DIN3962AccuracyGrader"
        ],
        "_private.gears.gear_designs.cylindrical.accuracy_and_tolerances._1284": [
            "DIN3962AccuracyGrades"
        ],
        "_private.gears.gear_designs.cylindrical.accuracy_and_tolerances._1285": [
            "DIN3967SystemOfGearFits"
        ],
        "_private.gears.gear_designs.cylindrical.accuracy_and_tolerances._1286": [
            "ISO132811995AccuracyGrader"
        ],
        "_private.gears.gear_designs.cylindrical.accuracy_and_tolerances._1287": [
            "ISO132812013AccuracyGrader"
        ],
        "_private.gears.gear_designs.cylindrical.accuracy_and_tolerances._1288": [
            "ISO1328AccuracyGraderCommon"
        ],
        "_private.gears.gear_designs.cylindrical.accuracy_and_tolerances._1289": [
            "ISO1328AccuracyGrades"
        ],
        "_private.gears.gear_designs.cylindrical.accuracy_and_tolerances._1290": [
            "OverridableTolerance"
        ],
    }

    __sys.modules[__name__] = __LazyImporter(
        "mastapy",
        globals()["__file__"],
        __import_structure,
    )

__all__ = (
    "AGMA2000A88AccuracyGrader",
    "AGMA20151A01AccuracyGrader",
    "AGMA20151AccuracyGrades",
    "AGMAISO13281B14AccuracyGrader",
    "Customer102AGMA2000AccuracyGrader",
    "CylindricalAccuracyGrader",
    "CylindricalAccuracyGraderBase",
    "CylindricalAccuracyGraderWithProfileFormAndSlope",
    "CylindricalAccuracyGrades",
    "CylindricalGearAccuracyTolerances",
    "DIN3962AccuracyGrader",
    "DIN3962AccuracyGrades",
    "DIN3967SystemOfGearFits",
    "ISO132811995AccuracyGrader",
    "ISO132812013AccuracyGrader",
    "ISO1328AccuracyGraderCommon",
    "ISO1328AccuracyGrades",
    "OverridableTolerance",
)
