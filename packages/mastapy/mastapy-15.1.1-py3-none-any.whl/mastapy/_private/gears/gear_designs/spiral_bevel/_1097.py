"""SpiralBevelGearSetDesign"""

from __future__ import annotations

from typing import TYPE_CHECKING, ClassVar

from mastapy._private._internal.dataclasses import extended_dataclass
from mastapy._private._internal.exception_bridge import exception_bridge
from mastapy._private._internal.exceptions import CastException
from mastapy._private._internal.python_net import (
    python_net_import,
    pythonnet_property_get,
)

from mastapy._private._internal import conversion, utility
from mastapy._private.gears.gear_designs.bevel import _1328

_SPIRAL_BEVEL_GEAR_SET_DESIGN = python_net_import(
    "SMT.MastaAPI.Gears.GearDesigns.SpiralBevel", "SpiralBevelGearSetDesign"
)

if TYPE_CHECKING:
    from typing import Any, List, Type, TypeVar

    from mastapy._private.gears.gear_designs import _1074, _1076
    from mastapy._private.gears.gear_designs.agma_gleason_conical import _1341
    from mastapy._private.gears.gear_designs.conical import _1302
    from mastapy._private.gears.gear_designs.spiral_bevel import _1095, _1096

    Self = TypeVar("Self", bound="SpiralBevelGearSetDesign")
    CastSelf = TypeVar(
        "CastSelf", bound="SpiralBevelGearSetDesign._Cast_SpiralBevelGearSetDesign"
    )


__docformat__ = "restructuredtext en"
__all__ = ("SpiralBevelGearSetDesign",)


@extended_dataclass(frozen=True, slots=True, weakref_slot=True)
class _Cast_SpiralBevelGearSetDesign:
    """Special nested class for casting SpiralBevelGearSetDesign to subclasses."""

    __parent__: "SpiralBevelGearSetDesign"

    @property
    def bevel_gear_set_design(self: "CastSelf") -> "_1328.BevelGearSetDesign":
        return self.__parent__._cast(_1328.BevelGearSetDesign)

    @property
    def agma_gleason_conical_gear_set_design(
        self: "CastSelf",
    ) -> "_1341.AGMAGleasonConicalGearSetDesign":
        from mastapy._private.gears.gear_designs.agma_gleason_conical import _1341

        return self.__parent__._cast(_1341.AGMAGleasonConicalGearSetDesign)

    @property
    def conical_gear_set_design(self: "CastSelf") -> "_1302.ConicalGearSetDesign":
        from mastapy._private.gears.gear_designs.conical import _1302

        return self.__parent__._cast(_1302.ConicalGearSetDesign)

    @property
    def gear_set_design(self: "CastSelf") -> "_1076.GearSetDesign":
        from mastapy._private.gears.gear_designs import _1076

        return self.__parent__._cast(_1076.GearSetDesign)

    @property
    def gear_design_component(self: "CastSelf") -> "_1074.GearDesignComponent":
        from mastapy._private.gears.gear_designs import _1074

        return self.__parent__._cast(_1074.GearDesignComponent)

    @property
    def spiral_bevel_gear_set_design(self: "CastSelf") -> "SpiralBevelGearSetDesign":
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
class SpiralBevelGearSetDesign(_1328.BevelGearSetDesign):
    """SpiralBevelGearSetDesign

    This is a mastapy class.
    """

    TYPE: ClassVar["Type"] = _SPIRAL_BEVEL_GEAR_SET_DESIGN

    wrapped: "Any"

    def __post_init__(self: "Self") -> None:
        """Override of the post initialisation magic method."""
        if not hasattr(self.wrapped, "reference_count"):
            self.wrapped.reference_count = 0

        self.wrapped.reference_count += 1

    @property
    @exception_bridge
    def minimum_number_of_teeth_for_recommended_tooth_proportions(
        self: "Self",
    ) -> "int":
        """int

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(
            self.wrapped, "MinimumNumberOfTeethForRecommendedToothProportions"
        )

        if temp is None:
            return 0

        return temp

    @property
    @exception_bridge
    def spiral_bevel_gears(self: "Self") -> "List[_1095.SpiralBevelGearDesign]":
        """List[mastapy.gears.gear_designs.spiral_bevel.SpiralBevelGearDesign]

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "SpiralBevelGears")

        if temp is None:
            return None

        value = conversion.pn_to_mp_objects_in_list(temp)

        if value is None:
            return None

        return value

    @property
    @exception_bridge
    def spiral_bevel_meshes(self: "Self") -> "List[_1096.SpiralBevelGearMeshDesign]":
        """List[mastapy.gears.gear_designs.spiral_bevel.SpiralBevelGearMeshDesign]

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "SpiralBevelMeshes")

        if temp is None:
            return None

        value = conversion.pn_to_mp_objects_in_list(temp)

        if value is None:
            return None

        return value

    @property
    def cast_to(self: "Self") -> "_Cast_SpiralBevelGearSetDesign":
        """Cast to another type.

        Returns:
            _Cast_SpiralBevelGearSetDesign
        """
        return _Cast_SpiralBevelGearSetDesign(self)
