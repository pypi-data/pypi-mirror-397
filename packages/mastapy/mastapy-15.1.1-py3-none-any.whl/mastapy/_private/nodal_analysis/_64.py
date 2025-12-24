"""FEMeshingOptions"""

from __future__ import annotations

from typing import TYPE_CHECKING, ClassVar

from mastapy._private._internal.dataclasses import extended_dataclass
from mastapy._private._internal.exception_bridge import exception_bridge
from mastapy._private._internal.exceptions import CastException
from mastapy._private._internal.overridable_constructor import _unpack_overridable
from mastapy._private._internal.python_net import (
    python_net_import,
    pythonnet_method_call,
    pythonnet_property_get,
    pythonnet_property_set,
)
from mastapy._private._internal.type_enforcement import enforce_parameter_types

from mastapy._private import _0
from mastapy._private._internal import (
    constructor,
    conversion,
    enum_with_selected_value_runtime,
    utility,
)
from mastapy._private._internal.implicit import enum_with_selected_value, overridable
from mastapy._private.nodal_analysis import _99

_FE_MESHING_OPTIONS = python_net_import(
    "SMT.MastaAPI.NodalAnalysis", "FEMeshingOptions"
)

if TYPE_CHECKING:
    from typing import Any, List, Tuple, Type, TypeVar, Union

    from mastapy._private._internal.typing import PathLike

    from mastapy._private.electric_machines import _1415, _1417, _1418, _1419, _1422
    from mastapy._private.nodal_analysis import _61, _65, _81, _92

    Self = TypeVar("Self", bound="FEMeshingOptions")
    CastSelf = TypeVar("CastSelf", bound="FEMeshingOptions._Cast_FEMeshingOptions")


__docformat__ = "restructuredtext en"
__all__ = ("FEMeshingOptions",)


