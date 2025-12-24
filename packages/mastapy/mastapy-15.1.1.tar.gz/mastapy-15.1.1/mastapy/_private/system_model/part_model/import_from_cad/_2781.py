"""CylindricalRingGearFromCAD"""

from __future__ import annotations

from typing import TYPE_CHECKING, ClassVar

from mastapy._private._internal.dataclasses import extended_dataclass
from mastapy._private._internal.exceptions import CastException
from mastapy._private._internal.python_net import python_net_import

from mastapy._private._internal import utility
from mastapy._private.system_model.part_model.import_from_cad import _2779

_CYLINDRICAL_RING_GEAR_FROM_CAD = python_net_import(
    "SMT.MastaAPI.SystemModel.PartModel.ImportFromCAD", "CylindricalRingGearFromCAD"
)

if TYPE_CHECKING:
    from typing import Any, Type, TypeVar

    from mastapy._private.system_model.part_model.import_from_cad import (
        _2774,
        _2775,
        _2778,
        _2784,
    )

    Self = TypeVar("Self", bound="CylindricalRingGearFromCAD")
    CastSelf = TypeVar(
        "CastSelf", bound="CylindricalRingGearFromCAD._Cast_CylindricalRingGearFromCAD"
    )


__docformat__ = "restructuredtext en"
__all__ = ("CylindricalRingGearFromCAD",)


@extended_dataclass(frozen=True, slots=True, weakref_slot=True)
class _Cast_CylindricalRingGearFromCAD:
    """Special nested class for casting CylindricalRingGearFromCAD to subclasses."""

    __parent__: "CylindricalRingGearFromCAD"

    @property
    def cylindrical_gear_in_planetary_set_from_cad(
        self: "CastSelf",
    ) -> "_2779.CylindricalGearInPlanetarySetFromCAD":
        return self.__parent__._cast(_2779.CylindricalGearInPlanetarySetFromCAD)

    @property
    def cylindrical_gear_from_cad(self: "CastSelf") -> "_2778.CylindricalGearFromCAD":
        from mastapy._private.system_model.part_model.import_from_cad import _2778

        return self.__parent__._cast(_2778.CylindricalGearFromCAD)

    @property
    def mountable_component_from_cad(
        self: "CastSelf",
    ) -> "_2784.MountableComponentFromCAD":
        from mastapy._private.system_model.part_model.import_from_cad import _2784

        return self.__parent__._cast(_2784.MountableComponentFromCAD)

    @property
    def component_from_cad(self: "CastSelf") -> "_2774.ComponentFromCAD":
        from mastapy._private.system_model.part_model.import_from_cad import _2774

        return self.__parent__._cast(_2774.ComponentFromCAD)

    @property
    def component_from_cad_base(self: "CastSelf") -> "_2775.ComponentFromCADBase":
        from mastapy._private.system_model.part_model.import_from_cad import _2775

        return self.__parent__._cast(_2775.ComponentFromCADBase)

    @property
    def cylindrical_ring_gear_from_cad(
        self: "CastSelf",
    ) -> "CylindricalRingGearFromCAD":
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
class CylindricalRingGearFromCAD(_2779.CylindricalGearInPlanetarySetFromCAD):
    """CylindricalRingGearFromCAD

    This is a mastapy class.
    """

    TYPE: ClassVar["Type"] = _CYLINDRICAL_RING_GEAR_FROM_CAD

    wrapped: "Any"

    def __post_init__(self: "Self") -> None:
        """Override of the post initialisation magic method."""
        if not hasattr(self.wrapped, "reference_count"):
            self.wrapped.reference_count = 0

        self.wrapped.reference_count += 1

    @property
    def cast_to(self: "Self") -> "_Cast_CylindricalRingGearFromCAD":
        """Cast to another type.

        Returns:
            _Cast_CylindricalRingGearFromCAD
        """
        return _Cast_CylindricalRingGearFromCAD(self)
