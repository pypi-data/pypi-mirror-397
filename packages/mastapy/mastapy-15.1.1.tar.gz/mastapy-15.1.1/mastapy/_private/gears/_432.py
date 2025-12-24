"""DINToleranceStandard"""

from __future__ import annotations

from enum import Enum
from typing import TYPE_CHECKING

from mastapy._private._internal.python_net import python_net_import

_DIN_TOLERANCE_STANDARD = python_net_import(
    "SMT.MastaAPI.Gears", "DINToleranceStandard"
)

if TYPE_CHECKING:
    from typing import Any, Type, TypeVar

    Self = TypeVar("Self", bound="DINToleranceStandard")
    CastSelf = TypeVar(
        "CastSelf", bound="DINToleranceStandard._Cast_DINToleranceStandard"
    )


__docformat__ = "restructuredtext en"
__all__ = ("DINToleranceStandard",)


class DINToleranceStandard(Enum):
    """DINToleranceStandard

    This is a mastapy class.

    Note:
        This class is an Enum.
    """

    @classmethod
    def type_(cls) -> "Type":
        return _DIN_TOLERANCE_STANDARD

    DIN_39621978 = 0


def __enum_setattr(self: "Self", attr: str, value: "Any") -> None:
    raise AttributeError("Cannot set the attributes of an Enum.") from None


def __enum_delattr(self: "Self", attr: str) -> None:
    raise AttributeError("Cannot delete the attributes of an Enum.") from None


DINToleranceStandard.__setattr__ = __enum_setattr
DINToleranceStandard.__delattr__ = __enum_delattr
