"""Subpackage."""

from typing import TYPE_CHECKING as __tc

if __tc:
    from mastapy._private.system_model.part_model.gears.supercharger_rotor_set._2837 import (
        BoostPressureInputOptions,
    )
    from mastapy._private.system_model.part_model.gears.supercharger_rotor_set._2838 import (
        InputPowerInputOptions,
    )
    from mastapy._private.system_model.part_model.gears.supercharger_rotor_set._2839 import (
        PressureRatioInputOptions,
    )
    from mastapy._private.system_model.part_model.gears.supercharger_rotor_set._2840 import (
        RotorSetDataInputFileOptions,
    )
    from mastapy._private.system_model.part_model.gears.supercharger_rotor_set._2841 import (
        RotorSetMeasuredPoint,
    )
    from mastapy._private.system_model.part_model.gears.supercharger_rotor_set._2842 import (
        RotorSpeedInputOptions,
    )
    from mastapy._private.system_model.part_model.gears.supercharger_rotor_set._2843 import (
        SuperchargerMap,
    )
    from mastapy._private.system_model.part_model.gears.supercharger_rotor_set._2844 import (
        SuperchargerMaps,
    )
    from mastapy._private.system_model.part_model.gears.supercharger_rotor_set._2845 import (
        SuperchargerRotorSet,
    )
    from mastapy._private.system_model.part_model.gears.supercharger_rotor_set._2846 import (
        SuperchargerRotorSetDatabase,
    )
    from mastapy._private.system_model.part_model.gears.supercharger_rotor_set._2847 import (
        YVariableForImportedData,
    )
else:
    import sys as __sys

    from lazy_imports import LazyImporter as __LazyImporter

    __import_structure = {
        "_private.system_model.part_model.gears.supercharger_rotor_set._2837": [
            "BoostPressureInputOptions"
        ],
        "_private.system_model.part_model.gears.supercharger_rotor_set._2838": [
            "InputPowerInputOptions"
        ],
        "_private.system_model.part_model.gears.supercharger_rotor_set._2839": [
            "PressureRatioInputOptions"
        ],
        "_private.system_model.part_model.gears.supercharger_rotor_set._2840": [
            "RotorSetDataInputFileOptions"
        ],
        "_private.system_model.part_model.gears.supercharger_rotor_set._2841": [
            "RotorSetMeasuredPoint"
        ],
        "_private.system_model.part_model.gears.supercharger_rotor_set._2842": [
            "RotorSpeedInputOptions"
        ],
        "_private.system_model.part_model.gears.supercharger_rotor_set._2843": [
            "SuperchargerMap"
        ],
        "_private.system_model.part_model.gears.supercharger_rotor_set._2844": [
            "SuperchargerMaps"
        ],
        "_private.system_model.part_model.gears.supercharger_rotor_set._2845": [
            "SuperchargerRotorSet"
        ],
        "_private.system_model.part_model.gears.supercharger_rotor_set._2846": [
            "SuperchargerRotorSetDatabase"
        ],
        "_private.system_model.part_model.gears.supercharger_rotor_set._2847": [
            "YVariableForImportedData"
        ],
    }

    __sys.modules[__name__] = __LazyImporter(
        "mastapy",
        globals()["__file__"],
        __import_structure,
    )

__all__ = (
    "BoostPressureInputOptions",
    "InputPowerInputOptions",
    "PressureRatioInputOptions",
    "RotorSetDataInputFileOptions",
    "RotorSetMeasuredPoint",
    "RotorSpeedInputOptions",
    "SuperchargerMap",
    "SuperchargerMaps",
    "SuperchargerRotorSet",
    "SuperchargerRotorSetDatabase",
    "YVariableForImportedData",
)
