"""VirtualComponentCompoundDynamicAnalysis"""

from __future__ import annotations

from typing import TYPE_CHECKING, ClassVar

from mastapy._private._internal.dataclasses import extended_dataclass
from mastapy._private._internal.exception_bridge import exception_bridge
from mastapy._private._internal.exceptions import CastException
from mastapy._private._internal.python_net import (
    python_net_import,
    pythonnet_property_get,
)

from mastapy._private._internal import conversion, utility
from mastapy._private.system_model.analyses_and_results.dynamic_analyses.compound import (
    _6853,
)

_VIRTUAL_COMPONENT_COMPOUND_DYNAMIC_ANALYSIS = python_net_import(
    "SMT.MastaAPI.SystemModel.AnalysesAndResults.DynamicAnalyses.Compound",
    "VirtualComponentCompoundDynamicAnalysis",
)

if TYPE_CHECKING:
    from typing import Any, List, Type, TypeVar

    from mastapy._private.system_model.analyses_and_results import _2943
    from mastapy._private.system_model.analyses_and_results.analysis_cases import (
        _7939,
        _7942,
    )
    from mastapy._private.system_model.analyses_and_results.dynamic_analyses import (
        _6767,
    )
    from mastapy._private.system_model.analyses_and_results.dynamic_analyses.compound import (
        _6799,
        _6849,
        _6850,
        _6855,
        _6862,
        _6863,
        _6897,
    )

    Self = TypeVar("Self", bound="VirtualComponentCompoundDynamicAnalysis")
    CastSelf = TypeVar(
        "CastSelf",
        bound="VirtualComponentCompoundDynamicAnalysis._Cast_VirtualComponentCompoundDynamicAnalysis",
    )


__docformat__ = "restructuredtext en"
__all__ = ("VirtualComponentCompoundDynamicAnalysis",)


@extended_dataclass(frozen=True, slots=True, weakref_slot=True)
class _Cast_VirtualComponentCompoundDynamicAnalysis:
    """Special nested class for casting VirtualComponentCompoundDynamicAnalysis to subclasses."""

    __parent__: "VirtualComponentCompoundDynamicAnalysis"

    @property
    def mountable_component_compound_dynamic_analysis(
        self: "CastSelf",
    ) -> "_6853.MountableComponentCompoundDynamicAnalysis":
        return self.__parent__._cast(_6853.MountableComponentCompoundDynamicAnalysis)

    @property
    def component_compound_dynamic_analysis(
        self: "CastSelf",
    ) -> "_6799.ComponentCompoundDynamicAnalysis":
        from mastapy._private.system_model.analyses_and_results.dynamic_analyses.compound import (
            _6799,
        )

        return self.__parent__._cast(_6799.ComponentCompoundDynamicAnalysis)

    @property
    def part_compound_dynamic_analysis(
        self: "CastSelf",
    ) -> "_6855.PartCompoundDynamicAnalysis":
        from mastapy._private.system_model.analyses_and_results.dynamic_analyses.compound import (
            _6855,
        )

        return self.__parent__._cast(_6855.PartCompoundDynamicAnalysis)

    @property
    def part_compound_analysis(self: "CastSelf") -> "_7942.PartCompoundAnalysis":
        from mastapy._private.system_model.analyses_and_results.analysis_cases import (
            _7942,
        )

        return self.__parent__._cast(_7942.PartCompoundAnalysis)

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
    def mass_disc_compound_dynamic_analysis(
        self: "CastSelf",
    ) -> "_6849.MassDiscCompoundDynamicAnalysis":
        from mastapy._private.system_model.analyses_and_results.dynamic_analyses.compound import (
            _6849,
        )

        return self.__parent__._cast(_6849.MassDiscCompoundDynamicAnalysis)

    @property
    def measurement_component_compound_dynamic_analysis(
        self: "CastSelf",
    ) -> "_6850.MeasurementComponentCompoundDynamicAnalysis":
        from mastapy._private.system_model.analyses_and_results.dynamic_analyses.compound import (
            _6850,
        )

        return self.__parent__._cast(_6850.MeasurementComponentCompoundDynamicAnalysis)

    @property
    def point_load_compound_dynamic_analysis(
        self: "CastSelf",
    ) -> "_6862.PointLoadCompoundDynamicAnalysis":
        from mastapy._private.system_model.analyses_and_results.dynamic_analyses.compound import (
            _6862,
        )

        return self.__parent__._cast(_6862.PointLoadCompoundDynamicAnalysis)

    @property
    def power_load_compound_dynamic_analysis(
        self: "CastSelf",
    ) -> "_6863.PowerLoadCompoundDynamicAnalysis":
        from mastapy._private.system_model.analyses_and_results.dynamic_analyses.compound import (
            _6863,
        )

        return self.__parent__._cast(_6863.PowerLoadCompoundDynamicAnalysis)

    @property
    def unbalanced_mass_compound_dynamic_analysis(
        self: "CastSelf",
    ) -> "_6897.UnbalancedMassCompoundDynamicAnalysis":
        from mastapy._private.system_model.analyses_and_results.dynamic_analyses.compound import (
            _6897,
        )

        return self.__parent__._cast(_6897.UnbalancedMassCompoundDynamicAnalysis)

    @property
    def virtual_component_compound_dynamic_analysis(
        self: "CastSelf",
    ) -> "VirtualComponentCompoundDynamicAnalysis":
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
class VirtualComponentCompoundDynamicAnalysis(
    _6853.MountableComponentCompoundDynamicAnalysis
):
    """VirtualComponentCompoundDynamicAnalysis

    This is a mastapy class.
    """

    TYPE: ClassVar["Type"] = _VIRTUAL_COMPONENT_COMPOUND_DYNAMIC_ANALYSIS

    wrapped: "Any"

    def __post_init__(self: "Self") -> None:
        """Override of the post initialisation magic method."""
        if not hasattr(self.wrapped, "reference_count"):
            self.wrapped.reference_count = 0

        self.wrapped.reference_count += 1

    @property
    @exception_bridge
    def component_analysis_cases(
        self: "Self",
    ) -> "List[_6767.VirtualComponentDynamicAnalysis]":
        """List[mastapy.system_model.analyses_and_results.dynamic_analyses.VirtualComponentDynamicAnalysis]

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "ComponentAnalysisCases")

        if temp is None:
            return None

        value = conversion.pn_to_mp_objects_in_list(temp)

        if value is None:
            return None

        return value

    @property
    @exception_bridge
    def component_analysis_cases_ready(
        self: "Self",
    ) -> "List[_6767.VirtualComponentDynamicAnalysis]":
        """List[mastapy.system_model.analyses_and_results.dynamic_analyses.VirtualComponentDynamicAnalysis]

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "ComponentAnalysisCasesReady")

        if temp is None:
            return None

        value = conversion.pn_to_mp_objects_in_list(temp)

        if value is None:
            return None

        return value

    @property
    def cast_to(self: "Self") -> "_Cast_VirtualComponentCompoundDynamicAnalysis":
        """Cast to another type.

        Returns:
            _Cast_VirtualComponentCompoundDynamicAnalysis
        """
        return _Cast_VirtualComponentCompoundDynamicAnalysis(self)
