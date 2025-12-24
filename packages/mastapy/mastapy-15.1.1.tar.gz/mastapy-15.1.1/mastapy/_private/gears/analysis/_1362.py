"""AbstractGearMeshAnalysis"""

from __future__ import annotations

from typing import TYPE_CHECKING, ClassVar

from mastapy._private._internal.dataclasses import extended_dataclass
from mastapy._private._internal.exception_bridge import exception_bridge
from mastapy._private._internal.exceptions import CastException
from mastapy._private._internal.python_net import (
    python_net_import,
    pythonnet_method_call,
    pythonnet_property_get,
)
from mastapy._private._internal.type_enforcement import enforce_parameter_types

from mastapy._private import _0
from mastapy._private._internal import constructor, conversion, utility

_ABSTRACT_GEAR_MESH_ANALYSIS = python_net_import(
    "SMT.MastaAPI.Gears.Analysis", "AbstractGearMeshAnalysis"
)

if TYPE_CHECKING:
    from typing import Any, List, Type, TypeVar

    from mastapy._private._internal.typing import PathLike

    from mastapy._private.gears.analysis import _1361, _1363, _1368, _1369, _1370, _1371
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
    from mastapy._private.gears.rating import _465, _473, _478
    from mastapy._private.gears.rating.agma_gleason_conical import _678
    from mastapy._private.gears.rating.bevel import _667
    from mastapy._private.gears.rating.concept import _662, _663
    from mastapy._private.gears.rating.conical import _652, _657
    from mastapy._private.gears.rating.cylindrical import _571, _579
    from mastapy._private.gears.rating.face import _559, _560
    from mastapy._private.gears.rating.hypoid import _551
    from mastapy._private.gears.rating.klingelnberg_conical import _524
    from mastapy._private.gears.rating.klingelnberg_hypoid import _521
    from mastapy._private.gears.rating.klingelnberg_spiral_bevel import _518
    from mastapy._private.gears.rating.spiral_bevel import _515
    from mastapy._private.gears.rating.straight_bevel import _508
    from mastapy._private.gears.rating.straight_bevel_diff import _511
    from mastapy._private.gears.rating.worm import _486, _490
    from mastapy._private.gears.rating.zerol_bevel import _482

    Self = TypeVar("Self", bound="AbstractGearMeshAnalysis")
    CastSelf = TypeVar(
        "CastSelf", bound="AbstractGearMeshAnalysis._Cast_AbstractGearMeshAnalysis"
    )


__docformat__ = "restructuredtext en"
__all__ = ("AbstractGearMeshAnalysis",)


