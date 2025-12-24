"""ElmerResults"""

from __future__ import annotations

from typing import TYPE_CHECKING, ClassVar

from mastapy._private._internal.dataclasses import extended_dataclass
from mastapy._private._internal.exceptions import CastException
from mastapy._private._internal.python_net import python_net_import

from mastapy._private._internal import utility
from mastapy._private.nodal_analysis.elmer import _259
from mastapy._private.nodal_analysis.elmer.results import _271

_ELMER_RESULTS = python_net_import("SMT.MastaAPI.NodalAnalysis.Elmer", "ElmerResults")

if TYPE_CHECKING:
    from typing import Any, Type, TypeVar

    Self = TypeVar("Self", bound="ElmerResults")
    CastSelf = TypeVar("CastSelf", bound="ElmerResults._Cast_ElmerResults")


__docformat__ = "restructuredtext en"
__all__ = ("ElmerResults",)


@extended_dataclass(frozen=True, slots=True, weakref_slot=True)
class _Cast_ElmerResults:
    """Special nested class for casting ElmerResults to subclasses."""

    __parent__: "ElmerResults"

    @property
    def elmer_results_base(self: "CastSelf") -> "_259.ElmerResultsBase":
        return self.__parent__._cast(_259.ElmerResultsBase)

    @property
    def elmer_results(self: "CastSelf") -> "ElmerResults":
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
class ElmerResults(_259.ElmerResultsBase[_271.Element]):
    """ElmerResults

    This is a mastapy class.
    """

    TYPE: ClassVar["Type"] = _ELMER_RESULTS

    wrapped: "Any"

    def __post_init__(self: "Self") -> None:
        """Override of the post initialisation magic method."""
        if not hasattr(self.wrapped, "reference_count"):
            self.wrapped.reference_count = 0

        self.wrapped.reference_count += 1

    @property
    def cast_to(self: "Self") -> "_Cast_ElmerResults":
        """Cast to another type.

        Returns:
            _Cast_ElmerResults
        """
        return _Cast_ElmerResults(self)
