"""FaceGearDutyCycleRating"""

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
from mastapy._private.gears.rating import _470

_FACE_GEAR_DUTY_CYCLE_RATING = python_net_import(
    "SMT.MastaAPI.Gears.Rating.Face", "FaceGearDutyCycleRating"
)

if TYPE_CHECKING:
    from typing import Any, Type, TypeVar

    from mastapy._private.gears.analysis import _1361
    from mastapy._private.gears.rating import _466, _471

    Self = TypeVar("Self", bound="FaceGearDutyCycleRating")
    CastSelf = TypeVar(
        "CastSelf", bound="FaceGearDutyCycleRating._Cast_FaceGearDutyCycleRating"
    )


__docformat__ = "restructuredtext en"
__all__ = ("FaceGearDutyCycleRating",)


@extended_dataclass(frozen=True, slots=True, weakref_slot=True)
class _Cast_FaceGearDutyCycleRating:
    """Special nested class for casting FaceGearDutyCycleRating to subclasses."""

    __parent__: "FaceGearDutyCycleRating"

    @property
    def gear_duty_cycle_rating(self: "CastSelf") -> "_470.GearDutyCycleRating":
        return self.__parent__._cast(_470.GearDutyCycleRating)

    @property
    def abstract_gear_rating(self: "CastSelf") -> "_466.AbstractGearRating":
        from mastapy._private.gears.rating import _466

        return self.__parent__._cast(_466.AbstractGearRating)

    @property
    def abstract_gear_analysis(self: "CastSelf") -> "_1361.AbstractGearAnalysis":
        from mastapy._private.gears.analysis import _1361

        return self.__parent__._cast(_1361.AbstractGearAnalysis)

    @property
    def face_gear_duty_cycle_rating(self: "CastSelf") -> "FaceGearDutyCycleRating":
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
class FaceGearDutyCycleRating(_470.GearDutyCycleRating):
    """FaceGearDutyCycleRating

    This is a mastapy class.
    """

    TYPE: ClassVar["Type"] = _FACE_GEAR_DUTY_CYCLE_RATING

    wrapped: "Any"

    def __post_init__(self: "Self") -> None:
        """Override of the post initialisation magic method."""
        if not hasattr(self.wrapped, "reference_count"):
            self.wrapped.reference_count = 0

        self.wrapped.reference_count += 1

    @property
    @exception_bridge
    def left_flank_rating(self: "Self") -> "_471.GearFlankRating":
        """mastapy.gears.rating.GearFlankRating

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "LeftFlankRating")

        if temp is None:
            return None

        type_ = temp.GetType()
        return constructor.new(type_.Namespace, type_.Name)(temp)

    @property
    @exception_bridge
    def right_flank_rating(self: "Self") -> "_471.GearFlankRating":
        """mastapy.gears.rating.GearFlankRating

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "RightFlankRating")

        if temp is None:
            return None

        type_ = temp.GetType()
        return constructor.new(type_.Namespace, type_.Name)(temp)

    @property
    def cast_to(self: "Self") -> "_Cast_FaceGearDutyCycleRating":
        """Cast to another type.

        Returns:
            _Cast_FaceGearDutyCycleRating
        """
        return _Cast_FaceGearDutyCycleRating(self)
