"""AGMAGleasonConicalGearSetSystemDeflection"""

from __future__ import annotations

from typing import TYPE_CHECKING, ClassVar

from mastapy._private._internal.dataclasses import extended_dataclass
from mastapy._private._internal.exception_bridge import exception_bridge
from mastapy._private._internal.exceptions import CastException
from mastapy._private._internal.python_net import (
    python_net_import,
    pythonnet_method_call,
    pythonnet_property_get,
)
from mastapy._private._internal.type_enforcement import enforce_parameter_types

from mastapy._private._internal import constructor, conversion, utility
from mastapy._private.system_model.analyses_and_results.system_deflections import _3017

_AGMA_GLEASON_CONICAL_GEAR_SET_SYSTEM_DEFLECTION = python_net_import(
    "SMT.MastaAPI.SystemModel.AnalysesAndResults.SystemDeflections",
    "AGMAGleasonConicalGearSetSystemDeflection",
)

if TYPE_CHECKING:
    from typing import Any, List, Type, TypeVar

    from mastapy._private._internal.typing import PathLike

    from mastapy._private.system_model.analyses_and_results import _2943, _2945, _2949
    from mastapy._private.system_model.analyses_and_results.analysis_cases import (
        _7941,
        _7943,
        _7944,
    )
    from mastapy._private.system_model.analyses_and_results.power_flows import _4351
    from mastapy._private.system_model.analyses_and_results.system_deflections import (
        _2977,
        _2981,
        _2983,
        _2994,
        _2999,
        _3052,
        _3056,
        _3079,
        _3100,
        _3102,
        _3108,
        _3111,
        _3135,
    )
    from mastapy._private.system_model.part_model.gears import _2795

    Self = TypeVar("Self", bound="AGMAGleasonConicalGearSetSystemDeflection")
    CastSelf = TypeVar(
        "CastSelf",
        bound="AGMAGleasonConicalGearSetSystemDeflection._Cast_AGMAGleasonConicalGearSetSystemDeflection",
    )


__docformat__ = "restructuredtext en"
__all__ = ("AGMAGleasonConicalGearSetSystemDeflection",)


