"""Solver"""

from __future__ import annotations

from typing import TYPE_CHECKING, ClassVar

from mastapy._private._internal.dataclasses import extended_dataclass
from mastapy._private._internal.exception_bridge import exception_bridge
from mastapy._private._internal.exceptions import CastException
from mastapy._private._internal.python_net import (
    python_net_import,
    pythonnet_property_get,
)

from mastapy._private import _0
from mastapy._private._internal import utility

_SOLVER = python_net_import("SMT.MastaAPI.NodalAnalysis.SystemSolvers", "Solver")

if TYPE_CHECKING:
    from typing import Any, Type, TypeVar

    from mastapy._private.nodal_analysis.system_solvers import (
        _112,
        _113,
        _114,
        _115,
        _116,
        _117,
        _118,
        _121,
        _126,
        _127,
        _128,
        _129,
        _130,
    )

    Self = TypeVar("Self", bound="Solver")
    CastSelf = TypeVar("CastSelf", bound="Solver._Cast_Solver")


__docformat__ = "restructuredtext en"
__all__ = ("Solver",)


@extended_dataclass(frozen=True, slots=True, weakref_slot=True)
class _Cast_Solver:
    """Special nested class for casting Solver to subclasses."""

    __parent__: "Solver"

    @property
    def backward_euler_transient_solver(
        self: "CastSelf",
    ) -> "_112.BackwardEulerTransientSolver":
        from mastapy._private.nodal_analysis.system_solvers import _112

        return self.__parent__._cast(_112.BackwardEulerTransientSolver)

    @property
    def dense_stiffness_solver(self: "CastSelf") -> "_113.DenseStiffnessSolver":
        from mastapy._private.nodal_analysis.system_solvers import _113

        return self.__parent__._cast(_113.DenseStiffnessSolver)

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
    def stiffness_solver(self: "CastSelf") -> "_127.StiffnessSolver":
        from mastapy._private.nodal_analysis.system_solvers import _127

        return self.__parent__._cast(_127.StiffnessSolver)

    @property
    def thermal_solver(self: "CastSelf") -> "_128.ThermalSolver":
        from mastapy._private.nodal_analysis.system_solvers import _128

        return self.__parent__._cast(_128.ThermalSolver)

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
    def solver(self: "CastSelf") -> "Solver":
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
class Solver(_0.APIBase):
    """Solver

    This is a mastapy class.
    """

    TYPE: ClassVar["Type"] = _SOLVER

    wrapped: "Any"

    def __post_init__(self: "Self") -> None:
        """Override of the post initialisation magic method."""
        if not hasattr(self.wrapped, "reference_count"):
            self.wrapped.reference_count = 0

        self.wrapped.reference_count += 1

    @property
    @exception_bridge
    def average_number_of_jacobian_evaluations_per_newton_raphson_solve(
        self: "Self",
    ) -> "float":
        """float

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(
            self.wrapped, "AverageNumberOfJacobianEvaluationsPerNewtonRaphsonSolve"
        )

        if temp is None:
            return 0.0

        return temp

    @property
    @exception_bridge
    def number_of_failed_newton_raphson_solves(self: "Self") -> "int":
        """int

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "NumberOfFailedNewtonRaphsonSolves")

        if temp is None:
            return 0

        return temp

    @property
    @exception_bridge
    def number_of_newton_raphson_jacobian_evaluations(self: "Self") -> "int":
        """int

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(
            self.wrapped, "NumberOfNewtonRaphsonJacobianEvaluations"
        )

        if temp is None:
            return 0

        return temp

    @property
    @exception_bridge
    def number_of_newton_raphson_maximum_iterations_reached(self: "Self") -> "int":
        """int

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(
            self.wrapped, "NumberOfNewtonRaphsonMaximumIterationsReached"
        )

        if temp is None:
            return 0

        return temp

    @property
    @exception_bridge
    def number_of_newton_raphson_other_status_results(self: "Self") -> "int":
        """int

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(
            self.wrapped, "NumberOfNewtonRaphsonOtherStatusResults"
        )

        if temp is None:
            return 0

        return temp

    @property
    @exception_bridge
    def number_of_newton_raphson_residual_evaluations(self: "Self") -> "int":
        """int

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(
            self.wrapped, "NumberOfNewtonRaphsonResidualEvaluations"
        )

        if temp is None:
            return 0

        return temp

    @property
    @exception_bridge
    def number_of_newton_raphson_residual_tolerance_met(self: "Self") -> "int":
        """int

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(
            self.wrapped, "NumberOfNewtonRaphsonResidualToleranceMet"
        )

        if temp is None:
            return 0

        return temp

    @property
    @exception_bridge
    def number_of_newton_raphson_solves(self: "Self") -> "int":
        """int

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "NumberOfNewtonRaphsonSolves")

        if temp is None:
            return 0

        return temp

    @property
    @exception_bridge
    def number_of_newton_raphson_values_not_changing(self: "Self") -> "int":
        """int

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(
            self.wrapped, "NumberOfNewtonRaphsonValuesNotChanging"
        )

        if temp is None:
            return 0

        return temp

    @property
    @exception_bridge
    def number_of_nodes(self: "Self") -> "int":
        """int

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "NumberOfNodes")

        if temp is None:
            return 0

        return temp

    @property
    @exception_bridge
    def total_number_of_degrees_of_freedom(self: "Self") -> "int":
        """int

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "TotalNumberOfDegreesOfFreedom")

        if temp is None:
            return 0

        return temp

    @property
    def cast_to(self: "Self") -> "_Cast_Solver":
        """Cast to another type.

        Returns:
            _Cast_Solver
        """
        return _Cast_Solver(self)
