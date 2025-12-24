"""Subpackage."""

from typing import TYPE_CHECKING as __tc

if __tc:
    from mastapy._private.gears.ltca.cylindrical._977 import (
        CylindricalGearBendingStiffness,
    )
    from mastapy._private.gears.ltca.cylindrical._978 import (
        CylindricalGearBendingStiffnessNode,
    )
    from mastapy._private.gears.ltca.cylindrical._979 import (
        CylindricalGearContactStiffness,
    )
    from mastapy._private.gears.ltca.cylindrical._980 import (
        CylindricalGearContactStiffnessNode,
    )
    from mastapy._private.gears.ltca.cylindrical._981 import (
        CylindricalGearLoadDistributionAnalysis,
    )
    from mastapy._private.gears.ltca.cylindrical._982 import (
        CylindricalGearMeshLoadDistributionAnalysis,
    )
    from mastapy._private.gears.ltca.cylindrical._983 import (
        CylindricalGearMeshLoadedContactLine,
    )
    from mastapy._private.gears.ltca.cylindrical._984 import (
        CylindricalGearMeshLoadedContactPoint,
    )
    from mastapy._private.gears.ltca.cylindrical._985 import (
        CylindricalGearSetLoadDistributionAnalysis,
    )
    from mastapy._private.gears.ltca.cylindrical._986 import (
        CylindricalMeshLoadDistributionAtRotation,
    )
    from mastapy._private.gears.ltca.cylindrical._987 import (
        FaceGearSetLoadDistributionAnalysis,
    )
else:
    import sys as __sys

    from lazy_imports import LazyImporter as __LazyImporter

    __import_structure = {
        "_private.gears.ltca.cylindrical._977": ["CylindricalGearBendingStiffness"],
        "_private.gears.ltca.cylindrical._978": ["CylindricalGearBendingStiffnessNode"],
        "_private.gears.ltca.cylindrical._979": ["CylindricalGearContactStiffness"],
        "_private.gears.ltca.cylindrical._980": ["CylindricalGearContactStiffnessNode"],
        "_private.gears.ltca.cylindrical._981": [
            "CylindricalGearLoadDistributionAnalysis"
        ],
        "_private.gears.ltca.cylindrical._982": [
            "CylindricalGearMeshLoadDistributionAnalysis"
        ],
        "_private.gears.ltca.cylindrical._983": [
            "CylindricalGearMeshLoadedContactLine"
        ],
        "_private.gears.ltca.cylindrical._984": [
            "CylindricalGearMeshLoadedContactPoint"
        ],
        "_private.gears.ltca.cylindrical._985": [
            "CylindricalGearSetLoadDistributionAnalysis"
        ],
        "_private.gears.ltca.cylindrical._986": [
            "CylindricalMeshLoadDistributionAtRotation"
        ],
        "_private.gears.ltca.cylindrical._987": ["FaceGearSetLoadDistributionAnalysis"],
    }

    __sys.modules[__name__] = __LazyImporter(
        "mastapy",
        globals()["__file__"],
        __import_structure,
    )

__all__ = (
    "CylindricalGearBendingStiffness",
    "CylindricalGearBendingStiffnessNode",
    "CylindricalGearContactStiffness",
    "CylindricalGearContactStiffnessNode",
    "CylindricalGearLoadDistributionAnalysis",
    "CylindricalGearMeshLoadDistributionAnalysis",
    "CylindricalGearMeshLoadedContactLine",
    "CylindricalGearMeshLoadedContactPoint",
    "CylindricalGearSetLoadDistributionAnalysis",
    "CylindricalMeshLoadDistributionAtRotation",
    "FaceGearSetLoadDistributionAnalysis",
)
