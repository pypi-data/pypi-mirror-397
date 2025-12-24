"""ThermalFace"""

from __future__ import annotations

from typing import TYPE_CHECKING, ClassVar

from mastapy._private._internal.dataclasses import extended_dataclass
from mastapy._private._internal.exception_bridge import exception_bridge
from mastapy._private._internal.exceptions import CastException
from mastapy._private._internal.python_net import (
    python_net_import,
    pythonnet_method_call,
    pythonnet_property_get,
    pythonnet_property_set,
)
from mastapy._private._internal.type_enforcement import enforce_parameter_types

from mastapy._private import _0
from mastapy._private._internal import conversion, utility

_THERMAL_FACE = python_net_import(
    "SMT.MastaAPI.NodalAnalysis.LumpedParameterThermalAnalysis", "ThermalFace"
)

if TYPE_CHECKING:
    from typing import Any, List, Type, TypeVar

    from mastapy._private._internal.typing import PathLike

    from mastapy._private.nodal_analysis.lumped_parameter_thermal_analysis import (
        _182,
        _185,
        _189,
        _190,
        _192,
        _193,
        _195,
        _196,
        _198,
        _200,
        _201,
        _202,
        _206,
        _208,
        _210,
        _213,
        _221,
    )

    Self = TypeVar("Self", bound="ThermalFace")
    CastSelf = TypeVar("CastSelf", bound="ThermalFace._Cast_ThermalFace")


__docformat__ = "restructuredtext en"
__all__ = ("ThermalFace",)


