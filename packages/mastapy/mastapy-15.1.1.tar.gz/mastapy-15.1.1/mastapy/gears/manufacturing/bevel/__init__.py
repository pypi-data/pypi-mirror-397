"""Subpackage."""

from typing import TYPE_CHECKING as __tc

if __tc:
    from mastapy._private.gears.manufacturing.bevel._898 import AbstractTCA
    from mastapy._private.gears.manufacturing.bevel._899 import (
        BevelMachineSettingOptimizationResult,
    )
    from mastapy._private.gears.manufacturing.bevel._900 import (
        ConicalFlankDeviationsData,
    )
    from mastapy._private.gears.manufacturing.bevel._901 import (
        ConicalGearManufacturingAnalysis,
    )
    from mastapy._private.gears.manufacturing.bevel._902 import (
        ConicalGearManufacturingConfig,
    )
    from mastapy._private.gears.manufacturing.bevel._903 import (
        ConicalGearMicroGeometryConfig,
    )
    from mastapy._private.gears.manufacturing.bevel._904 import (
        ConicalGearMicroGeometryConfigBase,
    )
    from mastapy._private.gears.manufacturing.bevel._905 import (
        ConicalMeshedGearManufacturingAnalysis,
    )
    from mastapy._private.gears.manufacturing.bevel._906 import (
        ConicalMeshedWheelFlankManufacturingConfig,
    )
    from mastapy._private.gears.manufacturing.bevel._907 import (
        ConicalMeshFlankManufacturingConfig,
    )
    from mastapy._private.gears.manufacturing.bevel._908 import (
        ConicalMeshFlankMicroGeometryConfig,
    )
    from mastapy._private.gears.manufacturing.bevel._909 import (
        ConicalMeshFlankNURBSMicroGeometryConfig,
    )
    from mastapy._private.gears.manufacturing.bevel._910 import (
        ConicalMeshManufacturingAnalysis,
    )
    from mastapy._private.gears.manufacturing.bevel._911 import (
        ConicalMeshManufacturingConfig,
    )
    from mastapy._private.gears.manufacturing.bevel._912 import (
        ConicalMeshMicroGeometryConfig,
    )
    from mastapy._private.gears.manufacturing.bevel._913 import (
        ConicalMeshMicroGeometryConfigBase,
    )
    from mastapy._private.gears.manufacturing.bevel._914 import (
        ConicalPinionManufacturingConfig,
    )
    from mastapy._private.gears.manufacturing.bevel._915 import (
        ConicalPinionMicroGeometryConfig,
    )
    from mastapy._private.gears.manufacturing.bevel._916 import (
        ConicalSetManufacturingAnalysis,
    )
    from mastapy._private.gears.manufacturing.bevel._917 import (
        ConicalSetManufacturingConfig,
    )
    from mastapy._private.gears.manufacturing.bevel._918 import (
        ConicalSetMicroGeometryConfig,
    )
    from mastapy._private.gears.manufacturing.bevel._919 import (
        ConicalSetMicroGeometryConfigBase,
    )
    from mastapy._private.gears.manufacturing.bevel._920 import (
        ConicalWheelManufacturingConfig,
    )
    from mastapy._private.gears.manufacturing.bevel._921 import EaseOffBasedTCA
    from mastapy._private.gears.manufacturing.bevel._922 import FlankMeasurementBorder
    from mastapy._private.gears.manufacturing.bevel._923 import HypoidAdvancedLibrary
    from mastapy._private.gears.manufacturing.bevel._924 import MachineTypes
    from mastapy._private.gears.manufacturing.bevel._925 import ManufacturingMachine
    from mastapy._private.gears.manufacturing.bevel._926 import (
        ManufacturingMachineDatabase,
    )
    from mastapy._private.gears.manufacturing.bevel._927 import (
        PinionBevelGeneratingModifiedRollMachineSettings,
    )
    from mastapy._private.gears.manufacturing.bevel._928 import (
        PinionBevelGeneratingTiltMachineSettings,
    )
    from mastapy._private.gears.manufacturing.bevel._929 import PinionConcave
    from mastapy._private.gears.manufacturing.bevel._930 import (
        PinionConicalMachineSettingsSpecified,
    )
    from mastapy._private.gears.manufacturing.bevel._931 import PinionConvex
    from mastapy._private.gears.manufacturing.bevel._932 import (
        PinionFinishMachineSettings,
    )
    from mastapy._private.gears.manufacturing.bevel._933 import (
        PinionHypoidFormateTiltMachineSettings,
    )
    from mastapy._private.gears.manufacturing.bevel._934 import (
        PinionHypoidGeneratingTiltMachineSettings,
    )
    from mastapy._private.gears.manufacturing.bevel._935 import PinionMachineSettingsSMT
    from mastapy._private.gears.manufacturing.bevel._936 import (
        PinionRoughMachineSetting,
    )
    from mastapy._private.gears.manufacturing.bevel._937 import Wheel
    from mastapy._private.gears.manufacturing.bevel._938 import WheelFormatMachineTypes
