"""GearSetSystemDeflection"""

from __future__ import annotations

from typing import TYPE_CHECKING, ClassVar

from mastapy._private._internal.dataclasses import extended_dataclass
from mastapy._private._internal.exception_bridge import exception_bridge
from mastapy._private._internal.exceptions import CastException
from mastapy._private._internal.python_net import (
    python_net_import,
    pythonnet_method_call,
    pythonnet_method_call_overload,
    pythonnet_property_get,
)
from mastapy._private._internal.type_enforcement import enforce_parameter_types

from mastapy._private._internal import constructor, conversion, utility
from mastapy._private.system_model.analyses_and_results.system_deflections import _3100

_GEAR_SET_IMPLEMENTATION_DETAIL = python_net_import(
    "SMT.MastaAPI.Gears.Analysis", "GearSetImplementationDetail"
)
_GEAR_SET_MODES = python_net_import("SMT.MastaAPI.Gears", "GearSetModes")
_TASK_PROGRESS = python_net_import("SMT.MastaAPIUtility", "TaskProgress")
_BOOLEAN = python_net_import("System", "Boolean")
_GEAR_SET_SYSTEM_DEFLECTION = python_net_import(
    "SMT.MastaAPI.SystemModel.AnalysesAndResults.SystemDeflections",
    "GearSetSystemDeflection",
)

if TYPE_CHECKING:
    from typing import Any, List, Type, TypeVar

    from mastapy._private import _7955
    from mastapy._private.gears import _436
    from mastapy._private.gears.analysis import _1374, _1377
    from mastapy._private.gears.rating import _476
    from mastapy._private.system_model.analyses_and_results import _2943, _2945, _2949
    from mastapy._private.system_model.analyses_and_results.analysis_cases import (
        _7941,
        _7943,
        _7944,
    )
    from mastapy._private.system_model.analyses_and_results.power_flows import _4408
    from mastapy._private.system_model.analyses_and_results.system_deflections import (
        _2977,
        _2982,
        _2994,
        _2999,
        _3013,
        _3017,
        _3034,
        _3035,
        _3036,
        _3047,
        _3051,
        _3053,
        _3056,
        _3061,
        _3064,
        _3067,
        _3079,
        _3102,
        _3108,
        _3111,
        _3132,
        _3135,
    )
    from mastapy._private.system_model.part_model.gears import _2813

    Self = TypeVar("Self", bound="GearSetSystemDeflection")
    CastSelf = TypeVar(
        "CastSelf", bound="GearSetSystemDeflection._Cast_GearSetSystemDeflection"
    )


__docformat__ = "restructuredtext en"
__all__ = ("GearSetSystemDeflection",)


