"""Subpackage."""

from typing import TYPE_CHECKING as __tc

if __tc:
    from mastapy._private.electric_machines.harmonic_load_data._1589 import (
        ElectricMachineHarmonicLoadDataBase,
    )
    from mastapy._private.electric_machines.harmonic_load_data._1590 import (
        ForceDisplayOption,
    )
    from mastapy._private.electric_machines.harmonic_load_data._1591 import (
        HarmonicLoadDataBase,
    )
    from mastapy._private.electric_machines.harmonic_load_data._1592 import (
        HarmonicLoadDataControlExcitationOptionBase,
    )
    from mastapy._private.electric_machines.harmonic_load_data._1593 import (
        HarmonicLoadDataType,
    )
    from mastapy._private.electric_machines.harmonic_load_data._1594 import (
        SimpleElectricMachineTooth,
    )
    from mastapy._private.electric_machines.harmonic_load_data._1595 import (
        SpeedDependentHarmonicLoadData,
    )
    from mastapy._private.electric_machines.harmonic_load_data._1596 import (
        StatorToothInterpolator,
    )
    from mastapy._private.electric_machines.harmonic_load_data._1597 import (
        StatorToothLoadInterpolator,
    )
    from mastapy._private.electric_machines.harmonic_load_data._1598 import (
        StatorToothMomentInterpolator,
    )
else:
    import sys as __sys

    from lazy_imports import LazyImporter as __LazyImporter

    __import_structure = {
        "_private.electric_machines.harmonic_load_data._1589": [
            "ElectricMachineHarmonicLoadDataBase"
        ],
        "_private.electric_machines.harmonic_load_data._1590": ["ForceDisplayOption"],
        "_private.electric_machines.harmonic_load_data._1591": ["HarmonicLoadDataBase"],
        "_private.electric_machines.harmonic_load_data._1592": [
            "HarmonicLoadDataControlExcitationOptionBase"
        ],
        "_private.electric_machines.harmonic_load_data._1593": ["HarmonicLoadDataType"],
        "_private.electric_machines.harmonic_load_data._1594": [
            "SimpleElectricMachineTooth"
        ],
        "_private.electric_machines.harmonic_load_data._1595": [
            "SpeedDependentHarmonicLoadData"
        ],
        "_private.electric_machines.harmonic_load_data._1596": [
            "StatorToothInterpolator"
        ],
        "_private.electric_machines.harmonic_load_data._1597": [
            "StatorToothLoadInterpolator"
        ],
        "_private.electric_machines.harmonic_load_data._1598": [
            "StatorToothMomentInterpolator"
        ],
    }

    __sys.modules[__name__] = __LazyImporter(
        "mastapy",
        globals()["__file__"],
        __import_structure,
    )

__all__ = (
    "ElectricMachineHarmonicLoadDataBase",
    "ForceDisplayOption",
    "HarmonicLoadDataBase",
    "HarmonicLoadDataControlExcitationOptionBase",
    "HarmonicLoadDataType",
    "SimpleElectricMachineTooth",
    "SpeedDependentHarmonicLoadData",
    "StatorToothInterpolator",
    "StatorToothLoadInterpolator",
    "StatorToothMomentInterpolator",
)
