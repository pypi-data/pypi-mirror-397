"""CouplingHalfPowerFlow"""

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
from mastapy._private.system_model.analyses_and_results.power_flows import _4427

_COUPLING_HALF_POWER_FLOW = python_net_import(
    "SMT.MastaAPI.SystemModel.AnalysesAndResults.PowerFlows", "CouplingHalfPowerFlow"
)

if TYPE_CHECKING:
    from typing import Any, Type, TypeVar

    from mastapy._private.system_model.analyses_and_results import _2943, _2945, _2949
    from mastapy._private.system_model.analyses_and_results.analysis_cases import (
        _7941,
        _7944,
    )
    from mastapy._private.system_model.analyses_and_results.power_flows import (
        _4367,
        _4370,
        _4372,
        _4387,
        _4429,
        _4431,
        _4440,
        _4445,
        _4455,
        _4465,
        _4466,
        _4468,
        _4472,
        _4473,
    )
    from mastapy._private.system_model.part_model.couplings import _2868

    Self = TypeVar("Self", bound="CouplingHalfPowerFlow")
    CastSelf = TypeVar(
        "CastSelf", bound="CouplingHalfPowerFlow._Cast_CouplingHalfPowerFlow"
    )


__docformat__ = "restructuredtext en"
__all__ = ("CouplingHalfPowerFlow",)


@extended_dataclass(frozen=True, slots=True, weakref_slot=True)
class _Cast_CouplingHalfPowerFlow:
    """Special nested class for casting CouplingHalfPowerFlow to subclasses."""

    __parent__: "CouplingHalfPowerFlow"

    @property
    def mountable_component_power_flow(
        self: "CastSelf",
    ) -> "_4427.MountableComponentPowerFlow":
        return self.__parent__._cast(_4427.MountableComponentPowerFlow)

    @property
    def component_power_flow(self: "CastSelf") -> "_4370.ComponentPowerFlow":
        from mastapy._private.system_model.analyses_and_results.power_flows import _4370

        return self.__parent__._cast(_4370.ComponentPowerFlow)

    @property
    def part_power_flow(self: "CastSelf") -> "_4429.PartPowerFlow":
        from mastapy._private.system_model.analyses_and_results.power_flows import _4429

        return self.__parent__._cast(_4429.PartPowerFlow)

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
    def clutch_half_power_flow(self: "CastSelf") -> "_4367.ClutchHalfPowerFlow":
        from mastapy._private.system_model.analyses_and_results.power_flows import _4367

        return self.__parent__._cast(_4367.ClutchHalfPowerFlow)

    @property
    def concept_coupling_half_power_flow(
        self: "CastSelf",
    ) -> "_4372.ConceptCouplingHalfPowerFlow":
        from mastapy._private.system_model.analyses_and_results.power_flows import _4372

        return self.__parent__._cast(_4372.ConceptCouplingHalfPowerFlow)

    @property
    def cvt_pulley_power_flow(self: "CastSelf") -> "_4387.CVTPulleyPowerFlow":
        from mastapy._private.system_model.analyses_and_results.power_flows import _4387

        return self.__parent__._cast(_4387.CVTPulleyPowerFlow)

    @property
    def part_to_part_shear_coupling_half_power_flow(
        self: "CastSelf",
    ) -> "_4431.PartToPartShearCouplingHalfPowerFlow":
        from mastapy._private.system_model.analyses_and_results.power_flows import _4431

        return self.__parent__._cast(_4431.PartToPartShearCouplingHalfPowerFlow)

    @property
    def pulley_power_flow(self: "CastSelf") -> "_4440.PulleyPowerFlow":
        from mastapy._private.system_model.analyses_and_results.power_flows import _4440

        return self.__parent__._cast(_4440.PulleyPowerFlow)

    @property
    def rolling_ring_power_flow(self: "CastSelf") -> "_4445.RollingRingPowerFlow":
        from mastapy._private.system_model.analyses_and_results.power_flows import _4445

        return self.__parent__._cast(_4445.RollingRingPowerFlow)

    @property
    def spring_damper_half_power_flow(
        self: "CastSelf",
    ) -> "_4455.SpringDamperHalfPowerFlow":
        from mastapy._private.system_model.analyses_and_results.power_flows import _4455

        return self.__parent__._cast(_4455.SpringDamperHalfPowerFlow)

    @property
    def synchroniser_half_power_flow(
        self: "CastSelf",
    ) -> "_4465.SynchroniserHalfPowerFlow":
        from mastapy._private.system_model.analyses_and_results.power_flows import _4465

        return self.__parent__._cast(_4465.SynchroniserHalfPowerFlow)

    @property
    def synchroniser_part_power_flow(
        self: "CastSelf",
    ) -> "_4466.SynchroniserPartPowerFlow":
        from mastapy._private.system_model.analyses_and_results.power_flows import _4466

        return self.__parent__._cast(_4466.SynchroniserPartPowerFlow)

    @property
    def synchroniser_sleeve_power_flow(
        self: "CastSelf",
    ) -> "_4468.SynchroniserSleevePowerFlow":
        from mastapy._private.system_model.analyses_and_results.power_flows import _4468

        return self.__parent__._cast(_4468.SynchroniserSleevePowerFlow)

    @property
    def torque_converter_pump_power_flow(
        self: "CastSelf",
    ) -> "_4472.TorqueConverterPumpPowerFlow":
        from mastapy._private.system_model.analyses_and_results.power_flows import _4472

        return self.__parent__._cast(_4472.TorqueConverterPumpPowerFlow)

    @property
    def torque_converter_turbine_power_flow(
        self: "CastSelf",
    ) -> "_4473.TorqueConverterTurbinePowerFlow":
        from mastapy._private.system_model.analyses_and_results.power_flows import _4473

        return self.__parent__._cast(_4473.TorqueConverterTurbinePowerFlow)

    @property
    def coupling_half_power_flow(self: "CastSelf") -> "CouplingHalfPowerFlow":
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
class CouplingHalfPowerFlow(_4427.MountableComponentPowerFlow):
    """CouplingHalfPowerFlow

    This is a mastapy class.
    """

    TYPE: ClassVar["Type"] = _COUPLING_HALF_POWER_FLOW

    wrapped: "Any"

    def __post_init__(self: "Self") -> None:
        """Override of the post initialisation magic method."""
        if not hasattr(self.wrapped, "reference_count"):
            self.wrapped.reference_count = 0

        self.wrapped.reference_count += 1

    @property
    @exception_bridge
    def component_design(self: "Self") -> "_2868.CouplingHalf":
        """mastapy.system_model.part_model.couplings.CouplingHalf

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "ComponentDesign")

        if temp is None:
            return None

        type_ = temp.GetType()
        return constructor.new(type_.Namespace, type_.Name)(temp)

    @property
    def cast_to(self: "Self") -> "_Cast_CouplingHalfPowerFlow":
        """Cast to another type.

        Returns:
            _Cast_CouplingHalfPowerFlow
        """
        return _Cast_CouplingHalfPowerFlow(self)
