"""ArbitraryNodalComponentBase"""

from __future__ import annotations

from typing import TYPE_CHECKING, ClassVar

from mastapy._private._internal.dataclasses import extended_dataclass
from mastapy._private._internal.exceptions import CastException
from mastapy._private._internal.python_net import python_net_import

from mastapy._private._internal import utility
from mastapy._private.nodal_analysis.nodal_entities import _159

_ARBITRARY_NODAL_COMPONENT_BASE = python_net_import(
    "SMT.MastaAPI.NodalAnalysis.NodalEntities", "ArbitraryNodalComponentBase"
)

if TYPE_CHECKING:
    from typing import Any, Type, TypeVar

    from mastapy._private.nodal_analysis.nodal_entities import (
        _136,
        _144,
        _145,
        _154,
        _158,
        _161,
        _169,
    )

    Self = TypeVar("Self", bound="ArbitraryNodalComponentBase")
    CastSelf = TypeVar(
        "CastSelf",
        bound="ArbitraryNodalComponentBase._Cast_ArbitraryNodalComponentBase",
    )


__docformat__ = "restructuredtext en"
__all__ = ("ArbitraryNodalComponentBase",)


@extended_dataclass(frozen=True, slots=True, weakref_slot=True)
class _Cast_ArbitraryNodalComponentBase:
    """Special nested class for casting ArbitraryNodalComponentBase to subclasses."""

    __parent__: "ArbitraryNodalComponentBase"

    @property
    def nodal_component(self: "CastSelf") -> "_159.NodalComponent":
        return self.__parent__._cast(_159.NodalComponent)

    @property
    def nodal_entity(self: "CastSelf") -> "_161.NodalEntity":
        from mastapy._private.nodal_analysis.nodal_entities import _161

        return self.__parent__._cast(_161.NodalEntity)

    @property
    def arbitrary_nodal_component(self: "CastSelf") -> "_136.ArbitraryNodalComponent":
        from mastapy._private.nodal_analysis.nodal_entities import _136

        return self.__parent__._cast(_136.ArbitraryNodalComponent)

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
    def gear_mesh_node_pair(self: "CastSelf") -> "_154.GearMeshNodePair":
        from mastapy._private.nodal_analysis.nodal_entities import _154

        return self.__parent__._cast(_154.GearMeshNodePair)

    @property
    def line_contact_stiffness_entity(
        self: "CastSelf",
    ) -> "_158.LineContactStiffnessEntity":
        from mastapy._private.nodal_analysis.nodal_entities import _158

        return self.__parent__._cast(_158.LineContactStiffnessEntity)

    @property
    def surface_to_surface_contact_stiffness_entity(
        self: "CastSelf",
    ) -> "_169.SurfaceToSurfaceContactStiffnessEntity":
        from mastapy._private.nodal_analysis.nodal_entities import _169

        return self.__parent__._cast(_169.SurfaceToSurfaceContactStiffnessEntity)

    @property
    def arbitrary_nodal_component_base(
        self: "CastSelf",
    ) -> "ArbitraryNodalComponentBase":
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
class ArbitraryNodalComponentBase(_159.NodalComponent):
    """ArbitraryNodalComponentBase

    This is a mastapy class.
    """

    TYPE: ClassVar["Type"] = _ARBITRARY_NODAL_COMPONENT_BASE

    wrapped: "Any"

    def __post_init__(self: "Self") -> None:
        """Override of the post initialisation magic method."""
        if not hasattr(self.wrapped, "reference_count"):
            self.wrapped.reference_count = 0

        self.wrapped.reference_count += 1

    @property
    def cast_to(self: "Self") -> "_Cast_ArbitraryNodalComponentBase":
        """Cast to another type.

        Returns:
            _Cast_ArbitraryNodalComponentBase
        """
        return _Cast_ArbitraryNodalComponentBase(self)
