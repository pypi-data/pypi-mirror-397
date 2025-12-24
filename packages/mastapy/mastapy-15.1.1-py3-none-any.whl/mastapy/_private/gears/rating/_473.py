"""GearMeshRating"""

from __future__ import annotations

from typing import TYPE_CHECKING, ClassVar

from mastapy._private._internal.dataclasses import extended_dataclass
from mastapy._private._internal.exception_bridge import exception_bridge
from mastapy._private._internal.exceptions import CastException
from mastapy._private._internal.python_net import (
    python_net_import,
    pythonnet_property_get,
)

from mastapy._private._internal import constructor, utility
from mastapy._private.gears.rating import _465

_GEAR_MESH_RATING = python_net_import("SMT.MastaAPI.Gears.Rating", "GearMeshRating")

if TYPE_CHECKING:
    from typing import Any, Type, TypeVar

    from mastapy._private.gears.analysis import _1362
    from mastapy._private.gears.load_case import _1000
    from mastapy._private.gears.rating import _476
    from mastapy._private.gears.rating.agma_gleason_conical import _678
    from mastapy._private.gears.rating.bevel import _667
    from mastapy._private.gears.rating.concept import _663
    from mastapy._private.gears.rating.conical import _652
    from mastapy._private.gears.rating.cylindrical import _571
    from mastapy._private.gears.rating.face import _560
    from mastapy._private.gears.rating.hypoid import _551
    from mastapy._private.gears.rating.klingelnberg_conical import _524
    from mastapy._private.gears.rating.klingelnberg_hypoid import _521
    from mastapy._private.gears.rating.klingelnberg_spiral_bevel import _518
    from mastapy._private.gears.rating.spiral_bevel import _515
    from mastapy._private.gears.rating.straight_bevel import _508
    from mastapy._private.gears.rating.straight_bevel_diff import _511
    from mastapy._private.gears.rating.worm import _486
    from mastapy._private.gears.rating.zerol_bevel import _482

    Self = TypeVar("Self", bound="GearMeshRating")
    CastSelf = TypeVar("CastSelf", bound="GearMeshRating._Cast_GearMeshRating")


__docformat__ = "restructuredtext en"
__all__ = ("GearMeshRating",)


@extended_dataclass(frozen=True, slots=True, weakref_slot=True)
class _Cast_GearMeshRating:
    """Special nested class for casting GearMeshRating to subclasses."""

    __parent__: "GearMeshRating"

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
    def conical_gear_mesh_rating(self: "CastSelf") -> "_652.ConicalGearMeshRating":
        from mastapy._private.gears.rating.conical import _652

        return self.__parent__._cast(_652.ConicalGearMeshRating)

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
    def gear_mesh_rating(self: "CastSelf") -> "GearMeshRating":
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
class GearMeshRating(_465.AbstractGearMeshRating):
    """GearMeshRating

    This is a mastapy class.
    """

    TYPE: ClassVar["Type"] = _GEAR_MESH_RATING

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
    def driving_gear(self: "Self") -> "str":
        """str

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "DrivingGear")

        if temp is None:
            return ""

        return temp

    @property
    @exception_bridge
    def is_loaded(self: "Self") -> "bool":
        """bool

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "IsLoaded")

        if temp is None:
            return False

        return temp

    @property
    @exception_bridge
    def pinion_name(self: "Self") -> "str":
        """str

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "PinionName")

        if temp is None:
            return ""

        return temp

    @property
    @exception_bridge
    def pinion_torque(self: "Self") -> "float":
        """float

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "PinionTorque")

        if temp is None:
            return 0.0

        return temp

    @property
    @exception_bridge
    def signed_pinion_torque(self: "Self") -> "float":
        """float

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "SignedPinionTorque")

        if temp is None:
            return 0.0

        return temp

    @property
    @exception_bridge
    def signed_wheel_torque(self: "Self") -> "float":
        """float

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "SignedWheelTorque")

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
    def wheel_name(self: "Self") -> "str":
        """str

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "WheelName")

        if temp is None:
            return ""

        return temp

    @property
    @exception_bridge
    def wheel_torque(self: "Self") -> "float":
        """float

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "WheelTorque")

        if temp is None:
            return 0.0

        return temp

    @property
    @exception_bridge
    def mesh_load_case(self: "Self") -> "_1000.MeshLoadCase":
        """mastapy.gears.load_case.MeshLoadCase

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "MeshLoadCase")

        if temp is None:
            return None

        type_ = temp.GetType()
        return constructor.new(type_.Namespace, type_.Name)(temp)

    @property
    @exception_bridge
    def gear_set(self: "Self") -> "_476.GearSetRating":
        """mastapy.gears.rating.GearSetRating

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "GearSet")

        if temp is None:
            return None

        type_ = temp.GetType()
        return constructor.new(type_.Namespace, type_.Name)(temp)

    @property
    def cast_to(self: "Self") -> "_Cast_GearMeshRating":
        """Cast to another type.

        Returns:
            _Cast_GearMeshRating
        """
        return _Cast_GearMeshRating(self)
