"""DIN3962AccuracyGrades"""

from __future__ import annotations

from typing import TYPE_CHECKING, ClassVar

from mastapy._private._internal.dataclasses import extended_dataclass
from mastapy._private._internal.exception_bridge import exception_bridge
from mastapy._private._internal.exceptions import CastException
from mastapy._private._internal.python_net import (
    python_net_import,
    pythonnet_property_get,
    pythonnet_property_set,
)
from mastapy._private._internal.type_enforcement import enforce_parameter_types

from mastapy._private._internal import utility
from mastapy._private.gears.gear_designs.cylindrical.accuracy_and_tolerances import (
    _1281,
)

_DIN3962_ACCURACY_GRADES = python_net_import(
    "SMT.MastaAPI.Gears.GearDesigns.Cylindrical.AccuracyAndTolerances",
    "DIN3962AccuracyGrades",
)

if TYPE_CHECKING:
    from typing import Any, Type, TypeVar

    from mastapy._private.gears import _420

    Self = TypeVar("Self", bound="DIN3962AccuracyGrades")
    CastSelf = TypeVar(
        "CastSelf", bound="DIN3962AccuracyGrades._Cast_DIN3962AccuracyGrades"
    )


__docformat__ = "restructuredtext en"
__all__ = ("DIN3962AccuracyGrades",)


@extended_dataclass(frozen=True, slots=True, weakref_slot=True)
class _Cast_DIN3962AccuracyGrades:
    """Special nested class for casting DIN3962AccuracyGrades to subclasses."""

    __parent__: "DIN3962AccuracyGrades"

    @property
    def cylindrical_accuracy_grades(
        self: "CastSelf",
    ) -> "_1281.CylindricalAccuracyGrades":
        return self.__parent__._cast(_1281.CylindricalAccuracyGrades)

    @property
    def accuracy_grades(self: "CastSelf") -> "_420.AccuracyGrades":
        from mastapy._private.gears import _420

        return self.__parent__._cast(_420.AccuracyGrades)

    @property
    def din3962_accuracy_grades(self: "CastSelf") -> "DIN3962AccuracyGrades":
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
class DIN3962AccuracyGrades(_1281.CylindricalAccuracyGrades):
    """DIN3962AccuracyGrades

    This is a mastapy class.
    """

    TYPE: ClassVar["Type"] = _DIN3962_ACCURACY_GRADES

    wrapped: "Any"

    def __post_init__(self: "Self") -> None:
        """Override of the post initialisation magic method."""
        if not hasattr(self.wrapped, "reference_count"):
            self.wrapped.reference_count = 0

        self.wrapped.reference_count += 1

    @property
    @exception_bridge
    def helix_din_quality_grade(self: "Self") -> "int":
        """int"""
        temp = pythonnet_property_get(self.wrapped, "HelixDINQualityGrade")

        if temp is None:
            return 0

        return temp

    @helix_din_quality_grade.setter
    @exception_bridge
    @enforce_parameter_types
    def helix_din_quality_grade(self: "Self", value: "int") -> None:
        pythonnet_property_set(
            self.wrapped, "HelixDINQualityGrade", int(value) if value is not None else 0
        )

    @property
    @exception_bridge
    def pitch_din_quality_grade(self: "Self") -> "int":
        """int"""
        temp = pythonnet_property_get(self.wrapped, "PitchDINQualityGrade")

        if temp is None:
            return 0

        return temp

    @pitch_din_quality_grade.setter
    @exception_bridge
    @enforce_parameter_types
    def pitch_din_quality_grade(self: "Self", value: "int") -> None:
        pythonnet_property_set(
            self.wrapped, "PitchDINQualityGrade", int(value) if value is not None else 0
        )

    @property
    @exception_bridge
    def profile_din_quality_grade(self: "Self") -> "int":
        """int"""
        temp = pythonnet_property_get(self.wrapped, "ProfileDINQualityGrade")

        if temp is None:
            return 0

        return temp

    @profile_din_quality_grade.setter
    @exception_bridge
    @enforce_parameter_types
    def profile_din_quality_grade(self: "Self", value: "int") -> None:
        pythonnet_property_set(
            self.wrapped,
            "ProfileDINQualityGrade",
            int(value) if value is not None else 0,
        )

    @property
    @exception_bridge
    def radial_din_quality_grade(self: "Self") -> "int":
        """int"""
        temp = pythonnet_property_get(self.wrapped, "RadialDINQualityGrade")

        if temp is None:
            return 0

        return temp

    @radial_din_quality_grade.setter
    @exception_bridge
    @enforce_parameter_types
    def radial_din_quality_grade(self: "Self", value: "int") -> None:
        pythonnet_property_set(
            self.wrapped,
            "RadialDINQualityGrade",
            int(value) if value is not None else 0,
        )

    @property
    def cast_to(self: "Self") -> "_Cast_DIN3962AccuracyGrades":
        """Cast to another type.

        Returns:
            _Cast_DIN3962AccuracyGrades
        """
        return _Cast_DIN3962AccuracyGrades(self)
