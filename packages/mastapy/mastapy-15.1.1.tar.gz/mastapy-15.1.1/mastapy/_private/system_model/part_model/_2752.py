"""SpecialisedAssembly"""

from __future__ import annotations

from typing import TYPE_CHECKING, ClassVar

from mastapy._private._internal.dataclasses import extended_dataclass
from mastapy._private._internal.exceptions import CastException
from mastapy._private._internal.python_net import python_net_import

from mastapy._private._internal import utility
from mastapy._private.system_model.part_model import _2703

_SPECIALISED_ASSEMBLY = python_net_import(
    "SMT.MastaAPI.SystemModel.PartModel", "SpecialisedAssembly"
)

if TYPE_CHECKING:
    from typing import Any, Type, TypeVar

    from mastapy._private.system_model import _2451
    from mastapy._private.system_model.part_model import _2712, _2725, _2736, _2742
    from mastapy._private.system_model.part_model.couplings import (
        _2859,
        _2861,
        _2864,
        _2867,
        _2870,
        _2872,
        _2883,
        _2890,
        _2892,
        _2897,
    )
    from mastapy._private.system_model.part_model.cycloidal import _2850
    from mastapy._private.system_model.part_model.gears import (
        _2795,
        _2797,
        _2801,
        _2803,
        _2805,
        _2807,
        _2810,
        _2813,
        _2816,
        _2818,
        _2820,
        _2822,
        _2823,
        _2826,
        _2828,
        _2830,
        _2834,
        _2836,
    )

    Self = TypeVar("Self", bound="SpecialisedAssembly")
    CastSelf = TypeVar(
        "CastSelf", bound="SpecialisedAssembly._Cast_SpecialisedAssembly"
    )


__docformat__ = "restructuredtext en"
__all__ = ("SpecialisedAssembly",)


