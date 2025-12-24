"""OilSealType"""

from __future__ import annotations

from enum import Enum
from typing import TYPE_CHECKING

from mastapy._private._internal.python_net import python_net_import

_OIL_SEAL_TYPE = python_net_import("SMT.MastaAPI.Materials.Efficiency", "OilSealType")

if TYPE_CHECKING:
    from typing import Any, Type, TypeVar

    Self = TypeVar("Self", bound="OilSealType")
    CastSelf = TypeVar("CastSelf", bound="OilSealType._Cast_OilSealType")


__docformat__ = "restructuredtext en"
__all__ = ("OilSealType",)


class OilSealType(Enum):
    """OilSealType

    This is a mastapy class.

    Note:
        This class is an Enum.
    """

    @classmethod
    def type_(cls) -> "Type":
        return _OIL_SEAL_TYPE

    INPUT_SEAL = 0
    AXLE_SEAL = 1
    PRESSURE_SEAL = 2


def __enum_setattr(self: "Self", attr: str, value: "Any") -> None:
    raise AttributeError("Cannot set the attributes of an Enum.") from None


def __enum_delattr(self: "Self", attr: str) -> None:
    raise AttributeError("Cannot delete the attributes of an Enum.") from None


OilSealType.__setattr__ = __enum_setattr
OilSealType.__delattr__ = __enum_delattr
