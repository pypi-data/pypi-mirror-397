"""GearPowerFlow"""

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

_GEAR_POWER_FLOW = python_net_import(
    "SMT.MastaAPI.SystemModel.AnalysesAndResults.PowerFlows", "GearPowerFlow"
)

if TYPE_CHECKING:
    from typing import Any, Type, TypeVar

    from mastapy._private.system_model.analyses_and_results import _2943, _2945, _2949
    from mastapy._private.system_model.analyses_and_results.analysis_cases import (
        _7941,
        _7944,
    )
    from mastapy._private.system_model.analyses_and_results.power_flows import (
        _4350,
        _4357,
        _4359,
        _4360,
        _4362,
        _4370,
        _4375,
        _4378,
        _4394,
        _4396,
        _4400,
        _4411,
        _4415,
        _4418,
        _4421,
        _4429,
        _4452,
        _4458,
        _4461,
        _4463,
        _4464,
        _4477,
        _4480,
    )
    from mastapy._private.system_model.part_model.gears import _2811

    Self = TypeVar("Self", bound="GearPowerFlow")
    CastSelf = TypeVar("CastSelf", bound="GearPowerFlow._Cast_GearPowerFlow")


__docformat__ = "restructuredtext en"
__all__ = ("GearPowerFlow",)


