"""ConnectionHarmonicAnalysisOfSingleExcitation"""

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
from mastapy._private.system_model.analyses_and_results.analysis_cases import _7937

_CONNECTION_HARMONIC_ANALYSIS_OF_SINGLE_EXCITATION = python_net_import(
    "SMT.MastaAPI.SystemModel.AnalysesAndResults.HarmonicAnalysesSingleExcitation",
    "ConnectionHarmonicAnalysisOfSingleExcitation",
)

if TYPE_CHECKING:
    from typing import Any, Type, TypeVar

    from mastapy._private.system_model.analyses_and_results import _2941, _2943, _2945
    from mastapy._private.system_model.analyses_and_results.analysis_cases import _7934
    from mastapy._private.system_model.analyses_and_results.harmonic_analyses_single_excitation import (
        _6371,
        _6373,
        _6377,
        _6380,
        _6385,
        _6389,
        _6392,
        _6394,
        _6398,
        _6401,
        _6405,
        _6408,
        _6412,
        _6414,
        _6416,
        _6422,
        _6427,
        _6430,
        _6432,
        _6434,
        _6436,
        _6439,
        _6442,
        _6452,
        _6455,
        _6462,
        _6464,
        _6469,
        _6472,
        _6474,
        _6478,
        _6481,
        _6489,
        _6496,
        _6499,
    )
    from mastapy._private.system_model.connections_and_sockets import _2531

    Self = TypeVar("Self", bound="ConnectionHarmonicAnalysisOfSingleExcitation")
    CastSelf = TypeVar(
        "CastSelf",
        bound="ConnectionHarmonicAnalysisOfSingleExcitation._Cast_ConnectionHarmonicAnalysisOfSingleExcitation",
    )


__docformat__ = "restructuredtext en"
__all__ = ("ConnectionHarmonicAnalysisOfSingleExcitation",)


