"""AGMAGleasonConicalGearCompoundPowerFlow"""

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
    _4514,
)

_AGMA_GLEASON_CONICAL_GEAR_COMPOUND_POWER_FLOW = python_net_import(
    "SMT.MastaAPI.SystemModel.AnalysesAndResults.PowerFlows.Compound",
    "AGMAGleasonConicalGearCompoundPowerFlow",
)

if TYPE_CHECKING:
    from typing import Any, List, Type, TypeVar

    from mastapy._private.system_model.analyses_and_results import _2943
    from mastapy._private.system_model.analyses_and_results.analysis_cases import (
        _7939,
        _7942,
    )
    from mastapy._private.system_model.analyses_and_results.power_flows import _4350
    from mastapy._private.system_model.analyses_and_results.power_flows.compound import (
        _4493,
        _4496,
        _4497,
        _4498,
        _4507,
        _4540,
        _4544,
        _4561,
        _4563,
        _4583,
        _4589,
        _4592,
        _4595,
        _4596,
        _4610,
    )

    Self = TypeVar("Self", bound="AGMAGleasonConicalGearCompoundPowerFlow")
    CastSelf = TypeVar(
        "CastSelf",
        bound="AGMAGleasonConicalGearCompoundPowerFlow._Cast_AGMAGleasonConicalGearCompoundPowerFlow",
    )


__docformat__ = "restructuredtext en"
__all__ = ("AGMAGleasonConicalGearCompoundPowerFlow",)


