"""GearMeshOilInjectionDirection"""

from __future__ import annotations

from enum import Enum
from typing import TYPE_CHECKING

from mastapy._private._internal.python_net import python_net_import

_GEAR_MESH_OIL_INJECTION_DIRECTION = python_net_import(
    "SMT.MastaAPI.Gears", "GearMeshOilInjectionDirection"
)

if TYPE_CHECKING:
    from typing import Any, Type, TypeVar

    Self = TypeVar("Self", bound="GearMeshOilInjectionDirection")
    CastSelf = TypeVar(
        "CastSelf",
        bound="GearMeshOilInjectionDirection._Cast_GearMeshOilInjectionDirection",
    )


__docformat__ = "restructuredtext en"
__all__ = ("GearMeshOilInjectionDirection",)


class GearMeshOilInjectionDirection(Enum):
    """GearMeshOilInjectionDirection

    This is a mastapy class.

    Note:
        This class is an Enum.
    """

    @classmethod
    def type_(cls) -> "Type":
        return _GEAR_MESH_OIL_INJECTION_DIRECTION

    INTO_POINT_OF_ENGAGEMENT = 0
    INTO_POINT_OF_DISENGAGEMENT = 1


def __enum_setattr(self: "Self", attr: str, value: "Any") -> None:
    raise AttributeError("Cannot set the attributes of an Enum.") from None


def __enum_delattr(self: "Self", attr: str) -> None:
    raise AttributeError("Cannot delete the attributes of an Enum.") from None


GearMeshOilInjectionDirection.__setattr__ = __enum_setattr
GearMeshOilInjectionDirection.__delattr__ = __enum_delattr
