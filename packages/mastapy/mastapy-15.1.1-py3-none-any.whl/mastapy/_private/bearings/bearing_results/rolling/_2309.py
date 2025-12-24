"""PowerRatingFactorScalingMethod"""

from __future__ import annotations

from enum import Enum
from typing import TYPE_CHECKING

from mastapy._private._internal.python_net import python_net_import

_POWER_RATING_FACTOR_SCALING_METHOD = python_net_import(
    "SMT.MastaAPI.Bearings.BearingResults.Rolling", "PowerRatingFactorScalingMethod"
)

if TYPE_CHECKING:
    from typing import Any, Type, TypeVar

    Self = TypeVar("Self", bound="PowerRatingFactorScalingMethod")
    CastSelf = TypeVar(
        "CastSelf",
        bound="PowerRatingFactorScalingMethod._Cast_PowerRatingFactorScalingMethod",
    )


__docformat__ = "restructuredtext en"
__all__ = ("PowerRatingFactorScalingMethod",)


class PowerRatingFactorScalingMethod(Enum):
    """PowerRatingFactorScalingMethod

    This is a mastapy class.

    Note:
        This class is an Enum.
    """

    @classmethod
    def type_(cls) -> "Type":
        return _POWER_RATING_FACTOR_SCALING_METHOD

    CONSTANT = 0
    ONEDIMENSIONAL_LOOKUP_TABLE = 1


def __enum_setattr(self: "Self", attr: str, value: "Any") -> None:
    raise AttributeError("Cannot set the attributes of an Enum.") from None


def __enum_delattr(self: "Self", attr: str) -> None:
    raise AttributeError("Cannot delete the attributes of an Enum.") from None


PowerRatingFactorScalingMethod.__setattr__ = __enum_setattr
PowerRatingFactorScalingMethod.__delattr__ = __enum_delattr
