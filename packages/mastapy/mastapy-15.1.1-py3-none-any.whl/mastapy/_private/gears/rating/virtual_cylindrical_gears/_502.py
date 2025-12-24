"""VirtualCylindricalGearBasic"""

from __future__ import annotations

from typing import TYPE_CHECKING, ClassVar

from mastapy._private._internal.dataclasses import extended_dataclass
from mastapy._private._internal.exception_bridge import exception_bridge
from mastapy._private._internal.exceptions import CastException
from mastapy._private._internal.python_net import (
    python_net_import,
    pythonnet_property_get,
)

from mastapy._private import _0
from mastapy._private._internal import utility

_VIRTUAL_CYLINDRICAL_GEAR_BASIC = python_net_import(
    "SMT.MastaAPI.Gears.Rating.VirtualCylindricalGears", "VirtualCylindricalGearBasic"
)

if TYPE_CHECKING:
    from typing import Any, Type, TypeVar

    from mastapy._private.gears.rating.virtual_cylindrical_gears import (
        _491,
        _494,
        _497,
        _498,
        _499,
        _501,
        _503,
        _504,
    )

    Self = TypeVar("Self", bound="VirtualCylindricalGearBasic")
    CastSelf = TypeVar(
        "CastSelf",
        bound="VirtualCylindricalGearBasic._Cast_VirtualCylindricalGearBasic",
    )


__docformat__ = "restructuredtext en"
__all__ = ("VirtualCylindricalGearBasic",)


@extended_dataclass(frozen=True, slots=True, weakref_slot=True)
class _Cast_VirtualCylindricalGearBasic:
    """Special nested class for casting VirtualCylindricalGearBasic to subclasses."""

    __parent__: "VirtualCylindricalGearBasic"

    @property
    def bevel_virtual_cylindrical_gear_iso10300_method_b2(
        self: "CastSelf",
    ) -> "_491.BevelVirtualCylindricalGearISO10300MethodB2":
        from mastapy._private.gears.rating.virtual_cylindrical_gears import _491

        return self.__parent__._cast(_491.BevelVirtualCylindricalGearISO10300MethodB2)

    @property
    def hypoid_virtual_cylindrical_gear_iso10300_method_b2(
        self: "CastSelf",
    ) -> "_494.HypoidVirtualCylindricalGearISO10300MethodB2":
        from mastapy._private.gears.rating.virtual_cylindrical_gears import _494

        return self.__parent__._cast(_494.HypoidVirtualCylindricalGearISO10300MethodB2)

    @property
    def klingelnberg_hypoid_virtual_cylindrical_gear(
        self: "CastSelf",
    ) -> "_497.KlingelnbergHypoidVirtualCylindricalGear":
        from mastapy._private.gears.rating.virtual_cylindrical_gears import _497

        return self.__parent__._cast(_497.KlingelnbergHypoidVirtualCylindricalGear)

    @property
    def klingelnberg_spiral_bevel_virtual_cylindrical_gear(
        self: "CastSelf",
    ) -> "_498.KlingelnbergSpiralBevelVirtualCylindricalGear":
        from mastapy._private.gears.rating.virtual_cylindrical_gears import _498

        return self.__parent__._cast(_498.KlingelnbergSpiralBevelVirtualCylindricalGear)

    @property
    def klingelnberg_virtual_cylindrical_gear(
        self: "CastSelf",
    ) -> "_499.KlingelnbergVirtualCylindricalGear":
        from mastapy._private.gears.rating.virtual_cylindrical_gears import _499

        return self.__parent__._cast(_499.KlingelnbergVirtualCylindricalGear)

    @property
    def virtual_cylindrical_gear(self: "CastSelf") -> "_501.VirtualCylindricalGear":
        from mastapy._private.gears.rating.virtual_cylindrical_gears import _501

        return self.__parent__._cast(_501.VirtualCylindricalGear)

    @property
    def virtual_cylindrical_gear_iso10300_method_b1(
        self: "CastSelf",
    ) -> "_503.VirtualCylindricalGearISO10300MethodB1":
        from mastapy._private.gears.rating.virtual_cylindrical_gears import _503

        return self.__parent__._cast(_503.VirtualCylindricalGearISO10300MethodB1)

    @property
    def virtual_cylindrical_gear_iso10300_method_b2(
        self: "CastSelf",
    ) -> "_504.VirtualCylindricalGearISO10300MethodB2":
        from mastapy._private.gears.rating.virtual_cylindrical_gears import _504

        return self.__parent__._cast(_504.VirtualCylindricalGearISO10300MethodB2)

    @property
    def virtual_cylindrical_gear_basic(
        self: "CastSelf",
    ) -> "VirtualCylindricalGearBasic":
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
class VirtualCylindricalGearBasic(_0.APIBase):
    """VirtualCylindricalGearBasic

    This is a mastapy class.
    """

    TYPE: ClassVar["Type"] = _VIRTUAL_CYLINDRICAL_GEAR_BASIC

    wrapped: "Any"

    def __post_init__(self: "Self") -> None:
        """Override of the post initialisation magic method."""
        if not hasattr(self.wrapped, "reference_count"):
            self.wrapped.reference_count = 0

        self.wrapped.reference_count += 1

    @property
    @exception_bridge
    def helix_angle_at_base_circle_of_virtual_cylindrical_gears(
        self: "Self",
    ) -> "float":
        """float

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(
            self.wrapped, "HelixAngleAtBaseCircleOfVirtualCylindricalGears"
        )

        if temp is None:
            return 0.0

        return temp

    @property
    @exception_bridge
    def helix_angle_of_virtual_cylindrical_gears(self: "Self") -> "float":
        """float

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(
            self.wrapped, "HelixAngleOfVirtualCylindricalGears"
        )

        if temp is None:
            return 0.0

        return temp

    @property
    @exception_bridge
    def name(self: "Self") -> "str":
        """str

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "Name")

        if temp is None:
            return ""

        return temp

    @property
    @exception_bridge
    def normal_module(self: "Self") -> "float":
        """float

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "NormalModule")

        if temp is None:
            return 0.0

        return temp

    @property
    @exception_bridge
    def reference_diameter_of_virtual_cylindrical_gear(self: "Self") -> "float":
        """float

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(
            self.wrapped, "ReferenceDiameterOfVirtualCylindricalGear"
        )

        if temp is None:
            return 0.0

        return temp

    @property
    @exception_bridge
    def tip_diameter_of_virtual_cylindrical_gear(self: "Self") -> "float":
        """float

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(
            self.wrapped, "TipDiameterOfVirtualCylindricalGear"
        )

        if temp is None:
            return 0.0

        return temp

    @property
    @exception_bridge
    def tip_radius_of_virtual_cylindrical_gear(self: "Self") -> "float":
        """float

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "TipRadiusOfVirtualCylindricalGear")

        if temp is None:
            return 0.0

        return temp

    @property
    def cast_to(self: "Self") -> "_Cast_VirtualCylindricalGearBasic":
        """Cast to another type.

        Returns:
            _Cast_VirtualCylindricalGearBasic
        """
        return _Cast_VirtualCylindricalGearBasic(self)