@extended_dataclass(frozen=True, slots=True, weakref_slot=True)
class _Cast_GearPowerFlow:
    """Special nested class for casting GearPowerFlow to subclasses."""

    __parent__: "GearPowerFlow"

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
    def agma_gleason_conical_gear_power_flow(
        self: "CastSelf",
    ) -> "_4350.AGMAGleasonConicalGearPowerFlow":
        from mastapy._private.system_model.analyses_and_results.power_flows import _4350

        return self.__parent__._cast(_4350.AGMAGleasonConicalGearPowerFlow)

    @property
    def bevel_differential_gear_power_flow(
        self: "CastSelf",
    ) -> "_4357.BevelDifferentialGearPowerFlow":
        from mastapy._private.system_model.analyses_and_results.power_flows import _4357

        return self.__parent__._cast(_4357.BevelDifferentialGearPowerFlow)

    @property
    def bevel_differential_planet_gear_power_flow(
        self: "CastSelf",
    ) -> "_4359.BevelDifferentialPlanetGearPowerFlow":
        from mastapy._private.system_model.analyses_and_results.power_flows import _4359

        return self.__parent__._cast(_4359.BevelDifferentialPlanetGearPowerFlow)

    @property
    def bevel_differential_sun_gear_power_flow(
        self: "CastSelf",
    ) -> "_4360.BevelDifferentialSunGearPowerFlow":
        from mastapy._private.system_model.analyses_and_results.power_flows import _4360

        return self.__parent__._cast(_4360.BevelDifferentialSunGearPowerFlow)

    @property
    def bevel_gear_power_flow(self: "CastSelf") -> "_4362.BevelGearPowerFlow":
        from mastapy._private.system_model.analyses_and_results.power_flows import _4362

        return self.__parent__._cast(_4362.BevelGearPowerFlow)

    @property
    def concept_gear_power_flow(self: "CastSelf") -> "_4375.ConceptGearPowerFlow":
        from mastapy._private.system_model.analyses_and_results.power_flows import _4375

        return self.__parent__._cast(_4375.ConceptGearPowerFlow)

    @property
    def conical_gear_power_flow(self: "CastSelf") -> "_4378.ConicalGearPowerFlow":
        from mastapy._private.system_model.analyses_and_results.power_flows import _4378

        return self.__parent__._cast(_4378.ConicalGearPowerFlow)

    @property
    def cylindrical_gear_power_flow(
        self: "CastSelf",
    ) -> "_4394.CylindricalGearPowerFlow":
        from mastapy._private.system_model.analyses_and_results.power_flows import _4394

        return self.__parent__._cast(_4394.CylindricalGearPowerFlow)

    @property
    def cylindrical_planet_gear_power_flow(
        self: "CastSelf",
    ) -> "_4396.CylindricalPlanetGearPowerFlow":
        from mastapy._private.system_model.analyses_and_results.power_flows import _4396

        return self.__parent__._cast(_4396.CylindricalPlanetGearPowerFlow)

    @property
    def face_gear_power_flow(self: "CastSelf") -> "_4400.FaceGearPowerFlow":
        from mastapy._private.system_model.analyses_and_results.power_flows import _4400

        return self.__parent__._cast(_4400.FaceGearPowerFlow)

    @property
    def hypoid_gear_power_flow(self: "CastSelf") -> "_4411.HypoidGearPowerFlow":
        from mastapy._private.system_model.analyses_and_results.power_flows import _4411

        return self.__parent__._cast(_4411.HypoidGearPowerFlow)

    @property
    def klingelnberg_cyclo_palloid_conical_gear_power_flow(
        self: "CastSelf",
    ) -> "_4415.KlingelnbergCycloPalloidConicalGearPowerFlow":
        from mastapy._private.system_model.analyses_and_results.power_flows import _4415

        return self.__parent__._cast(_4415.KlingelnbergCycloPalloidConicalGearPowerFlow)

    @property
    def klingelnberg_cyclo_palloid_hypoid_gear_power_flow(
        self: "CastSelf",
    ) -> "_4418.KlingelnbergCycloPalloidHypoidGearPowerFlow":
        from mastapy._private.system_model.analyses_and_results.power_flows import _4418

        return self.__parent__._cast(_4418.KlingelnbergCycloPalloidHypoidGearPowerFlow)

    @property
    def klingelnberg_cyclo_palloid_spiral_bevel_gear_power_flow(
        self: "CastSelf",
    ) -> "_4421.KlingelnbergCycloPalloidSpiralBevelGearPowerFlow":
        from mastapy._private.system_model.analyses_and_results.power_flows import _4421

        return self.__parent__._cast(
            _4421.KlingelnbergCycloPalloidSpiralBevelGearPowerFlow
        )

    @property
    def spiral_bevel_gear_power_flow(
        self: "CastSelf",
    ) -> "_4452.SpiralBevelGearPowerFlow":
        from mastapy._private.system_model.analyses_and_results.power_flows import _4452

        return self.__parent__._cast(_4452.SpiralBevelGearPowerFlow)

    @property
    def straight_bevel_diff_gear_power_flow(
        self: "CastSelf",
    ) -> "_4458.StraightBevelDiffGearPowerFlow":
        from mastapy._private.system_model.analyses_and_results.power_flows import _4458

        return self.__parent__._cast(_4458.StraightBevelDiffGearPowerFlow)

    @property
    def straight_bevel_gear_power_flow(
        self: "CastSelf",
    ) -> "_4461.StraightBevelGearPowerFlow":
        from mastapy._private.system_model.analyses_and_results.power_flows import _4461

        return self.__parent__._cast(_4461.StraightBevelGearPowerFlow)

    @property
    def straight_bevel_planet_gear_power_flow(
        self: "CastSelf",
    ) -> "_4463.StraightBevelPlanetGearPowerFlow":
        from mastapy._private.system_model.analyses_and_results.power_flows import _4463

        return self.__parent__._cast(_4463.StraightBevelPlanetGearPowerFlow)

    @property
    def straight_bevel_sun_gear_power_flow(
        self: "CastSelf",
    ) -> "_4464.StraightBevelSunGearPowerFlow":
        from mastapy._private.system_model.analyses_and_results.power_flows import _4464

        return self.__parent__._cast(_4464.StraightBevelSunGearPowerFlow)

    @property
    def worm_gear_power_flow(self: "CastSelf") -> "_4477.WormGearPowerFlow":
        from mastapy._private.system_model.analyses_and_results.power_flows import _4477

        return self.__parent__._cast(_4477.WormGearPowerFlow)

    @property
    def zerol_bevel_gear_power_flow(
        self: "CastSelf",
    ) -> "_4480.ZerolBevelGearPowerFlow":
        from mastapy._private.system_model.analyses_and_results.power_flows import _4480

        return self.__parent__._cast(_4480.ZerolBevelGearPowerFlow)

    @property
    def gear_power_flow(self: "CastSelf") -> "GearPowerFlow":
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
class GearPowerFlow(_4427.MountableComponentPowerFlow):
    """GearPowerFlow

    This is a mastapy class.
    """

    TYPE: ClassVar["Type"] = _GEAR_POWER_FLOW

    wrapped: "Any"

    def __post_init__(self: "Self") -> None:
        """Override of the post initialisation magic method."""
        if not hasattr(self.wrapped, "reference_count"):
            self.wrapped.reference_count = 0

        self.wrapped.reference_count += 1

    @property
    @exception_bridge
    def is_loaded(self: "Self") -> "bool":
        """bool

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "IsLoaded")

        if temp is None:
            return False

        return temp

    @property
    @exception_bridge
    def component_design(self: "Self") -> "_2811.Gear":
        """mastapy.system_model.part_model.gears.Gear

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "ComponentDesign")

        if temp is None:
            return None

        type_ = temp.GetType()
        return constructor.new(type_.Namespace, type_.Name)(temp)

    @property
    def cast_to(self: "Self") -> "_Cast_GearPowerFlow":
        """Cast to another type.

        Returns:
            _Cast_GearPowerFlow
        """
        return _Cast_GearPowerFlow(self)
