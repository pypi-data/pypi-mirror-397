"""ConicalGearMeshDesign"""

from __future__ import annotations

from typing import TYPE_CHECKING, ClassVar

from mastapy._private._internal.dataclasses import extended_dataclass
from mastapy._private._internal.exception_bridge import exception_bridge
from mastapy._private._internal.exceptions import CastException
from mastapy._private._internal.overridable_constructor import _unpack_overridable
from mastapy._private._internal.python_net import (
    python_net_import,
    pythonnet_property_get,
    pythonnet_property_set,
)
from mastapy._private._internal.type_enforcement import enforce_parameter_types

from mastapy._private._internal import constructor, conversion, utility
from mastapy._private._internal.implicit import overridable
from mastapy._private.gears.gear_designs import _1075

_CONICAL_GEAR_MESH_DESIGN = python_net_import(
    "SMT.MastaAPI.Gears.GearDesigns.Conical", "ConicalGearMeshDesign"
)

if TYPE_CHECKING:
    from typing import Any, Tuple, Type, TypeVar, Union

    from mastapy._private.gears.gear_designs import _1074
    from mastapy._private.gears.gear_designs.agma_gleason_conical import _1340
    from mastapy._private.gears.gear_designs.bevel import _1327, _1330, _1333, _1334
    from mastapy._private.gears.gear_designs.conical import _1300
    from mastapy._private.gears.gear_designs.hypoid import _1112
    from mastapy._private.gears.gear_designs.klingelnberg_conical import _1108
    from mastapy._private.gears.gear_designs.klingelnberg_hypoid import _1104
    from mastapy._private.gears.gear_designs.klingelnberg_spiral_bevel import _1100
    from mastapy._private.gears.gear_designs.spiral_bevel import _1096
    from mastapy._private.gears.gear_designs.straight_bevel import _1088
    from mastapy._private.gears.gear_designs.straight_bevel_diff import _1092
    from mastapy._private.gears.gear_designs.zerol_bevel import _1079

    Self = TypeVar("Self", bound="ConicalGearMeshDesign")
    CastSelf = TypeVar(
        "CastSelf", bound="ConicalGearMeshDesign._Cast_ConicalGearMeshDesign"
    )


__docformat__ = "restructuredtext en"
__all__ = ("ConicalGearMeshDesign",)


