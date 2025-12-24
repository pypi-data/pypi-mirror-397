"""ConnectionPowerFlow"""

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

_CONNECTION_POWER_FLOW = python_net_import(
    "SMT.MastaAPI.SystemModel.AnalysesAndResults.PowerFlows", "ConnectionPowerFlow"
)

if TYPE_CHECKING:
    from typing import Any, Type, TypeVar

    from mastapy._private.system_model.analyses_and_results import _2941, _2943, _2945
    from mastapy._private.system_model.analyses_and_results.analysis_cases import _7934
    from mastapy._private.system_model.analyses_and_results.power_flows import (
        _4348,
        _4349,
        _4354,
        _4356,
        _4361,
        _4366,
        _4369,
        _4371,
        _4374,
        _4377,
        _4382,
        _4385,
        _4389,
        _4390,
        _4393,
        _4399,
        _4406,
        _4410,
        _4413,
        _4414,
        _4417,
        _4420,
        _4430,
        _4433,
        _4437,
        _4442,
        _4444,
        _4449,
        _4451,
        _4454,
        _4457,
        _4460,
        _4470,
        _4476,
        _4479,
    )
    from mastapy._private.system_model.analyses_and_results.system_deflections import (
        _3019,
    )
    from mastapy._private.system_model.connections_and_sockets import _2531

    Self = TypeVar("Self", bound="ConnectionPowerFlow")
    CastSelf = TypeVar(
        "CastSelf", bound="ConnectionPowerFlow._Cast_ConnectionPowerFlow"
    )


__docformat__ = "restructuredtext en"
__all__ = ("ConnectionPowerFlow",)


