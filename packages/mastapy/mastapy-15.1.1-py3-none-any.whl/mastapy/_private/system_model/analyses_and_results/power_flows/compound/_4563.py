"""PartCompoundPowerFlow"""

from __future__ import annotations

from typing import TYPE_CHECKING, ClassVar

from mastapy._private._internal.dataclasses import extended_dataclass
from mastapy._private._internal.exception_bridge import exception_bridge
from mastapy._private._internal.exceptions import CastException
from mastapy._private._internal.python_net import (
    python_net_import,
    pythonnet_property_get,
)

from mastapy._private._internal import conversion, utility
from mastapy._private.system_model.analyses_and_results.analysis_cases import _7942

_PART_COMPOUND_POWER_FLOW = python_net_import(
    "SMT.MastaAPI.SystemModel.AnalysesAndResults.PowerFlows.Compound",
    "PartCompoundPowerFlow",
)

if TYPE_CHECKING:
    from typing import Any, List, Type, TypeVar

    from mastapy._private.system_model.analyses_and_results import _2943
    from mastapy._private.system_model.analyses_and_results.analysis_cases import _7939
    from mastapy._private.system_model.analyses_and_results.power_flows import _4429
    from mastapy._private.system_model.analyses_and_results.power_flows.compound import (
        _4482,
        _4483,
        _4484,
        _4486,
        _4488,
        _4489,
        _4490,
        _4492,
        _4493,
        _4495,
        _4496,
        _4497,
        _4498,
        _4500,
        _4501,
        _4502,
        _4503,
        _4505,
        _4507,
        _4508,
        _4510,
        _4511,
        _4513,
        _4514,
        _4516,
        _4518,
        _4519,
        _4521,
        _4523,
        _4524,
        _4525,
        _4527,
        _4529,
        _4531,
        _4532,
        _4533,
        _4534,
        _4535,
        _4537,
        _4538,
        _4539,
        _4540,
        _4542,
        _4543,
        _4544,
        _4546,
        _4548,
        _4550,
        _4551,
        _4553,
        _4554,
        _4556,
        _4557,
        _4558,
        _4559,
        _4560,
        _4561,
        _4562,
        _4564,
        _4566,
        _4568,
        _4569,
        _4570,
        _4571,
        _4572,
        _4573,
        _4575,
        _4576,
        _4578,
        _4579,
        _4580,
        _4582,
        _4583,
        _4585,
        _4586,
        _4588,
        _4589,
        _4591,
        _4592,
        _4594,
        _4595,
        _4596,
        _4597,
        _4598,
        _4599,
        _4600,
        _4601,
        _4603,
        _4604,
        _4605,
        _4606,
        _4607,
        _4609,
        _4610,
        _4612,
    )

    Self = TypeVar("Self", bound="PartCompoundPowerFlow")
    CastSelf = TypeVar(
        "CastSelf", bound="PartCompoundPowerFlow._Cast_PartCompoundPowerFlow"
    )


__docformat__ = "restructuredtext en"
__all__ = ("PartCompoundPowerFlow",)


