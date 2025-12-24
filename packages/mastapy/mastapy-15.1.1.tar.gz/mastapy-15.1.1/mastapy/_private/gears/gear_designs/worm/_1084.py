"""WormGearMeshDesign"""

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
from mastapy._private.gears.gear_designs import _1075

_WORM_GEAR_MESH_DESIGN = python_net_import(
    "SMT.MastaAPI.Gears.GearDesigns.Worm", "WormGearMeshDesign"
)

if TYPE_CHECKING:
    from typing import Any, List, Type, TypeVar

    from mastapy._private.gears.gear_designs import _1074
    from mastapy._private.gears.gear_designs.worm import _1082, _1083, _1085, _1086

    Self = TypeVar("Self", bound="WormGearMeshDesign")
    CastSelf = TypeVar("CastSelf", bound="WormGearMeshDesign._Cast_WormGearMeshDesign")


__docformat__ = "restructuredtext en"
__all__ = ("WormGearMeshDesign",)


@extended_dataclass(frozen=True, slots=True, weakref_slot=True)
class _Cast_WormGearMeshDesign:
    """Special nested class for casting WormGearMeshDesign to subclasses."""

    __parent__: "WormGearMeshDesign"

    @property
    def gear_mesh_design(self: "CastSelf") -> "_1075.GearMeshDesign":
        return self.__parent__._cast(_1075.GearMeshDesign)

    @property
    def gear_design_component(self: "CastSelf") -> "_1074.GearDesignComponent":
        from mastapy._private.gears.gear_designs import _1074

        return self.__parent__._cast(_1074.GearDesignComponent)

    @property
    def worm_gear_mesh_design(self: "CastSelf") -> "WormGearMeshDesign":
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
class WormGearMeshDesign(_1075.GearMeshDesign):
    """WormGearMeshDesign

    This is a mastapy class.
    """

    TYPE: ClassVar["Type"] = _WORM_GEAR_MESH_DESIGN

    wrapped: "Any"

    def __post_init__(self: "Self") -> None:
        """Override of the post initialisation magic method."""
        if not hasattr(self.wrapped, "reference_count"):
            self.wrapped.reference_count = 0

        self.wrapped.reference_count += 1

    @property
    @exception_bridge
    def centre_distance(self: "Self") -> "float":
        """float"""
        temp = pythonnet_property_get(self.wrapped, "CentreDistance")

        if temp is None:
            return 0.0

        return temp

    @centre_distance.setter
    @exception_bridge
    @enforce_parameter_types
    def centre_distance(self: "Self", value: "float") -> None:
        pythonnet_property_set(
            self.wrapped, "CentreDistance", float(value) if value is not None else 0.0
        )

    @property
    @exception_bridge
    def coefficient_of_friction(self: "Self") -> "float":
        """float"""
        temp = pythonnet_property_get(self.wrapped, "CoefficientOfFriction")

        if temp is None:
            return 0.0

        return temp

    @coefficient_of_friction.setter
    @exception_bridge
    @enforce_parameter_types
    def coefficient_of_friction(self: "Self", value: "float") -> None:
        pythonnet_property_set(
            self.wrapped,
            "CoefficientOfFriction",
            float(value) if value is not None else 0.0,
        )

    @property
    @exception_bridge
    def meshing_friction_angle(self: "Self") -> "float":
        """float"""
        temp = pythonnet_property_get(self.wrapped, "MeshingFrictionAngle")

        if temp is None:
            return 0.0

        return temp

    @meshing_friction_angle.setter
    @exception_bridge
    @enforce_parameter_types
    def meshing_friction_angle(self: "Self", value: "float") -> None:
        pythonnet_property_set(
            self.wrapped,
            "MeshingFrictionAngle",
            float(value) if value is not None else 0.0,
        )

    @property
    @exception_bridge
    def shaft_angle(self: "Self") -> "float":
        """float

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "ShaftAngle")

        if temp is None:
            return 0.0

        return temp

    @property
    @exception_bridge
    def standard_centre_distance(self: "Self") -> "float":
        """float"""
        temp = pythonnet_property_get(self.wrapped, "StandardCentreDistance")

        if temp is None:
            return 0.0

        return temp

    @standard_centre_distance.setter
    @exception_bridge
    @enforce_parameter_types
    def standard_centre_distance(self: "Self", value: "float") -> None:
        pythonnet_property_set(
            self.wrapped,
            "StandardCentreDistance",
            float(value) if value is not None else 0.0,
        )

    @property
    @exception_bridge
    def wheel_addendum_modification_factor(self: "Self") -> "float":
        """float"""
        temp = pythonnet_property_get(self.wrapped, "WheelAddendumModificationFactor")

        if temp is None:
            return 0.0

        return temp

    @wheel_addendum_modification_factor.setter
    @exception_bridge
    @enforce_parameter_types
    def wheel_addendum_modification_factor(self: "Self", value: "float") -> None:
        pythonnet_property_set(
            self.wrapped,
            "WheelAddendumModificationFactor",
            float(value) if value is not None else 0.0,
        )

    @property
    @exception_bridge
    def wheel(self: "Self") -> "_1086.WormWheelDesign":
        """mastapy.gears.gear_designs.worm.WormWheelDesign

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "Wheel")

        if temp is None:
            return None

        type_ = temp.GetType()
        return constructor.new(type_.Namespace, type_.Name)(temp)

    @property
    @exception_bridge
    def worm(self: "Self") -> "_1082.WormDesign":
        """mastapy.gears.gear_designs.worm.WormDesign

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "Worm")

        if temp is None:
            return None

        type_ = temp.GetType()
        return constructor.new(type_.Namespace, type_.Name)(temp)

    @property
    @exception_bridge
    def worm_gear_set(self: "Self") -> "_1085.WormGearSetDesign":
        """mastapy.gears.gear_designs.worm.WormGearSetDesign

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "WormGearSet")

        if temp is None:
            return None

        type_ = temp.GetType()
        return constructor.new(type_.Namespace, type_.Name)(temp)

    @property
    @exception_bridge
    def worm_gears(self: "Self") -> "List[_1083.WormGearDesign]":
        """List[mastapy.gears.gear_designs.worm.WormGearDesign]

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "WormGears")

        if temp is None:
            return None

        value = conversion.pn_to_mp_objects_in_list(temp)

        if value is None:
            return None

        return value

    @property
    @exception_bridge
    def gear_a(self: "Self") -> "_1083.WormGearDesign":
        """mastapy.gears.gear_designs.worm.WormGearDesign

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
    def gear_b(self: "Self") -> "_1083.WormGearDesign":
        """mastapy.gears.gear_designs.worm.WormGearDesign

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "GearB")

        if temp is None:
            return None

        type_ = temp.GetType()
        return constructor.new(type_.Namespace, type_.Name)(temp)

    @property
    def cast_to(self: "Self") -> "_Cast_WormGearMeshDesign":
        """Cast to another type.

        Returns:
            _Cast_WormGearMeshDesign
        """
        return _Cast_WormGearMeshDesign(self)
