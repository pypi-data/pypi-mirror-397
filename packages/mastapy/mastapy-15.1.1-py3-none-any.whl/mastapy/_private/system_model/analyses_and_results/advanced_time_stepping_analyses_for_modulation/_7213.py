"""ConicalGearAdvancedTimeSteppingAnalysisForModulation"""

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
from mastapy._private.system_model.analyses_and_results.advanced_time_stepping_analyses_for_modulation import (
    _7239,
)

_CONICAL_GEAR_ADVANCED_TIME_STEPPING_ANALYSIS_FOR_MODULATION = python_net_import(
    "SMT.MastaAPI.SystemModel.AnalysesAndResults.AdvancedTimeSteppingAnalysesForModulation",
    "ConicalGearAdvancedTimeSteppingAnalysisForModulation",
)

if TYPE_CHECKING:
    from typing import Any, List, Type, TypeVar

    from mastapy._private.system_model.analyses_and_results import _2943, _2945, _2949
    from mastapy._private.system_model.analyses_and_results.advanced_time_stepping_analyses_for_modulation import (
        _7184,
        _7192,
        _7195,
        _7196,
        _7197,
        _7206,
        _7244,
        _7248,
        _7251,
        _7254,
        _7261,
        _7263,
        _7283,
        _7289,
        _7292,
        _7295,
        _7296,
        _7310,
    )
    from mastapy._private.system_model.analyses_and_results.analysis_cases import (
        _7941,
        _7944,
    )
    from mastapy._private.system_model.analyses_and_results.system_deflections import (
        _3018,
    )
    from mastapy._private.system_model.part_model.gears import _2804

    Self = TypeVar("Self", bound="ConicalGearAdvancedTimeSteppingAnalysisForModulation")
    CastSelf = TypeVar(
        "CastSelf",
        bound="ConicalGearAdvancedTimeSteppingAnalysisForModulation._Cast_ConicalGearAdvancedTimeSteppingAnalysisForModulation",
    )


__docformat__ = "restructuredtext en"
__all__ = ("ConicalGearAdvancedTimeSteppingAnalysisForModulation",)


