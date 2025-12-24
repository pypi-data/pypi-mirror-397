"""ComponentNodalComposite"""

from __future__ import annotations

from typing import TYPE_CHECKING, ClassVar

from mastapy._private._internal.dataclasses import extended_dataclass
from mastapy._private._internal.exceptions import CastException
from mastapy._private._internal.python_net import python_net_import

from mastapy._private._internal import utility
from mastapy._private.nodal_analysis.nodal_entities import _147

_COMPONENT_NODAL_COMPOSITE = python_net_import(
    "SMT.MastaAPI.NodalAnalysis.NodalEntities", "ComponentNodalComposite"
)

if TYPE_CHECKING:
    from typing import Any, Type, TypeVar

    from mastapy._private.nodal_analysis.nodal_entities import _160, _161

    Self = TypeVar("Self", bound="ComponentNodalComposite")
    CastSelf = TypeVar(
        "CastSelf", bound="ComponentNodalComposite._Cast_ComponentNodalComposite"
    )


__docformat__ = "restructuredtext en"
__all__ = ("ComponentNodalComposite",)


@extended_dataclass(frozen=True, slots=True, weakref_slot=True)
class _Cast_ComponentNodalComposite:
    """Special nested class for casting ComponentNodalComposite to subclasses."""

    __parent__: "ComponentNodalComposite"

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
    def component_nodal_composite(self: "CastSelf") -> "ComponentNodalComposite":
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
class ComponentNodalComposite(_147.ComponentNodalCompositeBase):
    """ComponentNodalComposite

    This is a mastapy class.
    """

    TYPE: ClassVar["Type"] = _COMPONENT_NODAL_COMPOSITE

    wrapped: "Any"

    def __post_init__(self: "Self") -> None:
        """Override of the post initialisation magic method."""
        if not hasattr(self.wrapped, "reference_count"):
            self.wrapped.reference_count = 0

        self.wrapped.reference_count += 1

    @property
    def cast_to(self: "Self") -> "_Cast_ComponentNodalComposite":
        """Cast to another type.

        Returns:
            _Cast_ComponentNodalComposite
        """
        return _Cast_ComponentNodalComposite(self)
