"""InterMountableComponentConnectionModalAnalysis"""

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
from mastapy._private.system_model.analyses_and_results.modal_analyses import _4929

_INTER_MOUNTABLE_COMPONENT_CONNECTION_MODAL_ANALYSIS = python_net_import(
    "SMT.MastaAPI.SystemModel.AnalysesAndResults.ModalAnalyses",
    "InterMountableComponentConnectionModalAnalysis",
)

if TYPE_CHECKING:
    from typing import Any, Type, TypeVar

    from mastapy._private.system_model.analyses_and_results import _2941, _2943, _2945
    from mastapy._private.system_model.analyses_and_results.analysis_cases import (
        _7934,
        _7937,
    )
    from mastapy._private.system_model.analyses_and_results.modal_analyses import (
        _4898,
        _4903,
        _4905,
        _4910,
        _4915,
        _4920,
        _4923,
        _4926,
        _4932,
        _4935,
        _4942,
        _4951,
        _4957,
        _4961,
        _4965,
        _4968,
        _4971,
        _4988,
        _4998,
        _5000,
        _5008,
        _5011,
        _5014,
        _5017,
        _5026,
        _5035,
        _5038,
    )
    from mastapy._private.system_model.analyses_and_results.system_deflections import (
        _3059,
    )
    from mastapy._private.system_model.connections_and_sockets import _2540

    Self = TypeVar("Self", bound="InterMountableComponentConnectionModalAnalysis")
    CastSelf = TypeVar(
        "CastSelf",
        bound="InterMountableComponentConnectionModalAnalysis._Cast_InterMountableComponentConnectionModalAnalysis",
    )


__docformat__ = "restructuredtext en"
__all__ = ("InterMountableComponentConnectionModalAnalysis",)