@extended_dataclass(frozen=True, slots=True, weakref_slot=True)
class _Cast_ThermalFace:
    """Special nested class for casting ThermalFace to subclasses."""

    __parent__: "ThermalFace"

    @property
    def air_gap_convection_face(self: "CastSelf") -> "_182.AirGapConvectionFace":
        from mastapy._private.nodal_analysis.lumped_parameter_thermal_analysis import (
            _182,
        )

        return self.__parent__._cast(_182.AirGapConvectionFace)

    @property
    def arbitrary_thermal_face(self: "CastSelf") -> "_185.ArbitraryThermalFace":
        from mastapy._private.nodal_analysis.lumped_parameter_thermal_analysis import (
            _185,
        )

        return self.__parent__._cast(_185.ArbitraryThermalFace)

    @property
    def capacitive_transport_face(self: "CastSelf") -> "_189.CapacitiveTransportFace":
        from mastapy._private.nodal_analysis.lumped_parameter_thermal_analysis import (
            _189,
        )

        return self.__parent__._cast(_189.CapacitiveTransportFace)

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
    def convection_face_base(self: "CastSelf") -> "_193.ConvectionFaceBase":
        from mastapy._private.nodal_analysis.lumped_parameter_thermal_analysis import (
            _193,
        )

        return self.__parent__._cast(_193.ConvectionFaceBase)

    @property
    def cuboid_thermal_face(self: "CastSelf") -> "_195.CuboidThermalFace":
        from mastapy._private.nodal_analysis.lumped_parameter_thermal_analysis import (
            _195,
        )

        return self.__parent__._cast(_195.CuboidThermalFace)

    @property
    def cuboid_wall_axial_thermal_face(
        self: "CastSelf",
    ) -> "_196.CuboidWallAxialThermalFace":
        from mastapy._private.nodal_analysis.lumped_parameter_thermal_analysis import (
            _196,
        )

        return self.__parent__._cast(_196.CuboidWallAxialThermalFace)

    @property
    def cuboid_wall_thermal_face(self: "CastSelf") -> "_198.CuboidWallThermalFace":
        from mastapy._private.nodal_analysis.lumped_parameter_thermal_analysis import (
            _198,
        )

        return self.__parent__._cast(_198.CuboidWallThermalFace)

    @property
    def cylindrical_axial_thermal_face(
        self: "CastSelf",
    ) -> "_200.CylindricalAxialThermalFace":
        from mastapy._private.nodal_analysis.lumped_parameter_thermal_analysis import (
            _200,
        )

        return self.__parent__._cast(_200.CylindricalAxialThermalFace)

    @property
    def cylindrical_circumferential_thermal_face(
        self: "CastSelf",
    ) -> "_201.CylindricalCircumferentialThermalFace":
        from mastapy._private.nodal_analysis.lumped_parameter_thermal_analysis import (
            _201,
        )

        return self.__parent__._cast(_201.CylindricalCircumferentialThermalFace)

    @property
    def cylindrical_radial_thermal_face(
        self: "CastSelf",
    ) -> "_202.CylindricalRadialThermalFace":
        from mastapy._private.nodal_analysis.lumped_parameter_thermal_analysis import (
            _202,
        )

        return self.__parent__._cast(_202.CylindricalRadialThermalFace)

    @property
    def fe_interface_thermal_face(self: "CastSelf") -> "_206.FEInterfaceThermalFace":
        from mastapy._private.nodal_analysis.lumped_parameter_thermal_analysis import (
            _206,
        )

        return self.__parent__._cast(_206.FEInterfaceThermalFace)

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
    def sub_fe_interface_thermal_face(
        self: "CastSelf",
    ) -> "_221.SubFEInterfaceThermalFace":
        from mastapy._private.nodal_analysis.lumped_parameter_thermal_analysis import (
            _221,
        )

        return self.__parent__._cast(_221.SubFEInterfaceThermalFace)

    @property
    def thermal_face(self: "CastSelf") -> "ThermalFace":
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
class ThermalFace(_0.APIBase):
    """ThermalFace

    This is a mastapy class.
    """

    TYPE: ClassVar["Type"] = _THERMAL_FACE

    wrapped: "Any"

    def __post_init__(self: "Self") -> None:
        """Override of the post initialisation magic method."""
        if not hasattr(self.wrapped, "reference_count"):
            self.wrapped.reference_count = 0

        self.wrapped.reference_count += 1

    @property
    @exception_bridge
    def heat_transfer_coefficient(self: "Self") -> "float":
        """float"""
        temp = pythonnet_property_get(self.wrapped, "HeatTransferCoefficient")

        if temp is None:
            return 0.0

        return temp

    @heat_transfer_coefficient.setter
    @exception_bridge
    @enforce_parameter_types
    def heat_transfer_coefficient(self: "Self", value: "float") -> None:
        pythonnet_property_set(
            self.wrapped,
            "HeatTransferCoefficient",
            float(value) if value is not None else 0.0,
        )

    @property
    @exception_bridge
    def nusselt_number_calculation_method(self: "Self") -> "str":
        """str

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "NusseltNumberCalculationMethod")

        if temp is None:
            return ""

        return temp

    @property
    @exception_bridge
    def report_names(self: "Self") -> "List[str]":
        """List[str]

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "ReportNames")

        if temp is None:
            return None

        value = conversion.pn_to_mp_objects_in_list(temp, str)

        if value is None:
            return None

        return value

    @exception_bridge
    @enforce_parameter_types
    def output_default_report_to(self: "Self", file_path: "PathLike") -> None:
        """Method does not return.

        Args:
            file_path (PathLike)
        """
        file_path = str(file_path)
        pythonnet_method_call(self.wrapped, "OutputDefaultReportTo", file_path)

    @exception_bridge
    def get_default_report_with_encoded_images(self: "Self") -> "str":
        """str"""
        method_result = pythonnet_method_call(
            self.wrapped, "GetDefaultReportWithEncodedImages"
        )
        return method_result

    @exception_bridge
    @enforce_parameter_types
    def output_active_report_to(self: "Self", file_path: "PathLike") -> None:
        """Method does not return.

        Args:
            file_path (PathLike)
        """
        file_path = str(file_path)
        pythonnet_method_call(self.wrapped, "OutputActiveReportTo", file_path)

    @exception_bridge
    @enforce_parameter_types
    def output_active_report_as_text_to(self: "Self", file_path: "PathLike") -> None:
        """Method does not return.

        Args:
            file_path (PathLike)
        """
        file_path = str(file_path)
        pythonnet_method_call(self.wrapped, "OutputActiveReportAsTextTo", file_path)

    @exception_bridge
    def get_active_report_with_encoded_images(self: "Self") -> "str":
        """str"""
        method_result = pythonnet_method_call(
            self.wrapped, "GetActiveReportWithEncodedImages"
        )
        return method_result

    @exception_bridge
    @enforce_parameter_types
    def output_named_report_to(
        self: "Self", report_name: "str", file_path: "PathLike"
    ) -> None:
        """Method does not return.

        Args:
            report_name (str)
            file_path (PathLike)
        """
        report_name = str(report_name)
        file_path = str(file_path)
        pythonnet_method_call(
            self.wrapped,
            "OutputNamedReportTo",
            report_name if report_name else "",
            file_path,
        )

    @exception_bridge
    @enforce_parameter_types
    def output_named_report_as_masta_report(
        self: "Self", report_name: "str", file_path: "PathLike"
    ) -> None:
        """Method does not return.

        Args:
            report_name (str)
            file_path (PathLike)
        """
        report_name = str(report_name)
        file_path = str(file_path)
        pythonnet_method_call(
            self.wrapped,
            "OutputNamedReportAsMastaReport",
            report_name if report_name else "",
            file_path,
        )

    @exception_bridge
    @enforce_parameter_types
    def output_named_report_as_text_to(
        self: "Self", report_name: "str", file_path: "PathLike"
    ) -> None:
        """Method does not return.

        Args:
            report_name (str)
            file_path (PathLike)
        """
        report_name = str(report_name)
        file_path = str(file_path)
        pythonnet_method_call(
            self.wrapped,
            "OutputNamedReportAsTextTo",
            report_name if report_name else "",
            file_path,
        )

    @exception_bridge
    @enforce_parameter_types
    def get_named_report_with_encoded_images(self: "Self", report_name: "str") -> "str":
        """str

        Args:
            report_name (str)
        """
        report_name = str(report_name)
        method_result = pythonnet_method_call(
            self.wrapped,
            "GetNamedReportWithEncodedImages",
            report_name if report_name else "",
        )
        return method_result

    @property
    def cast_to(self: "Self") -> "_Cast_ThermalFace":
        """Cast to another type.

        Returns:
            _Cast_ThermalFace
        """
        return _Cast_ThermalFace(self)
