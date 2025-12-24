"""CouplingHarmonicAnalysis"""

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
from mastapy._private.system_model.analyses_and_results.harmonic_analyses import _6158

_COUPLING_HARMONIC_ANALYSIS = python_net_import(
    "SMT.MastaAPI.SystemModel.AnalysesAndResults.HarmonicAnalyses",
    "CouplingHarmonicAnalysis",
)

if TYPE_CHECKING:
    from typing import Any, Type, TypeVar

    from mastapy._private.system_model.analyses_and_results import _2943, _2945, _2949
    from mastapy._private.system_model.analyses_and_results.analysis_cases import (
        _7941,
        _7944,
    )
    from mastapy._private.system_model.analyses_and_results.harmonic_analyses import (
        _6020,
        _6044,
        _6050,
        _6136,
        _6139,
        _6165,
        _6180,
    )
    from mastapy._private.system_model.analyses_and_results.system_deflections import (
        _3023,
    )
    from mastapy._private.system_model.part_model.couplings import _2867

    Self = TypeVar("Self", bound="CouplingHarmonicAnalysis")
    CastSelf = TypeVar(
        "CastSelf", bound="CouplingHarmonicAnalysis._Cast_CouplingHarmonicAnalysis"
    )


__docformat__ = "restructuredtext en"
__all__ = ("CouplingHarmonicAnalysis",)


@extended_dataclass(frozen=True, slots=True, weakref_slot=True)
class _Cast_CouplingHarmonicAnalysis:
    """Special nested class for casting CouplingHarmonicAnalysis to subclasses."""

    __parent__: "CouplingHarmonicAnalysis"

    @property
    def specialised_assembly_harmonic_analysis(
        self: "CastSelf",
    ) -> "_6158.SpecialisedAssemblyHarmonicAnalysis":
        return self.__parent__._cast(_6158.SpecialisedAssemblyHarmonicAnalysis)

    @property
    def abstract_assembly_harmonic_analysis(
        self: "CastSelf",
    ) -> "_6020.AbstractAssemblyHarmonicAnalysis":
        from mastapy._private.system_model.analyses_and_results.harmonic_analyses import (
            _6020,
        )

        return self.__parent__._cast(_6020.AbstractAssemblyHarmonicAnalysis)

    @property
    def part_harmonic_analysis(self: "CastSelf") -> "_6136.PartHarmonicAnalysis":
        from mastapy._private.system_model.analyses_and_results.harmonic_analyses import (
            _6136,
        )

        return self.__parent__._cast(_6136.PartHarmonicAnalysis)

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
    def clutch_harmonic_analysis(self: "CastSelf") -> "_6044.ClutchHarmonicAnalysis":
        from mastapy._private.system_model.analyses_and_results.harmonic_analyses import (
            _6044,
        )

        return self.__parent__._cast(_6044.ClutchHarmonicAnalysis)

    @property
    def concept_coupling_harmonic_analysis(
        self: "CastSelf",
    ) -> "_6050.ConceptCouplingHarmonicAnalysis":
        from mastapy._private.system_model.analyses_and_results.harmonic_analyses import (
            _6050,
        )

        return self.__parent__._cast(_6050.ConceptCouplingHarmonicAnalysis)

    @property
    def part_to_part_shear_coupling_harmonic_analysis(
        self: "CastSelf",
    ) -> "_6139.PartToPartShearCouplingHarmonicAnalysis":
        from mastapy._private.system_model.analyses_and_results.harmonic_analyses import (
            _6139,
        )

        return self.__parent__._cast(_6139.PartToPartShearCouplingHarmonicAnalysis)

    @property
    def spring_damper_harmonic_analysis(
        self: "CastSelf",
    ) -> "_6165.SpringDamperHarmonicAnalysis":
        from mastapy._private.system_model.analyses_and_results.harmonic_analyses import (
            _6165,
        )

        return self.__parent__._cast(_6165.SpringDamperHarmonicAnalysis)

    @property
    def torque_converter_harmonic_analysis(
        self: "CastSelf",
    ) -> "_6180.TorqueConverterHarmonicAnalysis":
        from mastapy._private.system_model.analyses_and_results.harmonic_analyses import (
            _6180,
        )

        return self.__parent__._cast(_6180.TorqueConverterHarmonicAnalysis)

    @property
    def coupling_harmonic_analysis(self: "CastSelf") -> "CouplingHarmonicAnalysis":
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
class CouplingHarmonicAnalysis(_6158.SpecialisedAssemblyHarmonicAnalysis):
    """CouplingHarmonicAnalysis

    This is a mastapy class.
    """

    TYPE: ClassVar["Type"] = _COUPLING_HARMONIC_ANALYSIS

    wrapped: "Any"

    def __post_init__(self: "Self") -> None:
        """Override of the post initialisation magic method."""
        if not hasattr(self.wrapped, "reference_count"):
            self.wrapped.reference_count = 0

        self.wrapped.reference_count += 1

    @property
    @exception_bridge
    def assembly_design(self: "Self") -> "_2867.Coupling":
        """mastapy.system_model.part_model.couplings.Coupling

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
    def system_deflection_results(self: "Self") -> "_3023.CouplingSystemDeflection":
        """mastapy.system_model.analyses_and_results.system_deflections.CouplingSystemDeflection

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "SystemDeflectionResults")

        if temp is None:
            return None

        type_ = temp.GetType()
        return constructor.new(type_.Namespace, type_.Name)(temp)

    @property
    def cast_to(self: "Self") -> "_Cast_CouplingHarmonicAnalysis":
        """Cast to another type.

        Returns:
            _Cast_CouplingHarmonicAnalysis
        """
        return _Cast_CouplingHarmonicAnalysis(self)
