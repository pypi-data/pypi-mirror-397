"""PartToPartShearCouplingSocket"""

from __future__ import annotations

from typing import TYPE_CHECKING, ClassVar

from mastapy._private._internal.dataclasses import extended_dataclass
from mastapy._private._internal.exceptions import CastException
from mastapy._private._internal.python_net import python_net_import

from mastapy._private._internal import utility
from mastapy._private.system_model.connections_and_sockets.couplings import _2606

_PART_TO_PART_SHEAR_COUPLING_SOCKET = python_net_import(
    "SMT.MastaAPI.SystemModel.ConnectionsAndSockets.Couplings",
    "PartToPartShearCouplingSocket",
)

if TYPE_CHECKING:
    from typing import Any, Type, TypeVar

    from mastapy._private.system_model.connections_and_sockets import _2535, _2555

    Self = TypeVar("Self", bound="PartToPartShearCouplingSocket")
    CastSelf = TypeVar(
        "CastSelf",
        bound="PartToPartShearCouplingSocket._Cast_PartToPartShearCouplingSocket",
    )


__docformat__ = "restructuredtext en"
__all__ = ("PartToPartShearCouplingSocket",)


@extended_dataclass(frozen=True, slots=True, weakref_slot=True)
class _Cast_PartToPartShearCouplingSocket:
    """Special nested class for casting PartToPartShearCouplingSocket to subclasses."""

    __parent__: "PartToPartShearCouplingSocket"

    @property
    def coupling_socket(self: "CastSelf") -> "_2606.CouplingSocket":
        return self.__parent__._cast(_2606.CouplingSocket)

    @property
    def cylindrical_socket(self: "CastSelf") -> "_2535.CylindricalSocket":
        from mastapy._private.system_model.connections_and_sockets import _2535

        return self.__parent__._cast(_2535.CylindricalSocket)

    @property
    def socket(self: "CastSelf") -> "_2555.Socket":
        from mastapy._private.system_model.connections_and_sockets import _2555

        return self.__parent__._cast(_2555.Socket)

    @property
    def part_to_part_shear_coupling_socket(
        self: "CastSelf",
    ) -> "PartToPartShearCouplingSocket":
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
class PartToPartShearCouplingSocket(_2606.CouplingSocket):
    """PartToPartShearCouplingSocket

    This is a mastapy class.
    """

    TYPE: ClassVar["Type"] = _PART_TO_PART_SHEAR_COUPLING_SOCKET

    wrapped: "Any"

    def __post_init__(self: "Self") -> None:
        """Override of the post initialisation magic method."""
        if not hasattr(self.wrapped, "reference_count"):
            self.wrapped.reference_count = 0

        self.wrapped.reference_count += 1

    @property
    def cast_to(self: "Self") -> "_Cast_PartToPartShearCouplingSocket":
        """Cast to another type.

        Returns:
            _Cast_PartToPartShearCouplingSocket
        """
        return _Cast_PartToPartShearCouplingSocket(self)
