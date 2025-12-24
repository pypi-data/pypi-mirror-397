"""BevelDifferentialGearSet"""

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
from mastapy._private.system_model.part_model.gears import _2801

_BEVEL_DIFFERENTIAL_GEAR_SET = python_net_import(
    "SMT.MastaAPI.SystemModel.PartModel.Gears", "BevelDifferentialGearSet"
)

if TYPE_CHECKING:
    from typing import Any, List, Type, TypeVar

    from mastapy._private.gears.gear_designs.bevel import _1328
    from mastapy._private.system_model import _2451
    from mastapy._private.system_model.connections_and_sockets.gears import _2562
    from mastapy._private.system_model.part_model import _2703, _2742, _2752
    from mastapy._private.system_model.part_model.gears import (
        _2795,
        _2800,
        _2805,
        _2813,
    )

    Self = TypeVar("Self", bound="BevelDifferentialGearSet")
    CastSelf = TypeVar(
        "CastSelf", bound="BevelDifferentialGearSet._Cast_BevelDifferentialGearSet"
    )


__docformat__ = "restructuredtext en"
__all__ = ("BevelDifferentialGearSet",)


@extended_dataclass(frozen=True, slots=True, weakref_slot=True)
class _Cast_BevelDifferentialGearSet:
    """Special nested class for casting BevelDifferentialGearSet to subclasses."""

    __parent__: "BevelDifferentialGearSet"

    @property
    def bevel_gear_set(self: "CastSelf") -> "_2801.BevelGearSet":
        return self.__parent__._cast(_2801.BevelGearSet)

    @property
    def agma_gleason_conical_gear_set(
        self: "CastSelf",
    ) -> "_2795.AGMAGleasonConicalGearSet":
        from mastapy._private.system_model.part_model.gears import _2795

        return self.__parent__._cast(_2795.AGMAGleasonConicalGearSet)

    @property
    def conical_gear_set(self: "CastSelf") -> "_2805.ConicalGearSet":
        from mastapy._private.system_model.part_model.gears import _2805

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
    def bevel_differential_gear_set(self: "CastSelf") -> "BevelDifferentialGearSet":
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
class BevelDifferentialGearSet(_2801.BevelGearSet):
    """BevelDifferentialGearSet

    This is a mastapy class.
    """

    TYPE: ClassVar["Type"] = _BEVEL_DIFFERENTIAL_GEAR_SET

    wrapped: "Any"

    def __post_init__(self: "Self") -> None:
        """Override of the post initialisation magic method."""
        if not hasattr(self.wrapped, "reference_count"):
            self.wrapped.reference_count = 0

        self.wrapped.reference_count += 1

    @property
    @exception_bridge
    def conical_gear_set_design(self: "Self") -> "_1328.BevelGearSetDesign":
        """mastapy.gears.gear_designs.bevel.BevelGearSetDesign

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "ConicalGearSetDesign")

        if temp is None:
            return None

        type_ = temp.GetType()
        return constructor.new(type_.Namespace, type_.Name)(temp)

    @property
    @exception_bridge
    def bevel_gear_set_design(self: "Self") -> "_1328.BevelGearSetDesign":
        """mastapy.gears.gear_designs.bevel.BevelGearSetDesign

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "BevelGearSetDesign")

        if temp is None:
            return None

        type_ = temp.GetType()
        return constructor.new(type_.Namespace, type_.Name)(temp)

    @property
    @exception_bridge
    def bevel_gears(self: "Self") -> "List[_2800.BevelGear]":
        """List[mastapy.system_model.part_model.gears.BevelGear]

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "BevelGears")

        if temp is None:
            return None

        value = conversion.pn_to_mp_objects_in_list(temp)

        if value is None:
            return None

        return value

    @property
    @exception_bridge
    def bevel_meshes(self: "Self") -> "List[_2562.BevelGearMesh]":
        """List[mastapy.system_model.connections_and_sockets.gears.BevelGearMesh]

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "BevelMeshes")

        if temp is None:
            return None

        value = conversion.pn_to_mp_objects_in_list(temp)

        if value is None:
            return None

        return value

    @property
    def cast_to(self: "Self") -> "_Cast_BevelDifferentialGearSet":
        """Cast to another type.

        Returns:
            _Cast_BevelDifferentialGearSet
        """
        return _Cast_BevelDifferentialGearSet(self)
