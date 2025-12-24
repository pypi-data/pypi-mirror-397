"""NodesForPlanetInSocket"""

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

from mastapy._private import _0
from mastapy._private._internal import constructor, conversion, utility
from mastapy._private._internal.implicit import list_with_selected_item
from mastapy._private.system_model.fe import _2677

_NODES_FOR_PLANET_IN_SOCKET = python_net_import(
    "SMT.MastaAPI.SystemModel.FE", "NodesForPlanetInSocket"
)

if TYPE_CHECKING:
    from typing import Any, Type, TypeVar

    Self = TypeVar("Self", bound="NodesForPlanetInSocket")
    CastSelf = TypeVar(
        "CastSelf", bound="NodesForPlanetInSocket._Cast_NodesForPlanetInSocket"
    )


__docformat__ = "restructuredtext en"
__all__ = ("NodesForPlanetInSocket",)


@extended_dataclass(frozen=True, slots=True, weakref_slot=True)
class _Cast_NodesForPlanetInSocket:
    """Special nested class for casting NodesForPlanetInSocket to subclasses."""

    __parent__: "NodesForPlanetInSocket"

    @property
    def nodes_for_planet_in_socket(self: "CastSelf") -> "NodesForPlanetInSocket":
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
class NodesForPlanetInSocket(_0.APIBase):
    """NodesForPlanetInSocket

    This is a mastapy class.
    """

    TYPE: ClassVar["Type"] = _NODES_FOR_PLANET_IN_SOCKET

    wrapped: "Any"

    def __post_init__(self: "Self") -> None:
        """Override of the post initialisation magic method."""
        if not hasattr(self.wrapped, "reference_count"):
            self.wrapped.reference_count = 0

        self.wrapped.reference_count += 1

    @property
    @exception_bridge
    def name(self: "Self") -> "str":
        """str

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "Name")

        if temp is None:
            return ""

        return temp

    @property
    @exception_bridge
    def nodes_for_windup(
        self: "Self",
    ) -> "list_with_selected_item.ListWithSelectedItem_SelectableNodeAtAngle":
        """ListWithSelectedItem[mastapy.system_model.fe.SelectableNodeAtAngle]"""
        temp = pythonnet_property_get(self.wrapped, "NodesForWindup")

        if temp is None:
            return None

        selected_value = temp.SelectedValue

        if selected_value is None:
            return ListWithSelectedItem_None(temp)

        return constructor.new_from_mastapy(
            "mastapy._private._internal.implicit.list_with_selected_item",
            "ListWithSelectedItem_SelectableNodeAtAngle",
        )(temp)

    @nodes_for_windup.setter
    @exception_bridge
    @enforce_parameter_types
    def nodes_for_windup(self: "Self", value: "_2677.SelectableNodeAtAngle") -> None:
        generic_type = list_with_selected_item.ListWithSelectedItem_SelectableNodeAtAngle.implicit_type()
        value = promote_to_list_with_selected_item(value)
        value = conversion.mp_to_pn_smt_list_with_selected_item(
            self, value, generic_type
        )
        pythonnet_property_set(self.wrapped, "NodesForWindup", value)

    @property
    def cast_to(self: "Self") -> "_Cast_NodesForPlanetInSocket":
        """Cast to another type.

        Returns:
            _Cast_NodesForPlanetInSocket
        """
        return _Cast_NodesForPlanetInSocket(self)
