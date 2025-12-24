"""PerMachineSettings"""

from __future__ import annotations

from typing import TYPE_CHECKING, ClassVar

from mastapy._private._internal.dataclasses import extended_dataclass
from mastapy._private._internal.exception_bridge import exception_bridge
from mastapy._private._internal.exceptions import CastException
from mastapy._private._internal.python_net import (
    python_net_import,
    pythonnet_method_call,
)

from mastapy._private._internal import utility
from mastapy._private.utility import _1819

_PER_MACHINE_SETTINGS = python_net_import("SMT.MastaAPI.Utility", "PerMachineSettings")

if TYPE_CHECKING:
    from typing import Any, Type, TypeVar

    from mastapy._private.bearings import _2136
    from mastapy._private.gears.gear_designs.cylindrical import _1143
    from mastapy._private.gears.materials import _712
    from mastapy._private.nodal_analysis import _71
    from mastapy._private.nodal_analysis.geometry_modeller_link import _245
    from mastapy._private.system_model.part_model import _2719, _2745
    from mastapy._private.utility import _1820
    from mastapy._private.utility.cad_export import _2067
    from mastapy._private.utility.databases import _2059
    from mastapy._private.utility.scripting import _1966
    from mastapy._private.utility.units_and_measurements import _1830

    Self = TypeVar("Self", bound="PerMachineSettings")
    CastSelf = TypeVar("CastSelf", bound="PerMachineSettings._Cast_PerMachineSettings")


__docformat__ = "restructuredtext en"
__all__ = ("PerMachineSettings",)


@extended_dataclass(frozen=True, slots=True, weakref_slot=True)
class _Cast_PerMachineSettings:
    """Special nested class for casting PerMachineSettings to subclasses."""

    __parent__: "PerMachineSettings"

    @property
    def persistent_singleton(self: "CastSelf") -> "_1819.PersistentSingleton":
        return self.__parent__._cast(_1819.PersistentSingleton)

    @property
    def fe_user_settings(self: "CastSelf") -> "_71.FEUserSettings":
        from mastapy._private.nodal_analysis import _71

        return self.__parent__._cast(_71.FEUserSettings)

    @property
    def geometry_modeller_settings(self: "CastSelf") -> "_245.GeometryModellerSettings":
        from mastapy._private.nodal_analysis.geometry_modeller_link import _245

        return self.__parent__._cast(_245.GeometryModellerSettings)

    @property
    def gear_material_expert_system_factor_settings(
        self: "CastSelf",
    ) -> "_712.GearMaterialExpertSystemFactorSettings":
        from mastapy._private.gears.materials import _712

        return self.__parent__._cast(_712.GearMaterialExpertSystemFactorSettings)

    @property
    def cylindrical_gear_defaults(self: "CastSelf") -> "_1143.CylindricalGearDefaults":
        from mastapy._private.gears.gear_designs.cylindrical import _1143

        return self.__parent__._cast(_1143.CylindricalGearDefaults)

    @property
    def program_settings(self: "CastSelf") -> "_1820.ProgramSettings":
        from mastapy._private.utility import _1820

        return self.__parent__._cast(_1820.ProgramSettings)

    @property
    def measurement_settings(self: "CastSelf") -> "_1830.MeasurementSettings":
        from mastapy._private.utility.units_and_measurements import _1830

        return self.__parent__._cast(_1830.MeasurementSettings)

    @property
    def scripting_setup(self: "CastSelf") -> "_1966.ScriptingSetup":
        from mastapy._private.utility.scripting import _1966

        return self.__parent__._cast(_1966.ScriptingSetup)

    @property
    def database_settings(self: "CastSelf") -> "_2059.DatabaseSettings":
        from mastapy._private.utility.databases import _2059

        return self.__parent__._cast(_2059.DatabaseSettings)

    @property
    def cad_export_settings(self: "CastSelf") -> "_2067.CADExportSettings":
        from mastapy._private.utility.cad_export import _2067

        return self.__parent__._cast(_2067.CADExportSettings)

    @property
    def skf_settings(self: "CastSelf") -> "_2136.SKFSettings":
        from mastapy._private.bearings import _2136

        return self.__parent__._cast(_2136.SKFSettings)

    @property
    def default_export_settings(self: "CastSelf") -> "_2719.DefaultExportSettings":
        from mastapy._private.system_model.part_model import _2719

        return self.__parent__._cast(_2719.DefaultExportSettings)

    @property
    def planet_carrier_settings(self: "CastSelf") -> "_2745.PlanetCarrierSettings":
        from mastapy._private.system_model.part_model import _2745

        return self.__parent__._cast(_2745.PlanetCarrierSettings)

    @property
    def per_machine_settings(self: "CastSelf") -> "PerMachineSettings":
        return self.__parent__

    def __getattr__(self: "CastSelf", name: str) -> "Any":
        try:
            return self.__getattribute__(name)
        except AttributeError:
            class_name = utility.camel(name)
            raise CastException(
                f'Detected an invalid cast. Cannot cast to type "{class_name}"'
            ) from None


@extended_dataclass(frozen=True, slots=True, weakref_slot=True, eq=False)
class PerMachineSettings(_1819.PersistentSingleton):
    """PerMachineSettings

    This is a mastapy class.
    """

    TYPE: ClassVar["Type"] = _PER_MACHINE_SETTINGS

    wrapped: "Any"

    def __post_init__(self: "Self") -> None:
        """Override of the post initialisation magic method."""
        if not hasattr(self.wrapped, "reference_count"):
            self.wrapped.reference_count = 0

        self.wrapped.reference_count += 1

    @exception_bridge
    def reset_to_defaults(self: "Self") -> None:
        """Method does not return."""
        pythonnet_method_call(self.wrapped, "ResetToDefaults")

    @property
    def cast_to(self: "Self") -> "_Cast_PerMachineSettings":
        """Cast to another type.

        Returns:
            _Cast_PerMachineSettings
        """
        return _Cast_PerMachineSettings(self)
