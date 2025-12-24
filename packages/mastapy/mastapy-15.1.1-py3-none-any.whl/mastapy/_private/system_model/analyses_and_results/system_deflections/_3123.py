"""TorqueConverterPumpSystemDeflection"""

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
from mastapy._private.system_model.analyses_and_results.system_deflections import _3022

_TORQUE_CONVERTER_PUMP_SYSTEM_DEFLECTION = python_net_import(
    "SMT.MastaAPI.SystemModel.AnalysesAndResults.SystemDeflections",
    "TorqueConverterPumpSystemDeflection",
)

if TYPE_CHECKING:
    from typing import Any, Type, TypeVar

    from mastapy._private.system_model.analyses_and_results import _2943, _2945, _2949
    from mastapy._private.system_model.analyses_and_results.analysis_cases import (
        _7941,
        _7943,
        _7944,
    )
    from mastapy._private.system_model.analyses_and_results.power_flows import _4472
    from mastapy._private.system_model.analyses_and_results.static_loads import _7900
    from mastapy._private.system_model.analyses_and_results.system_deflections import (
        _3007,
        _3076,
        _3079,
    )
    from mastapy._private.system_model.part_model.couplings import _2898

    Self = TypeVar("Self", bound="TorqueConverterPumpSystemDeflection")
    CastSelf = TypeVar(
        "CastSelf",
        bound="TorqueConverterPumpSystemDeflection._Cast_TorqueConverterPumpSystemDeflection",
    )


__docformat__ = "restructuredtext en"
__all__ = ("TorqueConverterPumpSystemDeflection",)


@extended_dataclass(frozen=True, slots=True, weakref_slot=True)
class _Cast_TorqueConverterPumpSystemDeflection:
    """Special nested class for casting TorqueConverterPumpSystemDeflection to subclasses."""

    __parent__: "TorqueConverterPumpSystemDeflection"

    @property
    def coupling_half_system_deflection(
        self: "CastSelf",
    ) -> "_3022.CouplingHalfSystemDeflection":
        return self.__parent__._cast(_3022.CouplingHalfSystemDeflection)

    @property
    def mountable_component_system_deflection(
        self: "CastSelf",
    ) -> "_3076.MountableComponentSystemDeflection":
        from mastapy._private.system_model.analyses_and_results.system_deflections import (
            _3076,
        )

        return self.__parent__._cast(_3076.MountableComponentSystemDeflection)

    @property
    def component_system_deflection(
        self: "CastSelf",
    ) -> "_3007.ComponentSystemDeflection":
        from mastapy._private.system_model.analyses_and_results.system_deflections import (
            _3007,
        )

        return self.__parent__._cast(_3007.ComponentSystemDeflection)

    @property
    def part_system_deflection(self: "CastSelf") -> "_3079.PartSystemDeflection":
        from mastapy._private.system_model.analyses_and_results.system_deflections import (
            _3079,
        )

        return self.__parent__._cast(_3079.PartSystemDeflection)

    @property
    def part_fe_analysis(self: "CastSelf") -> "_7943.PartFEAnalysis":
        from mastapy._private.system_model.analyses_and_results.analysis_cases import (
            _7943,
        )

        return self.__parent__._cast(_7943.PartFEAnalysis)

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
    def torque_converter_pump_system_deflection(
        self: "CastSelf",
    ) -> "TorqueConverterPumpSystemDeflection":
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
class TorqueConverterPumpSystemDeflection(_3022.CouplingHalfSystemDeflection):
    """TorqueConverterPumpSystemDeflection

    This is a mastapy class.
    """

    TYPE: ClassVar["Type"] = _TORQUE_CONVERTER_PUMP_SYSTEM_DEFLECTION

    wrapped: "Any"

    def __post_init__(self: "Self") -> None:
        """Override of the post initialisation magic method."""
        if not hasattr(self.wrapped, "reference_count"):
            self.wrapped.reference_count = 0

        self.wrapped.reference_count += 1

    @property
    @exception_bridge
    def component_design(self: "Self") -> "_2898.TorqueConverterPump":
        """mastapy.system_model.part_model.couplings.TorqueConverterPump

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
    def component_load_case(self: "Self") -> "_7900.TorqueConverterPumpLoadCase":
        """mastapy.system_model.analyses_and_results.static_loads.TorqueConverterPumpLoadCase

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "ComponentLoadCase")

        if temp is None:
            return None

        type_ = temp.GetType()
        return constructor.new(type_.Namespace, type_.Name)(temp)

    @property
    @exception_bridge
    def power_flow_results(self: "Self") -> "_4472.TorqueConverterPumpPowerFlow":
        """mastapy.system_model.analyses_and_results.power_flows.TorqueConverterPumpPowerFlow

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "PowerFlowResults")

        if temp is None:
            return None

        type_ = temp.GetType()
        return constructor.new(type_.Namespace, type_.Name)(temp)

    @property
    def cast_to(self: "Self") -> "_Cast_TorqueConverterPumpSystemDeflection":
        """Cast to another type.

        Returns:
            _Cast_TorqueConverterPumpSystemDeflection
        """
        return _Cast_TorqueConverterPumpSystemDeflection(self)
