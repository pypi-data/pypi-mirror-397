"""CouplingConnection"""

from __future__ import annotations

from typing import TYPE_CHECKING, ClassVar

from mastapy._private._internal.dataclasses import extended_dataclass
from mastapy._private._internal.exceptions import CastException
from mastapy._private._internal.python_net import python_net_import

from mastapy._private._internal import utility
from mastapy._private.system_model.connections_and_sockets import _2540

_COUPLING_CONNECTION = python_net_import(
    "SMT.MastaAPI.SystemModel.ConnectionsAndSockets.Couplings", "CouplingConnection"
)

if TYPE_CHECKING:
    from typing import Any, Type, TypeVar

    from mastapy._private.system_model import _2451
    from mastapy._private.system_model.connections_and_sockets import _2531
    from mastapy._private.system_model.connections_and_sockets.couplings import (
        _2601,
        _2603,
        _2607,
        _2609,
        _2611,
    )

    Self = TypeVar("Self", bound="CouplingConnection")
    CastSelf = TypeVar("CastSelf", bound="CouplingConnection._Cast_CouplingConnection")


__docformat__ = "restructuredtext en"
__all__ = ("CouplingConnection",)


@extended_dataclass(frozen=True, slots=True, weakref_slot=True)
class _Cast_CouplingConnection:
    """Special nested class for casting CouplingConnection to subclasses."""

    __parent__: "CouplingConnection"

    @property
    def inter_mountable_component_connection(
        self: "CastSelf",
    ) -> "_2540.InterMountableComponentConnection":
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
    def clutch_connection(self: "CastSelf") -> "_2601.ClutchConnection":
        from mastapy._private.system_model.connections_and_sockets.couplings import (
            _2601,
        )

        return self.__parent__._cast(_2601.ClutchConnection)

    @property
    def concept_coupling_connection(
        self: "CastSelf",
    ) -> "_2603.ConceptCouplingConnection":
        from mastapy._private.system_model.connections_and_sockets.couplings import (
            _2603,
        )

        return self.__parent__._cast(_2603.ConceptCouplingConnection)

    @property
    def part_to_part_shear_coupling_connection(
        self: "CastSelf",
    ) -> "_2607.PartToPartShearCouplingConnection":
        from mastapy._private.system_model.connections_and_sockets.couplings import (
            _2607,
        )

        return self.__parent__._cast(_2607.PartToPartShearCouplingConnection)

    @property
    def spring_damper_connection(self: "CastSelf") -> "_2609.SpringDamperConnection":
        from mastapy._private.system_model.connections_and_sockets.couplings import (
            _2609,
        )

        return self.__parent__._cast(_2609.SpringDamperConnection)

    @property
    def torque_converter_connection(
        self: "CastSelf",
    ) -> "_2611.TorqueConverterConnection":
        from mastapy._private.system_model.connections_and_sockets.couplings import (
            _2611,
        )

        return self.__parent__._cast(_2611.TorqueConverterConnection)

    @property
    def coupling_connection(self: "CastSelf") -> "CouplingConnection":
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
class CouplingConnection(_2540.InterMountableComponentConnection):
    """CouplingConnection

    This is a mastapy class.
    """

    TYPE: ClassVar["Type"] = _COUPLING_CONNECTION

    wrapped: "Any"

    def __post_init__(self: "Self") -> None:
        """Override of the post initialisation magic method."""
        if not hasattr(self.wrapped, "reference_count"):
            self.wrapped.reference_count = 0

        self.wrapped.reference_count += 1

    @property
    def cast_to(self: "Self") -> "_Cast_CouplingConnection":
        """Cast to another type.

        Returns:
            _Cast_CouplingConnection
        """
        return _Cast_CouplingConnection(self)