@extended_dataclass(frozen=True, slots=True, weakref_slot=True)
class _Cast_PartCompoundPowerFlow:
    """Special nested class for casting PartCompoundPowerFlow to subclasses."""

    __parent__: "PartCompoundPowerFlow"

    @property
    def part_compound_analysis(self: "CastSelf") -> "_7942.PartCompoundAnalysis":
        return self.__parent__._cast(_7942.PartCompoundAnalysis)

    @property
    def design_entity_compound_analysis(
        self: "CastSelf",
    ) -> "_7939.DesignEntityCompoundAnalysis":
        from mastapy._private.system_model.analyses_and_results.analysis_cases import (
            _7939,
        )

        return self.__parent__._cast(_7939.DesignEntityCompoundAnalysis)

    @property
    def design_entity_analysis(self: "CastSelf") -> "_2943.DesignEntityAnalysis":
        from mastapy._private.system_model.analyses_and_results import _2943

        return self.__parent__._cast(_2943.DesignEntityAnalysis)

    @property
    def abstract_assembly_compound_power_flow(
        self: "CastSelf",
    ) -> "_4482.AbstractAssemblyCompoundPowerFlow":
        from mastapy._private.system_model.analyses_and_results.power_flows.compound import (
            _4482,
        )

        return self.__parent__._cast(_4482.AbstractAssemblyCompoundPowerFlow)

    @property
    def abstract_shaft_compound_power_flow(
        self: "CastSelf",
    ) -> "_4483.AbstractShaftCompoundPowerFlow":
        from mastapy._private.system_model.analyses_and_results.power_flows.compound import (
            _4483,
        )

        return self.__parent__._cast(_4483.AbstractShaftCompoundPowerFlow)

    @property
    def abstract_shaft_or_housing_compound_power_flow(
        self: "CastSelf",
    ) -> "_4484.AbstractShaftOrHousingCompoundPowerFlow":
        from mastapy._private.system_model.analyses_and_results.power_flows.compound import (
            _4484,
        )

        return self.__parent__._cast(_4484.AbstractShaftOrHousingCompoundPowerFlow)

    @property
    def agma_gleason_conical_gear_compound_power_flow(
        self: "CastSelf",
    ) -> "_4486.AGMAGleasonConicalGearCompoundPowerFlow":
        from mastapy._private.system_model.analyses_and_results.power_flows.compound import (
            _4486,
        )

        return self.__parent__._cast(_4486.AGMAGleasonConicalGearCompoundPowerFlow)

    @property
    def agma_gleason_conical_gear_set_compound_power_flow(
        self: "CastSelf",
    ) -> "_4488.AGMAGleasonConicalGearSetCompoundPowerFlow":
        from mastapy._private.system_model.analyses_and_results.power_flows.compound import (
            _4488,
        )

        return self.__parent__._cast(_4488.AGMAGleasonConicalGearSetCompoundPowerFlow)

    @property
    def assembly_compound_power_flow(
        self: "CastSelf",
    ) -> "_4489.AssemblyCompoundPowerFlow":
        from mastapy._private.system_model.analyses_and_results.power_flows.compound import (
            _4489,
        )

        return self.__parent__._cast(_4489.AssemblyCompoundPowerFlow)

    @property
    def bearing_compound_power_flow(
        self: "CastSelf",
    ) -> "_4490.BearingCompoundPowerFlow":
        from mastapy._private.system_model.analyses_and_results.power_flows.compound import (
            _4490,
        )

        return self.__parent__._cast(_4490.BearingCompoundPowerFlow)

    @property
    def belt_drive_compound_power_flow(
        self: "CastSelf",
    ) -> "_4492.BeltDriveCompoundPowerFlow":
        from mastapy._private.system_model.analyses_and_results.power_flows.compound import (
            _4492,
        )

        return self.__parent__._cast(_4492.BeltDriveCompoundPowerFlow)

    @property
    def bevel_differential_gear_compound_power_flow(
        self: "CastSelf",
    ) -> "_4493.BevelDifferentialGearCompoundPowerFlow":
        from mastapy._private.system_model.analyses_and_results.power_flows.compound import (
            _4493,
        )

        return self.__parent__._cast(_4493.BevelDifferentialGearCompoundPowerFlow)

    @property
    def bevel_differential_gear_set_compound_power_flow(
        self: "CastSelf",
    ) -> "_4495.BevelDifferentialGearSetCompoundPowerFlow":
        from mastapy._private.system_model.analyses_and_results.power_flows.compound import (
            _4495,
        )

        return self.__parent__._cast(_4495.BevelDifferentialGearSetCompoundPowerFlow)

    @property
    def bevel_differential_planet_gear_compound_power_flow(
        self: "CastSelf",
    ) -> "_4496.BevelDifferentialPlanetGearCompoundPowerFlow":
        from mastapy._private.system_model.analyses_and_results.power_flows.compound import (
            _4496,
        )

        return self.__parent__._cast(_4496.BevelDifferentialPlanetGearCompoundPowerFlow)

    @property
    def bevel_differential_sun_gear_compound_power_flow(
        self: "CastSelf",
    ) -> "_4497.BevelDifferentialSunGearCompoundPowerFlow":
        from mastapy._private.system_model.analyses_and_results.power_flows.compound import (
            _4497,
        )

        return self.__parent__._cast(_4497.BevelDifferentialSunGearCompoundPowerFlow)

    @property
    def bevel_gear_compound_power_flow(
        self: "CastSelf",
    ) -> "_4498.BevelGearCompoundPowerFlow":
        from mastapy._private.system_model.analyses_and_results.power_flows.compound import (
            _4498,
        )

        return self.__parent__._cast(_4498.BevelGearCompoundPowerFlow)

    @property
    def bevel_gear_set_compound_power_flow(
        self: "CastSelf",
    ) -> "_4500.BevelGearSetCompoundPowerFlow":
        from mastapy._private.system_model.analyses_and_results.power_flows.compound import (
            _4500,
        )

        return self.__parent__._cast(_4500.BevelGearSetCompoundPowerFlow)

    @property
    def bolt_compound_power_flow(self: "CastSelf") -> "_4501.BoltCompoundPowerFlow":
        from mastapy._private.system_model.analyses_and_results.power_flows.compound import (
            _4501,
        )

        return self.__parent__._cast(_4501.BoltCompoundPowerFlow)

    @property
    def bolted_joint_compound_power_flow(
        self: "CastSelf",
    ) -> "_4502.BoltedJointCompoundPowerFlow":
        from mastapy._private.system_model.analyses_and_results.power_flows.compound import (
            _4502,
        )

        return self.__parent__._cast(_4502.BoltedJointCompoundPowerFlow)

    @property
    def clutch_compound_power_flow(self: "CastSelf") -> "_4503.ClutchCompoundPowerFlow":
        from mastapy._private.system_model.analyses_and_results.power_flows.compound import (
            _4503,
        )

        return self.__parent__._cast(_4503.ClutchCompoundPowerFlow)

    @property
    def clutch_half_compound_power_flow(
        self: "CastSelf",
    ) -> "_4505.ClutchHalfCompoundPowerFlow":
        from mastapy._private.system_model.analyses_and_results.power_flows.compound import (
            _4505,
        )

        return self.__parent__._cast(_4505.ClutchHalfCompoundPowerFlow)

    @property
    def component_compound_power_flow(
        self: "CastSelf",
    ) -> "_4507.ComponentCompoundPowerFlow":
        from mastapy._private.system_model.analyses_and_results.power_flows.compound import (
            _4507,
        )

        return self.__parent__._cast(_4507.ComponentCompoundPowerFlow)

    @property
    def concept_coupling_compound_power_flow(
        self: "CastSelf",
    ) -> "_4508.ConceptCouplingCompoundPowerFlow":
        from mastapy._private.system_model.analyses_and_results.power_flows.compound import (
            _4508,
        )

        return self.__parent__._cast(_4508.ConceptCouplingCompoundPowerFlow)

    @property
    def concept_coupling_half_compound_power_flow(
        self: "CastSelf",
    ) -> "_4510.ConceptCouplingHalfCompoundPowerFlow":
        from mastapy._private.system_model.analyses_and_results.power_flows.compound import (
            _4510,
        )

        return self.__parent__._cast(_4510.ConceptCouplingHalfCompoundPowerFlow)

    @property
    def concept_gear_compound_power_flow(
        self: "CastSelf",
    ) -> "_4511.ConceptGearCompoundPowerFlow":
        from mastapy._private.system_model.analyses_and_results.power_flows.compound import (
            _4511,
        )

        return self.__parent__._cast(_4511.ConceptGearCompoundPowerFlow)

    @property
    def concept_gear_set_compound_power_flow(
        self: "CastSelf",
    ) -> "_4513.ConceptGearSetCompoundPowerFlow":
        from mastapy._private.system_model.analyses_and_results.power_flows.compound import (
            _4513,
        )

        return self.__parent__._cast(_4513.ConceptGearSetCompoundPowerFlow)

    @property
    def conical_gear_compound_power_flow(
        self: "CastSelf",
    ) -> "_4514.ConicalGearCompoundPowerFlow":
        from mastapy._private.system_model.analyses_and_results.power_flows.compound import (
            _4514,
        )

        return self.__parent__._cast(_4514.ConicalGearCompoundPowerFlow)

    @property
    def conical_gear_set_compound_power_flow(
        self: "CastSelf",
    ) -> "_4516.ConicalGearSetCompoundPowerFlow":
        from mastapy._private.system_model.analyses_and_results.power_flows.compound import (
            _4516,
        )

        return self.__parent__._cast(_4516.ConicalGearSetCompoundPowerFlow)

    @property
    def connector_compound_power_flow(
        self: "CastSelf",
    ) -> "_4518.ConnectorCompoundPowerFlow":
        from mastapy._private.system_model.analyses_and_results.power_flows.compound import (
            _4518,
        )

        return self.__parent__._cast(_4518.ConnectorCompoundPowerFlow)

    @property
    def coupling_compound_power_flow(
        self: "CastSelf",
    ) -> "_4519.CouplingCompoundPowerFlow":
        from mastapy._private.system_model.analyses_and_results.power_flows.compound import (
            _4519,
        )

        return self.__parent__._cast(_4519.CouplingCompoundPowerFlow)

    @property
    def coupling_half_compound_power_flow(
        self: "CastSelf",
    ) -> "_4521.CouplingHalfCompoundPowerFlow":
        from mastapy._private.system_model.analyses_and_results.power_flows.compound import (
            _4521,
        )

        return self.__parent__._cast(_4521.CouplingHalfCompoundPowerFlow)

    @property
    def cvt_compound_power_flow(self: "CastSelf") -> "_4523.CVTCompoundPowerFlow":
        from mastapy._private.system_model.analyses_and_results.power_flows.compound import (
            _4523,
        )

        return self.__parent__._cast(_4523.CVTCompoundPowerFlow)

    @property
    def cvt_pulley_compound_power_flow(
        self: "CastSelf",
    ) -> "_4524.CVTPulleyCompoundPowerFlow":
        from mastapy._private.system_model.analyses_and_results.power_flows.compound import (
            _4524,
        )

        return self.__parent__._cast(_4524.CVTPulleyCompoundPowerFlow)

    @property
    def cycloidal_assembly_compound_power_flow(
        self: "CastSelf",
    ) -> "_4525.CycloidalAssemblyCompoundPowerFlow":
        from mastapy._private.system_model.analyses_and_results.power_flows.compound import (
            _4525,
        )

        return self.__parent__._cast(_4525.CycloidalAssemblyCompoundPowerFlow)

    @property
    def cycloidal_disc_compound_power_flow(
        self: "CastSelf",
    ) -> "_4527.CycloidalDiscCompoundPowerFlow":
        from mastapy._private.system_model.analyses_and_results.power_flows.compound import (
            _4527,
        )

        return self.__parent__._cast(_4527.CycloidalDiscCompoundPowerFlow)

    @property
    def cylindrical_gear_compound_power_flow(
        self: "CastSelf",
    ) -> "_4529.CylindricalGearCompoundPowerFlow":
        from mastapy._private.system_model.analyses_and_results.power_flows.compound import (
            _4529,
        )

        return self.__parent__._cast(_4529.CylindricalGearCompoundPowerFlow)

    @property
    def cylindrical_gear_set_compound_power_flow(
        self: "CastSelf",
    ) -> "_4531.CylindricalGearSetCompoundPowerFlow":
        from mastapy._private.system_model.analyses_and_results.power_flows.compound import (
            _4531,
        )

        return self.__parent__._cast(_4531.CylindricalGearSetCompoundPowerFlow)

    @property
    def cylindrical_planet_gear_compound_power_flow(
        self: "CastSelf",
    ) -> "_4532.CylindricalPlanetGearCompoundPowerFlow":
        from mastapy._private.system_model.analyses_and_results.power_flows.compound import (
            _4532,
        )

        return self.__parent__._cast(_4532.CylindricalPlanetGearCompoundPowerFlow)

    @property
    def datum_compound_power_flow(self: "CastSelf") -> "_4533.DatumCompoundPowerFlow":
        from mastapy._private.system_model.analyses_and_results.power_flows.compound import (
            _4533,
        )

        return self.__parent__._cast(_4533.DatumCompoundPowerFlow)

    @property
    def external_cad_model_compound_power_flow(
        self: "CastSelf",
    ) -> "_4534.ExternalCADModelCompoundPowerFlow":
        from mastapy._private.system_model.analyses_and_results.power_flows.compound import (
            _4534,
        )

        return self.__parent__._cast(_4534.ExternalCADModelCompoundPowerFlow)

    @property
    def face_gear_compound_power_flow(
        self: "CastSelf",
    ) -> "_4535.FaceGearCompoundPowerFlow":
        from mastapy._private.system_model.analyses_and_results.power_flows.compound import (
            _4535,
        )

        return self.__parent__._cast(_4535.FaceGearCompoundPowerFlow)

    @property
    def face_gear_set_compound_power_flow(
        self: "CastSelf",
    ) -> "_4537.FaceGearSetCompoundPowerFlow":
        from mastapy._private.system_model.analyses_and_results.power_flows.compound import (
            _4537,
        )

        return self.__parent__._cast(_4537.FaceGearSetCompoundPowerFlow)

    @property
    def fe_part_compound_power_flow(
        self: "CastSelf",
    ) -> "_4538.FEPartCompoundPowerFlow":
        from mastapy._private.system_model.analyses_and_results.power_flows.compound import (
            _4538,
        )

        return self.__parent__._cast(_4538.FEPartCompoundPowerFlow)

    @property
    def flexible_pin_assembly_compound_power_flow(
        self: "CastSelf",
    ) -> "_4539.FlexiblePinAssemblyCompoundPowerFlow":
        from mastapy._private.system_model.analyses_and_results.power_flows.compound import (
            _4539,
        )

        return self.__parent__._cast(_4539.FlexiblePinAssemblyCompoundPowerFlow)

    @property
    def gear_compound_power_flow(self: "CastSelf") -> "_4540.GearCompoundPowerFlow":
        from mastapy._private.system_model.analyses_and_results.power_flows.compound import (
            _4540,
        )

        return self.__parent__._cast(_4540.GearCompoundPowerFlow)

    @property
    def gear_set_compound_power_flow(
        self: "CastSelf",
    ) -> "_4542.GearSetCompoundPowerFlow":
        from mastapy._private.system_model.analyses_and_results.power_flows.compound import (
            _4542,
        )

        return self.__parent__._cast(_4542.GearSetCompoundPowerFlow)

    @property
    def guide_dxf_model_compound_power_flow(
        self: "CastSelf",
    ) -> "_4543.GuideDxfModelCompoundPowerFlow":
        from mastapy._private.system_model.analyses_and_results.power_flows.compound import (
            _4543,
        )

        return self.__parent__._cast(_4543.GuideDxfModelCompoundPowerFlow)

    @property
    def hypoid_gear_compound_power_flow(
        self: "CastSelf",
    ) -> "_4544.HypoidGearCompoundPowerFlow":
        from mastapy._private.system_model.analyses_and_results.power_flows.compound import (
            _4544,
        )

        return self.__parent__._cast(_4544.HypoidGearCompoundPowerFlow)

    @property
    def hypoid_gear_set_compound_power_flow(
        self: "CastSelf",
    ) -> "_4546.HypoidGearSetCompoundPowerFlow":
        from mastapy._private.system_model.analyses_and_results.power_flows.compound import (
            _4546,
        )

        return self.__parent__._cast(_4546.HypoidGearSetCompoundPowerFlow)

    @property
    def klingelnberg_cyclo_palloid_conical_gear_compound_power_flow(
        self: "CastSelf",
    ) -> "_4548.KlingelnbergCycloPalloidConicalGearCompoundPowerFlow":
        from mastapy._private.system_model.analyses_and_results.power_flows.compound import (
            _4548,
        )

        return self.__parent__._cast(
            _4548.KlingelnbergCycloPalloidConicalGearCompoundPowerFlow
        )

    @property
    def klingelnberg_cyclo_palloid_conical_gear_set_compound_power_flow(
        self: "CastSelf",
    ) -> "_4550.KlingelnbergCycloPalloidConicalGearSetCompoundPowerFlow":
        from mastapy._private.system_model.analyses_and_results.power_flows.compound import (
            _4550,
        )

        return self.__parent__._cast(
            _4550.KlingelnbergCycloPalloidConicalGearSetCompoundPowerFlow
        )

    @property
    def klingelnberg_cyclo_palloid_hypoid_gear_compound_power_flow(
        self: "CastSelf",
    ) -> "_4551.KlingelnbergCycloPalloidHypoidGearCompoundPowerFlow":
        from mastapy._private.system_model.analyses_and_results.power_flows.compound import (
            _4551,
        )

        return self.__parent__._cast(
            _4551.KlingelnbergCycloPalloidHypoidGearCompoundPowerFlow
        )

    @property
    def klingelnberg_cyclo_palloid_hypoid_gear_set_compound_power_flow(
        self: "CastSelf",
    ) -> "_4553.KlingelnbergCycloPalloidHypoidGearSetCompoundPowerFlow":
        from mastapy._private.system_model.analyses_and_results.power_flows.compound import (
            _4553,
        )

        return self.__parent__._cast(
            _4553.KlingelnbergCycloPalloidHypoidGearSetCompoundPowerFlow
        )

    @property
    def klingelnberg_cyclo_palloid_spiral_bevel_gear_compound_power_flow(
        self: "CastSelf",
    ) -> "_4554.KlingelnbergCycloPalloidSpiralBevelGearCompoundPowerFlow":
        from mastapy._private.system_model.analyses_and_results.power_flows.compound import (
            _4554,
        )

        return self.__parent__._cast(
            _4554.KlingelnbergCycloPalloidSpiralBevelGearCompoundPowerFlow
        )

    @property
    def klingelnberg_cyclo_palloid_spiral_bevel_gear_set_compound_power_flow(
        self: "CastSelf",
    ) -> "_4556.KlingelnbergCycloPalloidSpiralBevelGearSetCompoundPowerFlow":
        from mastapy._private.system_model.analyses_and_results.power_flows.compound import (
            _4556,
        )

        return self.__parent__._cast(
            _4556.KlingelnbergCycloPalloidSpiralBevelGearSetCompoundPowerFlow
        )

    @property
    def mass_disc_compound_power_flow(
        self: "CastSelf",
    ) -> "_4557.MassDiscCompoundPowerFlow":
        from mastapy._private.system_model.analyses_and_results.power_flows.compound import (
            _4557,
        )

        return self.__parent__._cast(_4557.MassDiscCompoundPowerFlow)

    @property
    def measurement_component_compound_power_flow(
        self: "CastSelf",
    ) -> "_4558.MeasurementComponentCompoundPowerFlow":
        from mastapy._private.system_model.analyses_and_results.power_flows.compound import (
            _4558,
        )

        return self.__parent__._cast(_4558.MeasurementComponentCompoundPowerFlow)

    @property
    def microphone_array_compound_power_flow(
        self: "CastSelf",
    ) -> "_4559.MicrophoneArrayCompoundPowerFlow":
        from mastapy._private.system_model.analyses_and_results.power_flows.compound import (
            _4559,
        )

        return self.__parent__._cast(_4559.MicrophoneArrayCompoundPowerFlow)

    @property
    def microphone_compound_power_flow(
        self: "CastSelf",
    ) -> "_4560.MicrophoneCompoundPowerFlow":
        from mastapy._private.system_model.analyses_and_results.power_flows.compound import (
            _4560,
        )

        return self.__parent__._cast(_4560.MicrophoneCompoundPowerFlow)

    @property
    def mountable_component_compound_power_flow(
        self: "CastSelf",
    ) -> "_4561.MountableComponentCompoundPowerFlow":
        from mastapy._private.system_model.analyses_and_results.power_flows.compound import (
            _4561,
        )

        return self.__parent__._cast(_4561.MountableComponentCompoundPowerFlow)

    @property
    def oil_seal_compound_power_flow(
        self: "CastSelf",
    ) -> "_4562.OilSealCompoundPowerFlow":
        from mastapy._private.system_model.analyses_and_results.power_flows.compound import (
            _4562,
        )

        return self.__parent__._cast(_4562.OilSealCompoundPowerFlow)

    @property
    def part_to_part_shear_coupling_compound_power_flow(
        self: "CastSelf",
    ) -> "_4564.PartToPartShearCouplingCompoundPowerFlow":
        from mastapy._private.system_model.analyses_and_results.power_flows.compound import (
            _4564,
        )

        return self.__parent__._cast(_4564.PartToPartShearCouplingCompoundPowerFlow)

    @property
    def part_to_part_shear_coupling_half_compound_power_flow(
        self: "CastSelf",
    ) -> "_4566.PartToPartShearCouplingHalfCompoundPowerFlow":
        from mastapy._private.system_model.analyses_and_results.power_flows.compound import (
            _4566,
        )

        return self.__parent__._cast(_4566.PartToPartShearCouplingHalfCompoundPowerFlow)

    @property
    def planetary_gear_set_compound_power_flow(
        self: "CastSelf",
    ) -> "_4568.PlanetaryGearSetCompoundPowerFlow":
        from mastapy._private.system_model.analyses_and_results.power_flows.compound import (
            _4568,
        )

        return self.__parent__._cast(_4568.PlanetaryGearSetCompoundPowerFlow)

    @property
    def planet_carrier_compound_power_flow(
        self: "CastSelf",
    ) -> "_4569.PlanetCarrierCompoundPowerFlow":
        from mastapy._private.system_model.analyses_and_results.power_flows.compound import (
            _4569,
        )

        return self.__parent__._cast(_4569.PlanetCarrierCompoundPowerFlow)

    @property
    def point_load_compound_power_flow(
        self: "CastSelf",
    ) -> "_4570.PointLoadCompoundPowerFlow":
        from mastapy._private.system_model.analyses_and_results.power_flows.compound import (
            _4570,
        )

        return self.__parent__._cast(_4570.PointLoadCompoundPowerFlow)

    @property
    def power_load_compound_power_flow(
        self: "CastSelf",
    ) -> "_4571.PowerLoadCompoundPowerFlow":
        from mastapy._private.system_model.analyses_and_results.power_flows.compound import (
            _4571,
        )

        return self.__parent__._cast(_4571.PowerLoadCompoundPowerFlow)

    @property
    def pulley_compound_power_flow(self: "CastSelf") -> "_4572.PulleyCompoundPowerFlow":
        from mastapy._private.system_model.analyses_and_results.power_flows.compound import (
            _4572,
        )

        return self.__parent__._cast(_4572.PulleyCompoundPowerFlow)

    @property
    def ring_pins_compound_power_flow(
        self: "CastSelf",
    ) -> "_4573.RingPinsCompoundPowerFlow":
        from mastapy._private.system_model.analyses_and_results.power_flows.compound import (
            _4573,
        )

        return self.__parent__._cast(_4573.RingPinsCompoundPowerFlow)

    @property
    def rolling_ring_assembly_compound_power_flow(
        self: "CastSelf",
    ) -> "_4575.RollingRingAssemblyCompoundPowerFlow":
        from mastapy._private.system_model.analyses_and_results.power_flows.compound import (
            _4575,
        )

        return self.__parent__._cast(_4575.RollingRingAssemblyCompoundPowerFlow)

    @property
    def rolling_ring_compound_power_flow(
        self: "CastSelf",
    ) -> "_4576.RollingRingCompoundPowerFlow":
        from mastapy._private.system_model.analyses_and_results.power_flows.compound import (
            _4576,
        )

        return self.__parent__._cast(_4576.RollingRingCompoundPowerFlow)

    @property
    def root_assembly_compound_power_flow(
        self: "CastSelf",
    ) -> "_4578.RootAssemblyCompoundPowerFlow":
        from mastapy._private.system_model.analyses_and_results.power_flows.compound import (
            _4578,
        )

        return self.__parent__._cast(_4578.RootAssemblyCompoundPowerFlow)

    @property
    def shaft_compound_power_flow(self: "CastSelf") -> "_4579.ShaftCompoundPowerFlow":
        from mastapy._private.system_model.analyses_and_results.power_flows.compound import (
            _4579,
        )

        return self.__parent__._cast(_4579.ShaftCompoundPowerFlow)

    @property
    def shaft_hub_connection_compound_power_flow(
        self: "CastSelf",
    ) -> "_4580.ShaftHubConnectionCompoundPowerFlow":
        from mastapy._private.system_model.analyses_and_results.power_flows.compound import (
            _4580,
        )

        return self.__parent__._cast(_4580.ShaftHubConnectionCompoundPowerFlow)

    @property
    def specialised_assembly_compound_power_flow(
        self: "CastSelf",
    ) -> "_4582.SpecialisedAssemblyCompoundPowerFlow":
        from mastapy._private.system_model.analyses_and_results.power_flows.compound import (
            _4582,
        )

        return self.__parent__._cast(_4582.SpecialisedAssemblyCompoundPowerFlow)

    @property
    def spiral_bevel_gear_compound_power_flow(
        self: "CastSelf",
    ) -> "_4583.SpiralBevelGearCompoundPowerFlow":
        from mastapy._private.system_model.analyses_and_results.power_flows.compound import (
            _4583,
        )

        return self.__parent__._cast(_4583.SpiralBevelGearCompoundPowerFlow)

    @property
    def spiral_bevel_gear_set_compound_power_flow(
        self: "CastSelf",
    ) -> "_4585.SpiralBevelGearSetCompoundPowerFlow":
        from mastapy._private.system_model.analyses_and_results.power_flows.compound import (
            _4585,
        )

        return self.__parent__._cast(_4585.SpiralBevelGearSetCompoundPowerFlow)

    @property
    def spring_damper_compound_power_flow(
        self: "CastSelf",
    ) -> "_4586.SpringDamperCompoundPowerFlow":
        from mastapy._private.system_model.analyses_and_results.power_flows.compound import (
            _4586,
        )

        return self.__parent__._cast(_4586.SpringDamperCompoundPowerFlow)

    @property
    def spring_damper_half_compound_power_flow(
        self: "CastSelf",
    ) -> "_4588.SpringDamperHalfCompoundPowerFlow":
        from mastapy._private.system_model.analyses_and_results.power_flows.compound import (
            _4588,
        )

        return self.__parent__._cast(_4588.SpringDamperHalfCompoundPowerFlow)

    @property
    def straight_bevel_diff_gear_compound_power_flow(
        self: "CastSelf",
    ) -> "_4589.StraightBevelDiffGearCompoundPowerFlow":
        from mastapy._private.system_model.analyses_and_results.power_flows.compound import (
            _4589,
        )

        return self.__parent__._cast(_4589.StraightBevelDiffGearCompoundPowerFlow)

    @property
    def straight_bevel_diff_gear_set_compound_power_flow(
        self: "CastSelf",
    ) -> "_4591.StraightBevelDiffGearSetCompoundPowerFlow":
        from mastapy._private.system_model.analyses_and_results.power_flows.compound import (
            _4591,
        )

        return self.__parent__._cast(_4591.StraightBevelDiffGearSetCompoundPowerFlow)

    @property
    def straight_bevel_gear_compound_power_flow(
        self: "CastSelf",
    ) -> "_4592.StraightBevelGearCompoundPowerFlow":
        from mastapy._private.system_model.analyses_and_results.power_flows.compound import (
            _4592,
        )

        return self.__parent__._cast(_4592.StraightBevelGearCompoundPowerFlow)

    @property
    def straight_bevel_gear_set_compound_power_flow(
        self: "CastSelf",
    ) -> "_4594.StraightBevelGearSetCompoundPowerFlow":
        from mastapy._private.system_model.analyses_and_results.power_flows.compound import (
            _4594,
        )

        return self.__parent__._cast(_4594.StraightBevelGearSetCompoundPowerFlow)

    @property
    def straight_bevel_planet_gear_compound_power_flow(
        self: "CastSelf",
    ) -> "_4595.StraightBevelPlanetGearCompoundPowerFlow":
        from mastapy._private.system_model.analyses_and_results.power_flows.compound import (
            _4595,
        )

        return self.__parent__._cast(_4595.StraightBevelPlanetGearCompoundPowerFlow)

    @property
    def straight_bevel_sun_gear_compound_power_flow(
        self: "CastSelf",
    ) -> "_4596.StraightBevelSunGearCompoundPowerFlow":
        from mastapy._private.system_model.analyses_and_results.power_flows.compound import (
            _4596,
        )

        return self.__parent__._cast(_4596.StraightBevelSunGearCompoundPowerFlow)

    @property
    def synchroniser_compound_power_flow(
        self: "CastSelf",
    ) -> "_4597.SynchroniserCompoundPowerFlow":
        from mastapy._private.system_model.analyses_and_results.power_flows.compound import (
            _4597,
        )

        return self.__parent__._cast(_4597.SynchroniserCompoundPowerFlow)

    @property
    def synchroniser_half_compound_power_flow(
        self: "CastSelf",
    ) -> "_4598.SynchroniserHalfCompoundPowerFlow":
        from mastapy._private.system_model.analyses_and_results.power_flows.compound import (
            _4598,
        )

        return self.__parent__._cast(_4598.SynchroniserHalfCompoundPowerFlow)

    @property
    def synchroniser_part_compound_power_flow(
        self: "CastSelf",
    ) -> "_4599.SynchroniserPartCompoundPowerFlow":
        from mastapy._private.system_model.analyses_and_results.power_flows.compound import (
            _4599,
        )

        return self.__parent__._cast(_4599.SynchroniserPartCompoundPowerFlow)

    @property
    def synchroniser_sleeve_compound_power_flow(
        self: "CastSelf",
    ) -> "_4600.SynchroniserSleeveCompoundPowerFlow":
        from mastapy._private.system_model.analyses_and_results.power_flows.compound import (
            _4600,
        )

        return self.__parent__._cast(_4600.SynchroniserSleeveCompoundPowerFlow)

    @property
    def torque_converter_compound_power_flow(
        self: "CastSelf",
    ) -> "_4601.TorqueConverterCompoundPowerFlow":
        from mastapy._private.system_model.analyses_and_results.power_flows.compound import (
            _4601,
        )

        return self.__parent__._cast(_4601.TorqueConverterCompoundPowerFlow)

    @property
    def torque_converter_pump_compound_power_flow(
        self: "CastSelf",
    ) -> "_4603.TorqueConverterPumpCompoundPowerFlow":
        from mastapy._private.system_model.analyses_and_results.power_flows.compound import (
            _4603,
        )

        return self.__parent__._cast(_4603.TorqueConverterPumpCompoundPowerFlow)

    @property
    def torque_converter_turbine_compound_power_flow(
        self: "CastSelf",
    ) -> "_4604.TorqueConverterTurbineCompoundPowerFlow":
        from mastapy._private.system_model.analyses_and_results.power_flows.compound import (
            _4604,
        )

        return self.__parent__._cast(_4604.TorqueConverterTurbineCompoundPowerFlow)

    @property
    def unbalanced_mass_compound_power_flow(
        self: "CastSelf",
    ) -> "_4605.UnbalancedMassCompoundPowerFlow":
        from mastapy._private.system_model.analyses_and_results.power_flows.compound import (
            _4605,
        )

        return self.__parent__._cast(_4605.UnbalancedMassCompoundPowerFlow)

    @property
    def virtual_component_compound_power_flow(
        self: "CastSelf",
    ) -> "_4606.VirtualComponentCompoundPowerFlow":
        from mastapy._private.system_model.analyses_and_results.power_flows.compound import (
            _4606,
        )

        return self.__parent__._cast(_4606.VirtualComponentCompoundPowerFlow)

    @property
    def worm_gear_compound_power_flow(
        self: "CastSelf",
    ) -> "_4607.WormGearCompoundPowerFlow":
        from mastapy._private.system_model.analyses_and_results.power_flows.compound import (
            _4607,
        )

        return self.__parent__._cast(_4607.WormGearCompoundPowerFlow)

    @property
    def worm_gear_set_compound_power_flow(
        self: "CastSelf",
    ) -> "_4609.WormGearSetCompoundPowerFlow":
        from mastapy._private.system_model.analyses_and_results.power_flows.compound import (
            _4609,
        )

        return self.__parent__._cast(_4609.WormGearSetCompoundPowerFlow)

    @property
    def zerol_bevel_gear_compound_power_flow(
        self: "CastSelf",
    ) -> "_4610.ZerolBevelGearCompoundPowerFlow":
        from mastapy._private.system_model.analyses_and_results.power_flows.compound import (
            _4610,
        )

        return self.__parent__._cast(_4610.ZerolBevelGearCompoundPowerFlow)

    @property
    def zerol_bevel_gear_set_compound_power_flow(
        self: "CastSelf",
    ) -> "_4612.ZerolBevelGearSetCompoundPowerFlow":
        from mastapy._private.system_model.analyses_and_results.power_flows.compound import (
            _4612,
        )

        return self.__parent__._cast(_4612.ZerolBevelGearSetCompoundPowerFlow)

    @property
    def part_compound_power_flow(self: "CastSelf") -> "PartCompoundPowerFlow":
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
class PartCompoundPowerFlow(_7942.PartCompoundAnalysis):
    """PartCompoundPowerFlow

    This is a mastapy class.
    """

    TYPE: ClassVar["Type"] = _PART_COMPOUND_POWER_FLOW

    wrapped: "Any"

    def __post_init__(self: "Self") -> None:
        """Override of the post initialisation magic method."""
        if not hasattr(self.wrapped, "reference_count"):
            self.wrapped.reference_count = 0

        self.wrapped.reference_count += 1

    @property
    @exception_bridge
    def component_analysis_cases(self: "Self") -> "List[_4429.PartPowerFlow]":
        """List[mastapy.system_model.analyses_and_results.power_flows.PartPowerFlow]

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "ComponentAnalysisCases")

        if temp is None:
            return None

        value = conversion.pn_to_mp_objects_in_list(temp)

        if value is None:
            return None

        return value

    @property
    @exception_bridge
    def component_analysis_cases_ready(self: "Self") -> "List[_4429.PartPowerFlow]":
        """List[mastapy.system_model.analyses_and_results.power_flows.PartPowerFlow]

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "ComponentAnalysisCasesReady")

        if temp is None:
            return None

        value = conversion.pn_to_mp_objects_in_list(temp)

        if value is None:
            return None

        return value

    @property
    def cast_to(self: "Self") -> "_Cast_PartCompoundPowerFlow":
        """Cast to another type.

        Returns:
            _Cast_PartCompoundPowerFlow
        """
        return _Cast_PartCompoundPowerFlow(self)
