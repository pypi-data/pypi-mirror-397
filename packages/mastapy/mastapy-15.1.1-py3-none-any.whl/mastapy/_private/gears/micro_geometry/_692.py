"""Modification"""

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
from mastapy._private._internal import constructor, conversion, utility

_MODIFICATION = python_net_import("SMT.MastaAPI.Gears.MicroGeometry", "Modification")

if TYPE_CHECKING:
    from typing import Any, List, Type, TypeVar

    from mastapy._private._internal.typing import PathLike

    from mastapy._private.gears.gear_designs.conical.micro_geometry import (
        _1318,
        _1320,
        _1321,
    )
    from mastapy._private.gears.gear_designs.cylindrical import _1154
    from mastapy._private.gears.gear_designs.cylindrical.micro_geometry import (
        _1229,
        _1232,
        _1233,
        _1241,
        _1242,
        _1246,
    )
    from mastapy._private.gears.micro_geometry import _682, _685, _695

    Self = TypeVar("Self", bound="Modification")
    CastSelf = TypeVar("CastSelf", bound="Modification._Cast_Modification")


__docformat__ = "restructuredtext en"
__all__ = ("Modification",)


@extended_dataclass(frozen=True, slots=True, weakref_slot=True)
class _Cast_Modification:
    """Special nested class for casting Modification to subclasses."""

    __parent__: "Modification"

    @property
    def bias_modification(self: "CastSelf") -> "_682.BiasModification":
        from mastapy._private.gears.micro_geometry import _682

        return self.__parent__._cast(_682.BiasModification)

    @property
    def lead_modification(self: "CastSelf") -> "_685.LeadModification":
        from mastapy._private.gears.micro_geometry import _685

        return self.__parent__._cast(_685.LeadModification)

    @property
    def profile_modification(self: "CastSelf") -> "_695.ProfileModification":
        from mastapy._private.gears.micro_geometry import _695

        return self.__parent__._cast(_695.ProfileModification)

    @property
    def cylindrical_gear_bias_modification(
        self: "CastSelf",
    ) -> "_1229.CylindricalGearBiasModification":
        from mastapy._private.gears.gear_designs.cylindrical.micro_geometry import _1229

        return self.__parent__._cast(_1229.CylindricalGearBiasModification)

    @property
    def cylindrical_gear_lead_modification(
        self: "CastSelf",
    ) -> "_1232.CylindricalGearLeadModification":
        from mastapy._private.gears.gear_designs.cylindrical.micro_geometry import _1232

        return self.__parent__._cast(_1232.CylindricalGearLeadModification)

    @property
    def cylindrical_gear_lead_modification_at_profile_position(
        self: "CastSelf",
    ) -> "_1233.CylindricalGearLeadModificationAtProfilePosition":
        from mastapy._private.gears.gear_designs.cylindrical.micro_geometry import _1233

        return self.__parent__._cast(
            _1233.CylindricalGearLeadModificationAtProfilePosition
        )

    @property
    def cylindrical_gear_profile_modification(
        self: "CastSelf",
    ) -> "_1241.CylindricalGearProfileModification":
        from mastapy._private.gears.gear_designs.cylindrical.micro_geometry import _1241

        return self.__parent__._cast(_1241.CylindricalGearProfileModification)

    @property
    def cylindrical_gear_profile_modification_at_face_width_position(
        self: "CastSelf",
    ) -> "_1242.CylindricalGearProfileModificationAtFaceWidthPosition":
        from mastapy._private.gears.gear_designs.cylindrical.micro_geometry import _1242

        return self.__parent__._cast(
            _1242.CylindricalGearProfileModificationAtFaceWidthPosition
        )

    @property
    def cylindrical_gear_triangular_end_modification(
        self: "CastSelf",
    ) -> "_1246.CylindricalGearTriangularEndModification":
        from mastapy._private.gears.gear_designs.cylindrical.micro_geometry import _1246

        return self.__parent__._cast(_1246.CylindricalGearTriangularEndModification)

    @property
    def conical_gear_bias_modification(
        self: "CastSelf",
    ) -> "_1318.ConicalGearBiasModification":
        from mastapy._private.gears.gear_designs.conical.micro_geometry import _1318

        return self.__parent__._cast(_1318.ConicalGearBiasModification)

    @property
    def conical_gear_lead_modification(
        self: "CastSelf",
    ) -> "_1320.ConicalGearLeadModification":
        from mastapy._private.gears.gear_designs.conical.micro_geometry import _1320

        return self.__parent__._cast(_1320.ConicalGearLeadModification)

    @property
    def conical_gear_profile_modification(
        self: "CastSelf",
    ) -> "_1321.ConicalGearProfileModification":
        from mastapy._private.gears.gear_designs.conical.micro_geometry import _1321

        return self.__parent__._cast(_1321.ConicalGearProfileModification)

    @property
    def modification(self: "CastSelf") -> "Modification":
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
class Modification(_0.APIBase):
    """Modification

    This is a mastapy class.
    """

    TYPE: ClassVar["Type"] = _MODIFICATION

    wrapped: "Any"

    def __post_init__(self: "Self") -> None:
        """Override of the post initialisation magic method."""
        if not hasattr(self.wrapped, "reference_count"):
            self.wrapped.reference_count = 0

        self.wrapped.reference_count += 1

    @property
    @exception_bridge
    def settings(self: "Self") -> "_1154.CylindricalGearMicroGeometrySettingsItem":
        """mastapy.gears.gear_designs.cylindrical.CylindricalGearMicroGeometrySettingsItem

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "Settings")

        if temp is None:
            return None

        type_ = temp.GetType()
        return constructor.new(type_.Namespace, type_.Name)(temp)

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
    def cast_to(self: "Self") -> "_Cast_Modification":
        """Cast to another type.

        Returns:
            _Cast_Modification
        """
        return _Cast_Modification(self)
