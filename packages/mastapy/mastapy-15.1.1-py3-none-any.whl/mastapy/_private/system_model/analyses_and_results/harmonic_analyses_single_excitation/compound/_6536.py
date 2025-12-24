"""ConnectionCompoundHarmonicAnalysisOfSingleExcitation"""

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
from mastapy._private.system_model.analyses_and_results.analysis_cases import _7935

_CONNECTION_COMPOUND_HARMONIC_ANALYSIS_OF_SINGLE_EXCITATION = python_net_import(
    "SMT.MastaAPI.SystemModel.AnalysesAndResults.HarmonicAnalysesSingleExcitation.Compound",
    "ConnectionCompoundHarmonicAnalysisOfSingleExcitation",
)

if TYPE_CHECKING:
    from typing import Any, List, Type, TypeVar

    from mastapy._private.system_model.analyses_and_results import _2943
    from mastapy._private.system_model.analyses_and_results.analysis_cases import _7939
    from mastapy._private.system_model.analyses_and_results.harmonic_analyses_single_excitation import (
        _6403,
    )
    from mastapy._private.system_model.analyses_and_results.harmonic_analyses_single_excitation.compound import (
        _6504,
        _6506,
        _6510,
        _6513,
        _6518,
        _6523,
        _6525,
        _6528,
        _6531,
        _6534,
        _6539,
        _6541,
        _6545,
        _6547,
        _6549,
        _6555,
        _6560,
        _6564,
        _6566,
        _6568,
        _6571,
        _6574,
        _6584,
        _6586,
        _6593,
        _6596,
        _6600,
        _6603,
        _6606,
        _6609,
        _6612,
        _6621,
        _6627,
        _6630,
    )

    Self = TypeVar("Self", bound="ConnectionCompoundHarmonicAnalysisOfSingleExcitation")
    CastSelf = TypeVar(
        "CastSelf",
        bound="ConnectionCompoundHarmonicAnalysisOfSingleExcitation._Cast_ConnectionCompoundHarmonicAnalysisOfSingleExcitation",
    )


__docformat__ = "restructuredtext en"
__all__ = ("ConnectionCompoundHarmonicAnalysisOfSingleExcitation",)


