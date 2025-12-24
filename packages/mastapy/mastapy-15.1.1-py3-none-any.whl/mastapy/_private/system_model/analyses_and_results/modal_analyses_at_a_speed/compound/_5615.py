"""ConnectionCompoundModalAnalysisAtASpeed"""

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

_CONNECTION_COMPOUND_MODAL_ANALYSIS_AT_A_SPEED = python_net_import(
    "SMT.MastaAPI.SystemModel.AnalysesAndResults.ModalAnalysesAtASpeed.Compound",
    "ConnectionCompoundModalAnalysisAtASpeed",
)

if TYPE_CHECKING:
    from typing import Any, List, Type, TypeVar

    from mastapy._private.system_model.analyses_and_results import _2943
    from mastapy._private.system_model.analyses_and_results.analysis_cases import _7939
    from mastapy._private.system_model.analyses_and_results.modal_analyses_at_a_speed import (
        _5483,
    )
    from mastapy._private.system_model.analyses_and_results.modal_analyses_at_a_speed.compound import (
        _5583,
        _5585,
        _5589,
        _5592,
        _5597,
        _5602,
        _5604,
        _5607,
        _5610,
        _5613,
        _5618,
        _5620,
        _5624,
        _5626,
        _5628,
        _5634,
        _5639,
        _5643,
        _5645,
        _5647,
        _5650,
        _5653,
        _5663,
        _5665,
        _5672,
        _5675,
        _5679,
        _5682,
        _5685,
        _5688,
        _5691,
        _5700,
        _5706,
        _5709,
    )

    Self = TypeVar("Self", bound="ConnectionCompoundModalAnalysisAtASpeed")
    CastSelf = TypeVar(
        "CastSelf",
        bound="ConnectionCompoundModalAnalysisAtASpeed._Cast_ConnectionCompoundModalAnalysisAtASpeed",
    )


__docformat__ = "restructuredtext en"
__all__ = ("ConnectionCompoundModalAnalysisAtASpeed",)