@extended_dataclass(frozen=True, slots=True, weakref_slot=True)
class _Cast_InterMountableComponentConnectionModalAnalysis:
    """Special nested class for casting InterMountableComponentConnectionModalAnalysis to subclasses."""

    __parent__: "InterMountableComponentConnectionModalAnalysis"

    @property
    def connection_modal_analysis(self: "CastSelf") -> "_4929.ConnectionModalAnalysis":
        return self.__parent__._cast(_4929.ConnectionModalAnalysis)

    @property
    def connection_static_load_analysis_case(
        self: "CastSelf",
    ) -> "_7937.ConnectionStaticLoadAnalysisCase":
        from mastapy._private.system_model.analyses_and_results.analysis_cases import (
            _7937,
        )

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
    def agma_gleason_conical_gear_mesh_modal_analysis(
        self: "CastSelf",
    ) -> "_4898.AGMAGleasonConicalGearMeshModalAnalysis":
        from mastapy._private.system_model.analyses_and_results.modal_analyses import (
            _4898,
        )

        return self.__parent__._cast(_4898.AGMAGleasonConicalGearMeshModalAnalysis)

    @property
    def belt_connection_modal_analysis(
        self: "CastSelf",
    ) -> "_4903.BeltConnectionModalAnalysis":
        from mastapy._private.system_model.analyses_and_results.modal_analyses import (
            _4903,
        )

        return self.__parent__._cast(_4903.BeltConnectionModalAnalysis)

    @property
    def bevel_differential_gear_mesh_modal_analysis(
        self: "CastSelf",
    ) -> "_4905.BevelDifferentialGearMeshModalAnalysis":
        from mastapy._private.system_model.analyses_and_results.modal_analyses import (
            _4905,
        )

        return self.__parent__._cast(_4905.BevelDifferentialGearMeshModalAnalysis)

    @property
    def bevel_gear_mesh_modal_analysis(
        self: "CastSelf",
    ) -> "_4910.BevelGearMeshModalAnalysis":
        from mastapy._private.system_model.analyses_and_results.modal_analyses import (
            _4910,
        )

        return self.__parent__._cast(_4910.BevelGearMeshModalAnalysis)

    @property
    def clutch_connection_modal_analysis(
        self: "CastSelf",
    ) -> "_4915.ClutchConnectionModalAnalysis":
        from mastapy._private.system_model.analyses_and_results.modal_analyses import (
            _4915,
        )

        return self.__parent__._cast(_4915.ClutchConnectionModalAnalysis)

    @property
    def concept_coupling_connection_modal_analysis(
        self: "CastSelf",
    ) -> "_4920.ConceptCouplingConnectionModalAnalysis":
        from mastapy._private.system_model.analyses_and_results.modal_analyses import (
            _4920,
        )

        return self.__parent__._cast(_4920.ConceptCouplingConnectionModalAnalysis)

    @property
    def concept_gear_mesh_modal_analysis(
        self: "CastSelf",
    ) -> "_4923.ConceptGearMeshModalAnalysis":
        from mastapy._private.system_model.analyses_and_results.modal_analyses import (
            _4923,
        )

        return self.__parent__._cast(_4923.ConceptGearMeshModalAnalysis)

    @property
    def conical_gear_mesh_modal_analysis(
        self: "CastSelf",
    ) -> "_4926.ConicalGearMeshModalAnalysis":
        from mastapy._private.system_model.analyses_and_results.modal_analyses import (
            _4926,
        )

        return self.__parent__._cast(_4926.ConicalGearMeshModalAnalysis)

    @property
    def coupling_connection_modal_analysis(
        self: "CastSelf",
    ) -> "_4932.CouplingConnectionModalAnalysis":
        from mastapy._private.system_model.analyses_and_results.modal_analyses import (
            _4932,
        )

        return self.__parent__._cast(_4932.CouplingConnectionModalAnalysis)

    @property
    def cvt_belt_connection_modal_analysis(
        self: "CastSelf",
    ) -> "_4935.CVTBeltConnectionModalAnalysis":
        from mastapy._private.system_model.analyses_and_results.modal_analyses import (
            _4935,
        )

        return self.__parent__._cast(_4935.CVTBeltConnectionModalAnalysis)

    @property
    def cylindrical_gear_mesh_modal_analysis(
        self: "CastSelf",
    ) -> "_4942.CylindricalGearMeshModalAnalysis":
        from mastapy._private.system_model.analyses_and_results.modal_analyses import (
            _4942,
        )

        return self.__parent__._cast(_4942.CylindricalGearMeshModalAnalysis)

    @property
    def face_gear_mesh_modal_analysis(
        self: "CastSelf",
    ) -> "_4951.FaceGearMeshModalAnalysis":
        from mastapy._private.system_model.analyses_and_results.modal_analyses import (
            _4951,
        )

        return self.__parent__._cast(_4951.FaceGearMeshModalAnalysis)

    @property
    def gear_mesh_modal_analysis(self: "CastSelf") -> "_4957.GearMeshModalAnalysis":
        from mastapy._private.system_model.analyses_and_results.modal_analyses import (
            _4957,
        )

        return self.__parent__._cast(_4957.GearMeshModalAnalysis)

    @property
    def hypoid_gear_mesh_modal_analysis(
        self: "CastSelf",
    ) -> "_4961.HypoidGearMeshModalAnalysis":
        from mastapy._private.system_model.analyses_and_results.modal_analyses import (
            _4961,
        )

        return self.__parent__._cast(_4961.HypoidGearMeshModalAnalysis)

    @property
    def klingelnberg_cyclo_palloid_conical_gear_mesh_modal_analysis(
        self: "CastSelf",
    ) -> "_4965.KlingelnbergCycloPalloidConicalGearMeshModalAnalysis":
        from mastapy._private.system_model.analyses_and_results.modal_analyses import (
            _4965,
        )

        return self.__parent__._cast(
            _4965.KlingelnbergCycloPalloidConicalGearMeshModalAnalysis
        )

    @property
    def klingelnberg_cyclo_palloid_hypoid_gear_mesh_modal_analysis(
        self: "CastSelf",
    ) -> "_4968.KlingelnbergCycloPalloidHypoidGearMeshModalAnalysis":
        from mastapy._private.system_model.analyses_and_results.modal_analyses import (
            _4968,
        )

        return self.__parent__._cast(
            _4968.KlingelnbergCycloPalloidHypoidGearMeshModalAnalysis
        )

    @property
    def klingelnberg_cyclo_palloid_spiral_bevel_gear_mesh_modal_analysis(
        self: "CastSelf",
    ) -> "_4971.KlingelnbergCycloPalloidSpiralBevelGearMeshModalAnalysis":
        from mastapy._private.system_model.analyses_and_results.modal_analyses import (
            _4971,
        )

        return self.__parent__._cast(
            _4971.KlingelnbergCycloPalloidSpiralBevelGearMeshModalAnalysis
        )

    @property
    def part_to_part_shear_coupling_connection_modal_analysis(
        self: "CastSelf",
    ) -> "_4988.PartToPartShearCouplingConnectionModalAnalysis":
        from mastapy._private.system_model.analyses_and_results.modal_analyses import (
            _4988,
        )

        return self.__parent__._cast(
            _4988.PartToPartShearCouplingConnectionModalAnalysis
        )

    @property
    def ring_pins_to_disc_connection_modal_analysis(
        self: "CastSelf",
    ) -> "_4998.RingPinsToDiscConnectionModalAnalysis":
        from mastapy._private.system_model.analyses_and_results.modal_analyses import (
            _4998,
        )

        return self.__parent__._cast(_4998.RingPinsToDiscConnectionModalAnalysis)

    @property
    def rolling_ring_connection_modal_analysis(
        self: "CastSelf",
    ) -> "_5000.RollingRingConnectionModalAnalysis":
        from mastapy._private.system_model.analyses_and_results.modal_analyses import (
            _5000,
        )

        return self.__parent__._cast(_5000.RollingRingConnectionModalAnalysis)

    @property
    def spiral_bevel_gear_mesh_modal_analysis(
        self: "CastSelf",
    ) -> "_5008.SpiralBevelGearMeshModalAnalysis":
        from mastapy._private.system_model.analyses_and_results.modal_analyses import (
            _5008,
        )

        return self.__parent__._cast(_5008.SpiralBevelGearMeshModalAnalysis)

    @property
    def spring_damper_connection_modal_analysis(
        self: "CastSelf",
    ) -> "_5011.SpringDamperConnectionModalAnalysis":
        from mastapy._private.system_model.analyses_and_results.modal_analyses import (
            _5011,
        )

        return self.__parent__._cast(_5011.SpringDamperConnectionModalAnalysis)

    @property
    def straight_bevel_diff_gear_mesh_modal_analysis(
        self: "CastSelf",
    ) -> "_5014.StraightBevelDiffGearMeshModalAnalysis":
        from mastapy._private.system_model.analyses_and_results.modal_analyses import (
            _5014,
        )

        return self.__parent__._cast(_5014.StraightBevelDiffGearMeshModalAnalysis)

    @property
    def straight_bevel_gear_mesh_modal_analysis(
        self: "CastSelf",
    ) -> "_5017.StraightBevelGearMeshModalAnalysis":
        from mastapy._private.system_model.analyses_and_results.modal_analyses import (
            _5017,
        )

        return self.__parent__._cast(_5017.StraightBevelGearMeshModalAnalysis)

    @property
    def torque_converter_connection_modal_analysis(
        self: "CastSelf",
    ) -> "_5026.TorqueConverterConnectionModalAnalysis":
        from mastapy._private.system_model.analyses_and_results.modal_analyses import (
            _5026,
        )

        return self.__parent__._cast(_5026.TorqueConverterConnectionModalAnalysis)

    @property
    def worm_gear_mesh_modal_analysis(
        self: "CastSelf",
    ) -> "_5035.WormGearMeshModalAnalysis":
        from mastapy._private.system_model.analyses_and_results.modal_analyses import (
            _5035,
        )

        return self.__parent__._cast(_5035.WormGearMeshModalAnalysis)

    @property
    def zerol_bevel_gear_mesh_modal_analysis(
        self: "CastSelf",
    ) -> "_5038.ZerolBevelGearMeshModalAnalysis":
        from mastapy._private.system_model.analyses_and_results.modal_analyses import (
            _5038,
        )

        return self.__parent__._cast(_5038.ZerolBevelGearMeshModalAnalysis)

    @property
    def inter_mountable_component_connection_modal_analysis(
        self: "CastSelf",
    ) -> "InterMountableComponentConnectionModalAnalysis":
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
class InterMountableComponentConnectionModalAnalysis(_4929.ConnectionModalAnalysis):
    """InterMountableComponentConnectionModalAnalysis

    This is a mastapy class.
    """

    TYPE: ClassVar["Type"] = _INTER_MOUNTABLE_COMPONENT_CONNECTION_MODAL_ANALYSIS

    wrapped: "Any"

    def __post_init__(self: "Self") -> None:
        """Override of the post initialisation magic method."""
        if not hasattr(self.wrapped, "reference_count"):
            self.wrapped.reference_count = 0

        self.wrapped.reference_count += 1

    @property
    @exception_bridge
    def connection_design(self: "Self") -> "_2540.InterMountableComponentConnection":
        """mastapy.system_model.connections_and_sockets.InterMountableComponentConnection

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
    def system_deflection_results(
        self: "Self",
    ) -> "_3059.InterMountableComponentConnectionSystemDeflection":
        """mastapy.system_model.analyses_and_results.system_deflections.InterMountableComponentConnectionSystemDeflection

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "SystemDeflectionResults")

        if temp is None:
            return None

        type_ = temp.GetType()
        return constructor.new(type_.Namespace, type_.Name)(temp)

    @property
    def cast_to(self: "Self") -> "_Cast_InterMountableComponentConnectionModalAnalysis":
        """Cast to another type.

        Returns:
            _Cast_InterMountableComponentConnectionModalAnalysis
        """
        return _Cast_InterMountableComponentConnectionModalAnalysis(self)
