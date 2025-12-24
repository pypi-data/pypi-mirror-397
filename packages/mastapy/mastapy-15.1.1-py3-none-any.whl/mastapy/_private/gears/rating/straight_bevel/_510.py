"""StraightBevelGearSetRating"""

from __future__ import annotations

from typing import TYPE_CHECKING, ClassVar

from mastapy._private._internal.dataclasses import extended_dataclass
from mastapy._private._internal.exception_bridge import exception_bridge
from mastapy._private._internal.exceptions import CastException
from mastapy._private._internal.python_net import (
    python_net_import,
    pythonnet_property_get,
)

from mastapy._private._internal import constructor, conversion, utility
from mastapy._private.gears.rating.bevel import _669

_STRAIGHT_BEVEL_GEAR_SET_RATING = python_net_import(
    "SMT.MastaAPI.Gears.Rating.StraightBevel", "StraightBevelGearSetRating"
)

if TYPE_CHECKING:
    from typing import Any, List, Type, TypeVar

    from mastapy._private.gears.analysis import _1363
    from mastapy._private.gears.gear_designs.straight_bevel import _1089
    from mastapy._private.gears.rating import _467, _476
    from mastapy._private.gears.rating.agma_gleason_conical import _680
    from mastapy._private.gears.rating.conical import _655
    from mastapy._private.gears.rating.straight_bevel import _508, _509

    Self = TypeVar("Self", bound="StraightBevelGearSetRating")
    CastSelf = TypeVar(
        "CastSelf", bound="StraightBevelGearSetRating._Cast_StraightBevelGearSetRating"
    )


__docformat__ = "restructuredtext en"
__all__ = ("StraightBevelGearSetRating",)


@extended_dataclass(frozen=True, slots=True, weakref_slot=True)
class _Cast_StraightBevelGearSetRating:
    """Special nested class for casting StraightBevelGearSetRating to subclasses."""

    __parent__: "StraightBevelGearSetRating"

    @property
    def bevel_gear_set_rating(self: "CastSelf") -> "_669.BevelGearSetRating":
        return self.__parent__._cast(_669.BevelGearSetRating)

    @property
    def agma_gleason_conical_gear_set_rating(
        self: "CastSelf",
    ) -> "_680.AGMAGleasonConicalGearSetRating":
        from mastapy._private.gears.rating.agma_gleason_conical import _680

        return self.__parent__._cast(_680.AGMAGleasonConicalGearSetRating)

    @property
    def conical_gear_set_rating(self: "CastSelf") -> "_655.ConicalGearSetRating":
        from mastapy._private.gears.rating.conical import _655

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
    def straight_bevel_gear_set_rating(
        self: "CastSelf",
    ) -> "StraightBevelGearSetRating":
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
class StraightBevelGearSetRating(_669.BevelGearSetRating):
    """StraightBevelGearSetRating

    This is a mastapy class.
    """

    TYPE: ClassVar["Type"] = _STRAIGHT_BEVEL_GEAR_SET_RATING

    wrapped: "Any"

    def __post_init__(self: "Self") -> None:
        """Override of the post initialisation magic method."""
        if not hasattr(self.wrapped, "reference_count"):
            self.wrapped.reference_count = 0

        self.wrapped.reference_count += 1

    @property
    @exception_bridge
    def straight_bevel_gear_set(self: "Self") -> "_1089.StraightBevelGearSetDesign":
        """mastapy.gears.gear_designs.straight_bevel.StraightBevelGearSetDesign

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "StraightBevelGearSet")

        if temp is None:
            return None

        type_ = temp.GetType()
        return constructor.new(type_.Namespace, type_.Name)(temp)

    @property
    @exception_bridge
    def straight_bevel_gear_ratings(
        self: "Self",
    ) -> "List[_509.StraightBevelGearRating]":
        """List[mastapy.gears.rating.straight_bevel.StraightBevelGearRating]

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "StraightBevelGearRatings")

        if temp is None:
            return None

        value = conversion.pn_to_mp_objects_in_list(temp)

        if value is None:
            return None

        return value

    @property
    @exception_bridge
    def straight_bevel_mesh_ratings(
        self: "Self",
    ) -> "List[_508.StraightBevelGearMeshRating]":
        """List[mastapy.gears.rating.straight_bevel.StraightBevelGearMeshRating]

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "StraightBevelMeshRatings")

        if temp is None:
            return None

        value = conversion.pn_to_mp_objects_in_list(temp)

        if value is None:
            return None

        return value

    @property
    def cast_to(self: "Self") -> "_Cast_StraightBevelGearSetRating":
        """Cast to another type.

        Returns:
            _Cast_StraightBevelGearSetRating
        """
        return _Cast_StraightBevelGearSetRating(self)
