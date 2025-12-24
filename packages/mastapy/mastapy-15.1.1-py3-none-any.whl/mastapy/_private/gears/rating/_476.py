"""GearSetRating"""

from __future__ import annotations

from typing import TYPE_CHECKING, ClassVar

from mastapy._private._internal.dataclasses import extended_dataclass
from mastapy._private._internal.exception_bridge import exception_bridge
from mastapy._private._internal.exceptions import CastException
from mastapy._private._internal.python_net import (
    python_net_import,
    pythonnet_property_get,
    pythonnet_property_set,
)
from mastapy._private._internal.type_enforcement import enforce_parameter_types

from mastapy._private._internal import constructor, conversion, utility
from mastapy._private.gears.rating import _467

_GEAR_SET_RATING = python_net_import("SMT.MastaAPI.Gears.Rating", "GearSetRating")

if TYPE_CHECKING:
    from typing import Any, List, Type, TypeVar

    from mastapy._private.gears.analysis import _1363
    from mastapy._private.gears.rating import _473, _474
    from mastapy._private.gears.rating.agma_gleason_conical import _680
    from mastapy._private.gears.rating.bevel import _669
    from mastapy._private.gears.rating.concept import _666
    from mastapy._private.gears.rating.conical import _655
    from mastapy._private.gears.rating.cylindrical import _577
    from mastapy._private.gears.rating.face import _563
    from mastapy._private.gears.rating.hypoid import _553
    from mastapy._private.gears.rating.klingelnberg_conical import _526
    from mastapy._private.gears.rating.klingelnberg_hypoid import _523
    from mastapy._private.gears.rating.klingelnberg_spiral_bevel import _520
    from mastapy._private.gears.rating.spiral_bevel import _517
    from mastapy._private.gears.rating.straight_bevel import _510
    from mastapy._private.gears.rating.straight_bevel_diff import _513
    from mastapy._private.gears.rating.worm import _489
    from mastapy._private.gears.rating.zerol_bevel import _484
    from mastapy._private.materials import _369

    Self = TypeVar("Self", bound="GearSetRating")
    CastSelf = TypeVar("CastSelf", bound="GearSetRating._Cast_GearSetRating")


__docformat__ = "restructuredtext en"
__all__ = ("GearSetRating",)


