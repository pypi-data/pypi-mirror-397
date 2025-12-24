"""CouplingConnectionCompoundHarmonicAnalysis"""

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
from mastapy._private.system_model.analyses_and_results.harmonic_analyses.compound import (
    _6302,
)

_COUPLING_CONNECTION_COMPOUND_HARMONIC_ANALYSIS = python_net_import(
    "SMT.MastaAPI.SystemModel.AnalysesAndResults.HarmonicAnalyses.Compound",
    "CouplingConnectionCompoundHarmonicAnalysis",
)

if TYPE_CHECKING:
    from typing import Any, List, Type, TypeVar

    from mastapy._private.system_model.analyses_and_results import _2943
    from mastapy._private.system_model.analyses_and_results.analysis_cases import (
        _7935,
        _7939,
    )
    from mastapy._private.system_model.analyses_and_results.harmonic_analyses import (
        _6059,
    )
    from mastapy._private.system_model.analyses_and_results.harmonic_analyses.compound import (
        _6259,
        _6264,
        _6272,
        _6320,
        _6342,
        _6357,
    )

    Self = TypeVar("Self", bound="CouplingConnectionCompoundHarmonicAnalysis")
    CastSelf = TypeVar(
        "CastSelf",
        bound="CouplingConnectionCompoundHarmonicAnalysis._Cast_CouplingConnectionCompoundHarmonicAnalysis",
    )


__docformat__ = "restructuredtext en"
__all__ = ("CouplingConnectionCompoundHarmonicAnalysis",)


@extended_dataclass(frozen=True, slots=True, weakref_slot=True)
class _Cast_CouplingConnectionCompoundHarmonicAnalysis:
    """Special nested class for casting CouplingConnectionCompoundHarmonicAnalysis to subclasses."""

    __parent__: "CouplingConnectionCompoundHarmonicAnalysis"

    @property
    def inter_mountable_component_connection_compound_harmonic_analysis(
        self: "CastSelf",
    ) -> "_6302.InterMountableComponentConnectionCompoundHarmonicAnalysis":
        return self.__parent__._cast(
            _6302.InterMountableComponentConnectionCompoundHarmonicAnalysis
        )

    @property
    def connection_compound_harmonic_analysis(
        self: "CastSelf",
    ) -> "_6272.ConnectionCompoundHarmonicAnalysis":
        from mastapy._private.system_model.analyses_and_results.harmonic_analyses.compound import (
            _6272,
        )

        return self.__parent__._cast(_6272.ConnectionCompoundHarmonicAnalysis)

    @property
    def connection_compound_analysis(
        self: "CastSelf",
    ) -> "_7935.ConnectionCompoundAnalysis":
        from mastapy._private.system_model.analyses_and_results.analysis_cases import (
            _7935,
        )

        return self.__parent__._cast(_7935.ConnectionCompoundAnalysis)

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
    def clutch_connection_compound_harmonic_analysis(
        self: "CastSelf",
    ) -> "_6259.ClutchConnectionCompoundHarmonicAnalysis":
        from mastapy._private.system_model.analyses_and_results.harmonic_analyses.compound import (
            _6259,
        )

        return self.__parent__._cast(_6259.ClutchConnectionCompoundHarmonicAnalysis)

    @property
    def concept_coupling_connection_compound_harmonic_analysis(
        self: "CastSelf",
    ) -> "_6264.ConceptCouplingConnectionCompoundHarmonicAnalysis":
        from mastapy._private.system_model.analyses_and_results.harmonic_analyses.compound import (
            _6264,
        )

        return self.__parent__._cast(
            _6264.ConceptCouplingConnectionCompoundHarmonicAnalysis
        )

    @property
    def part_to_part_shear_coupling_connection_compound_harmonic_analysis(
        self: "CastSelf",
    ) -> "_6320.PartToPartShearCouplingConnectionCompoundHarmonicAnalysis":
        from mastapy._private.system_model.analyses_and_results.harmonic_analyses.compound import (
            _6320,
        )

        return self.__parent__._cast(
            _6320.PartToPartShearCouplingConnectionCompoundHarmonicAnalysis
        )

    @property
    def spring_damper_connection_compound_harmonic_analysis(
        self: "CastSelf",
    ) -> "_6342.SpringDamperConnectionCompoundHarmonicAnalysis":
        from mastapy._private.system_model.analyses_and_results.harmonic_analyses.compound import (
            _6342,
        )

        return self.__parent__._cast(
            _6342.SpringDamperConnectionCompoundHarmonicAnalysis
        )

    @property
    def torque_converter_connection_compound_harmonic_analysis(
        self: "CastSelf",
    ) -> "_6357.TorqueConverterConnectionCompoundHarmonicAnalysis":
        from mastapy._private.system_model.analyses_and_results.harmonic_analyses.compound import (
            _6357,
        )

        return self.__parent__._cast(
            _6357.TorqueConverterConnectionCompoundHarmonicAnalysis
        )

    @property
    def coupling_connection_compound_harmonic_analysis(
        self: "CastSelf",
    ) -> "CouplingConnectionCompoundHarmonicAnalysis":
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
class CouplingConnectionCompoundHarmonicAnalysis(
    _6302.InterMountableComponentConnectionCompoundHarmonicAnalysis
):
    """CouplingConnectionCompoundHarmonicAnalysis

    This is a mastapy class.
    """

    TYPE: ClassVar["Type"] = _COUPLING_CONNECTION_COMPOUND_HARMONIC_ANALYSIS

    wrapped: "Any"

    def __post_init__(self: "Self") -> None:
        """Override of the post initialisation magic method."""
        if not hasattr(self.wrapped, "reference_count"):
            self.wrapped.reference_count = 0

        self.wrapped.reference_count += 1

    @property
    @exception_bridge
    def connection_analysis_cases(
        self: "Self",
    ) -> "List[_6059.CouplingConnectionHarmonicAnalysis]":
        """List[mastapy.system_model.analyses_and_results.harmonic_analyses.CouplingConnectionHarmonicAnalysis]

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "ConnectionAnalysisCases")

        if temp is None:
            return None

        value = conversion.pn_to_mp_objects_in_list(temp)

        if value is None:
            return None

        return value

    @property
    @exception_bridge
    def connection_analysis_cases_ready(
        self: "Self",
    ) -> "List[_6059.CouplingConnectionHarmonicAnalysis]":
        """List[mastapy.system_model.analyses_and_results.harmonic_analyses.CouplingConnectionHarmonicAnalysis]

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "ConnectionAnalysisCasesReady")

        if temp is None:
            return None

        value = conversion.pn_to_mp_objects_in_list(temp)

        if value is None:
            return None

        return value

    @property
    def cast_to(self: "Self") -> "_Cast_CouplingConnectionCompoundHarmonicAnalysis":
        """Cast to another type.

        Returns:
            _Cast_CouplingConnectionCompoundHarmonicAnalysis
        """
        return _Cast_CouplingConnectionCompoundHarmonicAnalysis(self)
