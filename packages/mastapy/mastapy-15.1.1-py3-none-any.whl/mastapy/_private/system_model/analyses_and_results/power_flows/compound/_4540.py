"""GearCompoundPowerFlow"""

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
from mastapy._private.system_model.analyses_and_results.power_flows.compound import (
    _4561,
)

_GEAR_COMPOUND_POWER_FLOW = python_net_import(
    "SMT.MastaAPI.SystemModel.AnalysesAndResults.PowerFlows.Compound",
    "GearCompoundPowerFlow",
)

if TYPE_CHECKING:
    from typing import Any, List, Type, TypeVar

    from mastapy._private.gears.rating import _470
    from mastapy._private.system_model.analyses_and_results import _2943
    from mastapy._private.system_model.analyses_and_results.analysis_cases import (
        _7939,
        _7942,
    )
    from mastapy._private.system_model.analyses_and_results.power_flows import _4407
    from mastapy._private.system_model.analyses_and_results.power_flows.compound import (
        _4486,
        _4493,
        _4496,
        _4497,
        _4498,
        _4507,
        _4511,
        _4514,
        _4529,
        _4532,
        _4535,
        _4544,
        _4548,
        _4551,
        _4554,
        _4563,
        _4583,
        _4589,
        _4592,
        _4595,
        _4596,
        _4607,
        _4610,
    )

    Self = TypeVar("Self", bound="GearCompoundPowerFlow")
    CastSelf = TypeVar(
        "CastSelf", bound="GearCompoundPowerFlow._Cast_GearCompoundPowerFlow"
    )


__docformat__ = "restructuredtext en"
__all__ = ("GearCompoundPowerFlow",)


