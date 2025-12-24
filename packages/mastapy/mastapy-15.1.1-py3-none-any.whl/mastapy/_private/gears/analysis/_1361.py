"""AbstractGearAnalysis"""

from __future__ import annotations

from typing import TYPE_CHECKING, ClassVar

from mastapy._private._internal.dataclasses import extended_dataclass
from mastapy._private._internal.exception_bridge import exception_bridge
from mastapy._private._internal.exceptions import CastException
from mastapy._private._internal.python_net import (
    python_net_import,
    pythonnet_method_call,
    pythonnet_property_get,
    pythonnet_property_set,
)
from mastapy._private._internal.type_enforcement import enforce_parameter_types

from mastapy._private import _0
from mastapy._private._internal import constructor, conversion, utility

_ABSTRACT_GEAR_ANALYSIS = python_net_import(
    "SMT.MastaAPI.Gears.Analysis", "AbstractGearAnalysis"
)

if TYPE_CHECKING:
    from typing import Any, List, Type, TypeVar

    from mastapy._private._internal.typing import PathLike

    from mastapy._private.gears.analysis import _1362, _1363, _1364, _1365, _1366, _1367
    from mastapy._private.gears.fe_model import _1343
    from mastapy._private.gears.fe_model.conical import _1350
    from mastapy._private.gears.fe_model.cylindrical import _1347
    from mastapy._private.gears.gear_designs.cylindrical.micro_geometry import (
        _1236,
        _1237,
        _1238,
        _1240,
    )
    from mastapy._private.gears.gear_designs.face import _1119
    from mastapy._private.gears.gear_two_d_fe_analysis import _1023, _1024
    from mastapy._private.gears.load_case import _998
    from mastapy._private.gears.load_case.bevel import _1016
    from mastapy._private.gears.load_case.concept import _1013
    from mastapy._private.gears.load_case.conical import _1010
    from mastapy._private.gears.load_case.cylindrical import _1007
    from mastapy._private.gears.load_case.face import _1004
    from mastapy._private.gears.load_case.worm import _1001
    from mastapy._private.gears.ltca import _966
    from mastapy._private.gears.ltca.conical import _992
    from mastapy._private.gears.ltca.cylindrical import _981
    from mastapy._private.gears.manufacturing.bevel import (
        _901,
        _902,
        _903,
        _904,
        _914,
        _915,
        _920,
    )
    from mastapy._private.gears.manufacturing.cylindrical import _738, _742, _743
    from mastapy._private.gears.rating import _466, _470, _474
    from mastapy._private.gears.rating.agma_gleason_conical import _679
    from mastapy._private.gears.rating.bevel import _668
    from mastapy._private.gears.rating.concept import _661, _664
    from mastapy._private.gears.rating.conical import _651, _653
    from mastapy._private.gears.rating.cylindrical import _568, _573
    from mastapy._private.gears.rating.face import _558, _561
    from mastapy._private.gears.rating.hypoid import _552
    from mastapy._private.gears.rating.klingelnberg_conical import _525
    from mastapy._private.gears.rating.klingelnberg_hypoid import _522
    from mastapy._private.gears.rating.klingelnberg_spiral_bevel import _519
    from mastapy._private.gears.rating.spiral_bevel import _516
    from mastapy._private.gears.rating.straight_bevel import _509
    from mastapy._private.gears.rating.straight_bevel_diff import _512
    from mastapy._private.gears.rating.worm import _485, _487
    from mastapy._private.gears.rating.zerol_bevel import _483

    Self = TypeVar("Self", bound="AbstractGearAnalysis")
    CastSelf = TypeVar(
        "CastSelf", bound="AbstractGearAnalysis._Cast_AbstractGearAnalysis"
    )


__docformat__ = "restructuredtext en"
__all__ = ("AbstractGearAnalysis",)