@extended_dataclass(frozen=True, slots=True, weakref_slot=True)
class _Cast_ConnectionPowerFlow:
    """Special nested class for casting ConnectionPowerFlow to subclasses."""

    __parent__: "ConnectionPowerFlow"

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
    def abstract_shaft_to_mountable_component_connection_power_flow(
        self: "CastSelf",
    ) -> "_4348.AbstractShaftToMountableComponentConnectionPowerFlow":
        from mastapy._private.system_model.analyses_and_results.power_flows import _4348

        return self.__parent__._cast(
            _4348.AbstractShaftToMountableComponentConnectionPowerFlow
        )

    @property
    def agma_gleason_conical_gear_mesh_power_flow(
        self: "CastSelf",
    ) -> "_4349.AGMAGleasonConicalGearMeshPowerFlow":
        from mastapy._private.system_model.analyses_and_results.power_flows import _4349

        return self.__parent__._cast(_4349.AGMAGleasonConicalGearMeshPowerFlow)

    @property
    def belt_connection_power_flow(self: "CastSelf") -> "_4354.BeltConnectionPowerFlow":
        from mastapy._private.system_model.analyses_and_results.power_flows import _4354

        return self.__parent__._cast(_4354.BeltConnectionPowerFlow)

    @property
    def bevel_differential_gear_mesh_power_flow(
        self: "CastSelf",
    ) -> "_4356.BevelDifferentialGearMeshPowerFlow":
        from mastapy._private.system_model.analyses_and_results.power_flows import _4356

        return self.__parent__._cast(_4356.BevelDifferentialGearMeshPowerFlow)

    @property
    def bevel_gear_mesh_power_flow(self: "CastSelf") -> "_4361.BevelGearMeshPowerFlow":
        from mastapy._private.system_model.analyses_and_results.power_flows import _4361

        return self.__parent__._cast(_4361.BevelGearMeshPowerFlow)

    @property
    def clutch_connection_power_flow(
        self: "CastSelf",
    ) -> "_4366.ClutchConnectionPowerFlow":
        from mastapy._private.system_model.analyses_and_results.power_flows import _4366

        return self.__parent__._cast(_4366.ClutchConnectionPowerFlow)

    @property
    def coaxial_connection_power_flow(
        self: "CastSelf",
    ) -> "_4369.CoaxialConnectionPowerFlow":
        from mastapy._private.system_model.analyses_and_results.power_flows import _4369

        return self.__parent__._cast(_4369.CoaxialConnectionPowerFlow)

    @property
    def concept_coupling_connection_power_flow(
        self: "CastSelf",
    ) -> "_4371.ConceptCouplingConnectionPowerFlow":
        from mastapy._private.system_model.analyses_and_results.power_flows import _4371

        return self.__parent__._cast(_4371.ConceptCouplingConnectionPowerFlow)

    @property
    def concept_gear_mesh_power_flow(
        self: "CastSelf",
    ) -> "_4374.ConceptGearMeshPowerFlow":
        from mastapy._private.system_model.analyses_and_results.power_flows import _4374

        return self.__parent__._cast(_4374.ConceptGearMeshPowerFlow)

    @property
    def conical_gear_mesh_power_flow(
        self: "CastSelf",
    ) -> "_4377.ConicalGearMeshPowerFlow":
        from mastapy._private.system_model.analyses_and_results.power_flows import _4377

        return self.__parent__._cast(_4377.ConicalGearMeshPowerFlow)

    @property
    def coupling_connection_power_flow(
        self: "CastSelf",
    ) -> "_4382.CouplingConnectionPowerFlow":
        from mastapy._private.system_model.analyses_and_results.power_flows import _4382

        return self.__parent__._cast(_4382.CouplingConnectionPowerFlow)

    @property
    def cvt_belt_connection_power_flow(
        self: "CastSelf",
    ) -> "_4385.CVTBeltConnectionPowerFlow":
        from mastapy._private.system_model.analyses_and_results.power_flows import _4385

        return self.__parent__._cast(_4385.CVTBeltConnectionPowerFlow)

    @property
    def cycloidal_disc_central_bearing_connection_power_flow(
        self: "CastSelf",
    ) -> "_4389.CycloidalDiscCentralBearingConnectionPowerFlow":
        from mastapy._private.system_model.analyses_and_results.power_flows import _4389

        return self.__parent__._cast(
            _4389.CycloidalDiscCentralBearingConnectionPowerFlow
        )

    @property
    def cycloidal_disc_planetary_bearing_connection_power_flow(
        self: "CastSelf",
    ) -> "_4390.CycloidalDiscPlanetaryBearingConnectionPowerFlow":
        from mastapy._private.system_model.analyses_and_results.power_flows import _4390

        return self.__parent__._cast(
            _4390.CycloidalDiscPlanetaryBearingConnectionPowerFlow
        )

    @property
    def cylindrical_gear_mesh_power_flow(
        self: "CastSelf",
    ) -> "_4393.CylindricalGearMeshPowerFlow":
        from mastapy._private.system_model.analyses_and_results.power_flows import _4393

        return self.__parent__._cast(_4393.CylindricalGearMeshPowerFlow)

    @property
    def face_gear_mesh_power_flow(self: "CastSelf") -> "_4399.FaceGearMeshPowerFlow":
        from mastapy._private.system_model.analyses_and_results.power_flows import _4399

        return self.__parent__._cast(_4399.FaceGearMeshPowerFlow)

    @property
    def gear_mesh_power_flow(self: "CastSelf") -> "_4406.GearMeshPowerFlow":
        from mastapy._private.system_model.analyses_and_results.power_flows import _4406

        return self.__parent__._cast(_4406.GearMeshPowerFlow)

    @property
    def hypoid_gear_mesh_power_flow(
        self: "CastSelf",
    ) -> "_4410.HypoidGearMeshPowerFlow":
        from mastapy._private.system_model.analyses_and_results.power_flows import _4410

        return self.__parent__._cast(_4410.HypoidGearMeshPowerFlow)

    @property
    def inter_mountable_component_connection_power_flow(
        self: "CastSelf",
    ) -> "_4413.InterMountableComponentConnectionPowerFlow":
        from mastapy._private.system_model.analyses_and_results.power_flows import _4413

        return self.__parent__._cast(_4413.InterMountableComponentConnectionPowerFlow)

    @property
    def klingelnberg_cyclo_palloid_conical_gear_mesh_power_flow(
        self: "CastSelf",
    ) -> "_4414.KlingelnbergCycloPalloidConicalGearMeshPowerFlow":
        from mastapy._private.system_model.analyses_and_results.power_flows import _4414

        return self.__parent__._cast(
            _4414.KlingelnbergCycloPalloidConicalGearMeshPowerFlow
        )

    @property
    def klingelnberg_cyclo_palloid_hypoid_gear_mesh_power_flow(
        self: "CastSelf",
    ) -> "_4417.KlingelnbergCycloPalloidHypoidGearMeshPowerFlow":
        from mastapy._private.system_model.analyses_and_results.power_flows import _4417

        return self.__parent__._cast(
            _4417.KlingelnbergCycloPalloidHypoidGearMeshPowerFlow
        )

    @property
    def klingelnberg_cyclo_palloid_spiral_bevel_gear_mesh_power_flow(
        self: "CastSelf",
    ) -> "_4420.KlingelnbergCycloPalloidSpiralBevelGearMeshPowerFlow":
        from mastapy._private.system_model.analyses_and_results.power_flows import _4420

        return self.__parent__._cast(
            _4420.KlingelnbergCycloPalloidSpiralBevelGearMeshPowerFlow
        )

    @property
    def part_to_part_shear_coupling_connection_power_flow(
        self: "CastSelf",
    ) -> "_4430.PartToPartShearCouplingConnectionPowerFlow":
        from mastapy._private.system_model.analyses_and_results.power_flows import _4430

        return self.__parent__._cast(_4430.PartToPartShearCouplingConnectionPowerFlow)

    @property
    def planetary_connection_power_flow(
        self: "CastSelf",
    ) -> "_4433.PlanetaryConnectionPowerFlow":
        from mastapy._private.system_model.analyses_and_results.power_flows import _4433

        return self.__parent__._cast(_4433.PlanetaryConnectionPowerFlow)

    @property
    def ring_pins_to_disc_connection_power_flow(
        self: "CastSelf",
    ) -> "_4442.RingPinsToDiscConnectionPowerFlow":
        from mastapy._private.system_model.analyses_and_results.power_flows import _4442

        return self.__parent__._cast(_4442.RingPinsToDiscConnectionPowerFlow)

    @property
    def rolling_ring_connection_power_flow(
        self: "CastSelf",
    ) -> "_4444.RollingRingConnectionPowerFlow":
        from mastapy._private.system_model.analyses_and_results.power_flows import _4444

        return self.__parent__._cast(_4444.RollingRingConnectionPowerFlow)

    @property
    def shaft_to_mountable_component_connection_power_flow(
        self: "CastSelf",
    ) -> "_4449.ShaftToMountableComponentConnectionPowerFlow":
        from mastapy._private.system_model.analyses_and_results.power_flows import _4449

        return self.__parent__._cast(_4449.ShaftToMountableComponentConnectionPowerFlow)

    @property
    def spiral_bevel_gear_mesh_power_flow(
        self: "CastSelf",
    ) -> "_4451.SpiralBevelGearMeshPowerFlow":
        from mastapy._private.system_model.analyses_and_results.power_flows import _4451

        return self.__parent__._cast(_4451.SpiralBevelGearMeshPowerFlow)

    @property
    def spring_damper_connection_power_flow(
        self: "CastSelf",
    ) -> "_4454.SpringDamperConnectionPowerFlow":
        from mastapy._private.system_model.analyses_and_results.power_flows import _4454

        return self.__parent__._cast(_4454.SpringDamperConnectionPowerFlow)

    @property
    def straight_bevel_diff_gear_mesh_power_flow(
        self: "CastSelf",
    ) -> "_4457.StraightBevelDiffGearMeshPowerFlow":
        from mastapy._private.system_model.analyses_and_results.power_flows import _4457

        return self.__parent__._cast(_4457.StraightBevelDiffGearMeshPowerFlow)

    @property
    def straight_bevel_gear_mesh_power_flow(
        self: "CastSelf",
    ) -> "_4460.StraightBevelGearMeshPowerFlow":
        from mastapy._private.system_model.analyses_and_results.power_flows import _4460

        return self.__parent__._cast(_4460.StraightBevelGearMeshPowerFlow)

    @property
    def torque_converter_connection_power_flow(
        self: "CastSelf",
    ) -> "_4470.TorqueConverterConnectionPowerFlow":
        from mastapy._private.system_model.analyses_and_results.power_flows import _4470

        return self.__parent__._cast(_4470.TorqueConverterConnectionPowerFlow)

    @property
    def worm_gear_mesh_power_flow(self: "CastSelf") -> "_4476.WormGearMeshPowerFlow":
        from mastapy._private.system_model.analyses_and_results.power_flows import _4476

        return self.__parent__._cast(_4476.WormGearMeshPowerFlow)

    @property
    def zerol_bevel_gear_mesh_power_flow(
        self: "CastSelf",
    ) -> "_4479.ZerolBevelGearMeshPowerFlow":
        from mastapy._private.system_model.analyses_and_results.power_flows import _4479

        return self.__parent__._cast(_4479.ZerolBevelGearMeshPowerFlow)

    @property
    def connection_power_flow(self: "CastSelf") -> "ConnectionPowerFlow":
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
class ConnectionPowerFlow(_7937.ConnectionStaticLoadAnalysisCase):
    """ConnectionPowerFlow

    This is a mastapy class.
    """

    TYPE: ClassVar["Type"] = _CONNECTION_POWER_FLOW

    wrapped: "Any"

    def __post_init__(self: "Self") -> None:
        """Override of the post initialisation magic method."""
        if not hasattr(self.wrapped, "reference_count"):
            self.wrapped.reference_count = 0

        self.wrapped.reference_count += 1

    @property
    @exception_bridge
    def is_transmitting_power(self: "Self") -> "bool":
        """bool

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "IsTransmittingPower")

        if temp is None:
            return False

        return temp

    @property
    @exception_bridge
    def relative_speed(self: "Self") -> "float":
        """float

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "RelativeSpeed")

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
    def power_flow(self: "Self") -> "_4437.PowerFlow":
        """mastapy.system_model.analyses_and_results.power_flows.PowerFlow

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "PowerFlow")

        if temp is None:
            return None

        type_ = temp.GetType()
        return constructor.new(type_.Namespace, type_.Name)(temp)

    @property
    @exception_bridge
    def torsional_system_deflection_analysis(
        self: "Self",
    ) -> "_3019.ConnectionSystemDeflection":
        """mastapy.system_model.analyses_and_results.system_deflections.ConnectionSystemDeflection

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "TorsionalSystemDeflectionAnalysis")

        if temp is None:
            return None

        type_ = temp.GetType()
        return constructor.new(type_.Namespace, type_.Name)(temp)

    @property
    def cast_to(self: "Self") -> "_Cast_ConnectionPowerFlow":
        """Cast to another type.

        Returns:
            _Cast_ConnectionPowerFlow
        """
        return _Cast_ConnectionPowerFlow(self)
