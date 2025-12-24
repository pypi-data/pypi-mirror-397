"""FluidChannelElement"""

from __future__ import annotations

from typing import TYPE_CHECKING, ClassVar

from mastapy._private._internal.dataclasses import extended_dataclass
from mastapy._private._internal.exceptions import CastException
from mastapy._private._internal.python_net import python_net_import

from mastapy._private._internal import utility
from mastapy._private.nodal_analysis.lumped_parameter_thermal_analysis import _225

_FLUID_CHANNEL_ELEMENT = python_net_import(
    "SMT.MastaAPI.NodalAnalysis.LumpedParameterThermalAnalysis", "FluidChannelElement"
)

if TYPE_CHECKING:
    from typing import Any, Type, TypeVar

    from mastapy._private.nodal_analysis.lumped_parameter_thermal_analysis import (
        _209,
        _211,
    )

    Self = TypeVar("Self", bound="FluidChannelElement")
    CastSelf = TypeVar(
        "CastSelf", bound="FluidChannelElement._Cast_FluidChannelElement"
    )


__docformat__ = "restructuredtext en"
__all__ = ("FluidChannelElement",)


@extended_dataclass(frozen=True, slots=True, weakref_slot=True)
class _Cast_FluidChannelElement:
    """Special nested class for casting FluidChannelElement to subclasses."""

    __parent__: "FluidChannelElement"

    @property
    def thermal_element(self: "CastSelf") -> "_225.ThermalElement":
        return self.__parent__._cast(_225.ThermalElement)

    @property
    def fluid_channel_cuboid_element(
        self: "CastSelf",
    ) -> "_209.FluidChannelCuboidElement":
        from mastapy._private.nodal_analysis.lumped_parameter_thermal_analysis import (
            _209,
        )

        return self.__parent__._cast(_209.FluidChannelCuboidElement)

    @property
    def fluid_channel_cylindrical_radial_element(
        self: "CastSelf",
    ) -> "_211.FluidChannelCylindricalRadialElement":
        from mastapy._private.nodal_analysis.lumped_parameter_thermal_analysis import (
            _211,
        )

        return self.__parent__._cast(_211.FluidChannelCylindricalRadialElement)

    @property
    def fluid_channel_element(self: "CastSelf") -> "FluidChannelElement":
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
class FluidChannelElement(_225.ThermalElement):
    """FluidChannelElement

    This is a mastapy class.
    """

    TYPE: ClassVar["Type"] = _FLUID_CHANNEL_ELEMENT

    wrapped: "Any"

    def __post_init__(self: "Self") -> None:
        """Override of the post initialisation magic method."""
        if not hasattr(self.wrapped, "reference_count"):
            self.wrapped.reference_count = 0

        self.wrapped.reference_count += 1

    @property
    def cast_to(self: "Self") -> "_Cast_FluidChannelElement":
        """Cast to another type.

        Returns:
            _Cast_FluidChannelElement
        """
        return _Cast_FluidChannelElement(self)
