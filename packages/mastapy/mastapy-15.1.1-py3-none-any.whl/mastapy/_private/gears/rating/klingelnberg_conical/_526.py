"""KlingelnbergCycloPalloidConicalGearSetRating"""

from __future__ import annotations

from typing import TYPE_CHECKING, ClassVar

from mastapy._private._internal.dataclasses import extended_dataclass
from mastapy._private._internal.exception_bridge import exception_bridge
from mastapy._private._internal.exceptions import CastException
from mastapy._private._internal.python_net import (
    python_net_import,
    pythonnet_property_get,
)

from mastapy._private._internal import utility
from mastapy._private.gears.rating.conical import _655

_KLINGELNBERG_CYCLO_PALLOID_CONICAL_GEAR_SET_RATING = python_net_import(
    "SMT.MastaAPI.Gears.Rating.KlingelnbergConical",
    "KlingelnbergCycloPalloidConicalGearSetRating",
)

if TYPE_CHECKING:
    from typing import Any, Type, TypeVar

    from mastapy._private.gears.analysis import _1363
    from mastapy._private.gears.rating import _467, _476
    from mastapy._private.gears.rating.klingelnberg_hypoid import _523
    from mastapy._private.gears.rating.klingelnberg_spiral_bevel import _520

    Self = TypeVar("Self", bound="KlingelnbergCycloPalloidConicalGearSetRating")
    CastSelf = TypeVar(
        "CastSelf",
        bound="KlingelnbergCycloPalloidConicalGearSetRating._Cast_KlingelnbergCycloPalloidConicalGearSetRating",
    )


__docformat__ = "restructuredtext en"
__all__ = ("KlingelnbergCycloPalloidConicalGearSetRating",)


@extended_dataclass(frozen=True, slots=True, weakref_slot=True)
class _Cast_KlingelnbergCycloPalloidConicalGearSetRating:
    """Special nested class for casting KlingelnbergCycloPalloidConicalGearSetRating to subclasses."""

    __parent__: "KlingelnbergCycloPalloidConicalGearSetRating"

    @property
    def conical_gear_set_rating(self: "CastSelf") -> "_655.ConicalGearSetRating":
        return self.__parent__._cast(_655.ConicalGearSetRating)

    @property
    def gear_set_rating(self: "CastSelf") -> "_476.GearSetRating":
        from mastapy._private.gears.rating import _476

        return self.__parent__._cast(_476.GearSetRating)

    @property
    def abstract_gear_set_rating(self: "CastSelf") -> "_467.AbstractGearSetRating":
        from mastapy._private.gears.rating import _467

        return self.__parent__._cast(_467.AbstractGearSetRating)

    @property
    def abstract_gear_set_analysis(self: "CastSelf") -> "_1363.AbstractGearSetAnalysis":
        from mastapy._private.gears.analysis import _1363

        return self.__parent__._cast(_1363.AbstractGearSetAnalysis)

    @property
    def klingelnberg_cyclo_palloid_spiral_bevel_gear_set_rating(
        self: "CastSelf",
    ) -> "_520.KlingelnbergCycloPalloidSpiralBevelGearSetRating":
        from mastapy._private.gears.rating.klingelnberg_spiral_bevel import _520

        return self.__parent__._cast(
            _520.KlingelnbergCycloPalloidSpiralBevelGearSetRating
        )

    @property
    def klingelnberg_cyclo_palloid_hypoid_gear_set_rating(
        self: "CastSelf",
    ) -> "_523.KlingelnbergCycloPalloidHypoidGearSetRating":
        from mastapy._private.gears.rating.klingelnberg_hypoid import _523

        return self.__parent__._cast(_523.KlingelnbergCycloPalloidHypoidGearSetRating)

    @property
    def klingelnberg_cyclo_palloid_conical_gear_set_rating(
        self: "CastSelf",
    ) -> "KlingelnbergCycloPalloidConicalGearSetRating":
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
class KlingelnbergCycloPalloidConicalGearSetRating(_655.ConicalGearSetRating):
    """KlingelnbergCycloPalloidConicalGearSetRating

    This is a mastapy class.
    """

    TYPE: ClassVar["Type"] = _KLINGELNBERG_CYCLO_PALLOID_CONICAL_GEAR_SET_RATING

    wrapped: "Any"

    def __post_init__(self: "Self") -> None:
        """Override of the post initialisation magic method."""
        if not hasattr(self.wrapped, "reference_count"):
            self.wrapped.reference_count = 0

        self.wrapped.reference_count += 1

    @property
    @exception_bridge
    def rating(self: "Self") -> "str":
        """str

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "Rating")

        if temp is None:
            return ""

        return temp

    @property
    def cast_to(self: "Self") -> "_Cast_KlingelnbergCycloPalloidConicalGearSetRating":
        """Cast to another type.

        Returns:
            _Cast_KlingelnbergCycloPalloidConicalGearSetRating
        """
        return _Cast_KlingelnbergCycloPalloidConicalGearSetRating(self)
