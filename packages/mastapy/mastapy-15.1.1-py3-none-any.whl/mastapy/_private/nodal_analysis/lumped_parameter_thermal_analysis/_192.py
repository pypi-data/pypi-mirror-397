"""ConvectionFace"""

from __future__ import annotations

from typing import TYPE_CHECKING, ClassVar

from mastapy._private._internal.dataclasses import extended_dataclass
from mastapy._private._internal.exceptions import CastException
from mastapy._private._internal.python_net import python_net_import

from mastapy._private._internal import utility
from mastapy._private.nodal_analysis.lumped_parameter_thermal_analysis import _193

_CONVECTION_FACE = python_net_import(
    "SMT.MastaAPI.NodalAnalysis.LumpedParameterThermalAnalysis", "ConvectionFace"
)

if TYPE_CHECKING:
    from typing import Any, Type, TypeVar

    from mastapy._private.nodal_analysis.lumped_parameter_thermal_analysis import (
        _190,
        _208,
        _210,
        _213,
        _226,
    )

    Self = TypeVar("Self", bound="ConvectionFace")
    CastSelf = TypeVar("CastSelf", bound="ConvectionFace._Cast_ConvectionFace")


__docformat__ = "restructuredtext en"
__all__ = ("ConvectionFace",)


@extended_dataclass(frozen=True, slots=True, weakref_slot=True)
class _Cast_ConvectionFace:
    """Special nested class for casting ConvectionFace to subclasses."""

    __parent__: "ConvectionFace"

    @property
    def convection_face_base(self: "CastSelf") -> "_193.ConvectionFaceBase":
        return self.__parent__._cast(_193.ConvectionFaceBase)

    @property
    def thermal_face(self: "CastSelf") -> "_226.ThermalFace":
        from mastapy._private.nodal_analysis.lumped_parameter_thermal_analysis import (
            _226,
        )

        return self.__parent__._cast(_226.ThermalFace)

    @property
    def channel_convection_face(self: "CastSelf") -> "_190.ChannelConvectionFace":
        from mastapy._private.nodal_analysis.lumped_parameter_thermal_analysis import (
            _190,
        )

        return self.__parent__._cast(_190.ChannelConvectionFace)

    @property
    def fluid_channel_cuboid_convection_face(
        self: "CastSelf",
    ) -> "_208.FluidChannelCuboidConvectionFace":
        from mastapy._private.nodal_analysis.lumped_parameter_thermal_analysis import (
            _208,
        )

        return self.__parent__._cast(_208.FluidChannelCuboidConvectionFace)

    @property
    def fluid_channel_cylindrical_radial_convection_face(
        self: "CastSelf",
    ) -> "_210.FluidChannelCylindricalRadialConvectionFace":
        from mastapy._private.nodal_analysis.lumped_parameter_thermal_analysis import (
            _210,
        )

        return self.__parent__._cast(_210.FluidChannelCylindricalRadialConvectionFace)

    @property
    def generic_convection_face(self: "CastSelf") -> "_213.GenericConvectionFace":
        from mastapy._private.nodal_analysis.lumped_parameter_thermal_analysis import (
            _213,
        )

        return self.__parent__._cast(_213.GenericConvectionFace)

    @property
    def convection_face(self: "CastSelf") -> "ConvectionFace":
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
class ConvectionFace(_193.ConvectionFaceBase):
    """ConvectionFace

    This is a mastapy class.
    """

    TYPE: ClassVar["Type"] = _CONVECTION_FACE

    wrapped: "Any"

    def __post_init__(self: "Self") -> None:
        """Override of the post initialisation magic method."""
        if not hasattr(self.wrapped, "reference_count"):
            self.wrapped.reference_count = 0

        self.wrapped.reference_count += 1

    @property
    def cast_to(self: "Self") -> "_Cast_ConvectionFace":
        """Cast to another type.

        Returns:
            _Cast_ConvectionFace
        """
        return _Cast_ConvectionFace(self)
