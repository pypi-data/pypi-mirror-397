"""RightParallelepipedEnvelopeTypes"""

from __future__ import annotations

from enum import Enum
from typing import TYPE_CHECKING

from mastapy._private._internal.python_net import python_net_import

_RIGHT_PARALLELEPIPED_ENVELOPE_TYPES = python_net_import(
    "SMT.MastaAPI.SystemModel.PartModel.Acoustics", "RightParallelepipedEnvelopeTypes"
)

if TYPE_CHECKING:
    from typing import Any, Type, TypeVar

    Self = TypeVar("Self", bound="RightParallelepipedEnvelopeTypes")
    CastSelf = TypeVar(
        "CastSelf",
        bound="RightParallelepipedEnvelopeTypes._Cast_RightParallelepipedEnvelopeTypes",
    )


__docformat__ = "restructuredtext en"
__all__ = ("RightParallelepipedEnvelopeTypes",)


class RightParallelepipedEnvelopeTypes(Enum):
    """RightParallelepipedEnvelopeTypes

    This is a mastapy class.

    Note:
        This class is an Enum.
    """

    @classmethod
    def type_(cls) -> "Type":
        return _RIGHT_PARALLELEPIPED_ENVELOPE_TYPES

    RECTANGULAR = 0
    EXTENDED_RECTANGULAR = 1
    TRIANGULAR = 2
    EXTENDED_TRIANGULAR = 3


def __enum_setattr(self: "Self", attr: str, value: "Any") -> None:
    raise AttributeError("Cannot set the attributes of an Enum.") from None


def __enum_delattr(self: "Self", attr: str) -> None:
    raise AttributeError("Cannot delete the attributes of an Enum.") from None


RightParallelepipedEnvelopeTypes.__setattr__ = __enum_setattr
RightParallelepipedEnvelopeTypes.__delattr__ = __enum_delattr
