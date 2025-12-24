"""GearMeshImplementationAnalysis"""

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
from mastapy._private.gears.analysis import _1368

_GEAR_MESH_IMPLEMENTATION_ANALYSIS = python_net_import(
    "SMT.MastaAPI.Gears.Analysis", "GearMeshImplementationAnalysis"
)

if TYPE_CHECKING:
    from typing import Any, Type, TypeVar

    from mastapy._private.gears.analysis import _1362, _1374
    from mastapy._private.gears.ltca import _967
    from mastapy._private.gears.ltca.conical import _995
    from mastapy._private.gears.ltca.cylindrical import _982
    from mastapy._private.gears.manufacturing.bevel import _910
    from mastapy._private.gears.manufacturing.cylindrical import _745

    Self = TypeVar("Self", bound="GearMeshImplementationAnalysis")
    CastSelf = TypeVar(
        "CastSelf",
        bound="GearMeshImplementationAnalysis._Cast_GearMeshImplementationAnalysis",
    )


__docformat__ = "restructuredtext en"
__all__ = ("GearMeshImplementationAnalysis",)


@extended_dataclass(frozen=True, slots=True, weakref_slot=True)
class _Cast_GearMeshImplementationAnalysis:
    """Special nested class for casting GearMeshImplementationAnalysis to subclasses."""

    __parent__: "GearMeshImplementationAnalysis"

    @property
    def gear_mesh_design_analysis(self: "CastSelf") -> "_1368.GearMeshDesignAnalysis":
        return self.__parent__._cast(_1368.GearMeshDesignAnalysis)

    @property
    def abstract_gear_mesh_analysis(
        self: "CastSelf",
    ) -> "_1362.AbstractGearMeshAnalysis":
        from mastapy._private.gears.analysis import _1362

        return self.__parent__._cast(_1362.AbstractGearMeshAnalysis)

    @property
    def cylindrical_manufactured_gear_mesh_load_case(
        self: "CastSelf",
    ) -> "_745.CylindricalManufacturedGearMeshLoadCase":
        from mastapy._private.gears.manufacturing.cylindrical import _745

        return self.__parent__._cast(_745.CylindricalManufacturedGearMeshLoadCase)

    @property
    def conical_mesh_manufacturing_analysis(
        self: "CastSelf",
    ) -> "_910.ConicalMeshManufacturingAnalysis":
        from mastapy._private.gears.manufacturing.bevel import _910

        return self.__parent__._cast(_910.ConicalMeshManufacturingAnalysis)

    @property
    def gear_mesh_load_distribution_analysis(
        self: "CastSelf",
    ) -> "_967.GearMeshLoadDistributionAnalysis":
        from mastapy._private.gears.ltca import _967

        return self.__parent__._cast(_967.GearMeshLoadDistributionAnalysis)

    @property
    def cylindrical_gear_mesh_load_distribution_analysis(
        self: "CastSelf",
    ) -> "_982.CylindricalGearMeshLoadDistributionAnalysis":
        from mastapy._private.gears.ltca.cylindrical import _982

        return self.__parent__._cast(_982.CylindricalGearMeshLoadDistributionAnalysis)

    @property
    def conical_mesh_load_distribution_analysis(
        self: "CastSelf",
    ) -> "_995.ConicalMeshLoadDistributionAnalysis":
        from mastapy._private.gears.ltca.conical import _995

        return self.__parent__._cast(_995.ConicalMeshLoadDistributionAnalysis)

    @property
    def gear_mesh_implementation_analysis(
        self: "CastSelf",
    ) -> "GearMeshImplementationAnalysis":
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
class GearMeshImplementationAnalysis(_1368.GearMeshDesignAnalysis):
    """GearMeshImplementationAnalysis

    This is a mastapy class.
    """

    TYPE: ClassVar["Type"] = _GEAR_MESH_IMPLEMENTATION_ANALYSIS

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
    def cast_to(self: "Self") -> "_Cast_GearMeshImplementationAnalysis":
        """Cast to another type.

        Returns:
            _Cast_GearMeshImplementationAnalysis
        """
        return _Cast_GearMeshImplementationAnalysis(self)
