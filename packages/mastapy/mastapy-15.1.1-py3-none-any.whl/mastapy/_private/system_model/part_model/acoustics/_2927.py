"""MicrophoneArrayDesign"""

from __future__ import annotations

from typing import TYPE_CHECKING, ClassVar

from mastapy._private._internal.dataclasses import extended_dataclass
from mastapy._private._internal.exception_bridge import exception_bridge
from mastapy._private._internal.exceptions import CastException
from mastapy._private._internal.list_with_selected_item import (
    promote_to_list_with_selected_item,
)
from mastapy._private._internal.python_net import (
    python_net_import,
    pythonnet_method_call,
    pythonnet_property_get,
    pythonnet_property_set,
)
from mastapy._private._internal.sentinels import ListWithSelectedItem_None
from mastapy._private._internal.type_enforcement import enforce_parameter_types

from mastapy._private import _0
from mastapy._private._internal import constructor, conversion, utility
from mastapy._private._internal.implicit import list_with_selected_item
from mastapy._private.system_model.part_model import _2718

_MICROPHONE_ARRAY_DESIGN = python_net_import(
    "SMT.MastaAPI.SystemModel.PartModel.Acoustics", "MicrophoneArrayDesign"
)

if TYPE_CHECKING:
    from typing import Any, List, Type, TypeVar

    from mastapy._private._internal.typing import PathLike

    from mastapy._private.math_utility import _1703
    from mastapy._private.system_model.part_model.acoustics import (
        _2914,
        _2917,
        _2921,
        _2928,
        _2936,
        _2937,
        _2938,
    )

    Self = TypeVar("Self", bound="MicrophoneArrayDesign")
    CastSelf = TypeVar(
        "CastSelf", bound="MicrophoneArrayDesign._Cast_MicrophoneArrayDesign"
    )


__docformat__ = "restructuredtext en"
__all__ = ("MicrophoneArrayDesign",)