@extended_dataclass(frozen=True, slots=True, weakref_slot=True)
class _Cast_ConnectionCompoundModalAnalysisAtASpeed:
    """Special nested class for casting ConnectionCompoundModalAnalysisAtASpeed to subclasses."""

    __parent__: "ConnectionCompoundModalAnalysisAtASpeed"

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
    def abstract_shaft_to_mountable_component_connection_compound_modal_analysis_at_a_speed(
        self: "CastSelf",
    ) -> (
        "_5583.AbstractShaftToMountableComponentConnectionCompoundModalAnalysisAtASpeed"
    ):
        from mastapy._private.system_model.analyses_and_results.modal_analyses_at_a_speed.compound import (
            _5583,
        )

        return self.__parent__._cast(
            _5583.AbstractShaftToMountableComponentConnectionCompoundModalAnalysisAtASpeed
        )

    @property
    def agma_gleason_conical_gear_mesh_compound_modal_analysis_at_a_speed(
        self: "CastSelf",
    ) -> "_5585.AGMAGleasonConicalGearMeshCompoundModalAnalysisAtASpeed":
        from mastapy._private.system_model.analyses_and_results.modal_analyses_at_a_speed.compound import (
            _5585,
        )

        return self.__parent__._cast(
            _5585.AGMAGleasonConicalGearMeshCompoundModalAnalysisAtASpeed
        )

    @property
    def belt_connection_compound_modal_analysis_at_a_speed(
        self: "CastSelf",
    ) -> "_5589.BeltConnectionCompoundModalAnalysisAtASpeed":
        from mastapy._private.system_model.analyses_and_results.modal_analyses_at_a_speed.compound import (
            _5589,
        )

        return self.__parent__._cast(_5589.BeltConnectionCompoundModalAnalysisAtASpeed)

    @property
    def bevel_differential_gear_mesh_compound_modal_analysis_at_a_speed(
        self: "CastSelf",
    ) -> "_5592.BevelDifferentialGearMeshCompoundModalAnalysisAtASpeed":
        from mastapy._private.system_model.analyses_and_results.modal_analyses_at_a_speed.compound import (
            _5592,
        )

        return self.__parent__._cast(
            _5592.BevelDifferentialGearMeshCompoundModalAnalysisAtASpeed
        )

    @property
    def bevel_gear_mesh_compound_modal_analysis_at_a_speed(
        self: "CastSelf",
    ) -> "_5597.BevelGearMeshCompoundModalAnalysisAtASpeed":
        from mastapy._private.system_model.analyses_and_results.modal_analyses_at_a_speed.compound import (
            _5597,
        )

        return self.__parent__._cast(_5597.BevelGearMeshCompoundModalAnalysisAtASpeed)

    @property
    def clutch_connection_compound_modal_analysis_at_a_speed(
        self: "CastSelf",
    ) -> "_5602.ClutchConnectionCompoundModalAnalysisAtASpeed":
        from mastapy._private.system_model.analyses_and_results.modal_analyses_at_a_speed.compound import (
            _5602,
        )

        return self.__parent__._cast(
            _5602.ClutchConnectionCompoundModalAnalysisAtASpeed
        )

    @property
    def coaxial_connection_compound_modal_analysis_at_a_speed(
        self: "CastSelf",
    ) -> "_5604.CoaxialConnectionCompoundModalAnalysisAtASpeed":
        from mastapy._private.system_model.analyses_and_results.modal_analyses_at_a_speed.compound import (
            _5604,
        )

        return self.__parent__._cast(
            _5604.CoaxialConnectionCompoundModalAnalysisAtASpeed
        )

    @property
    def concept_coupling_connection_compound_modal_analysis_at_a_speed(
        self: "CastSelf",
    ) -> "_5607.ConceptCouplingConnectionCompoundModalAnalysisAtASpeed":
        from mastapy._private.system_model.analyses_and_results.modal_analyses_at_a_speed.compound import (
            _5607,
        )

        return self.__parent__._cast(
            _5607.ConceptCouplingConnectionCompoundModalAnalysisAtASpeed
        )

    @property
    def concept_gear_mesh_compound_modal_analysis_at_a_speed(
        self: "CastSelf",
    ) -> "_5610.ConceptGearMeshCompoundModalAnalysisAtASpeed":
        from mastapy._private.system_model.analyses_and_results.modal_analyses_at_a_speed.compound import (
            _5610,
        )

        return self.__parent__._cast(_5610.ConceptGearMeshCompoundModalAnalysisAtASpeed)

    @property
    def conical_gear_mesh_compound_modal_analysis_at_a_speed(
        self: "CastSelf",
    ) -> "_5613.ConicalGearMeshCompoundModalAnalysisAtASpeed":
        from mastapy._private.system_model.analyses_and_results.modal_analyses_at_a_speed.compound import (
            _5613,
        )

        return self.__parent__._cast(_5613.ConicalGearMeshCompoundModalAnalysisAtASpeed)

    @property
    def coupling_connection_compound_modal_analysis_at_a_speed(
        self: "CastSelf",
    ) -> "_5618.CouplingConnectionCompoundModalAnalysisAtASpeed":
        from mastapy._private.system_model.analyses_and_results.modal_analyses_at_a_speed.compound import (
            _5618,
        )

        return self.__parent__._cast(
            _5618.CouplingConnectionCompoundModalAnalysisAtASpeed
        )

    @property
    def cvt_belt_connection_compound_modal_analysis_at_a_speed(
        self: "CastSelf",
    ) -> "_5620.CVTBeltConnectionCompoundModalAnalysisAtASpeed":
        from mastapy._private.system_model.analyses_and_results.modal_analyses_at_a_speed.compound import (
            _5620,
        )

        return self.__parent__._cast(
            _5620.CVTBeltConnectionCompoundModalAnalysisAtASpeed
        )

    @property
    def cycloidal_disc_central_bearing_connection_compound_modal_analysis_at_a_speed(
        self: "CastSelf",
    ) -> "_5624.CycloidalDiscCentralBearingConnectionCompoundModalAnalysisAtASpeed":
        from mastapy._private.system_model.analyses_and_results.modal_analyses_at_a_speed.compound import (
            _5624,
        )

        return self.__parent__._cast(
            _5624.CycloidalDiscCentralBearingConnectionCompoundModalAnalysisAtASpeed
        )

    @property
    def cycloidal_disc_planetary_bearing_connection_compound_modal_analysis_at_a_speed(
        self: "CastSelf",
    ) -> "_5626.CycloidalDiscPlanetaryBearingConnectionCompoundModalAnalysisAtASpeed":
        from mastapy._private.system_model.analyses_and_results.modal_analyses_at_a_speed.compound import (
            _5626,
        )

        return self.__parent__._cast(
            _5626.CycloidalDiscPlanetaryBearingConnectionCompoundModalAnalysisAtASpeed
        )

    @property
    def cylindrical_gear_mesh_compound_modal_analysis_at_a_speed(
        self: "CastSelf",
    ) -> "_5628.CylindricalGearMeshCompoundModalAnalysisAtASpeed":
        from mastapy._private.system_model.analyses_and_results.modal_analyses_at_a_speed.compound import (
            _5628,
        )

        return self.__parent__._cast(
            _5628.CylindricalGearMeshCompoundModalAnalysisAtASpeed
        )

    @property
    def face_gear_mesh_compound_modal_analysis_at_a_speed(
        self: "CastSelf",
    ) -> "_5634.FaceGearMeshCompoundModalAnalysisAtASpeed":
        from mastapy._private.system_model.analyses_and_results.modal_analyses_at_a_speed.compound import (
            _5634,
        )

        return self.__parent__._cast(_5634.FaceGearMeshCompoundModalAnalysisAtASpeed)

    @property
    def gear_mesh_compound_modal_analysis_at_a_speed(
        self: "CastSelf",
    ) -> "_5639.GearMeshCompoundModalAnalysisAtASpeed":
        from mastapy._private.system_model.analyses_and_results.modal_analyses_at_a_speed.compound import (
            _5639,
        )

        return self.__parent__._cast(_5639.GearMeshCompoundModalAnalysisAtASpeed)

    @property
    def hypoid_gear_mesh_compound_modal_analysis_at_a_speed(
        self: "CastSelf",
    ) -> "_5643.HypoidGearMeshCompoundModalAnalysisAtASpeed":
        from mastapy._private.system_model.analyses_and_results.modal_analyses_at_a_speed.compound import (
            _5643,
        )

        return self.__parent__._cast(_5643.HypoidGearMeshCompoundModalAnalysisAtASpeed)

    @property
    def inter_mountable_component_connection_compound_modal_analysis_at_a_speed(
        self: "CastSelf",
    ) -> "_5645.InterMountableComponentConnectionCompoundModalAnalysisAtASpeed":
        from mastapy._private.system_model.analyses_and_results.modal_analyses_at_a_speed.compound import (
            _5645,
        )

        return self.__parent__._cast(
            _5645.InterMountableComponentConnectionCompoundModalAnalysisAtASpeed
        )

    @property
    def klingelnberg_cyclo_palloid_conical_gear_mesh_compound_modal_analysis_at_a_speed(
        self: "CastSelf",
    ) -> "_5647.KlingelnbergCycloPalloidConicalGearMeshCompoundModalAnalysisAtASpeed":
        from mastapy._private.system_model.analyses_and_results.modal_analyses_at_a_speed.compound import (
            _5647,
        )

        return self.__parent__._cast(
            _5647.KlingelnbergCycloPalloidConicalGearMeshCompoundModalAnalysisAtASpeed
        )

    @property
    def klingelnberg_cyclo_palloid_hypoid_gear_mesh_compound_modal_analysis_at_a_speed(
        self: "CastSelf",
    ) -> "_5650.KlingelnbergCycloPalloidHypoidGearMeshCompoundModalAnalysisAtASpeed":
        from mastapy._private.system_model.analyses_and_results.modal_analyses_at_a_speed.compound import (
            _5650,
        )

        return self.__parent__._cast(
            _5650.KlingelnbergCycloPalloidHypoidGearMeshCompoundModalAnalysisAtASpeed
        )

    @property
    def klingelnberg_cyclo_palloid_spiral_bevel_gear_mesh_compound_modal_analysis_at_a_speed(
        self: "CastSelf",
    ) -> (
        "_5653.KlingelnbergCycloPalloidSpiralBevelGearMeshCompoundModalAnalysisAtASpeed"
    ):
        from mastapy._private.system_model.analyses_and_results.modal_analyses_at_a_speed.compound import (
            _5653,
        )

        return self.__parent__._cast(
            _5653.KlingelnbergCycloPalloidSpiralBevelGearMeshCompoundModalAnalysisAtASpeed
        )

    @property
    def part_to_part_shear_coupling_connection_compound_modal_analysis_at_a_speed(
        self: "CastSelf",
    ) -> "_5663.PartToPartShearCouplingConnectionCompoundModalAnalysisAtASpeed":
        from mastapy._private.system_model.analyses_and_results.modal_analyses_at_a_speed.compound import (
            _5663,
        )

        return self.__parent__._cast(
            _5663.PartToPartShearCouplingConnectionCompoundModalAnalysisAtASpeed
        )

    @property
    def planetary_connection_compound_modal_analysis_at_a_speed(
        self: "CastSelf",
    ) -> "_5665.PlanetaryConnectionCompoundModalAnalysisAtASpeed":
        from mastapy._private.system_model.analyses_and_results.modal_analyses_at_a_speed.compound import (
            _5665,
        )

        return self.__parent__._cast(
            _5665.PlanetaryConnectionCompoundModalAnalysisAtASpeed
        )

    @property
    def ring_pins_to_disc_connection_compound_modal_analysis_at_a_speed(
        self: "CastSelf",
    ) -> "_5672.RingPinsToDiscConnectionCompoundModalAnalysisAtASpeed":
        from mastapy._private.system_model.analyses_and_results.modal_analyses_at_a_speed.compound import (
            _5672,
        )

        return self.__parent__._cast(
            _5672.RingPinsToDiscConnectionCompoundModalAnalysisAtASpeed
        )

    @property
    def rolling_ring_connection_compound_modal_analysis_at_a_speed(
        self: "CastSelf",
    ) -> "_5675.RollingRingConnectionCompoundModalAnalysisAtASpeed":
        from mastapy._private.system_model.analyses_and_results.modal_analyses_at_a_speed.compound import (
            _5675,
        )

        return self.__parent__._cast(
            _5675.RollingRingConnectionCompoundModalAnalysisAtASpeed
        )

    @property
    def shaft_to_mountable_component_connection_compound_modal_analysis_at_a_speed(
        self: "CastSelf",
    ) -> "_5679.ShaftToMountableComponentConnectionCompoundModalAnalysisAtASpeed":
        from mastapy._private.system_model.analyses_and_results.modal_analyses_at_a_speed.compound import (
            _5679,
        )

        return self.__parent__._cast(
            _5679.ShaftToMountableComponentConnectionCompoundModalAnalysisAtASpeed
        )

    @property
    def spiral_bevel_gear_mesh_compound_modal_analysis_at_a_speed(
        self: "CastSelf",
    ) -> "_5682.SpiralBevelGearMeshCompoundModalAnalysisAtASpeed":
        from mastapy._private.system_model.analyses_and_results.modal_analyses_at_a_speed.compound import (
            _5682,
        )

        return self.__parent__._cast(
            _5682.SpiralBevelGearMeshCompoundModalAnalysisAtASpeed
        )

    @property
    def spring_damper_connection_compound_modal_analysis_at_a_speed(
        self: "CastSelf",
    ) -> "_5685.SpringDamperConnectionCompoundModalAnalysisAtASpeed":
        from mastapy._private.system_model.analyses_and_results.modal_analyses_at_a_speed.compound import (
            _5685,
        )

        return self.__parent__._cast(
            _5685.SpringDamperConnectionCompoundModalAnalysisAtASpeed
        )

    @property
    def straight_bevel_diff_gear_mesh_compound_modal_analysis_at_a_speed(
        self: "CastSelf",
    ) -> "_5688.StraightBevelDiffGearMeshCompoundModalAnalysisAtASpeed":
        from mastapy._private.system_model.analyses_and_results.modal_analyses_at_a_speed.compound import (
            _5688,
        )

        return self.__parent__._cast(
            _5688.StraightBevelDiffGearMeshCompoundModalAnalysisAtASpeed
        )

    @property
    def straight_bevel_gear_mesh_compound_modal_analysis_at_a_speed(
        self: "CastSelf",
    ) -> "_5691.StraightBevelGearMeshCompoundModalAnalysisAtASpeed":
        from mastapy._private.system_model.analyses_and_results.modal_analyses_at_a_speed.compound import (
            _5691,
        )

        return self.__parent__._cast(
            _5691.StraightBevelGearMeshCompoundModalAnalysisAtASpeed
        )

    @property
    def torque_converter_connection_compound_modal_analysis_at_a_speed(
        self: "CastSelf",
    ) -> "_5700.TorqueConverterConnectionCompoundModalAnalysisAtASpeed":
        from mastapy._private.system_model.analyses_and_results.modal_analyses_at_a_speed.compound import (
            _5700,
        )

        return self.__parent__._cast(
            _5700.TorqueConverterConnectionCompoundModalAnalysisAtASpeed
        )

    @property
    def worm_gear_mesh_compound_modal_analysis_at_a_speed(
        self: "CastSelf",
    ) -> "_5706.WormGearMeshCompoundModalAnalysisAtASpeed":
        from mastapy._private.system_model.analyses_and_results.modal_analyses_at_a_speed.compound import (
            _5706,
        )

        return self.__parent__._cast(_5706.WormGearMeshCompoundModalAnalysisAtASpeed)

    @property
    def zerol_bevel_gear_mesh_compound_modal_analysis_at_a_speed(
        self: "CastSelf",
    ) -> "_5709.ZerolBevelGearMeshCompoundModalAnalysisAtASpeed":
        from mastapy._private.system_model.analyses_and_results.modal_analyses_at_a_speed.compound import (
            _5709,
        )

        return self.__parent__._cast(
            _5709.ZerolBevelGearMeshCompoundModalAnalysisAtASpeed
        )

    @property
    def connection_compound_modal_analysis_at_a_speed(
        self: "CastSelf",
    ) -> "ConnectionCompoundModalAnalysisAtASpeed":
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
class ConnectionCompoundModalAnalysisAtASpeed(_7935.ConnectionCompoundAnalysis):
    """ConnectionCompoundModalAnalysisAtASpeed

    This is a mastapy class.
    """

    TYPE: ClassVar["Type"] = _CONNECTION_COMPOUND_MODAL_ANALYSIS_AT_A_SPEED

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
    ) -> "List[_5483.ConnectionModalAnalysisAtASpeed]":
        """List[mastapy.system_model.analyses_and_results.modal_analyses_at_a_speed.ConnectionModalAnalysisAtASpeed]

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
    ) -> "List[_5483.ConnectionModalAnalysisAtASpeed]":
        """List[mastapy.system_model.analyses_and_results.modal_analyses_at_a_speed.ConnectionModalAnalysisAtASpeed]

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
    def cast_to(self: "Self") -> "_Cast_ConnectionCompoundModalAnalysisAtASpeed":
        """Cast to another type.

        Returns:
            _Cast_ConnectionCompoundModalAnalysisAtASpeed
        """
        return _Cast_ConnectionCompoundModalAnalysisAtASpeed(self)
