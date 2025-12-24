"""VirtualComponentCompoundPowerFlow"""

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
from mastapy._private.system_model.analyses_and_results.power_flows.compound import (
    _4561,
)

_VIRTUAL_COMPONENT_COMPOUND_POWER_FLOW = python_net_import(
    "SMT.MastaAPI.SystemModel.AnalysesAndResults.PowerFlows.Compound",
    "VirtualComponentCompoundPowerFlow",
)

if TYPE_CHECKING:
    from typing import Any, List, Type, TypeVar

    from mastapy._private.system_model.analyses_and_results import _2943
    from mastapy._private.system_model.analyses_and_results.analysis_cases import (
        _7939,
        _7942,
    )
    from mastapy._private.system_model.analyses_and_results.power_flows import _4475
    from mastapy._private.system_model.analyses_and_results.power_flows.compound import (
        _4507,
        _4557,
        _4558,
        _4563,
        _4570,
        _4571,
        _4605,
    )

    Self = TypeVar("Self", bound="VirtualComponentCompoundPowerFlow")
    CastSelf = TypeVar(
        "CastSelf",
        bound="VirtualComponentCompoundPowerFlow._Cast_VirtualComponentCompoundPowerFlow",
    )


__docformat__ = "restructuredtext en"
__all__ = ("VirtualComponentCompoundPowerFlow",)


@extended_dataclass(frozen=True, slots=True, weakref_slot=True)
class _Cast_VirtualComponentCompoundPowerFlow:
    """Special nested class for casting VirtualComponentCompoundPowerFlow to subclasses."""

    __parent__: "VirtualComponentCompoundPowerFlow"

    @property
    def mountable_component_compound_power_flow(
        self: "CastSelf",
    ) -> "_4561.MountableComponentCompoundPowerFlow":
        return self.__parent__._cast(_4561.MountableComponentCompoundPowerFlow)

    @property
    def component_compound_power_flow(
        self: "CastSelf",
    ) -> "_4507.ComponentCompoundPowerFlow":
        from mastapy._private.system_model.analyses_and_results.power_flows.compound import (
            _4507,
        )

        return self.__parent__._cast(_4507.ComponentCompoundPowerFlow)

    @property
    def part_compound_power_flow(self: "CastSelf") -> "_4563.PartCompoundPowerFlow":
        from mastapy._private.system_model.analyses_and_results.power_flows.compound import (
            _4563,
        )

        return self.__parent__._cast(_4563.PartCompoundPowerFlow)

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
    def mass_disc_compound_power_flow(
        self: "CastSelf",
    ) -> "_4557.MassDiscCompoundPowerFlow":
        from mastapy._private.system_model.analyses_and_results.power_flows.compound import (
            _4557,
        )

        return self.__parent__._cast(_4557.MassDiscCompoundPowerFlow)

    @property
    def measurement_component_compound_power_flow(
        self: "CastSelf",
    ) -> "_4558.MeasurementComponentCompoundPowerFlow":
        from mastapy._private.system_model.analyses_and_results.power_flows.compound import (
            _4558,
        )

        return self.__parent__._cast(_4558.MeasurementComponentCompoundPowerFlow)

    @property
    def point_load_compound_power_flow(
        self: "CastSelf",
    ) -> "_4570.PointLoadCompoundPowerFlow":
        from mastapy._private.system_model.analyses_and_results.power_flows.compound import (
            _4570,
        )

        return self.__parent__._cast(_4570.PointLoadCompoundPowerFlow)

    @property
    def power_load_compound_power_flow(
        self: "CastSelf",
    ) -> "_4571.PowerLoadCompoundPowerFlow":
        from mastapy._private.system_model.analyses_and_results.power_flows.compound import (
            _4571,
        )

        return self.__parent__._cast(_4571.PowerLoadCompoundPowerFlow)

    @property
    def unbalanced_mass_compound_power_flow(
        self: "CastSelf",
    ) -> "_4605.UnbalancedMassCompoundPowerFlow":
        from mastapy._private.system_model.analyses_and_results.power_flows.compound import (
            _4605,
        )

        return self.__parent__._cast(_4605.UnbalancedMassCompoundPowerFlow)

    @property
    def virtual_component_compound_power_flow(
        self: "CastSelf",
    ) -> "VirtualComponentCompoundPowerFlow":
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
class VirtualComponentCompoundPowerFlow(_4561.MountableComponentCompoundPowerFlow):
    """VirtualComponentCompoundPowerFlow

    This is a mastapy class.
    """

    TYPE: ClassVar["Type"] = _VIRTUAL_COMPONENT_COMPOUND_POWER_FLOW

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
    ) -> "List[_4475.VirtualComponentPowerFlow]":
        """List[mastapy.system_model.analyses_and_results.power_flows.VirtualComponentPowerFlow]

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
    ) -> "List[_4475.VirtualComponentPowerFlow]":
        """List[mastapy.system_model.analyses_and_results.power_flows.VirtualComponentPowerFlow]

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
    def cast_to(self: "Self") -> "_Cast_VirtualComponentCompoundPowerFlow":
        """Cast to another type.

        Returns:
            _Cast_VirtualComponentCompoundPowerFlow
        """
        return _Cast_VirtualComponentCompoundPowerFlow(self)
