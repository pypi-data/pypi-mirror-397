"""GearMeshDesignAnalysis"""

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
from mastapy._private.gears.analysis import _1362

_GEAR_MESH_DESIGN_ANALYSIS = python_net_import(
    "SMT.MastaAPI.Gears.Analysis", "GearMeshDesignAnalysis"
)

if TYPE_CHECKING:
    from typing import Any, Type, TypeVar

    from mastapy._private.gears.analysis import _1364, _1369, _1370, _1371, _1372
    from mastapy._private.gears.fe_model import _1344
    from mastapy._private.gears.fe_model.conical import _1351
    from mastapy._private.gears.fe_model.cylindrical import _1348
    from mastapy._private.gears.gear_designs.cylindrical.micro_geometry import (
        _1234,
        _1235,
    )
    from mastapy._private.gears.gear_designs.face import _1118
    from mastapy._private.gears.gear_two_d_fe_analysis import _1019, _1020
    from mastapy._private.gears.load_case import _1000
    from mastapy._private.gears.load_case.bevel import _1017
    from mastapy._private.gears.load_case.concept import _1015
    from mastapy._private.gears.load_case.conical import _1012
    from mastapy._private.gears.load_case.cylindrical import _1009
    from mastapy._private.gears.load_case.face import _1006
    from mastapy._private.gears.load_case.worm import _1003
    from mastapy._private.gears.ltca import _967
    from mastapy._private.gears.ltca.conical import _995
    from mastapy._private.gears.ltca.cylindrical import _982
    from mastapy._private.gears.manufacturing.bevel import _910, _911, _912, _913
    from mastapy._private.gears.manufacturing.cylindrical import _744, _745, _748

    Self = TypeVar("Self", bound="GearMeshDesignAnalysis")
    CastSelf = TypeVar(
        "CastSelf", bound="GearMeshDesignAnalysis._Cast_GearMeshDesignAnalysis"
    )


__docformat__ = "restructuredtext en"
__all__ = ("GearMeshDesignAnalysis",)


