"""HemisphericalEnvelopeType"""

from __future__ import annotations

from enum import Enum
from typing import TYPE_CHECKING

from mastapy._private._internal.python_net import python_net_import

_HEMISPHERICAL_ENVELOPE_TYPE = python_net_import(
    "SMT.MastaAPI.SystemModel.PartModel.Acoustics", "HemisphericalEnvelopeType"
)

if TYPE_CHECKING:
    from typing import Any, Type, TypeVar

    Self = TypeVar("Self", bound="HemisphericalEnvelopeType")
    CastSelf = TypeVar(
        "CastSelf", bound="HemisphericalEnvelopeType._Cast_HemisphericalEnvelopeType"
    )


__docformat__ = "restructuredtext en"
__all__ = ("HemisphericalEnvelopeType",)


class HemisphericalEnvelopeType(Enum):
    """HemisphericalEnvelopeType

    This is a mastapy class.

    Note:
        This class is an Enum.
    """

    @classmethod
    def type_(cls) -> "Type":
        return _HEMISPHERICAL_ENVELOPE_TYPE

    PREFERRED = 0
    EXTENDED_PREFERRED = 1
    ALTERNATIVE = 2
    EXTENDED_ALTERNATIVE = 3
    REDUCED_ALTERNATIVE = 4
    ORBITAL = 5


def __enum_setattr(self: "Self", attr: str, value: "Any") -> None:
    raise AttributeError("Cannot set the attributes of an Enum.") from None


def __enum_delattr(self: "Self", attr: str) -> None:
    raise AttributeError("Cannot delete the attributes of an Enum.") from None


HemisphericalEnvelopeType.__setattr__ = __enum_setattr
HemisphericalEnvelopeType.__delattr__ = __enum_delattr
