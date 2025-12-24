"""GearImplementationAnalysis"""

from __future__ import annotations

from typing import TYPE_CHECKING, ClassVar

from mastapy._private._internal.dataclasses import extended_dataclass
from mastapy._private._internal.exception_bridge import exception_bridge
from mastapy._private._internal.exceptions import CastException
from mastapy._private._internal.python_net import (
    python_net_import,
    pythonnet_property_get,
)

from mastapy._private._internal import constructor, utility
from mastapy._private.gears.analysis import _1364

_GEAR_IMPLEMENTATION_ANALYSIS = python_net_import(
    "SMT.MastaAPI.Gears.Analysis", "GearImplementationAnalysis"
)

if TYPE_CHECKING:
    from typing import Any, Type, TypeVar

    from mastapy._private.gears.analysis import _1361, _1374
    from mastapy._private.gears.ltca import _966
    from mastapy._private.gears.ltca.conical import _992
    from mastapy._private.gears.ltca.cylindrical import _981
    from mastapy._private.gears.manufacturing.bevel import _901
    from mastapy._private.gears.manufacturing.cylindrical import _743

    Self = TypeVar("Self", bound="GearImplementationAnalysis")
    CastSelf = TypeVar(
        "CastSelf", bound="GearImplementationAnalysis._Cast_GearImplementationAnalysis"
    )


__docformat__ = "restructuredtext en"
__all__ = ("GearImplementationAnalysis",)


@extended_dataclass(frozen=True, slots=True, weakref_slot=True)
class _Cast_GearImplementationAnalysis:
    """Special nested class for casting GearImplementationAnalysis to subclasses."""

    __parent__: "GearImplementationAnalysis"

    @property
    def gear_design_analysis(self: "CastSelf") -> "_1364.GearDesignAnalysis":
        return self.__parent__._cast(_1364.GearDesignAnalysis)

    @property
    def abstract_gear_analysis(self: "CastSelf") -> "_1361.AbstractGearAnalysis":
        from mastapy._private.gears.analysis import _1361

        return self.__parent__._cast(_1361.AbstractGearAnalysis)

    @property
    def cylindrical_manufactured_gear_load_case(
        self: "CastSelf",
    ) -> "_743.CylindricalManufacturedGearLoadCase":
        from mastapy._private.gears.manufacturing.cylindrical import _743

        return self.__parent__._cast(_743.CylindricalManufacturedGearLoadCase)

    @property
    def conical_gear_manufacturing_analysis(
        self: "CastSelf",
    ) -> "_901.ConicalGearManufacturingAnalysis":
        from mastapy._private.gears.manufacturing.bevel import _901

        return self.__parent__._cast(_901.ConicalGearManufacturingAnalysis)

    @property
    def gear_load_distribution_analysis(
        self: "CastSelf",
    ) -> "_966.GearLoadDistributionAnalysis":
        from mastapy._private.gears.ltca import _966

        return self.__parent__._cast(_966.GearLoadDistributionAnalysis)

    @property
    def cylindrical_gear_load_distribution_analysis(
        self: "CastSelf",
    ) -> "_981.CylindricalGearLoadDistributionAnalysis":
        from mastapy._private.gears.ltca.cylindrical import _981

        return self.__parent__._cast(_981.CylindricalGearLoadDistributionAnalysis)

    @property
    def conical_gear_load_distribution_analysis(
        self: "CastSelf",
    ) -> "_992.ConicalGearLoadDistributionAnalysis":
        from mastapy._private.gears.ltca.conical import _992

        return self.__parent__._cast(_992.ConicalGearLoadDistributionAnalysis)

    @property
    def gear_implementation_analysis(self: "CastSelf") -> "GearImplementationAnalysis":
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
class GearImplementationAnalysis(_1364.GearDesignAnalysis):
    """GearImplementationAnalysis

    This is a mastapy class.
    """

    TYPE: ClassVar["Type"] = _GEAR_IMPLEMENTATION_ANALYSIS

    wrapped: "Any"

    def __post_init__(self: "Self") -> None:
        """Override of the post initialisation magic method."""
        if not hasattr(self.wrapped, "reference_count"):
            self.wrapped.reference_count = 0

        self.wrapped.reference_count += 1

    @property
    @exception_bridge
    def gear_set(self: "Self") -> "_1374.GearSetImplementationAnalysis":
        """mastapy.gears.analysis.GearSetImplementationAnalysis

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "GearSet")

        if temp is None:
            return None

        type_ = temp.GetType()
        return constructor.new(type_.Namespace, type_.Name)(temp)

    @property
    def cast_to(self: "Self") -> "_Cast_GearImplementationAnalysis":
        """Cast to another type.

        Returns:
            _Cast_GearImplementationAnalysis
        """
        return _Cast_GearImplementationAnalysis(self)
