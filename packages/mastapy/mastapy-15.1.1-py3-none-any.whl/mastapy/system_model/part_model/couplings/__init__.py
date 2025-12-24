"""Subpackage."""

from typing import TYPE_CHECKING as __tc

if __tc:
    from mastapy._private.system_model.part_model.couplings._2859 import BeltDrive
    from mastapy._private.system_model.part_model.couplings._2860 import BeltDriveType
    from mastapy._private.system_model.part_model.couplings._2861 import Clutch
    from mastapy._private.system_model.part_model.couplings._2862 import ClutchHalf
    from mastapy._private.system_model.part_model.couplings._2863 import ClutchType
    from mastapy._private.system_model.part_model.couplings._2864 import ConceptCoupling
    from mastapy._private.system_model.part_model.couplings._2865 import (
        ConceptCouplingHalf,
    )
    from mastapy._private.system_model.part_model.couplings._2866 import (
        ConceptCouplingHalfPositioning,
    )
    from mastapy._private.system_model.part_model.couplings._2867 import Coupling
    from mastapy._private.system_model.part_model.couplings._2868 import CouplingHalf
    from mastapy._private.system_model.part_model.couplings._2869 import (
        CrowningSpecification,
    )
    from mastapy._private.system_model.part_model.couplings._2870 import CVT
    from mastapy._private.system_model.part_model.couplings._2871 import CVTPulley
    from mastapy._private.system_model.part_model.couplings._2872 import (
        PartToPartShearCoupling,
    )
    from mastapy._private.system_model.part_model.couplings._2873 import (
        PartToPartShearCouplingHalf,
    )
    from mastapy._private.system_model.part_model.couplings._2874 import (
        PitchErrorFlankOptions,
    )
    from mastapy._private.system_model.part_model.couplings._2875 import Pulley
    from mastapy._private.system_model.part_model.couplings._2876 import (
        RigidConnectorSettings,
    )
    from mastapy._private.system_model.part_model.couplings._2877 import (
        RigidConnectorStiffnessType,
    )
    from mastapy._private.system_model.part_model.couplings._2878 import (
        RigidConnectorTiltStiffnessTypes,
    )
    from mastapy._private.system_model.part_model.couplings._2879 import (
        RigidConnectorToothLocation,
    )
    from mastapy._private.system_model.part_model.couplings._2880 import (
        RigidConnectorToothSpacingType,
    )
    from mastapy._private.system_model.part_model.couplings._2881 import (
        RigidConnectorTypes,
    )
    from mastapy._private.system_model.part_model.couplings._2882 import RollingRing
    from mastapy._private.system_model.part_model.couplings._2883 import (
        RollingRingAssembly,
    )
    from mastapy._private.system_model.part_model.couplings._2884 import (
        ShaftHubConnection,
    )
    from mastapy._private.system_model.part_model.couplings._2885 import (
        SplineFitOptions,
    )
    from mastapy._private.system_model.part_model.couplings._2886 import (
        SplineHalfManufacturingError,
    )
    from mastapy._private.system_model.part_model.couplings._2887 import (
        SplineLeadRelief,
    )
    from mastapy._private.system_model.part_model.couplings._2888 import (
        SplinePitchErrorInputType,
    )
    from mastapy._private.system_model.part_model.couplings._2889 import (
        SplinePitchErrorOptions,
    )
    from mastapy._private.system_model.part_model.couplings._2890 import SpringDamper
    from mastapy._private.system_model.part_model.couplings._2891 import (
        SpringDamperHalf,
    )
    from mastapy._private.system_model.part_model.couplings._2892 import Synchroniser
    from mastapy._private.system_model.part_model.couplings._2893 import (
        SynchroniserCone,
    )
    from mastapy._private.system_model.part_model.couplings._2894 import (
        SynchroniserHalf,
    )
    from mastapy._private.system_model.part_model.couplings._2895 import (
        SynchroniserPart,
    )
    from mastapy._private.system_model.part_model.couplings._2896 import (
        SynchroniserSleeve,
    )
    from mastapy._private.system_model.part_model.couplings._2897 import TorqueConverter
    from mastapy._private.system_model.part_model.couplings._2898 import (
        TorqueConverterPump,
    )
    from mastapy._private.system_model.part_model.couplings._2899 import (
        TorqueConverterSpeedRatio,
    )
    from mastapy._private.system_model.part_model.couplings._2900 import (
        TorqueConverterTurbine,
    )
