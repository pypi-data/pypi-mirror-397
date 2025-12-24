"""ISOTR1417912001CoefficientOfFrictionConstants"""

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
from mastapy._private.utility.databases import _2061

_ISOTR1417912001_COEFFICIENT_OF_FRICTION_CONSTANTS = python_net_import(
    "SMT.MastaAPI.Gears.Materials", "ISOTR1417912001CoefficientOfFrictionConstants"
)

if TYPE_CHECKING:
    from typing import Any, Tuple, Type, TypeVar, Union

    from mastapy._private.gears.materials import _715
    from mastapy._private.math_utility import _1750

    Self = TypeVar("Self", bound="ISOTR1417912001CoefficientOfFrictionConstants")
    CastSelf = TypeVar(
        "CastSelf",
        bound="ISOTR1417912001CoefficientOfFrictionConstants._Cast_ISOTR1417912001CoefficientOfFrictionConstants",
    )


__docformat__ = "restructuredtext en"
__all__ = ("ISOTR1417912001CoefficientOfFrictionConstants",)


@extended_dataclass(frozen=True, slots=True, weakref_slot=True)
class _Cast_ISOTR1417912001CoefficientOfFrictionConstants:
    """Special nested class for casting ISOTR1417912001CoefficientOfFrictionConstants to subclasses."""

    __parent__: "ISOTR1417912001CoefficientOfFrictionConstants"

    @property
    def named_database_item(self: "CastSelf") -> "_2061.NamedDatabaseItem":
        return self.__parent__._cast(_2061.NamedDatabaseItem)

    @property
    def isotr1417912001_coefficient_of_friction_constants(
        self: "CastSelf",
    ) -> "ISOTR1417912001CoefficientOfFrictionConstants":
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
class ISOTR1417912001CoefficientOfFrictionConstants(_2061.NamedDatabaseItem):
    """ISOTR1417912001CoefficientOfFrictionConstants

    This is a mastapy class.
    """

    TYPE: ClassVar["Type"] = _ISOTR1417912001_COEFFICIENT_OF_FRICTION_CONSTANTS

    wrapped: "Any"

    def __post_init__(self: "Self") -> None:
        """Override of the post initialisation magic method."""
        if not hasattr(self.wrapped, "reference_count"):
            self.wrapped.reference_count = 0

        self.wrapped.reference_count += 1

    @property
    @exception_bridge
    def c1_lookup_table(self: "Self") -> "_1750.Vector2DListAccessor":
        """mastapy.math_utility.Vector2DListAccessor"""
        temp = pythonnet_property_get(self.wrapped, "C1LookupTable")

        if temp is None:
            return None

        type_ = temp.GetType()
        return constructor.new(type_.Namespace, type_.Name)(temp)

    @c1_lookup_table.setter
    @exception_bridge
    @enforce_parameter_types
    def c1_lookup_table(self: "Self", value: "_1750.Vector2DListAccessor") -> None:
        pythonnet_property_set(self.wrapped, "C1LookupTable", value.wrapped)

    @property
    @exception_bridge
    def c1_specification_method(
        self: "Self",
    ) -> "_715.ISO14179Part1ConstantC1SpecificationMethod":
        """mastapy.gears.materials.ISO14179Part1ConstantC1SpecificationMethod"""
        temp = pythonnet_property_get(self.wrapped, "C1SpecificationMethod")

        if temp is None:
            return None

        value = conversion.pn_to_mp_enum(
            temp,
            "SMT.MastaAPI.Gears.Materials.ISO14179Part1ConstantC1SpecificationMethod",
        )

        if value is None:
            return None

        return constructor.new_from_mastapy(
            "mastapy._private.gears.materials._715",
            "ISO14179Part1ConstantC1SpecificationMethod",
        )(value)

    @c1_specification_method.setter
    @exception_bridge
    @enforce_parameter_types
    def c1_specification_method(
        self: "Self", value: "_715.ISO14179Part1ConstantC1SpecificationMethod"
    ) -> None:
        value = conversion.mp_to_pn_enum(
            value,
            "SMT.MastaAPI.Gears.Materials.ISO14179Part1ConstantC1SpecificationMethod",
        )
        pythonnet_property_set(self.wrapped, "C1SpecificationMethod", value)

    @property
    @exception_bridge
    def clip_pitch_line_velocity_and_load_intensity_to_valid_ranges(
        self: "Self",
    ) -> "bool":
        """bool"""
        temp = pythonnet_property_get(
            self.wrapped, "ClipPitchLineVelocityAndLoadIntensityToValidRanges"
        )

        if temp is None:
            return False

        return temp

    @clip_pitch_line_velocity_and_load_intensity_to_valid_ranges.setter
    @exception_bridge
    @enforce_parameter_types
    def clip_pitch_line_velocity_and_load_intensity_to_valid_ranges(
        self: "Self", value: "bool"
    ) -> None:
        pythonnet_property_set(
            self.wrapped,
            "ClipPitchLineVelocityAndLoadIntensityToValidRanges",
            bool(value) if value is not None else False,
        )

    @property
    @exception_bridge
    def constant_c1(self: "Self") -> "overridable.Overridable_float":
        """Overridable[float]"""
        temp = pythonnet_property_get(self.wrapped, "ConstantC1")

        if temp is None:
            return 0.0

        return constructor.new_from_mastapy(
            "mastapy._private._internal.implicit.overridable", "Overridable_float"
        )(temp)

    @constant_c1.setter
    @exception_bridge
    @enforce_parameter_types
    def constant_c1(self: "Self", value: "Union[float, Tuple[float, bool]]") -> None:
        wrapper_type = overridable.Overridable_float.wrapper_type()
        enclosed_type = overridable.Overridable_float.implicit_type()
        value, is_overridden = _unpack_overridable(value)
        value = wrapper_type[enclosed_type](
            enclosed_type(value) if value is not None else 0.0, is_overridden
        )
        pythonnet_property_set(self.wrapped, "ConstantC1", value)

    @property
    @exception_bridge
    def load_intensity_exponent(self: "Self") -> "overridable.Overridable_float":
        """Overridable[float]"""
        temp = pythonnet_property_get(self.wrapped, "LoadIntensityExponent")

        if temp is None:
            return 0.0

        return constructor.new_from_mastapy(
            "mastapy._private._internal.implicit.overridable", "Overridable_float"
        )(temp)

    @load_intensity_exponent.setter
    @exception_bridge
    @enforce_parameter_types
    def load_intensity_exponent(
        self: "Self", value: "Union[float, Tuple[float, bool]]"
    ) -> None:
        wrapper_type = overridable.Overridable_float.wrapper_type()
        enclosed_type = overridable.Overridable_float.implicit_type()
        value, is_overridden = _unpack_overridable(value)
        value = wrapper_type[enclosed_type](
            enclosed_type(value) if value is not None else 0.0, is_overridden
        )
        pythonnet_property_set(self.wrapped, "LoadIntensityExponent", value)

    @property
    @exception_bridge
    def maximum_load_intensity(self: "Self") -> "overridable.Overridable_float":
        """Overridable[float]"""
        temp = pythonnet_property_get(self.wrapped, "MaximumLoadIntensity")

        if temp is None:
            return 0.0

        return constructor.new_from_mastapy(
            "mastapy._private._internal.implicit.overridable", "Overridable_float"
        )(temp)

    @maximum_load_intensity.setter
    @exception_bridge
    @enforce_parameter_types
    def maximum_load_intensity(
        self: "Self", value: "Union[float, Tuple[float, bool]]"
    ) -> None:
        wrapper_type = overridable.Overridable_float.wrapper_type()
        enclosed_type = overridable.Overridable_float.implicit_type()
        value, is_overridden = _unpack_overridable(value)
        value = wrapper_type[enclosed_type](
            enclosed_type(value) if value is not None else 0.0, is_overridden
        )
        pythonnet_property_set(self.wrapped, "MaximumLoadIntensity", value)

    @property
    @exception_bridge
    def maximum_pitch_line_velocity(self: "Self") -> "overridable.Overridable_float":
        """Overridable[float]"""
        temp = pythonnet_property_get(self.wrapped, "MaximumPitchLineVelocity")

        if temp is None:
            return 0.0

        return constructor.new_from_mastapy(
            "mastapy._private._internal.implicit.overridable", "Overridable_float"
        )(temp)

    @maximum_pitch_line_velocity.setter
    @exception_bridge
    @enforce_parameter_types
    def maximum_pitch_line_velocity(
        self: "Self", value: "Union[float, Tuple[float, bool]]"
    ) -> None:
        wrapper_type = overridable.Overridable_float.wrapper_type()
        enclosed_type = overridable.Overridable_float.implicit_type()
        value, is_overridden = _unpack_overridable(value)
        value = wrapper_type[enclosed_type](
            enclosed_type(value) if value is not None else 0.0, is_overridden
        )
        pythonnet_property_set(self.wrapped, "MaximumPitchLineVelocity", value)

    @property
    @exception_bridge
    def minimum_load_intensity(self: "Self") -> "overridable.Overridable_float":
        """Overridable[float]"""
        temp = pythonnet_property_get(self.wrapped, "MinimumLoadIntensity")

        if temp is None:
            return 0.0

        return constructor.new_from_mastapy(
            "mastapy._private._internal.implicit.overridable", "Overridable_float"
        )(temp)

    @minimum_load_intensity.setter
    @exception_bridge
    @enforce_parameter_types
    def minimum_load_intensity(
        self: "Self", value: "Union[float, Tuple[float, bool]]"
    ) -> None:
        wrapper_type = overridable.Overridable_float.wrapper_type()
        enclosed_type = overridable.Overridable_float.implicit_type()
        value, is_overridden = _unpack_overridable(value)
        value = wrapper_type[enclosed_type](
            enclosed_type(value) if value is not None else 0.0, is_overridden
        )
        pythonnet_property_set(self.wrapped, "MinimumLoadIntensity", value)

    @property
    @exception_bridge
    def minimum_pitch_line_velocity(self: "Self") -> "overridable.Overridable_float":
        """Overridable[float]"""
        temp = pythonnet_property_get(self.wrapped, "MinimumPitchLineVelocity")

        if temp is None:
            return 0.0

        return constructor.new_from_mastapy(
            "mastapy._private._internal.implicit.overridable", "Overridable_float"
        )(temp)

    @minimum_pitch_line_velocity.setter
    @exception_bridge
    @enforce_parameter_types
    def minimum_pitch_line_velocity(
        self: "Self", value: "Union[float, Tuple[float, bool]]"
    ) -> None:
        wrapper_type = overridable.Overridable_float.wrapper_type()
        enclosed_type = overridable.Overridable_float.implicit_type()
        value, is_overridden = _unpack_overridable(value)
        value = wrapper_type[enclosed_type](
            enclosed_type(value) if value is not None else 0.0, is_overridden
        )
        pythonnet_property_set(self.wrapped, "MinimumPitchLineVelocity", value)

    @property
    @exception_bridge
    def oil_viscosity_exponent(self: "Self") -> "overridable.Overridable_float":
        """Overridable[float]"""
        temp = pythonnet_property_get(self.wrapped, "OilViscosityExponent")

        if temp is None:
            return 0.0

        return constructor.new_from_mastapy(
            "mastapy._private._internal.implicit.overridable", "Overridable_float"
        )(temp)

    @oil_viscosity_exponent.setter
    @exception_bridge
    @enforce_parameter_types
    def oil_viscosity_exponent(
        self: "Self", value: "Union[float, Tuple[float, bool]]"
    ) -> None:
        wrapper_type = overridable.Overridable_float.wrapper_type()
        enclosed_type = overridable.Overridable_float.implicit_type()
        value, is_overridden = _unpack_overridable(value)
        value = wrapper_type[enclosed_type](
            enclosed_type(value) if value is not None else 0.0, is_overridden
        )
        pythonnet_property_set(self.wrapped, "OilViscosityExponent", value)

    @property
    @exception_bridge
    def pitch_line_velocity_exponent(self: "Self") -> "overridable.Overridable_float":
        """Overridable[float]"""
        temp = pythonnet_property_get(self.wrapped, "PitchLineVelocityExponent")

        if temp is None:
            return 0.0

        return constructor.new_from_mastapy(
            "mastapy._private._internal.implicit.overridable", "Overridable_float"
        )(temp)

    @pitch_line_velocity_exponent.setter
    @exception_bridge
    @enforce_parameter_types
    def pitch_line_velocity_exponent(
        self: "Self", value: "Union[float, Tuple[float, bool]]"
    ) -> None:
        wrapper_type = overridable.Overridable_float.wrapper_type()
        enclosed_type = overridable.Overridable_float.implicit_type()
        value, is_overridden = _unpack_overridable(value)
        value = wrapper_type[enclosed_type](
            enclosed_type(value) if value is not None else 0.0, is_overridden
        )
        pythonnet_property_set(self.wrapped, "PitchLineVelocityExponent", value)

    @property
    def cast_to(self: "Self") -> "_Cast_ISOTR1417912001CoefficientOfFrictionConstants":
        """Cast to another type.

        Returns:
            _Cast_ISOTR1417912001CoefficientOfFrictionConstants
        """
        return _Cast_ISOTR1417912001CoefficientOfFrictionConstants(self)
