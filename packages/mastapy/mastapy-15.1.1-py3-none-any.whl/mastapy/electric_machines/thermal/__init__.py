"""Subpackage."""

from typing import TYPE_CHECKING as __tc

if __tc:
    from mastapy._private.electric_machines.thermal._1487 import (
        AdditionalSliceSpecification,
    )
    from mastapy._private.electric_machines.thermal._1488 import Channel
    from mastapy._private.electric_machines.thermal._1489 import ComponentSetup
    from mastapy._private.electric_machines.thermal._1490 import (
        CoolingChannelForThermalAnalysis,
    )
    from mastapy._private.electric_machines.thermal._1491 import CoolingJacketType
    from mastapy._private.electric_machines.thermal._1492 import EdgeSelector
    from mastapy._private.electric_machines.thermal._1493 import (
        EndWindingCoolingFlowSource,
    )
    from mastapy._private.electric_machines.thermal._1494 import EndWindingLengthSource
    from mastapy._private.electric_machines.thermal._1495 import (
        EndWindingThermalElement,
    )
    from mastapy._private.electric_machines.thermal._1496 import (
        HeatTransferCoefficientCalculationMethod,
    )
    from mastapy._private.electric_machines.thermal._1497 import (
        HousingChannelModificationFactors,
    )
    from mastapy._private.electric_machines.thermal._1498 import HousingFlowDirection
    from mastapy._private.electric_machines.thermal._1499 import InitialInformation
    from mastapy._private.electric_machines.thermal._1500 import InletLocation
    from mastapy._private.electric_machines.thermal._1501 import (
        RegionIDForThermalAnalysis,
    )
    from mastapy._private.electric_machines.thermal._1502 import RotorSetup
    from mastapy._private.electric_machines.thermal._1503 import SliceLengthInformation
    from mastapy._private.electric_machines.thermal._1504 import (
        SliceLengthInformationPerRegion,
    )
    from mastapy._private.electric_machines.thermal._1505 import (
        SliceLengthInformationReporter,
    )
    from mastapy._private.electric_machines.thermal._1506 import StatorSetup
    from mastapy._private.electric_machines.thermal._1507 import ThermalElectricMachine
    from mastapy._private.electric_machines.thermal._1508 import (
        ThermalElectricMachineSetup,
    )
    from mastapy._private.electric_machines.thermal._1509 import ThermalEndcap
    from mastapy._private.electric_machines.thermal._1510 import ThermalEndWinding
    from mastapy._private.electric_machines.thermal._1511 import (
        ThermalEndWindingSurfaceCollection,
    )
    from mastapy._private.electric_machines.thermal._1512 import ThermalHousing
    from mastapy._private.electric_machines.thermal._1513 import ThermalRotor
    from mastapy._private.electric_machines.thermal._1514 import ThermalStator
    from mastapy._private.electric_machines.thermal._1515 import ThermalWindings
    from mastapy._private.electric_machines.thermal._1516 import (
        UserSpecifiedEdgeIndices,
    )
else:
    import sys as __sys

    from lazy_imports import LazyImporter as __LazyImporter

    __import_structure = {
        "_private.electric_machines.thermal._1487": ["AdditionalSliceSpecification"],
        "_private.electric_machines.thermal._1488": ["Channel"],
        "_private.electric_machines.thermal._1489": ["ComponentSetup"],
        "_private.electric_machines.thermal._1490": [
            "CoolingChannelForThermalAnalysis"
        ],
        "_private.electric_machines.thermal._1491": ["CoolingJacketType"],
        "_private.electric_machines.thermal._1492": ["EdgeSelector"],
        "_private.electric_machines.thermal._1493": ["EndWindingCoolingFlowSource"],
        "_private.electric_machines.thermal._1494": ["EndWindingLengthSource"],
        "_private.electric_machines.thermal._1495": ["EndWindingThermalElement"],
        "_private.electric_machines.thermal._1496": [
            "HeatTransferCoefficientCalculationMethod"
        ],
        "_private.electric_machines.thermal._1497": [
            "HousingChannelModificationFactors"
        ],
        "_private.electric_machines.thermal._1498": ["HousingFlowDirection"],
        "_private.electric_machines.thermal._1499": ["InitialInformation"],
        "_private.electric_machines.thermal._1500": ["InletLocation"],
        "_private.electric_machines.thermal._1501": ["RegionIDForThermalAnalysis"],
        "_private.electric_machines.thermal._1502": ["RotorSetup"],
        "_private.electric_machines.thermal._1503": ["SliceLengthInformation"],
        "_private.electric_machines.thermal._1504": ["SliceLengthInformationPerRegion"],
        "_private.electric_machines.thermal._1505": ["SliceLengthInformationReporter"],
        "_private.electric_machines.thermal._1506": ["StatorSetup"],
        "_private.electric_machines.thermal._1507": ["ThermalElectricMachine"],
        "_private.electric_machines.thermal._1508": ["ThermalElectricMachineSetup"],
        "_private.electric_machines.thermal._1509": ["ThermalEndcap"],
        "_private.electric_machines.thermal._1510": ["ThermalEndWinding"],
        "_private.electric_machines.thermal._1511": [
            "ThermalEndWindingSurfaceCollection"
        ],
        "_private.electric_machines.thermal._1512": ["ThermalHousing"],
        "_private.electric_machines.thermal._1513": ["ThermalRotor"],
        "_private.electric_machines.thermal._1514": ["ThermalStator"],
        "_private.electric_machines.thermal._1515": ["ThermalWindings"],
        "_private.electric_machines.thermal._1516": ["UserSpecifiedEdgeIndices"],
    }

    __sys.modules[__name__] = __LazyImporter(
        "mastapy",
        globals()["__file__"],
        __import_structure,
    )

__all__ = (
    "AdditionalSliceSpecification",
    "Channel",
    "ComponentSetup",
    "CoolingChannelForThermalAnalysis",
    "CoolingJacketType",
    "EdgeSelector",
    "EndWindingCoolingFlowSource",
    "EndWindingLengthSource",
    "EndWindingThermalElement",
    "HeatTransferCoefficientCalculationMethod",
    "HousingChannelModificationFactors",
    "HousingFlowDirection",
    "InitialInformation",
    "InletLocation",
    "RegionIDForThermalAnalysis",
    "RotorSetup",
    "SliceLengthInformation",
    "SliceLengthInformationPerRegion",
    "SliceLengthInformationReporter",
    "StatorSetup",
    "ThermalElectricMachine",
    "ThermalElectricMachineSetup",
    "ThermalEndcap",
    "ThermalEndWinding",
    "ThermalEndWindingSurfaceCollection",
    "ThermalHousing",
    "ThermalRotor",
    "ThermalStator",
    "ThermalWindings",
    "UserSpecifiedEdgeIndices",
)
