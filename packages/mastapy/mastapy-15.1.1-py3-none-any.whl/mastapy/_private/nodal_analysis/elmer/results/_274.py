"""ElementFromMechanicalAnalysis"""

from __future__ import annotations

from typing import TYPE_CHECKING, ClassVar

from mastapy._private._internal.dataclasses import extended_dataclass
from mastapy._private._internal.exceptions import CastException
from mastapy._private._internal.python_net import python_net_import

from mastapy._private._internal import utility
from mastapy._private.nodal_analysis.elmer.results import _272

_ELEMENT_FROM_MECHANICAL_ANALYSIS = python_net_import(
    "SMT.MastaAPI.NodalAnalysis.Elmer.Results", "ElementFromMechanicalAnalysis"
)

if TYPE_CHECKING:
    from typing import Any, Type, TypeVar

    Self = TypeVar("Self", bound="ElementFromMechanicalAnalysis")
    CastSelf = TypeVar(
        "CastSelf",
        bound="ElementFromMechanicalAnalysis._Cast_ElementFromMechanicalAnalysis",
    )


__docformat__ = "restructuredtext en"
__all__ = ("ElementFromMechanicalAnalysis",)


@extended_dataclass(frozen=True, slots=True, weakref_slot=True)
class _Cast_ElementFromMechanicalAnalysis:
    """Special nested class for casting ElementFromMechanicalAnalysis to subclasses."""

    __parent__: "ElementFromMechanicalAnalysis"

    @property
    def element_base(self: "CastSelf") -> "_272.ElementBase":
        return self.__parent__._cast(_272.ElementBase)

    @property
    def element_from_mechanical_analysis(
        self: "CastSelf",
    ) -> "ElementFromMechanicalAnalysis":
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
class ElementFromMechanicalAnalysis(_272.ElementBase):
    """ElementFromMechanicalAnalysis

    This is a mastapy class.
    """

    TYPE: ClassVar["Type"] = _ELEMENT_FROM_MECHANICAL_ANALYSIS

    wrapped: "Any"

    def __post_init__(self: "Self") -> None:
        """Override of the post initialisation magic method."""
        if not hasattr(self.wrapped, "reference_count"):
            self.wrapped.reference_count = 0

        self.wrapped.reference_count += 1

    @property
    def cast_to(self: "Self") -> "_Cast_ElementFromMechanicalAnalysis":
        """Cast to another type.

        Returns:
            _Cast_ElementFromMechanicalAnalysis
        """
        return _Cast_ElementFromMechanicalAnalysis(self)
