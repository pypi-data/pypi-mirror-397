"""LoadedAxialThrustCylindricalRollerBearingElement"""

from __future__ import annotations

from typing import TYPE_CHECKING, ClassVar

from mastapy._private._internal.dataclasses import extended_dataclass
from mastapy._private._internal.exceptions import CastException
from mastapy._private._internal.python_net import python_net_import

from mastapy._private._internal import utility
from mastapy._private.bearings.bearing_results.rolling import _2269

_LOADED_AXIAL_THRUST_CYLINDRICAL_ROLLER_BEARING_ELEMENT = python_net_import(
    "SMT.MastaAPI.Bearings.BearingResults.Rolling",
    "LoadedAxialThrustCylindricalRollerBearingElement",
)

if TYPE_CHECKING:
    from typing import Any, Type, TypeVar

    from mastapy._private.bearings.bearing_results.rolling import _2238, _2256, _2271

    Self = TypeVar("Self", bound="LoadedAxialThrustCylindricalRollerBearingElement")
    CastSelf = TypeVar(
        "CastSelf",
        bound="LoadedAxialThrustCylindricalRollerBearingElement._Cast_LoadedAxialThrustCylindricalRollerBearingElement",
    )


__docformat__ = "restructuredtext en"
__all__ = ("LoadedAxialThrustCylindricalRollerBearingElement",)


@extended_dataclass(frozen=True, slots=True, weakref_slot=True)
class _Cast_LoadedAxialThrustCylindricalRollerBearingElement:
    """Special nested class for casting LoadedAxialThrustCylindricalRollerBearingElement to subclasses."""

    __parent__: "LoadedAxialThrustCylindricalRollerBearingElement"

    @property
    def loaded_non_barrel_roller_element(
        self: "CastSelf",
    ) -> "_2269.LoadedNonBarrelRollerElement":
        return self.__parent__._cast(_2269.LoadedNonBarrelRollerElement)

    @property
    def loaded_roller_bearing_element(
        self: "CastSelf",
    ) -> "_2271.LoadedRollerBearingElement":
        from mastapy._private.bearings.bearing_results.rolling import _2271

        return self.__parent__._cast(_2271.LoadedRollerBearingElement)

    @property
    def loaded_element(self: "CastSelf") -> "_2256.LoadedElement":
        from mastapy._private.bearings.bearing_results.rolling import _2256

        return self.__parent__._cast(_2256.LoadedElement)

    @property
    def loaded_axial_thrust_needle_roller_bearing_element(
        self: "CastSelf",
    ) -> "_2238.LoadedAxialThrustNeedleRollerBearingElement":
        from mastapy._private.bearings.bearing_results.rolling import _2238

        return self.__parent__._cast(_2238.LoadedAxialThrustNeedleRollerBearingElement)

    @property
    def loaded_axial_thrust_cylindrical_roller_bearing_element(
        self: "CastSelf",
    ) -> "LoadedAxialThrustCylindricalRollerBearingElement":
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
class LoadedAxialThrustCylindricalRollerBearingElement(
    _2269.LoadedNonBarrelRollerElement
):
    """LoadedAxialThrustCylindricalRollerBearingElement

    This is a mastapy class.
    """

    TYPE: ClassVar["Type"] = _LOADED_AXIAL_THRUST_CYLINDRICAL_ROLLER_BEARING_ELEMENT

    wrapped: "Any"

    def __post_init__(self: "Self") -> None:
        """Override of the post initialisation magic method."""
        if not hasattr(self.wrapped, "reference_count"):
            self.wrapped.reference_count = 0

        self.wrapped.reference_count += 1

    @property
    def cast_to(
        self: "Self",
    ) -> "_Cast_LoadedAxialThrustCylindricalRollerBearingElement":
        """Cast to another type.

        Returns:
            _Cast_LoadedAxialThrustCylindricalRollerBearingElement
        """
        return _Cast_LoadedAxialThrustCylindricalRollerBearingElement(self)