@extended_dataclass(frozen=True, slots=True, weakref_slot=True)
class _Cast_MicrophoneArrayDesign:
    """Special nested class for casting MicrophoneArrayDesign to subclasses."""

    __parent__: "MicrophoneArrayDesign"

    @property
    def microphone_array_design(self: "CastSelf") -> "MicrophoneArrayDesign":
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
class MicrophoneArrayDesign(_0.APIBase):
    """MicrophoneArrayDesign

    This is a mastapy class.
    """

    TYPE: ClassVar["Type"] = _MICROPHONE_ARRAY_DESIGN

    wrapped: "Any"

    def __post_init__(self: "Self") -> None:
        """Override of the post initialisation magic method."""
        if not hasattr(self.wrapped, "reference_count"):
            self.wrapped.reference_count = 0

        self.wrapped.reference_count += 1

    @property
    @exception_bridge
    def cylindrical_envelope_type(self: "Self") -> "_2917.CylindricalEnvelopeTypes":
        """mastapy.system_model.part_model.acoustics.CylindricalEnvelopeTypes"""
        temp = pythonnet_property_get(self.wrapped, "CylindricalEnvelopeType")

        if temp is None:
            return None

        value = conversion.pn_to_mp_enum(
            temp,
            "SMT.MastaAPI.SystemModel.PartModel.Acoustics.CylindricalEnvelopeTypes",
        )

        if value is None:
            return None

        return constructor.new_from_mastapy(
            "mastapy._private.system_model.part_model.acoustics._2917",
            "CylindricalEnvelopeTypes",
        )(value)

    @cylindrical_envelope_type.setter
    @exception_bridge
    @enforce_parameter_types
    def cylindrical_envelope_type(
        self: "Self", value: "_2917.CylindricalEnvelopeTypes"
    ) -> None:
        value = conversion.mp_to_pn_enum(
            value,
            "SMT.MastaAPI.SystemModel.PartModel.Acoustics.CylindricalEnvelopeTypes",
        )
        pythonnet_property_set(self.wrapped, "CylindricalEnvelopeType", value)

    @property
    @exception_bridge
    def datum_vertical_axis(self: "Self") -> "_1703.Axis":
        """mastapy.math_utility.Axis"""
        temp = pythonnet_property_get(self.wrapped, "DatumVerticalAxis")

        if temp is None:
            return None

        value = conversion.pn_to_mp_enum(temp, "SMT.MastaAPI.MathUtility.Axis")

        if value is None:
            return None

        return constructor.new_from_mastapy(
            "mastapy._private.math_utility._1703", "Axis"
        )(value)

    @datum_vertical_axis.setter
    @exception_bridge
    @enforce_parameter_types
    def datum_vertical_axis(self: "Self", value: "_1703.Axis") -> None:
        value = conversion.mp_to_pn_enum(value, "SMT.MastaAPI.MathUtility.Axis")
        pythonnet_property_set(self.wrapped, "DatumVerticalAxis", value)

    @property
    @exception_bridge
    def distance(self: "Self") -> "float":
        """float"""
        temp = pythonnet_property_get(self.wrapped, "Distance")

        if temp is None:
            return 0.0

        return temp

    @distance.setter
    @exception_bridge
    @enforce_parameter_types
    def distance(self: "Self", value: "float") -> None:
        pythonnet_property_set(
            self.wrapped, "Distance", float(value) if value is not None else 0.0
        )

    @property
    @exception_bridge
    def envelope_type(self: "Self") -> "_2914.AcousticEnvelopeType":
        """mastapy.system_model.part_model.acoustics.AcousticEnvelopeType"""
        temp = pythonnet_property_get(self.wrapped, "EnvelopeType")

        if temp is None:
            return None

        value = conversion.pn_to_mp_enum(
            temp, "SMT.MastaAPI.SystemModel.PartModel.Acoustics.AcousticEnvelopeType"
        )

        if value is None:
            return None

        return constructor.new_from_mastapy(
            "mastapy._private.system_model.part_model.acoustics._2914",
            "AcousticEnvelopeType",
        )(value)

    @envelope_type.setter
    @exception_bridge
    @enforce_parameter_types
    def envelope_type(self: "Self", value: "_2914.AcousticEnvelopeType") -> None:
        value = conversion.mp_to_pn_enum(
            value, "SMT.MastaAPI.SystemModel.PartModel.Acoustics.AcousticEnvelopeType"
        )
        pythonnet_property_set(self.wrapped, "EnvelopeType", value)

    @property
    @exception_bridge
    def height(self: "Self") -> "float":
        """float"""
        temp = pythonnet_property_get(self.wrapped, "Height")

        if temp is None:
            return 0.0

        return temp

    @height.setter
    @exception_bridge
    @enforce_parameter_types
    def height(self: "Self", value: "float") -> None:
        pythonnet_property_set(
            self.wrapped, "Height", float(value) if value is not None else 0.0
        )

    @property
    @exception_bridge
    def iso3744_hemispherical_envelope_type(
        self: "Self",
    ) -> "_2921.HemisphericalEnvelopeType":
        """mastapy.system_model.part_model.acoustics.HemisphericalEnvelopeType"""
        temp = pythonnet_property_get(self.wrapped, "ISO3744HemisphericalEnvelopeType")

        if temp is None:
            return None

        value = conversion.pn_to_mp_enum(
            temp,
            "SMT.MastaAPI.SystemModel.PartModel.Acoustics.HemisphericalEnvelopeType",
        )

        if value is None:
            return None

        return constructor.new_from_mastapy(
            "mastapy._private.system_model.part_model.acoustics._2921",
            "HemisphericalEnvelopeType",
        )(value)

    @iso3744_hemispherical_envelope_type.setter
    @exception_bridge
    @enforce_parameter_types
    def iso3744_hemispherical_envelope_type(
        self: "Self", value: "_2921.HemisphericalEnvelopeType"
    ) -> None:
        value = conversion.mp_to_pn_enum(
            value,
            "SMT.MastaAPI.SystemModel.PartModel.Acoustics.HemisphericalEnvelopeType",
        )
        pythonnet_property_set(self.wrapped, "ISO3744HemisphericalEnvelopeType", value)

    @property
    @exception_bridge
    def number_of_partial_areas_in_x(self: "Self") -> "int":
        """int"""
        temp = pythonnet_property_get(self.wrapped, "NumberOfPartialAreasInX")

        if temp is None:
            return 0

        return temp

    @number_of_partial_areas_in_x.setter
    @exception_bridge
    @enforce_parameter_types
    def number_of_partial_areas_in_x(self: "Self", value: "int") -> None:
        pythonnet_property_set(
            self.wrapped,
            "NumberOfPartialAreasInX",
            int(value) if value is not None else 0,
        )

    @property
    @exception_bridge
    def number_of_partial_areas_in_y(self: "Self") -> "int":
        """int"""
        temp = pythonnet_property_get(self.wrapped, "NumberOfPartialAreasInY")

        if temp is None:
            return 0

        return temp

    @number_of_partial_areas_in_y.setter
    @exception_bridge
    @enforce_parameter_types
    def number_of_partial_areas_in_y(self: "Self", value: "int") -> None:
        pythonnet_property_set(
            self.wrapped,
            "NumberOfPartialAreasInY",
            int(value) if value is not None else 0,
        )

    @property
    @exception_bridge
    def number_of_partial_areas_in_z(self: "Self") -> "int":
        """int"""
        temp = pythonnet_property_get(self.wrapped, "NumberOfPartialAreasInZ")

        if temp is None:
            return 0

        return temp

    @number_of_partial_areas_in_z.setter
    @exception_bridge
    @enforce_parameter_types
    def number_of_partial_areas_in_z(self: "Self", value: "int") -> None:
        pythonnet_property_set(
            self.wrapped,
            "NumberOfPartialAreasInZ",
            int(value) if value is not None else 0,
        )

    @property
    @exception_bridge
    def number_of_circumferential_microphones(self: "Self") -> "int":
        """int"""
        temp = pythonnet_property_get(
            self.wrapped, "NumberOfCircumferentialMicrophones"
        )

        if temp is None:
            return 0

        return temp

    @number_of_circumferential_microphones.setter
    @exception_bridge
    @enforce_parameter_types
    def number_of_circumferential_microphones(self: "Self", value: "int") -> None:
        pythonnet_property_set(
            self.wrapped,
            "NumberOfCircumferentialMicrophones",
            int(value) if value is not None else 0,
        )

    @property
    @exception_bridge
    def number_of_microphones(self: "Self") -> "int":
        """int"""
        temp = pythonnet_property_get(self.wrapped, "NumberOfMicrophones")

        if temp is None:
            return 0

        return temp

    @number_of_microphones.setter
    @exception_bridge
    @enforce_parameter_types
    def number_of_microphones(self: "Self", value: "int") -> None:
        pythonnet_property_set(
            self.wrapped, "NumberOfMicrophones", int(value) if value is not None else 0
        )

    @property
    @exception_bridge
    def number_of_side_microphones(self: "Self") -> "int":
        """int"""
        temp = pythonnet_property_get(self.wrapped, "NumberOfSideMicrophones")

        if temp is None:
            return 0

        return temp

    @number_of_side_microphones.setter
    @exception_bridge
    @enforce_parameter_types
    def number_of_side_microphones(self: "Self", value: "int") -> None:
        pythonnet_property_set(
            self.wrapped,
            "NumberOfSideMicrophones",
            int(value) if value is not None else 0,
        )

    @property
    @exception_bridge
    def number_of_top_microphones(self: "Self") -> "int":
        """int"""
        temp = pythonnet_property_get(self.wrapped, "NumberOfTopMicrophones")

        if temp is None:
            return 0

        return temp

    @number_of_top_microphones.setter
    @exception_bridge
    @enforce_parameter_types
    def number_of_top_microphones(self: "Self", value: "int") -> None:
        pythonnet_property_set(
            self.wrapped,
            "NumberOfTopMicrophones",
            int(value) if value is not None else 0,
        )

    @property
    @exception_bridge
    def right_parallelepiped_envelope_type(
        self: "Self",
    ) -> "_2936.RightParallelepipedEnvelopeTypes":
        """mastapy.system_model.part_model.acoustics.RightParallelepipedEnvelopeTypes"""
        temp = pythonnet_property_get(self.wrapped, "RightParallelepipedEnvelopeType")

        if temp is None:
            return None

        value = conversion.pn_to_mp_enum(
            temp,
            "SMT.MastaAPI.SystemModel.PartModel.Acoustics.RightParallelepipedEnvelopeTypes",
        )

        if value is None:
            return None

        return constructor.new_from_mastapy(
            "mastapy._private.system_model.part_model.acoustics._2936",
            "RightParallelepipedEnvelopeTypes",
        )(value)

    @right_parallelepiped_envelope_type.setter
    @exception_bridge
    @enforce_parameter_types
    def right_parallelepiped_envelope_type(
        self: "Self", value: "_2936.RightParallelepipedEnvelopeTypes"
    ) -> None:
        value = conversion.mp_to_pn_enum(
            value,
            "SMT.MastaAPI.SystemModel.PartModel.Acoustics.RightParallelepipedEnvelopeTypes",
        )
        pythonnet_property_set(self.wrapped, "RightParallelepipedEnvelopeType", value)

    @property
    @exception_bridge
    def selected_datum(
        self: "Self",
    ) -> "list_with_selected_item.ListWithSelectedItem_Datum":
        """ListWithSelectedItem[mastapy.system_model.part_model.Datum]"""
        temp = pythonnet_property_get(self.wrapped, "SelectedDatum")

        if temp is None:
            return None

        selected_value = temp.SelectedValue

        if selected_value is None:
            return ListWithSelectedItem_None(temp)

        return constructor.new_from_mastapy(
            "mastapy._private._internal.implicit.list_with_selected_item",
            "ListWithSelectedItem_Datum",
        )(temp)

    @selected_datum.setter
    @exception_bridge
    @enforce_parameter_types
    def selected_datum(self: "Self", value: "_2718.Datum") -> None:
        generic_type = (
            list_with_selected_item.ListWithSelectedItem_Datum.implicit_type()
        )
        value = promote_to_list_with_selected_item(value)
        value = conversion.mp_to_pn_smt_list_with_selected_item(
            self, value, generic_type
        )
        pythonnet_property_set(self.wrapped, "SelectedDatum", value)

    @property
    @exception_bridge
    def size_in_x_direction(self: "Self") -> "float":
        """float"""
        temp = pythonnet_property_get(self.wrapped, "SizeInXDirection")

        if temp is None:
            return 0.0

        return temp

    @size_in_x_direction.setter
    @exception_bridge
    @enforce_parameter_types
    def size_in_x_direction(self: "Self", value: "float") -> None:
        pythonnet_property_set(
            self.wrapped, "SizeInXDirection", float(value) if value is not None else 0.0
        )

    @property
    @exception_bridge
    def size_in_z_direction(self: "Self") -> "float":
        """float"""
        temp = pythonnet_property_get(self.wrapped, "SizeInZDirection")

        if temp is None:
            return 0.0

        return temp

    @size_in_z_direction.setter
    @exception_bridge
    @enforce_parameter_types
    def size_in_z_direction(self: "Self", value: "float") -> None:
        pythonnet_property_set(
            self.wrapped, "SizeInZDirection", float(value) if value is not None else 0.0
        )

    @property
    @exception_bridge
    def specify_datum_for_coordinate_system(self: "Self") -> "bool":
        """bool"""
        temp = pythonnet_property_get(self.wrapped, "SpecifyDatumForCoordinateSystem")

        if temp is None:
            return False

        return temp

    @specify_datum_for_coordinate_system.setter
    @exception_bridge
    @enforce_parameter_types
    def specify_datum_for_coordinate_system(self: "Self", value: "bool") -> None:
        pythonnet_property_set(
            self.wrapped,
            "SpecifyDatumForCoordinateSystem",
            bool(value) if value is not None else False,
        )

    @property
    @exception_bridge
    def spherical_envelope_centre(
        self: "Self",
    ) -> "_2937.SphericalEnvelopeCentreDefinition":
        """mastapy.system_model.part_model.acoustics.SphericalEnvelopeCentreDefinition"""
        temp = pythonnet_property_get(self.wrapped, "SphericalEnvelopeCentre")

        if temp is None:
            return None

        value = conversion.pn_to_mp_enum(
            temp,
            "SMT.MastaAPI.SystemModel.PartModel.Acoustics.SphericalEnvelopeCentreDefinition",
        )

        if value is None:
            return None

        return constructor.new_from_mastapy(
            "mastapy._private.system_model.part_model.acoustics._2937",
            "SphericalEnvelopeCentreDefinition",
        )(value)

    @spherical_envelope_centre.setter
    @exception_bridge
    @enforce_parameter_types
    def spherical_envelope_centre(
        self: "Self", value: "_2937.SphericalEnvelopeCentreDefinition"
    ) -> None:
        value = conversion.mp_to_pn_enum(
            value,
            "SMT.MastaAPI.SystemModel.PartModel.Acoustics.SphericalEnvelopeCentreDefinition",
        )
        pythonnet_property_set(self.wrapped, "SphericalEnvelopeCentre", value)

    @property
    @exception_bridge
    def spherical_envelope_type(self: "Self") -> "_2938.SphericalEnvelopeType":
        """mastapy.system_model.part_model.acoustics.SphericalEnvelopeType"""
        temp = pythonnet_property_get(self.wrapped, "SphericalEnvelopeType")

        if temp is None:
            return None

        value = conversion.pn_to_mp_enum(
            temp, "SMT.MastaAPI.SystemModel.PartModel.Acoustics.SphericalEnvelopeType"
        )

        if value is None:
            return None

        return constructor.new_from_mastapy(
            "mastapy._private.system_model.part_model.acoustics._2938",
            "SphericalEnvelopeType",
        )(value)

    @spherical_envelope_type.setter
    @exception_bridge
    @enforce_parameter_types
    def spherical_envelope_type(
        self: "Self", value: "_2938.SphericalEnvelopeType"
    ) -> None:
        value = conversion.mp_to_pn_enum(
            value, "SMT.MastaAPI.SystemModel.PartModel.Acoustics.SphericalEnvelopeType"
        )
        pythonnet_property_set(self.wrapped, "SphericalEnvelopeType", value)

    @property
    @exception_bridge
    def selected_part(self: "Self") -> "List[_2928.PartSelectionForAcousticEnvelope]":
        """List[mastapy.system_model.part_model.acoustics.PartSelectionForAcousticEnvelope]

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "SelectedPart")

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
    def cast_to(self: "Self") -> "_Cast_MicrophoneArrayDesign":
        """Cast to another type.

        Returns:
            _Cast_MicrophoneArrayDesign
        """
        return _Cast_MicrophoneArrayDesign(self)
