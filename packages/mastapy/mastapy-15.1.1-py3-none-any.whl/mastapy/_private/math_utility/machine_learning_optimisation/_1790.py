"""MachineLearningOptimizationVariable"""

from __future__ import annotations

from typing import TYPE_CHECKING, ClassVar

from mastapy._private._internal.dataclasses import extended_dataclass
from mastapy._private._internal.exceptions import CastException
from mastapy._private._internal.python_net import python_net_import

from mastapy._private._internal import utility
from mastapy._private.math_utility.optimisation import _1761

_MACHINE_LEARNING_OPTIMIZATION_VARIABLE = python_net_import(
    "SMT.MastaAPI.MathUtility.MachineLearningOptimisation",
    "MachineLearningOptimizationVariable",
)

if TYPE_CHECKING:
    from typing import Any, Type, TypeVar

    Self = TypeVar("Self", bound="MachineLearningOptimizationVariable")
    CastSelf = TypeVar(
        "CastSelf",
        bound="MachineLearningOptimizationVariable._Cast_MachineLearningOptimizationVariable",
    )


__docformat__ = "restructuredtext en"
__all__ = ("MachineLearningOptimizationVariable",)


@extended_dataclass(frozen=True, slots=True, weakref_slot=True)
class _Cast_MachineLearningOptimizationVariable:
    """Special nested class for casting MachineLearningOptimizationVariable to subclasses."""

    __parent__: "MachineLearningOptimizationVariable"

    @property
    def optimization_variable(self: "CastSelf") -> "_1761.OptimizationVariable":
        return self.__parent__._cast(_1761.OptimizationVariable)

    @property
    def machine_learning_optimization_variable(
        self: "CastSelf",
    ) -> "MachineLearningOptimizationVariable":
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
class MachineLearningOptimizationVariable(_1761.OptimizationVariable):
    """MachineLearningOptimizationVariable

    This is a mastapy class.
    """

    TYPE: ClassVar["Type"] = _MACHINE_LEARNING_OPTIMIZATION_VARIABLE

    wrapped: "Any"

    def __post_init__(self: "Self") -> None:
        """Override of the post initialisation magic method."""
        if not hasattr(self.wrapped, "reference_count"):
            self.wrapped.reference_count = 0

        self.wrapped.reference_count += 1

    @property
    def cast_to(self: "Self") -> "_Cast_MachineLearningOptimizationVariable":
        """Cast to another type.

        Returns:
            _Cast_MachineLearningOptimizationVariable
        """
        return _Cast_MachineLearningOptimizationVariable(self)
