"""Subpackage."""

from typing import TYPE_CHECKING as __tc

if __tc:
    from mastapy._private.system_model.part_model.import_from_cad._2772 import (
        AbstractShaftFromCAD,
    )
    from mastapy._private.system_model.part_model.import_from_cad._2773 import (
        ClutchFromCAD,
    )
    from mastapy._private.system_model.part_model.import_from_cad._2774 import (
        ComponentFromCAD,
    )
    from mastapy._private.system_model.part_model.import_from_cad._2775 import (
        ComponentFromCADBase,
    )
    from mastapy._private.system_model.part_model.import_from_cad._2776 import (
        ConceptBearingFromCAD,
    )
    from mastapy._private.system_model.part_model.import_from_cad._2777 import (
        ConnectorFromCAD,
    )
    from mastapy._private.system_model.part_model.import_from_cad._2778 import (
        CylindricalGearFromCAD,
    )
    from mastapy._private.system_model.part_model.import_from_cad._2779 import (
        CylindricalGearInPlanetarySetFromCAD,
    )
    from mastapy._private.system_model.part_model.import_from_cad._2780 import (
        CylindricalPlanetGearFromCAD,
    )
    from mastapy._private.system_model.part_model.import_from_cad._2781 import (
        CylindricalRingGearFromCAD,
    )
    from mastapy._private.system_model.part_model.import_from_cad._2782 import (
        CylindricalSunGearFromCAD,
    )
    from mastapy._private.system_model.part_model.import_from_cad._2783 import (
        HousedOrMounted,
    )
    from mastapy._private.system_model.part_model.import_from_cad._2784 import (
        MountableComponentFromCAD,
    )
    from mastapy._private.system_model.part_model.import_from_cad._2785 import (
        PlanetShaftFromCAD,
    )
    from mastapy._private.system_model.part_model.import_from_cad._2786 import (
        PulleyFromCAD,
    )
    from mastapy._private.system_model.part_model.import_from_cad._2787 import (
        RigidConnectorFromCAD,
    )
    from mastapy._private.system_model.part_model.import_from_cad._2788 import (
        RollingBearingFromCAD,
    )
    from mastapy._private.system_model.part_model.import_from_cad._2789 import (
        ShaftFromCAD,
    )
    from mastapy._private.system_model.part_model.import_from_cad._2790 import (
        ShaftFromCADAuto,
    )
else:
    import sys as __sys

    from lazy_imports import LazyImporter as __LazyImporter

    __import_structure = {
        "_private.system_model.part_model.import_from_cad._2772": [
            "AbstractShaftFromCAD"
        ],
        "_private.system_model.part_model.import_from_cad._2773": ["ClutchFromCAD"],
        "_private.system_model.part_model.import_from_cad._2774": ["ComponentFromCAD"],
        "_private.system_model.part_model.import_from_cad._2775": [
            "ComponentFromCADBase"
        ],
        "_private.system_model.part_model.import_from_cad._2776": [
            "ConceptBearingFromCAD"
        ],
        "_private.system_model.part_model.import_from_cad._2777": ["ConnectorFromCAD"],
        "_private.system_model.part_model.import_from_cad._2778": [
            "CylindricalGearFromCAD"
        ],
        "_private.system_model.part_model.import_from_cad._2779": [
            "CylindricalGearInPlanetarySetFromCAD"
        ],
        "_private.system_model.part_model.import_from_cad._2780": [
            "CylindricalPlanetGearFromCAD"
        ],
        "_private.system_model.part_model.import_from_cad._2781": [
            "CylindricalRingGearFromCAD"
        ],
        "_private.system_model.part_model.import_from_cad._2782": [
            "CylindricalSunGearFromCAD"
        ],
        "_private.system_model.part_model.import_from_cad._2783": ["HousedOrMounted"],
        "_private.system_model.part_model.import_from_cad._2784": [
            "MountableComponentFromCAD"
        ],
        "_private.system_model.part_model.import_from_cad._2785": [
            "PlanetShaftFromCAD"
        ],
        "_private.system_model.part_model.import_from_cad._2786": ["PulleyFromCAD"],
        "_private.system_model.part_model.import_from_cad._2787": [
            "RigidConnectorFromCAD"
        ],
        "_private.system_model.part_model.import_from_cad._2788": [
            "RollingBearingFromCAD"
        ],
        "_private.system_model.part_model.import_from_cad._2789": ["ShaftFromCAD"],
        "_private.system_model.part_model.import_from_cad._2790": ["ShaftFromCADAuto"],
    }

    __sys.modules[__name__] = __LazyImporter(
        "mastapy",
        globals()["__file__"],
        __import_structure,
    )

__all__ = (
    "AbstractShaftFromCAD",
    "ClutchFromCAD",
    "ComponentFromCAD",
    "ComponentFromCADBase",
    "ConceptBearingFromCAD",
    "ConnectorFromCAD",
    "CylindricalGearFromCAD",
    "CylindricalGearInPlanetarySetFromCAD",
    "CylindricalPlanetGearFromCAD",
    "CylindricalRingGearFromCAD",
    "CylindricalSunGearFromCAD",
    "HousedOrMounted",
    "MountableComponentFromCAD",
    "PlanetShaftFromCAD",
    "PulleyFromCAD",
    "RigidConnectorFromCAD",
    "RollingBearingFromCAD",
    "ShaftFromCAD",
    "ShaftFromCADAuto",
)
