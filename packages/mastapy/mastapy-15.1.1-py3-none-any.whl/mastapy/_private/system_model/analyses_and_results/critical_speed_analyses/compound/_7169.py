"""VirtualComponentCompoundCriticalSpeedAnalysis"""

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
from mastapy._private.system_model.analyses_and_results.critical_speed_analyses.compound import (
    _7124,
)

_VIRTUAL_COMPONENT_COMPOUND_CRITICAL_SPEED_ANALYSIS = python_net_import(
    "SMT.MastaAPI.SystemModel.AnalysesAndResults.CriticalSpeedAnalyses.Compound",
    "VirtualComponentCompoundCriticalSpeedAnalysis",
)

if TYPE_CHECKING:
    from typing import Any, List, Type, TypeVar

    from mastapy._private.system_model.analyses_and_results import _2943
    from mastapy._private.system_model.analyses_and_results.analysis_cases import (
        _7939,
        _7942,
    )
    from mastapy._private.system_model.analyses_and_results.critical_speed_analyses import (
        _7038,
    )
    from mastapy._private.system_model.analyses_and_results.critical_speed_analyses.compound import (
        _7070,
        _7120,
        _7121,
        _7126,
        _7133,
        _7134,
        _7168,
    )

    Self = TypeVar("Self", bound="VirtualComponentCompoundCriticalSpeedAnalysis")
    CastSelf = TypeVar(
        "CastSelf",
        bound="VirtualComponentCompoundCriticalSpeedAnalysis._Cast_VirtualComponentCompoundCriticalSpeedAnalysis",
    )


__docformat__ = "restructuredtext en"
__all__ = ("VirtualComponentCompoundCriticalSpeedAnalysis",)


@extended_dataclass(frozen=True, slots=True, weakref_slot=True)
class _Cast_VirtualComponentCompoundCriticalSpeedAnalysis:
    """Special nested class for casting VirtualComponentCompoundCriticalSpeedAnalysis to subclasses."""

    __parent__: "VirtualComponentCompoundCriticalSpeedAnalysis"

    @property
    def mountable_component_compound_critical_speed_analysis(
        self: "CastSelf",
    ) -> "_7124.MountableComponentCompoundCriticalSpeedAnalysis":
        return self.__parent__._cast(
            _7124.MountableComponentCompoundCriticalSpeedAnalysis
        )

    @property
    def component_compound_critical_speed_analysis(
        self: "CastSelf",
    ) -> "_7070.ComponentCompoundCriticalSpeedAnalysis":
        from mastapy._private.system_model.analyses_and_results.critical_speed_analyses.compound import (
            _7070,
        )

        return self.__parent__._cast(_7070.ComponentCompoundCriticalSpeedAnalysis)

    @property
    def part_compound_critical_speed_analysis(
        self: "CastSelf",
    ) -> "_7126.PartCompoundCriticalSpeedAnalysis":
        from mastapy._private.system_model.analyses_and_results.critical_speed_analyses.compound import (
            _7126,
        )

        return self.__parent__._cast(_7126.PartCompoundCriticalSpeedAnalysis)

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
    def mass_disc_compound_critical_speed_analysis(
        self: "CastSelf",
    ) -> "_7120.MassDiscCompoundCriticalSpeedAnalysis":
        from mastapy._private.system_model.analyses_and_results.critical_speed_analyses.compound import (
            _7120,
        )

        return self.__parent__._cast(_7120.MassDiscCompoundCriticalSpeedAnalysis)

    @property
    def measurement_component_compound_critical_speed_analysis(
        self: "CastSelf",
    ) -> "_7121.MeasurementComponentCompoundCriticalSpeedAnalysis":
        from mastapy._private.system_model.analyses_and_results.critical_speed_analyses.compound import (
            _7121,
        )

        return self.__parent__._cast(
            _7121.MeasurementComponentCompoundCriticalSpeedAnalysis
        )

    @property
    def point_load_compound_critical_speed_analysis(
        self: "CastSelf",
    ) -> "_7133.PointLoadCompoundCriticalSpeedAnalysis":
        from mastapy._private.system_model.analyses_and_results.critical_speed_analyses.compound import (
            _7133,
        )

        return self.__parent__._cast(_7133.PointLoadCompoundCriticalSpeedAnalysis)

    @property
    def power_load_compound_critical_speed_analysis(
        self: "CastSelf",
    ) -> "_7134.PowerLoadCompoundCriticalSpeedAnalysis":
        from mastapy._private.system_model.analyses_and_results.critical_speed_analyses.compound import (
            _7134,
        )

        return self.__parent__._cast(_7134.PowerLoadCompoundCriticalSpeedAnalysis)

    @property
    def unbalanced_mass_compound_critical_speed_analysis(
        self: "CastSelf",
    ) -> "_7168.UnbalancedMassCompoundCriticalSpeedAnalysis":
        from mastapy._private.system_model.analyses_and_results.critical_speed_analyses.compound import (
            _7168,
        )

        return self.__parent__._cast(_7168.UnbalancedMassCompoundCriticalSpeedAnalysis)

    @property
    def virtual_component_compound_critical_speed_analysis(
        self: "CastSelf",
    ) -> "VirtualComponentCompoundCriticalSpeedAnalysis":
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
class VirtualComponentCompoundCriticalSpeedAnalysis(
    _7124.MountableComponentCompoundCriticalSpeedAnalysis
):
    """VirtualComponentCompoundCriticalSpeedAnalysis

    This is a mastapy class.
    """

    TYPE: ClassVar["Type"] = _VIRTUAL_COMPONENT_COMPOUND_CRITICAL_SPEED_ANALYSIS

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
    ) -> "List[_7038.VirtualComponentCriticalSpeedAnalysis]":
        """List[mastapy.system_model.analyses_and_results.critical_speed_analyses.VirtualComponentCriticalSpeedAnalysis]

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
    ) -> "List[_7038.VirtualComponentCriticalSpeedAnalysis]":
        """List[mastapy.system_model.analyses_and_results.critical_speed_analyses.VirtualComponentCriticalSpeedAnalysis]

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
    def cast_to(self: "Self") -> "_Cast_VirtualComponentCompoundCriticalSpeedAnalysis":
        """Cast to another type.

        Returns:
            _Cast_VirtualComponentCompoundCriticalSpeedAnalysis
        """
        return _Cast_VirtualComponentCompoundCriticalSpeedAnalysis(self)
