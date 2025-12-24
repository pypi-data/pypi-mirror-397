"""PartCompoundDynamicAnalysis"""

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

_PART_COMPOUND_DYNAMIC_ANALYSIS = python_net_import(
    "SMT.MastaAPI.SystemModel.AnalysesAndResults.DynamicAnalyses.Compound",
    "PartCompoundDynamicAnalysis",
)

if TYPE_CHECKING:
    from typing import Any, List, Type, TypeVar

    from mastapy._private.system_model.analyses_and_results import _2943
    from mastapy._private.system_model.analyses_and_results.analysis_cases import _7939
    from mastapy._private.system_model.analyses_and_results.dynamic_analyses import (
        _6724,
    )
    from mastapy._private.system_model.analyses_and_results.dynamic_analyses.compound import (
        _6774,
        _6775,
        _6776,
        _6778,
        _6780,
        _6781,
        _6782,
        _6784,
        _6785,
        _6787,
        _6788,
        _6789,
        _6790,
        _6792,
        _6793,
        _6794,
        _6795,
        _6797,
        _6799,
        _6800,
        _6802,
        _6803,
        _6805,
        _6806,
        _6808,
        _6810,
        _6811,
        _6813,
        _6815,
        _6816,
        _6817,
        _6819,
        _6821,
        _6823,
        _6824,
        _6825,
        _6826,
        _6827,
        _6829,
        _6830,
        _6831,
        _6832,
        _6834,
        _6835,
        _6836,
        _6838,
        _6840,
        _6842,
        _6843,
        _6845,
        _6846,
        _6848,
        _6849,
        _6850,
        _6851,
        _6852,
        _6853,
        _6854,
        _6856,
        _6858,
        _6860,
        _6861,
        _6862,
        _6863,
        _6864,
        _6865,
        _6867,
        _6868,
        _6870,
        _6871,
        _6872,
        _6874,
        _6875,
        _6877,
        _6878,
        _6880,
        _6881,
        _6883,
        _6884,
        _6886,
        _6887,
        _6888,
        _6889,
        _6890,
        _6891,
        _6892,
        _6893,
        _6895,
        _6896,
        _6897,
        _6898,
        _6899,
        _6901,
        _6902,
        _6904,
    )

    Self = TypeVar("Self", bound="PartCompoundDynamicAnalysis")
    CastSelf = TypeVar(
        "CastSelf",
        bound="PartCompoundDynamicAnalysis._Cast_PartCompoundDynamicAnalysis",
    )


__docformat__ = "restructuredtext en"
__all__ = ("PartCompoundDynamicAnalysis",)


