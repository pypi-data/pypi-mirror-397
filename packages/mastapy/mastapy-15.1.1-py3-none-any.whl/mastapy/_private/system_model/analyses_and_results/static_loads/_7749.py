"""BevelGearMeshLoadCase"""

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
from mastapy._private.system_model.analyses_and_results.static_loads import _7735

_BEVEL_GEAR_MESH_LOAD_CASE = python_net_import(
    "SMT.MastaAPI.SystemModel.AnalysesAndResults.StaticLoads", "BevelGearMeshLoadCase"
)

if TYPE_CHECKING:
    from typing import Any, Type, TypeVar

    from mastapy._private.system_model.analyses_and_results import _2941, _2943, _2945
    from mastapy._private.system_model.analyses_and_results.static_loads import (
        _7744,
        _7767,
        _7770,
        _7813,
        _7832,
        _7879,
        _7885,
        _7888,
        _7912,
    )
    from mastapy._private.system_model.connections_and_sockets.gears import _2562

    Self = TypeVar("Self", bound="BevelGearMeshLoadCase")
    CastSelf = TypeVar(
        "CastSelf", bound="BevelGearMeshLoadCase._Cast_BevelGearMeshLoadCase"
    )


__docformat__ = "restructuredtext en"
__all__ = ("BevelGearMeshLoadCase",)


@extended_dataclass(frozen=True, slots=True, weakref_slot=True)
class _Cast_BevelGearMeshLoadCase:
    """Special nested class for casting BevelGearMeshLoadCase to subclasses."""

    __parent__: "BevelGearMeshLoadCase"

    @property
    def agma_gleason_conical_gear_mesh_load_case(
        self: "CastSelf",
    ) -> "_7735.AGMAGleasonConicalGearMeshLoadCase":
        return self.__parent__._cast(_7735.AGMAGleasonConicalGearMeshLoadCase)

    @property
    def conical_gear_mesh_load_case(
        self: "CastSelf",
    ) -> "_7767.ConicalGearMeshLoadCase":
        from mastapy._private.system_model.analyses_and_results.static_loads import (
            _7767,
        )

        return self.__parent__._cast(_7767.ConicalGearMeshLoadCase)

    @property
    def gear_mesh_load_case(self: "CastSelf") -> "_7813.GearMeshLoadCase":
        from mastapy._private.system_model.analyses_and_results.static_loads import (
            _7813,
        )

        return self.__parent__._cast(_7813.GearMeshLoadCase)

    @property
    def inter_mountable_component_connection_load_case(
        self: "CastSelf",
    ) -> "_7832.InterMountableComponentConnectionLoadCase":
        from mastapy._private.system_model.analyses_and_results.static_loads import (
            _7832,
        )

        return self.__parent__._cast(_7832.InterMountableComponentConnectionLoadCase)

    @property
    def connection_load_case(self: "CastSelf") -> "_7770.ConnectionLoadCase":
        from mastapy._private.system_model.analyses_and_results.static_loads import (
            _7770,
        )

        return self.__parent__._cast(_7770.ConnectionLoadCase)

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
    def bevel_differential_gear_mesh_load_case(
        self: "CastSelf",
    ) -> "_7744.BevelDifferentialGearMeshLoadCase":
        from mastapy._private.system_model.analyses_and_results.static_loads import (
            _7744,
        )

        return self.__parent__._cast(_7744.BevelDifferentialGearMeshLoadCase)

    @property
    def spiral_bevel_gear_mesh_load_case(
        self: "CastSelf",
    ) -> "_7879.SpiralBevelGearMeshLoadCase":
        from mastapy._private.system_model.analyses_and_results.static_loads import (
            _7879,
        )

        return self.__parent__._cast(_7879.SpiralBevelGearMeshLoadCase)

    @property
    def straight_bevel_diff_gear_mesh_load_case(
        self: "CastSelf",
    ) -> "_7885.StraightBevelDiffGearMeshLoadCase":
        from mastapy._private.system_model.analyses_and_results.static_loads import (
            _7885,
        )

        return self.__parent__._cast(_7885.StraightBevelDiffGearMeshLoadCase)

    @property
    def straight_bevel_gear_mesh_load_case(
        self: "CastSelf",
    ) -> "_7888.StraightBevelGearMeshLoadCase":
        from mastapy._private.system_model.analyses_and_results.static_loads import (
            _7888,
        )

        return self.__parent__._cast(_7888.StraightBevelGearMeshLoadCase)

    @property
    def zerol_bevel_gear_mesh_load_case(
        self: "CastSelf",
    ) -> "_7912.ZerolBevelGearMeshLoadCase":
        from mastapy._private.system_model.analyses_and_results.static_loads import (
            _7912,
        )

        return self.__parent__._cast(_7912.ZerolBevelGearMeshLoadCase)

    @property
    def bevel_gear_mesh_load_case(self: "CastSelf") -> "BevelGearMeshLoadCase":
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
class BevelGearMeshLoadCase(_7735.AGMAGleasonConicalGearMeshLoadCase):
    """BevelGearMeshLoadCase

    This is a mastapy class.
    """

    TYPE: ClassVar["Type"] = _BEVEL_GEAR_MESH_LOAD_CASE

    wrapped: "Any"

    def __post_init__(self: "Self") -> None:
        """Override of the post initialisation magic method."""
        if not hasattr(self.wrapped, "reference_count"):
            self.wrapped.reference_count = 0

        self.wrapped.reference_count += 1

    @property
    @exception_bridge
    def connection_design(self: "Self") -> "_2562.BevelGearMesh":
        """mastapy.system_model.connections_and_sockets.gears.BevelGearMesh

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "ConnectionDesign")

        if temp is None:
            return None

        type_ = temp.GetType()
        return constructor.new(type_.Namespace, type_.Name)(temp)

    @property
    def cast_to(self: "Self") -> "_Cast_BevelGearMeshLoadCase":
        """Cast to another type.

        Returns:
            _Cast_BevelGearMeshLoadCase
        """
        return _Cast_BevelGearMeshLoadCase(self)
