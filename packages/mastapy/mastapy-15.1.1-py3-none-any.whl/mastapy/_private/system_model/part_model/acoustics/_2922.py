"""MeshedReflectingPlane"""

from __future__ import annotations

from typing import TYPE_CHECKING, ClassVar

from mastapy._private._internal.dataclasses import extended_dataclass
from mastapy._private._internal.exceptions import CastException
from mastapy._private._internal.python_net import python_net_import

from mastapy._private._internal import utility
from mastapy._private.system_model.part_model.acoustics import _2926

_MESHED_REFLECTING_PLANE = python_net_import(
    "SMT.MastaAPI.SystemModel.PartModel.Acoustics", "MeshedReflectingPlane"
)

if TYPE_CHECKING:
    from typing import Any, Type, TypeVar

    Self = TypeVar("Self", bound="MeshedReflectingPlane")
    CastSelf = TypeVar(
        "CastSelf", bound="MeshedReflectingPlane._Cast_MeshedReflectingPlane"
    )


__docformat__ = "restructuredtext en"
__all__ = ("MeshedReflectingPlane",)


@extended_dataclass(frozen=True, slots=True, weakref_slot=True)
class _Cast_MeshedReflectingPlane:
    """Special nested class for casting MeshedReflectingPlane to subclasses."""

    __parent__: "MeshedReflectingPlane"

    @property
    def meshed_result_surface_base(self: "CastSelf") -> "_2926.MeshedResultSurfaceBase":
        return self.__parent__._cast(_2926.MeshedResultSurfaceBase)

    @property
    def meshed_reflecting_plane(self: "CastSelf") -> "MeshedReflectingPlane":
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
class MeshedReflectingPlane(_2926.MeshedResultSurfaceBase):
    """MeshedReflectingPlane

    This is a mastapy class.
    """

    TYPE: ClassVar["Type"] = _MESHED_REFLECTING_PLANE

    wrapped: "Any"

    def __post_init__(self: "Self") -> None:
        """Override of the post initialisation magic method."""
        if not hasattr(self.wrapped, "reference_count"):
            self.wrapped.reference_count = 0

        self.wrapped.reference_count += 1

    @property
    def cast_to(self: "Self") -> "_Cast_MeshedReflectingPlane":
        """Cast to another type.

        Returns:
            _Cast_MeshedReflectingPlane
        """
        return _Cast_MeshedReflectingPlane(self)
