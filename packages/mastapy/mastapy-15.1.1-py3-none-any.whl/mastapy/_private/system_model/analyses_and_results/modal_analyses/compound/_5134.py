"""PartCompoundModalAnalysis"""

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
from mastapy._private.system_model.analyses_and_results.analysis_cases import _7942

_PART_COMPOUND_MODAL_ANALYSIS = python_net_import(
    "SMT.MastaAPI.SystemModel.AnalysesAndResults.ModalAnalyses.Compound",
    "PartCompoundModalAnalysis",
)

if TYPE_CHECKING:
    from typing import Any, List, Type, TypeVar

    from mastapy._private.system_model.analyses_and_results import _2943
    from mastapy._private.system_model.analyses_and_results.analysis_cases import _7939
    from mastapy._private.system_model.analyses_and_results.modal_analyses import _4987
    from mastapy._private.system_model.analyses_and_results.modal_analyses.compound import (
        _5053,
        _5054,
        _5055,
        _5057,
        _5059,
        _5060,
        _5061,
        _5063,
        _5064,
        _5066,
        _5067,
        _5068,
        _5069,
        _5071,
        _5072,
        _5073,
        _5074,
        _5076,
        _5078,
        _5079,
        _5081,
        _5082,
        _5084,
        _5085,
        _5087,
        _5089,
        _5090,
        _5092,
        _5094,
        _5095,
        _5096,
        _5098,
        _5100,
        _5102,
        _5103,
        _5104,
        _5105,
        _5106,
        _5108,
        _5109,
        _5110,
        _5111,
        _5113,
        _5114,
        _5115,
        _5117,
        _5119,
        _5121,
        _5122,
        _5124,
        _5125,
        _5127,
        _5128,
        _5129,
        _5130,
        _5131,
        _5132,
        _5133,
        _5135,
        _5137,
        _5139,
        _5140,
        _5141,
        _5142,
        _5143,
        _5144,
        _5146,
        _5147,
        _5149,
        _5150,
        _5151,
        _5153,
        _5154,
        _5156,
        _5157,
        _5159,
        _5160,
        _5162,
        _5163,
        _5165,
        _5166,
        _5167,
        _5168,
        _5169,
        _5170,
        _5171,
        _5172,
        _5174,
        _5175,
        _5176,
        _5177,
        _5178,
        _5180,
        _5181,
        _5183,
    )

    Self = TypeVar("Self", bound="PartCompoundModalAnalysis")
    CastSelf = TypeVar(
        "CastSelf", bound="PartCompoundModalAnalysis._Cast_PartCompoundModalAnalysis"
    )


__docformat__ = "restructuredtext en"
__all__ = ("PartCompoundModalAnalysis",)


