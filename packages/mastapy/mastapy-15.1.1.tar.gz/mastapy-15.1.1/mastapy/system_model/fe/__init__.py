"""Subpackage."""

from typing import TYPE_CHECKING as __tc

if __tc:
    from mastapy._private.system_model.fe._2614 import AlignConnectedComponentOptions
    from mastapy._private.system_model.fe._2615 import AlignmentMethod
    from mastapy._private.system_model.fe._2616 import AlignmentMethodForRaceBearing
    from mastapy._private.system_model.fe._2617 import AlignmentUsingAxialNodePositions
    from mastapy._private.system_model.fe._2618 import AngleSource
    from mastapy._private.system_model.fe._2619 import BaseFEWithSelection
    from mastapy._private.system_model.fe._2620 import BatchOperations
    from mastapy._private.system_model.fe._2621 import BearingNodeAlignmentOption
    from mastapy._private.system_model.fe._2622 import BearingNodeOption
    from mastapy._private.system_model.fe._2623 import BearingRaceNodeLink
    from mastapy._private.system_model.fe._2624 import BearingRacePosition
    from mastapy._private.system_model.fe._2625 import ComponentOrientationOption
    from mastapy._private.system_model.fe._2626 import ContactPairWithSelection
    from mastapy._private.system_model.fe._2627 import CoordinateSystemWithSelection
    from mastapy._private.system_model.fe._2628 import CreateConnectedComponentOptions
    from mastapy._private.system_model.fe._2629 import (
        CreateMicrophoneNormalToSurfaceOptions,
    )
    from mastapy._private.system_model.fe._2630 import DegreeOfFreedomBoundaryCondition
    from mastapy._private.system_model.fe._2631 import (
        DegreeOfFreedomBoundaryConditionAngular,
    )
    from mastapy._private.system_model.fe._2632 import (
        DegreeOfFreedomBoundaryConditionLinear,
    )
    from mastapy._private.system_model.fe._2633 import ElectricMachineDataSet
    from mastapy._private.system_model.fe._2634 import ElectricMachineDynamicLoadData
    from mastapy._private.system_model.fe._2635 import ElementFaceGroupWithSelection
    from mastapy._private.system_model.fe._2636 import ElementPropertiesWithSelection
    from mastapy._private.system_model.fe._2637 import ExportOptionsForNode
    from mastapy._private.system_model.fe._2638 import (
        ExportOptionsForNodeWithBoundaryConditionType,
    )
    from mastapy._private.system_model.fe._2639 import FEEntityGroupWithSelection
    from mastapy._private.system_model.fe._2640 import FEExportSettings
    from mastapy._private.system_model.fe._2641 import FEPartDRIVASurfaceSelection
    from mastapy._private.system_model.fe._2642 import FEPartWithBatchOptions
    from mastapy._private.system_model.fe._2643 import FEStiffnessGeometry
    from mastapy._private.system_model.fe._2644 import FEStiffnessTester
    from mastapy._private.system_model.fe._2645 import FESubstructure
    from mastapy._private.system_model.fe._2646 import FESubstructureExportOptions
    from mastapy._private.system_model.fe._2647 import FESubstructureNode
    from mastapy._private.system_model.fe._2648 import FESubstructureNodeModeShape
    from mastapy._private.system_model.fe._2649 import FESubstructureNodeModeShapes
    from mastapy._private.system_model.fe._2650 import FESubstructureType
    from mastapy._private.system_model.fe._2651 import FESubstructureWithBatchOptions
    from mastapy._private.system_model.fe._2652 import FESubstructureWithSelection
    from mastapy._private.system_model.fe._2653 import (
        FESubstructureWithSelectionComponents,
    )
    from mastapy._private.system_model.fe._2654 import (
        FESubstructureWithSelectionForHarmonicAnalysis,
    )
    from mastapy._private.system_model.fe._2655 import (
        FESubstructureWithSelectionForModalAnalysis,
    )
    from mastapy._private.system_model.fe._2656 import (
        FESubstructureWithSelectionForStaticAnalysis,
    )
    from mastapy._private.system_model.fe._2657 import GearMeshingOptions
    from mastapy._private.system_model.fe._2658 import (
        IndependentMASTACreatedCondensationNode,
    )
    from mastapy._private.system_model.fe._2659 import (
        IndependentMASTACreatedConstrainedNodes,
    )
    from mastapy._private.system_model.fe._2660 import (
        IndependentMASTACreatedConstrainedNodesWithSelectionComponents,
    )
    from mastapy._private.system_model.fe._2661 import (
        IndependentMASTACreatedRigidlyConnectedNodeGroup,
    )
    from mastapy._private.system_model.fe._2662 import (
        LinkComponentAxialPositionErrorReporter,
    )
    from mastapy._private.system_model.fe._2663 import LinkNodeSource
    from mastapy._private.system_model.fe._2664 import MaterialPropertiesWithSelection
    from mastapy._private.system_model.fe._2665 import (
        NodeBoundaryConditionsForFlexibleInterpolationConnection,
    )
    from mastapy._private.system_model.fe._2666 import (
        NodeBoundaryConditionStaticAnalysis,
    )
    from mastapy._private.system_model.fe._2667 import NodeGroupWithSelection
    from mastapy._private.system_model.fe._2668 import NodeSelectionDepthOption
    from mastapy._private.system_model.fe._2669 import NodesForPlanetarySocket
    from mastapy._private.system_model.fe._2670 import NodesForPlanetInSocket
    from mastapy._private.system_model.fe._2671 import (
        OptionsWhenExternalFEFileAlreadyExists,
    )
    from mastapy._private.system_model.fe._2672 import PerLinkExportOptions
    from mastapy._private.system_model.fe._2673 import RaceBearingFE
    from mastapy._private.system_model.fe._2674 import RaceBearingFESystemDeflection
    from mastapy._private.system_model.fe._2675 import RaceBearingFEWithSelection
    from mastapy._private.system_model.fe._2676 import ReplacedShaftSelectionHelper
    from mastapy._private.system_model.fe._2677 import SelectableNodeAtAngle
    from mastapy._private.system_model.fe._2678 import SystemDeflectionFEExportOptions
    from mastapy._private.system_model.fe._2679 import ThermalExpansionOption
