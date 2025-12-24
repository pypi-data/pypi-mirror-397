"""GearSingleFlankRating"""

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
from mastapy._private._internal import conversion, utility

_GEAR_SINGLE_FLANK_RATING = python_net_import(
    "SMT.MastaAPI.Gears.Rating", "GearSingleFlankRating"
)

if TYPE_CHECKING:
    from typing import Any, List, Type, TypeVar

    from mastapy._private._internal.typing import PathLike

    from mastapy._private.gears.rating.bevel.standards import _670, _672, _674
    from mastapy._private.gears.rating.conical import _656
    from mastapy._private.gears.rating.cylindrical import _578
    from mastapy._private.gears.rating.cylindrical.agma import _647
    from mastapy._private.gears.rating.cylindrical.din3990 import _645
    from mastapy._private.gears.rating.cylindrical.iso6336 import (
        _624,
        _626,
        _628,
        _630,
        _632,
    )
    from mastapy._private.gears.rating.cylindrical.plastic_vdi2736 import (
        _604,
        _609,
        _610,
    )
    from mastapy._private.gears.rating.hypoid.standards import _555
    from mastapy._private.gears.rating.iso_10300 import _542, _543, _544, _545, _546
    from mastapy._private.gears.rating.klingelnberg_conical.kn3030 import _529, _530

    Self = TypeVar("Self", bound="GearSingleFlankRating")
    CastSelf = TypeVar(
        "CastSelf", bound="GearSingleFlankRating._Cast_GearSingleFlankRating"
    )


__docformat__ = "restructuredtext en"
__all__ = ("GearSingleFlankRating",)