@extended_dataclass(frozen=True, slots=True, weakref_slot=True)
class _Cast_ConicalGearMeshDesign:
    """Special nested class for casting ConicalGearMeshDesign to subclasses."""

    __parent__: "ConicalGearMeshDesign"

    @property
    def gear_mesh_design(self: "CastSelf") -> "_1075.GearMeshDesign":
        return self.__parent__._cast(_1075.GearMeshDesign)

    @property
    def gear_design_component(self: "CastSelf") -> "_1074.GearDesignComponent":
        from mastapy._private.gears.gear_designs import _1074

        return self.__parent__._cast(_1074.GearDesignComponent)

    @property
    def zerol_bevel_gear_mesh_design(
        self: "CastSelf",
    ) -> "_1079.ZerolBevelGearMeshDesign":
        from mastapy._private.gears.gear_designs.zerol_bevel import _1079

        return self.__parent__._cast(_1079.ZerolBevelGearMeshDesign)

    @property
    def straight_bevel_gear_mesh_design(
        self: "CastSelf",
    ) -> "_1088.StraightBevelGearMeshDesign":
        from mastapy._private.gears.gear_designs.straight_bevel import _1088

        return self.__parent__._cast(_1088.StraightBevelGearMeshDesign)

    @property
    def straight_bevel_diff_gear_mesh_design(
        self: "CastSelf",
    ) -> "_1092.StraightBevelDiffGearMeshDesign":
        from mastapy._private.gears.gear_designs.straight_bevel_diff import _1092

        return self.__parent__._cast(_1092.StraightBevelDiffGearMeshDesign)

    @property
    def spiral_bevel_gear_mesh_design(
        self: "CastSelf",
    ) -> "_1096.SpiralBevelGearMeshDesign":
        from mastapy._private.gears.gear_designs.spiral_bevel import _1096

        return self.__parent__._cast(_1096.SpiralBevelGearMeshDesign)

    @property
    def klingelnberg_cyclo_palloid_spiral_bevel_gear_mesh_design(
        self: "CastSelf",
    ) -> "_1100.KlingelnbergCycloPalloidSpiralBevelGearMeshDesign":
        from mastapy._private.gears.gear_designs.klingelnberg_spiral_bevel import _1100

        return self.__parent__._cast(
            _1100.KlingelnbergCycloPalloidSpiralBevelGearMeshDesign
        )

    @property
    def klingelnberg_cyclo_palloid_hypoid_gear_mesh_design(
        self: "CastSelf",
    ) -> "_1104.KlingelnbergCycloPalloidHypoidGearMeshDesign":
        from mastapy._private.gears.gear_designs.klingelnberg_hypoid import _1104

        return self.__parent__._cast(_1104.KlingelnbergCycloPalloidHypoidGearMeshDesign)

    @property
    def klingelnberg_conical_gear_mesh_design(
        self: "CastSelf",
    ) -> "_1108.KlingelnbergConicalGearMeshDesign":
        from mastapy._private.gears.gear_designs.klingelnberg_conical import _1108

        return self.__parent__._cast(_1108.KlingelnbergConicalGearMeshDesign)

    @property
    def hypoid_gear_mesh_design(self: "CastSelf") -> "_1112.HypoidGearMeshDesign":
        from mastapy._private.gears.gear_designs.hypoid import _1112

        return self.__parent__._cast(_1112.HypoidGearMeshDesign)

    @property
    def bevel_gear_mesh_design(self: "CastSelf") -> "_1327.BevelGearMeshDesign":
        from mastapy._private.gears.gear_designs.bevel import _1327

        return self.__parent__._cast(_1327.BevelGearMeshDesign)

    @property
    def agma_gleason_conical_gear_mesh_design(
        self: "CastSelf",
    ) -> "_1340.AGMAGleasonConicalGearMeshDesign":
        from mastapy._private.gears.gear_designs.agma_gleason_conical import _1340

        return self.__parent__._cast(_1340.AGMAGleasonConicalGearMeshDesign)

    @property
    def conical_gear_mesh_design(self: "CastSelf") -> "ConicalGearMeshDesign":
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
class ConicalGearMeshDesign(_1075.GearMeshDesign):
    """ConicalGearMeshDesign

    This is a mastapy class.
    """

    TYPE: ClassVar["Type"] = _CONICAL_GEAR_MESH_DESIGN

    wrapped: "Any"

    def __post_init__(self: "Self") -> None:
        """Override of the post initialisation magic method."""
        if not hasattr(self.wrapped, "reference_count"):
            self.wrapped.reference_count = 0

        self.wrapped.reference_count += 1

    @property
    @exception_bridge
    def driven_machine_characteristic(
        self: "Self",
    ) -> "_1333.MachineCharacteristicAGMAKlingelnberg":
        """mastapy.gears.gear_designs.bevel.MachineCharacteristicAGMAKlingelnberg"""
        temp = pythonnet_property_get(self.wrapped, "DrivenMachineCharacteristic")

        if temp is None:
            return None

        value = conversion.pn_to_mp_enum(
            temp,
            "SMT.MastaAPI.Gears.GearDesigns.Bevel.MachineCharacteristicAGMAKlingelnberg",
        )

        if value is None:
            return None

        return constructor.new_from_mastapy(
            "mastapy._private.gears.gear_designs.bevel._1333",
            "MachineCharacteristicAGMAKlingelnberg",
        )(value)

    @driven_machine_characteristic.setter
    @exception_bridge
    @enforce_parameter_types
    def driven_machine_characteristic(
        self: "Self", value: "_1333.MachineCharacteristicAGMAKlingelnberg"
    ) -> None:
        value = conversion.mp_to_pn_enum(
            value,
            "SMT.MastaAPI.Gears.GearDesigns.Bevel.MachineCharacteristicAGMAKlingelnberg",
        )
        pythonnet_property_set(self.wrapped, "DrivenMachineCharacteristic", value)

    @property
    @exception_bridge
    def driven_machine_characteristic_gleason(
        self: "Self",
    ) -> "_1330.DrivenMachineCharacteristicGleason":
        """mastapy.gears.gear_designs.bevel.DrivenMachineCharacteristicGleason"""
        temp = pythonnet_property_get(
            self.wrapped, "DrivenMachineCharacteristicGleason"
        )

        if temp is None:
            return None

        value = conversion.pn_to_mp_enum(
            temp,
            "SMT.MastaAPI.Gears.GearDesigns.Bevel.DrivenMachineCharacteristicGleason",
        )

        if value is None:
            return None

        return constructor.new_from_mastapy(
            "mastapy._private.gears.gear_designs.bevel._1330",
            "DrivenMachineCharacteristicGleason",
        )(value)

    @driven_machine_characteristic_gleason.setter
    @exception_bridge
    @enforce_parameter_types
    def driven_machine_characteristic_gleason(
        self: "Self", value: "_1330.DrivenMachineCharacteristicGleason"
    ) -> None:
        value = conversion.mp_to_pn_enum(
            value,
            "SMT.MastaAPI.Gears.GearDesigns.Bevel.DrivenMachineCharacteristicGleason",
        )
        pythonnet_property_set(
            self.wrapped, "DrivenMachineCharacteristicGleason", value
        )

    @property
    @exception_bridge
    def maximum_normal_backlash(self: "Self") -> "float":
        """float

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "MaximumNormalBacklash")

        if temp is None:
            return 0.0

        return temp

    @property
    @exception_bridge
    def minimum_normal_backlash(self: "Self") -> "float":
        """float

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "MinimumNormalBacklash")

        if temp is None:
            return 0.0

        return temp

    @property
    @exception_bridge
    def overload_factor(self: "Self") -> "overridable.Overridable_float":
        """Overridable[float]"""
        temp = pythonnet_property_get(self.wrapped, "OverloadFactor")

        if temp is None:
            return 0.0

        return constructor.new_from_mastapy(
            "mastapy._private._internal.implicit.overridable", "Overridable_float"
        )(temp)

    @overload_factor.setter
    @exception_bridge
    @enforce_parameter_types
    def overload_factor(
        self: "Self", value: "Union[float, Tuple[float, bool]]"
    ) -> None:
        wrapper_type = overridable.Overridable_float.wrapper_type()
        enclosed_type = overridable.Overridable_float.implicit_type()
        value, is_overridden = _unpack_overridable(value)
        value = wrapper_type[enclosed_type](
            enclosed_type(value) if value is not None else 0.0, is_overridden
        )
        pythonnet_property_set(self.wrapped, "OverloadFactor", value)

    @property
    @exception_bridge
    def pinion_full_circle_edge_radius(self: "Self") -> "float":
        """float

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "PinionFullCircleEdgeRadius")

        if temp is None:
            return 0.0

        return temp

    @property
    @exception_bridge
    def prime_mover_characteristic(
        self: "Self",
    ) -> "_1333.MachineCharacteristicAGMAKlingelnberg":
        """mastapy.gears.gear_designs.bevel.MachineCharacteristicAGMAKlingelnberg"""
        temp = pythonnet_property_get(self.wrapped, "PrimeMoverCharacteristic")

        if temp is None:
            return None

        value = conversion.pn_to_mp_enum(
            temp,
            "SMT.MastaAPI.Gears.GearDesigns.Bevel.MachineCharacteristicAGMAKlingelnberg",
        )

        if value is None:
            return None

        return constructor.new_from_mastapy(
            "mastapy._private.gears.gear_designs.bevel._1333",
            "MachineCharacteristicAGMAKlingelnberg",
        )(value)

    @prime_mover_characteristic.setter
    @exception_bridge
    @enforce_parameter_types
    def prime_mover_characteristic(
        self: "Self", value: "_1333.MachineCharacteristicAGMAKlingelnberg"
    ) -> None:
        value = conversion.mp_to_pn_enum(
            value,
            "SMT.MastaAPI.Gears.GearDesigns.Bevel.MachineCharacteristicAGMAKlingelnberg",
        )
        pythonnet_property_set(self.wrapped, "PrimeMoverCharacteristic", value)

    @property
    @exception_bridge
    def prime_mover_characteristic_gleason(
        self: "Self",
    ) -> "_1334.PrimeMoverCharacteristicGleason":
        """mastapy.gears.gear_designs.bevel.PrimeMoverCharacteristicGleason"""
        temp = pythonnet_property_get(self.wrapped, "PrimeMoverCharacteristicGleason")

        if temp is None:
            return None

        value = conversion.pn_to_mp_enum(
            temp, "SMT.MastaAPI.Gears.GearDesigns.Bevel.PrimeMoverCharacteristicGleason"
        )

        if value is None:
            return None

        return constructor.new_from_mastapy(
            "mastapy._private.gears.gear_designs.bevel._1334",
            "PrimeMoverCharacteristicGleason",
        )(value)

    @prime_mover_characteristic_gleason.setter
    @exception_bridge
    @enforce_parameter_types
    def prime_mover_characteristic_gleason(
        self: "Self", value: "_1334.PrimeMoverCharacteristicGleason"
    ) -> None:
        value = conversion.mp_to_pn_enum(
            value,
            "SMT.MastaAPI.Gears.GearDesigns.Bevel.PrimeMoverCharacteristicGleason",
        )
        pythonnet_property_set(self.wrapped, "PrimeMoverCharacteristicGleason", value)

    @property
    @exception_bridge
    def shaft_angle(self: "Self") -> "float":
        """float"""
        temp = pythonnet_property_get(self.wrapped, "ShaftAngle")

        if temp is None:
            return 0.0

        return temp

    @shaft_angle.setter
    @exception_bridge
    @enforce_parameter_types
    def shaft_angle(self: "Self", value: "float") -> None:
        pythonnet_property_set(
            self.wrapped, "ShaftAngle", float(value) if value is not None else 0.0
        )

    @property
    @exception_bridge
    def specified_backlash_range_max(self: "Self") -> "float":
        """float"""
        temp = pythonnet_property_get(self.wrapped, "SpecifiedBacklashRangeMax")

        if temp is None:
            return 0.0

        return temp

    @specified_backlash_range_max.setter
    @exception_bridge
    @enforce_parameter_types
    def specified_backlash_range_max(self: "Self", value: "float") -> None:
        pythonnet_property_set(
            self.wrapped,
            "SpecifiedBacklashRangeMax",
            float(value) if value is not None else 0.0,
        )

    @property
    @exception_bridge
    def specified_backlash_range_min(self: "Self") -> "float":
        """float"""
        temp = pythonnet_property_get(self.wrapped, "SpecifiedBacklashRangeMin")

        if temp is None:
            return 0.0

        return temp

    @specified_backlash_range_min.setter
    @exception_bridge
    @enforce_parameter_types
    def specified_backlash_range_min(self: "Self", value: "float") -> None:
        pythonnet_property_set(
            self.wrapped,
            "SpecifiedBacklashRangeMin",
            float(value) if value is not None else 0.0,
        )

    @property
    @exception_bridge
    def specify_backlash(self: "Self") -> "bool":
        """bool"""
        temp = pythonnet_property_get(self.wrapped, "SpecifyBacklash")

        if temp is None:
            return False

        return temp

    @specify_backlash.setter
    @exception_bridge
    @enforce_parameter_types
    def specify_backlash(self: "Self", value: "bool") -> None:
        pythonnet_property_set(
            self.wrapped, "SpecifyBacklash", bool(value) if value is not None else False
        )

    @property
    @exception_bridge
    def gear_a(self: "Self") -> "_1300.ConicalGearDesign":
        """mastapy.gears.gear_designs.conical.ConicalGearDesign

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
    def gear_b(self: "Self") -> "_1300.ConicalGearDesign":
        """mastapy.gears.gear_designs.conical.ConicalGearDesign

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "GearB")

        if temp is None:
            return None

        type_ = temp.GetType()
        return constructor.new(type_.Namespace, type_.Name)(temp)

    @property
    def cast_to(self: "Self") -> "_Cast_ConicalGearMeshDesign":
        """Cast to another type.

        Returns:
            _Cast_ConicalGearMeshDesign
        """
        return _Cast_ConicalGearMeshDesign(self)