@extended_dataclass(frozen=True, slots=True, weakref_slot=True)
class _Cast_AGMAGleasonConicalGearSetSystemDeflection:
    """Special nested class for casting AGMAGleasonConicalGearSetSystemDeflection to subclasses."""

    __parent__: "AGMAGleasonConicalGearSetSystemDeflection"

    @property
    def conical_gear_set_system_deflection(
        self: "CastSelf",
    ) -> "_3017.ConicalGearSetSystemDeflection":
        return self.__parent__._cast(_3017.ConicalGearSetSystemDeflection)

    @property
    def gear_set_system_deflection(self: "CastSelf") -> "_3052.GearSetSystemDeflection":
        from mastapy._private.system_model.analyses_and_results.system_deflections import (
            _3052,
        )

        return self.__parent__._cast(_3052.GearSetSystemDeflection)

    @property
    def specialised_assembly_system_deflection(
        self: "CastSelf",
    ) -> "_3100.SpecialisedAssemblySystemDeflection":
        from mastapy._private.system_model.analyses_and_results.system_deflections import (
            _3100,
        )

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
    def hypoid_gear_set_system_deflection(
        self: "CastSelf",
    ) -> "_3056.HypoidGearSetSystemDeflection":
        from mastapy._private.system_model.analyses_and_results.system_deflections import (
            _3056,
        )

        return self.__parent__._cast(_3056.HypoidGearSetSystemDeflection)

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
    def zerol_bevel_gear_set_system_deflection(
        self: "CastSelf",
    ) -> "_3135.ZerolBevelGearSetSystemDeflection":
        from mastapy._private.system_model.analyses_and_results.system_deflections import (
            _3135,
        )

        return self.__parent__._cast(_3135.ZerolBevelGearSetSystemDeflection)

    @property
    def agma_gleason_conical_gear_set_system_deflection(
        self: "CastSelf",
    ) -> "AGMAGleasonConicalGearSetSystemDeflection":
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
class AGMAGleasonConicalGearSetSystemDeflection(_3017.ConicalGearSetSystemDeflection):
    """AGMAGleasonConicalGearSetSystemDeflection

    This is a mastapy class.
    """

    TYPE: ClassVar["Type"] = _AGMA_GLEASON_CONICAL_GEAR_SET_SYSTEM_DEFLECTION

    wrapped: "Any"

    def __post_init__(self: "Self") -> None:
        """Override of the post initialisation magic method."""
        if not hasattr(self.wrapped, "reference_count"):
            self.wrapped.reference_count = 0

        self.wrapped.reference_count += 1

    @property
    @exception_bridge
    def assembly_design(self: "Self") -> "_2795.AGMAGleasonConicalGearSet":
        """mastapy.system_model.part_model.gears.AGMAGleasonConicalGearSet

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
    def conical_gears_system_deflection(
        self: "Self",
    ) -> "List[_2983.AGMAGleasonConicalGearSystemDeflection]":
        """List[mastapy.system_model.analyses_and_results.system_deflections.AGMAGleasonConicalGearSystemDeflection]

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "ConicalGearsSystemDeflection")

        if temp is None:
            return None

        value = conversion.pn_to_mp_objects_in_list(temp)

        if value is None:
            return None

        return value

    @property
    @exception_bridge
    def agma_gleason_conical_gears_system_deflection(
        self: "Self",
    ) -> "List[_2983.AGMAGleasonConicalGearSystemDeflection]":
        """List[mastapy.system_model.analyses_and_results.system_deflections.AGMAGleasonConicalGearSystemDeflection]

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(
            self.wrapped, "AGMAGleasonConicalGearsSystemDeflection"
        )

        if temp is None:
            return None

        value = conversion.pn_to_mp_objects_in_list(temp)

        if value is None:
            return None

        return value

    @property
    @exception_bridge
    def conical_meshes_system_deflection(
        self: "Self",
    ) -> "List[_2981.AGMAGleasonConicalGearMeshSystemDeflection]":
        """List[mastapy.system_model.analyses_and_results.system_deflections.AGMAGleasonConicalGearMeshSystemDeflection]

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "ConicalMeshesSystemDeflection")

        if temp is None:
            return None

        value = conversion.pn_to_mp_objects_in_list(temp)

        if value is None:
            return None

        return value

    @property
    @exception_bridge
    def agma_gleason_conical_meshes_system_deflection(
        self: "Self",
    ) -> "List[_2981.AGMAGleasonConicalGearMeshSystemDeflection]":
        """List[mastapy.system_model.analyses_and_results.system_deflections.AGMAGleasonConicalGearMeshSystemDeflection]

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(
            self.wrapped, "AGMAGleasonConicalMeshesSystemDeflection"
        )

        if temp is None:
            return None

        value = conversion.pn_to_mp_objects_in_list(temp)

        if value is None:
            return None

        return value

    @property
    @exception_bridge
    def power_flow_results(self: "Self") -> "_4351.AGMAGleasonConicalGearSetPowerFlow":
        """mastapy.system_model.analyses_and_results.power_flows.AGMAGleasonConicalGearSetPowerFlow

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
    def export_misalignments(self: "Self", file_name: "PathLike") -> None:
        """Method does not return.

        Args:
            file_name (PathLike)
        """
        file_name = str(file_name)
        pythonnet_method_call(self.wrapped, "ExportMisalignments", file_name)

    @exception_bridge
    @enforce_parameter_types
    def export_misalignments_with_respect_to_cross_point_for_reference_fe_node(
        self: "Self", file_name: "PathLike"
    ) -> None:
        """Method does not return.

        Args:
            file_name (PathLike)
        """
        file_name = str(file_name)
        pythonnet_method_call(
            self.wrapped,
            "ExportMisalignmentsWithRespectToCrossPointForReferenceFENode",
            file_name,
        )

    @property
    def cast_to(self: "Self") -> "_Cast_AGMAGleasonConicalGearSetSystemDeflection":
        """Cast to another type.

        Returns:
            _Cast_AGMAGleasonConicalGearSetSystemDeflection
        """
        return _Cast_AGMAGleasonConicalGearSetSystemDeflection(self)
