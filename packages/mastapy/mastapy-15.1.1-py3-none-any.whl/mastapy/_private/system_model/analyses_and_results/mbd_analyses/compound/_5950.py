"""PartCompoundMultibodyDynamicsAnalysis"""

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

_PART_COMPOUND_MULTIBODY_DYNAMICS_ANALYSIS = python_net_import(
    "SMT.MastaAPI.SystemModel.AnalysesAndResults.MBDAnalyses.Compound",
    "PartCompoundMultibodyDynamicsAnalysis",
)

if TYPE_CHECKING:
    from typing import Any, List, Type, TypeVar

    from mastapy._private.system_model.analyses_and_results import _2943
    from mastapy._private.system_model.analyses_and_results.analysis_cases import _7939
    from mastapy._private.system_model.analyses_and_results.mbd_analyses import _5805
    from mastapy._private.system_model.analyses_and_results.mbd_analyses.compound import (
        _5869,
        _5870,
        _5871,
        _5873,
        _5875,
        _5876,
        _5877,
        _5879,
        _5880,
        _5882,
        _5883,
        _5884,
        _5885,
        _5887,
        _5888,
        _5889,
        _5890,
        _5892,
        _5894,
        _5895,
        _5897,
        _5898,
        _5900,
        _5901,
        _5903,
        _5905,
        _5906,
        _5908,
        _5910,
        _5911,
        _5912,
        _5914,
        _5916,
        _5918,
        _5919,
        _5920,
        _5921,
        _5922,
        _5924,
        _5925,
        _5926,
        _5927,
        _5929,
        _5930,
        _5931,
        _5933,
        _5935,
        _5937,
        _5938,
        _5940,
        _5941,
        _5943,
        _5944,
        _5945,
        _5946,
        _5947,
        _5948,
        _5949,
        _5951,
        _5953,
        _5955,
        _5956,
        _5957,
        _5958,
        _5959,
        _5960,
        _5962,
        _5963,
        _5965,
        _5966,
        _5967,
        _5969,
        _5970,
        _5972,
        _5973,
        _5975,
        _5976,
        _5978,
        _5979,
        _5981,
        _5982,
        _5983,
        _5984,
        _5985,
        _5986,
        _5987,
        _5988,
        _5990,
        _5991,
        _5992,
        _5993,
        _5994,
        _5996,
        _5997,
        _5999,
    )

    Self = TypeVar("Self", bound="PartCompoundMultibodyDynamicsAnalysis")
    CastSelf = TypeVar(
        "CastSelf",
        bound="PartCompoundMultibodyDynamicsAnalysis._Cast_PartCompoundMultibodyDynamicsAnalysis",
    )


__docformat__ = "restructuredtext en"
__all__ = ("PartCompoundMultibodyDynamicsAnalysis",)


