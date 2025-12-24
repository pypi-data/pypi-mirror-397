"""PartTimeSeriesLoadAnalysisCase"""

from __future__ import annotations

from typing import TYPE_CHECKING, ClassVar

from mastapy._private._internal.dataclasses import extended_dataclass
from mastapy._private._internal.exceptions import CastException
from mastapy._private._internal.python_net import python_net_import

from mastapy._private._internal import utility
from mastapy._private.system_model.analyses_and_results.analysis_cases import _7941

_PART_TIME_SERIES_LOAD_ANALYSIS_CASE = python_net_import(
    "SMT.MastaAPI.SystemModel.AnalysesAndResults.AnalysisCases",
    "PartTimeSeriesLoadAnalysisCase",
)

if TYPE_CHECKING:
    from typing import Any, Type, TypeVar

    from mastapy._private.system_model.analyses_and_results import _2943, _2945, _2949
    from mastapy._private.system_model.analyses_and_results.mbd_analyses import (
        _5711,
        _5712,
        _5713,
        _5716,
        _5717,
        _5719,
        _5721,
        _5724,
        _5726,
        _5727,
        _5728,
        _5729,
        _5731,
        _5732,
        _5733,
        _5734,
        _5736,
        _5737,
        _5740,
        _5742,
        _5743,
        _5745,
        _5746,
        _5748,
        _5749,
        _5751,
        _5753,
        _5754,
        _5756,
        _5757,
        _5758,
        _5760,
        _5763,
        _5764,
        _5765,
        _5766,
        _5767,
        _5769,
        _5770,
        _5771,
        _5772,
        _5775,
        _5776,
        _5777,
        _5779,
        _5780,
        _5787,
        _5788,
        _5790,
        _5791,
        _5793,
        _5794,
        _5795,
        _5799,
        _5800,
        _5801,
        _5802,
        _5804,
        _5805,
        _5807,
        _5808,
        _5810,
        _5811,
        _5812,
        _5813,
        _5814,
        _5815,
        _5817,
        _5819,
        _5820,
        _5823,
        _5824,
        _5827,
        _5829,
        _5830,
        _5833,
        _5834,
        _5836,
        _5837,
        _5839,
        _5840,
        _5841,
        _5842,
        _5843,
        _5844,
        _5845,
        _5846,
        _5849,
        _5850,
        _5852,
        _5853,
        _5854,
        _5857,
        _5858,
        _5860,
        _5861,
    )

    Self = TypeVar("Self", bound="PartTimeSeriesLoadAnalysisCase")
    CastSelf = TypeVar(
        "CastSelf",
        bound="PartTimeSeriesLoadAnalysisCase._Cast_PartTimeSeriesLoadAnalysisCase",
    )


__docformat__ = "restructuredtext en"
__all__ = ("PartTimeSeriesLoadAnalysisCase",)


