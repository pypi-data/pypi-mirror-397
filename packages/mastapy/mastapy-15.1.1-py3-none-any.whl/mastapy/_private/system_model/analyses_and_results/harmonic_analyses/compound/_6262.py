"""ComponentCompoundHarmonicAnalysis"""

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
    _6318,
)

_COMPONENT_COMPOUND_HARMONIC_ANALYSIS = python_net_import(
    "SMT.MastaAPI.SystemModel.AnalysesAndResults.HarmonicAnalyses.Compound",
    "ComponentCompoundHarmonicAnalysis",
)

if TYPE_CHECKING:
    from typing import Any, List, Type, TypeVar

    from mastapy._private.system_model.analyses_and_results import _2943
    from mastapy._private.system_model.analyses_and_results.analysis_cases import (
        _7939,
        _7942,
    )
    from mastapy._private.system_model.analyses_and_results.harmonic_analyses import (
        _6047,
    )
    from mastapy._private.system_model.analyses_and_results.harmonic_analyses.compound import (
        _6238,
        _6239,
        _6241,
        _6245,
        _6248,
        _6251,
        _6252,
        _6253,
        _6256,
        _6260,
        _6265,
        _6266,
        _6269,
        _6273,
        _6276,
        _6279,
        _6282,
        _6284,
        _6287,
        _6288,
        _6289,
        _6290,
        _6293,
        _6295,
        _6298,
        _6299,
        _6303,
        _6306,
        _6309,
        _6312,
        _6313,
        _6315,
        _6316,
        _6317,
        _6321,
        _6324,
        _6325,
        _6326,
        _6327,
        _6328,
        _6331,
        _6334,
        _6335,
        _6338,
        _6343,
        _6344,
        _6347,
        _6350,
        _6351,
        _6353,
        _6354,
        _6355,
        _6358,
        _6359,
        _6360,
        _6361,
        _6362,
        _6365,
    )

    Self = TypeVar("Self", bound="ComponentCompoundHarmonicAnalysis")
    CastSelf = TypeVar(
        "CastSelf",
        bound="ComponentCompoundHarmonicAnalysis._Cast_ComponentCompoundHarmonicAnalysis",
    )


__docformat__ = "restructuredtext en"
__all__ = ("ComponentCompoundHarmonicAnalysis",)


