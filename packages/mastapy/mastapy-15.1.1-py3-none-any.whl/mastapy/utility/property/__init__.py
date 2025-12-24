"""Subpackage."""

from typing import TYPE_CHECKING as __tc

if __tc:
    from mastapy._private.utility.property._2072 import DeletableCollectionMember
    from mastapy._private.utility.property._2073 import DutyCyclePropertySummary
    from mastapy._private.utility.property._2074 import DutyCyclePropertySummaryForce
    from mastapy._private.utility.property._2075 import (
        DutyCyclePropertySummaryPercentage,
    )
    from mastapy._private.utility.property._2076 import (
        DutyCyclePropertySummarySmallAngle,
    )
    from mastapy._private.utility.property._2077 import DutyCyclePropertySummaryStress
    from mastapy._private.utility.property._2078 import (
        DutyCyclePropertySummaryVeryShortLength,
    )
    from mastapy._private.utility.property._2079 import EnumWithBoolean
    from mastapy._private.utility.property._2080 import (
        NamedRangeWithOverridableMinAndMax,
    )
    from mastapy._private.utility.property._2081 import OverridableRange
    from mastapy._private.utility.property._2082 import TypedObjectsWithOption
else:
    import sys as __sys

    from lazy_imports import LazyImporter as __LazyImporter

    __import_structure = {
        "_private.utility.property._2072": ["DeletableCollectionMember"],
        "_private.utility.property._2073": ["DutyCyclePropertySummary"],
        "_private.utility.property._2074": ["DutyCyclePropertySummaryForce"],
        "_private.utility.property._2075": ["DutyCyclePropertySummaryPercentage"],
        "_private.utility.property._2076": ["DutyCyclePropertySummarySmallAngle"],
        "_private.utility.property._2077": ["DutyCyclePropertySummaryStress"],
        "_private.utility.property._2078": ["DutyCyclePropertySummaryVeryShortLength"],
        "_private.utility.property._2079": ["EnumWithBoolean"],
        "_private.utility.property._2080": ["NamedRangeWithOverridableMinAndMax"],
        "_private.utility.property._2081": ["OverridableRange"],
        "_private.utility.property._2082": ["TypedObjectsWithOption"],
    }

    __sys.modules[__name__] = __LazyImporter(
        "mastapy",
        globals()["__file__"],
        __import_structure,
    )

__all__ = (
    "DeletableCollectionMember",
    "DutyCyclePropertySummary",
    "DutyCyclePropertySummaryForce",
    "DutyCyclePropertySummaryPercentage",
    "DutyCyclePropertySummarySmallAngle",
    "DutyCyclePropertySummaryStress",
    "DutyCyclePropertySummaryVeryShortLength",
    "EnumWithBoolean",
    "NamedRangeWithOverridableMinAndMax",
    "OverridableRange",
    "TypedObjectsWithOption",
)
