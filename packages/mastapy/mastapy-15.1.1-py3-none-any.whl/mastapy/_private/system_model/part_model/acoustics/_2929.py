"""PlaneShape"""

from __future__ import annotations

from enum import Enum
from typing import TYPE_CHECKING

from mastapy._private._internal.python_net import python_net_import

_PLANE_SHAPE = python_net_import(
    "SMT.MastaAPI.SystemModel.PartModel.Acoustics", "PlaneShape"
)

if TYPE_CHECKING:
    from typing import Any, Type, TypeVar

    Self = TypeVar("Self", bound="PlaneShape")
    CastSelf = TypeVar("CastSelf", bound="PlaneShape._Cast_PlaneShape")


__docformat__ = "restructuredtext en"
__all__ = ("PlaneShape",)


class PlaneShape(Enum):
    """PlaneShape

    This is a mastapy class.

    Note:
        This class is an Enum.
    """

    @classmethod
    def type_(cls) -> "Type":
        return _PLANE_SHAPE

    SQUARE = 0
    CIRCLE = 1


def __enum_setattr(self: "Self", attr: str, value: "Any") -> None:
    raise AttributeError("Cannot set the attributes of an Enum.") from None


def __enum_delattr(self: "Self", attr: str) -> None:
    raise AttributeError("Cannot delete the attributes of an Enum.") from None


PlaneShape.__setattr__ = __enum_setattr
PlaneShape.__delattr__ = __enum_delattr
