"""Subpackage."""

from typing import TYPE_CHECKING as __tc

if __tc:
    from mastapy._private.electric_machines.load_cases_and_analyses._1557 import (
        BasicDynamicForceLoadCase,
    )
    from mastapy._private.electric_machines.load_cases_and_analyses._1558 import (
        DynamicForceAnalysis,
    )
    from mastapy._private.electric_machines.load_cases_and_analyses._1559 import (
        DynamicForceLoadCase,
    )
    from mastapy._private.electric_machines.load_cases_and_analyses._1560 import (
        DynamicForcesOperatingPoint,
    )
    from mastapy._private.electric_machines.load_cases_and_analyses._1561 import (
        EfficiencyMapAnalysis,
    )
    from mastapy._private.electric_machines.load_cases_and_analyses._1562 import (
        EfficiencyMapLoadCase,
    )
    from mastapy._private.electric_machines.load_cases_and_analyses._1563 import (
        ElectricMachineAnalysis,
    )
    from mastapy._private.electric_machines.load_cases_and_analyses._1564 import (
        ElectricMachineBasicMechanicalLossSettings,
    )
    from mastapy._private.electric_machines.load_cases_and_analyses._1565 import (
        ElectricMachineControlStrategy,
    )
    from mastapy._private.electric_machines.load_cases_and_analyses._1566 import (
        ElectricMachineEfficiencyMapSettings,
    )
    from mastapy._private.electric_machines.load_cases_and_analyses._1567 import (
        ElectricMachineFEAnalysis,
    )
    from mastapy._private.electric_machines.load_cases_and_analyses._1568 import (
        ElectricMachineFEMechanicalAnalysis,
    )
    from mastapy._private.electric_machines.load_cases_and_analyses._1569 import (
        ElectricMachineLoadCase,
    )
    from mastapy._private.electric_machines.load_cases_and_analyses._1570 import (
        ElectricMachineLoadCaseBase,
    )
    from mastapy._private.electric_machines.load_cases_and_analyses._1571 import (
        ElectricMachineLoadCaseGroup,
    )
    from mastapy._private.electric_machines.load_cases_and_analyses._1572 import (
        ElectricMachineMechanicalLoadCase,
    )
    from mastapy._private.electric_machines.load_cases_and_analyses._1573 import (
        EndWindingInductanceMethod,
    )
    from mastapy._private.electric_machines.load_cases_and_analyses._1574 import (
        LeadingOrLagging,
    )
    from mastapy._private.electric_machines.load_cases_and_analyses._1575 import (
        LoadCaseType,
    )
    from mastapy._private.electric_machines.load_cases_and_analyses._1576 import (
        LoadCaseTypeSelector,
    )
    from mastapy._private.electric_machines.load_cases_and_analyses._1577 import (
        MotoringOrGenerating,
    )
    from mastapy._private.electric_machines.load_cases_and_analyses._1578 import (
        NonLinearDQModelMultipleOperatingPointsLoadCase,
    )
    from mastapy._private.electric_machines.load_cases_and_analyses._1579 import (
        NumberOfStepsPerOperatingPointSpecificationMethod,
    )
    from mastapy._private.electric_machines.load_cases_and_analyses._1580 import (
        OperatingPointsSpecificationMethod,
    )
    from mastapy._private.electric_machines.load_cases_and_analyses._1581 import (
        SingleOperatingPointAnalysis,
    )
    from mastapy._private.electric_machines.load_cases_and_analyses._1582 import (
        SlotDetailForAnalysis,
    )
    from mastapy._private.electric_machines.load_cases_and_analyses._1583 import (
        SpecifyTorqueOrCurrent,
    )
    from mastapy._private.electric_machines.load_cases_and_analyses._1584 import (
        SpeedPointsDistribution,
    )
    from mastapy._private.electric_machines.load_cases_and_analyses._1585 import (
        SpeedTorqueCurveAnalysis,
    )
    from mastapy._private.electric_machines.load_cases_and_analyses._1586 import (
        SpeedTorqueCurveLoadCase,
    )
    from mastapy._private.electric_machines.load_cases_and_analyses._1587 import (
        SpeedTorqueLoadCase,
    )
    from mastapy._private.electric_machines.load_cases_and_analyses._1588 import (
        Temperatures,
    )
