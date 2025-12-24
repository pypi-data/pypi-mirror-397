"""CouplingSteadyStateSynchronousResponse"""

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
from mastapy._private.system_model.analyses_and_results.steady_state_synchronous_responses import (
    _3381,
)

_COUPLING_STEADY_STATE_SYNCHRONOUS_RESPONSE = python_net_import(
    "SMT.MastaAPI.SystemModel.AnalysesAndResults.SteadyStateSynchronousResponses",
    "CouplingSteadyStateSynchronousResponse",
)

if TYPE_CHECKING:
    from typing import Any, Type, TypeVar

    from mastapy._private.system_model.analyses_and_results import _2943, _2945, _2949
    from mastapy._private.system_model.analyses_and_results.analysis_cases import (
        _7941,
        _7944,
    )
    from mastapy._private.system_model.analyses_and_results.steady_state_synchronous_responses import (
        _3280,
        _3303,
        _3308,
        _3362,
        _3365,
        _3387,
        _3405,
    )
    from mastapy._private.system_model.part_model.couplings import _2867

    Self = TypeVar("Self", bound="CouplingSteadyStateSynchronousResponse")
    CastSelf = TypeVar(
        "CastSelf",
        bound="CouplingSteadyStateSynchronousResponse._Cast_CouplingSteadyStateSynchronousResponse",
    )


__docformat__ = "restructuredtext en"
__all__ = ("CouplingSteadyStateSynchronousResponse",)


@extended_dataclass(frozen=True, slots=True, weakref_slot=True)
class _Cast_CouplingSteadyStateSynchronousResponse:
    """Special nested class for casting CouplingSteadyStateSynchronousResponse to subclasses."""

    __parent__: "CouplingSteadyStateSynchronousResponse"

    @property
    def specialised_assembly_steady_state_synchronous_response(
        self: "CastSelf",
    ) -> "_3381.SpecialisedAssemblySteadyStateSynchronousResponse":
        return self.__parent__._cast(
            _3381.SpecialisedAssemblySteadyStateSynchronousResponse
        )

    @property
    def abstract_assembly_steady_state_synchronous_response(
        self: "CastSelf",
    ) -> "_3280.AbstractAssemblySteadyStateSynchronousResponse":
        from mastapy._private.system_model.analyses_and_results.steady_state_synchronous_responses import (
            _3280,
        )

        return self.__parent__._cast(
            _3280.AbstractAssemblySteadyStateSynchronousResponse
        )

    @property
    def part_steady_state_synchronous_response(
        self: "CastSelf",
    ) -> "_3362.PartSteadyStateSynchronousResponse":
        from mastapy._private.system_model.analyses_and_results.steady_state_synchronous_responses import (
            _3362,
        )

        return self.__parent__._cast(_3362.PartSteadyStateSynchronousResponse)

    @property
    def part_static_load_analysis_case(
        self: "CastSelf",
    ) -> "_7944.PartStaticLoadAnalysisCase":
        from mastapy._private.system_model.analyses_and_results.analysis_cases import (
            _7944,
        )

        return self.__parent__._cast(_7944.PartStaticLoadAnalysisCase)

    @property
    def part_analysis_case(self: "CastSelf") -> "_7941.PartAnalysisCase":
        from mastapy._private.system_model.analyses_and_results.analysis_cases import (
            _7941,
        )

        return self.__parent__._cast(_7941.PartAnalysisCase)

    @property
    def part_analysis(self: "CastSelf") -> "_2949.PartAnalysis":
        from mastapy._private.system_model.analyses_and_results import _2949

        return self.__parent__._cast(_2949.PartAnalysis)

    @property
    def design_entity_single_context_analysis(
        self: "CastSelf",
    ) -> "_2945.DesignEntitySingleContextAnalysis":
        from mastapy._private.system_model.analyses_and_results import _2945

        return self.__parent__._cast(_2945.DesignEntitySingleContextAnalysis)

    @property
    def design_entity_analysis(self: "CastSelf") -> "_2943.DesignEntityAnalysis":
        from mastapy._private.system_model.analyses_and_results import _2943

        return self.__parent__._cast(_2943.DesignEntityAnalysis)

    @property
    def clutch_steady_state_synchronous_response(
        self: "CastSelf",
    ) -> "_3303.ClutchSteadyStateSynchronousResponse":
        from mastapy._private.system_model.analyses_and_results.steady_state_synchronous_responses import (
            _3303,
        )

        return self.__parent__._cast(_3303.ClutchSteadyStateSynchronousResponse)

    @property
    def concept_coupling_steady_state_synchronous_response(
        self: "CastSelf",
    ) -> "_3308.ConceptCouplingSteadyStateSynchronousResponse":
        from mastapy._private.system_model.analyses_and_results.steady_state_synchronous_responses import (
            _3308,
        )

        return self.__parent__._cast(
            _3308.ConceptCouplingSteadyStateSynchronousResponse
        )

    @property
    def part_to_part_shear_coupling_steady_state_synchronous_response(
        self: "CastSelf",
    ) -> "_3365.PartToPartShearCouplingSteadyStateSynchronousResponse":
        from mastapy._private.system_model.analyses_and_results.steady_state_synchronous_responses import (
            _3365,
        )

        return self.__parent__._cast(
            _3365.PartToPartShearCouplingSteadyStateSynchronousResponse
        )

    @property
    def spring_damper_steady_state_synchronous_response(
        self: "CastSelf",
    ) -> "_3387.SpringDamperSteadyStateSynchronousResponse":
        from mastapy._private.system_model.analyses_and_results.steady_state_synchronous_responses import (
            _3387,
        )

        return self.__parent__._cast(_3387.SpringDamperSteadyStateSynchronousResponse)

    @property
    def torque_converter_steady_state_synchronous_response(
        self: "CastSelf",
    ) -> "_3405.TorqueConverterSteadyStateSynchronousResponse":
        from mastapy._private.system_model.analyses_and_results.steady_state_synchronous_responses import (
            _3405,
        )

        return self.__parent__._cast(
            _3405.TorqueConverterSteadyStateSynchronousResponse
        )

    @property
    def coupling_steady_state_synchronous_response(
        self: "CastSelf",
    ) -> "CouplingSteadyStateSynchronousResponse":
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
class CouplingSteadyStateSynchronousResponse(
    _3381.SpecialisedAssemblySteadyStateSynchronousResponse
):
    """CouplingSteadyStateSynchronousResponse

    This is a mastapy class.
    """

    TYPE: ClassVar["Type"] = _COUPLING_STEADY_STATE_SYNCHRONOUS_RESPONSE

    wrapped: "Any"

    def __post_init__(self: "Self") -> None:
        """Override of the post initialisation magic method."""
        if not hasattr(self.wrapped, "reference_count"):
            self.wrapped.reference_count = 0

        self.wrapped.reference_count += 1

    @property
    @exception_bridge
    def assembly_design(self: "Self") -> "_2867.Coupling":
        """mastapy.system_model.part_model.couplings.Coupling

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "AssemblyDesign")

        if temp is None:
            return None

        type_ = temp.GetType()
        return constructor.new(type_.Namespace, type_.Name)(temp)

    @property
    def cast_to(self: "Self") -> "_Cast_CouplingSteadyStateSynchronousResponse":
        """Cast to another type.

        Returns:
            _Cast_CouplingSteadyStateSynchronousResponse
        """
        return _Cast_CouplingSteadyStateSynchronousResponse(self)
