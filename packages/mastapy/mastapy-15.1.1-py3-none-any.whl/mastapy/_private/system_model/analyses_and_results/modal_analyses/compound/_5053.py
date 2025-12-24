"""AbstractAssemblyCompoundModalAnalysis"""

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
from mastapy._private.system_model.analyses_and_results.modal_analyses.compound import (
    _5134,
)

_ABSTRACT_ASSEMBLY_COMPOUND_MODAL_ANALYSIS = python_net_import(
    "SMT.MastaAPI.SystemModel.AnalysesAndResults.ModalAnalyses.Compound",
    "AbstractAssemblyCompoundModalAnalysis",
)

if TYPE_CHECKING:
    from typing import Any, List, Type, TypeVar

    from mastapy._private.system_model.analyses_and_results import _2943
    from mastapy._private.system_model.analyses_and_results.analysis_cases import (
        _7939,
        _7942,
    )
    from mastapy._private.system_model.analyses_and_results.modal_analyses import _4894
    from mastapy._private.system_model.analyses_and_results.modal_analyses.compound import (
        _5059,
        _5060,
        _5063,
        _5066,
        _5071,
        _5073,
        _5074,
        _5079,
        _5084,
        _5087,
        _5090,
        _5094,
        _5096,
        _5102,
        _5108,
        _5110,
        _5113,
        _5117,
        _5121,
        _5124,
        _5127,
        _5130,
        _5135,
        _5139,
        _5146,
        _5149,
        _5153,
        _5156,
        _5157,
        _5162,
        _5165,
        _5168,
        _5172,
        _5180,
        _5183,
    )

    Self = TypeVar("Self", bound="AbstractAssemblyCompoundModalAnalysis")
    CastSelf = TypeVar(
        "CastSelf",
        bound="AbstractAssemblyCompoundModalAnalysis._Cast_AbstractAssemblyCompoundModalAnalysis",
    )


__docformat__ = "restructuredtext en"
__all__ = ("AbstractAssemblyCompoundModalAnalysis",)


