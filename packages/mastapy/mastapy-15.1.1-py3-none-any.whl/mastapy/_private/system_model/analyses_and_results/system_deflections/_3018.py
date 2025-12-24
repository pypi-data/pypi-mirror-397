"""ConicalGearSystemDeflection"""

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
from mastapy._private.system_model.analyses_and_results.system_deflections import _3053

_CONICAL_GEAR_SYSTEM_DEFLECTION = python_net_import(
    "SMT.MastaAPI.SystemModel.AnalysesAndResults.SystemDeflections",
    "ConicalGearSystemDeflection",
)

if TYPE_CHECKING:
    from typing import Any, List, Type, TypeVar

    from mastapy._private.gears.ltca.conical import _992
    from mastapy._private.system_model.analyses_and_results import _2943, _2945, _2949
    from mastapy._private.system_model.analyses_and_results.analysis_cases import (
        _7941,
        _7943,
        _7944,
    )
    from mastapy._private.system_model.analyses_and_results.power_flows import _4378
    from mastapy._private.system_model.analyses_and_results.system_deflections import (
        _2983,
        _2995,
        _2996,
        _2997,
        _3000,
        _3007,
        _3057,
        _3062,
        _3065,
        _3068,
        _3076,
        _3079,
        _3103,
        _3109,
        _3112,
        _3113,
        _3114,
        _3136,
    )
    from mastapy._private.system_model.part_model.gears import _2804

    Self = TypeVar("Self", bound="ConicalGearSystemDeflection")
    CastSelf = TypeVar(
        "CastSelf",
        bound="ConicalGearSystemDeflection._Cast_ConicalGearSystemDeflection",
    )


__docformat__ = "restructuredtext en"
__all__ = ("ConicalGearSystemDeflection",)


