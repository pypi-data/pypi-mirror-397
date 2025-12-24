"""ComponentModalAnalysis"""

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
from mastapy._private.system_model.analyses_and_results.modal_analyses import _4987

_COMPONENT_MODAL_ANALYSIS = python_net_import(
    "SMT.MastaAPI.SystemModel.AnalysesAndResults.ModalAnalyses",
    "ComponentModalAnalysis",
)

if TYPE_CHECKING:
    from typing import Any, Type, TypeVar

    from mastapy._private.system_model.analyses_and_results import _2943, _2945, _2949
    from mastapy._private.system_model.analyses_and_results.analysis_cases import (
        _7941,
        _7944,
    )
    from mastapy._private.system_model.analyses_and_results.modal_analyses import (
        _4895,
        _4896,
        _4899,
        _4902,
        _4906,
        _4908,
        _4909,
        _4911,
        _4914,
        _4916,
        _4921,
        _4924,
        _4927,
        _4930,
        _4933,
        _4937,
        _4940,
        _4943,
        _4945,
        _4946,
        _4950,
        _4952,
        _4954,
        _4958,
        _4960,
        _4962,
        _4966,
        _4969,
        _4972,
        _4974,
        _4975,
        _4977,
        _4983,
        _4985,
        _4989,
        _4993,
        _4994,
        _4995,
        _4996,
        _4997,
        _5001,
        _5003,
        _5004,
        _5009,
        _5012,
        _5015,
        _5018,
        _5020,
        _5021,
        _5022,
        _5024,
        _5025,
        _5028,
        _5029,
        _5030,
        _5031,
        _5036,
        _5039,
    )
    from mastapy._private.system_model.analyses_and_results.system_deflections import (
        _3007,
    )
    from mastapy._private.system_model.part_model import _2714

    Self = TypeVar("Self", bound="ComponentModalAnalysis")
    CastSelf = TypeVar(
        "CastSelf", bound="ComponentModalAnalysis._Cast_ComponentModalAnalysis"
    )


__docformat__ = "restructuredtext en"
__all__ = ("ComponentModalAnalysis",)


