"""ElementFromElectromagneticAnalysis"""

from __future__ import annotations

from typing import TYPE_CHECKING, ClassVar

from mastapy._private._internal.dataclasses import extended_dataclass
from mastapy._private._internal.exceptions import CastException
from mastapy._private._internal.python_net import python_net_import

from mastapy._private._internal import utility
from mastapy._private.nodal_analysis.elmer.results import _272

_ELEMENT_FROM_ELECTROMAGNETIC_ANALYSIS = python_net_import(
    "SMT.MastaAPI.NodalAnalysis.Elmer.Results", "ElementFromElectromagneticAnalysis"
)

if TYPE_CHECKING:
    from typing import Any, Type, TypeVar

    Self = TypeVar("Self", bound="ElementFromElectromagneticAnalysis")
    CastSelf = TypeVar(
        "CastSelf",
        bound="ElementFromElectromagneticAnalysis._Cast_ElementFromElectromagneticAnalysis",
    )


__docformat__ = "restructuredtext en"
__all__ = ("ElementFromElectromagneticAnalysis",)


@extended_dataclass(frozen=True, slots=True, weakref_slot=True)
class _Cast_ElementFromElectromagneticAnalysis:
    """Special nested class for casting ElementFromElectromagneticAnalysis to subclasses."""

    __parent__: "ElementFromElectromagneticAnalysis"

    @property
    def element_base(self: "CastSelf") -> "_272.ElementBase":
        return self.__parent__._cast(_272.ElementBase)

    @property
    def element_from_electromagnetic_analysis(
        self: "CastSelf",
    ) -> "ElementFromElectromagneticAnalysis":
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
class ElementFromElectromagneticAnalysis(_272.ElementBase):
    """ElementFromElectromagneticAnalysis

    This is a mastapy class.
    """

    TYPE: ClassVar["Type"] = _ELEMENT_FROM_ELECTROMAGNETIC_ANALYSIS

    wrapped: "Any"

    def __post_init__(self: "Self") -> None:
        """Override of the post initialisation magic method."""
        if not hasattr(self.wrapped, "reference_count"):
            self.wrapped.reference_count = 0

        self.wrapped.reference_count += 1

    @property
    def cast_to(self: "Self") -> "_Cast_ElementFromElectromagneticAnalysis":
        """Cast to another type.

        Returns:
            _Cast_ElementFromElectromagneticAnalysis
        """
        return _Cast_ElementFromElectromagneticAnalysis(self)
