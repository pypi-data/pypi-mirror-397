"""MountableComponentLoadCase"""

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
from mastapy._private.system_model.analyses_and_results.static_loads import _7758

_MOUNTABLE_COMPONENT_LOAD_CASE = python_net_import(
    "SMT.MastaAPI.SystemModel.AnalysesAndResults.StaticLoads",
    "MountableComponentLoadCase",
)

if TYPE_CHECKING:
    from typing import Any, Type, TypeVar

    from mastapy._private.system_model.analyses_and_results import _2943, _2945, _2949
    from mastapy._private.system_model.analyses_and_results.static_loads import (
        _7734,
        _7740,
        _7743,
        _7746,
        _7747,
        _7748,
        _7754,
        _7760,
        _7762,
        _7765,
        _7771,
        _7773,
        _7777,
        _7782,
        _7787,
        _7805,
        _7811,
        _7826,
        _7833,
        _7836,
        _7839,
        _7842,
        _7843,
        _7849,
        _7851,
        _7853,
        _7858,
        _7861,
        _7862,
        _7863,
        _7868,
        _7872,
        _7874,
        _7878,
        _7882,
        _7884,
        _7887,
        _7890,
        _7891,
        _7892,
        _7894,
        _7895,
        _7900,
        _7901,
        _7906,
        _7907,
        _7908,
        _7911,
    )
    from mastapy._private.system_model.part_model import _2737

    Self = TypeVar("Self", bound="MountableComponentLoadCase")
    CastSelf = TypeVar(
        "CastSelf", bound="MountableComponentLoadCase._Cast_MountableComponentLoadCase"
    )


__docformat__ = "restructuredtext en"
__all__ = ("MountableComponentLoadCase",)


