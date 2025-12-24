"""Subpackage."""

from typing import TYPE_CHECKING as __tc

if __tc:
    from mastapy._private.gears.gear_designs._1066 import (
        BevelHypoidGearDesignSettingsDatabase,
    )
    from mastapy._private.gears.gear_designs._1067 import (
        BevelHypoidGearDesignSettingsItem,
    )
    from mastapy._private.gears.gear_designs._1068 import (
        BevelHypoidGearRatingSettingsDatabase,
    )
    from mastapy._private.gears.gear_designs._1069 import (
        BevelHypoidGearRatingSettingsItem,
    )
    from mastapy._private.gears.gear_designs._1070 import DesignConstraint
    from mastapy._private.gears.gear_designs._1071 import (
        DesignConstraintCollectionDatabase,
    )
    from mastapy._private.gears.gear_designs._1072 import DesignConstraintsCollection
    from mastapy._private.gears.gear_designs._1073 import GearDesign
    from mastapy._private.gears.gear_designs._1074 import GearDesignComponent
    from mastapy._private.gears.gear_designs._1075 import GearMeshDesign
    from mastapy._private.gears.gear_designs._1076 import GearSetDesign
    from mastapy._private.gears.gear_designs._1077 import (
        SelectedDesignConstraintsCollection,
    )
else:
    import sys as __sys

    from lazy_imports import LazyImporter as __LazyImporter

    __import_structure = {
        "_private.gears.gear_designs._1066": ["BevelHypoidGearDesignSettingsDatabase"],
        "_private.gears.gear_designs._1067": ["BevelHypoidGearDesignSettingsItem"],
        "_private.gears.gear_designs._1068": ["BevelHypoidGearRatingSettingsDatabase"],
        "_private.gears.gear_designs._1069": ["BevelHypoidGearRatingSettingsItem"],
        "_private.gears.gear_designs._1070": ["DesignConstraint"],
        "_private.gears.gear_designs._1071": ["DesignConstraintCollectionDatabase"],
        "_private.gears.gear_designs._1072": ["DesignConstraintsCollection"],
        "_private.gears.gear_designs._1073": ["GearDesign"],
        "_private.gears.gear_designs._1074": ["GearDesignComponent"],
        "_private.gears.gear_designs._1075": ["GearMeshDesign"],
        "_private.gears.gear_designs._1076": ["GearSetDesign"],
        "_private.gears.gear_designs._1077": ["SelectedDesignConstraintsCollection"],
    }

    __sys.modules[__name__] = __LazyImporter(
        "mastapy",
        globals()["__file__"],
        __import_structure,
    )

__all__ = (
    "BevelHypoidGearDesignSettingsDatabase",
    "BevelHypoidGearDesignSettingsItem",
    "BevelHypoidGearRatingSettingsDatabase",
    "BevelHypoidGearRatingSettingsItem",
    "DesignConstraint",
    "DesignConstraintCollectionDatabase",
    "DesignConstraintsCollection",
    "GearDesign",
    "GearDesignComponent",
    "GearMeshDesign",
    "GearSetDesign",
    "SelectedDesignConstraintsCollection",
)
