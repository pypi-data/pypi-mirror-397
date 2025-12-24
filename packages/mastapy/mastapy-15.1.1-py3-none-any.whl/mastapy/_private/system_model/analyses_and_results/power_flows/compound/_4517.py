"""ConnectionCompoundPowerFlow"""

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

_CONNECTION_COMPOUND_POWER_FLOW = python_net_import(
    "SMT.MastaAPI.SystemModel.AnalysesAndResults.PowerFlows.Compound",
    "ConnectionCompoundPowerFlow",
)

if TYPE_CHECKING:
    from typing import Any, List, Type, TypeVar

    from mastapy._private.system_model.analyses_and_results import _2943
    from mastapy._private.system_model.analyses_and_results.analysis_cases import _7939
    from mastapy._private.system_model.analyses_and_results.power_flows import _4380
    from mastapy._private.system_model.analyses_and_results.power_flows.compound import (
        _4485,
        _4487,
        _4491,
        _4494,
        _4499,
        _4504,
        _4506,
        _4509,
        _4512,
        _4515,
        _4520,
        _4522,
        _4526,
        _4528,
        _4530,
        _4536,
        _4541,
        _4545,
        _4547,
        _4549,
        _4552,
        _4555,
        _4565,
        _4567,
        _4574,
        _4577,
        _4581,
        _4584,
        _4587,
        _4590,
        _4593,
        _4602,
        _4608,
        _4611,
    )

    Self = TypeVar("Self", bound="ConnectionCompoundPowerFlow")
    CastSelf = TypeVar(
        "CastSelf",
        bound="ConnectionCompoundPowerFlow._Cast_ConnectionCompoundPowerFlow",
    )


__docformat__ = "restructuredtext en"
__all__ = ("ConnectionCompoundPowerFlow",)


