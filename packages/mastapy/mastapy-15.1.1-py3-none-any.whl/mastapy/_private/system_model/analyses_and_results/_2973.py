"""CompoundSystemDeflection"""

from __future__ import annotations

from typing import TYPE_CHECKING, ClassVar

from mastapy._private._internal.dataclasses import extended_dataclass
from mastapy._private._internal.exception_bridge import exception_bridge
from mastapy._private._internal.exceptions import CastException
from mastapy._private._internal.python_net import (
    python_net_import,
    pythonnet_method_call_overload,
)
from mastapy._private._internal.type_enforcement import enforce_parameter_types

from mastapy._private._internal import conversion, utility
from mastapy._private.system_model.analyses_and_results import _2939

_CONCEPT_COUPLING_CONNECTION = python_net_import(
    "SMT.MastaAPI.SystemModel.ConnectionsAndSockets.Couplings",
    "ConceptCouplingConnection",
)
_COUPLING_CONNECTION = python_net_import(
    "SMT.MastaAPI.SystemModel.ConnectionsAndSockets.Couplings", "CouplingConnection"
)
_SPRING_DAMPER_CONNECTION = python_net_import(
    "SMT.MastaAPI.SystemModel.ConnectionsAndSockets.Couplings", "SpringDamperConnection"
)
_TORQUE_CONVERTER_CONNECTION = python_net_import(
    "SMT.MastaAPI.SystemModel.ConnectionsAndSockets.Couplings",
    "TorqueConverterConnection",
)
_PART_TO_PART_SHEAR_COUPLING_CONNECTION = python_net_import(
    "SMT.MastaAPI.SystemModel.ConnectionsAndSockets.Couplings",
    "PartToPartShearCouplingConnection",
)
_CLUTCH_CONNECTION = python_net_import(
    "SMT.MastaAPI.SystemModel.ConnectionsAndSockets.Couplings", "ClutchConnection"
)
_ABSTRACT_SHAFT = python_net_import(
    "SMT.MastaAPI.SystemModel.PartModel", "AbstractShaft"
)
_MICROPHONE = python_net_import("SMT.MastaAPI.SystemModel.PartModel", "Microphone")
_MICROPHONE_ARRAY = python_net_import(
    "SMT.MastaAPI.SystemModel.PartModel", "MicrophoneArray"
)
_ABSTRACT_ASSEMBLY = python_net_import(
    "SMT.MastaAPI.SystemModel.PartModel", "AbstractAssembly"
)
_ABSTRACT_SHAFT_OR_HOUSING = python_net_import(
    "SMT.MastaAPI.SystemModel.PartModel", "AbstractShaftOrHousing"
)
_BEARING = python_net_import("SMT.MastaAPI.SystemModel.PartModel", "Bearing")
_BOLT = python_net_import("SMT.MastaAPI.SystemModel.PartModel", "Bolt")
_BOLTED_JOINT = python_net_import("SMT.MastaAPI.SystemModel.PartModel", "BoltedJoint")
_COMPONENT = python_net_import("SMT.MastaAPI.SystemModel.PartModel", "Component")
_CONNECTOR = python_net_import("SMT.MastaAPI.SystemModel.PartModel", "Connector")
_DATUM = python_net_import("SMT.MastaAPI.SystemModel.PartModel", "Datum")
_EXTERNAL_CAD_MODEL = python_net_import(
    "SMT.MastaAPI.SystemModel.PartModel", "ExternalCADModel"
)
_FE_PART = python_net_import("SMT.MastaAPI.SystemModel.PartModel", "FEPart")
_FLEXIBLE_PIN_ASSEMBLY = python_net_import(
    "SMT.MastaAPI.SystemModel.PartModel", "FlexiblePinAssembly"
)
_ASSEMBLY = python_net_import("SMT.MastaAPI.SystemModel.PartModel", "Assembly")
_GUIDE_DXF_MODEL = python_net_import(
    "SMT.MastaAPI.SystemModel.PartModel", "GuideDxfModel"
)
_MASS_DISC = python_net_import("SMT.MastaAPI.SystemModel.PartModel", "MassDisc")
_MEASUREMENT_COMPONENT = python_net_import(
    "SMT.MastaAPI.SystemModel.PartModel", "MeasurementComponent"
)
_MOUNTABLE_COMPONENT = python_net_import(
    "SMT.MastaAPI.SystemModel.PartModel", "MountableComponent"
)
_OIL_SEAL = python_net_import("SMT.MastaAPI.SystemModel.PartModel", "OilSeal")
_PART = python_net_import("SMT.MastaAPI.SystemModel.PartModel", "Part")
_PLANET_CARRIER = python_net_import(
    "SMT.MastaAPI.SystemModel.PartModel", "PlanetCarrier"
)
_POINT_LOAD = python_net_import("SMT.MastaAPI.SystemModel.PartModel", "PointLoad")
_POWER_LOAD = python_net_import("SMT.MastaAPI.SystemModel.PartModel", "PowerLoad")
_ROOT_ASSEMBLY = python_net_import("SMT.MastaAPI.SystemModel.PartModel", "RootAssembly")
_SPECIALISED_ASSEMBLY = python_net_import(
    "SMT.MastaAPI.SystemModel.PartModel", "SpecialisedAssembly"
)
_UNBALANCED_MASS = python_net_import(
    "SMT.MastaAPI.SystemModel.PartModel", "UnbalancedMass"
)
_VIRTUAL_COMPONENT = python_net_import(
    "SMT.MastaAPI.SystemModel.PartModel", "VirtualComponent"
)
_SHAFT = python_net_import("SMT.MastaAPI.SystemModel.PartModel.ShaftModel", "Shaft")
_CONCEPT_GEAR = python_net_import(
    "SMT.MastaAPI.SystemModel.PartModel.Gears", "ConceptGear"
)
_CONCEPT_GEAR_SET = python_net_import(
    "SMT.MastaAPI.SystemModel.PartModel.Gears", "ConceptGearSet"
)
_FACE_GEAR = python_net_import("SMT.MastaAPI.SystemModel.PartModel.Gears", "FaceGear")
_FACE_GEAR_SET = python_net_import(
    "SMT.MastaAPI.SystemModel.PartModel.Gears", "FaceGearSet"
)
_AGMA_GLEASON_CONICAL_GEAR = python_net_import(
    "SMT.MastaAPI.SystemModel.PartModel.Gears", "AGMAGleasonConicalGear"
)
_AGMA_GLEASON_CONICAL_GEAR_SET = python_net_import(
    "SMT.MastaAPI.SystemModel.PartModel.Gears", "AGMAGleasonConicalGearSet"
)
_BEVEL_DIFFERENTIAL_GEAR = python_net_import(
    "SMT.MastaAPI.SystemModel.PartModel.Gears", "BevelDifferentialGear"
)
_BEVEL_DIFFERENTIAL_GEAR_SET = python_net_import(
    "SMT.MastaAPI.SystemModel.PartModel.Gears", "BevelDifferentialGearSet"
)
_BEVEL_DIFFERENTIAL_PLANET_GEAR = python_net_import(
    "SMT.MastaAPI.SystemModel.PartModel.Gears", "BevelDifferentialPlanetGear"
)
_BEVEL_DIFFERENTIAL_SUN_GEAR = python_net_import(
    "SMT.MastaAPI.SystemModel.PartModel.Gears", "BevelDifferentialSunGear"
)
_BEVEL_GEAR = python_net_import("SMT.MastaAPI.SystemModel.PartModel.Gears", "BevelGear")
_BEVEL_GEAR_SET = python_net_import(
    "SMT.MastaAPI.SystemModel.PartModel.Gears", "BevelGearSet"
)
_CONICAL_GEAR = python_net_import(
    "SMT.MastaAPI.SystemModel.PartModel.Gears", "ConicalGear"
)
_CONICAL_GEAR_SET = python_net_import(
    "SMT.MastaAPI.SystemModel.PartModel.Gears", "ConicalGearSet"
)
_CYLINDRICAL_GEAR = python_net_import(
    "SMT.MastaAPI.SystemModel.PartModel.Gears", "CylindricalGear"
)
_CYLINDRICAL_GEAR_SET = python_net_import(
    "SMT.MastaAPI.SystemModel.PartModel.Gears", "CylindricalGearSet"
)
_CYLINDRICAL_PLANET_GEAR = python_net_import(
    "SMT.MastaAPI.SystemModel.PartModel.Gears", "CylindricalPlanetGear"
)
_GEAR = python_net_import("SMT.MastaAPI.SystemModel.PartModel.Gears", "Gear")
_GEAR_SET = python_net_import("SMT.MastaAPI.SystemModel.PartModel.Gears", "GearSet")
_HYPOID_GEAR = python_net_import(
    "SMT.MastaAPI.SystemModel.PartModel.Gears", "HypoidGear"
)
_HYPOID_GEAR_SET = python_net_import(
    "SMT.MastaAPI.SystemModel.PartModel.Gears", "HypoidGearSet"
)
_KLINGELNBERG_CYCLO_PALLOID_CONICAL_GEAR = python_net_import(
    "SMT.MastaAPI.SystemModel.PartModel.Gears", "KlingelnbergCycloPalloidConicalGear"
)
_KLINGELNBERG_CYCLO_PALLOID_CONICAL_GEAR_SET = python_net_import(
    "SMT.MastaAPI.SystemModel.PartModel.Gears", "KlingelnbergCycloPalloidConicalGearSet"
)
_KLINGELNBERG_CYCLO_PALLOID_HYPOID_GEAR = python_net_import(
    "SMT.MastaAPI.SystemModel.PartModel.Gears", "KlingelnbergCycloPalloidHypoidGear"
)
_KLINGELNBERG_CYCLO_PALLOID_HYPOID_GEAR_SET = python_net_import(
    "SMT.MastaAPI.SystemModel.PartModel.Gears", "KlingelnbergCycloPalloidHypoidGearSet"
)
_KLINGELNBERG_CYCLO_PALLOID_SPIRAL_BEVEL_GEAR = python_net_import(
    "SMT.MastaAPI.SystemModel.PartModel.Gears",
    "KlingelnbergCycloPalloidSpiralBevelGear",
)
_KLINGELNBERG_CYCLO_PALLOID_SPIRAL_BEVEL_GEAR_SET = python_net_import(
    "SMT.MastaAPI.SystemModel.PartModel.Gears",
    "KlingelnbergCycloPalloidSpiralBevelGearSet",
)
_PLANETARY_GEAR_SET = python_net_import(
    "SMT.MastaAPI.SystemModel.PartModel.Gears", "PlanetaryGearSet"
)
_SPIRAL_BEVEL_GEAR = python_net_import(
    "SMT.MastaAPI.SystemModel.PartModel.Gears", "SpiralBevelGear"
)
_SPIRAL_BEVEL_GEAR_SET = python_net_import(
    "SMT.MastaAPI.SystemModel.PartModel.Gears", "SpiralBevelGearSet"
)
_STRAIGHT_BEVEL_DIFF_GEAR = python_net_import(
    "SMT.MastaAPI.SystemModel.PartModel.Gears", "StraightBevelDiffGear"
)
_STRAIGHT_BEVEL_DIFF_GEAR_SET = python_net_import(
    "SMT.MastaAPI.SystemModel.PartModel.Gears", "StraightBevelDiffGearSet"
)
_STRAIGHT_BEVEL_GEAR = python_net_import(
    "SMT.MastaAPI.SystemModel.PartModel.Gears", "StraightBevelGear"
)
_STRAIGHT_BEVEL_GEAR_SET = python_net_import(
    "SMT.MastaAPI.SystemModel.PartModel.Gears", "StraightBevelGearSet"
)
_STRAIGHT_BEVEL_PLANET_GEAR = python_net_import(
    "SMT.MastaAPI.SystemModel.PartModel.Gears", "StraightBevelPlanetGear"
)
_STRAIGHT_BEVEL_SUN_GEAR = python_net_import(
    "SMT.MastaAPI.SystemModel.PartModel.Gears", "StraightBevelSunGear"
)
_WORM_GEAR = python_net_import("SMT.MastaAPI.SystemModel.PartModel.Gears", "WormGear")
_WORM_GEAR_SET = python_net_import(
    "SMT.MastaAPI.SystemModel.PartModel.Gears", "WormGearSet"
)
_ZEROL_BEVEL_GEAR = python_net_import(
    "SMT.MastaAPI.SystemModel.PartModel.Gears", "ZerolBevelGear"
)
_ZEROL_BEVEL_GEAR_SET = python_net_import(
    "SMT.MastaAPI.SystemModel.PartModel.Gears", "ZerolBevelGearSet"
)
_CYCLOIDAL_ASSEMBLY = python_net_import(
    "SMT.MastaAPI.SystemModel.PartModel.Cycloidal", "CycloidalAssembly"
)
_CYCLOIDAL_DISC = python_net_import(
    "SMT.MastaAPI.SystemModel.PartModel.Cycloidal", "CycloidalDisc"
)
_RING_PINS = python_net_import(
    "SMT.MastaAPI.SystemModel.PartModel.Cycloidal", "RingPins"
)
_PART_TO_PART_SHEAR_COUPLING = python_net_import(
    "SMT.MastaAPI.SystemModel.PartModel.Couplings", "PartToPartShearCoupling"
)
_PART_TO_PART_SHEAR_COUPLING_HALF = python_net_import(
    "SMT.MastaAPI.SystemModel.PartModel.Couplings", "PartToPartShearCouplingHalf"
)
_BELT_DRIVE = python_net_import(
    "SMT.MastaAPI.SystemModel.PartModel.Couplings", "BeltDrive"
)
_CLUTCH = python_net_import("SMT.MastaAPI.SystemModel.PartModel.Couplings", "Clutch")
_CLUTCH_HALF = python_net_import(
    "SMT.MastaAPI.SystemModel.PartModel.Couplings", "ClutchHalf"
)
_CONCEPT_COUPLING = python_net_import(
    "SMT.MastaAPI.SystemModel.PartModel.Couplings", "ConceptCoupling"
)
_CONCEPT_COUPLING_HALF = python_net_import(
    "SMT.MastaAPI.SystemModel.PartModel.Couplings", "ConceptCouplingHalf"
)
_COUPLING = python_net_import(
    "SMT.MastaAPI.SystemModel.PartModel.Couplings", "Coupling"
)
_COUPLING_HALF = python_net_import(
    "SMT.MastaAPI.SystemModel.PartModel.Couplings", "CouplingHalf"
)
_CVT = python_net_import("SMT.MastaAPI.SystemModel.PartModel.Couplings", "CVT")
_CVT_PULLEY = python_net_import(
    "SMT.MastaAPI.SystemModel.PartModel.Couplings", "CVTPulley"
)
_PULLEY = python_net_import("SMT.MastaAPI.SystemModel.PartModel.Couplings", "Pulley")
_SHAFT_HUB_CONNECTION = python_net_import(
    "SMT.MastaAPI.SystemModel.PartModel.Couplings", "ShaftHubConnection"
)
_ROLLING_RING = python_net_import(
    "SMT.MastaAPI.SystemModel.PartModel.Couplings", "RollingRing"
)
_ROLLING_RING_ASSEMBLY = python_net_import(
    "SMT.MastaAPI.SystemModel.PartModel.Couplings", "RollingRingAssembly"
)
_SPRING_DAMPER = python_net_import(
    "SMT.MastaAPI.SystemModel.PartModel.Couplings", "SpringDamper"
)
_SPRING_DAMPER_HALF = python_net_import(
    "SMT.MastaAPI.SystemModel.PartModel.Couplings", "SpringDamperHalf"
)
_SYNCHRONISER = python_net_import(
    "SMT.MastaAPI.SystemModel.PartModel.Couplings", "Synchroniser"
)
_SYNCHRONISER_HALF = python_net_import(
    "SMT.MastaAPI.SystemModel.PartModel.Couplings", "SynchroniserHalf"
)
_SYNCHRONISER_PART = python_net_import(
    "SMT.MastaAPI.SystemModel.PartModel.Couplings", "SynchroniserPart"
)
_SYNCHRONISER_SLEEVE = python_net_import(
    "SMT.MastaAPI.SystemModel.PartModel.Couplings", "SynchroniserSleeve"
)
_TORQUE_CONVERTER = python_net_import(
    "SMT.MastaAPI.SystemModel.PartModel.Couplings", "TorqueConverter"
)
_TORQUE_CONVERTER_PUMP = python_net_import(
    "SMT.MastaAPI.SystemModel.PartModel.Couplings", "TorqueConverterPump"
)
_TORQUE_CONVERTER_TURBINE = python_net_import(
    "SMT.MastaAPI.SystemModel.PartModel.Couplings", "TorqueConverterTurbine"
)
_SHAFT_TO_MOUNTABLE_COMPONENT_CONNECTION = python_net_import(
    "SMT.MastaAPI.SystemModel.ConnectionsAndSockets",
    "ShaftToMountableComponentConnection",
)
_CVT_BELT_CONNECTION = python_net_import(
    "SMT.MastaAPI.SystemModel.ConnectionsAndSockets", "CVTBeltConnection"
)
_BELT_CONNECTION = python_net_import(
    "SMT.MastaAPI.SystemModel.ConnectionsAndSockets", "BeltConnection"
)
_COAXIAL_CONNECTION = python_net_import(
    "SMT.MastaAPI.SystemModel.ConnectionsAndSockets", "CoaxialConnection"
)
_CONNECTION = python_net_import(
    "SMT.MastaAPI.SystemModel.ConnectionsAndSockets", "Connection"
)
_INTER_MOUNTABLE_COMPONENT_CONNECTION = python_net_import(
    "SMT.MastaAPI.SystemModel.ConnectionsAndSockets",
    "InterMountableComponentConnection",
)
_PLANETARY_CONNECTION = python_net_import(
    "SMT.MastaAPI.SystemModel.ConnectionsAndSockets", "PlanetaryConnection"
)
_ROLLING_RING_CONNECTION = python_net_import(
    "SMT.MastaAPI.SystemModel.ConnectionsAndSockets", "RollingRingConnection"
)
_ABSTRACT_SHAFT_TO_MOUNTABLE_COMPONENT_CONNECTION = python_net_import(
    "SMT.MastaAPI.SystemModel.ConnectionsAndSockets",
    "AbstractShaftToMountableComponentConnection",
)
_BEVEL_DIFFERENTIAL_GEAR_MESH = python_net_import(
    "SMT.MastaAPI.SystemModel.ConnectionsAndSockets.Gears", "BevelDifferentialGearMesh"
)
_CONCEPT_GEAR_MESH = python_net_import(
    "SMT.MastaAPI.SystemModel.ConnectionsAndSockets.Gears", "ConceptGearMesh"
)
_FACE_GEAR_MESH = python_net_import(
    "SMT.MastaAPI.SystemModel.ConnectionsAndSockets.Gears", "FaceGearMesh"
)
_STRAIGHT_BEVEL_DIFF_GEAR_MESH = python_net_import(
    "SMT.MastaAPI.SystemModel.ConnectionsAndSockets.Gears", "StraightBevelDiffGearMesh"
)
_BEVEL_GEAR_MESH = python_net_import(
    "SMT.MastaAPI.SystemModel.ConnectionsAndSockets.Gears", "BevelGearMesh"
)
_CONICAL_GEAR_MESH = python_net_import(
    "SMT.MastaAPI.SystemModel.ConnectionsAndSockets.Gears", "ConicalGearMesh"
)
_AGMA_GLEASON_CONICAL_GEAR_MESH = python_net_import(
    "SMT.MastaAPI.SystemModel.ConnectionsAndSockets.Gears", "AGMAGleasonConicalGearMesh"
)
_CYLINDRICAL_GEAR_MESH = python_net_import(
    "SMT.MastaAPI.SystemModel.ConnectionsAndSockets.Gears", "CylindricalGearMesh"
)
_HYPOID_GEAR_MESH = python_net_import(
    "SMT.MastaAPI.SystemModel.ConnectionsAndSockets.Gears", "HypoidGearMesh"
)
_KLINGELNBERG_CYCLO_PALLOID_CONICAL_GEAR_MESH = python_net_import(
    "SMT.MastaAPI.SystemModel.ConnectionsAndSockets.Gears",
    "KlingelnbergCycloPalloidConicalGearMesh",
)
_KLINGELNBERG_CYCLO_PALLOID_HYPOID_GEAR_MESH = python_net_import(
    "SMT.MastaAPI.SystemModel.ConnectionsAndSockets.Gears",
    "KlingelnbergCycloPalloidHypoidGearMesh",
)
_KLINGELNBERG_CYCLO_PALLOID_SPIRAL_BEVEL_GEAR_MESH = python_net_import(
    "SMT.MastaAPI.SystemModel.ConnectionsAndSockets.Gears",
    "KlingelnbergCycloPalloidSpiralBevelGearMesh",
)
_SPIRAL_BEVEL_GEAR_MESH = python_net_import(
    "SMT.MastaAPI.SystemModel.ConnectionsAndSockets.Gears", "SpiralBevelGearMesh"
)
_STRAIGHT_BEVEL_GEAR_MESH = python_net_import(
    "SMT.MastaAPI.SystemModel.ConnectionsAndSockets.Gears", "StraightBevelGearMesh"
)
_WORM_GEAR_MESH = python_net_import(
    "SMT.MastaAPI.SystemModel.ConnectionsAndSockets.Gears", "WormGearMesh"
)
_ZEROL_BEVEL_GEAR_MESH = python_net_import(
    "SMT.MastaAPI.SystemModel.ConnectionsAndSockets.Gears", "ZerolBevelGearMesh"
)
_GEAR_MESH = python_net_import(
    "SMT.MastaAPI.SystemModel.ConnectionsAndSockets.Gears", "GearMesh"
)
_CYCLOIDAL_DISC_CENTRAL_BEARING_CONNECTION = python_net_import(
    "SMT.MastaAPI.SystemModel.ConnectionsAndSockets.Cycloidal",
    "CycloidalDiscCentralBearingConnection",
)
_CYCLOIDAL_DISC_PLANETARY_BEARING_CONNECTION = python_net_import(
    "SMT.MastaAPI.SystemModel.ConnectionsAndSockets.Cycloidal",
    "CycloidalDiscPlanetaryBearingConnection",
)
_RING_PINS_TO_DISC_CONNECTION = python_net_import(
    "SMT.MastaAPI.SystemModel.ConnectionsAndSockets.Cycloidal",
    "RingPinsToDiscConnection",
)
_COMPOUND_SYSTEM_DEFLECTION = python_net_import(
    "SMT.MastaAPI.SystemModel.AnalysesAndResults", "CompoundSystemDeflection"
)

