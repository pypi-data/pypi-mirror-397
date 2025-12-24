"""CouplingHalfLoadCase"""

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

_COUPLING_HALF_LOAD_CASE = python_net_import(
    "SMT.MastaAPI.SystemModel.AnalysesAndResults.StaticLoads", "CouplingHalfLoadCase"
)

if TYPE_CHECKING:
    from typing import Any, Type, TypeVar

    from mastapy._private.system_model.analyses_and_results import _2943, _2945, _2949
    from mastapy._private.system_model.analyses_and_results.static_loads import (
        _7754,
        _7758,
        _7760,
        _7777,
        _7851,
        _7853,
        _7863,
        _7872,
        _7882,
        _7892,
        _7894,
        _7895,
        _7900,
        _7901,
    )
    from mastapy._private.system_model.part_model.couplings import _2868

    Self = TypeVar("Self", bound="CouplingHalfLoadCase")
    CastSelf = TypeVar(
        "CastSelf", bound="CouplingHalfLoadCase._Cast_CouplingHalfLoadCase"
    )


__docformat__ = "restructuredtext en"
__all__ = ("CouplingHalfLoadCase",)


@extended_dataclass(frozen=True, slots=True, weakref_slot=True)
class _Cast_CouplingHalfLoadCase:
    """Special nested class for casting CouplingHalfLoadCase to subclasses."""

    __parent__: "CouplingHalfLoadCase"

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
    def clutch_half_load_case(self: "CastSelf") -> "_7754.ClutchHalfLoadCase":
        from mastapy._private.system_model.analyses_and_results.static_loads import (
            _7754,
        )

        return self.__parent__._cast(_7754.ClutchHalfLoadCase)

    @property
    def concept_coupling_half_load_case(
        self: "CastSelf",
    ) -> "_7760.ConceptCouplingHalfLoadCase":
        from mastapy._private.system_model.analyses_and_results.static_loads import (
            _7760,
        )

        return self.__parent__._cast(_7760.ConceptCouplingHalfLoadCase)

    @property
    def cvt_pulley_load_case(self: "CastSelf") -> "_7777.CVTPulleyLoadCase":
        from mastapy._private.system_model.analyses_and_results.static_loads import (
            _7777,
        )

        return self.__parent__._cast(_7777.CVTPulleyLoadCase)

    @property
    def part_to_part_shear_coupling_half_load_case(
        self: "CastSelf",
    ) -> "_7853.PartToPartShearCouplingHalfLoadCase":
        from mastapy._private.system_model.analyses_and_results.static_loads import (
            _7853,
        )

        return self.__parent__._cast(_7853.PartToPartShearCouplingHalfLoadCase)

    @property
    def pulley_load_case(self: "CastSelf") -> "_7863.PulleyLoadCase":
        from mastapy._private.system_model.analyses_and_results.static_loads import (
            _7863,
        )

        return self.__parent__._cast(_7863.PulleyLoadCase)

    @property
    def rolling_ring_load_case(self: "CastSelf") -> "_7872.RollingRingLoadCase":
        from mastapy._private.system_model.analyses_and_results.static_loads import (
            _7872,
        )

        return self.__parent__._cast(_7872.RollingRingLoadCase)

    @property
    def spring_damper_half_load_case(
        self: "CastSelf",
    ) -> "_7882.SpringDamperHalfLoadCase":
        from mastapy._private.system_model.analyses_and_results.static_loads import (
            _7882,
        )

        return self.__parent__._cast(_7882.SpringDamperHalfLoadCase)

    @property
    def synchroniser_half_load_case(
        self: "CastSelf",
    ) -> "_7892.SynchroniserHalfLoadCase":
        from mastapy._private.system_model.analyses_and_results.static_loads import (
            _7892,
        )

        return self.__parent__._cast(_7892.SynchroniserHalfLoadCase)

    @property
    def synchroniser_part_load_case(
        self: "CastSelf",
    ) -> "_7894.SynchroniserPartLoadCase":
        from mastapy._private.system_model.analyses_and_results.static_loads import (
            _7894,
        )

        return self.__parent__._cast(_7894.SynchroniserPartLoadCase)

    @property
    def synchroniser_sleeve_load_case(
        self: "CastSelf",
    ) -> "_7895.SynchroniserSleeveLoadCase":
        from mastapy._private.system_model.analyses_and_results.static_loads import (
            _7895,
        )

        return self.__parent__._cast(_7895.SynchroniserSleeveLoadCase)

    @property
    def torque_converter_pump_load_case(
        self: "CastSelf",
    ) -> "_7900.TorqueConverterPumpLoadCase":
        from mastapy._private.system_model.analyses_and_results.static_loads import (
            _7900,
        )

        return self.__parent__._cast(_7900.TorqueConverterPumpLoadCase)

    @property
    def torque_converter_turbine_load_case(
        self: "CastSelf",
    ) -> "_7901.TorqueConverterTurbineLoadCase":
        from mastapy._private.system_model.analyses_and_results.static_loads import (
            _7901,
        )

        return self.__parent__._cast(_7901.TorqueConverterTurbineLoadCase)

    @property
    def coupling_half_load_case(self: "CastSelf") -> "CouplingHalfLoadCase":
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
class CouplingHalfLoadCase(_7847.MountableComponentLoadCase):
    """CouplingHalfLoadCase

    This is a mastapy class.
    """

    TYPE: ClassVar["Type"] = _COUPLING_HALF_LOAD_CASE

    wrapped: "Any"

    def __post_init__(self: "Self") -> None:
        """Override of the post initialisation magic method."""
        if not hasattr(self.wrapped, "reference_count"):
            self.wrapped.reference_count = 0

        self.wrapped.reference_count += 1

    @property
    @exception_bridge
    def component_design(self: "Self") -> "_2868.CouplingHalf":
        """mastapy.system_model.part_model.couplings.CouplingHalf

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "ComponentDesign")

        if temp is None:
            return None

        type_ = temp.GetType()
        return constructor.new(type_.Namespace, type_.Name)(temp)

    @property
    def cast_to(self: "Self") -> "_Cast_CouplingHalfLoadCase":
        """Cast to another type.

        Returns:
            _Cast_CouplingHalfLoadCase
        """
        return _Cast_CouplingHalfLoadCase(self)
