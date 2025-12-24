"""BearingConnectionComponent"""

from __future__ import annotations

from typing import TYPE_CHECKING, ClassVar

from mastapy._private._internal.dataclasses import extended_dataclass
from mastapy._private._internal.exceptions import CastException
from mastapy._private._internal.python_net import python_net_import

from mastapy._private import _0
from mastapy._private._internal import utility

_BEARING_CONNECTION_COMPONENT = python_net_import(
    "SMT.MastaAPI.Bearings.Tolerances", "BearingConnectionComponent"
)

if TYPE_CHECKING:
    from typing import Any, Type, TypeVar

    from mastapy._private.bearings.tolerances import (
        _2143,
        _2144,
        _2145,
        _2146,
        _2148,
        _2149,
        _2150,
        _2153,
        _2154,
        _2157,
        _2159,
    )

    Self = TypeVar("Self", bound="BearingConnectionComponent")
    CastSelf = TypeVar(
        "CastSelf", bound="BearingConnectionComponent._Cast_BearingConnectionComponent"
    )


__docformat__ = "restructuredtext en"
__all__ = ("BearingConnectionComponent",)


@extended_dataclass(frozen=True, slots=True, weakref_slot=True)
class _Cast_BearingConnectionComponent:
    """Special nested class for casting BearingConnectionComponent to subclasses."""

    __parent__: "BearingConnectionComponent"

    @property
    def inner_ring_tolerance(self: "CastSelf") -> "_2143.InnerRingTolerance":
        from mastapy._private.bearings.tolerances import _2143

        return self.__parent__._cast(_2143.InnerRingTolerance)

    @property
    def inner_support_tolerance(self: "CastSelf") -> "_2144.InnerSupportTolerance":
        from mastapy._private.bearings.tolerances import _2144

        return self.__parent__._cast(_2144.InnerSupportTolerance)

    @property
    def interference_detail(self: "CastSelf") -> "_2145.InterferenceDetail":
        from mastapy._private.bearings.tolerances import _2145

        return self.__parent__._cast(_2145.InterferenceDetail)

    @property
    def interference_tolerance(self: "CastSelf") -> "_2146.InterferenceTolerance":
        from mastapy._private.bearings.tolerances import _2146

        return self.__parent__._cast(_2146.InterferenceTolerance)

    @property
    def mounting_sleeve_diameter_detail(
        self: "CastSelf",
    ) -> "_2148.MountingSleeveDiameterDetail":
        from mastapy._private.bearings.tolerances import _2148

        return self.__parent__._cast(_2148.MountingSleeveDiameterDetail)

    @property
    def outer_ring_tolerance(self: "CastSelf") -> "_2149.OuterRingTolerance":
        from mastapy._private.bearings.tolerances import _2149

        return self.__parent__._cast(_2149.OuterRingTolerance)

    @property
    def outer_support_tolerance(self: "CastSelf") -> "_2150.OuterSupportTolerance":
        from mastapy._private.bearings.tolerances import _2150

        return self.__parent__._cast(_2150.OuterSupportTolerance)

    @property
    def ring_detail(self: "CastSelf") -> "_2153.RingDetail":
        from mastapy._private.bearings.tolerances import _2153

        return self.__parent__._cast(_2153.RingDetail)

    @property
    def ring_tolerance(self: "CastSelf") -> "_2154.RingTolerance":
        from mastapy._private.bearings.tolerances import _2154

        return self.__parent__._cast(_2154.RingTolerance)

    @property
    def support_detail(self: "CastSelf") -> "_2157.SupportDetail":
        from mastapy._private.bearings.tolerances import _2157

        return self.__parent__._cast(_2157.SupportDetail)

    @property
    def support_tolerance(self: "CastSelf") -> "_2159.SupportTolerance":
        from mastapy._private.bearings.tolerances import _2159

        return self.__parent__._cast(_2159.SupportTolerance)

    @property
    def bearing_connection_component(self: "CastSelf") -> "BearingConnectionComponent":
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
class BearingConnectionComponent(_0.APIBase):
    """BearingConnectionComponent

    This is a mastapy class.
    """

    TYPE: ClassVar["Type"] = _BEARING_CONNECTION_COMPONENT

    wrapped: "Any"

    def __post_init__(self: "Self") -> None:
        """Override of the post initialisation magic method."""
        if not hasattr(self.wrapped, "reference_count"):
            self.wrapped.reference_count = 0

        self.wrapped.reference_count += 1

    @property
    def cast_to(self: "Self") -> "_Cast_BearingConnectionComponent":
        """Cast to another type.

        Returns:
            _Cast_BearingConnectionComponent
        """
        return _Cast_BearingConnectionComponent(self)
