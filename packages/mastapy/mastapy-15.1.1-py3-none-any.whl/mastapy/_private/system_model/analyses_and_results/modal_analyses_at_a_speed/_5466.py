"""BevelGearSetModalAnalysisAtASpeed"""

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
from mastapy._private.system_model.analyses_and_results.modal_analyses_at_a_speed import (
    _5454,
)

_BEVEL_GEAR_SET_MODAL_ANALYSIS_AT_A_SPEED = python_net_import(
    "SMT.MastaAPI.SystemModel.AnalysesAndResults.ModalAnalysesAtASpeed",
    "BevelGearSetModalAnalysisAtASpeed",
)

if TYPE_CHECKING:
    from typing import Any, List, Type, TypeVar

    from mastapy._private.system_model.analyses_and_results import _2943, _2945, _2949
    from mastapy._private.system_model.analyses_and_results.analysis_cases import (
        _7941,
        _7944,
    )
    from mastapy._private.system_model.analyses_and_results.modal_analyses_at_a_speed import (
        _5448,
        _5461,
        _5464,
        _5465,
        _5482,
        _5508,
        _5530,
        _5549,
        _5552,
        _5558,
        _5561,
        _5579,
    )
    from mastapy._private.system_model.part_model.gears import _2801

    Self = TypeVar("Self", bound="BevelGearSetModalAnalysisAtASpeed")
    CastSelf = TypeVar(
        "CastSelf",
        bound="BevelGearSetModalAnalysisAtASpeed._Cast_BevelGearSetModalAnalysisAtASpeed",
    )


__docformat__ = "restructuredtext en"
__all__ = ("BevelGearSetModalAnalysisAtASpeed",)


