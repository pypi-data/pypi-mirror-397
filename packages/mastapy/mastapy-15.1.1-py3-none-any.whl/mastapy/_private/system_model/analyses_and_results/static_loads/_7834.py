"""KlingelnbergCycloPalloidConicalGearMeshLoadCase"""

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
from mastapy._private.system_model.analyses_and_results.static_loads import _7767

_KLINGELNBERG_CYCLO_PALLOID_CONICAL_GEAR_MESH_LOAD_CASE = python_net_import(
    "SMT.MastaAPI.SystemModel.AnalysesAndResults.StaticLoads",
    "KlingelnbergCycloPalloidConicalGearMeshLoadCase",
)

if TYPE_CHECKING:
    from typing import Any, Type, TypeVar

    from mastapy._private.system_model.analyses_and_results import _2941, _2943, _2945
    from mastapy._private.system_model.analyses_and_results.static_loads import (
        _7770,
        _7813,
        _7832,
        _7837,
        _7840,
    )
    from mastapy._private.system_model.connections_and_sockets.gears import _2577

    Self = TypeVar("Self", bound="KlingelnbergCycloPalloidConicalGearMeshLoadCase")
    CastSelf = TypeVar(
        "CastSelf",
        bound="KlingelnbergCycloPalloidConicalGearMeshLoadCase._Cast_KlingelnbergCycloPalloidConicalGearMeshLoadCase",
    )


__docformat__ = "restructuredtext en"
__all__ = ("KlingelnbergCycloPalloidConicalGearMeshLoadCase",)


@extended_dataclass(frozen=True, slots=True, weakref_slot=True)
class _Cast_KlingelnbergCycloPalloidConicalGearMeshLoadCase:
    """Special nested class for casting KlingelnbergCycloPalloidConicalGearMeshLoadCase to subclasses."""

    __parent__: "KlingelnbergCycloPalloidConicalGearMeshLoadCase"

    @property
    def conical_gear_mesh_load_case(
        self: "CastSelf",
    ) -> "_7767.ConicalGearMeshLoadCase":
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
    def klingelnberg_cyclo_palloid_hypoid_gear_mesh_load_case(
        self: "CastSelf",
    ) -> "_7837.KlingelnbergCycloPalloidHypoidGearMeshLoadCase":
        from mastapy._private.system_model.analyses_and_results.static_loads import (
            _7837,
        )

        return self.__parent__._cast(
            _7837.KlingelnbergCycloPalloidHypoidGearMeshLoadCase
        )

    @property
    def klingelnberg_cyclo_palloid_spiral_bevel_gear_mesh_load_case(
        self: "CastSelf",
    ) -> "_7840.KlingelnbergCycloPalloidSpiralBevelGearMeshLoadCase":
        from mastapy._private.system_model.analyses_and_results.static_loads import (
            _7840,
        )

        return self.__parent__._cast(
            _7840.KlingelnbergCycloPalloidSpiralBevelGearMeshLoadCase
        )

    @property
    def klingelnberg_cyclo_palloid_conical_gear_mesh_load_case(
        self: "CastSelf",
    ) -> "KlingelnbergCycloPalloidConicalGearMeshLoadCase":
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
class KlingelnbergCycloPalloidConicalGearMeshLoadCase(_7767.ConicalGearMeshLoadCase):
    """KlingelnbergCycloPalloidConicalGearMeshLoadCase

    This is a mastapy class.
    """

    TYPE: ClassVar["Type"] = _KLINGELNBERG_CYCLO_PALLOID_CONICAL_GEAR_MESH_LOAD_CASE

    wrapped: "Any"

    def __post_init__(self: "Self") -> None:
        """Override of the post initialisation magic method."""
        if not hasattr(self.wrapped, "reference_count"):
            self.wrapped.reference_count = 0

        self.wrapped.reference_count += 1

    @property
    @exception_bridge
    def connection_design(
        self: "Self",
    ) -> "_2577.KlingelnbergCycloPalloidConicalGearMesh":
        """mastapy.system_model.connections_and_sockets.gears.KlingelnbergCycloPalloidConicalGearMesh

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "ConnectionDesign")

        if temp is None:
            return None

        type_ = temp.GetType()
        return constructor.new(type_.Namespace, type_.Name)(temp)

    @property
    def cast_to(
        self: "Self",
    ) -> "_Cast_KlingelnbergCycloPalloidConicalGearMeshLoadCase":
        """Cast to another type.

        Returns:
            _Cast_KlingelnbergCycloPalloidConicalGearMeshLoadCase
        """
        return _Cast_KlingelnbergCycloPalloidConicalGearMeshLoadCase(self)
