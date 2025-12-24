"""MultiNodeFELink"""

from __future__ import annotations

from typing import TYPE_CHECKING, ClassVar

from mastapy._private._internal.dataclasses import extended_dataclass
from mastapy._private._internal.exceptions import CastException
from mastapy._private._internal.python_net import python_net_import

from mastapy._private._internal import utility
from mastapy._private.system_model.fe.links import _2686

_MULTI_NODE_FE_LINK = python_net_import(
    "SMT.MastaAPI.SystemModel.FE.Links", "MultiNodeFELink"
)

if TYPE_CHECKING:
    from typing import Any, Type, TypeVar

    from mastapy._private.system_model.fe.links import (
        _2687,
        _2690,
        _2691,
        _2692,
        _2693,
        _2695,
        _2696,
        _2697,
        _2698,
        _2699,
        _2700,
    )

    Self = TypeVar("Self", bound="MultiNodeFELink")
    CastSelf = TypeVar("CastSelf", bound="MultiNodeFELink._Cast_MultiNodeFELink")


__docformat__ = "restructuredtext en"
__all__ = ("MultiNodeFELink",)


@extended_dataclass(frozen=True, slots=True, weakref_slot=True)
class _Cast_MultiNodeFELink:
    """Special nested class for casting MultiNodeFELink to subclasses."""

    __parent__: "MultiNodeFELink"

    @property
    def fe_link(self: "CastSelf") -> "_2686.FELink":
        return self.__parent__._cast(_2686.FELink)

    @property
    def electric_machine_stator_fe_link(
        self: "CastSelf",
    ) -> "_2687.ElectricMachineStatorFELink":
        from mastapy._private.system_model.fe.links import _2687

        return self.__parent__._cast(_2687.ElectricMachineStatorFELink)

    @property
    def gear_mesh_fe_link(self: "CastSelf") -> "_2690.GearMeshFELink":
        from mastapy._private.system_model.fe.links import _2690

        return self.__parent__._cast(_2690.GearMeshFELink)

    @property
    def gear_with_duplicated_meshes_fe_link(
        self: "CastSelf",
    ) -> "_2691.GearWithDuplicatedMeshesFELink":
        from mastapy._private.system_model.fe.links import _2691

        return self.__parent__._cast(_2691.GearWithDuplicatedMeshesFELink)

    @property
    def multi_angle_connection_fe_link(
        self: "CastSelf",
    ) -> "_2692.MultiAngleConnectionFELink":
        from mastapy._private.system_model.fe.links import _2692

        return self.__parent__._cast(_2692.MultiAngleConnectionFELink)

    @property
    def multi_node_connector_fe_link(
        self: "CastSelf",
    ) -> "_2693.MultiNodeConnectorFELink":
        from mastapy._private.system_model.fe.links import _2693

        return self.__parent__._cast(_2693.MultiNodeConnectorFELink)

    @property
    def planetary_connector_multi_node_fe_link(
        self: "CastSelf",
    ) -> "_2695.PlanetaryConnectorMultiNodeFELink":
        from mastapy._private.system_model.fe.links import _2695

        return self.__parent__._cast(_2695.PlanetaryConnectorMultiNodeFELink)

    @property
    def planet_based_fe_link(self: "CastSelf") -> "_2696.PlanetBasedFELink":
        from mastapy._private.system_model.fe.links import _2696

        return self.__parent__._cast(_2696.PlanetBasedFELink)

    @property
    def planet_carrier_fe_link(self: "CastSelf") -> "_2697.PlanetCarrierFELink":
        from mastapy._private.system_model.fe.links import _2697

        return self.__parent__._cast(_2697.PlanetCarrierFELink)

    @property
    def point_load_fe_link(self: "CastSelf") -> "_2698.PointLoadFELink":
        from mastapy._private.system_model.fe.links import _2698

        return self.__parent__._cast(_2698.PointLoadFELink)

    @property
    def rolling_ring_connection_fe_link(
        self: "CastSelf",
    ) -> "_2699.RollingRingConnectionFELink":
        from mastapy._private.system_model.fe.links import _2699

        return self.__parent__._cast(_2699.RollingRingConnectionFELink)

    @property
    def shaft_hub_connection_fe_link(
        self: "CastSelf",
    ) -> "_2700.ShaftHubConnectionFELink":
        from mastapy._private.system_model.fe.links import _2700

        return self.__parent__._cast(_2700.ShaftHubConnectionFELink)

    @property
    def multi_node_fe_link(self: "CastSelf") -> "MultiNodeFELink":
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
class MultiNodeFELink(_2686.FELink):
    """MultiNodeFELink

    This is a mastapy class.
    """

    TYPE: ClassVar["Type"] = _MULTI_NODE_FE_LINK

    wrapped: "Any"

    def __post_init__(self: "Self") -> None:
        """Override of the post initialisation magic method."""
        if not hasattr(self.wrapped, "reference_count"):
            self.wrapped.reference_count = 0

        self.wrapped.reference_count += 1

    @property
    def cast_to(self: "Self") -> "_Cast_MultiNodeFELink":
        """Cast to another type.

        Returns:
            _Cast_MultiNodeFELink
        """
        return _Cast_MultiNodeFELink(self)