@extended_dataclass(frozen=True, slots=True, weakref_slot=True)
class _Cast_GearMeshDesignAnalysis:
    """Special nested class for casting GearMeshDesignAnalysis to subclasses."""

    __parent__: "GearMeshDesignAnalysis"

    @property
    def abstract_gear_mesh_analysis(
        self: "CastSelf",
    ) -> "_1362.AbstractGearMeshAnalysis":
        return self.__parent__._cast(_1362.AbstractGearMeshAnalysis)

    @property
    def cylindrical_manufactured_gear_mesh_duty_cycle(
        self: "CastSelf",
    ) -> "_744.CylindricalManufacturedGearMeshDutyCycle":
        from mastapy._private.gears.manufacturing.cylindrical import _744

        return self.__parent__._cast(_744.CylindricalManufacturedGearMeshDutyCycle)

    @property
    def cylindrical_manufactured_gear_mesh_load_case(
        self: "CastSelf",
    ) -> "_745.CylindricalManufacturedGearMeshLoadCase":
        from mastapy._private.gears.manufacturing.cylindrical import _745

        return self.__parent__._cast(_745.CylindricalManufacturedGearMeshLoadCase)

    @property
    def cylindrical_mesh_manufacturing_config(
        self: "CastSelf",
    ) -> "_748.CylindricalMeshManufacturingConfig":
        from mastapy._private.gears.manufacturing.cylindrical import _748

        return self.__parent__._cast(_748.CylindricalMeshManufacturingConfig)

    @property
    def conical_mesh_manufacturing_analysis(
        self: "CastSelf",
    ) -> "_910.ConicalMeshManufacturingAnalysis":
        from mastapy._private.gears.manufacturing.bevel import _910

        return self.__parent__._cast(_910.ConicalMeshManufacturingAnalysis)

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
    def mesh_load_case(self: "CastSelf") -> "_1000.MeshLoadCase":
        from mastapy._private.gears.load_case import _1000

        return self.__parent__._cast(_1000.MeshLoadCase)

    @property
    def worm_mesh_load_case(self: "CastSelf") -> "_1003.WormMeshLoadCase":
        from mastapy._private.gears.load_case.worm import _1003

        return self.__parent__._cast(_1003.WormMeshLoadCase)

    @property
    def face_mesh_load_case(self: "CastSelf") -> "_1006.FaceMeshLoadCase":
        from mastapy._private.gears.load_case.face import _1006

        return self.__parent__._cast(_1006.FaceMeshLoadCase)

    @property
    def cylindrical_mesh_load_case(self: "CastSelf") -> "_1009.CylindricalMeshLoadCase":
        from mastapy._private.gears.load_case.cylindrical import _1009

        return self.__parent__._cast(_1009.CylindricalMeshLoadCase)

    @property
    def conical_mesh_load_case(self: "CastSelf") -> "_1012.ConicalMeshLoadCase":
        from mastapy._private.gears.load_case.conical import _1012

        return self.__parent__._cast(_1012.ConicalMeshLoadCase)

    @property
    def concept_mesh_load_case(self: "CastSelf") -> "_1015.ConceptMeshLoadCase":
        from mastapy._private.gears.load_case.concept import _1015

        return self.__parent__._cast(_1015.ConceptMeshLoadCase)

    @property
    def bevel_mesh_load_case(self: "CastSelf") -> "_1017.BevelMeshLoadCase":
        from mastapy._private.gears.load_case.bevel import _1017

        return self.__parent__._cast(_1017.BevelMeshLoadCase)

    @property
    def cylindrical_gear_mesh_tiff_analysis(
        self: "CastSelf",
    ) -> "_1019.CylindricalGearMeshTIFFAnalysis":
        from mastapy._private.gears.gear_two_d_fe_analysis import _1019

        return self.__parent__._cast(_1019.CylindricalGearMeshTIFFAnalysis)

    @property
    def cylindrical_gear_mesh_tiff_analysis_duty_cycle(
        self: "CastSelf",
    ) -> "_1020.CylindricalGearMeshTIFFAnalysisDutyCycle":
        from mastapy._private.gears.gear_two_d_fe_analysis import _1020

        return self.__parent__._cast(_1020.CylindricalGearMeshTIFFAnalysisDutyCycle)

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
    def cylindrical_gear_mesh_micro_geometry_duty_cycle(
        self: "CastSelf",
    ) -> "_1235.CylindricalGearMeshMicroGeometryDutyCycle":
        from mastapy._private.gears.gear_designs.cylindrical.micro_geometry import _1235

        return self.__parent__._cast(_1235.CylindricalGearMeshMicroGeometryDutyCycle)

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
    def gear_mesh_implementation_analysis(
        self: "CastSelf",
    ) -> "_1369.GearMeshImplementationAnalysis":
        from mastapy._private.gears.analysis import _1369

        return self.__parent__._cast(_1369.GearMeshImplementationAnalysis)

    @property
    def gear_mesh_implementation_analysis_duty_cycle(
        self: "CastSelf",
    ) -> "_1370.GearMeshImplementationAnalysisDutyCycle":
        from mastapy._private.gears.analysis import _1370

        return self.__parent__._cast(_1370.GearMeshImplementationAnalysisDutyCycle)

    @property
    def gear_mesh_implementation_detail(
        self: "CastSelf",
    ) -> "_1371.GearMeshImplementationDetail":
        from mastapy._private.gears.analysis import _1371

        return self.__parent__._cast(_1371.GearMeshImplementationDetail)

    @property
    def gear_mesh_design_analysis(self: "CastSelf") -> "GearMeshDesignAnalysis":
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
class GearMeshDesignAnalysis(_1362.AbstractGearMeshAnalysis):
    """GearMeshDesignAnalysis

    This is a mastapy class.
    """

    TYPE: ClassVar["Type"] = _GEAR_MESH_DESIGN_ANALYSIS

    wrapped: "Any"

    def __post_init__(self: "Self") -> None:
        """Override of the post initialisation magic method."""
        if not hasattr(self.wrapped, "reference_count"):
            self.wrapped.reference_count = 0

        self.wrapped.reference_count += 1

    @property
    @exception_bridge
    def gear_a(self: "Self") -> "_1364.GearDesignAnalysis":
        """mastapy.gears.analysis.GearDesignAnalysis

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "GearA")

        if temp is None:
            return None

        type_ = temp.GetType()
        return constructor.new(type_.Namespace, type_.Name)(temp)

    @property
    @exception_bridge
    def gear_b(self: "Self") -> "_1364.GearDesignAnalysis":
        """mastapy.gears.analysis.GearDesignAnalysis

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "GearB")

        if temp is None:
            return None

        type_ = temp.GetType()
        return constructor.new(type_.Namespace, type_.Name)(temp)

    @property
    @exception_bridge
    def gear_set(self: "Self") -> "_1372.GearSetDesignAnalysis":
        """mastapy.gears.analysis.GearSetDesignAnalysis

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "GearSet")

        if temp is None:
            return None

        type_ = temp.GetType()
        return constructor.new(type_.Namespace, type_.Name)(temp)

    @property
    def cast_to(self: "Self") -> "_Cast_GearMeshDesignAnalysis":
        """Cast to another type.

        Returns:
            _Cast_GearMeshDesignAnalysis
        """
        return _Cast_GearMeshDesignAnalysis(self)
