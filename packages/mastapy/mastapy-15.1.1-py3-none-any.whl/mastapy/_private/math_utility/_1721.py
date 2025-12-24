"""EulerParameters"""

from __future__ import annotations

from typing import TYPE_CHECKING, ClassVar

from mastapy._private._internal.dataclasses import extended_dataclass
from mastapy._private._internal.exceptions import CastException
from mastapy._private._internal.python_net import python_net_import

from mastapy._private._internal import utility
from mastapy._private.math_utility import _1742

_EULER_PARAMETERS = python_net_import("SMT.MastaAPI.MathUtility", "EulerParameters")

if TYPE_CHECKING:
    from typing import Any, Type, TypeVar

    from mastapy._private.math_utility import _1726, _1741

    Self = TypeVar("Self", bound="EulerParameters")
    CastSelf = TypeVar("CastSelf", bound="EulerParameters._Cast_EulerParameters")


__docformat__ = "restructuredtext en"
__all__ = ("EulerParameters",)


@extended_dataclass(frozen=True, slots=True, weakref_slot=True)
class _Cast_EulerParameters:
    """Special nested class for casting EulerParameters to subclasses."""

    __parent__: "EulerParameters"

    @property
    def real_vector(self: "CastSelf") -> "_1742.RealVector":
        return self.__parent__._cast(_1742.RealVector)

    @property
    def real_matrix(self: "CastSelf") -> "_1741.RealMatrix":
        from mastapy._private.math_utility import _1741

        return self.__parent__._cast(_1741.RealMatrix)

    @property
    def generic_matrix(self: "CastSelf") -> "_1726.GenericMatrix":
        from mastapy._private.math_utility import _1726

        return self.__parent__._cast(_1726.GenericMatrix)

    @property
    def euler_parameters(self: "CastSelf") -> "EulerParameters":
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
class EulerParameters(_1742.RealVector):
    """EulerParameters

    This is a mastapy class.
    """

    TYPE: ClassVar["Type"] = _EULER_PARAMETERS

    wrapped: "Any"

    def __post_init__(self: "Self") -> None:
        """Override of the post initialisation magic method."""
        if not hasattr(self.wrapped, "reference_count"):
            self.wrapped.reference_count = 0

        self.wrapped.reference_count += 1

    @property
    def cast_to(self: "Self") -> "_Cast_EulerParameters":
        """Cast to another type.

        Returns:
            _Cast_EulerParameters
        """
        return _Cast_EulerParameters(self)
