"""AbstractGearRating"""

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
from mastapy._private.gears.analysis import _1361

_ABSTRACT_GEAR_RATING = python_net_import(
    "SMT.MastaAPI.Gears.Rating", "AbstractGearRating"
)

if TYPE_CHECKING:
    from typing import Any, List, Type, TypeVar

    from mastapy._private.gears.rating import _465, _467, _470, _474
    from mastapy._private.gears.rating.agma_gleason_conical import _679
    from mastapy._private.gears.rating.bevel import _668
    from mastapy._private.gears.rating.concept import _661, _664
    from mastapy._private.gears.rating.conical import _651, _653
    from mastapy._private.gears.rating.cylindrical import _568, _573
    from mastapy._private.gears.rating.face import _558, _561
    from mastapy._private.gears.rating.hypoid import _552
    from mastapy._private.gears.rating.klingelnberg_conical import _525
    from mastapy._private.gears.rating.klingelnberg_hypoid import _522
    from mastapy._private.gears.rating.klingelnberg_spiral_bevel import _519
    from mastapy._private.gears.rating.spiral_bevel import _516
    from mastapy._private.gears.rating.straight_bevel import _509
    from mastapy._private.gears.rating.straight_bevel_diff import _512
    from mastapy._private.gears.rating.worm import _485, _487
    from mastapy._private.gears.rating.zerol_bevel import _483

    Self = TypeVar("Self", bound="AbstractGearRating")
    CastSelf = TypeVar("CastSelf", bound="AbstractGearRating._Cast_AbstractGearRating")


__docformat__ = "restructuredtext en"
__all__ = ("AbstractGearRating",)


