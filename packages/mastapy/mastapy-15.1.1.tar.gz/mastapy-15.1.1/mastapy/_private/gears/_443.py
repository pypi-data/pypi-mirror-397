"""LubricationMethodForNoLoadLossesCalc"""

from __future__ import annotations

from enum import Enum
from typing import TYPE_CHECKING

from mastapy._private._internal.python_net import python_net_import

_LUBRICATION_METHOD_FOR_NO_LOAD_LOSSES_CALC = python_net_import(
    "SMT.MastaAPI.Gears", "LubricationMethodForNoLoadLossesCalc"
)

if TYPE_CHECKING:
    from typing import Any, Type, TypeVar

    Self = TypeVar("Self", bound="LubricationMethodForNoLoadLossesCalc")
    CastSelf = TypeVar(
        "CastSelf",
        bound="LubricationMethodForNoLoadLossesCalc._Cast_LubricationMethodForNoLoadLossesCalc",
    )


__docformat__ = "restructuredtext en"
__all__ = ("LubricationMethodForNoLoadLossesCalc",)


class LubricationMethodForNoLoadLossesCalc(Enum):
    """LubricationMethodForNoLoadLossesCalc

    This is a mastapy class.

    Note:
        This class is an Enum.
    """

    @classmethod
    def type_(cls) -> "Type":
        return _LUBRICATION_METHOD_FOR_NO_LOAD_LOSSES_CALC

    SPLASH = 0
    INJECTION = 1
    SPLASH_INJECTION = 2


def __enum_setattr(self: "Self", attr: str, value: "Any") -> None:
    raise AttributeError("Cannot set the attributes of an Enum.") from None


def __enum_delattr(self: "Self", attr: str) -> None:
    raise AttributeError("Cannot delete the attributes of an Enum.") from None


LubricationMethodForNoLoadLossesCalc.__setattr__ = __enum_setattr
LubricationMethodForNoLoadLossesCalc.__delattr__ = __enum_delattr
