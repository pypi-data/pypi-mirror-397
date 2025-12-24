"""ChannelConvectionFace"""

from __future__ import annotations

from typing import TYPE_CHECKING, ClassVar

from mastapy._private._internal.dataclasses import extended_dataclass
from mastapy._private._internal.exceptions import CastException
from mastapy._private._internal.python_net import python_net_import

from mastapy._private._internal import utility
from mastapy._private.nodal_analysis.lumped_parameter_thermal_analysis import _192

_CHANNEL_CONVECTION_FACE = python_net_import(
    "SMT.MastaAPI.NodalAnalysis.LumpedParameterThermalAnalysis", "ChannelConvectionFace"
)

if TYPE_CHECKING:
    from typing import Any, Type, TypeVar

    from mastapy._private.nodal_analysis.lumped_parameter_thermal_analysis import (
        _193,
        _208,
        _210,
        _226,
    )

    Self = TypeVar("Self", bound="ChannelConvectionFace")
    CastSelf = TypeVar(
        "CastSelf", bound="ChannelConvectionFace._Cast_ChannelConvectionFace"
    )


__docformat__ = "restructuredtext en"
__all__ = ("ChannelConvectionFace",)


@extended_dataclass(frozen=True, slots=True, weakref_slot=True)
class _Cast_ChannelConvectionFace:
    """Special nested class for casting ChannelConvectionFace to subclasses."""

    __parent__: "ChannelConvectionFace"

    @property
    def convection_face(self: "CastSelf") -> "_192.ConvectionFace":
        return self.__parent__._cast(_192.ConvectionFace)

    @property
    def convection_face_base(self: "CastSelf") -> "_193.ConvectionFaceBase":
        from mastapy._private.nodal_analysis.lumped_parameter_thermal_analysis import (
            _193,
        )

        return self.__parent__._cast(_193.ConvectionFaceBase)

    @property
    def thermal_face(self: "CastSelf") -> "_226.ThermalFace":
        from mastapy._private.nodal_analysis.lumped_parameter_thermal_analysis import (
            _226,
        )

        return self.__parent__._cast(_226.ThermalFace)

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
    def channel_convection_face(self: "CastSelf") -> "ChannelConvectionFace":
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
class ChannelConvectionFace(_192.ConvectionFace):
    """ChannelConvectionFace

    This is a mastapy class.
    """

    TYPE: ClassVar["Type"] = _CHANNEL_CONVECTION_FACE

    wrapped: "Any"

    def __post_init__(self: "Self") -> None:
        """Override of the post initialisation magic method."""
        if not hasattr(self.wrapped, "reference_count"):
            self.wrapped.reference_count = 0

        self.wrapped.reference_count += 1

    @property
    def cast_to(self: "Self") -> "_Cast_ChannelConvectionFace":
        """Cast to another type.

        Returns:
            _Cast_ChannelConvectionFace
        """
        return _Cast_ChannelConvectionFace(self)
