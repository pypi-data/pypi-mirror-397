"""BevelGearSetCompoundSystemDeflection"""

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
    _3152,
)

_BEVEL_GEAR_SET_COMPOUND_SYSTEM_DEFLECTION = python_net_import(
    "SMT.MastaAPI.SystemModel.AnalysesAndResults.SystemDeflections.Compound",
    "BevelGearSetCompoundSystemDeflection",
)

if TYPE_CHECKING:
    from typing import Any, List, Type, TypeVar

    from mastapy._private.system_model.analyses_and_results import _2943
    from mastapy._private.system_model.analyses_and_results.analysis_cases import (
        _7939,
        _7942,
    )
    from mastapy._private.system_model.analyses_and_results.system_deflections import (
        _2999,
    )
    from mastapy._private.system_model.analyses_and_results.system_deflections.compound import (
        _3146,
        _3159,
        _3180,
        _3207,
        _3228,
        _3248,
        _3251,
        _3257,
        _3260,
        _3278,
    )

    Self = TypeVar("Self", bound="BevelGearSetCompoundSystemDeflection")
    CastSelf = TypeVar(
        "CastSelf",
        bound="BevelGearSetCompoundSystemDeflection._Cast_BevelGearSetCompoundSystemDeflection",
    )


__docformat__ = "restructuredtext en"
__all__ = ("BevelGearSetCompoundSystemDeflection",)


@extended_dataclass(frozen=True, slots=True, weakref_slot=True)
class _Cast_BevelGearSetCompoundSystemDeflection:
    """Special nested class for casting BevelGearSetCompoundSystemDeflection to subclasses."""

    __parent__: "BevelGearSetCompoundSystemDeflection"

    @property
    def agma_gleason_conical_gear_set_compound_system_deflection(
        self: "CastSelf",
    ) -> "_3152.AGMAGleasonConicalGearSetCompoundSystemDeflection":
        return self.__parent__._cast(
            _3152.AGMAGleasonConicalGearSetCompoundSystemDeflection
        )

    @property
    def conical_gear_set_compound_system_deflection(
        self: "CastSelf",
    ) -> "_3180.ConicalGearSetCompoundSystemDeflection":
        from mastapy._private.system_model.analyses_and_results.system_deflections.compound import (
            _3180,
        )

        return self.__parent__._cast(_3180.ConicalGearSetCompoundSystemDeflection)

    @property
    def gear_set_compound_system_deflection(
        self: "CastSelf",
    ) -> "_3207.GearSetCompoundSystemDeflection":
        from mastapy._private.system_model.analyses_and_results.system_deflections.compound import (
            _3207,
        )

        return self.__parent__._cast(_3207.GearSetCompoundSystemDeflection)

    @property
    def specialised_assembly_compound_system_deflection(
        self: "CastSelf",
    ) -> "_3248.SpecialisedAssemblyCompoundSystemDeflection":
        from mastapy._private.system_model.analyses_and_results.system_deflections.compound import (
            _3248,
        )

        return self.__parent__._cast(_3248.SpecialisedAssemblyCompoundSystemDeflection)

    @property
    def abstract_assembly_compound_system_deflection(
        self: "CastSelf",
    ) -> "_3146.AbstractAssemblyCompoundSystemDeflection":
        from mastapy._private.system_model.analyses_and_results.system_deflections.compound import (
            _3146,
        )

        return self.__parent__._cast(_3146.AbstractAssemblyCompoundSystemDeflection)

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
    def bevel_differential_gear_set_compound_system_deflection(
        self: "CastSelf",
    ) -> "_3159.BevelDifferentialGearSetCompoundSystemDeflection":
        from mastapy._private.system_model.analyses_and_results.system_deflections.compound import (
            _3159,
        )

        return self.__parent__._cast(
            _3159.BevelDifferentialGearSetCompoundSystemDeflection
        )

    @property
    def spiral_bevel_gear_set_compound_system_deflection(
        self: "CastSelf",
    ) -> "_3251.SpiralBevelGearSetCompoundSystemDeflection":
        from mastapy._private.system_model.analyses_and_results.system_deflections.compound import (
            _3251,
        )

        return self.__parent__._cast(_3251.SpiralBevelGearSetCompoundSystemDeflection)

    @property
    def straight_bevel_diff_gear_set_compound_system_deflection(
        self: "CastSelf",
    ) -> "_3257.StraightBevelDiffGearSetCompoundSystemDeflection":
        from mastapy._private.system_model.analyses_and_results.system_deflections.compound import (
            _3257,
        )

        return self.__parent__._cast(
            _3257.StraightBevelDiffGearSetCompoundSystemDeflection
        )

    @property
    def straight_bevel_gear_set_compound_system_deflection(
        self: "CastSelf",
    ) -> "_3260.StraightBevelGearSetCompoundSystemDeflection":
        from mastapy._private.system_model.analyses_and_results.system_deflections.compound import (
            _3260,
        )

        return self.__parent__._cast(_3260.StraightBevelGearSetCompoundSystemDeflection)

    @property
    def zerol_bevel_gear_set_compound_system_deflection(
        self: "CastSelf",
    ) -> "_3278.ZerolBevelGearSetCompoundSystemDeflection":
        from mastapy._private.system_model.analyses_and_results.system_deflections.compound import (
            _3278,
        )

        return self.__parent__._cast(_3278.ZerolBevelGearSetCompoundSystemDeflection)

    @property
    def bevel_gear_set_compound_system_deflection(
        self: "CastSelf",
    ) -> "BevelGearSetCompoundSystemDeflection":
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
class BevelGearSetCompoundSystemDeflection(
    _3152.AGMAGleasonConicalGearSetCompoundSystemDeflection
):
    """BevelGearSetCompoundSystemDeflection

    This is a mastapy class.
    """

    TYPE: ClassVar["Type"] = _BEVEL_GEAR_SET_COMPOUND_SYSTEM_DEFLECTION

    wrapped: "Any"

    def __post_init__(self: "Self") -> None:
        """Override of the post initialisation magic method."""
        if not hasattr(self.wrapped, "reference_count"):
            self.wrapped.reference_count = 0

        self.wrapped.reference_count += 1

    @property
    @exception_bridge
    def assembly_analysis_cases(
        self: "Self",
    ) -> "List[_2999.BevelGearSetSystemDeflection]":
        """List[mastapy.system_model.analyses_and_results.system_deflections.BevelGearSetSystemDeflection]

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "AssemblyAnalysisCases")

        if temp is None:
            return None

        value = conversion.pn_to_mp_objects_in_list(temp)

        if value is None:
            return None

        return value

    @property
    @exception_bridge
    def assembly_analysis_cases_ready(
        self: "Self",
    ) -> "List[_2999.BevelGearSetSystemDeflection]":
        """List[mastapy.system_model.analyses_and_results.system_deflections.BevelGearSetSystemDeflection]

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "AssemblyAnalysisCasesReady")

        if temp is None:
            return None

        value = conversion.pn_to_mp_objects_in_list(temp)

        if value is None:
            return None

        return value

    @property
    def cast_to(self: "Self") -> "_Cast_BevelGearSetCompoundSystemDeflection":
        """Cast to another type.

        Returns:
            _Cast_BevelGearSetCompoundSystemDeflection
        """
        return _Cast_BevelGearSetCompoundSystemDeflection(self)
