"""FEPartModalAnalysis"""

from __future__ import annotations

from typing import TYPE_CHECKING, ClassVar

from mastapy._private._internal.dataclasses import extended_dataclass
from mastapy._private._internal.exception_bridge import exception_bridge
from mastapy._private._internal.exceptions import CastException
from mastapy._private._internal.python_net import (
    python_net_import,
    pythonnet_method_call,
    pythonnet_property_get,
)

from mastapy._private._internal import constructor, conversion, utility
from mastapy._private.system_model.analyses_and_results.modal_analyses import _4896

_FE_PART_MODAL_ANALYSIS = python_net_import(
    "SMT.MastaAPI.SystemModel.AnalysesAndResults.ModalAnalyses", "FEPartModalAnalysis"
)

if TYPE_CHECKING:
    from typing import Any, List, Type, TypeVar

    from mastapy._private.nodal_analysis.component_mode_synthesis import _331
    from mastapy._private.system_model.analyses_and_results import _2943, _2945, _2949
    from mastapy._private.system_model.analyses_and_results.analysis_cases import (
        _7941,
        _7944,
    )
    from mastapy._private.system_model.analyses_and_results.modal_analyses import (
        _4919,
        _4987,
    )
    from mastapy._private.system_model.analyses_and_results.static_loads import _7808
    from mastapy._private.system_model.analyses_and_results.system_deflections import (
        _3049,
    )
    from mastapy._private.system_model.part_model import _2724

    Self = TypeVar("Self", bound="FEPartModalAnalysis")
    CastSelf = TypeVar(
        "CastSelf", bound="FEPartModalAnalysis._Cast_FEPartModalAnalysis"
    )


__docformat__ = "restructuredtext en"
__all__ = ("FEPartModalAnalysis",)


@extended_dataclass(frozen=True, slots=True, weakref_slot=True)
class _Cast_FEPartModalAnalysis:
    """Special nested class for casting FEPartModalAnalysis to subclasses."""

    __parent__: "FEPartModalAnalysis"

    @property
    def abstract_shaft_or_housing_modal_analysis(
        self: "CastSelf",
    ) -> "_4896.AbstractShaftOrHousingModalAnalysis":
        return self.__parent__._cast(_4896.AbstractShaftOrHousingModalAnalysis)

    @property
    def component_modal_analysis(self: "CastSelf") -> "_4919.ComponentModalAnalysis":
        from mastapy._private.system_model.analyses_and_results.modal_analyses import (
            _4919,
        )

        return self.__parent__._cast(_4919.ComponentModalAnalysis)

    @property
    def part_modal_analysis(self: "CastSelf") -> "_4987.PartModalAnalysis":
        from mastapy._private.system_model.analyses_and_results.modal_analyses import (
            _4987,
        )

        return self.__parent__._cast(_4987.PartModalAnalysis)

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
    def fe_part_modal_analysis(self: "CastSelf") -> "FEPartModalAnalysis":
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
class FEPartModalAnalysis(_4896.AbstractShaftOrHousingModalAnalysis):
    """FEPartModalAnalysis

    This is a mastapy class.
    """

    TYPE: ClassVar["Type"] = _FE_PART_MODAL_ANALYSIS

    wrapped: "Any"

    def __post_init__(self: "Self") -> None:
        """Override of the post initialisation magic method."""
        if not hasattr(self.wrapped, "reference_count"):
            self.wrapped.reference_count = 0

        self.wrapped.reference_count += 1

    @property
    @exception_bridge
    def no_results_available(self: "Self") -> "str":
        """str

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "NoResultsAvailable")

        if temp is None:
            return ""

        return temp

    @property
    @exception_bridge
    def component_design(self: "Self") -> "_2724.FEPart":
        """mastapy.system_model.part_model.FEPart

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
    def component_load_case(self: "Self") -> "_7808.FEPartLoadCase":
        """mastapy.system_model.analyses_and_results.static_loads.FEPartLoadCase

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
    def system_deflection_results(self: "Self") -> "_3049.FEPartSystemDeflection":
        """mastapy.system_model.analyses_and_results.system_deflections.FEPartSystemDeflection

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "SystemDeflectionResults")

        if temp is None:
            return None

        type_ = temp.GetType()
        return constructor.new(type_.Namespace, type_.Name)(temp)

    @property
    @exception_bridge
    def modal_full_fe_results(self: "Self") -> "List[_331.ModalCMSResults]":
        """List[mastapy.nodal_analysis.component_mode_synthesis.ModalCMSResults]

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "ModalFullFEResults")

        if temp is None:
            return None

        value = conversion.pn_to_mp_objects_in_list(temp)

        if value is None:
            return None

        return value

    @property
    @exception_bridge
    def planetaries(self: "Self") -> "List[FEPartModalAnalysis]":
        """List[mastapy.system_model.analyses_and_results.modal_analyses.FEPartModalAnalysis]

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "Planetaries")

        if temp is None:
            return None

        value = conversion.pn_to_mp_objects_in_list(temp)

        if value is None:
            return None

        return value

    @exception_bridge
    def calculate_all_strain_and_kinetic_energies(self: "Self") -> None:
        """Method does not return."""
        pythonnet_method_call(self.wrapped, "CalculateAllStrainAndKineticEnergies")

    @exception_bridge
    def calculate_mode_shapes(self: "Self") -> None:
        """Method does not return."""
        pythonnet_method_call(self.wrapped, "CalculateModeShapes")

    @exception_bridge
    def calculate_selected_strain_and_kinetic_energy(self: "Self") -> None:
        """Method does not return."""
        pythonnet_method_call(self.wrapped, "CalculateSelectedStrainAndKineticEnergy")

    @property
    def cast_to(self: "Self") -> "_Cast_FEPartModalAnalysis":
        """Cast to another type.

        Returns:
            _Cast_FEPartModalAnalysis
        """
        return _Cast_FEPartModalAnalysis(self)