@extended_dataclass(frozen=True, slots=True, weakref_slot=True)
class _Cast_GearSetRating:
    """Special nested class for casting GearSetRating to subclasses."""

    __parent__: "GearSetRating"

    @property
    def abstract_gear_set_rating(self: "CastSelf") -> "_467.AbstractGearSetRating":
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
    def worm_gear_set_rating(self: "CastSelf") -> "_489.WormGearSetRating":
        from mastapy._private.gears.rating.worm import _489

        return self.__parent__._cast(_489.WormGearSetRating)

    @property
    def straight_bevel_gear_set_rating(
        self: "CastSelf",
    ) -> "_510.StraightBevelGearSetRating":
        from mastapy._private.gears.rating.straight_bevel import _510

        return self.__parent__._cast(_510.StraightBevelGearSetRating)

    @property
    def straight_bevel_diff_gear_set_rating(
        self: "CastSelf",
    ) -> "_513.StraightBevelDiffGearSetRating":
        from mastapy._private.gears.rating.straight_bevel_diff import _513

        return self.__parent__._cast(_513.StraightBevelDiffGearSetRating)

    @property
    def spiral_bevel_gear_set_rating(
        self: "CastSelf",
    ) -> "_517.SpiralBevelGearSetRating":
        from mastapy._private.gears.rating.spiral_bevel import _517

        return self.__parent__._cast(_517.SpiralBevelGearSetRating)

    @property
    def klingelnberg_cyclo_palloid_spiral_bevel_gear_set_rating(
        self: "CastSelf",
    ) -> "_520.KlingelnbergCycloPalloidSpiralBevelGearSetRating":
        from mastapy._private.gears.rating.klingelnberg_spiral_bevel import _520

        return self.__parent__._cast(
            _520.KlingelnbergCycloPalloidSpiralBevelGearSetRating
        )

    @property
    def klingelnberg_cyclo_palloid_hypoid_gear_set_rating(
        self: "CastSelf",
    ) -> "_523.KlingelnbergCycloPalloidHypoidGearSetRating":
        from mastapy._private.gears.rating.klingelnberg_hypoid import _523

        return self.__parent__._cast(_523.KlingelnbergCycloPalloidHypoidGearSetRating)

    @property
    def klingelnberg_cyclo_palloid_conical_gear_set_rating(
        self: "CastSelf",
    ) -> "_526.KlingelnbergCycloPalloidConicalGearSetRating":
        from mastapy._private.gears.rating.klingelnberg_conical import _526

        return self.__parent__._cast(_526.KlingelnbergCycloPalloidConicalGearSetRating)

    @property
    def hypoid_gear_set_rating(self: "CastSelf") -> "_553.HypoidGearSetRating":
        from mastapy._private.gears.rating.hypoid import _553

        return self.__parent__._cast(_553.HypoidGearSetRating)

    @property
    def face_gear_set_rating(self: "CastSelf") -> "_563.FaceGearSetRating":
        from mastapy._private.gears.rating.face import _563

        return self.__parent__._cast(_563.FaceGearSetRating)

    @property
    def cylindrical_gear_set_rating(
        self: "CastSelf",
    ) -> "_577.CylindricalGearSetRating":
        from mastapy._private.gears.rating.cylindrical import _577

        return self.__parent__._cast(_577.CylindricalGearSetRating)

    @property
    def conical_gear_set_rating(self: "CastSelf") -> "_655.ConicalGearSetRating":
        from mastapy._private.gears.rating.conical import _655

        return self.__parent__._cast(_655.ConicalGearSetRating)

    @property
    def concept_gear_set_rating(self: "CastSelf") -> "_666.ConceptGearSetRating":
        from mastapy._private.gears.rating.concept import _666

        return self.__parent__._cast(_666.ConceptGearSetRating)

    @property
    def bevel_gear_set_rating(self: "CastSelf") -> "_669.BevelGearSetRating":
        from mastapy._private.gears.rating.bevel import _669

        return self.__parent__._cast(_669.BevelGearSetRating)

    @property
    def agma_gleason_conical_gear_set_rating(
        self: "CastSelf",
    ) -> "_680.AGMAGleasonConicalGearSetRating":
        from mastapy._private.gears.rating.agma_gleason_conical import _680

        return self.__parent__._cast(_680.AGMAGleasonConicalGearSetRating)

    @property
    def gear_set_rating(self: "CastSelf") -> "GearSetRating":
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
class GearSetRating(_467.AbstractGearSetRating):
    """GearSetRating

    This is a mastapy class.
    """

    TYPE: ClassVar["Type"] = _GEAR_SET_RATING

    wrapped: "Any"

    def __post_init__(self: "Self") -> None:
        """Override of the post initialisation magic method."""
        if not hasattr(self.wrapped, "reference_count"):
            self.wrapped.reference_count = 0

        self.wrapped.reference_count += 1

    @property
    @exception_bridge
    def name(self: "Self") -> "str":
        """str"""
        temp = pythonnet_property_get(self.wrapped, "Name")

        if temp is None:
            return ""

        return temp

    @name.setter
    @exception_bridge
    @enforce_parameter_types
    def name(self: "Self", value: "str") -> None:
        pythonnet_property_set(
            self.wrapped, "Name", str(value) if value is not None else ""
        )

    @property
    @exception_bridge
    def rating(self: "Self") -> "str":
        """str

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "Rating")

        if temp is None:
            return ""

        return temp

    @property
    @exception_bridge
    def total_gear_set_reliability(self: "Self") -> "float":
        """float

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "TotalGearSetReliability")

        if temp is None:
            return 0.0

        return temp

    @property
    @exception_bridge
    def lubrication_detail(self: "Self") -> "_369.LubricationDetail":
        """mastapy.materials.LubricationDetail

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "LubricationDetail")

        if temp is None:
            return None

        type_ = temp.GetType()
        return constructor.new(type_.Namespace, type_.Name)(temp)

    @property
    @exception_bridge
    def gear_mesh_ratings(self: "Self") -> "List[_473.GearMeshRating]":
        """List[mastapy.gears.rating.GearMeshRating]

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "GearMeshRatings")

        if temp is None:
            return None

        value = conversion.pn_to_mp_objects_in_list(temp)

        if value is None:
            return None

        return value

    @property
    @exception_bridge
    def gear_ratings(self: "Self") -> "List[_474.GearRating]":
        """List[mastapy.gears.rating.GearRating]

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "GearRatings")

        if temp is None:
            return None

        value = conversion.pn_to_mp_objects_in_list(temp)

        if value is None:
            return None

        return value

    @property
    def cast_to(self: "Self") -> "_Cast_GearSetRating":
        """Cast to another type.

        Returns:
            _Cast_GearSetRating
        """
        return _Cast_GearSetRating(self)
