"""GearWithDuplicatedMeshesFELink"""

from __future__ import annotations

from typing import TYPE_CHECKING, ClassVar

from mastapy._private._internal.dataclasses import extended_dataclass
from mastapy._private._internal.exceptions import CastException
from mastapy._private._internal.python_net import python_net_import

from mastapy._private._internal import utility
from mastapy._private.system_model.fe.links import _2696

_GEAR_WITH_DUPLICATED_MESHES_FE_LINK = python_net_import(
    "SMT.MastaAPI.SystemModel.FE.Links", "GearWithDuplicatedMeshesFELink"
)

if TYPE_CHECKING:
    from typing import Any, Type, TypeVar

    from mastapy._private.system_model.fe.links import _2686, _2694

    Self = TypeVar("Self", bound="GearWithDuplicatedMeshesFELink")
    CastSelf = TypeVar(
        "CastSelf",
        bound="GearWithDuplicatedMeshesFELink._Cast_GearWithDuplicatedMeshesFELink",
    )


__docformat__ = "restructuredtext en"
__all__ = ("GearWithDuplicatedMeshesFELink",)


@extended_dataclass(frozen=True, slots=True, weakref_slot=True)
class _Cast_GearWithDuplicatedMeshesFELink:
    """Special nested class for casting GearWithDuplicatedMeshesFELink to subclasses."""

    __parent__: "GearWithDuplicatedMeshesFELink"

    @property
    def planet_based_fe_link(self: "CastSelf") -> "_2696.PlanetBasedFELink":
        return self.__parent__._cast(_2696.PlanetBasedFELink)

    @property
    def multi_node_fe_link(self: "CastSelf") -> "_2694.MultiNodeFELink":
        from mastapy._private.system_model.fe.links import _2694

        return self.__parent__._cast(_2694.MultiNodeFELink)

    @property
    def fe_link(self: "CastSelf") -> "_2686.FELink":
        from mastapy._private.system_model.fe.links import _2686

        return self.__parent__._cast(_2686.FELink)

    @property
    def gear_with_duplicated_meshes_fe_link(
        self: "CastSelf",
    ) -> "GearWithDuplicatedMeshesFELink":
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
class GearWithDuplicatedMeshesFELink(_2696.PlanetBasedFELink):
    """GearWithDuplicatedMeshesFELink

    This is a mastapy class.
    """

    TYPE: ClassVar["Type"] = _GEAR_WITH_DUPLICATED_MESHES_FE_LINK

    wrapped: "Any"

    def __post_init__(self: "Self") -> None:
        """Override of the post initialisation magic method."""
        if not hasattr(self.wrapped, "reference_count"):
            self.wrapped.reference_count = 0

        self.wrapped.reference_count += 1

    @property
    def cast_to(self: "Self") -> "_Cast_GearWithDuplicatedMeshesFELink":
        """Cast to another type.

        Returns:
            _Cast_GearWithDuplicatedMeshesFELink
        """
        return _Cast_GearWithDuplicatedMeshesFELink(self)
