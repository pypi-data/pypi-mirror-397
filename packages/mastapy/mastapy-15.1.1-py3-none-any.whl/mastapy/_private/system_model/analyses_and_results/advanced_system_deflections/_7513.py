"""HypoidGearSetAdvancedSystemDeflection"""

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
from mastapy._private.system_model.analyses_and_results.advanced_system_deflections import (
    _7453,
)

_HYPOID_GEAR_SET_ADVANCED_SYSTEM_DEFLECTION = python_net_import(
    "SMT.MastaAPI.SystemModel.AnalysesAndResults.AdvancedSystemDeflections",
    "HypoidGearSetAdvancedSystemDeflection",
)

if TYPE_CHECKING:
    from typing import Any, List, Type, TypeVar

    from mastapy._private.gears.rating.hypoid import _553
    from mastapy._private.system_model.analyses_and_results import _2943, _2945, _2949
    from mastapy._private.system_model.analyses_and_results.advanced_system_deflections import (
        _7444,
        _7481,
        _7509,
        _7511,
        _7512,
        _7531,
        _7550,
    )
    from mastapy._private.system_model.analyses_and_results.analysis_cases import (
        _7941,
        _7944,
    )
    from mastapy._private.system_model.analyses_and_results.static_loads import _7828
    from mastapy._private.system_model.analyses_and_results.system_deflections import (
        _3056,
    )
    from mastapy._private.system_model.part_model.gears import _2816

    Self = TypeVar("Self", bound="HypoidGearSetAdvancedSystemDeflection")
    CastSelf = TypeVar(
        "CastSelf",
        bound="HypoidGearSetAdvancedSystemDeflection._Cast_HypoidGearSetAdvancedSystemDeflection",
    )


__docformat__ = "restructuredtext en"
__all__ = ("HypoidGearSetAdvancedSystemDeflection",)


