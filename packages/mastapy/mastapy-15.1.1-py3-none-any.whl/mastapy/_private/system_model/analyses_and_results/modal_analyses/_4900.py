"""AGMAGleasonConicalGearSetModalAnalysis"""

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
from mastapy._private.system_model.analyses_and_results.modal_analyses import _4928

_AGMA_GLEASON_CONICAL_GEAR_SET_MODAL_ANALYSIS = python_net_import(
    "SMT.MastaAPI.SystemModel.AnalysesAndResults.ModalAnalyses",
    "AGMAGleasonConicalGearSetModalAnalysis",
)

if TYPE_CHECKING:
    from typing import Any, List, Type, TypeVar

    from mastapy._private.system_model.analyses_and_results import _2943, _2945, _2949
    from mastapy._private.system_model.analyses_and_results.analysis_cases import (
        _7941,
        _7944,
    )
    from mastapy._private.system_model.analyses_and_results.modal_analyses import (
        _4894,
        _4898,
        _4899,
        _4907,
        _4912,
        _4959,
        _4963,
        _4987,
        _5007,
        _5010,
        _5016,
        _5019,
        _5040,
    )
    from mastapy._private.system_model.analyses_and_results.system_deflections import (
        _2982,
    )
    from mastapy._private.system_model.part_model.gears import _2795

    Self = TypeVar("Self", bound="AGMAGleasonConicalGearSetModalAnalysis")
    CastSelf = TypeVar(
        "CastSelf",
        bound="AGMAGleasonConicalGearSetModalAnalysis._Cast_AGMAGleasonConicalGearSetModalAnalysis",
    )


__docformat__ = "restructuredtext en"
__all__ = ("AGMAGleasonConicalGearSetModalAnalysis",)


