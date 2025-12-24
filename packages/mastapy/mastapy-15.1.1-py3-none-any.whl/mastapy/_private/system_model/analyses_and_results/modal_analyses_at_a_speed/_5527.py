"""ModalAnalysisAtASpeed"""

from __future__ import annotations

from typing import TYPE_CHECKING, ClassVar

from mastapy._private._internal.dataclasses import extended_dataclass
from mastapy._private._internal.exceptions import CastException
from mastapy._private._internal.python_net import python_net_import

from mastapy._private._internal import utility
from mastapy._private.system_model.analyses_and_results.analysis_cases import _7946

_MODAL_ANALYSIS_AT_A_SPEED = python_net_import(
    "SMT.MastaAPI.SystemModel.AnalysesAndResults.ModalAnalysesAtASpeed",
    "ModalAnalysisAtASpeed",
)

if TYPE_CHECKING:
    from typing import Any, Type, TypeVar

    from mastapy._private.system_model.analyses_and_results import _2942
    from mastapy._private.system_model.analyses_and_results.analysis_cases import _7931

    Self = TypeVar("Self", bound="ModalAnalysisAtASpeed")
    CastSelf = TypeVar(
        "CastSelf", bound="ModalAnalysisAtASpeed._Cast_ModalAnalysisAtASpeed"
    )


__docformat__ = "restructuredtext en"
__all__ = ("ModalAnalysisAtASpeed",)


@extended_dataclass(frozen=True, slots=True, weakref_slot=True)
class _Cast_ModalAnalysisAtASpeed:
    """Special nested class for casting ModalAnalysisAtASpeed to subclasses."""

    __parent__: "ModalAnalysisAtASpeed"

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
    def modal_analysis_at_a_speed(self: "CastSelf") -> "ModalAnalysisAtASpeed":
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
class ModalAnalysisAtASpeed(_7946.StaticLoadAnalysisCase):
    """ModalAnalysisAtASpeed

    This is a mastapy class.
    """

    TYPE: ClassVar["Type"] = _MODAL_ANALYSIS_AT_A_SPEED

    wrapped: "Any"

    def __post_init__(self: "Self") -> None:
        """Override of the post initialisation magic method."""
        if not hasattr(self.wrapped, "reference_count"):
            self.wrapped.reference_count = 0

        self.wrapped.reference_count += 1

    @property
    def cast_to(self: "Self") -> "_Cast_ModalAnalysisAtASpeed":
        """Cast to another type.

        Returns:
            _Cast_ModalAnalysisAtASpeed
        """
        return _Cast_ModalAnalysisAtASpeed(self)
