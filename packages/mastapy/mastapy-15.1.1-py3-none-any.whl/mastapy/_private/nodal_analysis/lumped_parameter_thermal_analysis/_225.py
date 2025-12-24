"""ThermalElement"""

from __future__ import annotations

from typing import TYPE_CHECKING, ClassVar

from mastapy._private._internal.dataclasses import extended_dataclass
from mastapy._private._internal.exception_bridge import exception_bridge
from mastapy._private._internal.exceptions import CastException
from mastapy._private._internal.python_net import (
    python_net_import,
    pythonnet_method_call,
    pythonnet_property_get,
)
from mastapy._private._internal.type_enforcement import enforce_parameter_types

from mastapy._private import _0
from mastapy._private._internal import conversion, utility

_THERMAL_ELEMENT = python_net_import(
    "SMT.MastaAPI.NodalAnalysis.LumpedParameterThermalAnalysis", "ThermalElement"
)

if TYPE_CHECKING:
    from typing import Any, List, Type, TypeVar

    from mastapy._private._internal.typing import PathLike

    from mastapy._private.electric_machines.thermal import _1495
    from mastapy._private.nodal_analysis.lumped_parameter_thermal_analysis import (
        _183,
        _184,
        _194,
        _197,
        _203,
        _205,
        _209,
        _211,
        _212,
    )

    Self = TypeVar("Self", bound="ThermalElement")
    CastSelf = TypeVar("CastSelf", bound="ThermalElement._Cast_ThermalElement")


__docformat__ = "restructuredtext en"
__all__ = ("ThermalElement",)


@extended_dataclass(frozen=True, slots=True, weakref_slot=True)
class _Cast_ThermalElement:
    """Special nested class for casting ThermalElement to subclasses."""

    __parent__: "ThermalElement"

    @property
    def air_gap_thermal_element(self: "CastSelf") -> "_183.AirGapThermalElement":
        from mastapy._private.nodal_analysis.lumped_parameter_thermal_analysis import (
            _183,
        )

        return self.__parent__._cast(_183.AirGapThermalElement)

    @property
    def arbitrary_thermal_element(self: "CastSelf") -> "_184.ArbitraryThermalElement":
        from mastapy._private.nodal_analysis.lumped_parameter_thermal_analysis import (
            _184,
        )

        return self.__parent__._cast(_184.ArbitraryThermalElement)

    @property
    def cuboid_thermal_element(self: "CastSelf") -> "_194.CuboidThermalElement":
        from mastapy._private.nodal_analysis.lumped_parameter_thermal_analysis import (
            _194,
        )

        return self.__parent__._cast(_194.CuboidThermalElement)

    @property
    def cuboid_wall_thermal_element(
        self: "CastSelf",
    ) -> "_197.CuboidWallThermalElement":
        from mastapy._private.nodal_analysis.lumped_parameter_thermal_analysis import (
            _197,
        )

        return self.__parent__._cast(_197.CuboidWallThermalElement)

    @property
    def cylindrical_thermal_element(
        self: "CastSelf",
    ) -> "_203.CylindricalThermalElement":
        from mastapy._private.nodal_analysis.lumped_parameter_thermal_analysis import (
            _203,
        )

        return self.__parent__._cast(_203.CylindricalThermalElement)

    @property
    def fe_interface_thermal_element(
        self: "CastSelf",
    ) -> "_205.FEInterfaceThermalElement":
        from mastapy._private.nodal_analysis.lumped_parameter_thermal_analysis import (
            _205,
        )

        return self.__parent__._cast(_205.FEInterfaceThermalElement)

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
    def fluid_channel_element(self: "CastSelf") -> "_212.FluidChannelElement":
        from mastapy._private.nodal_analysis.lumped_parameter_thermal_analysis import (
            _212,
        )

        return self.__parent__._cast(_212.FluidChannelElement)

    @property
    def end_winding_thermal_element(
        self: "CastSelf",
    ) -> "_1495.EndWindingThermalElement":
        from mastapy._private.electric_machines.thermal import _1495

        return self.__parent__._cast(_1495.EndWindingThermalElement)

    @property
    def thermal_element(self: "CastSelf") -> "ThermalElement":
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
class ThermalElement(_0.APIBase):
    """ThermalElement

    This is a mastapy class.
    """

    TYPE: ClassVar["Type"] = _THERMAL_ELEMENT

    wrapped: "Any"

    def __post_init__(self: "Self") -> None:
        """Override of the post initialisation magic method."""
        if not hasattr(self.wrapped, "reference_count"):
            self.wrapped.reference_count = 0

        self.wrapped.reference_count += 1

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
    def cast_to(self: "Self") -> "_Cast_ThermalElement":
        """Cast to another type.

        Returns:
            _Cast_ThermalElement
        """
        return _Cast_ThermalElement(self)
