"""LobattoIIICTransientSolver"""

from __future__ import annotations

from typing import TYPE_CHECKING, ClassVar

from mastapy._private._internal.dataclasses import extended_dataclass
from mastapy._private._internal.exceptions import CastException
from mastapy._private._internal.python_net import python_net_import

from mastapy._private._internal import utility
from mastapy._private.nodal_analysis.system_solvers import _126

_LOBATTO_IIIC_TRANSIENT_SOLVER = python_net_import(
    "SMT.MastaAPI.NodalAnalysis.SystemSolvers", "LobattoIIICTransientSolver"
)

if TYPE_CHECKING:
    from typing import Any, Type, TypeVar

    from mastapy._private.nodal_analysis.system_solvers import (
        _115,
        _116,
        _125,
        _127,
        _129,
    )

    Self = TypeVar("Self", bound="LobattoIIICTransientSolver")
    CastSelf = TypeVar(
        "CastSelf", bound="LobattoIIICTransientSolver._Cast_LobattoIIICTransientSolver"
    )


__docformat__ = "restructuredtext en"
__all__ = ("LobattoIIICTransientSolver",)


@extended_dataclass(frozen=True, slots=True, weakref_slot=True)
class _Cast_LobattoIIICTransientSolver:
    """Special nested class for casting LobattoIIICTransientSolver to subclasses."""

    __parent__: "LobattoIIICTransientSolver"

    @property
    def step_halving_transient_solver(
        self: "CastSelf",
    ) -> "_126.StepHalvingTransientSolver":
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
    def lobatto_iiic_transient_solver(self: "CastSelf") -> "LobattoIIICTransientSolver":
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
class LobattoIIICTransientSolver(_126.StepHalvingTransientSolver):
    """LobattoIIICTransientSolver

    This is a mastapy class.
    """

    TYPE: ClassVar["Type"] = _LOBATTO_IIIC_TRANSIENT_SOLVER

    wrapped: "Any"

    def __post_init__(self: "Self") -> None:
        """Override of the post initialisation magic method."""
        if not hasattr(self.wrapped, "reference_count"):
            self.wrapped.reference_count = 0

        self.wrapped.reference_count += 1

    @property
    def cast_to(self: "Self") -> "_Cast_LobattoIIICTransientSolver":
        """Cast to another type.

        Returns:
            _Cast_LobattoIIICTransientSolver
        """
        return _Cast_LobattoIIICTransientSolver(self)
