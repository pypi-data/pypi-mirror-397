"""Subpackage."""

from typing import TYPE_CHECKING as __tc

if __tc:
    from mastapy._private.system_model._2448 import Design
    from mastapy._private.system_model._2449 import ComponentDampingOption
    from mastapy._private.system_model._2450 import (
        ConceptCouplingSpeedRatioSpecificationMethod,
    )
    from mastapy._private.system_model._2451 import DesignEntity
    from mastapy._private.system_model._2452 import DesignEntityId
    from mastapy._private.system_model._2453 import DesignSettings
    from mastapy._private.system_model._2454 import DutyCycleImporter
    from mastapy._private.system_model._2455 import DutyCycleImporterDesignEntityMatch
    from mastapy._private.system_model._2456 import ExternalFullFELoader
    from mastapy._private.system_model._2457 import HypoidWindUpRemovalMethod
    from mastapy._private.system_model._2458 import IncludeDutyCycleOption
    from mastapy._private.system_model._2459 import MAAElectricMachineGroup
    from mastapy._private.system_model._2460 import MASTASettings
    from mastapy._private.system_model._2461 import MemorySummary
    from mastapy._private.system_model._2462 import MeshStiffnessModel
    from mastapy._private.system_model._2463 import (
        PlanetPinManufacturingErrorsCoordinateSystem,
    )
    from mastapy._private.system_model._2464 import (
        PowerLoadDragTorqueSpecificationMethod,
    )
    from mastapy._private.system_model._2465 import PowerLoadForInjectionLossScripts
    from mastapy._private.system_model._2466 import (
        PowerLoadInputTorqueSpecificationMethod,
    )
    from mastapy._private.system_model._2467 import PowerLoadPIDControlSpeedInputType
    from mastapy._private.system_model._2468 import PowerLoadType
    from mastapy._private.system_model._2469 import RelativeComponentAlignment
    from mastapy._private.system_model._2470 import RelativeOffsetOption
    from mastapy._private.system_model._2471 import SystemReporting
    from mastapy._private.system_model._2472 import (
        ThermalExpansionOptionForGroundedNodes,
    )
    from mastapy._private.system_model._2473 import TransmissionTemperatureSet
else:
    import sys as __sys

    from lazy_imports import LazyImporter as __LazyImporter

    __import_structure = {
        "_private.system_model._2448": ["Design"],
        "_private.system_model._2449": ["ComponentDampingOption"],
        "_private.system_model._2450": ["ConceptCouplingSpeedRatioSpecificationMethod"],
        "_private.system_model._2451": ["DesignEntity"],
        "_private.system_model._2452": ["DesignEntityId"],
        "_private.system_model._2453": ["DesignSettings"],
        "_private.system_model._2454": ["DutyCycleImporter"],
        "_private.system_model._2455": ["DutyCycleImporterDesignEntityMatch"],
        "_private.system_model._2456": ["ExternalFullFELoader"],
        "_private.system_model._2457": ["HypoidWindUpRemovalMethod"],
        "_private.system_model._2458": ["IncludeDutyCycleOption"],
        "_private.system_model._2459": ["MAAElectricMachineGroup"],
        "_private.system_model._2460": ["MASTASettings"],
        "_private.system_model._2461": ["MemorySummary"],
        "_private.system_model._2462": ["MeshStiffnessModel"],
        "_private.system_model._2463": ["PlanetPinManufacturingErrorsCoordinateSystem"],
        "_private.system_model._2464": ["PowerLoadDragTorqueSpecificationMethod"],
        "_private.system_model._2465": ["PowerLoadForInjectionLossScripts"],
        "_private.system_model._2466": ["PowerLoadInputTorqueSpecificationMethod"],
        "_private.system_model._2467": ["PowerLoadPIDControlSpeedInputType"],
        "_private.system_model._2468": ["PowerLoadType"],
        "_private.system_model._2469": ["RelativeComponentAlignment"],
        "_private.system_model._2470": ["RelativeOffsetOption"],
        "_private.system_model._2471": ["SystemReporting"],
        "_private.system_model._2472": ["ThermalExpansionOptionForGroundedNodes"],
        "_private.system_model._2473": ["TransmissionTemperatureSet"],
    }

    __sys.modules[__name__] = __LazyImporter(
        "mastapy",
        globals()["__file__"],
        __import_structure,
    )

__all__ = (
    "Design",
    "ComponentDampingOption",
    "ConceptCouplingSpeedRatioSpecificationMethod",
    "DesignEntity",
    "DesignEntityId",
    "DesignSettings",
    "DutyCycleImporter",
    "DutyCycleImporterDesignEntityMatch",
    "ExternalFullFELoader",
    "HypoidWindUpRemovalMethod",
    "IncludeDutyCycleOption",
    "MAAElectricMachineGroup",
    "MASTASettings",
    "MemorySummary",
    "MeshStiffnessModel",
    "PlanetPinManufacturingErrorsCoordinateSystem",
    "PowerLoadDragTorqueSpecificationMethod",
    "PowerLoadForInjectionLossScripts",
    "PowerLoadInputTorqueSpecificationMethod",
    "PowerLoadPIDControlSpeedInputType",
    "PowerLoadType",
    "RelativeComponentAlignment",
    "RelativeOffsetOption",
    "SystemReporting",
    "ThermalExpansionOptionForGroundedNodes",
    "TransmissionTemperatureSet",
)
