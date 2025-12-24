"""Subpackage."""

from typing import TYPE_CHECKING as __tc

if __tc:
    from mastapy._private.electric_machines._1391 import AbstractStator
    from mastapy._private.electric_machines._1392 import AbstractToothAndSlot
    from mastapy._private.electric_machines._1393 import CADConductor
    from mastapy._private.electric_machines._1394 import CADElectricMachineDetail
    from mastapy._private.electric_machines._1395 import CADFieldWindingSpecification
    from mastapy._private.electric_machines._1396 import CADMagnetDetails
    from mastapy._private.electric_machines._1397 import CADMagnetsForLayer
    from mastapy._private.electric_machines._1398 import CADRotor
    from mastapy._private.electric_machines._1399 import CADStator
    from mastapy._private.electric_machines._1400 import CADToothAndSlot
    from mastapy._private.electric_machines._1401 import CADWoundFieldSynchronousRotor
    from mastapy._private.electric_machines._1402 import Coil
    from mastapy._private.electric_machines._1403 import CoilPositionInSlot
    from mastapy._private.electric_machines._1404 import CoolingChannelShape
    from mastapy._private.electric_machines._1405 import CoolingDuctLayerSpecification
    from mastapy._private.electric_machines._1406 import CoolingDuctShape
    from mastapy._private.electric_machines._1407 import (
        CoreLossBuildFactorSpecificationMethod,
    )
    from mastapy._private.electric_machines._1408 import CoreLossCoefficients
    from mastapy._private.electric_machines._1409 import DoubleLayerWindingSlotPositions
    from mastapy._private.electric_machines._1410 import DQAxisConvention
    from mastapy._private.electric_machines._1411 import Eccentricity
    from mastapy._private.electric_machines._1412 import ElectricMachineDesignBase
    from mastapy._private.electric_machines._1413 import ElectricMachineDetail
    from mastapy._private.electric_machines._1414 import (
        ElectricMachineDetailInitialInformation,
    )
    from mastapy._private.electric_machines._1415 import (
        ElectricMachineElectromagneticAndThermalMeshingOptions,
    )
    from mastapy._private.electric_machines._1416 import ElectricMachineGroup
    from mastapy._private.electric_machines._1417 import (
        ElectricMachineMechanicalAnalysisMeshingOptions,
    )
    from mastapy._private.electric_machines._1418 import ElectricMachineMeshingOptions
    from mastapy._private.electric_machines._1419 import (
        ElectricMachineMeshingOptionsBase,
    )
    from mastapy._private.electric_machines._1420 import ElectricMachineSetup
    from mastapy._private.electric_machines._1421 import ElectricMachineSetupBase
    from mastapy._private.electric_machines._1422 import (
        ElectricMachineThermalMeshingOptions,
    )
    from mastapy._private.electric_machines._1423 import ElectricMachineType
    from mastapy._private.electric_machines._1424 import FieldWindingSpecification
    from mastapy._private.electric_machines._1425 import FieldWindingSpecificationBase
    from mastapy._private.electric_machines._1426 import FillFactorSpecificationMethod
    from mastapy._private.electric_machines._1427 import FluxBarriers
    from mastapy._private.electric_machines._1428 import FluxBarrierOrWeb
    from mastapy._private.electric_machines._1429 import FluxBarrierStyle
    from mastapy._private.electric_machines._1430 import GeneralElectricMachineMaterial
    from mastapy._private.electric_machines._1431 import (
        GeneralElectricMachineMaterialDatabase,
    )
    from mastapy._private.electric_machines._1432 import HairpinConductor
    from mastapy._private.electric_machines._1433 import (
        HarmonicLoadDataControlExcitationOptionForElectricMachineMode,
    )
    from mastapy._private.electric_machines._1434 import (
        IndividualConductorSpecificationSource,
    )
    from mastapy._private.electric_machines._1435 import (
        InteriorPermanentMagnetAndSynchronousReluctanceRotor,
    )
    from mastapy._private.electric_machines._1436 import InteriorPermanentMagnetMachine
    from mastapy._private.electric_machines._1437 import (
        IronLossCoefficientSpecificationMethod,
    )
    from mastapy._private.electric_machines._1438 import MagnetClearance
    from mastapy._private.electric_machines._1439 import MagnetConfiguration
    from mastapy._private.electric_machines._1440 import MagnetData
    from mastapy._private.electric_machines._1441 import MagnetDesign
    from mastapy._private.electric_machines._1442 import MagnetForLayer
    from mastapy._private.electric_machines._1443 import MagnetisationDirection
    from mastapy._private.electric_machines._1444 import MagnetMaterial
    from mastapy._private.electric_machines._1445 import MagnetMaterialDatabase
    from mastapy._private.electric_machines._1446 import MotorRotorSideFaceDetail
    from mastapy._private.electric_machines._1447 import NonCADElectricMachineDetail
    from mastapy._private.electric_machines._1448 import NotchShape
    from mastapy._private.electric_machines._1449 import NotchSpecification
    from mastapy._private.electric_machines._1450 import (
        PermanentMagnetAssistedSynchronousReluctanceMachine,
    )
    from mastapy._private.electric_machines._1451 import PermanentMagnetRotor
    from mastapy._private.electric_machines._1452 import Phase
    from mastapy._private.electric_machines._1453 import RegionID
    from mastapy._private.electric_machines._1454 import RemanenceModifier
    from mastapy._private.electric_machines._1455 import ResultsLocationsSpecification
    from mastapy._private.electric_machines._1456 import Rotor
    from mastapy._private.electric_machines._1457 import RotorInternalLayerSpecification
    from mastapy._private.electric_machines._1458 import RotorSkewSlice
    from mastapy._private.electric_machines._1459 import RotorType
    from mastapy._private.electric_machines._1460 import SingleOrDoubleLayerWindings
    from mastapy._private.electric_machines._1461 import SlotSectionDetail
    from mastapy._private.electric_machines._1462 import Stator
    from mastapy._private.electric_machines._1463 import StatorCutoutSpecification
    from mastapy._private.electric_machines._1464 import StatorRotorMaterial
    from mastapy._private.electric_machines._1465 import StatorRotorMaterialDatabase
    from mastapy._private.electric_machines._1466 import SurfacePermanentMagnetMachine
    from mastapy._private.electric_machines._1467 import SurfacePermanentMagnetRotor
    from mastapy._private.electric_machines._1468 import SynchronousReluctanceMachine
    from mastapy._private.electric_machines._1469 import ToothAndSlot
    from mastapy._private.electric_machines._1470 import ToothSlotStyle
    from mastapy._private.electric_machines._1471 import ToothTaperSpecification
    from mastapy._private.electric_machines._1472 import (
        TwoDimensionalFEModelForAnalysis,
    )
    from mastapy._private.electric_machines._1473 import (
        TwoDimensionalFEModelForElectromagneticAnalysis,
    )
    from mastapy._private.electric_machines._1474 import (
        TwoDimensionalFEModelForMechanicalAnalysis,
    )
    from mastapy._private.electric_machines._1475 import UShapedLayerSpecification
    from mastapy._private.electric_machines._1476 import VShapedMagnetLayerSpecification
    from mastapy._private.electric_machines._1477 import WindingConductor
    from mastapy._private.electric_machines._1478 import WindingConnection
    from mastapy._private.electric_machines._1479 import WindingMaterial
    from mastapy._private.electric_machines._1480 import WindingMaterialDatabase
    from mastapy._private.electric_machines._1481 import Windings
    from mastapy._private.electric_machines._1482 import WindingsViewer
    from mastapy._private.electric_machines._1483 import WindingType
    from mastapy._private.electric_machines._1484 import WireSizeSpecificationMethod
    from mastapy._private.electric_machines._1485 import WoundFieldSynchronousMachine
    from mastapy._private.electric_machines._1486 import WoundFieldSynchronousRotor
