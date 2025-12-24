"""GearSetMultibodyDynamicsAnalysis"""

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
from mastapy._private.system_model.analyses_and_results.mbd_analyses import _5827

_GEAR_SET_MULTIBODY_DYNAMICS_ANALYSIS = python_net_import(
    "SMT.MastaAPI.SystemModel.AnalysesAndResults.MBDAnalyses",
    "GearSetMultibodyDynamicsAnalysis",
)

if TYPE_CHECKING:
    from typing import Any, List, Type, TypeVar

    from mastapy._private.system_model.analyses_and_results import _2943, _2945, _2949
    from mastapy._private.system_model.analyses_and_results.analysis_cases import (
        _7941,
        _7945,
    )
    from mastapy._private.system_model.analyses_and_results.mbd_analyses import (
        _5711,
        _5717,
        _5727,
        _5732,
        _5746,
        _5749,
        _5764,
        _5770,
        _5773,
        _5775,
        _5780,
        _5788,
        _5791,
        _5794,
        _5805,
        _5810,
        _5830,
        _5837,
        _5840,
        _5858,
        _5861,
    )
    from mastapy._private.system_model.part_model.gears import _2813

    Self = TypeVar("Self", bound="GearSetMultibodyDynamicsAnalysis")
    CastSelf = TypeVar(
        "CastSelf",
        bound="GearSetMultibodyDynamicsAnalysis._Cast_GearSetMultibodyDynamicsAnalysis",
    )


__docformat__ = "restructuredtext en"
__all__ = ("GearSetMultibodyDynamicsAnalysis",)


