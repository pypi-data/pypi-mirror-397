"""CompoundModalAnalysis"""

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
_COMPOUND_MODAL_ANALYSIS = python_net_import(
    "SMT.MastaAPI.SystemModel.AnalysesAndResults", "CompoundModalAnalysis"
)

if TYPE_CHECKING:
    from typing import Any, Iterable, Type, TypeVar

    from mastapy._private import _7949
    from mastapy._private.system_model.analyses_and_results.modal_analyses.compound import (
        _5053,
        _5054,
        _5055,
        _5056,
        _5057,
        _5058,
        _5059,
        _5060,
        _5061,
        _5062,
        _5063,
        _5064,
        _5065,
        _5066,
        _5067,
        _5068,
        _5069,
        _5070,
        _5071,
        _5072,
        _5073,
        _5074,
        _5075,
        _5076,
        _5077,
        _5078,
        _5079,
        _5080,
        _5081,
        _5082,
        _5083,
        _5084,
        _5085,
        _5086,
        _5087,
        _5088,
        _5089,
        _5090,
        _5091,
        _5092,
        _5093,
        _5094,
        _5095,
        _5096,
        _5097,
        _5098,
        _5099,
        _5100,
        _5101,
        _5102,
        _5103,
        _5104,
        _5105,
        _5106,
        _5107,
        _5108,
        _5109,
        _5110,
        _5111,
        _5112,
        _5113,
        _5114,
        _5115,
        _5116,
        _5117,
        _5118,
        _5119,
        _5120,
        _5121,
        _5122,
        _5123,
        _5124,
        _5125,
        _5126,
        _5127,
        _5128,
        _5129,
        _5130,
        _5131,
        _5132,
        _5133,
        _5134,
        _5135,
        _5136,
        _5137,
        _5138,
        _5139,
        _5140,
        _5141,
        _5142,
        _5143,
        _5144,
        _5145,
        _5146,
        _5147,
        _5148,
        _5149,
        _5150,
        _5151,
        _5152,
        _5153,
        _5154,
        _5155,
        _5156,
        _5157,
        _5158,
        _5159,
        _5160,
        _5161,
        _5162,
        _5163,
        _5164,
        _5165,
        _5166,
        _5167,
        _5168,
        _5169,
        _5170,
        _5171,
        _5172,
        _5173,
        _5174,
        _5175,
        _5176,
        _5177,
        _5178,
        _5179,
        _5180,
        _5181,
        _5182,
        _5183,
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

    Self = TypeVar("Self", bound="CompoundModalAnalysis")
    CastSelf = TypeVar(
        "CastSelf", bound="CompoundModalAnalysis._Cast_CompoundModalAnalysis"
    )


__docformat__ = "restructuredtext en"
__all__ = ("CompoundModalAnalysis",)


@extended_dataclass(frozen=True, slots=True, weakref_slot=True)
class _Cast_CompoundModalAnalysis:
    """Special nested class for casting CompoundModalAnalysis to subclasses."""

    __parent__: "CompoundModalAnalysis"

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
    def compound_modal_analysis(self: "CastSelf") -> "CompoundModalAnalysis":
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
class CompoundModalAnalysis(_2939.CompoundAnalysis):
    """CompoundModalAnalysis

    This is a mastapy class.
    """

    TYPE: ClassVar["Type"] = _COMPOUND_MODAL_ANALYSIS

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
    ) -> "Iterable[_5080.ConceptCouplingConnectionCompoundModalAnalysis]":
        """Iterable[mastapy.system_model.analyses_and_results.modal_analyses.compound.ConceptCouplingConnectionCompoundModalAnalysis]

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
    ) -> "Iterable[_5091.CouplingConnectionCompoundModalAnalysis]":
        """Iterable[mastapy.system_model.analyses_and_results.modal_analyses.compound.CouplingConnectionCompoundModalAnalysis]

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
    ) -> "Iterable[_5158.SpringDamperConnectionCompoundModalAnalysis]":
        """Iterable[mastapy.system_model.analyses_and_results.modal_analyses.compound.SpringDamperConnectionCompoundModalAnalysis]

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
    ) -> "Iterable[_5173.TorqueConverterConnectionCompoundModalAnalysis]":
        """Iterable[mastapy.system_model.analyses_and_results.modal_analyses.compound.TorqueConverterConnectionCompoundModalAnalysis]

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
    ) -> "Iterable[_5054.AbstractShaftCompoundModalAnalysis]":
        """Iterable[mastapy.system_model.analyses_and_results.modal_analyses.compound.AbstractShaftCompoundModalAnalysis]

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
    ) -> "Iterable[_5131.MicrophoneCompoundModalAnalysis]":
        """Iterable[mastapy.system_model.analyses_and_results.modal_analyses.compound.MicrophoneCompoundModalAnalysis]

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
    ) -> "Iterable[_5130.MicrophoneArrayCompoundModalAnalysis]":
        """Iterable[mastapy.system_model.analyses_and_results.modal_analyses.compound.MicrophoneArrayCompoundModalAnalysis]

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
    ) -> "Iterable[_5053.AbstractAssemblyCompoundModalAnalysis]":
        """Iterable[mastapy.system_model.analyses_and_results.modal_analyses.compound.AbstractAssemblyCompoundModalAnalysis]

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
    ) -> "Iterable[_5055.AbstractShaftOrHousingCompoundModalAnalysis]":
        """Iterable[mastapy.system_model.analyses_and_results.modal_analyses.compound.AbstractShaftOrHousingCompoundModalAnalysis]

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
    ) -> "Iterable[_5061.BearingCompoundModalAnalysis]":
        """Iterable[mastapy.system_model.analyses_and_results.modal_analyses.compound.BearingCompoundModalAnalysis]

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
    ) -> "Iterable[_5072.BoltCompoundModalAnalysis]":
        """Iterable[mastapy.system_model.analyses_and_results.modal_analyses.compound.BoltCompoundModalAnalysis]

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
    ) -> "Iterable[_5073.BoltedJointCompoundModalAnalysis]":
        """Iterable[mastapy.system_model.analyses_and_results.modal_analyses.compound.BoltedJointCompoundModalAnalysis]

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
    ) -> "Iterable[_5078.ComponentCompoundModalAnalysis]":
        """Iterable[mastapy.system_model.analyses_and_results.modal_analyses.compound.ComponentCompoundModalAnalysis]

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
    ) -> "Iterable[_5089.ConnectorCompoundModalAnalysis]":
        """Iterable[mastapy.system_model.analyses_and_results.modal_analyses.compound.ConnectorCompoundModalAnalysis]

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
    ) -> "Iterable[_5104.DatumCompoundModalAnalysis]":
        """Iterable[mastapy.system_model.analyses_and_results.modal_analyses.compound.DatumCompoundModalAnalysis]

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
    ) -> "Iterable[_5105.ExternalCADModelCompoundModalAnalysis]":
        """Iterable[mastapy.system_model.analyses_and_results.modal_analyses.compound.ExternalCADModelCompoundModalAnalysis]

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
    ) -> "Iterable[_5109.FEPartCompoundModalAnalysis]":
        """Iterable[mastapy.system_model.analyses_and_results.modal_analyses.compound.FEPartCompoundModalAnalysis]

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
    ) -> "Iterable[_5110.FlexiblePinAssemblyCompoundModalAnalysis]":
        """Iterable[mastapy.system_model.analyses_and_results.modal_analyses.compound.FlexiblePinAssemblyCompoundModalAnalysis]

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
    ) -> "Iterable[_5060.AssemblyCompoundModalAnalysis]":
        """Iterable[mastapy.system_model.analyses_and_results.modal_analyses.compound.AssemblyCompoundModalAnalysis]

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
    ) -> "Iterable[_5114.GuideDxfModelCompoundModalAnalysis]":
        """Iterable[mastapy.system_model.analyses_and_results.modal_analyses.compound.GuideDxfModelCompoundModalAnalysis]

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
    ) -> "Iterable[_5128.MassDiscCompoundModalAnalysis]":
        """Iterable[mastapy.system_model.analyses_and_results.modal_analyses.compound.MassDiscCompoundModalAnalysis]

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
    ) -> "Iterable[_5129.MeasurementComponentCompoundModalAnalysis]":
        """Iterable[mastapy.system_model.analyses_and_results.modal_analyses.compound.MeasurementComponentCompoundModalAnalysis]

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
    ) -> "Iterable[_5132.MountableComponentCompoundModalAnalysis]":
        """Iterable[mastapy.system_model.analyses_and_results.modal_analyses.compound.MountableComponentCompoundModalAnalysis]

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
    ) -> "Iterable[_5133.OilSealCompoundModalAnalysis]":
        """Iterable[mastapy.system_model.analyses_and_results.modal_analyses.compound.OilSealCompoundModalAnalysis]

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
    ) -> "Iterable[_5134.PartCompoundModalAnalysis]":
        """Iterable[mastapy.system_model.analyses_and_results.modal_analyses.compound.PartCompoundModalAnalysis]

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
    ) -> "Iterable[_5140.PlanetCarrierCompoundModalAnalysis]":
        """Iterable[mastapy.system_model.analyses_and_results.modal_analyses.compound.PlanetCarrierCompoundModalAnalysis]

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
    ) -> "Iterable[_5141.PointLoadCompoundModalAnalysis]":
        """Iterable[mastapy.system_model.analyses_and_results.modal_analyses.compound.PointLoadCompoundModalAnalysis]

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
    ) -> "Iterable[_5142.PowerLoadCompoundModalAnalysis]":
        """Iterable[mastapy.system_model.analyses_and_results.modal_analyses.compound.PowerLoadCompoundModalAnalysis]

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
    ) -> "Iterable[_5149.RootAssemblyCompoundModalAnalysis]":
        """Iterable[mastapy.system_model.analyses_and_results.modal_analyses.compound.RootAssemblyCompoundModalAnalysis]

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
    ) -> "Iterable[_5153.SpecialisedAssemblyCompoundModalAnalysis]":
        """Iterable[mastapy.system_model.analyses_and_results.modal_analyses.compound.SpecialisedAssemblyCompoundModalAnalysis]

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
    ) -> "Iterable[_5176.UnbalancedMassCompoundModalAnalysis]":
        """Iterable[mastapy.system_model.analyses_and_results.modal_analyses.compound.UnbalancedMassCompoundModalAnalysis]

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
    ) -> "Iterable[_5177.VirtualComponentCompoundModalAnalysis]":
        """Iterable[mastapy.system_model.analyses_and_results.modal_analyses.compound.VirtualComponentCompoundModalAnalysis]

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
    ) -> "Iterable[_5150.ShaftCompoundModalAnalysis]":
        """Iterable[mastapy.system_model.analyses_and_results.modal_analyses.compound.ShaftCompoundModalAnalysis]

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
    ) -> "Iterable[_5082.ConceptGearCompoundModalAnalysis]":
        """Iterable[mastapy.system_model.analyses_and_results.modal_analyses.compound.ConceptGearCompoundModalAnalysis]

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
    ) -> "Iterable[_5084.ConceptGearSetCompoundModalAnalysis]":
        """Iterable[mastapy.system_model.analyses_and_results.modal_analyses.compound.ConceptGearSetCompoundModalAnalysis]

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
    ) -> "Iterable[_5106.FaceGearCompoundModalAnalysis]":
        """Iterable[mastapy.system_model.analyses_and_results.modal_analyses.compound.FaceGearCompoundModalAnalysis]

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
    ) -> "Iterable[_5108.FaceGearSetCompoundModalAnalysis]":
        """Iterable[mastapy.system_model.analyses_and_results.modal_analyses.compound.FaceGearSetCompoundModalAnalysis]

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
    ) -> "Iterable[_5057.AGMAGleasonConicalGearCompoundModalAnalysis]":
        """Iterable[mastapy.system_model.analyses_and_results.modal_analyses.compound.AGMAGleasonConicalGearCompoundModalAnalysis]

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
    ) -> "Iterable[_5059.AGMAGleasonConicalGearSetCompoundModalAnalysis]":
        """Iterable[mastapy.system_model.analyses_and_results.modal_analyses.compound.AGMAGleasonConicalGearSetCompoundModalAnalysis]

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
    ) -> "Iterable[_5064.BevelDifferentialGearCompoundModalAnalysis]":
        """Iterable[mastapy.system_model.analyses_and_results.modal_analyses.compound.BevelDifferentialGearCompoundModalAnalysis]

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
    ) -> "Iterable[_5066.BevelDifferentialGearSetCompoundModalAnalysis]":
        """Iterable[mastapy.system_model.analyses_and_results.modal_analyses.compound.BevelDifferentialGearSetCompoundModalAnalysis]

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
    ) -> "Iterable[_5067.BevelDifferentialPlanetGearCompoundModalAnalysis]":
        """Iterable[mastapy.system_model.analyses_and_results.modal_analyses.compound.BevelDifferentialPlanetGearCompoundModalAnalysis]

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
    ) -> "Iterable[_5068.BevelDifferentialSunGearCompoundModalAnalysis]":
        """Iterable[mastapy.system_model.analyses_and_results.modal_analyses.compound.BevelDifferentialSunGearCompoundModalAnalysis]

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
    ) -> "Iterable[_5069.BevelGearCompoundModalAnalysis]":
        """Iterable[mastapy.system_model.analyses_and_results.modal_analyses.compound.BevelGearCompoundModalAnalysis]

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
    ) -> "Iterable[_5071.BevelGearSetCompoundModalAnalysis]":
        """Iterable[mastapy.system_model.analyses_and_results.modal_analyses.compound.BevelGearSetCompoundModalAnalysis]

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
    ) -> "Iterable[_5085.ConicalGearCompoundModalAnalysis]":
        """Iterable[mastapy.system_model.analyses_and_results.modal_analyses.compound.ConicalGearCompoundModalAnalysis]

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
    ) -> "Iterable[_5087.ConicalGearSetCompoundModalAnalysis]":
        """Iterable[mastapy.system_model.analyses_and_results.modal_analyses.compound.ConicalGearSetCompoundModalAnalysis]

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
    ) -> "Iterable[_5100.CylindricalGearCompoundModalAnalysis]":
        """Iterable[mastapy.system_model.analyses_and_results.modal_analyses.compound.CylindricalGearCompoundModalAnalysis]

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
    ) -> "Iterable[_5102.CylindricalGearSetCompoundModalAnalysis]":
        """Iterable[mastapy.system_model.analyses_and_results.modal_analyses.compound.CylindricalGearSetCompoundModalAnalysis]

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
    ) -> "Iterable[_5103.CylindricalPlanetGearCompoundModalAnalysis]":
        """Iterable[mastapy.system_model.analyses_and_results.modal_analyses.compound.CylindricalPlanetGearCompoundModalAnalysis]

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
    ) -> "Iterable[_5111.GearCompoundModalAnalysis]":
        """Iterable[mastapy.system_model.analyses_and_results.modal_analyses.compound.GearCompoundModalAnalysis]

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
    ) -> "Iterable[_5113.GearSetCompoundModalAnalysis]":
        """Iterable[mastapy.system_model.analyses_and_results.modal_analyses.compound.GearSetCompoundModalAnalysis]

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
    ) -> "Iterable[_5115.HypoidGearCompoundModalAnalysis]":
        """Iterable[mastapy.system_model.analyses_and_results.modal_analyses.compound.HypoidGearCompoundModalAnalysis]

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
    ) -> "Iterable[_5117.HypoidGearSetCompoundModalAnalysis]":
        """Iterable[mastapy.system_model.analyses_and_results.modal_analyses.compound.HypoidGearSetCompoundModalAnalysis]

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
    ) -> "Iterable[_5119.KlingelnbergCycloPalloidConicalGearCompoundModalAnalysis]":
        """Iterable[mastapy.system_model.analyses_and_results.modal_analyses.compound.KlingelnbergCycloPalloidConicalGearCompoundModalAnalysis]

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
    ) -> "Iterable[_5121.KlingelnbergCycloPalloidConicalGearSetCompoundModalAnalysis]":
        """Iterable[mastapy.system_model.analyses_and_results.modal_analyses.compound.KlingelnbergCycloPalloidConicalGearSetCompoundModalAnalysis]

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
    ) -> "Iterable[_5122.KlingelnbergCycloPalloidHypoidGearCompoundModalAnalysis]":
        """Iterable[mastapy.system_model.analyses_and_results.modal_analyses.compound.KlingelnbergCycloPalloidHypoidGearCompoundModalAnalysis]

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
    ) -> "Iterable[_5124.KlingelnbergCycloPalloidHypoidGearSetCompoundModalAnalysis]":
        """Iterable[mastapy.system_model.analyses_and_results.modal_analyses.compound.KlingelnbergCycloPalloidHypoidGearSetCompoundModalAnalysis]

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
    ) -> "Iterable[_5125.KlingelnbergCycloPalloidSpiralBevelGearCompoundModalAnalysis]":
        """Iterable[mastapy.system_model.analyses_and_results.modal_analyses.compound.KlingelnbergCycloPalloidSpiralBevelGearCompoundModalAnalysis]

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
    ) -> "Iterable[_5127.KlingelnbergCycloPalloidSpiralBevelGearSetCompoundModalAnalysis]":
        """Iterable[mastapy.system_model.analyses_and_results.modal_analyses.compound.KlingelnbergCycloPalloidSpiralBevelGearSetCompoundModalAnalysis]

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
    ) -> "Iterable[_5139.PlanetaryGearSetCompoundModalAnalysis]":
        """Iterable[mastapy.system_model.analyses_and_results.modal_analyses.compound.PlanetaryGearSetCompoundModalAnalysis]

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
    ) -> "Iterable[_5154.SpiralBevelGearCompoundModalAnalysis]":
        """Iterable[mastapy.system_model.analyses_and_results.modal_analyses.compound.SpiralBevelGearCompoundModalAnalysis]

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
    ) -> "Iterable[_5156.SpiralBevelGearSetCompoundModalAnalysis]":
        """Iterable[mastapy.system_model.analyses_and_results.modal_analyses.compound.SpiralBevelGearSetCompoundModalAnalysis]

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
    ) -> "Iterable[_5160.StraightBevelDiffGearCompoundModalAnalysis]":
        """Iterable[mastapy.system_model.analyses_and_results.modal_analyses.compound.StraightBevelDiffGearCompoundModalAnalysis]

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
    ) -> "Iterable[_5162.StraightBevelDiffGearSetCompoundModalAnalysis]":
        """Iterable[mastapy.system_model.analyses_and_results.modal_analyses.compound.StraightBevelDiffGearSetCompoundModalAnalysis]

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
    ) -> "Iterable[_5163.StraightBevelGearCompoundModalAnalysis]":
        """Iterable[mastapy.system_model.analyses_and_results.modal_analyses.compound.StraightBevelGearCompoundModalAnalysis]

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
    ) -> "Iterable[_5165.StraightBevelGearSetCompoundModalAnalysis]":
        """Iterable[mastapy.system_model.analyses_and_results.modal_analyses.compound.StraightBevelGearSetCompoundModalAnalysis]

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
    ) -> "Iterable[_5166.StraightBevelPlanetGearCompoundModalAnalysis]":
        """Iterable[mastapy.system_model.analyses_and_results.modal_analyses.compound.StraightBevelPlanetGearCompoundModalAnalysis]

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
    ) -> "Iterable[_5167.StraightBevelSunGearCompoundModalAnalysis]":
        """Iterable[mastapy.system_model.analyses_and_results.modal_analyses.compound.StraightBevelSunGearCompoundModalAnalysis]

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
    ) -> "Iterable[_5178.WormGearCompoundModalAnalysis]":
        """Iterable[mastapy.system_model.analyses_and_results.modal_analyses.compound.WormGearCompoundModalAnalysis]

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
    ) -> "Iterable[_5180.WormGearSetCompoundModalAnalysis]":
        """Iterable[mastapy.system_model.analyses_and_results.modal_analyses.compound.WormGearSetCompoundModalAnalysis]

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
    ) -> "Iterable[_5181.ZerolBevelGearCompoundModalAnalysis]":
        """Iterable[mastapy.system_model.analyses_and_results.modal_analyses.compound.ZerolBevelGearCompoundModalAnalysis]

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
    ) -> "Iterable[_5183.ZerolBevelGearSetCompoundModalAnalysis]":
        """Iterable[mastapy.system_model.analyses_and_results.modal_analyses.compound.ZerolBevelGearSetCompoundModalAnalysis]

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
    ) -> "Iterable[_5096.CycloidalAssemblyCompoundModalAnalysis]":
        """Iterable[mastapy.system_model.analyses_and_results.modal_analyses.compound.CycloidalAssemblyCompoundModalAnalysis]

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
    ) -> "Iterable[_5098.CycloidalDiscCompoundModalAnalysis]":
        """Iterable[mastapy.system_model.analyses_and_results.modal_analyses.compound.CycloidalDiscCompoundModalAnalysis]

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
    ) -> "Iterable[_5144.RingPinsCompoundModalAnalysis]":
        """Iterable[mastapy.system_model.analyses_and_results.modal_analyses.compound.RingPinsCompoundModalAnalysis]

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
    ) -> "Iterable[_5135.PartToPartShearCouplingCompoundModalAnalysis]":
        """Iterable[mastapy.system_model.analyses_and_results.modal_analyses.compound.PartToPartShearCouplingCompoundModalAnalysis]

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
    ) -> "Iterable[_5137.PartToPartShearCouplingHalfCompoundModalAnalysis]":
        """Iterable[mastapy.system_model.analyses_and_results.modal_analyses.compound.PartToPartShearCouplingHalfCompoundModalAnalysis]

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
    ) -> "Iterable[_5063.BeltDriveCompoundModalAnalysis]":
        """Iterable[mastapy.system_model.analyses_and_results.modal_analyses.compound.BeltDriveCompoundModalAnalysis]

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
    ) -> "Iterable[_5074.ClutchCompoundModalAnalysis]":
        """Iterable[mastapy.system_model.analyses_and_results.modal_analyses.compound.ClutchCompoundModalAnalysis]

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
    ) -> "Iterable[_5076.ClutchHalfCompoundModalAnalysis]":
        """Iterable[mastapy.system_model.analyses_and_results.modal_analyses.compound.ClutchHalfCompoundModalAnalysis]

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
    ) -> "Iterable[_5079.ConceptCouplingCompoundModalAnalysis]":
        """Iterable[mastapy.system_model.analyses_and_results.modal_analyses.compound.ConceptCouplingCompoundModalAnalysis]

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
    ) -> "Iterable[_5081.ConceptCouplingHalfCompoundModalAnalysis]":
        """Iterable[mastapy.system_model.analyses_and_results.modal_analyses.compound.ConceptCouplingHalfCompoundModalAnalysis]

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
    ) -> "Iterable[_5090.CouplingCompoundModalAnalysis]":
        """Iterable[mastapy.system_model.analyses_and_results.modal_analyses.compound.CouplingCompoundModalAnalysis]

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
    ) -> "Iterable[_5092.CouplingHalfCompoundModalAnalysis]":
        """Iterable[mastapy.system_model.analyses_and_results.modal_analyses.compound.CouplingHalfCompoundModalAnalysis]

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
    ) -> "Iterable[_5094.CVTCompoundModalAnalysis]":
        """Iterable[mastapy.system_model.analyses_and_results.modal_analyses.compound.CVTCompoundModalAnalysis]

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
    ) -> "Iterable[_5095.CVTPulleyCompoundModalAnalysis]":
        """Iterable[mastapy.system_model.analyses_and_results.modal_analyses.compound.CVTPulleyCompoundModalAnalysis]

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
    ) -> "Iterable[_5143.PulleyCompoundModalAnalysis]":
        """Iterable[mastapy.system_model.analyses_and_results.modal_analyses.compound.PulleyCompoundModalAnalysis]

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
    ) -> "Iterable[_5151.ShaftHubConnectionCompoundModalAnalysis]":
        """Iterable[mastapy.system_model.analyses_and_results.modal_analyses.compound.ShaftHubConnectionCompoundModalAnalysis]

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
    ) -> "Iterable[_5147.RollingRingCompoundModalAnalysis]":
        """Iterable[mastapy.system_model.analyses_and_results.modal_analyses.compound.RollingRingCompoundModalAnalysis]

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
    ) -> "Iterable[_5146.RollingRingAssemblyCompoundModalAnalysis]":
        """Iterable[mastapy.system_model.analyses_and_results.modal_analyses.compound.RollingRingAssemblyCompoundModalAnalysis]

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
    ) -> "Iterable[_5157.SpringDamperCompoundModalAnalysis]":
        """Iterable[mastapy.system_model.analyses_and_results.modal_analyses.compound.SpringDamperCompoundModalAnalysis]

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
    ) -> "Iterable[_5159.SpringDamperHalfCompoundModalAnalysis]":
        """Iterable[mastapy.system_model.analyses_and_results.modal_analyses.compound.SpringDamperHalfCompoundModalAnalysis]

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
    ) -> "Iterable[_5168.SynchroniserCompoundModalAnalysis]":
        """Iterable[mastapy.system_model.analyses_and_results.modal_analyses.compound.SynchroniserCompoundModalAnalysis]

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
    ) -> "Iterable[_5169.SynchroniserHalfCompoundModalAnalysis]":
        """Iterable[mastapy.system_model.analyses_and_results.modal_analyses.compound.SynchroniserHalfCompoundModalAnalysis]

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
    ) -> "Iterable[_5170.SynchroniserPartCompoundModalAnalysis]":
        """Iterable[mastapy.system_model.analyses_and_results.modal_analyses.compound.SynchroniserPartCompoundModalAnalysis]

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
    ) -> "Iterable[_5171.SynchroniserSleeveCompoundModalAnalysis]":
        """Iterable[mastapy.system_model.analyses_and_results.modal_analyses.compound.SynchroniserSleeveCompoundModalAnalysis]

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
    ) -> "Iterable[_5172.TorqueConverterCompoundModalAnalysis]":
        """Iterable[mastapy.system_model.analyses_and_results.modal_analyses.compound.TorqueConverterCompoundModalAnalysis]

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
    ) -> "Iterable[_5174.TorqueConverterPumpCompoundModalAnalysis]":
        """Iterable[mastapy.system_model.analyses_and_results.modal_analyses.compound.TorqueConverterPumpCompoundModalAnalysis]

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
    ) -> "Iterable[_5175.TorqueConverterTurbineCompoundModalAnalysis]":
        """Iterable[mastapy.system_model.analyses_and_results.modal_analyses.compound.TorqueConverterTurbineCompoundModalAnalysis]

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
    ) -> "Iterable[_5152.ShaftToMountableComponentConnectionCompoundModalAnalysis]":
        """Iterable[mastapy.system_model.analyses_and_results.modal_analyses.compound.ShaftToMountableComponentConnectionCompoundModalAnalysis]

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
    ) -> "Iterable[_5093.CVTBeltConnectionCompoundModalAnalysis]":
        """Iterable[mastapy.system_model.analyses_and_results.modal_analyses.compound.CVTBeltConnectionCompoundModalAnalysis]

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
    ) -> "Iterable[_5062.BeltConnectionCompoundModalAnalysis]":
        """Iterable[mastapy.system_model.analyses_and_results.modal_analyses.compound.BeltConnectionCompoundModalAnalysis]

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
    ) -> "Iterable[_5077.CoaxialConnectionCompoundModalAnalysis]":
        """Iterable[mastapy.system_model.analyses_and_results.modal_analyses.compound.CoaxialConnectionCompoundModalAnalysis]

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
    ) -> "Iterable[_5088.ConnectionCompoundModalAnalysis]":
        """Iterable[mastapy.system_model.analyses_and_results.modal_analyses.compound.ConnectionCompoundModalAnalysis]

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
    ) -> "Iterable[_5118.InterMountableComponentConnectionCompoundModalAnalysis]":
        """Iterable[mastapy.system_model.analyses_and_results.modal_analyses.compound.InterMountableComponentConnectionCompoundModalAnalysis]

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
    ) -> "Iterable[_5138.PlanetaryConnectionCompoundModalAnalysis]":
        """Iterable[mastapy.system_model.analyses_and_results.modal_analyses.compound.PlanetaryConnectionCompoundModalAnalysis]

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
    ) -> "Iterable[_5148.RollingRingConnectionCompoundModalAnalysis]":
        """Iterable[mastapy.system_model.analyses_and_results.modal_analyses.compound.RollingRingConnectionCompoundModalAnalysis]

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
    ) -> "Iterable[_5056.AbstractShaftToMountableComponentConnectionCompoundModalAnalysis]":
        """Iterable[mastapy.system_model.analyses_and_results.modal_analyses.compound.AbstractShaftToMountableComponentConnectionCompoundModalAnalysis]

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
    ) -> "Iterable[_5065.BevelDifferentialGearMeshCompoundModalAnalysis]":
        """Iterable[mastapy.system_model.analyses_and_results.modal_analyses.compound.BevelDifferentialGearMeshCompoundModalAnalysis]

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
    ) -> "Iterable[_5083.ConceptGearMeshCompoundModalAnalysis]":
        """Iterable[mastapy.system_model.analyses_and_results.modal_analyses.compound.ConceptGearMeshCompoundModalAnalysis]

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
    ) -> "Iterable[_5107.FaceGearMeshCompoundModalAnalysis]":
        """Iterable[mastapy.system_model.analyses_and_results.modal_analyses.compound.FaceGearMeshCompoundModalAnalysis]

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
    ) -> "Iterable[_5161.StraightBevelDiffGearMeshCompoundModalAnalysis]":
        """Iterable[mastapy.system_model.analyses_and_results.modal_analyses.compound.StraightBevelDiffGearMeshCompoundModalAnalysis]

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
    ) -> "Iterable[_5070.BevelGearMeshCompoundModalAnalysis]":
        """Iterable[mastapy.system_model.analyses_and_results.modal_analyses.compound.BevelGearMeshCompoundModalAnalysis]

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
    ) -> "Iterable[_5086.ConicalGearMeshCompoundModalAnalysis]":
        """Iterable[mastapy.system_model.analyses_and_results.modal_analyses.compound.ConicalGearMeshCompoundModalAnalysis]

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
    ) -> "Iterable[_5058.AGMAGleasonConicalGearMeshCompoundModalAnalysis]":
        """Iterable[mastapy.system_model.analyses_and_results.modal_analyses.compound.AGMAGleasonConicalGearMeshCompoundModalAnalysis]

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
    ) -> "Iterable[_5101.CylindricalGearMeshCompoundModalAnalysis]":
        """Iterable[mastapy.system_model.analyses_and_results.modal_analyses.compound.CylindricalGearMeshCompoundModalAnalysis]

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
    ) -> "Iterable[_5116.HypoidGearMeshCompoundModalAnalysis]":
        """Iterable[mastapy.system_model.analyses_and_results.modal_analyses.compound.HypoidGearMeshCompoundModalAnalysis]

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
    ) -> "Iterable[_5120.KlingelnbergCycloPalloidConicalGearMeshCompoundModalAnalysis]":
        """Iterable[mastapy.system_model.analyses_and_results.modal_analyses.compound.KlingelnbergCycloPalloidConicalGearMeshCompoundModalAnalysis]

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
    ) -> "Iterable[_5123.KlingelnbergCycloPalloidHypoidGearMeshCompoundModalAnalysis]":
        """Iterable[mastapy.system_model.analyses_and_results.modal_analyses.compound.KlingelnbergCycloPalloidHypoidGearMeshCompoundModalAnalysis]

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
    ) -> "Iterable[_5126.KlingelnbergCycloPalloidSpiralBevelGearMeshCompoundModalAnalysis]":
        """Iterable[mastapy.system_model.analyses_and_results.modal_analyses.compound.KlingelnbergCycloPalloidSpiralBevelGearMeshCompoundModalAnalysis]

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
    ) -> "Iterable[_5155.SpiralBevelGearMeshCompoundModalAnalysis]":
        """Iterable[mastapy.system_model.analyses_and_results.modal_analyses.compound.SpiralBevelGearMeshCompoundModalAnalysis]

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
    ) -> "Iterable[_5164.StraightBevelGearMeshCompoundModalAnalysis]":
        """Iterable[mastapy.system_model.analyses_and_results.modal_analyses.compound.StraightBevelGearMeshCompoundModalAnalysis]

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
    ) -> "Iterable[_5179.WormGearMeshCompoundModalAnalysis]":
        """Iterable[mastapy.system_model.analyses_and_results.modal_analyses.compound.WormGearMeshCompoundModalAnalysis]

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
    ) -> "Iterable[_5182.ZerolBevelGearMeshCompoundModalAnalysis]":
        """Iterable[mastapy.system_model.analyses_and_results.modal_analyses.compound.ZerolBevelGearMeshCompoundModalAnalysis]

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
    ) -> "Iterable[_5112.GearMeshCompoundModalAnalysis]":
        """Iterable[mastapy.system_model.analyses_and_results.modal_analyses.compound.GearMeshCompoundModalAnalysis]

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
    ) -> "Iterable[_5097.CycloidalDiscCentralBearingConnectionCompoundModalAnalysis]":
        """Iterable[mastapy.system_model.analyses_and_results.modal_analyses.compound.CycloidalDiscCentralBearingConnectionCompoundModalAnalysis]

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
    ) -> "Iterable[_5099.CycloidalDiscPlanetaryBearingConnectionCompoundModalAnalysis]":
        """Iterable[mastapy.system_model.analyses_and_results.modal_analyses.compound.CycloidalDiscPlanetaryBearingConnectionCompoundModalAnalysis]

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
    ) -> "Iterable[_5145.RingPinsToDiscConnectionCompoundModalAnalysis]":
        """Iterable[mastapy.system_model.analyses_and_results.modal_analyses.compound.RingPinsToDiscConnectionCompoundModalAnalysis]

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
    ) -> "Iterable[_5136.PartToPartShearCouplingConnectionCompoundModalAnalysis]":
        """Iterable[mastapy.system_model.analyses_and_results.modal_analyses.compound.PartToPartShearCouplingConnectionCompoundModalAnalysis]

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
    ) -> "Iterable[_5075.ClutchConnectionCompoundModalAnalysis]":
        """Iterable[mastapy.system_model.analyses_and_results.modal_analyses.compound.ClutchConnectionCompoundModalAnalysis]

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
    def cast_to(self: "Self") -> "_Cast_CompoundModalAnalysis":
        """Cast to another type.

        Returns:
            _Cast_CompoundModalAnalysis
        """
        return _Cast_CompoundModalAnalysis(self)
