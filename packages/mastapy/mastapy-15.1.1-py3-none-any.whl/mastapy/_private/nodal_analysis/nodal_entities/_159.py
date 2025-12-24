"""NodalComponent"""

from __future__ import annotations

from typing import TYPE_CHECKING, ClassVar

from mastapy._private._internal.dataclasses import extended_dataclass
from mastapy._private._internal.exceptions import CastException
from mastapy._private._internal.python_net import python_net_import

from mastapy._private._internal import utility
from mastapy._private.nodal_analysis.nodal_entities import _161

_NODAL_COMPONENT = python_net_import(
    "SMT.MastaAPI.NodalAnalysis.NodalEntities", "NodalComponent"
)

if TYPE_CHECKING:
    from typing import Any, Type, TypeVar

    from mastapy._private.nodal_analysis.nodal_entities import (
        _136,
        _137,
        _138,
        _139,
        _144,
        _145,
        _150,
        _151,
        _152,
        _154,
        _157,
        _158,
        _163,
        _164,
        _165,
        _166,
        _169,
        _170,
        _171,
        _172,
    )
    from mastapy._private.nodal_analysis.nodal_entities.external_force import (
        _177,
        _178,
        _179,
    )
    from mastapy._private.system_model.analyses_and_results.system_deflections import (
        _3097,
    )

    Self = TypeVar("Self", bound="NodalComponent")
    CastSelf = TypeVar("CastSelf", bound="NodalComponent._Cast_NodalComponent")


__docformat__ = "restructuredtext en"
__all__ = ("NodalComponent",)


