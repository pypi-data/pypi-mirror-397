"""Subpackage."""

from typing import TYPE_CHECKING as __tc

if __tc:
    from mastapy._private.math_utility._1701 import AcousticWeighting
    from mastapy._private.math_utility._1702 import AlignmentAxis
    from mastapy._private.math_utility._1703 import Axis
    from mastapy._private.math_utility._1704 import CirclesOnAxis
    from mastapy._private.math_utility._1705 import ComplexMatrix
    from mastapy._private.math_utility._1706 import ComplexPartDisplayOption
    from mastapy._private.math_utility._1707 import ComplexVector
    from mastapy._private.math_utility._1708 import ComplexVector3D
    from mastapy._private.math_utility._1709 import ComplexVector6D
    from mastapy._private.math_utility._1710 import CoordinateSystem3D
    from mastapy._private.math_utility._1711 import CoordinateSystemEditor
    from mastapy._private.math_utility._1712 import CoordinateSystemForRotation
    from mastapy._private.math_utility._1713 import CoordinateSystemForRotationOrigin
    from mastapy._private.math_utility._1714 import DataPrecision
    from mastapy._private.math_utility._1715 import DegreeOfFreedom
    from mastapy._private.math_utility._1716 import DynamicsResponseScalarResult
    from mastapy._private.math_utility._1717 import DynamicsResponseScaling
    from mastapy._private.math_utility._1718 import EdgeNamedSelectionDetails
    from mastapy._private.math_utility._1719 import Eigenmode
    from mastapy._private.math_utility._1720 import Eigenmodes
    from mastapy._private.math_utility._1721 import EulerParameters
    from mastapy._private.math_utility._1722 import ExtrapolationOptions
    from mastapy._private.math_utility._1723 import FacetedBody
    from mastapy._private.math_utility._1724 import FacetedSurface
    from mastapy._private.math_utility._1725 import FourierSeries
    from mastapy._private.math_utility._1726 import GenericMatrix
    from mastapy._private.math_utility._1727 import GriddedSurface
    from mastapy._private.math_utility._1728 import HarmonicValue
    from mastapy._private.math_utility._1729 import InertiaTensor
    from mastapy._private.math_utility._1730 import MassProperties
    from mastapy._private.math_utility._1731 import MaxMinMean
    from mastapy._private.math_utility._1732 import ComplexMagnitudeMethod
    from mastapy._private.math_utility._1733 import MultipleFourierSeriesInterpolator
    from mastapy._private.math_utility._1734 import Named2DLocation
    from mastapy._private.math_utility._1735 import NamedSelection
    from mastapy._private.math_utility._1736 import NamedSelectionEdge
    from mastapy._private.math_utility._1737 import NamedSelectionFace
    from mastapy._private.math_utility._1738 import NamedSelections
    from mastapy._private.math_utility._1739 import PIDControlUpdateMethod
    from mastapy._private.math_utility._1740 import Quaternion
    from mastapy._private.math_utility._1741 import RealMatrix
    from mastapy._private.math_utility._1742 import RealVector
    from mastapy._private.math_utility._1743 import ResultOptionsFor3DVector
    from mastapy._private.math_utility._1744 import RotationAxis
    from mastapy._private.math_utility._1745 import RoundedOrder
    from mastapy._private.math_utility._1746 import SinCurve
    from mastapy._private.math_utility._1747 import SquareMatrix
    from mastapy._private.math_utility._1748 import StressPoint
    from mastapy._private.math_utility._1749 import TranslationRotation
    from mastapy._private.math_utility._1750 import Vector2DListAccessor
    from mastapy._private.math_utility._1751 import Vector6D
