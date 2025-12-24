"""Subpackage."""

from typing import TYPE_CHECKING as __tc

if __tc:
    from mastapy._private.detailed_rigid_connectors.splines.ratings._1635 import (
        AGMA6123SplineHalfRating,
    )
    from mastapy._private.detailed_rigid_connectors.splines.ratings._1636 import (
        AGMA6123SplineJointRating,
    )
    from mastapy._private.detailed_rigid_connectors.splines.ratings._1637 import (
        DIN5466SplineHalfRating,
    )
    from mastapy._private.detailed_rigid_connectors.splines.ratings._1638 import (
        DIN5466SplineRating,
    )
    from mastapy._private.detailed_rigid_connectors.splines.ratings._1639 import (
        GBT17855SplineHalfRating,
    )
    from mastapy._private.detailed_rigid_connectors.splines.ratings._1640 import (
        GBT17855SplineJointRating,
    )
    from mastapy._private.detailed_rigid_connectors.splines.ratings._1641 import (
        SAESplineHalfRating,
    )
    from mastapy._private.detailed_rigid_connectors.splines.ratings._1642 import (
        SAESplineJointRating,
    )
    from mastapy._private.detailed_rigid_connectors.splines.ratings._1643 import (
        SplineHalfRating,
    )
    from mastapy._private.detailed_rigid_connectors.splines.ratings._1644 import (
        SplineJointRating,
    )
else:
    import sys as __sys

    from lazy_imports import LazyImporter as __LazyImporter

    __import_structure = {
        "_private.detailed_rigid_connectors.splines.ratings._1635": [
            "AGMA6123SplineHalfRating"
        ],
        "_private.detailed_rigid_connectors.splines.ratings._1636": [
            "AGMA6123SplineJointRating"
        ],
        "_private.detailed_rigid_connectors.splines.ratings._1637": [
            "DIN5466SplineHalfRating"
        ],
        "_private.detailed_rigid_connectors.splines.ratings._1638": [
            "DIN5466SplineRating"
        ],
        "_private.detailed_rigid_connectors.splines.ratings._1639": [
            "GBT17855SplineHalfRating"
        ],
        "_private.detailed_rigid_connectors.splines.ratings._1640": [
            "GBT17855SplineJointRating"
        ],
        "_private.detailed_rigid_connectors.splines.ratings._1641": [
            "SAESplineHalfRating"
        ],
        "_private.detailed_rigid_connectors.splines.ratings._1642": [
            "SAESplineJointRating"
        ],
        "_private.detailed_rigid_connectors.splines.ratings._1643": [
            "SplineHalfRating"
        ],
        "_private.detailed_rigid_connectors.splines.ratings._1644": [
            "SplineJointRating"
        ],
    }

    __sys.modules[__name__] = __LazyImporter(
        "mastapy",
        globals()["__file__"],
        __import_structure,
    )

__all__ = (
    "AGMA6123SplineHalfRating",
    "AGMA6123SplineJointRating",
    "DIN5466SplineHalfRating",
    "DIN5466SplineRating",
    "GBT17855SplineHalfRating",
    "GBT17855SplineJointRating",
    "SAESplineHalfRating",
    "SAESplineJointRating",
    "SplineHalfRating",
    "SplineJointRating",
)
