"""GearSetDynamicAnalysis"""

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
from mastapy._private.system_model.analyses_and_results.dynamic_analyses import _6743

_GEAR_SET_DYNAMIC_ANALYSIS = python_net_import(
    "SMT.MastaAPI.SystemModel.AnalysesAndResults.DynamicAnalyses",
    "GearSetDynamicAnalysis",
)

if TYPE_CHECKING:
    from typing import Any, List, Type, TypeVar

    from mastapy._private.system_model.analyses_and_results import _2943, _2945, _2949
    from mastapy._private.system_model.analyses_and_results.analysis_cases import (
        _7941,
        _7943,
        _7944,
    )
    from mastapy._private.system_model.analyses_and_results.dynamic_analyses import (
        _6641,
        _6647,
        _6654,
        _6659,
        _6672,
        _6675,
        _6690,
        _6698,
        _6701,
        _6702,
        _6707,
        _6711,
        _6714,
        _6717,
        _6724,
        _6729,
        _6746,
        _6752,
        _6755,
        _6770,
        _6773,
    )
    from mastapy._private.system_model.part_model.gears import _2813

    Self = TypeVar("Self", bound="GearSetDynamicAnalysis")
    CastSelf = TypeVar(
        "CastSelf", bound="GearSetDynamicAnalysis._Cast_GearSetDynamicAnalysis"
    )


__docformat__ = "restructuredtext en"
__all__ = ("GearSetDynamicAnalysis",)


