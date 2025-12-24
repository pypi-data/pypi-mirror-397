"""KlingelnbergCycloPalloidSpiralBevelGearSetRating"""

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
from mastapy._private.gears.rating.klingelnberg_conical import _526

_KLINGELNBERG_CYCLO_PALLOID_SPIRAL_BEVEL_GEAR_SET_RATING = python_net_import(
    "SMT.MastaAPI.Gears.Rating.KlingelnbergSpiralBevel",
    "KlingelnbergCycloPalloidSpiralBevelGearSetRating",
)

if TYPE_CHECKING:
    from typing import Any, List, Type, TypeVar

    from mastapy._private.gears.analysis import _1363
    from mastapy._private.gears.gear_designs.klingelnberg_spiral_bevel import _1101
    from mastapy._private.gears.rating import _467, _476
    from mastapy._private.gears.rating.conical import _655
    from mastapy._private.gears.rating.klingelnberg_spiral_bevel import _518, _519

    Self = TypeVar("Self", bound="KlingelnbergCycloPalloidSpiralBevelGearSetRating")
    CastSelf = TypeVar(
        "CastSelf",
        bound="KlingelnbergCycloPalloidSpiralBevelGearSetRating._Cast_KlingelnbergCycloPalloidSpiralBevelGearSetRating",
    )


__docformat__ = "restructuredtext en"
__all__ = ("KlingelnbergCycloPalloidSpiralBevelGearSetRating",)


@extended_dataclass(frozen=True, slots=True, weakref_slot=True)
class _Cast_KlingelnbergCycloPalloidSpiralBevelGearSetRating:
    """Special nested class for casting KlingelnbergCycloPalloidSpiralBevelGearSetRating to subclasses."""

    __parent__: "KlingelnbergCycloPalloidSpiralBevelGearSetRating"

    @property
    def klingelnberg_cyclo_palloid_conical_gear_set_rating(
        self: "CastSelf",
    ) -> "_526.KlingelnbergCycloPalloidConicalGearSetRating":
        return self.__parent__._cast(_526.KlingelnbergCycloPalloidConicalGearSetRating)

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
    def klingelnberg_cyclo_palloid_spiral_bevel_gear_set_rating(
        self: "CastSelf",
    ) -> "KlingelnbergCycloPalloidSpiralBevelGearSetRating":
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
class KlingelnbergCycloPalloidSpiralBevelGearSetRating(
    _526.KlingelnbergCycloPalloidConicalGearSetRating
):
    """KlingelnbergCycloPalloidSpiralBevelGearSetRating

    This is a mastapy class.
    """

    TYPE: ClassVar["Type"] = _KLINGELNBERG_CYCLO_PALLOID_SPIRAL_BEVEL_GEAR_SET_RATING

    wrapped: "Any"

    def __post_init__(self: "Self") -> None:
        """Override of the post initialisation magic method."""
        if not hasattr(self.wrapped, "reference_count"):
            self.wrapped.reference_count = 0

        self.wrapped.reference_count += 1

    @property
    @exception_bridge
    def klingelnberg_cyclo_palloid_spiral_bevel_gear_set(
        self: "Self",
    ) -> "_1101.KlingelnbergCycloPalloidSpiralBevelGearSetDesign":
        """mastapy.gears.gear_designs.klingelnberg_spiral_bevel.KlingelnbergCycloPalloidSpiralBevelGearSetDesign

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(
            self.wrapped, "KlingelnbergCycloPalloidSpiralBevelGearSet"
        )

        if temp is None:
            return None

        type_ = temp.GetType()
        return constructor.new(type_.Namespace, type_.Name)(temp)

    @property
    @exception_bridge
    def klingelnberg_cyclo_palloid_spiral_bevel_gear_ratings(
        self: "Self",
    ) -> "List[_519.KlingelnbergCycloPalloidSpiralBevelGearRating]":
        """List[mastapy.gears.rating.klingelnberg_spiral_bevel.KlingelnbergCycloPalloidSpiralBevelGearRating]

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(
            self.wrapped, "KlingelnbergCycloPalloidSpiralBevelGearRatings"
        )

        if temp is None:
            return None

        value = conversion.pn_to_mp_objects_in_list(temp)

        if value is None:
            return None

        return value

    @property
    @exception_bridge
    def klingelnberg_cyclo_palloid_spiral_bevel_mesh_ratings(
        self: "Self",
    ) -> "List[_518.KlingelnbergCycloPalloidSpiralBevelGearMeshRating]":
        """List[mastapy.gears.rating.klingelnberg_spiral_bevel.KlingelnbergCycloPalloidSpiralBevelGearMeshRating]

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(
            self.wrapped, "KlingelnbergCycloPalloidSpiralBevelMeshRatings"
        )

        if temp is None:
            return None

        value = conversion.pn_to_mp_objects_in_list(temp)

        if value is None:
            return None

        return value

    @property
    def cast_to(
        self: "Self",
    ) -> "_Cast_KlingelnbergCycloPalloidSpiralBevelGearSetRating":
        """Cast to another type.

        Returns:
            _Cast_KlingelnbergCycloPalloidSpiralBevelGearSetRating
        """
        return _Cast_KlingelnbergCycloPalloidSpiralBevelGearSetRating(self)
