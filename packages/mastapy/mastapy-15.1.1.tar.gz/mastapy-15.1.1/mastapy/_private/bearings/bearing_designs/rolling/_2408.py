"""NonBarrelRollerBearing"""

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
from mastapy._private.bearings.bearing_designs.rolling import _2409

_NON_BARREL_ROLLER_BEARING = python_net_import(
    "SMT.MastaAPI.Bearings.BearingDesigns.Rolling", "NonBarrelRollerBearing"
)

if TYPE_CHECKING:
    from typing import Any, List, Tuple, Type, TypeVar, Union

    from mastapy._private.bearings.bearing_designs import _2377, _2378, _2381
    from mastapy._private.bearings.bearing_designs.rolling import (
        _2385,
        _2386,
        _2396,
        _2407,
        _2410,
        _2411,
        _2412,
        _2419,
    )

    Self = TypeVar("Self", bound="NonBarrelRollerBearing")
    CastSelf = TypeVar(
        "CastSelf", bound="NonBarrelRollerBearing._Cast_NonBarrelRollerBearing"
    )


__docformat__ = "restructuredtext en"
__all__ = ("NonBarrelRollerBearing",)


@extended_dataclass(frozen=True, slots=True, weakref_slot=True)
class _Cast_NonBarrelRollerBearing:
    """Special nested class for casting NonBarrelRollerBearing to subclasses."""

    __parent__: "NonBarrelRollerBearing"

    @property
    def roller_bearing(self: "CastSelf") -> "_2409.RollerBearing":
        return self.__parent__._cast(_2409.RollerBearing)

    @property
    def rolling_bearing(self: "CastSelf") -> "_2412.RollingBearing":
        from mastapy._private.bearings.bearing_designs.rolling import _2412

        return self.__parent__._cast(_2412.RollingBearing)

    @property
    def detailed_bearing(self: "CastSelf") -> "_2378.DetailedBearing":
        from mastapy._private.bearings.bearing_designs import _2378

        return self.__parent__._cast(_2378.DetailedBearing)

    @property
    def non_linear_bearing(self: "CastSelf") -> "_2381.NonLinearBearing":
        from mastapy._private.bearings.bearing_designs import _2381

        return self.__parent__._cast(_2381.NonLinearBearing)

    @property
    def bearing_design(self: "CastSelf") -> "_2377.BearingDesign":
        from mastapy._private.bearings.bearing_designs import _2377

        return self.__parent__._cast(_2377.BearingDesign)

    @property
    def axial_thrust_cylindrical_roller_bearing(
        self: "CastSelf",
    ) -> "_2385.AxialThrustCylindricalRollerBearing":
        from mastapy._private.bearings.bearing_designs.rolling import _2385

        return self.__parent__._cast(_2385.AxialThrustCylindricalRollerBearing)

    @property
    def axial_thrust_needle_roller_bearing(
        self: "CastSelf",
    ) -> "_2386.AxialThrustNeedleRollerBearing":
        from mastapy._private.bearings.bearing_designs.rolling import _2386

        return self.__parent__._cast(_2386.AxialThrustNeedleRollerBearing)

    @property
    def cylindrical_roller_bearing(
        self: "CastSelf",
    ) -> "_2396.CylindricalRollerBearing":
        from mastapy._private.bearings.bearing_designs.rolling import _2396

        return self.__parent__._cast(_2396.CylindricalRollerBearing)

    @property
    def needle_roller_bearing(self: "CastSelf") -> "_2407.NeedleRollerBearing":
        from mastapy._private.bearings.bearing_designs.rolling import _2407

        return self.__parent__._cast(_2407.NeedleRollerBearing)

    @property
    def taper_roller_bearing(self: "CastSelf") -> "_2419.TaperRollerBearing":
        from mastapy._private.bearings.bearing_designs.rolling import _2419

        return self.__parent__._cast(_2419.TaperRollerBearing)

    @property
    def non_barrel_roller_bearing(self: "CastSelf") -> "NonBarrelRollerBearing":
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
class NonBarrelRollerBearing(_2409.RollerBearing):
    """NonBarrelRollerBearing

    This is a mastapy class.
    """

    TYPE: ClassVar["Type"] = _NON_BARREL_ROLLER_BEARING

    wrapped: "Any"

    def __post_init__(self: "Self") -> None:
        """Override of the post initialisation magic method."""
        if not hasattr(self.wrapped, "reference_count"):
            self.wrapped.reference_count = 0

        self.wrapped.reference_count += 1

    @property
    @exception_bridge
    def roller_end_radius(self: "Self") -> "overridable.Overridable_float":
        """Overridable[float]"""
        temp = pythonnet_property_get(self.wrapped, "RollerEndRadius")

        if temp is None:
            return 0.0

        return constructor.new_from_mastapy(
            "mastapy._private._internal.implicit.overridable", "Overridable_float"
        )(temp)

    @roller_end_radius.setter
    @exception_bridge
    @enforce_parameter_types
    def roller_end_radius(
        self: "Self", value: "Union[float, Tuple[float, bool]]"
    ) -> None:
        wrapper_type = overridable.Overridable_float.wrapper_type()
        enclosed_type = overridable.Overridable_float.implicit_type()
        value, is_overridden = _unpack_overridable(value)
        value = wrapper_type[enclosed_type](
            enclosed_type(value) if value is not None else 0.0, is_overridden
        )
        pythonnet_property_set(self.wrapped, "RollerEndRadius", value)

    @property
    @exception_bridge
    def roller_end_shape(self: "Self") -> "_2410.RollerEndShape":
        """mastapy.bearings.bearing_designs.rolling.RollerEndShape"""
        temp = pythonnet_property_get(self.wrapped, "RollerEndShape")

        if temp is None:
            return None

        value = conversion.pn_to_mp_enum(
            temp, "SMT.MastaAPI.Bearings.BearingDesigns.Rolling.RollerEndShape"
        )

        if value is None:
            return None

        return constructor.new_from_mastapy(
            "mastapy._private.bearings.bearing_designs.rolling._2410", "RollerEndShape"
        )(value)

    @roller_end_shape.setter
    @exception_bridge
    @enforce_parameter_types
    def roller_end_shape(self: "Self", value: "_2410.RollerEndShape") -> None:
        value = conversion.mp_to_pn_enum(
            value, "SMT.MastaAPI.Bearings.BearingDesigns.Rolling.RollerEndShape"
        )
        pythonnet_property_set(self.wrapped, "RollerEndShape", value)

    @property
    @exception_bridge
    def ribs(self: "Self") -> "List[_2411.RollerRibDetail]":
        """List[mastapy.bearings.bearing_designs.rolling.RollerRibDetail]

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "Ribs")

        if temp is None:
            return None

        value = conversion.pn_to_mp_objects_in_list(temp)

        if value is None:
            return None

        return value

    @property
    def cast_to(self: "Self") -> "_Cast_NonBarrelRollerBearing":
        """Cast to another type.

        Returns:
            _Cast_NonBarrelRollerBearing
        """
        return _Cast_NonBarrelRollerBearing(self)
