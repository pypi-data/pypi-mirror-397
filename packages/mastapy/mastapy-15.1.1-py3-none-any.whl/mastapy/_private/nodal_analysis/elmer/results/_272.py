"""ElementBase"""

from __future__ import annotations

from typing import TYPE_CHECKING, ClassVar

from mastapy._private._internal.dataclasses import extended_dataclass
from mastapy._private._internal.exceptions import CastException
from mastapy._private._internal.python_net import python_net_import

from mastapy._private import _0
from mastapy._private._internal import utility

_ELEMENT_BASE = python_net_import(
    "SMT.MastaAPI.NodalAnalysis.Elmer.Results", "ElementBase"
)

if TYPE_CHECKING:
    from typing import Any, Type, TypeVar

    from mastapy._private.nodal_analysis.elmer.results import _271, _273, _274

    Self = TypeVar("Self", bound="ElementBase")
    CastSelf = TypeVar("CastSelf", bound="ElementBase._Cast_ElementBase")


__docformat__ = "restructuredtext en"
__all__ = ("ElementBase",)


@extended_dataclass(frozen=True, slots=True, weakref_slot=True)
class _Cast_ElementBase:
    """Special nested class for casting ElementBase to subclasses."""

    __parent__: "ElementBase"

    @property
    def element(self: "CastSelf") -> "_271.Element":
        from mastapy._private.nodal_analysis.elmer.results import _271

        return self.__parent__._cast(_271.Element)

    @property
    def element_from_electromagnetic_analysis(
        self: "CastSelf",
    ) -> "_273.ElementFromElectromagneticAnalysis":
        from mastapy._private.nodal_analysis.elmer.results import _273

        return self.__parent__._cast(_273.ElementFromElectromagneticAnalysis)

    @property
    def element_from_mechanical_analysis(
        self: "CastSelf",
    ) -> "_274.ElementFromMechanicalAnalysis":
        from mastapy._private.nodal_analysis.elmer.results import _274

        return self.__parent__._cast(_274.ElementFromMechanicalAnalysis)

    @property
    def element_base(self: "CastSelf") -> "ElementBase":
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
class ElementBase(_0.APIBase):
    """ElementBase

    This is a mastapy class.
    """

    TYPE: ClassVar["Type"] = _ELEMENT_BASE

    wrapped: "Any"

    def __post_init__(self: "Self") -> None:
        """Override of the post initialisation magic method."""
        if not hasattr(self.wrapped, "reference_count"):
            self.wrapped.reference_count = 0

        self.wrapped.reference_count += 1

    @property
    def cast_to(self: "Self") -> "_Cast_ElementBase":
        """Cast to another type.

        Returns:
            _Cast_ElementBase
        """
        return _Cast_ElementBase(self)