@extended_dataclass(frozen=True, slots=True, weakref_slot=True)
class _Cast_NodalComponent:
    """Special nested class for casting NodalComponent to subclasses."""

    __parent__: "NodalComponent"

    @property
    def nodal_entity(self: "CastSelf") -> "_161.NodalEntity":
        return self.__parent__._cast(_161.NodalEntity)

    @property
    def arbitrary_nodal_component(self: "CastSelf") -> "_136.ArbitraryNodalComponent":
        from mastapy._private.nodal_analysis.nodal_entities import _136

        return self.__parent__._cast(_136.ArbitraryNodalComponent)

    @property
    def arbitrary_nodal_component_base(
        self: "CastSelf",
    ) -> "_137.ArbitraryNodalComponentBase":
        from mastapy._private.nodal_analysis.nodal_entities import _137

        return self.__parent__._cast(_137.ArbitraryNodalComponentBase)

    @property
    def bar(self: "CastSelf") -> "_138.Bar":
        from mastapy._private.nodal_analysis.nodal_entities import _138

        return self.__parent__._cast(_138.Bar)

    @property
    def bar_base(self: "CastSelf") -> "_139.BarBase":
        from mastapy._private.nodal_analysis.nodal_entities import _139

        return self.__parent__._cast(_139.BarBase)

    @property
    def bearing_axial_mounting_clearance(
        self: "CastSelf",
    ) -> "_144.BearingAxialMountingClearance":
        from mastapy._private.nodal_analysis.nodal_entities import _144

        return self.__parent__._cast(_144.BearingAxialMountingClearance)

    @property
    def cms_nodal_component(self: "CastSelf") -> "_145.CMSNodalComponent":
        from mastapy._private.nodal_analysis.nodal_entities import _145

        return self.__parent__._cast(_145.CMSNodalComponent)

    @property
    def distributed_rigid_bar_coupling(
        self: "CastSelf",
    ) -> "_150.DistributedRigidBarCoupling":
        from mastapy._private.nodal_analysis.nodal_entities import _150

        return self.__parent__._cast(_150.DistributedRigidBarCoupling)

    @property
    def flow_junction_nodal_component(
        self: "CastSelf",
    ) -> "_151.FlowJunctionNodalComponent":
        from mastapy._private.nodal_analysis.nodal_entities import _151

        return self.__parent__._cast(_151.FlowJunctionNodalComponent)

    @property
    def friction_nodal_component(self: "CastSelf") -> "_152.FrictionNodalComponent":
        from mastapy._private.nodal_analysis.nodal_entities import _152

        return self.__parent__._cast(_152.FrictionNodalComponent)

    @property
    def gear_mesh_node_pair(self: "CastSelf") -> "_154.GearMeshNodePair":
        from mastapy._private.nodal_analysis.nodal_entities import _154

        return self.__parent__._cast(_154.GearMeshNodePair)

    @property
    def inertial_force_component(self: "CastSelf") -> "_157.InertialForceComponent":
        from mastapy._private.nodal_analysis.nodal_entities import _157

        return self.__parent__._cast(_157.InertialForceComponent)

    @property
    def line_contact_stiffness_entity(
        self: "CastSelf",
    ) -> "_158.LineContactStiffnessEntity":
        from mastapy._private.nodal_analysis.nodal_entities import _158

        return self.__parent__._cast(_158.LineContactStiffnessEntity)

    @property
    def pid_control_nodal_component(
        self: "CastSelf",
    ) -> "_163.PIDControlNodalComponent":
        from mastapy._private.nodal_analysis.nodal_entities import _163

        return self.__parent__._cast(_163.PIDControlNodalComponent)

    @property
    def pressure_and_volumetric_flow_rate_nodal_component_v2(
        self: "CastSelf",
    ) -> "_164.PressureAndVolumetricFlowRateNodalComponentV2":
        from mastapy._private.nodal_analysis.nodal_entities import _164

        return self.__parent__._cast(_164.PressureAndVolumetricFlowRateNodalComponentV2)

    @property
    def pressure_constraint_nodal_component(
        self: "CastSelf",
    ) -> "_165.PressureConstraintNodalComponent":
        from mastapy._private.nodal_analysis.nodal_entities import _165

        return self.__parent__._cast(_165.PressureConstraintNodalComponent)

    @property
    def rigid_bar(self: "CastSelf") -> "_166.RigidBar":
        from mastapy._private.nodal_analysis.nodal_entities import _166

        return self.__parent__._cast(_166.RigidBar)

    @property
    def surface_to_surface_contact_stiffness_entity(
        self: "CastSelf",
    ) -> "_169.SurfaceToSurfaceContactStiffnessEntity":
        from mastapy._private.nodal_analysis.nodal_entities import _169

        return self.__parent__._cast(_169.SurfaceToSurfaceContactStiffnessEntity)

    @property
    def temperature_constraint(self: "CastSelf") -> "_170.TemperatureConstraint":
        from mastapy._private.nodal_analysis.nodal_entities import _170

        return self.__parent__._cast(_170.TemperatureConstraint)

    @property
    def thermal_connector_with_resistance_nodal_component(
        self: "CastSelf",
    ) -> "_171.ThermalConnectorWithResistanceNodalComponent":
        from mastapy._private.nodal_analysis.nodal_entities import _171

        return self.__parent__._cast(_171.ThermalConnectorWithResistanceNodalComponent)

    @property
    def thermal_nodal_component(self: "CastSelf") -> "_172.ThermalNodalComponent":
        from mastapy._private.nodal_analysis.nodal_entities import _172

        return self.__parent__._cast(_172.ThermalNodalComponent)

    @property
    def external_force_entity(self: "CastSelf") -> "_177.ExternalForceEntity":
        from mastapy._private.nodal_analysis.nodal_entities.external_force import _177

        return self.__parent__._cast(_177.ExternalForceEntity)

    @property
    def external_force_line_contact_entity(
        self: "CastSelf",
    ) -> "_178.ExternalForceLineContactEntity":
        from mastapy._private.nodal_analysis.nodal_entities.external_force import _178

        return self.__parent__._cast(_178.ExternalForceLineContactEntity)

    @property
    def external_force_single_point_entity(
        self: "CastSelf",
    ) -> "_179.ExternalForceSinglePointEntity":
        from mastapy._private.nodal_analysis.nodal_entities.external_force import _179

        return self.__parent__._cast(_179.ExternalForceSinglePointEntity)

    @property
    def shaft_section_system_deflection(
        self: "CastSelf",
    ) -> "_3097.ShaftSectionSystemDeflection":
        from mastapy._private.system_model.analyses_and_results.system_deflections import (
            _3097,
        )

        return self.__parent__._cast(_3097.ShaftSectionSystemDeflection)

    @property
    def nodal_component(self: "CastSelf") -> "NodalComponent":
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
class NodalComponent(_161.NodalEntity):
    """NodalComponent

    This is a mastapy class.
    """

    TYPE: ClassVar["Type"] = _NODAL_COMPONENT

    wrapped: "Any"

    def __post_init__(self: "Self") -> None:
        """Override of the post initialisation magic method."""
        if not hasattr(self.wrapped, "reference_count"):
            self.wrapped.reference_count = 0

        self.wrapped.reference_count += 1

    @property
    def cast_to(self: "Self") -> "_Cast_NodalComponent":
        """Cast to another type.

        Returns:
            _Cast_NodalComponent
        """
        return _Cast_NodalComponent(self)
