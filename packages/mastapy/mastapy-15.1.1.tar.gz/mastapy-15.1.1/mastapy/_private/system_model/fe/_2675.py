"""RaceBearingFEWithSelection"""

from __future__ import annotations

from typing import TYPE_CHECKING, ClassVar

from mastapy._private._internal.dataclasses import extended_dataclass
from mastapy._private._internal.exception_bridge import exception_bridge
from mastapy._private._internal.exceptions import CastException
from mastapy._private._internal.python_net import (
    python_net_import,
    pythonnet_property_get,
)

from mastapy._private._internal import constructor, utility
from mastapy._private.system_model.fe import _2619

_RACE_BEARING_FE_WITH_SELECTION = python_net_import(
    "SMT.MastaAPI.SystemModel.FE", "RaceBearingFEWithSelection"
)

if TYPE_CHECKING:
    from typing import Any, Type, TypeVar

    from mastapy._private.math_utility import _1711
    from mastapy._private.system_model.fe import _2673

    Self = TypeVar("Self", bound="RaceBearingFEWithSelection")
    CastSelf = TypeVar(
        "CastSelf", bound="RaceBearingFEWithSelection._Cast_RaceBearingFEWithSelection"
    )


__docformat__ = "restructuredtext en"
__all__ = ("RaceBearingFEWithSelection",)


@extended_dataclass(frozen=True, slots=True, weakref_slot=True)
class _Cast_RaceBearingFEWithSelection:
    """Special nested class for casting RaceBearingFEWithSelection to subclasses."""

    __parent__: "RaceBearingFEWithSelection"

    @property
    def base_fe_with_selection(self: "CastSelf") -> "_2619.BaseFEWithSelection":
        return self.__parent__._cast(_2619.BaseFEWithSelection)

    @property
    def race_bearing_fe_with_selection(
        self: "CastSelf",
    ) -> "RaceBearingFEWithSelection":
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
class RaceBearingFEWithSelection(_2619.BaseFEWithSelection):
    """RaceBearingFEWithSelection

    This is a mastapy class.
    """

    TYPE: ClassVar["Type"] = _RACE_BEARING_FE_WITH_SELECTION

    wrapped: "Any"

    def __post_init__(self: "Self") -> None:
        """Override of the post initialisation magic method."""
        if not hasattr(self.wrapped, "reference_count"):
            self.wrapped.reference_count = 0

        self.wrapped.reference_count += 1

    @property
    @exception_bridge
    def manual_alignment(self: "Self") -> "_1711.CoordinateSystemEditor":
        """mastapy.math_utility.CoordinateSystemEditor

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "ManualAlignment")

        if temp is None:
            return None

        type_ = temp.GetType()
        return constructor.new(type_.Namespace, type_.Name)(temp)

    @property
    @exception_bridge
    def race_bearing(self: "Self") -> "_2673.RaceBearingFE":
        """mastapy.system_model.fe.RaceBearingFE

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "RaceBearing")

        if temp is None:
            return None

        type_ = temp.GetType()
        return constructor.new(type_.Namespace, type_.Name)(temp)

    @property
    def cast_to(self: "Self") -> "_Cast_RaceBearingFEWithSelection":
        """Cast to another type.

        Returns:
            _Cast_RaceBearingFEWithSelection
        """
        return _Cast_RaceBearingFEWithSelection(self)