@extended_dataclass(frozen=True, slots=True, weakref_slot=True)
class _Cast_PartCompoundModalAnalysis:
    """Special nested class for casting PartCompoundModalAnalysis to subclasses."""

    __parent__: "PartCompoundModalAnalysis"

    @property
    def part_compound_analysis(self: "CastSelf") -> "_7942.PartCompoundAnalysis":
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
    def abstract_assembly_compound_modal_analysis(
        self: "CastSelf",
    ) -> "_5053.AbstractAssemblyCompoundModalAnalysis":
        from mastapy._private.system_model.analyses_and_results.modal_analyses.compound import (
            _5053,
        )

        return self.__parent__._cast(_5053.AbstractAssemblyCompoundModalAnalysis)

    @property
    def abstract_shaft_compound_modal_analysis(
        self: "CastSelf",
    ) -> "_5054.AbstractShaftCompoundModalAnalysis":
        from mastapy._private.system_model.analyses_and_results.modal_analyses.compound import (
            _5054,
        )

        return self.__parent__._cast(_5054.AbstractShaftCompoundModalAnalysis)

    @property
    def abstract_shaft_or_housing_compound_modal_analysis(
        self: "CastSelf",
    ) -> "_5055.AbstractShaftOrHousingCompoundModalAnalysis":
        from mastapy._private.system_model.analyses_and_results.modal_analyses.compound import (
            _5055,
        )

        return self.__parent__._cast(_5055.AbstractShaftOrHousingCompoundModalAnalysis)

    @property
    def agma_gleason_conical_gear_compound_modal_analysis(
        self: "CastSelf",
    ) -> "_5057.AGMAGleasonConicalGearCompoundModalAnalysis":
        from mastapy._private.system_model.analyses_and_results.modal_analyses.compound import (
            _5057,
        )

        return self.__parent__._cast(_5057.AGMAGleasonConicalGearCompoundModalAnalysis)

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
    def bearing_compound_modal_analysis(
        self: "CastSelf",
    ) -> "_5061.BearingCompoundModalAnalysis":
        from mastapy._private.system_model.analyses_and_results.modal_analyses.compound import (
            _5061,
        )

        return self.__parent__._cast(_5061.BearingCompoundModalAnalysis)

    @property
    def belt_drive_compound_modal_analysis(
        self: "CastSelf",
    ) -> "_5063.BeltDriveCompoundModalAnalysis":
        from mastapy._private.system_model.analyses_and_results.modal_analyses.compound import (
            _5063,
        )

        return self.__parent__._cast(_5063.BeltDriveCompoundModalAnalysis)

    @property
    def bevel_differential_gear_compound_modal_analysis(
        self: "CastSelf",
    ) -> "_5064.BevelDifferentialGearCompoundModalAnalysis":
        from mastapy._private.system_model.analyses_and_results.modal_analyses.compound import (
            _5064,
        )

        return self.__parent__._cast(_5064.BevelDifferentialGearCompoundModalAnalysis)

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
    def bevel_differential_planet_gear_compound_modal_analysis(
        self: "CastSelf",
    ) -> "_5067.BevelDifferentialPlanetGearCompoundModalAnalysis":
        from mastapy._private.system_model.analyses_and_results.modal_analyses.compound import (
            _5067,
        )

        return self.__parent__._cast(
            _5067.BevelDifferentialPlanetGearCompoundModalAnalysis
        )

    @property
    def bevel_differential_sun_gear_compound_modal_analysis(
        self: "CastSelf",
    ) -> "_5068.BevelDifferentialSunGearCompoundModalAnalysis":
        from mastapy._private.system_model.analyses_and_results.modal_analyses.compound import (
            _5068,
        )

        return self.__parent__._cast(
            _5068.BevelDifferentialSunGearCompoundModalAnalysis
        )

    @property
    def bevel_gear_compound_modal_analysis(
        self: "CastSelf",
    ) -> "_5069.BevelGearCompoundModalAnalysis":
        from mastapy._private.system_model.analyses_and_results.modal_analyses.compound import (
            _5069,
        )

        return self.__parent__._cast(_5069.BevelGearCompoundModalAnalysis)

    @property
    def bevel_gear_set_compound_modal_analysis(
        self: "CastSelf",
    ) -> "_5071.BevelGearSetCompoundModalAnalysis":
        from mastapy._private.system_model.analyses_and_results.modal_analyses.compound import (
            _5071,
        )

        return self.__parent__._cast(_5071.BevelGearSetCompoundModalAnalysis)

    @property
    def bolt_compound_modal_analysis(
        self: "CastSelf",
    ) -> "_5072.BoltCompoundModalAnalysis":
        from mastapy._private.system_model.analyses_and_results.modal_analyses.compound import (
            _5072,
        )

        return self.__parent__._cast(_5072.BoltCompoundModalAnalysis)

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
    def clutch_half_compound_modal_analysis(
        self: "CastSelf",
    ) -> "_5076.ClutchHalfCompoundModalAnalysis":
        from mastapy._private.system_model.analyses_and_results.modal_analyses.compound import (
            _5076,
        )

        return self.__parent__._cast(_5076.ClutchHalfCompoundModalAnalysis)

    @property
    def component_compound_modal_analysis(
        self: "CastSelf",
    ) -> "_5078.ComponentCompoundModalAnalysis":
        from mastapy._private.system_model.analyses_and_results.modal_analyses.compound import (
            _5078,
        )

        return self.__parent__._cast(_5078.ComponentCompoundModalAnalysis)

    @property
    def concept_coupling_compound_modal_analysis(
        self: "CastSelf",
    ) -> "_5079.ConceptCouplingCompoundModalAnalysis":
        from mastapy._private.system_model.analyses_and_results.modal_analyses.compound import (
            _5079,
        )

        return self.__parent__._cast(_5079.ConceptCouplingCompoundModalAnalysis)

    @property
    def concept_coupling_half_compound_modal_analysis(
        self: "CastSelf",
    ) -> "_5081.ConceptCouplingHalfCompoundModalAnalysis":
        from mastapy._private.system_model.analyses_and_results.modal_analyses.compound import (
            _5081,
        )

        return self.__parent__._cast(_5081.ConceptCouplingHalfCompoundModalAnalysis)

    @property
    def concept_gear_compound_modal_analysis(
        self: "CastSelf",
    ) -> "_5082.ConceptGearCompoundModalAnalysis":
        from mastapy._private.system_model.analyses_and_results.modal_analyses.compound import (
            _5082,
        )

        return self.__parent__._cast(_5082.ConceptGearCompoundModalAnalysis)

    @property
    def concept_gear_set_compound_modal_analysis(
        self: "CastSelf",
    ) -> "_5084.ConceptGearSetCompoundModalAnalysis":
        from mastapy._private.system_model.analyses_and_results.modal_analyses.compound import (
            _5084,
        )

        return self.__parent__._cast(_5084.ConceptGearSetCompoundModalAnalysis)

    @property
    def conical_gear_compound_modal_analysis(
        self: "CastSelf",
    ) -> "_5085.ConicalGearCompoundModalAnalysis":
        from mastapy._private.system_model.analyses_and_results.modal_analyses.compound import (
            _5085,
        )

        return self.__parent__._cast(_5085.ConicalGearCompoundModalAnalysis)

    @property
    def conical_gear_set_compound_modal_analysis(
        self: "CastSelf",
    ) -> "_5087.ConicalGearSetCompoundModalAnalysis":
        from mastapy._private.system_model.analyses_and_results.modal_analyses.compound import (
            _5087,
        )

        return self.__parent__._cast(_5087.ConicalGearSetCompoundModalAnalysis)

    @property
    def connector_compound_modal_analysis(
        self: "CastSelf",
    ) -> "_5089.ConnectorCompoundModalAnalysis":
        from mastapy._private.system_model.analyses_and_results.modal_analyses.compound import (
            _5089,
        )

        return self.__parent__._cast(_5089.ConnectorCompoundModalAnalysis)

    @property
    def coupling_compound_modal_analysis(
        self: "CastSelf",
    ) -> "_5090.CouplingCompoundModalAnalysis":
        from mastapy._private.system_model.analyses_and_results.modal_analyses.compound import (
            _5090,
        )

        return self.__parent__._cast(_5090.CouplingCompoundModalAnalysis)

    @property
    def coupling_half_compound_modal_analysis(
        self: "CastSelf",
    ) -> "_5092.CouplingHalfCompoundModalAnalysis":
        from mastapy._private.system_model.analyses_and_results.modal_analyses.compound import (
            _5092,
        )

        return self.__parent__._cast(_5092.CouplingHalfCompoundModalAnalysis)

    @property
    def cvt_compound_modal_analysis(
        self: "CastSelf",
    ) -> "_5094.CVTCompoundModalAnalysis":
        from mastapy._private.system_model.analyses_and_results.modal_analyses.compound import (
            _5094,
        )

        return self.__parent__._cast(_5094.CVTCompoundModalAnalysis)

    @property
    def cvt_pulley_compound_modal_analysis(
        self: "CastSelf",
    ) -> "_5095.CVTPulleyCompoundModalAnalysis":
        from mastapy._private.system_model.analyses_and_results.modal_analyses.compound import (
            _5095,
        )

        return self.__parent__._cast(_5095.CVTPulleyCompoundModalAnalysis)

    @property
    def cycloidal_assembly_compound_modal_analysis(
        self: "CastSelf",
    ) -> "_5096.CycloidalAssemblyCompoundModalAnalysis":
        from mastapy._private.system_model.analyses_and_results.modal_analyses.compound import (
            _5096,
        )

        return self.__parent__._cast(_5096.CycloidalAssemblyCompoundModalAnalysis)

    @property
    def cycloidal_disc_compound_modal_analysis(
        self: "CastSelf",
    ) -> "_5098.CycloidalDiscCompoundModalAnalysis":
        from mastapy._private.system_model.analyses_and_results.modal_analyses.compound import (
            _5098,
        )

        return self.__parent__._cast(_5098.CycloidalDiscCompoundModalAnalysis)

    @property
    def cylindrical_gear_compound_modal_analysis(
        self: "CastSelf",
    ) -> "_5100.CylindricalGearCompoundModalAnalysis":
        from mastapy._private.system_model.analyses_and_results.modal_analyses.compound import (
            _5100,
        )

        return self.__parent__._cast(_5100.CylindricalGearCompoundModalAnalysis)

    @property
    def cylindrical_gear_set_compound_modal_analysis(
        self: "CastSelf",
    ) -> "_5102.CylindricalGearSetCompoundModalAnalysis":
        from mastapy._private.system_model.analyses_and_results.modal_analyses.compound import (
            _5102,
        )

        return self.__parent__._cast(_5102.CylindricalGearSetCompoundModalAnalysis)

    @property
    def cylindrical_planet_gear_compound_modal_analysis(
        self: "CastSelf",
    ) -> "_5103.CylindricalPlanetGearCompoundModalAnalysis":
        from mastapy._private.system_model.analyses_and_results.modal_analyses.compound import (
            _5103,
        )

        return self.__parent__._cast(_5103.CylindricalPlanetGearCompoundModalAnalysis)

    @property
    def datum_compound_modal_analysis(
        self: "CastSelf",
    ) -> "_5104.DatumCompoundModalAnalysis":
        from mastapy._private.system_model.analyses_and_results.modal_analyses.compound import (
            _5104,
        )

        return self.__parent__._cast(_5104.DatumCompoundModalAnalysis)

    @property
    def external_cad_model_compound_modal_analysis(
        self: "CastSelf",
    ) -> "_5105.ExternalCADModelCompoundModalAnalysis":
        from mastapy._private.system_model.analyses_and_results.modal_analyses.compound import (
            _5105,
        )

        return self.__parent__._cast(_5105.ExternalCADModelCompoundModalAnalysis)

    @property
    def face_gear_compound_modal_analysis(
        self: "CastSelf",
    ) -> "_5106.FaceGearCompoundModalAnalysis":
        from mastapy._private.system_model.analyses_and_results.modal_analyses.compound import (
            _5106,
        )

        return self.__parent__._cast(_5106.FaceGearCompoundModalAnalysis)

    @property
    def face_gear_set_compound_modal_analysis(
        self: "CastSelf",
    ) -> "_5108.FaceGearSetCompoundModalAnalysis":
        from mastapy._private.system_model.analyses_and_results.modal_analyses.compound import (
            _5108,
        )

        return self.__parent__._cast(_5108.FaceGearSetCompoundModalAnalysis)

    @property
    def fe_part_compound_modal_analysis(
        self: "CastSelf",
    ) -> "_5109.FEPartCompoundModalAnalysis":
        from mastapy._private.system_model.analyses_and_results.modal_analyses.compound import (
            _5109,
        )

        return self.__parent__._cast(_5109.FEPartCompoundModalAnalysis)

    @property
    def flexible_pin_assembly_compound_modal_analysis(
        self: "CastSelf",
    ) -> "_5110.FlexiblePinAssemblyCompoundModalAnalysis":
        from mastapy._private.system_model.analyses_and_results.modal_analyses.compound import (
            _5110,
        )

        return self.__parent__._cast(_5110.FlexiblePinAssemblyCompoundModalAnalysis)

    @property
    def gear_compound_modal_analysis(
        self: "CastSelf",
    ) -> "_5111.GearCompoundModalAnalysis":
        from mastapy._private.system_model.analyses_and_results.modal_analyses.compound import (
            _5111,
        )

        return self.__parent__._cast(_5111.GearCompoundModalAnalysis)

    @property
    def gear_set_compound_modal_analysis(
        self: "CastSelf",
    ) -> "_5113.GearSetCompoundModalAnalysis":
        from mastapy._private.system_model.analyses_and_results.modal_analyses.compound import (
            _5113,
        )

        return self.__parent__._cast(_5113.GearSetCompoundModalAnalysis)

    @property
    def guide_dxf_model_compound_modal_analysis(
        self: "CastSelf",
    ) -> "_5114.GuideDxfModelCompoundModalAnalysis":
        from mastapy._private.system_model.analyses_and_results.modal_analyses.compound import (
            _5114,
        )

        return self.__parent__._cast(_5114.GuideDxfModelCompoundModalAnalysis)

    @property
    def hypoid_gear_compound_modal_analysis(
        self: "CastSelf",
    ) -> "_5115.HypoidGearCompoundModalAnalysis":
        from mastapy._private.system_model.analyses_and_results.modal_analyses.compound import (
            _5115,
        )

        return self.__parent__._cast(_5115.HypoidGearCompoundModalAnalysis)

    @property
    def hypoid_gear_set_compound_modal_analysis(
        self: "CastSelf",
    ) -> "_5117.HypoidGearSetCompoundModalAnalysis":
        from mastapy._private.system_model.analyses_and_results.modal_analyses.compound import (
            _5117,
        )

        return self.__parent__._cast(_5117.HypoidGearSetCompoundModalAnalysis)

    @property
    def klingelnberg_cyclo_palloid_conical_gear_compound_modal_analysis(
        self: "CastSelf",
    ) -> "_5119.KlingelnbergCycloPalloidConicalGearCompoundModalAnalysis":
        from mastapy._private.system_model.analyses_and_results.modal_analyses.compound import (
            _5119,
        )

        return self.__parent__._cast(
            _5119.KlingelnbergCycloPalloidConicalGearCompoundModalAnalysis
        )

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
    def klingelnberg_cyclo_palloid_hypoid_gear_compound_modal_analysis(
        self: "CastSelf",
    ) -> "_5122.KlingelnbergCycloPalloidHypoidGearCompoundModalAnalysis":
        from mastapy._private.system_model.analyses_and_results.modal_analyses.compound import (
            _5122,
        )

        return self.__parent__._cast(
            _5122.KlingelnbergCycloPalloidHypoidGearCompoundModalAnalysis
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
    def klingelnberg_cyclo_palloid_spiral_bevel_gear_compound_modal_analysis(
        self: "CastSelf",
    ) -> "_5125.KlingelnbergCycloPalloidSpiralBevelGearCompoundModalAnalysis":
        from mastapy._private.system_model.analyses_and_results.modal_analyses.compound import (
            _5125,
        )

        return self.__parent__._cast(
            _5125.KlingelnbergCycloPalloidSpiralBevelGearCompoundModalAnalysis
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
    def mass_disc_compound_modal_analysis(
        self: "CastSelf",
    ) -> "_5128.MassDiscCompoundModalAnalysis":
        from mastapy._private.system_model.analyses_and_results.modal_analyses.compound import (
            _5128,
        )

        return self.__parent__._cast(_5128.MassDiscCompoundModalAnalysis)

    @property
    def measurement_component_compound_modal_analysis(
        self: "CastSelf",
    ) -> "_5129.MeasurementComponentCompoundModalAnalysis":
        from mastapy._private.system_model.analyses_and_results.modal_analyses.compound import (
            _5129,
        )

        return self.__parent__._cast(_5129.MeasurementComponentCompoundModalAnalysis)

    @property
    def microphone_array_compound_modal_analysis(
        self: "CastSelf",
    ) -> "_5130.MicrophoneArrayCompoundModalAnalysis":
        from mastapy._private.system_model.analyses_and_results.modal_analyses.compound import (
            _5130,
        )

        return self.__parent__._cast(_5130.MicrophoneArrayCompoundModalAnalysis)

    @property
    def microphone_compound_modal_analysis(
        self: "CastSelf",
    ) -> "_5131.MicrophoneCompoundModalAnalysis":
        from mastapy._private.system_model.analyses_and_results.modal_analyses.compound import (
            _5131,
        )

        return self.__parent__._cast(_5131.MicrophoneCompoundModalAnalysis)

    @property
    def mountable_component_compound_modal_analysis(
        self: "CastSelf",
    ) -> "_5132.MountableComponentCompoundModalAnalysis":
        from mastapy._private.system_model.analyses_and_results.modal_analyses.compound import (
            _5132,
        )

        return self.__parent__._cast(_5132.MountableComponentCompoundModalAnalysis)

    @property
    def oil_seal_compound_modal_analysis(
        self: "CastSelf",
    ) -> "_5133.OilSealCompoundModalAnalysis":
        from mastapy._private.system_model.analyses_and_results.modal_analyses.compound import (
            _5133,
        )

        return self.__parent__._cast(_5133.OilSealCompoundModalAnalysis)

    @property
    def part_to_part_shear_coupling_compound_modal_analysis(
        self: "CastSelf",
    ) -> "_5135.PartToPartShearCouplingCompoundModalAnalysis":
        from mastapy._private.system_model.analyses_and_results.modal_analyses.compound import (
            _5135,
        )

        return self.__parent__._cast(_5135.PartToPartShearCouplingCompoundModalAnalysis)

    @property
    def part_to_part_shear_coupling_half_compound_modal_analysis(
        self: "CastSelf",
    ) -> "_5137.PartToPartShearCouplingHalfCompoundModalAnalysis":
        from mastapy._private.system_model.analyses_and_results.modal_analyses.compound import (
            _5137,
        )

        return self.__parent__._cast(
            _5137.PartToPartShearCouplingHalfCompoundModalAnalysis
        )

    @property
    def planetary_gear_set_compound_modal_analysis(
        self: "CastSelf",
    ) -> "_5139.PlanetaryGearSetCompoundModalAnalysis":
        from mastapy._private.system_model.analyses_and_results.modal_analyses.compound import (
            _5139,
        )

        return self.__parent__._cast(_5139.PlanetaryGearSetCompoundModalAnalysis)

    @property
    def planet_carrier_compound_modal_analysis(
        self: "CastSelf",
    ) -> "_5140.PlanetCarrierCompoundModalAnalysis":
        from mastapy._private.system_model.analyses_and_results.modal_analyses.compound import (
            _5140,
        )

        return self.__parent__._cast(_5140.PlanetCarrierCompoundModalAnalysis)

    @property
    def point_load_compound_modal_analysis(
        self: "CastSelf",
    ) -> "_5141.PointLoadCompoundModalAnalysis":
        from mastapy._private.system_model.analyses_and_results.modal_analyses.compound import (
            _5141,
        )

        return self.__parent__._cast(_5141.PointLoadCompoundModalAnalysis)

    @property
    def power_load_compound_modal_analysis(
        self: "CastSelf",
    ) -> "_5142.PowerLoadCompoundModalAnalysis":
        from mastapy._private.system_model.analyses_and_results.modal_analyses.compound import (
            _5142,
        )

        return self.__parent__._cast(_5142.PowerLoadCompoundModalAnalysis)

    @property
    def pulley_compound_modal_analysis(
        self: "CastSelf",
    ) -> "_5143.PulleyCompoundModalAnalysis":
        from mastapy._private.system_model.analyses_and_results.modal_analyses.compound import (
            _5143,
        )

        return self.__parent__._cast(_5143.PulleyCompoundModalAnalysis)

    @property
    def ring_pins_compound_modal_analysis(
        self: "CastSelf",
    ) -> "_5144.RingPinsCompoundModalAnalysis":
        from mastapy._private.system_model.analyses_and_results.modal_analyses.compound import (
            _5144,
        )

        return self.__parent__._cast(_5144.RingPinsCompoundModalAnalysis)

    @property
    def rolling_ring_assembly_compound_modal_analysis(
        self: "CastSelf",
    ) -> "_5146.RollingRingAssemblyCompoundModalAnalysis":
        from mastapy._private.system_model.analyses_and_results.modal_analyses.compound import (
            _5146,
        )

        return self.__parent__._cast(_5146.RollingRingAssemblyCompoundModalAnalysis)

    @property
    def rolling_ring_compound_modal_analysis(
        self: "CastSelf",
    ) -> "_5147.RollingRingCompoundModalAnalysis":
        from mastapy._private.system_model.analyses_and_results.modal_analyses.compound import (
            _5147,
        )

        return self.__parent__._cast(_5147.RollingRingCompoundModalAnalysis)

    @property
    def root_assembly_compound_modal_analysis(
        self: "CastSelf",
    ) -> "_5149.RootAssemblyCompoundModalAnalysis":
        from mastapy._private.system_model.analyses_and_results.modal_analyses.compound import (
            _5149,
        )

        return self.__parent__._cast(_5149.RootAssemblyCompoundModalAnalysis)

    @property
    def shaft_compound_modal_analysis(
        self: "CastSelf",
    ) -> "_5150.ShaftCompoundModalAnalysis":
        from mastapy._private.system_model.analyses_and_results.modal_analyses.compound import (
            _5150,
        )

        return self.__parent__._cast(_5150.ShaftCompoundModalAnalysis)

    @property
    def shaft_hub_connection_compound_modal_analysis(
        self: "CastSelf",
    ) -> "_5151.ShaftHubConnectionCompoundModalAnalysis":
        from mastapy._private.system_model.analyses_and_results.modal_analyses.compound import (
            _5151,
        )

        return self.__parent__._cast(_5151.ShaftHubConnectionCompoundModalAnalysis)

    @property
    def specialised_assembly_compound_modal_analysis(
        self: "CastSelf",
    ) -> "_5153.SpecialisedAssemblyCompoundModalAnalysis":
        from mastapy._private.system_model.analyses_and_results.modal_analyses.compound import (
            _5153,
        )

        return self.__parent__._cast(_5153.SpecialisedAssemblyCompoundModalAnalysis)

    @property
    def spiral_bevel_gear_compound_modal_analysis(
        self: "CastSelf",
    ) -> "_5154.SpiralBevelGearCompoundModalAnalysis":
        from mastapy._private.system_model.analyses_and_results.modal_analyses.compound import (
            _5154,
        )

        return self.__parent__._cast(_5154.SpiralBevelGearCompoundModalAnalysis)

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
    def spring_damper_half_compound_modal_analysis(
        self: "CastSelf",
    ) -> "_5159.SpringDamperHalfCompoundModalAnalysis":
        from mastapy._private.system_model.analyses_and_results.modal_analyses.compound import (
            _5159,
        )

        return self.__parent__._cast(_5159.SpringDamperHalfCompoundModalAnalysis)

    @property
    def straight_bevel_diff_gear_compound_modal_analysis(
        self: "CastSelf",
    ) -> "_5160.StraightBevelDiffGearCompoundModalAnalysis":
        from mastapy._private.system_model.analyses_and_results.modal_analyses.compound import (
            _5160,
        )

        return self.__parent__._cast(_5160.StraightBevelDiffGearCompoundModalAnalysis)

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
    def straight_bevel_gear_compound_modal_analysis(
        self: "CastSelf",
    ) -> "_5163.StraightBevelGearCompoundModalAnalysis":
        from mastapy._private.system_model.analyses_and_results.modal_analyses.compound import (
            _5163,
        )

        return self.__parent__._cast(_5163.StraightBevelGearCompoundModalAnalysis)

    @property
    def straight_bevel_gear_set_compound_modal_analysis(
        self: "CastSelf",
    ) -> "_5165.StraightBevelGearSetCompoundModalAnalysis":
        from mastapy._private.system_model.analyses_and_results.modal_analyses.compound import (
            _5165,
        )

        return self.__parent__._cast(_5165.StraightBevelGearSetCompoundModalAnalysis)

    @property
    def straight_bevel_planet_gear_compound_modal_analysis(
        self: "CastSelf",
    ) -> "_5166.StraightBevelPlanetGearCompoundModalAnalysis":
        from mastapy._private.system_model.analyses_and_results.modal_analyses.compound import (
            _5166,
        )

        return self.__parent__._cast(_5166.StraightBevelPlanetGearCompoundModalAnalysis)

    @property
    def straight_bevel_sun_gear_compound_modal_analysis(
        self: "CastSelf",
    ) -> "_5167.StraightBevelSunGearCompoundModalAnalysis":
        from mastapy._private.system_model.analyses_and_results.modal_analyses.compound import (
            _5167,
        )

        return self.__parent__._cast(_5167.StraightBevelSunGearCompoundModalAnalysis)

    @property
    def synchroniser_compound_modal_analysis(
        self: "CastSelf",
    ) -> "_5168.SynchroniserCompoundModalAnalysis":
        from mastapy._private.system_model.analyses_and_results.modal_analyses.compound import (
            _5168,
        )

        return self.__parent__._cast(_5168.SynchroniserCompoundModalAnalysis)

    @property
    def synchroniser_half_compound_modal_analysis(
        self: "CastSelf",
    ) -> "_5169.SynchroniserHalfCompoundModalAnalysis":
        from mastapy._private.system_model.analyses_and_results.modal_analyses.compound import (
            _5169,
        )

        return self.__parent__._cast(_5169.SynchroniserHalfCompoundModalAnalysis)

    @property
    def synchroniser_part_compound_modal_analysis(
        self: "CastSelf",
    ) -> "_5170.SynchroniserPartCompoundModalAnalysis":
        from mastapy._private.system_model.analyses_and_results.modal_analyses.compound import (
            _5170,
        )

        return self.__parent__._cast(_5170.SynchroniserPartCompoundModalAnalysis)

    @property
    def synchroniser_sleeve_compound_modal_analysis(
        self: "CastSelf",
    ) -> "_5171.SynchroniserSleeveCompoundModalAnalysis":
        from mastapy._private.system_model.analyses_and_results.modal_analyses.compound import (
            _5171,
        )

        return self.__parent__._cast(_5171.SynchroniserSleeveCompoundModalAnalysis)

    @property
    def torque_converter_compound_modal_analysis(
        self: "CastSelf",
    ) -> "_5172.TorqueConverterCompoundModalAnalysis":
        from mastapy._private.system_model.analyses_and_results.modal_analyses.compound import (
            _5172,
        )

        return self.__parent__._cast(_5172.TorqueConverterCompoundModalAnalysis)

    @property
    def torque_converter_pump_compound_modal_analysis(
        self: "CastSelf",
    ) -> "_5174.TorqueConverterPumpCompoundModalAnalysis":
        from mastapy._private.system_model.analyses_and_results.modal_analyses.compound import (
            _5174,
        )

        return self.__parent__._cast(_5174.TorqueConverterPumpCompoundModalAnalysis)

    @property
    def torque_converter_turbine_compound_modal_analysis(
        self: "CastSelf",
    ) -> "_5175.TorqueConverterTurbineCompoundModalAnalysis":
        from mastapy._private.system_model.analyses_and_results.modal_analyses.compound import (
            _5175,
        )

        return self.__parent__._cast(_5175.TorqueConverterTurbineCompoundModalAnalysis)

    @property
    def unbalanced_mass_compound_modal_analysis(
        self: "CastSelf",
    ) -> "_5176.UnbalancedMassCompoundModalAnalysis":
        from mastapy._private.system_model.analyses_and_results.modal_analyses.compound import (
            _5176,
        )

        return self.__parent__._cast(_5176.UnbalancedMassCompoundModalAnalysis)

    @property
    def virtual_component_compound_modal_analysis(
        self: "CastSelf",
    ) -> "_5177.VirtualComponentCompoundModalAnalysis":
        from mastapy._private.system_model.analyses_and_results.modal_analyses.compound import (
            _5177,
        )

        return self.__parent__._cast(_5177.VirtualComponentCompoundModalAnalysis)

    @property
    def worm_gear_compound_modal_analysis(
        self: "CastSelf",
    ) -> "_5178.WormGearCompoundModalAnalysis":
        from mastapy._private.system_model.analyses_and_results.modal_analyses.compound import (
            _5178,
        )

        return self.__parent__._cast(_5178.WormGearCompoundModalAnalysis)

    @property
    def worm_gear_set_compound_modal_analysis(
        self: "CastSelf",
    ) -> "_5180.WormGearSetCompoundModalAnalysis":
        from mastapy._private.system_model.analyses_and_results.modal_analyses.compound import (
            _5180,
        )

        return self.__parent__._cast(_5180.WormGearSetCompoundModalAnalysis)

    @property
    def zerol_bevel_gear_compound_modal_analysis(
        self: "CastSelf",
    ) -> "_5181.ZerolBevelGearCompoundModalAnalysis":
        from mastapy._private.system_model.analyses_and_results.modal_analyses.compound import (
            _5181,
        )

        return self.__parent__._cast(_5181.ZerolBevelGearCompoundModalAnalysis)

    @property
    def zerol_bevel_gear_set_compound_modal_analysis(
        self: "CastSelf",
    ) -> "_5183.ZerolBevelGearSetCompoundModalAnalysis":
        from mastapy._private.system_model.analyses_and_results.modal_analyses.compound import (
            _5183,
        )

        return self.__parent__._cast(_5183.ZerolBevelGearSetCompoundModalAnalysis)

    @property
    def part_compound_modal_analysis(self: "CastSelf") -> "PartCompoundModalAnalysis":
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
class PartCompoundModalAnalysis(_7942.PartCompoundAnalysis):
    """PartCompoundModalAnalysis

    This is a mastapy class.
    """

    TYPE: ClassVar["Type"] = _PART_COMPOUND_MODAL_ANALYSIS

    wrapped: "Any"

    def __post_init__(self: "Self") -> None:
        """Override of the post initialisation magic method."""
        if not hasattr(self.wrapped, "reference_count"):
            self.wrapped.reference_count = 0

        self.wrapped.reference_count += 1

    @property
    @exception_bridge
    def component_analysis_cases(self: "Self") -> "List[_4987.PartModalAnalysis]":
        """List[mastapy.system_model.analyses_and_results.modal_analyses.PartModalAnalysis]

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
    def component_analysis_cases_ready(self: "Self") -> "List[_4987.PartModalAnalysis]":
        """List[mastapy.system_model.analyses_and_results.modal_analyses.PartModalAnalysis]

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
    def cast_to(self: "Self") -> "_Cast_PartCompoundModalAnalysis":
        """Cast to another type.

        Returns:
            _Cast_PartCompoundModalAnalysis
        """
        return _Cast_PartCompoundModalAnalysis(self)
