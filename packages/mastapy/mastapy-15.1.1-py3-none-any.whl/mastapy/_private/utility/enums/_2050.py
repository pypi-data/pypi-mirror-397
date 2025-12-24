"""SplineForceArrowOption"""

from __future__ import annotations

from enum import Enum
from typing import TYPE_CHECKING

from mastapy._private._internal.python_net import python_net_import

_SPLINE_FORCE_ARROW_OPTION = python_net_import(
    "SMT.MastaAPI.Utility.Enums", "SplineForceArrowOption"
)

if TYPE_CHECKING:
    from typing import Any, Type, TypeVar

    Self = TypeVar("Self", bound="SplineForceArrowOption")
    CastSelf = TypeVar(
        "CastSelf", bound="SplineForceArrowOption._Cast_SplineForceArrowOption"
    )


__docformat__ = "restructuredtext en"
__all__ = ("SplineForceArrowOption",)


class SplineForceArrowOption(Enum):
    """SplineForceArrowOption

    This is a mastapy class.

    Note:
        This class is an Enum.
    """

    @classmethod
    def type_(cls) -> "Type":
        return _SPLINE_FORCE_ARROW_OPTION

    FORCE_PER_TOOTH_FLANK = 0
    LOAD_DISTRIBUTION = 1


def __enum_setattr(self: "Self", attr: str, value: "Any") -> None:
    raise AttributeError("Cannot set the attributes of an Enum.") from None


def __enum_delattr(self: "Self", attr: str) -> None:
    raise AttributeError("Cannot delete the attributes of an Enum.") from None


SplineForceArrowOption.__setattr__ = __enum_setattr
SplineForceArrowOption.__delattr__ = __enum_delattr
