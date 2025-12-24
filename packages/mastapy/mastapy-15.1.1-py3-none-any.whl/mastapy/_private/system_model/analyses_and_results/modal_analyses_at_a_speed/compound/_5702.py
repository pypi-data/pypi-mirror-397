"""TorqueConverterTurbineCompoundModalAnalysisAtASpeed"""

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
from mastapy._private.system_model.analyses_and_results.modal_analyses_at_a_speed.compound import (
    _5619,
)

_TORQUE_CONVERTER_TURBINE_COMPOUND_MODAL_ANALYSIS_AT_A_SPEED = python_net_import(
    "SMT.MastaAPI.SystemModel.AnalysesAndResults.ModalAnalysesAtASpeed.Compound",
    "TorqueConverterTurbineCompoundModalAnalysisAtASpeed",
)

if TYPE_CHECKING:
    from typing import Any, List, Type, TypeVar

    from mastapy._private.system_model.analyses_and_results import _2943
    from mastapy._private.system_model.analyses_and_results.analysis_cases import (
        _7939,
        _7942,
    )
    from mastapy._private.system_model.analyses_and_results.modal_analyses_at_a_speed import (
        _5571,
    )
    from mastapy._private.system_model.analyses_and_results.modal_analyses_at_a_speed.compound import (
        _5605,
        _5659,
        _5661,
    )
    from mastapy._private.system_model.part_model.couplings import _2900

    Self = TypeVar("Self", bound="TorqueConverterTurbineCompoundModalAnalysisAtASpeed")
    CastSelf = TypeVar(
        "CastSelf",
        bound="TorqueConverterTurbineCompoundModalAnalysisAtASpeed._Cast_TorqueConverterTurbineCompoundModalAnalysisAtASpeed",
    )


__docformat__ = "restructuredtext en"
__all__ = ("TorqueConverterTurbineCompoundModalAnalysisAtASpeed",)


@extended_dataclass(frozen=True, slots=True, weakref_slot=True)
class _Cast_TorqueConverterTurbineCompoundModalAnalysisAtASpeed:
    """Special nested class for casting TorqueConverterTurbineCompoundModalAnalysisAtASpeed to subclasses."""

    __parent__: "TorqueConverterTurbineCompoundModalAnalysisAtASpeed"

    @property
    def coupling_half_compound_modal_analysis_at_a_speed(
        self: "CastSelf",
    ) -> "_5619.CouplingHalfCompoundModalAnalysisAtASpeed":
        return self.__parent__._cast(_5619.CouplingHalfCompoundModalAnalysisAtASpeed)

    @property
    def mountable_component_compound_modal_analysis_at_a_speed(
        self: "CastSelf",
    ) -> "_5659.MountableComponentCompoundModalAnalysisAtASpeed":
        from mastapy._private.system_model.analyses_and_results.modal_analyses_at_a_speed.compound import (
            _5659,
        )

        return self.__parent__._cast(
            _5659.MountableComponentCompoundModalAnalysisAtASpeed
        )

    @property
    def component_compound_modal_analysis_at_a_speed(
        self: "CastSelf",
    ) -> "_5605.ComponentCompoundModalAnalysisAtASpeed":
        from mastapy._private.system_model.analyses_and_results.modal_analyses_at_a_speed.compound import (
            _5605,
        )

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
    def torque_converter_turbine_compound_modal_analysis_at_a_speed(
        self: "CastSelf",
    ) -> "TorqueConverterTurbineCompoundModalAnalysisAtASpeed":
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
class TorqueConverterTurbineCompoundModalAnalysisAtASpeed(
    _5619.CouplingHalfCompoundModalAnalysisAtASpeed
):
    """TorqueConverterTurbineCompoundModalAnalysisAtASpeed

    This is a mastapy class.
    """

    TYPE: ClassVar["Type"] = (
        _TORQUE_CONVERTER_TURBINE_COMPOUND_MODAL_ANALYSIS_AT_A_SPEED
    )

    wrapped: "Any"

    def __post_init__(self: "Self") -> None:
        """Override of the post initialisation magic method."""
        if not hasattr(self.wrapped, "reference_count"):
            self.wrapped.reference_count = 0

        self.wrapped.reference_count += 1

    @property
    @exception_bridge
    def component_design(self: "Self") -> "_2900.TorqueConverterTurbine":
        """mastapy.system_model.part_model.couplings.TorqueConverterTurbine

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
    def component_analysis_cases_ready(
        self: "Self",
    ) -> "List[_5571.TorqueConverterTurbineModalAnalysisAtASpeed]":
        """List[mastapy.system_model.analyses_and_results.modal_analyses_at_a_speed.TorqueConverterTurbineModalAnalysisAtASpeed]

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
    @exception_bridge
    def component_analysis_cases(
        self: "Self",
    ) -> "List[_5571.TorqueConverterTurbineModalAnalysisAtASpeed]":
        """List[mastapy.system_model.analyses_and_results.modal_analyses_at_a_speed.TorqueConverterTurbineModalAnalysisAtASpeed]

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
    def cast_to(
        self: "Self",
    ) -> "_Cast_TorqueConverterTurbineCompoundModalAnalysisAtASpeed":
        """Cast to another type.

        Returns:
            _Cast_TorqueConverterTurbineCompoundModalAnalysisAtASpeed
        """
        return _Cast_TorqueConverterTurbineCompoundModalAnalysisAtASpeed(self)