else:
    import sys as __sys

    from lazy_imports import LazyImporter as __LazyImporter

    __import_structure = {
        "_private.system_model.fe._2614": ["AlignConnectedComponentOptions"],
        "_private.system_model.fe._2615": ["AlignmentMethod"],
        "_private.system_model.fe._2616": ["AlignmentMethodForRaceBearing"],
        "_private.system_model.fe._2617": ["AlignmentUsingAxialNodePositions"],
        "_private.system_model.fe._2618": ["AngleSource"],
        "_private.system_model.fe._2619": ["BaseFEWithSelection"],
        "_private.system_model.fe._2620": ["BatchOperations"],
        "_private.system_model.fe._2621": ["BearingNodeAlignmentOption"],
        "_private.system_model.fe._2622": ["BearingNodeOption"],
        "_private.system_model.fe._2623": ["BearingRaceNodeLink"],
        "_private.system_model.fe._2624": ["BearingRacePosition"],
        "_private.system_model.fe._2625": ["ComponentOrientationOption"],
        "_private.system_model.fe._2626": ["ContactPairWithSelection"],
        "_private.system_model.fe._2627": ["CoordinateSystemWithSelection"],
        "_private.system_model.fe._2628": ["CreateConnectedComponentOptions"],
        "_private.system_model.fe._2629": ["CreateMicrophoneNormalToSurfaceOptions"],
        "_private.system_model.fe._2630": ["DegreeOfFreedomBoundaryCondition"],
        "_private.system_model.fe._2631": ["DegreeOfFreedomBoundaryConditionAngular"],
        "_private.system_model.fe._2632": ["DegreeOfFreedomBoundaryConditionLinear"],
        "_private.system_model.fe._2633": ["ElectricMachineDataSet"],
        "_private.system_model.fe._2634": ["ElectricMachineDynamicLoadData"],
        "_private.system_model.fe._2635": ["ElementFaceGroupWithSelection"],
        "_private.system_model.fe._2636": ["ElementPropertiesWithSelection"],
        "_private.system_model.fe._2637": ["ExportOptionsForNode"],
        "_private.system_model.fe._2638": [
            "ExportOptionsForNodeWithBoundaryConditionType"
        ],
        "_private.system_model.fe._2639": ["FEEntityGroupWithSelection"],
        "_private.system_model.fe._2640": ["FEExportSettings"],
        "_private.system_model.fe._2641": ["FEPartDRIVASurfaceSelection"],
        "_private.system_model.fe._2642": ["FEPartWithBatchOptions"],
        "_private.system_model.fe._2643": ["FEStiffnessGeometry"],
        "_private.system_model.fe._2644": ["FEStiffnessTester"],
        "_private.system_model.fe._2645": ["FESubstructure"],
        "_private.system_model.fe._2646": ["FESubstructureExportOptions"],
        "_private.system_model.fe._2647": ["FESubstructureNode"],
        "_private.system_model.fe._2648": ["FESubstructureNodeModeShape"],
        "_private.system_model.fe._2649": ["FESubstructureNodeModeShapes"],
        "_private.system_model.fe._2650": ["FESubstructureType"],
        "_private.system_model.fe._2651": ["FESubstructureWithBatchOptions"],
        "_private.system_model.fe._2652": ["FESubstructureWithSelection"],
        "_private.system_model.fe._2653": ["FESubstructureWithSelectionComponents"],
        "_private.system_model.fe._2654": [
            "FESubstructureWithSelectionForHarmonicAnalysis"
        ],
        "_private.system_model.fe._2655": [
            "FESubstructureWithSelectionForModalAnalysis"
        ],
        "_private.system_model.fe._2656": [
            "FESubstructureWithSelectionForStaticAnalysis"
        ],
        "_private.system_model.fe._2657": ["GearMeshingOptions"],
        "_private.system_model.fe._2658": ["IndependentMASTACreatedCondensationNode"],
        "_private.system_model.fe._2659": ["IndependentMASTACreatedConstrainedNodes"],
        "_private.system_model.fe._2660": [
            "IndependentMASTACreatedConstrainedNodesWithSelectionComponents"
        ],
        "_private.system_model.fe._2661": [
            "IndependentMASTACreatedRigidlyConnectedNodeGroup"
        ],
        "_private.system_model.fe._2662": ["LinkComponentAxialPositionErrorReporter"],
        "_private.system_model.fe._2663": ["LinkNodeSource"],
        "_private.system_model.fe._2664": ["MaterialPropertiesWithSelection"],
        "_private.system_model.fe._2665": [
            "NodeBoundaryConditionsForFlexibleInterpolationConnection"
        ],
        "_private.system_model.fe._2666": ["NodeBoundaryConditionStaticAnalysis"],
        "_private.system_model.fe._2667": ["NodeGroupWithSelection"],
        "_private.system_model.fe._2668": ["NodeSelectionDepthOption"],
        "_private.system_model.fe._2669": ["NodesForPlanetarySocket"],
        "_private.system_model.fe._2670": ["NodesForPlanetInSocket"],
        "_private.system_model.fe._2671": ["OptionsWhenExternalFEFileAlreadyExists"],
        "_private.system_model.fe._2672": ["PerLinkExportOptions"],
        "_private.system_model.fe._2673": ["RaceBearingFE"],
        "_private.system_model.fe._2674": ["RaceBearingFESystemDeflection"],
        "_private.system_model.fe._2675": ["RaceBearingFEWithSelection"],
        "_private.system_model.fe._2676": ["ReplacedShaftSelectionHelper"],
        "_private.system_model.fe._2677": ["SelectableNodeAtAngle"],
        "_private.system_model.fe._2678": ["SystemDeflectionFEExportOptions"],
        "_private.system_model.fe._2679": ["ThermalExpansionOption"],
    }

    __sys.modules[__name__] = __LazyImporter(
        "mastapy",
        globals()["__file__"],
        __import_structure,
    )

