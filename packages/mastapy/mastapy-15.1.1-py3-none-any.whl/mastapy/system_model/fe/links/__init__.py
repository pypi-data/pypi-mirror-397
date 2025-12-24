"""Subpackage."""

from typing import TYPE_CHECKING as __tc

if __tc:
    from mastapy._private.system_model.fe.links._2686 import FELink
    from mastapy._private.system_model.fe.links._2687 import ElectricMachineStatorFELink
    from mastapy._private.system_model.fe.links._2688 import FELinkWithSelection
    from mastapy._private.system_model.fe.links._2689 import (
        FlexibleInterpolationDefinitionSettings,
    )
    from mastapy._private.system_model.fe.links._2690 import GearMeshFELink
    from mastapy._private.system_model.fe.links._2691 import (
        GearWithDuplicatedMeshesFELink,
    )
    from mastapy._private.system_model.fe.links._2692 import MultiAngleConnectionFELink
    from mastapy._private.system_model.fe.links._2693 import MultiNodeConnectorFELink
    from mastapy._private.system_model.fe.links._2694 import MultiNodeFELink
    from mastapy._private.system_model.fe.links._2695 import (
        PlanetaryConnectorMultiNodeFELink,
    )
    from mastapy._private.system_model.fe.links._2696 import PlanetBasedFELink
    from mastapy._private.system_model.fe.links._2697 import PlanetCarrierFELink
    from mastapy._private.system_model.fe.links._2698 import PointLoadFELink
    from mastapy._private.system_model.fe.links._2699 import RollingRingConnectionFELink
    from mastapy._private.system_model.fe.links._2700 import ShaftHubConnectionFELink
    from mastapy._private.system_model.fe.links._2701 import SingleNodeFELink
else:
    import sys as __sys

    from lazy_imports import LazyImporter as __LazyImporter

    __import_structure = {
        "_private.system_model.fe.links._2686": ["FELink"],
        "_private.system_model.fe.links._2687": ["ElectricMachineStatorFELink"],
        "_private.system_model.fe.links._2688": ["FELinkWithSelection"],
        "_private.system_model.fe.links._2689": [
            "FlexibleInterpolationDefinitionSettings"
        ],
        "_private.system_model.fe.links._2690": ["GearMeshFELink"],
        "_private.system_model.fe.links._2691": ["GearWithDuplicatedMeshesFELink"],
        "_private.system_model.fe.links._2692": ["MultiAngleConnectionFELink"],
        "_private.system_model.fe.links._2693": ["MultiNodeConnectorFELink"],
        "_private.system_model.fe.links._2694": ["MultiNodeFELink"],
        "_private.system_model.fe.links._2695": ["PlanetaryConnectorMultiNodeFELink"],
        "_private.system_model.fe.links._2696": ["PlanetBasedFELink"],
        "_private.system_model.fe.links._2697": ["PlanetCarrierFELink"],
        "_private.system_model.fe.links._2698": ["PointLoadFELink"],
        "_private.system_model.fe.links._2699": ["RollingRingConnectionFELink"],
        "_private.system_model.fe.links._2700": ["ShaftHubConnectionFELink"],
        "_private.system_model.fe.links._2701": ["SingleNodeFELink"],
    }

    __sys.modules[__name__] = __LazyImporter(
        "mastapy",
        globals()["__file__"],
        __import_structure,
    )

__all__ = (
    "FELink",
    "ElectricMachineStatorFELink",
    "FELinkWithSelection",
    "FlexibleInterpolationDefinitionSettings",
    "GearMeshFELink",
    "GearWithDuplicatedMeshesFELink",
    "MultiAngleConnectionFELink",
    "MultiNodeConnectorFELink",
    "MultiNodeFELink",
    "PlanetaryConnectorMultiNodeFELink",
    "PlanetBasedFELink",
    "PlanetCarrierFELink",
    "PointLoadFELink",
    "RollingRingConnectionFELink",
    "ShaftHubConnectionFELink",
    "SingleNodeFELink",
)
