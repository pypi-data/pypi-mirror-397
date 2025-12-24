"""NamedSelectionFace"""

from __future__ import annotations

from typing import TYPE_CHECKING, ClassVar

from mastapy._private._internal.dataclasses import extended_dataclass
from mastapy._private._internal.exceptions import CastException
from mastapy._private._internal.python_net import python_net_import

from mastapy._private._internal import utility
from mastapy._private.math_utility import _1735

_NAMED_SELECTION_FACE = python_net_import(
    "SMT.MastaAPI.MathUtility", "NamedSelectionFace"
)

if TYPE_CHECKING:
    from typing import Any, Type, TypeVar

    Self = TypeVar("Self", bound="NamedSelectionFace")
    CastSelf = TypeVar("CastSelf", bound="NamedSelectionFace._Cast_NamedSelectionFace")


__docformat__ = "restructuredtext en"
__all__ = ("NamedSelectionFace",)


@extended_dataclass(frozen=True, slots=True, weakref_slot=True)
class _Cast_NamedSelectionFace:
    """Special nested class for casting NamedSelectionFace to subclasses."""

    __parent__: "NamedSelectionFace"

    @property
    def named_selection(self: "CastSelf") -> "_1735.NamedSelection":
        return self.__parent__._cast(_1735.NamedSelection)

    @property
    def named_selection_face(self: "CastSelf") -> "NamedSelectionFace":
        return self.__parent__

    def __getattr__(self: "CastSelf", name: str) -> "Any":
        try:
            return self.__getattribute__(name)
        except AttributeError:
            class_name = utility.camel(name)
            raise CastException(
                f'Detected an invalid cast. Cannot cast to type "{class_name}"'
            ) from None


@extended_dataclass(frozen=True, slots=True, weakref_slot=True, eq=False)
class NamedSelectionFace(_1735.NamedSelection):
    """NamedSelectionFace

    This is a mastapy class.
    """

    TYPE: ClassVar["Type"] = _NAMED_SELECTION_FACE

    wrapped: "Any"

    def __post_init__(self: "Self") -> None:
        """Override of the post initialisation magic method."""
        if not hasattr(self.wrapped, "reference_count"):
            self.wrapped.reference_count = 0

        self.wrapped.reference_count += 1

    @property
    def cast_to(self: "Self") -> "_Cast_NamedSelectionFace":
        """Cast to another type.

        Returns:
            _Cast_NamedSelectionFace
        """
        return _Cast_NamedSelectionFace(self)
