"""AbstractGearSetAnalysis"""

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

_ABSTRACT_GEAR_SET_ANALYSIS = python_net_import(
    "SMT.MastaAPI.Gears.Analysis", "AbstractGearSetAnalysis"
)

if TYPE_CHECKING:
    from typing import Any, List, Type, TypeVar

    from mastapy._private._internal.typing import PathLike

    from mastapy._private.gears.analysis import _1372, _1374, _1375, _1376, _1377
    from mastapy._private.gears.fe_model import _1346
    from mastapy._private.gears.fe_model.conical import _1352
    from mastapy._private.gears.fe_model.cylindrical import _1349
    from mastapy._private.gears.gear_designs.cylindrical.micro_geometry import (
        _1243,
        _1244,
    )
    from mastapy._private.gears.gear_designs.face import _1122
    from mastapy._private.gears.gear_two_d_fe_analysis import _1021, _1022
    from mastapy._private.gears.load_case import _999
    from mastapy._private.gears.load_case.bevel import _1018
    from mastapy._private.gears.load_case.concept import _1014
    from mastapy._private.gears.load_case.conical import _1011
    from mastapy._private.gears.load_case.cylindrical import _1008
    from mastapy._private.gears.load_case.face import _1005
    from mastapy._private.gears.load_case.worm import _1002
    from mastapy._private.gears.ltca import _972
    from mastapy._private.gears.ltca.conical import _993
    from mastapy._private.gears.ltca.cylindrical import _985, _987
    from mastapy._private.gears.manufacturing.bevel import _916, _917, _918, _919
    from mastapy._private.gears.manufacturing.cylindrical import _746, _747, _751
    from mastapy._private.gears.rating import _467, _475, _476
    from mastapy._private.gears.rating.agma_gleason_conical import _680
    from mastapy._private.gears.rating.bevel import _669
    from mastapy._private.gears.rating.concept import _665, _666
    from mastapy._private.gears.rating.conical import _654, _655
    from mastapy._private.gears.rating.cylindrical import _576, _577, _593
    from mastapy._private.gears.rating.face import _562, _563
    from mastapy._private.gears.rating.hypoid import _553
    from mastapy._private.gears.rating.klingelnberg_conical import _526
    from mastapy._private.gears.rating.klingelnberg_hypoid import _523
    from mastapy._private.gears.rating.klingelnberg_spiral_bevel import _520
    from mastapy._private.gears.rating.spiral_bevel import _517
    from mastapy._private.gears.rating.straight_bevel import _510
    from mastapy._private.gears.rating.straight_bevel_diff import _513
    from mastapy._private.gears.rating.worm import _488, _489
    from mastapy._private.gears.rating.zerol_bevel import _484
    from mastapy._private.utility.model_validation import _2020, _2021

    Self = TypeVar("Self", bound="AbstractGearSetAnalysis")
    CastSelf = TypeVar(
        "CastSelf", bound="AbstractGearSetAnalysis._Cast_AbstractGearSetAnalysis"
    )


__docformat__ = "restructuredtext en"
__all__ = ("AbstractGearSetAnalysis",)