@extended_dataclass(frozen=True, slots=True, weakref_slot=True)
class _Cast_ConicalGearSystemDeflection:
    """Special nested class for casting ConicalGearSystemDeflection to subclasses."""

    __parent__: "ConicalGearSystemDeflection"

    @property
    def gear_system_deflection(self: "CastSelf") -> "_3053.GearSystemDeflection":
        return self.__parent__._cast(_3053.GearSystemDeflection)

    @property
    def mountable_component_system_deflection(
        self: "CastSelf",
    ) -> "_3076.MountableComponentSystemDeflection":
        from mastapy._private.system_model.analyses_and_results.system_deflections import (
            _3076,
        )

        return self.__parent__._cast(_3076.MountableComponentSystemDeflection)

    @property
    def component_system_deflection(
        self: "CastSelf",
    ) -> "_3007.ComponentSystemDeflection":
        from mastapy._private.system_model.analyses_and_results.system_deflections import (
            _3007,
        )

        return self.__parent__._cast(_3007.ComponentSystemDeflection)

    @property
    def part_system_deflection(self: "CastSelf") -> "_3079.PartSystemDeflection":
        from mastapy._private.system_model.analyses_and_results.system_deflections import (
            _3079,
        )

        return self.__parent__._cast(_3079.PartSystemDeflection)

    @property
    def part_fe_analysis(self: "CastSelf") -> "_7943.PartFEAnalysis":
        from mastapy._private.system_model.analyses_and_results.analysis_cases import (
            _7943,
        )

        return self.__parent__._cast(_7943.PartFEAnalysis)

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
    def agma_gleason_conical_gear_system_deflection(
        self: "CastSelf",
    ) -> "_2983.AGMAGleasonConicalGearSystemDeflection":
        from mastapy._private.system_model.analyses_and_results.system_deflections import (
            _2983,
        )

        return self.__parent__._cast(_2983.AGMAGleasonConicalGearSystemDeflection)

    @property
    def bevel_differential_gear_system_deflection(
        self: "CastSelf",
    ) -> "_2995.BevelDifferentialGearSystemDeflection":
        from mastapy._private.system_model.analyses_and_results.system_deflections import (
            _2995,
        )

        return self.__parent__._cast(_2995.BevelDifferentialGearSystemDeflection)

    @property
    def bevel_differential_planet_gear_system_deflection(
        self: "CastSelf",
    ) -> "_2996.BevelDifferentialPlanetGearSystemDeflection":
        from mastapy._private.system_model.analyses_and_results.system_deflections import (
            _2996,
        )

        return self.__parent__._cast(_2996.BevelDifferentialPlanetGearSystemDeflection)

    @property
    def bevel_differential_sun_gear_system_deflection(
        self: "CastSelf",
    ) -> "_2997.BevelDifferentialSunGearSystemDeflection":
        from mastapy._private.system_model.analyses_and_results.system_deflections import (
            _2997,
        )

        return self.__parent__._cast(_2997.BevelDifferentialSunGearSystemDeflection)

    @property
    def bevel_gear_system_deflection(
        self: "CastSelf",
    ) -> "_3000.BevelGearSystemDeflection":
        from mastapy._private.system_model.analyses_and_results.system_deflections import (
            _3000,
        )

        return self.__parent__._cast(_3000.BevelGearSystemDeflection)

    @property
    def hypoid_gear_system_deflection(
        self: "CastSelf",
    ) -> "_3057.HypoidGearSystemDeflection":
        from mastapy._private.system_model.analyses_and_results.system_deflections import (
            _3057,
        )

        return self.__parent__._cast(_3057.HypoidGearSystemDeflection)

    @property
    def klingelnberg_cyclo_palloid_conical_gear_system_deflection(
        self: "CastSelf",
    ) -> "_3062.KlingelnbergCycloPalloidConicalGearSystemDeflection":
        from mastapy._private.system_model.analyses_and_results.system_deflections import (
            _3062,
        )

        return self.__parent__._cast(
            _3062.KlingelnbergCycloPalloidConicalGearSystemDeflection
        )

    @property
    def klingelnberg_cyclo_palloid_hypoid_gear_system_deflection(
        self: "CastSelf",
    ) -> "_3065.KlingelnbergCycloPalloidHypoidGearSystemDeflection":
        from mastapy._private.system_model.analyses_and_results.system_deflections import (
            _3065,
        )

        return self.__parent__._cast(
            _3065.KlingelnbergCycloPalloidHypoidGearSystemDeflection
        )

    @property
    def klingelnberg_cyclo_palloid_spiral_bevel_gear_system_deflection(
        self: "CastSelf",
    ) -> "_3068.KlingelnbergCycloPalloidSpiralBevelGearSystemDeflection":
        from mastapy._private.system_model.analyses_and_results.system_deflections import (
            _3068,
        )

        return self.__parent__._cast(
            _3068.KlingelnbergCycloPalloidSpiralBevelGearSystemDeflection
        )

    @property
    def spiral_bevel_gear_system_deflection(
        self: "CastSelf",
    ) -> "_3103.SpiralBevelGearSystemDeflection":
        from mastapy._private.system_model.analyses_and_results.system_deflections import (
            _3103,
        )

        return self.__parent__._cast(_3103.SpiralBevelGearSystemDeflection)

    @property
    def straight_bevel_diff_gear_system_deflection(
        self: "CastSelf",
    ) -> "_3109.StraightBevelDiffGearSystemDeflection":
        from mastapy._private.system_model.analyses_and_results.system_deflections import (
            _3109,
        )

        return self.__parent__._cast(_3109.StraightBevelDiffGearSystemDeflection)

    @property
    def straight_bevel_gear_system_deflection(
        self: "CastSelf",
    ) -> "_3112.StraightBevelGearSystemDeflection":
        from mastapy._private.system_model.analyses_and_results.system_deflections import (
            _3112,
        )

        return self.__parent__._cast(_3112.StraightBevelGearSystemDeflection)

    @property
    def straight_bevel_planet_gear_system_deflection(
        self: "CastSelf",
    ) -> "_3113.StraightBevelPlanetGearSystemDeflection":
        from mastapy._private.system_model.analyses_and_results.system_deflections import (
            _3113,
        )

        return self.__parent__._cast(_3113.StraightBevelPlanetGearSystemDeflection)

    @property
    def straight_bevel_sun_gear_system_deflection(
        self: "CastSelf",
    ) -> "_3114.StraightBevelSunGearSystemDeflection":
        from mastapy._private.system_model.analyses_and_results.system_deflections import (
            _3114,
        )

        return self.__parent__._cast(_3114.StraightBevelSunGearSystemDeflection)

    @property
    def zerol_bevel_gear_system_deflection(
        self: "CastSelf",
    ) -> "_3136.ZerolBevelGearSystemDeflection":
        from mastapy._private.system_model.analyses_and_results.system_deflections import (
            _3136,
        )

        return self.__parent__._cast(_3136.ZerolBevelGearSystemDeflection)

    @property
    def conical_gear_system_deflection(
        self: "CastSelf",
    ) -> "ConicalGearSystemDeflection":
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
class ConicalGearSystemDeflection(_3053.GearSystemDeflection):
    """ConicalGearSystemDeflection

    This is a mastapy class.
    """

    TYPE: ClassVar["Type"] = _CONICAL_GEAR_SYSTEM_DEFLECTION

    wrapped: "Any"

    def __post_init__(self: "Self") -> None:
        """Override of the post initialisation magic method."""
        if not hasattr(self.wrapped, "reference_count"):
            self.wrapped.reference_count = 0

        self.wrapped.reference_count += 1

    @property
    @exception_bridge
    def component_design(self: "Self") -> "_2804.ConicalGear":
        """mastapy.system_model.part_model.gears.ConicalGear

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
    def conical_gear_ltca_results(
        self: "Self",
    ) -> "_992.ConicalGearLoadDistributionAnalysis":
        """mastapy.gears.ltca.conical.ConicalGearLoadDistributionAnalysis

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "ConicalGearLTCAResults")

        if temp is None:
            return None

        type_ = temp.GetType()
        return constructor.new(type_.Namespace, type_.Name)(temp)

    @property
    @exception_bridge
    def planetaries(self: "Self") -> "List[ConicalGearSystemDeflection]":
        """List[mastapy.system_model.analyses_and_results.system_deflections.ConicalGearSystemDeflection]

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "Planetaries")

        if temp is None:
            return None

        value = conversion.pn_to_mp_objects_in_list(temp)

        if value is None:
            return None

        return value

    @property
    @exception_bridge
    def power_flow_results(self: "Self") -> "_4378.ConicalGearPowerFlow":
        """mastapy.system_model.analyses_and_results.power_flows.ConicalGearPowerFlow

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "PowerFlowResults")

        if temp is None:
            return None

        type_ = temp.GetType()
        return constructor.new(type_.Namespace, type_.Name)(temp)

    @property
    def cast_to(self: "Self") -> "_Cast_ConicalGearSystemDeflection":
        """Cast to another type.

        Returns:
            _Cast_ConicalGearSystemDeflection
        """
        return _Cast_ConicalGearSystemDeflection(self)
