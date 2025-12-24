"""NewmarkTransientSolver"""

from __future__ import annotations

from typing import TYPE_CHECKING, ClassVar

from mastapy._private._internal.dataclasses import extended_dataclass
from mastapy._private._internal.exceptions import CastException
from mastapy._private._internal.python_net import python_net_import

from mastapy._private._internal import utility
from mastapy._private.nodal_analysis.system_solvers import _121

_NEWMARK_TRANSIENT_SOLVER = python_net_import(
    "SMT.MastaAPI.NodalAnalysis.SystemSolvers", "NewmarkTransientSolver"
)

if TYPE_CHECKING:
    from typing import Any, Type, TypeVar

    from mastapy._private.nodal_analysis.system_solvers import (
        _115,
        _116,
        _125,
        _126,
        _127,
        _129,
    )

    Self = TypeVar("Self", bound="NewmarkTransientSolver")
    CastSelf = TypeVar(
        "CastSelf", bound="NewmarkTransientSolver._Cast_NewmarkTransientSolver"
    )


__docformat__ = "restructuredtext en"
__all__ = ("NewmarkTransientSolver",)


@extended_dataclass(frozen=True, slots=True, weakref_slot=True)
class _Cast_NewmarkTransientSolver:
    """Special nested class for casting NewmarkTransientSolver to subclasses."""

    __parent__: "NewmarkTransientSolver"

    @property
    def simple_velocity_based_step_halving_transient_solver(
        self: "CastSelf",
    ) -> "_121.SimpleVelocityBasedStepHalvingTransientSolver":
        return self.__parent__._cast(_121.SimpleVelocityBasedStepHalvingTransientSolver)

    @property
    def step_halving_transient_solver(
        self: "CastSelf",
    ) -> "_126.StepHalvingTransientSolver":
        from mastapy._private.nodal_analysis.system_solvers import _126

        return self.__parent__._cast(_126.StepHalvingTransientSolver)

    @property
    def internal_transient_solver(self: "CastSelf") -> "_116.InternalTransientSolver":
        from mastapy._private.nodal_analysis.system_solvers import _116

        return self.__parent__._cast(_116.InternalTransientSolver)

    @property
    def transient_solver(self: "CastSelf") -> "_129.TransientSolver":
        from mastapy._private.nodal_analysis.system_solvers import _129

        return self.__parent__._cast(_129.TransientSolver)

    @property
    def dynamic_solver(self: "CastSelf") -> "_115.DynamicSolver":
        from mastapy._private.nodal_analysis.system_solvers import _115

        return self.__parent__._cast(_115.DynamicSolver)

    @property
    def stiffness_solver(self: "CastSelf") -> "_127.StiffnessSolver":
        from mastapy._private.nodal_analysis.system_solvers import _127

        return self.__parent__._cast(_127.StiffnessSolver)

    @property
    def solver(self: "CastSelf") -> "_125.Solver":
        from mastapy._private.nodal_analysis.system_solvers import _125

        return self.__parent__._cast(_125.Solver)

    @property
    def newmark_transient_solver(self: "CastSelf") -> "NewmarkTransientSolver":
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
class NewmarkTransientSolver(_121.SimpleVelocityBasedStepHalvingTransientSolver):
    """NewmarkTransientSolver

    This is a mastapy class.
    """

    TYPE: ClassVar["Type"] = _NEWMARK_TRANSIENT_SOLVER

    wrapped: "Any"

    def __post_init__(self: "Self") -> None:
        """Override of the post initialisation magic method."""
        if not hasattr(self.wrapped, "reference_count"):
            self.wrapped.reference_count = 0

        self.wrapped.reference_count += 1

    @property
    def cast_to(self: "Self") -> "_Cast_NewmarkTransientSolver":
        """Cast to another type.

        Returns:
            _Cast_NewmarkTransientSolver
        """
        return _Cast_NewmarkTransientSolver(self)