@extended_dataclass(frozen=True, slots=True, weakref_slot=True)
class _Cast_AbstractGearMeshAnalysis:
    """Special nested class for casting AbstractGearMeshAnalysis to subclasses."""

    __parent__: "AbstractGearMeshAnalysis"

    @property
    def abstract_gear_mesh_rating(self: "CastSelf") -> "_465.AbstractGearMeshRating":
        from mastapy._private.gears.rating import _465

        return self.__parent__._cast(_465.AbstractGearMeshRating)

    @property
    def gear_mesh_rating(self: "CastSelf") -> "_473.GearMeshRating":
        from mastapy._private.gears.rating import _473

        return self.__parent__._cast(_473.GearMeshRating)

    @property
    def mesh_duty_cycle_rating(self: "CastSelf") -> "_478.MeshDutyCycleRating":
        from mastapy._private.gears.rating import _478

        return self.__parent__._cast(_478.MeshDutyCycleRating)

    @property
    def zerol_bevel_gear_mesh_rating(
        self: "CastSelf",
    ) -> "_482.ZerolBevelGearMeshRating":
        from mastapy._private.gears.rating.zerol_bevel import _482

        return self.__parent__._cast(_482.ZerolBevelGearMeshRating)

    @property
    def worm_gear_mesh_rating(self: "CastSelf") -> "_486.WormGearMeshRating":
        from mastapy._private.gears.rating.worm import _486

        return self.__parent__._cast(_486.WormGearMeshRating)

    @property
    def worm_mesh_duty_cycle_rating(self: "CastSelf") -> "_490.WormMeshDutyCycleRating":
        from mastapy._private.gears.rating.worm import _490

        return self.__parent__._cast(_490.WormMeshDutyCycleRating)

    @property
    def straight_bevel_gear_mesh_rating(
        self: "CastSelf",
    ) -> "_508.StraightBevelGearMeshRating":
        from mastapy._private.gears.rating.straight_bevel import _508

        return self.__parent__._cast(_508.StraightBevelGearMeshRating)

    @property
    def straight_bevel_diff_gear_mesh_rating(
        self: "CastSelf",
    ) -> "_511.StraightBevelDiffGearMeshRating":
        from mastapy._private.gears.rating.straight_bevel_diff import _511

        return self.__parent__._cast(_511.StraightBevelDiffGearMeshRating)

    @property
    def spiral_bevel_gear_mesh_rating(
        self: "CastSelf",
    ) -> "_515.SpiralBevelGearMeshRating":
        from mastapy._private.gears.rating.spiral_bevel import _515

        return self.__parent__._cast(_515.SpiralBevelGearMeshRating)

    @property
    def klingelnberg_cyclo_palloid_spiral_bevel_gear_mesh_rating(
        self: "CastSelf",
    ) -> "_518.KlingelnbergCycloPalloidSpiralBevelGearMeshRating":
        from mastapy._private.gears.rating.klingelnberg_spiral_bevel import _518

        return self.__parent__._cast(
            _518.KlingelnbergCycloPalloidSpiralBevelGearMeshRating
        )

    @property
    def klingelnberg_cyclo_palloid_hypoid_gear_mesh_rating(
        self: "CastSelf",
    ) -> "_521.KlingelnbergCycloPalloidHypoidGearMeshRating":
        from mastapy._private.gears.rating.klingelnberg_hypoid import _521

        return self.__parent__._cast(_521.KlingelnbergCycloPalloidHypoidGearMeshRating)

    @property
    def klingelnberg_cyclo_palloid_conical_gear_mesh_rating(
        self: "CastSelf",
    ) -> "_524.KlingelnbergCycloPalloidConicalGearMeshRating":
        from mastapy._private.gears.rating.klingelnberg_conical import _524

        return self.__parent__._cast(_524.KlingelnbergCycloPalloidConicalGearMeshRating)

    @property
    def hypoid_gear_mesh_rating(self: "CastSelf") -> "_551.HypoidGearMeshRating":
        from mastapy._private.gears.rating.hypoid import _551

        return self.__parent__._cast(_551.HypoidGearMeshRating)

    @property
    def face_gear_mesh_duty_cycle_rating(
        self: "CastSelf",
    ) -> "_559.FaceGearMeshDutyCycleRating":
        from mastapy._private.gears.rating.face import _559

        return self.__parent__._cast(_559.FaceGearMeshDutyCycleRating)

    @property
    def face_gear_mesh_rating(self: "CastSelf") -> "_560.FaceGearMeshRating":
        from mastapy._private.gears.rating.face import _560

        return self.__parent__._cast(_560.FaceGearMeshRating)

    @property
    def cylindrical_gear_mesh_rating(
        self: "CastSelf",
    ) -> "_571.CylindricalGearMeshRating":
        from mastapy._private.gears.rating.cylindrical import _571

        return self.__parent__._cast(_571.CylindricalGearMeshRating)

    @property
    def cylindrical_mesh_duty_cycle_rating(
        self: "CastSelf",
    ) -> "_579.CylindricalMeshDutyCycleRating":
        from mastapy._private.gears.rating.cylindrical import _579

        return self.__parent__._cast(_579.CylindricalMeshDutyCycleRating)

    @property
    def conical_gear_mesh_rating(self: "CastSelf") -> "_652.ConicalGearMeshRating":
        from mastapy._private.gears.rating.conical import _652

        return self.__parent__._cast(_652.ConicalGearMeshRating)

    @property
    def conical_mesh_duty_cycle_rating(
        self: "CastSelf",
    ) -> "_657.ConicalMeshDutyCycleRating":
        from mastapy._private.gears.rating.conical import _657

        return self.__parent__._cast(_657.ConicalMeshDutyCycleRating)

    @property
    def concept_gear_mesh_duty_cycle_rating(
        self: "CastSelf",
    ) -> "_662.ConceptGearMeshDutyCycleRating":
        from mastapy._private.gears.rating.concept import _662

        return self.__parent__._cast(_662.ConceptGearMeshDutyCycleRating)

    @property
    def concept_gear_mesh_rating(self: "CastSelf") -> "_663.ConceptGearMeshRating":
        from mastapy._private.gears.rating.concept import _663

        return self.__parent__._cast(_663.ConceptGearMeshRating)

    @property
    def bevel_gear_mesh_rating(self: "CastSelf") -> "_667.BevelGearMeshRating":
        from mastapy._private.gears.rating.bevel import _667

        return self.__parent__._cast(_667.BevelGearMeshRating)

    @property
    def agma_gleason_conical_gear_mesh_rating(
        self: "CastSelf",
    ) -> "_678.AGMAGleasonConicalGearMeshRating":
        from mastapy._private.gears.rating.agma_gleason_conical import _678

        return self.__parent__._cast(_678.AGMAGleasonConicalGearMeshRating)

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
    def gear_mesh_design_analysis(self: "CastSelf") -> "_1368.GearMeshDesignAnalysis":
        from mastapy._private.gears.analysis import _1368

        return self.__parent__._cast(_1368.GearMeshDesignAnalysis)

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
    def abstract_gear_mesh_analysis(self: "CastSelf") -> "AbstractGearMeshAnalysis":
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
class AbstractGearMeshAnalysis(_0.APIBase):
    """AbstractGearMeshAnalysis

    This is a mastapy class.
    """

    TYPE: ClassVar["Type"] = _ABSTRACT_GEAR_MESH_ANALYSIS

    wrapped: "Any"

    def __post_init__(self: "Self") -> None:
        """Override of the post initialisation magic method."""
        if not hasattr(self.wrapped, "reference_count"):
            self.wrapped.reference_count = 0

        self.wrapped.reference_count += 1

    @property
    @exception_bridge
    def mesh_name(self: "Self") -> "str":
        """str

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "MeshName")

        if temp is None:
            return ""

        return temp

    @property
    @exception_bridge
    def name(self: "Self") -> "str":
        """str

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "Name")

        if temp is None:
            return ""

        return temp

    @property
    @exception_bridge
    def gear_a(self: "Self") -> "_1361.AbstractGearAnalysis":
        """mastapy.gears.analysis.AbstractGearAnalysis

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
    def gear_b(self: "Self") -> "_1361.AbstractGearAnalysis":
        """mastapy.gears.analysis.AbstractGearAnalysis

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
    def gear_set(self: "Self") -> "_1363.AbstractGearSetAnalysis":
        """mastapy.gears.analysis.AbstractGearSetAnalysis

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
    def report_names(self: "Self") -> "List[str]":
        """List[str]

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "ReportNames")

        if temp is None:
            return None

        value = conversion.pn_to_mp_objects_in_list(temp, str)

        if value is None:
            return None

        return value

    @exception_bridge
    @enforce_parameter_types
    def output_default_report_to(self: "Self", file_path: "PathLike") -> None:
        """Method does not return.

        Args:
            file_path (PathLike)
        """
        file_path = str(file_path)
        pythonnet_method_call(self.wrapped, "OutputDefaultReportTo", file_path)

    @exception_bridge
    def get_default_report_with_encoded_images(self: "Self") -> "str":
        """str"""
        method_result = pythonnet_method_call(
            self.wrapped, "GetDefaultReportWithEncodedImages"
        )
        return method_result

    @exception_bridge
    @enforce_parameter_types
    def output_active_report_to(self: "Self", file_path: "PathLike") -> None:
        """Method does not return.

        Args:
            file_path (PathLike)
        """
        file_path = str(file_path)
        pythonnet_method_call(self.wrapped, "OutputActiveReportTo", file_path)

    @exception_bridge
    @enforce_parameter_types
    def output_active_report_as_text_to(self: "Self", file_path: "PathLike") -> None:
        """Method does not return.

        Args:
            file_path (PathLike)
        """
        file_path = str(file_path)
        pythonnet_method_call(self.wrapped, "OutputActiveReportAsTextTo", file_path)

    @exception_bridge
    def get_active_report_with_encoded_images(self: "Self") -> "str":
        """str"""
        method_result = pythonnet_method_call(
            self.wrapped, "GetActiveReportWithEncodedImages"
        )
        return method_result

    @exception_bridge
    @enforce_parameter_types
    def output_named_report_to(
        self: "Self", report_name: "str", file_path: "PathLike"
    ) -> None:
        """Method does not return.

        Args:
            report_name (str)
            file_path (PathLike)
        """
        report_name = str(report_name)
        file_path = str(file_path)
        pythonnet_method_call(
            self.wrapped,
            "OutputNamedReportTo",
            report_name if report_name else "",
            file_path,
        )

    @exception_bridge
    @enforce_parameter_types
    def output_named_report_as_masta_report(
        self: "Self", report_name: "str", file_path: "PathLike"
    ) -> None:
        """Method does not return.

        Args:
            report_name (str)
            file_path (PathLike)
        """
        report_name = str(report_name)
        file_path = str(file_path)
        pythonnet_method_call(
            self.wrapped,
            "OutputNamedReportAsMastaReport",
            report_name if report_name else "",
            file_path,
        )

    @exception_bridge
    @enforce_parameter_types
    def output_named_report_as_text_to(
        self: "Self", report_name: "str", file_path: "PathLike"
    ) -> None:
        """Method does not return.

        Args:
            report_name (str)
            file_path (PathLike)
        """
        report_name = str(report_name)
        file_path = str(file_path)
        pythonnet_method_call(
            self.wrapped,
            "OutputNamedReportAsTextTo",
            report_name if report_name else "",
            file_path,
        )

    @exception_bridge
    @enforce_parameter_types
    def get_named_report_with_encoded_images(self: "Self", report_name: "str") -> "str":
        """str

        Args:
            report_name (str)
        """
        report_name = str(report_name)
        method_result = pythonnet_method_call(
            self.wrapped,
            "GetNamedReportWithEncodedImages",
            report_name if report_name else "",
        )
        return method_result

    @property
    def cast_to(self: "Self") -> "_Cast_AbstractGearMeshAnalysis":
        """Cast to another type.

        Returns:
            _Cast_AbstractGearMeshAnalysis
        """
        return _Cast_AbstractGearMeshAnalysis(self)
