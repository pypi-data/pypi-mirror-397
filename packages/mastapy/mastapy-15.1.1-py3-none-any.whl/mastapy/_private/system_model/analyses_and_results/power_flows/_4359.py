"""BevelDifferentialPlanetGearPowerFlow"""

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
from mastapy._private.system_model.analyses_and_results.power_flows import _4357

_BEVEL_DIFFERENTIAL_PLANET_GEAR_POWER_FLOW = python_net_import(
    "SMT.MastaAPI.SystemModel.AnalysesAndResults.PowerFlows",
    "BevelDifferentialPlanetGearPowerFlow",
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
        _4362,
        _4370,
        _4378,
        _4407,
        _4427,
        _4429,
    )
    from mastapy._private.system_model.part_model.gears import _2798

    Self = TypeVar("Self", bound="BevelDifferentialPlanetGearPowerFlow")
    CastSelf = TypeVar(
        "CastSelf",
        bound="BevelDifferentialPlanetGearPowerFlow._Cast_BevelDifferentialPlanetGearPowerFlow",
    )


__docformat__ = "restructuredtext en"
__all__ = ("BevelDifferentialPlanetGearPowerFlow",)


@extended_dataclass(frozen=True, slots=True, weakref_slot=True)
class _Cast_BevelDifferentialPlanetGearPowerFlow:
    """Special nested class for casting BevelDifferentialPlanetGearPowerFlow to subclasses."""

    __parent__: "BevelDifferentialPlanetGearPowerFlow"

    @property
    def bevel_differential_gear_power_flow(
        self: "CastSelf",
    ) -> "_4357.BevelDifferentialGearPowerFlow":
        return self.__parent__._cast(_4357.BevelDifferentialGearPowerFlow)

    @property
    def bevel_gear_power_flow(self: "CastSelf") -> "_4362.BevelGearPowerFlow":
        from mastapy._private.system_model.analyses_and_results.power_flows import _4362

        return self.__parent__._cast(_4362.BevelGearPowerFlow)

    @property
    def agma_gleason_conical_gear_power_flow(
        self: "CastSelf",
    ) -> "_4350.AGMAGleasonConicalGearPowerFlow":
        from mastapy._private.system_model.analyses_and_results.power_flows import _4350

        return self.__parent__._cast(_4350.AGMAGleasonConicalGearPowerFlow)

    @property
    def conical_gear_power_flow(self: "CastSelf") -> "_4378.ConicalGearPowerFlow":
        from mastapy._private.system_model.analyses_and_results.power_flows import _4378

        return self.__parent__._cast(_4378.ConicalGearPowerFlow)

    @property
    def gear_power_flow(self: "CastSelf") -> "_4407.GearPowerFlow":
        from mastapy._private.system_model.analyses_and_results.power_flows import _4407

        return self.__parent__._cast(_4407.GearPowerFlow)

    @property
    def mountable_component_power_flow(
        self: "CastSelf",
    ) -> "_4427.MountableComponentPowerFlow":
        from mastapy._private.system_model.analyses_and_results.power_flows import _4427

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
    def bevel_differential_planet_gear_power_flow(
        self: "CastSelf",
    ) -> "BevelDifferentialPlanetGearPowerFlow":
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
class BevelDifferentialPlanetGearPowerFlow(_4357.BevelDifferentialGearPowerFlow):
    """BevelDifferentialPlanetGearPowerFlow

    This is a mastapy class.
    """

    TYPE: ClassVar["Type"] = _BEVEL_DIFFERENTIAL_PLANET_GEAR_POWER_FLOW

    wrapped: "Any"

    def __post_init__(self: "Self") -> None:
        """Override of the post initialisation magic method."""
        if not hasattr(self.wrapped, "reference_count"):
            self.wrapped.reference_count = 0

        self.wrapped.reference_count += 1

    @property
    @exception_bridge
    def component_design(self: "Self") -> "_2798.BevelDifferentialPlanetGear":
        """mastapy.system_model.part_model.gears.BevelDifferentialPlanetGear

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "ComponentDesign")

        if temp is None:
            return None

        type_ = temp.GetType()
        return constructor.new(type_.Namespace, type_.Name)(temp)

    @property
    def cast_to(self: "Self") -> "_Cast_BevelDifferentialPlanetGearPowerFlow":
        """Cast to another type.

        Returns:
            _Cast_BevelDifferentialPlanetGearPowerFlow
        """
        return _Cast_BevelDifferentialPlanetGearPowerFlow(self)
