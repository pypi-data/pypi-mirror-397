"""InterMountableComponentConnectionCompoundSystemDeflection"""

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
from mastapy._private.system_model.analyses_and_results.system_deflections.compound import (
    _3181,
)

_INTER_MOUNTABLE_COMPONENT_CONNECTION_COMPOUND_SYSTEM_DEFLECTION = python_net_import(
    "SMT.MastaAPI.SystemModel.AnalysesAndResults.SystemDeflections.Compound",
    "InterMountableComponentConnectionCompoundSystemDeflection",
)

if TYPE_CHECKING:
    from typing import Any, List, Type, TypeVar

    from mastapy._private.system_model.analyses_and_results import _2943
    from mastapy._private.system_model.analyses_and_results.analysis_cases import (
        _7935,
        _7939,
    )
    from mastapy._private.system_model.analyses_and_results.system_deflections import (
        _3059,
    )
    from mastapy._private.system_model.analyses_and_results.system_deflections.compound import (
        _3151,
        _3155,
        _3158,
        _3163,
        _3168,
        _3173,
        _3176,
        _3179,
        _3184,
        _3186,
        _3194,
        _3201,
        _3206,
        _3210,
        _3214,
        _3217,
        _3220,
        _3230,
        _3239,
        _3242,
        _3250,
        _3253,
        _3256,
        _3259,
        _3268,
        _3274,
        _3277,
    )

    Self = TypeVar(
        "Self", bound="InterMountableComponentConnectionCompoundSystemDeflection"
    )
    CastSelf = TypeVar(
        "CastSelf",
        bound="InterMountableComponentConnectionCompoundSystemDeflection._Cast_InterMountableComponentConnectionCompoundSystemDeflection",
    )


__docformat__ = "restructuredtext en"
__all__ = ("InterMountableComponentConnectionCompoundSystemDeflection",)


