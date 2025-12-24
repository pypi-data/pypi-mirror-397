"""FrequencyDomainTEExcitationMethod"""

from __future__ import annotations

from enum import Enum
from typing import TYPE_CHECKING

from mastapy._private._internal.python_net import python_net_import

_FREQUENCY_DOMAIN_TE_EXCITATION_METHOD = python_net_import(
    "SMT.MastaAPI.NodalAnalysis", "FrequencyDomainTEExcitationMethod"
)

if TYPE_CHECKING:
    from typing import Any, Type, TypeVar

    Self = TypeVar("Self", bound="FrequencyDomainTEExcitationMethod")
    CastSelf = TypeVar(
        "CastSelf",
        bound="FrequencyDomainTEExcitationMethod._Cast_FrequencyDomainTEExcitationMethod",
    )


__docformat__ = "restructuredtext en"
__all__ = ("FrequencyDomainTEExcitationMethod",)


class FrequencyDomainTEExcitationMethod(Enum):
    """FrequencyDomainTEExcitationMethod

    This is a mastapy class.

    Note:
        This class is an Enum.
    """

    @classmethod
    def type_(cls) -> "Type":
        return _FREQUENCY_DOMAIN_TE_EXCITATION_METHOD

    STATIC_TE_DYNAMIC_MESH_FORCE_SPLITTING_MESH_STIFFNESS_STEYER = 0
    STIFFNESS_STATIC_TE = 1
    STATIC_RESPONSE_AT_ZERO_FREQUENCY = 2


def __enum_setattr(self: "Self", attr: str, value: "Any") -> None:
    raise AttributeError("Cannot set the attributes of an Enum.") from None


def __enum_delattr(self: "Self", attr: str) -> None:
    raise AttributeError("Cannot delete the attributes of an Enum.") from None


FrequencyDomainTEExcitationMethod.__setattr__ = __enum_setattr
FrequencyDomainTEExcitationMethod.__delattr__ = __enum_delattr
