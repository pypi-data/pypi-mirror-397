"""InterMountableComponentConnectionCompoundStabilityAnalysis"""

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
from mastapy._private.system_model.analyses_and_results.stability_analyses.compound import (
    _4243,
)

_INTER_MOUNTABLE_COMPONENT_CONNECTION_COMPOUND_STABILITY_ANALYSIS = python_net_import(
    "SMT.MastaAPI.SystemModel.AnalysesAndResults.StabilityAnalyses.Compound",
    "InterMountableComponentConnectionCompoundStabilityAnalysis",
)

if TYPE_CHECKING:
    from typing import Any, List, Type, TypeVar

    from mastapy._private.system_model.analyses_and_results import _2943
    from mastapy._private.system_model.analyses_and_results.analysis_cases import (
        _7935,
        _7939,
    )
    from mastapy._private.system_model.analyses_and_results.stability_analyses import (
        _4139,
    )
    from mastapy._private.system_model.analyses_and_results.stability_analyses.compound import (
        _4213,
        _4217,
        _4220,
        _4225,
        _4230,
        _4235,
        _4238,
        _4241,
        _4246,
        _4248,
        _4256,
        _4262,
        _4267,
        _4271,
        _4275,
        _4278,
        _4281,
        _4291,
        _4300,
        _4303,
        _4310,
        _4313,
        _4316,
        _4319,
        _4328,
        _4334,
        _4337,
    )

    Self = TypeVar(
        "Self", bound="InterMountableComponentConnectionCompoundStabilityAnalysis"
    )
    CastSelf = TypeVar(
        "CastSelf",
        bound="InterMountableComponentConnectionCompoundStabilityAnalysis._Cast_InterMountableComponentConnectionCompoundStabilityAnalysis",
    )


__docformat__ = "restructuredtext en"
__all__ = ("InterMountableComponentConnectionCompoundStabilityAnalysis",)


