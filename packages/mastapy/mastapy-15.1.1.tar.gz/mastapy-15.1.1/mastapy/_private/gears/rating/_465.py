"""AbstractGearMeshRating"""

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
from mastapy._private.gears.analysis import _1362

_ABSTRACT_GEAR_MESH_RATING = python_net_import(
    "SMT.MastaAPI.Gears.Rating", "AbstractGearMeshRating"
)

if TYPE_CHECKING:
    from typing import Any, Type, TypeVar

    from mastapy._private.gears.rating import _473, _478
    from mastapy._private.gears.rating.agma_gleason_conical import _678
    from mastapy._private.gears.rating.bevel import _667
    from mastapy._private.gears.rating.concept import _662, _663
    from mastapy._private.gears.rating.conical import _652, _657
    from mastapy._private.gears.rating.cylindrical import _571, _579
    from mastapy._private.gears.rating.face import _559, _560
    from mastapy._private.gears.rating.hypoid import _551
    from mastapy._private.gears.rating.klingelnberg_conical import _524
    from mastapy._private.gears.rating.klingelnberg_hypoid import _521
    from mastapy._private.gears.rating.klingelnberg_spiral_bevel import _518
    from mastapy._private.gears.rating.spiral_bevel import _515
    from mastapy._private.gears.rating.straight_bevel import _508
    from mastapy._private.gears.rating.straight_bevel_diff import _511
    from mastapy._private.gears.rating.worm import _486, _490
    from mastapy._private.gears.rating.zerol_bevel import _482

    Self = TypeVar("Self", bound="AbstractGearMeshRating")
    CastSelf = TypeVar(
        "CastSelf", bound="AbstractGearMeshRating._Cast_AbstractGearMeshRating"
    )


__docformat__ = "restructuredtext en"
__all__ = ("AbstractGearMeshRating",)


