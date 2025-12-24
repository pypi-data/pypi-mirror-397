"""StraightBevelGearMeshRating"""

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
from mastapy._private.gears.rating.bevel import _667

_STRAIGHT_BEVEL_GEAR_MESH_RATING = python_net_import(
    "SMT.MastaAPI.Gears.Rating.StraightBevel", "StraightBevelGearMeshRating"
)

if TYPE_CHECKING:
    from typing import Any, List, Type, TypeVar

    from mastapy._private.gears.analysis import _1362
    from mastapy._private.gears.gear_designs.straight_bevel import _1088
    from mastapy._private.gears.rating import _465, _473
    from mastapy._private.gears.rating.agma_gleason_conical import _678
    from mastapy._private.gears.rating.conical import _652
    from mastapy._private.gears.rating.straight_bevel import _509

    Self = TypeVar("Self", bound="StraightBevelGearMeshRating")
    CastSelf = TypeVar(
        "CastSelf",
        bound="StraightBevelGearMeshRating._Cast_StraightBevelGearMeshRating",
    )


__docformat__ = "restructuredtext en"
__all__ = ("StraightBevelGearMeshRating",)


@extended_dataclass(frozen=True, slots=True, weakref_slot=True)
class _Cast_StraightBevelGearMeshRating:
    """Special nested class for casting StraightBevelGearMeshRating to subclasses."""

    __parent__: "StraightBevelGearMeshRating"

    @property
    def bevel_gear_mesh_rating(self: "CastSelf") -> "_667.BevelGearMeshRating":
        return self.__parent__._cast(_667.BevelGearMeshRating)

    @property
    def agma_gleason_conical_gear_mesh_rating(
        self: "CastSelf",
    ) -> "_678.AGMAGleasonConicalGearMeshRating":
        from mastapy._private.gears.rating.agma_gleason_conical import _678

        return self.__parent__._cast(_678.AGMAGleasonConicalGearMeshRating)

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
    def straight_bevel_gear_mesh_rating(
        self: "CastSelf",
    ) -> "StraightBevelGearMeshRating":
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
class StraightBevelGearMeshRating(_667.BevelGearMeshRating):
    """StraightBevelGearMeshRating

    This is a mastapy class.
    """

    TYPE: ClassVar["Type"] = _STRAIGHT_BEVEL_GEAR_MESH_RATING

    wrapped: "Any"

    def __post_init__(self: "Self") -> None:
        """Override of the post initialisation magic method."""
        if not hasattr(self.wrapped, "reference_count"):
            self.wrapped.reference_count = 0

        self.wrapped.reference_count += 1

    @property
    @exception_bridge
    def straight_bevel_gear_mesh(self: "Self") -> "_1088.StraightBevelGearMeshDesign":
        """mastapy.gears.gear_designs.straight_bevel.StraightBevelGearMeshDesign

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "StraightBevelGearMesh")

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
    def cast_to(self: "Self") -> "_Cast_StraightBevelGearMeshRating":
        """Cast to another type.

        Returns:
            _Cast_StraightBevelGearMeshRating
        """
        return _Cast_StraightBevelGearMeshRating(self)
