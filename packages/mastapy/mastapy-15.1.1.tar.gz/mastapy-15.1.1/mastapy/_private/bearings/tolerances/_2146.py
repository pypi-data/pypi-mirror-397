"""InterferenceTolerance"""

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
from mastapy._private.bearings.tolerances import _2138

_INTERFERENCE_TOLERANCE = python_net_import(
    "SMT.MastaAPI.Bearings.Tolerances", "InterferenceTolerance"
)

if TYPE_CHECKING:
    from typing import Any, Tuple, Type, TypeVar, Union

    from mastapy._private.bearings import _2125
    from mastapy._private.bearings.tolerances import (
        _2141,
        _2143,
        _2144,
        _2149,
        _2150,
        _2154,
        _2159,
    )

    Self = TypeVar("Self", bound="InterferenceTolerance")
    CastSelf = TypeVar(
        "CastSelf", bound="InterferenceTolerance._Cast_InterferenceTolerance"
    )


__docformat__ = "restructuredtext en"
__all__ = ("InterferenceTolerance",)


@extended_dataclass(frozen=True, slots=True, weakref_slot=True)
class _Cast_InterferenceTolerance:
    """Special nested class for casting InterferenceTolerance to subclasses."""

    __parent__: "InterferenceTolerance"

    @property
    def bearing_connection_component(
        self: "CastSelf",
    ) -> "_2138.BearingConnectionComponent":
        return self.__parent__._cast(_2138.BearingConnectionComponent)

    @property
    def inner_ring_tolerance(self: "CastSelf") -> "_2143.InnerRingTolerance":
        from mastapy._private.bearings.tolerances import _2143

        return self.__parent__._cast(_2143.InnerRingTolerance)

    @property
    def inner_support_tolerance(self: "CastSelf") -> "_2144.InnerSupportTolerance":
        from mastapy._private.bearings.tolerances import _2144

        return self.__parent__._cast(_2144.InnerSupportTolerance)

    @property
    def outer_ring_tolerance(self: "CastSelf") -> "_2149.OuterRingTolerance":
        from mastapy._private.bearings.tolerances import _2149

        return self.__parent__._cast(_2149.OuterRingTolerance)

    @property
    def outer_support_tolerance(self: "CastSelf") -> "_2150.OuterSupportTolerance":
        from mastapy._private.bearings.tolerances import _2150

        return self.__parent__._cast(_2150.OuterSupportTolerance)

    @property
    def ring_tolerance(self: "CastSelf") -> "_2154.RingTolerance":
        from mastapy._private.bearings.tolerances import _2154

        return self.__parent__._cast(_2154.RingTolerance)

    @property
    def support_tolerance(self: "CastSelf") -> "_2159.SupportTolerance":
        from mastapy._private.bearings.tolerances import _2159

        return self.__parent__._cast(_2159.SupportTolerance)

    @property
    def interference_tolerance(self: "CastSelf") -> "InterferenceTolerance":
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
class InterferenceTolerance(_2138.BearingConnectionComponent):
    """InterferenceTolerance

    This is a mastapy class.
    """

    TYPE: ClassVar["Type"] = _INTERFERENCE_TOLERANCE

    wrapped: "Any"

    def __post_init__(self: "Self") -> None:
        """Override of the post initialisation magic method."""
        if not hasattr(self.wrapped, "reference_count"):
            self.wrapped.reference_count = 0

        self.wrapped.reference_count += 1

    @property
    @exception_bridge
    def definition_option(self: "Self") -> "_2141.BearingToleranceDefinitionOptions":
        """mastapy.bearings.tolerances.BearingToleranceDefinitionOptions"""
        temp = pythonnet_property_get(self.wrapped, "DefinitionOption")

        if temp is None:
            return None

        value = conversion.pn_to_mp_enum(
            temp, "SMT.MastaAPI.Bearings.Tolerances.BearingToleranceDefinitionOptions"
        )

        if value is None:
            return None

        return constructor.new_from_mastapy(
            "mastapy._private.bearings.tolerances._2141",
            "BearingToleranceDefinitionOptions",
        )(value)

    @definition_option.setter
    @exception_bridge
    @enforce_parameter_types
    def definition_option(
        self: "Self", value: "_2141.BearingToleranceDefinitionOptions"
    ) -> None:
        value = conversion.mp_to_pn_enum(
            value, "SMT.MastaAPI.Bearings.Tolerances.BearingToleranceDefinitionOptions"
        )
        pythonnet_property_set(self.wrapped, "DefinitionOption", value)

    @property
    @exception_bridge
    def mounting_point_surface_finish(
        self: "Self",
    ) -> "_2125.MountingPointSurfaceFinishes":
        """mastapy.bearings.MountingPointSurfaceFinishes"""
        temp = pythonnet_property_get(self.wrapped, "MountingPointSurfaceFinish")

        if temp is None:
            return None

        value = conversion.pn_to_mp_enum(
            temp, "SMT.MastaAPI.Bearings.MountingPointSurfaceFinishes"
        )

        if value is None:
            return None

        return constructor.new_from_mastapy(
            "mastapy._private.bearings._2125", "MountingPointSurfaceFinishes"
        )(value)

    @mounting_point_surface_finish.setter
    @exception_bridge
    @enforce_parameter_types
    def mounting_point_surface_finish(
        self: "Self", value: "_2125.MountingPointSurfaceFinishes"
    ) -> None:
        value = conversion.mp_to_pn_enum(
            value, "SMT.MastaAPI.Bearings.MountingPointSurfaceFinishes"
        )
        pythonnet_property_set(self.wrapped, "MountingPointSurfaceFinish", value)

    @property
    @exception_bridge
    def non_contacting_diameter(self: "Self") -> "overridable.Overridable_float":
        """Overridable[float]"""
        temp = pythonnet_property_get(self.wrapped, "NonContactingDiameter")

        if temp is None:
            return 0.0

        return constructor.new_from_mastapy(
            "mastapy._private._internal.implicit.overridable", "Overridable_float"
        )(temp)

    @non_contacting_diameter.setter
    @exception_bridge
    @enforce_parameter_types
    def non_contacting_diameter(
        self: "Self", value: "Union[float, Tuple[float, bool]]"
    ) -> None:
        wrapper_type = overridable.Overridable_float.wrapper_type()
        enclosed_type = overridable.Overridable_float.implicit_type()
        value, is_overridden = _unpack_overridable(value)
        value = wrapper_type[enclosed_type](
            enclosed_type(value) if value is not None else 0.0, is_overridden
        )
        pythonnet_property_set(self.wrapped, "NonContactingDiameter", value)

    @property
    @exception_bridge
    def surface_fitting_reduction(self: "Self") -> "float":
        """float"""
        temp = pythonnet_property_get(self.wrapped, "SurfaceFittingReduction")

        if temp is None:
            return 0.0

        return temp

    @surface_fitting_reduction.setter
    @exception_bridge
    @enforce_parameter_types
    def surface_fitting_reduction(self: "Self", value: "float") -> None:
        pythonnet_property_set(
            self.wrapped,
            "SurfaceFittingReduction",
            float(value) if value is not None else 0.0,
        )

    @property
    @exception_bridge
    def tolerance_lower_limit(self: "Self") -> "float":
        """float"""
        temp = pythonnet_property_get(self.wrapped, "ToleranceLowerLimit")

        if temp is None:
            return 0.0

        return temp

    @tolerance_lower_limit.setter
    @exception_bridge
    @enforce_parameter_types
    def tolerance_lower_limit(self: "Self", value: "float") -> None:
        pythonnet_property_set(
            self.wrapped,
            "ToleranceLowerLimit",
            float(value) if value is not None else 0.0,
        )

    @property
    @exception_bridge
    def tolerance_upper_limit(self: "Self") -> "float":
        """float"""
        temp = pythonnet_property_get(self.wrapped, "ToleranceUpperLimit")

        if temp is None:
            return 0.0

        return temp

    @tolerance_upper_limit.setter
    @exception_bridge
    @enforce_parameter_types
    def tolerance_upper_limit(self: "Self", value: "float") -> None:
        pythonnet_property_set(
            self.wrapped,
            "ToleranceUpperLimit",
            float(value) if value is not None else 0.0,
        )

    @property
    def cast_to(self: "Self") -> "_Cast_InterferenceTolerance":
        """Cast to another type.

        Returns:
            _Cast_InterferenceTolerance
        """
        return _Cast_InterferenceTolerance(self)
