"""StraightBevelDiffGearCompoundSystemDeflection"""

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
from mastapy._private.system_model.analyses_and_results.system_deflections.compound import (
    _3162,
)

_STRAIGHT_BEVEL_DIFF_GEAR_COMPOUND_SYSTEM_DEFLECTION = python_net_import(
    "SMT.MastaAPI.SystemModel.AnalysesAndResults.SystemDeflections.Compound",
    "StraightBevelDiffGearCompoundSystemDeflection",
)

if TYPE_CHECKING:
    from typing import Any, List, Type, TypeVar

    from mastapy._private.system_model.analyses_and_results import _2943
    from mastapy._private.system_model.analyses_and_results.analysis_cases import (
        _7939,
        _7942,
    )
    from mastapy._private.system_model.analyses_and_results.system_deflections import (
        _3109,
    )
    from mastapy._private.system_model.analyses_and_results.system_deflections.compound import (
        _3150,
        _3171,
        _3178,
        _3205,
        _3226,
        _3228,
        _3261,
        _3262,
    )
    from mastapy._private.system_model.part_model.gears import _2827

    Self = TypeVar("Self", bound="StraightBevelDiffGearCompoundSystemDeflection")
    CastSelf = TypeVar(
        "CastSelf",
        bound="StraightBevelDiffGearCompoundSystemDeflection._Cast_StraightBevelDiffGearCompoundSystemDeflection",
    )


__docformat__ = "restructuredtext en"
__all__ = ("StraightBevelDiffGearCompoundSystemDeflection",)


@extended_dataclass(frozen=True, slots=True, weakref_slot=True)
class _Cast_StraightBevelDiffGearCompoundSystemDeflection:
    """Special nested class for casting StraightBevelDiffGearCompoundSystemDeflection to subclasses."""

    __parent__: "StraightBevelDiffGearCompoundSystemDeflection"

    @property
    def bevel_gear_compound_system_deflection(
        self: "CastSelf",
    ) -> "_3162.BevelGearCompoundSystemDeflection":
        return self.__parent__._cast(_3162.BevelGearCompoundSystemDeflection)

    @property
    def agma_gleason_conical_gear_compound_system_deflection(
        self: "CastSelf",
    ) -> "_3150.AGMAGleasonConicalGearCompoundSystemDeflection":
        from mastapy._private.system_model.analyses_and_results.system_deflections.compound import (
            _3150,
        )

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
    def straight_bevel_diff_gear_compound_system_deflection(
        self: "CastSelf",
    ) -> "StraightBevelDiffGearCompoundSystemDeflection":
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
class StraightBevelDiffGearCompoundSystemDeflection(
    _3162.BevelGearCompoundSystemDeflection
):
    """StraightBevelDiffGearCompoundSystemDeflection

    This is a mastapy class.
    """

    TYPE: ClassVar["Type"] = _STRAIGHT_BEVEL_DIFF_GEAR_COMPOUND_SYSTEM_DEFLECTION

    wrapped: "Any"

    def __post_init__(self: "Self") -> None:
        """Override of the post initialisation magic method."""
        if not hasattr(self.wrapped, "reference_count"):
            self.wrapped.reference_count = 0

        self.wrapped.reference_count += 1

    @property
    @exception_bridge
    def component_design(self: "Self") -> "_2827.StraightBevelDiffGear":
        """mastapy.system_model.part_model.gears.StraightBevelDiffGear

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
    def component_analysis_cases_ready(
        self: "Self",
    ) -> "List[_3109.StraightBevelDiffGearSystemDeflection]":
        """List[mastapy.system_model.analyses_and_results.system_deflections.StraightBevelDiffGearSystemDeflection]

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
    @exception_bridge
    def component_analysis_cases(
        self: "Self",
    ) -> "List[_3109.StraightBevelDiffGearSystemDeflection]":
        """List[mastapy.system_model.analyses_and_results.system_deflections.StraightBevelDiffGearSystemDeflection]

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
    def cast_to(self: "Self") -> "_Cast_StraightBevelDiffGearCompoundSystemDeflection":
        """Cast to another type.

        Returns:
            _Cast_StraightBevelDiffGearCompoundSystemDeflection
        """
        return _Cast_StraightBevelDiffGearCompoundSystemDeflection(self)
