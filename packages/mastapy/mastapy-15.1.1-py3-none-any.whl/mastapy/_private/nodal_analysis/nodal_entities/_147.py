"""ComponentNodalCompositeBase"""

from __future__ import annotations

from typing import TYPE_CHECKING, ClassVar

from mastapy._private._internal.dataclasses import extended_dataclass
from mastapy._private._internal.exceptions import CastException
from mastapy._private._internal.python_net import python_net_import

from mastapy._private._internal import utility
from mastapy._private.nodal_analysis.nodal_entities import _160

_COMPONENT_NODAL_COMPOSITE_BASE = python_net_import(
    "SMT.MastaAPI.NodalAnalysis.NodalEntities", "ComponentNodalCompositeBase"
)

if TYPE_CHECKING:
    from typing import Any, Type, TypeVar

    from mastapy._private.nodal_analysis.nodal_entities import (
        _140,
        _141,
        _142,
        _146,
        _148,
        _149,
        _155,
        _161,
        _167,
        _168,
        _173,
        _174,
        _175,
        _176,
    )

    Self = TypeVar("Self", bound="ComponentNodalCompositeBase")
    CastSelf = TypeVar(
        "CastSelf",
        bound="ComponentNodalCompositeBase._Cast_ComponentNodalCompositeBase",
    )


__docformat__ = "restructuredtext en"
__all__ = ("ComponentNodalCompositeBase",)


@extended_dataclass(frozen=True, slots=True, weakref_slot=True)
class _Cast_ComponentNodalCompositeBase:
    """Special nested class for casting ComponentNodalCompositeBase to subclasses."""

    __parent__: "ComponentNodalCompositeBase"

    @property
    def nodal_composite(self: "CastSelf") -> "_160.NodalComposite":
        return self.__parent__._cast(_160.NodalComposite)

    @property
    def nodal_entity(self: "CastSelf") -> "_161.NodalEntity":
        from mastapy._private.nodal_analysis.nodal_entities import _161

        return self.__parent__._cast(_161.NodalEntity)

    @property
    def bar_elastic_mbd(self: "CastSelf") -> "_140.BarElasticMBD":
        from mastapy._private.nodal_analysis.nodal_entities import _140

        return self.__parent__._cast(_140.BarElasticMBD)

    @property
    def bar_mbd(self: "CastSelf") -> "_141.BarMBD":
        from mastapy._private.nodal_analysis.nodal_entities import _141

        return self.__parent__._cast(_141.BarMBD)

    @property
    def bar_rigid_mbd(self: "CastSelf") -> "_142.BarRigidMBD":
        from mastapy._private.nodal_analysis.nodal_entities import _142

        return self.__parent__._cast(_142.BarRigidMBD)

    @property
    def component_nodal_composite(self: "CastSelf") -> "_146.ComponentNodalComposite":
        from mastapy._private.nodal_analysis.nodal_entities import _146

        return self.__parent__._cast(_146.ComponentNodalComposite)

    @property
    def concentric_connection_nodal_component(
        self: "CastSelf",
    ) -> "_148.ConcentricConnectionNodalComponent":
        from mastapy._private.nodal_analysis.nodal_entities import _148

        return self.__parent__._cast(_148.ConcentricConnectionNodalComponent)

    @property
    def concentric_connection_nodal_component_base(
        self: "CastSelf",
    ) -> "_149.ConcentricConnectionNodalComponentBase":
        from mastapy._private.nodal_analysis.nodal_entities import _149

        return self.__parent__._cast(_149.ConcentricConnectionNodalComponentBase)

    @property
    def gear_mesh_point_on_flank_contact(
        self: "CastSelf",
    ) -> "_155.GearMeshPointOnFlankContact":
        from mastapy._private.nodal_analysis.nodal_entities import _155

        return self.__parent__._cast(_155.GearMeshPointOnFlankContact)

    @property
    def simple_bar(self: "CastSelf") -> "_167.SimpleBar":
        from mastapy._private.nodal_analysis.nodal_entities import _167

        return self.__parent__._cast(_167.SimpleBar)

    @property
    def spline_contact_nodal_component(
        self: "CastSelf",
    ) -> "_168.SplineContactNodalComponent":
        from mastapy._private.nodal_analysis.nodal_entities import _168

        return self.__parent__._cast(_168.SplineContactNodalComponent)

    @property
    def torsional_friction_node_pair(
        self: "CastSelf",
    ) -> "_173.TorsionalFrictionNodePair":
        from mastapy._private.nodal_analysis.nodal_entities import _173

        return self.__parent__._cast(_173.TorsionalFrictionNodePair)

    @property
    def torsional_friction_node_pair_base(
        self: "CastSelf",
    ) -> "_174.TorsionalFrictionNodePairBase":
        from mastapy._private.nodal_analysis.nodal_entities import _174

        return self.__parent__._cast(_174.TorsionalFrictionNodePairBase)

    @property
    def torsional_friction_node_pair_simple_locked_stiffness(
        self: "CastSelf",
    ) -> "_175.TorsionalFrictionNodePairSimpleLockedStiffness":
        from mastapy._private.nodal_analysis.nodal_entities import _175

        return self.__parent__._cast(
            _175.TorsionalFrictionNodePairSimpleLockedStiffness
        )

    @property
    def two_body_connection_nodal_component(
        self: "CastSelf",
    ) -> "_176.TwoBodyConnectionNodalComponent":
        from mastapy._private.nodal_analysis.nodal_entities import _176

        return self.__parent__._cast(_176.TwoBodyConnectionNodalComponent)

    @property
    def component_nodal_composite_base(
        self: "CastSelf",
    ) -> "ComponentNodalCompositeBase":
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
class ComponentNodalCompositeBase(_160.NodalComposite):
    """ComponentNodalCompositeBase

    This is a mastapy class.
    """

    TYPE: ClassVar["Type"] = _COMPONENT_NODAL_COMPOSITE_BASE

    wrapped: "Any"

    def __post_init__(self: "Self") -> None:
        """Override of the post initialisation magic method."""
        if not hasattr(self.wrapped, "reference_count"):
            self.wrapped.reference_count = 0

        self.wrapped.reference_count += 1

    @property
    def cast_to(self: "Self") -> "_Cast_ComponentNodalCompositeBase":
        """Cast to another type.

        Returns:
            _Cast_ComponentNodalCompositeBase
        """
        return _Cast_ComponentNodalCompositeBase(self)