@extended_dataclass(frozen=True, slots=True, weakref_slot=True)
class _Cast_PartCompoundDynamicAnalysis:
    """Special nested class for casting PartCompoundDynamicAnalysis to subclasses."""

    __parent__: "PartCompoundDynamicAnalysis"

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
    def abstract_assembly_compound_dynamic_analysis(
        self: "CastSelf",
    ) -> "_6774.AbstractAssemblyCompoundDynamicAnalysis":
        from mastapy._private.system_model.analyses_and_results.dynamic_analyses.compound import (
            _6774,
        )

        return self.__parent__._cast(_6774.AbstractAssemblyCompoundDynamicAnalysis)

    @property
    def abstract_shaft_compound_dynamic_analysis(
        self: "CastSelf",
    ) -> "_6775.AbstractShaftCompoundDynamicAnalysis":
        from mastapy._private.system_model.analyses_and_results.dynamic_analyses.compound import (
            _6775,
        )

        return self.__parent__._cast(_6775.AbstractShaftCompoundDynamicAnalysis)

    @property
    def abstract_shaft_or_housing_compound_dynamic_analysis(
        self: "CastSelf",
    ) -> "_6776.AbstractShaftOrHousingCompoundDynamicAnalysis":
        from mastapy._private.system_model.analyses_and_results.dynamic_analyses.compound import (
            _6776,
        )

        return self.__parent__._cast(
            _6776.AbstractShaftOrHousingCompoundDynamicAnalysis
        )

    @property
    def agma_gleason_conical_gear_compound_dynamic_analysis(
        self: "CastSelf",
    ) -> "_6778.AGMAGleasonConicalGearCompoundDynamicAnalysis":
        from mastapy._private.system_model.analyses_and_results.dynamic_analyses.compound import (
            _6778,
        )

        return self.__parent__._cast(
            _6778.AGMAGleasonConicalGearCompoundDynamicAnalysis
        )

    @property
    def agma_gleason_conical_gear_set_compound_dynamic_analysis(
        self: "CastSelf",
    ) -> "_6780.AGMAGleasonConicalGearSetCompoundDynamicAnalysis":
        from mastapy._private.system_model.analyses_and_results.dynamic_analyses.compound import (
            _6780,
        )

        return self.__parent__._cast(
            _6780.AGMAGleasonConicalGearSetCompoundDynamicAnalysis
        )

    @property
    def assembly_compound_dynamic_analysis(
        self: "CastSelf",
    ) -> "_6781.AssemblyCompoundDynamicAnalysis":
        from mastapy._private.system_model.analyses_and_results.dynamic_analyses.compound import (
            _6781,
        )

        return self.__parent__._cast(_6781.AssemblyCompoundDynamicAnalysis)

    @property
    def bearing_compound_dynamic_analysis(
        self: "CastSelf",
    ) -> "_6782.BearingCompoundDynamicAnalysis":
        from mastapy._private.system_model.analyses_and_results.dynamic_analyses.compound import (
            _6782,
        )

        return self.__parent__._cast(_6782.BearingCompoundDynamicAnalysis)

    @property
    def belt_drive_compound_dynamic_analysis(
        self: "CastSelf",
    ) -> "_6784.BeltDriveCompoundDynamicAnalysis":
        from mastapy._private.system_model.analyses_and_results.dynamic_analyses.compound import (
            _6784,
        )

        return self.__parent__._cast(_6784.BeltDriveCompoundDynamicAnalysis)

    @property
    def bevel_differential_gear_compound_dynamic_analysis(
        self: "CastSelf",
    ) -> "_6785.BevelDifferentialGearCompoundDynamicAnalysis":
        from mastapy._private.system_model.analyses_and_results.dynamic_analyses.compound import (
            _6785,
        )

        return self.__parent__._cast(_6785.BevelDifferentialGearCompoundDynamicAnalysis)

    @property
    def bevel_differential_gear_set_compound_dynamic_analysis(
        self: "CastSelf",
    ) -> "_6787.BevelDifferentialGearSetCompoundDynamicAnalysis":
        from mastapy._private.system_model.analyses_and_results.dynamic_analyses.compound import (
            _6787,
        )

        return self.__parent__._cast(
            _6787.BevelDifferentialGearSetCompoundDynamicAnalysis
        )

    @property
    def bevel_differential_planet_gear_compound_dynamic_analysis(
        self: "CastSelf",
    ) -> "_6788.BevelDifferentialPlanetGearCompoundDynamicAnalysis":
        from mastapy._private.system_model.analyses_and_results.dynamic_analyses.compound import (
            _6788,
        )

        return self.__parent__._cast(
            _6788.BevelDifferentialPlanetGearCompoundDynamicAnalysis
        )

    @property
    def bevel_differential_sun_gear_compound_dynamic_analysis(
        self: "CastSelf",
    ) -> "_6789.BevelDifferentialSunGearCompoundDynamicAnalysis":
        from mastapy._private.system_model.analyses_and_results.dynamic_analyses.compound import (
            _6789,
        )

        return self.__parent__._cast(
            _6789.BevelDifferentialSunGearCompoundDynamicAnalysis
        )

    @property
    def bevel_gear_compound_dynamic_analysis(
        self: "CastSelf",
    ) -> "_6790.BevelGearCompoundDynamicAnalysis":
        from mastapy._private.system_model.analyses_and_results.dynamic_analyses.compound import (
            _6790,
        )

        return self.__parent__._cast(_6790.BevelGearCompoundDynamicAnalysis)

    @property
    def bevel_gear_set_compound_dynamic_analysis(
        self: "CastSelf",
    ) -> "_6792.BevelGearSetCompoundDynamicAnalysis":
        from mastapy._private.system_model.analyses_and_results.dynamic_analyses.compound import (
            _6792,
        )

        return self.__parent__._cast(_6792.BevelGearSetCompoundDynamicAnalysis)

    @property
    def bolt_compound_dynamic_analysis(
        self: "CastSelf",
    ) -> "_6793.BoltCompoundDynamicAnalysis":
        from mastapy._private.system_model.analyses_and_results.dynamic_analyses.compound import (
            _6793,
        )

        return self.__parent__._cast(_6793.BoltCompoundDynamicAnalysis)

    @property
    def bolted_joint_compound_dynamic_analysis(
        self: "CastSelf",
    ) -> "_6794.BoltedJointCompoundDynamicAnalysis":
        from mastapy._private.system_model.analyses_and_results.dynamic_analyses.compound import (
            _6794,
        )

        return self.__parent__._cast(_6794.BoltedJointCompoundDynamicAnalysis)

    @property
    def clutch_compound_dynamic_analysis(
        self: "CastSelf",
    ) -> "_6795.ClutchCompoundDynamicAnalysis":
        from mastapy._private.system_model.analyses_and_results.dynamic_analyses.compound import (
            _6795,
        )

        return self.__parent__._cast(_6795.ClutchCompoundDynamicAnalysis)

    @property
    def clutch_half_compound_dynamic_analysis(
        self: "CastSelf",
    ) -> "_6797.ClutchHalfCompoundDynamicAnalysis":
        from mastapy._private.system_model.analyses_and_results.dynamic_analyses.compound import (
            _6797,
        )

        return self.__parent__._cast(_6797.ClutchHalfCompoundDynamicAnalysis)

    @property
    def component_compound_dynamic_analysis(
        self: "CastSelf",
    ) -> "_6799.ComponentCompoundDynamicAnalysis":
        from mastapy._private.system_model.analyses_and_results.dynamic_analyses.compound import (
            _6799,
        )

        return self.__parent__._cast(_6799.ComponentCompoundDynamicAnalysis)

    @property
    def concept_coupling_compound_dynamic_analysis(
        self: "CastSelf",
    ) -> "_6800.ConceptCouplingCompoundDynamicAnalysis":
        from mastapy._private.system_model.analyses_and_results.dynamic_analyses.compound import (
            _6800,
        )

        return self.__parent__._cast(_6800.ConceptCouplingCompoundDynamicAnalysis)

    @property
    def concept_coupling_half_compound_dynamic_analysis(
        self: "CastSelf",
    ) -> "_6802.ConceptCouplingHalfCompoundDynamicAnalysis":
        from mastapy._private.system_model.analyses_and_results.dynamic_analyses.compound import (
            _6802,
        )

        return self.__parent__._cast(_6802.ConceptCouplingHalfCompoundDynamicAnalysis)

    @property
    def concept_gear_compound_dynamic_analysis(
        self: "CastSelf",
    ) -> "_6803.ConceptGearCompoundDynamicAnalysis":
        from mastapy._private.system_model.analyses_and_results.dynamic_analyses.compound import (
            _6803,
        )

        return self.__parent__._cast(_6803.ConceptGearCompoundDynamicAnalysis)

    @property
    def concept_gear_set_compound_dynamic_analysis(
        self: "CastSelf",
    ) -> "_6805.ConceptGearSetCompoundDynamicAnalysis":
        from mastapy._private.system_model.analyses_and_results.dynamic_analyses.compound import (
            _6805,
        )

        return self.__parent__._cast(_6805.ConceptGearSetCompoundDynamicAnalysis)

    @property
    def conical_gear_compound_dynamic_analysis(
        self: "CastSelf",
    ) -> "_6806.ConicalGearCompoundDynamicAnalysis":
        from mastapy._private.system_model.analyses_and_results.dynamic_analyses.compound import (
            _6806,
        )

        return self.__parent__._cast(_6806.ConicalGearCompoundDynamicAnalysis)

    @property
    def conical_gear_set_compound_dynamic_analysis(
        self: "CastSelf",
    ) -> "_6808.ConicalGearSetCompoundDynamicAnalysis":
        from mastapy._private.system_model.analyses_and_results.dynamic_analyses.compound import (
            _6808,
        )

        return self.__parent__._cast(_6808.ConicalGearSetCompoundDynamicAnalysis)

    @property
    def connector_compound_dynamic_analysis(
        self: "CastSelf",
    ) -> "_6810.ConnectorCompoundDynamicAnalysis":
        from mastapy._private.system_model.analyses_and_results.dynamic_analyses.compound import (
            _6810,
        )

        return self.__parent__._cast(_6810.ConnectorCompoundDynamicAnalysis)

    @property
    def coupling_compound_dynamic_analysis(
        self: "CastSelf",
    ) -> "_6811.CouplingCompoundDynamicAnalysis":
        from mastapy._private.system_model.analyses_and_results.dynamic_analyses.compound import (
            _6811,
        )

        return self.__parent__._cast(_6811.CouplingCompoundDynamicAnalysis)

    @property
    def coupling_half_compound_dynamic_analysis(
        self: "CastSelf",
    ) -> "_6813.CouplingHalfCompoundDynamicAnalysis":
        from mastapy._private.system_model.analyses_and_results.dynamic_analyses.compound import (
            _6813,
        )

        return self.__parent__._cast(_6813.CouplingHalfCompoundDynamicAnalysis)

    @property
    def cvt_compound_dynamic_analysis(
        self: "CastSelf",
    ) -> "_6815.CVTCompoundDynamicAnalysis":
        from mastapy._private.system_model.analyses_and_results.dynamic_analyses.compound import (
            _6815,
        )

        return self.__parent__._cast(_6815.CVTCompoundDynamicAnalysis)

    @property
    def cvt_pulley_compound_dynamic_analysis(
        self: "CastSelf",
    ) -> "_6816.CVTPulleyCompoundDynamicAnalysis":
        from mastapy._private.system_model.analyses_and_results.dynamic_analyses.compound import (
            _6816,
        )

        return self.__parent__._cast(_6816.CVTPulleyCompoundDynamicAnalysis)

    @property
    def cycloidal_assembly_compound_dynamic_analysis(
        self: "CastSelf",
    ) -> "_6817.CycloidalAssemblyCompoundDynamicAnalysis":
        from mastapy._private.system_model.analyses_and_results.dynamic_analyses.compound import (
            _6817,
        )

        return self.__parent__._cast(_6817.CycloidalAssemblyCompoundDynamicAnalysis)

    @property
    def cycloidal_disc_compound_dynamic_analysis(
        self: "CastSelf",
    ) -> "_6819.CycloidalDiscCompoundDynamicAnalysis":
        from mastapy._private.system_model.analyses_and_results.dynamic_analyses.compound import (
            _6819,
        )

        return self.__parent__._cast(_6819.CycloidalDiscCompoundDynamicAnalysis)

    @property
    def cylindrical_gear_compound_dynamic_analysis(
        self: "CastSelf",
    ) -> "_6821.CylindricalGearCompoundDynamicAnalysis":
        from mastapy._private.system_model.analyses_and_results.dynamic_analyses.compound import (
            _6821,
        )

        return self.__parent__._cast(_6821.CylindricalGearCompoundDynamicAnalysis)

    @property
    def cylindrical_gear_set_compound_dynamic_analysis(
        self: "CastSelf",
    ) -> "_6823.CylindricalGearSetCompoundDynamicAnalysis":
        from mastapy._private.system_model.analyses_and_results.dynamic_analyses.compound import (
            _6823,
        )

        return self.__parent__._cast(_6823.CylindricalGearSetCompoundDynamicAnalysis)

    @property
    def cylindrical_planet_gear_compound_dynamic_analysis(
        self: "CastSelf",
    ) -> "_6824.CylindricalPlanetGearCompoundDynamicAnalysis":
        from mastapy._private.system_model.analyses_and_results.dynamic_analyses.compound import (
            _6824,
        )

        return self.__parent__._cast(_6824.CylindricalPlanetGearCompoundDynamicAnalysis)

    @property
    def datum_compound_dynamic_analysis(
        self: "CastSelf",
    ) -> "_6825.DatumCompoundDynamicAnalysis":
        from mastapy._private.system_model.analyses_and_results.dynamic_analyses.compound import (
            _6825,
        )

        return self.__parent__._cast(_6825.DatumCompoundDynamicAnalysis)

    @property
    def external_cad_model_compound_dynamic_analysis(
        self: "CastSelf",
    ) -> "_6826.ExternalCADModelCompoundDynamicAnalysis":
        from mastapy._private.system_model.analyses_and_results.dynamic_analyses.compound import (
            _6826,
        )

        return self.__parent__._cast(_6826.ExternalCADModelCompoundDynamicAnalysis)

    @property
    def face_gear_compound_dynamic_analysis(
        self: "CastSelf",
    ) -> "_6827.FaceGearCompoundDynamicAnalysis":
        from mastapy._private.system_model.analyses_and_results.dynamic_analyses.compound import (
            _6827,
        )

        return self.__parent__._cast(_6827.FaceGearCompoundDynamicAnalysis)

    @property
    def face_gear_set_compound_dynamic_analysis(
        self: "CastSelf",
    ) -> "_6829.FaceGearSetCompoundDynamicAnalysis":
        from mastapy._private.system_model.analyses_and_results.dynamic_analyses.compound import (
            _6829,
        )

        return self.__parent__._cast(_6829.FaceGearSetCompoundDynamicAnalysis)

    @property
    def fe_part_compound_dynamic_analysis(
        self: "CastSelf",
    ) -> "_6830.FEPartCompoundDynamicAnalysis":
        from mastapy._private.system_model.analyses_and_results.dynamic_analyses.compound import (
            _6830,
        )

        return self.__parent__._cast(_6830.FEPartCompoundDynamicAnalysis)

    @property
    def flexible_pin_assembly_compound_dynamic_analysis(
        self: "CastSelf",
    ) -> "_6831.FlexiblePinAssemblyCompoundDynamicAnalysis":
        from mastapy._private.system_model.analyses_and_results.dynamic_analyses.compound import (
            _6831,
        )

        return self.__parent__._cast(_6831.FlexiblePinAssemblyCompoundDynamicAnalysis)

    @property
    def gear_compound_dynamic_analysis(
        self: "CastSelf",
    ) -> "_6832.GearCompoundDynamicAnalysis":
        from mastapy._private.system_model.analyses_and_results.dynamic_analyses.compound import (
            _6832,
        )

        return self.__parent__._cast(_6832.GearCompoundDynamicAnalysis)

    @property
    def gear_set_compound_dynamic_analysis(
        self: "CastSelf",
    ) -> "_6834.GearSetCompoundDynamicAnalysis":
        from mastapy._private.system_model.analyses_and_results.dynamic_analyses.compound import (
            _6834,
        )

        return self.__parent__._cast(_6834.GearSetCompoundDynamicAnalysis)

    @property
    def guide_dxf_model_compound_dynamic_analysis(
        self: "CastSelf",
    ) -> "_6835.GuideDxfModelCompoundDynamicAnalysis":
        from mastapy._private.system_model.analyses_and_results.dynamic_analyses.compound import (
            _6835,
        )

        return self.__parent__._cast(_6835.GuideDxfModelCompoundDynamicAnalysis)

    @property
    def hypoid_gear_compound_dynamic_analysis(
        self: "CastSelf",
    ) -> "_6836.HypoidGearCompoundDynamicAnalysis":
        from mastapy._private.system_model.analyses_and_results.dynamic_analyses.compound import (
            _6836,
        )

        return self.__parent__._cast(_6836.HypoidGearCompoundDynamicAnalysis)

    @property
    def hypoid_gear_set_compound_dynamic_analysis(
        self: "CastSelf",
    ) -> "_6838.HypoidGearSetCompoundDynamicAnalysis":
        from mastapy._private.system_model.analyses_and_results.dynamic_analyses.compound import (
            _6838,
        )

        return self.__parent__._cast(_6838.HypoidGearSetCompoundDynamicAnalysis)

    @property
    def klingelnberg_cyclo_palloid_conical_gear_compound_dynamic_analysis(
        self: "CastSelf",
    ) -> "_6840.KlingelnbergCycloPalloidConicalGearCompoundDynamicAnalysis":
        from mastapy._private.system_model.analyses_and_results.dynamic_analyses.compound import (
            _6840,
        )

        return self.__parent__._cast(
            _6840.KlingelnbergCycloPalloidConicalGearCompoundDynamicAnalysis
        )

    @property
    def klingelnberg_cyclo_palloid_conical_gear_set_compound_dynamic_analysis(
        self: "CastSelf",
    ) -> "_6842.KlingelnbergCycloPalloidConicalGearSetCompoundDynamicAnalysis":
        from mastapy._private.system_model.analyses_and_results.dynamic_analyses.compound import (
            _6842,
        )

        return self.__parent__._cast(
            _6842.KlingelnbergCycloPalloidConicalGearSetCompoundDynamicAnalysis
        )

    @property
    def klingelnberg_cyclo_palloid_hypoid_gear_compound_dynamic_analysis(
        self: "CastSelf",
    ) -> "_6843.KlingelnbergCycloPalloidHypoidGearCompoundDynamicAnalysis":
        from mastapy._private.system_model.analyses_and_results.dynamic_analyses.compound import (
            _6843,
        )

        return self.__parent__._cast(
            _6843.KlingelnbergCycloPalloidHypoidGearCompoundDynamicAnalysis
        )

    @property
    def klingelnberg_cyclo_palloid_hypoid_gear_set_compound_dynamic_analysis(
        self: "CastSelf",
    ) -> "_6845.KlingelnbergCycloPalloidHypoidGearSetCompoundDynamicAnalysis":
        from mastapy._private.system_model.analyses_and_results.dynamic_analyses.compound import (
            _6845,
        )

        return self.__parent__._cast(
            _6845.KlingelnbergCycloPalloidHypoidGearSetCompoundDynamicAnalysis
        )

    @property
    def klingelnberg_cyclo_palloid_spiral_bevel_gear_compound_dynamic_analysis(
        self: "CastSelf",
    ) -> "_6846.KlingelnbergCycloPalloidSpiralBevelGearCompoundDynamicAnalysis":
        from mastapy._private.system_model.analyses_and_results.dynamic_analyses.compound import (
            _6846,
        )

        return self.__parent__._cast(
            _6846.KlingelnbergCycloPalloidSpiralBevelGearCompoundDynamicAnalysis
        )

    @property
    def klingelnberg_cyclo_palloid_spiral_bevel_gear_set_compound_dynamic_analysis(
        self: "CastSelf",
    ) -> "_6848.KlingelnbergCycloPalloidSpiralBevelGearSetCompoundDynamicAnalysis":
        from mastapy._private.system_model.analyses_and_results.dynamic_analyses.compound import (
            _6848,
        )

        return self.__parent__._cast(
            _6848.KlingelnbergCycloPalloidSpiralBevelGearSetCompoundDynamicAnalysis
        )

    @property
    def mass_disc_compound_dynamic_analysis(
        self: "CastSelf",
    ) -> "_6849.MassDiscCompoundDynamicAnalysis":
        from mastapy._private.system_model.analyses_and_results.dynamic_analyses.compound import (
            _6849,
        )

        return self.__parent__._cast(_6849.MassDiscCompoundDynamicAnalysis)

    @property
    def measurement_component_compound_dynamic_analysis(
        self: "CastSelf",
    ) -> "_6850.MeasurementComponentCompoundDynamicAnalysis":
        from mastapy._private.system_model.analyses_and_results.dynamic_analyses.compound import (
            _6850,
        )

        return self.__parent__._cast(_6850.MeasurementComponentCompoundDynamicAnalysis)

    @property
    def microphone_array_compound_dynamic_analysis(
        self: "CastSelf",
    ) -> "_6851.MicrophoneArrayCompoundDynamicAnalysis":
        from mastapy._private.system_model.analyses_and_results.dynamic_analyses.compound import (
            _6851,
        )

        return self.__parent__._cast(_6851.MicrophoneArrayCompoundDynamicAnalysis)

    @property
    def microphone_compound_dynamic_analysis(
        self: "CastSelf",
    ) -> "_6852.MicrophoneCompoundDynamicAnalysis":
        from mastapy._private.system_model.analyses_and_results.dynamic_analyses.compound import (
            _6852,
        )

        return self.__parent__._cast(_6852.MicrophoneCompoundDynamicAnalysis)

    @property
    def mountable_component_compound_dynamic_analysis(
        self: "CastSelf",
    ) -> "_6853.MountableComponentCompoundDynamicAnalysis":
        from mastapy._private.system_model.analyses_and_results.dynamic_analyses.compound import (
            _6853,
        )

        return self.__parent__._cast(_6853.MountableComponentCompoundDynamicAnalysis)

    @property
    def oil_seal_compound_dynamic_analysis(
        self: "CastSelf",
    ) -> "_6854.OilSealCompoundDynamicAnalysis":
        from mastapy._private.system_model.analyses_and_results.dynamic_analyses.compound import (
            _6854,
        )

        return self.__parent__._cast(_6854.OilSealCompoundDynamicAnalysis)

    @property
    def part_to_part_shear_coupling_compound_dynamic_analysis(
        self: "CastSelf",
    ) -> "_6856.PartToPartShearCouplingCompoundDynamicAnalysis":
        from mastapy._private.system_model.analyses_and_results.dynamic_analyses.compound import (
            _6856,
        )

        return self.__parent__._cast(
            _6856.PartToPartShearCouplingCompoundDynamicAnalysis
        )

    @property
    def part_to_part_shear_coupling_half_compound_dynamic_analysis(
        self: "CastSelf",
    ) -> "_6858.PartToPartShearCouplingHalfCompoundDynamicAnalysis":
        from mastapy._private.system_model.analyses_and_results.dynamic_analyses.compound import (
            _6858,
        )

        return self.__parent__._cast(
            _6858.PartToPartShearCouplingHalfCompoundDynamicAnalysis
        )

    @property
    def planetary_gear_set_compound_dynamic_analysis(
        self: "CastSelf",
    ) -> "_6860.PlanetaryGearSetCompoundDynamicAnalysis":
        from mastapy._private.system_model.analyses_and_results.dynamic_analyses.compound import (
            _6860,
        )

        return self.__parent__._cast(_6860.PlanetaryGearSetCompoundDynamicAnalysis)

    @property
    def planet_carrier_compound_dynamic_analysis(
        self: "CastSelf",
    ) -> "_6861.PlanetCarrierCompoundDynamicAnalysis":
        from mastapy._private.system_model.analyses_and_results.dynamic_analyses.compound import (
            _6861,
        )

        return self.__parent__._cast(_6861.PlanetCarrierCompoundDynamicAnalysis)

    @property
    def point_load_compound_dynamic_analysis(
        self: "CastSelf",
    ) -> "_6862.PointLoadCompoundDynamicAnalysis":
        from mastapy._private.system_model.analyses_and_results.dynamic_analyses.compound import (
            _6862,
        )

        return self.__parent__._cast(_6862.PointLoadCompoundDynamicAnalysis)

    @property
    def power_load_compound_dynamic_analysis(
        self: "CastSelf",
    ) -> "_6863.PowerLoadCompoundDynamicAnalysis":
        from mastapy._private.system_model.analyses_and_results.dynamic_analyses.compound import (
            _6863,
        )

        return self.__parent__._cast(_6863.PowerLoadCompoundDynamicAnalysis)

    @property
    def pulley_compound_dynamic_analysis(
        self: "CastSelf",
    ) -> "_6864.PulleyCompoundDynamicAnalysis":
        from mastapy._private.system_model.analyses_and_results.dynamic_analyses.compound import (
            _6864,
        )

        return self.__parent__._cast(_6864.PulleyCompoundDynamicAnalysis)

    @property
    def ring_pins_compound_dynamic_analysis(
        self: "CastSelf",
    ) -> "_6865.RingPinsCompoundDynamicAnalysis":
        from mastapy._private.system_model.analyses_and_results.dynamic_analyses.compound import (
            _6865,
        )

        return self.__parent__._cast(_6865.RingPinsCompoundDynamicAnalysis)

    @property
    def rolling_ring_assembly_compound_dynamic_analysis(
        self: "CastSelf",
    ) -> "_6867.RollingRingAssemblyCompoundDynamicAnalysis":
        from mastapy._private.system_model.analyses_and_results.dynamic_analyses.compound import (
            _6867,
        )

        return self.__parent__._cast(_6867.RollingRingAssemblyCompoundDynamicAnalysis)

    @property
    def rolling_ring_compound_dynamic_analysis(
        self: "CastSelf",
    ) -> "_6868.RollingRingCompoundDynamicAnalysis":
        from mastapy._private.system_model.analyses_and_results.dynamic_analyses.compound import (
            _6868,
        )

        return self.__parent__._cast(_6868.RollingRingCompoundDynamicAnalysis)

    @property
    def root_assembly_compound_dynamic_analysis(
        self: "CastSelf",
    ) -> "_6870.RootAssemblyCompoundDynamicAnalysis":
        from mastapy._private.system_model.analyses_and_results.dynamic_analyses.compound import (
            _6870,
        )

        return self.__parent__._cast(_6870.RootAssemblyCompoundDynamicAnalysis)

    @property
    def shaft_compound_dynamic_analysis(
        self: "CastSelf",
    ) -> "_6871.ShaftCompoundDynamicAnalysis":
        from mastapy._private.system_model.analyses_and_results.dynamic_analyses.compound import (
            _6871,
        )

        return self.__parent__._cast(_6871.ShaftCompoundDynamicAnalysis)

    @property
    def shaft_hub_connection_compound_dynamic_analysis(
        self: "CastSelf",
    ) -> "_6872.ShaftHubConnectionCompoundDynamicAnalysis":
        from mastapy._private.system_model.analyses_and_results.dynamic_analyses.compound import (
            _6872,
        )

        return self.__parent__._cast(_6872.ShaftHubConnectionCompoundDynamicAnalysis)

    @property
    def specialised_assembly_compound_dynamic_analysis(
        self: "CastSelf",
    ) -> "_6874.SpecialisedAssemblyCompoundDynamicAnalysis":
        from mastapy._private.system_model.analyses_and_results.dynamic_analyses.compound import (
            _6874,
        )

        return self.__parent__._cast(_6874.SpecialisedAssemblyCompoundDynamicAnalysis)

    @property
    def spiral_bevel_gear_compound_dynamic_analysis(
        self: "CastSelf",
    ) -> "_6875.SpiralBevelGearCompoundDynamicAnalysis":
        from mastapy._private.system_model.analyses_and_results.dynamic_analyses.compound import (
            _6875,
        )

        return self.__parent__._cast(_6875.SpiralBevelGearCompoundDynamicAnalysis)

    @property
    def spiral_bevel_gear_set_compound_dynamic_analysis(
        self: "CastSelf",
    ) -> "_6877.SpiralBevelGearSetCompoundDynamicAnalysis":
        from mastapy._private.system_model.analyses_and_results.dynamic_analyses.compound import (
            _6877,
        )

        return self.__parent__._cast(_6877.SpiralBevelGearSetCompoundDynamicAnalysis)

    @property
    def spring_damper_compound_dynamic_analysis(
        self: "CastSelf",
    ) -> "_6878.SpringDamperCompoundDynamicAnalysis":
        from mastapy._private.system_model.analyses_and_results.dynamic_analyses.compound import (
            _6878,
        )

        return self.__parent__._cast(_6878.SpringDamperCompoundDynamicAnalysis)

    @property
    def spring_damper_half_compound_dynamic_analysis(
        self: "CastSelf",
    ) -> "_6880.SpringDamperHalfCompoundDynamicAnalysis":
        from mastapy._private.system_model.analyses_and_results.dynamic_analyses.compound import (
            _6880,
        )

        return self.__parent__._cast(_6880.SpringDamperHalfCompoundDynamicAnalysis)

    @property
    def straight_bevel_diff_gear_compound_dynamic_analysis(
        self: "CastSelf",
    ) -> "_6881.StraightBevelDiffGearCompoundDynamicAnalysis":
        from mastapy._private.system_model.analyses_and_results.dynamic_analyses.compound import (
            _6881,
        )

        return self.__parent__._cast(_6881.StraightBevelDiffGearCompoundDynamicAnalysis)

    @property
    def straight_bevel_diff_gear_set_compound_dynamic_analysis(
        self: "CastSelf",
    ) -> "_6883.StraightBevelDiffGearSetCompoundDynamicAnalysis":
        from mastapy._private.system_model.analyses_and_results.dynamic_analyses.compound import (
            _6883,
        )

        return self.__parent__._cast(
            _6883.StraightBevelDiffGearSetCompoundDynamicAnalysis
        )

    @property
    def straight_bevel_gear_compound_dynamic_analysis(
        self: "CastSelf",
    ) -> "_6884.StraightBevelGearCompoundDynamicAnalysis":
        from mastapy._private.system_model.analyses_and_results.dynamic_analyses.compound import (
            _6884,
        )

        return self.__parent__._cast(_6884.StraightBevelGearCompoundDynamicAnalysis)

    @property
    def straight_bevel_gear_set_compound_dynamic_analysis(
        self: "CastSelf",
    ) -> "_6886.StraightBevelGearSetCompoundDynamicAnalysis":
        from mastapy._private.system_model.analyses_and_results.dynamic_analyses.compound import (
            _6886,
        )

        return self.__parent__._cast(_6886.StraightBevelGearSetCompoundDynamicAnalysis)

    @property
    def straight_bevel_planet_gear_compound_dynamic_analysis(
        self: "CastSelf",
    ) -> "_6887.StraightBevelPlanetGearCompoundDynamicAnalysis":
        from mastapy._private.system_model.analyses_and_results.dynamic_analyses.compound import (
            _6887,
        )

        return self.__parent__._cast(
            _6887.StraightBevelPlanetGearCompoundDynamicAnalysis
        )

    @property
    def straight_bevel_sun_gear_compound_dynamic_analysis(
        self: "CastSelf",
    ) -> "_6888.StraightBevelSunGearCompoundDynamicAnalysis":
        from mastapy._private.system_model.analyses_and_results.dynamic_analyses.compound import (
            _6888,
        )

        return self.__parent__._cast(_6888.StraightBevelSunGearCompoundDynamicAnalysis)

    @property
    def synchroniser_compound_dynamic_analysis(
        self: "CastSelf",
    ) -> "_6889.SynchroniserCompoundDynamicAnalysis":
        from mastapy._private.system_model.analyses_and_results.dynamic_analyses.compound import (
            _6889,
        )

        return self.__parent__._cast(_6889.SynchroniserCompoundDynamicAnalysis)

    @property
    def synchroniser_half_compound_dynamic_analysis(
        self: "CastSelf",
    ) -> "_6890.SynchroniserHalfCompoundDynamicAnalysis":
        from mastapy._private.system_model.analyses_and_results.dynamic_analyses.compound import (
            _6890,
        )

        return self.__parent__._cast(_6890.SynchroniserHalfCompoundDynamicAnalysis)

    @property
    def synchroniser_part_compound_dynamic_analysis(
        self: "CastSelf",
    ) -> "_6891.SynchroniserPartCompoundDynamicAnalysis":
        from mastapy._private.system_model.analyses_and_results.dynamic_analyses.compound import (
            _6891,
        )

        return self.__parent__._cast(_6891.SynchroniserPartCompoundDynamicAnalysis)

    @property
    def synchroniser_sleeve_compound_dynamic_analysis(
        self: "CastSelf",
    ) -> "_6892.SynchroniserSleeveCompoundDynamicAnalysis":
        from mastapy._private.system_model.analyses_and_results.dynamic_analyses.compound import (
            _6892,
        )

        return self.__parent__._cast(_6892.SynchroniserSleeveCompoundDynamicAnalysis)

    @property
    def torque_converter_compound_dynamic_analysis(
        self: "CastSelf",
    ) -> "_6893.TorqueConverterCompoundDynamicAnalysis":
        from mastapy._private.system_model.analyses_and_results.dynamic_analyses.compound import (
            _6893,
        )

        return self.__parent__._cast(_6893.TorqueConverterCompoundDynamicAnalysis)

    @property
    def torque_converter_pump_compound_dynamic_analysis(
        self: "CastSelf",
    ) -> "_6895.TorqueConverterPumpCompoundDynamicAnalysis":
        from mastapy._private.system_model.analyses_and_results.dynamic_analyses.compound import (
            _6895,
        )

        return self.__parent__._cast(_6895.TorqueConverterPumpCompoundDynamicAnalysis)

    @property
    def torque_converter_turbine_compound_dynamic_analysis(
        self: "CastSelf",
    ) -> "_6896.TorqueConverterTurbineCompoundDynamicAnalysis":
        from mastapy._private.system_model.analyses_and_results.dynamic_analyses.compound import (
            _6896,
        )

        return self.__parent__._cast(
            _6896.TorqueConverterTurbineCompoundDynamicAnalysis
        )

    @property
    def unbalanced_mass_compound_dynamic_analysis(
        self: "CastSelf",
    ) -> "_6897.UnbalancedMassCompoundDynamicAnalysis":
        from mastapy._private.system_model.analyses_and_results.dynamic_analyses.compound import (
            _6897,
        )

        return self.__parent__._cast(_6897.UnbalancedMassCompoundDynamicAnalysis)

    @property
    def virtual_component_compound_dynamic_analysis(
        self: "CastSelf",
    ) -> "_6898.VirtualComponentCompoundDynamicAnalysis":
        from mastapy._private.system_model.analyses_and_results.dynamic_analyses.compound import (
            _6898,
        )

        return self.__parent__._cast(_6898.VirtualComponentCompoundDynamicAnalysis)

    @property
    def worm_gear_compound_dynamic_analysis(
        self: "CastSelf",
    ) -> "_6899.WormGearCompoundDynamicAnalysis":
        from mastapy._private.system_model.analyses_and_results.dynamic_analyses.compound import (
            _6899,
        )

        return self.__parent__._cast(_6899.WormGearCompoundDynamicAnalysis)

    @property
    def worm_gear_set_compound_dynamic_analysis(
        self: "CastSelf",
    ) -> "_6901.WormGearSetCompoundDynamicAnalysis":
        from mastapy._private.system_model.analyses_and_results.dynamic_analyses.compound import (
            _6901,
        )

        return self.__parent__._cast(_6901.WormGearSetCompoundDynamicAnalysis)

    @property
    def zerol_bevel_gear_compound_dynamic_analysis(
        self: "CastSelf",
    ) -> "_6902.ZerolBevelGearCompoundDynamicAnalysis":
        from mastapy._private.system_model.analyses_and_results.dynamic_analyses.compound import (
            _6902,
        )

        return self.__parent__._cast(_6902.ZerolBevelGearCompoundDynamicAnalysis)

    @property
    def zerol_bevel_gear_set_compound_dynamic_analysis(
        self: "CastSelf",
    ) -> "_6904.ZerolBevelGearSetCompoundDynamicAnalysis":
        from mastapy._private.system_model.analyses_and_results.dynamic_analyses.compound import (
            _6904,
        )

        return self.__parent__._cast(_6904.ZerolBevelGearSetCompoundDynamicAnalysis)

    @property
    def part_compound_dynamic_analysis(
        self: "CastSelf",
    ) -> "PartCompoundDynamicAnalysis":
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
class PartCompoundDynamicAnalysis(_7942.PartCompoundAnalysis):
    """PartCompoundDynamicAnalysis

    This is a mastapy class.
    """

    TYPE: ClassVar["Type"] = _PART_COMPOUND_DYNAMIC_ANALYSIS

    wrapped: "Any"

    def __post_init__(self: "Self") -> None:
        """Override of the post initialisation magic method."""
        if not hasattr(self.wrapped, "reference_count"):
            self.wrapped.reference_count = 0

        self.wrapped.reference_count += 1

    @property
    @exception_bridge
    def component_analysis_cases(self: "Self") -> "List[_6724.PartDynamicAnalysis]":
        """List[mastapy.system_model.analyses_and_results.dynamic_analyses.PartDynamicAnalysis]

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
    ) -> "List[_6724.PartDynamicAnalysis]":
        """List[mastapy.system_model.analyses_and_results.dynamic_analyses.PartDynamicAnalysis]

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
    def cast_to(self: "Self") -> "_Cast_PartCompoundDynamicAnalysis":
        """Cast to another type.

        Returns:
            _Cast_PartCompoundDynamicAnalysis
        """
        return _Cast_PartCompoundDynamicAnalysis(self)
