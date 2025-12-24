"""ISO4156SplineJointDesign"""

from __future__ import annotations

from typing import TYPE_CHECKING, ClassVar

from mastapy._private._internal.dataclasses import extended_dataclass
from mastapy._private._internal.exception_bridge import exception_bridge
from mastapy._private._internal.exceptions import CastException
from mastapy._private._internal.python_net import (
    python_net_import,
    pythonnet_property_get,
)

from mastapy._private._internal import utility
from mastapy._private.detailed_rigid_connectors.splines import _1632

_ISO4156_SPLINE_JOINT_DESIGN = python_net_import(
    "SMT.MastaAPI.DetailedRigidConnectors.Splines", "ISO4156SplineJointDesign"
)

if TYPE_CHECKING:
    from typing import Any, Type, TypeVar

    from mastapy._private.detailed_rigid_connectors import _1599
    from mastapy._private.detailed_rigid_connectors.splines import _1609, _1613, _1627

    Self = TypeVar("Self", bound="ISO4156SplineJointDesign")
    CastSelf = TypeVar(
        "CastSelf", bound="ISO4156SplineJointDesign._Cast_ISO4156SplineJointDesign"
    )


__docformat__ = "restructuredtext en"
__all__ = ("ISO4156SplineJointDesign",)


@extended_dataclass(frozen=True, slots=True, weakref_slot=True)
class _Cast_ISO4156SplineJointDesign:
    """Special nested class for casting ISO4156SplineJointDesign to subclasses."""

    __parent__: "ISO4156SplineJointDesign"

    @property
    def standard_spline_joint_design(
        self: "CastSelf",
    ) -> "_1632.StandardSplineJointDesign":
        return self.__parent__._cast(_1632.StandardSplineJointDesign)

    @property
    def spline_joint_design(self: "CastSelf") -> "_1627.SplineJointDesign":
        from mastapy._private.detailed_rigid_connectors.splines import _1627

        return self.__parent__._cast(_1627.SplineJointDesign)

    @property
    def detailed_rigid_connector_design(
        self: "CastSelf",
    ) -> "_1599.DetailedRigidConnectorDesign":
        from mastapy._private.detailed_rigid_connectors import _1599

        return self.__parent__._cast(_1599.DetailedRigidConnectorDesign)

    @property
    def gbt3478_spline_joint_design(
        self: "CastSelf",
    ) -> "_1609.GBT3478SplineJointDesign":
        from mastapy._private.detailed_rigid_connectors.splines import _1609

        return self.__parent__._cast(_1609.GBT3478SplineJointDesign)

    @property
    def jisb1603_spline_joint_design(
        self: "CastSelf",
    ) -> "_1613.JISB1603SplineJointDesign":
        from mastapy._private.detailed_rigid_connectors.splines import _1613

        return self.__parent__._cast(_1613.JISB1603SplineJointDesign)

    @property
    def iso4156_spline_joint_design(self: "CastSelf") -> "ISO4156SplineJointDesign":
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
class ISO4156SplineJointDesign(_1632.StandardSplineJointDesign):
    """ISO4156SplineJointDesign

    This is a mastapy class.
    """

    TYPE: ClassVar["Type"] = _ISO4156_SPLINE_JOINT_DESIGN

    wrapped: "Any"

    def __post_init__(self: "Self") -> None:
        """Override of the post initialisation magic method."""
        if not hasattr(self.wrapped, "reference_count"):
            self.wrapped.reference_count = 0

        self.wrapped.reference_count += 1

    @property
    @exception_bridge
    def form_clearance(self: "Self") -> "float":
        """float

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "FormClearance")

        if temp is None:
            return 0.0

        return temp

    @property
    @exception_bridge
    def maximum_effective_clearance(self: "Self") -> "float":
        """float

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "MaximumEffectiveClearance")

        if temp is None:
            return 0.0

        return temp

    @property
    @exception_bridge
    def minimum_effective_clearance(self: "Self") -> "float":
        """float

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "MinimumEffectiveClearance")

        if temp is None:
            return 0.0

        return temp

    @property
    def cast_to(self: "Self") -> "_Cast_ISO4156SplineJointDesign":
        """Cast to another type.

        Returns:
            _Cast_ISO4156SplineJointDesign
        """
        return _Cast_ISO4156SplineJointDesign(self)