if TYPE_CHECKING:
    from typing import Any, Iterable, Type, TypeVar

    from mastapy._private import _7949
    from mastapy._private.system_model.analyses_and_results.system_deflections.compound import (
        _3146,
        _3147,
        _3148,
        _3149,
        _3150,
        _3151,
        _3152,
        _3153,
        _3154,
        _3155,
        _3156,
        _3157,
        _3158,
        _3159,
        _3160,
        _3161,
        _3162,
        _3163,
        _3164,
        _3165,
        _3166,
        _3167,
        _3168,
        _3169,
        _3170,
        _3171,
        _3172,
        _3173,
        _3174,
        _3175,
        _3176,
        _3177,
        _3178,
        _3179,
        _3180,
        _3181,
        _3182,
        _3183,
        _3184,
        _3185,
        _3186,
        _3187,
        _3188,
        _3189,
        _3190,
        _3191,
        _3192,
        _3193,
        _3194,
        _3195,
        _3196,
        _3197,
        _3199,
        _3200,
        _3201,
        _3202,
        _3203,
        _3204,
        _3205,
        _3206,
        _3207,
        _3208,
        _3209,
        _3210,
        _3211,
        _3212,
        _3213,
        _3214,
        _3215,
        _3216,
        _3217,
        _3218,
        _3219,
        _3220,
        _3221,
        _3222,
        _3223,
        _3224,
        _3225,
        _3226,
        _3227,
        _3228,
        _3229,
        _3230,
        _3231,
        _3232,
        _3233,
        _3234,
        _3235,
        _3236,
        _3237,
        _3238,
        _3239,
        _3240,
        _3241,
        _3242,
        _3243,
        _3244,
        _3246,
        _3247,
        _3248,
        _3249,
        _3250,
        _3251,
        _3252,
        _3253,
        _3254,
        _3255,
        _3256,
        _3257,
        _3258,
        _3259,
        _3260,
        _3261,
        _3262,
        _3263,
        _3264,
        _3265,
        _3266,
        _3267,
        _3268,
        _3269,
        _3270,
        _3271,
        _3272,
        _3273,
        _3274,
        _3275,
        _3276,
        _3277,
        _3278,
    )
    from mastapy._private.system_model.connections_and_sockets import (
        _2524,
        _2527,
        _2528,
        _2531,
        _2532,
        _2540,
        _2546,
        _2551,
        _2554,
    )
    from mastapy._private.system_model.connections_and_sockets.couplings import (
        _2601,
        _2603,
        _2605,
        _2607,
        _2609,
        _2611,
    )
    from mastapy._private.system_model.connections_and_sockets.cycloidal import (
        _2594,
        _2597,
        _2600,
    )
    from mastapy._private.system_model.connections_and_sockets.gears import (
        _2558,
        _2560,
        _2562,
        _2564,
        _2566,
        _2568,
        _2570,
        _2572,
        _2574,
        _2577,
        _2578,
        _2579,
        _2582,
        _2584,
        _2586,
        _2588,
        _2590,
    )
    from mastapy._private.system_model.part_model import (
        _2702,
        _2703,
        _2704,
        _2705,
        _2708,
        _2711,
        _2712,
        _2714,
        _2717,
        _2718,
        _2723,
        _2724,
        _2725,
        _2726,
        _2733,
        _2734,
        _2735,
        _2736,
        _2737,
        _2739,
        _2742,
        _2744,
        _2746,
        _2747,
        _2750,
        _2752,
        _2753,
        _2755,
    )
    from mastapy._private.system_model.part_model.couplings import (
        _2859,
        _2861,
        _2862,
        _2864,
        _2865,
        _2867,
        _2868,
        _2870,
        _2871,
        _2872,
        _2873,
        _2875,
        _2882,
        _2883,
        _2884,
        _2890,
        _2891,
        _2892,
        _2894,
        _2895,
        _2896,
        _2897,
        _2898,
        _2900,
    )
    from mastapy._private.system_model.part_model.cycloidal import _2850, _2851, _2852
    from mastapy._private.system_model.part_model.gears import (
        _2794,
        _2795,
        _2796,
        _2797,
        _2798,
        _2799,
        _2800,
        _2801,
        _2802,
        _2803,
        _2804,
        _2805,
        _2806,
        _2807,
        _2808,
        _2809,
        _2810,
        _2811,
        _2813,
        _2815,
        _2816,
        _2817,
        _2818,
        _2819,
        _2820,
        _2821,
        _2822,
        _2823,
        _2825,
        _2826,
        _2827,
        _2828,
        _2829,
        _2830,
        _2831,
        _2832,
        _2833,
        _2834,
        _2835,
        _2836,
    )
    from mastapy._private.system_model.part_model.shaft_model import _2758

    Self = TypeVar("Self", bound="CompoundSystemDeflection")
    CastSelf = TypeVar(
        "CastSelf", bound="CompoundSystemDeflection._Cast_CompoundSystemDeflection"
    )


__docformat__ = "restructuredtext en"
__all__ = ("CompoundSystemDeflection",)


