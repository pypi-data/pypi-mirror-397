"""Subpackage."""

from typing import TYPE_CHECKING as __tc

if __tc:
    from mastapy._private.gears.manufacturing.bevel.basic_machine_settings._947 import (
        BasicConicalGearMachineSettings,
    )
    from mastapy._private.gears.manufacturing.bevel.basic_machine_settings._948 import (
        BasicConicalGearMachineSettingsFormate,
    )
    from mastapy._private.gears.manufacturing.bevel.basic_machine_settings._949 import (
        BasicConicalGearMachineSettingsGenerated,
    )
    from mastapy._private.gears.manufacturing.bevel.basic_machine_settings._950 import (
        CradleStyleConicalMachineSettingsGenerated,
    )
else:
    import sys as __sys

    from lazy_imports import LazyImporter as __LazyImporter

    __import_structure = {
        "_private.gears.manufacturing.bevel.basic_machine_settings._947": [
            "BasicConicalGearMachineSettings"
        ],
        "_private.gears.manufacturing.bevel.basic_machine_settings._948": [
            "BasicConicalGearMachineSettingsFormate"
        ],
        "_private.gears.manufacturing.bevel.basic_machine_settings._949": [
            "BasicConicalGearMachineSettingsGenerated"
        ],
        "_private.gears.manufacturing.bevel.basic_machine_settings._950": [
            "CradleStyleConicalMachineSettingsGenerated"
        ],
    }

    __sys.modules[__name__] = __LazyImporter(
        "mastapy",
        globals()["__file__"],
        __import_structure,
    )

__all__ = (
    "BasicConicalGearMachineSettings",
    "BasicConicalGearMachineSettingsFormate",
    "BasicConicalGearMachineSettingsGenerated",
    "CradleStyleConicalMachineSettingsGenerated",
)