@extended_dataclass(frozen=True, slots=True, weakref_slot=True)
class _Cast_ConicalGearAdvancedTimeSteppingAnalysisForModulation:
    """Special nested class for casting ConicalGearAdvancedTimeSteppingAnalysisForModulation to subclasses."""

    __parent__: "ConicalGearAdvancedTimeSteppingAnalysisForModulation"

    @property
    def gear_advanced_time_stepping_analysis_for_modulation(
        self: "CastSelf",
    ) -> "_7239.GearAdvancedTimeSteppingAnalysisForModulation":
        return self.__parent__._cast(
            _7239.GearAdvancedTimeSteppingAnalysisForModulation
        )

    @property
    def mountable_component_advanced_time_stepping_analysis_for_modulation(
        self: "CastSelf",
    ) -> "_7261.MountableComponentAdvancedTimeSteppingAnalysisForModulation":
        from mastapy._private.system_model.analyses_and_results.advanced_time_stepping_analyses_for_modulation import (
            _7261,
        )

        return self.__parent__._cast(
            _7261.MountableComponentAdvancedTimeSteppingAnalysisForModulation
        )

    @property
    def component_advanced_time_stepping_analysis_for_modulation(
        self: "CastSelf",
    ) -> "_7206.ComponentAdvancedTimeSteppingAnalysisForModulation":
        from mastapy._private.system_model.analyses_and_results.advanced_time_stepping_analyses_for_modulation import (
            _7206,
        )

        return self.__parent__._cast(
            _7206.ComponentAdvancedTimeSteppingAnalysisForModulation
        )

    @property
    def part_advanced_time_stepping_analysis_for_modulation(
        self: "CastSelf",
    ) -> "_7263.PartAdvancedTimeSteppingAnalysisForModulation":
        from mastapy._private.system_model.analyses_and_results.advanced_time_stepping_analyses_for_modulation import (
            _7263,
        )

        return self.__parent__._cast(
            _7263.PartAdvancedTimeSteppingAnalysisForModulation
        )

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
    def agma_gleason_conical_gear_advanced_time_stepping_analysis_for_modulation(
        self: "CastSelf",
    ) -> "_7184.AGMAGleasonConicalGearAdvancedTimeSteppingAnalysisForModulation":
        from mastapy._private.system_model.analyses_and_results.advanced_time_stepping_analyses_for_modulation import (
            _7184,
        )

        return self.__parent__._cast(
            _7184.AGMAGleasonConicalGearAdvancedTimeSteppingAnalysisForModulation
        )

    @property
    def bevel_differential_gear_advanced_time_stepping_analysis_for_modulation(
        self: "CastSelf",
    ) -> "_7192.BevelDifferentialGearAdvancedTimeSteppingAnalysisForModulation":
        from mastapy._private.system_model.analyses_and_results.advanced_time_stepping_analyses_for_modulation import (
            _7192,
        )

        return self.__parent__._cast(
            _7192.BevelDifferentialGearAdvancedTimeSteppingAnalysisForModulation
        )

    @property
    def bevel_differential_planet_gear_advanced_time_stepping_analysis_for_modulation(
        self: "CastSelf",
    ) -> "_7195.BevelDifferentialPlanetGearAdvancedTimeSteppingAnalysisForModulation":
        from mastapy._private.system_model.analyses_and_results.advanced_time_stepping_analyses_for_modulation import (
            _7195,
        )

        return self.__parent__._cast(
            _7195.BevelDifferentialPlanetGearAdvancedTimeSteppingAnalysisForModulation
        )

    @property
    def bevel_differential_sun_gear_advanced_time_stepping_analysis_for_modulation(
        self: "CastSelf",
    ) -> "_7196.BevelDifferentialSunGearAdvancedTimeSteppingAnalysisForModulation":
        from mastapy._private.system_model.analyses_and_results.advanced_time_stepping_analyses_for_modulation import (
            _7196,
        )

        return self.__parent__._cast(
            _7196.BevelDifferentialSunGearAdvancedTimeSteppingAnalysisForModulation
        )

    @property
    def bevel_gear_advanced_time_stepping_analysis_for_modulation(
        self: "CastSelf",
    ) -> "_7197.BevelGearAdvancedTimeSteppingAnalysisForModulation":
        from mastapy._private.system_model.analyses_and_results.advanced_time_stepping_analyses_for_modulation import (
            _7197,
        )

        return self.__parent__._cast(
            _7197.BevelGearAdvancedTimeSteppingAnalysisForModulation
        )

    @property
    def hypoid_gear_advanced_time_stepping_analysis_for_modulation(
        self: "CastSelf",
    ) -> "_7244.HypoidGearAdvancedTimeSteppingAnalysisForModulation":
        from mastapy._private.system_model.analyses_and_results.advanced_time_stepping_analyses_for_modulation import (
            _7244,
        )

        return self.__parent__._cast(
            _7244.HypoidGearAdvancedTimeSteppingAnalysisForModulation
        )

    @property
    def klingelnberg_cyclo_palloid_conical_gear_advanced_time_stepping_analysis_for_modulation(
        self: "CastSelf",
    ) -> "_7248.KlingelnbergCycloPalloidConicalGearAdvancedTimeSteppingAnalysisForModulation":
        from mastapy._private.system_model.analyses_and_results.advanced_time_stepping_analyses_for_modulation import (
            _7248,
        )

        return self.__parent__._cast(
            _7248.KlingelnbergCycloPalloidConicalGearAdvancedTimeSteppingAnalysisForModulation
        )

    @property
    def klingelnberg_cyclo_palloid_hypoid_gear_advanced_time_stepping_analysis_for_modulation(
        self: "CastSelf",
    ) -> "_7251.KlingelnbergCycloPalloidHypoidGearAdvancedTimeSteppingAnalysisForModulation":
        from mastapy._private.system_model.analyses_and_results.advanced_time_stepping_analyses_for_modulation import (
            _7251,
        )

        return self.__parent__._cast(
            _7251.KlingelnbergCycloPalloidHypoidGearAdvancedTimeSteppingAnalysisForModulation
        )

    @property
    def klingelnberg_cyclo_palloid_spiral_bevel_gear_advanced_time_stepping_analysis_for_modulation(
        self: "CastSelf",
    ) -> "_7254.KlingelnbergCycloPalloidSpiralBevelGearAdvancedTimeSteppingAnalysisForModulation":
        from mastapy._private.system_model.analyses_and_results.advanced_time_stepping_analyses_for_modulation import (
            _7254,
        )

        return self.__parent__._cast(
            _7254.KlingelnbergCycloPalloidSpiralBevelGearAdvancedTimeSteppingAnalysisForModulation
        )

    @property
    def spiral_bevel_gear_advanced_time_stepping_analysis_for_modulation(
        self: "CastSelf",
    ) -> "_7283.SpiralBevelGearAdvancedTimeSteppingAnalysisForModulation":
        from mastapy._private.system_model.analyses_and_results.advanced_time_stepping_analyses_for_modulation import (
            _7283,
        )

        return self.__parent__._cast(
            _7283.SpiralBevelGearAdvancedTimeSteppingAnalysisForModulation
        )

    @property
    def straight_bevel_diff_gear_advanced_time_stepping_analysis_for_modulation(
        self: "CastSelf",
    ) -> "_7289.StraightBevelDiffGearAdvancedTimeSteppingAnalysisForModulation":
        from mastapy._private.system_model.analyses_and_results.advanced_time_stepping_analyses_for_modulation import (
            _7289,
        )

        return self.__parent__._cast(
            _7289.StraightBevelDiffGearAdvancedTimeSteppingAnalysisForModulation
        )

    @property
    def straight_bevel_gear_advanced_time_stepping_analysis_for_modulation(
        self: "CastSelf",
    ) -> "_7292.StraightBevelGearAdvancedTimeSteppingAnalysisForModulation":
        from mastapy._private.system_model.analyses_and_results.advanced_time_stepping_analyses_for_modulation import (
            _7292,
        )

        return self.__parent__._cast(
            _7292.StraightBevelGearAdvancedTimeSteppingAnalysisForModulation
        )

    @property
    def straight_bevel_planet_gear_advanced_time_stepping_analysis_for_modulation(
        self: "CastSelf",
    ) -> "_7295.StraightBevelPlanetGearAdvancedTimeSteppingAnalysisForModulation":
        from mastapy._private.system_model.analyses_and_results.advanced_time_stepping_analyses_for_modulation import (
            _7295,
        )

        return self.__parent__._cast(
            _7295.StraightBevelPlanetGearAdvancedTimeSteppingAnalysisForModulation
        )

    @property
    def straight_bevel_sun_gear_advanced_time_stepping_analysis_for_modulation(
        self: "CastSelf",
    ) -> "_7296.StraightBevelSunGearAdvancedTimeSteppingAnalysisForModulation":
        from mastapy._private.system_model.analyses_and_results.advanced_time_stepping_analyses_for_modulation import (
            _7296,
        )

        return self.__parent__._cast(
            _7296.StraightBevelSunGearAdvancedTimeSteppingAnalysisForModulation
        )

    @property
    def zerol_bevel_gear_advanced_time_stepping_analysis_for_modulation(
        self: "CastSelf",
    ) -> "_7310.ZerolBevelGearAdvancedTimeSteppingAnalysisForModulation":
        from mastapy._private.system_model.analyses_and_results.advanced_time_stepping_analyses_for_modulation import (
            _7310,
        )

        return self.__parent__._cast(
            _7310.ZerolBevelGearAdvancedTimeSteppingAnalysisForModulation
        )

    @property
    def conical_gear_advanced_time_stepping_analysis_for_modulation(
        self: "CastSelf",
    ) -> "ConicalGearAdvancedTimeSteppingAnalysisForModulation":
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
class ConicalGearAdvancedTimeSteppingAnalysisForModulation(
    _7239.GearAdvancedTimeSteppingAnalysisForModulation
):
    """ConicalGearAdvancedTimeSteppingAnalysisForModulation

    This is a mastapy class.
    """

    TYPE: ClassVar["Type"] = (
        _CONICAL_GEAR_ADVANCED_TIME_STEPPING_ANALYSIS_FOR_MODULATION
    )

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
    def planetaries(
        self: "Self",
    ) -> "List[ConicalGearAdvancedTimeSteppingAnalysisForModulation]":
        """List[mastapy.system_model.analyses_and_results.advanced_time_stepping_analyses_for_modulation.ConicalGearAdvancedTimeSteppingAnalysisForModulation]

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
    def system_deflection_results(self: "Self") -> "_3018.ConicalGearSystemDeflection":
        """mastapy.system_model.analyses_and_results.system_deflections.ConicalGearSystemDeflection

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "SystemDeflectionResults")

        if temp is None:
            return None

        type_ = temp.GetType()
        return constructor.new(type_.Namespace, type_.Name)(temp)

    @property
    def cast_to(
        self: "Self",
    ) -> "_Cast_ConicalGearAdvancedTimeSteppingAnalysisForModulation":
        """Cast to another type.

        Returns:
            _Cast_ConicalGearAdvancedTimeSteppingAnalysisForModulation
        """
        return _Cast_ConicalGearAdvancedTimeSteppingAnalysisForModulation(self)