@extended_dataclass(frozen=True, slots=True, weakref_slot=True)
class _Cast_ComponentCompoundHarmonicAnalysis:
    """Special nested class for casting ComponentCompoundHarmonicAnalysis to subclasses."""

    __parent__: "ComponentCompoundHarmonicAnalysis"

    @property
    def part_compound_harmonic_analysis(
        self: "CastSelf",
    ) -> "_6318.PartCompoundHarmonicAnalysis":
        return self.__parent__._cast(_6318.PartCompoundHarmonicAnalysis)

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
    def abstract_shaft_compound_harmonic_analysis(
        self: "CastSelf",
    ) -> "_6238.AbstractShaftCompoundHarmonicAnalysis":
        from mastapy._private.system_model.analyses_and_results.harmonic_analyses.compound import (
            _6238,
        )

        return self.__parent__._cast(_6238.AbstractShaftCompoundHarmonicAnalysis)

    @property
    def abstract_shaft_or_housing_compound_harmonic_analysis(
        self: "CastSelf",
    ) -> "_6239.AbstractShaftOrHousingCompoundHarmonicAnalysis":
        from mastapy._private.system_model.analyses_and_results.harmonic_analyses.compound import (
            _6239,
        )

        return self.__parent__._cast(
            _6239.AbstractShaftOrHousingCompoundHarmonicAnalysis
        )

    @property
    def agma_gleason_conical_gear_compound_harmonic_analysis(
        self: "CastSelf",
    ) -> "_6241.AGMAGleasonConicalGearCompoundHarmonicAnalysis":
        from mastapy._private.system_model.analyses_and_results.harmonic_analyses.compound import (
            _6241,
        )

        return self.__parent__._cast(
            _6241.AGMAGleasonConicalGearCompoundHarmonicAnalysis
        )

    @property
    def bearing_compound_harmonic_analysis(
        self: "CastSelf",
    ) -> "_6245.BearingCompoundHarmonicAnalysis":
        from mastapy._private.system_model.analyses_and_results.harmonic_analyses.compound import (
            _6245,
        )

        return self.__parent__._cast(_6245.BearingCompoundHarmonicAnalysis)

    @property
    def bevel_differential_gear_compound_harmonic_analysis(
        self: "CastSelf",
    ) -> "_6248.BevelDifferentialGearCompoundHarmonicAnalysis":
        from mastapy._private.system_model.analyses_and_results.harmonic_analyses.compound import (
            _6248,
        )

        return self.__parent__._cast(
            _6248.BevelDifferentialGearCompoundHarmonicAnalysis
        )

    @property
    def bevel_differential_planet_gear_compound_harmonic_analysis(
        self: "CastSelf",
    ) -> "_6251.BevelDifferentialPlanetGearCompoundHarmonicAnalysis":
        from mastapy._private.system_model.analyses_and_results.harmonic_analyses.compound import (
            _6251,
        )

        return self.__parent__._cast(
            _6251.BevelDifferentialPlanetGearCompoundHarmonicAnalysis
        )

    @property
    def bevel_differential_sun_gear_compound_harmonic_analysis(
        self: "CastSelf",
    ) -> "_6252.BevelDifferentialSunGearCompoundHarmonicAnalysis":
        from mastapy._private.system_model.analyses_and_results.harmonic_analyses.compound import (
            _6252,
        )

        return self.__parent__._cast(
            _6252.BevelDifferentialSunGearCompoundHarmonicAnalysis
        )

    @property
    def bevel_gear_compound_harmonic_analysis(
        self: "CastSelf",
    ) -> "_6253.BevelGearCompoundHarmonicAnalysis":
        from mastapy._private.system_model.analyses_and_results.harmonic_analyses.compound import (
            _6253,
        )

        return self.__parent__._cast(_6253.BevelGearCompoundHarmonicAnalysis)

    @property
    def bolt_compound_harmonic_analysis(
        self: "CastSelf",
    ) -> "_6256.BoltCompoundHarmonicAnalysis":
        from mastapy._private.system_model.analyses_and_results.harmonic_analyses.compound import (
            _6256,
        )

        return self.__parent__._cast(_6256.BoltCompoundHarmonicAnalysis)

    @property
    def clutch_half_compound_harmonic_analysis(
        self: "CastSelf",
    ) -> "_6260.ClutchHalfCompoundHarmonicAnalysis":
        from mastapy._private.system_model.analyses_and_results.harmonic_analyses.compound import (
            _6260,
        )

        return self.__parent__._cast(_6260.ClutchHalfCompoundHarmonicAnalysis)

    @property
    def concept_coupling_half_compound_harmonic_analysis(
        self: "CastSelf",
    ) -> "_6265.ConceptCouplingHalfCompoundHarmonicAnalysis":
        from mastapy._private.system_model.analyses_and_results.harmonic_analyses.compound import (
            _6265,
        )

        return self.__parent__._cast(_6265.ConceptCouplingHalfCompoundHarmonicAnalysis)

    @property
    def concept_gear_compound_harmonic_analysis(
        self: "CastSelf",
    ) -> "_6266.ConceptGearCompoundHarmonicAnalysis":
        from mastapy._private.system_model.analyses_and_results.harmonic_analyses.compound import (
            _6266,
        )

        return self.__parent__._cast(_6266.ConceptGearCompoundHarmonicAnalysis)

    @property
    def conical_gear_compound_harmonic_analysis(
        self: "CastSelf",
    ) -> "_6269.ConicalGearCompoundHarmonicAnalysis":
        from mastapy._private.system_model.analyses_and_results.harmonic_analyses.compound import (
            _6269,
        )

        return self.__parent__._cast(_6269.ConicalGearCompoundHarmonicAnalysis)

    @property
    def connector_compound_harmonic_analysis(
        self: "CastSelf",
    ) -> "_6273.ConnectorCompoundHarmonicAnalysis":
        from mastapy._private.system_model.analyses_and_results.harmonic_analyses.compound import (
            _6273,
        )

        return self.__parent__._cast(_6273.ConnectorCompoundHarmonicAnalysis)

    @property
    def coupling_half_compound_harmonic_analysis(
        self: "CastSelf",
    ) -> "_6276.CouplingHalfCompoundHarmonicAnalysis":
        from mastapy._private.system_model.analyses_and_results.harmonic_analyses.compound import (
            _6276,
        )

        return self.__parent__._cast(_6276.CouplingHalfCompoundHarmonicAnalysis)

    @property
    def cvt_pulley_compound_harmonic_analysis(
        self: "CastSelf",
    ) -> "_6279.CVTPulleyCompoundHarmonicAnalysis":
        from mastapy._private.system_model.analyses_and_results.harmonic_analyses.compound import (
            _6279,
        )

        return self.__parent__._cast(_6279.CVTPulleyCompoundHarmonicAnalysis)

    @property
    def cycloidal_disc_compound_harmonic_analysis(
        self: "CastSelf",
    ) -> "_6282.CycloidalDiscCompoundHarmonicAnalysis":
        from mastapy._private.system_model.analyses_and_results.harmonic_analyses.compound import (
            _6282,
        )

        return self.__parent__._cast(_6282.CycloidalDiscCompoundHarmonicAnalysis)

    @property
    def cylindrical_gear_compound_harmonic_analysis(
        self: "CastSelf",
    ) -> "_6284.CylindricalGearCompoundHarmonicAnalysis":
        from mastapy._private.system_model.analyses_and_results.harmonic_analyses.compound import (
            _6284,
        )

        return self.__parent__._cast(_6284.CylindricalGearCompoundHarmonicAnalysis)

    @property
    def cylindrical_planet_gear_compound_harmonic_analysis(
        self: "CastSelf",
    ) -> "_6287.CylindricalPlanetGearCompoundHarmonicAnalysis":
        from mastapy._private.system_model.analyses_and_results.harmonic_analyses.compound import (
            _6287,
        )

        return self.__parent__._cast(
            _6287.CylindricalPlanetGearCompoundHarmonicAnalysis
        )

    @property
    def datum_compound_harmonic_analysis(
        self: "CastSelf",
    ) -> "_6288.DatumCompoundHarmonicAnalysis":
        from mastapy._private.system_model.analyses_and_results.harmonic_analyses.compound import (
            _6288,
        )

        return self.__parent__._cast(_6288.DatumCompoundHarmonicAnalysis)

    @property
    def external_cad_model_compound_harmonic_analysis(
        self: "CastSelf",
    ) -> "_6289.ExternalCADModelCompoundHarmonicAnalysis":
        from mastapy._private.system_model.analyses_and_results.harmonic_analyses.compound import (
            _6289,
        )

        return self.__parent__._cast(_6289.ExternalCADModelCompoundHarmonicAnalysis)

    @property
    def face_gear_compound_harmonic_analysis(
        self: "CastSelf",
    ) -> "_6290.FaceGearCompoundHarmonicAnalysis":
        from mastapy._private.system_model.analyses_and_results.harmonic_analyses.compound import (
            _6290,
        )

        return self.__parent__._cast(_6290.FaceGearCompoundHarmonicAnalysis)

    @property
    def fe_part_compound_harmonic_analysis(
        self: "CastSelf",
    ) -> "_6293.FEPartCompoundHarmonicAnalysis":
        from mastapy._private.system_model.analyses_and_results.harmonic_analyses.compound import (
            _6293,
        )

        return self.__parent__._cast(_6293.FEPartCompoundHarmonicAnalysis)

    @property
    def gear_compound_harmonic_analysis(
        self: "CastSelf",
    ) -> "_6295.GearCompoundHarmonicAnalysis":
        from mastapy._private.system_model.analyses_and_results.harmonic_analyses.compound import (
            _6295,
        )

        return self.__parent__._cast(_6295.GearCompoundHarmonicAnalysis)

    @property
    def guide_dxf_model_compound_harmonic_analysis(
        self: "CastSelf",
    ) -> "_6298.GuideDxfModelCompoundHarmonicAnalysis":
        from mastapy._private.system_model.analyses_and_results.harmonic_analyses.compound import (
            _6298,
        )

        return self.__parent__._cast(_6298.GuideDxfModelCompoundHarmonicAnalysis)

    @property
    def hypoid_gear_compound_harmonic_analysis(
        self: "CastSelf",
    ) -> "_6299.HypoidGearCompoundHarmonicAnalysis":
        from mastapy._private.system_model.analyses_and_results.harmonic_analyses.compound import (
            _6299,
        )

        return self.__parent__._cast(_6299.HypoidGearCompoundHarmonicAnalysis)

    @property
    def klingelnberg_cyclo_palloid_conical_gear_compound_harmonic_analysis(
        self: "CastSelf",
    ) -> "_6303.KlingelnbergCycloPalloidConicalGearCompoundHarmonicAnalysis":
        from mastapy._private.system_model.analyses_and_results.harmonic_analyses.compound import (
            _6303,
        )

        return self.__parent__._cast(
            _6303.KlingelnbergCycloPalloidConicalGearCompoundHarmonicAnalysis
        )

    @property
    def klingelnberg_cyclo_palloid_hypoid_gear_compound_harmonic_analysis(
        self: "CastSelf",
    ) -> "_6306.KlingelnbergCycloPalloidHypoidGearCompoundHarmonicAnalysis":
        from mastapy._private.system_model.analyses_and_results.harmonic_analyses.compound import (
            _6306,
        )

        return self.__parent__._cast(
            _6306.KlingelnbergCycloPalloidHypoidGearCompoundHarmonicAnalysis
        )

    @property
    def klingelnberg_cyclo_palloid_spiral_bevel_gear_compound_harmonic_analysis(
        self: "CastSelf",
    ) -> "_6309.KlingelnbergCycloPalloidSpiralBevelGearCompoundHarmonicAnalysis":
        from mastapy._private.system_model.analyses_and_results.harmonic_analyses.compound import (
            _6309,
        )

        return self.__parent__._cast(
            _6309.KlingelnbergCycloPalloidSpiralBevelGearCompoundHarmonicAnalysis
        )

    @property
    def mass_disc_compound_harmonic_analysis(
        self: "CastSelf",
    ) -> "_6312.MassDiscCompoundHarmonicAnalysis":
        from mastapy._private.system_model.analyses_and_results.harmonic_analyses.compound import (
            _6312,
        )

        return self.__parent__._cast(_6312.MassDiscCompoundHarmonicAnalysis)

    @property
    def measurement_component_compound_harmonic_analysis(
        self: "CastSelf",
    ) -> "_6313.MeasurementComponentCompoundHarmonicAnalysis":
        from mastapy._private.system_model.analyses_and_results.harmonic_analyses.compound import (
            _6313,
        )

        return self.__parent__._cast(_6313.MeasurementComponentCompoundHarmonicAnalysis)

    @property
    def microphone_compound_harmonic_analysis(
        self: "CastSelf",
    ) -> "_6315.MicrophoneCompoundHarmonicAnalysis":
        from mastapy._private.system_model.analyses_and_results.harmonic_analyses.compound import (
            _6315,
        )

        return self.__parent__._cast(_6315.MicrophoneCompoundHarmonicAnalysis)

    @property
    def mountable_component_compound_harmonic_analysis(
        self: "CastSelf",
    ) -> "_6316.MountableComponentCompoundHarmonicAnalysis":
        from mastapy._private.system_model.analyses_and_results.harmonic_analyses.compound import (
            _6316,
        )

        return self.__parent__._cast(_6316.MountableComponentCompoundHarmonicAnalysis)

    @property
    def oil_seal_compound_harmonic_analysis(
        self: "CastSelf",
    ) -> "_6317.OilSealCompoundHarmonicAnalysis":
        from mastapy._private.system_model.analyses_and_results.harmonic_analyses.compound import (
            _6317,
        )

        return self.__parent__._cast(_6317.OilSealCompoundHarmonicAnalysis)

    @property
    def part_to_part_shear_coupling_half_compound_harmonic_analysis(
        self: "CastSelf",
    ) -> "_6321.PartToPartShearCouplingHalfCompoundHarmonicAnalysis":
        from mastapy._private.system_model.analyses_and_results.harmonic_analyses.compound import (
            _6321,
        )

        return self.__parent__._cast(
            _6321.PartToPartShearCouplingHalfCompoundHarmonicAnalysis
        )

    @property
    def planet_carrier_compound_harmonic_analysis(
        self: "CastSelf",
    ) -> "_6324.PlanetCarrierCompoundHarmonicAnalysis":
        from mastapy._private.system_model.analyses_and_results.harmonic_analyses.compound import (
            _6324,
        )

        return self.__parent__._cast(_6324.PlanetCarrierCompoundHarmonicAnalysis)

    @property
    def point_load_compound_harmonic_analysis(
        self: "CastSelf",
    ) -> "_6325.PointLoadCompoundHarmonicAnalysis":
        from mastapy._private.system_model.analyses_and_results.harmonic_analyses.compound import (
            _6325,
        )

        return self.__parent__._cast(_6325.PointLoadCompoundHarmonicAnalysis)

    @property
    def power_load_compound_harmonic_analysis(
        self: "CastSelf",
    ) -> "_6326.PowerLoadCompoundHarmonicAnalysis":
        from mastapy._private.system_model.analyses_and_results.harmonic_analyses.compound import (
            _6326,
        )

        return self.__parent__._cast(_6326.PowerLoadCompoundHarmonicAnalysis)

    @property
    def pulley_compound_harmonic_analysis(
        self: "CastSelf",
    ) -> "_6327.PulleyCompoundHarmonicAnalysis":
        from mastapy._private.system_model.analyses_and_results.harmonic_analyses.compound import (
            _6327,
        )

        return self.__parent__._cast(_6327.PulleyCompoundHarmonicAnalysis)

    @property
    def ring_pins_compound_harmonic_analysis(
        self: "CastSelf",
    ) -> "_6328.RingPinsCompoundHarmonicAnalysis":
        from mastapy._private.system_model.analyses_and_results.harmonic_analyses.compound import (
            _6328,
        )

        return self.__parent__._cast(_6328.RingPinsCompoundHarmonicAnalysis)

    @property
    def rolling_ring_compound_harmonic_analysis(
        self: "CastSelf",
    ) -> "_6331.RollingRingCompoundHarmonicAnalysis":
        from mastapy._private.system_model.analyses_and_results.harmonic_analyses.compound import (
            _6331,
        )

        return self.__parent__._cast(_6331.RollingRingCompoundHarmonicAnalysis)

    @property
    def shaft_compound_harmonic_analysis(
        self: "CastSelf",
    ) -> "_6334.ShaftCompoundHarmonicAnalysis":
        from mastapy._private.system_model.analyses_and_results.harmonic_analyses.compound import (
            _6334,
        )

        return self.__parent__._cast(_6334.ShaftCompoundHarmonicAnalysis)

    @property
    def shaft_hub_connection_compound_harmonic_analysis(
        self: "CastSelf",
    ) -> "_6335.ShaftHubConnectionCompoundHarmonicAnalysis":
        from mastapy._private.system_model.analyses_and_results.harmonic_analyses.compound import (
            _6335,
        )

        return self.__parent__._cast(_6335.ShaftHubConnectionCompoundHarmonicAnalysis)

    @property
    def spiral_bevel_gear_compound_harmonic_analysis(
        self: "CastSelf",
    ) -> "_6338.SpiralBevelGearCompoundHarmonicAnalysis":
        from mastapy._private.system_model.analyses_and_results.harmonic_analyses.compound import (
            _6338,
        )

        return self.__parent__._cast(_6338.SpiralBevelGearCompoundHarmonicAnalysis)

    @property
    def spring_damper_half_compound_harmonic_analysis(
        self: "CastSelf",
    ) -> "_6343.SpringDamperHalfCompoundHarmonicAnalysis":
        from mastapy._private.system_model.analyses_and_results.harmonic_analyses.compound import (
            _6343,
        )

        return self.__parent__._cast(_6343.SpringDamperHalfCompoundHarmonicAnalysis)

    @property
    def straight_bevel_diff_gear_compound_harmonic_analysis(
        self: "CastSelf",
    ) -> "_6344.StraightBevelDiffGearCompoundHarmonicAnalysis":
        from mastapy._private.system_model.analyses_and_results.harmonic_analyses.compound import (
            _6344,
        )

        return self.__parent__._cast(
            _6344.StraightBevelDiffGearCompoundHarmonicAnalysis
        )

    @property
    def straight_bevel_gear_compound_harmonic_analysis(
        self: "CastSelf",
    ) -> "_6347.StraightBevelGearCompoundHarmonicAnalysis":
        from mastapy._private.system_model.analyses_and_results.harmonic_analyses.compound import (
            _6347,
        )

        return self.__parent__._cast(_6347.StraightBevelGearCompoundHarmonicAnalysis)

    @property
    def straight_bevel_planet_gear_compound_harmonic_analysis(
        self: "CastSelf",
    ) -> "_6350.StraightBevelPlanetGearCompoundHarmonicAnalysis":
        from mastapy._private.system_model.analyses_and_results.harmonic_analyses.compound import (
            _6350,
        )

        return self.__parent__._cast(
            _6350.StraightBevelPlanetGearCompoundHarmonicAnalysis
        )

    @property
    def straight_bevel_sun_gear_compound_harmonic_analysis(
        self: "CastSelf",
    ) -> "_6351.StraightBevelSunGearCompoundHarmonicAnalysis":
        from mastapy._private.system_model.analyses_and_results.harmonic_analyses.compound import (
            _6351,
        )

        return self.__parent__._cast(_6351.StraightBevelSunGearCompoundHarmonicAnalysis)

    @property
    def synchroniser_half_compound_harmonic_analysis(
        self: "CastSelf",
    ) -> "_6353.SynchroniserHalfCompoundHarmonicAnalysis":
        from mastapy._private.system_model.analyses_and_results.harmonic_analyses.compound import (
            _6353,
        )

        return self.__parent__._cast(_6353.SynchroniserHalfCompoundHarmonicAnalysis)

    @property
    def synchroniser_part_compound_harmonic_analysis(
        self: "CastSelf",
    ) -> "_6354.SynchroniserPartCompoundHarmonicAnalysis":
        from mastapy._private.system_model.analyses_and_results.harmonic_analyses.compound import (
            _6354,
        )

        return self.__parent__._cast(_6354.SynchroniserPartCompoundHarmonicAnalysis)

    @property
    def synchroniser_sleeve_compound_harmonic_analysis(
        self: "CastSelf",
    ) -> "_6355.SynchroniserSleeveCompoundHarmonicAnalysis":
        from mastapy._private.system_model.analyses_and_results.harmonic_analyses.compound import (
            _6355,
        )

        return self.__parent__._cast(_6355.SynchroniserSleeveCompoundHarmonicAnalysis)

    @property
    def torque_converter_pump_compound_harmonic_analysis(
        self: "CastSelf",
    ) -> "_6358.TorqueConverterPumpCompoundHarmonicAnalysis":
        from mastapy._private.system_model.analyses_and_results.harmonic_analyses.compound import (
            _6358,
        )

        return self.__parent__._cast(_6358.TorqueConverterPumpCompoundHarmonicAnalysis)

    @property
    def torque_converter_turbine_compound_harmonic_analysis(
        self: "CastSelf",
    ) -> "_6359.TorqueConverterTurbineCompoundHarmonicAnalysis":
        from mastapy._private.system_model.analyses_and_results.harmonic_analyses.compound import (
            _6359,
        )

        return self.__parent__._cast(
            _6359.TorqueConverterTurbineCompoundHarmonicAnalysis
        )

    @property
    def unbalanced_mass_compound_harmonic_analysis(
        self: "CastSelf",
    ) -> "_6360.UnbalancedMassCompoundHarmonicAnalysis":
        from mastapy._private.system_model.analyses_and_results.harmonic_analyses.compound import (
            _6360,
        )

        return self.__parent__._cast(_6360.UnbalancedMassCompoundHarmonicAnalysis)

    @property
    def virtual_component_compound_harmonic_analysis(
        self: "CastSelf",
    ) -> "_6361.VirtualComponentCompoundHarmonicAnalysis":
        from mastapy._private.system_model.analyses_and_results.harmonic_analyses.compound import (
            _6361,
        )

        return self.__parent__._cast(_6361.VirtualComponentCompoundHarmonicAnalysis)

    @property
    def worm_gear_compound_harmonic_analysis(
        self: "CastSelf",
    ) -> "_6362.WormGearCompoundHarmonicAnalysis":
        from mastapy._private.system_model.analyses_and_results.harmonic_analyses.compound import (
            _6362,
        )

        return self.__parent__._cast(_6362.WormGearCompoundHarmonicAnalysis)

    @property
    def zerol_bevel_gear_compound_harmonic_analysis(
        self: "CastSelf",
    ) -> "_6365.ZerolBevelGearCompoundHarmonicAnalysis":
        from mastapy._private.system_model.analyses_and_results.harmonic_analyses.compound import (
            _6365,
        )

        return self.__parent__._cast(_6365.ZerolBevelGearCompoundHarmonicAnalysis)

    @property
    def component_compound_harmonic_analysis(
        self: "CastSelf",
    ) -> "ComponentCompoundHarmonicAnalysis":
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
class ComponentCompoundHarmonicAnalysis(_6318.PartCompoundHarmonicAnalysis):
    """ComponentCompoundHarmonicAnalysis

    This is a mastapy class.
    """

    TYPE: ClassVar["Type"] = _COMPONENT_COMPOUND_HARMONIC_ANALYSIS

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
    ) -> "List[_6047.ComponentHarmonicAnalysis]":
        """List[mastapy.system_model.analyses_and_results.harmonic_analyses.ComponentHarmonicAnalysis]

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
    ) -> "List[_6047.ComponentHarmonicAnalysis]":
        """List[mastapy.system_model.analyses_and_results.harmonic_analyses.ComponentHarmonicAnalysis]

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
    def cast_to(self: "Self") -> "_Cast_ComponentCompoundHarmonicAnalysis":
        """Cast to another type.

        Returns:
            _Cast_ComponentCompoundHarmonicAnalysis
        """
        return _Cast_ComponentCompoundHarmonicAnalysis(self)