@extended_dataclass(frozen=True, slots=True, weakref_slot=True)
class _Cast_AbstractGearSetAnalysis:
    """Special nested class for casting AbstractGearSetAnalysis to subclasses."""

    __parent__: "AbstractGearSetAnalysis"

    @property
    def abstract_gear_set_rating(self: "CastSelf") -> "_467.AbstractGearSetRating":
        from mastapy._private.gears.rating import _467

        return self.__parent__._cast(_467.AbstractGearSetRating)

    @property
    def gear_set_duty_cycle_rating(self: "CastSelf") -> "_475.GearSetDutyCycleRating":
        from mastapy._private.gears.rating import _475

        return self.__parent__._cast(_475.GearSetDutyCycleRating)

    @property
    def gear_set_rating(self: "CastSelf") -> "_476.GearSetRating":
        from mastapy._private.gears.rating import _476

        return self.__parent__._cast(_476.GearSetRating)

    @property
    def zerol_bevel_gear_set_rating(self: "CastSelf") -> "_484.ZerolBevelGearSetRating":
        from mastapy._private.gears.rating.zerol_bevel import _484

        return self.__parent__._cast(_484.ZerolBevelGearSetRating)

    @property
    def worm_gear_set_duty_cycle_rating(
        self: "CastSelf",
    ) -> "_488.WormGearSetDutyCycleRating":
        from mastapy._private.gears.rating.worm import _488

        return self.__parent__._cast(_488.WormGearSetDutyCycleRating)

    @property
    def worm_gear_set_rating(self: "CastSelf") -> "_489.WormGearSetRating":
        from mastapy._private.gears.rating.worm import _489

        return self.__parent__._cast(_489.WormGearSetRating)

    @property
    def straight_bevel_gear_set_rating(
        self: "CastSelf",
    ) -> "_510.StraightBevelGearSetRating":
        from mastapy._private.gears.rating.straight_bevel import _510

        return self.__parent__._cast(_510.StraightBevelGearSetRating)

    @property
    def straight_bevel_diff_gear_set_rating(
        self: "CastSelf",
    ) -> "_513.StraightBevelDiffGearSetRating":
        from mastapy._private.gears.rating.straight_bevel_diff import _513

        return self.__parent__._cast(_513.StraightBevelDiffGearSetRating)

    @property
    def spiral_bevel_gear_set_rating(
        self: "CastSelf",
    ) -> "_517.SpiralBevelGearSetRating":
        from mastapy._private.gears.rating.spiral_bevel import _517

        return self.__parent__._cast(_517.SpiralBevelGearSetRating)

    @property
    def klingelnberg_cyclo_palloid_spiral_bevel_gear_set_rating(
        self: "CastSelf",
    ) -> "_520.KlingelnbergCycloPalloidSpiralBevelGearSetRating":
        from mastapy._private.gears.rating.klingelnberg_spiral_bevel import _520

        return self.__parent__._cast(
            _520.KlingelnbergCycloPalloidSpiralBevelGearSetRating
        )

    @property
    def klingelnberg_cyclo_palloid_hypoid_gear_set_rating(
        self: "CastSelf",
    ) -> "_523.KlingelnbergCycloPalloidHypoidGearSetRating":
        from mastapy._private.gears.rating.klingelnberg_hypoid import _523

        return self.__parent__._cast(_523.KlingelnbergCycloPalloidHypoidGearSetRating)

    @property
    def klingelnberg_cyclo_palloid_conical_gear_set_rating(
        self: "CastSelf",
    ) -> "_526.KlingelnbergCycloPalloidConicalGearSetRating":
        from mastapy._private.gears.rating.klingelnberg_conical import _526

        return self.__parent__._cast(_526.KlingelnbergCycloPalloidConicalGearSetRating)

    @property
    def hypoid_gear_set_rating(self: "CastSelf") -> "_553.HypoidGearSetRating":
        from mastapy._private.gears.rating.hypoid import _553

        return self.__parent__._cast(_553.HypoidGearSetRating)

    @property
    def face_gear_set_duty_cycle_rating(
        self: "CastSelf",
    ) -> "_562.FaceGearSetDutyCycleRating":
        from mastapy._private.gears.rating.face import _562

        return self.__parent__._cast(_562.FaceGearSetDutyCycleRating)

    @property
    def face_gear_set_rating(self: "CastSelf") -> "_563.FaceGearSetRating":
        from mastapy._private.gears.rating.face import _563

        return self.__parent__._cast(_563.FaceGearSetRating)

    @property
    def cylindrical_gear_set_duty_cycle_rating(
        self: "CastSelf",
    ) -> "_576.CylindricalGearSetDutyCycleRating":
        from mastapy._private.gears.rating.cylindrical import _576

        return self.__parent__._cast(_576.CylindricalGearSetDutyCycleRating)

    @property
    def cylindrical_gear_set_rating(
        self: "CastSelf",
    ) -> "_577.CylindricalGearSetRating":
        from mastapy._private.gears.rating.cylindrical import _577

        return self.__parent__._cast(_577.CylindricalGearSetRating)

    @property
    def reduced_cylindrical_gear_set_duty_cycle_rating(
        self: "CastSelf",
    ) -> "_593.ReducedCylindricalGearSetDutyCycleRating":
        from mastapy._private.gears.rating.cylindrical import _593

        return self.__parent__._cast(_593.ReducedCylindricalGearSetDutyCycleRating)

    @property
    def conical_gear_set_duty_cycle_rating(
        self: "CastSelf",
    ) -> "_654.ConicalGearSetDutyCycleRating":
        from mastapy._private.gears.rating.conical import _654

        return self.__parent__._cast(_654.ConicalGearSetDutyCycleRating)

    @property
    def conical_gear_set_rating(self: "CastSelf") -> "_655.ConicalGearSetRating":
        from mastapy._private.gears.rating.conical import _655

        return self.__parent__._cast(_655.ConicalGearSetRating)

    @property
    def concept_gear_set_duty_cycle_rating(
        self: "CastSelf",
    ) -> "_665.ConceptGearSetDutyCycleRating":
        from mastapy._private.gears.rating.concept import _665

        return self.__parent__._cast(_665.ConceptGearSetDutyCycleRating)

    @property
    def concept_gear_set_rating(self: "CastSelf") -> "_666.ConceptGearSetRating":
        from mastapy._private.gears.rating.concept import _666

        return self.__parent__._cast(_666.ConceptGearSetRating)

    @property
    def bevel_gear_set_rating(self: "CastSelf") -> "_669.BevelGearSetRating":
        from mastapy._private.gears.rating.bevel import _669

        return self.__parent__._cast(_669.BevelGearSetRating)

    @property
    def agma_gleason_conical_gear_set_rating(
        self: "CastSelf",
    ) -> "_680.AGMAGleasonConicalGearSetRating":
        from mastapy._private.gears.rating.agma_gleason_conical import _680

        return self.__parent__._cast(_680.AGMAGleasonConicalGearSetRating)

    @property
    def cylindrical_manufactured_gear_set_duty_cycle(
        self: "CastSelf",
    ) -> "_746.CylindricalManufacturedGearSetDutyCycle":
        from mastapy._private.gears.manufacturing.cylindrical import _746

        return self.__parent__._cast(_746.CylindricalManufacturedGearSetDutyCycle)

    @property
    def cylindrical_manufactured_gear_set_load_case(
        self: "CastSelf",
    ) -> "_747.CylindricalManufacturedGearSetLoadCase":
        from mastapy._private.gears.manufacturing.cylindrical import _747

        return self.__parent__._cast(_747.CylindricalManufacturedGearSetLoadCase)

    @property
    def cylindrical_set_manufacturing_config(
        self: "CastSelf",
    ) -> "_751.CylindricalSetManufacturingConfig":
        from mastapy._private.gears.manufacturing.cylindrical import _751

        return self.__parent__._cast(_751.CylindricalSetManufacturingConfig)

    @property
    def conical_set_manufacturing_analysis(
        self: "CastSelf",
    ) -> "_916.ConicalSetManufacturingAnalysis":
        from mastapy._private.gears.manufacturing.bevel import _916

        return self.__parent__._cast(_916.ConicalSetManufacturingAnalysis)

    @property
    def conical_set_manufacturing_config(
        self: "CastSelf",
    ) -> "_917.ConicalSetManufacturingConfig":
        from mastapy._private.gears.manufacturing.bevel import _917

        return self.__parent__._cast(_917.ConicalSetManufacturingConfig)

    @property
    def conical_set_micro_geometry_config(
        self: "CastSelf",
    ) -> "_918.ConicalSetMicroGeometryConfig":
        from mastapy._private.gears.manufacturing.bevel import _918

        return self.__parent__._cast(_918.ConicalSetMicroGeometryConfig)

    @property
    def conical_set_micro_geometry_config_base(
        self: "CastSelf",
    ) -> "_919.ConicalSetMicroGeometryConfigBase":
        from mastapy._private.gears.manufacturing.bevel import _919

        return self.__parent__._cast(_919.ConicalSetMicroGeometryConfigBase)

    @property
    def gear_set_load_distribution_analysis(
        self: "CastSelf",
    ) -> "_972.GearSetLoadDistributionAnalysis":
        from mastapy._private.gears.ltca import _972

        return self.__parent__._cast(_972.GearSetLoadDistributionAnalysis)

    @property
    def cylindrical_gear_set_load_distribution_analysis(
        self: "CastSelf",
    ) -> "_985.CylindricalGearSetLoadDistributionAnalysis":
        from mastapy._private.gears.ltca.cylindrical import _985

        return self.__parent__._cast(_985.CylindricalGearSetLoadDistributionAnalysis)

    @property
    def face_gear_set_load_distribution_analysis(
        self: "CastSelf",
    ) -> "_987.FaceGearSetLoadDistributionAnalysis":
        from mastapy._private.gears.ltca.cylindrical import _987

        return self.__parent__._cast(_987.FaceGearSetLoadDistributionAnalysis)

    @property
    def conical_gear_set_load_distribution_analysis(
        self: "CastSelf",
    ) -> "_993.ConicalGearSetLoadDistributionAnalysis":
        from mastapy._private.gears.ltca.conical import _993

        return self.__parent__._cast(_993.ConicalGearSetLoadDistributionAnalysis)

    @property
    def gear_set_load_case_base(self: "CastSelf") -> "_999.GearSetLoadCaseBase":
        from mastapy._private.gears.load_case import _999

        return self.__parent__._cast(_999.GearSetLoadCaseBase)

    @property
    def worm_gear_set_load_case(self: "CastSelf") -> "_1002.WormGearSetLoadCase":
        from mastapy._private.gears.load_case.worm import _1002

        return self.__parent__._cast(_1002.WormGearSetLoadCase)

    @property
    def face_gear_set_load_case(self: "CastSelf") -> "_1005.FaceGearSetLoadCase":
        from mastapy._private.gears.load_case.face import _1005

        return self.__parent__._cast(_1005.FaceGearSetLoadCase)

    @property
    def cylindrical_gear_set_load_case(
        self: "CastSelf",
    ) -> "_1008.CylindricalGearSetLoadCase":
        from mastapy._private.gears.load_case.cylindrical import _1008

        return self.__parent__._cast(_1008.CylindricalGearSetLoadCase)

    @property
    def conical_gear_set_load_case(self: "CastSelf") -> "_1011.ConicalGearSetLoadCase":
        from mastapy._private.gears.load_case.conical import _1011

        return self.__parent__._cast(_1011.ConicalGearSetLoadCase)

    @property
    def concept_gear_set_load_case(self: "CastSelf") -> "_1014.ConceptGearSetLoadCase":
        from mastapy._private.gears.load_case.concept import _1014

        return self.__parent__._cast(_1014.ConceptGearSetLoadCase)

    @property
    def bevel_set_load_case(self: "CastSelf") -> "_1018.BevelSetLoadCase":
        from mastapy._private.gears.load_case.bevel import _1018

        return self.__parent__._cast(_1018.BevelSetLoadCase)

    @property
    def cylindrical_gear_set_tiff_analysis(
        self: "CastSelf",
    ) -> "_1021.CylindricalGearSetTIFFAnalysis":
        from mastapy._private.gears.gear_two_d_fe_analysis import _1021

        return self.__parent__._cast(_1021.CylindricalGearSetTIFFAnalysis)

    @property
    def cylindrical_gear_set_tiff_analysis_duty_cycle(
        self: "CastSelf",
    ) -> "_1022.CylindricalGearSetTIFFAnalysisDutyCycle":
        from mastapy._private.gears.gear_two_d_fe_analysis import _1022

        return self.__parent__._cast(_1022.CylindricalGearSetTIFFAnalysisDutyCycle)

    @property
    def face_gear_set_micro_geometry(
        self: "CastSelf",
    ) -> "_1122.FaceGearSetMicroGeometry":
        from mastapy._private.gears.gear_designs.face import _1122

        return self.__parent__._cast(_1122.FaceGearSetMicroGeometry)

    @property
    def cylindrical_gear_set_micro_geometry(
        self: "CastSelf",
    ) -> "_1243.CylindricalGearSetMicroGeometry":
        from mastapy._private.gears.gear_designs.cylindrical.micro_geometry import _1243

        return self.__parent__._cast(_1243.CylindricalGearSetMicroGeometry)

    @property
    def cylindrical_gear_set_micro_geometry_duty_cycle(
        self: "CastSelf",
    ) -> "_1244.CylindricalGearSetMicroGeometryDutyCycle":
        from mastapy._private.gears.gear_designs.cylindrical.micro_geometry import _1244

        return self.__parent__._cast(_1244.CylindricalGearSetMicroGeometryDutyCycle)

    @property
    def gear_set_fe_model(self: "CastSelf") -> "_1346.GearSetFEModel":
        from mastapy._private.gears.fe_model import _1346

        return self.__parent__._cast(_1346.GearSetFEModel)

    @property
    def cylindrical_gear_set_fe_model(
        self: "CastSelf",
    ) -> "_1349.CylindricalGearSetFEModel":
        from mastapy._private.gears.fe_model.cylindrical import _1349

        return self.__parent__._cast(_1349.CylindricalGearSetFEModel)

    @property
    def conical_set_fe_model(self: "CastSelf") -> "_1352.ConicalSetFEModel":
        from mastapy._private.gears.fe_model.conical import _1352

        return self.__parent__._cast(_1352.ConicalSetFEModel)

    @property
    def gear_set_design_analysis(self: "CastSelf") -> "_1372.GearSetDesignAnalysis":
        from mastapy._private.gears.analysis import _1372

        return self.__parent__._cast(_1372.GearSetDesignAnalysis)

    @property
    def gear_set_implementation_analysis(
        self: "CastSelf",
    ) -> "_1374.GearSetImplementationAnalysis":
        from mastapy._private.gears.analysis import _1374

        return self.__parent__._cast(_1374.GearSetImplementationAnalysis)

    @property
    def gear_set_implementation_analysis_abstract(
        self: "CastSelf",
    ) -> "_1375.GearSetImplementationAnalysisAbstract":
        from mastapy._private.gears.analysis import _1375

        return self.__parent__._cast(_1375.GearSetImplementationAnalysisAbstract)

    @property
    def gear_set_implementation_analysis_duty_cycle(
        self: "CastSelf",
    ) -> "_1376.GearSetImplementationAnalysisDutyCycle":
        from mastapy._private.gears.analysis import _1376

        return self.__parent__._cast(_1376.GearSetImplementationAnalysisDutyCycle)

    @property
    def gear_set_implementation_detail(
        self: "CastSelf",
    ) -> "_1377.GearSetImplementationDetail":
        from mastapy._private.gears.analysis import _1377

        return self.__parent__._cast(_1377.GearSetImplementationDetail)

    @property
    def abstract_gear_set_analysis(self: "CastSelf") -> "AbstractGearSetAnalysis":
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
class AbstractGearSetAnalysis(_0.APIBase):
    """AbstractGearSetAnalysis

    This is a mastapy class.
    """

    TYPE: ClassVar["Type"] = _ABSTRACT_GEAR_SET_ANALYSIS

    wrapped: "Any"

    def __post_init__(self: "Self") -> None:
        """Override of the post initialisation magic method."""
        if not hasattr(self.wrapped, "reference_count"):
            self.wrapped.reference_count = 0

        self.wrapped.reference_count += 1

    @property
    @exception_bridge
    def name(self: "Self") -> "str":
        """str"""
        temp = pythonnet_property_get(self.wrapped, "Name")

        if temp is None:
            return ""

        return temp

    @name.setter
    @exception_bridge
    @enforce_parameter_types
    def name(self: "Self", value: "str") -> None:
        pythonnet_property_set(
            self.wrapped, "Name", str(value) if value is not None else ""
        )

    @property
    @exception_bridge
    def all_status_errors(self: "Self") -> "List[_2021.StatusItem]":
        """List[mastapy.utility.model_validation.StatusItem]

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "AllStatusErrors")

        if temp is None:
            return None

        value = conversion.pn_to_mp_objects_in_list(temp)

        if value is None:
            return None

        return value

    @property
    @exception_bridge
    def status(self: "Self") -> "_2020.Status":
        """mastapy.utility.model_validation.Status

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "Status")

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
    def cast_to(self: "Self") -> "_Cast_AbstractGearSetAnalysis":
        """Cast to another type.

        Returns:
            _Cast_AbstractGearSetAnalysis
        """
        return _Cast_AbstractGearSetAnalysis(self)
