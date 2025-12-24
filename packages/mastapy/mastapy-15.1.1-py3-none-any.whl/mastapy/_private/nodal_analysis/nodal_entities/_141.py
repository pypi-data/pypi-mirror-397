"""BarMBD"""

from __future__ import annotations

from typing import TYPE_CHECKING, ClassVar

from mastapy._private._internal.dataclasses import extended_dataclass
from mastapy._private._internal.exceptions import CastException
from mastapy._private._internal.python_net import python_net_import

from mastapy._private._internal import utility
from mastapy._private.nodal_analysis.nodal_entities import _147

_BAR_MBD = python_net_import("SMT.MastaAPI.NodalAnalysis.NodalEntities", "BarMBD")

if TYPE_CHECKING:
    from typing import Any, Type, TypeVar

    from mastapy._private.nodal_analysis.nodal_entities import _140, _142, _160, _161

    Self = TypeVar("Self", bound="BarMBD")
    CastSelf = TypeVar("CastSelf", bound="BarMBD._Cast_BarMBD")


__docformat__ = "restructuredtext en"
__all__ = ("BarMBD",)


@extended_dataclass(frozen=True, slots=True, weakref_slot=True)
class _Cast_BarMBD:
    """Special nested class for casting BarMBD to subclasses."""

    __parent__: "BarMBD"

    @property
    def component_nodal_composite_base(
        self: "CastSelf",
    ) -> "_147.ComponentNodalCompositeBase":
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
    def bar_elastic_mbd(self: "CastSelf") -> "_140.BarElasticMBD":
        from mastapy._private.nodal_analysis.nodal_entities import _140

        return self.__parent__._cast(_140.BarElasticMBD)

    @property
    def bar_rigid_mbd(self: "CastSelf") -> "_142.BarRigidMBD":
        from mastapy._private.nodal_analysis.nodal_entities import _142

        return self.__parent__._cast(_142.BarRigidMBD)

    @property
    def bar_mbd(self: "CastSelf") -> "BarMBD":
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
class BarMBD(_147.ComponentNodalCompositeBase):
    """BarMBD

    This is a mastapy class.
    """

    TYPE: ClassVar["Type"] = _BAR_MBD

    wrapped: "Any"

    def __post_init__(self: "Self") -> None:
        """Override of the post initialisation magic method."""
        if not hasattr(self.wrapped, "reference_count"):
            self.wrapped.reference_count = 0

        self.wrapped.reference_count += 1

    @property
    def cast_to(self: "Self") -> "_Cast_BarMBD":
        """Cast to another type.

        Returns:
            _Cast_BarMBD
        """
        return _Cast_BarMBD(self)
