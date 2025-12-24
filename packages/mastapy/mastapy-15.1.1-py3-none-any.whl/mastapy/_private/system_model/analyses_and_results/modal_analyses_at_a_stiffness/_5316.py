"""ZerolBevelGearSetModalAnalysisAtAStiffness"""

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
from mastapy._private.system_model.analyses_and_results.modal_analyses_at_a_stiffness import (
    _5202,
)

_ZEROL_BEVEL_GEAR_SET_MODAL_ANALYSIS_AT_A_STIFFNESS = python_net_import(
    "SMT.MastaAPI.SystemModel.AnalysesAndResults.ModalAnalysesAtAStiffness",
    "ZerolBevelGearSetModalAnalysisAtAStiffness",
)

if TYPE_CHECKING:
    from typing import Any, List, Type, TypeVar

    from mastapy._private.system_model.analyses_and_results import _2943, _2945, _2949
    from mastapy._private.system_model.analyses_and_results.analysis_cases import (
        _7941,
        _7944,
    )
    from mastapy._private.system_model.analyses_and_results.modal_analyses_at_a_stiffness import (
        _5184,
        _5190,
        _5218,
        _5245,
        _5267,
        _5286,
        _5314,
        _5315,
    )
    from mastapy._private.system_model.analyses_and_results.static_loads import _7913
    from mastapy._private.system_model.part_model.gears import _2836

    Self = TypeVar("Self", bound="ZerolBevelGearSetModalAnalysisAtAStiffness")
    CastSelf = TypeVar(
        "CastSelf",
        bound="ZerolBevelGearSetModalAnalysisAtAStiffness._Cast_ZerolBevelGearSetModalAnalysisAtAStiffness",
    )


__docformat__ = "restructuredtext en"
__all__ = ("ZerolBevelGearSetModalAnalysisAtAStiffness",)