@extended_dataclass(frozen=True, slots=True, weakref_slot=True)
class _Cast_FEMeshingOptions:
    """Special nested class for casting FEMeshingOptions to subclasses."""

    __parent__: "FEMeshingOptions"

    @property
    def meshing_options(self: "CastSelf") -> "_81.MeshingOptions":
        from mastapy._private.nodal_analysis import _81

        return self.__parent__._cast(_81.MeshingOptions)

    @property
    def shaft_fe_meshing_options(self: "CastSelf") -> "_92.ShaftFEMeshingOptions":
        from mastapy._private.nodal_analysis import _92

        return self.__parent__._cast(_92.ShaftFEMeshingOptions)

    @property
    def electric_machine_electromagnetic_and_thermal_meshing_options(
        self: "CastSelf",
    ) -> "_1415.ElectricMachineElectromagneticAndThermalMeshingOptions":
        from mastapy._private.electric_machines import _1415

        return self.__parent__._cast(
            _1415.ElectricMachineElectromagneticAndThermalMeshingOptions
        )

    @property
    def electric_machine_mechanical_analysis_meshing_options(
        self: "CastSelf",
    ) -> "_1417.ElectricMachineMechanicalAnalysisMeshingOptions":
        from mastapy._private.electric_machines import _1417

        return self.__parent__._cast(
            _1417.ElectricMachineMechanicalAnalysisMeshingOptions
        )

    @property
    def electric_machine_meshing_options(
        self: "CastSelf",
    ) -> "_1418.ElectricMachineMeshingOptions":
        from mastapy._private.electric_machines import _1418

        return self.__parent__._cast(_1418.ElectricMachineMeshingOptions)

    @property
    def electric_machine_meshing_options_base(
        self: "CastSelf",
    ) -> "_1419.ElectricMachineMeshingOptionsBase":
        from mastapy._private.electric_machines import _1419

        return self.__parent__._cast(_1419.ElectricMachineMeshingOptionsBase)

    @property
    def electric_machine_thermal_meshing_options(
        self: "CastSelf",
    ) -> "_1422.ElectricMachineThermalMeshingOptions":
        from mastapy._private.electric_machines import _1422

        return self.__parent__._cast(_1422.ElectricMachineThermalMeshingOptions)

    @property
    def fe_meshing_options(self: "CastSelf") -> "FEMeshingOptions":
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
class FEMeshingOptions(_0.APIBase):
    """FEMeshingOptions

    This is a mastapy class.
    """

    TYPE: ClassVar["Type"] = _FE_MESHING_OPTIONS

    wrapped: "Any"

    def __post_init__(self: "Self") -> None:
        """Override of the post initialisation magic method."""
        if not hasattr(self.wrapped, "reference_count"):
            self.wrapped.reference_count = 0

        self.wrapped.reference_count += 1

    @property
    @exception_bridge
    def element_order(self: "Self") -> "_61.ElementOrder":
        """mastapy.nodal_analysis.ElementOrder"""
        temp = pythonnet_property_get(self.wrapped, "ElementOrder")

        if temp is None:
            return None

        value = conversion.pn_to_mp_enum(
            temp, "SMT.MastaAPI.NodalAnalysis.ElementOrder"
        )

        if value is None:
            return None

        return constructor.new_from_mastapy(
            "mastapy._private.nodal_analysis._61", "ElementOrder"
        )(value)

    @element_order.setter
    @exception_bridge
    @enforce_parameter_types
    def element_order(self: "Self", value: "_61.ElementOrder") -> None:
        value = conversion.mp_to_pn_enum(
            value, "SMT.MastaAPI.NodalAnalysis.ElementOrder"
        )
        pythonnet_property_set(self.wrapped, "ElementOrder", value)

    @property
    @exception_bridge
    def element_shape(
        self: "Self",
    ) -> "enum_with_selected_value.EnumWithSelectedValue_VolumeElementShape":
        """EnumWithSelectedValue[mastapy.nodal_analysis.VolumeElementShape]"""
        temp = pythonnet_property_get(self.wrapped, "ElementShape")

        if temp is None:
            return None

        value = enum_with_selected_value.EnumWithSelectedValue_VolumeElementShape.wrapped_type()
        return enum_with_selected_value_runtime.create(temp, value)

    @element_shape.setter
    @exception_bridge
    @enforce_parameter_types
    def element_shape(self: "Self", value: "_99.VolumeElementShape") -> None:
        wrapper_type = enum_with_selected_value_runtime.ENUM_WITH_SELECTED_VALUE
        enclosed_type = enum_with_selected_value.EnumWithSelectedValue_VolumeElementShape.implicit_type()
        value = conversion.mp_to_pn_enum(value, enclosed_type)
        value = wrapper_type[enclosed_type](value)
        pythonnet_property_set(self.wrapped, "ElementShape", value)

    @property
    @exception_bridge
    def maximum_chord_height(self: "Self") -> "overridable.Overridable_float":
        """Overridable[float]"""
        temp = pythonnet_property_get(self.wrapped, "MaximumChordHeight")

        if temp is None:
            return 0.0

        return constructor.new_from_mastapy(
            "mastapy._private._internal.implicit.overridable", "Overridable_float"
        )(temp)

    @maximum_chord_height.setter
    @exception_bridge
    @enforce_parameter_types
    def maximum_chord_height(
        self: "Self", value: "Union[float, Tuple[float, bool]]"
    ) -> None:
        wrapper_type = overridable.Overridable_float.wrapper_type()
        enclosed_type = overridable.Overridable_float.implicit_type()
        value, is_overridden = _unpack_overridable(value)
        value = wrapper_type[enclosed_type](
            enclosed_type(value) if value is not None else 0.0, is_overridden
        )
        pythonnet_property_set(self.wrapped, "MaximumChordHeight", value)

    @property
    @exception_bridge
    def maximum_edge_altitude_ratio(self: "Self") -> "float":
        """float"""
        temp = pythonnet_property_get(self.wrapped, "MaximumEdgeAltitudeRatio")

        if temp is None:
            return 0.0

        return temp

    @maximum_edge_altitude_ratio.setter
    @exception_bridge
    @enforce_parameter_types
    def maximum_edge_altitude_ratio(self: "Self", value: "float") -> None:
        pythonnet_property_set(
            self.wrapped,
            "MaximumEdgeAltitudeRatio",
            float(value) if value is not None else 0.0,
        )

    @property
    @exception_bridge
    def maximum_growth_rate(self: "Self") -> "float":
        """float"""
        temp = pythonnet_property_get(self.wrapped, "MaximumGrowthRate")

        if temp is None:
            return 0.0

        return temp

    @maximum_growth_rate.setter
    @exception_bridge
    @enforce_parameter_types
    def maximum_growth_rate(self: "Self", value: "float") -> None:
        pythonnet_property_set(
            self.wrapped,
            "MaximumGrowthRate",
            float(value) if value is not None else 0.0,
        )

    @property
    @exception_bridge
    def maximum_spanning_angle(self: "Self") -> "float":
        """float"""
        temp = pythonnet_property_get(self.wrapped, "MaximumSpanningAngle")

        if temp is None:
            return 0.0

        return temp

    @maximum_spanning_angle.setter
    @exception_bridge
    @enforce_parameter_types
    def maximum_spanning_angle(self: "Self", value: "float") -> None:
        pythonnet_property_set(
            self.wrapped,
            "MaximumSpanningAngle",
            float(value) if value is not None else 0.0,
        )

    @property
    @exception_bridge
    def minimum_element_size(self: "Self") -> "overridable.Overridable_float":
        """Overridable[float]"""
        temp = pythonnet_property_get(self.wrapped, "MinimumElementSize")

        if temp is None:
            return 0.0

        return constructor.new_from_mastapy(
            "mastapy._private._internal.implicit.overridable", "Overridable_float"
        )(temp)

    @minimum_element_size.setter
    @exception_bridge
    @enforce_parameter_types
    def minimum_element_size(
        self: "Self", value: "Union[float, Tuple[float, bool]]"
    ) -> None:
        wrapper_type = overridable.Overridable_float.wrapper_type()
        enclosed_type = overridable.Overridable_float.implicit_type()
        value, is_overridden = _unpack_overridable(value)
        value = wrapper_type[enclosed_type](
            enclosed_type(value) if value is not None else 0.0, is_overridden
        )
        pythonnet_property_set(self.wrapped, "MinimumElementSize", value)

    @property
    @exception_bridge
    def minimum_triangle_angle(self: "Self") -> "float":
        """float"""
        temp = pythonnet_property_get(self.wrapped, "MinimumTriangleAngle")

        if temp is None:
            return 0.0

        return temp

    @minimum_triangle_angle.setter
    @exception_bridge
    @enforce_parameter_types
    def minimum_triangle_angle(self: "Self", value: "float") -> None:
        pythonnet_property_set(
            self.wrapped,
            "MinimumTriangleAngle",
            float(value) if value is not None else 0.0,
        )

    @property
    @exception_bridge
    def preserve_edge_angle(self: "Self") -> "float":
        """float"""
        temp = pythonnet_property_get(self.wrapped, "PreserveEdgeAngle")

        if temp is None:
            return 0.0

        return temp

    @preserve_edge_angle.setter
    @exception_bridge
    @enforce_parameter_types
    def preserve_edge_angle(self: "Self", value: "float") -> None:
        pythonnet_property_set(
            self.wrapped,
            "PreserveEdgeAngle",
            float(value) if value is not None else 0.0,
        )

    @property
    @exception_bridge
    def preserve_node_angle(self: "Self") -> "float":
        """float"""
        temp = pythonnet_property_get(self.wrapped, "PreserveNodeAngle")

        if temp is None:
            return 0.0

        return temp

    @preserve_node_angle.setter
    @exception_bridge
    @enforce_parameter_types
    def preserve_node_angle(self: "Self", value: "float") -> None:
        pythonnet_property_set(
            self.wrapped,
            "PreserveNodeAngle",
            float(value) if value is not None else 0.0,
        )

    @property
    @exception_bridge
    def meshing_problems(self: "Self") -> "List[_65.FEMeshingProblem]":
        """List[mastapy.nodal_analysis.FEMeshingProblem]

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "MeshingProblems")

        if temp is None:
            return None

        value = conversion.pn_to_mp_objects_in_list(temp)

        if value is None:
            return None

        return value

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
    def cast_to(self: "Self") -> "_Cast_FEMeshingOptions":
        """Cast to another type.

        Returns:
            _Cast_FEMeshingOptions
        """
        return _Cast_FEMeshingOptions(self)
