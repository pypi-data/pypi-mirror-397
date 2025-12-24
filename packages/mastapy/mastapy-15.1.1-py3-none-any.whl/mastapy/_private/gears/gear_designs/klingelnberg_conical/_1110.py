"""KlingelnbergConicalMeshedGearDesign"""

from __future__ import annotations

from typing import TYPE_CHECKING, ClassVar

from mastapy._private._internal.dataclasses import extended_dataclass
from mastapy._private._internal.exceptions import CastException
from mastapy._private._internal.python_net import python_net_import

from mastapy._private._internal import utility
from mastapy._private.gears.gear_designs.conical import _1305

_KLINGELNBERG_CONICAL_MESHED_GEAR_DESIGN = python_net_import(
    "SMT.MastaAPI.Gears.GearDesigns.KlingelnbergConical",
    "KlingelnbergConicalMeshedGearDesign",
)

if TYPE_CHECKING:
    from typing import Any, Type, TypeVar

    from mastapy._private.gears.gear_designs import _1074
    from mastapy._private.gears.gear_designs.klingelnberg_hypoid import _1106
    from mastapy._private.gears.gear_designs.klingelnberg_spiral_bevel import _1102

    Self = TypeVar("Self", bound="KlingelnbergConicalMeshedGearDesign")
    CastSelf = TypeVar(
        "CastSelf",
        bound="KlingelnbergConicalMeshedGearDesign._Cast_KlingelnbergConicalMeshedGearDesign",
    )


__docformat__ = "restructuredtext en"
__all__ = ("KlingelnbergConicalMeshedGearDesign",)


@extended_dataclass(frozen=True, slots=True, weakref_slot=True)
class _Cast_KlingelnbergConicalMeshedGearDesign:
    """Special nested class for casting KlingelnbergConicalMeshedGearDesign to subclasses."""

    __parent__: "KlingelnbergConicalMeshedGearDesign"

    @property
    def conical_meshed_gear_design(self: "CastSelf") -> "_1305.ConicalMeshedGearDesign":
        return self.__parent__._cast(_1305.ConicalMeshedGearDesign)

    @property
    def gear_design_component(self: "CastSelf") -> "_1074.GearDesignComponent":
        from mastapy._private.gears.gear_designs import _1074

        return self.__parent__._cast(_1074.GearDesignComponent)

    @property
    def klingelnberg_cyclo_palloid_spiral_bevel_meshed_gear_design(
        self: "CastSelf",
    ) -> "_1102.KlingelnbergCycloPalloidSpiralBevelMeshedGearDesign":
        from mastapy._private.gears.gear_designs.klingelnberg_spiral_bevel import _1102

        return self.__parent__._cast(
            _1102.KlingelnbergCycloPalloidSpiralBevelMeshedGearDesign
        )

    @property
    def klingelnberg_cyclo_palloid_hypoid_meshed_gear_design(
        self: "CastSelf",
    ) -> "_1106.KlingelnbergCycloPalloidHypoidMeshedGearDesign":
        from mastapy._private.gears.gear_designs.klingelnberg_hypoid import _1106

        return self.__parent__._cast(
            _1106.KlingelnbergCycloPalloidHypoidMeshedGearDesign
        )

    @property
    def klingelnberg_conical_meshed_gear_design(
        self: "CastSelf",
    ) -> "KlingelnbergConicalMeshedGearDesign":
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
class KlingelnbergConicalMeshedGearDesign(_1305.ConicalMeshedGearDesign):
    """KlingelnbergConicalMeshedGearDesign

    This is a mastapy class.
    """

    TYPE: ClassVar["Type"] = _KLINGELNBERG_CONICAL_MESHED_GEAR_DESIGN

    wrapped: "Any"

    def __post_init__(self: "Self") -> None:
        """Override of the post initialisation magic method."""
        if not hasattr(self.wrapped, "reference_count"):
            self.wrapped.reference_count = 0

        self.wrapped.reference_count += 1

    @property
    def cast_to(self: "Self") -> "_Cast_KlingelnbergConicalMeshedGearDesign":
        """Cast to another type.

        Returns:
            _Cast_KlingelnbergConicalMeshedGearDesign
        """
        return _Cast_KlingelnbergConicalMeshedGearDesign(self)
