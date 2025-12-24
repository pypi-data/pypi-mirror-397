"""GearSetImplementationAnalysisDutyCycle"""

from __future__ import annotations

from typing import TYPE_CHECKING, ClassVar

from mastapy._private._internal.dataclasses import extended_dataclass
from mastapy._private._internal.exception_bridge import exception_bridge
from mastapy._private._internal.exceptions import CastException
from mastapy._private._internal.python_net import (
    python_net_import,
    pythonnet_property_get,
)

from mastapy._private._internal import utility
from mastapy._private.gears.analysis import _1375

_GEAR_SET_IMPLEMENTATION_ANALYSIS_DUTY_CYCLE = python_net_import(
    "SMT.MastaAPI.Gears.Analysis", "GearSetImplementationAnalysisDutyCycle"
)

if TYPE_CHECKING:
    from typing import Any, Type, TypeVar

    from mastapy._private.gears.analysis import _1363, _1372
    from mastapy._private.gears.gear_designs.cylindrical.micro_geometry import _1244
    from mastapy._private.gears.manufacturing.cylindrical import _746

    Self = TypeVar("Self", bound="GearSetImplementationAnalysisDutyCycle")
    CastSelf = TypeVar(
        "CastSelf",
        bound="GearSetImplementationAnalysisDutyCycle._Cast_GearSetImplementationAnalysisDutyCycle",
    )


__docformat__ = "restructuredtext en"
__all__ = ("GearSetImplementationAnalysisDutyCycle",)


@extended_dataclass(frozen=True, slots=True, weakref_slot=True)
class _Cast_GearSetImplementationAnalysisDutyCycle:
    """Special nested class for casting GearSetImplementationAnalysisDutyCycle to subclasses."""

    __parent__: "GearSetImplementationAnalysisDutyCycle"

    @property
    def gear_set_implementation_analysis_abstract(
        self: "CastSelf",
    ) -> "_1375.GearSetImplementationAnalysisAbstract":
        return self.__parent__._cast(_1375.GearSetImplementationAnalysisAbstract)

    @property
    def gear_set_design_analysis(self: "CastSelf") -> "_1372.GearSetDesignAnalysis":
        from mastapy._private.gears.analysis import _1372

        return self.__parent__._cast(_1372.GearSetDesignAnalysis)

    @property
    def abstract_gear_set_analysis(self: "CastSelf") -> "_1363.AbstractGearSetAnalysis":
        from mastapy._private.gears.analysis import _1363

        return self.__parent__._cast(_1363.AbstractGearSetAnalysis)

    @property
    def cylindrical_manufactured_gear_set_duty_cycle(
        self: "CastSelf",
    ) -> "_746.CylindricalManufacturedGearSetDutyCycle":
        from mastapy._private.gears.manufacturing.cylindrical import _746

        return self.__parent__._cast(_746.CylindricalManufacturedGearSetDutyCycle)

    @property
    def cylindrical_gear_set_micro_geometry_duty_cycle(
        self: "CastSelf",
    ) -> "_1244.CylindricalGearSetMicroGeometryDutyCycle":
        from mastapy._private.gears.gear_designs.cylindrical.micro_geometry import _1244

        return self.__parent__._cast(_1244.CylindricalGearSetMicroGeometryDutyCycle)

    @property
    def gear_set_implementation_analysis_duty_cycle(
        self: "CastSelf",
    ) -> "GearSetImplementationAnalysisDutyCycle":
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
class GearSetImplementationAnalysisDutyCycle(
    _1375.GearSetImplementationAnalysisAbstract
):
    """GearSetImplementationAnalysisDutyCycle

    This is a mastapy class.
    """

    TYPE: ClassVar["Type"] = _GEAR_SET_IMPLEMENTATION_ANALYSIS_DUTY_CYCLE

    wrapped: "Any"

    def __post_init__(self: "Self") -> None:
        """Override of the post initialisation magic method."""
        if not hasattr(self.wrapped, "reference_count"):
            self.wrapped.reference_count = 0

        self.wrapped.reference_count += 1

    @property
    @exception_bridge
    def duty_cycle_name(self: "Self") -> "str":
        """str

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "DutyCycleName")

        if temp is None:
            return ""

        return temp

    @property
    def cast_to(self: "Self") -> "_Cast_GearSetImplementationAnalysisDutyCycle":
        """Cast to another type.

        Returns:
            _Cast_GearSetImplementationAnalysisDutyCycle
        """
        return _Cast_GearSetImplementationAnalysisDutyCycle(self)
