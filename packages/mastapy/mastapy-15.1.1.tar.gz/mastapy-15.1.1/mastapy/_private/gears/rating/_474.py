"""GearRating"""

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
from mastapy._private.gears.rating import _466

_GEAR_RATING = python_net_import("SMT.MastaAPI.Gears.Rating", "GearRating")

if TYPE_CHECKING:
    from typing import Any, List, Type, TypeVar

    from mastapy._private.gears.analysis import _1361
    from mastapy._private.gears.rating import _468, _473
    from mastapy._private.gears.rating.agma_gleason_conical import _679
    from mastapy._private.gears.rating.bevel import _668
    from mastapy._private.gears.rating.concept import _664
    from mastapy._private.gears.rating.conical import _653
    from mastapy._private.gears.rating.cylindrical import _573
    from mastapy._private.gears.rating.face import _561
    from mastapy._private.gears.rating.hypoid import _552
    from mastapy._private.gears.rating.klingelnberg_conical import _525
    from mastapy._private.gears.rating.klingelnberg_hypoid import _522
    from mastapy._private.gears.rating.klingelnberg_spiral_bevel import _519
    from mastapy._private.gears.rating.spiral_bevel import _516
    from mastapy._private.gears.rating.straight_bevel import _509
    from mastapy._private.gears.rating.straight_bevel_diff import _512
    from mastapy._private.gears.rating.worm import _487
    from mastapy._private.gears.rating.zerol_bevel import _483
    from mastapy._private.materials import _382

    Self = TypeVar("Self", bound="GearRating")
    CastSelf = TypeVar("CastSelf", bound="GearRating._Cast_GearRating")


__docformat__ = "restructuredtext en"
__all__ = ("GearRating",)


@extended_dataclass(frozen=True, slots=True, weakref_slot=True)
class _Cast_GearRating:
    """Special nested class for casting GearRating to subclasses."""

    __parent__: "GearRating"

    @property
    def abstract_gear_rating(self: "CastSelf") -> "_466.AbstractGearRating":
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
    def worm_gear_rating(self: "CastSelf") -> "_487.WormGearRating":
        from mastapy._private.gears.rating.worm import _487

        return self.__parent__._cast(_487.WormGearRating)

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
    def face_gear_rating(self: "CastSelf") -> "_561.FaceGearRating":
        from mastapy._private.gears.rating.face import _561

        return self.__parent__._cast(_561.FaceGearRating)

    @property
    def cylindrical_gear_rating(self: "CastSelf") -> "_573.CylindricalGearRating":
        from mastapy._private.gears.rating.cylindrical import _573

        return self.__parent__._cast(_573.CylindricalGearRating)

    @property
    def conical_gear_rating(self: "CastSelf") -> "_653.ConicalGearRating":
        from mastapy._private.gears.rating.conical import _653

        return self.__parent__._cast(_653.ConicalGearRating)

    @property
    def concept_gear_rating(self: "CastSelf") -> "_664.ConceptGearRating":
        from mastapy._private.gears.rating.concept import _664

        return self.__parent__._cast(_664.ConceptGearRating)

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
    def gear_rating(self: "CastSelf") -> "GearRating":
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
class GearRating(_466.AbstractGearRating):
    """GearRating

    This is a mastapy class.
    """

    TYPE: ClassVar["Type"] = _GEAR_RATING

    wrapped: "Any"

    def __post_init__(self: "Self") -> None:
        """Override of the post initialisation magic method."""
        if not hasattr(self.wrapped, "reference_count"):
            self.wrapped.reference_count = 0

        self.wrapped.reference_count += 1

    @property
    @exception_bridge
    def bending_safety_factor_results(self: "Self") -> "_382.SafetyFactorItem":
        """mastapy.materials.SafetyFactorItem

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "BendingSafetyFactorResults")

        if temp is None:
            return None

        type_ = temp.GetType()
        return constructor.new(type_.Namespace, type_.Name)(temp)

    @property
    @exception_bridge
    def contact_safety_factor_results(self: "Self") -> "_382.SafetyFactorItem":
        """mastapy.materials.SafetyFactorItem

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "ContactSafetyFactorResults")

        if temp is None:
            return None

        type_ = temp.GetType()
        return constructor.new(type_.Namespace, type_.Name)(temp)

    @property
    @exception_bridge
    def static_safety_factor(self: "Self") -> "_468.BendingAndContactReportingObject":
        """mastapy.gears.rating.BendingAndContactReportingObject

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "StaticSafetyFactor")

        if temp is None:
            return None

        type_ = temp.GetType()
        return constructor.new(type_.Namespace, type_.Name)(temp)

    @property
    @exception_bridge
    def meshes(self: "Self") -> "List[_473.GearMeshRating]":
        """List[mastapy.gears.rating.GearMeshRating]

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "Meshes")

        if temp is None:
            return None

        value = conversion.pn_to_mp_objects_in_list(temp)

        if value is None:
            return None

        return value

    @property
    def cast_to(self: "Self") -> "_Cast_GearRating":
        """Cast to another type.

        Returns:
            _Cast_GearRating
        """
        return _Cast_GearRating(self)
