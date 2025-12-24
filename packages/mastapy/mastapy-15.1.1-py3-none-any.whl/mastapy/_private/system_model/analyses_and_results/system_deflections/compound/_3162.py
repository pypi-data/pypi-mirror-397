"""BevelGearCompoundSystemDeflection"""

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
from mastapy._private.system_model.analyses_and_results.system_deflections.compound import (
    _3150,
)

_BEVEL_GEAR_COMPOUND_SYSTEM_DEFLECTION = python_net_import(
    "SMT.MastaAPI.SystemModel.AnalysesAndResults.SystemDeflections.Compound",
    "BevelGearCompoundSystemDeflection",
)

if TYPE_CHECKING:
    from typing import Any, List, Type, TypeVar

    from mastapy._private.system_model.analyses_and_results import _2943
    from mastapy._private.system_model.analyses_and_results.analysis_cases import (
        _7939,
        _7942,
    )
    from mastapy._private.system_model.analyses_and_results.system_deflections import (
        _3000,
    )
    from mastapy._private.system_model.analyses_and_results.system_deflections.compound import (
        _3157,
        _3160,
        _3161,
        _3171,
        _3178,
        _3205,
        _3226,
        _3228,
        _3249,
        _3255,
        _3258,
        _3261,
        _3262,
        _3276,
    )

    Self = TypeVar("Self", bound="BevelGearCompoundSystemDeflection")
    CastSelf = TypeVar(
        "CastSelf",
        bound="BevelGearCompoundSystemDeflection._Cast_BevelGearCompoundSystemDeflection",
    )


__docformat__ = "restructuredtext en"
__all__ = ("BevelGearCompoundSystemDeflection",)