@extended_dataclass(frozen=True, slots=True, weakref_slot=True)
class _Cast_ConnectionCompoundHarmonicAnalysisOfSingleExcitation:
    """Special nested class for casting ConnectionCompoundHarmonicAnalysisOfSingleExcitation to subclasses."""

    __parent__: "ConnectionCompoundHarmonicAnalysisOfSingleExcitation"

    @property
    def connection_compound_analysis(
        self: "CastSelf",
    ) -> "_7935.ConnectionCompoundAnalysis":
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
    def abstract_shaft_to_mountable_component_connection_compound_harmonic_analysis_of_single_excitation(
        self: "CastSelf",
    ) -> "_6504.AbstractShaftToMountableComponentConnectionCompoundHarmonicAnalysisOfSingleExcitation":
        from mastapy._private.system_model.analyses_and_results.harmonic_analyses_single_excitation.compound import (
            _6504,
        )

        return self.__parent__._cast(
            _6504.AbstractShaftToMountableComponentConnectionCompoundHarmonicAnalysisOfSingleExcitation
        )

    @property
    def agma_gleason_conical_gear_mesh_compound_harmonic_analysis_of_single_excitation(
        self: "CastSelf",
    ) -> "_6506.AGMAGleasonConicalGearMeshCompoundHarmonicAnalysisOfSingleExcitation":
        from mastapy._private.system_model.analyses_and_results.harmonic_analyses_single_excitation.compound import (
            _6506,
        )

        return self.__parent__._cast(
            _6506.AGMAGleasonConicalGearMeshCompoundHarmonicAnalysisOfSingleExcitation
        )

    @property
    def belt_connection_compound_harmonic_analysis_of_single_excitation(
        self: "CastSelf",
    ) -> "_6510.BeltConnectionCompoundHarmonicAnalysisOfSingleExcitation":
        from mastapy._private.system_model.analyses_and_results.harmonic_analyses_single_excitation.compound import (
            _6510,
        )

        return self.__parent__._cast(
            _6510.BeltConnectionCompoundHarmonicAnalysisOfSingleExcitation
        )

    @property
    def bevel_differential_gear_mesh_compound_harmonic_analysis_of_single_excitation(
        self: "CastSelf",
    ) -> "_6513.BevelDifferentialGearMeshCompoundHarmonicAnalysisOfSingleExcitation":
        from mastapy._private.system_model.analyses_and_results.harmonic_analyses_single_excitation.compound import (
            _6513,
        )

        return self.__parent__._cast(
            _6513.BevelDifferentialGearMeshCompoundHarmonicAnalysisOfSingleExcitation
        )

    @property
    def bevel_gear_mesh_compound_harmonic_analysis_of_single_excitation(
        self: "CastSelf",
    ) -> "_6518.BevelGearMeshCompoundHarmonicAnalysisOfSingleExcitation":
        from mastapy._private.system_model.analyses_and_results.harmonic_analyses_single_excitation.compound import (
            _6518,
        )

        return self.__parent__._cast(
            _6518.BevelGearMeshCompoundHarmonicAnalysisOfSingleExcitation
        )

    @property
    def clutch_connection_compound_harmonic_analysis_of_single_excitation(
        self: "CastSelf",
    ) -> "_6523.ClutchConnectionCompoundHarmonicAnalysisOfSingleExcitation":
        from mastapy._private.system_model.analyses_and_results.harmonic_analyses_single_excitation.compound import (
            _6523,
        )

        return self.__parent__._cast(
            _6523.ClutchConnectionCompoundHarmonicAnalysisOfSingleExcitation
        )

    @property
    def coaxial_connection_compound_harmonic_analysis_of_single_excitation(
        self: "CastSelf",
    ) -> "_6525.CoaxialConnectionCompoundHarmonicAnalysisOfSingleExcitation":
        from mastapy._private.system_model.analyses_and_results.harmonic_analyses_single_excitation.compound import (
            _6525,
        )

        return self.__parent__._cast(
            _6525.CoaxialConnectionCompoundHarmonicAnalysisOfSingleExcitation
        )

    @property
    def concept_coupling_connection_compound_harmonic_analysis_of_single_excitation(
        self: "CastSelf",
    ) -> "_6528.ConceptCouplingConnectionCompoundHarmonicAnalysisOfSingleExcitation":
        from mastapy._private.system_model.analyses_and_results.harmonic_analyses_single_excitation.compound import (
            _6528,
        )

        return self.__parent__._cast(
            _6528.ConceptCouplingConnectionCompoundHarmonicAnalysisOfSingleExcitation
        )

    @property
    def concept_gear_mesh_compound_harmonic_analysis_of_single_excitation(
        self: "CastSelf",
    ) -> "_6531.ConceptGearMeshCompoundHarmonicAnalysisOfSingleExcitation":
        from mastapy._private.system_model.analyses_and_results.harmonic_analyses_single_excitation.compound import (
            _6531,
        )

        return self.__parent__._cast(
            _6531.ConceptGearMeshCompoundHarmonicAnalysisOfSingleExcitation
        )

    @property
    def conical_gear_mesh_compound_harmonic_analysis_of_single_excitation(
        self: "CastSelf",
    ) -> "_6534.ConicalGearMeshCompoundHarmonicAnalysisOfSingleExcitation":
        from mastapy._private.system_model.analyses_and_results.harmonic_analyses_single_excitation.compound import (
            _6534,
        )

        return self.__parent__._cast(
            _6534.ConicalGearMeshCompoundHarmonicAnalysisOfSingleExcitation
        )

    @property
    def coupling_connection_compound_harmonic_analysis_of_single_excitation(
        self: "CastSelf",
    ) -> "_6539.CouplingConnectionCompoundHarmonicAnalysisOfSingleExcitation":
        from mastapy._private.system_model.analyses_and_results.harmonic_analyses_single_excitation.compound import (
            _6539,
        )

        return self.__parent__._cast(
            _6539.CouplingConnectionCompoundHarmonicAnalysisOfSingleExcitation
        )

    @property
    def cvt_belt_connection_compound_harmonic_analysis_of_single_excitation(
        self: "CastSelf",
    ) -> "_6541.CVTBeltConnectionCompoundHarmonicAnalysisOfSingleExcitation":
        from mastapy._private.system_model.analyses_and_results.harmonic_analyses_single_excitation.compound import (
            _6541,
        )

        return self.__parent__._cast(
            _6541.CVTBeltConnectionCompoundHarmonicAnalysisOfSingleExcitation
        )

    @property
    def cycloidal_disc_central_bearing_connection_compound_harmonic_analysis_of_single_excitation(
        self: "CastSelf",
    ) -> "_6545.CycloidalDiscCentralBearingConnectionCompoundHarmonicAnalysisOfSingleExcitation":
        from mastapy._private.system_model.analyses_and_results.harmonic_analyses_single_excitation.compound import (
            _6545,
        )

        return self.__parent__._cast(
            _6545.CycloidalDiscCentralBearingConnectionCompoundHarmonicAnalysisOfSingleExcitation
        )

    @property
    def cycloidal_disc_planetary_bearing_connection_compound_harmonic_analysis_of_single_excitation(
        self: "CastSelf",
    ) -> "_6547.CycloidalDiscPlanetaryBearingConnectionCompoundHarmonicAnalysisOfSingleExcitation":
        from mastapy._private.system_model.analyses_and_results.harmonic_analyses_single_excitation.compound import (
            _6547,
        )

        return self.__parent__._cast(
            _6547.CycloidalDiscPlanetaryBearingConnectionCompoundHarmonicAnalysisOfSingleExcitation
        )

    @property
    def cylindrical_gear_mesh_compound_harmonic_analysis_of_single_excitation(
        self: "CastSelf",
    ) -> "_6549.CylindricalGearMeshCompoundHarmonicAnalysisOfSingleExcitation":
        from mastapy._private.system_model.analyses_and_results.harmonic_analyses_single_excitation.compound import (
            _6549,
        )

        return self.__parent__._cast(
            _6549.CylindricalGearMeshCompoundHarmonicAnalysisOfSingleExcitation
        )

    @property
    def face_gear_mesh_compound_harmonic_analysis_of_single_excitation(
        self: "CastSelf",
    ) -> "_6555.FaceGearMeshCompoundHarmonicAnalysisOfSingleExcitation":
        from mastapy._private.system_model.analyses_and_results.harmonic_analyses_single_excitation.compound import (
            _6555,
        )

        return self.__parent__._cast(
            _6555.FaceGearMeshCompoundHarmonicAnalysisOfSingleExcitation
        )

    @property
    def gear_mesh_compound_harmonic_analysis_of_single_excitation(
        self: "CastSelf",
    ) -> "_6560.GearMeshCompoundHarmonicAnalysisOfSingleExcitation":
        from mastapy._private.system_model.analyses_and_results.harmonic_analyses_single_excitation.compound import (
            _6560,
        )

        return self.__parent__._cast(
            _6560.GearMeshCompoundHarmonicAnalysisOfSingleExcitation
        )

    @property
    def hypoid_gear_mesh_compound_harmonic_analysis_of_single_excitation(
        self: "CastSelf",
    ) -> "_6564.HypoidGearMeshCompoundHarmonicAnalysisOfSingleExcitation":
        from mastapy._private.system_model.analyses_and_results.harmonic_analyses_single_excitation.compound import (
            _6564,
        )

        return self.__parent__._cast(
            _6564.HypoidGearMeshCompoundHarmonicAnalysisOfSingleExcitation
        )

    @property
    def inter_mountable_component_connection_compound_harmonic_analysis_of_single_excitation(
        self: "CastSelf",
    ) -> "_6566.InterMountableComponentConnectionCompoundHarmonicAnalysisOfSingleExcitation":
        from mastapy._private.system_model.analyses_and_results.harmonic_analyses_single_excitation.compound import (
            _6566,
        )

        return self.__parent__._cast(
            _6566.InterMountableComponentConnectionCompoundHarmonicAnalysisOfSingleExcitation
        )

    @property
    def klingelnberg_cyclo_palloid_conical_gear_mesh_compound_harmonic_analysis_of_single_excitation(
        self: "CastSelf",
    ) -> "_6568.KlingelnbergCycloPalloidConicalGearMeshCompoundHarmonicAnalysisOfSingleExcitation":
        from mastapy._private.system_model.analyses_and_results.harmonic_analyses_single_excitation.compound import (
            _6568,
        )

        return self.__parent__._cast(
            _6568.KlingelnbergCycloPalloidConicalGearMeshCompoundHarmonicAnalysisOfSingleExcitation
        )

    @property
    def klingelnberg_cyclo_palloid_hypoid_gear_mesh_compound_harmonic_analysis_of_single_excitation(
        self: "CastSelf",
    ) -> "_6571.KlingelnbergCycloPalloidHypoidGearMeshCompoundHarmonicAnalysisOfSingleExcitation":
        from mastapy._private.system_model.analyses_and_results.harmonic_analyses_single_excitation.compound import (
            _6571,
        )

        return self.__parent__._cast(
            _6571.KlingelnbergCycloPalloidHypoidGearMeshCompoundHarmonicAnalysisOfSingleExcitation
        )

    @property
    def klingelnberg_cyclo_palloid_spiral_bevel_gear_mesh_compound_harmonic_analysis_of_single_excitation(
        self: "CastSelf",
    ) -> "_6574.KlingelnbergCycloPalloidSpiralBevelGearMeshCompoundHarmonicAnalysisOfSingleExcitation":
        from mastapy._private.system_model.analyses_and_results.harmonic_analyses_single_excitation.compound import (
            _6574,
        )

        return self.__parent__._cast(
            _6574.KlingelnbergCycloPalloidSpiralBevelGearMeshCompoundHarmonicAnalysisOfSingleExcitation
        )

    @property
    def part_to_part_shear_coupling_connection_compound_harmonic_analysis_of_single_excitation(
        self: "CastSelf",
    ) -> "_6584.PartToPartShearCouplingConnectionCompoundHarmonicAnalysisOfSingleExcitation":
        from mastapy._private.system_model.analyses_and_results.harmonic_analyses_single_excitation.compound import (
            _6584,
        )

        return self.__parent__._cast(
            _6584.PartToPartShearCouplingConnectionCompoundHarmonicAnalysisOfSingleExcitation
        )

    @property
    def planetary_connection_compound_harmonic_analysis_of_single_excitation(
        self: "CastSelf",
    ) -> "_6586.PlanetaryConnectionCompoundHarmonicAnalysisOfSingleExcitation":
        from mastapy._private.system_model.analyses_and_results.harmonic_analyses_single_excitation.compound import (
            _6586,
        )

        return self.__parent__._cast(
            _6586.PlanetaryConnectionCompoundHarmonicAnalysisOfSingleExcitation
        )

    @property
    def ring_pins_to_disc_connection_compound_harmonic_analysis_of_single_excitation(
        self: "CastSelf",
    ) -> "_6593.RingPinsToDiscConnectionCompoundHarmonicAnalysisOfSingleExcitation":
        from mastapy._private.system_model.analyses_and_results.harmonic_analyses_single_excitation.compound import (
            _6593,
        )

        return self.__parent__._cast(
            _6593.RingPinsToDiscConnectionCompoundHarmonicAnalysisOfSingleExcitation
        )

    @property
    def rolling_ring_connection_compound_harmonic_analysis_of_single_excitation(
        self: "CastSelf",
    ) -> "_6596.RollingRingConnectionCompoundHarmonicAnalysisOfSingleExcitation":
        from mastapy._private.system_model.analyses_and_results.harmonic_analyses_single_excitation.compound import (
            _6596,
        )

        return self.__parent__._cast(
            _6596.RollingRingConnectionCompoundHarmonicAnalysisOfSingleExcitation
        )

    @property
    def shaft_to_mountable_component_connection_compound_harmonic_analysis_of_single_excitation(
        self: "CastSelf",
    ) -> "_6600.ShaftToMountableComponentConnectionCompoundHarmonicAnalysisOfSingleExcitation":
        from mastapy._private.system_model.analyses_and_results.harmonic_analyses_single_excitation.compound import (
            _6600,
        )

        return self.__parent__._cast(
            _6600.ShaftToMountableComponentConnectionCompoundHarmonicAnalysisOfSingleExcitation
        )

    @property
    def spiral_bevel_gear_mesh_compound_harmonic_analysis_of_single_excitation(
        self: "CastSelf",
    ) -> "_6603.SpiralBevelGearMeshCompoundHarmonicAnalysisOfSingleExcitation":
        from mastapy._private.system_model.analyses_and_results.harmonic_analyses_single_excitation.compound import (
            _6603,
        )

        return self.__parent__._cast(
            _6603.SpiralBevelGearMeshCompoundHarmonicAnalysisOfSingleExcitation
        )

    @property
    def spring_damper_connection_compound_harmonic_analysis_of_single_excitation(
        self: "CastSelf",
    ) -> "_6606.SpringDamperConnectionCompoundHarmonicAnalysisOfSingleExcitation":
        from mastapy._private.system_model.analyses_and_results.harmonic_analyses_single_excitation.compound import (
            _6606,
        )

        return self.__parent__._cast(
            _6606.SpringDamperConnectionCompoundHarmonicAnalysisOfSingleExcitation
        )

    @property
    def straight_bevel_diff_gear_mesh_compound_harmonic_analysis_of_single_excitation(
        self: "CastSelf",
    ) -> "_6609.StraightBevelDiffGearMeshCompoundHarmonicAnalysisOfSingleExcitation":
        from mastapy._private.system_model.analyses_and_results.harmonic_analyses_single_excitation.compound import (
            _6609,
        )

        return self.__parent__._cast(
            _6609.StraightBevelDiffGearMeshCompoundHarmonicAnalysisOfSingleExcitation
        )

    @property
    def straight_bevel_gear_mesh_compound_harmonic_analysis_of_single_excitation(
        self: "CastSelf",
    ) -> "_6612.StraightBevelGearMeshCompoundHarmonicAnalysisOfSingleExcitation":
        from mastapy._private.system_model.analyses_and_results.harmonic_analyses_single_excitation.compound import (
            _6612,
        )

        return self.__parent__._cast(
            _6612.StraightBevelGearMeshCompoundHarmonicAnalysisOfSingleExcitation
        )

    @property
    def torque_converter_connection_compound_harmonic_analysis_of_single_excitation(
        self: "CastSelf",
    ) -> "_6621.TorqueConverterConnectionCompoundHarmonicAnalysisOfSingleExcitation":
        from mastapy._private.system_model.analyses_and_results.harmonic_analyses_single_excitation.compound import (
            _6621,
        )

        return self.__parent__._cast(
            _6621.TorqueConverterConnectionCompoundHarmonicAnalysisOfSingleExcitation
        )

    @property
    def worm_gear_mesh_compound_harmonic_analysis_of_single_excitation(
        self: "CastSelf",
    ) -> "_6627.WormGearMeshCompoundHarmonicAnalysisOfSingleExcitation":
        from mastapy._private.system_model.analyses_and_results.harmonic_analyses_single_excitation.compound import (
            _6627,
        )

        return self.__parent__._cast(
            _6627.WormGearMeshCompoundHarmonicAnalysisOfSingleExcitation
        )

    @property
    def zerol_bevel_gear_mesh_compound_harmonic_analysis_of_single_excitation(
        self: "CastSelf",
    ) -> "_6630.ZerolBevelGearMeshCompoundHarmonicAnalysisOfSingleExcitation":
        from mastapy._private.system_model.analyses_and_results.harmonic_analyses_single_excitation.compound import (
            _6630,
        )

        return self.__parent__._cast(
            _6630.ZerolBevelGearMeshCompoundHarmonicAnalysisOfSingleExcitation
        )

    @property
    def connection_compound_harmonic_analysis_of_single_excitation(
        self: "CastSelf",
    ) -> "ConnectionCompoundHarmonicAnalysisOfSingleExcitation":
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
class ConnectionCompoundHarmonicAnalysisOfSingleExcitation(
    _7935.ConnectionCompoundAnalysis
):
    """ConnectionCompoundHarmonicAnalysisOfSingleExcitation

    This is a mastapy class.
    """

    TYPE: ClassVar["Type"] = _CONNECTION_COMPOUND_HARMONIC_ANALYSIS_OF_SINGLE_EXCITATION

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
    ) -> "List[_6403.ConnectionHarmonicAnalysisOfSingleExcitation]":
        """List[mastapy.system_model.analyses_and_results.harmonic_analyses_single_excitation.ConnectionHarmonicAnalysisOfSingleExcitation]

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
    ) -> "List[_6403.ConnectionHarmonicAnalysisOfSingleExcitation]":
        """List[mastapy.system_model.analyses_and_results.harmonic_analyses_single_excitation.ConnectionHarmonicAnalysisOfSingleExcitation]

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
    def cast_to(
        self: "Self",
    ) -> "_Cast_ConnectionCompoundHarmonicAnalysisOfSingleExcitation":
        """Cast to another type.

        Returns:
            _Cast_ConnectionCompoundHarmonicAnalysisOfSingleExcitation
        """
        return _Cast_ConnectionCompoundHarmonicAnalysisOfSingleExcitation(self)
