"""ConvectionFaceBase"""

from __future__ import annotations

from typing import TYPE_CHECKING, ClassVar

from mastapy._private._internal.dataclasses import extended_dataclass
from mastapy._private._internal.exception_bridge import exception_bridge
from mastapy._private._internal.exceptions import CastException
from mastapy._private._internal.python_net import (
    python_net_import,
    pythonnet_property_get,
)

from mastapy._private._internal import constructor, utility
from mastapy._private.nodal_analysis.lumped_parameter_thermal_analysis import _226

_CONVECTION_FACE_BASE = python_net_import(
    "SMT.MastaAPI.NodalAnalysis.LumpedParameterThermalAnalysis", "ConvectionFaceBase"
)

if TYPE_CHECKING:
    from typing import Any, Type, TypeVar

    from mastapy._private.nodal_analysis.lumped_parameter_thermal_analysis import (
        _182,
        _190,
        _192,
        _208,
        _210,
        _213,
        _230,
    )

    Self = TypeVar("Self", bound="ConvectionFaceBase")
    CastSelf = TypeVar("CastSelf", bound="ConvectionFaceBase._Cast_ConvectionFaceBase")


__docformat__ = "restructuredtext en"
__all__ = ("ConvectionFaceBase",)


@extended_dataclass(frozen=True, slots=True, weakref_slot=True)
class _Cast_ConvectionFaceBase:
    """Special nested class for casting ConvectionFaceBase to subclasses."""

    __parent__: "ConvectionFaceBase"

    @property
    def thermal_face(self: "CastSelf") -> "_226.ThermalFace":
        return self.__parent__._cast(_226.ThermalFace)

    @property
    def air_gap_convection_face(self: "CastSelf") -> "_182.AirGapConvectionFace":
        from mastapy._private.nodal_analysis.lumped_parameter_thermal_analysis import (
            _182,
        )

        return self.__parent__._cast(_182.AirGapConvectionFace)

    @property
    def channel_convection_face(self: "CastSelf") -> "_190.ChannelConvectionFace":
        from mastapy._private.nodal_analysis.lumped_parameter_thermal_analysis import (
            _190,
        )

        return self.__parent__._cast(_190.ChannelConvectionFace)

    @property
    def convection_face(self: "CastSelf") -> "_192.ConvectionFace":
        from mastapy._private.nodal_analysis.lumped_parameter_thermal_analysis import (
            _192,
        )

        return self.__parent__._cast(_192.ConvectionFace)

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
    def convection_face_base(self: "CastSelf") -> "ConvectionFaceBase":
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
class ConvectionFaceBase(_226.ThermalFace):
    """ConvectionFaceBase

    This is a mastapy class.
    """

    TYPE: ClassVar["Type"] = _CONVECTION_FACE_BASE

    wrapped: "Any"

    def __post_init__(self: "Self") -> None:
        """Override of the post initialisation magic method."""
        if not hasattr(self.wrapped, "reference_count"):
            self.wrapped.reference_count = 0

        self.wrapped.reference_count += 1

    @property
    @exception_bridge
    def user_defined_heat_transfer_coefficient(
        self: "Self",
    ) -> "_230.UserDefinedHeatTransferCoefficient":
        """mastapy.nodal_analysis.lumped_parameter_thermal_analysis.UserDefinedHeatTransferCoefficient

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(
            self.wrapped, "UserDefinedHeatTransferCoefficient"
        )

        if temp is None:
            return None

        type_ = temp.GetType()
        return constructor.new(type_.Namespace, type_.Name)(temp)

    @property
    def cast_to(self: "Self") -> "_Cast_ConvectionFaceBase":
        """Cast to another type.

        Returns:
            _Cast_ConvectionFaceBase
        """
        return _Cast_ConvectionFaceBase(self)
