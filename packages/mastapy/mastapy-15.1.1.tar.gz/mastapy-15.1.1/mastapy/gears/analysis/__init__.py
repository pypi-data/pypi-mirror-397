"""Subpackage."""

from typing import TYPE_CHECKING as __tc

if __tc:
    from mastapy._private.gears.analysis._1361 import AbstractGearAnalysis
    from mastapy._private.gears.analysis._1362 import AbstractGearMeshAnalysis
    from mastapy._private.gears.analysis._1363 import AbstractGearSetAnalysis
    from mastapy._private.gears.analysis._1364 import GearDesignAnalysis
    from mastapy._private.gears.analysis._1365 import GearImplementationAnalysis
    from mastapy._private.gears.analysis._1366 import (
        GearImplementationAnalysisDutyCycle,
    )
    from mastapy._private.gears.analysis._1367 import GearImplementationDetail
    from mastapy._private.gears.analysis._1368 import GearMeshDesignAnalysis
    from mastapy._private.gears.analysis._1369 import GearMeshImplementationAnalysis
    from mastapy._private.gears.analysis._1370 import (
        GearMeshImplementationAnalysisDutyCycle,
    )
    from mastapy._private.gears.analysis._1371 import GearMeshImplementationDetail
    from mastapy._private.gears.analysis._1372 import GearSetDesignAnalysis
    from mastapy._private.gears.analysis._1373 import GearSetGroupDutyCycle
    from mastapy._private.gears.analysis._1374 import GearSetImplementationAnalysis
    from mastapy._private.gears.analysis._1375 import (
        GearSetImplementationAnalysisAbstract,
    )
    from mastapy._private.gears.analysis._1376 import (
        GearSetImplementationAnalysisDutyCycle,
    )
    from mastapy._private.gears.analysis._1377 import GearSetImplementationDetail
else:
    import sys as __sys

    from lazy_imports import LazyImporter as __LazyImporter

    __import_structure = {
        "_private.gears.analysis._1361": ["AbstractGearAnalysis"],
        "_private.gears.analysis._1362": ["AbstractGearMeshAnalysis"],
        "_private.gears.analysis._1363": ["AbstractGearSetAnalysis"],
        "_private.gears.analysis._1364": ["GearDesignAnalysis"],
        "_private.gears.analysis._1365": ["GearImplementationAnalysis"],
        "_private.gears.analysis._1366": ["GearImplementationAnalysisDutyCycle"],
        "_private.gears.analysis._1367": ["GearImplementationDetail"],
        "_private.gears.analysis._1368": ["GearMeshDesignAnalysis"],
        "_private.gears.analysis._1369": ["GearMeshImplementationAnalysis"],
        "_private.gears.analysis._1370": ["GearMeshImplementationAnalysisDutyCycle"],
        "_private.gears.analysis._1371": ["GearMeshImplementationDetail"],
        "_private.gears.analysis._1372": ["GearSetDesignAnalysis"],
        "_private.gears.analysis._1373": ["GearSetGroupDutyCycle"],
        "_private.gears.analysis._1374": ["GearSetImplementationAnalysis"],
        "_private.gears.analysis._1375": ["GearSetImplementationAnalysisAbstract"],
        "_private.gears.analysis._1376": ["GearSetImplementationAnalysisDutyCycle"],
        "_private.gears.analysis._1377": ["GearSetImplementationDetail"],
    }

    __sys.modules[__name__] = __LazyImporter(
        "mastapy",
        globals()["__file__"],
        __import_structure,
    )

__all__ = (
    "AbstractGearAnalysis",
    "AbstractGearMeshAnalysis",
    "AbstractGearSetAnalysis",
    "GearDesignAnalysis",
    "GearImplementationAnalysis",
    "GearImplementationAnalysisDutyCycle",
    "GearImplementationDetail",
    "GearMeshDesignAnalysis",
    "GearMeshImplementationAnalysis",
    "GearMeshImplementationAnalysisDutyCycle",
    "GearMeshImplementationDetail",
    "GearSetDesignAnalysis",
    "GearSetGroupDutyCycle",
    "GearSetImplementationAnalysis",
    "GearSetImplementationAnalysisAbstract",
    "GearSetImplementationAnalysisDutyCycle",
    "GearSetImplementationDetail",
)