else:
    import sys as __sys

    from lazy_imports import LazyImporter as __LazyImporter

    __import_structure = {
        "_private.system_model.part_model.couplings._2859": ["BeltDrive"],
        "_private.system_model.part_model.couplings._2860": ["BeltDriveType"],
        "_private.system_model.part_model.couplings._2861": ["Clutch"],
        "_private.system_model.part_model.couplings._2862": ["ClutchHalf"],
        "_private.system_model.part_model.couplings._2863": ["ClutchType"],
        "_private.system_model.part_model.couplings._2864": ["ConceptCoupling"],
        "_private.system_model.part_model.couplings._2865": ["ConceptCouplingHalf"],
        "_private.system_model.part_model.couplings._2866": [
            "ConceptCouplingHalfPositioning"
        ],
        "_private.system_model.part_model.couplings._2867": ["Coupling"],
        "_private.system_model.part_model.couplings._2868": ["CouplingHalf"],
        "_private.system_model.part_model.couplings._2869": ["CrowningSpecification"],
        "_private.system_model.part_model.couplings._2870": ["CVT"],
        "_private.system_model.part_model.couplings._2871": ["CVTPulley"],
        "_private.system_model.part_model.couplings._2872": ["PartToPartShearCoupling"],
        "_private.system_model.part_model.couplings._2873": [
            "PartToPartShearCouplingHalf"
        ],
        "_private.system_model.part_model.couplings._2874": ["PitchErrorFlankOptions"],
        "_private.system_model.part_model.couplings._2875": ["Pulley"],
        "_private.system_model.part_model.couplings._2876": ["RigidConnectorSettings"],
        "_private.system_model.part_model.couplings._2877": [
            "RigidConnectorStiffnessType"
        ],
        "_private.system_model.part_model.couplings._2878": [
            "RigidConnectorTiltStiffnessTypes"
        ],
        "_private.system_model.part_model.couplings._2879": [
            "RigidConnectorToothLocation"
        ],
        "_private.system_model.part_model.couplings._2880": [
            "RigidConnectorToothSpacingType"
        ],
        "_private.system_model.part_model.couplings._2881": ["RigidConnectorTypes"],
        "_private.system_model.part_model.couplings._2882": ["RollingRing"],
        "_private.system_model.part_model.couplings._2883": ["RollingRingAssembly"],
        "_private.system_model.part_model.couplings._2884": ["ShaftHubConnection"],
        "_private.system_model.part_model.couplings._2885": ["SplineFitOptions"],
        "_private.system_model.part_model.couplings._2886": [
            "SplineHalfManufacturingError"
        ],
        "_private.system_model.part_model.couplings._2887": ["SplineLeadRelief"],
        "_private.system_model.part_model.couplings._2888": [
            "SplinePitchErrorInputType"
        ],
        "_private.system_model.part_model.couplings._2889": ["SplinePitchErrorOptions"],
        "_private.system_model.part_model.couplings._2890": ["SpringDamper"],
        "_private.system_model.part_model.couplings._2891": ["SpringDamperHalf"],
        "_private.system_model.part_model.couplings._2892": ["Synchroniser"],
        "_private.system_model.part_model.couplings._2893": ["SynchroniserCone"],
        "_private.system_model.part_model.couplings._2894": ["SynchroniserHalf"],
        "_private.system_model.part_model.couplings._2895": ["SynchroniserPart"],
        "_private.system_model.part_model.couplings._2896": ["SynchroniserSleeve"],
        "_private.system_model.part_model.couplings._2897": ["TorqueConverter"],
        "_private.system_model.part_model.couplings._2898": ["TorqueConverterPump"],
        "_private.system_model.part_model.couplings._2899": [
            "TorqueConverterSpeedRatio"
        ],
        "_private.system_model.part_model.couplings._2900": ["TorqueConverterTurbine"],
    }

    __sys.modules[__name__] = __LazyImporter(
        "mastapy",
        globals()["__file__"],
        __import_structure,
    )

__all__ = (
    "BeltDrive",
    "BeltDriveType",
    "Clutch",
    "ClutchHalf",
    "ClutchType",
    "ConceptCoupling",
    "ConceptCouplingHalf",
    "ConceptCouplingHalfPositioning",
    "Coupling",
    "CouplingHalf",
    "CrowningSpecification",
    "CVT",
    "CVTPulley",
    "PartToPartShearCoupling",
    "PartToPartShearCouplingHalf",
    "PitchErrorFlankOptions",
    "Pulley",
    "RigidConnectorSettings",
    "RigidConnectorStiffnessType",
    "RigidConnectorTiltStiffnessTypes",
    "RigidConnectorToothLocation",
    "RigidConnectorToothSpacingType",
    "RigidConnectorTypes",
    "RollingRing",
    "RollingRingAssembly",
    "ShaftHubConnection",
    "SplineFitOptions",
    "SplineHalfManufacturingError",
    "SplineLeadRelief",
    "SplinePitchErrorInputType",
    "SplinePitchErrorOptions",
    "SpringDamper",
    "SpringDamperHalf",
    "Synchroniser",
    "SynchroniserCone",
    "SynchroniserHalf",
    "SynchroniserPart",
    "SynchroniserSleeve",
    "TorqueConverter",
    "TorqueConverterPump",
    "TorqueConverterSpeedRatio",
    "TorqueConverterTurbine",
)
