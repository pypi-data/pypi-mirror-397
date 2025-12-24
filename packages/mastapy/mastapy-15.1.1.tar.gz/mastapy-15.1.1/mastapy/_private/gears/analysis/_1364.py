"""GearDesignAnalysis"""

from __future__ import annotations

from typing import TYPE_CHECKING, ClassVar

from mastapy._private._internal.dataclasses import extended_dataclass
from mastapy._private._internal.exceptions import CastException
from mastapy._private._internal.python_net import python_net_import

from mastapy._private._internal import utility
from mastapy._private.gears.analysis import _1361

_GEAR_DESIGN_ANALYSIS = python_net_import(
    "SMT.MastaAPI.Gears.Analysis", "GearDesignAnalysis"
)

if TYPE_CHECKING:
    from typing import Any, Type, TypeVar

    from mastapy._private.gears.analysis import _1365, _1366, _1367
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

    Self = TypeVar("Self", bound="GearDesignAnalysis")
    CastSelf = TypeVar("CastSelf", bound="GearDesignAnalysis._Cast_GearDesignAnalysis")


__docformat__ = "restructuredtext en"
__all__ = ("GearDesignAnalysis",)


@extended_dataclass(frozen=True, slots=True, weakref_slot=True)
class _Cast_GearDesignAnalysis:
    """Special nested class for casting GearDesignAnalysis to subclasses."""

    __parent__: "GearDesignAnalysis"

    @property
    def abstract_gear_analysis(self: "CastSelf") -> "_1361.AbstractGearAnalysis":
        return self.__parent__._cast(_1361.AbstractGearAnalysis)

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
    def gear_design_analysis(self: "CastSelf") -> "GearDesignAnalysis":
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
class GearDesignAnalysis(_1361.AbstractGearAnalysis):
    """GearDesignAnalysis

    This is a mastapy class.
    """

    TYPE: ClassVar["Type"] = _GEAR_DESIGN_ANALYSIS

    wrapped: "Any"

    def __post_init__(self: "Self") -> None:
        """Override of the post initialisation magic method."""
        if not hasattr(self.wrapped, "reference_count"):
            self.wrapped.reference_count = 0

        self.wrapped.reference_count += 1

    @property
    def cast_to(self: "Self") -> "_Cast_GearDesignAnalysis":
        """Cast to another type.

        Returns:
            _Cast_GearDesignAnalysis
        """
        return _Cast_GearDesignAnalysis(self)
