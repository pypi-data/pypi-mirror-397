"""ModalAnalysisAtAStiffness"""

from __future__ import annotations

from typing import TYPE_CHECKING, ClassVar

from mastapy._private._internal.dataclasses import extended_dataclass
from mastapy._private._internal.exceptions import CastException
from mastapy._private._internal.python_net import python_net_import

from mastapy._private._internal import utility
from mastapy._private.system_model.analyses_and_results.analysis_cases import _7946

_MODAL_ANALYSIS_AT_A_STIFFNESS = python_net_import(
    "SMT.MastaAPI.SystemModel.AnalysesAndResults.ModalAnalysesAtAStiffness",
    "ModalAnalysisAtAStiffness",
)

if TYPE_CHECKING:
    from typing import Any, Type, TypeVar

    from mastapy._private.system_model.analyses_and_results import _2942
    from mastapy._private.system_model.analyses_and_results.analysis_cases import _7931

    Self = TypeVar("Self", bound="ModalAnalysisAtAStiffness")
    CastSelf = TypeVar(
        "CastSelf", bound="ModalAnalysisAtAStiffness._Cast_ModalAnalysisAtAStiffness"
    )


__docformat__ = "restructuredtext en"
__all__ = ("ModalAnalysisAtAStiffness",)


@extended_dataclass(frozen=True, slots=True, weakref_slot=True)
class _Cast_ModalAnalysisAtAStiffness:
    """Special nested class for casting ModalAnalysisAtAStiffness to subclasses."""

    __parent__: "ModalAnalysisAtAStiffness"

    @property
    def static_load_analysis_case(self: "CastSelf") -> "_7946.StaticLoadAnalysisCase":
        return self.__parent__._cast(_7946.StaticLoadAnalysisCase)

    @property
    def analysis_case(self: "CastSelf") -> "_7931.AnalysisCase":
        from mastapy._private.system_model.analyses_and_results.analysis_cases import (
            _7931,
        )

        return self.__parent__._cast(_7931.AnalysisCase)

    @property
    def context(self: "CastSelf") -> "_2942.Context":
        from mastapy._private.system_model.analyses_and_results import _2942

        return self.__parent__._cast(_2942.Context)

    @property
    def modal_analysis_at_a_stiffness(self: "CastSelf") -> "ModalAnalysisAtAStiffness":
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
class ModalAnalysisAtAStiffness(_7946.StaticLoadAnalysisCase):
    """ModalAnalysisAtAStiffness

    This is a mastapy class.
    """

    TYPE: ClassVar["Type"] = _MODAL_ANALYSIS_AT_A_STIFFNESS

    wrapped: "Any"

    def __post_init__(self: "Self") -> None:
        """Override of the post initialisation magic method."""
        if not hasattr(self.wrapped, "reference_count"):
            self.wrapped.reference_count = 0

        self.wrapped.reference_count += 1

    @property
    def cast_to(self: "Self") -> "_Cast_ModalAnalysisAtAStiffness":
        """Cast to another type.

        Returns:
            _Cast_ModalAnalysisAtAStiffness
        """
        return _Cast_ModalAnalysisAtAStiffness(self)