@extended_dataclass(frozen=True, slots=True, weakref_slot=True)
class _Cast_GearSetMultibodyDynamicsAnalysis:
    """Special nested class for casting GearSetMultibodyDynamicsAnalysis to subclasses."""

    __parent__: "GearSetMultibodyDynamicsAnalysis"

    @property
    def specialised_assembly_multibody_dynamics_analysis(
        self: "CastSelf",
    ) -> "_5827.SpecialisedAssemblyMultibodyDynamicsAnalysis":
        return self.__parent__._cast(_5827.SpecialisedAssemblyMultibodyDynamicsAnalysis)

    @property
    def abstract_assembly_multibody_dynamics_analysis(
        self: "CastSelf",
    ) -> "_5711.AbstractAssemblyMultibodyDynamicsAnalysis":
        from mastapy._private.system_model.analyses_and_results.mbd_analyses import (
            _5711,
        )

        return self.__parent__._cast(_5711.AbstractAssemblyMultibodyDynamicsAnalysis)

    @property
    def part_multibody_dynamics_analysis(
        self: "CastSelf",
    ) -> "_5805.PartMultibodyDynamicsAnalysis":
        from mastapy._private.system_model.analyses_and_results.mbd_analyses import (
            _5805,
        )

        return self.__parent__._cast(_5805.PartMultibodyDynamicsAnalysis)

    @property
    def part_time_series_load_analysis_case(
        self: "CastSelf",
    ) -> "_7945.PartTimeSeriesLoadAnalysisCase":
        from mastapy._private.system_model.analyses_and_results.analysis_cases import (
            _7945,
        )

        return self.__parent__._cast(_7945.PartTimeSeriesLoadAnalysisCase)

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
    def agma_gleason_conical_gear_set_multibody_dynamics_analysis(
        self: "CastSelf",
    ) -> "_5717.AGMAGleasonConicalGearSetMultibodyDynamicsAnalysis":
        from mastapy._private.system_model.analyses_and_results.mbd_analyses import (
            _5717,
        )

        return self.__parent__._cast(
            _5717.AGMAGleasonConicalGearSetMultibodyDynamicsAnalysis
        )

    @property
    def bevel_differential_gear_set_multibody_dynamics_analysis(
        self: "CastSelf",
    ) -> "_5727.BevelDifferentialGearSetMultibodyDynamicsAnalysis":
        from mastapy._private.system_model.analyses_and_results.mbd_analyses import (
            _5727,
        )

        return self.__parent__._cast(
            _5727.BevelDifferentialGearSetMultibodyDynamicsAnalysis
        )

    @property
    def bevel_gear_set_multibody_dynamics_analysis(
        self: "CastSelf",
    ) -> "_5732.BevelGearSetMultibodyDynamicsAnalysis":
        from mastapy._private.system_model.analyses_and_results.mbd_analyses import (
            _5732,
        )

        return self.__parent__._cast(_5732.BevelGearSetMultibodyDynamicsAnalysis)

    @property
    def concept_gear_set_multibody_dynamics_analysis(
        self: "CastSelf",
    ) -> "_5746.ConceptGearSetMultibodyDynamicsAnalysis":
        from mastapy._private.system_model.analyses_and_results.mbd_analyses import (
            _5746,
        )

        return self.__parent__._cast(_5746.ConceptGearSetMultibodyDynamicsAnalysis)

    @property
    def conical_gear_set_multibody_dynamics_analysis(
        self: "CastSelf",
    ) -> "_5749.ConicalGearSetMultibodyDynamicsAnalysis":
        from mastapy._private.system_model.analyses_and_results.mbd_analyses import (
            _5749,
        )

        return self.__parent__._cast(_5749.ConicalGearSetMultibodyDynamicsAnalysis)

    @property
    def cylindrical_gear_set_multibody_dynamics_analysis(
        self: "CastSelf",
    ) -> "_5764.CylindricalGearSetMultibodyDynamicsAnalysis":
        from mastapy._private.system_model.analyses_and_results.mbd_analyses import (
            _5764,
        )

        return self.__parent__._cast(_5764.CylindricalGearSetMultibodyDynamicsAnalysis)

    @property
    def face_gear_set_multibody_dynamics_analysis(
        self: "CastSelf",
    ) -> "_5770.FaceGearSetMultibodyDynamicsAnalysis":
        from mastapy._private.system_model.analyses_and_results.mbd_analyses import (
            _5770,
        )

        return self.__parent__._cast(_5770.FaceGearSetMultibodyDynamicsAnalysis)

    @property
    def hypoid_gear_set_multibody_dynamics_analysis(
        self: "CastSelf",
    ) -> "_5780.HypoidGearSetMultibodyDynamicsAnalysis":
        from mastapy._private.system_model.analyses_and_results.mbd_analyses import (
            _5780,
        )

        return self.__parent__._cast(_5780.HypoidGearSetMultibodyDynamicsAnalysis)

    @property
    def klingelnberg_cyclo_palloid_conical_gear_set_multibody_dynamics_analysis(
        self: "CastSelf",
    ) -> "_5788.KlingelnbergCycloPalloidConicalGearSetMultibodyDynamicsAnalysis":
        from mastapy._private.system_model.analyses_and_results.mbd_analyses import (
            _5788,
        )

        return self.__parent__._cast(
            _5788.KlingelnbergCycloPalloidConicalGearSetMultibodyDynamicsAnalysis
        )

    @property
    def klingelnberg_cyclo_palloid_hypoid_gear_set_multibody_dynamics_analysis(
        self: "CastSelf",
    ) -> "_5791.KlingelnbergCycloPalloidHypoidGearSetMultibodyDynamicsAnalysis":
        from mastapy._private.system_model.analyses_and_results.mbd_analyses import (
            _5791,
        )

        return self.__parent__._cast(
            _5791.KlingelnbergCycloPalloidHypoidGearSetMultibodyDynamicsAnalysis
        )

    @property
    def klingelnberg_cyclo_palloid_spiral_bevel_gear_set_multibody_dynamics_analysis(
        self: "CastSelf",
    ) -> "_5794.KlingelnbergCycloPalloidSpiralBevelGearSetMultibodyDynamicsAnalysis":
        from mastapy._private.system_model.analyses_and_results.mbd_analyses import (
            _5794,
        )

        return self.__parent__._cast(
            _5794.KlingelnbergCycloPalloidSpiralBevelGearSetMultibodyDynamicsAnalysis
        )

    @property
    def planetary_gear_set_multibody_dynamics_analysis(
        self: "CastSelf",
    ) -> "_5810.PlanetaryGearSetMultibodyDynamicsAnalysis":
        from mastapy._private.system_model.analyses_and_results.mbd_analyses import (
            _5810,
        )

        return self.__parent__._cast(_5810.PlanetaryGearSetMultibodyDynamicsAnalysis)

    @property
    def spiral_bevel_gear_set_multibody_dynamics_analysis(
        self: "CastSelf",
    ) -> "_5830.SpiralBevelGearSetMultibodyDynamicsAnalysis":
        from mastapy._private.system_model.analyses_and_results.mbd_analyses import (
            _5830,
        )

        return self.__parent__._cast(_5830.SpiralBevelGearSetMultibodyDynamicsAnalysis)

    @property
    def straight_bevel_diff_gear_set_multibody_dynamics_analysis(
        self: "CastSelf",
    ) -> "_5837.StraightBevelDiffGearSetMultibodyDynamicsAnalysis":
        from mastapy._private.system_model.analyses_and_results.mbd_analyses import (
            _5837,
        )

        return self.__parent__._cast(
            _5837.StraightBevelDiffGearSetMultibodyDynamicsAnalysis
        )

    @property
    def straight_bevel_gear_set_multibody_dynamics_analysis(
        self: "CastSelf",
    ) -> "_5840.StraightBevelGearSetMultibodyDynamicsAnalysis":
        from mastapy._private.system_model.analyses_and_results.mbd_analyses import (
            _5840,
        )

        return self.__parent__._cast(
            _5840.StraightBevelGearSetMultibodyDynamicsAnalysis
        )

    @property
    def worm_gear_set_multibody_dynamics_analysis(
        self: "CastSelf",
    ) -> "_5858.WormGearSetMultibodyDynamicsAnalysis":
        from mastapy._private.system_model.analyses_and_results.mbd_analyses import (
            _5858,
        )

        return self.__parent__._cast(_5858.WormGearSetMultibodyDynamicsAnalysis)

    @property
    def zerol_bevel_gear_set_multibody_dynamics_analysis(
        self: "CastSelf",
    ) -> "_5861.ZerolBevelGearSetMultibodyDynamicsAnalysis":
        from mastapy._private.system_model.analyses_and_results.mbd_analyses import (
            _5861,
        )

        return self.__parent__._cast(_5861.ZerolBevelGearSetMultibodyDynamicsAnalysis)

    @property
    def gear_set_multibody_dynamics_analysis(
        self: "CastSelf",
    ) -> "GearSetMultibodyDynamicsAnalysis":
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
class GearSetMultibodyDynamicsAnalysis(
    _5827.SpecialisedAssemblyMultibodyDynamicsAnalysis
):
    """GearSetMultibodyDynamicsAnalysis

    This is a mastapy class.
    """

    TYPE: ClassVar["Type"] = _GEAR_SET_MULTIBODY_DYNAMICS_ANALYSIS

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
    def gears_multibody_dynamics_analysis(
        self: "Self",
    ) -> "List[_5775.GearMultibodyDynamicsAnalysis]":
        """List[mastapy.system_model.analyses_and_results.mbd_analyses.GearMultibodyDynamicsAnalysis]

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "GearsMultibodyDynamicsAnalysis")

        if temp is None:
            return None

        value = conversion.pn_to_mp_objects_in_list(temp)

        if value is None:
            return None

        return value

    @property
    @exception_bridge
    def meshes_multibody_dynamics_analysis(
        self: "Self",
    ) -> "List[_5773.GearMeshMultibodyDynamicsAnalysis]":
        """List[mastapy.system_model.analyses_and_results.mbd_analyses.GearMeshMultibodyDynamicsAnalysis]

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "MeshesMultibodyDynamicsAnalysis")

        if temp is None:
            return None

        value = conversion.pn_to_mp_objects_in_list(temp)

        if value is None:
            return None

        return value

    @property
    def cast_to(self: "Self") -> "_Cast_GearSetMultibodyDynamicsAnalysis":
        """Cast to another type.

        Returns:
            _Cast_GearSetMultibodyDynamicsAnalysis
        """
        return _Cast_GearSetMultibodyDynamicsAnalysis(self)
