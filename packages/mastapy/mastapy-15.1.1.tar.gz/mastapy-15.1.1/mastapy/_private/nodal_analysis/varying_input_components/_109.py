"""ConstraintType"""

from __future__ import annotations

from enum import Enum
from typing import TYPE_CHECKING

from mastapy._private._internal.python_net import python_net_import

_CONSTRAINT_TYPE = python_net_import(
    "SMT.MastaAPI.NodalAnalysis.VaryingInputComponents", "ConstraintType"
)

if TYPE_CHECKING:
    from typing import Any, Type, TypeVar

    Self = TypeVar("Self", bound="ConstraintType")
    CastSelf = TypeVar("CastSelf", bound="ConstraintType._Cast_ConstraintType")


__docformat__ = "restructuredtext en"
__all__ = ("ConstraintType",)


class ConstraintType(Enum):
    """ConstraintType

    This is a mastapy class.

    Note:
        This class is an Enum.
    """

    @classmethod
    def type_(cls) -> "Type":
        return _CONSTRAINT_TYPE

    NONE = 0
    LINEAR_OR_MOMENT_FORCE = 1
    LINEAR_OR_ANGULAR_DISPLACEMENT = 2


def __enum_setattr(self: "Self", attr: str, value: "Any") -> None:
    raise AttributeError("Cannot set the attributes of an Enum.") from None


def __enum_delattr(self: "Self", attr: str) -> None:
    raise AttributeError("Cannot delete the attributes of an Enum.") from None


ConstraintType.__setattr__ = __enum_setattr
ConstraintType.__delattr__ = __enum_delattr
