"""Subpackage."""

from typing import TYPE_CHECKING as __tc

if __tc:
    from mastapy._private.gears.ltca.conical._988 import ConicalGearBendingStiffness
    from mastapy._private.gears.ltca.conical._989 import ConicalGearBendingStiffnessNode
    from mastapy._private.gears.ltca.conical._990 import ConicalGearContactStiffness
    from mastapy._private.gears.ltca.conical._991 import ConicalGearContactStiffnessNode
    from mastapy._private.gears.ltca.conical._992 import (
        ConicalGearLoadDistributionAnalysis,
    )
    from mastapy._private.gears.ltca.conical._993 import (
        ConicalGearSetLoadDistributionAnalysis,
    )
    from mastapy._private.gears.ltca.conical._994 import (
        ConicalMeshedGearLoadDistributionAnalysis,
    )
    from mastapy._private.gears.ltca.conical._995 import (
        ConicalMeshLoadDistributionAnalysis,
    )
    from mastapy._private.gears.ltca.conical._996 import (
        ConicalMeshLoadDistributionAtRotation,
    )
    from mastapy._private.gears.ltca.conical._997 import ConicalMeshLoadedContactLine
else:
    import sys as __sys

    from lazy_imports import LazyImporter as __LazyImporter

    __import_structure = {
        "_private.gears.ltca.conical._988": ["ConicalGearBendingStiffness"],
        "_private.gears.ltca.conical._989": ["ConicalGearBendingStiffnessNode"],
        "_private.gears.ltca.conical._990": ["ConicalGearContactStiffness"],
        "_private.gears.ltca.conical._991": ["ConicalGearContactStiffnessNode"],
        "_private.gears.ltca.conical._992": ["ConicalGearLoadDistributionAnalysis"],
        "_private.gears.ltca.conical._993": ["ConicalGearSetLoadDistributionAnalysis"],
        "_private.gears.ltca.conical._994": [
            "ConicalMeshedGearLoadDistributionAnalysis"
        ],
        "_private.gears.ltca.conical._995": ["ConicalMeshLoadDistributionAnalysis"],
        "_private.gears.ltca.conical._996": ["ConicalMeshLoadDistributionAtRotation"],
        "_private.gears.ltca.conical._997": ["ConicalMeshLoadedContactLine"],
    }

    __sys.modules[__name__] = __LazyImporter(
        "mastapy",
        globals()["__file__"],
        __import_structure,
    )

__all__ = (
    "ConicalGearBendingStiffness",
    "ConicalGearBendingStiffnessNode",
    "ConicalGearContactStiffness",
    "ConicalGearContactStiffnessNode",
    "ConicalGearLoadDistributionAnalysis",
    "ConicalGearSetLoadDistributionAnalysis",
    "ConicalMeshedGearLoadDistributionAnalysis",
    "ConicalMeshLoadDistributionAnalysis",
    "ConicalMeshLoadDistributionAtRotation",
    "ConicalMeshLoadedContactLine",
)
