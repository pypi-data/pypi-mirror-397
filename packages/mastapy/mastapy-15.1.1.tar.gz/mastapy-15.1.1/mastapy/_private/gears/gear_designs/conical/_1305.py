"""ConicalMeshedGearDesign"""

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

from mastapy._private._internal import utility
from mastapy._private.gears.gear_designs import _1074

_CONICAL_MESHED_GEAR_DESIGN = python_net_import(
    "SMT.MastaAPI.Gears.GearDesigns.Conical", "ConicalMeshedGearDesign"
)

if TYPE_CHECKING:
    from typing import Any, Type, TypeVar

    from mastapy._private.gears.gear_designs.agma_gleason_conical import _1342
    from mastapy._private.gears.gear_designs.bevel import _1329
    from mastapy._private.gears.gear_designs.hypoid import _1114
    from mastapy._private.gears.gear_designs.klingelnberg_conical import _1110
    from mastapy._private.gears.gear_designs.klingelnberg_hypoid import _1106
    from mastapy._private.gears.gear_designs.klingelnberg_spiral_bevel import _1102
    from mastapy._private.gears.gear_designs.spiral_bevel import _1098
    from mastapy._private.gears.gear_designs.straight_bevel import _1090
    from mastapy._private.gears.gear_designs.straight_bevel_diff import _1094
    from mastapy._private.gears.gear_designs.zerol_bevel import _1081

    Self = TypeVar("Self", bound="ConicalMeshedGearDesign")
    CastSelf = TypeVar(
        "CastSelf", bound="ConicalMeshedGearDesign._Cast_ConicalMeshedGearDesign"
    )


__docformat__ = "restructuredtext en"
__all__ = ("ConicalMeshedGearDesign",)


@extended_dataclass(frozen=True, slots=True, weakref_slot=True)
class _Cast_ConicalMeshedGearDesign:
    """Special nested class for casting ConicalMeshedGearDesign to subclasses."""

    __parent__: "ConicalMeshedGearDesign"

    @property
    def gear_design_component(self: "CastSelf") -> "_1074.GearDesignComponent":
        return self.__parent__._cast(_1074.GearDesignComponent)

    @property
    def zerol_bevel_meshed_gear_design(
        self: "CastSelf",
    ) -> "_1081.ZerolBevelMeshedGearDesign":
        from mastapy._private.gears.gear_designs.zerol_bevel import _1081

        return self.__parent__._cast(_1081.ZerolBevelMeshedGearDesign)

    @property
    def straight_bevel_meshed_gear_design(
        self: "CastSelf",
    ) -> "_1090.StraightBevelMeshedGearDesign":
        from mastapy._private.gears.gear_designs.straight_bevel import _1090

        return self.__parent__._cast(_1090.StraightBevelMeshedGearDesign)

    @property
    def straight_bevel_diff_meshed_gear_design(
        self: "CastSelf",
    ) -> "_1094.StraightBevelDiffMeshedGearDesign":
        from mastapy._private.gears.gear_designs.straight_bevel_diff import _1094

        return self.__parent__._cast(_1094.StraightBevelDiffMeshedGearDesign)

    @property
    def spiral_bevel_meshed_gear_design(
        self: "CastSelf",
    ) -> "_1098.SpiralBevelMeshedGearDesign":
        from mastapy._private.gears.gear_designs.spiral_bevel import _1098

        return self.__parent__._cast(_1098.SpiralBevelMeshedGearDesign)

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
    ) -> "_1110.KlingelnbergConicalMeshedGearDesign":
        from mastapy._private.gears.gear_designs.klingelnberg_conical import _1110

        return self.__parent__._cast(_1110.KlingelnbergConicalMeshedGearDesign)

    @property
    def hypoid_meshed_gear_design(self: "CastSelf") -> "_1114.HypoidMeshedGearDesign":
        from mastapy._private.gears.gear_designs.hypoid import _1114

        return self.__parent__._cast(_1114.HypoidMeshedGearDesign)

    @property
    def bevel_meshed_gear_design(self: "CastSelf") -> "_1329.BevelMeshedGearDesign":
        from mastapy._private.gears.gear_designs.bevel import _1329

        return self.__parent__._cast(_1329.BevelMeshedGearDesign)

    @property
    def agma_gleason_conical_meshed_gear_design(
        self: "CastSelf",
    ) -> "_1342.AGMAGleasonConicalMeshedGearDesign":
        from mastapy._private.gears.gear_designs.agma_gleason_conical import _1342

        return self.__parent__._cast(_1342.AGMAGleasonConicalMeshedGearDesign)

    @property
    def conical_meshed_gear_design(self: "CastSelf") -> "ConicalMeshedGearDesign":
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
class ConicalMeshedGearDesign(_1074.GearDesignComponent):
    """ConicalMeshedGearDesign

    This is a mastapy class.
    """

    TYPE: ClassVar["Type"] = _CONICAL_MESHED_GEAR_DESIGN

    wrapped: "Any"

    def __post_init__(self: "Self") -> None:
        """Override of the post initialisation magic method."""
        if not hasattr(self.wrapped, "reference_count"):
            self.wrapped.reference_count = 0

        self.wrapped.reference_count += 1

    @property
    @exception_bridge
    def axial_force_type(self: "Self") -> "str":
        """str

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "AxialForceType")

        if temp is None:
            return ""

        return temp

    @property
    @exception_bridge
    def axial_force_type_convex(self: "Self") -> "str":
        """str

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "AxialForceTypeConvex")

        if temp is None:
            return ""

        return temp

    @property
    @exception_bridge
    def gleason_axial_factor_concave(self: "Self") -> "float":
        """float

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "GleasonAxialFactorConcave")

        if temp is None:
            return 0.0

        return temp

    @property
    @exception_bridge
    def gleason_axial_factor_convex(self: "Self") -> "float":
        """float

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "GleasonAxialFactorConvex")

        if temp is None:
            return 0.0

        return temp

    @property
    @exception_bridge
    def gleason_separating_factor_concave(self: "Self") -> "float":
        """float

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "GleasonSeparatingFactorConcave")

        if temp is None:
            return 0.0

        return temp

    @property
    @exception_bridge
    def gleason_separating_factor_convex(self: "Self") -> "float":
        """float

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "GleasonSeparatingFactorConvex")

        if temp is None:
            return 0.0

        return temp

    @property
    @exception_bridge
    def module(self: "Self") -> "float":
        """float

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "Module")

        if temp is None:
            return 0.0

        return temp

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
    def pitch_angle(self: "Self") -> "float":
        """float

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "PitchAngle")

        if temp is None:
            return 0.0

        return temp

    @property
    @exception_bridge
    def radial_force_type_concave(self: "Self") -> "str":
        """str

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "RadialForceTypeConcave")

        if temp is None:
            return ""

        return temp

    @property
    @exception_bridge
    def radial_force_type_convex(self: "Self") -> "str":
        """str

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "RadialForceTypeConvex")

        if temp is None:
            return ""

        return temp

    @property
    def cast_to(self: "Self") -> "_Cast_ConicalMeshedGearDesign":
        """Cast to another type.

        Returns:
            _Cast_ConicalMeshedGearDesign
        """
        return _Cast_ConicalMeshedGearDesign(self)