else:
    import sys as __sys

    from lazy_imports import LazyImporter as __LazyImporter

    __import_structure = {
        "_private.electric_machines._1391": ["AbstractStator"],
        "_private.electric_machines._1392": ["AbstractToothAndSlot"],
        "_private.electric_machines._1393": ["CADConductor"],
        "_private.electric_machines._1394": ["CADElectricMachineDetail"],
        "_private.electric_machines._1395": ["CADFieldWindingSpecification"],
        "_private.electric_machines._1396": ["CADMagnetDetails"],
        "_private.electric_machines._1397": ["CADMagnetsForLayer"],
        "_private.electric_machines._1398": ["CADRotor"],
        "_private.electric_machines._1399": ["CADStator"],
        "_private.electric_machines._1400": ["CADToothAndSlot"],
        "_private.electric_machines._1401": ["CADWoundFieldSynchronousRotor"],
        "_private.electric_machines._1402": ["Coil"],
        "_private.electric_machines._1403": ["CoilPositionInSlot"],
        "_private.electric_machines._1404": ["CoolingChannelShape"],
        "_private.electric_machines._1405": ["CoolingDuctLayerSpecification"],
        "_private.electric_machines._1406": ["CoolingDuctShape"],
        "_private.electric_machines._1407": ["CoreLossBuildFactorSpecificationMethod"],
        "_private.electric_machines._1408": ["CoreLossCoefficients"],
        "_private.electric_machines._1409": ["DoubleLayerWindingSlotPositions"],
        "_private.electric_machines._1410": ["DQAxisConvention"],
        "_private.electric_machines._1411": ["Eccentricity"],
        "_private.electric_machines._1412": ["ElectricMachineDesignBase"],
        "_private.electric_machines._1413": ["ElectricMachineDetail"],
        "_private.electric_machines._1414": ["ElectricMachineDetailInitialInformation"],
        "_private.electric_machines._1415": [
            "ElectricMachineElectromagneticAndThermalMeshingOptions"
        ],
        "_private.electric_machines._1416": ["ElectricMachineGroup"],
        "_private.electric_machines._1417": [
            "ElectricMachineMechanicalAnalysisMeshingOptions"
        ],
        "_private.electric_machines._1418": ["ElectricMachineMeshingOptions"],
        "_private.electric_machines._1419": ["ElectricMachineMeshingOptionsBase"],
        "_private.electric_machines._1420": ["ElectricMachineSetup"],
        "_private.electric_machines._1421": ["ElectricMachineSetupBase"],
        "_private.electric_machines._1422": ["ElectricMachineThermalMeshingOptions"],
        "_private.electric_machines._1423": ["ElectricMachineType"],
        "_private.electric_machines._1424": ["FieldWindingSpecification"],
        "_private.electric_machines._1425": ["FieldWindingSpecificationBase"],
        "_private.electric_machines._1426": ["FillFactorSpecificationMethod"],
        "_private.electric_machines._1427": ["FluxBarriers"],
        "_private.electric_machines._1428": ["FluxBarrierOrWeb"],
        "_private.electric_machines._1429": ["FluxBarrierStyle"],
        "_private.electric_machines._1430": ["GeneralElectricMachineMaterial"],
        "_private.electric_machines._1431": ["GeneralElectricMachineMaterialDatabase"],
        "_private.electric_machines._1432": ["HairpinConductor"],
        "_private.electric_machines._1433": [
            "HarmonicLoadDataControlExcitationOptionForElectricMachineMode"
        ],
        "_private.electric_machines._1434": ["IndividualConductorSpecificationSource"],
        "_private.electric_machines._1435": [
            "InteriorPermanentMagnetAndSynchronousReluctanceRotor"
        ],
        "_private.electric_machines._1436": ["InteriorPermanentMagnetMachine"],
        "_private.electric_machines._1437": ["IronLossCoefficientSpecificationMethod"],
        "_private.electric_machines._1438": ["MagnetClearance"],
        "_private.electric_machines._1439": ["MagnetConfiguration"],
        "_private.electric_machines._1440": ["MagnetData"],
        "_private.electric_machines._1441": ["MagnetDesign"],
        "_private.electric_machines._1442": ["MagnetForLayer"],
        "_private.electric_machines._1443": ["MagnetisationDirection"],
        "_private.electric_machines._1444": ["MagnetMaterial"],
        "_private.electric_machines._1445": ["MagnetMaterialDatabase"],
        "_private.electric_machines._1446": ["MotorRotorSideFaceDetail"],
        "_private.electric_machines._1447": ["NonCADElectricMachineDetail"],
        "_private.electric_machines._1448": ["NotchShape"],
        "_private.electric_machines._1449": ["NotchSpecification"],
        "_private.electric_machines._1450": [
            "PermanentMagnetAssistedSynchronousReluctanceMachine"
        ],
        "_private.electric_machines._1451": ["PermanentMagnetRotor"],
        "_private.electric_machines._1452": ["Phase"],
        "_private.electric_machines._1453": ["RegionID"],
        "_private.electric_machines._1454": ["RemanenceModifier"],
        "_private.electric_machines._1455": ["ResultsLocationsSpecification"],
        "_private.electric_machines._1456": ["Rotor"],
        "_private.electric_machines._1457": ["RotorInternalLayerSpecification"],
        "_private.electric_machines._1458": ["RotorSkewSlice"],
        "_private.electric_machines._1459": ["RotorType"],
        "_private.electric_machines._1460": ["SingleOrDoubleLayerWindings"],
        "_private.electric_machines._1461": ["SlotSectionDetail"],
        "_private.electric_machines._1462": ["Stator"],
        "_private.electric_machines._1463": ["StatorCutoutSpecification"],
        "_private.electric_machines._1464": ["StatorRotorMaterial"],
        "_private.electric_machines._1465": ["StatorRotorMaterialDatabase"],
        "_private.electric_machines._1466": ["SurfacePermanentMagnetMachine"],
        "_private.electric_machines._1467": ["SurfacePermanentMagnetRotor"],
        "_private.electric_machines._1468": ["SynchronousReluctanceMachine"],
        "_private.electric_machines._1469": ["ToothAndSlot"],
        "_private.electric_machines._1470": ["ToothSlotStyle"],
        "_private.electric_machines._1471": ["ToothTaperSpecification"],
        "_private.electric_machines._1472": ["TwoDimensionalFEModelForAnalysis"],
        "_private.electric_machines._1473": [
            "TwoDimensionalFEModelForElectromagneticAnalysis"
        ],
        "_private.electric_machines._1474": [
            "TwoDimensionalFEModelForMechanicalAnalysis"
        ],
        "_private.electric_machines._1475": ["UShapedLayerSpecification"],
        "_private.electric_machines._1476": ["VShapedMagnetLayerSpecification"],
        "_private.electric_machines._1477": ["WindingConductor"],
        "_private.electric_machines._1478": ["WindingConnection"],
        "_private.electric_machines._1479": ["WindingMaterial"],
        "_private.electric_machines._1480": ["WindingMaterialDatabase"],
        "_private.electric_machines._1481": ["Windings"],
        "_private.electric_machines._1482": ["WindingsViewer"],
        "_private.electric_machines._1483": ["WindingType"],
        "_private.electric_machines._1484": ["WireSizeSpecificationMethod"],
        "_private.electric_machines._1485": ["WoundFieldSynchronousMachine"],
        "_private.electric_machines._1486": ["WoundFieldSynchronousRotor"],
    }

    __sys.modules[__name__] = __LazyImporter(
        "mastapy",
        globals()["__file__"],
        __import_structure,
    )

