"""MeshDutyCycleRating"""

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
from mastapy._private.gears.rating import _465

_MESH_DUTY_CYCLE_RATING = python_net_import(
    "SMT.MastaAPI.Gears.Rating", "MeshDutyCycleRating"
)

if TYPE_CHECKING:
    from typing import Any, List, Type, TypeVar

    from mastapy._private.gears.analysis import _1362
    from mastapy._private.gears.rating import _470, _475
    from mastapy._private.gears.rating.concept import _662
    from mastapy._private.gears.rating.conical import _657
    from mastapy._private.gears.rating.cylindrical import _579
    from mastapy._private.gears.rating.face import _559
    from mastapy._private.gears.rating.worm import _490

    Self = TypeVar("Self", bound="MeshDutyCycleRating")
    CastSelf = TypeVar(
        "CastSelf", bound="MeshDutyCycleRating._Cast_MeshDutyCycleRating"
    )


__docformat__ = "restructuredtext en"
__all__ = ("MeshDutyCycleRating",)


@extended_dataclass(frozen=True, slots=True, weakref_slot=True)
class _Cast_MeshDutyCycleRating:
    """Special nested class for casting MeshDutyCycleRating to subclasses."""

    __parent__: "MeshDutyCycleRating"

    @property
    def abstract_gear_mesh_rating(self: "CastSelf") -> "_465.AbstractGearMeshRating":
        return self.__parent__._cast(_465.AbstractGearMeshRating)

    @property
    def abstract_gear_mesh_analysis(
        self: "CastSelf",
    ) -> "_1362.AbstractGearMeshAnalysis":
        from mastapy._private.gears.analysis import _1362

        return self.__parent__._cast(_1362.AbstractGearMeshAnalysis)

    @property
    def worm_mesh_duty_cycle_rating(self: "CastSelf") -> "_490.WormMeshDutyCycleRating":
        from mastapy._private.gears.rating.worm import _490

        return self.__parent__._cast(_490.WormMeshDutyCycleRating)

    @property
    def face_gear_mesh_duty_cycle_rating(
        self: "CastSelf",
    ) -> "_559.FaceGearMeshDutyCycleRating":
        from mastapy._private.gears.rating.face import _559

        return self.__parent__._cast(_559.FaceGearMeshDutyCycleRating)

    @property
    def cylindrical_mesh_duty_cycle_rating(
        self: "CastSelf",
    ) -> "_579.CylindricalMeshDutyCycleRating":
        from mastapy._private.gears.rating.cylindrical import _579

        return self.__parent__._cast(_579.CylindricalMeshDutyCycleRating)

    @property
    def conical_mesh_duty_cycle_rating(
        self: "CastSelf",
    ) -> "_657.ConicalMeshDutyCycleRating":
        from mastapy._private.gears.rating.conical import _657

        return self.__parent__._cast(_657.ConicalMeshDutyCycleRating)

    @property
    def concept_gear_mesh_duty_cycle_rating(
        self: "CastSelf",
    ) -> "_662.ConceptGearMeshDutyCycleRating":
        from mastapy._private.gears.rating.concept import _662

        return self.__parent__._cast(_662.ConceptGearMeshDutyCycleRating)

    @property
    def mesh_duty_cycle_rating(self: "CastSelf") -> "MeshDutyCycleRating":
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
class MeshDutyCycleRating(_465.AbstractGearMeshRating):
    """MeshDutyCycleRating

    This is a mastapy class.
    """

    TYPE: ClassVar["Type"] = _MESH_DUTY_CYCLE_RATING

    wrapped: "Any"

    def __post_init__(self: "Self") -> None:
        """Override of the post initialisation magic method."""
        if not hasattr(self.wrapped, "reference_count"):
            self.wrapped.reference_count = 0

        self.wrapped.reference_count += 1

    @property
    @exception_bridge
    def calculated_energy_loss(self: "Self") -> "float":
        """float

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "CalculatedEnergyLoss")

        if temp is None:
            return 0.0

        return temp

    @property
    @exception_bridge
    def calculated_mesh_efficiency(self: "Self") -> "float":
        """float

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "CalculatedMeshEfficiency")

        if temp is None:
            return 0.0

        return temp

    @property
    @exception_bridge
    def total_energy(self: "Self") -> "float":
        """float

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "TotalEnergy")

        if temp is None:
            return 0.0

        return temp

    @property
    @exception_bridge
    def gear_duty_cycle_ratings(self: "Self") -> "List[_470.GearDutyCycleRating]":
        """List[mastapy.gears.rating.GearDutyCycleRating]

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "GearDutyCycleRatings")

        if temp is None:
            return None

        value = conversion.pn_to_mp_objects_in_list(temp)

        if value is None:
            return None

        return value

    @property
    @exception_bridge
    def gear_set(self: "Self") -> "_475.GearSetDutyCycleRating":
        """mastapy.gears.rating.GearSetDutyCycleRating

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "GearSet")

        if temp is None:
            return None

        type_ = temp.GetType()
        return constructor.new(type_.Namespace, type_.Name)(temp)

    @property
    def cast_to(self: "Self") -> "_Cast_MeshDutyCycleRating":
        """Cast to another type.

        Returns:
            _Cast_MeshDutyCycleRating
        """
        return _Cast_MeshDutyCycleRating(self)
