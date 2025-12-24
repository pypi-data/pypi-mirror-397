"""OilJetVelocitySpecificationMethod"""

from __future__ import annotations

from enum import Enum
from typing import TYPE_CHECKING

from mastapy._private._internal.python_net import python_net_import

_OIL_JET_VELOCITY_SPECIFICATION_METHOD = python_net_import(
    "SMT.MastaAPI.Gears", "OilJetVelocitySpecificationMethod"
)

if TYPE_CHECKING:
    from typing import Any, Type, TypeVar

    Self = TypeVar("Self", bound="OilJetVelocitySpecificationMethod")
    CastSelf = TypeVar(
        "CastSelf",
        bound="OilJetVelocitySpecificationMethod._Cast_OilJetVelocitySpecificationMethod",
    )


__docformat__ = "restructuredtext en"
__all__ = ("OilJetVelocitySpecificationMethod",)


class OilJetVelocitySpecificationMethod(Enum):
    """OilJetVelocitySpecificationMethod

    This is a mastapy class.

    Note:
        This class is an Enum.
    """

    @classmethod
    def type_(cls) -> "Type":
        return _OIL_JET_VELOCITY_SPECIFICATION_METHOD

    CONSTANT = 0
    SCRIPT = 1


def __enum_setattr(self: "Self", attr: str, value: "Any") -> None:
    raise AttributeError("Cannot set the attributes of an Enum.") from None


def __enum_delattr(self: "Self", attr: str) -> None:
    raise AttributeError("Cannot delete the attributes of an Enum.") from None


OilJetVelocitySpecificationMethod.__setattr__ = __enum_setattr
OilJetVelocitySpecificationMethod.__delattr__ = __enum_delattr
