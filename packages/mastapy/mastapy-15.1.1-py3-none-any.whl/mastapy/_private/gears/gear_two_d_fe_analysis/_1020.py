"""CylindricalGearMeshTIFFAnalysisDutyCycle"""

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
from mastapy._private.gears.analysis import _1368

_CYLINDRICAL_GEAR_MESH_TIFF_ANALYSIS_DUTY_CYCLE = python_net_import(
    "SMT.MastaAPI.Gears.GearTwoDFEAnalysis", "CylindricalGearMeshTIFFAnalysisDutyCycle"
)

if TYPE_CHECKING:
    from typing import Any, Type, TypeVar

    from mastapy._private.gears.analysis import _1362
    from mastapy._private.gears.gear_two_d_fe_analysis import _1022

    Self = TypeVar("Self", bound="CylindricalGearMeshTIFFAnalysisDutyCycle")
    CastSelf = TypeVar(
        "CastSelf",
        bound="CylindricalGearMeshTIFFAnalysisDutyCycle._Cast_CylindricalGearMeshTIFFAnalysisDutyCycle",
    )


__docformat__ = "restructuredtext en"
__all__ = ("CylindricalGearMeshTIFFAnalysisDutyCycle",)


@extended_dataclass(frozen=True, slots=True, weakref_slot=True)
class _Cast_CylindricalGearMeshTIFFAnalysisDutyCycle:
    """Special nested class for casting CylindricalGearMeshTIFFAnalysisDutyCycle to subclasses."""

    __parent__: "CylindricalGearMeshTIFFAnalysisDutyCycle"

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
    def cylindrical_gear_mesh_tiff_analysis_duty_cycle(
        self: "CastSelf",
    ) -> "CylindricalGearMeshTIFFAnalysisDutyCycle":
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
class CylindricalGearMeshTIFFAnalysisDutyCycle(_1368.GearMeshDesignAnalysis):
    """CylindricalGearMeshTIFFAnalysisDutyCycle

    This is a mastapy class.
    """

    TYPE: ClassVar["Type"] = _CYLINDRICAL_GEAR_MESH_TIFF_ANALYSIS_DUTY_CYCLE

    wrapped: "Any"

    def __post_init__(self: "Self") -> None:
        """Override of the post initialisation magic method."""
        if not hasattr(self.wrapped, "reference_count"):
            self.wrapped.reference_count = 0

        self.wrapped.reference_count += 1

    @property
    @exception_bridge
    def gear_set(self: "Self") -> "_1022.CylindricalGearSetTIFFAnalysisDutyCycle":
        """mastapy.gears.gear_two_d_fe_analysis.CylindricalGearSetTIFFAnalysisDutyCycle

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "GearSet")

        if temp is None:
            return None

        type_ = temp.GetType()
        return constructor.new(type_.Namespace, type_.Name)(temp)

    @property
    def cast_to(self: "Self") -> "_Cast_CylindricalGearMeshTIFFAnalysisDutyCycle":
        """Cast to another type.

        Returns:
            _Cast_CylindricalGearMeshTIFFAnalysisDutyCycle
        """
        return _Cast_CylindricalGearMeshTIFFAnalysisDutyCycle(self)
