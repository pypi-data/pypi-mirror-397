"""GearMaterial"""

from __future__ import annotations

from typing import TYPE_CHECKING, ClassVar

from mastapy._private._internal.dataclasses import extended_dataclass
from mastapy._private._internal.exception_bridge import exception_bridge
from mastapy._private._internal.exceptions import CastException
from mastapy._private._internal.python_net import (
    python_net_import,
    pythonnet_property_get,
    pythonnet_property_set,
)
from mastapy._private._internal.type_enforcement import enforce_parameter_types

from mastapy._private._internal import constructor, utility
from mastapy._private.materials import _371

_GEAR_MATERIAL = python_net_import("SMT.MastaAPI.Gears.Materials", "GearMaterial")

if TYPE_CHECKING:
    from typing import Any, Type, TypeVar

    from mastapy._private.gears.materials import (
        _696,
        _699,
        _701,
        _706,
        _719,
        _724,
        _728,
    )
    from mastapy._private.materials import _383
    from mastapy._private.utility.databases import _2061

    Self = TypeVar("Self", bound="GearMaterial")
    CastSelf = TypeVar("CastSelf", bound="GearMaterial._Cast_GearMaterial")


__docformat__ = "restructuredtext en"
__all__ = ("GearMaterial",)


@extended_dataclass(frozen=True, slots=True, weakref_slot=True)
class _Cast_GearMaterial:
    """Special nested class for casting GearMaterial to subclasses."""

    __parent__: "GearMaterial"

    @property
    def material(self: "CastSelf") -> "_371.Material":
        return self.__parent__._cast(_371.Material)

    @property
    def named_database_item(self: "CastSelf") -> "_2061.NamedDatabaseItem":
        from mastapy._private.utility.databases import _2061

        return self.__parent__._cast(_2061.NamedDatabaseItem)

    @property
    def agma_cylindrical_gear_material(
        self: "CastSelf",
    ) -> "_696.AGMACylindricalGearMaterial":
        from mastapy._private.gears.materials import _696

        return self.__parent__._cast(_696.AGMACylindricalGearMaterial)

    @property
    def bevel_gear_iso_material(self: "CastSelf") -> "_699.BevelGearISOMaterial":
        from mastapy._private.gears.materials import _699

        return self.__parent__._cast(_699.BevelGearISOMaterial)

    @property
    def bevel_gear_material(self: "CastSelf") -> "_701.BevelGearMaterial":
        from mastapy._private.gears.materials import _701

        return self.__parent__._cast(_701.BevelGearMaterial)

    @property
    def cylindrical_gear_material(self: "CastSelf") -> "_706.CylindricalGearMaterial":
        from mastapy._private.gears.materials import _706

        return self.__parent__._cast(_706.CylindricalGearMaterial)

    @property
    def iso_cylindrical_gear_material(
        self: "CastSelf",
    ) -> "_719.ISOCylindricalGearMaterial":
        from mastapy._private.gears.materials import _719

        return self.__parent__._cast(_719.ISOCylindricalGearMaterial)

    @property
    def klingelnberg_cyclo_palloid_conical_gear_material(
        self: "CastSelf",
    ) -> "_724.KlingelnbergCycloPalloidConicalGearMaterial":
        from mastapy._private.gears.materials import _724

        return self.__parent__._cast(_724.KlingelnbergCycloPalloidConicalGearMaterial)

    @property
    def plastic_cylindrical_gear_material(
        self: "CastSelf",
    ) -> "_728.PlasticCylindricalGearMaterial":
        from mastapy._private.gears.materials import _728

        return self.__parent__._cast(_728.PlasticCylindricalGearMaterial)

    @property
    def gear_material(self: "CastSelf") -> "GearMaterial":
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
class GearMaterial(_371.Material):
    """GearMaterial

    This is a mastapy class.
    """

    TYPE: ClassVar["Type"] = _GEAR_MATERIAL

    wrapped: "Any"

    def __post_init__(self: "Self") -> None:
        """Override of the post initialisation magic method."""
        if not hasattr(self.wrapped, "reference_count"):
            self.wrapped.reference_count = 0

        self.wrapped.reference_count += 1

    @property
    @exception_bridge
    def apply_derating_factors_to_bending_custom_sn_curve(self: "Self") -> "bool":
        """bool"""
        temp = pythonnet_property_get(
            self.wrapped, "ApplyDeratingFactorsToBendingCustomSNCurve"
        )

        if temp is None:
            return False

        return temp

    @apply_derating_factors_to_bending_custom_sn_curve.setter
    @exception_bridge
    @enforce_parameter_types
    def apply_derating_factors_to_bending_custom_sn_curve(
        self: "Self", value: "bool"
    ) -> None:
        pythonnet_property_set(
            self.wrapped,
            "ApplyDeratingFactorsToBendingCustomSNCurve",
            bool(value) if value is not None else False,
        )

    @property
    @exception_bridge
    def apply_derating_factors_to_contact_custom_sn_curve(self: "Self") -> "bool":
        """bool"""
        temp = pythonnet_property_get(
            self.wrapped, "ApplyDeratingFactorsToContactCustomSNCurve"
        )

        if temp is None:
            return False

        return temp

    @apply_derating_factors_to_contact_custom_sn_curve.setter
    @exception_bridge
    @enforce_parameter_types
    def apply_derating_factors_to_contact_custom_sn_curve(
        self: "Self", value: "bool"
    ) -> None:
        pythonnet_property_set(
            self.wrapped,
            "ApplyDeratingFactorsToContactCustomSNCurve",
            bool(value) if value is not None else False,
        )

    @property
    @exception_bridge
    def core_hardness(self: "Self") -> "float":
        """float"""
        temp = pythonnet_property_get(self.wrapped, "CoreHardness")

        if temp is None:
            return 0.0

        return temp

    @core_hardness.setter
    @exception_bridge
    @enforce_parameter_types
    def core_hardness(self: "Self", value: "float") -> None:
        pythonnet_property_set(
            self.wrapped, "CoreHardness", float(value) if value is not None else 0.0
        )

    @property
    @exception_bridge
    def n0_bending(self: "Self") -> "float":
        """float

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "N0Bending")

        if temp is None:
            return 0.0

        return temp

    @property
    @exception_bridge
    def n0_contact(self: "Self") -> "float":
        """float

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "N0Contact")

        if temp is None:
            return 0.0

        return temp

    @property
    @exception_bridge
    def nc_bending(self: "Self") -> "float":
        """float

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "NCBending")

        if temp is None:
            return 0.0

        return temp

    @property
    @exception_bridge
    def nc_contact(self: "Self") -> "float":
        """float

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "NCContact")

        if temp is None:
            return 0.0

        return temp

    @property
    @exception_bridge
    def number_of_known_points_for_user_sn_curve_bending_stress(self: "Self") -> "int":
        """int

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(
            self.wrapped, "NumberOfKnownPointsForUserSNCurveBendingStress"
        )

        if temp is None:
            return 0

        return temp

    @property
    @exception_bridge
    def number_of_known_points_for_user_sn_curve_for_contact_stress(
        self: "Self",
    ) -> "int":
        """int

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(
            self.wrapped, "NumberOfKnownPointsForUserSNCurveForContactStress"
        )

        if temp is None:
            return 0

        return temp

    @property
    @exception_bridge
    def sn_curve_bending(self: "Self") -> "_383.SNCurve":
        """mastapy.materials.SNCurve

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "SNCurveBending")

        if temp is None:
            return None

        type_ = temp.GetType()
        return constructor.new(type_.Namespace, type_.Name)(temp)

    @property
    @exception_bridge
    def sn_curve_contact(self: "Self") -> "_383.SNCurve":
        """mastapy.materials.SNCurve

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "SNCurveContact")

        if temp is None:
            return None

        type_ = temp.GetType()
        return constructor.new(type_.Namespace, type_.Name)(temp)

    @property
    def cast_to(self: "Self") -> "_Cast_GearMaterial":
        """Cast to another type.

        Returns:
            _Cast_GearMaterial
        """
        return _Cast_GearMaterial(self)
