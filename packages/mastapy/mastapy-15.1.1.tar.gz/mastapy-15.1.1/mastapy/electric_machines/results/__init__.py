"""Subpackage."""

from typing import TYPE_CHECKING as __tc

if __tc:
    from mastapy._private.electric_machines.results._1532 import DynamicForceResults
    from mastapy._private.electric_machines.results._1533 import EfficiencyResults
    from mastapy._private.electric_machines.results._1534 import ElectricMachineDQModel
    from mastapy._private.electric_machines.results._1535 import (
        ElectricMachineMechanicalResults,
    )
    from mastapy._private.electric_machines.results._1536 import (
        ElectricMachineMechanicalResultsViewable,
    )
    from mastapy._private.electric_machines.results._1537 import ElectricMachineResults
    from mastapy._private.electric_machines.results._1538 import (
        ElectricMachineResultsForConductorTurn,
    )
    from mastapy._private.electric_machines.results._1539 import (
        ElectricMachineResultsForConductorTurnAtTimeStep,
    )
    from mastapy._private.electric_machines.results._1540 import (
        ElectricMachineResultsForLineToLine,
    )
    from mastapy._private.electric_machines.results._1541 import (
        ElectricMachineResultsForOpenCircuitAndOnLoad,
    )
    from mastapy._private.electric_machines.results._1542 import (
        ElectricMachineResultsForPhase,
    )
    from mastapy._private.electric_machines.results._1543 import (
        ElectricMachineResultsForPhaseAtTimeStep,
    )
    from mastapy._private.electric_machines.results._1544 import (
        ElectricMachineResultsForStatorToothAtTimeStep,
    )
    from mastapy._private.electric_machines.results._1545 import (
        ElectricMachineResultsLineToLineAtTimeStep,
    )
    from mastapy._private.electric_machines.results._1546 import (
        ElectricMachineResultsTimeStep,
    )
    from mastapy._private.electric_machines.results._1547 import (
        ElectricMachineResultsTimeStepAtLocation,
    )
    from mastapy._private.electric_machines.results._1548 import (
        ElectricMachineResultsViewable,
    )
    from mastapy._private.electric_machines.results._1549 import (
        ElectricMachineForceViewOptions,
    )
    from mastapy._private.electric_machines.results._1551 import LinearDQModel
    from mastapy._private.electric_machines.results._1552 import (
        MaximumTorqueResultsPoints,
    )
    from mastapy._private.electric_machines.results._1553 import NonLinearDQModel
    from mastapy._private.electric_machines.results._1554 import (
        NonLinearDQModelGeneratorSettings,
    )
    from mastapy._private.electric_machines.results._1555 import (
        OnLoadElectricMachineResults,
    )
    from mastapy._private.electric_machines.results._1556 import (
        OpenCircuitElectricMachineResults,
    )
else:
    import sys as __sys

    from lazy_imports import LazyImporter as __LazyImporter

    __import_structure = {
        "_private.electric_machines.results._1532": ["DynamicForceResults"],
        "_private.electric_machines.results._1533": ["EfficiencyResults"],
        "_private.electric_machines.results._1534": ["ElectricMachineDQModel"],
        "_private.electric_machines.results._1535": [
            "ElectricMachineMechanicalResults"
        ],
        "_private.electric_machines.results._1536": [
            "ElectricMachineMechanicalResultsViewable"
        ],
        "_private.electric_machines.results._1537": ["ElectricMachineResults"],
        "_private.electric_machines.results._1538": [
            "ElectricMachineResultsForConductorTurn"
        ],
        "_private.electric_machines.results._1539": [
            "ElectricMachineResultsForConductorTurnAtTimeStep"
        ],
        "_private.electric_machines.results._1540": [
            "ElectricMachineResultsForLineToLine"
        ],
        "_private.electric_machines.results._1541": [
            "ElectricMachineResultsForOpenCircuitAndOnLoad"
        ],
        "_private.electric_machines.results._1542": ["ElectricMachineResultsForPhase"],
        "_private.electric_machines.results._1543": [
            "ElectricMachineResultsForPhaseAtTimeStep"
        ],
        "_private.electric_machines.results._1544": [
            "ElectricMachineResultsForStatorToothAtTimeStep"
        ],
        "_private.electric_machines.results._1545": [
            "ElectricMachineResultsLineToLineAtTimeStep"
        ],
        "_private.electric_machines.results._1546": ["ElectricMachineResultsTimeStep"],
        "_private.electric_machines.results._1547": [
            "ElectricMachineResultsTimeStepAtLocation"
        ],
        "_private.electric_machines.results._1548": ["ElectricMachineResultsViewable"],
        "_private.electric_machines.results._1549": ["ElectricMachineForceViewOptions"],
        "_private.electric_machines.results._1551": ["LinearDQModel"],
        "_private.electric_machines.results._1552": ["MaximumTorqueResultsPoints"],
        "_private.electric_machines.results._1553": ["NonLinearDQModel"],
        "_private.electric_machines.results._1554": [
            "NonLinearDQModelGeneratorSettings"
        ],
        "_private.electric_machines.results._1555": ["OnLoadElectricMachineResults"],
        "_private.electric_machines.results._1556": [
            "OpenCircuitElectricMachineResults"
        ],
    }

    __sys.modules[__name__] = __LazyImporter(
        "mastapy",
        globals()["__file__"],
        __import_structure,
    )

__all__ = (
    "DynamicForceResults",
    "EfficiencyResults",
    "ElectricMachineDQModel",
    "ElectricMachineMechanicalResults",
    "ElectricMachineMechanicalResultsViewable",
    "ElectricMachineResults",
    "ElectricMachineResultsForConductorTurn",
    "ElectricMachineResultsForConductorTurnAtTimeStep",
    "ElectricMachineResultsForLineToLine",
    "ElectricMachineResultsForOpenCircuitAndOnLoad",
    "ElectricMachineResultsForPhase",
    "ElectricMachineResultsForPhaseAtTimeStep",
    "ElectricMachineResultsForStatorToothAtTimeStep",
    "ElectricMachineResultsLineToLineAtTimeStep",
    "ElectricMachineResultsTimeStep",
    "ElectricMachineResultsTimeStepAtLocation",
    "ElectricMachineResultsViewable",
    "ElectricMachineForceViewOptions",
    "LinearDQModel",
    "MaximumTorqueResultsPoints",
    "NonLinearDQModel",
    "NonLinearDQModelGeneratorSettings",
    "OnLoadElectricMachineResults",
    "OpenCircuitElectricMachineResults",
)
