"""GearImplementationDetail"""

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

_GEAR_IMPLEMENTATION_DETAIL = python_net_import(
    "SMT.MastaAPI.Gears.Analysis", "GearImplementationDetail"
)

if TYPE_CHECKING:
    from typing import Any, Type, TypeVar

    from mastapy._private.gears.analysis import _1361, _1377
    from mastapy._private.gears.fe_model import _1343
    from mastapy._private.gears.fe_model.conical import _1350
    from mastapy._private.gears.fe_model.cylindrical import _1347
    from mastapy._private.gears.gear_designs.cylindrical.micro_geometry import (
        _1236,
        _1237,
        _1240,
    )
    from mastapy._private.gears.gear_designs.face import _1119
    from mastapy._private.gears.manufacturing.bevel import (
        _902,
        _903,
        _904,
        _914,
        _915,
        _920,
    )
    from mastapy._private.gears.manufacturing.cylindrical import _738
    from mastapy._private.utility.scripting import _1968

    Self = TypeVar("Self", bound="GearImplementationDetail")
    CastSelf = TypeVar(
        "CastSelf", bound="GearImplementationDetail._Cast_GearImplementationDetail"
    )


__docformat__ = "restructuredtext en"
__all__ = ("GearImplementationDetail",)


@extended_dataclass(frozen=True, slots=True, weakref_slot=True)
class _Cast_GearImplementationDetail:
    """Special nested class for casting GearImplementationDetail to subclasses."""

    __parent__: "GearImplementationDetail"

    @property
    def gear_design_analysis(self: "CastSelf") -> "_1364.GearDesignAnalysis":
        return self.__parent__._cast(_1364.GearDesignAnalysis)

    @property
    def abstract_gear_analysis(self: "CastSelf") -> "_1361.AbstractGearAnalysis":
        from mastapy._private.gears.analysis import _1361

        return self.__parent__._cast(_1361.AbstractGearAnalysis)

    @property
    def cylindrical_gear_manufacturing_config(
        self: "CastSelf",
    ) -> "_738.CylindricalGearManufacturingConfig":
        from mastapy._private.gears.manufacturing.cylindrical import _738

        return self.__parent__._cast(_738.CylindricalGearManufacturingConfig)

    @property
    def conical_gear_manufacturing_config(
        self: "CastSelf",
    ) -> "_902.ConicalGearManufacturingConfig":
        from mastapy._private.gears.manufacturing.bevel import _902

        return self.__parent__._cast(_902.ConicalGearManufacturingConfig)

    @property
    def conical_gear_micro_geometry_config(
        self: "CastSelf",
    ) -> "_903.ConicalGearMicroGeometryConfig":
        from mastapy._private.gears.manufacturing.bevel import _903

        return self.__parent__._cast(_903.ConicalGearMicroGeometryConfig)

    @property
    def conical_gear_micro_geometry_config_base(
        self: "CastSelf",
    ) -> "_904.ConicalGearMicroGeometryConfigBase":
        from mastapy._private.gears.manufacturing.bevel import _904

        return self.__parent__._cast(_904.ConicalGearMicroGeometryConfigBase)

    @property
    def conical_pinion_manufacturing_config(
        self: "CastSelf",
    ) -> "_914.ConicalPinionManufacturingConfig":
        from mastapy._private.gears.manufacturing.bevel import _914

        return self.__parent__._cast(_914.ConicalPinionManufacturingConfig)

    @property
    def conical_pinion_micro_geometry_config(
        self: "CastSelf",
    ) -> "_915.ConicalPinionMicroGeometryConfig":
        from mastapy._private.gears.manufacturing.bevel import _915

        return self.__parent__._cast(_915.ConicalPinionMicroGeometryConfig)

    @property
    def conical_wheel_manufacturing_config(
        self: "CastSelf",
    ) -> "_920.ConicalWheelManufacturingConfig":
        from mastapy._private.gears.manufacturing.bevel import _920

        return self.__parent__._cast(_920.ConicalWheelManufacturingConfig)

    @property
    def face_gear_micro_geometry(self: "CastSelf") -> "_1119.FaceGearMicroGeometry":
        from mastapy._private.gears.gear_designs.face import _1119

        return self.__parent__._cast(_1119.FaceGearMicroGeometry)

    @property
    def cylindrical_gear_micro_geometry(
        self: "CastSelf",
    ) -> "_1236.CylindricalGearMicroGeometry":
        from mastapy._private.gears.gear_designs.cylindrical.micro_geometry import _1236

        return self.__parent__._cast(_1236.CylindricalGearMicroGeometry)

    @property
    def cylindrical_gear_micro_geometry_base(
        self: "CastSelf",
    ) -> "_1237.CylindricalGearMicroGeometryBase":
        from mastapy._private.gears.gear_designs.cylindrical.micro_geometry import _1237

        return self.__parent__._cast(_1237.CylindricalGearMicroGeometryBase)

    @property
    def cylindrical_gear_micro_geometry_per_tooth(
        self: "CastSelf",
    ) -> "_1240.CylindricalGearMicroGeometryPerTooth":
        from mastapy._private.gears.gear_designs.cylindrical.micro_geometry import _1240

        return self.__parent__._cast(_1240.CylindricalGearMicroGeometryPerTooth)

    @property
    def gear_fe_model(self: "CastSelf") -> "_1343.GearFEModel":
        from mastapy._private.gears.fe_model import _1343

        return self.__parent__._cast(_1343.GearFEModel)

    @property
    def cylindrical_gear_fe_model(self: "CastSelf") -> "_1347.CylindricalGearFEModel":
        from mastapy._private.gears.fe_model.cylindrical import _1347

        return self.__parent__._cast(_1347.CylindricalGearFEModel)

    @property
    def conical_gear_fe_model(self: "CastSelf") -> "_1350.ConicalGearFEModel":
        from mastapy._private.gears.fe_model.conical import _1350

        return self.__parent__._cast(_1350.ConicalGearFEModel)

    @property
    def gear_implementation_detail(self: "CastSelf") -> "GearImplementationDetail":
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
class GearImplementationDetail(_1364.GearDesignAnalysis):
    """GearImplementationDetail

    This is a mastapy class.
    """

    TYPE: ClassVar["Type"] = _GEAR_IMPLEMENTATION_DETAIL

    wrapped: "Any"

    def __post_init__(self: "Self") -> None:
        """Override of the post initialisation magic method."""
        if not hasattr(self.wrapped, "reference_count"):
            self.wrapped.reference_count = 0

        self.wrapped.reference_count += 1

    @property
    @exception_bridge
    def gear_set(self: "Self") -> "_1377.GearSetImplementationDetail":
        """mastapy.gears.analysis.GearSetImplementationDetail

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "GearSet")

        if temp is None:
            return None

        type_ = temp.GetType()
        return constructor.new(type_.Namespace, type_.Name)(temp)

    @property
    @exception_bridge
    def user_specified_data(self: "Self") -> "_1968.UserSpecifiedData":
        """mastapy.utility.scripting.UserSpecifiedData

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "UserSpecifiedData")

        if temp is None:
            return None

        type_ = temp.GetType()
        return constructor.new(type_.Namespace, type_.Name)(temp)

    @property
    def cast_to(self: "Self") -> "_Cast_GearImplementationDetail":
        """Cast to another type.

        Returns:
            _Cast_GearImplementationDetail
        """
        return _Cast_GearImplementationDetail(self)
