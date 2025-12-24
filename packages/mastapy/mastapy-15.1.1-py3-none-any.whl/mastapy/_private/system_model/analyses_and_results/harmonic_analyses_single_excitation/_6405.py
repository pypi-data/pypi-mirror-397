"""CouplingConnectionHarmonicAnalysisOfSingleExcitation"""

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
from mastapy._private.system_model.analyses_and_results.harmonic_analyses_single_excitation import (
    _6434,
)

_COUPLING_CONNECTION_HARMONIC_ANALYSIS_OF_SINGLE_EXCITATION = python_net_import(
    "SMT.MastaAPI.SystemModel.AnalysesAndResults.HarmonicAnalysesSingleExcitation",
    "CouplingConnectionHarmonicAnalysisOfSingleExcitation",
)

if TYPE_CHECKING:
    from typing import Any, Type, TypeVar

    from mastapy._private.system_model.analyses_and_results import _2941, _2943, _2945
    from mastapy._private.system_model.analyses_and_results.analysis_cases import (
        _7934,
        _7937,
    )
    from mastapy._private.system_model.analyses_and_results.harmonic_analyses_single_excitation import (
        _6389,
        _6394,
        _6403,
        _6452,
        _6474,
        _6489,
    )
    from mastapy._private.system_model.connections_and_sockets.couplings import _2605

    Self = TypeVar("Self", bound="CouplingConnectionHarmonicAnalysisOfSingleExcitation")
    CastSelf = TypeVar(
        "CastSelf",
        bound="CouplingConnectionHarmonicAnalysisOfSingleExcitation._Cast_CouplingConnectionHarmonicAnalysisOfSingleExcitation",
    )


__docformat__ = "restructuredtext en"
__all__ = ("CouplingConnectionHarmonicAnalysisOfSingleExcitation",)


@extended_dataclass(frozen=True, slots=True, weakref_slot=True)
class _Cast_CouplingConnectionHarmonicAnalysisOfSingleExcitation:
    """Special nested class for casting CouplingConnectionHarmonicAnalysisOfSingleExcitation to subclasses."""

    __parent__: "CouplingConnectionHarmonicAnalysisOfSingleExcitation"

    @property
    def inter_mountable_component_connection_harmonic_analysis_of_single_excitation(
        self: "CastSelf",
    ) -> "_6434.InterMountableComponentConnectionHarmonicAnalysisOfSingleExcitation":
        return self.__parent__._cast(
            _6434.InterMountableComponentConnectionHarmonicAnalysisOfSingleExcitation
        )

    @property
    def connection_harmonic_analysis_of_single_excitation(
        self: "CastSelf",
    ) -> "_6403.ConnectionHarmonicAnalysisOfSingleExcitation":
        from mastapy._private.system_model.analyses_and_results.harmonic_analyses_single_excitation import (
            _6403,
        )

        return self.__parent__._cast(_6403.ConnectionHarmonicAnalysisOfSingleExcitation)

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
    def clutch_connection_harmonic_analysis_of_single_excitation(
        self: "CastSelf",
    ) -> "_6389.ClutchConnectionHarmonicAnalysisOfSingleExcitation":
        from mastapy._private.system_model.analyses_and_results.harmonic_analyses_single_excitation import (
            _6389,
        )

        return self.__parent__._cast(
            _6389.ClutchConnectionHarmonicAnalysisOfSingleExcitation
        )

    @property
    def concept_coupling_connection_harmonic_analysis_of_single_excitation(
        self: "CastSelf",
    ) -> "_6394.ConceptCouplingConnectionHarmonicAnalysisOfSingleExcitation":
        from mastapy._private.system_model.analyses_and_results.harmonic_analyses_single_excitation import (
            _6394,
        )

        return self.__parent__._cast(
            _6394.ConceptCouplingConnectionHarmonicAnalysisOfSingleExcitation
        )

    @property
    def part_to_part_shear_coupling_connection_harmonic_analysis_of_single_excitation(
        self: "CastSelf",
    ) -> "_6452.PartToPartShearCouplingConnectionHarmonicAnalysisOfSingleExcitation":
        from mastapy._private.system_model.analyses_and_results.harmonic_analyses_single_excitation import (
            _6452,
        )

        return self.__parent__._cast(
            _6452.PartToPartShearCouplingConnectionHarmonicAnalysisOfSingleExcitation
        )

    @property
    def spring_damper_connection_harmonic_analysis_of_single_excitation(
        self: "CastSelf",
    ) -> "_6474.SpringDamperConnectionHarmonicAnalysisOfSingleExcitation":
        from mastapy._private.system_model.analyses_and_results.harmonic_analyses_single_excitation import (
            _6474,
        )

        return self.__parent__._cast(
            _6474.SpringDamperConnectionHarmonicAnalysisOfSingleExcitation
        )

    @property
    def torque_converter_connection_harmonic_analysis_of_single_excitation(
        self: "CastSelf",
    ) -> "_6489.TorqueConverterConnectionHarmonicAnalysisOfSingleExcitation":
        from mastapy._private.system_model.analyses_and_results.harmonic_analyses_single_excitation import (
            _6489,
        )

        return self.__parent__._cast(
            _6489.TorqueConverterConnectionHarmonicAnalysisOfSingleExcitation
        )

    @property
    def coupling_connection_harmonic_analysis_of_single_excitation(
        self: "CastSelf",
    ) -> "CouplingConnectionHarmonicAnalysisOfSingleExcitation":
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
class CouplingConnectionHarmonicAnalysisOfSingleExcitation(
    _6434.InterMountableComponentConnectionHarmonicAnalysisOfSingleExcitation
):
    """CouplingConnectionHarmonicAnalysisOfSingleExcitation

    This is a mastapy class.
    """

    TYPE: ClassVar["Type"] = _COUPLING_CONNECTION_HARMONIC_ANALYSIS_OF_SINGLE_EXCITATION

    wrapped: "Any"

    def __post_init__(self: "Self") -> None:
        """Override of the post initialisation magic method."""
        if not hasattr(self.wrapped, "reference_count"):
            self.wrapped.reference_count = 0

        self.wrapped.reference_count += 1

    @property
    @exception_bridge
    def connection_design(self: "Self") -> "_2605.CouplingConnection":
        """mastapy.system_model.connections_and_sockets.couplings.CouplingConnection

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
    ) -> "_Cast_CouplingConnectionHarmonicAnalysisOfSingleExcitation":
        """Cast to another type.

        Returns:
            _Cast_CouplingConnectionHarmonicAnalysisOfSingleExcitation
        """
        return _Cast_CouplingConnectionHarmonicAnalysisOfSingleExcitation(self)
