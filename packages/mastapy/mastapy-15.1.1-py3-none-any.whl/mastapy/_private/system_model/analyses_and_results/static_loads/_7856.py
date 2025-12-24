"""PlanetaryGearSetLoadCase"""

from __future__ import annotations

from typing import TYPE_CHECKING, ClassVar

from mastapy._private._internal.dataclasses import extended_dataclass
from mastapy._private._internal.exception_bridge import exception_bridge
from mastapy._private._internal.exceptions import CastException
from mastapy._private._internal.python_net import (
    python_net_import,
    pythonnet_property_get,
    pythonnet_property_set,
)
from mastapy._private._internal.type_enforcement import enforce_parameter_types

from mastapy._private._internal import constructor, conversion, utility
from mastapy._private.system_model.analyses_and_results.static_loads import _7786

_PLANETARY_GEAR_SET_LOAD_CASE = python_net_import(
    "SMT.MastaAPI.SystemModel.AnalysesAndResults.StaticLoads",
    "PlanetaryGearSetLoadCase",
)

if TYPE_CHECKING:
    from typing import Any, Type, TypeVar

    from mastapy._private.system_model.analyses_and_results import _2943, _2945, _2949
    from mastapy._private.system_model.analyses_and_results.static_loads import (
        _7727,
        _7816,
        _7851,
        _7877,
    )
    from mastapy._private.system_model.part_model.gears import _2823
    from mastapy._private.utility import _1813

    Self = TypeVar("Self", bound="PlanetaryGearSetLoadCase")
    CastSelf = TypeVar(
        "CastSelf", bound="PlanetaryGearSetLoadCase._Cast_PlanetaryGearSetLoadCase"
    )


__docformat__ = "restructuredtext en"
__all__ = ("PlanetaryGearSetLoadCase",)


@extended_dataclass(frozen=True, slots=True, weakref_slot=True)
class _Cast_PlanetaryGearSetLoadCase:
    """Special nested class for casting PlanetaryGearSetLoadCase to subclasses."""

    __parent__: "PlanetaryGearSetLoadCase"

    @property
    def cylindrical_gear_set_load_case(
        self: "CastSelf",
    ) -> "_7786.CylindricalGearSetLoadCase":
        return self.__parent__._cast(_7786.CylindricalGearSetLoadCase)

    @property
    def gear_set_load_case(self: "CastSelf") -> "_7816.GearSetLoadCase":
        from mastapy._private.system_model.analyses_and_results.static_loads import (
            _7816,
        )

        return self.__parent__._cast(_7816.GearSetLoadCase)

    @property
    def specialised_assembly_load_case(
        self: "CastSelf",
    ) -> "_7877.SpecialisedAssemblyLoadCase":
        from mastapy._private.system_model.analyses_and_results.static_loads import (
            _7877,
        )

        return self.__parent__._cast(_7877.SpecialisedAssemblyLoadCase)

    @property
    def abstract_assembly_load_case(
        self: "CastSelf",
    ) -> "_7727.AbstractAssemblyLoadCase":
        from mastapy._private.system_model.analyses_and_results.static_loads import (
            _7727,
        )

        return self.__parent__._cast(_7727.AbstractAssemblyLoadCase)

    @property
    def part_load_case(self: "CastSelf") -> "_7851.PartLoadCase":
        from mastapy._private.system_model.analyses_and_results.static_loads import (
            _7851,
        )

        return self.__parent__._cast(_7851.PartLoadCase)

    @property
    def part_analysis(self: "CastSelf") -> "_2949.PartAnalysis":
        from mastapy._private.system_model.analyses_and_results import _2949

        return self.__parent__._cast(_2949.PartAnalysis)

    @property
    def design_entity_single_context_analysis(
        self: "CastSelf",
    ) -> "_2945.DesignEntitySingleContextAnalysis":
        from mastapy._private.system_model.analyses_and_results import _2945

        return self.__parent__._cast(_2945.DesignEntitySingleContextAnalysis)

    @property
    def design_entity_analysis(self: "CastSelf") -> "_2943.DesignEntityAnalysis":
        from mastapy._private.system_model.analyses_and_results import _2943

        return self.__parent__._cast(_2943.DesignEntityAnalysis)

    @property
    def planetary_gear_set_load_case(self: "CastSelf") -> "PlanetaryGearSetLoadCase":
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
class PlanetaryGearSetLoadCase(_7786.CylindricalGearSetLoadCase):
    """PlanetaryGearSetLoadCase

    This is a mastapy class.
    """

    TYPE: ClassVar["Type"] = _PLANETARY_GEAR_SET_LOAD_CASE

    wrapped: "Any"

    def __post_init__(self: "Self") -> None:
        """Override of the post initialisation magic method."""
        if not hasattr(self.wrapped, "reference_count"):
            self.wrapped.reference_count = 0

        self.wrapped.reference_count += 1

    @property
    @exception_bridge
    def include_gear_blank_elastic_distortion(
        self: "Self",
    ) -> "_1813.LoadCaseOverrideOption":
        """mastapy.utility.LoadCaseOverrideOption"""
        temp = pythonnet_property_get(self.wrapped, "IncludeGearBlankElasticDistortion")

        if temp is None:
            return None

        value = conversion.pn_to_mp_enum(
            temp, "SMT.MastaAPI.Utility.LoadCaseOverrideOption"
        )

        if value is None:
            return None

        return constructor.new_from_mastapy(
            "mastapy._private.utility._1813", "LoadCaseOverrideOption"
        )(value)

    @include_gear_blank_elastic_distortion.setter
    @exception_bridge
    @enforce_parameter_types
    def include_gear_blank_elastic_distortion(
        self: "Self", value: "_1813.LoadCaseOverrideOption"
    ) -> None:
        value = conversion.mp_to_pn_enum(
            value, "SMT.MastaAPI.Utility.LoadCaseOverrideOption"
        )
        pythonnet_property_set(self.wrapped, "IncludeGearBlankElasticDistortion", value)

    @property
    @exception_bridge
    def specify_separate_micro_geometry_for_each_planet_gear(self: "Self") -> "bool":
        """bool"""
        temp = pythonnet_property_get(
            self.wrapped, "SpecifySeparateMicroGeometryForEachPlanetGear"
        )

        if temp is None:
            return False

        return temp

    @specify_separate_micro_geometry_for_each_planet_gear.setter
    @exception_bridge
    @enforce_parameter_types
    def specify_separate_micro_geometry_for_each_planet_gear(
        self: "Self", value: "bool"
    ) -> None:
        pythonnet_property_set(
            self.wrapped,
            "SpecifySeparateMicroGeometryForEachPlanetGear",
            bool(value) if value is not None else False,
        )

    @property
    @exception_bridge
    def assembly_design(self: "Self") -> "_2823.PlanetaryGearSet":
        """mastapy.system_model.part_model.gears.PlanetaryGearSet

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "AssemblyDesign")

        if temp is None:
            return None

        type_ = temp.GetType()
        return constructor.new(type_.Namespace, type_.Name)(temp)

    @property
    def cast_to(self: "Self") -> "_Cast_PlanetaryGearSetLoadCase":
        """Cast to another type.

        Returns:
            _Cast_PlanetaryGearSetLoadCase
        """
        return _Cast_PlanetaryGearSetLoadCase(self)
