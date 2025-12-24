"""GearMeshParametricStudyTool"""

from __future__ import annotations

from typing import TYPE_CHECKING, ClassVar

from mastapy._private._internal.dataclasses import extended_dataclass
from mastapy._private._internal.exception_bridge import exception_bridge
from mastapy._private._internal.exceptions import CastException
from mastapy._private._internal.python_net import (
    python_net_import,
    pythonnet_property_get,
)

from mastapy._private._internal import constructor, utility
from mastapy._private.system_model.analyses_and_results.parametric_study_tools import (
    _4685,
)

_GEAR_MESH_PARAMETRIC_STUDY_TOOL = python_net_import(
    "SMT.MastaAPI.SystemModel.AnalysesAndResults.ParametricStudyTools",
    "GearMeshParametricStudyTool",
)

if TYPE_CHECKING:
    from typing import Any, Type, TypeVar

    from mastapy._private.system_model.analyses_and_results import _2941, _2943, _2945
    from mastapy._private.system_model.analyses_and_results.analysis_cases import _7934
    from mastapy._private.system_model.analyses_and_results.parametric_study_tools import (
        _4617,
        _4624,
        _4629,
        _4642,
        _4645,
        _4648,
        _4660,
        _4673,
        _4682,
        _4686,
        _4689,
        _4692,
        _4733,
        _4739,
        _4742,
        _4757,
        _4760,
    )
    from mastapy._private.system_model.connections_and_sockets.gears import _2572

    Self = TypeVar("Self", bound="GearMeshParametricStudyTool")
    CastSelf = TypeVar(
        "CastSelf",
        bound="GearMeshParametricStudyTool._Cast_GearMeshParametricStudyTool",
    )


__docformat__ = "restructuredtext en"
__all__ = ("GearMeshParametricStudyTool",)


