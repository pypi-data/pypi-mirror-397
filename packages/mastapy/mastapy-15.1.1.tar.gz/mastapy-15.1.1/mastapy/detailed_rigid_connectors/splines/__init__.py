"""Subpackage."""

from typing import TYPE_CHECKING as __tc

if __tc:
    from mastapy._private.detailed_rigid_connectors.splines._1601 import (
        CustomSplineHalfDesign,
    )
    from mastapy._private.detailed_rigid_connectors.splines._1602 import (
        CustomSplineJointDesign,
    )
    from mastapy._private.detailed_rigid_connectors.splines._1603 import (
        DetailedSplineJointSettings,
    )
    from mastapy._private.detailed_rigid_connectors.splines._1604 import (
        DIN5480SplineHalfDesign,
    )
    from mastapy._private.detailed_rigid_connectors.splines._1605 import (
        DIN5480SplineJointDesign,
    )
    from mastapy._private.detailed_rigid_connectors.splines._1606 import (
        DudleyEffectiveLengthApproximationOption,
    )
    from mastapy._private.detailed_rigid_connectors.splines._1607 import FitTypes
    from mastapy._private.detailed_rigid_connectors.splines._1608 import (
        GBT3478SplineHalfDesign,
    )
    from mastapy._private.detailed_rigid_connectors.splines._1609 import (
        GBT3478SplineJointDesign,
    )
    from mastapy._private.detailed_rigid_connectors.splines._1610 import (
        HeatTreatmentTypes,
    )
    from mastapy._private.detailed_rigid_connectors.splines._1611 import (
        ISO4156SplineHalfDesign,
    )
    from mastapy._private.detailed_rigid_connectors.splines._1612 import (
        ISO4156SplineJointDesign,
    )
    from mastapy._private.detailed_rigid_connectors.splines._1613 import (
        JISB1603SplineJointDesign,
    )
    from mastapy._private.detailed_rigid_connectors.splines._1614 import (
        ManufacturingTypes,
    )
    from mastapy._private.detailed_rigid_connectors.splines._1615 import Modules
    from mastapy._private.detailed_rigid_connectors.splines._1616 import (
        PressureAngleTypes,
    )
    from mastapy._private.detailed_rigid_connectors.splines._1617 import RootTypes
    from mastapy._private.detailed_rigid_connectors.splines._1618 import (
        SAEFatigueLifeFactorTypes,
    )
    from mastapy._private.detailed_rigid_connectors.splines._1619 import (
        SAESplineHalfDesign,
    )
    from mastapy._private.detailed_rigid_connectors.splines._1620 import (
        SAESplineJointDesign,
    )
    from mastapy._private.detailed_rigid_connectors.splines._1621 import SAETorqueCycles
    from mastapy._private.detailed_rigid_connectors.splines._1622 import (
        SplineDesignTypes,
    )
    from mastapy._private.detailed_rigid_connectors.splines._1623 import (
        FinishingMethods,
    )
    from mastapy._private.detailed_rigid_connectors.splines._1624 import (
        SplineFitClassType,
    )
    from mastapy._private.detailed_rigid_connectors.splines._1625 import (
        SplineFixtureTypes,
    )
    from mastapy._private.detailed_rigid_connectors.splines._1626 import (
        SplineHalfDesign,
    )
    from mastapy._private.detailed_rigid_connectors.splines._1627 import (
        SplineJointDesign,
    )
    from mastapy._private.detailed_rigid_connectors.splines._1628 import SplineMaterial
    from mastapy._private.detailed_rigid_connectors.splines._1629 import (
        SplineRatingTypes,
    )
    from mastapy._private.detailed_rigid_connectors.splines._1630 import (
        SplineToleranceClassTypes,
    )
    from mastapy._private.detailed_rigid_connectors.splines._1631 import (
        StandardSplineHalfDesign,
    )
    from mastapy._private.detailed_rigid_connectors.splines._1632 import (
        StandardSplineJointDesign,
    )
