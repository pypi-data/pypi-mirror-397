"""GearMeshImplementationDetail"""

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

_GEAR_MESH_IMPLEMENTATION_DETAIL = python_net_import(
    "SMT.MastaAPI.Gears.Analysis", "GearMeshImplementationDetail"
)

if TYPE_CHECKING:
    from typing import Any, Type, TypeVar

    from mastapy._private.gears.analysis import _1362, _1377
    from mastapy._private.gears.fe_model import _1344
    from mastapy._private.gears.fe_model.conical import _1351
    from mastapy._private.gears.fe_model.cylindrical import _1348
    from mastapy._private.gears.gear_designs.cylindrical.micro_geometry import _1234
    from mastapy._private.gears.gear_designs.face import _1118
    from mastapy._private.gears.manufacturing.bevel import _911, _912, _913
    from mastapy._private.gears.manufacturing.cylindrical import _748

    Self = TypeVar("Self", bound="GearMeshImplementationDetail")
    CastSelf = TypeVar(
        "CastSelf",
        bound="GearMeshImplementationDetail._Cast_GearMeshImplementationDetail",
    )


__docformat__ = "restructuredtext en"
__all__ = ("GearMeshImplementationDetail",)


@extended_dataclass(frozen=True, slots=True, weakref_slot=True)
class _Cast_GearMeshImplementationDetail:
    """Special nested class for casting GearMeshImplementationDetail to subclasses."""

    __parent__: "GearMeshImplementationDetail"

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
    def cylindrical_mesh_manufacturing_config(
        self: "CastSelf",
    ) -> "_748.CylindricalMeshManufacturingConfig":
        from mastapy._private.gears.manufacturing.cylindrical import _748

        return self.__parent__._cast(_748.CylindricalMeshManufacturingConfig)

    @property
    def conical_mesh_manufacturing_config(
        self: "CastSelf",
    ) -> "_911.ConicalMeshManufacturingConfig":
        from mastapy._private.gears.manufacturing.bevel import _911

        return self.__parent__._cast(_911.ConicalMeshManufacturingConfig)

    @property
    def conical_mesh_micro_geometry_config(
        self: "CastSelf",
    ) -> "_912.ConicalMeshMicroGeometryConfig":
        from mastapy._private.gears.manufacturing.bevel import _912

        return self.__parent__._cast(_912.ConicalMeshMicroGeometryConfig)

    @property
    def conical_mesh_micro_geometry_config_base(
        self: "CastSelf",
    ) -> "_913.ConicalMeshMicroGeometryConfigBase":
        from mastapy._private.gears.manufacturing.bevel import _913

        return self.__parent__._cast(_913.ConicalMeshMicroGeometryConfigBase)

    @property
    def face_gear_mesh_micro_geometry(
        self: "CastSelf",
    ) -> "_1118.FaceGearMeshMicroGeometry":
        from mastapy._private.gears.gear_designs.face import _1118

        return self.__parent__._cast(_1118.FaceGearMeshMicroGeometry)

    @property
    def cylindrical_gear_mesh_micro_geometry(
        self: "CastSelf",
    ) -> "_1234.CylindricalGearMeshMicroGeometry":
        from mastapy._private.gears.gear_designs.cylindrical.micro_geometry import _1234

        return self.__parent__._cast(_1234.CylindricalGearMeshMicroGeometry)

    @property
    def gear_mesh_fe_model(self: "CastSelf") -> "_1344.GearMeshFEModel":
        from mastapy._private.gears.fe_model import _1344

        return self.__parent__._cast(_1344.GearMeshFEModel)

    @property
    def cylindrical_gear_mesh_fe_model(
        self: "CastSelf",
    ) -> "_1348.CylindricalGearMeshFEModel":
        from mastapy._private.gears.fe_model.cylindrical import _1348

        return self.__parent__._cast(_1348.CylindricalGearMeshFEModel)

    @property
    def conical_mesh_fe_model(self: "CastSelf") -> "_1351.ConicalMeshFEModel":
        from mastapy._private.gears.fe_model.conical import _1351

        return self.__parent__._cast(_1351.ConicalMeshFEModel)

    @property
    def gear_mesh_implementation_detail(
        self: "CastSelf",
    ) -> "GearMeshImplementationDetail":
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
class GearMeshImplementationDetail(_1368.GearMeshDesignAnalysis):
    """GearMeshImplementationDetail

    This is a mastapy class.
    """

    TYPE: ClassVar["Type"] = _GEAR_MESH_IMPLEMENTATION_DETAIL

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
    def cast_to(self: "Self") -> "_Cast_GearMeshImplementationDetail":
        """Cast to another type.

        Returns:
            _Cast_GearMeshImplementationDetail
        """
        return _Cast_GearMeshImplementationDetail(self)