__all__ = (
    "AlignConnectedComponentOptions",
    "AlignmentMethod",
    "AlignmentMethodForRaceBearing",
    "AlignmentUsingAxialNodePositions",
    "AngleSource",
    "BaseFEWithSelection",
    "BatchOperations",
    "BearingNodeAlignmentOption",
    "BearingNodeOption",
    "BearingRaceNodeLink",
    "BearingRacePosition",
    "ComponentOrientationOption",
    "ContactPairWithSelection",
    "CoordinateSystemWithSelection",
    "CreateConnectedComponentOptions",
    "CreateMicrophoneNormalToSurfaceOptions",
    "DegreeOfFreedomBoundaryCondition",
    "DegreeOfFreedomBoundaryConditionAngular",
    "DegreeOfFreedomBoundaryConditionLinear",
    "ElectricMachineDataSet",
    "ElectricMachineDynamicLoadData",
    "ElementFaceGroupWithSelection",
    "ElementPropertiesWithSelection",
    "ExportOptionsForNode",
    "ExportOptionsForNodeWithBoundaryConditionType",
    "FEEntityGroupWithSelection",
    "FEExportSettings",
    "FEPartDRIVASurfaceSelection",
    "FEPartWithBatchOptions",
    "FEStiffnessGeometry",
    "FEStiffnessTester",
    "FESubstructure",
    "FESubstructureExportOptions",
    "FESubstructureNode",
    "FESubstructureNodeModeShape",
    "FESubstructureNodeModeShapes",
    "FESubstructureType",
    "FESubstructureWithBatchOptions",
    "FESubstructureWithSelection",
    "FESubstructureWithSelectionComponents",
    "FESubstructureWithSelectionForHarmonicAnalysis",
    "FESubstructureWithSelectionForModalAnalysis",
    "FESubstructureWithSelectionForStaticAnalysis",
    "GearMeshingOptions",
    "IndependentMASTACreatedCondensationNode",
    "IndependentMASTACreatedConstrainedNodes",
    "IndependentMASTACreatedConstrainedNodesWithSelectionComponents",
    "IndependentMASTACreatedRigidlyConnectedNodeGroup",
    "LinkComponentAxialPositionErrorReporter",
    "LinkNodeSource",
    "MaterialPropertiesWithSelection",
    "NodeBoundaryConditionsForFlexibleInterpolationConnection",
    "NodeBoundaryConditionStaticAnalysis",
    "NodeGroupWithSelection",
    "NodeSelectionDepthOption",
    "NodesForPlanetarySocket",
    "NodesForPlanetInSocket",
    "OptionsWhenExternalFEFileAlreadyExists",
    "PerLinkExportOptions",
    "RaceBearingFE",
    "RaceBearingFESystemDeflection",
    "RaceBearingFEWithSelection",
    "ReplacedShaftSelectionHelper",
    "SelectableNodeAtAngle",
    "SystemDeflectionFEExportOptions",
    "ThermalExpansionOption",
)