else:
    import sys as __sys

    from lazy_imports import LazyImporter as __LazyImporter

    __import_structure = {
        "_private.detailed_rigid_connectors.splines._1601": ["CustomSplineHalfDesign"],
        "_private.detailed_rigid_connectors.splines._1602": ["CustomSplineJointDesign"],
        "_private.detailed_rigid_connectors.splines._1603": [
            "DetailedSplineJointSettings"
        ],
        "_private.detailed_rigid_connectors.splines._1604": ["DIN5480SplineHalfDesign"],
        "_private.detailed_rigid_connectors.splines._1605": [
            "DIN5480SplineJointDesign"
        ],
        "_private.detailed_rigid_connectors.splines._1606": [
            "DudleyEffectiveLengthApproximationOption"
        ],
        "_private.detailed_rigid_connectors.splines._1607": ["FitTypes"],
        "_private.detailed_rigid_connectors.splines._1608": ["GBT3478SplineHalfDesign"],
        "_private.detailed_rigid_connectors.splines._1609": [
            "GBT3478SplineJointDesign"
        ],
        "_private.detailed_rigid_connectors.splines._1610": ["HeatTreatmentTypes"],
        "_private.detailed_rigid_connectors.splines._1611": ["ISO4156SplineHalfDesign"],
        "_private.detailed_rigid_connectors.splines._1612": [
            "ISO4156SplineJointDesign"
        ],
        "_private.detailed_rigid_connectors.splines._1613": [
            "JISB1603SplineJointDesign"
        ],
        "_private.detailed_rigid_connectors.splines._1614": ["ManufacturingTypes"],
        "_private.detailed_rigid_connectors.splines._1615": ["Modules"],
        "_private.detailed_rigid_connectors.splines._1616": ["PressureAngleTypes"],
        "_private.detailed_rigid_connectors.splines._1617": ["RootTypes"],
        "_private.detailed_rigid_connectors.splines._1618": [
            "SAEFatigueLifeFactorTypes"
        ],
        "_private.detailed_rigid_connectors.splines._1619": ["SAESplineHalfDesign"],
        "_private.detailed_rigid_connectors.splines._1620": ["SAESplineJointDesign"],
        "_private.detailed_rigid_connectors.splines._1621": ["SAETorqueCycles"],
        "_private.detailed_rigid_connectors.splines._1622": ["SplineDesignTypes"],
        "_private.detailed_rigid_connectors.splines._1623": ["FinishingMethods"],
        "_private.detailed_rigid_connectors.splines._1624": ["SplineFitClassType"],
        "_private.detailed_rigid_connectors.splines._1625": ["SplineFixtureTypes"],
        "_private.detailed_rigid_connectors.splines._1626": ["SplineHalfDesign"],
        "_private.detailed_rigid_connectors.splines._1627": ["SplineJointDesign"],
        "_private.detailed_rigid_connectors.splines._1628": ["SplineMaterial"],
        "_private.detailed_rigid_connectors.splines._1629": ["SplineRatingTypes"],
        "_private.detailed_rigid_connectors.splines._1630": [
            "SplineToleranceClassTypes"
        ],
        "_private.detailed_rigid_connectors.splines._1631": [
            "StandardSplineHalfDesign"
        ],
        "_private.detailed_rigid_connectors.splines._1632": [
            "StandardSplineJointDesign"
        ],
    }

    __sys.modules[__name__] = __LazyImporter(
        "mastapy",
        globals()["__file__"],
        __import_structure,
    )

__all__ = (
    "CustomSplineHalfDesign",
    "CustomSplineJointDesign",
    "DetailedSplineJointSettings",
    "DIN5480SplineHalfDesign",
    "DIN5480SplineJointDesign",
    "DudleyEffectiveLengthApproximationOption",
    "FitTypes",
    "GBT3478SplineHalfDesign",
    "GBT3478SplineJointDesign",
    "HeatTreatmentTypes",
    "ISO4156SplineHalfDesign",
    "ISO4156SplineJointDesign",
    "JISB1603SplineJointDesign",
    "ManufacturingTypes",
    "Modules",
    "PressureAngleTypes",
    "RootTypes",
    "SAEFatigueLifeFactorTypes",
    "SAESplineHalfDesign",
    "SAESplineJointDesign",
    "SAETorqueCycles",
    "SplineDesignTypes",
    "FinishingMethods",
    "SplineFitClassType",
    "SplineFixtureTypes",
    "SplineHalfDesign",
    "SplineJointDesign",
    "SplineMaterial",
    "SplineRatingTypes",
    "SplineToleranceClassTypes",
    "StandardSplineHalfDesign",
    "StandardSplineJointDesign",
)
