"""GearStiffness"""

from __future__ import annotations

from typing import TYPE_CHECKING, ClassVar

from mastapy._private._internal.dataclasses import extended_dataclass
from mastapy._private._internal.exceptions import CastException
from mastapy._private._internal.python_net import python_net_import

from mastapy._private._internal import utility
from mastapy._private.nodal_analysis import _69

_GEAR_STIFFNESS = python_net_import("SMT.MastaAPI.Gears.LTCA", "GearStiffness")

if TYPE_CHECKING:
    from typing import Any, Type, TypeVar

    from mastapy._private.gears.ltca import _959, _961
    from mastapy._private.gears.ltca.conical import _988, _990
    from mastapy._private.gears.ltca.cylindrical import _977, _979

    Self = TypeVar("Self", bound="GearStiffness")
    CastSelf = TypeVar("CastSelf", bound="GearStiffness._Cast_GearStiffness")


__docformat__ = "restructuredtext en"
__all__ = ("GearStiffness",)


@extended_dataclass(frozen=True, slots=True, weakref_slot=True)
class _Cast_GearStiffness:
    """Special nested class for casting GearStiffness to subclasses."""

    __parent__: "GearStiffness"

    @property
    def fe_stiffness(self: "CastSelf") -> "_69.FEStiffness":
        return self.__parent__._cast(_69.FEStiffness)

    @property
    def gear_bending_stiffness(self: "CastSelf") -> "_959.GearBendingStiffness":
        from mastapy._private.gears.ltca import _959

        return self.__parent__._cast(_959.GearBendingStiffness)

    @property
    def gear_contact_stiffness(self: "CastSelf") -> "_961.GearContactStiffness":
        from mastapy._private.gears.ltca import _961

        return self.__parent__._cast(_961.GearContactStiffness)

    @property
    def cylindrical_gear_bending_stiffness(
        self: "CastSelf",
    ) -> "_977.CylindricalGearBendingStiffness":
        from mastapy._private.gears.ltca.cylindrical import _977

        return self.__parent__._cast(_977.CylindricalGearBendingStiffness)

    @property
    def cylindrical_gear_contact_stiffness(
        self: "CastSelf",
    ) -> "_979.CylindricalGearContactStiffness":
        from mastapy._private.gears.ltca.cylindrical import _979

        return self.__parent__._cast(_979.CylindricalGearContactStiffness)

    @property
    def conical_gear_bending_stiffness(
        self: "CastSelf",
    ) -> "_988.ConicalGearBendingStiffness":
        from mastapy._private.gears.ltca.conical import _988

        return self.__parent__._cast(_988.ConicalGearBendingStiffness)

    @property
    def conical_gear_contact_stiffness(
        self: "CastSelf",
    ) -> "_990.ConicalGearContactStiffness":
        from mastapy._private.gears.ltca.conical import _990

        return self.__parent__._cast(_990.ConicalGearContactStiffness)

    @property
    def gear_stiffness(self: "CastSelf") -> "GearStiffness":
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
class GearStiffness(_69.FEStiffness):
    """GearStiffness

    This is a mastapy class.
    """

    TYPE: ClassVar["Type"] = _GEAR_STIFFNESS

    wrapped: "Any"

    def __post_init__(self: "Self") -> None:
        """Override of the post initialisation magic method."""
        if not hasattr(self.wrapped, "reference_count"):
            self.wrapped.reference_count = 0

        self.wrapped.reference_count += 1

    @property
    def cast_to(self: "Self") -> "_Cast_GearStiffness":
        """Cast to another type.

        Returns:
            _Cast_GearStiffness
        """
        return _Cast_GearStiffness(self)
