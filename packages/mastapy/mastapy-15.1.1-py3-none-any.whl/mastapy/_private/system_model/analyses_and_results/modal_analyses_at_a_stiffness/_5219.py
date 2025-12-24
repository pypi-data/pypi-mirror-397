"""ConnectionModalAnalysisAtAStiffness"""

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

_CONNECTION_MODAL_ANALYSIS_AT_A_STIFFNESS = python_net_import(
    "SMT.MastaAPI.SystemModel.AnalysesAndResults.ModalAnalysesAtAStiffness",
    "ConnectionModalAnalysisAtAStiffness",
)

if TYPE_CHECKING:
    from typing import Any, Type, TypeVar

    from mastapy._private.system_model.analyses_and_results import _2941, _2943, _2945
    from mastapy._private.system_model.analyses_and_results.analysis_cases import _7934
    from mastapy._private.system_model.analyses_and_results.modal_analyses_at_a_stiffness import (
        _5187,
        _5188,
        _5193,
        _5195,
        _5200,
        _5205,
        _5208,
        _5210,
        _5213,
        _5216,
        _5221,
        _5224,
        _5228,
        _5230,
        _5231,
        _5238,
        _5243,
        _5247,
        _5250,
        _5251,
        _5254,
        _5257,
        _5264,
        _5268,
        _5271,
        _5278,
        _5280,
        _5285,
        _5287,
        _5290,
        _5293,
        _5296,
        _5305,
        _5311,
        _5314,
    )
    from mastapy._private.system_model.connections_and_sockets import _2531

    Self = TypeVar("Self", bound="ConnectionModalAnalysisAtAStiffness")
    CastSelf = TypeVar(
        "CastSelf",
        bound="ConnectionModalAnalysisAtAStiffness._Cast_ConnectionModalAnalysisAtAStiffness",
    )


__docformat__ = "restructuredtext en"
__all__ = ("ConnectionModalAnalysisAtAStiffness",)


