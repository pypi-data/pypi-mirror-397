"""PreloadFactor"""

from __future__ import annotations

from enum import Enum
from typing import TYPE_CHECKING

from mastapy._private._internal.python_net import python_net_import

_PRELOAD_FACTOR = python_net_import(
    "SMT.MastaAPI.Bearings.BearingResults.Rolling", "PreloadFactor"
)

if TYPE_CHECKING:
    from typing import Any, Type, TypeVar

    Self = TypeVar("Self", bound="PreloadFactor")
    CastSelf = TypeVar("CastSelf", bound="PreloadFactor._Cast_PreloadFactor")


__docformat__ = "restructuredtext en"
__all__ = ("PreloadFactor",)


class PreloadFactor(Enum):
    """PreloadFactor

    This is a mastapy class.

    Note:
        This class is an Enum.
    """

    @classmethod
    def type_(cls) -> "Type":
        return _PRELOAD_FACTOR

    HIGH = 0
    MEDIUM = 1
    LOW = 2
    ZERO = 3


def __enum_setattr(self: "Self", attr: str, value: "Any") -> None:
    raise AttributeError("Cannot set the attributes of an Enum.") from None


def __enum_delattr(self: "Self", attr: str) -> None:
    raise AttributeError("Cannot delete the attributes of an Enum.") from None


PreloadFactor.__setattr__ = __enum_setattr
PreloadFactor.__delattr__ = __enum_delattr