@extended_dataclass(frozen=True, slots=True, weakref_slot=True)
class _Cast_BevelGearCompoundSystemDeflection:
    """Special nested class for casting BevelGearCompoundSystemDeflection to subclasses."""

    __parent__: "BevelGearCompoundSystemDeflection"

    @property
    def agma_gleason_conical_gear_compound_system_deflection(
        self: "CastSelf",
    ) -> "_3150.AGMAGleasonConicalGearCompoundSystemDeflection":
        return self.__parent__._cast(
            _3150.AGMAGleasonConicalGearCompoundSystemDeflection
        )

    @property
    def conical_gear_compound_system_deflection(
        self: "CastSelf",
    ) -> "_3178.ConicalGearCompoundSystemDeflection":
        from mastapy._private.system_model.analyses_and_results.system_deflections.compound import (
            _3178,
        )

        return self.__parent__._cast(_3178.ConicalGearCompoundSystemDeflection)

    @property
    def gear_compound_system_deflection(
        self: "CastSelf",
    ) -> "_3205.GearCompoundSystemDeflection":
        from mastapy._private.system_model.analyses_and_results.system_deflections.compound import (
            _3205,
        )

        return self.__parent__._cast(_3205.GearCompoundSystemDeflection)

    @property
    def mountable_component_compound_system_deflection(
        self: "CastSelf",
    ) -> "_3226.MountableComponentCompoundSystemDeflection":
        from mastapy._private.system_model.analyses_and_results.system_deflections.compound import (
            _3226,
        )

        return self.__parent__._cast(_3226.MountableComponentCompoundSystemDeflection)

    @property
    def component_compound_system_deflection(
        self: "CastSelf",
    ) -> "_3171.ComponentCompoundSystemDeflection":
        from mastapy._private.system_model.analyses_and_results.system_deflections.compound import (
            _3171,
        )

        return self.__parent__._cast(_3171.ComponentCompoundSystemDeflection)

    @property
    def part_compound_system_deflection(
        self: "CastSelf",
    ) -> "_3228.PartCompoundSystemDeflection":
        from mastapy._private.system_model.analyses_and_results.system_deflections.compound import (
            _3228,
        )

        return self.__parent__._cast(_3228.PartCompoundSystemDeflection)

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
    def bevel_differential_gear_compound_system_deflection(
        self: "CastSelf",
    ) -> "_3157.BevelDifferentialGearCompoundSystemDeflection":
        from mastapy._private.system_model.analyses_and_results.system_deflections.compound import (
            _3157,
        )

        return self.__parent__._cast(
            _3157.BevelDifferentialGearCompoundSystemDeflection
        )

    @property
    def bevel_differential_planet_gear_compound_system_deflection(
        self: "CastSelf",
    ) -> "_3160.BevelDifferentialPlanetGearCompoundSystemDeflection":
        from mastapy._private.system_model.analyses_and_results.system_deflections.compound import (
            _3160,
        )

        return self.__parent__._cast(
            _3160.BevelDifferentialPlanetGearCompoundSystemDeflection
        )

    @property
    def bevel_differential_sun_gear_compound_system_deflection(
        self: "CastSelf",
    ) -> "_3161.BevelDifferentialSunGearCompoundSystemDeflection":
        from mastapy._private.system_model.analyses_and_results.system_deflections.compound import (
            _3161,
        )

        return self.__parent__._cast(
            _3161.BevelDifferentialSunGearCompoundSystemDeflection
        )

    @property
    def spiral_bevel_gear_compound_system_deflection(
        self: "CastSelf",
    ) -> "_3249.SpiralBevelGearCompoundSystemDeflection":
        from mastapy._private.system_model.analyses_and_results.system_deflections.compound import (
            _3249,
        )

        return self.__parent__._cast(_3249.SpiralBevelGearCompoundSystemDeflection)

    @property
    def straight_bevel_diff_gear_compound_system_deflection(
        self: "CastSelf",
    ) -> "_3255.StraightBevelDiffGearCompoundSystemDeflection":
        from mastapy._private.system_model.analyses_and_results.system_deflections.compound import (
            _3255,
        )

        return self.__parent__._cast(
            _3255.StraightBevelDiffGearCompoundSystemDeflection
        )

    @property
    def straight_bevel_gear_compound_system_deflection(
        self: "CastSelf",
    ) -> "_3258.StraightBevelGearCompoundSystemDeflection":
        from mastapy._private.system_model.analyses_and_results.system_deflections.compound import (
            _3258,
        )

        return self.__parent__._cast(_3258.StraightBevelGearCompoundSystemDeflection)

    @property
    def straight_bevel_planet_gear_compound_system_deflection(
        self: "CastSelf",
    ) -> "_3261.StraightBevelPlanetGearCompoundSystemDeflection":
        from mastapy._private.system_model.analyses_and_results.system_deflections.compound import (
            _3261,
        )

        return self.__parent__._cast(
            _3261.StraightBevelPlanetGearCompoundSystemDeflection
        )

    @property
    def straight_bevel_sun_gear_compound_system_deflection(
        self: "CastSelf",
    ) -> "_3262.StraightBevelSunGearCompoundSystemDeflection":
        from mastapy._private.system_model.analyses_and_results.system_deflections.compound import (
            _3262,
        )

        return self.__parent__._cast(_3262.StraightBevelSunGearCompoundSystemDeflection)

    @property
    def zerol_bevel_gear_compound_system_deflection(
        self: "CastSelf",
    ) -> "_3276.ZerolBevelGearCompoundSystemDeflection":
        from mastapy._private.system_model.analyses_and_results.system_deflections.compound import (
            _3276,
        )

        return self.__parent__._cast(_3276.ZerolBevelGearCompoundSystemDeflection)

    @property
    def bevel_gear_compound_system_deflection(
        self: "CastSelf",
    ) -> "BevelGearCompoundSystemDeflection":
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
class BevelGearCompoundSystemDeflection(
    _3150.AGMAGleasonConicalGearCompoundSystemDeflection
):
    """BevelGearCompoundSystemDeflection

    This is a mastapy class.
    """

    TYPE: ClassVar["Type"] = _BEVEL_GEAR_COMPOUND_SYSTEM_DEFLECTION

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
    ) -> "List[_3000.BevelGearSystemDeflection]":
        """List[mastapy.system_model.analyses_and_results.system_deflections.BevelGearSystemDeflection]

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
    ) -> "List[_3000.BevelGearSystemDeflection]":
        """List[mastapy.system_model.analyses_and_results.system_deflections.BevelGearSystemDeflection]

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
    def cast_to(self: "Self") -> "_Cast_BevelGearCompoundSystemDeflection":
        """Cast to another type.

        Returns:
            _Cast_BevelGearCompoundSystemDeflection
        """
        return _Cast_BevelGearCompoundSystemDeflection(self)
