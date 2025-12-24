"""SpeedDependentHarmonicLoadData"""

from __future__ import annotations

from typing import TYPE_CHECKING, ClassVar

from mastapy._private._internal.dataclasses import extended_dataclass
from mastapy._private._internal.exception_bridge import exception_bridge
from mastapy._private._internal.exceptions import CastException
from mastapy._private._internal.list_with_selected_item import (
    promote_to_list_with_selected_item,
)
from mastapy._private._internal.python_net import (
    python_net_import,
    pythonnet_property_get,
    pythonnet_property_set,
)
from mastapy._private._internal.sentinels import ListWithSelectedItem_None
from mastapy._private._internal.type_enforcement import enforce_parameter_types

from mastapy._private._internal import constructor, conversion, utility
from mastapy._private._internal.implicit import list_with_selected_item
from mastapy._private.electric_machines.harmonic_load_data import _1591

_SPEED_DEPENDENT_HARMONIC_LOAD_DATA = python_net_import(
    "SMT.MastaAPI.ElectricMachines.HarmonicLoadData", "SpeedDependentHarmonicLoadData"
)

if TYPE_CHECKING:
    from typing import Any, Type, TypeVar

    from mastapy._private.electric_machines.harmonic_load_data import _1589
    from mastapy._private.electric_machines.results import _1532
    from mastapy._private.system_model.analyses_and_results.static_loads import (
        _7792,
        _7793,
        _7794,
        _7795,
        _7796,
        _7797,
        _7798,
        _7860,
        _7905,
    )

    Self = TypeVar("Self", bound="SpeedDependentHarmonicLoadData")
    CastSelf = TypeVar(
        "CastSelf",
        bound="SpeedDependentHarmonicLoadData._Cast_SpeedDependentHarmonicLoadData",
    )


__docformat__ = "restructuredtext en"
__all__ = ("SpeedDependentHarmonicLoadData",)