@extended_dataclass(frozen=True, slots=True, weakref_slot=True)
class _Cast_AbstractGearMeshRating:
    """Special nested class for casting AbstractGearMeshRating to subclasses."""

    __parent__: "AbstractGearMeshRating"

    @property
    def abstract_gear_mesh_analysis(
        self: "CastSelf",
    ) -> "_1362.AbstractGearMeshAnalysis":
        return self.__parent__._cast(_1362.AbstractGearMeshAnalysis)

    @property
    def gear_mesh_rating(self: "CastSelf") -> "_473.GearMeshRating":
        from mastapy._private.gears.rating import _473

        return self.__parent__._cast(_473.GearMeshRating)

    @property
    def mesh_duty_cycle_rating(self: "CastSelf") -> "_478.MeshDutyCycleRating":
        from mastapy._private.gears.rating import _478

        return self.__parent__._cast(_478.MeshDutyCycleRating)

    @property
    def zerol_bevel_gear_mesh_rating(
        self: "CastSelf",
    ) -> "_482.ZerolBevelGearMeshRating":
        from mastapy._private.gears.rating.zerol_bevel import _482

        return self.__parent__._cast(_482.ZerolBevelGearMeshRating)

    @property
    def worm_gear_mesh_rating(self: "CastSelf") -> "_486.WormGearMeshRating":
        from mastapy._private.gears.rating.worm import _486

        return self.__parent__._cast(_486.WormGearMeshRating)

    @property
    def worm_mesh_duty_cycle_rating(self: "CastSelf") -> "_490.WormMeshDutyCycleRating":
        from mastapy._private.gears.rating.worm import _490

        return self.__parent__._cast(_490.WormMeshDutyCycleRating)

    @property
    def straight_bevel_gear_mesh_rating(
        self: "CastSelf",
    ) -> "_508.StraightBevelGearMeshRating":
        from mastapy._private.gears.rating.straight_bevel import _508

        return self.__parent__._cast(_508.StraightBevelGearMeshRating)

    @property
    def straight_bevel_diff_gear_mesh_rating(
        self: "CastSelf",
    ) -> "_511.StraightBevelDiffGearMeshRating":
        from mastapy._private.gears.rating.straight_bevel_diff import _511

        return self.__parent__._cast(_511.StraightBevelDiffGearMeshRating)

    @property
    def spiral_bevel_gear_mesh_rating(
        self: "CastSelf",
    ) -> "_515.SpiralBevelGearMeshRating":
        from mastapy._private.gears.rating.spiral_bevel import _515

        return self.__parent__._cast(_515.SpiralBevelGearMeshRating)

    @property
    def klingelnberg_cyclo_palloid_spiral_bevel_gear_mesh_rating(
        self: "CastSelf",
    ) -> "_518.KlingelnbergCycloPalloidSpiralBevelGearMeshRating":
        from mastapy._private.gears.rating.klingelnberg_spiral_bevel import _518

        return self.__parent__._cast(
            _518.KlingelnbergCycloPalloidSpiralBevelGearMeshRating
        )

    @property
    def klingelnberg_cyclo_palloid_hypoid_gear_mesh_rating(
        self: "CastSelf",
    ) -> "_521.KlingelnbergCycloPalloidHypoidGearMeshRating":
        from mastapy._private.gears.rating.klingelnberg_hypoid import _521

        return self.__parent__._cast(_521.KlingelnbergCycloPalloidHypoidGearMeshRating)

    @property
    def klingelnberg_cyclo_palloid_conical_gear_mesh_rating(
        self: "CastSelf",
    ) -> "_524.KlingelnbergCycloPalloidConicalGearMeshRating":
        from mastapy._private.gears.rating.klingelnberg_conical import _524

        return self.__parent__._cast(_524.KlingelnbergCycloPalloidConicalGearMeshRating)

    @property
    def hypoid_gear_mesh_rating(self: "CastSelf") -> "_551.HypoidGearMeshRating":
        from mastapy._private.gears.rating.hypoid import _551

        return self.__parent__._cast(_551.HypoidGearMeshRating)

    @property
    def face_gear_mesh_duty_cycle_rating(
        self: "CastSelf",
    ) -> "_559.FaceGearMeshDutyCycleRating":
        from mastapy._private.gears.rating.face import _559

        return self.__parent__._cast(_559.FaceGearMeshDutyCycleRating)

    @property
    def face_gear_mesh_rating(self: "CastSelf") -> "_560.FaceGearMeshRating":
        from mastapy._private.gears.rating.face import _560

        return self.__parent__._cast(_560.FaceGearMeshRating)

    @property
    def cylindrical_gear_mesh_rating(
        self: "CastSelf",
    ) -> "_571.CylindricalGearMeshRating":
        from mastapy._private.gears.rating.cylindrical import _571

        return self.__parent__._cast(_571.CylindricalGearMeshRating)

    @property
    def cylindrical_mesh_duty_cycle_rating(
        self: "CastSelf",
    ) -> "_579.CylindricalMeshDutyCycleRating":
        from mastapy._private.gears.rating.cylindrical import _579

        return self.__parent__._cast(_579.CylindricalMeshDutyCycleRating)

    @property
    def conical_gear_mesh_rating(self: "CastSelf") -> "_652.ConicalGearMeshRating":
        from mastapy._private.gears.rating.conical import _652

        return self.__parent__._cast(_652.ConicalGearMeshRating)

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
    def concept_gear_mesh_rating(self: "CastSelf") -> "_663.ConceptGearMeshRating":
        from mastapy._private.gears.rating.concept import _663

        return self.__parent__._cast(_663.ConceptGearMeshRating)

    @property
    def bevel_gear_mesh_rating(self: "CastSelf") -> "_667.BevelGearMeshRating":
        from mastapy._private.gears.rating.bevel import _667

        return self.__parent__._cast(_667.BevelGearMeshRating)

    @property
    def agma_gleason_conical_gear_mesh_rating(
        self: "CastSelf",
    ) -> "_678.AGMAGleasonConicalGearMeshRating":
        from mastapy._private.gears.rating.agma_gleason_conical import _678

        return self.__parent__._cast(_678.AGMAGleasonConicalGearMeshRating)

    @property
    def abstract_gear_mesh_rating(self: "CastSelf") -> "AbstractGearMeshRating":
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
class AbstractGearMeshRating(_1362.AbstractGearMeshAnalysis):
    """AbstractGearMeshRating

    This is a mastapy class.
    """

    TYPE: ClassVar["Type"] = _ABSTRACT_GEAR_MESH_RATING

    wrapped: "Any"

    def __post_init__(self: "Self") -> None:
        """Override of the post initialisation magic method."""
        if not hasattr(self.wrapped, "reference_count"):
            self.wrapped.reference_count = 0

        self.wrapped.reference_count += 1

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
    def normalised_safety_factor_for_fatigue(self: "Self") -> "float":
        """float

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "NormalisedSafetyFactorForFatigue")

        if temp is None:
            return 0.0

        return temp

    @property
    @exception_bridge
    def normalised_safety_factor_for_fatigue_and_static(self: "Self") -> "float":
        """float

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(
            self.wrapped, "NormalisedSafetyFactorForFatigueAndStatic"
        )

        if temp is None:
            return 0.0

        return temp

    @property
    @exception_bridge
    def normalised_safety_factor_for_static(self: "Self") -> "float":
        """float

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "NormalisedSafetyFactorForStatic")

        if temp is None:
            return 0.0

        return temp

    @property
    def cast_to(self: "Self") -> "_Cast_AbstractGearMeshRating":
        """Cast to another type.

        Returns:
            _Cast_AbstractGearMeshRating
        """
        return _Cast_AbstractGearMeshRating(self)
