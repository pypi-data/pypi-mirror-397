"""ISO14179Part1ConstantC1SpecificationMethod"""

from __future__ import annotations

from enum import Enum
from typing import TYPE_CHECKING

from mastapy._private._internal.python_net import python_net_import

_ISO14179_PART_1_CONSTANT_C1_SPECIFICATION_METHOD = python_net_import(
    "SMT.MastaAPI.Gears.Materials", "ISO14179Part1ConstantC1SpecificationMethod"
)

if TYPE_CHECKING:
    from typing import Any, Type, TypeVar

    Self = TypeVar("Self", bound="ISO14179Part1ConstantC1SpecificationMethod")
    CastSelf = TypeVar(
        "CastSelf",
        bound="ISO14179Part1ConstantC1SpecificationMethod._Cast_ISO14179Part1ConstantC1SpecificationMethod",
    )


__docformat__ = "restructuredtext en"
__all__ = ("ISO14179Part1ConstantC1SpecificationMethod",)


class ISO14179Part1ConstantC1SpecificationMethod(Enum):
    """ISO14179Part1ConstantC1SpecificationMethod

    This is a mastapy class.

    Note:
        This class is an Enum.
    """

    @classmethod
    def type_(cls) -> "Type":
        return _ISO14179_PART_1_CONSTANT_C1_SPECIFICATION_METHOD

    CONSTANT = 0
    FUNCTION_OF_LOAD_INTENSITY = 1


def __enum_setattr(self: "Self", attr: str, value: "Any") -> None:
    raise AttributeError("Cannot set the attributes of an Enum.") from None


def __enum_delattr(self: "Self", attr: str) -> None:
    raise AttributeError("Cannot delete the attributes of an Enum.") from None


ISO14179Part1ConstantC1SpecificationMethod.__setattr__ = __enum_setattr
ISO14179Part1ConstantC1SpecificationMethod.__delattr__ = __enum_delattr