else:
    import sys as __sys

    from lazy_imports import LazyImporter as __LazyImporter

    __import_structure = {
        "_private.math_utility._1701": ["AcousticWeighting"],
        "_private.math_utility._1702": ["AlignmentAxis"],
        "_private.math_utility._1703": ["Axis"],
        "_private.math_utility._1704": ["CirclesOnAxis"],
        "_private.math_utility._1705": ["ComplexMatrix"],
        "_private.math_utility._1706": ["ComplexPartDisplayOption"],
        "_private.math_utility._1707": ["ComplexVector"],
        "_private.math_utility._1708": ["ComplexVector3D"],
        "_private.math_utility._1709": ["ComplexVector6D"],
        "_private.math_utility._1710": ["CoordinateSystem3D"],
        "_private.math_utility._1711": ["CoordinateSystemEditor"],
        "_private.math_utility._1712": ["CoordinateSystemForRotation"],
        "_private.math_utility._1713": ["CoordinateSystemForRotationOrigin"],
        "_private.math_utility._1714": ["DataPrecision"],
        "_private.math_utility._1715": ["DegreeOfFreedom"],
        "_private.math_utility._1716": ["DynamicsResponseScalarResult"],
        "_private.math_utility._1717": ["DynamicsResponseScaling"],
        "_private.math_utility._1718": ["EdgeNamedSelectionDetails"],
        "_private.math_utility._1719": ["Eigenmode"],
        "_private.math_utility._1720": ["Eigenmodes"],
        "_private.math_utility._1721": ["EulerParameters"],
        "_private.math_utility._1722": ["ExtrapolationOptions"],
        "_private.math_utility._1723": ["FacetedBody"],
        "_private.math_utility._1724": ["FacetedSurface"],
        "_private.math_utility._1725": ["FourierSeries"],
        "_private.math_utility._1726": ["GenericMatrix"],
        "_private.math_utility._1727": ["GriddedSurface"],
        "_private.math_utility._1728": ["HarmonicValue"],
        "_private.math_utility._1729": ["InertiaTensor"],
        "_private.math_utility._1730": ["MassProperties"],
        "_private.math_utility._1731": ["MaxMinMean"],
        "_private.math_utility._1732": ["ComplexMagnitudeMethod"],
        "_private.math_utility._1733": ["MultipleFourierSeriesInterpolator"],
        "_private.math_utility._1734": ["Named2DLocation"],
        "_private.math_utility._1735": ["NamedSelection"],
        "_private.math_utility._1736": ["NamedSelectionEdge"],
        "_private.math_utility._1737": ["NamedSelectionFace"],
        "_private.math_utility._1738": ["NamedSelections"],
        "_private.math_utility._1739": ["PIDControlUpdateMethod"],
        "_private.math_utility._1740": ["Quaternion"],
        "_private.math_utility._1741": ["RealMatrix"],
        "_private.math_utility._1742": ["RealVector"],
        "_private.math_utility._1743": ["ResultOptionsFor3DVector"],
        "_private.math_utility._1744": ["RotationAxis"],
        "_private.math_utility._1745": ["RoundedOrder"],
        "_private.math_utility._1746": ["SinCurve"],
        "_private.math_utility._1747": ["SquareMatrix"],
        "_private.math_utility._1748": ["StressPoint"],
        "_private.math_utility._1749": ["TranslationRotation"],
        "_private.math_utility._1750": ["Vector2DListAccessor"],
        "_private.math_utility._1751": ["Vector6D"],
    }

    __sys.modules[__name__] = __LazyImporter(
        "mastapy",
        globals()["__file__"],
        __import_structure,
    )

__all__ = (
    "AcousticWeighting",
    "AlignmentAxis",
    "Axis",
    "CirclesOnAxis",
    "ComplexMatrix",
    "ComplexPartDisplayOption",
    "ComplexVector",
    "ComplexVector3D",
    "ComplexVector6D",
    "CoordinateSystem3D",
    "CoordinateSystemEditor",
    "CoordinateSystemForRotation",
    "CoordinateSystemForRotationOrigin",
    "DataPrecision",
    "DegreeOfFreedom",
    "DynamicsResponseScalarResult",
    "DynamicsResponseScaling",
    "EdgeNamedSelectionDetails",
    "Eigenmode",
    "Eigenmodes",
    "EulerParameters",
    "ExtrapolationOptions",
    "FacetedBody",
    "FacetedSurface",
    "FourierSeries",
    "GenericMatrix",
    "GriddedSurface",
    "HarmonicValue",
    "InertiaTensor",
    "MassProperties",
    "MaxMinMean",
    "ComplexMagnitudeMethod",
    "MultipleFourierSeriesInterpolator",
    "Named2DLocation",
    "NamedSelection",
    "NamedSelectionEdge",
    "NamedSelectionFace",
    "NamedSelections",
    "PIDControlUpdateMethod",
    "Quaternion",
    "RealMatrix",
    "RealVector",
    "ResultOptionsFor3DVector",
    "RotationAxis",
    "RoundedOrder",
    "SinCurve",
    "SquareMatrix",
    "StressPoint",
    "TranslationRotation",
    "Vector2DListAccessor",
    "Vector6D",
)
