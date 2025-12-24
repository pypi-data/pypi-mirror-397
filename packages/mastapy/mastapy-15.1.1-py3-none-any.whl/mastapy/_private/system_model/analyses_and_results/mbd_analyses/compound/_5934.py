"""InterMountableComponentConnectionCompoundMultibodyDynamicsAnalysis"""

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
from mastapy._private.system_model.analyses_and_results.mbd_analyses.compound import (
    _5904,
)

_INTER_MOUNTABLE_COMPONENT_CONNECTION_COMPOUND_MULTIBODY_DYNAMICS_ANALYSIS = (
    python_net_import(
        "SMT.MastaAPI.SystemModel.AnalysesAndResults.MBDAnalyses.Compound",
        "InterMountableComponentConnectionCompoundMultibodyDynamicsAnalysis",
    )
)

if TYPE_CHECKING:
    from typing import Any, List, Type, TypeVar

    from mastapy._private.system_model.analyses_and_results import _2943
    from mastapy._private.system_model.analyses_and_results.analysis_cases import (
        _7935,
        _7939,
    )
    from mastapy._private.system_model.analyses_and_results.mbd_analyses import _5785
    from mastapy._private.system_model.analyses_and_results.mbd_analyses.compound import (
        _5874,
        _5878,
        _5881,
        _5886,
        _5891,
        _5896,
        _5899,
        _5902,
        _5907,
        _5909,
        _5917,
        _5923,
        _5928,
        _5932,
        _5936,
        _5939,
        _5942,
        _5952,
        _5961,
        _5964,
        _5971,
        _5974,
        _5977,
        _5980,
        _5989,
        _5995,
        _5998,
    )

    Self = TypeVar(
        "Self",
        bound="InterMountableComponentConnectionCompoundMultibodyDynamicsAnalysis",
    )
    CastSelf = TypeVar(
        "CastSelf",
        bound="InterMountableComponentConnectionCompoundMultibodyDynamicsAnalysis._Cast_InterMountableComponentConnectionCompoundMultibodyDynamicsAnalysis",
    )


__docformat__ = "restructuredtext en"
__all__ = ("InterMountableComponentConnectionCompoundMultibodyDynamicsAnalysis",)


