"""ConicalGearRating"""

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
from mastapy._private.gears.rating import _474

_CONICAL_GEAR_RATING = python_net_import(
    "SMT.MastaAPI.Gears.Rating.Conical", "ConicalGearRating"
)

if TYPE_CHECKING:
    from typing import Any, Type, TypeVar

    from mastapy._private.gears.analysis import _1361
    from mastapy._private.gears.rating import _466, _471
    from mastapy._private.gears.rating.agma_gleason_conical import _679
    from mastapy._private.gears.rating.bevel import _668
    from mastapy._private.gears.rating.hypoid import _552
    from mastapy._private.gears.rating.klingelnberg_conical import _525
    from mastapy._private.gears.rating.klingelnberg_hypoid import _522
    from mastapy._private.gears.rating.klingelnberg_spiral_bevel import _519
    from mastapy._private.gears.rating.spiral_bevel import _516
    from mastapy._private.gears.rating.straight_bevel import _509
    from mastapy._private.gears.rating.straight_bevel_diff import _512
    from mastapy._private.gears.rating.zerol_bevel import _483

    Self = TypeVar("Self", bound="ConicalGearRating")
    CastSelf = TypeVar("CastSelf", bound="ConicalGearRating._Cast_ConicalGearRating")


__docformat__ = "restructuredtext en"
__all__ = ("ConicalGearRating",)


@extended_dataclass(frozen=True, slots=True, weakref_slot=True)
class _Cast_ConicalGearRating:
    """Special nested class for casting ConicalGearRating to subclasses."""

    __parent__: "ConicalGearRating"

    @property
    def gear_rating(self: "CastSelf") -> "_474.GearRating":
        return self.__parent__._cast(_474.GearRating)

    @property
    def abstract_gear_rating(self: "CastSelf") -> "_466.AbstractGearRating":
        from mastapy._private.gears.rating import _466

        return self.__parent__._cast(_466.AbstractGearRating)

    @property
    def abstract_gear_analysis(self: "CastSelf") -> "_1361.AbstractGearAnalysis":
        from mastapy._private.gears.analysis import _1361

        return self.__parent__._cast(_1361.AbstractGearAnalysis)

    @property
    def zerol_bevel_gear_rating(self: "CastSelf") -> "_483.ZerolBevelGearRating":
        from mastapy._private.gears.rating.zerol_bevel import _483

        return self.__parent__._cast(_483.ZerolBevelGearRating)

    @property
    def straight_bevel_gear_rating(self: "CastSelf") -> "_509.StraightBevelGearRating":
        from mastapy._private.gears.rating.straight_bevel import _509

        return self.__parent__._cast(_509.StraightBevelGearRating)

    @property
    def straight_bevel_diff_gear_rating(
        self: "CastSelf",
    ) -> "_512.StraightBevelDiffGearRating":
        from mastapy._private.gears.rating.straight_bevel_diff import _512

        return self.__parent__._cast(_512.StraightBevelDiffGearRating)

    @property
    def spiral_bevel_gear_rating(self: "CastSelf") -> "_516.SpiralBevelGearRating":
        from mastapy._private.gears.rating.spiral_bevel import _516

        return self.__parent__._cast(_516.SpiralBevelGearRating)

    @property
    def klingelnberg_cyclo_palloid_spiral_bevel_gear_rating(
        self: "CastSelf",
    ) -> "_519.KlingelnbergCycloPalloidSpiralBevelGearRating":
        from mastapy._private.gears.rating.klingelnberg_spiral_bevel import _519

        return self.__parent__._cast(_519.KlingelnbergCycloPalloidSpiralBevelGearRating)

    @property
    def klingelnberg_cyclo_palloid_hypoid_gear_rating(
        self: "CastSelf",
    ) -> "_522.KlingelnbergCycloPalloidHypoidGearRating":
        from mastapy._private.gears.rating.klingelnberg_hypoid import _522

        return self.__parent__._cast(_522.KlingelnbergCycloPalloidHypoidGearRating)

    @property
    def klingelnberg_cyclo_palloid_conical_gear_rating(
        self: "CastSelf",
    ) -> "_525.KlingelnbergCycloPalloidConicalGearRating":
        from mastapy._private.gears.rating.klingelnberg_conical import _525

        return self.__parent__._cast(_525.KlingelnbergCycloPalloidConicalGearRating)

    @property
    def hypoid_gear_rating(self: "CastSelf") -> "_552.HypoidGearRating":
        from mastapy._private.gears.rating.hypoid import _552

        return self.__parent__._cast(_552.HypoidGearRating)

    @property
    def bevel_gear_rating(self: "CastSelf") -> "_668.BevelGearRating":
        from mastapy._private.gears.rating.bevel import _668

        return self.__parent__._cast(_668.BevelGearRating)

    @property
    def agma_gleason_conical_gear_rating(
        self: "CastSelf",
    ) -> "_679.AGMAGleasonConicalGearRating":
        from mastapy._private.gears.rating.agma_gleason_conical import _679

        return self.__parent__._cast(_679.AGMAGleasonConicalGearRating)

    @property
    def conical_gear_rating(self: "CastSelf") -> "ConicalGearRating":
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
class ConicalGearRating(_474.GearRating):
    """ConicalGearRating

    This is a mastapy class.
    """

    TYPE: ClassVar["Type"] = _CONICAL_GEAR_RATING

    wrapped: "Any"

    def __post_init__(self: "Self") -> None:
        """Override of the post initialisation magic method."""
        if not hasattr(self.wrapped, "reference_count"):
            self.wrapped.reference_count = 0

        self.wrapped.reference_count += 1

    @property
    @exception_bridge
    def concave_flank_rating(self: "Self") -> "_471.GearFlankRating":
        """mastapy.gears.rating.GearFlankRating

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "ConcaveFlankRating")

        if temp is None:
            return None

        type_ = temp.GetType()
        return constructor.new(type_.Namespace, type_.Name)(temp)

    @property
    @exception_bridge
    def convex_flank_rating(self: "Self") -> "_471.GearFlankRating":
        """mastapy.gears.rating.GearFlankRating

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "ConvexFlankRating")

        if temp is None:
            return None

        type_ = temp.GetType()
        return constructor.new(type_.Namespace, type_.Name)(temp)

    @property
    def cast_to(self: "Self") -> "_Cast_ConicalGearRating":
        """Cast to another type.

        Returns:
            _Cast_ConicalGearRating
        """
        return _Cast_ConicalGearRating(self)