@extended_dataclass(frozen=True, slots=True, weakref_slot=True)
class _Cast_ConnectionModalAnalysisAtAStiffness:
    """Special nested class for casting ConnectionModalAnalysisAtAStiffness to subclasses."""

    __parent__: "ConnectionModalAnalysisAtAStiffness"

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
    def abstract_shaft_to_mountable_component_connection_modal_analysis_at_a_stiffness(
        self: "CastSelf",
    ) -> "_5187.AbstractShaftToMountableComponentConnectionModalAnalysisAtAStiffness":
        from mastapy._private.system_model.analyses_and_results.modal_analyses_at_a_stiffness import (
            _5187,
        )

        return self.__parent__._cast(
            _5187.AbstractShaftToMountableComponentConnectionModalAnalysisAtAStiffness
        )

    @property
    def agma_gleason_conical_gear_mesh_modal_analysis_at_a_stiffness(
        self: "CastSelf",
    ) -> "_5188.AGMAGleasonConicalGearMeshModalAnalysisAtAStiffness":
        from mastapy._private.system_model.analyses_and_results.modal_analyses_at_a_stiffness import (
            _5188,
        )

        return self.__parent__._cast(
            _5188.AGMAGleasonConicalGearMeshModalAnalysisAtAStiffness
        )

    @property
    def belt_connection_modal_analysis_at_a_stiffness(
        self: "CastSelf",
    ) -> "_5193.BeltConnectionModalAnalysisAtAStiffness":
        from mastapy._private.system_model.analyses_and_results.modal_analyses_at_a_stiffness import (
            _5193,
        )

        return self.__parent__._cast(_5193.BeltConnectionModalAnalysisAtAStiffness)

    @property
    def bevel_differential_gear_mesh_modal_analysis_at_a_stiffness(
        self: "CastSelf",
    ) -> "_5195.BevelDifferentialGearMeshModalAnalysisAtAStiffness":
        from mastapy._private.system_model.analyses_and_results.modal_analyses_at_a_stiffness import (
            _5195,
        )

        return self.__parent__._cast(
            _5195.BevelDifferentialGearMeshModalAnalysisAtAStiffness
        )

    @property
    def bevel_gear_mesh_modal_analysis_at_a_stiffness(
        self: "CastSelf",
    ) -> "_5200.BevelGearMeshModalAnalysisAtAStiffness":
        from mastapy._private.system_model.analyses_and_results.modal_analyses_at_a_stiffness import (
            _5200,
        )

        return self.__parent__._cast(_5200.BevelGearMeshModalAnalysisAtAStiffness)

    @property
    def clutch_connection_modal_analysis_at_a_stiffness(
        self: "CastSelf",
    ) -> "_5205.ClutchConnectionModalAnalysisAtAStiffness":
        from mastapy._private.system_model.analyses_and_results.modal_analyses_at_a_stiffness import (
            _5205,
        )

        return self.__parent__._cast(_5205.ClutchConnectionModalAnalysisAtAStiffness)

    @property
    def coaxial_connection_modal_analysis_at_a_stiffness(
        self: "CastSelf",
    ) -> "_5208.CoaxialConnectionModalAnalysisAtAStiffness":
        from mastapy._private.system_model.analyses_and_results.modal_analyses_at_a_stiffness import (
            _5208,
        )

        return self.__parent__._cast(_5208.CoaxialConnectionModalAnalysisAtAStiffness)

    @property
    def concept_coupling_connection_modal_analysis_at_a_stiffness(
        self: "CastSelf",
    ) -> "_5210.ConceptCouplingConnectionModalAnalysisAtAStiffness":
        from mastapy._private.system_model.analyses_and_results.modal_analyses_at_a_stiffness import (
            _5210,
        )

        return self.__parent__._cast(
            _5210.ConceptCouplingConnectionModalAnalysisAtAStiffness
        )

    @property
    def concept_gear_mesh_modal_analysis_at_a_stiffness(
        self: "CastSelf",
    ) -> "_5213.ConceptGearMeshModalAnalysisAtAStiffness":
        from mastapy._private.system_model.analyses_and_results.modal_analyses_at_a_stiffness import (
            _5213,
        )

        return self.__parent__._cast(_5213.ConceptGearMeshModalAnalysisAtAStiffness)

    @property
    def conical_gear_mesh_modal_analysis_at_a_stiffness(
        self: "CastSelf",
    ) -> "_5216.ConicalGearMeshModalAnalysisAtAStiffness":
        from mastapy._private.system_model.analyses_and_results.modal_analyses_at_a_stiffness import (
            _5216,
        )

        return self.__parent__._cast(_5216.ConicalGearMeshModalAnalysisAtAStiffness)

    @property
    def coupling_connection_modal_analysis_at_a_stiffness(
        self: "CastSelf",
    ) -> "_5221.CouplingConnectionModalAnalysisAtAStiffness":
        from mastapy._private.system_model.analyses_and_results.modal_analyses_at_a_stiffness import (
            _5221,
        )

        return self.__parent__._cast(_5221.CouplingConnectionModalAnalysisAtAStiffness)

    @property
    def cvt_belt_connection_modal_analysis_at_a_stiffness(
        self: "CastSelf",
    ) -> "_5224.CVTBeltConnectionModalAnalysisAtAStiffness":
        from mastapy._private.system_model.analyses_and_results.modal_analyses_at_a_stiffness import (
            _5224,
        )

        return self.__parent__._cast(_5224.CVTBeltConnectionModalAnalysisAtAStiffness)

    @property
    def cycloidal_disc_central_bearing_connection_modal_analysis_at_a_stiffness(
        self: "CastSelf",
    ) -> "_5228.CycloidalDiscCentralBearingConnectionModalAnalysisAtAStiffness":
        from mastapy._private.system_model.analyses_and_results.modal_analyses_at_a_stiffness import (
            _5228,
        )

        return self.__parent__._cast(
            _5228.CycloidalDiscCentralBearingConnectionModalAnalysisAtAStiffness
        )

    @property
    def cycloidal_disc_planetary_bearing_connection_modal_analysis_at_a_stiffness(
        self: "CastSelf",
    ) -> "_5230.CycloidalDiscPlanetaryBearingConnectionModalAnalysisAtAStiffness":
        from mastapy._private.system_model.analyses_and_results.modal_analyses_at_a_stiffness import (
            _5230,
        )

        return self.__parent__._cast(
            _5230.CycloidalDiscPlanetaryBearingConnectionModalAnalysisAtAStiffness
        )

    @property
    def cylindrical_gear_mesh_modal_analysis_at_a_stiffness(
        self: "CastSelf",
    ) -> "_5231.CylindricalGearMeshModalAnalysisAtAStiffness":
        from mastapy._private.system_model.analyses_and_results.modal_analyses_at_a_stiffness import (
            _5231,
        )

        return self.__parent__._cast(_5231.CylindricalGearMeshModalAnalysisAtAStiffness)

    @property
    def face_gear_mesh_modal_analysis_at_a_stiffness(
        self: "CastSelf",
    ) -> "_5238.FaceGearMeshModalAnalysisAtAStiffness":
        from mastapy._private.system_model.analyses_and_results.modal_analyses_at_a_stiffness import (
            _5238,
        )

        return self.__parent__._cast(_5238.FaceGearMeshModalAnalysisAtAStiffness)

    @property
    def gear_mesh_modal_analysis_at_a_stiffness(
        self: "CastSelf",
    ) -> "_5243.GearMeshModalAnalysisAtAStiffness":
        from mastapy._private.system_model.analyses_and_results.modal_analyses_at_a_stiffness import (
            _5243,
        )

        return self.__parent__._cast(_5243.GearMeshModalAnalysisAtAStiffness)

    @property
    def hypoid_gear_mesh_modal_analysis_at_a_stiffness(
        self: "CastSelf",
    ) -> "_5247.HypoidGearMeshModalAnalysisAtAStiffness":
        from mastapy._private.system_model.analyses_and_results.modal_analyses_at_a_stiffness import (
            _5247,
        )

        return self.__parent__._cast(_5247.HypoidGearMeshModalAnalysisAtAStiffness)

    @property
    def inter_mountable_component_connection_modal_analysis_at_a_stiffness(
        self: "CastSelf",
    ) -> "_5250.InterMountableComponentConnectionModalAnalysisAtAStiffness":
        from mastapy._private.system_model.analyses_and_results.modal_analyses_at_a_stiffness import (
            _5250,
        )

        return self.__parent__._cast(
            _5250.InterMountableComponentConnectionModalAnalysisAtAStiffness
        )

    @property
    def klingelnberg_cyclo_palloid_conical_gear_mesh_modal_analysis_at_a_stiffness(
        self: "CastSelf",
    ) -> "_5251.KlingelnbergCycloPalloidConicalGearMeshModalAnalysisAtAStiffness":
        from mastapy._private.system_model.analyses_and_results.modal_analyses_at_a_stiffness import (
            _5251,
        )

        return self.__parent__._cast(
            _5251.KlingelnbergCycloPalloidConicalGearMeshModalAnalysisAtAStiffness
        )

    @property
    def klingelnberg_cyclo_palloid_hypoid_gear_mesh_modal_analysis_at_a_stiffness(
        self: "CastSelf",
    ) -> "_5254.KlingelnbergCycloPalloidHypoidGearMeshModalAnalysisAtAStiffness":
        from mastapy._private.system_model.analyses_and_results.modal_analyses_at_a_stiffness import (
            _5254,
        )

        return self.__parent__._cast(
            _5254.KlingelnbergCycloPalloidHypoidGearMeshModalAnalysisAtAStiffness
        )

    @property
    def klingelnberg_cyclo_palloid_spiral_bevel_gear_mesh_modal_analysis_at_a_stiffness(
        self: "CastSelf",
    ) -> "_5257.KlingelnbergCycloPalloidSpiralBevelGearMeshModalAnalysisAtAStiffness":
        from mastapy._private.system_model.analyses_and_results.modal_analyses_at_a_stiffness import (
            _5257,
        )

        return self.__parent__._cast(
            _5257.KlingelnbergCycloPalloidSpiralBevelGearMeshModalAnalysisAtAStiffness
        )

    @property
    def part_to_part_shear_coupling_connection_modal_analysis_at_a_stiffness(
        self: "CastSelf",
    ) -> "_5268.PartToPartShearCouplingConnectionModalAnalysisAtAStiffness":
        from mastapy._private.system_model.analyses_and_results.modal_analyses_at_a_stiffness import (
            _5268,
        )

        return self.__parent__._cast(
            _5268.PartToPartShearCouplingConnectionModalAnalysisAtAStiffness
        )

    @property
    def planetary_connection_modal_analysis_at_a_stiffness(
        self: "CastSelf",
    ) -> "_5271.PlanetaryConnectionModalAnalysisAtAStiffness":
        from mastapy._private.system_model.analyses_and_results.modal_analyses_at_a_stiffness import (
            _5271,
        )

        return self.__parent__._cast(_5271.PlanetaryConnectionModalAnalysisAtAStiffness)

    @property
    def ring_pins_to_disc_connection_modal_analysis_at_a_stiffness(
        self: "CastSelf",
    ) -> "_5278.RingPinsToDiscConnectionModalAnalysisAtAStiffness":
        from mastapy._private.system_model.analyses_and_results.modal_analyses_at_a_stiffness import (
            _5278,
        )

        return self.__parent__._cast(
            _5278.RingPinsToDiscConnectionModalAnalysisAtAStiffness
        )

    @property
    def rolling_ring_connection_modal_analysis_at_a_stiffness(
        self: "CastSelf",
    ) -> "_5280.RollingRingConnectionModalAnalysisAtAStiffness":
        from mastapy._private.system_model.analyses_and_results.modal_analyses_at_a_stiffness import (
            _5280,
        )

        return self.__parent__._cast(
            _5280.RollingRingConnectionModalAnalysisAtAStiffness
        )

    @property
    def shaft_to_mountable_component_connection_modal_analysis_at_a_stiffness(
        self: "CastSelf",
    ) -> "_5285.ShaftToMountableComponentConnectionModalAnalysisAtAStiffness":
        from mastapy._private.system_model.analyses_and_results.modal_analyses_at_a_stiffness import (
            _5285,
        )

        return self.__parent__._cast(
            _5285.ShaftToMountableComponentConnectionModalAnalysisAtAStiffness
        )

    @property
    def spiral_bevel_gear_mesh_modal_analysis_at_a_stiffness(
        self: "CastSelf",
    ) -> "_5287.SpiralBevelGearMeshModalAnalysisAtAStiffness":
        from mastapy._private.system_model.analyses_and_results.modal_analyses_at_a_stiffness import (
            _5287,
        )

        return self.__parent__._cast(_5287.SpiralBevelGearMeshModalAnalysisAtAStiffness)

    @property
    def spring_damper_connection_modal_analysis_at_a_stiffness(
        self: "CastSelf",
    ) -> "_5290.SpringDamperConnectionModalAnalysisAtAStiffness":
        from mastapy._private.system_model.analyses_and_results.modal_analyses_at_a_stiffness import (
            _5290,
        )

        return self.__parent__._cast(
            _5290.SpringDamperConnectionModalAnalysisAtAStiffness
        )

    @property
    def straight_bevel_diff_gear_mesh_modal_analysis_at_a_stiffness(
        self: "CastSelf",
    ) -> "_5293.StraightBevelDiffGearMeshModalAnalysisAtAStiffness":
        from mastapy._private.system_model.analyses_and_results.modal_analyses_at_a_stiffness import (
            _5293,
        )

        return self.__parent__._cast(
            _5293.StraightBevelDiffGearMeshModalAnalysisAtAStiffness
        )

    @property
    def straight_bevel_gear_mesh_modal_analysis_at_a_stiffness(
        self: "CastSelf",
    ) -> "_5296.StraightBevelGearMeshModalAnalysisAtAStiffness":
        from mastapy._private.system_model.analyses_and_results.modal_analyses_at_a_stiffness import (
            _5296,
        )

        return self.__parent__._cast(
            _5296.StraightBevelGearMeshModalAnalysisAtAStiffness
        )

    @property
    def torque_converter_connection_modal_analysis_at_a_stiffness(
        self: "CastSelf",
    ) -> "_5305.TorqueConverterConnectionModalAnalysisAtAStiffness":
        from mastapy._private.system_model.analyses_and_results.modal_analyses_at_a_stiffness import (
            _5305,
        )

        return self.__parent__._cast(
            _5305.TorqueConverterConnectionModalAnalysisAtAStiffness
        )

    @property
    def worm_gear_mesh_modal_analysis_at_a_stiffness(
        self: "CastSelf",
    ) -> "_5311.WormGearMeshModalAnalysisAtAStiffness":
        from mastapy._private.system_model.analyses_and_results.modal_analyses_at_a_stiffness import (
            _5311,
        )

        return self.__parent__._cast(_5311.WormGearMeshModalAnalysisAtAStiffness)

    @property
    def zerol_bevel_gear_mesh_modal_analysis_at_a_stiffness(
        self: "CastSelf",
    ) -> "_5314.ZerolBevelGearMeshModalAnalysisAtAStiffness":
        from mastapy._private.system_model.analyses_and_results.modal_analyses_at_a_stiffness import (
            _5314,
        )

        return self.__parent__._cast(_5314.ZerolBevelGearMeshModalAnalysisAtAStiffness)

    @property
    def connection_modal_analysis_at_a_stiffness(
        self: "CastSelf",
    ) -> "ConnectionModalAnalysisAtAStiffness":
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
class ConnectionModalAnalysisAtAStiffness(_7937.ConnectionStaticLoadAnalysisCase):
    """ConnectionModalAnalysisAtAStiffness

    This is a mastapy class.
    """

    TYPE: ClassVar["Type"] = _CONNECTION_MODAL_ANALYSIS_AT_A_STIFFNESS

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
    def modal_analysis_at_a_stiffness(
        self: "Self",
    ) -> "_5264.ModalAnalysisAtAStiffness":
        """mastapy.system_model.analyses_and_results.modal_analyses_at_a_stiffness.ModalAnalysisAtAStiffness

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "ModalAnalysisAtAStiffness")

        if temp is None:
            return None

        type_ = temp.GetType()
        return constructor.new(type_.Namespace, type_.Name)(temp)

    @property
    def cast_to(self: "Self") -> "_Cast_ConnectionModalAnalysisAtAStiffness":
        """Cast to another type.

        Returns:
            _Cast_ConnectionModalAnalysisAtAStiffness
        """
        return _Cast_ConnectionModalAnalysisAtAStiffness(self)
