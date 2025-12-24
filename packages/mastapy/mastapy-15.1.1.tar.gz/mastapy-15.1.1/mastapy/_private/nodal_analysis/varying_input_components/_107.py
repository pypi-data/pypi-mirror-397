"""MomentOrAngleInput"""

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

from mastapy._private._internal import constructor, utility
from mastapy._private._internal.implicit import overridable
from mastapy._private.nodal_analysis.varying_input_components import _101, _102, _106

_MOMENT_OR_ANGLE_INPUT = python_net_import(
    "SMT.MastaAPI.NodalAnalysis.VaryingInputComponents", "MomentOrAngleInput"
)

if TYPE_CHECKING:
    from typing import Any, Tuple, Type, TypeVar, Union

    Self = TypeVar("Self", bound="MomentOrAngleInput")
    CastSelf = TypeVar("CastSelf", bound="MomentOrAngleInput._Cast_MomentOrAngleInput")


__docformat__ = "restructuredtext en"
__all__ = ("MomentOrAngleInput",)


@extended_dataclass(frozen=True, slots=True, weakref_slot=True)
class _Cast_MomentOrAngleInput:
    """Special nested class for casting MomentOrAngleInput to subclasses."""

    __parent__: "MomentOrAngleInput"

    @property
    def constraint_switching_base(self: "CastSelf") -> "_102.ConstraintSwitchingBase":
        return self.__parent__._cast(_102.ConstraintSwitchingBase)

    @property
    def moment_or_angle_input(self: "CastSelf") -> "MomentOrAngleInput":
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
class MomentOrAngleInput(
    _102.ConstraintSwitchingBase[_106.MomentInputComponent, _101.AngleInputComponent]
):
    """MomentOrAngleInput

    This is a mastapy class.
    """

    TYPE: ClassVar["Type"] = _MOMENT_OR_ANGLE_INPUT

    wrapped: "Any"

    def __post_init__(self: "Self") -> None:
        """Override of the post initialisation magic method."""
        if not hasattr(self.wrapped, "reference_count"):
            self.wrapped.reference_count = 0

        self.wrapped.reference_count += 1

    @property
    @exception_bridge
    def angular_displacement(self: "Self") -> "overridable.Overridable_float":
        """Overridable[float]"""
        temp = pythonnet_property_get(self.wrapped, "AngularDisplacement")

        if temp is None:
            return 0.0

        return constructor.new_from_mastapy(
            "mastapy._private._internal.implicit.overridable", "Overridable_float"
        )(temp)

    @angular_displacement.setter
    @exception_bridge
    @enforce_parameter_types
    def angular_displacement(
        self: "Self", value: "Union[float, Tuple[float, bool]]"
    ) -> None:
        wrapper_type = overridable.Overridable_float.wrapper_type()
        enclosed_type = overridable.Overridable_float.implicit_type()
        value, is_overridden = _unpack_overridable(value)
        value = wrapper_type[enclosed_type](
            enclosed_type(value) if value is not None else 0.0, is_overridden
        )
        pythonnet_property_set(self.wrapped, "AngularDisplacement", value)

    @property
    def cast_to(self: "Self") -> "_Cast_MomentOrAngleInput":
        """Cast to another type.

        Returns:
            _Cast_MomentOrAngleInput
        """
        return _Cast_MomentOrAngleInput(self)
