"""CylindricalGearMeshMicroGeometryDutyCycle"""

from __future__ import annotations

from typing import TYPE_CHECKING, ClassVar

from mastapy._private._internal.dataclasses import extended_dataclass
from mastapy._private._internal.exception_bridge import exception_bridge
from mastapy._private._internal.exceptions import CastException
from mastapy._private._internal.python_net import (
    python_net_import,
    pythonnet_property_get,
)

from mastapy._private._internal import constructor, conversion, utility
from mastapy._private.gears.analysis import _1368
from mastapy._private.gears.ltca.cylindrical import _982

_CYLINDRICAL_GEAR_MESH_MICRO_GEOMETRY_DUTY_CYCLE = python_net_import(
    "SMT.MastaAPI.Gears.GearDesigns.Cylindrical.MicroGeometry",
    "CylindricalGearMeshMicroGeometryDutyCycle",
)

if TYPE_CHECKING:
    from typing import Any, List, Type, TypeVar

    from mastapy._private.gears.analysis import _1362
    from mastapy._private.gears.gear_designs.cylindrical.micro_geometry import _1244
    from mastapy._private.gears.rating.cylindrical import _576
    from mastapy._private.utility.property import _2078

    Self = TypeVar("Self", bound="CylindricalGearMeshMicroGeometryDutyCycle")
    CastSelf = TypeVar(
        "CastSelf",
        bound="CylindricalGearMeshMicroGeometryDutyCycle._Cast_CylindricalGearMeshMicroGeometryDutyCycle",
    )


__docformat__ = "restructuredtext en"
__all__ = ("CylindricalGearMeshMicroGeometryDutyCycle",)


@extended_dataclass(frozen=True, slots=True, weakref_slot=True)
class _Cast_CylindricalGearMeshMicroGeometryDutyCycle:
    """Special nested class for casting CylindricalGearMeshMicroGeometryDutyCycle to subclasses."""

    __parent__: "CylindricalGearMeshMicroGeometryDutyCycle"

    @property
    def gear_mesh_design_analysis(self: "CastSelf") -> "_1368.GearMeshDesignAnalysis":
        return self.__parent__._cast(_1368.GearMeshDesignAnalysis)

    @property
    def abstract_gear_mesh_analysis(
        self: "CastSelf",
    ) -> "_1362.AbstractGearMeshAnalysis":
        from mastapy._private.gears.analysis import _1362

        return self.__parent__._cast(_1362.AbstractGearMeshAnalysis)

    @property
    def cylindrical_gear_mesh_micro_geometry_duty_cycle(
        self: "CastSelf",
    ) -> "CylindricalGearMeshMicroGeometryDutyCycle":
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
class CylindricalGearMeshMicroGeometryDutyCycle(_1368.GearMeshDesignAnalysis):
    """CylindricalGearMeshMicroGeometryDutyCycle

    This is a mastapy class.
    """

    TYPE: ClassVar["Type"] = _CYLINDRICAL_GEAR_MESH_MICRO_GEOMETRY_DUTY_CYCLE

    wrapped: "Any"

    def __post_init__(self: "Self") -> None:
        """Override of the post initialisation magic method."""
        if not hasattr(self.wrapped, "reference_count"):
            self.wrapped.reference_count = 0

        self.wrapped.reference_count += 1

    @property
    @exception_bridge
    def mesh_name(self: "Self") -> "str":
        """str

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "MeshName")

        if temp is None:
            return ""

        return temp

    @property
    @exception_bridge
    def cylindrical_gear_set_duty_cycle_rating(
        self: "Self",
    ) -> "_576.CylindricalGearSetDutyCycleRating":
        """mastapy.gears.rating.cylindrical.CylindricalGearSetDutyCycleRating

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "CylindricalGearSetDutyCycleRating")

        if temp is None:
            return None

        type_ = temp.GetType()
        return constructor.new(type_.Namespace, type_.Name)(temp)

    @property
    @exception_bridge
    def peak_to_peak_te(
        self: "Self",
    ) -> "_2078.DutyCyclePropertySummaryVeryShortLength[_982.CylindricalGearMeshLoadDistributionAnalysis]":
        """mastapy.utility.property.DutyCyclePropertySummaryVeryShortLength[mastapy.gears.ltca.cylindrical.CylindricalGearMeshLoadDistributionAnalysis]

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "PeakToPeakTE")

        if temp is None:
            return None

        type_ = temp.GetType()
        return constructor.new(type_.Namespace, type_.Name)[
            _982.CylindricalGearMeshLoadDistributionAnalysis
        ](temp)

    @property
    @exception_bridge
    def meshes_analysis(
        self: "Self",
    ) -> "List[_982.CylindricalGearMeshLoadDistributionAnalysis]":
        """List[mastapy.gears.ltca.cylindrical.CylindricalGearMeshLoadDistributionAnalysis]

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "MeshesAnalysis")

        if temp is None:
            return None

        value = conversion.pn_to_mp_objects_in_list(temp)

        if value is None:
            return None

        return value

    @property
    @exception_bridge
    def gear_set(self: "Self") -> "_1244.CylindricalGearSetMicroGeometryDutyCycle":
        """mastapy.gears.gear_designs.cylindrical.micro_geometry.CylindricalGearSetMicroGeometryDutyCycle

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "GearSet")

        if temp is None:
            return None

        type_ = temp.GetType()
        return constructor.new(type_.Namespace, type_.Name)(temp)

    @property
    def cast_to(self: "Self") -> "_Cast_CylindricalGearMeshMicroGeometryDutyCycle":
        """Cast to another type.

        Returns:
            _Cast_CylindricalGearMeshMicroGeometryDutyCycle
        """
        return _Cast_CylindricalGearMeshMicroGeometryDutyCycle(self)