@extended_dataclass(frozen=True, slots=True, weakref_slot=True)
class _Cast_SpecialisedAssembly:
    """Special nested class for casting SpecialisedAssembly to subclasses."""

    __parent__: "SpecialisedAssembly"

    @property
    def abstract_assembly(self: "CastSelf") -> "_2703.AbstractAssembly":
        return self.__parent__._cast(_2703.AbstractAssembly)

    @property
    def part(self: "CastSelf") -> "_2742.Part":
        from mastapy._private.system_model.part_model import _2742

        return self.__parent__._cast(_2742.Part)

    @property
    def design_entity(self: "CastSelf") -> "_2451.DesignEntity":
        from mastapy._private.system_model import _2451

        return self.__parent__._cast(_2451.DesignEntity)

    @property
    def bolted_joint(self: "CastSelf") -> "_2712.BoltedJoint":
        from mastapy._private.system_model.part_model import _2712

        return self.__parent__._cast(_2712.BoltedJoint)

    @property
    def flexible_pin_assembly(self: "CastSelf") -> "_2725.FlexiblePinAssembly":
        from mastapy._private.system_model.part_model import _2725

        return self.__parent__._cast(_2725.FlexiblePinAssembly)

    @property
    def microphone_array(self: "CastSelf") -> "_2736.MicrophoneArray":
        from mastapy._private.system_model.part_model import _2736

        return self.__parent__._cast(_2736.MicrophoneArray)

    @property
    def agma_gleason_conical_gear_set(
        self: "CastSelf",
    ) -> "_2795.AGMAGleasonConicalGearSet":
        from mastapy._private.system_model.part_model.gears import _2795

        return self.__parent__._cast(_2795.AGMAGleasonConicalGearSet)

    @property
    def bevel_differential_gear_set(
        self: "CastSelf",
    ) -> "_2797.BevelDifferentialGearSet":
        from mastapy._private.system_model.part_model.gears import _2797

        return self.__parent__._cast(_2797.BevelDifferentialGearSet)

    @property
    def bevel_gear_set(self: "CastSelf") -> "_2801.BevelGearSet":
        from mastapy._private.system_model.part_model.gears import _2801

        return self.__parent__._cast(_2801.BevelGearSet)

    @property
    def concept_gear_set(self: "CastSelf") -> "_2803.ConceptGearSet":
        from mastapy._private.system_model.part_model.gears import _2803

        return self.__parent__._cast(_2803.ConceptGearSet)

    @property
    def conical_gear_set(self: "CastSelf") -> "_2805.ConicalGearSet":
        from mastapy._private.system_model.part_model.gears import _2805

        return self.__parent__._cast(_2805.ConicalGearSet)

    @property
    def cylindrical_gear_set(self: "CastSelf") -> "_2807.CylindricalGearSet":
        from mastapy._private.system_model.part_model.gears import _2807

        return self.__parent__._cast(_2807.CylindricalGearSet)

    @property
    def face_gear_set(self: "CastSelf") -> "_2810.FaceGearSet":
        from mastapy._private.system_model.part_model.gears import _2810

        return self.__parent__._cast(_2810.FaceGearSet)

    @property
    def gear_set(self: "CastSelf") -> "_2813.GearSet":
        from mastapy._private.system_model.part_model.gears import _2813

        return self.__parent__._cast(_2813.GearSet)

    @property
    def hypoid_gear_set(self: "CastSelf") -> "_2816.HypoidGearSet":
        from mastapy._private.system_model.part_model.gears import _2816

        return self.__parent__._cast(_2816.HypoidGearSet)

    @property
    def klingelnberg_cyclo_palloid_conical_gear_set(
        self: "CastSelf",
    ) -> "_2818.KlingelnbergCycloPalloidConicalGearSet":
        from mastapy._private.system_model.part_model.gears import _2818

        return self.__parent__._cast(_2818.KlingelnbergCycloPalloidConicalGearSet)

    @property
    def klingelnberg_cyclo_palloid_hypoid_gear_set(
        self: "CastSelf",
    ) -> "_2820.KlingelnbergCycloPalloidHypoidGearSet":
        from mastapy._private.system_model.part_model.gears import _2820

        return self.__parent__._cast(_2820.KlingelnbergCycloPalloidHypoidGearSet)

    @property
    def klingelnberg_cyclo_palloid_spiral_bevel_gear_set(
        self: "CastSelf",
    ) -> "_2822.KlingelnbergCycloPalloidSpiralBevelGearSet":
        from mastapy._private.system_model.part_model.gears import _2822

        return self.__parent__._cast(_2822.KlingelnbergCycloPalloidSpiralBevelGearSet)

    @property
    def planetary_gear_set(self: "CastSelf") -> "_2823.PlanetaryGearSet":
        from mastapy._private.system_model.part_model.gears import _2823

        return self.__parent__._cast(_2823.PlanetaryGearSet)

    @property
    def spiral_bevel_gear_set(self: "CastSelf") -> "_2826.SpiralBevelGearSet":
        from mastapy._private.system_model.part_model.gears import _2826

        return self.__parent__._cast(_2826.SpiralBevelGearSet)

    @property
    def straight_bevel_diff_gear_set(
        self: "CastSelf",
    ) -> "_2828.StraightBevelDiffGearSet":
        from mastapy._private.system_model.part_model.gears import _2828

        return self.__parent__._cast(_2828.StraightBevelDiffGearSet)

    @property
    def straight_bevel_gear_set(self: "CastSelf") -> "_2830.StraightBevelGearSet":
        from mastapy._private.system_model.part_model.gears import _2830

        return self.__parent__._cast(_2830.StraightBevelGearSet)

    @property
    def worm_gear_set(self: "CastSelf") -> "_2834.WormGearSet":
        from mastapy._private.system_model.part_model.gears import _2834

        return self.__parent__._cast(_2834.WormGearSet)

    @property
    def zerol_bevel_gear_set(self: "CastSelf") -> "_2836.ZerolBevelGearSet":
        from mastapy._private.system_model.part_model.gears import _2836

        return self.__parent__._cast(_2836.ZerolBevelGearSet)

    @property
    def cycloidal_assembly(self: "CastSelf") -> "_2850.CycloidalAssembly":
        from mastapy._private.system_model.part_model.cycloidal import _2850

        return self.__parent__._cast(_2850.CycloidalAssembly)

    @property
    def belt_drive(self: "CastSelf") -> "_2859.BeltDrive":
        from mastapy._private.system_model.part_model.couplings import _2859

        return self.__parent__._cast(_2859.BeltDrive)

    @property
    def clutch(self: "CastSelf") -> "_2861.Clutch":
        from mastapy._private.system_model.part_model.couplings import _2861

        return self.__parent__._cast(_2861.Clutch)

    @property
    def concept_coupling(self: "CastSelf") -> "_2864.ConceptCoupling":
        from mastapy._private.system_model.part_model.couplings import _2864

        return self.__parent__._cast(_2864.ConceptCoupling)

    @property
    def coupling(self: "CastSelf") -> "_2867.Coupling":
        from mastapy._private.system_model.part_model.couplings import _2867

        return self.__parent__._cast(_2867.Coupling)

    @property
    def cvt(self: "CastSelf") -> "_2870.CVT":
        from mastapy._private.system_model.part_model.couplings import _2870

        return self.__parent__._cast(_2870.CVT)

    @property
    def part_to_part_shear_coupling(
        self: "CastSelf",
    ) -> "_2872.PartToPartShearCoupling":
        from mastapy._private.system_model.part_model.couplings import _2872

        return self.__parent__._cast(_2872.PartToPartShearCoupling)

    @property
    def rolling_ring_assembly(self: "CastSelf") -> "_2883.RollingRingAssembly":
        from mastapy._private.system_model.part_model.couplings import _2883

        return self.__parent__._cast(_2883.RollingRingAssembly)

    @property
    def spring_damper(self: "CastSelf") -> "_2890.SpringDamper":
        from mastapy._private.system_model.part_model.couplings import _2890

        return self.__parent__._cast(_2890.SpringDamper)

    @property
    def synchroniser(self: "CastSelf") -> "_2892.Synchroniser":
        from mastapy._private.system_model.part_model.couplings import _2892

        return self.__parent__._cast(_2892.Synchroniser)

    @property
    def torque_converter(self: "CastSelf") -> "_2897.TorqueConverter":
        from mastapy._private.system_model.part_model.couplings import _2897

        return self.__parent__._cast(_2897.TorqueConverter)

    @property
    def specialised_assembly(self: "CastSelf") -> "SpecialisedAssembly":
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
class SpecialisedAssembly(_2703.AbstractAssembly):
    """SpecialisedAssembly

    This is a mastapy class.
    """

    TYPE: ClassVar["Type"] = _SPECIALISED_ASSEMBLY

    wrapped: "Any"

    def __post_init__(self: "Self") -> None:
        """Override of the post initialisation magic method."""
        if not hasattr(self.wrapped, "reference_count"):
            self.wrapped.reference_count = 0

        self.wrapped.reference_count += 1

    @property
    def cast_to(self: "Self") -> "_Cast_SpecialisedAssembly":
        """Cast to another type.

        Returns:
            _Cast_SpecialisedAssembly
        """
        return _Cast_SpecialisedAssembly(self)