@extended_dataclass(frozen=True, slots=True, weakref_slot=True)
class _Cast_AGMAGleasonConicalGearSetModalAnalysis:
    """Special nested class for casting AGMAGleasonConicalGearSetModalAnalysis to subclasses."""

    __parent__: "AGMAGleasonConicalGearSetModalAnalysis"

    @property
    def conical_gear_set_modal_analysis(
        self: "CastSelf",
    ) -> "_4928.ConicalGearSetModalAnalysis":
        return self.__parent__._cast(_4928.ConicalGearSetModalAnalysis)

    @property
    def gear_set_modal_analysis(self: "CastSelf") -> "_4959.GearSetModalAnalysis":
        from mastapy._private.system_model.analyses_and_results.modal_analyses import (
            _4959,
        )

        return self.__parent__._cast(_4959.GearSetModalAnalysis)

    @property
    def specialised_assembly_modal_analysis(
        self: "CastSelf",
    ) -> "_5007.SpecialisedAssemblyModalAnalysis":
        from mastapy._private.system_model.analyses_and_results.modal_analyses import (
            _5007,
        )

        return self.__parent__._cast(_5007.SpecialisedAssemblyModalAnalysis)

    @property
    def abstract_assembly_modal_analysis(
        self: "CastSelf",
    ) -> "_4894.AbstractAssemblyModalAnalysis":
        from mastapy._private.system_model.analyses_and_results.modal_analyses import (
            _4894,
        )

        return self.__parent__._cast(_4894.AbstractAssemblyModalAnalysis)

    @property
    def part_modal_analysis(self: "CastSelf") -> "_4987.PartModalAnalysis":
        from mastapy._private.system_model.analyses_and_results.modal_analyses import (
            _4987,
        )

        return self.__parent__._cast(_4987.PartModalAnalysis)

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
    def bevel_differential_gear_set_modal_analysis(
        self: "CastSelf",
    ) -> "_4907.BevelDifferentialGearSetModalAnalysis":
        from mastapy._private.system_model.analyses_and_results.modal_analyses import (
            _4907,
        )

        return self.__parent__._cast(_4907.BevelDifferentialGearSetModalAnalysis)

    @property
    def bevel_gear_set_modal_analysis(
        self: "CastSelf",
    ) -> "_4912.BevelGearSetModalAnalysis":
        from mastapy._private.system_model.analyses_and_results.modal_analyses import (
            _4912,
        )

        return self.__parent__._cast(_4912.BevelGearSetModalAnalysis)

    @property
    def hypoid_gear_set_modal_analysis(
        self: "CastSelf",
    ) -> "_4963.HypoidGearSetModalAnalysis":
        from mastapy._private.system_model.analyses_and_results.modal_analyses import (
            _4963,
        )

        return self.__parent__._cast(_4963.HypoidGearSetModalAnalysis)

    @property
    def spiral_bevel_gear_set_modal_analysis(
        self: "CastSelf",
    ) -> "_5010.SpiralBevelGearSetModalAnalysis":
        from mastapy._private.system_model.analyses_and_results.modal_analyses import (
            _5010,
        )

        return self.__parent__._cast(_5010.SpiralBevelGearSetModalAnalysis)

    @property
    def straight_bevel_diff_gear_set_modal_analysis(
        self: "CastSelf",
    ) -> "_5016.StraightBevelDiffGearSetModalAnalysis":
        from mastapy._private.system_model.analyses_and_results.modal_analyses import (
            _5016,
        )

        return self.__parent__._cast(_5016.StraightBevelDiffGearSetModalAnalysis)

    @property
    def straight_bevel_gear_set_modal_analysis(
        self: "CastSelf",
    ) -> "_5019.StraightBevelGearSetModalAnalysis":
        from mastapy._private.system_model.analyses_and_results.modal_analyses import (
            _5019,
        )

        return self.__parent__._cast(_5019.StraightBevelGearSetModalAnalysis)

    @property
    def zerol_bevel_gear_set_modal_analysis(
        self: "CastSelf",
    ) -> "_5040.ZerolBevelGearSetModalAnalysis":
        from mastapy._private.system_model.analyses_and_results.modal_analyses import (
            _5040,
        )

        return self.__parent__._cast(_5040.ZerolBevelGearSetModalAnalysis)

    @property
    def agma_gleason_conical_gear_set_modal_analysis(
        self: "CastSelf",
    ) -> "AGMAGleasonConicalGearSetModalAnalysis":
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
class AGMAGleasonConicalGearSetModalAnalysis(_4928.ConicalGearSetModalAnalysis):
    """AGMAGleasonConicalGearSetModalAnalysis

    This is a mastapy class.
    """

    TYPE: ClassVar["Type"] = _AGMA_GLEASON_CONICAL_GEAR_SET_MODAL_ANALYSIS

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
    def conical_gears_modal_analysis(
        self: "Self",
    ) -> "List[_4899.AGMAGleasonConicalGearModalAnalysis]":
        """List[mastapy.system_model.analyses_and_results.modal_analyses.AGMAGleasonConicalGearModalAnalysis]

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "ConicalGearsModalAnalysis")

        if temp is None:
            return None

        value = conversion.pn_to_mp_objects_in_list(temp)

        if value is None:
            return None

        return value

    @property
    @exception_bridge
    def agma_gleason_conical_gears_modal_analysis(
        self: "Self",
    ) -> "List[_4899.AGMAGleasonConicalGearModalAnalysis]":
        """List[mastapy.system_model.analyses_and_results.modal_analyses.AGMAGleasonConicalGearModalAnalysis]

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(
            self.wrapped, "AGMAGleasonConicalGearsModalAnalysis"
        )

        if temp is None:
            return None

        value = conversion.pn_to_mp_objects_in_list(temp)

        if value is None:
            return None

        return value

    @property
    @exception_bridge
    def conical_meshes_modal_analysis(
        self: "Self",
    ) -> "List[_4898.AGMAGleasonConicalGearMeshModalAnalysis]":
        """List[mastapy.system_model.analyses_and_results.modal_analyses.AGMAGleasonConicalGearMeshModalAnalysis]

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "ConicalMeshesModalAnalysis")

        if temp is None:
            return None

        value = conversion.pn_to_mp_objects_in_list(temp)

        if value is None:
            return None

        return value

    @property
    @exception_bridge
    def agma_gleason_conical_meshes_modal_analysis(
        self: "Self",
    ) -> "List[_4898.AGMAGleasonConicalGearMeshModalAnalysis]":
        """List[mastapy.system_model.analyses_and_results.modal_analyses.AGMAGleasonConicalGearMeshModalAnalysis]

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(
            self.wrapped, "AGMAGleasonConicalMeshesModalAnalysis"
        )

        if temp is None:
            return None

        value = conversion.pn_to_mp_objects_in_list(temp)

        if value is None:
            return None

        return value

    @property
    @exception_bridge
    def system_deflection_results(
        self: "Self",
    ) -> "_2982.AGMAGleasonConicalGearSetSystemDeflection":
        """mastapy.system_model.analyses_and_results.system_deflections.AGMAGleasonConicalGearSetSystemDeflection

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "SystemDeflectionResults")

        if temp is None:
            return None

        type_ = temp.GetType()
        return constructor.new(type_.Namespace, type_.Name)(temp)

    @property
    def cast_to(self: "Self") -> "_Cast_AGMAGleasonConicalGearSetModalAnalysis":
        """Cast to another type.

        Returns:
            _Cast_AGMAGleasonConicalGearSetModalAnalysis
        """
        return _Cast_AGMAGleasonConicalGearSetModalAnalysis(self)
