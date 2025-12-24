"""PowerLoadForInjectionLossScripts"""

from __future__ import annotations

from typing import TYPE_CHECKING, ClassVar

from mastapy._private._internal.dataclasses import extended_dataclass
from mastapy._private._internal.exception_bridge import exception_bridge
from mastapy._private._internal.exceptions import CastException
from mastapy._private._internal.python_net import (
    python_net_import,
    pythonnet_property_get,
)

from mastapy._private import _0
from mastapy._private._internal import utility

_POWER_LOAD_FOR_INJECTION_LOSS_SCRIPTS = python_net_import(
    "SMT.MastaAPI.SystemModel", "PowerLoadForInjectionLossScripts"
)

if TYPE_CHECKING:
    from typing import Any, Type, TypeVar

    Self = TypeVar("Self", bound="PowerLoadForInjectionLossScripts")
    CastSelf = TypeVar(
        "CastSelf",
        bound="PowerLoadForInjectionLossScripts._Cast_PowerLoadForInjectionLossScripts",
    )


__docformat__ = "restructuredtext en"
__all__ = ("PowerLoadForInjectionLossScripts",)


@extended_dataclass(frozen=True, slots=True, weakref_slot=True)
class _Cast_PowerLoadForInjectionLossScripts:
    """Special nested class for casting PowerLoadForInjectionLossScripts to subclasses."""

    __parent__: "PowerLoadForInjectionLossScripts"

    @property
    def power_load_for_injection_loss_scripts(
        self: "CastSelf",
    ) -> "PowerLoadForInjectionLossScripts":
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
class PowerLoadForInjectionLossScripts(_0.APIBase):
    """PowerLoadForInjectionLossScripts

    This is a mastapy class.
    """

    TYPE: ClassVar["Type"] = _POWER_LOAD_FOR_INJECTION_LOSS_SCRIPTS

    wrapped: "Any"

    def __post_init__(self: "Self") -> None:
        """Override of the post initialisation magic method."""
        if not hasattr(self.wrapped, "reference_count"):
            self.wrapped.reference_count = 0

        self.wrapped.reference_count += 1

    @property
    @exception_bridge
    def power(self: "Self") -> "float":
        """float

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "Power")

        if temp is None:
            return 0.0

        return temp

    @property
    @exception_bridge
    def speed(self: "Self") -> "float":
        """float

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "Speed")

        if temp is None:
            return 0.0

        return temp

    @property
    def cast_to(self: "Self") -> "_Cast_PowerLoadForInjectionLossScripts":
        """Cast to another type.

        Returns:
            _Cast_PowerLoadForInjectionLossScripts
        """
        return _Cast_PowerLoadForInjectionLossScripts(self)