@extended_dataclass(frozen=True, slots=True, weakref_slot=True)
class _Cast_InterMountableComponentConnectionCompoundMultibodyDynamicsAnalysis:
    """Special nested class for casting InterMountableComponentConnectionCompoundMultibodyDynamicsAnalysis to subclasses."""

    __parent__: "InterMountableComponentConnectionCompoundMultibodyDynamicsAnalysis"

    @property
    def connection_compound_multibody_dynamics_analysis(
        self: "CastSelf",
    ) -> "_5904.ConnectionCompoundMultibodyDynamicsAnalysis":
        return self.__parent__._cast(_5904.ConnectionCompoundMultibodyDynamicsAnalysis)

    @property
    def connection_compound_analysis(
        self: "CastSelf",
    ) -> "_7935.ConnectionCompoundAnalysis":
        from mastapy._private.system_model.analyses_and_results.analysis_cases import (
            _7935,
        )

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
    def agma_gleason_conical_gear_mesh_compound_multibody_dynamics_analysis(
        self: "CastSelf",
    ) -> "_5874.AGMAGleasonConicalGearMeshCompoundMultibodyDynamicsAnalysis":
        from mastapy._private.system_model.analyses_and_results.mbd_analyses.compound import (
            _5874,
        )

        return self.__parent__._cast(
            _5874.AGMAGleasonConicalGearMeshCompoundMultibodyDynamicsAnalysis
        )

    @property
    def belt_connection_compound_multibody_dynamics_analysis(
        self: "CastSelf",
    ) -> "_5878.BeltConnectionCompoundMultibodyDynamicsAnalysis":
        from mastapy._private.system_model.analyses_and_results.mbd_analyses.compound import (
            _5878,
        )

        return self.__parent__._cast(
            _5878.BeltConnectionCompoundMultibodyDynamicsAnalysis
        )

    @property
    def bevel_differential_gear_mesh_compound_multibody_dynamics_analysis(
        self: "CastSelf",
    ) -> "_5881.BevelDifferentialGearMeshCompoundMultibodyDynamicsAnalysis":
        from mastapy._private.system_model.analyses_and_results.mbd_analyses.compound import (
            _5881,
        )

        return self.__parent__._cast(
            _5881.BevelDifferentialGearMeshCompoundMultibodyDynamicsAnalysis
        )

    @property
    def bevel_gear_mesh_compound_multibody_dynamics_analysis(
        self: "CastSelf",
    ) -> "_5886.BevelGearMeshCompoundMultibodyDynamicsAnalysis":
        from mastapy._private.system_model.analyses_and_results.mbd_analyses.compound import (
            _5886,
        )

        return self.__parent__._cast(
            _5886.BevelGearMeshCompoundMultibodyDynamicsAnalysis
        )

    @property
    def clutch_connection_compound_multibody_dynamics_analysis(
        self: "CastSelf",
    ) -> "_5891.ClutchConnectionCompoundMultibodyDynamicsAnalysis":
        from mastapy._private.system_model.analyses_and_results.mbd_analyses.compound import (
            _5891,
        )

        return self.__parent__._cast(
            _5891.ClutchConnectionCompoundMultibodyDynamicsAnalysis
        )

    @property
    def concept_coupling_connection_compound_multibody_dynamics_analysis(
        self: "CastSelf",
    ) -> "_5896.ConceptCouplingConnectionCompoundMultibodyDynamicsAnalysis":
        from mastapy._private.system_model.analyses_and_results.mbd_analyses.compound import (
            _5896,
        )

        return self.__parent__._cast(
            _5896.ConceptCouplingConnectionCompoundMultibodyDynamicsAnalysis
        )

    @property
    def concept_gear_mesh_compound_multibody_dynamics_analysis(
        self: "CastSelf",
    ) -> "_5899.ConceptGearMeshCompoundMultibodyDynamicsAnalysis":
        from mastapy._private.system_model.analyses_and_results.mbd_analyses.compound import (
            _5899,
        )

        return self.__parent__._cast(
            _5899.ConceptGearMeshCompoundMultibodyDynamicsAnalysis
        )

    @property
    def conical_gear_mesh_compound_multibody_dynamics_analysis(
        self: "CastSelf",
    ) -> "_5902.ConicalGearMeshCompoundMultibodyDynamicsAnalysis":
        from mastapy._private.system_model.analyses_and_results.mbd_analyses.compound import (
            _5902,
        )

        return self.__parent__._cast(
            _5902.ConicalGearMeshCompoundMultibodyDynamicsAnalysis
        )

    @property
    def coupling_connection_compound_multibody_dynamics_analysis(
        self: "CastSelf",
    ) -> "_5907.CouplingConnectionCompoundMultibodyDynamicsAnalysis":
        from mastapy._private.system_model.analyses_and_results.mbd_analyses.compound import (
            _5907,
        )

        return self.__parent__._cast(
            _5907.CouplingConnectionCompoundMultibodyDynamicsAnalysis
        )

    @property
    def cvt_belt_connection_compound_multibody_dynamics_analysis(
        self: "CastSelf",
    ) -> "_5909.CVTBeltConnectionCompoundMultibodyDynamicsAnalysis":
        from mastapy._private.system_model.analyses_and_results.mbd_analyses.compound import (
            _5909,
        )

        return self.__parent__._cast(
            _5909.CVTBeltConnectionCompoundMultibodyDynamicsAnalysis
        )

    @property
    def cylindrical_gear_mesh_compound_multibody_dynamics_analysis(
        self: "CastSelf",
    ) -> "_5917.CylindricalGearMeshCompoundMultibodyDynamicsAnalysis":
        from mastapy._private.system_model.analyses_and_results.mbd_analyses.compound import (
            _5917,
        )

        return self.__parent__._cast(
            _5917.CylindricalGearMeshCompoundMultibodyDynamicsAnalysis
        )

    @property
    def face_gear_mesh_compound_multibody_dynamics_analysis(
        self: "CastSelf",
    ) -> "_5923.FaceGearMeshCompoundMultibodyDynamicsAnalysis":
        from mastapy._private.system_model.analyses_and_results.mbd_analyses.compound import (
            _5923,
        )

        return self.__parent__._cast(
            _5923.FaceGearMeshCompoundMultibodyDynamicsAnalysis
        )

    @property
    def gear_mesh_compound_multibody_dynamics_analysis(
        self: "CastSelf",
    ) -> "_5928.GearMeshCompoundMultibodyDynamicsAnalysis":
        from mastapy._private.system_model.analyses_and_results.mbd_analyses.compound import (
            _5928,
        )

        return self.__parent__._cast(_5928.GearMeshCompoundMultibodyDynamicsAnalysis)

    @property
    def hypoid_gear_mesh_compound_multibody_dynamics_analysis(
        self: "CastSelf",
    ) -> "_5932.HypoidGearMeshCompoundMultibodyDynamicsAnalysis":
        from mastapy._private.system_model.analyses_and_results.mbd_analyses.compound import (
            _5932,
        )

        return self.__parent__._cast(
            _5932.HypoidGearMeshCompoundMultibodyDynamicsAnalysis
        )

    @property
    def klingelnberg_cyclo_palloid_conical_gear_mesh_compound_multibody_dynamics_analysis(
        self: "CastSelf",
    ) -> (
        "_5936.KlingelnbergCycloPalloidConicalGearMeshCompoundMultibodyDynamicsAnalysis"
    ):
        from mastapy._private.system_model.analyses_and_results.mbd_analyses.compound import (
            _5936,
        )

        return self.__parent__._cast(
            _5936.KlingelnbergCycloPalloidConicalGearMeshCompoundMultibodyDynamicsAnalysis
        )

    @property
    def klingelnberg_cyclo_palloid_hypoid_gear_mesh_compound_multibody_dynamics_analysis(
        self: "CastSelf",
    ) -> (
        "_5939.KlingelnbergCycloPalloidHypoidGearMeshCompoundMultibodyDynamicsAnalysis"
    ):
        from mastapy._private.system_model.analyses_and_results.mbd_analyses.compound import (
            _5939,
        )

        return self.__parent__._cast(
            _5939.KlingelnbergCycloPalloidHypoidGearMeshCompoundMultibodyDynamicsAnalysis
        )

    @property
    def klingelnberg_cyclo_palloid_spiral_bevel_gear_mesh_compound_multibody_dynamics_analysis(
        self: "CastSelf",
    ) -> "_5942.KlingelnbergCycloPalloidSpiralBevelGearMeshCompoundMultibodyDynamicsAnalysis":
        from mastapy._private.system_model.analyses_and_results.mbd_analyses.compound import (
            _5942,
        )

        return self.__parent__._cast(
            _5942.KlingelnbergCycloPalloidSpiralBevelGearMeshCompoundMultibodyDynamicsAnalysis
        )

    @property
    def part_to_part_shear_coupling_connection_compound_multibody_dynamics_analysis(
        self: "CastSelf",
    ) -> "_5952.PartToPartShearCouplingConnectionCompoundMultibodyDynamicsAnalysis":
        from mastapy._private.system_model.analyses_and_results.mbd_analyses.compound import (
            _5952,
        )

        return self.__parent__._cast(
            _5952.PartToPartShearCouplingConnectionCompoundMultibodyDynamicsAnalysis
        )

    @property
    def ring_pins_to_disc_connection_compound_multibody_dynamics_analysis(
        self: "CastSelf",
    ) -> "_5961.RingPinsToDiscConnectionCompoundMultibodyDynamicsAnalysis":
        from mastapy._private.system_model.analyses_and_results.mbd_analyses.compound import (
            _5961,
        )

        return self.__parent__._cast(
            _5961.RingPinsToDiscConnectionCompoundMultibodyDynamicsAnalysis
        )

    @property
    def rolling_ring_connection_compound_multibody_dynamics_analysis(
        self: "CastSelf",
    ) -> "_5964.RollingRingConnectionCompoundMultibodyDynamicsAnalysis":
        from mastapy._private.system_model.analyses_and_results.mbd_analyses.compound import (
            _5964,
        )

        return self.__parent__._cast(
            _5964.RollingRingConnectionCompoundMultibodyDynamicsAnalysis
        )

    @property
    def spiral_bevel_gear_mesh_compound_multibody_dynamics_analysis(
        self: "CastSelf",
    ) -> "_5971.SpiralBevelGearMeshCompoundMultibodyDynamicsAnalysis":
        from mastapy._private.system_model.analyses_and_results.mbd_analyses.compound import (
            _5971,
        )

        return self.__parent__._cast(
            _5971.SpiralBevelGearMeshCompoundMultibodyDynamicsAnalysis
        )

    @property
    def spring_damper_connection_compound_multibody_dynamics_analysis(
        self: "CastSelf",
    ) -> "_5974.SpringDamperConnectionCompoundMultibodyDynamicsAnalysis":
        from mastapy._private.system_model.analyses_and_results.mbd_analyses.compound import (
            _5974,
        )

        return self.__parent__._cast(
            _5974.SpringDamperConnectionCompoundMultibodyDynamicsAnalysis
        )

    @property
    def straight_bevel_diff_gear_mesh_compound_multibody_dynamics_analysis(
        self: "CastSelf",
    ) -> "_5977.StraightBevelDiffGearMeshCompoundMultibodyDynamicsAnalysis":
        from mastapy._private.system_model.analyses_and_results.mbd_analyses.compound import (
            _5977,
        )

        return self.__parent__._cast(
            _5977.StraightBevelDiffGearMeshCompoundMultibodyDynamicsAnalysis
        )

    @property
    def straight_bevel_gear_mesh_compound_multibody_dynamics_analysis(
        self: "CastSelf",
    ) -> "_5980.StraightBevelGearMeshCompoundMultibodyDynamicsAnalysis":
        from mastapy._private.system_model.analyses_and_results.mbd_analyses.compound import (
            _5980,
        )

        return self.__parent__._cast(
            _5980.StraightBevelGearMeshCompoundMultibodyDynamicsAnalysis
        )

    @property
    def torque_converter_connection_compound_multibody_dynamics_analysis(
        self: "CastSelf",
    ) -> "_5989.TorqueConverterConnectionCompoundMultibodyDynamicsAnalysis":
        from mastapy._private.system_model.analyses_and_results.mbd_analyses.compound import (
            _5989,
        )

        return self.__parent__._cast(
            _5989.TorqueConverterConnectionCompoundMultibodyDynamicsAnalysis
        )

    @property
    def worm_gear_mesh_compound_multibody_dynamics_analysis(
        self: "CastSelf",
    ) -> "_5995.WormGearMeshCompoundMultibodyDynamicsAnalysis":
        from mastapy._private.system_model.analyses_and_results.mbd_analyses.compound import (
            _5995,
        )

        return self.__parent__._cast(
            _5995.WormGearMeshCompoundMultibodyDynamicsAnalysis
        )

    @property
    def zerol_bevel_gear_mesh_compound_multibody_dynamics_analysis(
        self: "CastSelf",
    ) -> "_5998.ZerolBevelGearMeshCompoundMultibodyDynamicsAnalysis":
        from mastapy._private.system_model.analyses_and_results.mbd_analyses.compound import (
            _5998,
        )

        return self.__parent__._cast(
            _5998.ZerolBevelGearMeshCompoundMultibodyDynamicsAnalysis
        )

    @property
    def inter_mountable_component_connection_compound_multibody_dynamics_analysis(
        self: "CastSelf",
    ) -> "InterMountableComponentConnectionCompoundMultibodyDynamicsAnalysis":
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
class InterMountableComponentConnectionCompoundMultibodyDynamicsAnalysis(
    _5904.ConnectionCompoundMultibodyDynamicsAnalysis
):
    """InterMountableComponentConnectionCompoundMultibodyDynamicsAnalysis

    This is a mastapy class.
    """

    TYPE: ClassVar["Type"] = (
        _INTER_MOUNTABLE_COMPONENT_CONNECTION_COMPOUND_MULTIBODY_DYNAMICS_ANALYSIS
    )

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
    ) -> "List[_5785.InterMountableComponentConnectionMultibodyDynamicsAnalysis]":
        """List[mastapy.system_model.analyses_and_results.mbd_analyses.InterMountableComponentConnectionMultibodyDynamicsAnalysis]

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
    ) -> "List[_5785.InterMountableComponentConnectionMultibodyDynamicsAnalysis]":
        """List[mastapy.system_model.analyses_and_results.mbd_analyses.InterMountableComponentConnectionMultibodyDynamicsAnalysis]

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
    ) -> "_Cast_InterMountableComponentConnectionCompoundMultibodyDynamicsAnalysis":
        """Cast to another type.

        Returns:
            _Cast_InterMountableComponentConnectionCompoundMultibodyDynamicsAnalysis
        """
        return _Cast_InterMountableComponentConnectionCompoundMultibodyDynamicsAnalysis(
            self
        )