@extended_dataclass(frozen=True, slots=True, weakref_slot=True)
class _Cast_ConnectionHarmonicAnalysisOfSingleExcitation:
    """Special nested class for casting ConnectionHarmonicAnalysisOfSingleExcitation to subclasses."""

    __parent__: "ConnectionHarmonicAnalysisOfSingleExcitation"

    @property
    def connection_static_load_analysis_case(
        self: "CastSelf",
    ) -> "_7937.ConnectionStaticLoadAnalysisCase":
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
    def abstract_shaft_to_mountable_component_connection_harmonic_analysis_of_single_excitation(
        self: "CastSelf",
    ) -> "_6371.AbstractShaftToMountableComponentConnectionHarmonicAnalysisOfSingleExcitation":
        from mastapy._private.system_model.analyses_and_results.harmonic_analyses_single_excitation import (
            _6371,
        )

        return self.__parent__._cast(
            _6371.AbstractShaftToMountableComponentConnectionHarmonicAnalysisOfSingleExcitation
        )

    @property
    def agma_gleason_conical_gear_mesh_harmonic_analysis_of_single_excitation(
        self: "CastSelf",
    ) -> "_6373.AGMAGleasonConicalGearMeshHarmonicAnalysisOfSingleExcitation":
        from mastapy._private.system_model.analyses_and_results.harmonic_analyses_single_excitation import (
            _6373,
        )

        return self.__parent__._cast(
            _6373.AGMAGleasonConicalGearMeshHarmonicAnalysisOfSingleExcitation
        )

    @property
    def belt_connection_harmonic_analysis_of_single_excitation(
        self: "CastSelf",
    ) -> "_6377.BeltConnectionHarmonicAnalysisOfSingleExcitation":
        from mastapy._private.system_model.analyses_and_results.harmonic_analyses_single_excitation import (
            _6377,
        )

        return self.__parent__._cast(
            _6377.BeltConnectionHarmonicAnalysisOfSingleExcitation
        )

    @property
    def bevel_differential_gear_mesh_harmonic_analysis_of_single_excitation(
        self: "CastSelf",
    ) -> "_6380.BevelDifferentialGearMeshHarmonicAnalysisOfSingleExcitation":
        from mastapy._private.system_model.analyses_and_results.harmonic_analyses_single_excitation import (
            _6380,
        )

        return self.__parent__._cast(
            _6380.BevelDifferentialGearMeshHarmonicAnalysisOfSingleExcitation
        )

    @property
    def bevel_gear_mesh_harmonic_analysis_of_single_excitation(
        self: "CastSelf",
    ) -> "_6385.BevelGearMeshHarmonicAnalysisOfSingleExcitation":
        from mastapy._private.system_model.analyses_and_results.harmonic_analyses_single_excitation import (
            _6385,
        )

        return self.__parent__._cast(
            _6385.BevelGearMeshHarmonicAnalysisOfSingleExcitation
        )

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
    def coaxial_connection_harmonic_analysis_of_single_excitation(
        self: "CastSelf",
    ) -> "_6392.CoaxialConnectionHarmonicAnalysisOfSingleExcitation":
        from mastapy._private.system_model.analyses_and_results.harmonic_analyses_single_excitation import (
            _6392,
        )

        return self.__parent__._cast(
            _6392.CoaxialConnectionHarmonicAnalysisOfSingleExcitation
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
    def concept_gear_mesh_harmonic_analysis_of_single_excitation(
        self: "CastSelf",
    ) -> "_6398.ConceptGearMeshHarmonicAnalysisOfSingleExcitation":
        from mastapy._private.system_model.analyses_and_results.harmonic_analyses_single_excitation import (
            _6398,
        )

        return self.__parent__._cast(
            _6398.ConceptGearMeshHarmonicAnalysisOfSingleExcitation
        )

    @property
    def conical_gear_mesh_harmonic_analysis_of_single_excitation(
        self: "CastSelf",
    ) -> "_6401.ConicalGearMeshHarmonicAnalysisOfSingleExcitation":
        from mastapy._private.system_model.analyses_and_results.harmonic_analyses_single_excitation import (
            _6401,
        )

        return self.__parent__._cast(
            _6401.ConicalGearMeshHarmonicAnalysisOfSingleExcitation
        )

    @property
    def coupling_connection_harmonic_analysis_of_single_excitation(
        self: "CastSelf",
    ) -> "_6405.CouplingConnectionHarmonicAnalysisOfSingleExcitation":
        from mastapy._private.system_model.analyses_and_results.harmonic_analyses_single_excitation import (
            _6405,
        )

        return self.__parent__._cast(
            _6405.CouplingConnectionHarmonicAnalysisOfSingleExcitation
        )

    @property
    def cvt_belt_connection_harmonic_analysis_of_single_excitation(
        self: "CastSelf",
    ) -> "_6408.CVTBeltConnectionHarmonicAnalysisOfSingleExcitation":
        from mastapy._private.system_model.analyses_and_results.harmonic_analyses_single_excitation import (
            _6408,
        )

        return self.__parent__._cast(
            _6408.CVTBeltConnectionHarmonicAnalysisOfSingleExcitation
        )

    @property
    def cycloidal_disc_central_bearing_connection_harmonic_analysis_of_single_excitation(
        self: "CastSelf",
    ) -> (
        "_6412.CycloidalDiscCentralBearingConnectionHarmonicAnalysisOfSingleExcitation"
    ):
        from mastapy._private.system_model.analyses_and_results.harmonic_analyses_single_excitation import (
            _6412,
        )

        return self.__parent__._cast(
            _6412.CycloidalDiscCentralBearingConnectionHarmonicAnalysisOfSingleExcitation
        )

    @property
    def cycloidal_disc_planetary_bearing_connection_harmonic_analysis_of_single_excitation(
        self: "CastSelf",
    ) -> "_6414.CycloidalDiscPlanetaryBearingConnectionHarmonicAnalysisOfSingleExcitation":
        from mastapy._private.system_model.analyses_and_results.harmonic_analyses_single_excitation import (
            _6414,
        )

        return self.__parent__._cast(
            _6414.CycloidalDiscPlanetaryBearingConnectionHarmonicAnalysisOfSingleExcitation
        )

    @property
    def cylindrical_gear_mesh_harmonic_analysis_of_single_excitation(
        self: "CastSelf",
    ) -> "_6416.CylindricalGearMeshHarmonicAnalysisOfSingleExcitation":
        from mastapy._private.system_model.analyses_and_results.harmonic_analyses_single_excitation import (
            _6416,
        )

        return self.__parent__._cast(
            _6416.CylindricalGearMeshHarmonicAnalysisOfSingleExcitation
        )

    @property
    def face_gear_mesh_harmonic_analysis_of_single_excitation(
        self: "CastSelf",
    ) -> "_6422.FaceGearMeshHarmonicAnalysisOfSingleExcitation":
        from mastapy._private.system_model.analyses_and_results.harmonic_analyses_single_excitation import (
            _6422,
        )

        return self.__parent__._cast(
            _6422.FaceGearMeshHarmonicAnalysisOfSingleExcitation
        )

    @property
    def gear_mesh_harmonic_analysis_of_single_excitation(
        self: "CastSelf",
    ) -> "_6427.GearMeshHarmonicAnalysisOfSingleExcitation":
        from mastapy._private.system_model.analyses_and_results.harmonic_analyses_single_excitation import (
            _6427,
        )

        return self.__parent__._cast(_6427.GearMeshHarmonicAnalysisOfSingleExcitation)

    @property
    def hypoid_gear_mesh_harmonic_analysis_of_single_excitation(
        self: "CastSelf",
    ) -> "_6432.HypoidGearMeshHarmonicAnalysisOfSingleExcitation":
        from mastapy._private.system_model.analyses_and_results.harmonic_analyses_single_excitation import (
            _6432,
        )

        return self.__parent__._cast(
            _6432.HypoidGearMeshHarmonicAnalysisOfSingleExcitation
        )

    @property
    def inter_mountable_component_connection_harmonic_analysis_of_single_excitation(
        self: "CastSelf",
    ) -> "_6434.InterMountableComponentConnectionHarmonicAnalysisOfSingleExcitation":
        from mastapy._private.system_model.analyses_and_results.harmonic_analyses_single_excitation import (
            _6434,
        )

        return self.__parent__._cast(
            _6434.InterMountableComponentConnectionHarmonicAnalysisOfSingleExcitation
        )

    @property
    def klingelnberg_cyclo_palloid_conical_gear_mesh_harmonic_analysis_of_single_excitation(
        self: "CastSelf",
    ) -> "_6436.KlingelnbergCycloPalloidConicalGearMeshHarmonicAnalysisOfSingleExcitation":
        from mastapy._private.system_model.analyses_and_results.harmonic_analyses_single_excitation import (
            _6436,
        )

        return self.__parent__._cast(
            _6436.KlingelnbergCycloPalloidConicalGearMeshHarmonicAnalysisOfSingleExcitation
        )

    @property
    def klingelnberg_cyclo_palloid_hypoid_gear_mesh_harmonic_analysis_of_single_excitation(
        self: "CastSelf",
    ) -> (
        "_6439.KlingelnbergCycloPalloidHypoidGearMeshHarmonicAnalysisOfSingleExcitation"
    ):
        from mastapy._private.system_model.analyses_and_results.harmonic_analyses_single_excitation import (
            _6439,
        )

        return self.__parent__._cast(
            _6439.KlingelnbergCycloPalloidHypoidGearMeshHarmonicAnalysisOfSingleExcitation
        )

    @property
    def klingelnberg_cyclo_palloid_spiral_bevel_gear_mesh_harmonic_analysis_of_single_excitation(
        self: "CastSelf",
    ) -> "_6442.KlingelnbergCycloPalloidSpiralBevelGearMeshHarmonicAnalysisOfSingleExcitation":
        from mastapy._private.system_model.analyses_and_results.harmonic_analyses_single_excitation import (
            _6442,
        )

        return self.__parent__._cast(
            _6442.KlingelnbergCycloPalloidSpiralBevelGearMeshHarmonicAnalysisOfSingleExcitation
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
    def planetary_connection_harmonic_analysis_of_single_excitation(
        self: "CastSelf",
    ) -> "_6455.PlanetaryConnectionHarmonicAnalysisOfSingleExcitation":
        from mastapy._private.system_model.analyses_and_results.harmonic_analyses_single_excitation import (
            _6455,
        )

        return self.__parent__._cast(
            _6455.PlanetaryConnectionHarmonicAnalysisOfSingleExcitation
        )

    @property
    def ring_pins_to_disc_connection_harmonic_analysis_of_single_excitation(
        self: "CastSelf",
    ) -> "_6462.RingPinsToDiscConnectionHarmonicAnalysisOfSingleExcitation":
        from mastapy._private.system_model.analyses_and_results.harmonic_analyses_single_excitation import (
            _6462,
        )

        return self.__parent__._cast(
            _6462.RingPinsToDiscConnectionHarmonicAnalysisOfSingleExcitation
        )

    @property
    def rolling_ring_connection_harmonic_analysis_of_single_excitation(
        self: "CastSelf",
    ) -> "_6464.RollingRingConnectionHarmonicAnalysisOfSingleExcitation":
        from mastapy._private.system_model.analyses_and_results.harmonic_analyses_single_excitation import (
            _6464,
        )

        return self.__parent__._cast(
            _6464.RollingRingConnectionHarmonicAnalysisOfSingleExcitation
        )

    @property
    def shaft_to_mountable_component_connection_harmonic_analysis_of_single_excitation(
        self: "CastSelf",
    ) -> "_6469.ShaftToMountableComponentConnectionHarmonicAnalysisOfSingleExcitation":
        from mastapy._private.system_model.analyses_and_results.harmonic_analyses_single_excitation import (
            _6469,
        )

        return self.__parent__._cast(
            _6469.ShaftToMountableComponentConnectionHarmonicAnalysisOfSingleExcitation
        )

    @property
    def spiral_bevel_gear_mesh_harmonic_analysis_of_single_excitation(
        self: "CastSelf",
    ) -> "_6472.SpiralBevelGearMeshHarmonicAnalysisOfSingleExcitation":
        from mastapy._private.system_model.analyses_and_results.harmonic_analyses_single_excitation import (
            _6472,
        )

        return self.__parent__._cast(
            _6472.SpiralBevelGearMeshHarmonicAnalysisOfSingleExcitation
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
    def straight_bevel_diff_gear_mesh_harmonic_analysis_of_single_excitation(
        self: "CastSelf",
    ) -> "_6478.StraightBevelDiffGearMeshHarmonicAnalysisOfSingleExcitation":
        from mastapy._private.system_model.analyses_and_results.harmonic_analyses_single_excitation import (
            _6478,
        )

        return self.__parent__._cast(
            _6478.StraightBevelDiffGearMeshHarmonicAnalysisOfSingleExcitation
        )

    @property
    def straight_bevel_gear_mesh_harmonic_analysis_of_single_excitation(
        self: "CastSelf",
    ) -> "_6481.StraightBevelGearMeshHarmonicAnalysisOfSingleExcitation":
        from mastapy._private.system_model.analyses_and_results.harmonic_analyses_single_excitation import (
            _6481,
        )

        return self.__parent__._cast(
            _6481.StraightBevelGearMeshHarmonicAnalysisOfSingleExcitation
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
    def worm_gear_mesh_harmonic_analysis_of_single_excitation(
        self: "CastSelf",
    ) -> "_6496.WormGearMeshHarmonicAnalysisOfSingleExcitation":
        from mastapy._private.system_model.analyses_and_results.harmonic_analyses_single_excitation import (
            _6496,
        )

        return self.__parent__._cast(
            _6496.WormGearMeshHarmonicAnalysisOfSingleExcitation
        )

    @property
    def zerol_bevel_gear_mesh_harmonic_analysis_of_single_excitation(
        self: "CastSelf",
    ) -> "_6499.ZerolBevelGearMeshHarmonicAnalysisOfSingleExcitation":
        from mastapy._private.system_model.analyses_and_results.harmonic_analyses_single_excitation import (
            _6499,
        )

        return self.__parent__._cast(
            _6499.ZerolBevelGearMeshHarmonicAnalysisOfSingleExcitation
        )

    @property
    def connection_harmonic_analysis_of_single_excitation(
        self: "CastSelf",
    ) -> "ConnectionHarmonicAnalysisOfSingleExcitation":
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
class ConnectionHarmonicAnalysisOfSingleExcitation(
    _7937.ConnectionStaticLoadAnalysisCase
):
    """ConnectionHarmonicAnalysisOfSingleExcitation

    This is a mastapy class.
    """

    TYPE: ClassVar["Type"] = _CONNECTION_HARMONIC_ANALYSIS_OF_SINGLE_EXCITATION

    wrapped: "Any"

    def __post_init__(self: "Self") -> None:
        """Override of the post initialisation magic method."""
        if not hasattr(self.wrapped, "reference_count"):
            self.wrapped.reference_count = 0

        self.wrapped.reference_count += 1

    @property
    @exception_bridge
    def component_design(self: "Self") -> "_2531.Connection":
        """mastapy.system_model.connections_and_sockets.Connection

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
    def connection_design(self: "Self") -> "_2531.Connection":
        """mastapy.system_model.connections_and_sockets.Connection

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "ConnectionDesign")

        if temp is None:
            return None

        type_ = temp.GetType()
        return constructor.new(type_.Namespace, type_.Name)(temp)

    @property
    @exception_bridge
    def harmonic_analysis_of_single_excitation(
        self: "Self",
    ) -> "_6430.HarmonicAnalysisOfSingleExcitation":
        """mastapy.system_model.analyses_and_results.harmonic_analyses_single_excitation.HarmonicAnalysisOfSingleExcitation

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(
            self.wrapped, "HarmonicAnalysisOfSingleExcitation"
        )

        if temp is None:
            return None

        type_ = temp.GetType()
        return constructor.new(type_.Namespace, type_.Name)(temp)

    @property
    def cast_to(self: "Self") -> "_Cast_ConnectionHarmonicAnalysisOfSingleExcitation":
        """Cast to another type.

        Returns:
            _Cast_ConnectionHarmonicAnalysisOfSingleExcitation
        """
        return _Cast_ConnectionHarmonicAnalysisOfSingleExcitation(self)
