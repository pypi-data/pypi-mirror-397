"""CouplingConnectionCompoundPowerFlow"""

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
    _4547,
)

_COUPLING_CONNECTION_COMPOUND_POWER_FLOW = python_net_import(
    "SMT.MastaAPI.SystemModel.AnalysesAndResults.PowerFlows.Compound",
    "CouplingConnectionCompoundPowerFlow",
)

if TYPE_CHECKING:
    from typing import Any, List, Type, TypeVar

    from mastapy._private.system_model.analyses_and_results import _2943
    from mastapy._private.system_model.analyses_and_results.analysis_cases import (
        _7935,
        _7939,
    )
    from mastapy._private.system_model.analyses_and_results.power_flows import _4382
    from mastapy._private.system_model.analyses_and_results.power_flows.compound import (
        _4504,
        _4509,
        _4517,
        _4565,
        _4587,
        _4602,
    )

    Self = TypeVar("Self", bound="CouplingConnectionCompoundPowerFlow")
    CastSelf = TypeVar(
        "CastSelf",
        bound="CouplingConnectionCompoundPowerFlow._Cast_CouplingConnectionCompoundPowerFlow",
    )


__docformat__ = "restructuredtext en"
__all__ = ("CouplingConnectionCompoundPowerFlow",)


@extended_dataclass(frozen=True, slots=True, weakref_slot=True)
class _Cast_CouplingConnectionCompoundPowerFlow:
    """Special nested class for casting CouplingConnectionCompoundPowerFlow to subclasses."""

    __parent__: "CouplingConnectionCompoundPowerFlow"

    @property
    def inter_mountable_component_connection_compound_power_flow(
        self: "CastSelf",
    ) -> "_4547.InterMountableComponentConnectionCompoundPowerFlow":
        return self.__parent__._cast(
            _4547.InterMountableComponentConnectionCompoundPowerFlow
        )

    @property
    def connection_compound_power_flow(
        self: "CastSelf",
    ) -> "_4517.ConnectionCompoundPowerFlow":
        from mastapy._private.system_model.analyses_and_results.power_flows.compound import (
            _4517,
        )

        return self.__parent__._cast(_4517.ConnectionCompoundPowerFlow)

    @property
    def connection_compound_analysis(
        self: "CastSelf",
    ) -> "_7935.ConnectionCompoundAnalysis":
        from mastapy._private.system_model.analyses_and_results.analysis_cases import (
            _7935,
        )

        return self.__parent__._cast(_7935.ConnectionCompoundAnalysis)

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
    def clutch_connection_compound_power_flow(
        self: "CastSelf",
    ) -> "_4504.ClutchConnectionCompoundPowerFlow":
        from mastapy._private.system_model.analyses_and_results.power_flows.compound import (
            _4504,
        )

        return self.__parent__._cast(_4504.ClutchConnectionCompoundPowerFlow)

    @property
    def concept_coupling_connection_compound_power_flow(
        self: "CastSelf",
    ) -> "_4509.ConceptCouplingConnectionCompoundPowerFlow":
        from mastapy._private.system_model.analyses_and_results.power_flows.compound import (
            _4509,
        )

        return self.__parent__._cast(_4509.ConceptCouplingConnectionCompoundPowerFlow)

    @property
    def part_to_part_shear_coupling_connection_compound_power_flow(
        self: "CastSelf",
    ) -> "_4565.PartToPartShearCouplingConnectionCompoundPowerFlow":
        from mastapy._private.system_model.analyses_and_results.power_flows.compound import (
            _4565,
        )

        return self.__parent__._cast(
            _4565.PartToPartShearCouplingConnectionCompoundPowerFlow
        )

    @property
    def spring_damper_connection_compound_power_flow(
        self: "CastSelf",
    ) -> "_4587.SpringDamperConnectionCompoundPowerFlow":
        from mastapy._private.system_model.analyses_and_results.power_flows.compound import (
            _4587,
        )

        return self.__parent__._cast(_4587.SpringDamperConnectionCompoundPowerFlow)

    @property
    def torque_converter_connection_compound_power_flow(
        self: "CastSelf",
    ) -> "_4602.TorqueConverterConnectionCompoundPowerFlow":
        from mastapy._private.system_model.analyses_and_results.power_flows.compound import (
            _4602,
        )

        return self.__parent__._cast(_4602.TorqueConverterConnectionCompoundPowerFlow)

    @property
    def coupling_connection_compound_power_flow(
        self: "CastSelf",
    ) -> "CouplingConnectionCompoundPowerFlow":
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
class CouplingConnectionCompoundPowerFlow(
    _4547.InterMountableComponentConnectionCompoundPowerFlow
):
    """CouplingConnectionCompoundPowerFlow

    This is a mastapy class.
    """

    TYPE: ClassVar["Type"] = _COUPLING_CONNECTION_COMPOUND_POWER_FLOW

    wrapped: "Any"

    def __post_init__(self: "Self") -> None:
        """Override of the post initialisation magic method."""
        if not hasattr(self.wrapped, "reference_count"):
            self.wrapped.reference_count = 0

        self.wrapped.reference_count += 1

    @property
    @exception_bridge
    def connection_analysis_cases(
        self: "Self",
    ) -> "List[_4382.CouplingConnectionPowerFlow]":
        """List[mastapy.system_model.analyses_and_results.power_flows.CouplingConnectionPowerFlow]

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "ConnectionAnalysisCases")

        if temp is None:
            return None

        value = conversion.pn_to_mp_objects_in_list(temp)

        if value is None:
            return None

        return value

    @property
    @exception_bridge
    def connection_analysis_cases_ready(
        self: "Self",
    ) -> "List[_4382.CouplingConnectionPowerFlow]":
        """List[mastapy.system_model.analyses_and_results.power_flows.CouplingConnectionPowerFlow]

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "ConnectionAnalysisCasesReady")

        if temp is None:
            return None

        value = conversion.pn_to_mp_objects_in_list(temp)

        if value is None:
            return None

        return value

    @property
    def cast_to(self: "Self") -> "_Cast_CouplingConnectionCompoundPowerFlow":
        """Cast to another type.

        Returns:
            _Cast_CouplingConnectionCompoundPowerFlow
        """
        return _Cast_CouplingConnectionCompoundPowerFlow(self)
