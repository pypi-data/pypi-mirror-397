"""AGMAGleasonConicalGearSetRating"""

from __future__ import annotations

from typing import TYPE_CHECKING, ClassVar

from mastapy._private._internal.dataclasses import extended_dataclass
from mastapy._private._internal.exceptions import CastException
from mastapy._private._internal.python_net import python_net_import

from mastapy._private._internal import utility
from mastapy._private.gears.rating.conical import _655

_AGMA_GLEASON_CONICAL_GEAR_SET_RATING = python_net_import(
    "SMT.MastaAPI.Gears.Rating.AGMAGleasonConical", "AGMAGleasonConicalGearSetRating"
)

if TYPE_CHECKING:
    from typing import Any, Type, TypeVar

    from mastapy._private.gears.analysis import _1363
    from mastapy._private.gears.rating import _467, _476
    from mastapy._private.gears.rating.bevel import _669
    from mastapy._private.gears.rating.hypoid import _553
    from mastapy._private.gears.rating.spiral_bevel import _517
    from mastapy._private.gears.rating.straight_bevel import _510
    from mastapy._private.gears.rating.zerol_bevel import _484

    Self = TypeVar("Self", bound="AGMAGleasonConicalGearSetRating")
    CastSelf = TypeVar(
        "CastSelf",
        bound="AGMAGleasonConicalGearSetRating._Cast_AGMAGleasonConicalGearSetRating",
    )


__docformat__ = "restructuredtext en"
__all__ = ("AGMAGleasonConicalGearSetRating",)


@extended_dataclass(frozen=True, slots=True, weakref_slot=True)
class _Cast_AGMAGleasonConicalGearSetRating:
    """Special nested class for casting AGMAGleasonConicalGearSetRating to subclasses."""

    __parent__: "AGMAGleasonConicalGearSetRating"

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
    def zerol_bevel_gear_set_rating(self: "CastSelf") -> "_484.ZerolBevelGearSetRating":
        from mastapy._private.gears.rating.zerol_bevel import _484

        return self.__parent__._cast(_484.ZerolBevelGearSetRating)

    @property
    def straight_bevel_gear_set_rating(
        self: "CastSelf",
    ) -> "_510.StraightBevelGearSetRating":
        from mastapy._private.gears.rating.straight_bevel import _510

        return self.__parent__._cast(_510.StraightBevelGearSetRating)

    @property
    def spiral_bevel_gear_set_rating(
        self: "CastSelf",
    ) -> "_517.SpiralBevelGearSetRating":
        from mastapy._private.gears.rating.spiral_bevel import _517

        return self.__parent__._cast(_517.SpiralBevelGearSetRating)

    @property
    def hypoid_gear_set_rating(self: "CastSelf") -> "_553.HypoidGearSetRating":
        from mastapy._private.gears.rating.hypoid import _553

        return self.__parent__._cast(_553.HypoidGearSetRating)

    @property
    def bevel_gear_set_rating(self: "CastSelf") -> "_669.BevelGearSetRating":
        from mastapy._private.gears.rating.bevel import _669

        return self.__parent__._cast(_669.BevelGearSetRating)

    @property
    def agma_gleason_conical_gear_set_rating(
        self: "CastSelf",
    ) -> "AGMAGleasonConicalGearSetRating":
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
class AGMAGleasonConicalGearSetRating(_655.ConicalGearSetRating):
    """AGMAGleasonConicalGearSetRating

    This is a mastapy class.
    """

    TYPE: ClassVar["Type"] = _AGMA_GLEASON_CONICAL_GEAR_SET_RATING

    wrapped: "Any"

    def __post_init__(self: "Self") -> None:
        """Override of the post initialisation magic method."""
        if not hasattr(self.wrapped, "reference_count"):
            self.wrapped.reference_count = 0

        self.wrapped.reference_count += 1

    @property
    def cast_to(self: "Self") -> "_Cast_AGMAGleasonConicalGearSetRating":
        """Cast to another type.

        Returns:
            _Cast_AGMAGleasonConicalGearSetRating
        """
        return _Cast_AGMAGleasonConicalGearSetRating(self)