@extended_dataclass(frozen=True, slots=True, weakref_slot=True)
class _Cast_GearSingleFlankRating:
    """Special nested class for casting GearSingleFlankRating to subclasses."""

    __parent__: "GearSingleFlankRating"

    @property
    def klingelnberg_cyclo_palloid_conical_gear_single_flank_rating(
        self: "CastSelf",
    ) -> "_529.KlingelnbergCycloPalloidConicalGearSingleFlankRating":
        from mastapy._private.gears.rating.klingelnberg_conical.kn3030 import _529

        return self.__parent__._cast(
            _529.KlingelnbergCycloPalloidConicalGearSingleFlankRating
        )

    @property
    def klingelnberg_cyclo_palloid_hypoid_gear_single_flank_rating(
        self: "CastSelf",
    ) -> "_530.KlingelnbergCycloPalloidHypoidGearSingleFlankRating":
        from mastapy._private.gears.rating.klingelnberg_conical.kn3030 import _530

        return self.__parent__._cast(
            _530.KlingelnbergCycloPalloidHypoidGearSingleFlankRating
        )

    @property
    def iso10300_single_flank_rating(
        self: "CastSelf",
    ) -> "_542.ISO10300SingleFlankRating":
        from mastapy._private.gears.rating.iso_10300 import _542

        return self.__parent__._cast(_542.ISO10300SingleFlankRating)

    @property
    def iso10300_single_flank_rating_bevel_method_b2(
        self: "CastSelf",
    ) -> "_543.ISO10300SingleFlankRatingBevelMethodB2":
        from mastapy._private.gears.rating.iso_10300 import _543

        return self.__parent__._cast(_543.ISO10300SingleFlankRatingBevelMethodB2)

    @property
    def iso10300_single_flank_rating_hypoid_method_b2(
        self: "CastSelf",
    ) -> "_544.ISO10300SingleFlankRatingHypoidMethodB2":
        from mastapy._private.gears.rating.iso_10300 import _544

        return self.__parent__._cast(_544.ISO10300SingleFlankRatingHypoidMethodB2)

    @property
    def iso10300_single_flank_rating_method_b1(
        self: "CastSelf",
    ) -> "_545.ISO10300SingleFlankRatingMethodB1":
        from mastapy._private.gears.rating.iso_10300 import _545

        return self.__parent__._cast(_545.ISO10300SingleFlankRatingMethodB1)

    @property
    def iso10300_single_flank_rating_method_b2(
        self: "CastSelf",
    ) -> "_546.ISO10300SingleFlankRatingMethodB2":
        from mastapy._private.gears.rating.iso_10300 import _546

        return self.__parent__._cast(_546.ISO10300SingleFlankRatingMethodB2)

    @property
    def gleason_hypoid_gear_single_flank_rating(
        self: "CastSelf",
    ) -> "_555.GleasonHypoidGearSingleFlankRating":
        from mastapy._private.gears.rating.hypoid.standards import _555

        return self.__parent__._cast(_555.GleasonHypoidGearSingleFlankRating)

    @property
    def cylindrical_gear_single_flank_rating(
        self: "CastSelf",
    ) -> "_578.CylindricalGearSingleFlankRating":
        from mastapy._private.gears.rating.cylindrical import _578

        return self.__parent__._cast(_578.CylindricalGearSingleFlankRating)

    @property
    def plastic_gear_vdi2736_abstract_gear_single_flank_rating(
        self: "CastSelf",
    ) -> "_604.PlasticGearVDI2736AbstractGearSingleFlankRating":
        from mastapy._private.gears.rating.cylindrical.plastic_vdi2736 import _604

        return self.__parent__._cast(
            _604.PlasticGearVDI2736AbstractGearSingleFlankRating
        )

    @property
    def plastic_vdi2736_gear_single_flank_rating_in_a_metal_plastic_or_a_plastic_metal_mesh(
        self: "CastSelf",
    ) -> "_609.PlasticVDI2736GearSingleFlankRatingInAMetalPlasticOrAPlasticMetalMesh":
        from mastapy._private.gears.rating.cylindrical.plastic_vdi2736 import _609

        return self.__parent__._cast(
            _609.PlasticVDI2736GearSingleFlankRatingInAMetalPlasticOrAPlasticMetalMesh
        )

    @property
    def plastic_vdi2736_gear_single_flank_rating_in_a_plastic_plastic_mesh(
        self: "CastSelf",
    ) -> "_610.PlasticVDI2736GearSingleFlankRatingInAPlasticPlasticMesh":
        from mastapy._private.gears.rating.cylindrical.plastic_vdi2736 import _610

        return self.__parent__._cast(
            _610.PlasticVDI2736GearSingleFlankRatingInAPlasticPlasticMesh
        )

    @property
    def iso63361996_gear_single_flank_rating(
        self: "CastSelf",
    ) -> "_624.ISO63361996GearSingleFlankRating":
        from mastapy._private.gears.rating.cylindrical.iso6336 import _624

        return self.__parent__._cast(_624.ISO63361996GearSingleFlankRating)

    @property
    def iso63362006_gear_single_flank_rating(
        self: "CastSelf",
    ) -> "_626.ISO63362006GearSingleFlankRating":
        from mastapy._private.gears.rating.cylindrical.iso6336 import _626

        return self.__parent__._cast(_626.ISO63362006GearSingleFlankRating)

    @property
    def iso63362019_gear_single_flank_rating(
        self: "CastSelf",
    ) -> "_628.ISO63362019GearSingleFlankRating":
        from mastapy._private.gears.rating.cylindrical.iso6336 import _628

        return self.__parent__._cast(_628.ISO63362019GearSingleFlankRating)

    @property
    def iso6336_abstract_gear_single_flank_rating(
        self: "CastSelf",
    ) -> "_630.ISO6336AbstractGearSingleFlankRating":
        from mastapy._private.gears.rating.cylindrical.iso6336 import _630

        return self.__parent__._cast(_630.ISO6336AbstractGearSingleFlankRating)

    @property
    def iso6336_abstract_metal_gear_single_flank_rating(
        self: "CastSelf",
    ) -> "_632.ISO6336AbstractMetalGearSingleFlankRating":
        from mastapy._private.gears.rating.cylindrical.iso6336 import _632

        return self.__parent__._cast(_632.ISO6336AbstractMetalGearSingleFlankRating)

    @property
    def din3990_gear_single_flank_rating(
        self: "CastSelf",
    ) -> "_645.DIN3990GearSingleFlankRating":
        from mastapy._private.gears.rating.cylindrical.din3990 import _645

        return self.__parent__._cast(_645.DIN3990GearSingleFlankRating)

    @property
    def agma2101_gear_single_flank_rating(
        self: "CastSelf",
    ) -> "_647.AGMA2101GearSingleFlankRating":
        from mastapy._private.gears.rating.cylindrical.agma import _647

        return self.__parent__._cast(_647.AGMA2101GearSingleFlankRating)

    @property
    def conical_gear_single_flank_rating(
        self: "CastSelf",
    ) -> "_656.ConicalGearSingleFlankRating":
        from mastapy._private.gears.rating.conical import _656

        return self.__parent__._cast(_656.ConicalGearSingleFlankRating)

    @property
    def agma_spiral_bevel_gear_single_flank_rating(
        self: "CastSelf",
    ) -> "_670.AGMASpiralBevelGearSingleFlankRating":
        from mastapy._private.gears.rating.bevel.standards import _670

        return self.__parent__._cast(_670.AGMASpiralBevelGearSingleFlankRating)

    @property
    def gleason_spiral_bevel_gear_single_flank_rating(
        self: "CastSelf",
    ) -> "_672.GleasonSpiralBevelGearSingleFlankRating":
        from mastapy._private.gears.rating.bevel.standards import _672

        return self.__parent__._cast(_672.GleasonSpiralBevelGearSingleFlankRating)

    @property
    def spiral_bevel_gear_single_flank_rating(
        self: "CastSelf",
    ) -> "_674.SpiralBevelGearSingleFlankRating":
        from mastapy._private.gears.rating.bevel.standards import _674

        return self.__parent__._cast(_674.SpiralBevelGearSingleFlankRating)

    @property
    def gear_single_flank_rating(self: "CastSelf") -> "GearSingleFlankRating":
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
class GearSingleFlankRating(_0.APIBase):
    """GearSingleFlankRating

    This is a mastapy class.
    """

    TYPE: ClassVar["Type"] = _GEAR_SINGLE_FLANK_RATING

    wrapped: "Any"

    def __post_init__(self: "Self") -> None:
        """Override of the post initialisation magic method."""
        if not hasattr(self.wrapped, "reference_count"):
            self.wrapped.reference_count = 0

        self.wrapped.reference_count += 1

    @property
    @exception_bridge
    def duration(self: "Self") -> "float":
        """float

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "Duration")

        if temp is None:
            return 0.0

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
    def number_of_load_cycles(self: "Self") -> "float":
        """float

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "NumberOfLoadCycles")

        if temp is None:
            return 0.0

        return temp

    @property
    @exception_bridge
    def power(self: "Self") -> "float":
        """float

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "Power")

        if temp is None:
            return 0.0

        return temp

    @property
    @exception_bridge
    def rotation_speed(self: "Self") -> "float":
        """float

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "RotationSpeed")

        if temp is None:
            return 0.0

        return temp

    @property
    @exception_bridge
    def torque(self: "Self") -> "float":
        """float

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "Torque")

        if temp is None:
            return 0.0

        return temp

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
    def cast_to(self: "Self") -> "_Cast_GearSingleFlankRating":
        """Cast to another type.

        Returns:
            _Cast_GearSingleFlankRating
        """
        return _Cast_GearSingleFlankRating(self)
