"""OilPumpLossCalculationMethod"""

from __future__ import annotations

from enum import Enum
from typing import TYPE_CHECKING

from mastapy._private._internal.python_net import python_net_import

_OIL_PUMP_LOSS_CALCULATION_METHOD = python_net_import(
    "SMT.MastaAPI.Materials.Efficiency", "OilPumpLossCalculationMethod"
)

if TYPE_CHECKING:
    from typing import Any, Type, TypeVar

    Self = TypeVar("Self", bound="OilPumpLossCalculationMethod")
    CastSelf = TypeVar(
        "CastSelf",
        bound="OilPumpLossCalculationMethod._Cast_OilPumpLossCalculationMethod",
    )


__docformat__ = "restructuredtext en"
__all__ = ("OilPumpLossCalculationMethod",)


class OilPumpLossCalculationMethod(Enum):
    """OilPumpLossCalculationMethod

    This is a mastapy class.

    Note:
        This class is an Enum.
    """

    @classmethod
    def type_(cls) -> "Type":
        return _OIL_PUMP_LOSS_CALCULATION_METHOD

    ISOTR_1417912001 = 0
    TAMAIS_METHOD = 1


def __enum_setattr(self: "Self", attr: str, value: "Any") -> None:
    raise AttributeError("Cannot set the attributes of an Enum.") from None


def __enum_delattr(self: "Self", attr: str) -> None:
    raise AttributeError("Cannot delete the attributes of an Enum.") from None


OilPumpLossCalculationMethod.__setattr__ = __enum_setattr
OilPumpLossCalculationMethod.__delattr__ = __enum_delattr
