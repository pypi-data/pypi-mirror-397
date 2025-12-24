"""AGMAGleasonConicalGearSet"""

from __future__ import annotations

from typing import TYPE_CHECKING, ClassVar

from mastapy._private._internal.dataclasses import extended_dataclass
from mastapy._private._internal.exceptions import CastException
from mastapy._private._internal.python_net import python_net_import

from mastapy._private._internal import utility
from mastapy._private.system_model.part_model.gears import _2805

_AGMA_GLEASON_CONICAL_GEAR_SET = python_net_import(
    "SMT.MastaAPI.SystemModel.PartModel.Gears", "AGMAGleasonConicalGearSet"
)

if TYPE_CHECKING:
    from typing import Any, Type, TypeVar

    from mastapy._private.system_model import _2451
    from mastapy._private.system_model.part_model import _2703, _2742, _2752
    from mastapy._private.system_model.part_model.gears import (
        _2797,
        _2801,
        _2813,
        _2816,
        _2826,
        _2828,
        _2830,
        _2836,
    )

    Self = TypeVar("Self", bound="AGMAGleasonConicalGearSet")
    CastSelf = TypeVar(
        "CastSelf", bound="AGMAGleasonConicalGearSet._Cast_AGMAGleasonConicalGearSet"
    )


__docformat__ = "restructuredtext en"
__all__ = ("AGMAGleasonConicalGearSet",)


@extended_dataclass(frozen=True, slots=True, weakref_slot=True)
class _Cast_AGMAGleasonConicalGearSet:
    """Special nested class for casting AGMAGleasonConicalGearSet to subclasses."""

    __parent__: "AGMAGleasonConicalGearSet"

    @property
    def conical_gear_set(self: "CastSelf") -> "_2805.ConicalGearSet":
        return self.__parent__._cast(_2805.ConicalGearSet)

    @property
    def gear_set(self: "CastSelf") -> "_2813.GearSet":
        from mastapy._private.system_model.part_model.gears import _2813

        return self.__parent__._cast(_2813.GearSet)

    @property
    def specialised_assembly(self: "CastSelf") -> "_2752.SpecialisedAssembly":
        from mastapy._private.system_model.part_model import _2752

        return self.__parent__._cast(_2752.SpecialisedAssembly)

    @property
    def abstract_assembly(self: "CastSelf") -> "_2703.AbstractAssembly":
        from mastapy._private.system_model.part_model import _2703

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
    def hypoid_gear_set(self: "CastSelf") -> "_2816.HypoidGearSet":
        from mastapy._private.system_model.part_model.gears import _2816

        return self.__parent__._cast(_2816.HypoidGearSet)

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
    def zerol_bevel_gear_set(self: "CastSelf") -> "_2836.ZerolBevelGearSet":
        from mastapy._private.system_model.part_model.gears import _2836

        return self.__parent__._cast(_2836.ZerolBevelGearSet)

    @property
    def agma_gleason_conical_gear_set(self: "CastSelf") -> "AGMAGleasonConicalGearSet":
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
class AGMAGleasonConicalGearSet(_2805.ConicalGearSet):
    """AGMAGleasonConicalGearSet

    This is a mastapy class.
    """

    TYPE: ClassVar["Type"] = _AGMA_GLEASON_CONICAL_GEAR_SET

    wrapped: "Any"

    def __post_init__(self: "Self") -> None:
        """Override of the post initialisation magic method."""
        if not hasattr(self.wrapped, "reference_count"):
            self.wrapped.reference_count = 0

        self.wrapped.reference_count += 1

    @property
    def cast_to(self: "Self") -> "_Cast_AGMAGleasonConicalGearSet":
        """Cast to another type.

        Returns:
            _Cast_AGMAGleasonConicalGearSet
        """
        return _Cast_AGMAGleasonConicalGearSet(self)