@extended_dataclass(frozen=True, slots=True, weakref_slot=True)
class _Cast_BevelGearSetModalAnalysisAtASpeed:
    """Special nested class for casting BevelGearSetModalAnalysisAtASpeed to subclasses."""

    __parent__: "BevelGearSetModalAnalysisAtASpeed"

    @property
    def agma_gleason_conical_gear_set_modal_analysis_at_a_speed(
        self: "CastSelf",
    ) -> "_5454.AGMAGleasonConicalGearSetModalAnalysisAtASpeed":
        return self.__parent__._cast(
            _5454.AGMAGleasonConicalGearSetModalAnalysisAtASpeed
        )

    @property
    def conical_gear_set_modal_analysis_at_a_speed(
        self: "CastSelf",
    ) -> "_5482.ConicalGearSetModalAnalysisAtASpeed":
        from mastapy._private.system_model.analyses_and_results.modal_analyses_at_a_speed import (
            _5482,
        )

        return self.__parent__._cast(_5482.ConicalGearSetModalAnalysisAtASpeed)

    @property
    def gear_set_modal_analysis_at_a_speed(
        self: "CastSelf",
    ) -> "_5508.GearSetModalAnalysisAtASpeed":
        from mastapy._private.system_model.analyses_and_results.modal_analyses_at_a_speed import (
            _5508,
        )

        return self.__parent__._cast(_5508.GearSetModalAnalysisAtASpeed)

    @property
    def specialised_assembly_modal_analysis_at_a_speed(
        self: "CastSelf",
    ) -> "_5549.SpecialisedAssemblyModalAnalysisAtASpeed":
        from mastapy._private.system_model.analyses_and_results.modal_analyses_at_a_speed import (
            _5549,
        )

        return self.__parent__._cast(_5549.SpecialisedAssemblyModalAnalysisAtASpeed)

    @property
    def abstract_assembly_modal_analysis_at_a_speed(
        self: "CastSelf",
    ) -> "_5448.AbstractAssemblyModalAnalysisAtASpeed":
        from mastapy._private.system_model.analyses_and_results.modal_analyses_at_a_speed import (
            _5448,
        )

        return self.__parent__._cast(_5448.AbstractAssemblyModalAnalysisAtASpeed)

    @property
    def part_modal_analysis_at_a_speed(
        self: "CastSelf",
    ) -> "_5530.PartModalAnalysisAtASpeed":
        from mastapy._private.system_model.analyses_and_results.modal_analyses_at_a_speed import (
            _5530,
        )

        return self.__parent__._cast(_5530.PartModalAnalysisAtASpeed)

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
    def bevel_differential_gear_set_modal_analysis_at_a_speed(
        self: "CastSelf",
    ) -> "_5461.BevelDifferentialGearSetModalAnalysisAtASpeed":
        from mastapy._private.system_model.analyses_and_results.modal_analyses_at_a_speed import (
            _5461,
        )

        return self.__parent__._cast(
            _5461.BevelDifferentialGearSetModalAnalysisAtASpeed
        )

    @property
    def spiral_bevel_gear_set_modal_analysis_at_a_speed(
        self: "CastSelf",
    ) -> "_5552.SpiralBevelGearSetModalAnalysisAtASpeed":
        from mastapy._private.system_model.analyses_and_results.modal_analyses_at_a_speed import (
            _5552,
        )

        return self.__parent__._cast(_5552.SpiralBevelGearSetModalAnalysisAtASpeed)

    @property
    def straight_bevel_diff_gear_set_modal_analysis_at_a_speed(
        self: "CastSelf",
    ) -> "_5558.StraightBevelDiffGearSetModalAnalysisAtASpeed":
        from mastapy._private.system_model.analyses_and_results.modal_analyses_at_a_speed import (
            _5558,
        )

        return self.__parent__._cast(
            _5558.StraightBevelDiffGearSetModalAnalysisAtASpeed
        )

    @property
    def straight_bevel_gear_set_modal_analysis_at_a_speed(
        self: "CastSelf",
    ) -> "_5561.StraightBevelGearSetModalAnalysisAtASpeed":
        from mastapy._private.system_model.analyses_and_results.modal_analyses_at_a_speed import (
            _5561,
        )

        return self.__parent__._cast(_5561.StraightBevelGearSetModalAnalysisAtASpeed)

    @property
    def zerol_bevel_gear_set_modal_analysis_at_a_speed(
        self: "CastSelf",
    ) -> "_5579.ZerolBevelGearSetModalAnalysisAtASpeed":
        from mastapy._private.system_model.analyses_and_results.modal_analyses_at_a_speed import (
            _5579,
        )

        return self.__parent__._cast(_5579.ZerolBevelGearSetModalAnalysisAtASpeed)

    @property
    def bevel_gear_set_modal_analysis_at_a_speed(
        self: "CastSelf",
    ) -> "BevelGearSetModalAnalysisAtASpeed":
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
class BevelGearSetModalAnalysisAtASpeed(
    _5454.AGMAGleasonConicalGearSetModalAnalysisAtASpeed
):
    """BevelGearSetModalAnalysisAtASpeed

    This is a mastapy class.
    """

    TYPE: ClassVar["Type"] = _BEVEL_GEAR_SET_MODAL_ANALYSIS_AT_A_SPEED

    wrapped: "Any"

    def __post_init__(self: "Self") -> None:
        """Override of the post initialisation magic method."""
        if not hasattr(self.wrapped, "reference_count"):
            self.wrapped.reference_count = 0

        self.wrapped.reference_count += 1

    @property
    @exception_bridge
    def assembly_design(self: "Self") -> "_2801.BevelGearSet":
        """mastapy.system_model.part_model.gears.BevelGearSet

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
    def agma_gleason_conical_gears_modal_analysis_at_a_speed(
        self: "Self",
    ) -> "List[_5465.BevelGearModalAnalysisAtASpeed]":
        """List[mastapy.system_model.analyses_and_results.modal_analyses_at_a_speed.BevelGearModalAnalysisAtASpeed]

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(
            self.wrapped, "AGMAGleasonConicalGearsModalAnalysisAtASpeed"
        )

        if temp is None:
            return None

        value = conversion.pn_to_mp_objects_in_list(temp)

        if value is None:
            return None

        return value

    @property
    @exception_bridge
    def bevel_gears_modal_analysis_at_a_speed(
        self: "Self",
    ) -> "List[_5465.BevelGearModalAnalysisAtASpeed]":
        """List[mastapy.system_model.analyses_and_results.modal_analyses_at_a_speed.BevelGearModalAnalysisAtASpeed]

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "BevelGearsModalAnalysisAtASpeed")

        if temp is None:
            return None

        value = conversion.pn_to_mp_objects_in_list(temp)

        if value is None:
            return None

        return value

    @property
    @exception_bridge
    def agma_gleason_conical_meshes_modal_analysis_at_a_speed(
        self: "Self",
    ) -> "List[_5464.BevelGearMeshModalAnalysisAtASpeed]":
        """List[mastapy.system_model.analyses_and_results.modal_analyses_at_a_speed.BevelGearMeshModalAnalysisAtASpeed]

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(
            self.wrapped, "AGMAGleasonConicalMeshesModalAnalysisAtASpeed"
        )

        if temp is None:
            return None

        value = conversion.pn_to_mp_objects_in_list(temp)

        if value is None:
            return None

        return value

    @property
    @exception_bridge
    def bevel_meshes_modal_analysis_at_a_speed(
        self: "Self",
    ) -> "List[_5464.BevelGearMeshModalAnalysisAtASpeed]":
        """List[mastapy.system_model.analyses_and_results.modal_analyses_at_a_speed.BevelGearMeshModalAnalysisAtASpeed]

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "BevelMeshesModalAnalysisAtASpeed")

        if temp is None:
            return None

        value = conversion.pn_to_mp_objects_in_list(temp)

        if value is None:
            return None

        return value

    @property
    def cast_to(self: "Self") -> "_Cast_BevelGearSetModalAnalysisAtASpeed":
        """Cast to another type.

        Returns:
            _Cast_BevelGearSetModalAnalysisAtASpeed
        """
        return _Cast_BevelGearSetModalAnalysisAtASpeed(self)
