"""KlingelnbergCycloPalloidSpiralBevelGearLoadCase"""

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
from mastapy._private.system_model.analyses_and_results.static_loads import _7833

_KLINGELNBERG_CYCLO_PALLOID_SPIRAL_BEVEL_GEAR_LOAD_CASE = python_net_import(
    "SMT.MastaAPI.SystemModel.AnalysesAndResults.StaticLoads",
    "KlingelnbergCycloPalloidSpiralBevelGearLoadCase",
)

if TYPE_CHECKING:
    from typing import Any, Type, TypeVar

    from mastapy._private.system_model.analyses_and_results import _2943, _2945, _2949
    from mastapy._private.system_model.analyses_and_results.static_loads import (
        _7758,
        _7765,
        _7811,
        _7847,
        _7851,
    )
    from mastapy._private.system_model.part_model.gears import _2821

    Self = TypeVar("Self", bound="KlingelnbergCycloPalloidSpiralBevelGearLoadCase")
    CastSelf = TypeVar(
        "CastSelf",
        bound="KlingelnbergCycloPalloidSpiralBevelGearLoadCase._Cast_KlingelnbergCycloPalloidSpiralBevelGearLoadCase",
    )


__docformat__ = "restructuredtext en"
__all__ = ("KlingelnbergCycloPalloidSpiralBevelGearLoadCase",)


@extended_dataclass(frozen=True, slots=True, weakref_slot=True)
class _Cast_KlingelnbergCycloPalloidSpiralBevelGearLoadCase:
    """Special nested class for casting KlingelnbergCycloPalloidSpiralBevelGearLoadCase to subclasses."""

    __parent__: "KlingelnbergCycloPalloidSpiralBevelGearLoadCase"

    @property
    def klingelnberg_cyclo_palloid_conical_gear_load_case(
        self: "CastSelf",
    ) -> "_7833.KlingelnbergCycloPalloidConicalGearLoadCase":
        return self.__parent__._cast(_7833.KlingelnbergCycloPalloidConicalGearLoadCase)

    @property
    def conical_gear_load_case(self: "CastSelf") -> "_7765.ConicalGearLoadCase":
        from mastapy._private.system_model.analyses_and_results.static_loads import (
            _7765,
        )

        return self.__parent__._cast(_7765.ConicalGearLoadCase)

    @property
    def gear_load_case(self: "CastSelf") -> "_7811.GearLoadCase":
        from mastapy._private.system_model.analyses_and_results.static_loads import (
            _7811,
        )

        return self.__parent__._cast(_7811.GearLoadCase)

    @property
    def mountable_component_load_case(
        self: "CastSelf",
    ) -> "_7847.MountableComponentLoadCase":
        from mastapy._private.system_model.analyses_and_results.static_loads import (
            _7847,
        )

        return self.__parent__._cast(_7847.MountableComponentLoadCase)

    @property
    def component_load_case(self: "CastSelf") -> "_7758.ComponentLoadCase":
        from mastapy._private.system_model.analyses_and_results.static_loads import (
            _7758,
        )

        return self.__parent__._cast(_7758.ComponentLoadCase)

    @property
    def part_load_case(self: "CastSelf") -> "_7851.PartLoadCase":
        from mastapy._private.system_model.analyses_and_results.static_loads import (
            _7851,
        )

        return self.__parent__._cast(_7851.PartLoadCase)

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
    def klingelnberg_cyclo_palloid_spiral_bevel_gear_load_case(
        self: "CastSelf",
    ) -> "KlingelnbergCycloPalloidSpiralBevelGearLoadCase":
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
class KlingelnbergCycloPalloidSpiralBevelGearLoadCase(
    _7833.KlingelnbergCycloPalloidConicalGearLoadCase
):
    """KlingelnbergCycloPalloidSpiralBevelGearLoadCase

    This is a mastapy class.
    """

    TYPE: ClassVar["Type"] = _KLINGELNBERG_CYCLO_PALLOID_SPIRAL_BEVEL_GEAR_LOAD_CASE

    wrapped: "Any"

    def __post_init__(self: "Self") -> None:
        """Override of the post initialisation magic method."""
        if not hasattr(self.wrapped, "reference_count"):
            self.wrapped.reference_count = 0

        self.wrapped.reference_count += 1

    @property
    @exception_bridge
    def component_design(
        self: "Self",
    ) -> "_2821.KlingelnbergCycloPalloidSpiralBevelGear":
        """mastapy.system_model.part_model.gears.KlingelnbergCycloPalloidSpiralBevelGear

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "ComponentDesign")

        if temp is None:
            return None

        type_ = temp.GetType()
        return constructor.new(type_.Namespace, type_.Name)(temp)

    @property
    def cast_to(
        self: "Self",
    ) -> "_Cast_KlingelnbergCycloPalloidSpiralBevelGearLoadCase":
        """Cast to another type.

        Returns:
            _Cast_KlingelnbergCycloPalloidSpiralBevelGearLoadCase
        """
        return _Cast_KlingelnbergCycloPalloidSpiralBevelGearLoadCase(self)