@extended_dataclass(frozen=True, slots=True, weakref_slot=True)
class _Cast_InterMountableComponentConnectionCompoundStabilityAnalysis:
    """Special nested class for casting InterMountableComponentConnectionCompoundStabilityAnalysis to subclasses."""

    __parent__: "InterMountableComponentConnectionCompoundStabilityAnalysis"

    @property
    def connection_compound_stability_analysis(
        self: "CastSelf",
    ) -> "_4243.ConnectionCompoundStabilityAnalysis":
        return self.__parent__._cast(_4243.ConnectionCompoundStabilityAnalysis)

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
    def agma_gleason_conical_gear_mesh_compound_stability_analysis(
        self: "CastSelf",
    ) -> "_4213.AGMAGleasonConicalGearMeshCompoundStabilityAnalysis":
        from mastapy._private.system_model.analyses_and_results.stability_analyses.compound import (
            _4213,
        )

        return self.__parent__._cast(
            _4213.AGMAGleasonConicalGearMeshCompoundStabilityAnalysis
        )

    @property
    def belt_connection_compound_stability_analysis(
        self: "CastSelf",
    ) -> "_4217.BeltConnectionCompoundStabilityAnalysis":
        from mastapy._private.system_model.analyses_and_results.stability_analyses.compound import (
            _4217,
        )

        return self.__parent__._cast(_4217.BeltConnectionCompoundStabilityAnalysis)

    @property
    def bevel_differential_gear_mesh_compound_stability_analysis(
        self: "CastSelf",
    ) -> "_4220.BevelDifferentialGearMeshCompoundStabilityAnalysis":
        from mastapy._private.system_model.analyses_and_results.stability_analyses.compound import (
            _4220,
        )

        return self.__parent__._cast(
            _4220.BevelDifferentialGearMeshCompoundStabilityAnalysis
        )

    @property
    def bevel_gear_mesh_compound_stability_analysis(
        self: "CastSelf",
    ) -> "_4225.BevelGearMeshCompoundStabilityAnalysis":
        from mastapy._private.system_model.analyses_and_results.stability_analyses.compound import (
            _4225,
        )

        return self.__parent__._cast(_4225.BevelGearMeshCompoundStabilityAnalysis)

    @property
    def clutch_connection_compound_stability_analysis(
        self: "CastSelf",
    ) -> "_4230.ClutchConnectionCompoundStabilityAnalysis":
        from mastapy._private.system_model.analyses_and_results.stability_analyses.compound import (
            _4230,
        )

        return self.__parent__._cast(_4230.ClutchConnectionCompoundStabilityAnalysis)

    @property
    def concept_coupling_connection_compound_stability_analysis(
        self: "CastSelf",
    ) -> "_4235.ConceptCouplingConnectionCompoundStabilityAnalysis":
        from mastapy._private.system_model.analyses_and_results.stability_analyses.compound import (
            _4235,
        )

        return self.__parent__._cast(
            _4235.ConceptCouplingConnectionCompoundStabilityAnalysis
        )

    @property
    def concept_gear_mesh_compound_stability_analysis(
        self: "CastSelf",
    ) -> "_4238.ConceptGearMeshCompoundStabilityAnalysis":
        from mastapy._private.system_model.analyses_and_results.stability_analyses.compound import (
            _4238,
        )

        return self.__parent__._cast(_4238.ConceptGearMeshCompoundStabilityAnalysis)

    @property
    def conical_gear_mesh_compound_stability_analysis(
        self: "CastSelf",
    ) -> "_4241.ConicalGearMeshCompoundStabilityAnalysis":
        from mastapy._private.system_model.analyses_and_results.stability_analyses.compound import (
            _4241,
        )

        return self.__parent__._cast(_4241.ConicalGearMeshCompoundStabilityAnalysis)

    @property
    def coupling_connection_compound_stability_analysis(
        self: "CastSelf",
    ) -> "_4246.CouplingConnectionCompoundStabilityAnalysis":
        from mastapy._private.system_model.analyses_and_results.stability_analyses.compound import (
            _4246,
        )

        return self.__parent__._cast(_4246.CouplingConnectionCompoundStabilityAnalysis)

    @property
    def cvt_belt_connection_compound_stability_analysis(
        self: "CastSelf",
    ) -> "_4248.CVTBeltConnectionCompoundStabilityAnalysis":
        from mastapy._private.system_model.analyses_and_results.stability_analyses.compound import (
            _4248,
        )

        return self.__parent__._cast(_4248.CVTBeltConnectionCompoundStabilityAnalysis)

    @property
    def cylindrical_gear_mesh_compound_stability_analysis(
        self: "CastSelf",
    ) -> "_4256.CylindricalGearMeshCompoundStabilityAnalysis":
        from mastapy._private.system_model.analyses_and_results.stability_analyses.compound import (
            _4256,
        )

        return self.__parent__._cast(_4256.CylindricalGearMeshCompoundStabilityAnalysis)

    @property
    def face_gear_mesh_compound_stability_analysis(
        self: "CastSelf",
    ) -> "_4262.FaceGearMeshCompoundStabilityAnalysis":
        from mastapy._private.system_model.analyses_and_results.stability_analyses.compound import (
            _4262,
        )

        return self.__parent__._cast(_4262.FaceGearMeshCompoundStabilityAnalysis)

    @property
    def gear_mesh_compound_stability_analysis(
        self: "CastSelf",
    ) -> "_4267.GearMeshCompoundStabilityAnalysis":
        from mastapy._private.system_model.analyses_and_results.stability_analyses.compound import (
            _4267,
        )

        return self.__parent__._cast(_4267.GearMeshCompoundStabilityAnalysis)

    @property
    def hypoid_gear_mesh_compound_stability_analysis(
        self: "CastSelf",
    ) -> "_4271.HypoidGearMeshCompoundStabilityAnalysis":
        from mastapy._private.system_model.analyses_and_results.stability_analyses.compound import (
            _4271,
        )

        return self.__parent__._cast(_4271.HypoidGearMeshCompoundStabilityAnalysis)

    @property
    def klingelnberg_cyclo_palloid_conical_gear_mesh_compound_stability_analysis(
        self: "CastSelf",
    ) -> "_4275.KlingelnbergCycloPalloidConicalGearMeshCompoundStabilityAnalysis":
        from mastapy._private.system_model.analyses_and_results.stability_analyses.compound import (
            _4275,
        )

        return self.__parent__._cast(
            _4275.KlingelnbergCycloPalloidConicalGearMeshCompoundStabilityAnalysis
        )

    @property
    def klingelnberg_cyclo_palloid_hypoid_gear_mesh_compound_stability_analysis(
        self: "CastSelf",
    ) -> "_4278.KlingelnbergCycloPalloidHypoidGearMeshCompoundStabilityAnalysis":
        from mastapy._private.system_model.analyses_and_results.stability_analyses.compound import (
            _4278,
        )

        return self.__parent__._cast(
            _4278.KlingelnbergCycloPalloidHypoidGearMeshCompoundStabilityAnalysis
        )

    @property
    def klingelnberg_cyclo_palloid_spiral_bevel_gear_mesh_compound_stability_analysis(
        self: "CastSelf",
    ) -> "_4281.KlingelnbergCycloPalloidSpiralBevelGearMeshCompoundStabilityAnalysis":
        from mastapy._private.system_model.analyses_and_results.stability_analyses.compound import (
            _4281,
        )

        return self.__parent__._cast(
            _4281.KlingelnbergCycloPalloidSpiralBevelGearMeshCompoundStabilityAnalysis
        )

    @property
    def part_to_part_shear_coupling_connection_compound_stability_analysis(
        self: "CastSelf",
    ) -> "_4291.PartToPartShearCouplingConnectionCompoundStabilityAnalysis":
        from mastapy._private.system_model.analyses_and_results.stability_analyses.compound import (
            _4291,
        )

        return self.__parent__._cast(
            _4291.PartToPartShearCouplingConnectionCompoundStabilityAnalysis
        )

    @property
    def ring_pins_to_disc_connection_compound_stability_analysis(
        self: "CastSelf",
    ) -> "_4300.RingPinsToDiscConnectionCompoundStabilityAnalysis":
        from mastapy._private.system_model.analyses_and_results.stability_analyses.compound import (
            _4300,
        )

        return self.__parent__._cast(
            _4300.RingPinsToDiscConnectionCompoundStabilityAnalysis
        )

    @property
    def rolling_ring_connection_compound_stability_analysis(
        self: "CastSelf",
    ) -> "_4303.RollingRingConnectionCompoundStabilityAnalysis":
        from mastapy._private.system_model.analyses_and_results.stability_analyses.compound import (
            _4303,
        )

        return self.__parent__._cast(
            _4303.RollingRingConnectionCompoundStabilityAnalysis
        )

    @property
    def spiral_bevel_gear_mesh_compound_stability_analysis(
        self: "CastSelf",
    ) -> "_4310.SpiralBevelGearMeshCompoundStabilityAnalysis":
        from mastapy._private.system_model.analyses_and_results.stability_analyses.compound import (
            _4310,
        )

        return self.__parent__._cast(_4310.SpiralBevelGearMeshCompoundStabilityAnalysis)

    @property
    def spring_damper_connection_compound_stability_analysis(
        self: "CastSelf",
    ) -> "_4313.SpringDamperConnectionCompoundStabilityAnalysis":
        from mastapy._private.system_model.analyses_and_results.stability_analyses.compound import (
            _4313,
        )

        return self.__parent__._cast(
            _4313.SpringDamperConnectionCompoundStabilityAnalysis
        )

    @property
    def straight_bevel_diff_gear_mesh_compound_stability_analysis(
        self: "CastSelf",
    ) -> "_4316.StraightBevelDiffGearMeshCompoundStabilityAnalysis":
        from mastapy._private.system_model.analyses_and_results.stability_analyses.compound import (
            _4316,
        )

        return self.__parent__._cast(
            _4316.StraightBevelDiffGearMeshCompoundStabilityAnalysis
        )

    @property
    def straight_bevel_gear_mesh_compound_stability_analysis(
        self: "CastSelf",
    ) -> "_4319.StraightBevelGearMeshCompoundStabilityAnalysis":
        from mastapy._private.system_model.analyses_and_results.stability_analyses.compound import (
            _4319,
        )

        return self.__parent__._cast(
            _4319.StraightBevelGearMeshCompoundStabilityAnalysis
        )

    @property
    def torque_converter_connection_compound_stability_analysis(
        self: "CastSelf",
    ) -> "_4328.TorqueConverterConnectionCompoundStabilityAnalysis":
        from mastapy._private.system_model.analyses_and_results.stability_analyses.compound import (
            _4328,
        )

        return self.__parent__._cast(
            _4328.TorqueConverterConnectionCompoundStabilityAnalysis
        )

    @property
    def worm_gear_mesh_compound_stability_analysis(
        self: "CastSelf",
    ) -> "_4334.WormGearMeshCompoundStabilityAnalysis":
        from mastapy._private.system_model.analyses_and_results.stability_analyses.compound import (
            _4334,
        )

        return self.__parent__._cast(_4334.WormGearMeshCompoundStabilityAnalysis)

    @property
    def zerol_bevel_gear_mesh_compound_stability_analysis(
        self: "CastSelf",
    ) -> "_4337.ZerolBevelGearMeshCompoundStabilityAnalysis":
        from mastapy._private.system_model.analyses_and_results.stability_analyses.compound import (
            _4337,
        )

        return self.__parent__._cast(_4337.ZerolBevelGearMeshCompoundStabilityAnalysis)

    @property
    def inter_mountable_component_connection_compound_stability_analysis(
        self: "CastSelf",
    ) -> "InterMountableComponentConnectionCompoundStabilityAnalysis":
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
class InterMountableComponentConnectionCompoundStabilityAnalysis(
    _4243.ConnectionCompoundStabilityAnalysis
):
    """InterMountableComponentConnectionCompoundStabilityAnalysis

    This is a mastapy class.
    """

    TYPE: ClassVar["Type"] = (
        _INTER_MOUNTABLE_COMPONENT_CONNECTION_COMPOUND_STABILITY_ANALYSIS
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
    ) -> "List[_4139.InterMountableComponentConnectionStabilityAnalysis]":
        """List[mastapy.system_model.analyses_and_results.stability_analyses.InterMountableComponentConnectionStabilityAnalysis]

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
    ) -> "List[_4139.InterMountableComponentConnectionStabilityAnalysis]":
        """List[mastapy.system_model.analyses_and_results.stability_analyses.InterMountableComponentConnectionStabilityAnalysis]

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
    ) -> "_Cast_InterMountableComponentConnectionCompoundStabilityAnalysis":
        """Cast to another type.

        Returns:
            _Cast_InterMountableComponentConnectionCompoundStabilityAnalysis
        """
        return _Cast_InterMountableComponentConnectionCompoundStabilityAnalysis(self)
