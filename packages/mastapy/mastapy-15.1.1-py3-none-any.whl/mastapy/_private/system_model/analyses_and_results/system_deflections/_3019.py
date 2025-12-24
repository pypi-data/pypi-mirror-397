"""ConnectionSystemDeflection"""

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
from mastapy._private.system_model.analyses_and_results.analysis_cases import _7936

_CONNECTION_SYSTEM_DEFLECTION = python_net_import(
    "SMT.MastaAPI.SystemModel.AnalysesAndResults.SystemDeflections",
    "ConnectionSystemDeflection",
)

if TYPE_CHECKING:
    from typing import Any, Type, TypeVar

    from mastapy._private.materials.efficiency import _407
    from mastapy._private.system_model.analyses_and_results import _2941, _2943, _2945
    from mastapy._private.system_model.analyses_and_results.analysis_cases import (
        _7934,
        _7937,
    )
    from mastapy._private.system_model.analyses_and_results.power_flows import _4380
    from mastapy._private.system_model.analyses_and_results.system_deflections import (
        _2980,
        _2981,
        _2991,
        _2993,
        _2998,
        _3003,
        _3006,
        _3009,
        _3012,
        _3016,
        _3021,
        _3024,
        _3028,
        _3029,
        _3031,
        _3032,
        _3033,
        _3046,
        _3051,
        _3055,
        _3059,
        _3060,
        _3063,
        _3066,
        _3080,
        _3083,
        _3089,
        _3092,
        _3099,
        _3101,
        _3104,
        _3107,
        _3110,
        _3119,
        _3122,
        _3131,
        _3134,
    )
    from mastapy._private.system_model.connections_and_sockets import _2531

    Self = TypeVar("Self", bound="ConnectionSystemDeflection")
    CastSelf = TypeVar(
        "CastSelf", bound="ConnectionSystemDeflection._Cast_ConnectionSystemDeflection"
    )


__docformat__ = "restructuredtext en"
__all__ = ("ConnectionSystemDeflection",)


