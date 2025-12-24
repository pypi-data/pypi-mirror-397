"""CylindricalEnvelopeTypes"""

from __future__ import annotations

from enum import Enum
from typing import TYPE_CHECKING

from mastapy._private._internal.python_net import python_net_import

_CYLINDRICAL_ENVELOPE_TYPES = python_net_import(
    "SMT.MastaAPI.SystemModel.PartModel.Acoustics", "CylindricalEnvelopeTypes"
)

if TYPE_CHECKING:
    from typing import Any, Type, TypeVar

    Self = TypeVar("Self", bound="CylindricalEnvelopeTypes")
    CastSelf = TypeVar(
        "CastSelf", bound="CylindricalEnvelopeTypes._Cast_CylindricalEnvelopeTypes"
    )


__docformat__ = "restructuredtext en"
__all__ = ("CylindricalEnvelopeTypes",)


class CylindricalEnvelopeTypes(Enum):
    """CylindricalEnvelopeTypes

    This is a mastapy class.

    Note:
        This class is an Enum.
    """

    @classmethod
    def type_(cls) -> "Type":
        return _CYLINDRICAL_ENVELOPE_TYPES

    CYLINDRICAL_SWEEP = 0
    CYLINDRICAL_DISCRETE = 1


def __enum_setattr(self: "Self", attr: str, value: "Any") -> None:
    raise AttributeError("Cannot set the attributes of an Enum.") from None


def __enum_delattr(self: "Self", attr: str) -> None:
    raise AttributeError("Cannot delete the attributes of an Enum.") from None


CylindricalEnvelopeTypes.__setattr__ = __enum_setattr
CylindricalEnvelopeTypes.__delattr__ = __enum_delattr