@extended_dataclass(frozen=True, slots=True, weakref_slot=True)
class _Cast_PartCompoundMultibodyDynamicsAnalysis:
    """Special nested class for casting PartCompoundMultibodyDynamicsAnalysis to subclasses."""

    __parent__: "PartCompoundMultibodyDynamicsAnalysis"

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
    def abstract_assembly_compound_multibody_dynamics_analysis(
        self: "CastSelf",
    ) -> "_5869.AbstractAssemblyCompoundMultibodyDynamicsAnalysis":
        from mastapy._private.system_model.analyses_and_results.mbd_analyses.compound import (
            _5869,
        )

        return self.__parent__._cast(
            _5869.AbstractAssemblyCompoundMultibodyDynamicsAnalysis
        )

    @property
    def abstract_shaft_compound_multibody_dynamics_analysis(
        self: "CastSelf",
    ) -> "_5870.AbstractShaftCompoundMultibodyDynamicsAnalysis":
        from mastapy._private.system_model.analyses_and_results.mbd_analyses.compound import (
            _5870,
        )

        return self.__parent__._cast(
            _5870.AbstractShaftCompoundMultibodyDynamicsAnalysis
        )

    @property
    def abstract_shaft_or_housing_compound_multibody_dynamics_analysis(
        self: "CastSelf",
    ) -> "_5871.AbstractShaftOrHousingCompoundMultibodyDynamicsAnalysis":
        from mastapy._private.system_model.analyses_and_results.mbd_analyses.compound import (
            _5871,
        )

        return self.__parent__._cast(
            _5871.AbstractShaftOrHousingCompoundMultibodyDynamicsAnalysis
        )

    @property
    def agma_gleason_conical_gear_compound_multibody_dynamics_analysis(
        self: "CastSelf",
    ) -> "_5873.AGMAGleasonConicalGearCompoundMultibodyDynamicsAnalysis":
        from mastapy._private.system_model.analyses_and_results.mbd_analyses.compound import (
            _5873,
        )

        return self.__parent__._cast(
            _5873.AGMAGleasonConicalGearCompoundMultibodyDynamicsAnalysis
        )

    @property
    def agma_gleason_conical_gear_set_compound_multibody_dynamics_analysis(
        self: "CastSelf",
    ) -> "_5875.AGMAGleasonConicalGearSetCompoundMultibodyDynamicsAnalysis":
        from mastapy._private.system_model.analyses_and_results.mbd_analyses.compound import (
            _5875,
        )

        return self.__parent__._cast(
            _5875.AGMAGleasonConicalGearSetCompoundMultibodyDynamicsAnalysis
        )

    @property
    def assembly_compound_multibody_dynamics_analysis(
        self: "CastSelf",
    ) -> "_5876.AssemblyCompoundMultibodyDynamicsAnalysis":
        from mastapy._private.system_model.analyses_and_results.mbd_analyses.compound import (
            _5876,
        )

        return self.__parent__._cast(_5876.AssemblyCompoundMultibodyDynamicsAnalysis)

    @property
    def bearing_compound_multibody_dynamics_analysis(
        self: "CastSelf",
    ) -> "_5877.BearingCompoundMultibodyDynamicsAnalysis":
        from mastapy._private.system_model.analyses_and_results.mbd_analyses.compound import (
            _5877,
        )

        return self.__parent__._cast(_5877.BearingCompoundMultibodyDynamicsAnalysis)

    @property
    def belt_drive_compound_multibody_dynamics_analysis(
        self: "CastSelf",
    ) -> "_5879.BeltDriveCompoundMultibodyDynamicsAnalysis":
        from mastapy._private.system_model.analyses_and_results.mbd_analyses.compound import (
            _5879,
        )

        return self.__parent__._cast(_5879.BeltDriveCompoundMultibodyDynamicsAnalysis)

    @property
    def bevel_differential_gear_compound_multibody_dynamics_analysis(
        self: "CastSelf",
    ) -> "_5880.BevelDifferentialGearCompoundMultibodyDynamicsAnalysis":
        from mastapy._private.system_model.analyses_and_results.mbd_analyses.compound import (
            _5880,
        )

        return self.__parent__._cast(
            _5880.BevelDifferentialGearCompoundMultibodyDynamicsAnalysis
        )

    @property
    def bevel_differential_gear_set_compound_multibody_dynamics_analysis(
        self: "CastSelf",
    ) -> "_5882.BevelDifferentialGearSetCompoundMultibodyDynamicsAnalysis":
        from mastapy._private.system_model.analyses_and_results.mbd_analyses.compound import (
            _5882,
        )

        return self.__parent__._cast(
            _5882.BevelDifferentialGearSetCompoundMultibodyDynamicsAnalysis
        )

    @property
    def bevel_differential_planet_gear_compound_multibody_dynamics_analysis(
        self: "CastSelf",
    ) -> "_5883.BevelDifferentialPlanetGearCompoundMultibodyDynamicsAnalysis":
        from mastapy._private.system_model.analyses_and_results.mbd_analyses.compound import (
            _5883,
        )

        return self.__parent__._cast(
            _5883.BevelDifferentialPlanetGearCompoundMultibodyDynamicsAnalysis
        )

    @property
    def bevel_differential_sun_gear_compound_multibody_dynamics_analysis(
        self: "CastSelf",
    ) -> "_5884.BevelDifferentialSunGearCompoundMultibodyDynamicsAnalysis":
        from mastapy._private.system_model.analyses_and_results.mbd_analyses.compound import (
            _5884,
        )

        return self.__parent__._cast(
            _5884.BevelDifferentialSunGearCompoundMultibodyDynamicsAnalysis
        )

    @property
    def bevel_gear_compound_multibody_dynamics_analysis(
        self: "CastSelf",
    ) -> "_5885.BevelGearCompoundMultibodyDynamicsAnalysis":
        from mastapy._private.system_model.analyses_and_results.mbd_analyses.compound import (
            _5885,
        )

        return self.__parent__._cast(_5885.BevelGearCompoundMultibodyDynamicsAnalysis)

    @property
    def bevel_gear_set_compound_multibody_dynamics_analysis(
        self: "CastSelf",
    ) -> "_5887.BevelGearSetCompoundMultibodyDynamicsAnalysis":
        from mastapy._private.system_model.analyses_and_results.mbd_analyses.compound import (
            _5887,
        )

        return self.__parent__._cast(
            _5887.BevelGearSetCompoundMultibodyDynamicsAnalysis
        )

    @property
    def bolt_compound_multibody_dynamics_analysis(
        self: "CastSelf",
    ) -> "_5888.BoltCompoundMultibodyDynamicsAnalysis":
        from mastapy._private.system_model.analyses_and_results.mbd_analyses.compound import (
            _5888,
        )

        return self.__parent__._cast(_5888.BoltCompoundMultibodyDynamicsAnalysis)

    @property
    def bolted_joint_compound_multibody_dynamics_analysis(
        self: "CastSelf",
    ) -> "_5889.BoltedJointCompoundMultibodyDynamicsAnalysis":
        from mastapy._private.system_model.analyses_and_results.mbd_analyses.compound import (
            _5889,
        )

        return self.__parent__._cast(_5889.BoltedJointCompoundMultibodyDynamicsAnalysis)

    @property
    def clutch_compound_multibody_dynamics_analysis(
        self: "CastSelf",
    ) -> "_5890.ClutchCompoundMultibodyDynamicsAnalysis":
        from mastapy._private.system_model.analyses_and_results.mbd_analyses.compound import (
            _5890,
        )

        return self.__parent__._cast(_5890.ClutchCompoundMultibodyDynamicsAnalysis)

    @property
    def clutch_half_compound_multibody_dynamics_analysis(
        self: "CastSelf",
    ) -> "_5892.ClutchHalfCompoundMultibodyDynamicsAnalysis":
        from mastapy._private.system_model.analyses_and_results.mbd_analyses.compound import (
            _5892,
        )

        return self.__parent__._cast(_5892.ClutchHalfCompoundMultibodyDynamicsAnalysis)

    @property
    def component_compound_multibody_dynamics_analysis(
        self: "CastSelf",
    ) -> "_5894.ComponentCompoundMultibodyDynamicsAnalysis":
        from mastapy._private.system_model.analyses_and_results.mbd_analyses.compound import (
            _5894,
        )

        return self.__parent__._cast(_5894.ComponentCompoundMultibodyDynamicsAnalysis)

    @property
    def concept_coupling_compound_multibody_dynamics_analysis(
        self: "CastSelf",
    ) -> "_5895.ConceptCouplingCompoundMultibodyDynamicsAnalysis":
        from mastapy._private.system_model.analyses_and_results.mbd_analyses.compound import (
            _5895,
        )

        return self.__parent__._cast(
            _5895.ConceptCouplingCompoundMultibodyDynamicsAnalysis
        )

    @property
    def concept_coupling_half_compound_multibody_dynamics_analysis(
        self: "CastSelf",
    ) -> "_5897.ConceptCouplingHalfCompoundMultibodyDynamicsAnalysis":
        from mastapy._private.system_model.analyses_and_results.mbd_analyses.compound import (
            _5897,
        )

        return self.__parent__._cast(
            _5897.ConceptCouplingHalfCompoundMultibodyDynamicsAnalysis
        )

    @property
    def concept_gear_compound_multibody_dynamics_analysis(
        self: "CastSelf",
    ) -> "_5898.ConceptGearCompoundMultibodyDynamicsAnalysis":
        from mastapy._private.system_model.analyses_and_results.mbd_analyses.compound import (
            _5898,
        )

        return self.__parent__._cast(_5898.ConceptGearCompoundMultibodyDynamicsAnalysis)

    @property
    def concept_gear_set_compound_multibody_dynamics_analysis(
        self: "CastSelf",
    ) -> "_5900.ConceptGearSetCompoundMultibodyDynamicsAnalysis":
        from mastapy._private.system_model.analyses_and_results.mbd_analyses.compound import (
            _5900,
        )

        return self.__parent__._cast(
            _5900.ConceptGearSetCompoundMultibodyDynamicsAnalysis
        )

    @property
    def conical_gear_compound_multibody_dynamics_analysis(
        self: "CastSelf",
    ) -> "_5901.ConicalGearCompoundMultibodyDynamicsAnalysis":
        from mastapy._private.system_model.analyses_and_results.mbd_analyses.compound import (
            _5901,
        )

        return self.__parent__._cast(_5901.ConicalGearCompoundMultibodyDynamicsAnalysis)

    @property
    def conical_gear_set_compound_multibody_dynamics_analysis(
        self: "CastSelf",
    ) -> "_5903.ConicalGearSetCompoundMultibodyDynamicsAnalysis":
        from mastapy._private.system_model.analyses_and_results.mbd_analyses.compound import (
            _5903,
        )

        return self.__parent__._cast(
            _5903.ConicalGearSetCompoundMultibodyDynamicsAnalysis
        )

    @property
    def connector_compound_multibody_dynamics_analysis(
        self: "CastSelf",
    ) -> "_5905.ConnectorCompoundMultibodyDynamicsAnalysis":
        from mastapy._private.system_model.analyses_and_results.mbd_analyses.compound import (
            _5905,
        )

        return self.__parent__._cast(_5905.ConnectorCompoundMultibodyDynamicsAnalysis)

    @property
    def coupling_compound_multibody_dynamics_analysis(
        self: "CastSelf",
    ) -> "_5906.CouplingCompoundMultibodyDynamicsAnalysis":
        from mastapy._private.system_model.analyses_and_results.mbd_analyses.compound import (
            _5906,
        )

        return self.__parent__._cast(_5906.CouplingCompoundMultibodyDynamicsAnalysis)

    @property
    def coupling_half_compound_multibody_dynamics_analysis(
        self: "CastSelf",
    ) -> "_5908.CouplingHalfCompoundMultibodyDynamicsAnalysis":
        from mastapy._private.system_model.analyses_and_results.mbd_analyses.compound import (
            _5908,
        )

        return self.__parent__._cast(
            _5908.CouplingHalfCompoundMultibodyDynamicsAnalysis
        )

    @property
    def cvt_compound_multibody_dynamics_analysis(
        self: "CastSelf",
    ) -> "_5910.CVTCompoundMultibodyDynamicsAnalysis":
        from mastapy._private.system_model.analyses_and_results.mbd_analyses.compound import (
            _5910,
        )

        return self.__parent__._cast(_5910.CVTCompoundMultibodyDynamicsAnalysis)

    @property
    def cvt_pulley_compound_multibody_dynamics_analysis(
        self: "CastSelf",
    ) -> "_5911.CVTPulleyCompoundMultibodyDynamicsAnalysis":
        from mastapy._private.system_model.analyses_and_results.mbd_analyses.compound import (
            _5911,
        )

        return self.__parent__._cast(_5911.CVTPulleyCompoundMultibodyDynamicsAnalysis)

    @property
    def cycloidal_assembly_compound_multibody_dynamics_analysis(
        self: "CastSelf",
    ) -> "_5912.CycloidalAssemblyCompoundMultibodyDynamicsAnalysis":
        from mastapy._private.system_model.analyses_and_results.mbd_analyses.compound import (
            _5912,
        )

        return self.__parent__._cast(
            _5912.CycloidalAssemblyCompoundMultibodyDynamicsAnalysis
        )

    @property
    def cycloidal_disc_compound_multibody_dynamics_analysis(
        self: "CastSelf",
    ) -> "_5914.CycloidalDiscCompoundMultibodyDynamicsAnalysis":
        from mastapy._private.system_model.analyses_and_results.mbd_analyses.compound import (
            _5914,
        )

        return self.__parent__._cast(
            _5914.CycloidalDiscCompoundMultibodyDynamicsAnalysis
        )

    @property
    def cylindrical_gear_compound_multibody_dynamics_analysis(
        self: "CastSelf",
    ) -> "_5916.CylindricalGearCompoundMultibodyDynamicsAnalysis":
        from mastapy._private.system_model.analyses_and_results.mbd_analyses.compound import (
            _5916,
        )

        return self.__parent__._cast(
            _5916.CylindricalGearCompoundMultibodyDynamicsAnalysis
        )

    @property
    def cylindrical_gear_set_compound_multibody_dynamics_analysis(
        self: "CastSelf",
    ) -> "_5918.CylindricalGearSetCompoundMultibodyDynamicsAnalysis":
        from mastapy._private.system_model.analyses_and_results.mbd_analyses.compound import (
            _5918,
        )

        return self.__parent__._cast(
            _5918.CylindricalGearSetCompoundMultibodyDynamicsAnalysis
        )

    @property
    def cylindrical_planet_gear_compound_multibody_dynamics_analysis(
        self: "CastSelf",
    ) -> "_5919.CylindricalPlanetGearCompoundMultibodyDynamicsAnalysis":
        from mastapy._private.system_model.analyses_and_results.mbd_analyses.compound import (
            _5919,
        )

        return self.__parent__._cast(
            _5919.CylindricalPlanetGearCompoundMultibodyDynamicsAnalysis
        )

    @property
    def datum_compound_multibody_dynamics_analysis(
        self: "CastSelf",
    ) -> "_5920.DatumCompoundMultibodyDynamicsAnalysis":
        from mastapy._private.system_model.analyses_and_results.mbd_analyses.compound import (
            _5920,
        )

        return self.__parent__._cast(_5920.DatumCompoundMultibodyDynamicsAnalysis)

    @property
    def external_cad_model_compound_multibody_dynamics_analysis(
        self: "CastSelf",
    ) -> "_5921.ExternalCADModelCompoundMultibodyDynamicsAnalysis":
        from mastapy._private.system_model.analyses_and_results.mbd_analyses.compound import (
            _5921,
        )

        return self.__parent__._cast(
            _5921.ExternalCADModelCompoundMultibodyDynamicsAnalysis
        )

    @property
    def face_gear_compound_multibody_dynamics_analysis(
        self: "CastSelf",
    ) -> "_5922.FaceGearCompoundMultibodyDynamicsAnalysis":
        from mastapy._private.system_model.analyses_and_results.mbd_analyses.compound import (
            _5922,
        )

        return self.__parent__._cast(_5922.FaceGearCompoundMultibodyDynamicsAnalysis)

    @property
    def face_gear_set_compound_multibody_dynamics_analysis(
        self: "CastSelf",
    ) -> "_5924.FaceGearSetCompoundMultibodyDynamicsAnalysis":
        from mastapy._private.system_model.analyses_and_results.mbd_analyses.compound import (
            _5924,
        )

        return self.__parent__._cast(_5924.FaceGearSetCompoundMultibodyDynamicsAnalysis)

    @property
    def fe_part_compound_multibody_dynamics_analysis(
        self: "CastSelf",
    ) -> "_5925.FEPartCompoundMultibodyDynamicsAnalysis":
        from mastapy._private.system_model.analyses_and_results.mbd_analyses.compound import (
            _5925,
        )

        return self.__parent__._cast(_5925.FEPartCompoundMultibodyDynamicsAnalysis)

    @property
    def flexible_pin_assembly_compound_multibody_dynamics_analysis(
        self: "CastSelf",
    ) -> "_5926.FlexiblePinAssemblyCompoundMultibodyDynamicsAnalysis":
        from mastapy._private.system_model.analyses_and_results.mbd_analyses.compound import (
            _5926,
        )

        return self.__parent__._cast(
            _5926.FlexiblePinAssemblyCompoundMultibodyDynamicsAnalysis
        )

    @property
    def gear_compound_multibody_dynamics_analysis(
        self: "CastSelf",
    ) -> "_5927.GearCompoundMultibodyDynamicsAnalysis":
        from mastapy._private.system_model.analyses_and_results.mbd_analyses.compound import (
            _5927,
        )

        return self.__parent__._cast(_5927.GearCompoundMultibodyDynamicsAnalysis)

    @property
    def gear_set_compound_multibody_dynamics_analysis(
        self: "CastSelf",
    ) -> "_5929.GearSetCompoundMultibodyDynamicsAnalysis":
        from mastapy._private.system_model.analyses_and_results.mbd_analyses.compound import (
            _5929,
        )

        return self.__parent__._cast(_5929.GearSetCompoundMultibodyDynamicsAnalysis)

    @property
    def guide_dxf_model_compound_multibody_dynamics_analysis(
        self: "CastSelf",
    ) -> "_5930.GuideDxfModelCompoundMultibodyDynamicsAnalysis":
        from mastapy._private.system_model.analyses_and_results.mbd_analyses.compound import (
            _5930,
        )

        return self.__parent__._cast(
            _5930.GuideDxfModelCompoundMultibodyDynamicsAnalysis
        )

    @property
    def hypoid_gear_compound_multibody_dynamics_analysis(
        self: "CastSelf",
    ) -> "_5931.HypoidGearCompoundMultibodyDynamicsAnalysis":
        from mastapy._private.system_model.analyses_and_results.mbd_analyses.compound import (
            _5931,
        )

        return self.__parent__._cast(_5931.HypoidGearCompoundMultibodyDynamicsAnalysis)

    @property
    def hypoid_gear_set_compound_multibody_dynamics_analysis(
        self: "CastSelf",
    ) -> "_5933.HypoidGearSetCompoundMultibodyDynamicsAnalysis":
        from mastapy._private.system_model.analyses_and_results.mbd_analyses.compound import (
            _5933,
        )

        return self.__parent__._cast(
            _5933.HypoidGearSetCompoundMultibodyDynamicsAnalysis
        )

    @property
    def klingelnberg_cyclo_palloid_conical_gear_compound_multibody_dynamics_analysis(
        self: "CastSelf",
    ) -> "_5935.KlingelnbergCycloPalloidConicalGearCompoundMultibodyDynamicsAnalysis":
        from mastapy._private.system_model.analyses_and_results.mbd_analyses.compound import (
            _5935,
        )

        return self.__parent__._cast(
            _5935.KlingelnbergCycloPalloidConicalGearCompoundMultibodyDynamicsAnalysis
        )

    @property
    def klingelnberg_cyclo_palloid_conical_gear_set_compound_multibody_dynamics_analysis(
        self: "CastSelf",
    ) -> (
        "_5937.KlingelnbergCycloPalloidConicalGearSetCompoundMultibodyDynamicsAnalysis"
    ):
        from mastapy._private.system_model.analyses_and_results.mbd_analyses.compound import (
            _5937,
        )

        return self.__parent__._cast(
            _5937.KlingelnbergCycloPalloidConicalGearSetCompoundMultibodyDynamicsAnalysis
        )

    @property
    def klingelnberg_cyclo_palloid_hypoid_gear_compound_multibody_dynamics_analysis(
        self: "CastSelf",
    ) -> "_5938.KlingelnbergCycloPalloidHypoidGearCompoundMultibodyDynamicsAnalysis":
        from mastapy._private.system_model.analyses_and_results.mbd_analyses.compound import (
            _5938,
        )

        return self.__parent__._cast(
            _5938.KlingelnbergCycloPalloidHypoidGearCompoundMultibodyDynamicsAnalysis
        )

    @property
    def klingelnberg_cyclo_palloid_hypoid_gear_set_compound_multibody_dynamics_analysis(
        self: "CastSelf",
    ) -> "_5940.KlingelnbergCycloPalloidHypoidGearSetCompoundMultibodyDynamicsAnalysis":
        from mastapy._private.system_model.analyses_and_results.mbd_analyses.compound import (
            _5940,
        )

        return self.__parent__._cast(
            _5940.KlingelnbergCycloPalloidHypoidGearSetCompoundMultibodyDynamicsAnalysis
        )

    @property
    def klingelnberg_cyclo_palloid_spiral_bevel_gear_compound_multibody_dynamics_analysis(
        self: "CastSelf",
    ) -> (
        "_5941.KlingelnbergCycloPalloidSpiralBevelGearCompoundMultibodyDynamicsAnalysis"
    ):
        from mastapy._private.system_model.analyses_and_results.mbd_analyses.compound import (
            _5941,
        )

        return self.__parent__._cast(
            _5941.KlingelnbergCycloPalloidSpiralBevelGearCompoundMultibodyDynamicsAnalysis
        )

    @property
    def klingelnberg_cyclo_palloid_spiral_bevel_gear_set_compound_multibody_dynamics_analysis(
        self: "CastSelf",
    ) -> "_5943.KlingelnbergCycloPalloidSpiralBevelGearSetCompoundMultibodyDynamicsAnalysis":
        from mastapy._private.system_model.analyses_and_results.mbd_analyses.compound import (
            _5943,
        )

        return self.__parent__._cast(
            _5943.KlingelnbergCycloPalloidSpiralBevelGearSetCompoundMultibodyDynamicsAnalysis
        )

    @property
    def mass_disc_compound_multibody_dynamics_analysis(
        self: "CastSelf",
    ) -> "_5944.MassDiscCompoundMultibodyDynamicsAnalysis":
        from mastapy._private.system_model.analyses_and_results.mbd_analyses.compound import (
            _5944,
        )

        return self.__parent__._cast(_5944.MassDiscCompoundMultibodyDynamicsAnalysis)

    @property
    def measurement_component_compound_multibody_dynamics_analysis(
        self: "CastSelf",
    ) -> "_5945.MeasurementComponentCompoundMultibodyDynamicsAnalysis":
        from mastapy._private.system_model.analyses_and_results.mbd_analyses.compound import (
            _5945,
        )

        return self.__parent__._cast(
            _5945.MeasurementComponentCompoundMultibodyDynamicsAnalysis
        )

    @property
    def microphone_array_compound_multibody_dynamics_analysis(
        self: "CastSelf",
    ) -> "_5946.MicrophoneArrayCompoundMultibodyDynamicsAnalysis":
        from mastapy._private.system_model.analyses_and_results.mbd_analyses.compound import (
            _5946,
        )

        return self.__parent__._cast(
            _5946.MicrophoneArrayCompoundMultibodyDynamicsAnalysis
        )

    @property
    def microphone_compound_multibody_dynamics_analysis(
        self: "CastSelf",
    ) -> "_5947.MicrophoneCompoundMultibodyDynamicsAnalysis":
        from mastapy._private.system_model.analyses_and_results.mbd_analyses.compound import (
            _5947,
        )

        return self.__parent__._cast(_5947.MicrophoneCompoundMultibodyDynamicsAnalysis)

    @property
    def mountable_component_compound_multibody_dynamics_analysis(
        self: "CastSelf",
    ) -> "_5948.MountableComponentCompoundMultibodyDynamicsAnalysis":
        from mastapy._private.system_model.analyses_and_results.mbd_analyses.compound import (
            _5948,
        )

        return self.__parent__._cast(
            _5948.MountableComponentCompoundMultibodyDynamicsAnalysis
        )

    @property
    def oil_seal_compound_multibody_dynamics_analysis(
        self: "CastSelf",
    ) -> "_5949.OilSealCompoundMultibodyDynamicsAnalysis":
        from mastapy._private.system_model.analyses_and_results.mbd_analyses.compound import (
            _5949,
        )

        return self.__parent__._cast(_5949.OilSealCompoundMultibodyDynamicsAnalysis)

    @property
    def part_to_part_shear_coupling_compound_multibody_dynamics_analysis(
        self: "CastSelf",
    ) -> "_5951.PartToPartShearCouplingCompoundMultibodyDynamicsAnalysis":
        from mastapy._private.system_model.analyses_and_results.mbd_analyses.compound import (
            _5951,
        )

        return self.__parent__._cast(
            _5951.PartToPartShearCouplingCompoundMultibodyDynamicsAnalysis
        )

    @property
    def part_to_part_shear_coupling_half_compound_multibody_dynamics_analysis(
        self: "CastSelf",
    ) -> "_5953.PartToPartShearCouplingHalfCompoundMultibodyDynamicsAnalysis":
        from mastapy._private.system_model.analyses_and_results.mbd_analyses.compound import (
            _5953,
        )

        return self.__parent__._cast(
            _5953.PartToPartShearCouplingHalfCompoundMultibodyDynamicsAnalysis
        )

    @property
    def planetary_gear_set_compound_multibody_dynamics_analysis(
        self: "CastSelf",
    ) -> "_5955.PlanetaryGearSetCompoundMultibodyDynamicsAnalysis":
        from mastapy._private.system_model.analyses_and_results.mbd_analyses.compound import (
            _5955,
        )

        return self.__parent__._cast(
            _5955.PlanetaryGearSetCompoundMultibodyDynamicsAnalysis
        )

    @property
    def planet_carrier_compound_multibody_dynamics_analysis(
        self: "CastSelf",
    ) -> "_5956.PlanetCarrierCompoundMultibodyDynamicsAnalysis":
        from mastapy._private.system_model.analyses_and_results.mbd_analyses.compound import (
            _5956,
        )

        return self.__parent__._cast(
            _5956.PlanetCarrierCompoundMultibodyDynamicsAnalysis
        )

    @property
    def point_load_compound_multibody_dynamics_analysis(
        self: "CastSelf",
    ) -> "_5957.PointLoadCompoundMultibodyDynamicsAnalysis":
        from mastapy._private.system_model.analyses_and_results.mbd_analyses.compound import (
            _5957,
        )

        return self.__parent__._cast(_5957.PointLoadCompoundMultibodyDynamicsAnalysis)

    @property
    def power_load_compound_multibody_dynamics_analysis(
        self: "CastSelf",
    ) -> "_5958.PowerLoadCompoundMultibodyDynamicsAnalysis":
        from mastapy._private.system_model.analyses_and_results.mbd_analyses.compound import (
            _5958,
        )

        return self.__parent__._cast(_5958.PowerLoadCompoundMultibodyDynamicsAnalysis)

    @property
    def pulley_compound_multibody_dynamics_analysis(
        self: "CastSelf",
    ) -> "_5959.PulleyCompoundMultibodyDynamicsAnalysis":
        from mastapy._private.system_model.analyses_and_results.mbd_analyses.compound import (
            _5959,
        )

        return self.__parent__._cast(_5959.PulleyCompoundMultibodyDynamicsAnalysis)

    @property
    def ring_pins_compound_multibody_dynamics_analysis(
        self: "CastSelf",
    ) -> "_5960.RingPinsCompoundMultibodyDynamicsAnalysis":
        from mastapy._private.system_model.analyses_and_results.mbd_analyses.compound import (
            _5960,
        )

        return self.__parent__._cast(_5960.RingPinsCompoundMultibodyDynamicsAnalysis)

    @property
    def rolling_ring_assembly_compound_multibody_dynamics_analysis(
        self: "CastSelf",
    ) -> "_5962.RollingRingAssemblyCompoundMultibodyDynamicsAnalysis":
        from mastapy._private.system_model.analyses_and_results.mbd_analyses.compound import (
            _5962,
        )

        return self.__parent__._cast(
            _5962.RollingRingAssemblyCompoundMultibodyDynamicsAnalysis
        )

    @property
    def rolling_ring_compound_multibody_dynamics_analysis(
        self: "CastSelf",
    ) -> "_5963.RollingRingCompoundMultibodyDynamicsAnalysis":
        from mastapy._private.system_model.analyses_and_results.mbd_analyses.compound import (
            _5963,
        )

        return self.__parent__._cast(_5963.RollingRingCompoundMultibodyDynamicsAnalysis)

    @property
    def root_assembly_compound_multibody_dynamics_analysis(
        self: "CastSelf",
    ) -> "_5965.RootAssemblyCompoundMultibodyDynamicsAnalysis":
        from mastapy._private.system_model.analyses_and_results.mbd_analyses.compound import (
            _5965,
        )

        return self.__parent__._cast(
            _5965.RootAssemblyCompoundMultibodyDynamicsAnalysis
        )

    @property
    def shaft_compound_multibody_dynamics_analysis(
        self: "CastSelf",
    ) -> "_5966.ShaftCompoundMultibodyDynamicsAnalysis":
        from mastapy._private.system_model.analyses_and_results.mbd_analyses.compound import (
            _5966,
        )

        return self.__parent__._cast(_5966.ShaftCompoundMultibodyDynamicsAnalysis)

    @property
    def shaft_hub_connection_compound_multibody_dynamics_analysis(
        self: "CastSelf",
    ) -> "_5967.ShaftHubConnectionCompoundMultibodyDynamicsAnalysis":
        from mastapy._private.system_model.analyses_and_results.mbd_analyses.compound import (
            _5967,
        )

        return self.__parent__._cast(
            _5967.ShaftHubConnectionCompoundMultibodyDynamicsAnalysis
        )

    @property
    def specialised_assembly_compound_multibody_dynamics_analysis(
        self: "CastSelf",
    ) -> "_5969.SpecialisedAssemblyCompoundMultibodyDynamicsAnalysis":
        from mastapy._private.system_model.analyses_and_results.mbd_analyses.compound import (
            _5969,
        )

        return self.__parent__._cast(
            _5969.SpecialisedAssemblyCompoundMultibodyDynamicsAnalysis
        )

    @property
    def spiral_bevel_gear_compound_multibody_dynamics_analysis(
        self: "CastSelf",
    ) -> "_5970.SpiralBevelGearCompoundMultibodyDynamicsAnalysis":
        from mastapy._private.system_model.analyses_and_results.mbd_analyses.compound import (
            _5970,
        )

        return self.__parent__._cast(
            _5970.SpiralBevelGearCompoundMultibodyDynamicsAnalysis
        )

    @property
    def spiral_bevel_gear_set_compound_multibody_dynamics_analysis(
        self: "CastSelf",
    ) -> "_5972.SpiralBevelGearSetCompoundMultibodyDynamicsAnalysis":
        from mastapy._private.system_model.analyses_and_results.mbd_analyses.compound import (
            _5972,
        )

        return self.__parent__._cast(
            _5972.SpiralBevelGearSetCompoundMultibodyDynamicsAnalysis
        )

    @property
    def spring_damper_compound_multibody_dynamics_analysis(
        self: "CastSelf",
    ) -> "_5973.SpringDamperCompoundMultibodyDynamicsAnalysis":
        from mastapy._private.system_model.analyses_and_results.mbd_analyses.compound import (
            _5973,
        )

        return self.__parent__._cast(
            _5973.SpringDamperCompoundMultibodyDynamicsAnalysis
        )

    @property
    def spring_damper_half_compound_multibody_dynamics_analysis(
        self: "CastSelf",
    ) -> "_5975.SpringDamperHalfCompoundMultibodyDynamicsAnalysis":
        from mastapy._private.system_model.analyses_and_results.mbd_analyses.compound import (
            _5975,
        )

        return self.__parent__._cast(
            _5975.SpringDamperHalfCompoundMultibodyDynamicsAnalysis
        )

    @property
    def straight_bevel_diff_gear_compound_multibody_dynamics_analysis(
        self: "CastSelf",
    ) -> "_5976.StraightBevelDiffGearCompoundMultibodyDynamicsAnalysis":
        from mastapy._private.system_model.analyses_and_results.mbd_analyses.compound import (
            _5976,
        )

        return self.__parent__._cast(
            _5976.StraightBevelDiffGearCompoundMultibodyDynamicsAnalysis
        )

    @property
    def straight_bevel_diff_gear_set_compound_multibody_dynamics_analysis(
        self: "CastSelf",
    ) -> "_5978.StraightBevelDiffGearSetCompoundMultibodyDynamicsAnalysis":
        from mastapy._private.system_model.analyses_and_results.mbd_analyses.compound import (
            _5978,
        )

        return self.__parent__._cast(
            _5978.StraightBevelDiffGearSetCompoundMultibodyDynamicsAnalysis
        )

    @property
    def straight_bevel_gear_compound_multibody_dynamics_analysis(
        self: "CastSelf",
    ) -> "_5979.StraightBevelGearCompoundMultibodyDynamicsAnalysis":
        from mastapy._private.system_model.analyses_and_results.mbd_analyses.compound import (
            _5979,
        )

        return self.__parent__._cast(
            _5979.StraightBevelGearCompoundMultibodyDynamicsAnalysis
        )

    @property
    def straight_bevel_gear_set_compound_multibody_dynamics_analysis(
        self: "CastSelf",
    ) -> "_5981.StraightBevelGearSetCompoundMultibodyDynamicsAnalysis":
        from mastapy._private.system_model.analyses_and_results.mbd_analyses.compound import (
            _5981,
        )

        return self.__parent__._cast(
            _5981.StraightBevelGearSetCompoundMultibodyDynamicsAnalysis
        )

    @property
    def straight_bevel_planet_gear_compound_multibody_dynamics_analysis(
        self: "CastSelf",
    ) -> "_5982.StraightBevelPlanetGearCompoundMultibodyDynamicsAnalysis":
        from mastapy._private.system_model.analyses_and_results.mbd_analyses.compound import (
            _5982,
        )

        return self.__parent__._cast(
            _5982.StraightBevelPlanetGearCompoundMultibodyDynamicsAnalysis
        )

    @property
    def straight_bevel_sun_gear_compound_multibody_dynamics_analysis(
        self: "CastSelf",
    ) -> "_5983.StraightBevelSunGearCompoundMultibodyDynamicsAnalysis":
        from mastapy._private.system_model.analyses_and_results.mbd_analyses.compound import (
            _5983,
        )

        return self.__parent__._cast(
            _5983.StraightBevelSunGearCompoundMultibodyDynamicsAnalysis
        )

    @property
    def synchroniser_compound_multibody_dynamics_analysis(
        self: "CastSelf",
    ) -> "_5984.SynchroniserCompoundMultibodyDynamicsAnalysis":
        from mastapy._private.system_model.analyses_and_results.mbd_analyses.compound import (
            _5984,
        )

        return self.__parent__._cast(
            _5984.SynchroniserCompoundMultibodyDynamicsAnalysis
        )

    @property
    def synchroniser_half_compound_multibody_dynamics_analysis(
        self: "CastSelf",
    ) -> "_5985.SynchroniserHalfCompoundMultibodyDynamicsAnalysis":
        from mastapy._private.system_model.analyses_and_results.mbd_analyses.compound import (
            _5985,
        )

        return self.__parent__._cast(
            _5985.SynchroniserHalfCompoundMultibodyDynamicsAnalysis
        )

    @property
    def synchroniser_part_compound_multibody_dynamics_analysis(
        self: "CastSelf",
    ) -> "_5986.SynchroniserPartCompoundMultibodyDynamicsAnalysis":
        from mastapy._private.system_model.analyses_and_results.mbd_analyses.compound import (
            _5986,
        )

        return self.__parent__._cast(
            _5986.SynchroniserPartCompoundMultibodyDynamicsAnalysis
        )

    @property
    def synchroniser_sleeve_compound_multibody_dynamics_analysis(
        self: "CastSelf",
    ) -> "_5987.SynchroniserSleeveCompoundMultibodyDynamicsAnalysis":
        from mastapy._private.system_model.analyses_and_results.mbd_analyses.compound import (
            _5987,
        )

        return self.__parent__._cast(
            _5987.SynchroniserSleeveCompoundMultibodyDynamicsAnalysis
        )

    @property
    def torque_converter_compound_multibody_dynamics_analysis(
        self: "CastSelf",
    ) -> "_5988.TorqueConverterCompoundMultibodyDynamicsAnalysis":
        from mastapy._private.system_model.analyses_and_results.mbd_analyses.compound import (
            _5988,
        )

        return self.__parent__._cast(
            _5988.TorqueConverterCompoundMultibodyDynamicsAnalysis
        )

    @property
    def torque_converter_pump_compound_multibody_dynamics_analysis(
        self: "CastSelf",
    ) -> "_5990.TorqueConverterPumpCompoundMultibodyDynamicsAnalysis":
        from mastapy._private.system_model.analyses_and_results.mbd_analyses.compound import (
            _5990,
        )

        return self.__parent__._cast(
            _5990.TorqueConverterPumpCompoundMultibodyDynamicsAnalysis
        )

    @property
    def torque_converter_turbine_compound_multibody_dynamics_analysis(
        self: "CastSelf",
    ) -> "_5991.TorqueConverterTurbineCompoundMultibodyDynamicsAnalysis":
        from mastapy._private.system_model.analyses_and_results.mbd_analyses.compound import (
            _5991,
        )

        return self.__parent__._cast(
            _5991.TorqueConverterTurbineCompoundMultibodyDynamicsAnalysis
        )

    @property
    def unbalanced_mass_compound_multibody_dynamics_analysis(
        self: "CastSelf",
    ) -> "_5992.UnbalancedMassCompoundMultibodyDynamicsAnalysis":
        from mastapy._private.system_model.analyses_and_results.mbd_analyses.compound import (
            _5992,
        )

        return self.__parent__._cast(
            _5992.UnbalancedMassCompoundMultibodyDynamicsAnalysis
        )

    @property
    def virtual_component_compound_multibody_dynamics_analysis(
        self: "CastSelf",
    ) -> "_5993.VirtualComponentCompoundMultibodyDynamicsAnalysis":
        from mastapy._private.system_model.analyses_and_results.mbd_analyses.compound import (
            _5993,
        )

        return self.__parent__._cast(
            _5993.VirtualComponentCompoundMultibodyDynamicsAnalysis
        )

    @property
    def worm_gear_compound_multibody_dynamics_analysis(
        self: "CastSelf",
    ) -> "_5994.WormGearCompoundMultibodyDynamicsAnalysis":
        from mastapy._private.system_model.analyses_and_results.mbd_analyses.compound import (
            _5994,
        )

        return self.__parent__._cast(_5994.WormGearCompoundMultibodyDynamicsAnalysis)

    @property
    def worm_gear_set_compound_multibody_dynamics_analysis(
        self: "CastSelf",
    ) -> "_5996.WormGearSetCompoundMultibodyDynamicsAnalysis":
        from mastapy._private.system_model.analyses_and_results.mbd_analyses.compound import (
            _5996,
        )

        return self.__parent__._cast(_5996.WormGearSetCompoundMultibodyDynamicsAnalysis)

    @property
    def zerol_bevel_gear_compound_multibody_dynamics_analysis(
        self: "CastSelf",
    ) -> "_5997.ZerolBevelGearCompoundMultibodyDynamicsAnalysis":
        from mastapy._private.system_model.analyses_and_results.mbd_analyses.compound import (
            _5997,
        )

        return self.__parent__._cast(
            _5997.ZerolBevelGearCompoundMultibodyDynamicsAnalysis
        )

    @property
    def zerol_bevel_gear_set_compound_multibody_dynamics_analysis(
        self: "CastSelf",
    ) -> "_5999.ZerolBevelGearSetCompoundMultibodyDynamicsAnalysis":
        from mastapy._private.system_model.analyses_and_results.mbd_analyses.compound import (
            _5999,
        )

        return self.__parent__._cast(
            _5999.ZerolBevelGearSetCompoundMultibodyDynamicsAnalysis
        )

    @property
    def part_compound_multibody_dynamics_analysis(
        self: "CastSelf",
    ) -> "PartCompoundMultibodyDynamicsAnalysis":
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
class PartCompoundMultibodyDynamicsAnalysis(_7942.PartCompoundAnalysis):
    """PartCompoundMultibodyDynamicsAnalysis

    This is a mastapy class.
    """

    TYPE: ClassVar["Type"] = _PART_COMPOUND_MULTIBODY_DYNAMICS_ANALYSIS

    wrapped: "Any"

    def __post_init__(self: "Self") -> None:
        """Override of the post initialisation magic method."""
        if not hasattr(self.wrapped, "reference_count"):
            self.wrapped.reference_count = 0

        self.wrapped.reference_count += 1

    @property
    @exception_bridge
    def component_analysis_cases(
        self: "Self",
    ) -> "List[_5805.PartMultibodyDynamicsAnalysis]":
        """List[mastapy.system_model.analyses_and_results.mbd_analyses.PartMultibodyDynamicsAnalysis]

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
    def component_analysis_cases_ready(
        self: "Self",
    ) -> "List[_5805.PartMultibodyDynamicsAnalysis]":
        """List[mastapy.system_model.analyses_and_results.mbd_analyses.PartMultibodyDynamicsAnalysis]

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
    def cast_to(self: "Self") -> "_Cast_PartCompoundMultibodyDynamicsAnalysis":
        """Cast to another type.

        Returns:
            _Cast_PartCompoundMultibodyDynamicsAnalysis
        """
        return _Cast_PartCompoundMultibodyDynamicsAnalysis(self)
