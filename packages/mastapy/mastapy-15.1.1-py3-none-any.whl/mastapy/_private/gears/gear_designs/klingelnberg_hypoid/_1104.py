"""KlingelnbergCycloPalloidHypoidGearMeshDesign"""

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
from mastapy._private.gears.gear_designs.klingelnberg_conical import _1108

_KLINGELNBERG_CYCLO_PALLOID_HYPOID_GEAR_MESH_DESIGN = python_net_import(
    "SMT.MastaAPI.Gears.GearDesigns.KlingelnbergHypoid",
    "KlingelnbergCycloPalloidHypoidGearMeshDesign",
)

if TYPE_CHECKING:
    from typing import Any, List, Type, TypeVar

    from mastapy._private.gears.gear_designs import _1074, _1075
    from mastapy._private.gears.gear_designs.conical import _1301
    from mastapy._private.gears.gear_designs.klingelnberg_hypoid import (
        _1103,
        _1105,
        _1106,
    )

    Self = TypeVar("Self", bound="KlingelnbergCycloPalloidHypoidGearMeshDesign")
    CastSelf = TypeVar(
        "CastSelf",
        bound="KlingelnbergCycloPalloidHypoidGearMeshDesign._Cast_KlingelnbergCycloPalloidHypoidGearMeshDesign",
    )


__docformat__ = "restructuredtext en"
__all__ = ("KlingelnbergCycloPalloidHypoidGearMeshDesign",)


@extended_dataclass(frozen=True, slots=True, weakref_slot=True)
class _Cast_KlingelnbergCycloPalloidHypoidGearMeshDesign:
    """Special nested class for casting KlingelnbergCycloPalloidHypoidGearMeshDesign to subclasses."""

    __parent__: "KlingelnbergCycloPalloidHypoidGearMeshDesign"

    @property
    def klingelnberg_conical_gear_mesh_design(
        self: "CastSelf",
    ) -> "_1108.KlingelnbergConicalGearMeshDesign":
        return self.__parent__._cast(_1108.KlingelnbergConicalGearMeshDesign)

    @property
    def conical_gear_mesh_design(self: "CastSelf") -> "_1301.ConicalGearMeshDesign":
        from mastapy._private.gears.gear_designs.conical import _1301

        return self.__parent__._cast(_1301.ConicalGearMeshDesign)

    @property
    def gear_mesh_design(self: "CastSelf") -> "_1075.GearMeshDesign":
        from mastapy._private.gears.gear_designs import _1075

        return self.__parent__._cast(_1075.GearMeshDesign)

    @property
    def gear_design_component(self: "CastSelf") -> "_1074.GearDesignComponent":
        from mastapy._private.gears.gear_designs import _1074

        return self.__parent__._cast(_1074.GearDesignComponent)

    @property
    def klingelnberg_cyclo_palloid_hypoid_gear_mesh_design(
        self: "CastSelf",
    ) -> "KlingelnbergCycloPalloidHypoidGearMeshDesign":
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
class KlingelnbergCycloPalloidHypoidGearMeshDesign(
    _1108.KlingelnbergConicalGearMeshDesign
):
    """KlingelnbergCycloPalloidHypoidGearMeshDesign

    This is a mastapy class.
    """

    TYPE: ClassVar["Type"] = _KLINGELNBERG_CYCLO_PALLOID_HYPOID_GEAR_MESH_DESIGN

    wrapped: "Any"

    def __post_init__(self: "Self") -> None:
        """Override of the post initialisation magic method."""
        if not hasattr(self.wrapped, "reference_count"):
            self.wrapped.reference_count = 0

        self.wrapped.reference_count += 1

    @property
    @exception_bridge
    def klingelnberg_cyclo_palloid_hypoid_gear_set(
        self: "Self",
    ) -> "_1105.KlingelnbergCycloPalloidHypoidGearSetDesign":
        """mastapy.gears.gear_designs.klingelnberg_hypoid.KlingelnbergCycloPalloidHypoidGearSetDesign

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(
            self.wrapped, "KlingelnbergCycloPalloidHypoidGearSet"
        )

        if temp is None:
            return None

        type_ = temp.GetType()
        return constructor.new(type_.Namespace, type_.Name)(temp)

    @property
    @exception_bridge
    def klingelnberg_cyclo_palloid_hypoid_gears(
        self: "Self",
    ) -> "List[_1103.KlingelnbergCycloPalloidHypoidGearDesign]":
        """List[mastapy.gears.gear_designs.klingelnberg_hypoid.KlingelnbergCycloPalloidHypoidGearDesign]

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(
            self.wrapped, "KlingelnbergCycloPalloidHypoidGears"
        )

        if temp is None:
            return None

        value = conversion.pn_to_mp_objects_in_list(temp)

        if value is None:
            return None

        return value

    @property
    @exception_bridge
    def klingelnberg_cyclo_palloid_hypoid_meshed_gears(
        self: "Self",
    ) -> "List[_1106.KlingelnbergCycloPalloidHypoidMeshedGearDesign]":
        """List[mastapy.gears.gear_designs.klingelnberg_hypoid.KlingelnbergCycloPalloidHypoidMeshedGearDesign]

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(
            self.wrapped, "KlingelnbergCycloPalloidHypoidMeshedGears"
        )

        if temp is None:
            return None

        value = conversion.pn_to_mp_objects_in_list(temp)

        if value is None:
            return None

        return value

    @property
    @exception_bridge
    def gear_a(self: "Self") -> "_1103.KlingelnbergCycloPalloidHypoidGearDesign":
        """mastapy.gears.gear_designs.klingelnberg_hypoid.KlingelnbergCycloPalloidHypoidGearDesign

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "GearA")

        if temp is None:
            return None

        type_ = temp.GetType()
        return constructor.new(type_.Namespace, type_.Name)(temp)

    @property
    @exception_bridge
    def gear_b(self: "Self") -> "_1103.KlingelnbergCycloPalloidHypoidGearDesign":
        """mastapy.gears.gear_designs.klingelnberg_hypoid.KlingelnbergCycloPalloidHypoidGearDesign

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "GearB")

        if temp is None:
            return None

        type_ = temp.GetType()
        return constructor.new(type_.Namespace, type_.Name)(temp)

    @property
    def cast_to(self: "Self") -> "_Cast_KlingelnbergCycloPalloidHypoidGearMeshDesign":
        """Cast to another type.

        Returns:
            _Cast_KlingelnbergCycloPalloidHypoidGearMeshDesign
        """
        return _Cast_KlingelnbergCycloPalloidHypoidGearMeshDesign(self)