@extended_dataclass(frozen=True, slots=True, weakref_slot=True)
class _Cast_AGMAGleasonConicalGearCompoundPowerFlow:
    """Special nested class for casting AGMAGleasonConicalGearCompoundPowerFlow to subclasses."""

    __parent__: "AGMAGleasonConicalGearCompoundPowerFlow"

    @property
    def conical_gear_compound_power_flow(
        self: "CastSelf",
    ) -> "_4514.ConicalGearCompoundPowerFlow":
        return self.__parent__._cast(_4514.ConicalGearCompoundPowerFlow)

    @property
    def gear_compound_power_flow(self: "CastSelf") -> "_4540.GearCompoundPowerFlow":
        from mastapy._private.system_model.analyses_and_results.power_flows.compound import (
            _4540,
        )

        return self.__parent__._cast(_4540.GearCompoundPowerFlow)

    @property
    def mountable_component_compound_power_flow(
        self: "CastSelf",
    ) -> "_4561.MountableComponentCompoundPowerFlow":
        from mastapy._private.system_model.analyses_and_results.power_flows.compound import (
            _4561,
        )

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
    def bevel_differential_gear_compound_power_flow(
        self: "CastSelf",
    ) -> "_4493.BevelDifferentialGearCompoundPowerFlow":
        from mastapy._private.system_model.analyses_and_results.power_flows.compound import (
            _4493,
        )

        return self.__parent__._cast(_4493.BevelDifferentialGearCompoundPowerFlow)

    @property
    def bevel_differential_planet_gear_compound_power_flow(
        self: "CastSelf",
    ) -> "_4496.BevelDifferentialPlanetGearCompoundPowerFlow":
        from mastapy._private.system_model.analyses_and_results.power_flows.compound import (
            _4496,
        )

        return self.__parent__._cast(_4496.BevelDifferentialPlanetGearCompoundPowerFlow)

    @property
    def bevel_differential_sun_gear_compound_power_flow(
        self: "CastSelf",
    ) -> "_4497.BevelDifferentialSunGearCompoundPowerFlow":
        from mastapy._private.system_model.analyses_and_results.power_flows.compound import (
            _4497,
        )

        return self.__parent__._cast(_4497.BevelDifferentialSunGearCompoundPowerFlow)

    @property
    def bevel_gear_compound_power_flow(
        self: "CastSelf",
    ) -> "_4498.BevelGearCompoundPowerFlow":
        from mastapy._private.system_model.analyses_and_results.power_flows.compound import (
            _4498,
        )

        return self.__parent__._cast(_4498.BevelGearCompoundPowerFlow)

    @property
    def hypoid_gear_compound_power_flow(
        self: "CastSelf",
    ) -> "_4544.HypoidGearCompoundPowerFlow":
        from mastapy._private.system_model.analyses_and_results.power_flows.compound import (
            _4544,
        )

        return self.__parent__._cast(_4544.HypoidGearCompoundPowerFlow)

    @property
    def spiral_bevel_gear_compound_power_flow(
        self: "CastSelf",
    ) -> "_4583.SpiralBevelGearCompoundPowerFlow":
        from mastapy._private.system_model.analyses_and_results.power_flows.compound import (
            _4583,
        )

        return self.__parent__._cast(_4583.SpiralBevelGearCompoundPowerFlow)

    @property
    def straight_bevel_diff_gear_compound_power_flow(
        self: "CastSelf",
    ) -> "_4589.StraightBevelDiffGearCompoundPowerFlow":
        from mastapy._private.system_model.analyses_and_results.power_flows.compound import (
            _4589,
        )

        return self.__parent__._cast(_4589.StraightBevelDiffGearCompoundPowerFlow)

    @property
    def straight_bevel_gear_compound_power_flow(
        self: "CastSelf",
    ) -> "_4592.StraightBevelGearCompoundPowerFlow":
        from mastapy._private.system_model.analyses_and_results.power_flows.compound import (
            _4592,
        )

        return self.__parent__._cast(_4592.StraightBevelGearCompoundPowerFlow)

    @property
    def straight_bevel_planet_gear_compound_power_flow(
        self: "CastSelf",
    ) -> "_4595.StraightBevelPlanetGearCompoundPowerFlow":
        from mastapy._private.system_model.analyses_and_results.power_flows.compound import (
            _4595,
        )

        return self.__parent__._cast(_4595.StraightBevelPlanetGearCompoundPowerFlow)

    @property
    def straight_bevel_sun_gear_compound_power_flow(
        self: "CastSelf",
    ) -> "_4596.StraightBevelSunGearCompoundPowerFlow":
        from mastapy._private.system_model.analyses_and_results.power_flows.compound import (
            _4596,
        )

        return self.__parent__._cast(_4596.StraightBevelSunGearCompoundPowerFlow)

    @property
    def zerol_bevel_gear_compound_power_flow(
        self: "CastSelf",
    ) -> "_4610.ZerolBevelGearCompoundPowerFlow":
        from mastapy._private.system_model.analyses_and_results.power_flows.compound import (
            _4610,
        )

        return self.__parent__._cast(_4610.ZerolBevelGearCompoundPowerFlow)

    @property
    def agma_gleason_conical_gear_compound_power_flow(
        self: "CastSelf",
    ) -> "AGMAGleasonConicalGearCompoundPowerFlow":
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
class AGMAGleasonConicalGearCompoundPowerFlow(_4514.ConicalGearCompoundPowerFlow):
    """AGMAGleasonConicalGearCompoundPowerFlow

    This is a mastapy class.
    """

    TYPE: ClassVar["Type"] = _AGMA_GLEASON_CONICAL_GEAR_COMPOUND_POWER_FLOW

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
    ) -> "List[_4350.AGMAGleasonConicalGearPowerFlow]":
        """List[mastapy.system_model.analyses_and_results.power_flows.AGMAGleasonConicalGearPowerFlow]

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
    ) -> "List[_4350.AGMAGleasonConicalGearPowerFlow]":
        """List[mastapy.system_model.analyses_and_results.power_flows.AGMAGleasonConicalGearPowerFlow]

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
    def cast_to(self: "Self") -> "_Cast_AGMAGleasonConicalGearCompoundPowerFlow":
        """Cast to another type.

        Returns:
            _Cast_AGMAGleasonConicalGearCompoundPowerFlow
        """
        return _Cast_AGMAGleasonConicalGearCompoundPowerFlow(self)