@extended_dataclass(frozen=True, slots=True, weakref_slot=True)
class _Cast_AbstractGearAnalysis:
    """Special nested class for casting AbstractGearAnalysis to subclasses."""

    __parent__: "AbstractGearAnalysis"

    @property
    def abstract_gear_rating(self: "CastSelf") -> "_466.AbstractGearRating":
        from mastapy._private.gears.rating import _466

        return self.__parent__._cast(_466.AbstractGearRating)

    @property
    def gear_duty_cycle_rating(self: "CastSelf") -> "_470.GearDutyCycleRating":
        from mastapy._private.gears.rating import _470

        return self.__parent__._cast(_470.GearDutyCycleRating)

    @property
    def gear_rating(self: "CastSelf") -> "_474.GearRating":
        from mastapy._private.gears.rating import _474

        return self.__parent__._cast(_474.GearRating)

    @property
    def zerol_bevel_gear_rating(self: "CastSelf") -> "_483.ZerolBevelGearRating":
        from mastapy._private.gears.rating.zerol_bevel import _483

        return self.__parent__._cast(_483.ZerolBevelGearRating)

    @property
    def worm_gear_duty_cycle_rating(self: "CastSelf") -> "_485.WormGearDutyCycleRating":
        from mastapy._private.gears.rating.worm import _485

        return self.__parent__._cast(_485.WormGearDutyCycleRating)

    @property
    def worm_gear_rating(self: "CastSelf") -> "_487.WormGearRating":
        from mastapy._private.gears.rating.worm import _487

        return self.__parent__._cast(_487.WormGearRating)

    @property
    def straight_bevel_gear_rating(self: "CastSelf") -> "_509.StraightBevelGearRating":
        from mastapy._private.gears.rating.straight_bevel import _509

        return self.__parent__._cast(_509.StraightBevelGearRating)

    @property
    def straight_bevel_diff_gear_rating(
        self: "CastSelf",
    ) -> "_512.StraightBevelDiffGearRating":
        from mastapy._private.gears.rating.straight_bevel_diff import _512

        return self.__parent__._cast(_512.StraightBevelDiffGearRating)

    @property
    def spiral_bevel_gear_rating(self: "CastSelf") -> "_516.SpiralBevelGearRating":
        from mastapy._private.gears.rating.spiral_bevel import _516

        return self.__parent__._cast(_516.SpiralBevelGearRating)

    @property
    def klingelnberg_cyclo_palloid_spiral_bevel_gear_rating(
        self: "CastSelf",
    ) -> "_519.KlingelnbergCycloPalloidSpiralBevelGearRating":
        from mastapy._private.gears.rating.klingelnberg_spiral_bevel import _519

        return self.__parent__._cast(_519.KlingelnbergCycloPalloidSpiralBevelGearRating)

    @property
    def klingelnberg_cyclo_palloid_hypoid_gear_rating(
        self: "CastSelf",
    ) -> "_522.KlingelnbergCycloPalloidHypoidGearRating":
        from mastapy._private.gears.rating.klingelnberg_hypoid import _522

        return self.__parent__._cast(_522.KlingelnbergCycloPalloidHypoidGearRating)

    @property
    def klingelnberg_cyclo_palloid_conical_gear_rating(
        self: "CastSelf",
    ) -> "_525.KlingelnbergCycloPalloidConicalGearRating":
        from mastapy._private.gears.rating.klingelnberg_conical import _525

        return self.__parent__._cast(_525.KlingelnbergCycloPalloidConicalGearRating)

    @property
    def hypoid_gear_rating(self: "CastSelf") -> "_552.HypoidGearRating":
        from mastapy._private.gears.rating.hypoid import _552

        return self.__parent__._cast(_552.HypoidGearRating)

    @property
    def face_gear_duty_cycle_rating(self: "CastSelf") -> "_558.FaceGearDutyCycleRating":
        from mastapy._private.gears.rating.face import _558

        return self.__parent__._cast(_558.FaceGearDutyCycleRating)

    @property
    def face_gear_rating(self: "CastSelf") -> "_561.FaceGearRating":
        from mastapy._private.gears.rating.face import _561

        return self.__parent__._cast(_561.FaceGearRating)

    @property
    def cylindrical_gear_duty_cycle_rating(
        self: "CastSelf",
    ) -> "_568.CylindricalGearDutyCycleRating":
        from mastapy._private.gears.rating.cylindrical import _568

        return self.__parent__._cast(_568.CylindricalGearDutyCycleRating)

    @property
    def cylindrical_gear_rating(self: "CastSelf") -> "_573.CylindricalGearRating":
        from mastapy._private.gears.rating.cylindrical import _573

        return self.__parent__._cast(_573.CylindricalGearRating)

    @property
    def conical_gear_duty_cycle_rating(
        self: "CastSelf",
    ) -> "_651.ConicalGearDutyCycleRating":
        from mastapy._private.gears.rating.conical import _651

        return self.__parent__._cast(_651.ConicalGearDutyCycleRating)

    @property
    def conical_gear_rating(self: "CastSelf") -> "_653.ConicalGearRating":
        from mastapy._private.gears.rating.conical import _653

        return self.__parent__._cast(_653.ConicalGearRating)

    @property
    def concept_gear_duty_cycle_rating(
        self: "CastSelf",
    ) -> "_661.ConceptGearDutyCycleRating":
        from mastapy._private.gears.rating.concept import _661

        return self.__parent__._cast(_661.ConceptGearDutyCycleRating)

    @property
    def concept_gear_rating(self: "CastSelf") -> "_664.ConceptGearRating":
        from mastapy._private.gears.rating.concept import _664

        return self.__parent__._cast(_664.ConceptGearRating)

    @property
    def bevel_gear_rating(self: "CastSelf") -> "_668.BevelGearRating":
        from mastapy._private.gears.rating.bevel import _668

        return self.__parent__._cast(_668.BevelGearRating)

    @property
    def agma_gleason_conical_gear_rating(
        self: "CastSelf",
    ) -> "_679.AGMAGleasonConicalGearRating":
        from mastapy._private.gears.rating.agma_gleason_conical import _679

        return self.__parent__._cast(_679.AGMAGleasonConicalGearRating)

    @property
    def cylindrical_gear_manufacturing_config(
        self: "CastSelf",
    ) -> "_738.CylindricalGearManufacturingConfig":
        from mastapy._private.gears.manufacturing.cylindrical import _738

        return self.__parent__._cast(_738.CylindricalGearManufacturingConfig)

    @property
    def cylindrical_manufactured_gear_duty_cycle(
        self: "CastSelf",
    ) -> "_742.CylindricalManufacturedGearDutyCycle":
        from mastapy._private.gears.manufacturing.cylindrical import _742

        return self.__parent__._cast(_742.CylindricalManufacturedGearDutyCycle)

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
    def gear_load_case_base(self: "CastSelf") -> "_998.GearLoadCaseBase":
        from mastapy._private.gears.load_case import _998

        return self.__parent__._cast(_998.GearLoadCaseBase)

    @property
    def worm_gear_load_case(self: "CastSelf") -> "_1001.WormGearLoadCase":
        from mastapy._private.gears.load_case.worm import _1001

        return self.__parent__._cast(_1001.WormGearLoadCase)

    @property
    def face_gear_load_case(self: "CastSelf") -> "_1004.FaceGearLoadCase":
        from mastapy._private.gears.load_case.face import _1004

        return self.__parent__._cast(_1004.FaceGearLoadCase)

    @property
    def cylindrical_gear_load_case(self: "CastSelf") -> "_1007.CylindricalGearLoadCase":
        from mastapy._private.gears.load_case.cylindrical import _1007

        return self.__parent__._cast(_1007.CylindricalGearLoadCase)

    @property
    def conical_gear_load_case(self: "CastSelf") -> "_1010.ConicalGearLoadCase":
        from mastapy._private.gears.load_case.conical import _1010

        return self.__parent__._cast(_1010.ConicalGearLoadCase)

    @property
    def concept_gear_load_case(self: "CastSelf") -> "_1013.ConceptGearLoadCase":
        from mastapy._private.gears.load_case.concept import _1013

        return self.__parent__._cast(_1013.ConceptGearLoadCase)

    @property
    def bevel_load_case(self: "CastSelf") -> "_1016.BevelLoadCase":
        from mastapy._private.gears.load_case.bevel import _1016

        return self.__parent__._cast(_1016.BevelLoadCase)

    @property
    def cylindrical_gear_tiff_analysis(
        self: "CastSelf",
    ) -> "_1023.CylindricalGearTIFFAnalysis":
        from mastapy._private.gears.gear_two_d_fe_analysis import _1023

        return self.__parent__._cast(_1023.CylindricalGearTIFFAnalysis)

    @property
    def cylindrical_gear_tiff_analysis_duty_cycle(
        self: "CastSelf",
    ) -> "_1024.CylindricalGearTIFFAnalysisDutyCycle":
        from mastapy._private.gears.gear_two_d_fe_analysis import _1024

        return self.__parent__._cast(_1024.CylindricalGearTIFFAnalysisDutyCycle)

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
    def cylindrical_gear_micro_geometry_duty_cycle(
        self: "CastSelf",
    ) -> "_1238.CylindricalGearMicroGeometryDutyCycle":
        from mastapy._private.gears.gear_designs.cylindrical.micro_geometry import _1238

        return self.__parent__._cast(_1238.CylindricalGearMicroGeometryDutyCycle)

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
    def gear_design_analysis(self: "CastSelf") -> "_1364.GearDesignAnalysis":
        from mastapy._private.gears.analysis import _1364

        return self.__parent__._cast(_1364.GearDesignAnalysis)

    @property
    def gear_implementation_analysis(
        self: "CastSelf",
    ) -> "_1365.GearImplementationAnalysis":
        from mastapy._private.gears.analysis import _1365

        return self.__parent__._cast(_1365.GearImplementationAnalysis)

    @property
    def gear_implementation_analysis_duty_cycle(
        self: "CastSelf",
    ) -> "_1366.GearImplementationAnalysisDutyCycle":
        from mastapy._private.gears.analysis import _1366

        return self.__parent__._cast(_1366.GearImplementationAnalysisDutyCycle)

    @property
    def gear_implementation_detail(
        self: "CastSelf",
    ) -> "_1367.GearImplementationDetail":
        from mastapy._private.gears.analysis import _1367

        return self.__parent__._cast(_1367.GearImplementationDetail)

    @property
    def abstract_gear_analysis(self: "CastSelf") -> "AbstractGearAnalysis":
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
class AbstractGearAnalysis(_0.APIBase):
    """AbstractGearAnalysis

    This is a mastapy class.
    """

    TYPE: ClassVar["Type"] = _ABSTRACT_GEAR_ANALYSIS

    wrapped: "Any"

    def __post_init__(self: "Self") -> None:
        """Override of the post initialisation magic method."""
        if not hasattr(self.wrapped, "reference_count"):
            self.wrapped.reference_count = 0

        self.wrapped.reference_count += 1

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
    def name_with_gear_set_name(self: "Self") -> "str":
        """str

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "NameWithGearSetName")

        if temp is None:
            return ""

        return temp

    @property
    @exception_bridge
    def planet_index(self: "Self") -> "int":
        """int"""
        temp = pythonnet_property_get(self.wrapped, "PlanetIndex")

        if temp is None:
            return 0

        return temp

    @planet_index.setter
    @exception_bridge
    @enforce_parameter_types
    def planet_index(self: "Self", value: "int") -> None:
        pythonnet_property_set(
            self.wrapped, "PlanetIndex", int(value) if value is not None else 0
        )

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
    def meshes(self: "Self") -> "List[_1362.AbstractGearMeshAnalysis]":
        """List[mastapy.gears.analysis.AbstractGearMeshAnalysis]

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "Meshes")

        if temp is None:
            return None

        value = conversion.pn_to_mp_objects_in_list(temp)

        if value is None:
            return None

        return value

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
    def cast_to(self: "Self") -> "_Cast_AbstractGearAnalysis":
        """Cast to another type.

        Returns:
            _Cast_AbstractGearAnalysis
        """
        return _Cast_AbstractGearAnalysis(self)