@extended_dataclass(frozen=True, slots=True, weakref_slot=True)
class _Cast_CompoundSystemDeflection:
    """Special nested class for casting CompoundSystemDeflection to subclasses."""

    __parent__: "CompoundSystemDeflection"

    @property
    def compound_analysis(self: "CastSelf") -> "_2939.CompoundAnalysis":
        return self.__parent__._cast(_2939.CompoundAnalysis)

    @property
    def marshal_by_ref_object_permanent(
        self: "CastSelf",
    ) -> "_7949.MarshalByRefObjectPermanent":
        from mastapy._private import _7949

        return self.__parent__._cast(_7949.MarshalByRefObjectPermanent)

    @property
    def compound_system_deflection(self: "CastSelf") -> "CompoundSystemDeflection":
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
class CompoundSystemDeflection(_2939.CompoundAnalysis):
    """CompoundSystemDeflection

    This is a mastapy class.
    """

    TYPE: ClassVar["Type"] = _COMPOUND_SYSTEM_DEFLECTION

    wrapped: "Any"

    def __post_init__(self: "Self") -> None:
        """Override of the post initialisation magic method."""
        if not hasattr(self.wrapped, "reference_count"):
            self.wrapped.reference_count = 0

        self.wrapped.reference_count += 1

    @exception_bridge
    @enforce_parameter_types
    def results_for_concept_coupling_connection(
        self: "Self", design_entity: "_2603.ConceptCouplingConnection"
    ) -> "Iterable[_3173.ConceptCouplingConnectionCompoundSystemDeflection]":
        """Iterable[mastapy.system_model.analyses_and_results.system_deflections.compound.ConceptCouplingConnectionCompoundSystemDeflection]

        Args:
            design_entity (mastapy.system_model.connections_and_sockets.couplings.ConceptCouplingConnection)
        """
        return conversion.pn_to_mp_objects_in_iterable(
            pythonnet_method_call_overload(
                self.wrapped,
                "ResultsFor",
                [_CONCEPT_COUPLING_CONNECTION],
                design_entity.wrapped if design_entity else None,
            )
        )

    @exception_bridge
    @enforce_parameter_types
    def results_for_coupling_connection(
        self: "Self", design_entity: "_2605.CouplingConnection"
    ) -> "Iterable[_3184.CouplingConnectionCompoundSystemDeflection]":
        """Iterable[mastapy.system_model.analyses_and_results.system_deflections.compound.CouplingConnectionCompoundSystemDeflection]

        Args:
            design_entity (mastapy.system_model.connections_and_sockets.couplings.CouplingConnection)
        """
        return conversion.pn_to_mp_objects_in_iterable(
            pythonnet_method_call_overload(
                self.wrapped,
                "ResultsFor",
                [_COUPLING_CONNECTION],
                design_entity.wrapped if design_entity else None,
            )
        )

    @exception_bridge
    @enforce_parameter_types
    def results_for_spring_damper_connection(
        self: "Self", design_entity: "_2609.SpringDamperConnection"
    ) -> "Iterable[_3253.SpringDamperConnectionCompoundSystemDeflection]":
        """Iterable[mastapy.system_model.analyses_and_results.system_deflections.compound.SpringDamperConnectionCompoundSystemDeflection]

        Args:
            design_entity (mastapy.system_model.connections_and_sockets.couplings.SpringDamperConnection)
        """
        return conversion.pn_to_mp_objects_in_iterable(
            pythonnet_method_call_overload(
                self.wrapped,
                "ResultsFor",
                [_SPRING_DAMPER_CONNECTION],
                design_entity.wrapped if design_entity else None,
            )
        )

    @exception_bridge
    @enforce_parameter_types
    def results_for_torque_converter_connection(
        self: "Self", design_entity: "_2611.TorqueConverterConnection"
    ) -> "Iterable[_3268.TorqueConverterConnectionCompoundSystemDeflection]":
        """Iterable[mastapy.system_model.analyses_and_results.system_deflections.compound.TorqueConverterConnectionCompoundSystemDeflection]

        Args:
            design_entity (mastapy.system_model.connections_and_sockets.couplings.TorqueConverterConnection)
        """
        return conversion.pn_to_mp_objects_in_iterable(
            pythonnet_method_call_overload(
                self.wrapped,
                "ResultsFor",
                [_TORQUE_CONVERTER_CONNECTION],
                design_entity.wrapped if design_entity else None,
            )
        )

    @exception_bridge
    @enforce_parameter_types
    def results_for_abstract_shaft(
        self: "Self", design_entity: "_2704.AbstractShaft"
    ) -> "Iterable[_3147.AbstractShaftCompoundSystemDeflection]":
        """Iterable[mastapy.system_model.analyses_and_results.system_deflections.compound.AbstractShaftCompoundSystemDeflection]

        Args:
            design_entity (mastapy.system_model.part_model.AbstractShaft)
        """
        return conversion.pn_to_mp_objects_in_iterable(
            pythonnet_method_call_overload(
                self.wrapped,
                "ResultsFor",
                [_ABSTRACT_SHAFT],
                design_entity.wrapped if design_entity else None,
            )
        )

    @exception_bridge
    @enforce_parameter_types
    def results_for_microphone(
        self: "Self", design_entity: "_2735.Microphone"
    ) -> "Iterable[_3225.MicrophoneCompoundSystemDeflection]":
        """Iterable[mastapy.system_model.analyses_and_results.system_deflections.compound.MicrophoneCompoundSystemDeflection]

        Args:
            design_entity (mastapy.system_model.part_model.Microphone)
        """
        return conversion.pn_to_mp_objects_in_iterable(
            pythonnet_method_call_overload(
                self.wrapped,
                "ResultsFor",
                [_MICROPHONE],
                design_entity.wrapped if design_entity else None,
            )
        )

    @exception_bridge
    @enforce_parameter_types
    def results_for_microphone_array(
        self: "Self", design_entity: "_2736.MicrophoneArray"
    ) -> "Iterable[_3224.MicrophoneArrayCompoundSystemDeflection]":
        """Iterable[mastapy.system_model.analyses_and_results.system_deflections.compound.MicrophoneArrayCompoundSystemDeflection]

        Args:
            design_entity (mastapy.system_model.part_model.MicrophoneArray)
        """
        return conversion.pn_to_mp_objects_in_iterable(
            pythonnet_method_call_overload(
                self.wrapped,
                "ResultsFor",
                [_MICROPHONE_ARRAY],
                design_entity.wrapped if design_entity else None,
            )
        )

    @exception_bridge
    @enforce_parameter_types
    def results_for_abstract_assembly(
        self: "Self", design_entity: "_2703.AbstractAssembly"
    ) -> "Iterable[_3146.AbstractAssemblyCompoundSystemDeflection]":
        """Iterable[mastapy.system_model.analyses_and_results.system_deflections.compound.AbstractAssemblyCompoundSystemDeflection]

        Args:
            design_entity (mastapy.system_model.part_model.AbstractAssembly)
        """
        return conversion.pn_to_mp_objects_in_iterable(
            pythonnet_method_call_overload(
                self.wrapped,
                "ResultsFor",
                [_ABSTRACT_ASSEMBLY],
                design_entity.wrapped if design_entity else None,
            )
        )

    @exception_bridge
    @enforce_parameter_types
    def results_for_abstract_shaft_or_housing(
        self: "Self", design_entity: "_2705.AbstractShaftOrHousing"
    ) -> "Iterable[_3148.AbstractShaftOrHousingCompoundSystemDeflection]":
        """Iterable[mastapy.system_model.analyses_and_results.system_deflections.compound.AbstractShaftOrHousingCompoundSystemDeflection]

        Args:
            design_entity (mastapy.system_model.part_model.AbstractShaftOrHousing)
        """
        return conversion.pn_to_mp_objects_in_iterable(
            pythonnet_method_call_overload(
                self.wrapped,
                "ResultsFor",
                [_ABSTRACT_SHAFT_OR_HOUSING],
                design_entity.wrapped if design_entity else None,
            )
        )

    @exception_bridge
    @enforce_parameter_types
    def results_for_bearing(
        self: "Self", design_entity: "_2708.Bearing"
    ) -> "Iterable[_3154.BearingCompoundSystemDeflection]":
        """Iterable[mastapy.system_model.analyses_and_results.system_deflections.compound.BearingCompoundSystemDeflection]

        Args:
            design_entity (mastapy.system_model.part_model.Bearing)
        """
        return conversion.pn_to_mp_objects_in_iterable(
            pythonnet_method_call_overload(
                self.wrapped,
                "ResultsFor",
                [_BEARING],
                design_entity.wrapped if design_entity else None,
            )
        )

    @exception_bridge
    @enforce_parameter_types
    def results_for_bolt(
        self: "Self", design_entity: "_2711.Bolt"
    ) -> "Iterable[_3165.BoltCompoundSystemDeflection]":
        """Iterable[mastapy.system_model.analyses_and_results.system_deflections.compound.BoltCompoundSystemDeflection]

        Args:
            design_entity (mastapy.system_model.part_model.Bolt)
        """
        return conversion.pn_to_mp_objects_in_iterable(
            pythonnet_method_call_overload(
                self.wrapped,
                "ResultsFor",
                [_BOLT],
                design_entity.wrapped if design_entity else None,
            )
        )

    @exception_bridge
    @enforce_parameter_types
    def results_for_bolted_joint(
        self: "Self", design_entity: "_2712.BoltedJoint"
    ) -> "Iterable[_3166.BoltedJointCompoundSystemDeflection]":
        """Iterable[mastapy.system_model.analyses_and_results.system_deflections.compound.BoltedJointCompoundSystemDeflection]

        Args:
            design_entity (mastapy.system_model.part_model.BoltedJoint)
        """
        return conversion.pn_to_mp_objects_in_iterable(
            pythonnet_method_call_overload(
                self.wrapped,
                "ResultsFor",
                [_BOLTED_JOINT],
                design_entity.wrapped if design_entity else None,
            )
        )

    @exception_bridge
    @enforce_parameter_types
    def results_for_component(
        self: "Self", design_entity: "_2714.Component"
    ) -> "Iterable[_3171.ComponentCompoundSystemDeflection]":
        """Iterable[mastapy.system_model.analyses_and_results.system_deflections.compound.ComponentCompoundSystemDeflection]

        Args:
            design_entity (mastapy.system_model.part_model.Component)
        """
        return conversion.pn_to_mp_objects_in_iterable(
            pythonnet_method_call_overload(
                self.wrapped,
                "ResultsFor",
                [_COMPONENT],
                design_entity.wrapped if design_entity else None,
            )
        )

    @exception_bridge
    @enforce_parameter_types
    def results_for_connector(
        self: "Self", design_entity: "_2717.Connector"
    ) -> "Iterable[_3182.ConnectorCompoundSystemDeflection]":
        """Iterable[mastapy.system_model.analyses_and_results.system_deflections.compound.ConnectorCompoundSystemDeflection]

        Args:
            design_entity (mastapy.system_model.part_model.Connector)
        """
        return conversion.pn_to_mp_objects_in_iterable(
            pythonnet_method_call_overload(
                self.wrapped,
                "ResultsFor",
                [_CONNECTOR],
                design_entity.wrapped if design_entity else None,
            )
        )

    @exception_bridge
    @enforce_parameter_types
    def results_for_datum(
        self: "Self", design_entity: "_2718.Datum"
    ) -> "Iterable[_3197.DatumCompoundSystemDeflection]":
        """Iterable[mastapy.system_model.analyses_and_results.system_deflections.compound.DatumCompoundSystemDeflection]

        Args:
            design_entity (mastapy.system_model.part_model.Datum)
        """
        return conversion.pn_to_mp_objects_in_iterable(
            pythonnet_method_call_overload(
                self.wrapped,
                "ResultsFor",
                [_DATUM],
                design_entity.wrapped if design_entity else None,
            )
        )

    @exception_bridge
    @enforce_parameter_types
    def results_for_external_cad_model(
        self: "Self", design_entity: "_2723.ExternalCADModel"
    ) -> "Iterable[_3199.ExternalCADModelCompoundSystemDeflection]":
        """Iterable[mastapy.system_model.analyses_and_results.system_deflections.compound.ExternalCADModelCompoundSystemDeflection]

        Args:
            design_entity (mastapy.system_model.part_model.ExternalCADModel)
        """
        return conversion.pn_to_mp_objects_in_iterable(
            pythonnet_method_call_overload(
                self.wrapped,
                "ResultsFor",
                [_EXTERNAL_CAD_MODEL],
                design_entity.wrapped if design_entity else None,
            )
        )

    @exception_bridge
    @enforce_parameter_types
    def results_for_fe_part(
        self: "Self", design_entity: "_2724.FEPart"
    ) -> "Iterable[_3203.FEPartCompoundSystemDeflection]":
        """Iterable[mastapy.system_model.analyses_and_results.system_deflections.compound.FEPartCompoundSystemDeflection]

        Args:
            design_entity (mastapy.system_model.part_model.FEPart)
        """
        return conversion.pn_to_mp_objects_in_iterable(
            pythonnet_method_call_overload(
                self.wrapped,
                "ResultsFor",
                [_FE_PART],
                design_entity.wrapped if design_entity else None,
            )
        )

    @exception_bridge
    @enforce_parameter_types
    def results_for_flexible_pin_assembly(
        self: "Self", design_entity: "_2725.FlexiblePinAssembly"
    ) -> "Iterable[_3204.FlexiblePinAssemblyCompoundSystemDeflection]":
        """Iterable[mastapy.system_model.analyses_and_results.system_deflections.compound.FlexiblePinAssemblyCompoundSystemDeflection]

        Args:
            design_entity (mastapy.system_model.part_model.FlexiblePinAssembly)
        """
        return conversion.pn_to_mp_objects_in_iterable(
            pythonnet_method_call_overload(
                self.wrapped,
                "ResultsFor",
                [_FLEXIBLE_PIN_ASSEMBLY],
                design_entity.wrapped if design_entity else None,
            )
        )

    @exception_bridge
    @enforce_parameter_types
    def results_for_assembly(
        self: "Self", design_entity: "_2702.Assembly"
    ) -> "Iterable[_3153.AssemblyCompoundSystemDeflection]":
        """Iterable[mastapy.system_model.analyses_and_results.system_deflections.compound.AssemblyCompoundSystemDeflection]

        Args:
            design_entity (mastapy.system_model.part_model.Assembly)
        """
        return conversion.pn_to_mp_objects_in_iterable(
            pythonnet_method_call_overload(
                self.wrapped,
                "ResultsFor",
                [_ASSEMBLY],
                design_entity.wrapped if design_entity else None,
            )
        )

    @exception_bridge
    @enforce_parameter_types
    def results_for_guide_dxf_model(
        self: "Self", design_entity: "_2726.GuideDxfModel"
    ) -> "Iterable[_3208.GuideDxfModelCompoundSystemDeflection]":
        """Iterable[mastapy.system_model.analyses_and_results.system_deflections.compound.GuideDxfModelCompoundSystemDeflection]

        Args:
            design_entity (mastapy.system_model.part_model.GuideDxfModel)
        """
        return conversion.pn_to_mp_objects_in_iterable(
            pythonnet_method_call_overload(
                self.wrapped,
                "ResultsFor",
                [_GUIDE_DXF_MODEL],
                design_entity.wrapped if design_entity else None,
            )
        )

    @exception_bridge
    @enforce_parameter_types
    def results_for_mass_disc(
        self: "Self", design_entity: "_2733.MassDisc"
    ) -> "Iterable[_3222.MassDiscCompoundSystemDeflection]":
        """Iterable[mastapy.system_model.analyses_and_results.system_deflections.compound.MassDiscCompoundSystemDeflection]

        Args:
            design_entity (mastapy.system_model.part_model.MassDisc)
        """
        return conversion.pn_to_mp_objects_in_iterable(
            pythonnet_method_call_overload(
                self.wrapped,
                "ResultsFor",
                [_MASS_DISC],
                design_entity.wrapped if design_entity else None,
            )
        )

    @exception_bridge
    @enforce_parameter_types
    def results_for_measurement_component(
        self: "Self", design_entity: "_2734.MeasurementComponent"
    ) -> "Iterable[_3223.MeasurementComponentCompoundSystemDeflection]":
        """Iterable[mastapy.system_model.analyses_and_results.system_deflections.compound.MeasurementComponentCompoundSystemDeflection]

        Args:
            design_entity (mastapy.system_model.part_model.MeasurementComponent)
        """
        return conversion.pn_to_mp_objects_in_iterable(
            pythonnet_method_call_overload(
                self.wrapped,
                "ResultsFor",
                [_MEASUREMENT_COMPONENT],
                design_entity.wrapped if design_entity else None,
            )
        )

    @exception_bridge
    @enforce_parameter_types
    def results_for_mountable_component(
        self: "Self", design_entity: "_2737.MountableComponent"
    ) -> "Iterable[_3226.MountableComponentCompoundSystemDeflection]":
        """Iterable[mastapy.system_model.analyses_and_results.system_deflections.compound.MountableComponentCompoundSystemDeflection]

        Args:
            design_entity (mastapy.system_model.part_model.MountableComponent)
        """
        return conversion.pn_to_mp_objects_in_iterable(
            pythonnet_method_call_overload(
                self.wrapped,
                "ResultsFor",
                [_MOUNTABLE_COMPONENT],
                design_entity.wrapped if design_entity else None,
            )
        )

    @exception_bridge
    @enforce_parameter_types
    def results_for_oil_seal(
        self: "Self", design_entity: "_2739.OilSeal"
    ) -> "Iterable[_3227.OilSealCompoundSystemDeflection]":
        """Iterable[mastapy.system_model.analyses_and_results.system_deflections.compound.OilSealCompoundSystemDeflection]

        Args:
            design_entity (mastapy.system_model.part_model.OilSeal)
        """
        return conversion.pn_to_mp_objects_in_iterable(
            pythonnet_method_call_overload(
                self.wrapped,
                "ResultsFor",
                [_OIL_SEAL],
                design_entity.wrapped if design_entity else None,
            )
        )

    @exception_bridge
    @enforce_parameter_types
    def results_for_part(
        self: "Self", design_entity: "_2742.Part"
    ) -> "Iterable[_3228.PartCompoundSystemDeflection]":
        """Iterable[mastapy.system_model.analyses_and_results.system_deflections.compound.PartCompoundSystemDeflection]

        Args:
            design_entity (mastapy.system_model.part_model.Part)
        """
        return conversion.pn_to_mp_objects_in_iterable(
            pythonnet_method_call_overload(
                self.wrapped,
                "ResultsFor",
                [_PART],
                design_entity.wrapped if design_entity else None,
            )
        )

    @exception_bridge
    @enforce_parameter_types
    def results_for_planet_carrier(
        self: "Self", design_entity: "_2744.PlanetCarrier"
    ) -> "Iterable[_3234.PlanetCarrierCompoundSystemDeflection]":
        """Iterable[mastapy.system_model.analyses_and_results.system_deflections.compound.PlanetCarrierCompoundSystemDeflection]

        Args:
            design_entity (mastapy.system_model.part_model.PlanetCarrier)
        """
        return conversion.pn_to_mp_objects_in_iterable(
            pythonnet_method_call_overload(
                self.wrapped,
                "ResultsFor",
                [_PLANET_CARRIER],
                design_entity.wrapped if design_entity else None,
            )
        )

    @exception_bridge
    @enforce_parameter_types
    def results_for_point_load(
        self: "Self", design_entity: "_2746.PointLoad"
    ) -> "Iterable[_3235.PointLoadCompoundSystemDeflection]":
        """Iterable[mastapy.system_model.analyses_and_results.system_deflections.compound.PointLoadCompoundSystemDeflection]

        Args:
            design_entity (mastapy.system_model.part_model.PointLoad)
        """
        return conversion.pn_to_mp_objects_in_iterable(
            pythonnet_method_call_overload(
                self.wrapped,
                "ResultsFor",
                [_POINT_LOAD],
                design_entity.wrapped if design_entity else None,
            )
        )

    @exception_bridge
    @enforce_parameter_types
    def results_for_power_load(
        self: "Self", design_entity: "_2747.PowerLoad"
    ) -> "Iterable[_3236.PowerLoadCompoundSystemDeflection]":
        """Iterable[mastapy.system_model.analyses_and_results.system_deflections.compound.PowerLoadCompoundSystemDeflection]

        Args:
            design_entity (mastapy.system_model.part_model.PowerLoad)
        """
        return conversion.pn_to_mp_objects_in_iterable(
            pythonnet_method_call_overload(
                self.wrapped,
                "ResultsFor",
                [_POWER_LOAD],
                design_entity.wrapped if design_entity else None,
            )
        )

    @exception_bridge
    @enforce_parameter_types
    def results_for_root_assembly(
        self: "Self", design_entity: "_2750.RootAssembly"
    ) -> "Iterable[_3243.RootAssemblyCompoundSystemDeflection]":
        """Iterable[mastapy.system_model.analyses_and_results.system_deflections.compound.RootAssemblyCompoundSystemDeflection]

        Args:
            design_entity (mastapy.system_model.part_model.RootAssembly)
        """
        return conversion.pn_to_mp_objects_in_iterable(
            pythonnet_method_call_overload(
                self.wrapped,
                "ResultsFor",
                [_ROOT_ASSEMBLY],
                design_entity.wrapped if design_entity else None,
            )
        )

    @exception_bridge
    @enforce_parameter_types
    def results_for_specialised_assembly(
        self: "Self", design_entity: "_2752.SpecialisedAssembly"
    ) -> "Iterable[_3248.SpecialisedAssemblyCompoundSystemDeflection]":
        """Iterable[mastapy.system_model.analyses_and_results.system_deflections.compound.SpecialisedAssemblyCompoundSystemDeflection]

        Args:
            design_entity (mastapy.system_model.part_model.SpecialisedAssembly)
        """
        return conversion.pn_to_mp_objects_in_iterable(
            pythonnet_method_call_overload(
                self.wrapped,
                "ResultsFor",
                [_SPECIALISED_ASSEMBLY],
                design_entity.wrapped if design_entity else None,
            )
        )

    @exception_bridge
    @enforce_parameter_types
    def results_for_unbalanced_mass(
        self: "Self", design_entity: "_2753.UnbalancedMass"
    ) -> "Iterable[_3271.UnbalancedMassCompoundSystemDeflection]":
        """Iterable[mastapy.system_model.analyses_and_results.system_deflections.compound.UnbalancedMassCompoundSystemDeflection]

        Args:
            design_entity (mastapy.system_model.part_model.UnbalancedMass)
        """
        return conversion.pn_to_mp_objects_in_iterable(
            pythonnet_method_call_overload(
                self.wrapped,
                "ResultsFor",
                [_UNBALANCED_MASS],
                design_entity.wrapped if design_entity else None,
            )
        )

    @exception_bridge
    @enforce_parameter_types
    def results_for_virtual_component(
        self: "Self", design_entity: "_2755.VirtualComponent"
    ) -> "Iterable[_3272.VirtualComponentCompoundSystemDeflection]":
        """Iterable[mastapy.system_model.analyses_and_results.system_deflections.compound.VirtualComponentCompoundSystemDeflection]

        Args:
            design_entity (mastapy.system_model.part_model.VirtualComponent)
        """
        return conversion.pn_to_mp_objects_in_iterable(
            pythonnet_method_call_overload(
                self.wrapped,
                "ResultsFor",
                [_VIRTUAL_COMPONENT],
                design_entity.wrapped if design_entity else None,
            )
        )

    @exception_bridge
    @enforce_parameter_types
    def results_for_shaft(
        self: "Self", design_entity: "_2758.Shaft"
    ) -> "Iterable[_3244.ShaftCompoundSystemDeflection]":
        """Iterable[mastapy.system_model.analyses_and_results.system_deflections.compound.ShaftCompoundSystemDeflection]

        Args:
            design_entity (mastapy.system_model.part_model.shaft_model.Shaft)
        """
        return conversion.pn_to_mp_objects_in_iterable(
            pythonnet_method_call_overload(
                self.wrapped,
                "ResultsFor",
                [_SHAFT],
                design_entity.wrapped if design_entity else None,
            )
        )

    @exception_bridge
    @enforce_parameter_types
    def results_for_concept_gear(
        self: "Self", design_entity: "_2802.ConceptGear"
    ) -> "Iterable[_3175.ConceptGearCompoundSystemDeflection]":
        """Iterable[mastapy.system_model.analyses_and_results.system_deflections.compound.ConceptGearCompoundSystemDeflection]

        Args:
            design_entity (mastapy.system_model.part_model.gears.ConceptGear)
        """
        return conversion.pn_to_mp_objects_in_iterable(
            pythonnet_method_call_overload(
                self.wrapped,
                "ResultsFor",
                [_CONCEPT_GEAR],
                design_entity.wrapped if design_entity else None,
            )
        )

    @exception_bridge
    @enforce_parameter_types
    def results_for_concept_gear_set(
        self: "Self", design_entity: "_2803.ConceptGearSet"
    ) -> "Iterable[_3177.ConceptGearSetCompoundSystemDeflection]":
        """Iterable[mastapy.system_model.analyses_and_results.system_deflections.compound.ConceptGearSetCompoundSystemDeflection]

        Args:
            design_entity (mastapy.system_model.part_model.gears.ConceptGearSet)
        """
        return conversion.pn_to_mp_objects_in_iterable(
            pythonnet_method_call_overload(
                self.wrapped,
                "ResultsFor",
                [_CONCEPT_GEAR_SET],
                design_entity.wrapped if design_entity else None,
            )
        )

    @exception_bridge
    @enforce_parameter_types
    def results_for_face_gear(
        self: "Self", design_entity: "_2809.FaceGear"
    ) -> "Iterable[_3200.FaceGearCompoundSystemDeflection]":
        """Iterable[mastapy.system_model.analyses_and_results.system_deflections.compound.FaceGearCompoundSystemDeflection]

        Args:
            design_entity (mastapy.system_model.part_model.gears.FaceGear)
        """
        return conversion.pn_to_mp_objects_in_iterable(
            pythonnet_method_call_overload(
                self.wrapped,
                "ResultsFor",
                [_FACE_GEAR],
                design_entity.wrapped if design_entity else None,
            )
        )

    @exception_bridge
    @enforce_parameter_types
    def results_for_face_gear_set(
        self: "Self", design_entity: "_2810.FaceGearSet"
    ) -> "Iterable[_3202.FaceGearSetCompoundSystemDeflection]":
        """Iterable[mastapy.system_model.analyses_and_results.system_deflections.compound.FaceGearSetCompoundSystemDeflection]

        Args:
            design_entity (mastapy.system_model.part_model.gears.FaceGearSet)
        """
        return conversion.pn_to_mp_objects_in_iterable(
            pythonnet_method_call_overload(
                self.wrapped,
                "ResultsFor",
                [_FACE_GEAR_SET],
                design_entity.wrapped if design_entity else None,
            )
        )

    @exception_bridge
    @enforce_parameter_types
    def results_for_agma_gleason_conical_gear(
        self: "Self", design_entity: "_2794.AGMAGleasonConicalGear"
    ) -> "Iterable[_3150.AGMAGleasonConicalGearCompoundSystemDeflection]":
        """Iterable[mastapy.system_model.analyses_and_results.system_deflections.compound.AGMAGleasonConicalGearCompoundSystemDeflection]

        Args:
            design_entity (mastapy.system_model.part_model.gears.AGMAGleasonConicalGear)
        """
        return conversion.pn_to_mp_objects_in_iterable(
            pythonnet_method_call_overload(
                self.wrapped,
                "ResultsFor",
                [_AGMA_GLEASON_CONICAL_GEAR],
                design_entity.wrapped if design_entity else None,
            )
        )

    @exception_bridge
    @enforce_parameter_types
    def results_for_agma_gleason_conical_gear_set(
        self: "Self", design_entity: "_2795.AGMAGleasonConicalGearSet"
    ) -> "Iterable[_3152.AGMAGleasonConicalGearSetCompoundSystemDeflection]":
        """Iterable[mastapy.system_model.analyses_and_results.system_deflections.compound.AGMAGleasonConicalGearSetCompoundSystemDeflection]

        Args:
            design_entity (mastapy.system_model.part_model.gears.AGMAGleasonConicalGearSet)
        """
        return conversion.pn_to_mp_objects_in_iterable(
            pythonnet_method_call_overload(
                self.wrapped,
                "ResultsFor",
                [_AGMA_GLEASON_CONICAL_GEAR_SET],
                design_entity.wrapped if design_entity else None,
            )
        )

    @exception_bridge
    @enforce_parameter_types
    def results_for_bevel_differential_gear(
        self: "Self", design_entity: "_2796.BevelDifferentialGear"
    ) -> "Iterable[_3157.BevelDifferentialGearCompoundSystemDeflection]":
        """Iterable[mastapy.system_model.analyses_and_results.system_deflections.compound.BevelDifferentialGearCompoundSystemDeflection]

        Args:
            design_entity (mastapy.system_model.part_model.gears.BevelDifferentialGear)
        """
        return conversion.pn_to_mp_objects_in_iterable(
            pythonnet_method_call_overload(
                self.wrapped,
                "ResultsFor",
                [_BEVEL_DIFFERENTIAL_GEAR],
                design_entity.wrapped if design_entity else None,
            )
        )

    @exception_bridge
    @enforce_parameter_types
    def results_for_bevel_differential_gear_set(
        self: "Self", design_entity: "_2797.BevelDifferentialGearSet"
    ) -> "Iterable[_3159.BevelDifferentialGearSetCompoundSystemDeflection]":
        """Iterable[mastapy.system_model.analyses_and_results.system_deflections.compound.BevelDifferentialGearSetCompoundSystemDeflection]

        Args:
            design_entity (mastapy.system_model.part_model.gears.BevelDifferentialGearSet)
        """
        return conversion.pn_to_mp_objects_in_iterable(
            pythonnet_method_call_overload(
                self.wrapped,
                "ResultsFor",
                [_BEVEL_DIFFERENTIAL_GEAR_SET],
                design_entity.wrapped if design_entity else None,
            )
        )

    @exception_bridge
    @enforce_parameter_types
    def results_for_bevel_differential_planet_gear(
        self: "Self", design_entity: "_2798.BevelDifferentialPlanetGear"
    ) -> "Iterable[_3160.BevelDifferentialPlanetGearCompoundSystemDeflection]":
        """Iterable[mastapy.system_model.analyses_and_results.system_deflections.compound.BevelDifferentialPlanetGearCompoundSystemDeflection]

        Args:
            design_entity (mastapy.system_model.part_model.gears.BevelDifferentialPlanetGear)
        """
        return conversion.pn_to_mp_objects_in_iterable(
            pythonnet_method_call_overload(
                self.wrapped,
                "ResultsFor",
                [_BEVEL_DIFFERENTIAL_PLANET_GEAR],
                design_entity.wrapped if design_entity else None,
            )
        )

    @exception_bridge
    @enforce_parameter_types
    def results_for_bevel_differential_sun_gear(
        self: "Self", design_entity: "_2799.BevelDifferentialSunGear"
    ) -> "Iterable[_3161.BevelDifferentialSunGearCompoundSystemDeflection]":
        """Iterable[mastapy.system_model.analyses_and_results.system_deflections.compound.BevelDifferentialSunGearCompoundSystemDeflection]

        Args:
            design_entity (mastapy.system_model.part_model.gears.BevelDifferentialSunGear)
        """
        return conversion.pn_to_mp_objects_in_iterable(
            pythonnet_method_call_overload(
                self.wrapped,
                "ResultsFor",
                [_BEVEL_DIFFERENTIAL_SUN_GEAR],
                design_entity.wrapped if design_entity else None,
            )
        )

    @exception_bridge
    @enforce_parameter_types
    def results_for_bevel_gear(
        self: "Self", design_entity: "_2800.BevelGear"
    ) -> "Iterable[_3162.BevelGearCompoundSystemDeflection]":
        """Iterable[mastapy.system_model.analyses_and_results.system_deflections.compound.BevelGearCompoundSystemDeflection]

        Args:
            design_entity (mastapy.system_model.part_model.gears.BevelGear)
        """
        return conversion.pn_to_mp_objects_in_iterable(
            pythonnet_method_call_overload(
                self.wrapped,
                "ResultsFor",
                [_BEVEL_GEAR],
                design_entity.wrapped if design_entity else None,
            )
        )

    @exception_bridge
    @enforce_parameter_types
    def results_for_bevel_gear_set(
        self: "Self", design_entity: "_2801.BevelGearSet"
    ) -> "Iterable[_3164.BevelGearSetCompoundSystemDeflection]":
        """Iterable[mastapy.system_model.analyses_and_results.system_deflections.compound.BevelGearSetCompoundSystemDeflection]

        Args:
            design_entity (mastapy.system_model.part_model.gears.BevelGearSet)
        """
        return conversion.pn_to_mp_objects_in_iterable(
            pythonnet_method_call_overload(
                self.wrapped,
                "ResultsFor",
                [_BEVEL_GEAR_SET],
                design_entity.wrapped if design_entity else None,
            )
        )

    @exception_bridge
    @enforce_parameter_types
    def results_for_conical_gear(
        self: "Self", design_entity: "_2804.ConicalGear"
    ) -> "Iterable[_3178.ConicalGearCompoundSystemDeflection]":
        """Iterable[mastapy.system_model.analyses_and_results.system_deflections.compound.ConicalGearCompoundSystemDeflection]

        Args:
            design_entity (mastapy.system_model.part_model.gears.ConicalGear)
        """
        return conversion.pn_to_mp_objects_in_iterable(
            pythonnet_method_call_overload(
                self.wrapped,
                "ResultsFor",
                [_CONICAL_GEAR],
                design_entity.wrapped if design_entity else None,
            )
        )

    @exception_bridge
    @enforce_parameter_types
    def results_for_conical_gear_set(
        self: "Self", design_entity: "_2805.ConicalGearSet"
    ) -> "Iterable[_3180.ConicalGearSetCompoundSystemDeflection]":
        """Iterable[mastapy.system_model.analyses_and_results.system_deflections.compound.ConicalGearSetCompoundSystemDeflection]

        Args:
            design_entity (mastapy.system_model.part_model.gears.ConicalGearSet)
        """
        return conversion.pn_to_mp_objects_in_iterable(
            pythonnet_method_call_overload(
                self.wrapped,
                "ResultsFor",
                [_CONICAL_GEAR_SET],
                design_entity.wrapped if design_entity else None,
            )
        )

    @exception_bridge
    @enforce_parameter_types
    def results_for_cylindrical_gear(
        self: "Self", design_entity: "_2806.CylindricalGear"
    ) -> "Iterable[_3193.CylindricalGearCompoundSystemDeflection]":
        """Iterable[mastapy.system_model.analyses_and_results.system_deflections.compound.CylindricalGearCompoundSystemDeflection]

        Args:
            design_entity (mastapy.system_model.part_model.gears.CylindricalGear)
        """
        return conversion.pn_to_mp_objects_in_iterable(
            pythonnet_method_call_overload(
                self.wrapped,
                "ResultsFor",
                [_CYLINDRICAL_GEAR],
                design_entity.wrapped if design_entity else None,
            )
        )

    @exception_bridge
    @enforce_parameter_types
    def results_for_cylindrical_gear_set(
        self: "Self", design_entity: "_2807.CylindricalGearSet"
    ) -> "Iterable[_3195.CylindricalGearSetCompoundSystemDeflection]":
        """Iterable[mastapy.system_model.analyses_and_results.system_deflections.compound.CylindricalGearSetCompoundSystemDeflection]

        Args:
            design_entity (mastapy.system_model.part_model.gears.CylindricalGearSet)
        """
        return conversion.pn_to_mp_objects_in_iterable(
            pythonnet_method_call_overload(
                self.wrapped,
                "ResultsFor",
                [_CYLINDRICAL_GEAR_SET],
                design_entity.wrapped if design_entity else None,
            )
        )

    @exception_bridge
    @enforce_parameter_types
    def results_for_cylindrical_planet_gear(
        self: "Self", design_entity: "_2808.CylindricalPlanetGear"
    ) -> "Iterable[_3196.CylindricalPlanetGearCompoundSystemDeflection]":
        """Iterable[mastapy.system_model.analyses_and_results.system_deflections.compound.CylindricalPlanetGearCompoundSystemDeflection]

        Args:
            design_entity (mastapy.system_model.part_model.gears.CylindricalPlanetGear)
        """
        return conversion.pn_to_mp_objects_in_iterable(
            pythonnet_method_call_overload(
                self.wrapped,
                "ResultsFor",
                [_CYLINDRICAL_PLANET_GEAR],
                design_entity.wrapped if design_entity else None,
            )
        )

    @exception_bridge
    @enforce_parameter_types
    def results_for_gear(
        self: "Self", design_entity: "_2811.Gear"
    ) -> "Iterable[_3205.GearCompoundSystemDeflection]":
        """Iterable[mastapy.system_model.analyses_and_results.system_deflections.compound.GearCompoundSystemDeflection]

        Args:
            design_entity (mastapy.system_model.part_model.gears.Gear)
        """
        return conversion.pn_to_mp_objects_in_iterable(
            pythonnet_method_call_overload(
                self.wrapped,
                "ResultsFor",
                [_GEAR],
                design_entity.wrapped if design_entity else None,
            )
        )

    @exception_bridge
    @enforce_parameter_types
    def results_for_gear_set(
        self: "Self", design_entity: "_2813.GearSet"
    ) -> "Iterable[_3207.GearSetCompoundSystemDeflection]":
        """Iterable[mastapy.system_model.analyses_and_results.system_deflections.compound.GearSetCompoundSystemDeflection]

        Args:
            design_entity (mastapy.system_model.part_model.gears.GearSet)
        """
        return conversion.pn_to_mp_objects_in_iterable(
            pythonnet_method_call_overload(
                self.wrapped,
                "ResultsFor",
                [_GEAR_SET],
                design_entity.wrapped if design_entity else None,
            )
        )

    @exception_bridge
    @enforce_parameter_types
    def results_for_hypoid_gear(
        self: "Self", design_entity: "_2815.HypoidGear"
    ) -> "Iterable[_3209.HypoidGearCompoundSystemDeflection]":
        """Iterable[mastapy.system_model.analyses_and_results.system_deflections.compound.HypoidGearCompoundSystemDeflection]

        Args:
            design_entity (mastapy.system_model.part_model.gears.HypoidGear)
        """
        return conversion.pn_to_mp_objects_in_iterable(
            pythonnet_method_call_overload(
                self.wrapped,
                "ResultsFor",
                [_HYPOID_GEAR],
                design_entity.wrapped if design_entity else None,
            )
        )

    @exception_bridge
    @enforce_parameter_types
    def results_for_hypoid_gear_set(
        self: "Self", design_entity: "_2816.HypoidGearSet"
    ) -> "Iterable[_3211.HypoidGearSetCompoundSystemDeflection]":
        """Iterable[mastapy.system_model.analyses_and_results.system_deflections.compound.HypoidGearSetCompoundSystemDeflection]

        Args:
            design_entity (mastapy.system_model.part_model.gears.HypoidGearSet)
        """
        return conversion.pn_to_mp_objects_in_iterable(
            pythonnet_method_call_overload(
                self.wrapped,
                "ResultsFor",
                [_HYPOID_GEAR_SET],
                design_entity.wrapped if design_entity else None,
            )
        )

    @exception_bridge
    @enforce_parameter_types
    def results_for_klingelnberg_cyclo_palloid_conical_gear(
        self: "Self", design_entity: "_2817.KlingelnbergCycloPalloidConicalGear"
    ) -> "Iterable[_3213.KlingelnbergCycloPalloidConicalGearCompoundSystemDeflection]":
        """Iterable[mastapy.system_model.analyses_and_results.system_deflections.compound.KlingelnbergCycloPalloidConicalGearCompoundSystemDeflection]

        Args:
            design_entity (mastapy.system_model.part_model.gears.KlingelnbergCycloPalloidConicalGear)
        """
        return conversion.pn_to_mp_objects_in_iterable(
            pythonnet_method_call_overload(
                self.wrapped,
                "ResultsFor",
                [_KLINGELNBERG_CYCLO_PALLOID_CONICAL_GEAR],
                design_entity.wrapped if design_entity else None,
            )
        )

    @exception_bridge
    @enforce_parameter_types
    def results_for_klingelnberg_cyclo_palloid_conical_gear_set(
        self: "Self", design_entity: "_2818.KlingelnbergCycloPalloidConicalGearSet"
    ) -> (
        "Iterable[_3215.KlingelnbergCycloPalloidConicalGearSetCompoundSystemDeflection]"
    ):
        """Iterable[mastapy.system_model.analyses_and_results.system_deflections.compound.KlingelnbergCycloPalloidConicalGearSetCompoundSystemDeflection]

        Args:
            design_entity (mastapy.system_model.part_model.gears.KlingelnbergCycloPalloidConicalGearSet)
        """
        return conversion.pn_to_mp_objects_in_iterable(
            pythonnet_method_call_overload(
                self.wrapped,
                "ResultsFor",
                [_KLINGELNBERG_CYCLO_PALLOID_CONICAL_GEAR_SET],
                design_entity.wrapped if design_entity else None,
            )
        )

    @exception_bridge
    @enforce_parameter_types
    def results_for_klingelnberg_cyclo_palloid_hypoid_gear(
        self: "Self", design_entity: "_2819.KlingelnbergCycloPalloidHypoidGear"
    ) -> "Iterable[_3216.KlingelnbergCycloPalloidHypoidGearCompoundSystemDeflection]":
        """Iterable[mastapy.system_model.analyses_and_results.system_deflections.compound.KlingelnbergCycloPalloidHypoidGearCompoundSystemDeflection]

        Args:
            design_entity (mastapy.system_model.part_model.gears.KlingelnbergCycloPalloidHypoidGear)
        """
        return conversion.pn_to_mp_objects_in_iterable(
            pythonnet_method_call_overload(
                self.wrapped,
                "ResultsFor",
                [_KLINGELNBERG_CYCLO_PALLOID_HYPOID_GEAR],
                design_entity.wrapped if design_entity else None,
            )
        )

    @exception_bridge
    @enforce_parameter_types
    def results_for_klingelnberg_cyclo_palloid_hypoid_gear_set(
        self: "Self", design_entity: "_2820.KlingelnbergCycloPalloidHypoidGearSet"
    ) -> (
        "Iterable[_3218.KlingelnbergCycloPalloidHypoidGearSetCompoundSystemDeflection]"
    ):
        """Iterable[mastapy.system_model.analyses_and_results.system_deflections.compound.KlingelnbergCycloPalloidHypoidGearSetCompoundSystemDeflection]

        Args:
            design_entity (mastapy.system_model.part_model.gears.KlingelnbergCycloPalloidHypoidGearSet)
        """
        return conversion.pn_to_mp_objects_in_iterable(
            pythonnet_method_call_overload(
                self.wrapped,
                "ResultsFor",
                [_KLINGELNBERG_CYCLO_PALLOID_HYPOID_GEAR_SET],
                design_entity.wrapped if design_entity else None,
            )
        )

    @exception_bridge
    @enforce_parameter_types
    def results_for_klingelnberg_cyclo_palloid_spiral_bevel_gear(
        self: "Self", design_entity: "_2821.KlingelnbergCycloPalloidSpiralBevelGear"
    ) -> "Iterable[_3219.KlingelnbergCycloPalloidSpiralBevelGearCompoundSystemDeflection]":
        """Iterable[mastapy.system_model.analyses_and_results.system_deflections.compound.KlingelnbergCycloPalloidSpiralBevelGearCompoundSystemDeflection]

        Args:
            design_entity (mastapy.system_model.part_model.gears.KlingelnbergCycloPalloidSpiralBevelGear)
        """
        return conversion.pn_to_mp_objects_in_iterable(
            pythonnet_method_call_overload(
                self.wrapped,
                "ResultsFor",
                [_KLINGELNBERG_CYCLO_PALLOID_SPIRAL_BEVEL_GEAR],
                design_entity.wrapped if design_entity else None,
            )
        )

    @exception_bridge
    @enforce_parameter_types
    def results_for_klingelnberg_cyclo_palloid_spiral_bevel_gear_set(
        self: "Self", design_entity: "_2822.KlingelnbergCycloPalloidSpiralBevelGearSet"
    ) -> "Iterable[_3221.KlingelnbergCycloPalloidSpiralBevelGearSetCompoundSystemDeflection]":
        """Iterable[mastapy.system_model.analyses_and_results.system_deflections.compound.KlingelnbergCycloPalloidSpiralBevelGearSetCompoundSystemDeflection]

        Args:
            design_entity (mastapy.system_model.part_model.gears.KlingelnbergCycloPalloidSpiralBevelGearSet)
        """
        return conversion.pn_to_mp_objects_in_iterable(
            pythonnet_method_call_overload(
                self.wrapped,
                "ResultsFor",
                [_KLINGELNBERG_CYCLO_PALLOID_SPIRAL_BEVEL_GEAR_SET],
                design_entity.wrapped if design_entity else None,
            )
        )

    @exception_bridge
    @enforce_parameter_types
    def results_for_planetary_gear_set(
        self: "Self", design_entity: "_2823.PlanetaryGearSet"
    ) -> "Iterable[_3233.PlanetaryGearSetCompoundSystemDeflection]":
        """Iterable[mastapy.system_model.analyses_and_results.system_deflections.compound.PlanetaryGearSetCompoundSystemDeflection]

        Args:
            design_entity (mastapy.system_model.part_model.gears.PlanetaryGearSet)
        """
        return conversion.pn_to_mp_objects_in_iterable(
            pythonnet_method_call_overload(
                self.wrapped,
                "ResultsFor",
                [_PLANETARY_GEAR_SET],
                design_entity.wrapped if design_entity else None,
            )
        )

    @exception_bridge
    @enforce_parameter_types
    def results_for_spiral_bevel_gear(
        self: "Self", design_entity: "_2825.SpiralBevelGear"
    ) -> "Iterable[_3249.SpiralBevelGearCompoundSystemDeflection]":
        """Iterable[mastapy.system_model.analyses_and_results.system_deflections.compound.SpiralBevelGearCompoundSystemDeflection]

        Args:
            design_entity (mastapy.system_model.part_model.gears.SpiralBevelGear)
        """
        return conversion.pn_to_mp_objects_in_iterable(
            pythonnet_method_call_overload(
                self.wrapped,
                "ResultsFor",
                [_SPIRAL_BEVEL_GEAR],
                design_entity.wrapped if design_entity else None,
            )
        )

    @exception_bridge
    @enforce_parameter_types
    def results_for_spiral_bevel_gear_set(
        self: "Self", design_entity: "_2826.SpiralBevelGearSet"
    ) -> "Iterable[_3251.SpiralBevelGearSetCompoundSystemDeflection]":
        """Iterable[mastapy.system_model.analyses_and_results.system_deflections.compound.SpiralBevelGearSetCompoundSystemDeflection]

        Args:
            design_entity (mastapy.system_model.part_model.gears.SpiralBevelGearSet)
        """
        return conversion.pn_to_mp_objects_in_iterable(
            pythonnet_method_call_overload(
                self.wrapped,
                "ResultsFor",
                [_SPIRAL_BEVEL_GEAR_SET],
                design_entity.wrapped if design_entity else None,
            )
        )

    @exception_bridge
    @enforce_parameter_types
    def results_for_straight_bevel_diff_gear(
        self: "Self", design_entity: "_2827.StraightBevelDiffGear"
    ) -> "Iterable[_3255.StraightBevelDiffGearCompoundSystemDeflection]":
        """Iterable[mastapy.system_model.analyses_and_results.system_deflections.compound.StraightBevelDiffGearCompoundSystemDeflection]

        Args:
            design_entity (mastapy.system_model.part_model.gears.StraightBevelDiffGear)
        """
        return conversion.pn_to_mp_objects_in_iterable(
            pythonnet_method_call_overload(
                self.wrapped,
                "ResultsFor",
                [_STRAIGHT_BEVEL_DIFF_GEAR],
                design_entity.wrapped if design_entity else None,
            )
        )

    @exception_bridge
    @enforce_parameter_types
    def results_for_straight_bevel_diff_gear_set(
        self: "Self", design_entity: "_2828.StraightBevelDiffGearSet"
    ) -> "Iterable[_3257.StraightBevelDiffGearSetCompoundSystemDeflection]":
        """Iterable[mastapy.system_model.analyses_and_results.system_deflections.compound.StraightBevelDiffGearSetCompoundSystemDeflection]

        Args:
            design_entity (mastapy.system_model.part_model.gears.StraightBevelDiffGearSet)
        """
        return conversion.pn_to_mp_objects_in_iterable(
            pythonnet_method_call_overload(
                self.wrapped,
                "ResultsFor",
                [_STRAIGHT_BEVEL_DIFF_GEAR_SET],
                design_entity.wrapped if design_entity else None,
            )
        )

    @exception_bridge
    @enforce_parameter_types
    def results_for_straight_bevel_gear(
        self: "Self", design_entity: "_2829.StraightBevelGear"
    ) -> "Iterable[_3258.StraightBevelGearCompoundSystemDeflection]":
        """Iterable[mastapy.system_model.analyses_and_results.system_deflections.compound.StraightBevelGearCompoundSystemDeflection]

        Args:
            design_entity (mastapy.system_model.part_model.gears.StraightBevelGear)
        """
        return conversion.pn_to_mp_objects_in_iterable(
            pythonnet_method_call_overload(
                self.wrapped,
                "ResultsFor",
                [_STRAIGHT_BEVEL_GEAR],
                design_entity.wrapped if design_entity else None,
            )
        )

    @exception_bridge
    @enforce_parameter_types
    def results_for_straight_bevel_gear_set(
        self: "Self", design_entity: "_2830.StraightBevelGearSet"
    ) -> "Iterable[_3260.StraightBevelGearSetCompoundSystemDeflection]":
        """Iterable[mastapy.system_model.analyses_and_results.system_deflections.compound.StraightBevelGearSetCompoundSystemDeflection]

        Args:
            design_entity (mastapy.system_model.part_model.gears.StraightBevelGearSet)
        """
        return conversion.pn_to_mp_objects_in_iterable(
            pythonnet_method_call_overload(
                self.wrapped,
                "ResultsFor",
                [_STRAIGHT_BEVEL_GEAR_SET],
                design_entity.wrapped if design_entity else None,
            )
        )

    @exception_bridge
    @enforce_parameter_types
    def results_for_straight_bevel_planet_gear(
        self: "Self", design_entity: "_2831.StraightBevelPlanetGear"
    ) -> "Iterable[_3261.StraightBevelPlanetGearCompoundSystemDeflection]":
        """Iterable[mastapy.system_model.analyses_and_results.system_deflections.compound.StraightBevelPlanetGearCompoundSystemDeflection]

        Args:
            design_entity (mastapy.system_model.part_model.gears.StraightBevelPlanetGear)
        """
        return conversion.pn_to_mp_objects_in_iterable(
            pythonnet_method_call_overload(
                self.wrapped,
                "ResultsFor",
                [_STRAIGHT_BEVEL_PLANET_GEAR],
                design_entity.wrapped if design_entity else None,
            )
        )

    @exception_bridge
    @enforce_parameter_types
    def results_for_straight_bevel_sun_gear(
        self: "Self", design_entity: "_2832.StraightBevelSunGear"
    ) -> "Iterable[_3262.StraightBevelSunGearCompoundSystemDeflection]":
        """Iterable[mastapy.system_model.analyses_and_results.system_deflections.compound.StraightBevelSunGearCompoundSystemDeflection]

        Args:
            design_entity (mastapy.system_model.part_model.gears.StraightBevelSunGear)
        """
        return conversion.pn_to_mp_objects_in_iterable(
            pythonnet_method_call_overload(
                self.wrapped,
                "ResultsFor",
                [_STRAIGHT_BEVEL_SUN_GEAR],
                design_entity.wrapped if design_entity else None,
            )
        )

    @exception_bridge
    @enforce_parameter_types
    def results_for_worm_gear(
        self: "Self", design_entity: "_2833.WormGear"
    ) -> "Iterable[_3273.WormGearCompoundSystemDeflection]":
        """Iterable[mastapy.system_model.analyses_and_results.system_deflections.compound.WormGearCompoundSystemDeflection]

        Args:
            design_entity (mastapy.system_model.part_model.gears.WormGear)
        """
        return conversion.pn_to_mp_objects_in_iterable(
            pythonnet_method_call_overload(
                self.wrapped,
                "ResultsFor",
                [_WORM_GEAR],
                design_entity.wrapped if design_entity else None,
            )
        )

    @exception_bridge
    @enforce_parameter_types
    def results_for_worm_gear_set(
        self: "Self", design_entity: "_2834.WormGearSet"
    ) -> "Iterable[_3275.WormGearSetCompoundSystemDeflection]":
        """Iterable[mastapy.system_model.analyses_and_results.system_deflections.compound.WormGearSetCompoundSystemDeflection]

        Args:
            design_entity (mastapy.system_model.part_model.gears.WormGearSet)
        """
        return conversion.pn_to_mp_objects_in_iterable(
            pythonnet_method_call_overload(
                self.wrapped,
                "ResultsFor",
                [_WORM_GEAR_SET],
                design_entity.wrapped if design_entity else None,
            )
        )

    @exception_bridge
    @enforce_parameter_types
    def results_for_zerol_bevel_gear(
        self: "Self", design_entity: "_2835.ZerolBevelGear"
    ) -> "Iterable[_3276.ZerolBevelGearCompoundSystemDeflection]":
        """Iterable[mastapy.system_model.analyses_and_results.system_deflections.compound.ZerolBevelGearCompoundSystemDeflection]

        Args:
            design_entity (mastapy.system_model.part_model.gears.ZerolBevelGear)
        """
        return conversion.pn_to_mp_objects_in_iterable(
            pythonnet_method_call_overload(
                self.wrapped,
                "ResultsFor",
                [_ZEROL_BEVEL_GEAR],
                design_entity.wrapped if design_entity else None,
            )
        )

    @exception_bridge
    @enforce_parameter_types
    def results_for_zerol_bevel_gear_set(
        self: "Self", design_entity: "_2836.ZerolBevelGearSet"
    ) -> "Iterable[_3278.ZerolBevelGearSetCompoundSystemDeflection]":
        """Iterable[mastapy.system_model.analyses_and_results.system_deflections.compound.ZerolBevelGearSetCompoundSystemDeflection]

        Args:
            design_entity (mastapy.system_model.part_model.gears.ZerolBevelGearSet)
        """
        return conversion.pn_to_mp_objects_in_iterable(
            pythonnet_method_call_overload(
                self.wrapped,
                "ResultsFor",
                [_ZEROL_BEVEL_GEAR_SET],
                design_entity.wrapped if design_entity else None,
            )
        )

    @exception_bridge
    @enforce_parameter_types
    def results_for_cycloidal_assembly(
        self: "Self", design_entity: "_2850.CycloidalAssembly"
    ) -> "Iterable[_3189.CycloidalAssemblyCompoundSystemDeflection]":
        """Iterable[mastapy.system_model.analyses_and_results.system_deflections.compound.CycloidalAssemblyCompoundSystemDeflection]

        Args:
            design_entity (mastapy.system_model.part_model.cycloidal.CycloidalAssembly)
        """
        return conversion.pn_to_mp_objects_in_iterable(
            pythonnet_method_call_overload(
                self.wrapped,
                "ResultsFor",
                [_CYCLOIDAL_ASSEMBLY],
                design_entity.wrapped if design_entity else None,
            )
        )

    @exception_bridge
    @enforce_parameter_types
    def results_for_cycloidal_disc(
        self: "Self", design_entity: "_2851.CycloidalDisc"
    ) -> "Iterable[_3191.CycloidalDiscCompoundSystemDeflection]":
        """Iterable[mastapy.system_model.analyses_and_results.system_deflections.compound.CycloidalDiscCompoundSystemDeflection]

        Args:
            design_entity (mastapy.system_model.part_model.cycloidal.CycloidalDisc)
        """
        return conversion.pn_to_mp_objects_in_iterable(
            pythonnet_method_call_overload(
                self.wrapped,
                "ResultsFor",
                [_CYCLOIDAL_DISC],
                design_entity.wrapped if design_entity else None,
            )
        )

    @exception_bridge
    @enforce_parameter_types
    def results_for_ring_pins(
        self: "Self", design_entity: "_2852.RingPins"
    ) -> "Iterable[_3238.RingPinsCompoundSystemDeflection]":
        """Iterable[mastapy.system_model.analyses_and_results.system_deflections.compound.RingPinsCompoundSystemDeflection]

        Args:
            design_entity (mastapy.system_model.part_model.cycloidal.RingPins)
        """
        return conversion.pn_to_mp_objects_in_iterable(
            pythonnet_method_call_overload(
                self.wrapped,
                "ResultsFor",
                [_RING_PINS],
                design_entity.wrapped if design_entity else None,
            )
        )

    @exception_bridge
    @enforce_parameter_types
    def results_for_part_to_part_shear_coupling(
        self: "Self", design_entity: "_2872.PartToPartShearCoupling"
    ) -> "Iterable[_3229.PartToPartShearCouplingCompoundSystemDeflection]":
        """Iterable[mastapy.system_model.analyses_and_results.system_deflections.compound.PartToPartShearCouplingCompoundSystemDeflection]

        Args:
            design_entity (mastapy.system_model.part_model.couplings.PartToPartShearCoupling)
        """
        return conversion.pn_to_mp_objects_in_iterable(
            pythonnet_method_call_overload(
                self.wrapped,
                "ResultsFor",
                [_PART_TO_PART_SHEAR_COUPLING],
                design_entity.wrapped if design_entity else None,
            )
        )

    @exception_bridge
    @enforce_parameter_types
    def results_for_part_to_part_shear_coupling_half(
        self: "Self", design_entity: "_2873.PartToPartShearCouplingHalf"
    ) -> "Iterable[_3231.PartToPartShearCouplingHalfCompoundSystemDeflection]":
        """Iterable[mastapy.system_model.analyses_and_results.system_deflections.compound.PartToPartShearCouplingHalfCompoundSystemDeflection]

        Args:
            design_entity (mastapy.system_model.part_model.couplings.PartToPartShearCouplingHalf)
        """
        return conversion.pn_to_mp_objects_in_iterable(
            pythonnet_method_call_overload(
                self.wrapped,
                "ResultsFor",
                [_PART_TO_PART_SHEAR_COUPLING_HALF],
                design_entity.wrapped if design_entity else None,
            )
        )

    @exception_bridge
    @enforce_parameter_types
    def results_for_belt_drive(
        self: "Self", design_entity: "_2859.BeltDrive"
    ) -> "Iterable[_3156.BeltDriveCompoundSystemDeflection]":
        """Iterable[mastapy.system_model.analyses_and_results.system_deflections.compound.BeltDriveCompoundSystemDeflection]

        Args:
            design_entity (mastapy.system_model.part_model.couplings.BeltDrive)
        """
        return conversion.pn_to_mp_objects_in_iterable(
            pythonnet_method_call_overload(
                self.wrapped,
                "ResultsFor",
                [_BELT_DRIVE],
                design_entity.wrapped if design_entity else None,
            )
        )

    @exception_bridge
    @enforce_parameter_types
    def results_for_clutch(
        self: "Self", design_entity: "_2861.Clutch"
    ) -> "Iterable[_3167.ClutchCompoundSystemDeflection]":
        """Iterable[mastapy.system_model.analyses_and_results.system_deflections.compound.ClutchCompoundSystemDeflection]

        Args:
            design_entity (mastapy.system_model.part_model.couplings.Clutch)
        """
        return conversion.pn_to_mp_objects_in_iterable(
            pythonnet_method_call_overload(
                self.wrapped,
                "ResultsFor",
                [_CLUTCH],
                design_entity.wrapped if design_entity else None,
            )
        )

    @exception_bridge
    @enforce_parameter_types
    def results_for_clutch_half(
        self: "Self", design_entity: "_2862.ClutchHalf"
    ) -> "Iterable[_3169.ClutchHalfCompoundSystemDeflection]":
        """Iterable[mastapy.system_model.analyses_and_results.system_deflections.compound.ClutchHalfCompoundSystemDeflection]

        Args:
            design_entity (mastapy.system_model.part_model.couplings.ClutchHalf)
        """
        return conversion.pn_to_mp_objects_in_iterable(
            pythonnet_method_call_overload(
                self.wrapped,
                "ResultsFor",
                [_CLUTCH_HALF],
                design_entity.wrapped if design_entity else None,
            )
        )

    @exception_bridge
    @enforce_parameter_types
    def results_for_concept_coupling(
        self: "Self", design_entity: "_2864.ConceptCoupling"
    ) -> "Iterable[_3172.ConceptCouplingCompoundSystemDeflection]":
        """Iterable[mastapy.system_model.analyses_and_results.system_deflections.compound.ConceptCouplingCompoundSystemDeflection]

        Args:
            design_entity (mastapy.system_model.part_model.couplings.ConceptCoupling)
        """
        return conversion.pn_to_mp_objects_in_iterable(
            pythonnet_method_call_overload(
                self.wrapped,
                "ResultsFor",
                [_CONCEPT_COUPLING],
                design_entity.wrapped if design_entity else None,
            )
        )

    @exception_bridge
    @enforce_parameter_types
    def results_for_concept_coupling_half(
        self: "Self", design_entity: "_2865.ConceptCouplingHalf"
    ) -> "Iterable[_3174.ConceptCouplingHalfCompoundSystemDeflection]":
        """Iterable[mastapy.system_model.analyses_and_results.system_deflections.compound.ConceptCouplingHalfCompoundSystemDeflection]

        Args:
            design_entity (mastapy.system_model.part_model.couplings.ConceptCouplingHalf)
        """
        return conversion.pn_to_mp_objects_in_iterable(
            pythonnet_method_call_overload(
                self.wrapped,
                "ResultsFor",
                [_CONCEPT_COUPLING_HALF],
                design_entity.wrapped if design_entity else None,
            )
        )

    @exception_bridge
    @enforce_parameter_types
    def results_for_coupling(
        self: "Self", design_entity: "_2867.Coupling"
    ) -> "Iterable[_3183.CouplingCompoundSystemDeflection]":
        """Iterable[mastapy.system_model.analyses_and_results.system_deflections.compound.CouplingCompoundSystemDeflection]

        Args:
            design_entity (mastapy.system_model.part_model.couplings.Coupling)
        """
        return conversion.pn_to_mp_objects_in_iterable(
            pythonnet_method_call_overload(
                self.wrapped,
                "ResultsFor",
                [_COUPLING],
                design_entity.wrapped if design_entity else None,
            )
        )

    @exception_bridge
    @enforce_parameter_types
    def results_for_coupling_half(
        self: "Self", design_entity: "_2868.CouplingHalf"
    ) -> "Iterable[_3185.CouplingHalfCompoundSystemDeflection]":
        """Iterable[mastapy.system_model.analyses_and_results.system_deflections.compound.CouplingHalfCompoundSystemDeflection]

        Args:
            design_entity (mastapy.system_model.part_model.couplings.CouplingHalf)
        """
        return conversion.pn_to_mp_objects_in_iterable(
            pythonnet_method_call_overload(
                self.wrapped,
                "ResultsFor",
                [_COUPLING_HALF],
                design_entity.wrapped if design_entity else None,
            )
        )

    @exception_bridge
    @enforce_parameter_types
    def results_for_cvt(
        self: "Self", design_entity: "_2870.CVT"
    ) -> "Iterable[_3187.CVTCompoundSystemDeflection]":
        """Iterable[mastapy.system_model.analyses_and_results.system_deflections.compound.CVTCompoundSystemDeflection]

        Args:
            design_entity (mastapy.system_model.part_model.couplings.CVT)
        """
        return conversion.pn_to_mp_objects_in_iterable(
            pythonnet_method_call_overload(
                self.wrapped,
                "ResultsFor",
                [_CVT],
                design_entity.wrapped if design_entity else None,
            )
        )

    @exception_bridge
    @enforce_parameter_types
    def results_for_cvt_pulley(
        self: "Self", design_entity: "_2871.CVTPulley"
    ) -> "Iterable[_3188.CVTPulleyCompoundSystemDeflection]":
        """Iterable[mastapy.system_model.analyses_and_results.system_deflections.compound.CVTPulleyCompoundSystemDeflection]

        Args:
            design_entity (mastapy.system_model.part_model.couplings.CVTPulley)
        """
        return conversion.pn_to_mp_objects_in_iterable(
            pythonnet_method_call_overload(
                self.wrapped,
                "ResultsFor",
                [_CVT_PULLEY],
                design_entity.wrapped if design_entity else None,
            )
        )

    @exception_bridge
    @enforce_parameter_types
    def results_for_pulley(
        self: "Self", design_entity: "_2875.Pulley"
    ) -> "Iterable[_3237.PulleyCompoundSystemDeflection]":
        """Iterable[mastapy.system_model.analyses_and_results.system_deflections.compound.PulleyCompoundSystemDeflection]

        Args:
            design_entity (mastapy.system_model.part_model.couplings.Pulley)
        """
        return conversion.pn_to_mp_objects_in_iterable(
            pythonnet_method_call_overload(
                self.wrapped,
                "ResultsFor",
                [_PULLEY],
                design_entity.wrapped if design_entity else None,
            )
        )

    @exception_bridge
    @enforce_parameter_types
    def results_for_shaft_hub_connection(
        self: "Self", design_entity: "_2884.ShaftHubConnection"
    ) -> "Iterable[_3246.ShaftHubConnectionCompoundSystemDeflection]":
        """Iterable[mastapy.system_model.analyses_and_results.system_deflections.compound.ShaftHubConnectionCompoundSystemDeflection]

        Args:
            design_entity (mastapy.system_model.part_model.couplings.ShaftHubConnection)
        """
        return conversion.pn_to_mp_objects_in_iterable(
            pythonnet_method_call_overload(
                self.wrapped,
                "ResultsFor",
                [_SHAFT_HUB_CONNECTION],
                design_entity.wrapped if design_entity else None,
            )
        )

    @exception_bridge
    @enforce_parameter_types
    def results_for_rolling_ring(
        self: "Self", design_entity: "_2882.RollingRing"
    ) -> "Iterable[_3241.RollingRingCompoundSystemDeflection]":
        """Iterable[mastapy.system_model.analyses_and_results.system_deflections.compound.RollingRingCompoundSystemDeflection]

        Args:
            design_entity (mastapy.system_model.part_model.couplings.RollingRing)
        """
        return conversion.pn_to_mp_objects_in_iterable(
            pythonnet_method_call_overload(
                self.wrapped,
                "ResultsFor",
                [_ROLLING_RING],
                design_entity.wrapped if design_entity else None,
            )
        )

    @exception_bridge
    @enforce_parameter_types
    def results_for_rolling_ring_assembly(
        self: "Self", design_entity: "_2883.RollingRingAssembly"
    ) -> "Iterable[_3240.RollingRingAssemblyCompoundSystemDeflection]":
        """Iterable[mastapy.system_model.analyses_and_results.system_deflections.compound.RollingRingAssemblyCompoundSystemDeflection]

        Args:
            design_entity (mastapy.system_model.part_model.couplings.RollingRingAssembly)
        """
        return conversion.pn_to_mp_objects_in_iterable(
            pythonnet_method_call_overload(
                self.wrapped,
                "ResultsFor",
                [_ROLLING_RING_ASSEMBLY],
                design_entity.wrapped if design_entity else None,
            )
        )

    @exception_bridge
    @enforce_parameter_types
    def results_for_spring_damper(
        self: "Self", design_entity: "_2890.SpringDamper"
    ) -> "Iterable[_3252.SpringDamperCompoundSystemDeflection]":
        """Iterable[mastapy.system_model.analyses_and_results.system_deflections.compound.SpringDamperCompoundSystemDeflection]

        Args:
            design_entity (mastapy.system_model.part_model.couplings.SpringDamper)
        """
        return conversion.pn_to_mp_objects_in_iterable(
            pythonnet_method_call_overload(
                self.wrapped,
                "ResultsFor",
                [_SPRING_DAMPER],
                design_entity.wrapped if design_entity else None,
            )
        )

    @exception_bridge
    @enforce_parameter_types
    def results_for_spring_damper_half(
        self: "Self", design_entity: "_2891.SpringDamperHalf"
    ) -> "Iterable[_3254.SpringDamperHalfCompoundSystemDeflection]":
        """Iterable[mastapy.system_model.analyses_and_results.system_deflections.compound.SpringDamperHalfCompoundSystemDeflection]

        Args:
            design_entity (mastapy.system_model.part_model.couplings.SpringDamperHalf)
        """
        return conversion.pn_to_mp_objects_in_iterable(
            pythonnet_method_call_overload(
                self.wrapped,
                "ResultsFor",
                [_SPRING_DAMPER_HALF],
                design_entity.wrapped if design_entity else None,
            )
        )

    @exception_bridge
    @enforce_parameter_types
    def results_for_synchroniser(
        self: "Self", design_entity: "_2892.Synchroniser"
    ) -> "Iterable[_3263.SynchroniserCompoundSystemDeflection]":
        """Iterable[mastapy.system_model.analyses_and_results.system_deflections.compound.SynchroniserCompoundSystemDeflection]

        Args:
            design_entity (mastapy.system_model.part_model.couplings.Synchroniser)
        """
        return conversion.pn_to_mp_objects_in_iterable(
            pythonnet_method_call_overload(
                self.wrapped,
                "ResultsFor",
                [_SYNCHRONISER],
                design_entity.wrapped if design_entity else None,
            )
        )

    @exception_bridge
    @enforce_parameter_types
    def results_for_synchroniser_half(
        self: "Self", design_entity: "_2894.SynchroniserHalf"
    ) -> "Iterable[_3264.SynchroniserHalfCompoundSystemDeflection]":
        """Iterable[mastapy.system_model.analyses_and_results.system_deflections.compound.SynchroniserHalfCompoundSystemDeflection]

        Args:
            design_entity (mastapy.system_model.part_model.couplings.SynchroniserHalf)
        """
        return conversion.pn_to_mp_objects_in_iterable(
            pythonnet_method_call_overload(
                self.wrapped,
                "ResultsFor",
                [_SYNCHRONISER_HALF],
                design_entity.wrapped if design_entity else None,
            )
        )

    @exception_bridge
    @enforce_parameter_types
    def results_for_synchroniser_part(
        self: "Self", design_entity: "_2895.SynchroniserPart"
    ) -> "Iterable[_3265.SynchroniserPartCompoundSystemDeflection]":
        """Iterable[mastapy.system_model.analyses_and_results.system_deflections.compound.SynchroniserPartCompoundSystemDeflection]

        Args:
            design_entity (mastapy.system_model.part_model.couplings.SynchroniserPart)
        """
        return conversion.pn_to_mp_objects_in_iterable(
            pythonnet_method_call_overload(
                self.wrapped,
                "ResultsFor",
                [_SYNCHRONISER_PART],
                design_entity.wrapped if design_entity else None,
            )
        )

    @exception_bridge
    @enforce_parameter_types
    def results_for_synchroniser_sleeve(
        self: "Self", design_entity: "_2896.SynchroniserSleeve"
    ) -> "Iterable[_3266.SynchroniserSleeveCompoundSystemDeflection]":
        """Iterable[mastapy.system_model.analyses_and_results.system_deflections.compound.SynchroniserSleeveCompoundSystemDeflection]

        Args:
            design_entity (mastapy.system_model.part_model.couplings.SynchroniserSleeve)
        """
        return conversion.pn_to_mp_objects_in_iterable(
            pythonnet_method_call_overload(
                self.wrapped,
                "ResultsFor",
                [_SYNCHRONISER_SLEEVE],
                design_entity.wrapped if design_entity else None,
            )
        )

    @exception_bridge
    @enforce_parameter_types
    def results_for_torque_converter(
        self: "Self", design_entity: "_2897.TorqueConverter"
    ) -> "Iterable[_3267.TorqueConverterCompoundSystemDeflection]":
        """Iterable[mastapy.system_model.analyses_and_results.system_deflections.compound.TorqueConverterCompoundSystemDeflection]

        Args:
            design_entity (mastapy.system_model.part_model.couplings.TorqueConverter)
        """
        return conversion.pn_to_mp_objects_in_iterable(
            pythonnet_method_call_overload(
                self.wrapped,
                "ResultsFor",
                [_TORQUE_CONVERTER],
                design_entity.wrapped if design_entity else None,
            )
        )

    @exception_bridge
    @enforce_parameter_types
    def results_for_torque_converter_pump(
        self: "Self", design_entity: "_2898.TorqueConverterPump"
    ) -> "Iterable[_3269.TorqueConverterPumpCompoundSystemDeflection]":
        """Iterable[mastapy.system_model.analyses_and_results.system_deflections.compound.TorqueConverterPumpCompoundSystemDeflection]

        Args:
            design_entity (mastapy.system_model.part_model.couplings.TorqueConverterPump)
        """
        return conversion.pn_to_mp_objects_in_iterable(
            pythonnet_method_call_overload(
                self.wrapped,
                "ResultsFor",
                [_TORQUE_CONVERTER_PUMP],
                design_entity.wrapped if design_entity else None,
            )
        )

    @exception_bridge
    @enforce_parameter_types
    def results_for_torque_converter_turbine(
        self: "Self", design_entity: "_2900.TorqueConverterTurbine"
    ) -> "Iterable[_3270.TorqueConverterTurbineCompoundSystemDeflection]":
        """Iterable[mastapy.system_model.analyses_and_results.system_deflections.compound.TorqueConverterTurbineCompoundSystemDeflection]

        Args:
            design_entity (mastapy.system_model.part_model.couplings.TorqueConverterTurbine)
        """
        return conversion.pn_to_mp_objects_in_iterable(
            pythonnet_method_call_overload(
                self.wrapped,
                "ResultsFor",
                [_TORQUE_CONVERTER_TURBINE],
                design_entity.wrapped if design_entity else None,
            )
        )

    @exception_bridge
    @enforce_parameter_types
    def results_for_shaft_to_mountable_component_connection(
        self: "Self", design_entity: "_2554.ShaftToMountableComponentConnection"
    ) -> "Iterable[_3247.ShaftToMountableComponentConnectionCompoundSystemDeflection]":
        """Iterable[mastapy.system_model.analyses_and_results.system_deflections.compound.ShaftToMountableComponentConnectionCompoundSystemDeflection]

        Args:
            design_entity (mastapy.system_model.connections_and_sockets.ShaftToMountableComponentConnection)
        """
        return conversion.pn_to_mp_objects_in_iterable(
            pythonnet_method_call_overload(
                self.wrapped,
                "ResultsFor",
                [_SHAFT_TO_MOUNTABLE_COMPONENT_CONNECTION],
                design_entity.wrapped if design_entity else None,
            )
        )

    @exception_bridge
    @enforce_parameter_types
    def results_for_cvt_belt_connection(
        self: "Self", design_entity: "_2532.CVTBeltConnection"
    ) -> "Iterable[_3186.CVTBeltConnectionCompoundSystemDeflection]":
        """Iterable[mastapy.system_model.analyses_and_results.system_deflections.compound.CVTBeltConnectionCompoundSystemDeflection]

        Args:
            design_entity (mastapy.system_model.connections_and_sockets.CVTBeltConnection)
        """
        return conversion.pn_to_mp_objects_in_iterable(
            pythonnet_method_call_overload(
                self.wrapped,
                "ResultsFor",
                [_CVT_BELT_CONNECTION],
                design_entity.wrapped if design_entity else None,
            )
        )

    @exception_bridge
    @enforce_parameter_types
    def results_for_belt_connection(
        self: "Self", design_entity: "_2527.BeltConnection"
    ) -> "Iterable[_3155.BeltConnectionCompoundSystemDeflection]":
        """Iterable[mastapy.system_model.analyses_and_results.system_deflections.compound.BeltConnectionCompoundSystemDeflection]

        Args:
            design_entity (mastapy.system_model.connections_and_sockets.BeltConnection)
        """
        return conversion.pn_to_mp_objects_in_iterable(
            pythonnet_method_call_overload(
                self.wrapped,
                "ResultsFor",
                [_BELT_CONNECTION],
                design_entity.wrapped if design_entity else None,
            )
        )

    @exception_bridge
    @enforce_parameter_types
    def results_for_coaxial_connection(
        self: "Self", design_entity: "_2528.CoaxialConnection"
    ) -> "Iterable[_3170.CoaxialConnectionCompoundSystemDeflection]":
        """Iterable[mastapy.system_model.analyses_and_results.system_deflections.compound.CoaxialConnectionCompoundSystemDeflection]

        Args:
            design_entity (mastapy.system_model.connections_and_sockets.CoaxialConnection)
        """
        return conversion.pn_to_mp_objects_in_iterable(
            pythonnet_method_call_overload(
                self.wrapped,
                "ResultsFor",
                [_COAXIAL_CONNECTION],
                design_entity.wrapped if design_entity else None,
            )
        )

    @exception_bridge
    @enforce_parameter_types
    def results_for_connection(
        self: "Self", design_entity: "_2531.Connection"
    ) -> "Iterable[_3181.ConnectionCompoundSystemDeflection]":
        """Iterable[mastapy.system_model.analyses_and_results.system_deflections.compound.ConnectionCompoundSystemDeflection]

        Args:
            design_entity (mastapy.system_model.connections_and_sockets.Connection)
        """
        return conversion.pn_to_mp_objects_in_iterable(
            pythonnet_method_call_overload(
                self.wrapped,
                "ResultsFor",
                [_CONNECTION],
                design_entity.wrapped if design_entity else None,
            )
        )

    @exception_bridge
    @enforce_parameter_types
    def results_for_inter_mountable_component_connection(
        self: "Self", design_entity: "_2540.InterMountableComponentConnection"
    ) -> "Iterable[_3212.InterMountableComponentConnectionCompoundSystemDeflection]":
        """Iterable[mastapy.system_model.analyses_and_results.system_deflections.compound.InterMountableComponentConnectionCompoundSystemDeflection]

        Args:
            design_entity (mastapy.system_model.connections_and_sockets.InterMountableComponentConnection)
        """
        return conversion.pn_to_mp_objects_in_iterable(
            pythonnet_method_call_overload(
                self.wrapped,
                "ResultsFor",
                [_INTER_MOUNTABLE_COMPONENT_CONNECTION],
                design_entity.wrapped if design_entity else None,
            )
        )

    @exception_bridge
    @enforce_parameter_types
    def results_for_planetary_connection(
        self: "Self", design_entity: "_2546.PlanetaryConnection"
    ) -> "Iterable[_3232.PlanetaryConnectionCompoundSystemDeflection]":
        """Iterable[mastapy.system_model.analyses_and_results.system_deflections.compound.PlanetaryConnectionCompoundSystemDeflection]

        Args:
            design_entity (mastapy.system_model.connections_and_sockets.PlanetaryConnection)
        """
        return conversion.pn_to_mp_objects_in_iterable(
            pythonnet_method_call_overload(
                self.wrapped,
                "ResultsFor",
                [_PLANETARY_CONNECTION],
                design_entity.wrapped if design_entity else None,
            )
        )

    @exception_bridge
    @enforce_parameter_types
    def results_for_rolling_ring_connection(
        self: "Self", design_entity: "_2551.RollingRingConnection"
    ) -> "Iterable[_3242.RollingRingConnectionCompoundSystemDeflection]":
        """Iterable[mastapy.system_model.analyses_and_results.system_deflections.compound.RollingRingConnectionCompoundSystemDeflection]

        Args:
            design_entity (mastapy.system_model.connections_and_sockets.RollingRingConnection)
        """
        return conversion.pn_to_mp_objects_in_iterable(
            pythonnet_method_call_overload(
                self.wrapped,
                "ResultsFor",
                [_ROLLING_RING_CONNECTION],
                design_entity.wrapped if design_entity else None,
            )
        )

    @exception_bridge
    @enforce_parameter_types
    def results_for_abstract_shaft_to_mountable_component_connection(
        self: "Self", design_entity: "_2524.AbstractShaftToMountableComponentConnection"
    ) -> "Iterable[_3149.AbstractShaftToMountableComponentConnectionCompoundSystemDeflection]":
        """Iterable[mastapy.system_model.analyses_and_results.system_deflections.compound.AbstractShaftToMountableComponentConnectionCompoundSystemDeflection]

        Args:
            design_entity (mastapy.system_model.connections_and_sockets.AbstractShaftToMountableComponentConnection)
        """
        return conversion.pn_to_mp_objects_in_iterable(
            pythonnet_method_call_overload(
                self.wrapped,
                "ResultsFor",
                [_ABSTRACT_SHAFT_TO_MOUNTABLE_COMPONENT_CONNECTION],
                design_entity.wrapped if design_entity else None,
            )
        )

    @exception_bridge
    @enforce_parameter_types
    def results_for_bevel_differential_gear_mesh(
        self: "Self", design_entity: "_2560.BevelDifferentialGearMesh"
    ) -> "Iterable[_3158.BevelDifferentialGearMeshCompoundSystemDeflection]":
        """Iterable[mastapy.system_model.analyses_and_results.system_deflections.compound.BevelDifferentialGearMeshCompoundSystemDeflection]

        Args:
            design_entity (mastapy.system_model.connections_and_sockets.gears.BevelDifferentialGearMesh)
        """
        return conversion.pn_to_mp_objects_in_iterable(
            pythonnet_method_call_overload(
                self.wrapped,
                "ResultsFor",
                [_BEVEL_DIFFERENTIAL_GEAR_MESH],
                design_entity.wrapped if design_entity else None,
            )
        )

    @exception_bridge
    @enforce_parameter_types
    def results_for_concept_gear_mesh(
        self: "Self", design_entity: "_2564.ConceptGearMesh"
    ) -> "Iterable[_3176.ConceptGearMeshCompoundSystemDeflection]":
        """Iterable[mastapy.system_model.analyses_and_results.system_deflections.compound.ConceptGearMeshCompoundSystemDeflection]

        Args:
            design_entity (mastapy.system_model.connections_and_sockets.gears.ConceptGearMesh)
        """
        return conversion.pn_to_mp_objects_in_iterable(
            pythonnet_method_call_overload(
                self.wrapped,
                "ResultsFor",
                [_CONCEPT_GEAR_MESH],
                design_entity.wrapped if design_entity else None,
            )
        )

    @exception_bridge
    @enforce_parameter_types
    def results_for_face_gear_mesh(
        self: "Self", design_entity: "_2570.FaceGearMesh"
    ) -> "Iterable[_3201.FaceGearMeshCompoundSystemDeflection]":
        """Iterable[mastapy.system_model.analyses_and_results.system_deflections.compound.FaceGearMeshCompoundSystemDeflection]

        Args:
            design_entity (mastapy.system_model.connections_and_sockets.gears.FaceGearMesh)
        """
        return conversion.pn_to_mp_objects_in_iterable(
            pythonnet_method_call_overload(
                self.wrapped,
                "ResultsFor",
                [_FACE_GEAR_MESH],
                design_entity.wrapped if design_entity else None,
            )
        )

    @exception_bridge
    @enforce_parameter_types
    def results_for_straight_bevel_diff_gear_mesh(
        self: "Self", design_entity: "_2584.StraightBevelDiffGearMesh"
    ) -> "Iterable[_3256.StraightBevelDiffGearMeshCompoundSystemDeflection]":
        """Iterable[mastapy.system_model.analyses_and_results.system_deflections.compound.StraightBevelDiffGearMeshCompoundSystemDeflection]

        Args:
            design_entity (mastapy.system_model.connections_and_sockets.gears.StraightBevelDiffGearMesh)
        """
        return conversion.pn_to_mp_objects_in_iterable(
            pythonnet_method_call_overload(
                self.wrapped,
                "ResultsFor",
                [_STRAIGHT_BEVEL_DIFF_GEAR_MESH],
                design_entity.wrapped if design_entity else None,
            )
        )

    @exception_bridge
    @enforce_parameter_types
    def results_for_bevel_gear_mesh(
        self: "Self", design_entity: "_2562.BevelGearMesh"
    ) -> "Iterable[_3163.BevelGearMeshCompoundSystemDeflection]":
        """Iterable[mastapy.system_model.analyses_and_results.system_deflections.compound.BevelGearMeshCompoundSystemDeflection]

        Args:
            design_entity (mastapy.system_model.connections_and_sockets.gears.BevelGearMesh)
        """
        return conversion.pn_to_mp_objects_in_iterable(
            pythonnet_method_call_overload(
                self.wrapped,
                "ResultsFor",
                [_BEVEL_GEAR_MESH],
                design_entity.wrapped if design_entity else None,
            )
        )

    @exception_bridge
    @enforce_parameter_types
    def results_for_conical_gear_mesh(
        self: "Self", design_entity: "_2566.ConicalGearMesh"
    ) -> "Iterable[_3179.ConicalGearMeshCompoundSystemDeflection]":
        """Iterable[mastapy.system_model.analyses_and_results.system_deflections.compound.ConicalGearMeshCompoundSystemDeflection]

        Args:
            design_entity (mastapy.system_model.connections_and_sockets.gears.ConicalGearMesh)
        """
        return conversion.pn_to_mp_objects_in_iterable(
            pythonnet_method_call_overload(
                self.wrapped,
                "ResultsFor",
                [_CONICAL_GEAR_MESH],
                design_entity.wrapped if design_entity else None,
            )
        )

    @exception_bridge
    @enforce_parameter_types
    def results_for_agma_gleason_conical_gear_mesh(
        self: "Self", design_entity: "_2558.AGMAGleasonConicalGearMesh"
    ) -> "Iterable[_3151.AGMAGleasonConicalGearMeshCompoundSystemDeflection]":
        """Iterable[mastapy.system_model.analyses_and_results.system_deflections.compound.AGMAGleasonConicalGearMeshCompoundSystemDeflection]

        Args:
            design_entity (mastapy.system_model.connections_and_sockets.gears.AGMAGleasonConicalGearMesh)
        """
        return conversion.pn_to_mp_objects_in_iterable(
            pythonnet_method_call_overload(
                self.wrapped,
                "ResultsFor",
                [_AGMA_GLEASON_CONICAL_GEAR_MESH],
                design_entity.wrapped if design_entity else None,
            )
        )

    @exception_bridge
    @enforce_parameter_types
    def results_for_cylindrical_gear_mesh(
        self: "Self", design_entity: "_2568.CylindricalGearMesh"
    ) -> "Iterable[_3194.CylindricalGearMeshCompoundSystemDeflection]":
        """Iterable[mastapy.system_model.analyses_and_results.system_deflections.compound.CylindricalGearMeshCompoundSystemDeflection]

        Args:
            design_entity (mastapy.system_model.connections_and_sockets.gears.CylindricalGearMesh)
        """
        return conversion.pn_to_mp_objects_in_iterable(
            pythonnet_method_call_overload(
                self.wrapped,
                "ResultsFor",
                [_CYLINDRICAL_GEAR_MESH],
                design_entity.wrapped if design_entity else None,
            )
        )

    @exception_bridge
    @enforce_parameter_types
    def results_for_hypoid_gear_mesh(
        self: "Self", design_entity: "_2574.HypoidGearMesh"
    ) -> "Iterable[_3210.HypoidGearMeshCompoundSystemDeflection]":
        """Iterable[mastapy.system_model.analyses_and_results.system_deflections.compound.HypoidGearMeshCompoundSystemDeflection]

        Args:
            design_entity (mastapy.system_model.connections_and_sockets.gears.HypoidGearMesh)
        """
        return conversion.pn_to_mp_objects_in_iterable(
            pythonnet_method_call_overload(
                self.wrapped,
                "ResultsFor",
                [_HYPOID_GEAR_MESH],
                design_entity.wrapped if design_entity else None,
            )
        )

    @exception_bridge
    @enforce_parameter_types
    def results_for_klingelnberg_cyclo_palloid_conical_gear_mesh(
        self: "Self", design_entity: "_2577.KlingelnbergCycloPalloidConicalGearMesh"
    ) -> "Iterable[_3214.KlingelnbergCycloPalloidConicalGearMeshCompoundSystemDeflection]":
        """Iterable[mastapy.system_model.analyses_and_results.system_deflections.compound.KlingelnbergCycloPalloidConicalGearMeshCompoundSystemDeflection]

        Args:
            design_entity (mastapy.system_model.connections_and_sockets.gears.KlingelnbergCycloPalloidConicalGearMesh)
        """
        return conversion.pn_to_mp_objects_in_iterable(
            pythonnet_method_call_overload(
                self.wrapped,
                "ResultsFor",
                [_KLINGELNBERG_CYCLO_PALLOID_CONICAL_GEAR_MESH],
                design_entity.wrapped if design_entity else None,
            )
        )

    @exception_bridge
    @enforce_parameter_types
    def results_for_klingelnberg_cyclo_palloid_hypoid_gear_mesh(
        self: "Self", design_entity: "_2578.KlingelnbergCycloPalloidHypoidGearMesh"
    ) -> (
        "Iterable[_3217.KlingelnbergCycloPalloidHypoidGearMeshCompoundSystemDeflection]"
    ):
        """Iterable[mastapy.system_model.analyses_and_results.system_deflections.compound.KlingelnbergCycloPalloidHypoidGearMeshCompoundSystemDeflection]

        Args:
            design_entity (mastapy.system_model.connections_and_sockets.gears.KlingelnbergCycloPalloidHypoidGearMesh)
        """
        return conversion.pn_to_mp_objects_in_iterable(
            pythonnet_method_call_overload(
                self.wrapped,
                "ResultsFor",
                [_KLINGELNBERG_CYCLO_PALLOID_HYPOID_GEAR_MESH],
                design_entity.wrapped if design_entity else None,
            )
        )

    @exception_bridge
    @enforce_parameter_types
    def results_for_klingelnberg_cyclo_palloid_spiral_bevel_gear_mesh(
        self: "Self", design_entity: "_2579.KlingelnbergCycloPalloidSpiralBevelGearMesh"
    ) -> "Iterable[_3220.KlingelnbergCycloPalloidSpiralBevelGearMeshCompoundSystemDeflection]":
        """Iterable[mastapy.system_model.analyses_and_results.system_deflections.compound.KlingelnbergCycloPalloidSpiralBevelGearMeshCompoundSystemDeflection]

        Args:
            design_entity (mastapy.system_model.connections_and_sockets.gears.KlingelnbergCycloPalloidSpiralBevelGearMesh)
        """
        return conversion.pn_to_mp_objects_in_iterable(
            pythonnet_method_call_overload(
                self.wrapped,
                "ResultsFor",
                [_KLINGELNBERG_CYCLO_PALLOID_SPIRAL_BEVEL_GEAR_MESH],
                design_entity.wrapped if design_entity else None,
            )
        )

    @exception_bridge
    @enforce_parameter_types
    def results_for_spiral_bevel_gear_mesh(
        self: "Self", design_entity: "_2582.SpiralBevelGearMesh"
    ) -> "Iterable[_3250.SpiralBevelGearMeshCompoundSystemDeflection]":
        """Iterable[mastapy.system_model.analyses_and_results.system_deflections.compound.SpiralBevelGearMeshCompoundSystemDeflection]

        Args:
            design_entity (mastapy.system_model.connections_and_sockets.gears.SpiralBevelGearMesh)
        """
        return conversion.pn_to_mp_objects_in_iterable(
            pythonnet_method_call_overload(
                self.wrapped,
                "ResultsFor",
                [_SPIRAL_BEVEL_GEAR_MESH],
                design_entity.wrapped if design_entity else None,
            )
        )

    @exception_bridge
    @enforce_parameter_types
    def results_for_straight_bevel_gear_mesh(
        self: "Self", design_entity: "_2586.StraightBevelGearMesh"
    ) -> "Iterable[_3259.StraightBevelGearMeshCompoundSystemDeflection]":
        """Iterable[mastapy.system_model.analyses_and_results.system_deflections.compound.StraightBevelGearMeshCompoundSystemDeflection]

        Args:
            design_entity (mastapy.system_model.connections_and_sockets.gears.StraightBevelGearMesh)
        """
        return conversion.pn_to_mp_objects_in_iterable(
            pythonnet_method_call_overload(
                self.wrapped,
                "ResultsFor",
                [_STRAIGHT_BEVEL_GEAR_MESH],
                design_entity.wrapped if design_entity else None,
            )
        )

    @exception_bridge
    @enforce_parameter_types
    def results_for_worm_gear_mesh(
        self: "Self", design_entity: "_2588.WormGearMesh"
    ) -> "Iterable[_3274.WormGearMeshCompoundSystemDeflection]":
        """Iterable[mastapy.system_model.analyses_and_results.system_deflections.compound.WormGearMeshCompoundSystemDeflection]

        Args:
            design_entity (mastapy.system_model.connections_and_sockets.gears.WormGearMesh)
        """
        return conversion.pn_to_mp_objects_in_iterable(
            pythonnet_method_call_overload(
                self.wrapped,
                "ResultsFor",
                [_WORM_GEAR_MESH],
                design_entity.wrapped if design_entity else None,
            )
        )

    @exception_bridge
    @enforce_parameter_types
    def results_for_zerol_bevel_gear_mesh(
        self: "Self", design_entity: "_2590.ZerolBevelGearMesh"
    ) -> "Iterable[_3277.ZerolBevelGearMeshCompoundSystemDeflection]":
        """Iterable[mastapy.system_model.analyses_and_results.system_deflections.compound.ZerolBevelGearMeshCompoundSystemDeflection]

        Args:
            design_entity (mastapy.system_model.connections_and_sockets.gears.ZerolBevelGearMesh)
        """
        return conversion.pn_to_mp_objects_in_iterable(
            pythonnet_method_call_overload(
                self.wrapped,
                "ResultsFor",
                [_ZEROL_BEVEL_GEAR_MESH],
                design_entity.wrapped if design_entity else None,
            )
        )

    @exception_bridge
    @enforce_parameter_types
    def results_for_gear_mesh(
        self: "Self", design_entity: "_2572.GearMesh"
    ) -> "Iterable[_3206.GearMeshCompoundSystemDeflection]":
        """Iterable[mastapy.system_model.analyses_and_results.system_deflections.compound.GearMeshCompoundSystemDeflection]

        Args:
            design_entity (mastapy.system_model.connections_and_sockets.gears.GearMesh)
        """
        return conversion.pn_to_mp_objects_in_iterable(
            pythonnet_method_call_overload(
                self.wrapped,
                "ResultsFor",
                [_GEAR_MESH],
                design_entity.wrapped if design_entity else None,
            )
        )

    @exception_bridge
    @enforce_parameter_types
    def results_for_cycloidal_disc_central_bearing_connection(
        self: "Self", design_entity: "_2594.CycloidalDiscCentralBearingConnection"
    ) -> (
        "Iterable[_3190.CycloidalDiscCentralBearingConnectionCompoundSystemDeflection]"
    ):
        """Iterable[mastapy.system_model.analyses_and_results.system_deflections.compound.CycloidalDiscCentralBearingConnectionCompoundSystemDeflection]

        Args:
            design_entity (mastapy.system_model.connections_and_sockets.cycloidal.CycloidalDiscCentralBearingConnection)
        """
        return conversion.pn_to_mp_objects_in_iterable(
            pythonnet_method_call_overload(
                self.wrapped,
                "ResultsFor",
                [_CYCLOIDAL_DISC_CENTRAL_BEARING_CONNECTION],
                design_entity.wrapped if design_entity else None,
            )
        )

    @exception_bridge
    @enforce_parameter_types
    def results_for_cycloidal_disc_planetary_bearing_connection(
        self: "Self", design_entity: "_2597.CycloidalDiscPlanetaryBearingConnection"
    ) -> "Iterable[_3192.CycloidalDiscPlanetaryBearingConnectionCompoundSystemDeflection]":
        """Iterable[mastapy.system_model.analyses_and_results.system_deflections.compound.CycloidalDiscPlanetaryBearingConnectionCompoundSystemDeflection]

        Args:
            design_entity (mastapy.system_model.connections_and_sockets.cycloidal.CycloidalDiscPlanetaryBearingConnection)
        """
        return conversion.pn_to_mp_objects_in_iterable(
            pythonnet_method_call_overload(
                self.wrapped,
                "ResultsFor",
                [_CYCLOIDAL_DISC_PLANETARY_BEARING_CONNECTION],
                design_entity.wrapped if design_entity else None,
            )
        )

    @exception_bridge
    @enforce_parameter_types
    def results_for_ring_pins_to_disc_connection(
        self: "Self", design_entity: "_2600.RingPinsToDiscConnection"
    ) -> "Iterable[_3239.RingPinsToDiscConnectionCompoundSystemDeflection]":
        """Iterable[mastapy.system_model.analyses_and_results.system_deflections.compound.RingPinsToDiscConnectionCompoundSystemDeflection]

        Args:
            design_entity (mastapy.system_model.connections_and_sockets.cycloidal.RingPinsToDiscConnection)
        """
        return conversion.pn_to_mp_objects_in_iterable(
            pythonnet_method_call_overload(
                self.wrapped,
                "ResultsFor",
                [_RING_PINS_TO_DISC_CONNECTION],
                design_entity.wrapped if design_entity else None,
            )
        )

    @exception_bridge
    @enforce_parameter_types
    def results_for_part_to_part_shear_coupling_connection(
        self: "Self", design_entity: "_2607.PartToPartShearCouplingConnection"
    ) -> "Iterable[_3230.PartToPartShearCouplingConnectionCompoundSystemDeflection]":
        """Iterable[mastapy.system_model.analyses_and_results.system_deflections.compound.PartToPartShearCouplingConnectionCompoundSystemDeflection]

        Args:
            design_entity (mastapy.system_model.connections_and_sockets.couplings.PartToPartShearCouplingConnection)
        """
        return conversion.pn_to_mp_objects_in_iterable(
            pythonnet_method_call_overload(
                self.wrapped,
                "ResultsFor",
                [_PART_TO_PART_SHEAR_COUPLING_CONNECTION],
                design_entity.wrapped if design_entity else None,
            )
        )

    @exception_bridge
    @enforce_parameter_types
    def results_for_clutch_connection(
        self: "Self", design_entity: "_2601.ClutchConnection"
    ) -> "Iterable[_3168.ClutchConnectionCompoundSystemDeflection]":
        """Iterable[mastapy.system_model.analyses_and_results.system_deflections.compound.ClutchConnectionCompoundSystemDeflection]

        Args:
            design_entity (mastapy.system_model.connections_and_sockets.couplings.ClutchConnection)
        """
        return conversion.pn_to_mp_objects_in_iterable(
            pythonnet_method_call_overload(
                self.wrapped,
                "ResultsFor",
                [_CLUTCH_CONNECTION],
                design_entity.wrapped if design_entity else None,
            )
        )

    @property
    def cast_to(self: "Self") -> "_Cast_CompoundSystemDeflection":
        """Cast to another type.

        Returns:
            _Cast_CompoundSystemDeflection
        """
        return _Cast_CompoundSystemDeflection(self)
