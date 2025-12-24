"""KlingelnbergCycloPalloidSpiralBevelGearMeshRating"""

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
from mastapy._private.gears.rating.klingelnberg_conical import _524

_KLINGELNBERG_CYCLO_PALLOID_SPIRAL_BEVEL_GEAR_MESH_RATING = python_net_import(
    "SMT.MastaAPI.Gears.Rating.KlingelnbergSpiralBevel",
    "KlingelnbergCycloPalloidSpiralBevelGearMeshRating",
)

if TYPE_CHECKING:
    from typing import Any, List, Type, TypeVar

    from mastapy._private.gears.analysis import _1362
    from mastapy._private.gears.gear_designs.klingelnberg_spiral_bevel import _1100
    from mastapy._private.gears.rating import _465, _473
    from mastapy._private.gears.rating.conical import _652
    from mastapy._private.gears.rating.klingelnberg_conical.kn3030 import _532
    from mastapy._private.gears.rating.klingelnberg_spiral_bevel import _519

    Self = TypeVar("Self", bound="KlingelnbergCycloPalloidSpiralBevelGearMeshRating")
    CastSelf = TypeVar(
        "CastSelf",
        bound="KlingelnbergCycloPalloidSpiralBevelGearMeshRating._Cast_KlingelnbergCycloPalloidSpiralBevelGearMeshRating",
    )


__docformat__ = "restructuredtext en"
__all__ = ("KlingelnbergCycloPalloidSpiralBevelGearMeshRating",)


@extended_dataclass(frozen=True, slots=True, weakref_slot=True)
class _Cast_KlingelnbergCycloPalloidSpiralBevelGearMeshRating:
    """Special nested class for casting KlingelnbergCycloPalloidSpiralBevelGearMeshRating to subclasses."""

    __parent__: "KlingelnbergCycloPalloidSpiralBevelGearMeshRating"

    @property
    def klingelnberg_cyclo_palloid_conical_gear_mesh_rating(
        self: "CastSelf",
    ) -> "_524.KlingelnbergCycloPalloidConicalGearMeshRating":
        return self.__parent__._cast(_524.KlingelnbergCycloPalloidConicalGearMeshRating)

    @property
    def conical_gear_mesh_rating(self: "CastSelf") -> "_652.ConicalGearMeshRating":
        from mastapy._private.gears.rating.conical import _652

        return self.__parent__._cast(_652.ConicalGearMeshRating)

    @property
    def gear_mesh_rating(self: "CastSelf") -> "_473.GearMeshRating":
        from mastapy._private.gears.rating import _473

        return self.__parent__._cast(_473.GearMeshRating)

    @property
    def abstract_gear_mesh_rating(self: "CastSelf") -> "_465.AbstractGearMeshRating":
        from mastapy._private.gears.rating import _465

        return self.__parent__._cast(_465.AbstractGearMeshRating)

    @property
    def abstract_gear_mesh_analysis(
        self: "CastSelf",
    ) -> "_1362.AbstractGearMeshAnalysis":
        from mastapy._private.gears.analysis import _1362

        return self.__parent__._cast(_1362.AbstractGearMeshAnalysis)

    @property
    def klingelnberg_cyclo_palloid_spiral_bevel_gear_mesh_rating(
        self: "CastSelf",
    ) -> "KlingelnbergCycloPalloidSpiralBevelGearMeshRating":
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
class KlingelnbergCycloPalloidSpiralBevelGearMeshRating(
    _524.KlingelnbergCycloPalloidConicalGearMeshRating
):
    """KlingelnbergCycloPalloidSpiralBevelGearMeshRating

    This is a mastapy class.
    """

    TYPE: ClassVar["Type"] = _KLINGELNBERG_CYCLO_PALLOID_SPIRAL_BEVEL_GEAR_MESH_RATING

    wrapped: "Any"

    def __post_init__(self: "Self") -> None:
        """Override of the post initialisation magic method."""
        if not hasattr(self.wrapped, "reference_count"):
            self.wrapped.reference_count = 0

        self.wrapped.reference_count += 1

    @property
    @exception_bridge
    def kn3030_klingelnberg_mesh_single_flank_rating(
        self: "Self",
    ) -> "_532.KlingelnbergCycloPalloidSpiralBevelMeshSingleFlankRating":
        """mastapy.gears.rating.klingelnberg_conical.kn3030.KlingelnbergCycloPalloidSpiralBevelMeshSingleFlankRating

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(
            self.wrapped, "KN3030KlingelnbergMeshSingleFlankRating"
        )

        if temp is None:
            return None

        type_ = temp.GetType()
        return constructor.new(type_.Namespace, type_.Name)(temp)

    @property
    @exception_bridge
    def klingelnberg_cyclo_palloid_spiral_bevel_gear_mesh(
        self: "Self",
    ) -> "_1100.KlingelnbergCycloPalloidSpiralBevelGearMeshDesign":
        """mastapy.gears.gear_designs.klingelnberg_spiral_bevel.KlingelnbergCycloPalloidSpiralBevelGearMeshDesign

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(
            self.wrapped, "KlingelnbergCycloPalloidSpiralBevelGearMesh"
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
    def cast_to(
        self: "Self",
    ) -> "_Cast_KlingelnbergCycloPalloidSpiralBevelGearMeshRating":
        """Cast to another type.

        Returns:
            _Cast_KlingelnbergCycloPalloidSpiralBevelGearMeshRating
        """
        return _Cast_KlingelnbergCycloPalloidSpiralBevelGearMeshRating(self)
