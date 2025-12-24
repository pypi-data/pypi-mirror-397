"""AbstractShaftOrHousingCompoundModalAnalysisAtASpeed"""

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
from mastapy._private.system_model.analyses_and_results.modal_analyses_at_a_speed.compound import (
    _5605,
)

_ABSTRACT_SHAFT_OR_HOUSING_COMPOUND_MODAL_ANALYSIS_AT_A_SPEED = python_net_import(
    "SMT.MastaAPI.SystemModel.AnalysesAndResults.ModalAnalysesAtASpeed.Compound",
    "AbstractShaftOrHousingCompoundModalAnalysisAtASpeed",
)

if TYPE_CHECKING:
    from typing import Any, List, Type, TypeVar

    from mastapy._private.system_model.analyses_and_results import _2943
    from mastapy._private.system_model.analyses_and_results.analysis_cases import (
        _7939,
        _7942,
    )
    from mastapy._private.system_model.analyses_and_results.modal_analyses_at_a_speed import (
        _5450,
    )
    from mastapy._private.system_model.analyses_and_results.modal_analyses_at_a_speed.compound import (
        _5581,
        _5625,
        _5636,
        _5661,
        _5677,
    )

    Self = TypeVar("Self", bound="AbstractShaftOrHousingCompoundModalAnalysisAtASpeed")
    CastSelf = TypeVar(
        "CastSelf",
        bound="AbstractShaftOrHousingCompoundModalAnalysisAtASpeed._Cast_AbstractShaftOrHousingCompoundModalAnalysisAtASpeed",
    )


__docformat__ = "restructuredtext en"
__all__ = ("AbstractShaftOrHousingCompoundModalAnalysisAtASpeed",)


@extended_dataclass(frozen=True, slots=True, weakref_slot=True)
class _Cast_AbstractShaftOrHousingCompoundModalAnalysisAtASpeed:
    """Special nested class for casting AbstractShaftOrHousingCompoundModalAnalysisAtASpeed to subclasses."""

    __parent__: "AbstractShaftOrHousingCompoundModalAnalysisAtASpeed"

    @property
    def component_compound_modal_analysis_at_a_speed(
        self: "CastSelf",
    ) -> "_5605.ComponentCompoundModalAnalysisAtASpeed":
        return self.__parent__._cast(_5605.ComponentCompoundModalAnalysisAtASpeed)

    @property
    def part_compound_modal_analysis_at_a_speed(
        self: "CastSelf",
    ) -> "_5661.PartCompoundModalAnalysisAtASpeed":
        from mastapy._private.system_model.analyses_and_results.modal_analyses_at_a_speed.compound import (
            _5661,
        )

        return self.__parent__._cast(_5661.PartCompoundModalAnalysisAtASpeed)

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
    def abstract_shaft_compound_modal_analysis_at_a_speed(
        self: "CastSelf",
    ) -> "_5581.AbstractShaftCompoundModalAnalysisAtASpeed":
        from mastapy._private.system_model.analyses_and_results.modal_analyses_at_a_speed.compound import (
            _5581,
        )

        return self.__parent__._cast(_5581.AbstractShaftCompoundModalAnalysisAtASpeed)

    @property
    def cycloidal_disc_compound_modal_analysis_at_a_speed(
        self: "CastSelf",
    ) -> "_5625.CycloidalDiscCompoundModalAnalysisAtASpeed":
        from mastapy._private.system_model.analyses_and_results.modal_analyses_at_a_speed.compound import (
            _5625,
        )

        return self.__parent__._cast(_5625.CycloidalDiscCompoundModalAnalysisAtASpeed)

    @property
    def fe_part_compound_modal_analysis_at_a_speed(
        self: "CastSelf",
    ) -> "_5636.FEPartCompoundModalAnalysisAtASpeed":
        from mastapy._private.system_model.analyses_and_results.modal_analyses_at_a_speed.compound import (
            _5636,
        )

        return self.__parent__._cast(_5636.FEPartCompoundModalAnalysisAtASpeed)

    @property
    def shaft_compound_modal_analysis_at_a_speed(
        self: "CastSelf",
    ) -> "_5677.ShaftCompoundModalAnalysisAtASpeed":
        from mastapy._private.system_model.analyses_and_results.modal_analyses_at_a_speed.compound import (
            _5677,
        )

        return self.__parent__._cast(_5677.ShaftCompoundModalAnalysisAtASpeed)

    @property
    def abstract_shaft_or_housing_compound_modal_analysis_at_a_speed(
        self: "CastSelf",
    ) -> "AbstractShaftOrHousingCompoundModalAnalysisAtASpeed":
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
class AbstractShaftOrHousingCompoundModalAnalysisAtASpeed(
    _5605.ComponentCompoundModalAnalysisAtASpeed
):
    """AbstractShaftOrHousingCompoundModalAnalysisAtASpeed

    This is a mastapy class.
    """

    TYPE: ClassVar["Type"] = (
        _ABSTRACT_SHAFT_OR_HOUSING_COMPOUND_MODAL_ANALYSIS_AT_A_SPEED
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
    ) -> "List[_5450.AbstractShaftOrHousingModalAnalysisAtASpeed]":
        """List[mastapy.system_model.analyses_and_results.modal_analyses_at_a_speed.AbstractShaftOrHousingModalAnalysisAtASpeed]

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
    ) -> "List[_5450.AbstractShaftOrHousingModalAnalysisAtASpeed]":
        """List[mastapy.system_model.analyses_and_results.modal_analyses_at_a_speed.AbstractShaftOrHousingModalAnalysisAtASpeed]

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
    ) -> "_Cast_AbstractShaftOrHousingCompoundModalAnalysisAtASpeed":
        """Cast to another type.

        Returns:
            _Cast_AbstractShaftOrHousingCompoundModalAnalysisAtASpeed
        """
        return _Cast_AbstractShaftOrHousingCompoundModalAnalysisAtASpeed(self)