@extended_dataclass(frozen=True, slots=True, weakref_slot=True)
class _Cast_AbstractGearRating:
    """Special nested class for casting AbstractGearRating to subclasses."""

    __parent__: "AbstractGearRating"

    @property
    def abstract_gear_analysis(self: "CastSelf") -> "_1361.AbstractGearAnalysis":
        return self.__parent__._cast(_1361.AbstractGearAnalysis)

    @property
    def gear_duty_cycle_rating(self: "CastSelf") -> "_470.GearDutyCycleRating":
        from mastapy._private.gears.rating import _470

        return self.__parent__._cast(_470.GearDutyCycleRating)

    @property
    def gear_rating(self: "CastSelf") -> "_474.GearRating":
        from mastapy._private.gears.rating import _474

        return self.__parent__._cast(_474.GearRating)

    @property
    def zerol_bevel_gear_rating(self: "CastSelf") -> "_483.ZerolBevelGearRating":
        from mastapy._private.gears.rating.zerol_bevel import _483

        return self.__parent__._cast(_483.ZerolBevelGearRating)

    @property
    def worm_gear_duty_cycle_rating(self: "CastSelf") -> "_485.WormGearDutyCycleRating":
        from mastapy._private.gears.rating.worm import _485

        return self.__parent__._cast(_485.WormGearDutyCycleRating)

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
    def face_gear_duty_cycle_rating(self: "CastSelf") -> "_558.FaceGearDutyCycleRating":
        from mastapy._private.gears.rating.face import _558

        return self.__parent__._cast(_558.FaceGearDutyCycleRating)

    @property
    def face_gear_rating(self: "CastSelf") -> "_561.FaceGearRating":
        from mastapy._private.gears.rating.face import _561

        return self.__parent__._cast(_561.FaceGearRating)

    @property
    def cylindrical_gear_duty_cycle_rating(
        self: "CastSelf",
    ) -> "_568.CylindricalGearDutyCycleRating":
        from mastapy._private.gears.rating.cylindrical import _568

        return self.__parent__._cast(_568.CylindricalGearDutyCycleRating)

    @property
    def cylindrical_gear_rating(self: "CastSelf") -> "_573.CylindricalGearRating":
        from mastapy._private.gears.rating.cylindrical import _573

        return self.__parent__._cast(_573.CylindricalGearRating)

    @property
    def conical_gear_duty_cycle_rating(
        self: "CastSelf",
    ) -> "_651.ConicalGearDutyCycleRating":
        from mastapy._private.gears.rating.conical import _651

        return self.__parent__._cast(_651.ConicalGearDutyCycleRating)

    @property
    def conical_gear_rating(self: "CastSelf") -> "_653.ConicalGearRating":
        from mastapy._private.gears.rating.conical import _653

        return self.__parent__._cast(_653.ConicalGearRating)

    @property
    def concept_gear_duty_cycle_rating(
        self: "CastSelf",
    ) -> "_661.ConceptGearDutyCycleRating":
        from mastapy._private.gears.rating.concept import _661

        return self.__parent__._cast(_661.ConceptGearDutyCycleRating)

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
    def abstract_gear_rating(self: "CastSelf") -> "AbstractGearRating":
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
class AbstractGearRating(_1361.AbstractGearAnalysis):
    """AbstractGearRating

    This is a mastapy class.
    """

    TYPE: ClassVar["Type"] = _ABSTRACT_GEAR_RATING

    wrapped: "Any"

    def __post_init__(self: "Self") -> None:
        """Override of the post initialisation magic method."""
        if not hasattr(self.wrapped, "reference_count"):
            self.wrapped.reference_count = 0

        self.wrapped.reference_count += 1

    @property
    @exception_bridge
    def bending_safety_factor_for_fatigue(self: "Self") -> "float":
        """float

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "BendingSafetyFactorForFatigue")

        if temp is None:
            return 0.0

        return temp

    @property
    @exception_bridge
    def bending_safety_factor_for_static(self: "Self") -> "float":
        """float

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "BendingSafetyFactorForStatic")

        if temp is None:
            return 0.0

        return temp

    @property
    @exception_bridge
    def contact_safety_factor_for_fatigue(self: "Self") -> "float":
        """float

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "ContactSafetyFactorForFatigue")

        if temp is None:
            return 0.0

        return temp

    @property
    @exception_bridge
    def contact_safety_factor_for_static(self: "Self") -> "float":
        """float

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "ContactSafetyFactorForStatic")

        if temp is None:
            return 0.0

        return temp

    @property
    @exception_bridge
    def cycles_to_fail(self: "Self") -> "float":
        """float

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "CyclesToFail")

        if temp is None:
            return 0.0

        return temp

    @property
    @exception_bridge
    def cycles_to_fail_bending(self: "Self") -> "float":
        """float

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "CyclesToFailBending")

        if temp is None:
            return 0.0

        return temp

    @property
    @exception_bridge
    def cycles_to_fail_contact(self: "Self") -> "float":
        """float

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "CyclesToFailContact")

        if temp is None:
            return 0.0

        return temp

    @property
    @exception_bridge
    def damage_bending(self: "Self") -> "float":
        """float

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "DamageBending")

        if temp is None:
            return 0.0

        return temp

    @property
    @exception_bridge
    def damage_contact(self: "Self") -> "float":
        """float

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "DamageContact")

        if temp is None:
            return 0.0

        return temp

    @property
    @exception_bridge
    def gear_reliability_bending(self: "Self") -> "float":
        """float

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "GearReliabilityBending")

        if temp is None:
            return 0.0

        return temp

    @property
    @exception_bridge
    def gear_reliability_contact(self: "Self") -> "float":
        """float

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "GearReliabilityContact")

        if temp is None:
            return 0.0

        return temp

    @property
    @exception_bridge
    def normalised_bending_safety_factor_for_fatigue(self: "Self") -> "float":
        """float

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(
            self.wrapped, "NormalisedBendingSafetyFactorForFatigue"
        )

        if temp is None:
            return 0.0

        return temp

    @property
    @exception_bridge
    def normalised_bending_safety_factor_for_static(self: "Self") -> "float":
        """float

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(
            self.wrapped, "NormalisedBendingSafetyFactorForStatic"
        )

        if temp is None:
            return 0.0

        return temp

    @property
    @exception_bridge
    def normalised_contact_safety_factor_for_fatigue(self: "Self") -> "float":
        """float

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(
            self.wrapped, "NormalisedContactSafetyFactorForFatigue"
        )

        if temp is None:
            return 0.0

        return temp

    @property
    @exception_bridge
    def normalised_contact_safety_factor_for_static(self: "Self") -> "float":
        """float

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(
            self.wrapped, "NormalisedContactSafetyFactorForStatic"
        )

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
    @exception_bridge
    def time_to_fail(self: "Self") -> "float":
        """float

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "TimeToFail")

        if temp is None:
            return 0.0

        return temp

    @property
    @exception_bridge
    def time_to_fail_bending(self: "Self") -> "float":
        """float

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "TimeToFailBending")

        if temp is None:
            return 0.0

        return temp

    @property
    @exception_bridge
    def time_to_fail_contact(self: "Self") -> "float":
        """float

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "TimeToFailContact")

        if temp is None:
            return 0.0

        return temp

    @property
    @exception_bridge
    def total_gear_reliability(self: "Self") -> "float":
        """float

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "TotalGearReliability")

        if temp is None:
            return 0.0

        return temp

    @property
    @exception_bridge
    def gear_set(self: "Self") -> "_467.AbstractGearSetRating":
        """mastapy.gears.rating.AbstractGearSetRating

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "GearSet")

        if temp is None:
            return None

        type_ = temp.GetType()
        return constructor.new(type_.Namespace, type_.Name)(temp)

    @property
    @exception_bridge
    def meshes(self: "Self") -> "List[_465.AbstractGearMeshRating]":
        """List[mastapy.gears.rating.AbstractGearMeshRating]

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
    def cast_to(self: "Self") -> "_Cast_AbstractGearRating":
        """Cast to another type.

        Returns:
            _Cast_AbstractGearRating
        """
        return _Cast_AbstractGearRating(self)
