"""WetClutchLossCalculationMethod"""

from __future__ import annotations

from enum import Enum
from typing import TYPE_CHECKING

from mastapy._private._internal.python_net import python_net_import

_WET_CLUTCH_LOSS_CALCULATION_METHOD = python_net_import(
    "SMT.MastaAPI.Materials.Efficiency", "WetClutchLossCalculationMethod"
)

if TYPE_CHECKING:
    from typing import Any, Type, TypeVar

    Self = TypeVar("Self", bound="WetClutchLossCalculationMethod")
    CastSelf = TypeVar(
        "CastSelf",
        bound="WetClutchLossCalculationMethod._Cast_WetClutchLossCalculationMethod",
    )


__docformat__ = "restructuredtext en"
__all__ = ("WetClutchLossCalculationMethod",)


class WetClutchLossCalculationMethod(Enum):
    """WetClutchLossCalculationMethod

    This is a mastapy class.

    Note:
        This class is an Enum.
    """

    @classmethod
    def type_(cls) -> "Type":
        return _WET_CLUTCH_LOSS_CALCULATION_METHOD

    PARKS_METHOD = 0
    TAMAIS_METHOD = 1


def __enum_setattr(self: "Self", attr: str, value: "Any") -> None:
    raise AttributeError("Cannot set the attributes of an Enum.") from None


def __enum_delattr(self: "Self", attr: str) -> None:
    raise AttributeError("Cannot delete the attributes of an Enum.") from None


WetClutchLossCalculationMethod.__setattr__ = __enum_setattr
WetClutchLossCalculationMethod.__delattr__ = __enum_delattr