@extended_dataclass(frozen=True, slots=True, weakref_slot=True)
class _Cast_ConnectionSystemDeflection:
    """Special nested class for casting ConnectionSystemDeflection to subclasses."""

    __parent__: "ConnectionSystemDeflection"

    @property
    def connection_fe_analysis(self: "CastSelf") -> "_7936.ConnectionFEAnalysis":
        return self.__parent__._cast(_7936.ConnectionFEAnalysis)

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
    def abstract_shaft_to_mountable_component_connection_system_deflection(
        self: "CastSelf",
    ) -> "_2980.AbstractShaftToMountableComponentConnectionSystemDeflection":
        from mastapy._private.system_model.analyses_and_results.system_deflections import (
            _2980,
        )

        return self.__parent__._cast(
            _2980.AbstractShaftToMountableComponentConnectionSystemDeflection
        )

    @property
    def agma_gleason_conical_gear_mesh_system_deflection(
        self: "CastSelf",
    ) -> "_2981.AGMAGleasonConicalGearMeshSystemDeflection":
        from mastapy._private.system_model.analyses_and_results.system_deflections import (
            _2981,
        )

        return self.__parent__._cast(_2981.AGMAGleasonConicalGearMeshSystemDeflection)

    @property
    def belt_connection_system_deflection(
        self: "CastSelf",
    ) -> "_2991.BeltConnectionSystemDeflection":
        from mastapy._private.system_model.analyses_and_results.system_deflections import (
            _2991,
        )

        return self.__parent__._cast(_2991.BeltConnectionSystemDeflection)

    @property
    def bevel_differential_gear_mesh_system_deflection(
        self: "CastSelf",
    ) -> "_2993.BevelDifferentialGearMeshSystemDeflection":
        from mastapy._private.system_model.analyses_and_results.system_deflections import (
            _2993,
        )

        return self.__parent__._cast(_2993.BevelDifferentialGearMeshSystemDeflection)

    @property
    def bevel_gear_mesh_system_deflection(
        self: "CastSelf",
    ) -> "_2998.BevelGearMeshSystemDeflection":
        from mastapy._private.system_model.analyses_and_results.system_deflections import (
            _2998,
        )

        return self.__parent__._cast(_2998.BevelGearMeshSystemDeflection)

    @property
    def clutch_connection_system_deflection(
        self: "CastSelf",
    ) -> "_3003.ClutchConnectionSystemDeflection":
        from mastapy._private.system_model.analyses_and_results.system_deflections import (
            _3003,
        )

        return self.__parent__._cast(_3003.ClutchConnectionSystemDeflection)

    @property
    def coaxial_connection_system_deflection(
        self: "CastSelf",
    ) -> "_3006.CoaxialConnectionSystemDeflection":
        from mastapy._private.system_model.analyses_and_results.system_deflections import (
            _3006,
        )

        return self.__parent__._cast(_3006.CoaxialConnectionSystemDeflection)

    @property
    def concept_coupling_connection_system_deflection(
        self: "CastSelf",
    ) -> "_3009.ConceptCouplingConnectionSystemDeflection":
        from mastapy._private.system_model.analyses_and_results.system_deflections import (
            _3009,
        )

        return self.__parent__._cast(_3009.ConceptCouplingConnectionSystemDeflection)

    @property
    def concept_gear_mesh_system_deflection(
        self: "CastSelf",
    ) -> "_3012.ConceptGearMeshSystemDeflection":
        from mastapy._private.system_model.analyses_and_results.system_deflections import (
            _3012,
        )

        return self.__parent__._cast(_3012.ConceptGearMeshSystemDeflection)

    @property
    def conical_gear_mesh_system_deflection(
        self: "CastSelf",
    ) -> "_3016.ConicalGearMeshSystemDeflection":
        from mastapy._private.system_model.analyses_and_results.system_deflections import (
            _3016,
        )

        return self.__parent__._cast(_3016.ConicalGearMeshSystemDeflection)

    @property
    def coupling_connection_system_deflection(
        self: "CastSelf",
    ) -> "_3021.CouplingConnectionSystemDeflection":
        from mastapy._private.system_model.analyses_and_results.system_deflections import (
            _3021,
        )

        return self.__parent__._cast(_3021.CouplingConnectionSystemDeflection)

    @property
    def cvt_belt_connection_system_deflection(
        self: "CastSelf",
    ) -> "_3024.CVTBeltConnectionSystemDeflection":
        from mastapy._private.system_model.analyses_and_results.system_deflections import (
            _3024,
        )

        return self.__parent__._cast(_3024.CVTBeltConnectionSystemDeflection)

    @property
    def cycloidal_disc_central_bearing_connection_system_deflection(
        self: "CastSelf",
    ) -> "_3028.CycloidalDiscCentralBearingConnectionSystemDeflection":
        from mastapy._private.system_model.analyses_and_results.system_deflections import (
            _3028,
        )

        return self.__parent__._cast(
            _3028.CycloidalDiscCentralBearingConnectionSystemDeflection
        )

    @property
    def cycloidal_disc_planetary_bearing_connection_system_deflection(
        self: "CastSelf",
    ) -> "_3029.CycloidalDiscPlanetaryBearingConnectionSystemDeflection":
        from mastapy._private.system_model.analyses_and_results.system_deflections import (
            _3029,
        )

        return self.__parent__._cast(
            _3029.CycloidalDiscPlanetaryBearingConnectionSystemDeflection
        )

    @property
    def cylindrical_gear_mesh_system_deflection(
        self: "CastSelf",
    ) -> "_3031.CylindricalGearMeshSystemDeflection":
        from mastapy._private.system_model.analyses_and_results.system_deflections import (
            _3031,
        )

        return self.__parent__._cast(_3031.CylindricalGearMeshSystemDeflection)

    @property
    def cylindrical_gear_mesh_system_deflection_timestep(
        self: "CastSelf",
    ) -> "_3032.CylindricalGearMeshSystemDeflectionTimestep":
        from mastapy._private.system_model.analyses_and_results.system_deflections import (
            _3032,
        )

        return self.__parent__._cast(_3032.CylindricalGearMeshSystemDeflectionTimestep)

    @property
    def cylindrical_gear_mesh_system_deflection_with_ltca_results(
        self: "CastSelf",
    ) -> "_3033.CylindricalGearMeshSystemDeflectionWithLTCAResults":
        from mastapy._private.system_model.analyses_and_results.system_deflections import (
            _3033,
        )

        return self.__parent__._cast(
            _3033.CylindricalGearMeshSystemDeflectionWithLTCAResults
        )

    @property
    def face_gear_mesh_system_deflection(
        self: "CastSelf",
    ) -> "_3046.FaceGearMeshSystemDeflection":
        from mastapy._private.system_model.analyses_and_results.system_deflections import (
            _3046,
        )

        return self.__parent__._cast(_3046.FaceGearMeshSystemDeflection)

    @property
    def gear_mesh_system_deflection(
        self: "CastSelf",
    ) -> "_3051.GearMeshSystemDeflection":
        from mastapy._private.system_model.analyses_and_results.system_deflections import (
            _3051,
        )

        return self.__parent__._cast(_3051.GearMeshSystemDeflection)

    @property
    def hypoid_gear_mesh_system_deflection(
        self: "CastSelf",
    ) -> "_3055.HypoidGearMeshSystemDeflection":
        from mastapy._private.system_model.analyses_and_results.system_deflections import (
            _3055,
        )

        return self.__parent__._cast(_3055.HypoidGearMeshSystemDeflection)

    @property
    def inter_mountable_component_connection_system_deflection(
        self: "CastSelf",
    ) -> "_3059.InterMountableComponentConnectionSystemDeflection":
        from mastapy._private.system_model.analyses_and_results.system_deflections import (
            _3059,
        )

        return self.__parent__._cast(
            _3059.InterMountableComponentConnectionSystemDeflection
        )

    @property
    def klingelnberg_cyclo_palloid_conical_gear_mesh_system_deflection(
        self: "CastSelf",
    ) -> "_3060.KlingelnbergCycloPalloidConicalGearMeshSystemDeflection":
        from mastapy._private.system_model.analyses_and_results.system_deflections import (
            _3060,
        )

        return self.__parent__._cast(
            _3060.KlingelnbergCycloPalloidConicalGearMeshSystemDeflection
        )

    @property
    def klingelnberg_cyclo_palloid_hypoid_gear_mesh_system_deflection(
        self: "CastSelf",
    ) -> "_3063.KlingelnbergCycloPalloidHypoidGearMeshSystemDeflection":
        from mastapy._private.system_model.analyses_and_results.system_deflections import (
            _3063,
        )

        return self.__parent__._cast(
            _3063.KlingelnbergCycloPalloidHypoidGearMeshSystemDeflection
        )

    @property
    def klingelnberg_cyclo_palloid_spiral_bevel_gear_mesh_system_deflection(
        self: "CastSelf",
    ) -> "_3066.KlingelnbergCycloPalloidSpiralBevelGearMeshSystemDeflection":
        from mastapy._private.system_model.analyses_and_results.system_deflections import (
            _3066,
        )

        return self.__parent__._cast(
            _3066.KlingelnbergCycloPalloidSpiralBevelGearMeshSystemDeflection
        )

    @property
    def part_to_part_shear_coupling_connection_system_deflection(
        self: "CastSelf",
    ) -> "_3080.PartToPartShearCouplingConnectionSystemDeflection":
        from mastapy._private.system_model.analyses_and_results.system_deflections import (
            _3080,
        )

        return self.__parent__._cast(
            _3080.PartToPartShearCouplingConnectionSystemDeflection
        )

    @property
    def planetary_connection_system_deflection(
        self: "CastSelf",
    ) -> "_3083.PlanetaryConnectionSystemDeflection":
        from mastapy._private.system_model.analyses_and_results.system_deflections import (
            _3083,
        )

        return self.__parent__._cast(_3083.PlanetaryConnectionSystemDeflection)

    @property
    def ring_pins_to_disc_connection_system_deflection(
        self: "CastSelf",
    ) -> "_3089.RingPinsToDiscConnectionSystemDeflection":
        from mastapy._private.system_model.analyses_and_results.system_deflections import (
            _3089,
        )

        return self.__parent__._cast(_3089.RingPinsToDiscConnectionSystemDeflection)

    @property
    def rolling_ring_connection_system_deflection(
        self: "CastSelf",
    ) -> "_3092.RollingRingConnectionSystemDeflection":
        from mastapy._private.system_model.analyses_and_results.system_deflections import (
            _3092,
        )

        return self.__parent__._cast(_3092.RollingRingConnectionSystemDeflection)

    @property
    def shaft_to_mountable_component_connection_system_deflection(
        self: "CastSelf",
    ) -> "_3099.ShaftToMountableComponentConnectionSystemDeflection":
        from mastapy._private.system_model.analyses_and_results.system_deflections import (
            _3099,
        )

        return self.__parent__._cast(
            _3099.ShaftToMountableComponentConnectionSystemDeflection
        )

    @property
    def spiral_bevel_gear_mesh_system_deflection(
        self: "CastSelf",
    ) -> "_3101.SpiralBevelGearMeshSystemDeflection":
        from mastapy._private.system_model.analyses_and_results.system_deflections import (
            _3101,
        )

        return self.__parent__._cast(_3101.SpiralBevelGearMeshSystemDeflection)

    @property
    def spring_damper_connection_system_deflection(
        self: "CastSelf",
    ) -> "_3104.SpringDamperConnectionSystemDeflection":
        from mastapy._private.system_model.analyses_and_results.system_deflections import (
            _3104,
        )

        return self.__parent__._cast(_3104.SpringDamperConnectionSystemDeflection)

    @property
    def straight_bevel_diff_gear_mesh_system_deflection(
        self: "CastSelf",
    ) -> "_3107.StraightBevelDiffGearMeshSystemDeflection":
        from mastapy._private.system_model.analyses_and_results.system_deflections import (
            _3107,
        )

        return self.__parent__._cast(_3107.StraightBevelDiffGearMeshSystemDeflection)

    @property
    def straight_bevel_gear_mesh_system_deflection(
        self: "CastSelf",
    ) -> "_3110.StraightBevelGearMeshSystemDeflection":
        from mastapy._private.system_model.analyses_and_results.system_deflections import (
            _3110,
        )

        return self.__parent__._cast(_3110.StraightBevelGearMeshSystemDeflection)

    @property
    def torque_converter_connection_system_deflection(
        self: "CastSelf",
    ) -> "_3122.TorqueConverterConnectionSystemDeflection":
        from mastapy._private.system_model.analyses_and_results.system_deflections import (
            _3122,
        )

        return self.__parent__._cast(_3122.TorqueConverterConnectionSystemDeflection)

    @property
    def worm_gear_mesh_system_deflection(
        self: "CastSelf",
    ) -> "_3131.WormGearMeshSystemDeflection":
        from mastapy._private.system_model.analyses_and_results.system_deflections import (
            _3131,
        )

        return self.__parent__._cast(_3131.WormGearMeshSystemDeflection)

    @property
    def zerol_bevel_gear_mesh_system_deflection(
        self: "CastSelf",
    ) -> "_3134.ZerolBevelGearMeshSystemDeflection":
        from mastapy._private.system_model.analyses_and_results.system_deflections import (
            _3134,
        )

        return self.__parent__._cast(_3134.ZerolBevelGearMeshSystemDeflection)

    @property
    def connection_system_deflection(self: "CastSelf") -> "ConnectionSystemDeflection":
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
class ConnectionSystemDeflection(_7936.ConnectionFEAnalysis):
    """ConnectionSystemDeflection

    This is a mastapy class.
    """

    TYPE: ClassVar["Type"] = _CONNECTION_SYSTEM_DEFLECTION

    wrapped: "Any"

    def __post_init__(self: "Self") -> None:
        """Override of the post initialisation magic method."""
        if not hasattr(self.wrapped, "reference_count"):
            self.wrapped.reference_count = 0

        self.wrapped.reference_count += 1

    @property
    @exception_bridge
    def convergence_status(self: "Self") -> "float":
        """float

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "ConvergenceStatus")

        if temp is None:
            return 0.0

        return temp

    @property
    @exception_bridge
    def efficiency(self: "Self") -> "float":
        """float

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "Efficiency")

        if temp is None:
            return 0.0

        return temp

    @property
    @exception_bridge
    def energy_loss_during_load_case(self: "Self") -> "float":
        """float

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "EnergyLossDuringLoadCase")

        if temp is None:
            return 0.0

        return temp

    @property
    @exception_bridge
    def has_converged(self: "Self") -> "bool":
        """bool

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "HasConverged")

        if temp is None:
            return False

        return temp

    @property
    @exception_bridge
    def is_loaded(self: "Self") -> "bool":
        """bool

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "IsLoaded")

        if temp is None:
            return False

        return temp

    @property
    @exception_bridge
    def largest_power(self: "Self") -> "float":
        """float

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "LargestPower")

        if temp is None:
            return 0.0

        return temp

    @property
    @exception_bridge
    def percentage_of_iterations_converged(self: "Self") -> "float":
        """float

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "PercentageOfIterationsConverged")

        if temp is None:
            return 0.0

        return temp

    @property
    @exception_bridge
    def reason_for_non_convergence(self: "Self") -> "str":
        """str

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "ReasonForNonConvergence")

        if temp is None:
            return ""

        return temp

    @property
    @exception_bridge
    def relaxation(self: "Self") -> "float":
        """float

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "Relaxation")

        if temp is None:
            return 0.0

        return temp

    @property
    @exception_bridge
    def socket_a_planetary_power(self: "Self") -> "float":
        """float

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "SocketAPlanetaryPower")

        if temp is None:
            return 0.0

        return temp

    @property
    @exception_bridge
    def socket_a_planetary_torque(self: "Self") -> "float":
        """float

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "SocketAPlanetaryTorque")

        if temp is None:
            return 0.0

        return temp

    @property
    @exception_bridge
    def socket_a_power(self: "Self") -> "float":
        """float

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "SocketAPower")

        if temp is None:
            return 0.0

        return temp

    @property
    @exception_bridge
    def socket_a_torque(self: "Self") -> "float":
        """float

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "SocketATorque")

        if temp is None:
            return 0.0

        return temp

    @property
    @exception_bridge
    def socket_a_total_power(self: "Self") -> "float":
        """float

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "SocketATotalPower")

        if temp is None:
            return 0.0

        return temp

    @property
    @exception_bridge
    def socket_b_planetary_power(self: "Self") -> "float":
        """float

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "SocketBPlanetaryPower")

        if temp is None:
            return 0.0

        return temp

    @property
    @exception_bridge
    def socket_b_planetary_torque(self: "Self") -> "float":
        """float

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "SocketBPlanetaryTorque")

        if temp is None:
            return 0.0

        return temp

    @property
    @exception_bridge
    def socket_b_power(self: "Self") -> "float":
        """float

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "SocketBPower")

        if temp is None:
            return 0.0

        return temp

    @property
    @exception_bridge
    def socket_b_torque(self: "Self") -> "float":
        """float

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "SocketBTorque")

        if temp is None:
            return 0.0

        return temp

    @property
    @exception_bridge
    def socket_b_total_power(self: "Self") -> "float":
        """float

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "SocketBTotalPower")

        if temp is None:
            return 0.0

        return temp

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
    def power_loss(self: "Self") -> "_407.PowerLoss":
        """mastapy.materials.efficiency.PowerLoss

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "PowerLoss")

        if temp is None:
            return None

        type_ = temp.GetType()
        return constructor.new(type_.Namespace, type_.Name)(temp)

    @property
    @exception_bridge
    def system_deflection(self: "Self") -> "_3119.SystemDeflection":
        """mastapy.system_model.analyses_and_results.system_deflections.SystemDeflection

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "SystemDeflection")

        if temp is None:
            return None

        type_ = temp.GetType()
        return constructor.new(type_.Namespace, type_.Name)(temp)

    @property
    @exception_bridge
    def power_flow_results(self: "Self") -> "_4380.ConnectionPowerFlow":
        """mastapy.system_model.analyses_and_results.power_flows.ConnectionPowerFlow

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "PowerFlowResults")

        if temp is None:
            return None

        type_ = temp.GetType()
        return constructor.new(type_.Namespace, type_.Name)(temp)

    @property
    def cast_to(self: "Self") -> "_Cast_ConnectionSystemDeflection":
        """Cast to another type.

        Returns:
            _Cast_ConnectionSystemDeflection
        """
        return _Cast_ConnectionSystemDeflection(self)