@extended_dataclass(frozen=True, slots=True, weakref_slot=True)
class _Cast_ConnectionCompoundPowerFlow:
    """Special nested class for casting ConnectionCompoundPowerFlow to subclasses."""

    __parent__: "ConnectionCompoundPowerFlow"

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
    def abstract_shaft_to_mountable_component_connection_compound_power_flow(
        self: "CastSelf",
    ) -> "_4485.AbstractShaftToMountableComponentConnectionCompoundPowerFlow":
        from mastapy._private.system_model.analyses_and_results.power_flows.compound import (
            _4485,
        )

        return self.__parent__._cast(
            _4485.AbstractShaftToMountableComponentConnectionCompoundPowerFlow
        )

    @property
    def agma_gleason_conical_gear_mesh_compound_power_flow(
        self: "CastSelf",
    ) -> "_4487.AGMAGleasonConicalGearMeshCompoundPowerFlow":
        from mastapy._private.system_model.analyses_and_results.power_flows.compound import (
            _4487,
        )

        return self.__parent__._cast(_4487.AGMAGleasonConicalGearMeshCompoundPowerFlow)

    @property
    def belt_connection_compound_power_flow(
        self: "CastSelf",
    ) -> "_4491.BeltConnectionCompoundPowerFlow":
        from mastapy._private.system_model.analyses_and_results.power_flows.compound import (
            _4491,
        )

        return self.__parent__._cast(_4491.BeltConnectionCompoundPowerFlow)

    @property
    def bevel_differential_gear_mesh_compound_power_flow(
        self: "CastSelf",
    ) -> "_4494.BevelDifferentialGearMeshCompoundPowerFlow":
        from mastapy._private.system_model.analyses_and_results.power_flows.compound import (
            _4494,
        )

        return self.__parent__._cast(_4494.BevelDifferentialGearMeshCompoundPowerFlow)

    @property
    def bevel_gear_mesh_compound_power_flow(
        self: "CastSelf",
    ) -> "_4499.BevelGearMeshCompoundPowerFlow":
        from mastapy._private.system_model.analyses_and_results.power_flows.compound import (
            _4499,
        )

        return self.__parent__._cast(_4499.BevelGearMeshCompoundPowerFlow)

    @property
    def clutch_connection_compound_power_flow(
        self: "CastSelf",
    ) -> "_4504.ClutchConnectionCompoundPowerFlow":
        from mastapy._private.system_model.analyses_and_results.power_flows.compound import (
            _4504,
        )

        return self.__parent__._cast(_4504.ClutchConnectionCompoundPowerFlow)

    @property
    def coaxial_connection_compound_power_flow(
        self: "CastSelf",
    ) -> "_4506.CoaxialConnectionCompoundPowerFlow":
        from mastapy._private.system_model.analyses_and_results.power_flows.compound import (
            _4506,
        )

        return self.__parent__._cast(_4506.CoaxialConnectionCompoundPowerFlow)

    @property
    def concept_coupling_connection_compound_power_flow(
        self: "CastSelf",
    ) -> "_4509.ConceptCouplingConnectionCompoundPowerFlow":
        from mastapy._private.system_model.analyses_and_results.power_flows.compound import (
            _4509,
        )

        return self.__parent__._cast(_4509.ConceptCouplingConnectionCompoundPowerFlow)

    @property
    def concept_gear_mesh_compound_power_flow(
        self: "CastSelf",
    ) -> "_4512.ConceptGearMeshCompoundPowerFlow":
        from mastapy._private.system_model.analyses_and_results.power_flows.compound import (
            _4512,
        )

        return self.__parent__._cast(_4512.ConceptGearMeshCompoundPowerFlow)

    @property
    def conical_gear_mesh_compound_power_flow(
        self: "CastSelf",
    ) -> "_4515.ConicalGearMeshCompoundPowerFlow":
        from mastapy._private.system_model.analyses_and_results.power_flows.compound import (
            _4515,
        )

        return self.__parent__._cast(_4515.ConicalGearMeshCompoundPowerFlow)

    @property
    def coupling_connection_compound_power_flow(
        self: "CastSelf",
    ) -> "_4520.CouplingConnectionCompoundPowerFlow":
        from mastapy._private.system_model.analyses_and_results.power_flows.compound import (
            _4520,
        )

        return self.__parent__._cast(_4520.CouplingConnectionCompoundPowerFlow)

    @property
    def cvt_belt_connection_compound_power_flow(
        self: "CastSelf",
    ) -> "_4522.CVTBeltConnectionCompoundPowerFlow":
        from mastapy._private.system_model.analyses_and_results.power_flows.compound import (
            _4522,
        )

        return self.__parent__._cast(_4522.CVTBeltConnectionCompoundPowerFlow)

    @property
    def cycloidal_disc_central_bearing_connection_compound_power_flow(
        self: "CastSelf",
    ) -> "_4526.CycloidalDiscCentralBearingConnectionCompoundPowerFlow":
        from mastapy._private.system_model.analyses_and_results.power_flows.compound import (
            _4526,
        )

        return self.__parent__._cast(
            _4526.CycloidalDiscCentralBearingConnectionCompoundPowerFlow
        )

    @property
    def cycloidal_disc_planetary_bearing_connection_compound_power_flow(
        self: "CastSelf",
    ) -> "_4528.CycloidalDiscPlanetaryBearingConnectionCompoundPowerFlow":
        from mastapy._private.system_model.analyses_and_results.power_flows.compound import (
            _4528,
        )

        return self.__parent__._cast(
            _4528.CycloidalDiscPlanetaryBearingConnectionCompoundPowerFlow
        )

    @property
    def cylindrical_gear_mesh_compound_power_flow(
        self: "CastSelf",
    ) -> "_4530.CylindricalGearMeshCompoundPowerFlow":
        from mastapy._private.system_model.analyses_and_results.power_flows.compound import (
            _4530,
        )

        return self.__parent__._cast(_4530.CylindricalGearMeshCompoundPowerFlow)

    @property
    def face_gear_mesh_compound_power_flow(
        self: "CastSelf",
    ) -> "_4536.FaceGearMeshCompoundPowerFlow":
        from mastapy._private.system_model.analyses_and_results.power_flows.compound import (
            _4536,
        )

        return self.__parent__._cast(_4536.FaceGearMeshCompoundPowerFlow)

    @property
    def gear_mesh_compound_power_flow(
        self: "CastSelf",
    ) -> "_4541.GearMeshCompoundPowerFlow":
        from mastapy._private.system_model.analyses_and_results.power_flows.compound import (
            _4541,
        )

        return self.__parent__._cast(_4541.GearMeshCompoundPowerFlow)

    @property
    def hypoid_gear_mesh_compound_power_flow(
        self: "CastSelf",
    ) -> "_4545.HypoidGearMeshCompoundPowerFlow":
        from mastapy._private.system_model.analyses_and_results.power_flows.compound import (
            _4545,
        )

        return self.__parent__._cast(_4545.HypoidGearMeshCompoundPowerFlow)

    @property
    def inter_mountable_component_connection_compound_power_flow(
        self: "CastSelf",
    ) -> "_4547.InterMountableComponentConnectionCompoundPowerFlow":
        from mastapy._private.system_model.analyses_and_results.power_flows.compound import (
            _4547,
        )

        return self.__parent__._cast(
            _4547.InterMountableComponentConnectionCompoundPowerFlow
        )

    @property
    def klingelnberg_cyclo_palloid_conical_gear_mesh_compound_power_flow(
        self: "CastSelf",
    ) -> "_4549.KlingelnbergCycloPalloidConicalGearMeshCompoundPowerFlow":
        from mastapy._private.system_model.analyses_and_results.power_flows.compound import (
            _4549,
        )

        return self.__parent__._cast(
            _4549.KlingelnbergCycloPalloidConicalGearMeshCompoundPowerFlow
        )

    @property
    def klingelnberg_cyclo_palloid_hypoid_gear_mesh_compound_power_flow(
        self: "CastSelf",
    ) -> "_4552.KlingelnbergCycloPalloidHypoidGearMeshCompoundPowerFlow":
        from mastapy._private.system_model.analyses_and_results.power_flows.compound import (
            _4552,
        )

        return self.__parent__._cast(
            _4552.KlingelnbergCycloPalloidHypoidGearMeshCompoundPowerFlow
        )

    @property
    def klingelnberg_cyclo_palloid_spiral_bevel_gear_mesh_compound_power_flow(
        self: "CastSelf",
    ) -> "_4555.KlingelnbergCycloPalloidSpiralBevelGearMeshCompoundPowerFlow":
        from mastapy._private.system_model.analyses_and_results.power_flows.compound import (
            _4555,
        )

        return self.__parent__._cast(
            _4555.KlingelnbergCycloPalloidSpiralBevelGearMeshCompoundPowerFlow
        )

    @property
    def part_to_part_shear_coupling_connection_compound_power_flow(
        self: "CastSelf",
    ) -> "_4565.PartToPartShearCouplingConnectionCompoundPowerFlow":
        from mastapy._private.system_model.analyses_and_results.power_flows.compound import (
            _4565,
        )

        return self.__parent__._cast(
            _4565.PartToPartShearCouplingConnectionCompoundPowerFlow
        )

    @property
    def planetary_connection_compound_power_flow(
        self: "CastSelf",
    ) -> "_4567.PlanetaryConnectionCompoundPowerFlow":
        from mastapy._private.system_model.analyses_and_results.power_flows.compound import (
            _4567,
        )

        return self.__parent__._cast(_4567.PlanetaryConnectionCompoundPowerFlow)

    @property
    def ring_pins_to_disc_connection_compound_power_flow(
        self: "CastSelf",
    ) -> "_4574.RingPinsToDiscConnectionCompoundPowerFlow":
        from mastapy._private.system_model.analyses_and_results.power_flows.compound import (
            _4574,
        )

        return self.__parent__._cast(_4574.RingPinsToDiscConnectionCompoundPowerFlow)

    @property
    def rolling_ring_connection_compound_power_flow(
        self: "CastSelf",
    ) -> "_4577.RollingRingConnectionCompoundPowerFlow":
        from mastapy._private.system_model.analyses_and_results.power_flows.compound import (
            _4577,
        )

        return self.__parent__._cast(_4577.RollingRingConnectionCompoundPowerFlow)

    @property
    def shaft_to_mountable_component_connection_compound_power_flow(
        self: "CastSelf",
    ) -> "_4581.ShaftToMountableComponentConnectionCompoundPowerFlow":
        from mastapy._private.system_model.analyses_and_results.power_flows.compound import (
            _4581,
        )

        return self.__parent__._cast(
            _4581.ShaftToMountableComponentConnectionCompoundPowerFlow
        )

    @property
    def spiral_bevel_gear_mesh_compound_power_flow(
        self: "CastSelf",
    ) -> "_4584.SpiralBevelGearMeshCompoundPowerFlow":
        from mastapy._private.system_model.analyses_and_results.power_flows.compound import (
            _4584,
        )

        return self.__parent__._cast(_4584.SpiralBevelGearMeshCompoundPowerFlow)

    @property
    def spring_damper_connection_compound_power_flow(
        self: "CastSelf",
    ) -> "_4587.SpringDamperConnectionCompoundPowerFlow":
        from mastapy._private.system_model.analyses_and_results.power_flows.compound import (
            _4587,
        )

        return self.__parent__._cast(_4587.SpringDamperConnectionCompoundPowerFlow)

    @property
    def straight_bevel_diff_gear_mesh_compound_power_flow(
        self: "CastSelf",
    ) -> "_4590.StraightBevelDiffGearMeshCompoundPowerFlow":
        from mastapy._private.system_model.analyses_and_results.power_flows.compound import (
            _4590,
        )

        return self.__parent__._cast(_4590.StraightBevelDiffGearMeshCompoundPowerFlow)

    @property
    def straight_bevel_gear_mesh_compound_power_flow(
        self: "CastSelf",
    ) -> "_4593.StraightBevelGearMeshCompoundPowerFlow":
        from mastapy._private.system_model.analyses_and_results.power_flows.compound import (
            _4593,
        )

        return self.__parent__._cast(_4593.StraightBevelGearMeshCompoundPowerFlow)

    @property
    def torque_converter_connection_compound_power_flow(
        self: "CastSelf",
    ) -> "_4602.TorqueConverterConnectionCompoundPowerFlow":
        from mastapy._private.system_model.analyses_and_results.power_flows.compound import (
            _4602,
        )

        return self.__parent__._cast(_4602.TorqueConverterConnectionCompoundPowerFlow)

    @property
    def worm_gear_mesh_compound_power_flow(
        self: "CastSelf",
    ) -> "_4608.WormGearMeshCompoundPowerFlow":
        from mastapy._private.system_model.analyses_and_results.power_flows.compound import (
            _4608,
        )

        return self.__parent__._cast(_4608.WormGearMeshCompoundPowerFlow)

    @property
    def zerol_bevel_gear_mesh_compound_power_flow(
        self: "CastSelf",
    ) -> "_4611.ZerolBevelGearMeshCompoundPowerFlow":
        from mastapy._private.system_model.analyses_and_results.power_flows.compound import (
            _4611,
        )

        return self.__parent__._cast(_4611.ZerolBevelGearMeshCompoundPowerFlow)

    @property
    def connection_compound_power_flow(
        self: "CastSelf",
    ) -> "ConnectionCompoundPowerFlow":
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
class ConnectionCompoundPowerFlow(_7935.ConnectionCompoundAnalysis):
    """ConnectionCompoundPowerFlow

    This is a mastapy class.
    """

    TYPE: ClassVar["Type"] = _CONNECTION_COMPOUND_POWER_FLOW

    wrapped: "Any"

    def __post_init__(self: "Self") -> None:
        """Override of the post initialisation magic method."""
        if not hasattr(self.wrapped, "reference_count"):
            self.wrapped.reference_count = 0

        self.wrapped.reference_count += 1

    @property
    @exception_bridge
    def connection_analysis_cases(self: "Self") -> "List[_4380.ConnectionPowerFlow]":
        """List[mastapy.system_model.analyses_and_results.power_flows.ConnectionPowerFlow]

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
    ) -> "List[_4380.ConnectionPowerFlow]":
        """List[mastapy.system_model.analyses_and_results.power_flows.ConnectionPowerFlow]

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
    def cast_to(self: "Self") -> "_Cast_ConnectionCompoundPowerFlow":
        """Cast to another type.

        Returns:
            _Cast_ConnectionCompoundPowerFlow
        """
        return _Cast_ConnectionCompoundPowerFlow(self)
