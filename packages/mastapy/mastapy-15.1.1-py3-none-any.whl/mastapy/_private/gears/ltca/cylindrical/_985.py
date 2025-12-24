"""CylindricalGearSetLoadDistributionAnalysis"""

from __future__ import annotations

from typing import TYPE_CHECKING, ClassVar

from mastapy._private._internal.dataclasses import extended_dataclass
from mastapy._private._internal.exception_bridge import exception_bridge
from mastapy._private._internal.exceptions import CastException
from mastapy._private._internal.python_net import (
    python_net_import,
    pythonnet_property_get,
)

from mastapy._private._internal import constructor, conversion, utility
from mastapy._private.gears.ltca import _972

_CYLINDRICAL_GEAR_SET_LOAD_DISTRIBUTION_ANALYSIS = python_net_import(
    "SMT.MastaAPI.Gears.LTCA.Cylindrical", "CylindricalGearSetLoadDistributionAnalysis"
)

if TYPE_CHECKING:
    from typing import Any, List, Type, TypeVar

    from mastapy._private.gears.analysis import _1363, _1372, _1374, _1375
    from mastapy._private.gears.gear_two_d_fe_analysis import _1021
    from mastapy._private.gears.ltca.cylindrical import _982, _987
    from mastapy._private.gears.rating.cylindrical import _577

    Self = TypeVar("Self", bound="CylindricalGearSetLoadDistributionAnalysis")
    CastSelf = TypeVar(
        "CastSelf",
        bound="CylindricalGearSetLoadDistributionAnalysis._Cast_CylindricalGearSetLoadDistributionAnalysis",
    )


__docformat__ = "restructuredtext en"
__all__ = ("CylindricalGearSetLoadDistributionAnalysis",)


@extended_dataclass(frozen=True, slots=True, weakref_slot=True)
class _Cast_CylindricalGearSetLoadDistributionAnalysis:
    """Special nested class for casting CylindricalGearSetLoadDistributionAnalysis to subclasses."""

    __parent__: "CylindricalGearSetLoadDistributionAnalysis"

    @property
    def gear_set_load_distribution_analysis(
        self: "CastSelf",
    ) -> "_972.GearSetLoadDistributionAnalysis":
        return self.__parent__._cast(_972.GearSetLoadDistributionAnalysis)

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
    def gear_set_design_analysis(self: "CastSelf") -> "_1372.GearSetDesignAnalysis":
        from mastapy._private.gears.analysis import _1372

        return self.__parent__._cast(_1372.GearSetDesignAnalysis)

    @property
    def abstract_gear_set_analysis(self: "CastSelf") -> "_1363.AbstractGearSetAnalysis":
        from mastapy._private.gears.analysis import _1363

        return self.__parent__._cast(_1363.AbstractGearSetAnalysis)

    @property
    def face_gear_set_load_distribution_analysis(
        self: "CastSelf",
    ) -> "_987.FaceGearSetLoadDistributionAnalysis":
        from mastapy._private.gears.ltca.cylindrical import _987

        return self.__parent__._cast(_987.FaceGearSetLoadDistributionAnalysis)

    @property
    def cylindrical_gear_set_load_distribution_analysis(
        self: "CastSelf",
    ) -> "CylindricalGearSetLoadDistributionAnalysis":
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
class CylindricalGearSetLoadDistributionAnalysis(_972.GearSetLoadDistributionAnalysis):
    """CylindricalGearSetLoadDistributionAnalysis

    This is a mastapy class.
    """

    TYPE: ClassVar["Type"] = _CYLINDRICAL_GEAR_SET_LOAD_DISTRIBUTION_ANALYSIS

    wrapped: "Any"

    def __post_init__(self: "Self") -> None:
        """Override of the post initialisation magic method."""
        if not hasattr(self.wrapped, "reference_count"):
            self.wrapped.reference_count = 0

        self.wrapped.reference_count += 1

    @property
    @exception_bridge
    def rating(self: "Self") -> "_577.CylindricalGearSetRating":
        """mastapy.gears.rating.cylindrical.CylindricalGearSetRating

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "Rating")

        if temp is None:
            return None

        type_ = temp.GetType()
        return constructor.new(type_.Namespace, type_.Name)(temp)

    @property
    @exception_bridge
    def tiff_analysis(self: "Self") -> "_1021.CylindricalGearSetTIFFAnalysis":
        """mastapy.gears.gear_two_d_fe_analysis.CylindricalGearSetTIFFAnalysis

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "TIFFAnalysis")

        if temp is None:
            return None

        type_ = temp.GetType()
        return constructor.new(type_.Namespace, type_.Name)(temp)

    @property
    @exception_bridge
    def meshes(
        self: "Self",
    ) -> "List[_982.CylindricalGearMeshLoadDistributionAnalysis]":
        """List[mastapy.gears.ltca.cylindrical.CylindricalGearMeshLoadDistributionAnalysis]

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
    def cast_to(self: "Self") -> "_Cast_CylindricalGearSetLoadDistributionAnalysis":
        """Cast to another type.

        Returns:
            _Cast_CylindricalGearSetLoadDistributionAnalysis
        """
        return _Cast_CylindricalGearSetLoadDistributionAnalysis(self)