@extended_dataclass(frozen=True, slots=True, weakref_slot=True)
class _Cast_InterMountableComponentConnectionCompoundSystemDeflection:
    """Special nested class for casting InterMountableComponentConnectionCompoundSystemDeflection to subclasses."""

    __parent__: "InterMountableComponentConnectionCompoundSystemDeflection"

    @property
    def connection_compound_system_deflection(
        self: "CastSelf",
    ) -> "_3181.ConnectionCompoundSystemDeflection":
        return self.__parent__._cast(_3181.ConnectionCompoundSystemDeflection)

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
    def agma_gleason_conical_gear_mesh_compound_system_deflection(
        self: "CastSelf",
    ) -> "_3151.AGMAGleasonConicalGearMeshCompoundSystemDeflection":
        from mastapy._private.system_model.analyses_and_results.system_deflections.compound import (
            _3151,
        )

        return self.__parent__._cast(
            _3151.AGMAGleasonConicalGearMeshCompoundSystemDeflection
        )

    @property
    def belt_connection_compound_system_deflection(
        self: "CastSelf",
    ) -> "_3155.BeltConnectionCompoundSystemDeflection":
        from mastapy._private.system_model.analyses_and_results.system_deflections.compound import (
            _3155,
        )

        return self.__parent__._cast(_3155.BeltConnectionCompoundSystemDeflection)

    @property
    def bevel_differential_gear_mesh_compound_system_deflection(
        self: "CastSelf",
    ) -> "_3158.BevelDifferentialGearMeshCompoundSystemDeflection":
        from mastapy._private.system_model.analyses_and_results.system_deflections.compound import (
            _3158,
        )

        return self.__parent__._cast(
            _3158.BevelDifferentialGearMeshCompoundSystemDeflection
        )

    @property
    def bevel_gear_mesh_compound_system_deflection(
        self: "CastSelf",
    ) -> "_3163.BevelGearMeshCompoundSystemDeflection":
        from mastapy._private.system_model.analyses_and_results.system_deflections.compound import (
            _3163,
        )

        return self.__parent__._cast(_3163.BevelGearMeshCompoundSystemDeflection)

    @property
    def clutch_connection_compound_system_deflection(
        self: "CastSelf",
    ) -> "_3168.ClutchConnectionCompoundSystemDeflection":
        from mastapy._private.system_model.analyses_and_results.system_deflections.compound import (
            _3168,
        )

        return self.__parent__._cast(_3168.ClutchConnectionCompoundSystemDeflection)

    @property
    def concept_coupling_connection_compound_system_deflection(
        self: "CastSelf",
    ) -> "_3173.ConceptCouplingConnectionCompoundSystemDeflection":
        from mastapy._private.system_model.analyses_and_results.system_deflections.compound import (
            _3173,
        )

        return self.__parent__._cast(
            _3173.ConceptCouplingConnectionCompoundSystemDeflection
        )

    @property
    def concept_gear_mesh_compound_system_deflection(
        self: "CastSelf",
    ) -> "_3176.ConceptGearMeshCompoundSystemDeflection":
        from mastapy._private.system_model.analyses_and_results.system_deflections.compound import (
            _3176,
        )

        return self.__parent__._cast(_3176.ConceptGearMeshCompoundSystemDeflection)

    @property
    def conical_gear_mesh_compound_system_deflection(
        self: "CastSelf",
    ) -> "_3179.ConicalGearMeshCompoundSystemDeflection":
        from mastapy._private.system_model.analyses_and_results.system_deflections.compound import (
            _3179,
        )

        return self.__parent__._cast(_3179.ConicalGearMeshCompoundSystemDeflection)

    @property
    def coupling_connection_compound_system_deflection(
        self: "CastSelf",
    ) -> "_3184.CouplingConnectionCompoundSystemDeflection":
        from mastapy._private.system_model.analyses_and_results.system_deflections.compound import (
            _3184,
        )

        return self.__parent__._cast(_3184.CouplingConnectionCompoundSystemDeflection)

    @property
    def cvt_belt_connection_compound_system_deflection(
        self: "CastSelf",
    ) -> "_3186.CVTBeltConnectionCompoundSystemDeflection":
        from mastapy._private.system_model.analyses_and_results.system_deflections.compound import (
            _3186,
        )

        return self.__parent__._cast(_3186.CVTBeltConnectionCompoundSystemDeflection)

    @property
    def cylindrical_gear_mesh_compound_system_deflection(
        self: "CastSelf",
    ) -> "_3194.CylindricalGearMeshCompoundSystemDeflection":
        from mastapy._private.system_model.analyses_and_results.system_deflections.compound import (
            _3194,
        )

        return self.__parent__._cast(_3194.CylindricalGearMeshCompoundSystemDeflection)

    @property
    def face_gear_mesh_compound_system_deflection(
        self: "CastSelf",
    ) -> "_3201.FaceGearMeshCompoundSystemDeflection":
        from mastapy._private.system_model.analyses_and_results.system_deflections.compound import (
            _3201,
        )

        return self.__parent__._cast(_3201.FaceGearMeshCompoundSystemDeflection)

    @property
    def gear_mesh_compound_system_deflection(
        self: "CastSelf",
    ) -> "_3206.GearMeshCompoundSystemDeflection":
        from mastapy._private.system_model.analyses_and_results.system_deflections.compound import (
            _3206,
        )

        return self.__parent__._cast(_3206.GearMeshCompoundSystemDeflection)

    @property
    def hypoid_gear_mesh_compound_system_deflection(
        self: "CastSelf",
    ) -> "_3210.HypoidGearMeshCompoundSystemDeflection":
        from mastapy._private.system_model.analyses_and_results.system_deflections.compound import (
            _3210,
        )

        return self.__parent__._cast(_3210.HypoidGearMeshCompoundSystemDeflection)

    @property
    def klingelnberg_cyclo_palloid_conical_gear_mesh_compound_system_deflection(
        self: "CastSelf",
    ) -> "_3214.KlingelnbergCycloPalloidConicalGearMeshCompoundSystemDeflection":
        from mastapy._private.system_model.analyses_and_results.system_deflections.compound import (
            _3214,
        )

        return self.__parent__._cast(
            _3214.KlingelnbergCycloPalloidConicalGearMeshCompoundSystemDeflection
        )

    @property
    def klingelnberg_cyclo_palloid_hypoid_gear_mesh_compound_system_deflection(
        self: "CastSelf",
    ) -> "_3217.KlingelnbergCycloPalloidHypoidGearMeshCompoundSystemDeflection":
        from mastapy._private.system_model.analyses_and_results.system_deflections.compound import (
            _3217,
        )

        return self.__parent__._cast(
            _3217.KlingelnbergCycloPalloidHypoidGearMeshCompoundSystemDeflection
        )

    @property
    def klingelnberg_cyclo_palloid_spiral_bevel_gear_mesh_compound_system_deflection(
        self: "CastSelf",
    ) -> "_3220.KlingelnbergCycloPalloidSpiralBevelGearMeshCompoundSystemDeflection":
        from mastapy._private.system_model.analyses_and_results.system_deflections.compound import (
            _3220,
        )

        return self.__parent__._cast(
            _3220.KlingelnbergCycloPalloidSpiralBevelGearMeshCompoundSystemDeflection
        )

    @property
    def part_to_part_shear_coupling_connection_compound_system_deflection(
        self: "CastSelf",
    ) -> "_3230.PartToPartShearCouplingConnectionCompoundSystemDeflection":
        from mastapy._private.system_model.analyses_and_results.system_deflections.compound import (
            _3230,
        )

        return self.__parent__._cast(
            _3230.PartToPartShearCouplingConnectionCompoundSystemDeflection
        )

    @property
    def ring_pins_to_disc_connection_compound_system_deflection(
        self: "CastSelf",
    ) -> "_3239.RingPinsToDiscConnectionCompoundSystemDeflection":
        from mastapy._private.system_model.analyses_and_results.system_deflections.compound import (
            _3239,
        )

        return self.__parent__._cast(
            _3239.RingPinsToDiscConnectionCompoundSystemDeflection
        )

    @property
    def rolling_ring_connection_compound_system_deflection(
        self: "CastSelf",
    ) -> "_3242.RollingRingConnectionCompoundSystemDeflection":
        from mastapy._private.system_model.analyses_and_results.system_deflections.compound import (
            _3242,
        )

        return self.__parent__._cast(
            _3242.RollingRingConnectionCompoundSystemDeflection
        )

    @property
    def spiral_bevel_gear_mesh_compound_system_deflection(
        self: "CastSelf",
    ) -> "_3250.SpiralBevelGearMeshCompoundSystemDeflection":
        from mastapy._private.system_model.analyses_and_results.system_deflections.compound import (
            _3250,
        )

        return self.__parent__._cast(_3250.SpiralBevelGearMeshCompoundSystemDeflection)

    @property
    def spring_damper_connection_compound_system_deflection(
        self: "CastSelf",
    ) -> "_3253.SpringDamperConnectionCompoundSystemDeflection":
        from mastapy._private.system_model.analyses_and_results.system_deflections.compound import (
            _3253,
        )

        return self.__parent__._cast(
            _3253.SpringDamperConnectionCompoundSystemDeflection
        )

    @property
    def straight_bevel_diff_gear_mesh_compound_system_deflection(
        self: "CastSelf",
    ) -> "_3256.StraightBevelDiffGearMeshCompoundSystemDeflection":
        from mastapy._private.system_model.analyses_and_results.system_deflections.compound import (
            _3256,
        )

        return self.__parent__._cast(
            _3256.StraightBevelDiffGearMeshCompoundSystemDeflection
        )

    @property
    def straight_bevel_gear_mesh_compound_system_deflection(
        self: "CastSelf",
    ) -> "_3259.StraightBevelGearMeshCompoundSystemDeflection":
        from mastapy._private.system_model.analyses_and_results.system_deflections.compound import (
            _3259,
        )

        return self.__parent__._cast(
            _3259.StraightBevelGearMeshCompoundSystemDeflection
        )

    @property
    def torque_converter_connection_compound_system_deflection(
        self: "CastSelf",
    ) -> "_3268.TorqueConverterConnectionCompoundSystemDeflection":
        from mastapy._private.system_model.analyses_and_results.system_deflections.compound import (
            _3268,
        )

        return self.__parent__._cast(
            _3268.TorqueConverterConnectionCompoundSystemDeflection
        )

    @property
    def worm_gear_mesh_compound_system_deflection(
        self: "CastSelf",
    ) -> "_3274.WormGearMeshCompoundSystemDeflection":
        from mastapy._private.system_model.analyses_and_results.system_deflections.compound import (
            _3274,
        )

        return self.__parent__._cast(_3274.WormGearMeshCompoundSystemDeflection)

    @property
    def zerol_bevel_gear_mesh_compound_system_deflection(
        self: "CastSelf",
    ) -> "_3277.ZerolBevelGearMeshCompoundSystemDeflection":
        from mastapy._private.system_model.analyses_and_results.system_deflections.compound import (
            _3277,
        )

        return self.__parent__._cast(_3277.ZerolBevelGearMeshCompoundSystemDeflection)

    @property
    def inter_mountable_component_connection_compound_system_deflection(
        self: "CastSelf",
    ) -> "InterMountableComponentConnectionCompoundSystemDeflection":
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
class InterMountableComponentConnectionCompoundSystemDeflection(
    _3181.ConnectionCompoundSystemDeflection
):
    """InterMountableComponentConnectionCompoundSystemDeflection

    This is a mastapy class.
    """

    TYPE: ClassVar["Type"] = (
        _INTER_MOUNTABLE_COMPONENT_CONNECTION_COMPOUND_SYSTEM_DEFLECTION
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
    ) -> "List[_3059.InterMountableComponentConnectionSystemDeflection]":
        """List[mastapy.system_model.analyses_and_results.system_deflections.InterMountableComponentConnectionSystemDeflection]

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
    ) -> "List[_3059.InterMountableComponentConnectionSystemDeflection]":
        """List[mastapy.system_model.analyses_and_results.system_deflections.InterMountableComponentConnectionSystemDeflection]

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
    ) -> "_Cast_InterMountableComponentConnectionCompoundSystemDeflection":
        """Cast to another type.

        Returns:
            _Cast_InterMountableComponentConnectionCompoundSystemDeflection
        """
        return _Cast_InterMountableComponentConnectionCompoundSystemDeflection(self)
