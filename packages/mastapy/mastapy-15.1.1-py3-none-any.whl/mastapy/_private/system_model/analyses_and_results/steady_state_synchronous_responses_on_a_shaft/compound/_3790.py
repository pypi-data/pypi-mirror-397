"""StraightBevelGearSetCompoundSteadyStateSynchronousResponseOnAShaft"""

from __future__ import annotations

from typing import TYPE_CHECKING, ClassVar

from mastapy._private._internal.dataclasses import extended_dataclass
from mastapy._private._internal.exception_bridge import exception_bridge
from mastapy._private._internal.exceptions import CastException
from mastapy._private._internal.python_net import (
    python_net_import,
    pythonnet_property_get,
)

from mastapy._private._internal import constructor, conversion, utility
from mastapy._private.system_model.analyses_and_results.steady_state_synchronous_responses_on_a_shaft.compound import (
    _3696,
)

_STRAIGHT_BEVEL_GEAR_SET_COMPOUND_STEADY_STATE_SYNCHRONOUS_RESPONSE_ON_A_SHAFT = python_net_import(
    "SMT.MastaAPI.SystemModel.AnalysesAndResults.SteadyStateSynchronousResponsesOnAShaft.Compound",
    "StraightBevelGearSetCompoundSteadyStateSynchronousResponseOnAShaft",
)

if TYPE_CHECKING:
    from typing import Any, List, Type, TypeVar

    from mastapy._private.system_model.analyses_and_results import _2943
    from mastapy._private.system_model.analyses_and_results.analysis_cases import (
        _7939,
        _7942,
    )
    from mastapy._private.system_model.analyses_and_results.steady_state_synchronous_responses_on_a_shaft import (
        _3658,
    )
    from mastapy._private.system_model.analyses_and_results.steady_state_synchronous_responses_on_a_shaft.compound import (
        _3678,
        _3684,
        _3712,
        _3738,
        _3759,
        _3778,
        _3788,
        _3789,
    )
    from mastapy._private.system_model.part_model.gears import _2830

    Self = TypeVar(
        "Self",
        bound="StraightBevelGearSetCompoundSteadyStateSynchronousResponseOnAShaft",
    )
    CastSelf = TypeVar(
        "CastSelf",
        bound="StraightBevelGearSetCompoundSteadyStateSynchronousResponseOnAShaft._Cast_StraightBevelGearSetCompoundSteadyStateSynchronousResponseOnAShaft",
    )


__docformat__ = "restructuredtext en"
__all__ = ("StraightBevelGearSetCompoundSteadyStateSynchronousResponseOnAShaft",)