@extended_dataclass(frozen=True, slots=True, weakref_slot=True)
class _Cast_GearSetSystemDeflection:
    """Special nested class for casting GearSetSystemDeflection to subclasses."""

    __parent__: "GearSetSystemDeflection"

    @property
    def specialised_assembly_system_deflection(
        self: "CastSelf",
    ) -> "_3100.SpecialisedAssemblySystemDeflection":
        return self.__parent__._cast(_3100.SpecialisedAssemblySystemDeflection)

    @property
    def abstract_assembly_system_deflection(
        self: "CastSelf",
    ) -> "_2977.AbstractAssemblySystemDeflection":
        from mastapy._private.system_model.analyses_and_results.system_deflections import (
            _2977,
        )

        return self.__parent__._cast(_2977.AbstractAssemblySystemDeflection)

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
    def agma_gleason_conical_gear_set_system_deflection(
        self: "CastSelf",
    ) -> "_2982.AGMAGleasonConicalGearSetSystemDeflection":
        from mastapy._private.system_model.analyses_and_results.system_deflections import (
            _2982,
        )

        return self.__parent__._cast(_2982.AGMAGleasonConicalGearSetSystemDeflection)

    @property
    def bevel_differential_gear_set_system_deflection(
        self: "CastSelf",
    ) -> "_2994.BevelDifferentialGearSetSystemDeflection":
        from mastapy._private.system_model.analyses_and_results.system_deflections import (
            _2994,
        )

        return self.__parent__._cast(_2994.BevelDifferentialGearSetSystemDeflection)

    @property
    def bevel_gear_set_system_deflection(
        self: "CastSelf",
    ) -> "_2999.BevelGearSetSystemDeflection":
        from mastapy._private.system_model.analyses_and_results.system_deflections import (
            _2999,
        )

        return self.__parent__._cast(_2999.BevelGearSetSystemDeflection)

    @property
    def concept_gear_set_system_deflection(
        self: "CastSelf",
    ) -> "_3013.ConceptGearSetSystemDeflection":
        from mastapy._private.system_model.analyses_and_results.system_deflections import (
            _3013,
        )

        return self.__parent__._cast(_3013.ConceptGearSetSystemDeflection)

    @property
    def conical_gear_set_system_deflection(
        self: "CastSelf",
    ) -> "_3017.ConicalGearSetSystemDeflection":
        from mastapy._private.system_model.analyses_and_results.system_deflections import (
            _3017,
        )

        return self.__parent__._cast(_3017.ConicalGearSetSystemDeflection)

    @property
    def cylindrical_gear_set_system_deflection(
        self: "CastSelf",
    ) -> "_3034.CylindricalGearSetSystemDeflection":
        from mastapy._private.system_model.analyses_and_results.system_deflections import (
            _3034,
        )

        return self.__parent__._cast(_3034.CylindricalGearSetSystemDeflection)

    @property
    def cylindrical_gear_set_system_deflection_timestep(
        self: "CastSelf",
    ) -> "_3035.CylindricalGearSetSystemDeflectionTimestep":
        from mastapy._private.system_model.analyses_and_results.system_deflections import (
            _3035,
        )

        return self.__parent__._cast(_3035.CylindricalGearSetSystemDeflectionTimestep)

    @property
    def cylindrical_gear_set_system_deflection_with_ltca_results(
        self: "CastSelf",
    ) -> "_3036.CylindricalGearSetSystemDeflectionWithLTCAResults":
        from mastapy._private.system_model.analyses_and_results.system_deflections import (
            _3036,
        )

        return self.__parent__._cast(
            _3036.CylindricalGearSetSystemDeflectionWithLTCAResults
        )

    @property
    def face_gear_set_system_deflection(
        self: "CastSelf",
    ) -> "_3047.FaceGearSetSystemDeflection":
        from mastapy._private.system_model.analyses_and_results.system_deflections import (
            _3047,
        )

        return self.__parent__._cast(_3047.FaceGearSetSystemDeflection)

    @property
    def hypoid_gear_set_system_deflection(
        self: "CastSelf",
    ) -> "_3056.HypoidGearSetSystemDeflection":
        from mastapy._private.system_model.analyses_and_results.system_deflections import (
            _3056,
        )

        return self.__parent__._cast(_3056.HypoidGearSetSystemDeflection)

    @property
    def klingelnberg_cyclo_palloid_conical_gear_set_system_deflection(
        self: "CastSelf",
    ) -> "_3061.KlingelnbergCycloPalloidConicalGearSetSystemDeflection":
        from mastapy._private.system_model.analyses_and_results.system_deflections import (
            _3061,
        )

        return self.__parent__._cast(
            _3061.KlingelnbergCycloPalloidConicalGearSetSystemDeflection
        )

    @property
    def klingelnberg_cyclo_palloid_hypoid_gear_set_system_deflection(
        self: "CastSelf",
    ) -> "_3064.KlingelnbergCycloPalloidHypoidGearSetSystemDeflection":
        from mastapy._private.system_model.analyses_and_results.system_deflections import (
            _3064,
        )

        return self.__parent__._cast(
            _3064.KlingelnbergCycloPalloidHypoidGearSetSystemDeflection
        )

    @property
    def klingelnberg_cyclo_palloid_spiral_bevel_gear_set_system_deflection(
        self: "CastSelf",
    ) -> "_3067.KlingelnbergCycloPalloidSpiralBevelGearSetSystemDeflection":
        from mastapy._private.system_model.analyses_and_results.system_deflections import (
            _3067,
        )

        return self.__parent__._cast(
            _3067.KlingelnbergCycloPalloidSpiralBevelGearSetSystemDeflection
        )

    @property
    def spiral_bevel_gear_set_system_deflection(
        self: "CastSelf",
    ) -> "_3102.SpiralBevelGearSetSystemDeflection":
        from mastapy._private.system_model.analyses_and_results.system_deflections import (
            _3102,
        )

        return self.__parent__._cast(_3102.SpiralBevelGearSetSystemDeflection)

    @property
    def straight_bevel_diff_gear_set_system_deflection(
        self: "CastSelf",
    ) -> "_3108.StraightBevelDiffGearSetSystemDeflection":
        from mastapy._private.system_model.analyses_and_results.system_deflections import (
            _3108,
        )

        return self.__parent__._cast(_3108.StraightBevelDiffGearSetSystemDeflection)

    @property
    def straight_bevel_gear_set_system_deflection(
        self: "CastSelf",
    ) -> "_3111.StraightBevelGearSetSystemDeflection":
        from mastapy._private.system_model.analyses_and_results.system_deflections import (
            _3111,
        )

        return self.__parent__._cast(_3111.StraightBevelGearSetSystemDeflection)

    @property
    def worm_gear_set_system_deflection(
        self: "CastSelf",
    ) -> "_3132.WormGearSetSystemDeflection":
        from mastapy._private.system_model.analyses_and_results.system_deflections import (
            _3132,
        )

        return self.__parent__._cast(_3132.WormGearSetSystemDeflection)

    @property
    def zerol_bevel_gear_set_system_deflection(
        self: "CastSelf",
    ) -> "_3135.ZerolBevelGearSetSystemDeflection":
        from mastapy._private.system_model.analyses_and_results.system_deflections import (
            _3135,
        )

        return self.__parent__._cast(_3135.ZerolBevelGearSetSystemDeflection)

    @property
    def gear_set_system_deflection(self: "CastSelf") -> "GearSetSystemDeflection":
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
class GearSetSystemDeflection(_3100.SpecialisedAssemblySystemDeflection):
    """GearSetSystemDeflection

    This is a mastapy class.
    """

    TYPE: ClassVar["Type"] = _GEAR_SET_SYSTEM_DEFLECTION

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
    def rating(self: "Self") -> "_476.GearSetRating":
        """mastapy.gears.rating.GearSetRating

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "Rating")

        if temp is None:
            return None

        type_ = temp.GetType()
        return constructor.new(type_.Namespace, type_.Name)(temp)

    @property
    @exception_bridge
    def gears_system_deflection(self: "Self") -> "List[_3053.GearSystemDeflection]":
        """List[mastapy.system_model.analyses_and_results.system_deflections.GearSystemDeflection]

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "GearsSystemDeflection")

        if temp is None:
            return None

        value = conversion.pn_to_mp_objects_in_list(temp)

        if value is None:
            return None

        return value

    @property
    @exception_bridge
    def meshes_system_deflection(
        self: "Self",
    ) -> "List[_3051.GearMeshSystemDeflection]":
        """List[mastapy.system_model.analyses_and_results.system_deflections.GearMeshSystemDeflection]

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "MeshesSystemDeflection")

        if temp is None:
            return None

        value = conversion.pn_to_mp_objects_in_list(temp)

        if value is None:
            return None

        return value

    @property
    @exception_bridge
    def power_flow_results(self: "Self") -> "_4408.GearSetPowerFlow":
        """mastapy.system_model.analyses_and_results.power_flows.GearSetPowerFlow

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "PowerFlowResults")

        if temp is None:
            return None

        type_ = temp.GetType()
        return constructor.new(type_.Namespace, type_.Name)(temp)

    @exception_bridge
    @enforce_parameter_types
    def analysis_for(
        self: "Self",
        gear_set_imp_detail: "_1377.GearSetImplementationDetail",
        gear_set_mode: "_436.GearSetModes",
    ) -> "_1374.GearSetImplementationAnalysis":
        """mastapy.gears.analysis.GearSetImplementationAnalysis

        Args:
            gear_set_imp_detail (mastapy.gears.analysis.GearSetImplementationDetail)
            gear_set_mode (mastapy.gears.GearSetModes)
        """
        gear_set_mode = conversion.mp_to_pn_enum(
            gear_set_mode, "SMT.MastaAPI.Gears.GearSetModes"
        )
        method_result = pythonnet_method_call(
            self.wrapped,
            "AnalysisFor",
            gear_set_imp_detail.wrapped if gear_set_imp_detail else None,
            gear_set_mode,
        )
        type_ = method_result.GetType()
        return (
            constructor.new(type_.Namespace, type_.Name)(method_result)
            if method_result is not None
            else None
        )

    @exception_bridge
    @enforce_parameter_types
    def implementation_detail_results_failed_for(
        self: "Self",
        gear_set_imp_detail: "_1377.GearSetImplementationDetail",
        gear_set_mode: "_436.GearSetModes",
    ) -> "bool":
        """bool

        Args:
            gear_set_imp_detail (mastapy.gears.analysis.GearSetImplementationDetail)
            gear_set_mode (mastapy.gears.GearSetModes)
        """
        gear_set_mode = conversion.mp_to_pn_enum(
            gear_set_mode, "SMT.MastaAPI.Gears.GearSetModes"
        )
        method_result = pythonnet_method_call(
            self.wrapped,
            "ImplementationDetailResultsFailedFor",
            gear_set_imp_detail.wrapped if gear_set_imp_detail else None,
            gear_set_mode,
        )
        return method_result

    @exception_bridge
    @enforce_parameter_types
    def perform_implementation_detail_analysis_with_progress(
        self: "Self",
        imp_detail: "_1377.GearSetImplementationDetail",
        gear_set_mode: "_436.GearSetModes",
        progress: "_7955.TaskProgress",
        run_all_planetary_meshes: "bool" = True,
    ) -> None:
        """Method does not return.

        Args:
            imp_detail (mastapy.gears.analysis.GearSetImplementationDetail)
            gear_set_mode (mastapy.gears.GearSetModes)
            progress (mastapy.TaskProgress)
            run_all_planetary_meshes (bool, optional)
        """
        gear_set_mode = conversion.mp_to_pn_enum(
            gear_set_mode, "SMT.MastaAPI.Gears.GearSetModes"
        )
        run_all_planetary_meshes = bool(run_all_planetary_meshes)
        pythonnet_method_call_overload(
            self.wrapped,
            "PerformImplementationDetailAnalysis",
            [
                _GEAR_SET_IMPLEMENTATION_DETAIL,
                _GEAR_SET_MODES,
                _TASK_PROGRESS,
                _BOOLEAN,
            ],
            imp_detail.wrapped if imp_detail else None,
            gear_set_mode,
            progress.wrapped if progress else None,
            run_all_planetary_meshes if run_all_planetary_meshes else False,
        )

    @exception_bridge
    @enforce_parameter_types
    def perform_implementation_detail_analysis(
        self: "Self",
        imp_detail: "_1377.GearSetImplementationDetail",
        gear_set_mode: "_436.GearSetModes",
        run_all_planetary_meshes: "bool" = True,
    ) -> None:
        """Method does not return.

        Args:
            imp_detail (mastapy.gears.analysis.GearSetImplementationDetail)
            gear_set_mode (mastapy.gears.GearSetModes)
            run_all_planetary_meshes (bool, optional)
        """
        gear_set_mode = conversion.mp_to_pn_enum(
            gear_set_mode, "SMT.MastaAPI.Gears.GearSetModes"
        )
        run_all_planetary_meshes = bool(run_all_planetary_meshes)
        pythonnet_method_call_overload(
            self.wrapped,
            "PerformImplementationDetailAnalysis",
            [_GEAR_SET_IMPLEMENTATION_DETAIL, _GEAR_SET_MODES, _BOOLEAN],
            imp_detail.wrapped if imp_detail else None,
            gear_set_mode,
            run_all_planetary_meshes if run_all_planetary_meshes else False,
        )

    @property
    def cast_to(self: "Self") -> "_Cast_GearSetSystemDeflection":
        """Cast to another type.

        Returns:
            _Cast_GearSetSystemDeflection
        """
        return _Cast_GearSetSystemDeflection(self)
