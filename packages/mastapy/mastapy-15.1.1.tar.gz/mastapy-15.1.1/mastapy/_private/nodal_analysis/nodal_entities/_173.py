"""TorsionalFrictionNodePair"""

from __future__ import annotations

from typing import TYPE_CHECKING, ClassVar

from mastapy._private._internal.dataclasses import extended_dataclass
from mastapy._private._internal.exceptions import CastException
from mastapy._private._internal.python_net import python_net_import

from mastapy._private._internal import utility
from mastapy._private.nodal_analysis.nodal_entities import _174

_TORSIONAL_FRICTION_NODE_PAIR = python_net_import(
    "SMT.MastaAPI.NodalAnalysis.NodalEntities", "TorsionalFrictionNodePair"
)

if TYPE_CHECKING:
    from typing import Any, Type, TypeVar

    from mastapy._private.nodal_analysis.nodal_entities import (
        _147,
        _149,
        _160,
        _161,
        _176,
    )

    Self = TypeVar("Self", bound="TorsionalFrictionNodePair")
    CastSelf = TypeVar(
        "CastSelf", bound="TorsionalFrictionNodePair._Cast_TorsionalFrictionNodePair"
    )


__docformat__ = "restructuredtext en"
__all__ = ("TorsionalFrictionNodePair",)


@extended_dataclass(frozen=True, slots=True, weakref_slot=True)
class _Cast_TorsionalFrictionNodePair:
    """Special nested class for casting TorsionalFrictionNodePair to subclasses."""

    __parent__: "TorsionalFrictionNodePair"

    @property
    def torsional_friction_node_pair_base(
        self: "CastSelf",
    ) -> "_174.TorsionalFrictionNodePairBase":
        return self.__parent__._cast(_174.TorsionalFrictionNodePairBase)

    @property
    def concentric_connection_nodal_component_base(
        self: "CastSelf",
    ) -> "_149.ConcentricConnectionNodalComponentBase":
        from mastapy._private.nodal_analysis.nodal_entities import _149

        return self.__parent__._cast(_149.ConcentricConnectionNodalComponentBase)

    @property
    def two_body_connection_nodal_component(
        self: "CastSelf",
    ) -> "_176.TwoBodyConnectionNodalComponent":
        from mastapy._private.nodal_analysis.nodal_entities import _176

        return self.__parent__._cast(_176.TwoBodyConnectionNodalComponent)

    @property
    def component_nodal_composite_base(
        self: "CastSelf",
    ) -> "_147.ComponentNodalCompositeBase":
        from mastapy._private.nodal_analysis.nodal_entities import _147

        return self.__parent__._cast(_147.ComponentNodalCompositeBase)

    @property
    def nodal_composite(self: "CastSelf") -> "_160.NodalComposite":
        from mastapy._private.nodal_analysis.nodal_entities import _160

        return self.__parent__._cast(_160.NodalComposite)

    @property
    def nodal_entity(self: "CastSelf") -> "_161.NodalEntity":
        from mastapy._private.nodal_analysis.nodal_entities import _161

        return self.__parent__._cast(_161.NodalEntity)

    @property
    def torsional_friction_node_pair(self: "CastSelf") -> "TorsionalFrictionNodePair":
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
class TorsionalFrictionNodePair(_174.TorsionalFrictionNodePairBase):
    """TorsionalFrictionNodePair

    This is a mastapy class.
    """

    TYPE: ClassVar["Type"] = _TORSIONAL_FRICTION_NODE_PAIR

    wrapped: "Any"

    def __post_init__(self: "Self") -> None:
        """Override of the post initialisation magic method."""
        if not hasattr(self.wrapped, "reference_count"):
            self.wrapped.reference_count = 0

        self.wrapped.reference_count += 1

    @property
    def cast_to(self: "Self") -> "_Cast_TorsionalFrictionNodePair":
        """Cast to another type.

        Returns:
            _Cast_TorsionalFrictionNodePair
        """
        return _Cast_TorsionalFrictionNodePair(self)
