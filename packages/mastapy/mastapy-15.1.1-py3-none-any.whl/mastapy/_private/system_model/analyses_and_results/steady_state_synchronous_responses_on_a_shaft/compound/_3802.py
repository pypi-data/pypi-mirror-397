"""VirtualComponentCompoundSteadyStateSynchronousResponseOnAShaft"""

from __future__ import annotations

from typing import TYPE_CHECKING, ClassVar

from mastapy._private._internal.dataclasses import extended_dataclass
from mastapy._private._internal.exception_bridge import exception_bridge
from mastapy._private._internal.exceptions import CastException
from mastapy._private._internal.python_net import (
    python_net_import,
    pythonnet_property_get,
)

from mastapy._private._internal import conversion, utility
from mastapy._private.system_model.analyses_and_results.steady_state_synchronous_responses_on_a_shaft.compound import (
    _3757,
)

_VIRTUAL_COMPONENT_COMPOUND_STEADY_STATE_SYNCHRONOUS_RESPONSE_ON_A_SHAFT = python_net_import(
    "SMT.MastaAPI.SystemModel.AnalysesAndResults.SteadyStateSynchronousResponsesOnAShaft.Compound",
    "VirtualComponentCompoundSteadyStateSynchronousResponseOnAShaft",
)

if TYPE_CHECKING:
    from typing import Any, List, Type, TypeVar

    from mastapy._private.system_model.analyses_and_results import _2943
    from mastapy._private.system_model.analyses_and_results.analysis_cases import (
        _7939,
        _7942,
    )
    from mastapy._private.system_model.analyses_and_results.steady_state_synchronous_responses_on_a_shaft import (
        _3671,
    )
    from mastapy._private.system_model.analyses_and_results.steady_state_synchronous_responses_on_a_shaft.compound import (
        _3703,
        _3753,
        _3754,
        _3759,
        _3766,
        _3767,
        _3801,
    )

    Self = TypeVar(
        "Self", bound="VirtualComponentCompoundSteadyStateSynchronousResponseOnAShaft"
    )
    CastSelf = TypeVar(
        "CastSelf",
        bound="VirtualComponentCompoundSteadyStateSynchronousResponseOnAShaft._Cast_VirtualComponentCompoundSteadyStateSynchronousResponseOnAShaft",
    )


__docformat__ = "restructuredtext en"
__all__ = ("VirtualComponentCompoundSteadyStateSynchronousResponseOnAShaft",)


