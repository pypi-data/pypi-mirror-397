"""Subpackage."""

from typing import TYPE_CHECKING as __tc

if __tc:
    from mastapy._private.gears.ltca._951 import ConicalGearFilletStressResults
    from mastapy._private.gears.ltca._952 import ConicalGearRootFilletStressResults
    from mastapy._private.gears.ltca._953 import ContactResultType
    from mastapy._private.gears.ltca._954 import CylindricalGearFilletNodeStressResults
    from mastapy._private.gears.ltca._955 import (
        CylindricalGearFilletNodeStressResultsColumn,
    )
    from mastapy._private.gears.ltca._956 import (
        CylindricalGearFilletNodeStressResultsRow,
    )
    from mastapy._private.gears.ltca._957 import CylindricalGearRootFilletStressResults
    from mastapy._private.gears.ltca._958 import (
        CylindricalMeshedGearLoadDistributionAnalysis,
    )
    from mastapy._private.gears.ltca._959 import GearBendingStiffness
    from mastapy._private.gears.ltca._960 import GearBendingStiffnessNode
    from mastapy._private.gears.ltca._961 import GearContactStiffness
    from mastapy._private.gears.ltca._962 import GearContactStiffnessNode
    from mastapy._private.gears.ltca._963 import GearFilletNodeStressResults
    from mastapy._private.gears.ltca._964 import GearFilletNodeStressResultsColumn
    from mastapy._private.gears.ltca._965 import GearFilletNodeStressResultsRow
    from mastapy._private.gears.ltca._966 import GearLoadDistributionAnalysis
    from mastapy._private.gears.ltca._967 import GearMeshLoadDistributionAnalysis
    from mastapy._private.gears.ltca._968 import GearMeshLoadDistributionAtRotation
    from mastapy._private.gears.ltca._969 import GearMeshLoadedContactLine
    from mastapy._private.gears.ltca._970 import GearMeshLoadedContactPoint
    from mastapy._private.gears.ltca._971 import GearRootFilletStressResults
    from mastapy._private.gears.ltca._972 import GearSetLoadDistributionAnalysis
    from mastapy._private.gears.ltca._973 import GearStiffness
    from mastapy._private.gears.ltca._974 import GearStiffnessNode
    from mastapy._private.gears.ltca._975 import (
        MeshedGearLoadDistributionAnalysisAtRotation,
    )
    from mastapy._private.gears.ltca._976 import UseAdvancedLTCAOptions
else:
    import sys as __sys

    from lazy_imports import LazyImporter as __LazyImporter

    __import_structure = {
        "_private.gears.ltca._951": ["ConicalGearFilletStressResults"],
        "_private.gears.ltca._952": ["ConicalGearRootFilletStressResults"],
        "_private.gears.ltca._953": ["ContactResultType"],
        "_private.gears.ltca._954": ["CylindricalGearFilletNodeStressResults"],
        "_private.gears.ltca._955": ["CylindricalGearFilletNodeStressResultsColumn"],
        "_private.gears.ltca._956": ["CylindricalGearFilletNodeStressResultsRow"],
        "_private.gears.ltca._957": ["CylindricalGearRootFilletStressResults"],
        "_private.gears.ltca._958": ["CylindricalMeshedGearLoadDistributionAnalysis"],
        "_private.gears.ltca._959": ["GearBendingStiffness"],
        "_private.gears.ltca._960": ["GearBendingStiffnessNode"],
        "_private.gears.ltca._961": ["GearContactStiffness"],
        "_private.gears.ltca._962": ["GearContactStiffnessNode"],
        "_private.gears.ltca._963": ["GearFilletNodeStressResults"],
        "_private.gears.ltca._964": ["GearFilletNodeStressResultsColumn"],
        "_private.gears.ltca._965": ["GearFilletNodeStressResultsRow"],
        "_private.gears.ltca._966": ["GearLoadDistributionAnalysis"],
        "_private.gears.ltca._967": ["GearMeshLoadDistributionAnalysis"],
        "_private.gears.ltca._968": ["GearMeshLoadDistributionAtRotation"],
        "_private.gears.ltca._969": ["GearMeshLoadedContactLine"],
        "_private.gears.ltca._970": ["GearMeshLoadedContactPoint"],
        "_private.gears.ltca._971": ["GearRootFilletStressResults"],
        "_private.gears.ltca._972": ["GearSetLoadDistributionAnalysis"],
        "_private.gears.ltca._973": ["GearStiffness"],
        "_private.gears.ltca._974": ["GearStiffnessNode"],
        "_private.gears.ltca._975": ["MeshedGearLoadDistributionAnalysisAtRotation"],
        "_private.gears.ltca._976": ["UseAdvancedLTCAOptions"],
    }

    __sys.modules[__name__] = __LazyImporter(
        "mastapy",
        globals()["__file__"],
        __import_structure,
    )

__all__ = (
    "ConicalGearFilletStressResults",
    "ConicalGearRootFilletStressResults",
    "ContactResultType",
    "CylindricalGearFilletNodeStressResults",
    "CylindricalGearFilletNodeStressResultsColumn",
    "CylindricalGearFilletNodeStressResultsRow",
    "CylindricalGearRootFilletStressResults",
    "CylindricalMeshedGearLoadDistributionAnalysis",
    "GearBendingStiffness",
    "GearBendingStiffnessNode",
    "GearContactStiffness",
    "GearContactStiffnessNode",
    "GearFilletNodeStressResults",
    "GearFilletNodeStressResultsColumn",
    "GearFilletNodeStressResultsRow",
    "GearLoadDistributionAnalysis",
    "GearMeshLoadDistributionAnalysis",
    "GearMeshLoadDistributionAtRotation",
    "GearMeshLoadedContactLine",
    "GearMeshLoadedContactPoint",
    "GearRootFilletStressResults",
    "GearSetLoadDistributionAnalysis",
    "GearStiffness",
    "GearStiffnessNode",
    "MeshedGearLoadDistributionAnalysisAtRotation",
    "UseAdvancedLTCAOptions",
)