@extended_dataclass(frozen=True, slots=True, weakref_slot=True)
class _Cast_HypoidGearSetAdvancedSystemDeflection:
    """Special nested class for casting HypoidGearSetAdvancedSystemDeflection to subclasses."""

    __parent__: "HypoidGearSetAdvancedSystemDeflection"

    @property
    def agma_gleason_conical_gear_set_advanced_system_deflection(
        self: "CastSelf",
    ) -> "_7453.AGMAGleasonConicalGearSetAdvancedSystemDeflection":
        return self.__parent__._cast(
            _7453.AGMAGleasonConicalGearSetAdvancedSystemDeflection
        )

    @property
    def conical_gear_set_advanced_system_deflection(
        self: "CastSelf",
    ) -> "_7481.ConicalGearSetAdvancedSystemDeflection":
        from mastapy._private.system_model.analyses_and_results.advanced_system_deflections import (
            _7481,
        )

        return self.__parent__._cast(_7481.ConicalGearSetAdvancedSystemDeflection)

    @property
    def gear_set_advanced_system_deflection(
        self: "CastSelf",
    ) -> "_7509.GearSetAdvancedSystemDeflection":
        from mastapy._private.system_model.analyses_and_results.advanced_system_deflections import (
            _7509,
        )

        return self.__parent__._cast(_7509.GearSetAdvancedSystemDeflection)

    @property
    def specialised_assembly_advanced_system_deflection(
        self: "CastSelf",
    ) -> "_7550.SpecialisedAssemblyAdvancedSystemDeflection":
        from mastapy._private.system_model.analyses_and_results.advanced_system_deflections import (
            _7550,
        )

        return self.__parent__._cast(_7550.SpecialisedAssemblyAdvancedSystemDeflection)

    @property
    def abstract_assembly_advanced_system_deflection(
        self: "CastSelf",
    ) -> "_7444.AbstractAssemblyAdvancedSystemDeflection":
        from mastapy._private.system_model.analyses_and_results.advanced_system_deflections import (
            _7444,
        )

        return self.__parent__._cast(_7444.AbstractAssemblyAdvancedSystemDeflection)

    @property
    def part_advanced_system_deflection(
        self: "CastSelf",
    ) -> "_7531.PartAdvancedSystemDeflection":
        from mastapy._private.system_model.analyses_and_results.advanced_system_deflections import (
            _7531,
        )

        return self.__parent__._cast(_7531.PartAdvancedSystemDeflection)

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
    def hypoid_gear_set_advanced_system_deflection(
        self: "CastSelf",
    ) -> "HypoidGearSetAdvancedSystemDeflection":
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
class HypoidGearSetAdvancedSystemDeflection(
    _7453.AGMAGleasonConicalGearSetAdvancedSystemDeflection
):
    """HypoidGearSetAdvancedSystemDeflection

    This is a mastapy class.
    """

    TYPE: ClassVar["Type"] = _HYPOID_GEAR_SET_ADVANCED_SYSTEM_DEFLECTION

    wrapped: "Any"

    def __post_init__(self: "Self") -> None:
        """Override of the post initialisation magic method."""
        if not hasattr(self.wrapped, "reference_count"):
            self.wrapped.reference_count = 0

        self.wrapped.reference_count += 1

    @property
    @exception_bridge
    def assembly_design(self: "Self") -> "_2816.HypoidGearSet":
        """mastapy.system_model.part_model.gears.HypoidGearSet

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
    def assembly_load_case(self: "Self") -> "_7828.HypoidGearSetLoadCase":
        """mastapy.system_model.analyses_and_results.static_loads.HypoidGearSetLoadCase

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
    def rating(self: "Self") -> "_553.HypoidGearSetRating":
        """mastapy.gears.rating.hypoid.HypoidGearSetRating

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
    def component_detailed_analysis(self: "Self") -> "_553.HypoidGearSetRating":
        """mastapy.gears.rating.hypoid.HypoidGearSetRating

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "ComponentDetailedAnalysis")

        if temp is None:
            return None

        type_ = temp.GetType()
        return constructor.new(type_.Namespace, type_.Name)(temp)

    @property
    @exception_bridge
    def assembly_system_deflection_results(
        self: "Self",
    ) -> "List[_3056.HypoidGearSetSystemDeflection]":
        """List[mastapy.system_model.analyses_and_results.system_deflections.HypoidGearSetSystemDeflection]

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "AssemblySystemDeflectionResults")

        if temp is None:
            return None

        value = conversion.pn_to_mp_objects_in_list(temp)

        if value is None:
            return None

        return value

    @property
    @exception_bridge
    def agma_gleason_conical_gears_advanced_system_deflection(
        self: "Self",
    ) -> "List[_7511.HypoidGearAdvancedSystemDeflection]":
        """List[mastapy.system_model.analyses_and_results.advanced_system_deflections.HypoidGearAdvancedSystemDeflection]

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(
            self.wrapped, "AGMAGleasonConicalGearsAdvancedSystemDeflection"
        )

        if temp is None:
            return None

        value = conversion.pn_to_mp_objects_in_list(temp)

        if value is None:
            return None

        return value

    @property
    @exception_bridge
    def hypoid_gears_advanced_system_deflection(
        self: "Self",
    ) -> "List[_7511.HypoidGearAdvancedSystemDeflection]":
        """List[mastapy.system_model.analyses_and_results.advanced_system_deflections.HypoidGearAdvancedSystemDeflection]

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(
            self.wrapped, "HypoidGearsAdvancedSystemDeflection"
        )

        if temp is None:
            return None

        value = conversion.pn_to_mp_objects_in_list(temp)

        if value is None:
            return None

        return value

    @property
    @exception_bridge
    def agma_gleason_conical_meshes_advanced_system_deflection(
        self: "Self",
    ) -> "List[_7512.HypoidGearMeshAdvancedSystemDeflection]":
        """List[mastapy.system_model.analyses_and_results.advanced_system_deflections.HypoidGearMeshAdvancedSystemDeflection]

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(
            self.wrapped, "AGMAGleasonConicalMeshesAdvancedSystemDeflection"
        )

        if temp is None:
            return None

        value = conversion.pn_to_mp_objects_in_list(temp)

        if value is None:
            return None

        return value

    @property
    @exception_bridge
    def hypoid_meshes_advanced_system_deflection(
        self: "Self",
    ) -> "List[_7512.HypoidGearMeshAdvancedSystemDeflection]":
        """List[mastapy.system_model.analyses_and_results.advanced_system_deflections.HypoidGearMeshAdvancedSystemDeflection]

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(
            self.wrapped, "HypoidMeshesAdvancedSystemDeflection"
        )

        if temp is None:
            return None

        value = conversion.pn_to_mp_objects_in_list(temp)

        if value is None:
            return None

        return value

    @property
    def cast_to(self: "Self") -> "_Cast_HypoidGearSetAdvancedSystemDeflection":
        """Cast to another type.

        Returns:
            _Cast_HypoidGearSetAdvancedSystemDeflection
        """
        return _Cast_HypoidGearSetAdvancedSystemDeflection(self)
