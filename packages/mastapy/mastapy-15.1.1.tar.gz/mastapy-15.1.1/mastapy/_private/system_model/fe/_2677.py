"""SelectableNodeAtAngle"""

from __future__ import annotations

from typing import TYPE_CHECKING, ClassVar

from mastapy._private._internal.dataclasses import extended_dataclass
from mastapy._private._internal.exceptions import CastException
from mastapy._private._internal.python_net import python_net_import

from mastapy._private import _0
from mastapy._private._internal import utility

_SELECTABLE_NODE_AT_ANGLE = python_net_import(
    "SMT.MastaAPI.SystemModel.FE", "SelectableNodeAtAngle"
)

if TYPE_CHECKING:
    from typing import Any, Type, TypeVar

    Self = TypeVar("Self", bound="SelectableNodeAtAngle")
    CastSelf = TypeVar(
        "CastSelf", bound="SelectableNodeAtAngle._Cast_SelectableNodeAtAngle"
    )


__docformat__ = "restructuredtext en"
__all__ = ("SelectableNodeAtAngle",)


@extended_dataclass(frozen=True, slots=True, weakref_slot=True)
class _Cast_SelectableNodeAtAngle:
    """Special nested class for casting SelectableNodeAtAngle to subclasses."""

    __parent__: "SelectableNodeAtAngle"

    @property
    def selectable_node_at_angle(self: "CastSelf") -> "SelectableNodeAtAngle":
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
class SelectableNodeAtAngle(_0.APIBase):
    """SelectableNodeAtAngle

    This is a mastapy class.
    """

    TYPE: ClassVar["Type"] = _SELECTABLE_NODE_AT_ANGLE

    wrapped: "Any"

    def __post_init__(self: "Self") -> None:
        """Override of the post initialisation magic method."""
        if not hasattr(self.wrapped, "reference_count"):
            self.wrapped.reference_count = 0

        self.wrapped.reference_count += 1

    @property
    def cast_to(self: "Self") -> "_Cast_SelectableNodeAtAngle":
        """Cast to another type.

        Returns:
            _Cast_SelectableNodeAtAngle
        """
        return _Cast_SelectableNodeAtAngle(self)
