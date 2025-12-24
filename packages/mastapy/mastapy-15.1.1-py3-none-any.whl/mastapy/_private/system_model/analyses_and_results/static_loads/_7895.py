"""SynchroniserSleeveLoadCase"""

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
from mastapy._private.system_model.analyses_and_results.static_loads import _7894

_SYNCHRONISER_SLEEVE_LOAD_CASE = python_net_import(
    "SMT.MastaAPI.SystemModel.AnalysesAndResults.StaticLoads",
    "SynchroniserSleeveLoadCase",
)

if TYPE_CHECKING:
    from typing import Any, Type, TypeVar

    from mastapy._private.system_model.analyses_and_results import _2943, _2945, _2949
    from mastapy._private.system_model.analyses_and_results.static_loads import (
        _7758,
        _7773,
        _7847,
        _7851,
    )
    from mastapy._private.system_model.part_model.couplings import _2896

    Self = TypeVar("Self", bound="SynchroniserSleeveLoadCase")
    CastSelf = TypeVar(
        "CastSelf", bound="SynchroniserSleeveLoadCase._Cast_SynchroniserSleeveLoadCase"
    )


__docformat__ = "restructuredtext en"
__all__ = ("SynchroniserSleeveLoadCase",)


@extended_dataclass(frozen=True, slots=True, weakref_slot=True)
class _Cast_SynchroniserSleeveLoadCase:
    """Special nested class for casting SynchroniserSleeveLoadCase to subclasses."""

    __parent__: "SynchroniserSleeveLoadCase"

    @property
    def synchroniser_part_load_case(
        self: "CastSelf",
    ) -> "_7894.SynchroniserPartLoadCase":
        return self.__parent__._cast(_7894.SynchroniserPartLoadCase)

    @property
    def coupling_half_load_case(self: "CastSelf") -> "_7773.CouplingHalfLoadCase":
        from mastapy._private.system_model.analyses_and_results.static_loads import (
            _7773,
        )

        return self.__parent__._cast(_7773.CouplingHalfLoadCase)

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
    def synchroniser_sleeve_load_case(self: "CastSelf") -> "SynchroniserSleeveLoadCase":
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
class SynchroniserSleeveLoadCase(_7894.SynchroniserPartLoadCase):
    """SynchroniserSleeveLoadCase

    This is a mastapy class.
    """

    TYPE: ClassVar["Type"] = _SYNCHRONISER_SLEEVE_LOAD_CASE

    wrapped: "Any"

    def __post_init__(self: "Self") -> None:
        """Override of the post initialisation magic method."""
        if not hasattr(self.wrapped, "reference_count"):
            self.wrapped.reference_count = 0

        self.wrapped.reference_count += 1

    @property
    @exception_bridge
    def component_design(self: "Self") -> "_2896.SynchroniserSleeve":
        """mastapy.system_model.part_model.couplings.SynchroniserSleeve

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "ComponentDesign")

        if temp is None:
            return None

        type_ = temp.GetType()
        return constructor.new(type_.Namespace, type_.Name)(temp)

    @property
    def cast_to(self: "Self") -> "_Cast_SynchroniserSleeveLoadCase":
        """Cast to another type.

        Returns:
            _Cast_SynchroniserSleeveLoadCase
        """
        return _Cast_SynchroniserSleeveLoadCase(self)