@extended_dataclass(frozen=True, slots=True, weakref_slot=True)
class _Cast_StraightBevelGearSetCompoundSteadyStateSynchronousResponseOnAShaft:
    """Special nested class for casting StraightBevelGearSetCompoundSteadyStateSynchronousResponseOnAShaft to subclasses."""

    __parent__: "StraightBevelGearSetCompoundSteadyStateSynchronousResponseOnAShaft"

    @property
    def bevel_gear_set_compound_steady_state_synchronous_response_on_a_shaft(
        self: "CastSelf",
    ) -> "_3696.BevelGearSetCompoundSteadyStateSynchronousResponseOnAShaft":
        return self.__parent__._cast(
            _3696.BevelGearSetCompoundSteadyStateSynchronousResponseOnAShaft
        )

    @property
    def agma_gleason_conical_gear_set_compound_steady_state_synchronous_response_on_a_shaft(
        self: "CastSelf",
    ) -> (
        "_3684.AGMAGleasonConicalGearSetCompoundSteadyStateSynchronousResponseOnAShaft"
    ):
        from mastapy._private.system_model.analyses_and_results.steady_state_synchronous_responses_on_a_shaft.compound import (
            _3684,
        )

        return self.__parent__._cast(
            _3684.AGMAGleasonConicalGearSetCompoundSteadyStateSynchronousResponseOnAShaft
        )

    @property
    def conical_gear_set_compound_steady_state_synchronous_response_on_a_shaft(
        self: "CastSelf",
    ) -> "_3712.ConicalGearSetCompoundSteadyStateSynchronousResponseOnAShaft":
        from mastapy._private.system_model.analyses_and_results.steady_state_synchronous_responses_on_a_shaft.compound import (
            _3712,
        )

        return self.__parent__._cast(
            _3712.ConicalGearSetCompoundSteadyStateSynchronousResponseOnAShaft
        )

    @property
    def gear_set_compound_steady_state_synchronous_response_on_a_shaft(
        self: "CastSelf",
    ) -> "_3738.GearSetCompoundSteadyStateSynchronousResponseOnAShaft":
        from mastapy._private.system_model.analyses_and_results.steady_state_synchronous_responses_on_a_shaft.compound import (
            _3738,
        )

        return self.__parent__._cast(
            _3738.GearSetCompoundSteadyStateSynchronousResponseOnAShaft
        )

    @property
    def specialised_assembly_compound_steady_state_synchronous_response_on_a_shaft(
        self: "CastSelf",
    ) -> "_3778.SpecialisedAssemblyCompoundSteadyStateSynchronousResponseOnAShaft":
        from mastapy._private.system_model.analyses_and_results.steady_state_synchronous_responses_on_a_shaft.compound import (
            _3778,
        )

        return self.__parent__._cast(
            _3778.SpecialisedAssemblyCompoundSteadyStateSynchronousResponseOnAShaft
        )

    @property
    def abstract_assembly_compound_steady_state_synchronous_response_on_a_shaft(
        self: "CastSelf",
    ) -> "_3678.AbstractAssemblyCompoundSteadyStateSynchronousResponseOnAShaft":
        from mastapy._private.system_model.analyses_and_results.steady_state_synchronous_responses_on_a_shaft.compound import (
            _3678,
        )

        return self.__parent__._cast(
            _3678.AbstractAssemblyCompoundSteadyStateSynchronousResponseOnAShaft
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
    def straight_bevel_gear_set_compound_steady_state_synchronous_response_on_a_shaft(
        self: "CastSelf",
    ) -> "StraightBevelGearSetCompoundSteadyStateSynchronousResponseOnAShaft":
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
class StraightBevelGearSetCompoundSteadyStateSynchronousResponseOnAShaft(
    _3696.BevelGearSetCompoundSteadyStateSynchronousResponseOnAShaft
):
    """StraightBevelGearSetCompoundSteadyStateSynchronousResponseOnAShaft

    This is a mastapy class.
    """

    TYPE: ClassVar["Type"] = (
        _STRAIGHT_BEVEL_GEAR_SET_COMPOUND_STEADY_STATE_SYNCHRONOUS_RESPONSE_ON_A_SHAFT
    )

    wrapped: "Any"

    def __post_init__(self: "Self") -> None:
        """Override of the post initialisation magic method."""
        if not hasattr(self.wrapped, "reference_count"):
            self.wrapped.reference_count = 0

        self.wrapped.reference_count += 1

    @property
    @exception_bridge
    def component_design(self: "Self") -> "_2830.StraightBevelGearSet":
        """mastapy.system_model.part_model.gears.StraightBevelGearSet

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "ComponentDesign")

        if temp is None:
            return None

        type_ = temp.GetType()
        return constructor.new(type_.Namespace, type_.Name)(temp)

    @property
    @exception_bridge
    def assembly_design(self: "Self") -> "_2830.StraightBevelGearSet":
        """mastapy.system_model.part_model.gears.StraightBevelGearSet

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "AssemblyDesign")

        if temp is None:
            return None

        type_ = temp.GetType()
        return constructor.new(type_.Namespace, type_.Name)(temp)

    @property
    @exception_bridge
    def assembly_analysis_cases_ready(
        self: "Self",
    ) -> "List[_3658.StraightBevelGearSetSteadyStateSynchronousResponseOnAShaft]":
        """List[mastapy.system_model.analyses_and_results.steady_state_synchronous_responses_on_a_shaft.StraightBevelGearSetSteadyStateSynchronousResponseOnAShaft]

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "AssemblyAnalysisCasesReady")

        if temp is None:
            return None

        value = conversion.pn_to_mp_objects_in_list(temp)

        if value is None:
            return None

        return value

    @property
    @exception_bridge
    def straight_bevel_gears_compound_steady_state_synchronous_response_on_a_shaft(
        self: "Self",
    ) -> "List[_3788.StraightBevelGearCompoundSteadyStateSynchronousResponseOnAShaft]":
        """List[mastapy.system_model.analyses_and_results.steady_state_synchronous_responses_on_a_shaft.compound.StraightBevelGearCompoundSteadyStateSynchronousResponseOnAShaft]

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(
            self.wrapped,
            "StraightBevelGearsCompoundSteadyStateSynchronousResponseOnAShaft",
        )

        if temp is None:
            return None

        value = conversion.pn_to_mp_objects_in_list(temp)

        if value is None:
            return None

        return value

    @property
    @exception_bridge
    def straight_bevel_meshes_compound_steady_state_synchronous_response_on_a_shaft(
        self: "Self",
    ) -> "List[_3789.StraightBevelGearMeshCompoundSteadyStateSynchronousResponseOnAShaft]":
        """List[mastapy.system_model.analyses_and_results.steady_state_synchronous_responses_on_a_shaft.compound.StraightBevelGearMeshCompoundSteadyStateSynchronousResponseOnAShaft]

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(
            self.wrapped,
            "StraightBevelMeshesCompoundSteadyStateSynchronousResponseOnAShaft",
        )

        if temp is None:
            return None

        value = conversion.pn_to_mp_objects_in_list(temp)

        if value is None:
            return None

        return value

    @property
    @exception_bridge
    def assembly_analysis_cases(
        self: "Self",
    ) -> "List[_3658.StraightBevelGearSetSteadyStateSynchronousResponseOnAShaft]":
        """List[mastapy.system_model.analyses_and_results.steady_state_synchronous_responses_on_a_shaft.StraightBevelGearSetSteadyStateSynchronousResponseOnAShaft]

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "AssemblyAnalysisCases")

        if temp is None:
            return None

        value = conversion.pn_to_mp_objects_in_list(temp)

        if value is None:
            return None

        return value

    @property
    def cast_to(
        self: "Self",
    ) -> "_Cast_StraightBevelGearSetCompoundSteadyStateSynchronousResponseOnAShaft":
        """Cast to another type.

        Returns:
            _Cast_StraightBevelGearSetCompoundSteadyStateSynchronousResponseOnAShaft
        """
        return _Cast_StraightBevelGearSetCompoundSteadyStateSynchronousResponseOnAShaft(
            self
        )
