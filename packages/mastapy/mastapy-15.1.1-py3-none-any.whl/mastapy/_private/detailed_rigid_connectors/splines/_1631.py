"""StandardSplineHalfDesign"""

from __future__ import annotations

from typing import TYPE_CHECKING, ClassVar

from mastapy._private._internal.dataclasses import extended_dataclass
from mastapy._private._internal.exceptions import CastException
from mastapy._private._internal.python_net import python_net_import

from mastapy._private._internal import utility
from mastapy._private.detailed_rigid_connectors.splines import _1626

_STANDARD_SPLINE_HALF_DESIGN = python_net_import(
    "SMT.MastaAPI.DetailedRigidConnectors.Splines", "StandardSplineHalfDesign"
)

if TYPE_CHECKING:
    from typing import Any, Type, TypeVar

    from mastapy._private.detailed_rigid_connectors import _1600
    from mastapy._private.detailed_rigid_connectors.splines import (
        _1604,
        _1608,
        _1611,
        _1619,
    )

    Self = TypeVar("Self", bound="StandardSplineHalfDesign")
    CastSelf = TypeVar(
        "CastSelf", bound="StandardSplineHalfDesign._Cast_StandardSplineHalfDesign"
    )


__docformat__ = "restructuredtext en"
__all__ = ("StandardSplineHalfDesign",)


@extended_dataclass(frozen=True, slots=True, weakref_slot=True)
class _Cast_StandardSplineHalfDesign:
    """Special nested class for casting StandardSplineHalfDesign to subclasses."""

    __parent__: "StandardSplineHalfDesign"

    @property
    def spline_half_design(self: "CastSelf") -> "_1626.SplineHalfDesign":
        return self.__parent__._cast(_1626.SplineHalfDesign)

    @property
    def detailed_rigid_connector_half_design(
        self: "CastSelf",
    ) -> "_1600.DetailedRigidConnectorHalfDesign":
        from mastapy._private.detailed_rigid_connectors import _1600

        return self.__parent__._cast(_1600.DetailedRigidConnectorHalfDesign)

    @property
    def din5480_spline_half_design(self: "CastSelf") -> "_1604.DIN5480SplineHalfDesign":
        from mastapy._private.detailed_rigid_connectors.splines import _1604

        return self.__parent__._cast(_1604.DIN5480SplineHalfDesign)

    @property
    def gbt3478_spline_half_design(self: "CastSelf") -> "_1608.GBT3478SplineHalfDesign":
        from mastapy._private.detailed_rigid_connectors.splines import _1608

        return self.__parent__._cast(_1608.GBT3478SplineHalfDesign)

    @property
    def iso4156_spline_half_design(self: "CastSelf") -> "_1611.ISO4156SplineHalfDesign":
        from mastapy._private.detailed_rigid_connectors.splines import _1611

        return self.__parent__._cast(_1611.ISO4156SplineHalfDesign)

    @property
    def sae_spline_half_design(self: "CastSelf") -> "_1619.SAESplineHalfDesign":
        from mastapy._private.detailed_rigid_connectors.splines import _1619

        return self.__parent__._cast(_1619.SAESplineHalfDesign)

    @property
    def standard_spline_half_design(self: "CastSelf") -> "StandardSplineHalfDesign":
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
class StandardSplineHalfDesign(_1626.SplineHalfDesign):
    """StandardSplineHalfDesign

    This is a mastapy class.
    """

    TYPE: ClassVar["Type"] = _STANDARD_SPLINE_HALF_DESIGN

    wrapped: "Any"

    def __post_init__(self: "Self") -> None:
        """Override of the post initialisation magic method."""
        if not hasattr(self.wrapped, "reference_count"):
            self.wrapped.reference_count = 0

        self.wrapped.reference_count += 1

    @property
    def cast_to(self: "Self") -> "_Cast_StandardSplineHalfDesign":
        """Cast to another type.

        Returns:
            _Cast_StandardSplineHalfDesign
        """
        return _Cast_StandardSplineHalfDesign(self)
