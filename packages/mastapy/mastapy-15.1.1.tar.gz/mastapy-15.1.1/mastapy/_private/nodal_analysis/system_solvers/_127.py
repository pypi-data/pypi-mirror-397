"""StiffnessSolver"""

from __future__ import annotations

from typing import TYPE_CHECKING, ClassVar

from mastapy._private._internal.dataclasses import extended_dataclass
from mastapy._private._internal.exceptions import CastException
from mastapy._private._internal.python_net import python_net_import

from mastapy._private._internal import utility
from mastapy._private.nodal_analysis.system_solvers import _125

_STIFFNESS_SOLVER = python_net_import(
    "SMT.MastaAPI.NodalAnalysis.SystemSolvers", "StiffnessSolver"
)

if TYPE_CHECKING:
    from typing import Any, Type, TypeVar

    from mastapy._private.nodal_analysis.system_solvers import (
        _112,
        _114,
        _115,
        _116,
        _117,
        _118,
        _121,
        _126,
        _129,
        _130,
    )

    Self = TypeVar("Self", bound="StiffnessSolver")
    CastSelf = TypeVar("CastSelf", bound="StiffnessSolver._Cast_StiffnessSolver")


__docformat__ = "restructuredtext en"
__all__ = ("StiffnessSolver",)


@extended_dataclass(frozen=True, slots=True, weakref_slot=True)
class _Cast_StiffnessSolver:
    """Special nested class for casting StiffnessSolver to subclasses."""

    __parent__: "StiffnessSolver"

    @property
    def solver(self: "CastSelf") -> "_125.Solver":
        return self.__parent__._cast(_125.Solver)

    @property
    def backward_euler_transient_solver(
        self: "CastSelf",
    ) -> "_112.BackwardEulerTransientSolver":
        from mastapy._private.nodal_analysis.system_solvers import _112

        return self.__parent__._cast(_112.BackwardEulerTransientSolver)

    @property
    def dirk_transient_solver(self: "CastSelf") -> "_114.DirkTransientSolver":
        from mastapy._private.nodal_analysis.system_solvers import _114

        return self.__parent__._cast(_114.DirkTransientSolver)

    @property
    def dynamic_solver(self: "CastSelf") -> "_115.DynamicSolver":
        from mastapy._private.nodal_analysis.system_solvers import _115

        return self.__parent__._cast(_115.DynamicSolver)

    @property
    def internal_transient_solver(self: "CastSelf") -> "_116.InternalTransientSolver":
        from mastapy._private.nodal_analysis.system_solvers import _116

        return self.__parent__._cast(_116.InternalTransientSolver)

    @property
    def lobatto_iiic_transient_solver(
        self: "CastSelf",
    ) -> "_117.LobattoIIICTransientSolver":
        from mastapy._private.nodal_analysis.system_solvers import _117

        return self.__parent__._cast(_117.LobattoIIICTransientSolver)

    @property
    def newmark_transient_solver(self: "CastSelf") -> "_118.NewmarkTransientSolver":
        from mastapy._private.nodal_analysis.system_solvers import _118

        return self.__parent__._cast(_118.NewmarkTransientSolver)

    @property
    def simple_velocity_based_step_halving_transient_solver(
        self: "CastSelf",
    ) -> "_121.SimpleVelocityBasedStepHalvingTransientSolver":
        from mastapy._private.nodal_analysis.system_solvers import _121

        return self.__parent__._cast(_121.SimpleVelocityBasedStepHalvingTransientSolver)

    @property
    def step_halving_transient_solver(
        self: "CastSelf",
    ) -> "_126.StepHalvingTransientSolver":
        from mastapy._private.nodal_analysis.system_solvers import _126

        return self.__parent__._cast(_126.StepHalvingTransientSolver)

    @property
    def transient_solver(self: "CastSelf") -> "_129.TransientSolver":
        from mastapy._private.nodal_analysis.system_solvers import _129

        return self.__parent__._cast(_129.TransientSolver)

    @property
    def wilson_theta_transient_solver(
        self: "CastSelf",
    ) -> "_130.WilsonThetaTransientSolver":
        from mastapy._private.nodal_analysis.system_solvers import _130

        return self.__parent__._cast(_130.WilsonThetaTransientSolver)

    @property
    def stiffness_solver(self: "CastSelf") -> "StiffnessSolver":
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
class StiffnessSolver(_125.Solver):
    """StiffnessSolver

    This is a mastapy class.
    """

    TYPE: ClassVar["Type"] = _STIFFNESS_SOLVER

    wrapped: "Any"

    def __post_init__(self: "Self") -> None:
        """Override of the post initialisation magic method."""
        if not hasattr(self.wrapped, "reference_count"):
            self.wrapped.reference_count = 0

        self.wrapped.reference_count += 1

    @property
    def cast_to(self: "Self") -> "_Cast_StiffnessSolver":
        """Cast to another type.

        Returns:
            _Cast_StiffnessSolver
        """
        return _Cast_StiffnessSolver(self)