@extended_dataclass(frozen=True, slots=True, weakref_slot=True)
class _Cast_VirtualComponentCompoundSteadyStateSynchronousResponseOnAShaft:
    """Special nested class for casting VirtualComponentCompoundSteadyStateSynchronousResponseOnAShaft to subclasses."""

    __parent__: "VirtualComponentCompoundSteadyStateSynchronousResponseOnAShaft"

    @property
    def mountable_component_compound_steady_state_synchronous_response_on_a_shaft(
        self: "CastSelf",
    ) -> "_3757.MountableComponentCompoundSteadyStateSynchronousResponseOnAShaft":
        return self.__parent__._cast(
            _3757.MountableComponentCompoundSteadyStateSynchronousResponseOnAShaft
        )

    @property
    def component_compound_steady_state_synchronous_response_on_a_shaft(
        self: "CastSelf",
    ) -> "_3703.ComponentCompoundSteadyStateSynchronousResponseOnAShaft":
        from mastapy._private.system_model.analyses_and_results.steady_state_synchronous_responses_on_a_shaft.compound import (
            _3703,
        )

        return self.__parent__._cast(
            _3703.ComponentCompoundSteadyStateSynchronousResponseOnAShaft
        )

    @property
    def part_compound_steady_state_synchronous_response_on_a_shaft(
        self: "CastSelf",
    ) -> "_3759.PartCompoundSteadyStateSynchronousResponseOnAShaft":
        from mastapy._private.system_model.analyses_and_results.steady_state_synchronous_responses_on_a_shaft.compound import (
            _3759,
        )

        return self.__parent__._cast(
            _3759.PartCompoundSteadyStateSynchronousResponseOnAShaft
        )

    @property
    def part_compound_analysis(self: "CastSelf") -> "_7942.PartCompoundAnalysis":
        from mastapy._private.system_model.analyses_and_results.analysis_cases import (
            _7942,
        )

        return self.__parent__._cast(_7942.PartCompoundAnalysis)

    @property
    def design_entity_compound_analysis(
        self: "CastSelf",
    ) -> "_7939.DesignEntityCompoundAnalysis":
        from mastapy._private.system_model.analyses_and_results.analysis_cases import (
            _7939,
        )

        return self.__parent__._cast(_7939.DesignEntityCompoundAnalysis)

    @property
    def design_entity_analysis(self: "CastSelf") -> "_2943.DesignEntityAnalysis":
        from mastapy._private.system_model.analyses_and_results import _2943

        return self.__parent__._cast(_2943.DesignEntityAnalysis)

    @property
    def mass_disc_compound_steady_state_synchronous_response_on_a_shaft(
        self: "CastSelf",
    ) -> "_3753.MassDiscCompoundSteadyStateSynchronousResponseOnAShaft":
        from mastapy._private.system_model.analyses_and_results.steady_state_synchronous_responses_on_a_shaft.compound import (
            _3753,
        )

        return self.__parent__._cast(
            _3753.MassDiscCompoundSteadyStateSynchronousResponseOnAShaft
        )

    @property
    def measurement_component_compound_steady_state_synchronous_response_on_a_shaft(
        self: "CastSelf",
    ) -> "_3754.MeasurementComponentCompoundSteadyStateSynchronousResponseOnAShaft":
        from mastapy._private.system_model.analyses_and_results.steady_state_synchronous_responses_on_a_shaft.compound import (
            _3754,
        )

        return self.__parent__._cast(
            _3754.MeasurementComponentCompoundSteadyStateSynchronousResponseOnAShaft
        )

    @property
    def point_load_compound_steady_state_synchronous_response_on_a_shaft(
        self: "CastSelf",
    ) -> "_3766.PointLoadCompoundSteadyStateSynchronousResponseOnAShaft":
        from mastapy._private.system_model.analyses_and_results.steady_state_synchronous_responses_on_a_shaft.compound import (
            _3766,
        )

        return self.__parent__._cast(
            _3766.PointLoadCompoundSteadyStateSynchronousResponseOnAShaft
        )

    @property
    def power_load_compound_steady_state_synchronous_response_on_a_shaft(
        self: "CastSelf",
    ) -> "_3767.PowerLoadCompoundSteadyStateSynchronousResponseOnAShaft":
        from mastapy._private.system_model.analyses_and_results.steady_state_synchronous_responses_on_a_shaft.compound import (
            _3767,
        )

        return self.__parent__._cast(
            _3767.PowerLoadCompoundSteadyStateSynchronousResponseOnAShaft
        )

    @property
    def unbalanced_mass_compound_steady_state_synchronous_response_on_a_shaft(
        self: "CastSelf",
    ) -> "_3801.UnbalancedMassCompoundSteadyStateSynchronousResponseOnAShaft":
        from mastapy._private.system_model.analyses_and_results.steady_state_synchronous_responses_on_a_shaft.compound import (
            _3801,
        )

        return self.__parent__._cast(
            _3801.UnbalancedMassCompoundSteadyStateSynchronousResponseOnAShaft
        )

    @property
    def virtual_component_compound_steady_state_synchronous_response_on_a_shaft(
        self: "CastSelf",
    ) -> "VirtualComponentCompoundSteadyStateSynchronousResponseOnAShaft":
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
class VirtualComponentCompoundSteadyStateSynchronousResponseOnAShaft(
    _3757.MountableComponentCompoundSteadyStateSynchronousResponseOnAShaft
):
    """VirtualComponentCompoundSteadyStateSynchronousResponseOnAShaft

    This is a mastapy class.
    """

    TYPE: ClassVar["Type"] = (
        _VIRTUAL_COMPONENT_COMPOUND_STEADY_STATE_SYNCHRONOUS_RESPONSE_ON_A_SHAFT
    )

    wrapped: "Any"

    def __post_init__(self: "Self") -> None:
        """Override of the post initialisation magic method."""
        if not hasattr(self.wrapped, "reference_count"):
            self.wrapped.reference_count = 0

        self.wrapped.reference_count += 1

    @property
    @exception_bridge
    def component_analysis_cases(
        self: "Self",
    ) -> "List[_3671.VirtualComponentSteadyStateSynchronousResponseOnAShaft]":
        """List[mastapy.system_model.analyses_and_results.steady_state_synchronous_responses_on_a_shaft.VirtualComponentSteadyStateSynchronousResponseOnAShaft]

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "ComponentAnalysisCases")

        if temp is None:
            return None

        value = conversion.pn_to_mp_objects_in_list(temp)

        if value is None:
            return None

        return value

    @property
    @exception_bridge
    def component_analysis_cases_ready(
        self: "Self",
    ) -> "List[_3671.VirtualComponentSteadyStateSynchronousResponseOnAShaft]":
        """List[mastapy.system_model.analyses_and_results.steady_state_synchronous_responses_on_a_shaft.VirtualComponentSteadyStateSynchronousResponseOnAShaft]

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "ComponentAnalysisCasesReady")

        if temp is None:
            return None

        value = conversion.pn_to_mp_objects_in_list(temp)

        if value is None:
            return None

        return value

    @property
    def cast_to(
        self: "Self",
    ) -> "_Cast_VirtualComponentCompoundSteadyStateSynchronousResponseOnAShaft":
        """Cast to another type.

        Returns:
            _Cast_VirtualComponentCompoundSteadyStateSynchronousResponseOnAShaft
        """
        return _Cast_VirtualComponentCompoundSteadyStateSynchronousResponseOnAShaft(
            self
        )
