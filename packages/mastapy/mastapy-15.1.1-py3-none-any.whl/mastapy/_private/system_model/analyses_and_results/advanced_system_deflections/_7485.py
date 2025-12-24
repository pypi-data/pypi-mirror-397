"""CouplingAdvancedSystemDeflection"""

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
from mastapy._private.system_model.analyses_and_results.advanced_system_deflections import (
    _7550,
)

_COUPLING_ADVANCED_SYSTEM_DEFLECTION = python_net_import(
    "SMT.MastaAPI.SystemModel.AnalysesAndResults.AdvancedSystemDeflections",
    "CouplingAdvancedSystemDeflection",
)

if TYPE_CHECKING:
    from typing import Any, Type, TypeVar

    from mastapy._private.system_model.analyses_and_results import _2943, _2945, _2949
    from mastapy._private.system_model.analyses_and_results.advanced_system_deflections import (
        _7444,
        _7468,
        _7473,
        _7531,
        _7532,
        _7554,
        _7569,
    )
    from mastapy._private.system_model.analyses_and_results.analysis_cases import (
        _7941,
        _7944,
    )
    from mastapy._private.system_model.part_model.couplings import _2867

    Self = TypeVar("Self", bound="CouplingAdvancedSystemDeflection")
    CastSelf = TypeVar(
        "CastSelf",
        bound="CouplingAdvancedSystemDeflection._Cast_CouplingAdvancedSystemDeflection",
    )


__docformat__ = "restructuredtext en"
__all__ = ("CouplingAdvancedSystemDeflection",)


@extended_dataclass(frozen=True, slots=True, weakref_slot=True)
class _Cast_CouplingAdvancedSystemDeflection:
    """Special nested class for casting CouplingAdvancedSystemDeflection to subclasses."""

    __parent__: "CouplingAdvancedSystemDeflection"

    @property
    def specialised_assembly_advanced_system_deflection(
        self: "CastSelf",
    ) -> "_7550.SpecialisedAssemblyAdvancedSystemDeflection":
        return self.__parent__._cast(_7550.SpecialisedAssemblyAdvancedSystemDeflection)

    @property
    def abstract_assembly_advanced_system_deflection(
        self: "CastSelf",
    ) -> "_7444.AbstractAssemblyAdvancedSystemDeflection":
        from mastapy._private.system_model.analyses_and_results.advanced_system_deflections import (
            _7444,
        )

        return self.__parent__._cast(_7444.AbstractAssemblyAdvancedSystemDeflection)

    @property
    def part_advanced_system_deflection(
        self: "CastSelf",
    ) -> "_7531.PartAdvancedSystemDeflection":
        from mastapy._private.system_model.analyses_and_results.advanced_system_deflections import (
            _7531,
        )

        return self.__parent__._cast(_7531.PartAdvancedSystemDeflection)

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
    def clutch_advanced_system_deflection(
        self: "CastSelf",
    ) -> "_7468.ClutchAdvancedSystemDeflection":
        from mastapy._private.system_model.analyses_and_results.advanced_system_deflections import (
            _7468,
        )

        return self.__parent__._cast(_7468.ClutchAdvancedSystemDeflection)

    @property
    def concept_coupling_advanced_system_deflection(
        self: "CastSelf",
    ) -> "_7473.ConceptCouplingAdvancedSystemDeflection":
        from mastapy._private.system_model.analyses_and_results.advanced_system_deflections import (
            _7473,
        )

        return self.__parent__._cast(_7473.ConceptCouplingAdvancedSystemDeflection)

    @property
    def part_to_part_shear_coupling_advanced_system_deflection(
        self: "CastSelf",
    ) -> "_7532.PartToPartShearCouplingAdvancedSystemDeflection":
        from mastapy._private.system_model.analyses_and_results.advanced_system_deflections import (
            _7532,
        )

        return self.__parent__._cast(
            _7532.PartToPartShearCouplingAdvancedSystemDeflection
        )

    @property
    def spring_damper_advanced_system_deflection(
        self: "CastSelf",
    ) -> "_7554.SpringDamperAdvancedSystemDeflection":
        from mastapy._private.system_model.analyses_and_results.advanced_system_deflections import (
            _7554,
        )

        return self.__parent__._cast(_7554.SpringDamperAdvancedSystemDeflection)

    @property
    def torque_converter_advanced_system_deflection(
        self: "CastSelf",
    ) -> "_7569.TorqueConverterAdvancedSystemDeflection":
        from mastapy._private.system_model.analyses_and_results.advanced_system_deflections import (
            _7569,
        )

        return self.__parent__._cast(_7569.TorqueConverterAdvancedSystemDeflection)

    @property
    def coupling_advanced_system_deflection(
        self: "CastSelf",
    ) -> "CouplingAdvancedSystemDeflection":
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
class CouplingAdvancedSystemDeflection(
    _7550.SpecialisedAssemblyAdvancedSystemDeflection
):
    """CouplingAdvancedSystemDeflection

    This is a mastapy class.
    """

    TYPE: ClassVar["Type"] = _COUPLING_ADVANCED_SYSTEM_DEFLECTION

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
    def cast_to(self: "Self") -> "_Cast_CouplingAdvancedSystemDeflection":
        """Cast to another type.

        Returns:
            _Cast_CouplingAdvancedSystemDeflection
        """
        return _Cast_CouplingAdvancedSystemDeflection(self)