@extended_dataclass(frozen=True, slots=True, weakref_slot=True)
class _Cast_AbstractAssemblyCompoundModalAnalysis:
    """Special nested class for casting AbstractAssemblyCompoundModalAnalysis to subclasses."""

    __parent__: "AbstractAssemblyCompoundModalAnalysis"

    @property
    def part_compound_modal_analysis(
        self: "CastSelf",
    ) -> "_5134.PartCompoundModalAnalysis":
        return self.__parent__._cast(_5134.PartCompoundModalAnalysis)

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
    def agma_gleason_conical_gear_set_compound_modal_analysis(
        self: "CastSelf",
    ) -> "_5059.AGMAGleasonConicalGearSetCompoundModalAnalysis":
        from mastapy._private.system_model.analyses_and_results.modal_analyses.compound import (
            _5059,
        )

        return self.__parent__._cast(
            _5059.AGMAGleasonConicalGearSetCompoundModalAnalysis
        )

    @property
    def assembly_compound_modal_analysis(
        self: "CastSelf",
    ) -> "_5060.AssemblyCompoundModalAnalysis":
        from mastapy._private.system_model.analyses_and_results.modal_analyses.compound import (
            _5060,
        )

        return self.__parent__._cast(_5060.AssemblyCompoundModalAnalysis)

    @property
    def belt_drive_compound_modal_analysis(
        self: "CastSelf",
    ) -> "_5063.BeltDriveCompoundModalAnalysis":
        from mastapy._private.system_model.analyses_and_results.modal_analyses.compound import (
            _5063,
        )

        return self.__parent__._cast(_5063.BeltDriveCompoundModalAnalysis)

    @property
    def bevel_differential_gear_set_compound_modal_analysis(
        self: "CastSelf",
    ) -> "_5066.BevelDifferentialGearSetCompoundModalAnalysis":
        from mastapy._private.system_model.analyses_and_results.modal_analyses.compound import (
            _5066,
        )

        return self.__parent__._cast(
            _5066.BevelDifferentialGearSetCompoundModalAnalysis
        )

    @property
    def bevel_gear_set_compound_modal_analysis(
        self: "CastSelf",
    ) -> "_5071.BevelGearSetCompoundModalAnalysis":
        from mastapy._private.system_model.analyses_and_results.modal_analyses.compound import (
            _5071,
        )

        return self.__parent__._cast(_5071.BevelGearSetCompoundModalAnalysis)

    @property
    def bolted_joint_compound_modal_analysis(
        self: "CastSelf",
    ) -> "_5073.BoltedJointCompoundModalAnalysis":
        from mastapy._private.system_model.analyses_and_results.modal_analyses.compound import (
            _5073,
        )

        return self.__parent__._cast(_5073.BoltedJointCompoundModalAnalysis)

    @property
    def clutch_compound_modal_analysis(
        self: "CastSelf",
    ) -> "_5074.ClutchCompoundModalAnalysis":
        from mastapy._private.system_model.analyses_and_results.modal_analyses.compound import (
            _5074,
        )

        return self.__parent__._cast(_5074.ClutchCompoundModalAnalysis)

    @property
    def concept_coupling_compound_modal_analysis(
        self: "CastSelf",
    ) -> "_5079.ConceptCouplingCompoundModalAnalysis":
        from mastapy._private.system_model.analyses_and_results.modal_analyses.compound import (
            _5079,
        )

        return self.__parent__._cast(_5079.ConceptCouplingCompoundModalAnalysis)

    @property
    def concept_gear_set_compound_modal_analysis(
        self: "CastSelf",
    ) -> "_5084.ConceptGearSetCompoundModalAnalysis":
        from mastapy._private.system_model.analyses_and_results.modal_analyses.compound import (
            _5084,
        )

        return self.__parent__._cast(_5084.ConceptGearSetCompoundModalAnalysis)

    @property
    def conical_gear_set_compound_modal_analysis(
        self: "CastSelf",
    ) -> "_5087.ConicalGearSetCompoundModalAnalysis":
        from mastapy._private.system_model.analyses_and_results.modal_analyses.compound import (
            _5087,
        )

        return self.__parent__._cast(_5087.ConicalGearSetCompoundModalAnalysis)

    @property
    def coupling_compound_modal_analysis(
        self: "CastSelf",
    ) -> "_5090.CouplingCompoundModalAnalysis":
        from mastapy._private.system_model.analyses_and_results.modal_analyses.compound import (
            _5090,
        )

        return self.__parent__._cast(_5090.CouplingCompoundModalAnalysis)

    @property
    def cvt_compound_modal_analysis(
        self: "CastSelf",
    ) -> "_5094.CVTCompoundModalAnalysis":
        from mastapy._private.system_model.analyses_and_results.modal_analyses.compound import (
            _5094,
        )

        return self.__parent__._cast(_5094.CVTCompoundModalAnalysis)

    @property
    def cycloidal_assembly_compound_modal_analysis(
        self: "CastSelf",
    ) -> "_5096.CycloidalAssemblyCompoundModalAnalysis":
        from mastapy._private.system_model.analyses_and_results.modal_analyses.compound import (
            _5096,
        )

        return self.__parent__._cast(_5096.CycloidalAssemblyCompoundModalAnalysis)

    @property
    def cylindrical_gear_set_compound_modal_analysis(
        self: "CastSelf",
    ) -> "_5102.CylindricalGearSetCompoundModalAnalysis":
        from mastapy._private.system_model.analyses_and_results.modal_analyses.compound import (
            _5102,
        )

        return self.__parent__._cast(_5102.CylindricalGearSetCompoundModalAnalysis)

    @property
    def face_gear_set_compound_modal_analysis(
        self: "CastSelf",
    ) -> "_5108.FaceGearSetCompoundModalAnalysis":
        from mastapy._private.system_model.analyses_and_results.modal_analyses.compound import (
            _5108,
        )

        return self.__parent__._cast(_5108.FaceGearSetCompoundModalAnalysis)

    @property
    def flexible_pin_assembly_compound_modal_analysis(
        self: "CastSelf",
    ) -> "_5110.FlexiblePinAssemblyCompoundModalAnalysis":
        from mastapy._private.system_model.analyses_and_results.modal_analyses.compound import (
            _5110,
        )

        return self.__parent__._cast(_5110.FlexiblePinAssemblyCompoundModalAnalysis)

    @property
    def gear_set_compound_modal_analysis(
        self: "CastSelf",
    ) -> "_5113.GearSetCompoundModalAnalysis":
        from mastapy._private.system_model.analyses_and_results.modal_analyses.compound import (
            _5113,
        )

        return self.__parent__._cast(_5113.GearSetCompoundModalAnalysis)

    @property
    def hypoid_gear_set_compound_modal_analysis(
        self: "CastSelf",
    ) -> "_5117.HypoidGearSetCompoundModalAnalysis":
        from mastapy._private.system_model.analyses_and_results.modal_analyses.compound import (
            _5117,
        )

        return self.__parent__._cast(_5117.HypoidGearSetCompoundModalAnalysis)

    @property
    def klingelnberg_cyclo_palloid_conical_gear_set_compound_modal_analysis(
        self: "CastSelf",
    ) -> "_5121.KlingelnbergCycloPalloidConicalGearSetCompoundModalAnalysis":
        from mastapy._private.system_model.analyses_and_results.modal_analyses.compound import (
            _5121,
        )

        return self.__parent__._cast(
            _5121.KlingelnbergCycloPalloidConicalGearSetCompoundModalAnalysis
        )

    @property
    def klingelnberg_cyclo_palloid_hypoid_gear_set_compound_modal_analysis(
        self: "CastSelf",
    ) -> "_5124.KlingelnbergCycloPalloidHypoidGearSetCompoundModalAnalysis":
        from mastapy._private.system_model.analyses_and_results.modal_analyses.compound import (
            _5124,
        )

        return self.__parent__._cast(
            _5124.KlingelnbergCycloPalloidHypoidGearSetCompoundModalAnalysis
        )

    @property
    def klingelnberg_cyclo_palloid_spiral_bevel_gear_set_compound_modal_analysis(
        self: "CastSelf",
    ) -> "_5127.KlingelnbergCycloPalloidSpiralBevelGearSetCompoundModalAnalysis":
        from mastapy._private.system_model.analyses_and_results.modal_analyses.compound import (
            _5127,
        )

        return self.__parent__._cast(
            _5127.KlingelnbergCycloPalloidSpiralBevelGearSetCompoundModalAnalysis
        )

    @property
    def microphone_array_compound_modal_analysis(
        self: "CastSelf",
    ) -> "_5130.MicrophoneArrayCompoundModalAnalysis":
        from mastapy._private.system_model.analyses_and_results.modal_analyses.compound import (
            _5130,
        )

        return self.__parent__._cast(_5130.MicrophoneArrayCompoundModalAnalysis)

    @property
    def part_to_part_shear_coupling_compound_modal_analysis(
        self: "CastSelf",
    ) -> "_5135.PartToPartShearCouplingCompoundModalAnalysis":
        from mastapy._private.system_model.analyses_and_results.modal_analyses.compound import (
            _5135,
        )

        return self.__parent__._cast(_5135.PartToPartShearCouplingCompoundModalAnalysis)

    @property
    def planetary_gear_set_compound_modal_analysis(
        self: "CastSelf",
    ) -> "_5139.PlanetaryGearSetCompoundModalAnalysis":
        from mastapy._private.system_model.analyses_and_results.modal_analyses.compound import (
            _5139,
        )

        return self.__parent__._cast(_5139.PlanetaryGearSetCompoundModalAnalysis)

    @property
    def rolling_ring_assembly_compound_modal_analysis(
        self: "CastSelf",
    ) -> "_5146.RollingRingAssemblyCompoundModalAnalysis":
        from mastapy._private.system_model.analyses_and_results.modal_analyses.compound import (
            _5146,
        )

        return self.__parent__._cast(_5146.RollingRingAssemblyCompoundModalAnalysis)

    @property
    def root_assembly_compound_modal_analysis(
        self: "CastSelf",
    ) -> "_5149.RootAssemblyCompoundModalAnalysis":
        from mastapy._private.system_model.analyses_and_results.modal_analyses.compound import (
            _5149,
        )

        return self.__parent__._cast(_5149.RootAssemblyCompoundModalAnalysis)

    @property
    def specialised_assembly_compound_modal_analysis(
        self: "CastSelf",
    ) -> "_5153.SpecialisedAssemblyCompoundModalAnalysis":
        from mastapy._private.system_model.analyses_and_results.modal_analyses.compound import (
            _5153,
        )

        return self.__parent__._cast(_5153.SpecialisedAssemblyCompoundModalAnalysis)

    @property
    def spiral_bevel_gear_set_compound_modal_analysis(
        self: "CastSelf",
    ) -> "_5156.SpiralBevelGearSetCompoundModalAnalysis":
        from mastapy._private.system_model.analyses_and_results.modal_analyses.compound import (
            _5156,
        )

        return self.__parent__._cast(_5156.SpiralBevelGearSetCompoundModalAnalysis)

    @property
    def spring_damper_compound_modal_analysis(
        self: "CastSelf",
    ) -> "_5157.SpringDamperCompoundModalAnalysis":
        from mastapy._private.system_model.analyses_and_results.modal_analyses.compound import (
            _5157,
        )

        return self.__parent__._cast(_5157.SpringDamperCompoundModalAnalysis)

    @property
    def straight_bevel_diff_gear_set_compound_modal_analysis(
        self: "CastSelf",
    ) -> "_5162.StraightBevelDiffGearSetCompoundModalAnalysis":
        from mastapy._private.system_model.analyses_and_results.modal_analyses.compound import (
            _5162,
        )

        return self.__parent__._cast(
            _5162.StraightBevelDiffGearSetCompoundModalAnalysis
        )

    @property
    def straight_bevel_gear_set_compound_modal_analysis(
        self: "CastSelf",
    ) -> "_5165.StraightBevelGearSetCompoundModalAnalysis":
        from mastapy._private.system_model.analyses_and_results.modal_analyses.compound import (
            _5165,
        )

        return self.__parent__._cast(_5165.StraightBevelGearSetCompoundModalAnalysis)

    @property
    def synchroniser_compound_modal_analysis(
        self: "CastSelf",
    ) -> "_5168.SynchroniserCompoundModalAnalysis":
        from mastapy._private.system_model.analyses_and_results.modal_analyses.compound import (
            _5168,
        )

        return self.__parent__._cast(_5168.SynchroniserCompoundModalAnalysis)

    @property
    def torque_converter_compound_modal_analysis(
        self: "CastSelf",
    ) -> "_5172.TorqueConverterCompoundModalAnalysis":
        from mastapy._private.system_model.analyses_and_results.modal_analyses.compound import (
            _5172,
        )

        return self.__parent__._cast(_5172.TorqueConverterCompoundModalAnalysis)

    @property
    def worm_gear_set_compound_modal_analysis(
        self: "CastSelf",
    ) -> "_5180.WormGearSetCompoundModalAnalysis":
        from mastapy._private.system_model.analyses_and_results.modal_analyses.compound import (
            _5180,
        )

        return self.__parent__._cast(_5180.WormGearSetCompoundModalAnalysis)

    @property
    def zerol_bevel_gear_set_compound_modal_analysis(
        self: "CastSelf",
    ) -> "_5183.ZerolBevelGearSetCompoundModalAnalysis":
        from mastapy._private.system_model.analyses_and_results.modal_analyses.compound import (
            _5183,
        )

        return self.__parent__._cast(_5183.ZerolBevelGearSetCompoundModalAnalysis)

    @property
    def abstract_assembly_compound_modal_analysis(
        self: "CastSelf",
    ) -> "AbstractAssemblyCompoundModalAnalysis":
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
class AbstractAssemblyCompoundModalAnalysis(_5134.PartCompoundModalAnalysis):
    """AbstractAssemblyCompoundModalAnalysis

    This is a mastapy class.
    """

    TYPE: ClassVar["Type"] = _ABSTRACT_ASSEMBLY_COMPOUND_MODAL_ANALYSIS

    wrapped: "Any"

    def __post_init__(self: "Self") -> None:
        """Override of the post initialisation magic method."""
        if not hasattr(self.wrapped, "reference_count"):
            self.wrapped.reference_count = 0

        self.wrapped.reference_count += 1

    @property
    @exception_bridge
    def assembly_analysis_cases(
        self: "Self",
    ) -> "List[_4894.AbstractAssemblyModalAnalysis]":
        """List[mastapy.system_model.analyses_and_results.modal_analyses.AbstractAssemblyModalAnalysis]

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "AssemblyAnalysisCases")

        if temp is None:
            return None

        value = conversion.pn_to_mp_objects_in_list(temp)

        if value is None:
            return None

        return value

    @property
    @exception_bridge
    def assembly_analysis_cases_ready(
        self: "Self",
    ) -> "List[_4894.AbstractAssemblyModalAnalysis]":
        """List[mastapy.system_model.analyses_and_results.modal_analyses.AbstractAssemblyModalAnalysis]

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "AssemblyAnalysisCasesReady")

        if temp is None:
            return None

        value = conversion.pn_to_mp_objects_in_list(temp)

        if value is None:
            return None

        return value

    @property
    def cast_to(self: "Self") -> "_Cast_AbstractAssemblyCompoundModalAnalysis":
        """Cast to another type.

        Returns:
            _Cast_AbstractAssemblyCompoundModalAnalysis
        """
        return _Cast_AbstractAssemblyCompoundModalAnalysis(self)