@extended_dataclass(frozen=True, slots=True, weakref_slot=True)
class _Cast_ComponentModalAnalysis:
    """Special nested class for casting ComponentModalAnalysis to subclasses."""

    __parent__: "ComponentModalAnalysis"

    @property
    def part_modal_analysis(self: "CastSelf") -> "_4987.PartModalAnalysis":
        return self.__parent__._cast(_4987.PartModalAnalysis)

    @property
    def part_static_load_analysis_case(
        self: "CastSelf",
    ) -> "_7944.PartStaticLoadAnalysisCase":
        from mastapy._private.system_model.analyses_and_results.analysis_cases import (
            _7944,
        )

        return self.__parent__._cast(_7944.PartStaticLoadAnalysisCase)

    @property
    def part_analysis_case(self: "CastSelf") -> "_7941.PartAnalysisCase":
        from mastapy._private.system_model.analyses_and_results.analysis_cases import (
            _7941,
        )

        return self.__parent__._cast(_7941.PartAnalysisCase)

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
    def abstract_shaft_modal_analysis(
        self: "CastSelf",
    ) -> "_4895.AbstractShaftModalAnalysis":
        from mastapy._private.system_model.analyses_and_results.modal_analyses import (
            _4895,
        )

        return self.__parent__._cast(_4895.AbstractShaftModalAnalysis)

    @property
    def abstract_shaft_or_housing_modal_analysis(
        self: "CastSelf",
    ) -> "_4896.AbstractShaftOrHousingModalAnalysis":
        from mastapy._private.system_model.analyses_and_results.modal_analyses import (
            _4896,
        )

        return self.__parent__._cast(_4896.AbstractShaftOrHousingModalAnalysis)

    @property
    def agma_gleason_conical_gear_modal_analysis(
        self: "CastSelf",
    ) -> "_4899.AGMAGleasonConicalGearModalAnalysis":
        from mastapy._private.system_model.analyses_and_results.modal_analyses import (
            _4899,
        )

        return self.__parent__._cast(_4899.AGMAGleasonConicalGearModalAnalysis)

    @property
    def bearing_modal_analysis(self: "CastSelf") -> "_4902.BearingModalAnalysis":
        from mastapy._private.system_model.analyses_and_results.modal_analyses import (
            _4902,
        )

        return self.__parent__._cast(_4902.BearingModalAnalysis)

    @property
    def bevel_differential_gear_modal_analysis(
        self: "CastSelf",
    ) -> "_4906.BevelDifferentialGearModalAnalysis":
        from mastapy._private.system_model.analyses_and_results.modal_analyses import (
            _4906,
        )

        return self.__parent__._cast(_4906.BevelDifferentialGearModalAnalysis)

    @property
    def bevel_differential_planet_gear_modal_analysis(
        self: "CastSelf",
    ) -> "_4908.BevelDifferentialPlanetGearModalAnalysis":
        from mastapy._private.system_model.analyses_and_results.modal_analyses import (
            _4908,
        )

        return self.__parent__._cast(_4908.BevelDifferentialPlanetGearModalAnalysis)

    @property
    def bevel_differential_sun_gear_modal_analysis(
        self: "CastSelf",
    ) -> "_4909.BevelDifferentialSunGearModalAnalysis":
        from mastapy._private.system_model.analyses_and_results.modal_analyses import (
            _4909,
        )

        return self.__parent__._cast(_4909.BevelDifferentialSunGearModalAnalysis)

    @property
    def bevel_gear_modal_analysis(self: "CastSelf") -> "_4911.BevelGearModalAnalysis":
        from mastapy._private.system_model.analyses_and_results.modal_analyses import (
            _4911,
        )

        return self.__parent__._cast(_4911.BevelGearModalAnalysis)

    @property
    def bolt_modal_analysis(self: "CastSelf") -> "_4914.BoltModalAnalysis":
        from mastapy._private.system_model.analyses_and_results.modal_analyses import (
            _4914,
        )

        return self.__parent__._cast(_4914.BoltModalAnalysis)

    @property
    def clutch_half_modal_analysis(self: "CastSelf") -> "_4916.ClutchHalfModalAnalysis":
        from mastapy._private.system_model.analyses_and_results.modal_analyses import (
            _4916,
        )

        return self.__parent__._cast(_4916.ClutchHalfModalAnalysis)

    @property
    def concept_coupling_half_modal_analysis(
        self: "CastSelf",
    ) -> "_4921.ConceptCouplingHalfModalAnalysis":
        from mastapy._private.system_model.analyses_and_results.modal_analyses import (
            _4921,
        )

        return self.__parent__._cast(_4921.ConceptCouplingHalfModalAnalysis)

    @property
    def concept_gear_modal_analysis(
        self: "CastSelf",
    ) -> "_4924.ConceptGearModalAnalysis":
        from mastapy._private.system_model.analyses_and_results.modal_analyses import (
            _4924,
        )

        return self.__parent__._cast(_4924.ConceptGearModalAnalysis)

    @property
    def conical_gear_modal_analysis(
        self: "CastSelf",
    ) -> "_4927.ConicalGearModalAnalysis":
        from mastapy._private.system_model.analyses_and_results.modal_analyses import (
            _4927,
        )

        return self.__parent__._cast(_4927.ConicalGearModalAnalysis)

    @property
    def connector_modal_analysis(self: "CastSelf") -> "_4930.ConnectorModalAnalysis":
        from mastapy._private.system_model.analyses_and_results.modal_analyses import (
            _4930,
        )

        return self.__parent__._cast(_4930.ConnectorModalAnalysis)

    @property
    def coupling_half_modal_analysis(
        self: "CastSelf",
    ) -> "_4933.CouplingHalfModalAnalysis":
        from mastapy._private.system_model.analyses_and_results.modal_analyses import (
            _4933,
        )

        return self.__parent__._cast(_4933.CouplingHalfModalAnalysis)

    @property
    def cvt_pulley_modal_analysis(self: "CastSelf") -> "_4937.CVTPulleyModalAnalysis":
        from mastapy._private.system_model.analyses_and_results.modal_analyses import (
            _4937,
        )

        return self.__parent__._cast(_4937.CVTPulleyModalAnalysis)

    @property
    def cycloidal_disc_modal_analysis(
        self: "CastSelf",
    ) -> "_4940.CycloidalDiscModalAnalysis":
        from mastapy._private.system_model.analyses_and_results.modal_analyses import (
            _4940,
        )

        return self.__parent__._cast(_4940.CycloidalDiscModalAnalysis)

    @property
    def cylindrical_gear_modal_analysis(
        self: "CastSelf",
    ) -> "_4943.CylindricalGearModalAnalysis":
        from mastapy._private.system_model.analyses_and_results.modal_analyses import (
            _4943,
        )

        return self.__parent__._cast(_4943.CylindricalGearModalAnalysis)

    @property
    def cylindrical_planet_gear_modal_analysis(
        self: "CastSelf",
    ) -> "_4945.CylindricalPlanetGearModalAnalysis":
        from mastapy._private.system_model.analyses_and_results.modal_analyses import (
            _4945,
        )

        return self.__parent__._cast(_4945.CylindricalPlanetGearModalAnalysis)

    @property
    def datum_modal_analysis(self: "CastSelf") -> "_4946.DatumModalAnalysis":
        from mastapy._private.system_model.analyses_and_results.modal_analyses import (
            _4946,
        )

        return self.__parent__._cast(_4946.DatumModalAnalysis)

    @property
    def external_cad_model_modal_analysis(
        self: "CastSelf",
    ) -> "_4950.ExternalCADModelModalAnalysis":
        from mastapy._private.system_model.analyses_and_results.modal_analyses import (
            _4950,
        )

        return self.__parent__._cast(_4950.ExternalCADModelModalAnalysis)

    @property
    def face_gear_modal_analysis(self: "CastSelf") -> "_4952.FaceGearModalAnalysis":
        from mastapy._private.system_model.analyses_and_results.modal_analyses import (
            _4952,
        )

        return self.__parent__._cast(_4952.FaceGearModalAnalysis)

    @property
    def fe_part_modal_analysis(self: "CastSelf") -> "_4954.FEPartModalAnalysis":
        from mastapy._private.system_model.analyses_and_results.modal_analyses import (
            _4954,
        )

        return self.__parent__._cast(_4954.FEPartModalAnalysis)

    @property
    def gear_modal_analysis(self: "CastSelf") -> "_4958.GearModalAnalysis":
        from mastapy._private.system_model.analyses_and_results.modal_analyses import (
            _4958,
        )

        return self.__parent__._cast(_4958.GearModalAnalysis)

    @property
    def guide_dxf_model_modal_analysis(
        self: "CastSelf",
    ) -> "_4960.GuideDxfModelModalAnalysis":
        from mastapy._private.system_model.analyses_and_results.modal_analyses import (
            _4960,
        )

        return self.__parent__._cast(_4960.GuideDxfModelModalAnalysis)

    @property
    def hypoid_gear_modal_analysis(self: "CastSelf") -> "_4962.HypoidGearModalAnalysis":
        from mastapy._private.system_model.analyses_and_results.modal_analyses import (
            _4962,
        )

        return self.__parent__._cast(_4962.HypoidGearModalAnalysis)

    @property
    def klingelnberg_cyclo_palloid_conical_gear_modal_analysis(
        self: "CastSelf",
    ) -> "_4966.KlingelnbergCycloPalloidConicalGearModalAnalysis":
        from mastapy._private.system_model.analyses_and_results.modal_analyses import (
            _4966,
        )

        return self.__parent__._cast(
            _4966.KlingelnbergCycloPalloidConicalGearModalAnalysis
        )

    @property
    def klingelnberg_cyclo_palloid_hypoid_gear_modal_analysis(
        self: "CastSelf",
    ) -> "_4969.KlingelnbergCycloPalloidHypoidGearModalAnalysis":
        from mastapy._private.system_model.analyses_and_results.modal_analyses import (
            _4969,
        )

        return self.__parent__._cast(
            _4969.KlingelnbergCycloPalloidHypoidGearModalAnalysis
        )

    @property
    def klingelnberg_cyclo_palloid_spiral_bevel_gear_modal_analysis(
        self: "CastSelf",
    ) -> "_4972.KlingelnbergCycloPalloidSpiralBevelGearModalAnalysis":
        from mastapy._private.system_model.analyses_and_results.modal_analyses import (
            _4972,
        )

        return self.__parent__._cast(
            _4972.KlingelnbergCycloPalloidSpiralBevelGearModalAnalysis
        )

    @property
    def mass_disc_modal_analysis(self: "CastSelf") -> "_4974.MassDiscModalAnalysis":
        from mastapy._private.system_model.analyses_and_results.modal_analyses import (
            _4974,
        )

        return self.__parent__._cast(_4974.MassDiscModalAnalysis)

    @property
    def measurement_component_modal_analysis(
        self: "CastSelf",
    ) -> "_4975.MeasurementComponentModalAnalysis":
        from mastapy._private.system_model.analyses_and_results.modal_analyses import (
            _4975,
        )

        return self.__parent__._cast(_4975.MeasurementComponentModalAnalysis)

    @property
    def microphone_modal_analysis(self: "CastSelf") -> "_4977.MicrophoneModalAnalysis":
        from mastapy._private.system_model.analyses_and_results.modal_analyses import (
            _4977,
        )

        return self.__parent__._cast(_4977.MicrophoneModalAnalysis)

    @property
    def mountable_component_modal_analysis(
        self: "CastSelf",
    ) -> "_4983.MountableComponentModalAnalysis":
        from mastapy._private.system_model.analyses_and_results.modal_analyses import (
            _4983,
        )

        return self.__parent__._cast(_4983.MountableComponentModalAnalysis)

    @property
    def oil_seal_modal_analysis(self: "CastSelf") -> "_4985.OilSealModalAnalysis":
        from mastapy._private.system_model.analyses_and_results.modal_analyses import (
            _4985,
        )

        return self.__parent__._cast(_4985.OilSealModalAnalysis)

    @property
    def part_to_part_shear_coupling_half_modal_analysis(
        self: "CastSelf",
    ) -> "_4989.PartToPartShearCouplingHalfModalAnalysis":
        from mastapy._private.system_model.analyses_and_results.modal_analyses import (
            _4989,
        )

        return self.__parent__._cast(_4989.PartToPartShearCouplingHalfModalAnalysis)

    @property
    def planet_carrier_modal_analysis(
        self: "CastSelf",
    ) -> "_4993.PlanetCarrierModalAnalysis":
        from mastapy._private.system_model.analyses_and_results.modal_analyses import (
            _4993,
        )

        return self.__parent__._cast(_4993.PlanetCarrierModalAnalysis)

    @property
    def point_load_modal_analysis(self: "CastSelf") -> "_4994.PointLoadModalAnalysis":
        from mastapy._private.system_model.analyses_and_results.modal_analyses import (
            _4994,
        )

        return self.__parent__._cast(_4994.PointLoadModalAnalysis)

    @property
    def power_load_modal_analysis(self: "CastSelf") -> "_4995.PowerLoadModalAnalysis":
        from mastapy._private.system_model.analyses_and_results.modal_analyses import (
            _4995,
        )

        return self.__parent__._cast(_4995.PowerLoadModalAnalysis)

    @property
    def pulley_modal_analysis(self: "CastSelf") -> "_4996.PulleyModalAnalysis":
        from mastapy._private.system_model.analyses_and_results.modal_analyses import (
            _4996,
        )

        return self.__parent__._cast(_4996.PulleyModalAnalysis)

    @property
    def ring_pins_modal_analysis(self: "CastSelf") -> "_4997.RingPinsModalAnalysis":
        from mastapy._private.system_model.analyses_and_results.modal_analyses import (
            _4997,
        )

        return self.__parent__._cast(_4997.RingPinsModalAnalysis)

    @property
    def rolling_ring_modal_analysis(
        self: "CastSelf",
    ) -> "_5001.RollingRingModalAnalysis":
        from mastapy._private.system_model.analyses_and_results.modal_analyses import (
            _5001,
        )

        return self.__parent__._cast(_5001.RollingRingModalAnalysis)

    @property
    def shaft_hub_connection_modal_analysis(
        self: "CastSelf",
    ) -> "_5003.ShaftHubConnectionModalAnalysis":
        from mastapy._private.system_model.analyses_and_results.modal_analyses import (
            _5003,
        )

        return self.__parent__._cast(_5003.ShaftHubConnectionModalAnalysis)

    @property
    def shaft_modal_analysis(self: "CastSelf") -> "_5004.ShaftModalAnalysis":
        from mastapy._private.system_model.analyses_and_results.modal_analyses import (
            _5004,
        )

        return self.__parent__._cast(_5004.ShaftModalAnalysis)

    @property
    def spiral_bevel_gear_modal_analysis(
        self: "CastSelf",
    ) -> "_5009.SpiralBevelGearModalAnalysis":
        from mastapy._private.system_model.analyses_and_results.modal_analyses import (
            _5009,
        )

        return self.__parent__._cast(_5009.SpiralBevelGearModalAnalysis)

    @property
    def spring_damper_half_modal_analysis(
        self: "CastSelf",
    ) -> "_5012.SpringDamperHalfModalAnalysis":
        from mastapy._private.system_model.analyses_and_results.modal_analyses import (
            _5012,
        )

        return self.__parent__._cast(_5012.SpringDamperHalfModalAnalysis)

    @property
    def straight_bevel_diff_gear_modal_analysis(
        self: "CastSelf",
    ) -> "_5015.StraightBevelDiffGearModalAnalysis":
        from mastapy._private.system_model.analyses_and_results.modal_analyses import (
            _5015,
        )

        return self.__parent__._cast(_5015.StraightBevelDiffGearModalAnalysis)

    @property
    def straight_bevel_gear_modal_analysis(
        self: "CastSelf",
    ) -> "_5018.StraightBevelGearModalAnalysis":
        from mastapy._private.system_model.analyses_and_results.modal_analyses import (
            _5018,
        )

        return self.__parent__._cast(_5018.StraightBevelGearModalAnalysis)

    @property
    def straight_bevel_planet_gear_modal_analysis(
        self: "CastSelf",
    ) -> "_5020.StraightBevelPlanetGearModalAnalysis":
        from mastapy._private.system_model.analyses_and_results.modal_analyses import (
            _5020,
        )

        return self.__parent__._cast(_5020.StraightBevelPlanetGearModalAnalysis)

    @property
    def straight_bevel_sun_gear_modal_analysis(
        self: "CastSelf",
    ) -> "_5021.StraightBevelSunGearModalAnalysis":
        from mastapy._private.system_model.analyses_and_results.modal_analyses import (
            _5021,
        )

        return self.__parent__._cast(_5021.StraightBevelSunGearModalAnalysis)

    @property
    def synchroniser_half_modal_analysis(
        self: "CastSelf",
    ) -> "_5022.SynchroniserHalfModalAnalysis":
        from mastapy._private.system_model.analyses_and_results.modal_analyses import (
            _5022,
        )

        return self.__parent__._cast(_5022.SynchroniserHalfModalAnalysis)

    @property
    def synchroniser_part_modal_analysis(
        self: "CastSelf",
    ) -> "_5024.SynchroniserPartModalAnalysis":
        from mastapy._private.system_model.analyses_and_results.modal_analyses import (
            _5024,
        )

        return self.__parent__._cast(_5024.SynchroniserPartModalAnalysis)

    @property
    def synchroniser_sleeve_modal_analysis(
        self: "CastSelf",
    ) -> "_5025.SynchroniserSleeveModalAnalysis":
        from mastapy._private.system_model.analyses_and_results.modal_analyses import (
            _5025,
        )

        return self.__parent__._cast(_5025.SynchroniserSleeveModalAnalysis)

    @property
    def torque_converter_pump_modal_analysis(
        self: "CastSelf",
    ) -> "_5028.TorqueConverterPumpModalAnalysis":
        from mastapy._private.system_model.analyses_and_results.modal_analyses import (
            _5028,
        )

        return self.__parent__._cast(_5028.TorqueConverterPumpModalAnalysis)

    @property
    def torque_converter_turbine_modal_analysis(
        self: "CastSelf",
    ) -> "_5029.TorqueConverterTurbineModalAnalysis":
        from mastapy._private.system_model.analyses_and_results.modal_analyses import (
            _5029,
        )

        return self.__parent__._cast(_5029.TorqueConverterTurbineModalAnalysis)

    @property
    def unbalanced_mass_modal_analysis(
        self: "CastSelf",
    ) -> "_5030.UnbalancedMassModalAnalysis":
        from mastapy._private.system_model.analyses_and_results.modal_analyses import (
            _5030,
        )

        return self.__parent__._cast(_5030.UnbalancedMassModalAnalysis)

    @property
    def virtual_component_modal_analysis(
        self: "CastSelf",
    ) -> "_5031.VirtualComponentModalAnalysis":
        from mastapy._private.system_model.analyses_and_results.modal_analyses import (
            _5031,
        )

        return self.__parent__._cast(_5031.VirtualComponentModalAnalysis)

    @property
    def worm_gear_modal_analysis(self: "CastSelf") -> "_5036.WormGearModalAnalysis":
        from mastapy._private.system_model.analyses_and_results.modal_analyses import (
            _5036,
        )

        return self.__parent__._cast(_5036.WormGearModalAnalysis)

    @property
    def zerol_bevel_gear_modal_analysis(
        self: "CastSelf",
    ) -> "_5039.ZerolBevelGearModalAnalysis":
        from mastapy._private.system_model.analyses_and_results.modal_analyses import (
            _5039,
        )

        return self.__parent__._cast(_5039.ZerolBevelGearModalAnalysis)

    @property
    def component_modal_analysis(self: "CastSelf") -> "ComponentModalAnalysis":
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
class ComponentModalAnalysis(_4987.PartModalAnalysis):
    """ComponentModalAnalysis

    This is a mastapy class.
    """

    TYPE: ClassVar["Type"] = _COMPONENT_MODAL_ANALYSIS

    wrapped: "Any"

    def __post_init__(self: "Self") -> None:
        """Override of the post initialisation magic method."""
        if not hasattr(self.wrapped, "reference_count"):
            self.wrapped.reference_count = 0

        self.wrapped.reference_count += 1

    @property
    @exception_bridge
    def component_design(self: "Self") -> "_2714.Component":
        """mastapy.system_model.part_model.Component

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "ComponentDesign")

        if temp is None:
            return None

        type_ = temp.GetType()
        return constructor.new(type_.Namespace, type_.Name)(temp)

    @property
    @exception_bridge
    def system_deflection_results(self: "Self") -> "_3007.ComponentSystemDeflection":
        """mastapy.system_model.analyses_and_results.system_deflections.ComponentSystemDeflection

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "SystemDeflectionResults")

        if temp is None:
            return None

        type_ = temp.GetType()
        return constructor.new(type_.Namespace, type_.Name)(temp)

    @property
    def cast_to(self: "Self") -> "_Cast_ComponentModalAnalysis":
        """Cast to another type.

        Returns:
            _Cast_ComponentModalAnalysis
        """
        return _Cast_ComponentModalAnalysis(self)
