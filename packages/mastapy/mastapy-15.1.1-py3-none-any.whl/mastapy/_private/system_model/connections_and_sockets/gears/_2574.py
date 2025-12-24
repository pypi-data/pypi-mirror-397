"""HypoidGearMesh"""

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
from mastapy._private.system_model.connections_and_sockets.gears import _2558

_HYPOID_GEAR_MESH = python_net_import(
    "SMT.MastaAPI.SystemModel.ConnectionsAndSockets.Gears", "HypoidGearMesh"
)

if TYPE_CHECKING:
    from typing import Any, Type, TypeVar

    from mastapy._private.gears.gear_designs.hypoid import _1112
    from mastapy._private.system_model import _2451
    from mastapy._private.system_model.connections_and_sockets import _2531, _2540
    from mastapy._private.system_model.connections_and_sockets.gears import _2566, _2572

    Self = TypeVar("Self", bound="HypoidGearMesh")
    CastSelf = TypeVar("CastSelf", bound="HypoidGearMesh._Cast_HypoidGearMesh")


__docformat__ = "restructuredtext en"
__all__ = ("HypoidGearMesh",)


@extended_dataclass(frozen=True, slots=True, weakref_slot=True)
class _Cast_HypoidGearMesh:
    """Special nested class for casting HypoidGearMesh to subclasses."""

    __parent__: "HypoidGearMesh"

    @property
    def agma_gleason_conical_gear_mesh(
        self: "CastSelf",
    ) -> "_2558.AGMAGleasonConicalGearMesh":
        return self.__parent__._cast(_2558.AGMAGleasonConicalGearMesh)

    @property
    def conical_gear_mesh(self: "CastSelf") -> "_2566.ConicalGearMesh":
        from mastapy._private.system_model.connections_and_sockets.gears import _2566

        return self.__parent__._cast(_2566.ConicalGearMesh)

    @property
    def gear_mesh(self: "CastSelf") -> "_2572.GearMesh":
        from mastapy._private.system_model.connections_and_sockets.gears import _2572

        return self.__parent__._cast(_2572.GearMesh)

    @property
    def inter_mountable_component_connection(
        self: "CastSelf",
    ) -> "_2540.InterMountableComponentConnection":
        from mastapy._private.system_model.connections_and_sockets import _2540

        return self.__parent__._cast(_2540.InterMountableComponentConnection)

    @property
    def connection(self: "CastSelf") -> "_2531.Connection":
        from mastapy._private.system_model.connections_and_sockets import _2531

        return self.__parent__._cast(_2531.Connection)

    @property
    def design_entity(self: "CastSelf") -> "_2451.DesignEntity":
        from mastapy._private.system_model import _2451

        return self.__parent__._cast(_2451.DesignEntity)

    @property
    def hypoid_gear_mesh(self: "CastSelf") -> "HypoidGearMesh":
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
class HypoidGearMesh(_2558.AGMAGleasonConicalGearMesh):
    """HypoidGearMesh

    This is a mastapy class.
    """

    TYPE: ClassVar["Type"] = _HYPOID_GEAR_MESH

    wrapped: "Any"

    def __post_init__(self: "Self") -> None:
        """Override of the post initialisation magic method."""
        if not hasattr(self.wrapped, "reference_count"):
            self.wrapped.reference_count = 0

        self.wrapped.reference_count += 1

    @property
    @exception_bridge
    def active_gear_mesh_design(self: "Self") -> "_1112.HypoidGearMeshDesign":
        """mastapy.gears.gear_designs.hypoid.HypoidGearMeshDesign

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "ActiveGearMeshDesign")

        if temp is None:
            return None

        type_ = temp.GetType()
        return constructor.new(type_.Namespace, type_.Name)(temp)

    @property
    @exception_bridge
    def hypoid_gear_mesh_design(self: "Self") -> "_1112.HypoidGearMeshDesign":
        """mastapy.gears.gear_designs.hypoid.HypoidGearMeshDesign

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "HypoidGearMeshDesign")

        if temp is None:
            return None

        type_ = temp.GetType()
        return constructor.new(type_.Namespace, type_.Name)(temp)

    @property
    def cast_to(self: "Self") -> "_Cast_HypoidGearMesh":
        """Cast to another type.

        Returns:
            _Cast_HypoidGearMesh
        """
        return _Cast_HypoidGearMesh(self)
