"""KlingelnbergCycloPalloidConicalGearMeshAdvancedSystemDeflection"""

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
from mastapy._private.system_model.analyses_and_results.advanced_system_deflections import (
    _7480,
)

_KLINGELNBERG_CYCLO_PALLOID_CONICAL_GEAR_MESH_ADVANCED_SYSTEM_DEFLECTION = (
    python_net_import(
        "SMT.MastaAPI.SystemModel.AnalysesAndResults.AdvancedSystemDeflections",
        "KlingelnbergCycloPalloidConicalGearMeshAdvancedSystemDeflection",
    )
)

if TYPE_CHECKING:
    from typing import Any, Type, TypeVar

    from mastapy._private.system_model.analyses_and_results import _2941, _2943, _2945
    from mastapy._private.system_model.analyses_and_results.advanced_system_deflections import (
        _7482,
        _7508,
        _7514,
        _7519,
        _7522,
    )
    from mastapy._private.system_model.analyses_and_results.analysis_cases import (
        _7934,
        _7937,
    )
    from mastapy._private.system_model.connections_and_sockets.gears import _2577

    Self = TypeVar(
        "Self", bound="KlingelnbergCycloPalloidConicalGearMeshAdvancedSystemDeflection"
    )
    CastSelf = TypeVar(
        "CastSelf",
        bound="KlingelnbergCycloPalloidConicalGearMeshAdvancedSystemDeflection._Cast_KlingelnbergCycloPalloidConicalGearMeshAdvancedSystemDeflection",
    )


__docformat__ = "restructuredtext en"
__all__ = ("KlingelnbergCycloPalloidConicalGearMeshAdvancedSystemDeflection",)


@extended_dataclass(frozen=True, slots=True, weakref_slot=True)
class _Cast_KlingelnbergCycloPalloidConicalGearMeshAdvancedSystemDeflection:
    """Special nested class for casting KlingelnbergCycloPalloidConicalGearMeshAdvancedSystemDeflection to subclasses."""

    __parent__: "KlingelnbergCycloPalloidConicalGearMeshAdvancedSystemDeflection"

    @property
    def conical_gear_mesh_advanced_system_deflection(
        self: "CastSelf",
    ) -> "_7480.ConicalGearMeshAdvancedSystemDeflection":
        return self.__parent__._cast(_7480.ConicalGearMeshAdvancedSystemDeflection)

    @property
    def gear_mesh_advanced_system_deflection(
        self: "CastSelf",
    ) -> "_7508.GearMeshAdvancedSystemDeflection":
        from mastapy._private.system_model.analyses_and_results.advanced_system_deflections import (
            _7508,
        )

        return self.__parent__._cast(_7508.GearMeshAdvancedSystemDeflection)

    @property
    def inter_mountable_component_connection_advanced_system_deflection(
        self: "CastSelf",
    ) -> "_7514.InterMountableComponentConnectionAdvancedSystemDeflection":
        from mastapy._private.system_model.analyses_and_results.advanced_system_deflections import (
            _7514,
        )

        return self.__parent__._cast(
            _7514.InterMountableComponentConnectionAdvancedSystemDeflection
        )

    @property
    def connection_advanced_system_deflection(
        self: "CastSelf",
    ) -> "_7482.ConnectionAdvancedSystemDeflection":
        from mastapy._private.system_model.analyses_and_results.advanced_system_deflections import (
            _7482,
        )

        return self.__parent__._cast(_7482.ConnectionAdvancedSystemDeflection)

    @property
    def connection_static_load_analysis_case(
        self: "CastSelf",
    ) -> "_7937.ConnectionStaticLoadAnalysisCase":
        from mastapy._private.system_model.analyses_and_results.analysis_cases import (
            _7937,
        )

        return self.__parent__._cast(_7937.ConnectionStaticLoadAnalysisCase)

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
    def klingelnberg_cyclo_palloid_hypoid_gear_mesh_advanced_system_deflection(
        self: "CastSelf",
    ) -> "_7519.KlingelnbergCycloPalloidHypoidGearMeshAdvancedSystemDeflection":
        from mastapy._private.system_model.analyses_and_results.advanced_system_deflections import (
            _7519,
        )

        return self.__parent__._cast(
            _7519.KlingelnbergCycloPalloidHypoidGearMeshAdvancedSystemDeflection
        )

    @property
    def klingelnberg_cyclo_palloid_spiral_bevel_gear_mesh_advanced_system_deflection(
        self: "CastSelf",
    ) -> "_7522.KlingelnbergCycloPalloidSpiralBevelGearMeshAdvancedSystemDeflection":
        from mastapy._private.system_model.analyses_and_results.advanced_system_deflections import (
            _7522,
        )

        return self.__parent__._cast(
            _7522.KlingelnbergCycloPalloidSpiralBevelGearMeshAdvancedSystemDeflection
        )

    @property
    def klingelnberg_cyclo_palloid_conical_gear_mesh_advanced_system_deflection(
        self: "CastSelf",
    ) -> "KlingelnbergCycloPalloidConicalGearMeshAdvancedSystemDeflection":
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
class KlingelnbergCycloPalloidConicalGearMeshAdvancedSystemDeflection(
    _7480.ConicalGearMeshAdvancedSystemDeflection
):
    """KlingelnbergCycloPalloidConicalGearMeshAdvancedSystemDeflection

    This is a mastapy class.
    """

    TYPE: ClassVar["Type"] = (
        _KLINGELNBERG_CYCLO_PALLOID_CONICAL_GEAR_MESH_ADVANCED_SYSTEM_DEFLECTION
    )

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
    ) -> "_Cast_KlingelnbergCycloPalloidConicalGearMeshAdvancedSystemDeflection":
        """Cast to another type.

        Returns:
            _Cast_KlingelnbergCycloPalloidConicalGearMeshAdvancedSystemDeflection
        """
        return _Cast_KlingelnbergCycloPalloidConicalGearMeshAdvancedSystemDeflection(
            self
        )
