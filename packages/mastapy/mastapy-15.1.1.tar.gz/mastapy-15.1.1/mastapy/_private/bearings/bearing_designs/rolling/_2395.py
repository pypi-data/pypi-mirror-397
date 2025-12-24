"""CrossedRollerBearing"""

from __future__ import annotations

from typing import TYPE_CHECKING, ClassVar

from mastapy._private._internal.dataclasses import extended_dataclass
from mastapy._private._internal.exceptions import CastException
from mastapy._private._internal.python_net import python_net_import

from mastapy._private._internal import utility
from mastapy._private.bearings.bearing_designs.rolling import _2409

_CROSSED_ROLLER_BEARING = python_net_import(
    "SMT.MastaAPI.Bearings.BearingDesigns.Rolling", "CrossedRollerBearing"
)

if TYPE_CHECKING:
    from typing import Any, Type, TypeVar

    from mastapy._private.bearings.bearing_designs import _2377, _2378, _2381
    from mastapy._private.bearings.bearing_designs.rolling import _2412

    Self = TypeVar("Self", bound="CrossedRollerBearing")
    CastSelf = TypeVar(
        "CastSelf", bound="CrossedRollerBearing._Cast_CrossedRollerBearing"
    )


__docformat__ = "restructuredtext en"
__all__ = ("CrossedRollerBearing",)


@extended_dataclass(frozen=True, slots=True, weakref_slot=True)
class _Cast_CrossedRollerBearing:
    """Special nested class for casting CrossedRollerBearing to subclasses."""

    __parent__: "CrossedRollerBearing"

    @property
    def roller_bearing(self: "CastSelf") -> "_2409.RollerBearing":
        return self.__parent__._cast(_2409.RollerBearing)

    @property
    def rolling_bearing(self: "CastSelf") -> "_2412.RollingBearing":
        from mastapy._private.bearings.bearing_designs.rolling import _2412

        return self.__parent__._cast(_2412.RollingBearing)

    @property
    def detailed_bearing(self: "CastSelf") -> "_2378.DetailedBearing":
        from mastapy._private.bearings.bearing_designs import _2378

        return self.__parent__._cast(_2378.DetailedBearing)

    @property
    def non_linear_bearing(self: "CastSelf") -> "_2381.NonLinearBearing":
        from mastapy._private.bearings.bearing_designs import _2381

        return self.__parent__._cast(_2381.NonLinearBearing)

    @property
    def bearing_design(self: "CastSelf") -> "_2377.BearingDesign":
        from mastapy._private.bearings.bearing_designs import _2377

        return self.__parent__._cast(_2377.BearingDesign)

    @property
    def crossed_roller_bearing(self: "CastSelf") -> "CrossedRollerBearing":
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
class CrossedRollerBearing(_2409.RollerBearing):
    """CrossedRollerBearing

    This is a mastapy class.
    """

    TYPE: ClassVar["Type"] = _CROSSED_ROLLER_BEARING

    wrapped: "Any"

    def __post_init__(self: "Self") -> None:
        """Override of the post initialisation magic method."""
        if not hasattr(self.wrapped, "reference_count"):
            self.wrapped.reference_count = 0

        self.wrapped.reference_count += 1

    @property
    def cast_to(self: "Self") -> "_Cast_CrossedRollerBearing":
        """Cast to another type.

        Returns:
            _Cast_CrossedRollerBearing
        """
        return _Cast_CrossedRollerBearing(self)
