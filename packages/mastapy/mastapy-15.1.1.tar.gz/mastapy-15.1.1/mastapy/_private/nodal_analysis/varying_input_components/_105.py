"""ForceOrDisplacementInput"""

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
from mastapy._private.nodal_analysis.varying_input_components import _102, _103, _104

_FORCE_OR_DISPLACEMENT_INPUT = python_net_import(
    "SMT.MastaAPI.NodalAnalysis.VaryingInputComponents", "ForceOrDisplacementInput"
)

if TYPE_CHECKING:
    from typing import Any, Tuple, Type, TypeVar, Union

    Self = TypeVar("Self", bound="ForceOrDisplacementInput")
    CastSelf = TypeVar(
        "CastSelf", bound="ForceOrDisplacementInput._Cast_ForceOrDisplacementInput"
    )


__docformat__ = "restructuredtext en"
__all__ = ("ForceOrDisplacementInput",)


@extended_dataclass(frozen=True, slots=True, weakref_slot=True)
class _Cast_ForceOrDisplacementInput:
    """Special nested class for casting ForceOrDisplacementInput to subclasses."""

    __parent__: "ForceOrDisplacementInput"

    @property
    def constraint_switching_base(self: "CastSelf") -> "_102.ConstraintSwitchingBase":
        return self.__parent__._cast(_102.ConstraintSwitchingBase)

    @property
    def force_or_displacement_input(self: "CastSelf") -> "ForceOrDisplacementInput":
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
class ForceOrDisplacementInput(
    _102.ConstraintSwitchingBase[
        _104.ForceInputComponent, _103.DisplacementInputComponent
    ]
):
    """ForceOrDisplacementInput

    This is a mastapy class.
    """

    TYPE: ClassVar["Type"] = _FORCE_OR_DISPLACEMENT_INPUT

    wrapped: "Any"

    def __post_init__(self: "Self") -> None:
        """Override of the post initialisation magic method."""
        if not hasattr(self.wrapped, "reference_count"):
            self.wrapped.reference_count = 0

        self.wrapped.reference_count += 1

    @property
    @exception_bridge
    def linear_displacement(self: "Self") -> "overridable.Overridable_float":
        """Overridable[float]"""
        temp = pythonnet_property_get(self.wrapped, "LinearDisplacement")

        if temp is None:
            return 0.0

        return constructor.new_from_mastapy(
            "mastapy._private._internal.implicit.overridable", "Overridable_float"
        )(temp)

    @linear_displacement.setter
    @exception_bridge
    @enforce_parameter_types
    def linear_displacement(
        self: "Self", value: "Union[float, Tuple[float, bool]]"
    ) -> None:
        wrapper_type = overridable.Overridable_float.wrapper_type()
        enclosed_type = overridable.Overridable_float.implicit_type()
        value, is_overridden = _unpack_overridable(value)
        value = wrapper_type[enclosed_type](
            enclosed_type(value) if value is not None else 0.0, is_overridden
        )
        pythonnet_property_set(self.wrapped, "LinearDisplacement", value)

    @property
    def cast_to(self: "Self") -> "_Cast_ForceOrDisplacementInput":
        """Cast to another type.

        Returns:
            _Cast_ForceOrDisplacementInput
        """
        return _Cast_ForceOrDisplacementInput(self)
