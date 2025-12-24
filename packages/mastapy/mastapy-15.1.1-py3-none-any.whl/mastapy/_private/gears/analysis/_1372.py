"""GearSetDesignAnalysis"""

from __future__ import annotations

from typing import TYPE_CHECKING, ClassVar

from mastapy._private._internal.dataclasses import extended_dataclass
from mastapy._private._internal.exceptions import CastException
from mastapy._private._internal.python_net import python_net_import

from mastapy._private._internal import utility
from mastapy._private.gears.analysis import _1363

_GEAR_SET_DESIGN_ANALYSIS = python_net_import(
    "SMT.MastaAPI.Gears.Analysis", "GearSetDesignAnalysis"
)

if TYPE_CHECKING:
    from typing import Any, Type, TypeVar

    from mastapy._private.gears.analysis import _1374, _1375, _1376, _1377
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

    Self = TypeVar("Self", bound="GearSetDesignAnalysis")
    CastSelf = TypeVar(
        "CastSelf", bound="GearSetDesignAnalysis._Cast_GearSetDesignAnalysis"
    )


__docformat__ = "restructuredtext en"
__all__ = ("GearSetDesignAnalysis",)


@extended_dataclass(frozen=True, slots=True, weakref_slot=True)
class _Cast_GearSetDesignAnalysis:
    """Special nested class for casting GearSetDesignAnalysis to subclasses."""

    __parent__: "GearSetDesignAnalysis"

    @property
    def abstract_gear_set_analysis(self: "CastSelf") -> "_1363.AbstractGearSetAnalysis":
        return self.__parent__._cast(_1363.AbstractGearSetAnalysis)

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
    def gear_set_design_analysis(self: "CastSelf") -> "GearSetDesignAnalysis":
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
class GearSetDesignAnalysis(_1363.AbstractGearSetAnalysis):
    """GearSetDesignAnalysis

    This is a mastapy class.
    """

    TYPE: ClassVar["Type"] = _GEAR_SET_DESIGN_ANALYSIS

    wrapped: "Any"

    def __post_init__(self: "Self") -> None:
        """Override of the post initialisation magic method."""
        if not hasattr(self.wrapped, "reference_count"):
            self.wrapped.reference_count = 0

        self.wrapped.reference_count += 1

    @property
    def cast_to(self: "Self") -> "_Cast_GearSetDesignAnalysis":
        """Cast to another type.

        Returns:
            _Cast_GearSetDesignAnalysis
        """
        return _Cast_GearSetDesignAnalysis(self)