else:
    import sys as __sys

    from lazy_imports import LazyImporter as __LazyImporter

    __import_structure = {
        "_private.gears.manufacturing.bevel._898": ["AbstractTCA"],
        "_private.gears.manufacturing.bevel._899": [
            "BevelMachineSettingOptimizationResult"
        ],
        "_private.gears.manufacturing.bevel._900": ["ConicalFlankDeviationsData"],
        "_private.gears.manufacturing.bevel._901": ["ConicalGearManufacturingAnalysis"],
        "_private.gears.manufacturing.bevel._902": ["ConicalGearManufacturingConfig"],
        "_private.gears.manufacturing.bevel._903": ["ConicalGearMicroGeometryConfig"],
        "_private.gears.manufacturing.bevel._904": [
            "ConicalGearMicroGeometryConfigBase"
        ],
        "_private.gears.manufacturing.bevel._905": [
            "ConicalMeshedGearManufacturingAnalysis"
        ],
        "_private.gears.manufacturing.bevel._906": [
            "ConicalMeshedWheelFlankManufacturingConfig"
        ],
        "_private.gears.manufacturing.bevel._907": [
            "ConicalMeshFlankManufacturingConfig"
        ],
        "_private.gears.manufacturing.bevel._908": [
            "ConicalMeshFlankMicroGeometryConfig"
        ],
        "_private.gears.manufacturing.bevel._909": [
            "ConicalMeshFlankNURBSMicroGeometryConfig"
        ],
        "_private.gears.manufacturing.bevel._910": ["ConicalMeshManufacturingAnalysis"],
        "_private.gears.manufacturing.bevel._911": ["ConicalMeshManufacturingConfig"],
        "_private.gears.manufacturing.bevel._912": ["ConicalMeshMicroGeometryConfig"],
        "_private.gears.manufacturing.bevel._913": [
            "ConicalMeshMicroGeometryConfigBase"
        ],
        "_private.gears.manufacturing.bevel._914": ["ConicalPinionManufacturingConfig"],
        "_private.gears.manufacturing.bevel._915": ["ConicalPinionMicroGeometryConfig"],
        "_private.gears.manufacturing.bevel._916": ["ConicalSetManufacturingAnalysis"],
        "_private.gears.manufacturing.bevel._917": ["ConicalSetManufacturingConfig"],
        "_private.gears.manufacturing.bevel._918": ["ConicalSetMicroGeometryConfig"],
        "_private.gears.manufacturing.bevel._919": [
            "ConicalSetMicroGeometryConfigBase"
        ],
        "_private.gears.manufacturing.bevel._920": ["ConicalWheelManufacturingConfig"],
        "_private.gears.manufacturing.bevel._921": ["EaseOffBasedTCA"],
        "_private.gears.manufacturing.bevel._922": ["FlankMeasurementBorder"],
        "_private.gears.manufacturing.bevel._923": ["HypoidAdvancedLibrary"],
        "_private.gears.manufacturing.bevel._924": ["MachineTypes"],
        "_private.gears.manufacturing.bevel._925": ["ManufacturingMachine"],
        "_private.gears.manufacturing.bevel._926": ["ManufacturingMachineDatabase"],
        "_private.gears.manufacturing.bevel._927": [
            "PinionBevelGeneratingModifiedRollMachineSettings"
        ],
        "_private.gears.manufacturing.bevel._928": [
            "PinionBevelGeneratingTiltMachineSettings"
        ],
        "_private.gears.manufacturing.bevel._929": ["PinionConcave"],
        "_private.gears.manufacturing.bevel._930": [
            "PinionConicalMachineSettingsSpecified"
        ],
        "_private.gears.manufacturing.bevel._931": ["PinionConvex"],
        "_private.gears.manufacturing.bevel._932": ["PinionFinishMachineSettings"],
        "_private.gears.manufacturing.bevel._933": [
            "PinionHypoidFormateTiltMachineSettings"
        ],
        "_private.gears.manufacturing.bevel._934": [
            "PinionHypoidGeneratingTiltMachineSettings"
        ],
        "_private.gears.manufacturing.bevel._935": ["PinionMachineSettingsSMT"],
        "_private.gears.manufacturing.bevel._936": ["PinionRoughMachineSetting"],
        "_private.gears.manufacturing.bevel._937": ["Wheel"],
        "_private.gears.manufacturing.bevel._938": ["WheelFormatMachineTypes"],
    }

    __sys.modules[__name__] = __LazyImporter(
        "mastapy",
        globals()["__file__"],
        __import_structure,
    )

__all__ = (
    "AbstractTCA",
    "BevelMachineSettingOptimizationResult",
    "ConicalFlankDeviationsData",
    "ConicalGearManufacturingAnalysis",
    "ConicalGearManufacturingConfig",
    "ConicalGearMicroGeometryConfig",
    "ConicalGearMicroGeometryConfigBase",
    "ConicalMeshedGearManufacturingAnalysis",
    "ConicalMeshedWheelFlankManufacturingConfig",
    "ConicalMeshFlankManufacturingConfig",
    "ConicalMeshFlankMicroGeometryConfig",
    "ConicalMeshFlankNURBSMicroGeometryConfig",
    "ConicalMeshManufacturingAnalysis",
    "ConicalMeshManufacturingConfig",
    "ConicalMeshMicroGeometryConfig",
    "ConicalMeshMicroGeometryConfigBase",
    "ConicalPinionManufacturingConfig",
    "ConicalPinionMicroGeometryConfig",
    "ConicalSetManufacturingAnalysis",
    "ConicalSetManufacturingConfig",
    "ConicalSetMicroGeometryConfig",
    "ConicalSetMicroGeometryConfigBase",
    "ConicalWheelManufacturingConfig",
    "EaseOffBasedTCA",
    "FlankMeasurementBorder",
    "HypoidAdvancedLibrary",
    "MachineTypes",
    "ManufacturingMachine",
    "ManufacturingMachineDatabase",
    "PinionBevelGeneratingModifiedRollMachineSettings",
    "PinionBevelGeneratingTiltMachineSettings",
    "PinionConcave",
    "PinionConicalMachineSettingsSpecified",
    "PinionConvex",
    "PinionFinishMachineSettings",
    "PinionHypoidFormateTiltMachineSettings",
    "PinionHypoidGeneratingTiltMachineSettings",
    "PinionMachineSettingsSMT",
    "PinionRoughMachineSetting",
    "Wheel",
    "WheelFormatMachineTypes",
)
