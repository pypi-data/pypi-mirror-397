"""AbstractShaftOrHousing"""

from __future__ import annotations

from typing import TYPE_CHECKING, ClassVar

from mastapy._private._internal.dataclasses import extended_dataclass
from mastapy._private._internal.exceptions import CastException
from mastapy._private._internal.python_net import python_net_import

from mastapy._private._internal import utility
from mastapy._private.system_model.part_model import _2714

_ABSTRACT_SHAFT_OR_HOUSING = python_net_import(
    "SMT.MastaAPI.SystemModel.PartModel", "AbstractShaftOrHousing"
)

if TYPE_CHECKING:
    from typing import Any, Type, TypeVar

    from mastapy._private.system_model import _2451
    from mastapy._private.system_model.part_model import _2704, _2724, _2742
    from mastapy._private.system_model.part_model.cycloidal import _2851
    from mastapy._private.system_model.part_model.shaft_model import _2758

    Self = TypeVar("Self", bound="AbstractShaftOrHousing")
    CastSelf = TypeVar(
        "CastSelf", bound="AbstractShaftOrHousing._Cast_AbstractShaftOrHousing"
    )


__docformat__ = "restructuredtext en"
__all__ = ("AbstractShaftOrHousing",)


@extended_dataclass(frozen=True, slots=True, weakref_slot=True)
class _Cast_AbstractShaftOrHousing:
    """Special nested class for casting AbstractShaftOrHousing to subclasses."""

    __parent__: "AbstractShaftOrHousing"

    @property
    def component(self: "CastSelf") -> "_2714.Component":
        return self.__parent__._cast(_2714.Component)

    @property
    def part(self: "CastSelf") -> "_2742.Part":
        from mastapy._private.system_model.part_model import _2742

        return self.__parent__._cast(_2742.Part)

    @property
    def design_entity(self: "CastSelf") -> "_2451.DesignEntity":
        from mastapy._private.system_model import _2451

        return self.__parent__._cast(_2451.DesignEntity)

    @property
    def abstract_shaft(self: "CastSelf") -> "_2704.AbstractShaft":
        from mastapy._private.system_model.part_model import _2704

        return self.__parent__._cast(_2704.AbstractShaft)

    @property
    def fe_part(self: "CastSelf") -> "_2724.FEPart":
        from mastapy._private.system_model.part_model import _2724

        return self.__parent__._cast(_2724.FEPart)

    @property
    def shaft(self: "CastSelf") -> "_2758.Shaft":
        from mastapy._private.system_model.part_model.shaft_model import _2758

        return self.__parent__._cast(_2758.Shaft)

    @property
    def cycloidal_disc(self: "CastSelf") -> "_2851.CycloidalDisc":
        from mastapy._private.system_model.part_model.cycloidal import _2851

        return self.__parent__._cast(_2851.CycloidalDisc)

    @property
    def abstract_shaft_or_housing(self: "CastSelf") -> "AbstractShaftOrHousing":
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
class AbstractShaftOrHousing(_2714.Component):
    """AbstractShaftOrHousing

    This is a mastapy class.
    """

    TYPE: ClassVar["Type"] = _ABSTRACT_SHAFT_OR_HOUSING

    wrapped: "Any"

    def __post_init__(self: "Self") -> None:
        """Override of the post initialisation magic method."""
        if not hasattr(self.wrapped, "reference_count"):
            self.wrapped.reference_count = 0

        self.wrapped.reference_count += 1

    @property
    def cast_to(self: "Self") -> "_Cast_AbstractShaftOrHousing":
        """Cast to another type.

        Returns:
            _Cast_AbstractShaftOrHousing
        """
        return _Cast_AbstractShaftOrHousing(self)