@extended_dataclass(frozen=True, slots=True, weakref_slot=True)
class _Cast_GearCompoundPowerFlow:
    """Special nested class for casting GearCompoundPowerFlow to subclasses."""

    __parent__: "GearCompoundPowerFlow"

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
    def agma_gleason_conical_gear_compound_power_flow(
        self: "CastSelf",
    ) -> "_4486.AGMAGleasonConicalGearCompoundPowerFlow":
        from mastapy._private.system_model.analyses_and_results.power_flows.compound import (
            _4486,
        )

        return self.__parent__._cast(_4486.AGMAGleasonConicalGearCompoundPowerFlow)

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
    def concept_gear_compound_power_flow(
        self: "CastSelf",
    ) -> "_4511.ConceptGearCompoundPowerFlow":
        from mastapy._private.system_model.analyses_and_results.power_flows.compound import (
            _4511,
        )

        return self.__parent__._cast(_4511.ConceptGearCompoundPowerFlow)

    @property
    def conical_gear_compound_power_flow(
        self: "CastSelf",
    ) -> "_4514.ConicalGearCompoundPowerFlow":
        from mastapy._private.system_model.analyses_and_results.power_flows.compound import (
            _4514,
        )

        return self.__parent__._cast(_4514.ConicalGearCompoundPowerFlow)

    @property
    def cylindrical_gear_compound_power_flow(
        self: "CastSelf",
    ) -> "_4529.CylindricalGearCompoundPowerFlow":
        from mastapy._private.system_model.analyses_and_results.power_flows.compound import (
            _4529,
        )

        return self.__parent__._cast(_4529.CylindricalGearCompoundPowerFlow)

    @property
    def cylindrical_planet_gear_compound_power_flow(
        self: "CastSelf",
    ) -> "_4532.CylindricalPlanetGearCompoundPowerFlow":
        from mastapy._private.system_model.analyses_and_results.power_flows.compound import (
            _4532,
        )

        return self.__parent__._cast(_4532.CylindricalPlanetGearCompoundPowerFlow)

    @property
    def face_gear_compound_power_flow(
        self: "CastSelf",
    ) -> "_4535.FaceGearCompoundPowerFlow":
        from mastapy._private.system_model.analyses_and_results.power_flows.compound import (
            _4535,
        )

        return self.__parent__._cast(_4535.FaceGearCompoundPowerFlow)

    @property
    def hypoid_gear_compound_power_flow(
        self: "CastSelf",
    ) -> "_4544.HypoidGearCompoundPowerFlow":
        from mastapy._private.system_model.analyses_and_results.power_flows.compound import (
            _4544,
        )

        return self.__parent__._cast(_4544.HypoidGearCompoundPowerFlow)

    @property
    def klingelnberg_cyclo_palloid_conical_gear_compound_power_flow(
        self: "CastSelf",
    ) -> "_4548.KlingelnbergCycloPalloidConicalGearCompoundPowerFlow":
        from mastapy._private.system_model.analyses_and_results.power_flows.compound import (
            _4548,
        )

        return self.__parent__._cast(
            _4548.KlingelnbergCycloPalloidConicalGearCompoundPowerFlow
        )

    @property
    def klingelnberg_cyclo_palloid_hypoid_gear_compound_power_flow(
        self: "CastSelf",
    ) -> "_4551.KlingelnbergCycloPalloidHypoidGearCompoundPowerFlow":
        from mastapy._private.system_model.analyses_and_results.power_flows.compound import (
            _4551,
        )

        return self.__parent__._cast(
            _4551.KlingelnbergCycloPalloidHypoidGearCompoundPowerFlow
        )

    @property
    def klingelnberg_cyclo_palloid_spiral_bevel_gear_compound_power_flow(
        self: "CastSelf",
    ) -> "_4554.KlingelnbergCycloPalloidSpiralBevelGearCompoundPowerFlow":
        from mastapy._private.system_model.analyses_and_results.power_flows.compound import (
            _4554,
        )

        return self.__parent__._cast(
            _4554.KlingelnbergCycloPalloidSpiralBevelGearCompoundPowerFlow
        )

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
    def worm_gear_compound_power_flow(
        self: "CastSelf",
    ) -> "_4607.WormGearCompoundPowerFlow":
        from mastapy._private.system_model.analyses_and_results.power_flows.compound import (
            _4607,
        )

        return self.__parent__._cast(_4607.WormGearCompoundPowerFlow)

    @property
    def zerol_bevel_gear_compound_power_flow(
        self: "CastSelf",
    ) -> "_4610.ZerolBevelGearCompoundPowerFlow":
        from mastapy._private.system_model.analyses_and_results.power_flows.compound import (
            _4610,
        )

        return self.__parent__._cast(_4610.ZerolBevelGearCompoundPowerFlow)

    @property
    def gear_compound_power_flow(self: "CastSelf") -> "GearCompoundPowerFlow":
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
class GearCompoundPowerFlow(_4561.MountableComponentCompoundPowerFlow):
    """GearCompoundPowerFlow

    This is a mastapy class.
    """

    TYPE: ClassVar["Type"] = _GEAR_COMPOUND_POWER_FLOW

    wrapped: "Any"

    def __post_init__(self: "Self") -> None:
        """Override of the post initialisation magic method."""
        if not hasattr(self.wrapped, "reference_count"):
            self.wrapped.reference_count = 0

        self.wrapped.reference_count += 1

    @property
    @exception_bridge
    def gear_duty_cycle_rating(self: "Self") -> "_470.GearDutyCycleRating":
        """mastapy.gears.rating.GearDutyCycleRating

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "GearDutyCycleRating")

        if temp is None:
            return None

        type_ = temp.GetType()
        return constructor.new(type_.Namespace, type_.Name)(temp)

    @property
    @exception_bridge
    def component_analysis_cases(self: "Self") -> "List[_4407.GearPowerFlow]":
        """List[mastapy.system_model.analyses_and_results.power_flows.GearPowerFlow]

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
    def component_analysis_cases_ready(self: "Self") -> "List[_4407.GearPowerFlow]":
        """List[mastapy.system_model.analyses_and_results.power_flows.GearPowerFlow]

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
    def cast_to(self: "Self") -> "_Cast_GearCompoundPowerFlow":
        """Cast to another type.

        Returns:
            _Cast_GearCompoundPowerFlow
        """
        return _Cast_GearCompoundPowerFlow(self)
