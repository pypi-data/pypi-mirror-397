"""ElectricMachineStatorFELink"""

from __future__ import annotations

from typing import TYPE_CHECKING, ClassVar

from mastapy._private._internal.dataclasses import extended_dataclass
from mastapy._private._internal.exception_bridge import exception_bridge
from mastapy._private._internal.exceptions import CastException
from mastapy._private._internal.python_net import (
    python_net_import,
    pythonnet_property_get,
    pythonnet_property_get_with_method,
    pythonnet_property_set,
    pythonnet_property_set_with_method,
)
from mastapy._private._internal.type_enforcement import enforce_parameter_types

from mastapy._private._internal import constructor, utility
from mastapy._private.system_model.fe.links import _2694

_DATABASE_WITH_SELECTED_ITEM = python_net_import(
    "SMT.MastaAPI.UtilityGUI.Databases", "DatabaseWithSelectedItem"
)
_ELECTRIC_MACHINE_STATOR_FE_LINK = python_net_import(
    "SMT.MastaAPI.SystemModel.FE.Links", "ElectricMachineStatorFELink"
)

if TYPE_CHECKING:
    from typing import Any, Type, TypeVar

    from mastapy._private.system_model.fe import _2634
    from mastapy._private.system_model.fe.links import _2686

    Self = TypeVar("Self", bound="ElectricMachineStatorFELink")
    CastSelf = TypeVar(
        "CastSelf",
        bound="ElectricMachineStatorFELink._Cast_ElectricMachineStatorFELink",
    )


__docformat__ = "restructuredtext en"
__all__ = ("ElectricMachineStatorFELink",)


@extended_dataclass(frozen=True, slots=True, weakref_slot=True)
class _Cast_ElectricMachineStatorFELink:
    """Special nested class for casting ElectricMachineStatorFELink to subclasses."""

    __parent__: "ElectricMachineStatorFELink"

    @property
    def multi_node_fe_link(self: "CastSelf") -> "_2694.MultiNodeFELink":
        return self.__parent__._cast(_2694.MultiNodeFELink)

    @property
    def fe_link(self: "CastSelf") -> "_2686.FELink":
        from mastapy._private.system_model.fe.links import _2686

        return self.__parent__._cast(_2686.FELink)

    @property
    def electric_machine_stator_fe_link(
        self: "CastSelf",
    ) -> "ElectricMachineStatorFELink":
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
class ElectricMachineStatorFELink(_2694.MultiNodeFELink):
    """ElectricMachineStatorFELink

    This is a mastapy class.
    """

    TYPE: ClassVar["Type"] = _ELECTRIC_MACHINE_STATOR_FE_LINK

    wrapped: "Any"

    def __post_init__(self: "Self") -> None:
        """Override of the post initialisation magic method."""
        if not hasattr(self.wrapped, "reference_count"):
            self.wrapped.reference_count = 0

        self.wrapped.reference_count += 1

    @property
    @exception_bridge
    def tamais_electric_machine_database_item_selector(self: "Self") -> "str":
        """str"""
        temp = pythonnet_property_get_with_method(
            self.wrapped,
            "TamaisElectricMachineDatabaseItemSelector",
            "SelectedItemName",
        )

        if temp is None:
            return ""

        return temp

    @tamais_electric_machine_database_item_selector.setter
    @exception_bridge
    @enforce_parameter_types
    def tamais_electric_machine_database_item_selector(
        self: "Self", value: "str"
    ) -> None:
        pythonnet_property_set_with_method(
            self.wrapped,
            "TamaisElectricMachineDatabaseItemSelector",
            "SetSelectedItem",
            str(value) if value is not None else "",
        )

    @property
    @exception_bridge
    def use_design_tamais_electric_machine(self: "Self") -> "bool":
        """bool"""
        temp = pythonnet_property_get(self.wrapped, "UseDesignTamaisElectricMachine")

        if temp is None:
            return False

        return temp

    @use_design_tamais_electric_machine.setter
    @exception_bridge
    @enforce_parameter_types
    def use_design_tamais_electric_machine(self: "Self", value: "bool") -> None:
        pythonnet_property_set(
            self.wrapped,
            "UseDesignTamaisElectricMachine",
            bool(value) if value is not None else False,
        )

    @property
    @exception_bridge
    def electric_machine_dynamic_load_data(
        self: "Self",
    ) -> "_2634.ElectricMachineDynamicLoadData":
        """mastapy.system_model.fe.ElectricMachineDynamicLoadData

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "ElectricMachineDynamicLoadData")

        if temp is None:
            return None

        type_ = temp.GetType()
        return constructor.new(type_.Namespace, type_.Name)(temp)

    @property
    def cast_to(self: "Self") -> "_Cast_ElectricMachineStatorFELink":
        """Cast to another type.

        Returns:
            _Cast_ElectricMachineStatorFELink
        """
        return _Cast_ElectricMachineStatorFELink(self)
