"""StraightBevelGearMeshCompoundDynamicAnalysis"""

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
from mastapy._private.system_model.analyses_and_results.dynamic_analyses.compound import (
    _6791,
)

_STRAIGHT_BEVEL_GEAR_MESH_COMPOUND_DYNAMIC_ANALYSIS = python_net_import(
    "SMT.MastaAPI.SystemModel.AnalysesAndResults.DynamicAnalyses.Compound",
    "StraightBevelGearMeshCompoundDynamicAnalysis",
)

if TYPE_CHECKING:
    from typing import Any, List, Type, TypeVar

    from mastapy._private.system_model.analyses_and_results import _2943
    from mastapy._private.system_model.analyses_and_results.analysis_cases import (
        _7935,
        _7939,
    )
    from mastapy._private.system_model.analyses_and_results.dynamic_analyses import (
        _6754,
    )
    from mastapy._private.system_model.analyses_and_results.dynamic_analyses.compound import (
        _6779,
        _6807,
        _6809,
        _6833,
        _6839,
    )
    from mastapy._private.system_model.connections_and_sockets.gears import _2586

    Self = TypeVar("Self", bound="StraightBevelGearMeshCompoundDynamicAnalysis")
    CastSelf = TypeVar(
        "CastSelf",
        bound="StraightBevelGearMeshCompoundDynamicAnalysis._Cast_StraightBevelGearMeshCompoundDynamicAnalysis",
    )


__docformat__ = "restructuredtext en"
__all__ = ("StraightBevelGearMeshCompoundDynamicAnalysis",)


@extended_dataclass(frozen=True, slots=True, weakref_slot=True)
class _Cast_StraightBevelGearMeshCompoundDynamicAnalysis:
    """Special nested class for casting StraightBevelGearMeshCompoundDynamicAnalysis to subclasses."""

    __parent__: "StraightBevelGearMeshCompoundDynamicAnalysis"

    @property
    def bevel_gear_mesh_compound_dynamic_analysis(
        self: "CastSelf",
    ) -> "_6791.BevelGearMeshCompoundDynamicAnalysis":
        return self.__parent__._cast(_6791.BevelGearMeshCompoundDynamicAnalysis)

    @property
    def agma_gleason_conical_gear_mesh_compound_dynamic_analysis(
        self: "CastSelf",
    ) -> "_6779.AGMAGleasonConicalGearMeshCompoundDynamicAnalysis":
        from mastapy._private.system_model.analyses_and_results.dynamic_analyses.compound import (
            _6779,
        )

        return self.__parent__._cast(
            _6779.AGMAGleasonConicalGearMeshCompoundDynamicAnalysis
        )

    @property
    def conical_gear_mesh_compound_dynamic_analysis(
        self: "CastSelf",
    ) -> "_6807.ConicalGearMeshCompoundDynamicAnalysis":
        from mastapy._private.system_model.analyses_and_results.dynamic_analyses.compound import (
            _6807,
        )

        return self.__parent__._cast(_6807.ConicalGearMeshCompoundDynamicAnalysis)

    @property
    def gear_mesh_compound_dynamic_analysis(
        self: "CastSelf",
    ) -> "_6833.GearMeshCompoundDynamicAnalysis":
        from mastapy._private.system_model.analyses_and_results.dynamic_analyses.compound import (
            _6833,
        )

        return self.__parent__._cast(_6833.GearMeshCompoundDynamicAnalysis)

    @property
    def inter_mountable_component_connection_compound_dynamic_analysis(
        self: "CastSelf",
    ) -> "_6839.InterMountableComponentConnectionCompoundDynamicAnalysis":
        from mastapy._private.system_model.analyses_and_results.dynamic_analyses.compound import (
            _6839,
        )

        return self.__parent__._cast(
            _6839.InterMountableComponentConnectionCompoundDynamicAnalysis
        )

    @property
    def connection_compound_dynamic_analysis(
        self: "CastSelf",
    ) -> "_6809.ConnectionCompoundDynamicAnalysis":
        from mastapy._private.system_model.analyses_and_results.dynamic_analyses.compound import (
            _6809,
        )

        return self.__parent__._cast(_6809.ConnectionCompoundDynamicAnalysis)

    @property
    def connection_compound_analysis(
        self: "CastSelf",
    ) -> "_7935.ConnectionCompoundAnalysis":
        from mastapy._private.system_model.analyses_and_results.analysis_cases import (
            _7935,
        )

        return self.__parent__._cast(_7935.ConnectionCompoundAnalysis)

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
    def straight_bevel_gear_mesh_compound_dynamic_analysis(
        self: "CastSelf",
    ) -> "StraightBevelGearMeshCompoundDynamicAnalysis":
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
class StraightBevelGearMeshCompoundDynamicAnalysis(
    _6791.BevelGearMeshCompoundDynamicAnalysis
):
    """StraightBevelGearMeshCompoundDynamicAnalysis

    This is a mastapy class.
    """

    TYPE: ClassVar["Type"] = _STRAIGHT_BEVEL_GEAR_MESH_COMPOUND_DYNAMIC_ANALYSIS

    wrapped: "Any"

    def __post_init__(self: "Self") -> None:
        """Override of the post initialisation magic method."""
        if not hasattr(self.wrapped, "reference_count"):
            self.wrapped.reference_count = 0

        self.wrapped.reference_count += 1

    @property
    @exception_bridge
    def component_design(self: "Self") -> "_2586.StraightBevelGearMesh":
        """mastapy.system_model.connections_and_sockets.gears.StraightBevelGearMesh

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
    def connection_design(self: "Self") -> "_2586.StraightBevelGearMesh":
        """mastapy.system_model.connections_and_sockets.gears.StraightBevelGearMesh

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "ConnectionDesign")

        if temp is None:
            return None

        type_ = temp.GetType()
        return constructor.new(type_.Namespace, type_.Name)(temp)

    @property
    @exception_bridge
    def connection_analysis_cases_ready(
        self: "Self",
    ) -> "List[_6754.StraightBevelGearMeshDynamicAnalysis]":
        """List[mastapy.system_model.analyses_and_results.dynamic_analyses.StraightBevelGearMeshDynamicAnalysis]

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "ConnectionAnalysisCasesReady")

        if temp is None:
            return None

        value = conversion.pn_to_mp_objects_in_list(temp)

        if value is None:
            return None

        return value

    @property
    @exception_bridge
    def connection_analysis_cases(
        self: "Self",
    ) -> "List[_6754.StraightBevelGearMeshDynamicAnalysis]":
        """List[mastapy.system_model.analyses_and_results.dynamic_analyses.StraightBevelGearMeshDynamicAnalysis]

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "ConnectionAnalysisCases")

        if temp is None:
            return None

        value = conversion.pn_to_mp_objects_in_list(temp)

        if value is None:
            return None

        return value

    @property
    def cast_to(self: "Self") -> "_Cast_StraightBevelGearMeshCompoundDynamicAnalysis":
        """Cast to another type.

        Returns:
            _Cast_StraightBevelGearMeshCompoundDynamicAnalysis
        """
        return _Cast_StraightBevelGearMeshCompoundDynamicAnalysis(self)
