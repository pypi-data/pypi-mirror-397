"""VirtualComponentLoadCase"""

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
from mastapy._private.system_model.analyses_and_results.static_loads import _7847

_VIRTUAL_COMPONENT_LOAD_CASE = python_net_import(
    "SMT.MastaAPI.SystemModel.AnalysesAndResults.StaticLoads",
    "VirtualComponentLoadCase",
)

if TYPE_CHECKING:
    from typing import Any, Type, TypeVar

    from mastapy._private.system_model.analyses_and_results import _2943, _2945, _2949
    from mastapy._private.system_model.analyses_and_results.static_loads import (
        _7758,
        _7842,
        _7843,
        _7851,
        _7861,
        _7862,
        _7906,
    )
    from mastapy._private.system_model.part_model import _2755

    Self = TypeVar("Self", bound="VirtualComponentLoadCase")
    CastSelf = TypeVar(
        "CastSelf", bound="VirtualComponentLoadCase._Cast_VirtualComponentLoadCase"
    )


__docformat__ = "restructuredtext en"
__all__ = ("VirtualComponentLoadCase",)


@extended_dataclass(frozen=True, slots=True, weakref_slot=True)
class _Cast_VirtualComponentLoadCase:
    """Special nested class for casting VirtualComponentLoadCase to subclasses."""

    __parent__: "VirtualComponentLoadCase"

    @property
    def mountable_component_load_case(
        self: "CastSelf",
    ) -> "_7847.MountableComponentLoadCase":
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
    def mass_disc_load_case(self: "CastSelf") -> "_7842.MassDiscLoadCase":
        from mastapy._private.system_model.analyses_and_results.static_loads import (
            _7842,
        )

        return self.__parent__._cast(_7842.MassDiscLoadCase)

    @property
    def measurement_component_load_case(
        self: "CastSelf",
    ) -> "_7843.MeasurementComponentLoadCase":
        from mastapy._private.system_model.analyses_and_results.static_loads import (
            _7843,
        )

        return self.__parent__._cast(_7843.MeasurementComponentLoadCase)

    @property
    def point_load_load_case(self: "CastSelf") -> "_7861.PointLoadLoadCase":
        from mastapy._private.system_model.analyses_and_results.static_loads import (
            _7861,
        )

        return self.__parent__._cast(_7861.PointLoadLoadCase)

    @property
    def power_load_load_case(self: "CastSelf") -> "_7862.PowerLoadLoadCase":
        from mastapy._private.system_model.analyses_and_results.static_loads import (
            _7862,
        )

        return self.__parent__._cast(_7862.PowerLoadLoadCase)

    @property
    def unbalanced_mass_load_case(self: "CastSelf") -> "_7906.UnbalancedMassLoadCase":
        from mastapy._private.system_model.analyses_and_results.static_loads import (
            _7906,
        )

        return self.__parent__._cast(_7906.UnbalancedMassLoadCase)

    @property
    def virtual_component_load_case(self: "CastSelf") -> "VirtualComponentLoadCase":
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
class VirtualComponentLoadCase(_7847.MountableComponentLoadCase):
    """VirtualComponentLoadCase

    This is a mastapy class.
    """

    TYPE: ClassVar["Type"] = _VIRTUAL_COMPONENT_LOAD_CASE

    wrapped: "Any"

    def __post_init__(self: "Self") -> None:
        """Override of the post initialisation magic method."""
        if not hasattr(self.wrapped, "reference_count"):
            self.wrapped.reference_count = 0

        self.wrapped.reference_count += 1

    @property
    @exception_bridge
    def component_design(self: "Self") -> "_2755.VirtualComponent":
        """mastapy.system_model.part_model.VirtualComponent

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "ComponentDesign")

        if temp is None:
            return None

        type_ = temp.GetType()
        return constructor.new(type_.Namespace, type_.Name)(temp)

    @property
    def cast_to(self: "Self") -> "_Cast_VirtualComponentLoadCase":
        """Cast to another type.

        Returns:
            _Cast_VirtualComponentLoadCase
        """
        return _Cast_VirtualComponentLoadCase(self)