@extended_dataclass(frozen=True, slots=True, weakref_slot=True)
class _Cast_MountableComponentLoadCase:
    """Special nested class for casting MountableComponentLoadCase to subclasses."""

    __parent__: "MountableComponentLoadCase"

    @property
    def component_load_case(self: "CastSelf") -> "_7758.ComponentLoadCase":
        return self.__parent__._cast(_7758.ComponentLoadCase)

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
    def agma_gleason_conical_gear_load_case(
        self: "CastSelf",
    ) -> "_7734.AGMAGleasonConicalGearLoadCase":
        from mastapy._private.system_model.analyses_and_results.static_loads import (
            _7734,
        )

        return self.__parent__._cast(_7734.AGMAGleasonConicalGearLoadCase)

    @property
    def bearing_load_case(self: "CastSelf") -> "_7740.BearingLoadCase":
        from mastapy._private.system_model.analyses_and_results.static_loads import (
            _7740,
        )

        return self.__parent__._cast(_7740.BearingLoadCase)

    @property
    def bevel_differential_gear_load_case(
        self: "CastSelf",
    ) -> "_7743.BevelDifferentialGearLoadCase":
        from mastapy._private.system_model.analyses_and_results.static_loads import (
            _7743,
        )

        return self.__parent__._cast(_7743.BevelDifferentialGearLoadCase)

    @property
    def bevel_differential_planet_gear_load_case(
        self: "CastSelf",
    ) -> "_7746.BevelDifferentialPlanetGearLoadCase":
        from mastapy._private.system_model.analyses_and_results.static_loads import (
            _7746,
        )

        return self.__parent__._cast(_7746.BevelDifferentialPlanetGearLoadCase)

    @property
    def bevel_differential_sun_gear_load_case(
        self: "CastSelf",
    ) -> "_7747.BevelDifferentialSunGearLoadCase":
        from mastapy._private.system_model.analyses_and_results.static_loads import (
            _7747,
        )

        return self.__parent__._cast(_7747.BevelDifferentialSunGearLoadCase)

    @property
    def bevel_gear_load_case(self: "CastSelf") -> "_7748.BevelGearLoadCase":
        from mastapy._private.system_model.analyses_and_results.static_loads import (
            _7748,
        )

        return self.__parent__._cast(_7748.BevelGearLoadCase)

    @property
    def clutch_half_load_case(self: "CastSelf") -> "_7754.ClutchHalfLoadCase":
        from mastapy._private.system_model.analyses_and_results.static_loads import (
            _7754,
        )

        return self.__parent__._cast(_7754.ClutchHalfLoadCase)

    @property
    def concept_coupling_half_load_case(
        self: "CastSelf",
    ) -> "_7760.ConceptCouplingHalfLoadCase":
        from mastapy._private.system_model.analyses_and_results.static_loads import (
            _7760,
        )

        return self.__parent__._cast(_7760.ConceptCouplingHalfLoadCase)

    @property
    def concept_gear_load_case(self: "CastSelf") -> "_7762.ConceptGearLoadCase":
        from mastapy._private.system_model.analyses_and_results.static_loads import (
            _7762,
        )

        return self.__parent__._cast(_7762.ConceptGearLoadCase)

    @property
    def conical_gear_load_case(self: "CastSelf") -> "_7765.ConicalGearLoadCase":
        from mastapy._private.system_model.analyses_and_results.static_loads import (
            _7765,
        )

        return self.__parent__._cast(_7765.ConicalGearLoadCase)

    @property
    def connector_load_case(self: "CastSelf") -> "_7771.ConnectorLoadCase":
        from mastapy._private.system_model.analyses_and_results.static_loads import (
            _7771,
        )

        return self.__parent__._cast(_7771.ConnectorLoadCase)

    @property
    def coupling_half_load_case(self: "CastSelf") -> "_7773.CouplingHalfLoadCase":
        from mastapy._private.system_model.analyses_and_results.static_loads import (
            _7773,
        )

        return self.__parent__._cast(_7773.CouplingHalfLoadCase)

    @property
    def cvt_pulley_load_case(self: "CastSelf") -> "_7777.CVTPulleyLoadCase":
        from mastapy._private.system_model.analyses_and_results.static_loads import (
            _7777,
        )

        return self.__parent__._cast(_7777.CVTPulleyLoadCase)

    @property
    def cylindrical_gear_load_case(self: "CastSelf") -> "_7782.CylindricalGearLoadCase":
        from mastapy._private.system_model.analyses_and_results.static_loads import (
            _7782,
        )

        return self.__parent__._cast(_7782.CylindricalGearLoadCase)

    @property
    def cylindrical_planet_gear_load_case(
        self: "CastSelf",
    ) -> "_7787.CylindricalPlanetGearLoadCase":
        from mastapy._private.system_model.analyses_and_results.static_loads import (
            _7787,
        )

        return self.__parent__._cast(_7787.CylindricalPlanetGearLoadCase)

    @property
    def face_gear_load_case(self: "CastSelf") -> "_7805.FaceGearLoadCase":
        from mastapy._private.system_model.analyses_and_results.static_loads import (
            _7805,
        )

        return self.__parent__._cast(_7805.FaceGearLoadCase)

    @property
    def gear_load_case(self: "CastSelf") -> "_7811.GearLoadCase":
        from mastapy._private.system_model.analyses_and_results.static_loads import (
            _7811,
        )

        return self.__parent__._cast(_7811.GearLoadCase)

    @property
    def hypoid_gear_load_case(self: "CastSelf") -> "_7826.HypoidGearLoadCase":
        from mastapy._private.system_model.analyses_and_results.static_loads import (
            _7826,
        )

        return self.__parent__._cast(_7826.HypoidGearLoadCase)

    @property
    def klingelnberg_cyclo_palloid_conical_gear_load_case(
        self: "CastSelf",
    ) -> "_7833.KlingelnbergCycloPalloidConicalGearLoadCase":
        from mastapy._private.system_model.analyses_and_results.static_loads import (
            _7833,
        )

        return self.__parent__._cast(_7833.KlingelnbergCycloPalloidConicalGearLoadCase)

    @property
    def klingelnberg_cyclo_palloid_hypoid_gear_load_case(
        self: "CastSelf",
    ) -> "_7836.KlingelnbergCycloPalloidHypoidGearLoadCase":
        from mastapy._private.system_model.analyses_and_results.static_loads import (
            _7836,
        )

        return self.__parent__._cast(_7836.KlingelnbergCycloPalloidHypoidGearLoadCase)

    @property
    def klingelnberg_cyclo_palloid_spiral_bevel_gear_load_case(
        self: "CastSelf",
    ) -> "_7839.KlingelnbergCycloPalloidSpiralBevelGearLoadCase":
        from mastapy._private.system_model.analyses_and_results.static_loads import (
            _7839,
        )

        return self.__parent__._cast(
            _7839.KlingelnbergCycloPalloidSpiralBevelGearLoadCase
        )

    @property
    def mass_disc_load_case(self: "CastSelf") -> "_7842.MassDiscLoadCase":
        from mastapy._private.system_model.analyses_and_results.static_loads import (
            _7842,
        )

        return self.__parent__._cast(_7842.MassDiscLoadCase)

    @property
    def measurement_component_load_case(
        self: "CastSelf",
    ) -> "_7843.MeasurementComponentLoadCase":
        from mastapy._private.system_model.analyses_and_results.static_loads import (
            _7843,
        )

        return self.__parent__._cast(_7843.MeasurementComponentLoadCase)

    @property
    def oil_seal_load_case(self: "CastSelf") -> "_7849.OilSealLoadCase":
        from mastapy._private.system_model.analyses_and_results.static_loads import (
            _7849,
        )

        return self.__parent__._cast(_7849.OilSealLoadCase)

    @property
    def part_to_part_shear_coupling_half_load_case(
        self: "CastSelf",
    ) -> "_7853.PartToPartShearCouplingHalfLoadCase":
        from mastapy._private.system_model.analyses_and_results.static_loads import (
            _7853,
        )

        return self.__parent__._cast(_7853.PartToPartShearCouplingHalfLoadCase)

    @property
    def planet_carrier_load_case(self: "CastSelf") -> "_7858.PlanetCarrierLoadCase":
        from mastapy._private.system_model.analyses_and_results.static_loads import (
            _7858,
        )

        return self.__parent__._cast(_7858.PlanetCarrierLoadCase)

    @property
    def point_load_load_case(self: "CastSelf") -> "_7861.PointLoadLoadCase":
        from mastapy._private.system_model.analyses_and_results.static_loads import (
            _7861,
        )

        return self.__parent__._cast(_7861.PointLoadLoadCase)

    @property
    def power_load_load_case(self: "CastSelf") -> "_7862.PowerLoadLoadCase":
        from mastapy._private.system_model.analyses_and_results.static_loads import (
            _7862,
        )

        return self.__parent__._cast(_7862.PowerLoadLoadCase)

    @property
    def pulley_load_case(self: "CastSelf") -> "_7863.PulleyLoadCase":
        from mastapy._private.system_model.analyses_and_results.static_loads import (
            _7863,
        )

        return self.__parent__._cast(_7863.PulleyLoadCase)

    @property
    def ring_pins_load_case(self: "CastSelf") -> "_7868.RingPinsLoadCase":
        from mastapy._private.system_model.analyses_and_results.static_loads import (
            _7868,
        )

        return self.__parent__._cast(_7868.RingPinsLoadCase)

    @property
    def rolling_ring_load_case(self: "CastSelf") -> "_7872.RollingRingLoadCase":
        from mastapy._private.system_model.analyses_and_results.static_loads import (
            _7872,
        )

        return self.__parent__._cast(_7872.RollingRingLoadCase)

    @property
    def shaft_hub_connection_load_case(
        self: "CastSelf",
    ) -> "_7874.ShaftHubConnectionLoadCase":
        from mastapy._private.system_model.analyses_and_results.static_loads import (
            _7874,
        )

        return self.__parent__._cast(_7874.ShaftHubConnectionLoadCase)

    @property
    def spiral_bevel_gear_load_case(
        self: "CastSelf",
    ) -> "_7878.SpiralBevelGearLoadCase":
        from mastapy._private.system_model.analyses_and_results.static_loads import (
            _7878,
        )

        return self.__parent__._cast(_7878.SpiralBevelGearLoadCase)

    @property
    def spring_damper_half_load_case(
        self: "CastSelf",
    ) -> "_7882.SpringDamperHalfLoadCase":
        from mastapy._private.system_model.analyses_and_results.static_loads import (
            _7882,
        )

        return self.__parent__._cast(_7882.SpringDamperHalfLoadCase)

    @property
    def straight_bevel_diff_gear_load_case(
        self: "CastSelf",
    ) -> "_7884.StraightBevelDiffGearLoadCase":
        from mastapy._private.system_model.analyses_and_results.static_loads import (
            _7884,
        )

        return self.__parent__._cast(_7884.StraightBevelDiffGearLoadCase)

    @property
    def straight_bevel_gear_load_case(
        self: "CastSelf",
    ) -> "_7887.StraightBevelGearLoadCase":
        from mastapy._private.system_model.analyses_and_results.static_loads import (
            _7887,
        )

        return self.__parent__._cast(_7887.StraightBevelGearLoadCase)

    @property
    def straight_bevel_planet_gear_load_case(
        self: "CastSelf",
    ) -> "_7890.StraightBevelPlanetGearLoadCase":
        from mastapy._private.system_model.analyses_and_results.static_loads import (
            _7890,
        )

        return self.__parent__._cast(_7890.StraightBevelPlanetGearLoadCase)

    @property
    def straight_bevel_sun_gear_load_case(
        self: "CastSelf",
    ) -> "_7891.StraightBevelSunGearLoadCase":
        from mastapy._private.system_model.analyses_and_results.static_loads import (
            _7891,
        )

        return self.__parent__._cast(_7891.StraightBevelSunGearLoadCase)

    @property
    def synchroniser_half_load_case(
        self: "CastSelf",
    ) -> "_7892.SynchroniserHalfLoadCase":
        from mastapy._private.system_model.analyses_and_results.static_loads import (
            _7892,
        )

        return self.__parent__._cast(_7892.SynchroniserHalfLoadCase)

    @property
    def synchroniser_part_load_case(
        self: "CastSelf",
    ) -> "_7894.SynchroniserPartLoadCase":
        from mastapy._private.system_model.analyses_and_results.static_loads import (
            _7894,
        )

        return self.__parent__._cast(_7894.SynchroniserPartLoadCase)

    @property
    def synchroniser_sleeve_load_case(
        self: "CastSelf",
    ) -> "_7895.SynchroniserSleeveLoadCase":
        from mastapy._private.system_model.analyses_and_results.static_loads import (
            _7895,
        )

        return self.__parent__._cast(_7895.SynchroniserSleeveLoadCase)

    @property
    def torque_converter_pump_load_case(
        self: "CastSelf",
    ) -> "_7900.TorqueConverterPumpLoadCase":
        from mastapy._private.system_model.analyses_and_results.static_loads import (
            _7900,
        )

        return self.__parent__._cast(_7900.TorqueConverterPumpLoadCase)

    @property
    def torque_converter_turbine_load_case(
        self: "CastSelf",
    ) -> "_7901.TorqueConverterTurbineLoadCase":
        from mastapy._private.system_model.analyses_and_results.static_loads import (
            _7901,
        )

        return self.__parent__._cast(_7901.TorqueConverterTurbineLoadCase)

    @property
    def unbalanced_mass_load_case(self: "CastSelf") -> "_7906.UnbalancedMassLoadCase":
        from mastapy._private.system_model.analyses_and_results.static_loads import (
            _7906,
        )

        return self.__parent__._cast(_7906.UnbalancedMassLoadCase)

    @property
    def virtual_component_load_case(
        self: "CastSelf",
    ) -> "_7907.VirtualComponentLoadCase":
        from mastapy._private.system_model.analyses_and_results.static_loads import (
            _7907,
        )

        return self.__parent__._cast(_7907.VirtualComponentLoadCase)

    @property
    def worm_gear_load_case(self: "CastSelf") -> "_7908.WormGearLoadCase":
        from mastapy._private.system_model.analyses_and_results.static_loads import (
            _7908,
        )

        return self.__parent__._cast(_7908.WormGearLoadCase)

    @property
    def zerol_bevel_gear_load_case(self: "CastSelf") -> "_7911.ZerolBevelGearLoadCase":
        from mastapy._private.system_model.analyses_and_results.static_loads import (
            _7911,
        )

        return self.__parent__._cast(_7911.ZerolBevelGearLoadCase)

    @property
    def mountable_component_load_case(self: "CastSelf") -> "MountableComponentLoadCase":
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
class MountableComponentLoadCase(_7758.ComponentLoadCase):
    """MountableComponentLoadCase

    This is a mastapy class.
    """

    TYPE: ClassVar["Type"] = _MOUNTABLE_COMPONENT_LOAD_CASE

    wrapped: "Any"

    def __post_init__(self: "Self") -> None:
        """Override of the post initialisation magic method."""
        if not hasattr(self.wrapped, "reference_count"):
            self.wrapped.reference_count = 0

        self.wrapped.reference_count += 1

    @property
    @exception_bridge
    def component_design(self: "Self") -> "_2737.MountableComponent":
        """mastapy.system_model.part_model.MountableComponent

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "ComponentDesign")

        if temp is None:
            return None

        type_ = temp.GetType()
        return constructor.new(type_.Namespace, type_.Name)(temp)

    @property
    def cast_to(self: "Self") -> "_Cast_MountableComponentLoadCase":
        """Cast to another type.

        Returns:
            _Cast_MountableComponentLoadCase
        """
        return _Cast_MountableComponentLoadCase(self)
