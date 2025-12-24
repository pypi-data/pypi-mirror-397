"""OptimizationVariable"""

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

from mastapy._private import _0
from mastapy._private._internal import constructor, conversion, utility

_OPTIMIZATION_VARIABLE = python_net_import(
    "SMT.MastaAPI.MathUtility.Optimisation", "OptimizationVariable"
)

if TYPE_CHECKING:
    from typing import Any, List, Type, TypeVar

    from mastapy._private.math_utility.machine_learning_optimisation import _1790
    from mastapy._private.math_utility.optimisation import _1759, _1772
    from mastapy._private.utility.units_and_measurements import _1829

    Self = TypeVar("Self", bound="OptimizationVariable")
    CastSelf = TypeVar(
        "CastSelf", bound="OptimizationVariable._Cast_OptimizationVariable"
    )


__docformat__ = "restructuredtext en"
__all__ = ("OptimizationVariable",)


@extended_dataclass(frozen=True, slots=True, weakref_slot=True)
class _Cast_OptimizationVariable:
    """Special nested class for casting OptimizationVariable to subclasses."""

    __parent__: "OptimizationVariable"

    @property
    def optimization_input(self: "CastSelf") -> "_1759.OptimizationInput":
        from mastapy._private.math_utility.optimisation import _1759

        return self.__parent__._cast(_1759.OptimizationInput)

    @property
    def reporting_optimization_input(
        self: "CastSelf",
    ) -> "_1772.ReportingOptimizationInput":
        from mastapy._private.math_utility.optimisation import _1772

        return self.__parent__._cast(_1772.ReportingOptimizationInput)

    @property
    def machine_learning_optimization_variable(
        self: "CastSelf",
    ) -> "_1790.MachineLearningOptimizationVariable":
        from mastapy._private.math_utility.machine_learning_optimisation import _1790

        return self.__parent__._cast(_1790.MachineLearningOptimizationVariable)

    @property
    def optimization_variable(self: "CastSelf") -> "OptimizationVariable":
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
class OptimizationVariable(_0.APIBase):
    """OptimizationVariable

    This is a mastapy class.
    """

    TYPE: ClassVar["Type"] = _OPTIMIZATION_VARIABLE

    wrapped: "Any"

    def __post_init__(self: "Self") -> None:
        """Override of the post initialisation magic method."""
        if not hasattr(self.wrapped, "reference_count"):
            self.wrapped.reference_count = 0

        self.wrapped.reference_count += 1

    @property
    @exception_bridge
    def measurement(self: "Self") -> "_1829.MeasurementBase":
        """mastapy.utility.units_and_measurements.MeasurementBase"""
        temp = pythonnet_property_get(self.wrapped, "Measurement")

        if temp is None:
            return None

        type_ = temp.GetType()
        return constructor.new(type_.Namespace, type_.Name)(temp)

    @measurement.setter
    @exception_bridge
    @enforce_parameter_types
    def measurement(self: "Self", value: "_1829.MeasurementBase") -> None:
        pythonnet_property_set(self.wrapped, "Measurement", value.wrapped)

    @property
    @exception_bridge
    def results(self: "Self") -> "List[float]":
        """List[float]

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "Results")

        if temp is None:
            return None

        value = conversion.to_list_any(temp)

        if value is None:
            return None

        return value

    @property
    def cast_to(self: "Self") -> "_Cast_OptimizationVariable":
        """Cast to another type.

        Returns:
            _Cast_OptimizationVariable
        """
        return _Cast_OptimizationVariable(self)