__all__ = (
    "AbstractStator",
    "AbstractToothAndSlot",
    "CADConductor",
    "CADElectricMachineDetail",
    "CADFieldWindingSpecification",
    "CADMagnetDetails",
    "CADMagnetsForLayer",
    "CADRotor",
    "CADStator",
    "CADToothAndSlot",
    "CADWoundFieldSynchronousRotor",
    "Coil",
    "CoilPositionInSlot",
    "CoolingChannelShape",
    "CoolingDuctLayerSpecification",
    "CoolingDuctShape",
    "CoreLossBuildFactorSpecificationMethod",
    "CoreLossCoefficients",
    "DoubleLayerWindingSlotPositions",
    "DQAxisConvention",
    "Eccentricity",
    "ElectricMachineDesignBase",
    "ElectricMachineDetail",
    "ElectricMachineDetailInitialInformation",
    "ElectricMachineElectromagneticAndThermalMeshingOptions",
    "ElectricMachineGroup",
    "ElectricMachineMechanicalAnalysisMeshingOptions",
    "ElectricMachineMeshingOptions",
    "ElectricMachineMeshingOptionsBase",
    "ElectricMachineSetup",
    "ElectricMachineSetupBase",
    "ElectricMachineThermalMeshingOptions",
    "ElectricMachineType",
    "FieldWindingSpecification",
    "FieldWindingSpecificationBase",
    "FillFactorSpecificationMethod",
    "FluxBarriers",
    "FluxBarrierOrWeb",
    "FluxBarrierStyle",
    "GeneralElectricMachineMaterial",
    "GeneralElectricMachineMaterialDatabase",
    "HairpinConductor",
    "HarmonicLoadDataControlExcitationOptionForElectricMachineMode",
    "IndividualConductorSpecificationSource",
    "InteriorPermanentMagnetAndSynchronousReluctanceRotor",
    "InteriorPermanentMagnetMachine",
    "IronLossCoefficientSpecificationMethod",
    "MagnetClearance",
    "MagnetConfiguration",
    "MagnetData",
    "MagnetDesign",
    "MagnetForLayer",
    "MagnetisationDirection",
    "MagnetMaterial",
    "MagnetMaterialDatabase",
    "MotorRotorSideFaceDetail",
    "NonCADElectricMachineDetail",
    "NotchShape",
    "NotchSpecification",
    "PermanentMagnetAssistedSynchronousReluctanceMachine",
    "PermanentMagnetRotor",
    "Phase",
    "RegionID",
    "RemanenceModifier",
    "ResultsLocationsSpecification",
    "Rotor",
    "RotorInternalLayerSpecification",
    "RotorSkewSlice",
    "RotorType",
    "SingleOrDoubleLayerWindings",
    "SlotSectionDetail",
    "Stator",
    "StatorCutoutSpecification",
    "StatorRotorMaterial",
    "StatorRotorMaterialDatabase",
    "SurfacePermanentMagnetMachine",
    "SurfacePermanentMagnetRotor",
    "SynchronousReluctanceMachine",
    "ToothAndSlot",
    "ToothSlotStyle",
    "ToothTaperSpecification",
    "TwoDimensionalFEModelForAnalysis",
    "TwoDimensionalFEModelForElectromagneticAnalysis",
    "TwoDimensionalFEModelForMechanicalAnalysis",
    "UShapedLayerSpecification",
    "VShapedMagnetLayerSpecification",
    "WindingConductor",
    "WindingConnection",
    "WindingMaterial",
    "WindingMaterialDatabase",
    "Windings",
    "WindingsViewer",
    "WindingType",
    "WireSizeSpecificationMethod",
    "WoundFieldSynchronousMachine",
    "WoundFieldSynchronousRotor",
)
