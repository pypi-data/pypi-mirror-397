"""ConicalSetManufacturingAnalysis"""

from __future__ import annotations

from typing import TYPE_CHECKING, ClassVar

from mastapy._private._internal.dataclasses import extended_dataclass
from mastapy._private._internal.exceptions import CastException
from mastapy._private._internal.python_net import python_net_import

from mastapy._private._internal import utility
from mastapy._private.gears.analysis import _1374

_CONICAL_SET_MANUFACTURING_ANALYSIS = python_net_import(
    "SMT.MastaAPI.Gears.Manufacturing.Bevel", "ConicalSetManufacturingAnalysis"
)

if TYPE_CHECKING:
    from typing import Any, Type, TypeVar

    from mastapy._private.gears.analysis import _1363, _1372, _1375

    Self = TypeVar("Self", bound="ConicalSetManufacturingAnalysis")
    CastSelf = TypeVar(
        "CastSelf",
        bound="ConicalSetManufacturingAnalysis._Cast_ConicalSetManufacturingAnalysis",
    )


__docformat__ = "restructuredtext en"
__all__ = ("ConicalSetManufacturingAnalysis",)


@extended_dataclass(frozen=True, slots=True, weakref_slot=True)
class _Cast_ConicalSetManufacturingAnalysis:
    """Special nested class for casting ConicalSetManufacturingAnalysis to subclasses."""

    __parent__: "ConicalSetManufacturingAnalysis"

    @property
    def gear_set_implementation_analysis(
        self: "CastSelf",
    ) -> "_1374.GearSetImplementationAnalysis":
        return self.__parent__._cast(_1374.GearSetImplementationAnalysis)

    @property
    def gear_set_implementation_analysis_abstract(
        self: "CastSelf",
    ) -> "_1375.GearSetImplementationAnalysisAbstract":
        from mastapy._private.gears.analysis import _1375

        return self.__parent__._cast(_1375.GearSetImplementationAnalysisAbstract)

    @property
    def gear_set_design_analysis(self: "CastSelf") -> "_1372.GearSetDesignAnalysis":
        from mastapy._private.gears.analysis import _1372

        return self.__parent__._cast(_1372.GearSetDesignAnalysis)

    @property
    def abstract_gear_set_analysis(self: "CastSelf") -> "_1363.AbstractGearSetAnalysis":
        from mastapy._private.gears.analysis import _1363

        return self.__parent__._cast(_1363.AbstractGearSetAnalysis)

    @property
    def conical_set_manufacturing_analysis(
        self: "CastSelf",
    ) -> "ConicalSetManufacturingAnalysis":
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
class ConicalSetManufacturingAnalysis(_1374.GearSetImplementationAnalysis):
    """ConicalSetManufacturingAnalysis

    This is a mastapy class.
    """

    TYPE: ClassVar["Type"] = _CONICAL_SET_MANUFACTURING_ANALYSIS

    wrapped: "Any"

    def __post_init__(self: "Self") -> None:
        """Override of the post initialisation magic method."""
        if not hasattr(self.wrapped, "reference_count"):
            self.wrapped.reference_count = 0

        self.wrapped.reference_count += 1

    @property
    def cast_to(self: "Self") -> "_Cast_ConicalSetManufacturingAnalysis":
        """Cast to another type.

        Returns:
            _Cast_ConicalSetManufacturingAnalysis
        """
        return _Cast_ConicalSetManufacturingAnalysis(self)
