"""Subpackage."""

from typing import TYPE_CHECKING as __tc

if __tc:
    from mastapy._private.bearings.tolerances._2138 import BearingConnectionComponent
    from mastapy._private.bearings.tolerances._2139 import InternalClearanceClass
    from mastapy._private.bearings.tolerances._2140 import BearingToleranceClass
    from mastapy._private.bearings.tolerances._2141 import (
        BearingToleranceDefinitionOptions,
    )
    from mastapy._private.bearings.tolerances._2142 import FitType
    from mastapy._private.bearings.tolerances._2143 import InnerRingTolerance
    from mastapy._private.bearings.tolerances._2144 import InnerSupportTolerance
    from mastapy._private.bearings.tolerances._2145 import InterferenceDetail
    from mastapy._private.bearings.tolerances._2146 import InterferenceTolerance
    from mastapy._private.bearings.tolerances._2147 import ITDesignation
    from mastapy._private.bearings.tolerances._2148 import MountingSleeveDiameterDetail
    from mastapy._private.bearings.tolerances._2149 import OuterRingTolerance
    from mastapy._private.bearings.tolerances._2150 import OuterSupportTolerance
    from mastapy._private.bearings.tolerances._2151 import RaceRoundnessAtAngle
    from mastapy._private.bearings.tolerances._2152 import RadialSpecificationMethod
    from mastapy._private.bearings.tolerances._2153 import RingDetail
    from mastapy._private.bearings.tolerances._2154 import RingTolerance
    from mastapy._private.bearings.tolerances._2155 import RoundnessSpecification
    from mastapy._private.bearings.tolerances._2156 import RoundnessSpecificationType
    from mastapy._private.bearings.tolerances._2157 import SupportDetail
    from mastapy._private.bearings.tolerances._2158 import SupportMaterialSource
    from mastapy._private.bearings.tolerances._2159 import SupportTolerance
    from mastapy._private.bearings.tolerances._2160 import (
        SupportToleranceLocationDesignation,
    )
    from mastapy._private.bearings.tolerances._2161 import ToleranceCombination
    from mastapy._private.bearings.tolerances._2162 import TypeOfFit
else:
    import sys as __sys

    from lazy_imports import LazyImporter as __LazyImporter

    __import_structure = {
        "_private.bearings.tolerances._2138": ["BearingConnectionComponent"],
        "_private.bearings.tolerances._2139": ["InternalClearanceClass"],
        "_private.bearings.tolerances._2140": ["BearingToleranceClass"],
        "_private.bearings.tolerances._2141": ["BearingToleranceDefinitionOptions"],
        "_private.bearings.tolerances._2142": ["FitType"],
        "_private.bearings.tolerances._2143": ["InnerRingTolerance"],
        "_private.bearings.tolerances._2144": ["InnerSupportTolerance"],
        "_private.bearings.tolerances._2145": ["InterferenceDetail"],
        "_private.bearings.tolerances._2146": ["InterferenceTolerance"],
        "_private.bearings.tolerances._2147": ["ITDesignation"],
        "_private.bearings.tolerances._2148": ["MountingSleeveDiameterDetail"],
        "_private.bearings.tolerances._2149": ["OuterRingTolerance"],
        "_private.bearings.tolerances._2150": ["OuterSupportTolerance"],
        "_private.bearings.tolerances._2151": ["RaceRoundnessAtAngle"],
        "_private.bearings.tolerances._2152": ["RadialSpecificationMethod"],
        "_private.bearings.tolerances._2153": ["RingDetail"],
        "_private.bearings.tolerances._2154": ["RingTolerance"],
        "_private.bearings.tolerances._2155": ["RoundnessSpecification"],
        "_private.bearings.tolerances._2156": ["RoundnessSpecificationType"],
        "_private.bearings.tolerances._2157": ["SupportDetail"],
        "_private.bearings.tolerances._2158": ["SupportMaterialSource"],
        "_private.bearings.tolerances._2159": ["SupportTolerance"],
        "_private.bearings.tolerances._2160": ["SupportToleranceLocationDesignation"],
        "_private.bearings.tolerances._2161": ["ToleranceCombination"],
        "_private.bearings.tolerances._2162": ["TypeOfFit"],
    }

    __sys.modules[__name__] = __LazyImporter(
        "mastapy",
        globals()["__file__"],
        __import_structure,
    )

__all__ = (
    "BearingConnectionComponent",
    "InternalClearanceClass",
    "BearingToleranceClass",
    "BearingToleranceDefinitionOptions",
    "FitType",
    "InnerRingTolerance",
    "InnerSupportTolerance",
    "InterferenceDetail",
    "InterferenceTolerance",
    "ITDesignation",
    "MountingSleeveDiameterDetail",
    "OuterRingTolerance",
    "OuterSupportTolerance",
    "RaceRoundnessAtAngle",
    "RadialSpecificationMethod",
    "RingDetail",
    "RingTolerance",
    "RoundnessSpecification",
    "RoundnessSpecificationType",
    "SupportDetail",
    "SupportMaterialSource",
    "SupportTolerance",
    "SupportToleranceLocationDesignation",
    "ToleranceCombination",
    "TypeOfFit",
)