@extended_dataclass(frozen=True, slots=True, weakref_slot=True)
class _Cast_PartTimeSeriesLoadAnalysisCase:
    """Special nested class for casting PartTimeSeriesLoadAnalysisCase to subclasses."""

    __parent__: "PartTimeSeriesLoadAnalysisCase"

    @property
    def part_analysis_case(self: "CastSelf") -> "_7941.PartAnalysisCase":
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
    def abstract_assembly_multibody_dynamics_analysis(
        self: "CastSelf",
    ) -> "_5711.AbstractAssemblyMultibodyDynamicsAnalysis":
        from mastapy._private.system_model.analyses_and_results.mbd_analyses import (
            _5711,
        )

        return self.__parent__._cast(_5711.AbstractAssemblyMultibodyDynamicsAnalysis)

    @property
    def abstract_shaft_multibody_dynamics_analysis(
        self: "CastSelf",
    ) -> "_5712.AbstractShaftMultibodyDynamicsAnalysis":
        from mastapy._private.system_model.analyses_and_results.mbd_analyses import (
            _5712,
        )

        return self.__parent__._cast(_5712.AbstractShaftMultibodyDynamicsAnalysis)

    @property
    def abstract_shaft_or_housing_multibody_dynamics_analysis(
        self: "CastSelf",
    ) -> "_5713.AbstractShaftOrHousingMultibodyDynamicsAnalysis":
        from mastapy._private.system_model.analyses_and_results.mbd_analyses import (
            _5713,
        )

        return self.__parent__._cast(
            _5713.AbstractShaftOrHousingMultibodyDynamicsAnalysis
        )

    @property
    def agma_gleason_conical_gear_multibody_dynamics_analysis(
        self: "CastSelf",
    ) -> "_5716.AGMAGleasonConicalGearMultibodyDynamicsAnalysis":
        from mastapy._private.system_model.analyses_and_results.mbd_analyses import (
            _5716,
        )

        return self.__parent__._cast(
            _5716.AGMAGleasonConicalGearMultibodyDynamicsAnalysis
        )

    @property
    def agma_gleason_conical_gear_set_multibody_dynamics_analysis(
        self: "CastSelf",
    ) -> "_5717.AGMAGleasonConicalGearSetMultibodyDynamicsAnalysis":
        from mastapy._private.system_model.analyses_and_results.mbd_analyses import (
            _5717,
        )

        return self.__parent__._cast(
            _5717.AGMAGleasonConicalGearSetMultibodyDynamicsAnalysis
        )

    @property
    def assembly_multibody_dynamics_analysis(
        self: "CastSelf",
    ) -> "_5719.AssemblyMultibodyDynamicsAnalysis":
        from mastapy._private.system_model.analyses_and_results.mbd_analyses import (
            _5719,
        )

        return self.__parent__._cast(_5719.AssemblyMultibodyDynamicsAnalysis)

    @property
    def bearing_multibody_dynamics_analysis(
        self: "CastSelf",
    ) -> "_5721.BearingMultibodyDynamicsAnalysis":
        from mastapy._private.system_model.analyses_and_results.mbd_analyses import (
            _5721,
        )

        return self.__parent__._cast(_5721.BearingMultibodyDynamicsAnalysis)

    @property
    def belt_drive_multibody_dynamics_analysis(
        self: "CastSelf",
    ) -> "_5724.BeltDriveMultibodyDynamicsAnalysis":
        from mastapy._private.system_model.analyses_and_results.mbd_analyses import (
            _5724,
        )

        return self.__parent__._cast(_5724.BeltDriveMultibodyDynamicsAnalysis)

    @property
    def bevel_differential_gear_multibody_dynamics_analysis(
        self: "CastSelf",
    ) -> "_5726.BevelDifferentialGearMultibodyDynamicsAnalysis":
        from mastapy._private.system_model.analyses_and_results.mbd_analyses import (
            _5726,
        )

        return self.__parent__._cast(
            _5726.BevelDifferentialGearMultibodyDynamicsAnalysis
        )

    @property
    def bevel_differential_gear_set_multibody_dynamics_analysis(
        self: "CastSelf",
    ) -> "_5727.BevelDifferentialGearSetMultibodyDynamicsAnalysis":
        from mastapy._private.system_model.analyses_and_results.mbd_analyses import (
            _5727,
        )

        return self.__parent__._cast(
            _5727.BevelDifferentialGearSetMultibodyDynamicsAnalysis
        )

    @property
    def bevel_differential_planet_gear_multibody_dynamics_analysis(
        self: "CastSelf",
    ) -> "_5728.BevelDifferentialPlanetGearMultibodyDynamicsAnalysis":
        from mastapy._private.system_model.analyses_and_results.mbd_analyses import (
            _5728,
        )

        return self.__parent__._cast(
            _5728.BevelDifferentialPlanetGearMultibodyDynamicsAnalysis
        )

    @property
    def bevel_differential_sun_gear_multibody_dynamics_analysis(
        self: "CastSelf",
    ) -> "_5729.BevelDifferentialSunGearMultibodyDynamicsAnalysis":
        from mastapy._private.system_model.analyses_and_results.mbd_analyses import (
            _5729,
        )

        return self.__parent__._cast(
            _5729.BevelDifferentialSunGearMultibodyDynamicsAnalysis
        )

    @property
    def bevel_gear_multibody_dynamics_analysis(
        self: "CastSelf",
    ) -> "_5731.BevelGearMultibodyDynamicsAnalysis":
        from mastapy._private.system_model.analyses_and_results.mbd_analyses import (
            _5731,
        )

        return self.__parent__._cast(_5731.BevelGearMultibodyDynamicsAnalysis)

    @property
    def bevel_gear_set_multibody_dynamics_analysis(
        self: "CastSelf",
    ) -> "_5732.BevelGearSetMultibodyDynamicsAnalysis":
        from mastapy._private.system_model.analyses_and_results.mbd_analyses import (
            _5732,
        )

        return self.__parent__._cast(_5732.BevelGearSetMultibodyDynamicsAnalysis)

    @property
    def bolted_joint_multibody_dynamics_analysis(
        self: "CastSelf",
    ) -> "_5733.BoltedJointMultibodyDynamicsAnalysis":
        from mastapy._private.system_model.analyses_and_results.mbd_analyses import (
            _5733,
        )

        return self.__parent__._cast(_5733.BoltedJointMultibodyDynamicsAnalysis)

    @property
    def bolt_multibody_dynamics_analysis(
        self: "CastSelf",
    ) -> "_5734.BoltMultibodyDynamicsAnalysis":
        from mastapy._private.system_model.analyses_and_results.mbd_analyses import (
            _5734,
        )

        return self.__parent__._cast(_5734.BoltMultibodyDynamicsAnalysis)

    @property
    def clutch_half_multibody_dynamics_analysis(
        self: "CastSelf",
    ) -> "_5736.ClutchHalfMultibodyDynamicsAnalysis":
        from mastapy._private.system_model.analyses_and_results.mbd_analyses import (
            _5736,
        )

        return self.__parent__._cast(_5736.ClutchHalfMultibodyDynamicsAnalysis)

    @property
    def clutch_multibody_dynamics_analysis(
        self: "CastSelf",
    ) -> "_5737.ClutchMultibodyDynamicsAnalysis":
        from mastapy._private.system_model.analyses_and_results.mbd_analyses import (
            _5737,
        )

        return self.__parent__._cast(_5737.ClutchMultibodyDynamicsAnalysis)

    @property
    def component_multibody_dynamics_analysis(
        self: "CastSelf",
    ) -> "_5740.ComponentMultibodyDynamicsAnalysis":
        from mastapy._private.system_model.analyses_and_results.mbd_analyses import (
            _5740,
        )

        return self.__parent__._cast(_5740.ComponentMultibodyDynamicsAnalysis)

    @property
    def concept_coupling_half_multibody_dynamics_analysis(
        self: "CastSelf",
    ) -> "_5742.ConceptCouplingHalfMultibodyDynamicsAnalysis":
        from mastapy._private.system_model.analyses_and_results.mbd_analyses import (
            _5742,
        )

        return self.__parent__._cast(_5742.ConceptCouplingHalfMultibodyDynamicsAnalysis)

    @property
    def concept_coupling_multibody_dynamics_analysis(
        self: "CastSelf",
    ) -> "_5743.ConceptCouplingMultibodyDynamicsAnalysis":
        from mastapy._private.system_model.analyses_and_results.mbd_analyses import (
            _5743,
        )

        return self.__parent__._cast(_5743.ConceptCouplingMultibodyDynamicsAnalysis)

    @property
    def concept_gear_multibody_dynamics_analysis(
        self: "CastSelf",
    ) -> "_5745.ConceptGearMultibodyDynamicsAnalysis":
        from mastapy._private.system_model.analyses_and_results.mbd_analyses import (
            _5745,
        )

        return self.__parent__._cast(_5745.ConceptGearMultibodyDynamicsAnalysis)

    @property
    def concept_gear_set_multibody_dynamics_analysis(
        self: "CastSelf",
    ) -> "_5746.ConceptGearSetMultibodyDynamicsAnalysis":
        from mastapy._private.system_model.analyses_and_results.mbd_analyses import (
            _5746,
        )

        return self.__parent__._cast(_5746.ConceptGearSetMultibodyDynamicsAnalysis)

    @property
    def conical_gear_multibody_dynamics_analysis(
        self: "CastSelf",
    ) -> "_5748.ConicalGearMultibodyDynamicsAnalysis":
        from mastapy._private.system_model.analyses_and_results.mbd_analyses import (
            _5748,
        )

        return self.__parent__._cast(_5748.ConicalGearMultibodyDynamicsAnalysis)

    @property
    def conical_gear_set_multibody_dynamics_analysis(
        self: "CastSelf",
    ) -> "_5749.ConicalGearSetMultibodyDynamicsAnalysis":
        from mastapy._private.system_model.analyses_and_results.mbd_analyses import (
            _5749,
        )

        return self.__parent__._cast(_5749.ConicalGearSetMultibodyDynamicsAnalysis)

    @property
    def connector_multibody_dynamics_analysis(
        self: "CastSelf",
    ) -> "_5751.ConnectorMultibodyDynamicsAnalysis":
        from mastapy._private.system_model.analyses_and_results.mbd_analyses import (
            _5751,
        )

        return self.__parent__._cast(_5751.ConnectorMultibodyDynamicsAnalysis)

    @property
    def coupling_half_multibody_dynamics_analysis(
        self: "CastSelf",
    ) -> "_5753.CouplingHalfMultibodyDynamicsAnalysis":
        from mastapy._private.system_model.analyses_and_results.mbd_analyses import (
            _5753,
        )

        return self.__parent__._cast(_5753.CouplingHalfMultibodyDynamicsAnalysis)

    @property
    def coupling_multibody_dynamics_analysis(
        self: "CastSelf",
    ) -> "_5754.CouplingMultibodyDynamicsAnalysis":
        from mastapy._private.system_model.analyses_and_results.mbd_analyses import (
            _5754,
        )

        return self.__parent__._cast(_5754.CouplingMultibodyDynamicsAnalysis)

    @property
    def cvt_multibody_dynamics_analysis(
        self: "CastSelf",
    ) -> "_5756.CVTMultibodyDynamicsAnalysis":
        from mastapy._private.system_model.analyses_and_results.mbd_analyses import (
            _5756,
        )

        return self.__parent__._cast(_5756.CVTMultibodyDynamicsAnalysis)

    @property
    def cvt_pulley_multibody_dynamics_analysis(
        self: "CastSelf",
    ) -> "_5757.CVTPulleyMultibodyDynamicsAnalysis":
        from mastapy._private.system_model.analyses_and_results.mbd_analyses import (
            _5757,
        )

        return self.__parent__._cast(_5757.CVTPulleyMultibodyDynamicsAnalysis)

    @property
    def cycloidal_assembly_multibody_dynamics_analysis(
        self: "CastSelf",
    ) -> "_5758.CycloidalAssemblyMultibodyDynamicsAnalysis":
        from mastapy._private.system_model.analyses_and_results.mbd_analyses import (
            _5758,
        )

        return self.__parent__._cast(_5758.CycloidalAssemblyMultibodyDynamicsAnalysis)

    @property
    def cycloidal_disc_multibody_dynamics_analysis(
        self: "CastSelf",
    ) -> "_5760.CycloidalDiscMultibodyDynamicsAnalysis":
        from mastapy._private.system_model.analyses_and_results.mbd_analyses import (
            _5760,
        )

        return self.__parent__._cast(_5760.CycloidalDiscMultibodyDynamicsAnalysis)

    @property
    def cylindrical_gear_multibody_dynamics_analysis(
        self: "CastSelf",
    ) -> "_5763.CylindricalGearMultibodyDynamicsAnalysis":
        from mastapy._private.system_model.analyses_and_results.mbd_analyses import (
            _5763,
        )

        return self.__parent__._cast(_5763.CylindricalGearMultibodyDynamicsAnalysis)

    @property
    def cylindrical_gear_set_multibody_dynamics_analysis(
        self: "CastSelf",
    ) -> "_5764.CylindricalGearSetMultibodyDynamicsAnalysis":
        from mastapy._private.system_model.analyses_and_results.mbd_analyses import (
            _5764,
        )

        return self.__parent__._cast(_5764.CylindricalGearSetMultibodyDynamicsAnalysis)

    @property
    def cylindrical_planet_gear_multibody_dynamics_analysis(
        self: "CastSelf",
    ) -> "_5765.CylindricalPlanetGearMultibodyDynamicsAnalysis":
        from mastapy._private.system_model.analyses_and_results.mbd_analyses import (
            _5765,
        )

        return self.__parent__._cast(
            _5765.CylindricalPlanetGearMultibodyDynamicsAnalysis
        )

    @property
    def datum_multibody_dynamics_analysis(
        self: "CastSelf",
    ) -> "_5766.DatumMultibodyDynamicsAnalysis":
        from mastapy._private.system_model.analyses_and_results.mbd_analyses import (
            _5766,
        )

        return self.__parent__._cast(_5766.DatumMultibodyDynamicsAnalysis)

    @property
    def external_cad_model_multibody_dynamics_analysis(
        self: "CastSelf",
    ) -> "_5767.ExternalCADModelMultibodyDynamicsAnalysis":
        from mastapy._private.system_model.analyses_and_results.mbd_analyses import (
            _5767,
        )

        return self.__parent__._cast(_5767.ExternalCADModelMultibodyDynamicsAnalysis)

    @property
    def face_gear_multibody_dynamics_analysis(
        self: "CastSelf",
    ) -> "_5769.FaceGearMultibodyDynamicsAnalysis":
        from mastapy._private.system_model.analyses_and_results.mbd_analyses import (
            _5769,
        )

        return self.__parent__._cast(_5769.FaceGearMultibodyDynamicsAnalysis)

    @property
    def face_gear_set_multibody_dynamics_analysis(
        self: "CastSelf",
    ) -> "_5770.FaceGearSetMultibodyDynamicsAnalysis":
        from mastapy._private.system_model.analyses_and_results.mbd_analyses import (
            _5770,
        )

        return self.__parent__._cast(_5770.FaceGearSetMultibodyDynamicsAnalysis)

    @property
    def fe_part_multibody_dynamics_analysis(
        self: "CastSelf",
    ) -> "_5771.FEPartMultibodyDynamicsAnalysis":
        from mastapy._private.system_model.analyses_and_results.mbd_analyses import (
            _5771,
        )

        return self.__parent__._cast(_5771.FEPartMultibodyDynamicsAnalysis)

    @property
    def flexible_pin_assembly_multibody_dynamics_analysis(
        self: "CastSelf",
    ) -> "_5772.FlexiblePinAssemblyMultibodyDynamicsAnalysis":
        from mastapy._private.system_model.analyses_and_results.mbd_analyses import (
            _5772,
        )

        return self.__parent__._cast(_5772.FlexiblePinAssemblyMultibodyDynamicsAnalysis)

    @property
    def gear_multibody_dynamics_analysis(
        self: "CastSelf",
    ) -> "_5775.GearMultibodyDynamicsAnalysis":
        from mastapy._private.system_model.analyses_and_results.mbd_analyses import (
            _5775,
        )

        return self.__parent__._cast(_5775.GearMultibodyDynamicsAnalysis)

    @property
    def gear_set_multibody_dynamics_analysis(
        self: "CastSelf",
    ) -> "_5776.GearSetMultibodyDynamicsAnalysis":
        from mastapy._private.system_model.analyses_and_results.mbd_analyses import (
            _5776,
        )

        return self.__parent__._cast(_5776.GearSetMultibodyDynamicsAnalysis)

    @property
    def guide_dxf_model_multibody_dynamics_analysis(
        self: "CastSelf",
    ) -> "_5777.GuideDxfModelMultibodyDynamicsAnalysis":
        from mastapy._private.system_model.analyses_and_results.mbd_analyses import (
            _5777,
        )

        return self.__parent__._cast(_5777.GuideDxfModelMultibodyDynamicsAnalysis)

    @property
    def hypoid_gear_multibody_dynamics_analysis(
        self: "CastSelf",
    ) -> "_5779.HypoidGearMultibodyDynamicsAnalysis":
        from mastapy._private.system_model.analyses_and_results.mbd_analyses import (
            _5779,
        )

        return self.__parent__._cast(_5779.HypoidGearMultibodyDynamicsAnalysis)

    @property
    def hypoid_gear_set_multibody_dynamics_analysis(
        self: "CastSelf",
    ) -> "_5780.HypoidGearSetMultibodyDynamicsAnalysis":
        from mastapy._private.system_model.analyses_and_results.mbd_analyses import (
            _5780,
        )

        return self.__parent__._cast(_5780.HypoidGearSetMultibodyDynamicsAnalysis)

    @property
    def klingelnberg_cyclo_palloid_conical_gear_multibody_dynamics_analysis(
        self: "CastSelf",
    ) -> "_5787.KlingelnbergCycloPalloidConicalGearMultibodyDynamicsAnalysis":
        from mastapy._private.system_model.analyses_and_results.mbd_analyses import (
            _5787,
        )

        return self.__parent__._cast(
            _5787.KlingelnbergCycloPalloidConicalGearMultibodyDynamicsAnalysis
        )

    @property
    def klingelnberg_cyclo_palloid_conical_gear_set_multibody_dynamics_analysis(
        self: "CastSelf",
    ) -> "_5788.KlingelnbergCycloPalloidConicalGearSetMultibodyDynamicsAnalysis":
        from mastapy._private.system_model.analyses_and_results.mbd_analyses import (
            _5788,
        )

        return self.__parent__._cast(
            _5788.KlingelnbergCycloPalloidConicalGearSetMultibodyDynamicsAnalysis
        )

    @property
    def klingelnberg_cyclo_palloid_hypoid_gear_multibody_dynamics_analysis(
        self: "CastSelf",
    ) -> "_5790.KlingelnbergCycloPalloidHypoidGearMultibodyDynamicsAnalysis":
        from mastapy._private.system_model.analyses_and_results.mbd_analyses import (
            _5790,
        )

        return self.__parent__._cast(
            _5790.KlingelnbergCycloPalloidHypoidGearMultibodyDynamicsAnalysis
        )

    @property
    def klingelnberg_cyclo_palloid_hypoid_gear_set_multibody_dynamics_analysis(
        self: "CastSelf",
    ) -> "_5791.KlingelnbergCycloPalloidHypoidGearSetMultibodyDynamicsAnalysis":
        from mastapy._private.system_model.analyses_and_results.mbd_analyses import (
            _5791,
        )

        return self.__parent__._cast(
            _5791.KlingelnbergCycloPalloidHypoidGearSetMultibodyDynamicsAnalysis
        )

    @property
    def klingelnberg_cyclo_palloid_spiral_bevel_gear_multibody_dynamics_analysis(
        self: "CastSelf",
    ) -> "_5793.KlingelnbergCycloPalloidSpiralBevelGearMultibodyDynamicsAnalysis":
        from mastapy._private.system_model.analyses_and_results.mbd_analyses import (
            _5793,
        )

        return self.__parent__._cast(
            _5793.KlingelnbergCycloPalloidSpiralBevelGearMultibodyDynamicsAnalysis
        )

    @property
    def klingelnberg_cyclo_palloid_spiral_bevel_gear_set_multibody_dynamics_analysis(
        self: "CastSelf",
    ) -> "_5794.KlingelnbergCycloPalloidSpiralBevelGearSetMultibodyDynamicsAnalysis":
        from mastapy._private.system_model.analyses_and_results.mbd_analyses import (
            _5794,
        )

        return self.__parent__._cast(
            _5794.KlingelnbergCycloPalloidSpiralBevelGearSetMultibodyDynamicsAnalysis
        )

    @property
    def mass_disc_multibody_dynamics_analysis(
        self: "CastSelf",
    ) -> "_5795.MassDiscMultibodyDynamicsAnalysis":
        from mastapy._private.system_model.analyses_and_results.mbd_analyses import (
            _5795,
        )

        return self.__parent__._cast(_5795.MassDiscMultibodyDynamicsAnalysis)

    @property
    def measurement_component_multibody_dynamics_analysis(
        self: "CastSelf",
    ) -> "_5799.MeasurementComponentMultibodyDynamicsAnalysis":
        from mastapy._private.system_model.analyses_and_results.mbd_analyses import (
            _5799,
        )

        return self.__parent__._cast(
            _5799.MeasurementComponentMultibodyDynamicsAnalysis
        )

    @property
    def microphone_array_multibody_dynamics_analysis(
        self: "CastSelf",
    ) -> "_5800.MicrophoneArrayMultibodyDynamicsAnalysis":
        from mastapy._private.system_model.analyses_and_results.mbd_analyses import (
            _5800,
        )

        return self.__parent__._cast(_5800.MicrophoneArrayMultibodyDynamicsAnalysis)

    @property
    def microphone_multibody_dynamics_analysis(
        self: "CastSelf",
    ) -> "_5801.MicrophoneMultibodyDynamicsAnalysis":
        from mastapy._private.system_model.analyses_and_results.mbd_analyses import (
            _5801,
        )

        return self.__parent__._cast(_5801.MicrophoneMultibodyDynamicsAnalysis)

    @property
    def mountable_component_multibody_dynamics_analysis(
        self: "CastSelf",
    ) -> "_5802.MountableComponentMultibodyDynamicsAnalysis":
        from mastapy._private.system_model.analyses_and_results.mbd_analyses import (
            _5802,
        )

        return self.__parent__._cast(_5802.MountableComponentMultibodyDynamicsAnalysis)

    @property
    def oil_seal_multibody_dynamics_analysis(
        self: "CastSelf",
    ) -> "_5804.OilSealMultibodyDynamicsAnalysis":
        from mastapy._private.system_model.analyses_and_results.mbd_analyses import (
            _5804,
        )

        return self.__parent__._cast(_5804.OilSealMultibodyDynamicsAnalysis)

    @property
    def part_multibody_dynamics_analysis(
        self: "CastSelf",
    ) -> "_5805.PartMultibodyDynamicsAnalysis":
        from mastapy._private.system_model.analyses_and_results.mbd_analyses import (
            _5805,
        )

        return self.__parent__._cast(_5805.PartMultibodyDynamicsAnalysis)

    @property
    def part_to_part_shear_coupling_half_multibody_dynamics_analysis(
        self: "CastSelf",
    ) -> "_5807.PartToPartShearCouplingHalfMultibodyDynamicsAnalysis":
        from mastapy._private.system_model.analyses_and_results.mbd_analyses import (
            _5807,
        )

        return self.__parent__._cast(
            _5807.PartToPartShearCouplingHalfMultibodyDynamicsAnalysis
        )

    @property
    def part_to_part_shear_coupling_multibody_dynamics_analysis(
        self: "CastSelf",
    ) -> "_5808.PartToPartShearCouplingMultibodyDynamicsAnalysis":
        from mastapy._private.system_model.analyses_and_results.mbd_analyses import (
            _5808,
        )

        return self.__parent__._cast(
            _5808.PartToPartShearCouplingMultibodyDynamicsAnalysis
        )

    @property
    def planetary_gear_set_multibody_dynamics_analysis(
        self: "CastSelf",
    ) -> "_5810.PlanetaryGearSetMultibodyDynamicsAnalysis":
        from mastapy._private.system_model.analyses_and_results.mbd_analyses import (
            _5810,
        )

        return self.__parent__._cast(_5810.PlanetaryGearSetMultibodyDynamicsAnalysis)

    @property
    def planet_carrier_multibody_dynamics_analysis(
        self: "CastSelf",
    ) -> "_5811.PlanetCarrierMultibodyDynamicsAnalysis":
        from mastapy._private.system_model.analyses_and_results.mbd_analyses import (
            _5811,
        )

        return self.__parent__._cast(_5811.PlanetCarrierMultibodyDynamicsAnalysis)

    @property
    def point_load_multibody_dynamics_analysis(
        self: "CastSelf",
    ) -> "_5812.PointLoadMultibodyDynamicsAnalysis":
        from mastapy._private.system_model.analyses_and_results.mbd_analyses import (
            _5812,
        )

        return self.__parent__._cast(_5812.PointLoadMultibodyDynamicsAnalysis)

    @property
    def power_load_multibody_dynamics_analysis(
        self: "CastSelf",
    ) -> "_5813.PowerLoadMultibodyDynamicsAnalysis":
        from mastapy._private.system_model.analyses_and_results.mbd_analyses import (
            _5813,
        )

        return self.__parent__._cast(_5813.PowerLoadMultibodyDynamicsAnalysis)

    @property
    def pulley_multibody_dynamics_analysis(
        self: "CastSelf",
    ) -> "_5814.PulleyMultibodyDynamicsAnalysis":
        from mastapy._private.system_model.analyses_and_results.mbd_analyses import (
            _5814,
        )

        return self.__parent__._cast(_5814.PulleyMultibodyDynamicsAnalysis)

    @property
    def ring_pins_multibody_dynamics_analysis(
        self: "CastSelf",
    ) -> "_5815.RingPinsMultibodyDynamicsAnalysis":
        from mastapy._private.system_model.analyses_and_results.mbd_analyses import (
            _5815,
        )

        return self.__parent__._cast(_5815.RingPinsMultibodyDynamicsAnalysis)

    @property
    def rolling_ring_assembly_multibody_dynamics_analysis(
        self: "CastSelf",
    ) -> "_5817.RollingRingAssemblyMultibodyDynamicsAnalysis":
        from mastapy._private.system_model.analyses_and_results.mbd_analyses import (
            _5817,
        )

        return self.__parent__._cast(_5817.RollingRingAssemblyMultibodyDynamicsAnalysis)

    @property
    def rolling_ring_multibody_dynamics_analysis(
        self: "CastSelf",
    ) -> "_5819.RollingRingMultibodyDynamicsAnalysis":
        from mastapy._private.system_model.analyses_and_results.mbd_analyses import (
            _5819,
        )

        return self.__parent__._cast(_5819.RollingRingMultibodyDynamicsAnalysis)

    @property
    def root_assembly_multibody_dynamics_analysis(
        self: "CastSelf",
    ) -> "_5820.RootAssemblyMultibodyDynamicsAnalysis":
        from mastapy._private.system_model.analyses_and_results.mbd_analyses import (
            _5820,
        )

        return self.__parent__._cast(_5820.RootAssemblyMultibodyDynamicsAnalysis)

    @property
    def shaft_hub_connection_multibody_dynamics_analysis(
        self: "CastSelf",
    ) -> "_5823.ShaftHubConnectionMultibodyDynamicsAnalysis":
        from mastapy._private.system_model.analyses_and_results.mbd_analyses import (
            _5823,
        )

        return self.__parent__._cast(_5823.ShaftHubConnectionMultibodyDynamicsAnalysis)

    @property
    def shaft_multibody_dynamics_analysis(
        self: "CastSelf",
    ) -> "_5824.ShaftMultibodyDynamicsAnalysis":
        from mastapy._private.system_model.analyses_and_results.mbd_analyses import (
            _5824,
        )

        return self.__parent__._cast(_5824.ShaftMultibodyDynamicsAnalysis)

    @property
    def specialised_assembly_multibody_dynamics_analysis(
        self: "CastSelf",
    ) -> "_5827.SpecialisedAssemblyMultibodyDynamicsAnalysis":
        from mastapy._private.system_model.analyses_and_results.mbd_analyses import (
            _5827,
        )

        return self.__parent__._cast(_5827.SpecialisedAssemblyMultibodyDynamicsAnalysis)

    @property
    def spiral_bevel_gear_multibody_dynamics_analysis(
        self: "CastSelf",
    ) -> "_5829.SpiralBevelGearMultibodyDynamicsAnalysis":
        from mastapy._private.system_model.analyses_and_results.mbd_analyses import (
            _5829,
        )

        return self.__parent__._cast(_5829.SpiralBevelGearMultibodyDynamicsAnalysis)

    @property
    def spiral_bevel_gear_set_multibody_dynamics_analysis(
        self: "CastSelf",
    ) -> "_5830.SpiralBevelGearSetMultibodyDynamicsAnalysis":
        from mastapy._private.system_model.analyses_and_results.mbd_analyses import (
            _5830,
        )

        return self.__parent__._cast(_5830.SpiralBevelGearSetMultibodyDynamicsAnalysis)

    @property
    def spring_damper_half_multibody_dynamics_analysis(
        self: "CastSelf",
    ) -> "_5833.SpringDamperHalfMultibodyDynamicsAnalysis":
        from mastapy._private.system_model.analyses_and_results.mbd_analyses import (
            _5833,
        )

        return self.__parent__._cast(_5833.SpringDamperHalfMultibodyDynamicsAnalysis)

    @property
    def spring_damper_multibody_dynamics_analysis(
        self: "CastSelf",
    ) -> "_5834.SpringDamperMultibodyDynamicsAnalysis":
        from mastapy._private.system_model.analyses_and_results.mbd_analyses import (
            _5834,
        )

        return self.__parent__._cast(_5834.SpringDamperMultibodyDynamicsAnalysis)

    @property
    def straight_bevel_diff_gear_multibody_dynamics_analysis(
        self: "CastSelf",
    ) -> "_5836.StraightBevelDiffGearMultibodyDynamicsAnalysis":
        from mastapy._private.system_model.analyses_and_results.mbd_analyses import (
            _5836,
        )

        return self.__parent__._cast(
            _5836.StraightBevelDiffGearMultibodyDynamicsAnalysis
        )

    @property
    def straight_bevel_diff_gear_set_multibody_dynamics_analysis(
        self: "CastSelf",
    ) -> "_5837.StraightBevelDiffGearSetMultibodyDynamicsAnalysis":
        from mastapy._private.system_model.analyses_and_results.mbd_analyses import (
            _5837,
        )

        return self.__parent__._cast(
            _5837.StraightBevelDiffGearSetMultibodyDynamicsAnalysis
        )

    @property
    def straight_bevel_gear_multibody_dynamics_analysis(
        self: "CastSelf",
    ) -> "_5839.StraightBevelGearMultibodyDynamicsAnalysis":
        from mastapy._private.system_model.analyses_and_results.mbd_analyses import (
            _5839,
        )

        return self.__parent__._cast(_5839.StraightBevelGearMultibodyDynamicsAnalysis)

    @property
    def straight_bevel_gear_set_multibody_dynamics_analysis(
        self: "CastSelf",
    ) -> "_5840.StraightBevelGearSetMultibodyDynamicsAnalysis":
        from mastapy._private.system_model.analyses_and_results.mbd_analyses import (
            _5840,
        )

        return self.__parent__._cast(
            _5840.StraightBevelGearSetMultibodyDynamicsAnalysis
        )

    @property
    def straight_bevel_planet_gear_multibody_dynamics_analysis(
        self: "CastSelf",
    ) -> "_5841.StraightBevelPlanetGearMultibodyDynamicsAnalysis":
        from mastapy._private.system_model.analyses_and_results.mbd_analyses import (
            _5841,
        )

        return self.__parent__._cast(
            _5841.StraightBevelPlanetGearMultibodyDynamicsAnalysis
        )

    @property
    def straight_bevel_sun_gear_multibody_dynamics_analysis(
        self: "CastSelf",
    ) -> "_5842.StraightBevelSunGearMultibodyDynamicsAnalysis":
        from mastapy._private.system_model.analyses_and_results.mbd_analyses import (
            _5842,
        )

        return self.__parent__._cast(
            _5842.StraightBevelSunGearMultibodyDynamicsAnalysis
        )

    @property
    def synchroniser_half_multibody_dynamics_analysis(
        self: "CastSelf",
    ) -> "_5843.SynchroniserHalfMultibodyDynamicsAnalysis":
        from mastapy._private.system_model.analyses_and_results.mbd_analyses import (
            _5843,
        )

        return self.__parent__._cast(_5843.SynchroniserHalfMultibodyDynamicsAnalysis)

    @property
    def synchroniser_multibody_dynamics_analysis(
        self: "CastSelf",
    ) -> "_5844.SynchroniserMultibodyDynamicsAnalysis":
        from mastapy._private.system_model.analyses_and_results.mbd_analyses import (
            _5844,
        )

        return self.__parent__._cast(_5844.SynchroniserMultibodyDynamicsAnalysis)

    @property
    def synchroniser_part_multibody_dynamics_analysis(
        self: "CastSelf",
    ) -> "_5845.SynchroniserPartMultibodyDynamicsAnalysis":
        from mastapy._private.system_model.analyses_and_results.mbd_analyses import (
            _5845,
        )

        return self.__parent__._cast(_5845.SynchroniserPartMultibodyDynamicsAnalysis)

    @property
    def synchroniser_sleeve_multibody_dynamics_analysis(
        self: "CastSelf",
    ) -> "_5846.SynchroniserSleeveMultibodyDynamicsAnalysis":
        from mastapy._private.system_model.analyses_and_results.mbd_analyses import (
            _5846,
        )

        return self.__parent__._cast(_5846.SynchroniserSleeveMultibodyDynamicsAnalysis)

    @property
    def torque_converter_multibody_dynamics_analysis(
        self: "CastSelf",
    ) -> "_5849.TorqueConverterMultibodyDynamicsAnalysis":
        from mastapy._private.system_model.analyses_and_results.mbd_analyses import (
            _5849,
        )

        return self.__parent__._cast(_5849.TorqueConverterMultibodyDynamicsAnalysis)

    @property
    def torque_converter_pump_multibody_dynamics_analysis(
        self: "CastSelf",
    ) -> "_5850.TorqueConverterPumpMultibodyDynamicsAnalysis":
        from mastapy._private.system_model.analyses_and_results.mbd_analyses import (
            _5850,
        )

        return self.__parent__._cast(_5850.TorqueConverterPumpMultibodyDynamicsAnalysis)

    @property
    def torque_converter_turbine_multibody_dynamics_analysis(
        self: "CastSelf",
    ) -> "_5852.TorqueConverterTurbineMultibodyDynamicsAnalysis":
        from mastapy._private.system_model.analyses_and_results.mbd_analyses import (
            _5852,
        )

        return self.__parent__._cast(
            _5852.TorqueConverterTurbineMultibodyDynamicsAnalysis
        )

    @property
    def unbalanced_mass_multibody_dynamics_analysis(
        self: "CastSelf",
    ) -> "_5853.UnbalancedMassMultibodyDynamicsAnalysis":
        from mastapy._private.system_model.analyses_and_results.mbd_analyses import (
            _5853,
        )

        return self.__parent__._cast(_5853.UnbalancedMassMultibodyDynamicsAnalysis)

    @property
    def virtual_component_multibody_dynamics_analysis(
        self: "CastSelf",
    ) -> "_5854.VirtualComponentMultibodyDynamicsAnalysis":
        from mastapy._private.system_model.analyses_and_results.mbd_analyses import (
            _5854,
        )

        return self.__parent__._cast(_5854.VirtualComponentMultibodyDynamicsAnalysis)

    @property
    def worm_gear_multibody_dynamics_analysis(
        self: "CastSelf",
    ) -> "_5857.WormGearMultibodyDynamicsAnalysis":
        from mastapy._private.system_model.analyses_and_results.mbd_analyses import (
            _5857,
        )

        return self.__parent__._cast(_5857.WormGearMultibodyDynamicsAnalysis)

    @property
    def worm_gear_set_multibody_dynamics_analysis(
        self: "CastSelf",
    ) -> "_5858.WormGearSetMultibodyDynamicsAnalysis":
        from mastapy._private.system_model.analyses_and_results.mbd_analyses import (
            _5858,
        )

        return self.__parent__._cast(_5858.WormGearSetMultibodyDynamicsAnalysis)

    @property
    def zerol_bevel_gear_multibody_dynamics_analysis(
        self: "CastSelf",
    ) -> "_5860.ZerolBevelGearMultibodyDynamicsAnalysis":
        from mastapy._private.system_model.analyses_and_results.mbd_analyses import (
            _5860,
        )

        return self.__parent__._cast(_5860.ZerolBevelGearMultibodyDynamicsAnalysis)

    @property
    def zerol_bevel_gear_set_multibody_dynamics_analysis(
        self: "CastSelf",
    ) -> "_5861.ZerolBevelGearSetMultibodyDynamicsAnalysis":
        from mastapy._private.system_model.analyses_and_results.mbd_analyses import (
            _5861,
        )

        return self.__parent__._cast(_5861.ZerolBevelGearSetMultibodyDynamicsAnalysis)

    @property
    def part_time_series_load_analysis_case(
        self: "CastSelf",
    ) -> "PartTimeSeriesLoadAnalysisCase":
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
class PartTimeSeriesLoadAnalysisCase(_7941.PartAnalysisCase):
    """PartTimeSeriesLoadAnalysisCase

    This is a mastapy class.
    """

    TYPE: ClassVar["Type"] = _PART_TIME_SERIES_LOAD_ANALYSIS_CASE

    wrapped: "Any"

    def __post_init__(self: "Self") -> None:
        """Override of the post initialisation magic method."""
        if not hasattr(self.wrapped, "reference_count"):
            self.wrapped.reference_count = 0

        self.wrapped.reference_count += 1

    @property
    def cast_to(self: "Self") -> "_Cast_PartTimeSeriesLoadAnalysisCase":
        """Cast to another type.

        Returns:
            _Cast_PartTimeSeriesLoadAnalysisCase
        """
        return _Cast_PartTimeSeriesLoadAnalysisCase(self)
