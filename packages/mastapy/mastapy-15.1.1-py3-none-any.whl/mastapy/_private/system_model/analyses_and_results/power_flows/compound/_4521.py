"""CouplingHalfCompoundPowerFlow"""

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

_COUPLING_HALF_COMPOUND_POWER_FLOW = python_net_import(
    "SMT.MastaAPI.SystemModel.AnalysesAndResults.PowerFlows.Compound",
    "CouplingHalfCompoundPowerFlow",
)

if TYPE_CHECKING:
    from typing import Any, List, Type, TypeVar

    from mastapy._private.system_model.analyses_and_results import _2943
    from mastapy._private.system_model.analyses_and_results.analysis_cases import (
        _7939,
        _7942,
    )
    from mastapy._private.system_model.analyses_and_results.power_flows import _4383
    from mastapy._private.system_model.analyses_and_results.power_flows.compound import (
        _4505,
        _4507,
        _4510,
        _4524,
        _4563,
        _4566,
        _4572,
        _4576,
        _4588,
        _4598,
        _4599,
        _4600,
        _4603,
        _4604,
    )

    Self = TypeVar("Self", bound="CouplingHalfCompoundPowerFlow")
    CastSelf = TypeVar(
        "CastSelf",
        bound="CouplingHalfCompoundPowerFlow._Cast_CouplingHalfCompoundPowerFlow",
    )


__docformat__ = "restructuredtext en"
__all__ = ("CouplingHalfCompoundPowerFlow",)


@extended_dataclass(frozen=True, slots=True, weakref_slot=True)
class _Cast_CouplingHalfCompoundPowerFlow:
    """Special nested class for casting CouplingHalfCompoundPowerFlow to subclasses."""

    __parent__: "CouplingHalfCompoundPowerFlow"

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
    def clutch_half_compound_power_flow(
        self: "CastSelf",
    ) -> "_4505.ClutchHalfCompoundPowerFlow":
        from mastapy._private.system_model.analyses_and_results.power_flows.compound import (
            _4505,
        )

        return self.__parent__._cast(_4505.ClutchHalfCompoundPowerFlow)

    @property
    def concept_coupling_half_compound_power_flow(
        self: "CastSelf",
    ) -> "_4510.ConceptCouplingHalfCompoundPowerFlow":
        from mastapy._private.system_model.analyses_and_results.power_flows.compound import (
            _4510,
        )

        return self.__parent__._cast(_4510.ConceptCouplingHalfCompoundPowerFlow)

    @property
    def cvt_pulley_compound_power_flow(
        self: "CastSelf",
    ) -> "_4524.CVTPulleyCompoundPowerFlow":
        from mastapy._private.system_model.analyses_and_results.power_flows.compound import (
            _4524,
        )

        return self.__parent__._cast(_4524.CVTPulleyCompoundPowerFlow)

    @property
    def part_to_part_shear_coupling_half_compound_power_flow(
        self: "CastSelf",
    ) -> "_4566.PartToPartShearCouplingHalfCompoundPowerFlow":
        from mastapy._private.system_model.analyses_and_results.power_flows.compound import (
            _4566,
        )

        return self.__parent__._cast(_4566.PartToPartShearCouplingHalfCompoundPowerFlow)

    @property
    def pulley_compound_power_flow(self: "CastSelf") -> "_4572.PulleyCompoundPowerFlow":
        from mastapy._private.system_model.analyses_and_results.power_flows.compound import (
            _4572,
        )

        return self.__parent__._cast(_4572.PulleyCompoundPowerFlow)

    @property
    def rolling_ring_compound_power_flow(
        self: "CastSelf",
    ) -> "_4576.RollingRingCompoundPowerFlow":
        from mastapy._private.system_model.analyses_and_results.power_flows.compound import (
            _4576,
        )

        return self.__parent__._cast(_4576.RollingRingCompoundPowerFlow)

    @property
    def spring_damper_half_compound_power_flow(
        self: "CastSelf",
    ) -> "_4588.SpringDamperHalfCompoundPowerFlow":
        from mastapy._private.system_model.analyses_and_results.power_flows.compound import (
            _4588,
        )

        return self.__parent__._cast(_4588.SpringDamperHalfCompoundPowerFlow)

    @property
    def synchroniser_half_compound_power_flow(
        self: "CastSelf",
    ) -> "_4598.SynchroniserHalfCompoundPowerFlow":
        from mastapy._private.system_model.analyses_and_results.power_flows.compound import (
            _4598,
        )

        return self.__parent__._cast(_4598.SynchroniserHalfCompoundPowerFlow)

    @property
    def synchroniser_part_compound_power_flow(
        self: "CastSelf",
    ) -> "_4599.SynchroniserPartCompoundPowerFlow":
        from mastapy._private.system_model.analyses_and_results.power_flows.compound import (
            _4599,
        )

        return self.__parent__._cast(_4599.SynchroniserPartCompoundPowerFlow)

    @property
    def synchroniser_sleeve_compound_power_flow(
        self: "CastSelf",
    ) -> "_4600.SynchroniserSleeveCompoundPowerFlow":
        from mastapy._private.system_model.analyses_and_results.power_flows.compound import (
            _4600,
        )

        return self.__parent__._cast(_4600.SynchroniserSleeveCompoundPowerFlow)

    @property
    def torque_converter_pump_compound_power_flow(
        self: "CastSelf",
    ) -> "_4603.TorqueConverterPumpCompoundPowerFlow":
        from mastapy._private.system_model.analyses_and_results.power_flows.compound import (
            _4603,
        )

        return self.__parent__._cast(_4603.TorqueConverterPumpCompoundPowerFlow)

    @property
    def torque_converter_turbine_compound_power_flow(
        self: "CastSelf",
    ) -> "_4604.TorqueConverterTurbineCompoundPowerFlow":
        from mastapy._private.system_model.analyses_and_results.power_flows.compound import (
            _4604,
        )

        return self.__parent__._cast(_4604.TorqueConverterTurbineCompoundPowerFlow)

    @property
    def coupling_half_compound_power_flow(
        self: "CastSelf",
    ) -> "CouplingHalfCompoundPowerFlow":
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
class CouplingHalfCompoundPowerFlow(_4561.MountableComponentCompoundPowerFlow):
    """CouplingHalfCompoundPowerFlow

    This is a mastapy class.
    """

    TYPE: ClassVar["Type"] = _COUPLING_HALF_COMPOUND_POWER_FLOW

    wrapped: "Any"

    def __post_init__(self: "Self") -> None:
        """Override of the post initialisation magic method."""
        if not hasattr(self.wrapped, "reference_count"):
            self.wrapped.reference_count = 0

        self.wrapped.reference_count += 1

    @property
    @exception_bridge
    def component_analysis_cases(self: "Self") -> "List[_4383.CouplingHalfPowerFlow]":
        """List[mastapy.system_model.analyses_and_results.power_flows.CouplingHalfPowerFlow]

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
    ) -> "List[_4383.CouplingHalfPowerFlow]":
        """List[mastapy.system_model.analyses_and_results.power_flows.CouplingHalfPowerFlow]

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
    def cast_to(self: "Self") -> "_Cast_CouplingHalfCompoundPowerFlow":
        """Cast to another type.

        Returns:
            _Cast_CouplingHalfCompoundPowerFlow
        """
        return _Cast_CouplingHalfCompoundPowerFlow(self)