else:
    import sys as __sys

    from lazy_imports import LazyImporter as __LazyImporter

    __import_structure = {
        "_private.electric_machines.load_cases_and_analyses._1557": [
            "BasicDynamicForceLoadCase"
        ],
        "_private.electric_machines.load_cases_and_analyses._1558": [
            "DynamicForceAnalysis"
        ],
        "_private.electric_machines.load_cases_and_analyses._1559": [
            "DynamicForceLoadCase"
        ],
        "_private.electric_machines.load_cases_and_analyses._1560": [
            "DynamicForcesOperatingPoint"
        ],
        "_private.electric_machines.load_cases_and_analyses._1561": [
            "EfficiencyMapAnalysis"
        ],
        "_private.electric_machines.load_cases_and_analyses._1562": [
            "EfficiencyMapLoadCase"
        ],
        "_private.electric_machines.load_cases_and_analyses._1563": [
            "ElectricMachineAnalysis"
        ],
        "_private.electric_machines.load_cases_and_analyses._1564": [
            "ElectricMachineBasicMechanicalLossSettings"
        ],
        "_private.electric_machines.load_cases_and_analyses._1565": [
            "ElectricMachineControlStrategy"
        ],
        "_private.electric_machines.load_cases_and_analyses._1566": [
            "ElectricMachineEfficiencyMapSettings"
        ],
        "_private.electric_machines.load_cases_and_analyses._1567": [
            "ElectricMachineFEAnalysis"
        ],
        "_private.electric_machines.load_cases_and_analyses._1568": [
            "ElectricMachineFEMechanicalAnalysis"
        ],
        "_private.electric_machines.load_cases_and_analyses._1569": [
            "ElectricMachineLoadCase"
        ],
        "_private.electric_machines.load_cases_and_analyses._1570": [
            "ElectricMachineLoadCaseBase"
        ],
        "_private.electric_machines.load_cases_and_analyses._1571": [
            "ElectricMachineLoadCaseGroup"
        ],
        "_private.electric_machines.load_cases_and_analyses._1572": [
            "ElectricMachineMechanicalLoadCase"
        ],
        "_private.electric_machines.load_cases_and_analyses._1573": [
            "EndWindingInductanceMethod"
        ],
        "_private.electric_machines.load_cases_and_analyses._1574": [
            "LeadingOrLagging"
        ],
        "_private.electric_machines.load_cases_and_analyses._1575": ["LoadCaseType"],
        "_private.electric_machines.load_cases_and_analyses._1576": [
            "LoadCaseTypeSelector"
        ],
        "_private.electric_machines.load_cases_and_analyses._1577": [
            "MotoringOrGenerating"
        ],
        "_private.electric_machines.load_cases_and_analyses._1578": [
            "NonLinearDQModelMultipleOperatingPointsLoadCase"
        ],
        "_private.electric_machines.load_cases_and_analyses._1579": [
            "NumberOfStepsPerOperatingPointSpecificationMethod"
        ],
        "_private.electric_machines.load_cases_and_analyses._1580": [
            "OperatingPointsSpecificationMethod"
        ],
        "_private.electric_machines.load_cases_and_analyses._1581": [
            "SingleOperatingPointAnalysis"
        ],
        "_private.electric_machines.load_cases_and_analyses._1582": [
            "SlotDetailForAnalysis"
        ],
        "_private.electric_machines.load_cases_and_analyses._1583": [
            "SpecifyTorqueOrCurrent"
        ],
        "_private.electric_machines.load_cases_and_analyses._1584": [
            "SpeedPointsDistribution"
        ],
        "_private.electric_machines.load_cases_and_analyses._1585": [
            "SpeedTorqueCurveAnalysis"
        ],
        "_private.electric_machines.load_cases_and_analyses._1586": [
            "SpeedTorqueCurveLoadCase"
        ],
        "_private.electric_machines.load_cases_and_analyses._1587": [
            "SpeedTorqueLoadCase"
        ],
        "_private.electric_machines.load_cases_and_analyses._1588": ["Temperatures"],
    }

    __sys.modules[__name__] = __LazyImporter(
        "mastapy",
        globals()["__file__"],
        __import_structure,
    )

__all__ = (
    "BasicDynamicForceLoadCase",
    "DynamicForceAnalysis",
    "DynamicForceLoadCase",
    "DynamicForcesOperatingPoint",
    "EfficiencyMapAnalysis",
    "EfficiencyMapLoadCase",
    "ElectricMachineAnalysis",
    "ElectricMachineBasicMechanicalLossSettings",
    "ElectricMachineControlStrategy",
    "ElectricMachineEfficiencyMapSettings",
    "ElectricMachineFEAnalysis",
    "ElectricMachineFEMechanicalAnalysis",
    "ElectricMachineLoadCase",
    "ElectricMachineLoadCaseBase",
    "ElectricMachineLoadCaseGroup",
    "ElectricMachineMechanicalLoadCase",
    "EndWindingInductanceMethod",
    "LeadingOrLagging",
    "LoadCaseType",
    "LoadCaseTypeSelector",
    "MotoringOrGenerating",
    "NonLinearDQModelMultipleOperatingPointsLoadCase",
    "NumberOfStepsPerOperatingPointSpecificationMethod",
    "OperatingPointsSpecificationMethod",
    "SingleOperatingPointAnalysis",
    "SlotDetailForAnalysis",
    "SpecifyTorqueOrCurrent",
    "SpeedPointsDistribution",
    "SpeedTorqueCurveAnalysis",
    "SpeedTorqueCurveLoadCase",
    "SpeedTorqueLoadCase",
    "Temperatures",
)