@extended_dataclass(frozen=True, slots=True, weakref_slot=True)
class _Cast_GearSetDynamicAnalysis:
    """Special nested class for casting GearSetDynamicAnalysis to subclasses."""

    __parent__: "GearSetDynamicAnalysis"

    @property
    def specialised_assembly_dynamic_analysis(
        self: "CastSelf",
    ) -> "_6743.SpecialisedAssemblyDynamicAnalysis":
        return self.__parent__._cast(_6743.SpecialisedAssemblyDynamicAnalysis)

    @property
    def abstract_assembly_dynamic_analysis(
        self: "CastSelf",
    ) -> "_6641.AbstractAssemblyDynamicAnalysis":
        from mastapy._private.system_model.analyses_and_results.dynamic_analyses import (
            _6641,
        )

        return self.__parent__._cast(_6641.AbstractAssemblyDynamicAnalysis)

    @property
    def part_dynamic_analysis(self: "CastSelf") -> "_6724.PartDynamicAnalysis":
        from mastapy._private.system_model.analyses_and_results.dynamic_analyses import (
            _6724,
        )

        return self.__parent__._cast(_6724.PartDynamicAnalysis)

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
    def agma_gleason_conical_gear_set_dynamic_analysis(
        self: "CastSelf",
    ) -> "_6647.AGMAGleasonConicalGearSetDynamicAnalysis":
        from mastapy._private.system_model.analyses_and_results.dynamic_analyses import (
            _6647,
        )

        return self.__parent__._cast(_6647.AGMAGleasonConicalGearSetDynamicAnalysis)

    @property
    def bevel_differential_gear_set_dynamic_analysis(
        self: "CastSelf",
    ) -> "_6654.BevelDifferentialGearSetDynamicAnalysis":
        from mastapy._private.system_model.analyses_and_results.dynamic_analyses import (
            _6654,
        )

        return self.__parent__._cast(_6654.BevelDifferentialGearSetDynamicAnalysis)

    @property
    def bevel_gear_set_dynamic_analysis(
        self: "CastSelf",
    ) -> "_6659.BevelGearSetDynamicAnalysis":
        from mastapy._private.system_model.analyses_and_results.dynamic_analyses import (
            _6659,
        )

        return self.__parent__._cast(_6659.BevelGearSetDynamicAnalysis)

    @property
    def concept_gear_set_dynamic_analysis(
        self: "CastSelf",
    ) -> "_6672.ConceptGearSetDynamicAnalysis":
        from mastapy._private.system_model.analyses_and_results.dynamic_analyses import (
            _6672,
        )

        return self.__parent__._cast(_6672.ConceptGearSetDynamicAnalysis)

    @property
    def conical_gear_set_dynamic_analysis(
        self: "CastSelf",
    ) -> "_6675.ConicalGearSetDynamicAnalysis":
        from mastapy._private.system_model.analyses_and_results.dynamic_analyses import (
            _6675,
        )

        return self.__parent__._cast(_6675.ConicalGearSetDynamicAnalysis)

    @property
    def cylindrical_gear_set_dynamic_analysis(
        self: "CastSelf",
    ) -> "_6690.CylindricalGearSetDynamicAnalysis":
        from mastapy._private.system_model.analyses_and_results.dynamic_analyses import (
            _6690,
        )

        return self.__parent__._cast(_6690.CylindricalGearSetDynamicAnalysis)

    @property
    def face_gear_set_dynamic_analysis(
        self: "CastSelf",
    ) -> "_6698.FaceGearSetDynamicAnalysis":
        from mastapy._private.system_model.analyses_and_results.dynamic_analyses import (
            _6698,
        )

        return self.__parent__._cast(_6698.FaceGearSetDynamicAnalysis)

    @property
    def hypoid_gear_set_dynamic_analysis(
        self: "CastSelf",
    ) -> "_6707.HypoidGearSetDynamicAnalysis":
        from mastapy._private.system_model.analyses_and_results.dynamic_analyses import (
            _6707,
        )

        return self.__parent__._cast(_6707.HypoidGearSetDynamicAnalysis)

    @property
    def klingelnberg_cyclo_palloid_conical_gear_set_dynamic_analysis(
        self: "CastSelf",
    ) -> "_6711.KlingelnbergCycloPalloidConicalGearSetDynamicAnalysis":
        from mastapy._private.system_model.analyses_and_results.dynamic_analyses import (
            _6711,
        )

        return self.__parent__._cast(
            _6711.KlingelnbergCycloPalloidConicalGearSetDynamicAnalysis
        )

    @property
    def klingelnberg_cyclo_palloid_hypoid_gear_set_dynamic_analysis(
        self: "CastSelf",
    ) -> "_6714.KlingelnbergCycloPalloidHypoidGearSetDynamicAnalysis":
        from mastapy._private.system_model.analyses_and_results.dynamic_analyses import (
            _6714,
        )

        return self.__parent__._cast(
            _6714.KlingelnbergCycloPalloidHypoidGearSetDynamicAnalysis
        )

    @property
    def klingelnberg_cyclo_palloid_spiral_bevel_gear_set_dynamic_analysis(
        self: "CastSelf",
    ) -> "_6717.KlingelnbergCycloPalloidSpiralBevelGearSetDynamicAnalysis":
        from mastapy._private.system_model.analyses_and_results.dynamic_analyses import (
            _6717,
        )

        return self.__parent__._cast(
            _6717.KlingelnbergCycloPalloidSpiralBevelGearSetDynamicAnalysis
        )

    @property
    def planetary_gear_set_dynamic_analysis(
        self: "CastSelf",
    ) -> "_6729.PlanetaryGearSetDynamicAnalysis":
        from mastapy._private.system_model.analyses_and_results.dynamic_analyses import (
            _6729,
        )

        return self.__parent__._cast(_6729.PlanetaryGearSetDynamicAnalysis)

    @property
    def spiral_bevel_gear_set_dynamic_analysis(
        self: "CastSelf",
    ) -> "_6746.SpiralBevelGearSetDynamicAnalysis":
        from mastapy._private.system_model.analyses_and_results.dynamic_analyses import (
            _6746,
        )

        return self.__parent__._cast(_6746.SpiralBevelGearSetDynamicAnalysis)

    @property
    def straight_bevel_diff_gear_set_dynamic_analysis(
        self: "CastSelf",
    ) -> "_6752.StraightBevelDiffGearSetDynamicAnalysis":
        from mastapy._private.system_model.analyses_and_results.dynamic_analyses import (
            _6752,
        )

        return self.__parent__._cast(_6752.StraightBevelDiffGearSetDynamicAnalysis)

    @property
    def straight_bevel_gear_set_dynamic_analysis(
        self: "CastSelf",
    ) -> "_6755.StraightBevelGearSetDynamicAnalysis":
        from mastapy._private.system_model.analyses_and_results.dynamic_analyses import (
            _6755,
        )

        return self.__parent__._cast(_6755.StraightBevelGearSetDynamicAnalysis)

    @property
    def worm_gear_set_dynamic_analysis(
        self: "CastSelf",
    ) -> "_6770.WormGearSetDynamicAnalysis":
        from mastapy._private.system_model.analyses_and_results.dynamic_analyses import (
            _6770,
        )

        return self.__parent__._cast(_6770.WormGearSetDynamicAnalysis)

    @property
    def zerol_bevel_gear_set_dynamic_analysis(
        self: "CastSelf",
    ) -> "_6773.ZerolBevelGearSetDynamicAnalysis":
        from mastapy._private.system_model.analyses_and_results.dynamic_analyses import (
            _6773,
        )

        return self.__parent__._cast(_6773.ZerolBevelGearSetDynamicAnalysis)

    @property
    def gear_set_dynamic_analysis(self: "CastSelf") -> "GearSetDynamicAnalysis":
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
class GearSetDynamicAnalysis(_6743.SpecialisedAssemblyDynamicAnalysis):
    """GearSetDynamicAnalysis

    This is a mastapy class.
    """

    TYPE: ClassVar["Type"] = _GEAR_SET_DYNAMIC_ANALYSIS

    wrapped: "Any"

    def __post_init__(self: "Self") -> None:
        """Override of the post initialisation magic method."""
        if not hasattr(self.wrapped, "reference_count"):
            self.wrapped.reference_count = 0

        self.wrapped.reference_count += 1

    @property
    @exception_bridge
    def assembly_design(self: "Self") -> "_2813.GearSet":
        """mastapy.system_model.part_model.gears.GearSet

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "AssemblyDesign")

        if temp is None:
            return None

        type_ = temp.GetType()
        return constructor.new(type_.Namespace, type_.Name)(temp)

    @property
    @exception_bridge
    def gears_dynamic_analysis(self: "Self") -> "List[_6701.GearDynamicAnalysis]":
        """List[mastapy.system_model.analyses_and_results.dynamic_analyses.GearDynamicAnalysis]

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "GearsDynamicAnalysis")

        if temp is None:
            return None

        value = conversion.pn_to_mp_objects_in_list(temp)

        if value is None:
            return None

        return value

    @property
    @exception_bridge
    def meshes_dynamic_analysis(self: "Self") -> "List[_6702.GearMeshDynamicAnalysis]":
        """List[mastapy.system_model.analyses_and_results.dynamic_analyses.GearMeshDynamicAnalysis]

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "MeshesDynamicAnalysis")

        if temp is None:
            return None

        value = conversion.pn_to_mp_objects_in_list(temp)

        if value is None:
            return None

        return value

    @property
    def cast_to(self: "Self") -> "_Cast_GearSetDynamicAnalysis":
        """Cast to another type.

        Returns:
            _Cast_GearSetDynamicAnalysis
        """
        return _Cast_GearSetDynamicAnalysis(self)