@extended_dataclass(frozen=True, slots=True, weakref_slot=True)
class _Cast_ZerolBevelGearSetModalAnalysisAtAStiffness:
    """Special nested class for casting ZerolBevelGearSetModalAnalysisAtAStiffness to subclasses."""

    __parent__: "ZerolBevelGearSetModalAnalysisAtAStiffness"

    @property
    def bevel_gear_set_modal_analysis_at_a_stiffness(
        self: "CastSelf",
    ) -> "_5202.BevelGearSetModalAnalysisAtAStiffness":
        return self.__parent__._cast(_5202.BevelGearSetModalAnalysisAtAStiffness)

    @property
    def agma_gleason_conical_gear_set_modal_analysis_at_a_stiffness(
        self: "CastSelf",
    ) -> "_5190.AGMAGleasonConicalGearSetModalAnalysisAtAStiffness":
        from mastapy._private.system_model.analyses_and_results.modal_analyses_at_a_stiffness import (
            _5190,
        )

        return self.__parent__._cast(
            _5190.AGMAGleasonConicalGearSetModalAnalysisAtAStiffness
        )

    @property
    def conical_gear_set_modal_analysis_at_a_stiffness(
        self: "CastSelf",
    ) -> "_5218.ConicalGearSetModalAnalysisAtAStiffness":
        from mastapy._private.system_model.analyses_and_results.modal_analyses_at_a_stiffness import (
            _5218,
        )

        return self.__parent__._cast(_5218.ConicalGearSetModalAnalysisAtAStiffness)

    @property
    def gear_set_modal_analysis_at_a_stiffness(
        self: "CastSelf",
    ) -> "_5245.GearSetModalAnalysisAtAStiffness":
        from mastapy._private.system_model.analyses_and_results.modal_analyses_at_a_stiffness import (
            _5245,
        )

        return self.__parent__._cast(_5245.GearSetModalAnalysisAtAStiffness)

    @property
    def specialised_assembly_modal_analysis_at_a_stiffness(
        self: "CastSelf",
    ) -> "_5286.SpecialisedAssemblyModalAnalysisAtAStiffness":
        from mastapy._private.system_model.analyses_and_results.modal_analyses_at_a_stiffness import (
            _5286,
        )

        return self.__parent__._cast(_5286.SpecialisedAssemblyModalAnalysisAtAStiffness)

    @property
    def abstract_assembly_modal_analysis_at_a_stiffness(
        self: "CastSelf",
    ) -> "_5184.AbstractAssemblyModalAnalysisAtAStiffness":
        from mastapy._private.system_model.analyses_and_results.modal_analyses_at_a_stiffness import (
            _5184,
        )

        return self.__parent__._cast(_5184.AbstractAssemblyModalAnalysisAtAStiffness)

    @property
    def part_modal_analysis_at_a_stiffness(
        self: "CastSelf",
    ) -> "_5267.PartModalAnalysisAtAStiffness":
        from mastapy._private.system_model.analyses_and_results.modal_analyses_at_a_stiffness import (
            _5267,
        )

        return self.__parent__._cast(_5267.PartModalAnalysisAtAStiffness)

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
    def zerol_bevel_gear_set_modal_analysis_at_a_stiffness(
        self: "CastSelf",
    ) -> "ZerolBevelGearSetModalAnalysisAtAStiffness":
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
class ZerolBevelGearSetModalAnalysisAtAStiffness(
    _5202.BevelGearSetModalAnalysisAtAStiffness
):
    """ZerolBevelGearSetModalAnalysisAtAStiffness

    This is a mastapy class.
    """

    TYPE: ClassVar["Type"] = _ZEROL_BEVEL_GEAR_SET_MODAL_ANALYSIS_AT_A_STIFFNESS

    wrapped: "Any"

    def __post_init__(self: "Self") -> None:
        """Override of the post initialisation magic method."""
        if not hasattr(self.wrapped, "reference_count"):
            self.wrapped.reference_count = 0

        self.wrapped.reference_count += 1

    @property
    @exception_bridge
    def assembly_design(self: "Self") -> "_2836.ZerolBevelGearSet":
        """mastapy.system_model.part_model.gears.ZerolBevelGearSet

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
    def assembly_load_case(self: "Self") -> "_7913.ZerolBevelGearSetLoadCase":
        """mastapy.system_model.analyses_and_results.static_loads.ZerolBevelGearSetLoadCase

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "AssemblyLoadCase")

        if temp is None:
            return None

        type_ = temp.GetType()
        return constructor.new(type_.Namespace, type_.Name)(temp)

    @property
    @exception_bridge
    def bevel_gears_modal_analysis_at_a_stiffness(
        self: "Self",
    ) -> "List[_5315.ZerolBevelGearModalAnalysisAtAStiffness]":
        """List[mastapy.system_model.analyses_and_results.modal_analyses_at_a_stiffness.ZerolBevelGearModalAnalysisAtAStiffness]

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(
            self.wrapped, "BevelGearsModalAnalysisAtAStiffness"
        )

        if temp is None:
            return None

        value = conversion.pn_to_mp_objects_in_list(temp)

        if value is None:
            return None

        return value

    @property
    @exception_bridge
    def zerol_bevel_gears_modal_analysis_at_a_stiffness(
        self: "Self",
    ) -> "List[_5315.ZerolBevelGearModalAnalysisAtAStiffness]":
        """List[mastapy.system_model.analyses_and_results.modal_analyses_at_a_stiffness.ZerolBevelGearModalAnalysisAtAStiffness]

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(
            self.wrapped, "ZerolBevelGearsModalAnalysisAtAStiffness"
        )

        if temp is None:
            return None

        value = conversion.pn_to_mp_objects_in_list(temp)

        if value is None:
            return None

        return value

    @property
    @exception_bridge
    def bevel_meshes_modal_analysis_at_a_stiffness(
        self: "Self",
    ) -> "List[_5314.ZerolBevelGearMeshModalAnalysisAtAStiffness]":
        """List[mastapy.system_model.analyses_and_results.modal_analyses_at_a_stiffness.ZerolBevelGearMeshModalAnalysisAtAStiffness]

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(
            self.wrapped, "BevelMeshesModalAnalysisAtAStiffness"
        )

        if temp is None:
            return None

        value = conversion.pn_to_mp_objects_in_list(temp)

        if value is None:
            return None

        return value

    @property
    @exception_bridge
    def zerol_bevel_meshes_modal_analysis_at_a_stiffness(
        self: "Self",
    ) -> "List[_5314.ZerolBevelGearMeshModalAnalysisAtAStiffness]":
        """List[mastapy.system_model.analyses_and_results.modal_analyses_at_a_stiffness.ZerolBevelGearMeshModalAnalysisAtAStiffness]

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(
            self.wrapped, "ZerolBevelMeshesModalAnalysisAtAStiffness"
        )

        if temp is None:
            return None

        value = conversion.pn_to_mp_objects_in_list(temp)

        if value is None:
            return None

        return value

    @property
    def cast_to(self: "Self") -> "_Cast_ZerolBevelGearSetModalAnalysisAtAStiffness":
        """Cast to another type.

        Returns:
            _Cast_ZerolBevelGearSetModalAnalysisAtAStiffness
        """
        return _Cast_ZerolBevelGearSetModalAnalysisAtAStiffness(self)