@extended_dataclass(frozen=True, slots=True, weakref_slot=True)
class _Cast_GearMeshParametricStudyTool:
    """Special nested class for casting GearMeshParametricStudyTool to subclasses."""

    __parent__: "GearMeshParametricStudyTool"

    @property
    def inter_mountable_component_connection_parametric_study_tool(
        self: "CastSelf",
    ) -> "_4685.InterMountableComponentConnectionParametricStudyTool":
        return self.__parent__._cast(
            _4685.InterMountableComponentConnectionParametricStudyTool
        )

    @property
    def connection_parametric_study_tool(
        self: "CastSelf",
    ) -> "_4648.ConnectionParametricStudyTool":
        from mastapy._private.system_model.analyses_and_results.parametric_study_tools import (
            _4648,
        )

        return self.__parent__._cast(_4648.ConnectionParametricStudyTool)

    @property
    def connection_analysis_case(self: "CastSelf") -> "_7934.ConnectionAnalysisCase":
        from mastapy._private.system_model.analyses_and_results.analysis_cases import (
            _7934,
        )

        return self.__parent__._cast(_7934.ConnectionAnalysisCase)

    @property
    def connection_analysis(self: "CastSelf") -> "_2941.ConnectionAnalysis":
        from mastapy._private.system_model.analyses_and_results import _2941

        return self.__parent__._cast(_2941.ConnectionAnalysis)

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
    def agma_gleason_conical_gear_mesh_parametric_study_tool(
        self: "CastSelf",
    ) -> "_4617.AGMAGleasonConicalGearMeshParametricStudyTool":
        from mastapy._private.system_model.analyses_and_results.parametric_study_tools import (
            _4617,
        )

        return self.__parent__._cast(
            _4617.AGMAGleasonConicalGearMeshParametricStudyTool
        )

    @property
    def bevel_differential_gear_mesh_parametric_study_tool(
        self: "CastSelf",
    ) -> "_4624.BevelDifferentialGearMeshParametricStudyTool":
        from mastapy._private.system_model.analyses_and_results.parametric_study_tools import (
            _4624,
        )

        return self.__parent__._cast(_4624.BevelDifferentialGearMeshParametricStudyTool)

    @property
    def bevel_gear_mesh_parametric_study_tool(
        self: "CastSelf",
    ) -> "_4629.BevelGearMeshParametricStudyTool":
        from mastapy._private.system_model.analyses_and_results.parametric_study_tools import (
            _4629,
        )

        return self.__parent__._cast(_4629.BevelGearMeshParametricStudyTool)

    @property
    def concept_gear_mesh_parametric_study_tool(
        self: "CastSelf",
    ) -> "_4642.ConceptGearMeshParametricStudyTool":
        from mastapy._private.system_model.analyses_and_results.parametric_study_tools import (
            _4642,
        )

        return self.__parent__._cast(_4642.ConceptGearMeshParametricStudyTool)

    @property
    def conical_gear_mesh_parametric_study_tool(
        self: "CastSelf",
    ) -> "_4645.ConicalGearMeshParametricStudyTool":
        from mastapy._private.system_model.analyses_and_results.parametric_study_tools import (
            _4645,
        )

        return self.__parent__._cast(_4645.ConicalGearMeshParametricStudyTool)

    @property
    def cylindrical_gear_mesh_parametric_study_tool(
        self: "CastSelf",
    ) -> "_4660.CylindricalGearMeshParametricStudyTool":
        from mastapy._private.system_model.analyses_and_results.parametric_study_tools import (
            _4660,
        )

        return self.__parent__._cast(_4660.CylindricalGearMeshParametricStudyTool)

    @property
    def face_gear_mesh_parametric_study_tool(
        self: "CastSelf",
    ) -> "_4673.FaceGearMeshParametricStudyTool":
        from mastapy._private.system_model.analyses_and_results.parametric_study_tools import (
            _4673,
        )

        return self.__parent__._cast(_4673.FaceGearMeshParametricStudyTool)

    @property
    def hypoid_gear_mesh_parametric_study_tool(
        self: "CastSelf",
    ) -> "_4682.HypoidGearMeshParametricStudyTool":
        from mastapy._private.system_model.analyses_and_results.parametric_study_tools import (
            _4682,
        )

        return self.__parent__._cast(_4682.HypoidGearMeshParametricStudyTool)

    @property
    def klingelnberg_cyclo_palloid_conical_gear_mesh_parametric_study_tool(
        self: "CastSelf",
    ) -> "_4686.KlingelnbergCycloPalloidConicalGearMeshParametricStudyTool":
        from mastapy._private.system_model.analyses_and_results.parametric_study_tools import (
            _4686,
        )

        return self.__parent__._cast(
            _4686.KlingelnbergCycloPalloidConicalGearMeshParametricStudyTool
        )

    @property
    def klingelnberg_cyclo_palloid_hypoid_gear_mesh_parametric_study_tool(
        self: "CastSelf",
    ) -> "_4689.KlingelnbergCycloPalloidHypoidGearMeshParametricStudyTool":
        from mastapy._private.system_model.analyses_and_results.parametric_study_tools import (
            _4689,
        )

        return self.__parent__._cast(
            _4689.KlingelnbergCycloPalloidHypoidGearMeshParametricStudyTool
        )

    @property
    def klingelnberg_cyclo_palloid_spiral_bevel_gear_mesh_parametric_study_tool(
        self: "CastSelf",
    ) -> "_4692.KlingelnbergCycloPalloidSpiralBevelGearMeshParametricStudyTool":
        from mastapy._private.system_model.analyses_and_results.parametric_study_tools import (
            _4692,
        )

        return self.__parent__._cast(
            _4692.KlingelnbergCycloPalloidSpiralBevelGearMeshParametricStudyTool
        )

    @property
    def spiral_bevel_gear_mesh_parametric_study_tool(
        self: "CastSelf",
    ) -> "_4733.SpiralBevelGearMeshParametricStudyTool":
        from mastapy._private.system_model.analyses_and_results.parametric_study_tools import (
            _4733,
        )

        return self.__parent__._cast(_4733.SpiralBevelGearMeshParametricStudyTool)

    @property
    def straight_bevel_diff_gear_mesh_parametric_study_tool(
        self: "CastSelf",
    ) -> "_4739.StraightBevelDiffGearMeshParametricStudyTool":
        from mastapy._private.system_model.analyses_and_results.parametric_study_tools import (
            _4739,
        )

        return self.__parent__._cast(_4739.StraightBevelDiffGearMeshParametricStudyTool)

    @property
    def straight_bevel_gear_mesh_parametric_study_tool(
        self: "CastSelf",
    ) -> "_4742.StraightBevelGearMeshParametricStudyTool":
        from mastapy._private.system_model.analyses_and_results.parametric_study_tools import (
            _4742,
        )

        return self.__parent__._cast(_4742.StraightBevelGearMeshParametricStudyTool)

    @property
    def worm_gear_mesh_parametric_study_tool(
        self: "CastSelf",
    ) -> "_4757.WormGearMeshParametricStudyTool":
        from mastapy._private.system_model.analyses_and_results.parametric_study_tools import (
            _4757,
        )

        return self.__parent__._cast(_4757.WormGearMeshParametricStudyTool)

    @property
    def zerol_bevel_gear_mesh_parametric_study_tool(
        self: "CastSelf",
    ) -> "_4760.ZerolBevelGearMeshParametricStudyTool":
        from mastapy._private.system_model.analyses_and_results.parametric_study_tools import (
            _4760,
        )

        return self.__parent__._cast(_4760.ZerolBevelGearMeshParametricStudyTool)

    @property
    def gear_mesh_parametric_study_tool(
        self: "CastSelf",
    ) -> "GearMeshParametricStudyTool":
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
class GearMeshParametricStudyTool(
    _4685.InterMountableComponentConnectionParametricStudyTool
):
    """GearMeshParametricStudyTool

    This is a mastapy class.
    """

    TYPE: ClassVar["Type"] = _GEAR_MESH_PARAMETRIC_STUDY_TOOL

    wrapped: "Any"

    def __post_init__(self: "Self") -> None:
        """Override of the post initialisation magic method."""
        if not hasattr(self.wrapped, "reference_count"):
            self.wrapped.reference_count = 0

        self.wrapped.reference_count += 1

    @property
    @exception_bridge
    def connection_design(self: "Self") -> "_2572.GearMesh":
        """mastapy.system_model.connections_and_sockets.gears.GearMesh

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "ConnectionDesign")

        if temp is None:
            return None

        type_ = temp.GetType()
        return constructor.new(type_.Namespace, type_.Name)(temp)

    @property
    def cast_to(self: "Self") -> "_Cast_GearMeshParametricStudyTool":
        """Cast to another type.

        Returns:
            _Cast_GearMeshParametricStudyTool
        """
        return _Cast_GearMeshParametricStudyTool(self)
