"""AGMAGleasonConicalGearMesh"""

from __future__ import annotations

from typing import TYPE_CHECKING, ClassVar

from mastapy._private._internal.dataclasses import extended_dataclass
from mastapy._private._internal.exceptions import CastException
from mastapy._private._internal.python_net import python_net_import

from mastapy._private._internal import utility
from mastapy._private.system_model.connections_and_sockets.gears import _2566

_AGMA_GLEASON_CONICAL_GEAR_MESH = python_net_import(
    "SMT.MastaAPI.SystemModel.ConnectionsAndSockets.Gears", "AGMAGleasonConicalGearMesh"
)

if TYPE_CHECKING:
    from typing import Any, Type, TypeVar

    from mastapy._private.system_model import _2451
    from mastapy._private.system_model.connections_and_sockets import _2531, _2540
    from mastapy._private.system_model.connections_and_sockets.gears import (
        _2560,
        _2562,
        _2572,
        _2574,
        _2582,
        _2584,
        _2586,
        _2590,
    )

    Self = TypeVar("Self", bound="AGMAGleasonConicalGearMesh")
    CastSelf = TypeVar(
        "CastSelf", bound="AGMAGleasonConicalGearMesh._Cast_AGMAGleasonConicalGearMesh"
    )


__docformat__ = "restructuredtext en"
__all__ = ("AGMAGleasonConicalGearMesh",)


@extended_dataclass(frozen=True, slots=True, weakref_slot=True)
class _Cast_AGMAGleasonConicalGearMesh:
    """Special nested class for casting AGMAGleasonConicalGearMesh to subclasses."""

    __parent__: "AGMAGleasonConicalGearMesh"

    @property
    def conical_gear_mesh(self: "CastSelf") -> "_2566.ConicalGearMesh":
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
    def bevel_differential_gear_mesh(
        self: "CastSelf",
    ) -> "_2560.BevelDifferentialGearMesh":
        from mastapy._private.system_model.connections_and_sockets.gears import _2560

        return self.__parent__._cast(_2560.BevelDifferentialGearMesh)

    @property
    def bevel_gear_mesh(self: "CastSelf") -> "_2562.BevelGearMesh":
        from mastapy._private.system_model.connections_and_sockets.gears import _2562

        return self.__parent__._cast(_2562.BevelGearMesh)

    @property
    def hypoid_gear_mesh(self: "CastSelf") -> "_2574.HypoidGearMesh":
        from mastapy._private.system_model.connections_and_sockets.gears import _2574

        return self.__parent__._cast(_2574.HypoidGearMesh)

    @property
    def spiral_bevel_gear_mesh(self: "CastSelf") -> "_2582.SpiralBevelGearMesh":
        from mastapy._private.system_model.connections_and_sockets.gears import _2582

        return self.__parent__._cast(_2582.SpiralBevelGearMesh)

    @property
    def straight_bevel_diff_gear_mesh(
        self: "CastSelf",
    ) -> "_2584.StraightBevelDiffGearMesh":
        from mastapy._private.system_model.connections_and_sockets.gears import _2584

        return self.__parent__._cast(_2584.StraightBevelDiffGearMesh)

    @property
    def straight_bevel_gear_mesh(self: "CastSelf") -> "_2586.StraightBevelGearMesh":
        from mastapy._private.system_model.connections_and_sockets.gears import _2586

        return self.__parent__._cast(_2586.StraightBevelGearMesh)

    @property
    def zerol_bevel_gear_mesh(self: "CastSelf") -> "_2590.ZerolBevelGearMesh":
        from mastapy._private.system_model.connections_and_sockets.gears import _2590

        return self.__parent__._cast(_2590.ZerolBevelGearMesh)

    @property
    def agma_gleason_conical_gear_mesh(
        self: "CastSelf",
    ) -> "AGMAGleasonConicalGearMesh":
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
class AGMAGleasonConicalGearMesh(_2566.ConicalGearMesh):
    """AGMAGleasonConicalGearMesh

    This is a mastapy class.
    """

    TYPE: ClassVar["Type"] = _AGMA_GLEASON_CONICAL_GEAR_MESH

    wrapped: "Any"

    def __post_init__(self: "Self") -> None:
        """Override of the post initialisation magic method."""
        if not hasattr(self.wrapped, "reference_count"):
            self.wrapped.reference_count = 0

        self.wrapped.reference_count += 1

    @property
    def cast_to(self: "Self") -> "_Cast_AGMAGleasonConicalGearMesh":
        """Cast to another type.

        Returns:
            _Cast_AGMAGleasonConicalGearMesh
        """
        return _Cast_AGMAGleasonConicalGearMesh(self)
