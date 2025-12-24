"""GearTeethSocket"""

from __future__ import annotations

from typing import TYPE_CHECKING, ClassVar

from mastapy._private._internal.dataclasses import extended_dataclass
from mastapy._private._internal.exceptions import CastException
from mastapy._private._internal.python_net import python_net_import

from mastapy._private._internal import utility
from mastapy._private.system_model.connections_and_sockets import _2555

_GEAR_TEETH_SOCKET = python_net_import(
    "SMT.MastaAPI.SystemModel.ConnectionsAndSockets.Gears", "GearTeethSocket"
)

if TYPE_CHECKING:
    from typing import Any, Type, TypeVar

    from mastapy._private.system_model.connections_and_sockets.gears import (
        _2559,
        _2561,
        _2563,
        _2565,
        _2567,
        _2571,
        _2575,
        _2576,
        _2580,
        _2581,
        _2583,
        _2585,
        _2587,
        _2589,
        _2591,
    )

    Self = TypeVar("Self", bound="GearTeethSocket")
    CastSelf = TypeVar("CastSelf", bound="GearTeethSocket._Cast_GearTeethSocket")


__docformat__ = "restructuredtext en"
__all__ = ("GearTeethSocket",)


@extended_dataclass(frozen=True, slots=True, weakref_slot=True)
class _Cast_GearTeethSocket:
    """Special nested class for casting GearTeethSocket to subclasses."""

    __parent__: "GearTeethSocket"

    @property
    def socket(self: "CastSelf") -> "_2555.Socket":
        return self.__parent__._cast(_2555.Socket)

    @property
    def agma_gleason_conical_gear_teeth_socket(
        self: "CastSelf",
    ) -> "_2559.AGMAGleasonConicalGearTeethSocket":
        from mastapy._private.system_model.connections_and_sockets.gears import _2559

        return self.__parent__._cast(_2559.AGMAGleasonConicalGearTeethSocket)

    @property
    def bevel_differential_gear_teeth_socket(
        self: "CastSelf",
    ) -> "_2561.BevelDifferentialGearTeethSocket":
        from mastapy._private.system_model.connections_and_sockets.gears import _2561

        return self.__parent__._cast(_2561.BevelDifferentialGearTeethSocket)

    @property
    def bevel_gear_teeth_socket(self: "CastSelf") -> "_2563.BevelGearTeethSocket":
        from mastapy._private.system_model.connections_and_sockets.gears import _2563

        return self.__parent__._cast(_2563.BevelGearTeethSocket)

    @property
    def concept_gear_teeth_socket(self: "CastSelf") -> "_2565.ConceptGearTeethSocket":
        from mastapy._private.system_model.connections_and_sockets.gears import _2565

        return self.__parent__._cast(_2565.ConceptGearTeethSocket)

    @property
    def conical_gear_teeth_socket(self: "CastSelf") -> "_2567.ConicalGearTeethSocket":
        from mastapy._private.system_model.connections_and_sockets.gears import _2567

        return self.__parent__._cast(_2567.ConicalGearTeethSocket)

    @property
    def face_gear_teeth_socket(self: "CastSelf") -> "_2571.FaceGearTeethSocket":
        from mastapy._private.system_model.connections_and_sockets.gears import _2571

        return self.__parent__._cast(_2571.FaceGearTeethSocket)

    @property
    def hypoid_gear_teeth_socket(self: "CastSelf") -> "_2575.HypoidGearTeethSocket":
        from mastapy._private.system_model.connections_and_sockets.gears import _2575

        return self.__parent__._cast(_2575.HypoidGearTeethSocket)

    @property
    def klingelnberg_conical_gear_teeth_socket(
        self: "CastSelf",
    ) -> "_2576.KlingelnbergConicalGearTeethSocket":
        from mastapy._private.system_model.connections_and_sockets.gears import _2576

        return self.__parent__._cast(_2576.KlingelnbergConicalGearTeethSocket)

    @property
    def klingelnberg_hypoid_gear_teeth_socket(
        self: "CastSelf",
    ) -> "_2580.KlingelnbergHypoidGearTeethSocket":
        from mastapy._private.system_model.connections_and_sockets.gears import _2580

        return self.__parent__._cast(_2580.KlingelnbergHypoidGearTeethSocket)

    @property
    def klingelnberg_spiral_bevel_gear_teeth_socket(
        self: "CastSelf",
    ) -> "_2581.KlingelnbergSpiralBevelGearTeethSocket":
        from mastapy._private.system_model.connections_and_sockets.gears import _2581

        return self.__parent__._cast(_2581.KlingelnbergSpiralBevelGearTeethSocket)

    @property
    def spiral_bevel_gear_teeth_socket(
        self: "CastSelf",
    ) -> "_2583.SpiralBevelGearTeethSocket":
        from mastapy._private.system_model.connections_and_sockets.gears import _2583

        return self.__parent__._cast(_2583.SpiralBevelGearTeethSocket)

    @property
    def straight_bevel_diff_gear_teeth_socket(
        self: "CastSelf",
    ) -> "_2585.StraightBevelDiffGearTeethSocket":
        from mastapy._private.system_model.connections_and_sockets.gears import _2585

        return self.__parent__._cast(_2585.StraightBevelDiffGearTeethSocket)

    @property
    def straight_bevel_gear_teeth_socket(
        self: "CastSelf",
    ) -> "_2587.StraightBevelGearTeethSocket":
        from mastapy._private.system_model.connections_and_sockets.gears import _2587

        return self.__parent__._cast(_2587.StraightBevelGearTeethSocket)

    @property
    def worm_gear_teeth_socket(self: "CastSelf") -> "_2589.WormGearTeethSocket":
        from mastapy._private.system_model.connections_and_sockets.gears import _2589

        return self.__parent__._cast(_2589.WormGearTeethSocket)

    @property
    def zerol_bevel_gear_teeth_socket(
        self: "CastSelf",
    ) -> "_2591.ZerolBevelGearTeethSocket":
        from mastapy._private.system_model.connections_and_sockets.gears import _2591

        return self.__parent__._cast(_2591.ZerolBevelGearTeethSocket)

    @property
    def gear_teeth_socket(self: "CastSelf") -> "GearTeethSocket":
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
class GearTeethSocket(_2555.Socket):
    """GearTeethSocket

    This is a mastapy class.
    """

    TYPE: ClassVar["Type"] = _GEAR_TEETH_SOCKET

    wrapped: "Any"

    def __post_init__(self: "Self") -> None:
        """Override of the post initialisation magic method."""
        if not hasattr(self.wrapped, "reference_count"):
            self.wrapped.reference_count = 0

        self.wrapped.reference_count += 1

    @property
    def cast_to(self: "Self") -> "_Cast_GearTeethSocket":
        """Cast to another type.

        Returns:
            _Cast_GearTeethSocket
        """
        return _Cast_GearTeethSocket(self)