@extended_dataclass(frozen=True, slots=True, weakref_slot=True)
class _Cast_SpeedDependentHarmonicLoadData:
    """Special nested class for casting SpeedDependentHarmonicLoadData to subclasses."""

    __parent__: "SpeedDependentHarmonicLoadData"

    @property
    def harmonic_load_data_base(self: "CastSelf") -> "_1591.HarmonicLoadDataBase":
        return self.__parent__._cast(_1591.HarmonicLoadDataBase)

    @property
    def dynamic_force_results(self: "CastSelf") -> "_1532.DynamicForceResults":
        from mastapy._private.electric_machines.results import _1532

        return self.__parent__._cast(_1532.DynamicForceResults)

    @property
    def electric_machine_harmonic_load_data_base(
        self: "CastSelf",
    ) -> "_1589.ElectricMachineHarmonicLoadDataBase":
        from mastapy._private.electric_machines.harmonic_load_data import _1589

        return self.__parent__._cast(_1589.ElectricMachineHarmonicLoadDataBase)

    @property
    def electric_machine_harmonic_load_data(
        self: "CastSelf",
    ) -> "_7792.ElectricMachineHarmonicLoadData":
        from mastapy._private.system_model.analyses_and_results.static_loads import (
            _7792,
        )

        return self.__parent__._cast(_7792.ElectricMachineHarmonicLoadData)

    @property
    def electric_machine_harmonic_load_data_from_excel(
        self: "CastSelf",
    ) -> "_7793.ElectricMachineHarmonicLoadDataFromExcel":
        from mastapy._private.system_model.analyses_and_results.static_loads import (
            _7793,
        )

        return self.__parent__._cast(_7793.ElectricMachineHarmonicLoadDataFromExcel)

    @property
    def electric_machine_harmonic_load_data_from_flux(
        self: "CastSelf",
    ) -> "_7794.ElectricMachineHarmonicLoadDataFromFlux":
        from mastapy._private.system_model.analyses_and_results.static_loads import (
            _7794,
        )

        return self.__parent__._cast(_7794.ElectricMachineHarmonicLoadDataFromFlux)

    @property
    def electric_machine_harmonic_load_data_from_jmag(
        self: "CastSelf",
    ) -> "_7795.ElectricMachineHarmonicLoadDataFromJMAG":
        from mastapy._private.system_model.analyses_and_results.static_loads import (
            _7795,
        )

        return self.__parent__._cast(_7795.ElectricMachineHarmonicLoadDataFromJMAG)

    @property
    def electric_machine_harmonic_load_data_from_masta(
        self: "CastSelf",
    ) -> "_7796.ElectricMachineHarmonicLoadDataFromMASTA":
        from mastapy._private.system_model.analyses_and_results.static_loads import (
            _7796,
        )

        return self.__parent__._cast(_7796.ElectricMachineHarmonicLoadDataFromMASTA)

    @property
    def electric_machine_harmonic_load_data_from_motor_cad(
        self: "CastSelf",
    ) -> "_7797.ElectricMachineHarmonicLoadDataFromMotorCAD":
        from mastapy._private.system_model.analyses_and_results.static_loads import (
            _7797,
        )

        return self.__parent__._cast(_7797.ElectricMachineHarmonicLoadDataFromMotorCAD)

    @property
    def electric_machine_harmonic_load_data_from_motor_packages(
        self: "CastSelf",
    ) -> "_7798.ElectricMachineHarmonicLoadDataFromMotorPackages":
        from mastapy._private.system_model.analyses_and_results.static_loads import (
            _7798,
        )

        return self.__parent__._cast(
            _7798.ElectricMachineHarmonicLoadDataFromMotorPackages
        )

    @property
    def point_load_harmonic_load_data(
        self: "CastSelf",
    ) -> "_7860.PointLoadHarmonicLoadData":
        from mastapy._private.system_model.analyses_and_results.static_loads import (
            _7860,
        )

        return self.__parent__._cast(_7860.PointLoadHarmonicLoadData)

    @property
    def unbalanced_mass_harmonic_load_data(
        self: "CastSelf",
    ) -> "_7905.UnbalancedMassHarmonicLoadData":
        from mastapy._private.system_model.analyses_and_results.static_loads import (
            _7905,
        )

        return self.__parent__._cast(_7905.UnbalancedMassHarmonicLoadData)

    @property
    def speed_dependent_harmonic_load_data(
        self: "CastSelf",
    ) -> "SpeedDependentHarmonicLoadData":
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
class SpeedDependentHarmonicLoadData(_1591.HarmonicLoadDataBase):
    """SpeedDependentHarmonicLoadData

    This is a mastapy class.
    """

    TYPE: ClassVar["Type"] = _SPEED_DEPENDENT_HARMONIC_LOAD_DATA

    wrapped: "Any"

    def __post_init__(self: "Self") -> None:
        """Override of the post initialisation magic method."""
        if not hasattr(self.wrapped, "reference_count"):
            self.wrapped.reference_count = 0

        self.wrapped.reference_count += 1

    @property
    @exception_bridge
    def selected_speed(
        self: "Self",
    ) -> "list_with_selected_item.ListWithSelectedItem_float":
        """ListWithSelectedItem[float]"""
        temp = pythonnet_property_get(self.wrapped, "SelectedSpeed")

        if temp is None:
            return 0.0

        selected_value = temp.SelectedValue

        if selected_value is None:
            return ListWithSelectedItem_None(temp)

        return constructor.new_from_mastapy(
            "mastapy._private._internal.implicit.list_with_selected_item",
            "ListWithSelectedItem_float",
        )(temp)

    @selected_speed.setter
    @exception_bridge
    @enforce_parameter_types
    def selected_speed(self: "Self", value: "float") -> None:
        generic_type = (
            list_with_selected_item.ListWithSelectedItem_float.implicit_type()
        )
        value = promote_to_list_with_selected_item(value)
        value = conversion.mp_to_pn_smt_list_with_selected_item(
            self, value, generic_type
        )
        pythonnet_property_set(self.wrapped, "SelectedSpeed", value)

    @property
    @exception_bridge
    def show_all_speeds(self: "Self") -> "bool":
        """bool"""
        temp = pythonnet_property_get(self.wrapped, "ShowAllSpeeds")

        if temp is None:
            return False

        return temp

    @show_all_speeds.setter
    @exception_bridge
    @enforce_parameter_types
    def show_all_speeds(self: "Self", value: "bool") -> None:
        pythonnet_property_set(
            self.wrapped, "ShowAllSpeeds", bool(value) if value is not None else False
        )

    @property
    def cast_to(self: "Self") -> "_Cast_SpeedDependentHarmonicLoadData":
        """Cast to another type.

        Returns:
            _Cast_SpeedDependentHarmonicLoadData
        """
        return _Cast_SpeedDependentHarmonicLoadData(self)
