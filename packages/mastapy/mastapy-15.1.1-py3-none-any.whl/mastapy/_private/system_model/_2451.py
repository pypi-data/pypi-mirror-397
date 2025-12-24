"""DesignEntity"""

from __future__ import annotations

from typing import TYPE_CHECKING, ClassVar

from mastapy._private._internal.dataclasses import extended_dataclass
from mastapy._private._internal.exception_bridge import exception_bridge
from mastapy._private._internal.exceptions import CastException
from mastapy._private._internal.python_net import (
    python_net_import,
    pythonnet_method_call,
    pythonnet_property_get,
    pythonnet_property_set,
)
from mastapy._private._internal.type_enforcement import enforce_parameter_types
from PIL.Image import Image

from mastapy._private import _0
from mastapy._private._internal import constructor, conversion, utility

_DESIGN_ENTITY = python_net_import("SMT.MastaAPI.SystemModel", "DesignEntity")

if TYPE_CHECKING:
    from typing import Any, List, Type, TypeVar

    from mastapy._private._internal.typing import PathLike

    from mastapy._private.system_model import _2448
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
    from mastapy._private.utility.model_validation import _2020, _2021
    from mastapy._private.utility.scripting import _1968

    Self = TypeVar("Self", bound="DesignEntity")
    CastSelf = TypeVar("CastSelf", bound="DesignEntity._Cast_DesignEntity")


__docformat__ = "restructuredtext en"
__all__ = ("DesignEntity",)


@extended_dataclass(frozen=True, slots=True, weakref_slot=True)
class _Cast_DesignEntity:
    """Special nested class for casting DesignEntity to subclasses."""

    __parent__: "DesignEntity"

    @property
    def abstract_shaft_to_mountable_component_connection(
        self: "CastSelf",
    ) -> "_2524.AbstractShaftToMountableComponentConnection":
        from mastapy._private.system_model.connections_and_sockets import _2524

        return self.__parent__._cast(_2524.AbstractShaftToMountableComponentConnection)

    @property
    def belt_connection(self: "CastSelf") -> "_2527.BeltConnection":
        from mastapy._private.system_model.connections_and_sockets import _2527

        return self.__parent__._cast(_2527.BeltConnection)

    @property
    def coaxial_connection(self: "CastSelf") -> "_2528.CoaxialConnection":
        from mastapy._private.system_model.connections_and_sockets import _2528

        return self.__parent__._cast(_2528.CoaxialConnection)

    @property
    def connection(self: "CastSelf") -> "_2531.Connection":
        from mastapy._private.system_model.connections_and_sockets import _2531

        return self.__parent__._cast(_2531.Connection)

    @property
    def cvt_belt_connection(self: "CastSelf") -> "_2532.CVTBeltConnection":
        from mastapy._private.system_model.connections_and_sockets import _2532

        return self.__parent__._cast(_2532.CVTBeltConnection)

    @property
    def inter_mountable_component_connection(
        self: "CastSelf",
    ) -> "_2540.InterMountableComponentConnection":
        from mastapy._private.system_model.connections_and_sockets import _2540

        return self.__parent__._cast(_2540.InterMountableComponentConnection)

    @property
    def planetary_connection(self: "CastSelf") -> "_2546.PlanetaryConnection":
        from mastapy._private.system_model.connections_and_sockets import _2546

        return self.__parent__._cast(_2546.PlanetaryConnection)

    @property
    def rolling_ring_connection(self: "CastSelf") -> "_2551.RollingRingConnection":
        from mastapy._private.system_model.connections_and_sockets import _2551

        return self.__parent__._cast(_2551.RollingRingConnection)

    @property
    def shaft_to_mountable_component_connection(
        self: "CastSelf",
    ) -> "_2554.ShaftToMountableComponentConnection":
        from mastapy._private.system_model.connections_and_sockets import _2554

        return self.__parent__._cast(_2554.ShaftToMountableComponentConnection)

    @property
    def agma_gleason_conical_gear_mesh(
        self: "CastSelf",
    ) -> "_2558.AGMAGleasonConicalGearMesh":
        from mastapy._private.system_model.connections_and_sockets.gears import _2558

        return self.__parent__._cast(_2558.AGMAGleasonConicalGearMesh)

    @property
    def bevel_differential_gear_mesh(
        self: "CastSelf",
    ) -> "_2560.BevelDifferentialGearMesh":
        from mastapy._private.system_model.connections_and_sockets.gears import _2560

        return self.__parent__._cast(_2560.BevelDifferentialGearMesh)

    @property
    def bevel_gear_mesh(self: "CastSelf") -> "_2562.BevelGearMesh":
        from mastapy._private.system_model.connections_and_sockets.gears import _2562

        return self.__parent__._cast(_2562.BevelGearMesh)

    @property
    def concept_gear_mesh(self: "CastSelf") -> "_2564.ConceptGearMesh":
        from mastapy._private.system_model.connections_and_sockets.gears import _2564

        return self.__parent__._cast(_2564.ConceptGearMesh)

    @property
    def conical_gear_mesh(self: "CastSelf") -> "_2566.ConicalGearMesh":
        from mastapy._private.system_model.connections_and_sockets.gears import _2566

        return self.__parent__._cast(_2566.ConicalGearMesh)

    @property
    def cylindrical_gear_mesh(self: "CastSelf") -> "_2568.CylindricalGearMesh":
        from mastapy._private.system_model.connections_and_sockets.gears import _2568

        return self.__parent__._cast(_2568.CylindricalGearMesh)

    @property
    def face_gear_mesh(self: "CastSelf") -> "_2570.FaceGearMesh":
        from mastapy._private.system_model.connections_and_sockets.gears import _2570

        return self.__parent__._cast(_2570.FaceGearMesh)

    @property
    def gear_mesh(self: "CastSelf") -> "_2572.GearMesh":
        from mastapy._private.system_model.connections_and_sockets.gears import _2572

        return self.__parent__._cast(_2572.GearMesh)

    @property
    def hypoid_gear_mesh(self: "CastSelf") -> "_2574.HypoidGearMesh":
        from mastapy._private.system_model.connections_and_sockets.gears import _2574

        return self.__parent__._cast(_2574.HypoidGearMesh)

    @property
    def klingelnberg_cyclo_palloid_conical_gear_mesh(
        self: "CastSelf",
    ) -> "_2577.KlingelnbergCycloPalloidConicalGearMesh":
        from mastapy._private.system_model.connections_and_sockets.gears import _2577

        return self.__parent__._cast(_2577.KlingelnbergCycloPalloidConicalGearMesh)

    @property
    def klingelnberg_cyclo_palloid_hypoid_gear_mesh(
        self: "CastSelf",
    ) -> "_2578.KlingelnbergCycloPalloidHypoidGearMesh":
        from mastapy._private.system_model.connections_and_sockets.gears import _2578

        return self.__parent__._cast(_2578.KlingelnbergCycloPalloidHypoidGearMesh)

    @property
    def klingelnberg_cyclo_palloid_spiral_bevel_gear_mesh(
        self: "CastSelf",
    ) -> "_2579.KlingelnbergCycloPalloidSpiralBevelGearMesh":
        from mastapy._private.system_model.connections_and_sockets.gears import _2579

        return self.__parent__._cast(_2579.KlingelnbergCycloPalloidSpiralBevelGearMesh)

    @property
    def spiral_bevel_gear_mesh(self: "CastSelf") -> "_2582.SpiralBevelGearMesh":
        from mastapy._private.system_model.connections_and_sockets.gears import _2582

        return self.__parent__._cast(_2582.SpiralBevelGearMesh)

    @property
    def straight_bevel_diff_gear_mesh(
        self: "CastSelf",
    ) -> "_2584.StraightBevelDiffGearMesh":
        from mastapy._private.system_model.connections_and_sockets.gears import _2584

        return self.__parent__._cast(_2584.StraightBevelDiffGearMesh)

    @property
    def straight_bevel_gear_mesh(self: "CastSelf") -> "_2586.StraightBevelGearMesh":
        from mastapy._private.system_model.connections_and_sockets.gears import _2586

        return self.__parent__._cast(_2586.StraightBevelGearMesh)

    @property
    def worm_gear_mesh(self: "CastSelf") -> "_2588.WormGearMesh":
        from mastapy._private.system_model.connections_and_sockets.gears import _2588

        return self.__parent__._cast(_2588.WormGearMesh)

    @property
    def zerol_bevel_gear_mesh(self: "CastSelf") -> "_2590.ZerolBevelGearMesh":
        from mastapy._private.system_model.connections_and_sockets.gears import _2590

        return self.__parent__._cast(_2590.ZerolBevelGearMesh)

    @property
    def cycloidal_disc_central_bearing_connection(
        self: "CastSelf",
    ) -> "_2594.CycloidalDiscCentralBearingConnection":
        from mastapy._private.system_model.connections_and_sockets.cycloidal import (
            _2594,
        )

        return self.__parent__._cast(_2594.CycloidalDiscCentralBearingConnection)

    @property
    def cycloidal_disc_planetary_bearing_connection(
        self: "CastSelf",
    ) -> "_2597.CycloidalDiscPlanetaryBearingConnection":
        from mastapy._private.system_model.connections_and_sockets.cycloidal import (
            _2597,
        )

        return self.__parent__._cast(_2597.CycloidalDiscPlanetaryBearingConnection)

    @property
    def ring_pins_to_disc_connection(
        self: "CastSelf",
    ) -> "_2600.RingPinsToDiscConnection":
        from mastapy._private.system_model.connections_and_sockets.cycloidal import (
            _2600,
        )

        return self.__parent__._cast(_2600.RingPinsToDiscConnection)

    @property
    def clutch_connection(self: "CastSelf") -> "_2601.ClutchConnection":
        from mastapy._private.system_model.connections_and_sockets.couplings import (
            _2601,
        )

        return self.__parent__._cast(_2601.ClutchConnection)

    @property
    def concept_coupling_connection(
        self: "CastSelf",
    ) -> "_2603.ConceptCouplingConnection":
        from mastapy._private.system_model.connections_and_sockets.couplings import (
            _2603,
        )

        return self.__parent__._cast(_2603.ConceptCouplingConnection)

    @property
    def coupling_connection(self: "CastSelf") -> "_2605.CouplingConnection":
        from mastapy._private.system_model.connections_and_sockets.couplings import (
            _2605,
        )

        return self.__parent__._cast(_2605.CouplingConnection)

    @property
    def part_to_part_shear_coupling_connection(
        self: "CastSelf",
    ) -> "_2607.PartToPartShearCouplingConnection":
        from mastapy._private.system_model.connections_and_sockets.couplings import (
            _2607,
        )

        return self.__parent__._cast(_2607.PartToPartShearCouplingConnection)

    @property
    def spring_damper_connection(self: "CastSelf") -> "_2609.SpringDamperConnection":
        from mastapy._private.system_model.connections_and_sockets.couplings import (
            _2609,
        )

        return self.__parent__._cast(_2609.SpringDamperConnection)

    @property
    def torque_converter_connection(
        self: "CastSelf",
    ) -> "_2611.TorqueConverterConnection":
        from mastapy._private.system_model.connections_and_sockets.couplings import (
            _2611,
        )

        return self.__parent__._cast(_2611.TorqueConverterConnection)

    @property
    def assembly(self: "CastSelf") -> "_2702.Assembly":
        from mastapy._private.system_model.part_model import _2702

        return self.__parent__._cast(_2702.Assembly)

    @property
    def abstract_assembly(self: "CastSelf") -> "_2703.AbstractAssembly":
        from mastapy._private.system_model.part_model import _2703

        return self.__parent__._cast(_2703.AbstractAssembly)

    @property
    def abstract_shaft(self: "CastSelf") -> "_2704.AbstractShaft":
        from mastapy._private.system_model.part_model import _2704

        return self.__parent__._cast(_2704.AbstractShaft)

    @property
    def abstract_shaft_or_housing(self: "CastSelf") -> "_2705.AbstractShaftOrHousing":
        from mastapy._private.system_model.part_model import _2705

        return self.__parent__._cast(_2705.AbstractShaftOrHousing)

    @property
    def bearing(self: "CastSelf") -> "_2708.Bearing":
        from mastapy._private.system_model.part_model import _2708

        return self.__parent__._cast(_2708.Bearing)

    @property
    def bolt(self: "CastSelf") -> "_2711.Bolt":
        from mastapy._private.system_model.part_model import _2711

        return self.__parent__._cast(_2711.Bolt)

    @property
    def bolted_joint(self: "CastSelf") -> "_2712.BoltedJoint":
        from mastapy._private.system_model.part_model import _2712

        return self.__parent__._cast(_2712.BoltedJoint)

    @property
    def component(self: "CastSelf") -> "_2714.Component":
        from mastapy._private.system_model.part_model import _2714

        return self.__parent__._cast(_2714.Component)

    @property
    def connector(self: "CastSelf") -> "_2717.Connector":
        from mastapy._private.system_model.part_model import _2717

        return self.__parent__._cast(_2717.Connector)

    @property
    def datum(self: "CastSelf") -> "_2718.Datum":
        from mastapy._private.system_model.part_model import _2718

        return self.__parent__._cast(_2718.Datum)

    @property
    def external_cad_model(self: "CastSelf") -> "_2723.ExternalCADModel":
        from mastapy._private.system_model.part_model import _2723

        return self.__parent__._cast(_2723.ExternalCADModel)

    @property
    def fe_part(self: "CastSelf") -> "_2724.FEPart":
        from mastapy._private.system_model.part_model import _2724

        return self.__parent__._cast(_2724.FEPart)

    @property
    def flexible_pin_assembly(self: "CastSelf") -> "_2725.FlexiblePinAssembly":
        from mastapy._private.system_model.part_model import _2725

        return self.__parent__._cast(_2725.FlexiblePinAssembly)

    @property
    def guide_dxf_model(self: "CastSelf") -> "_2726.GuideDxfModel":
        from mastapy._private.system_model.part_model import _2726

        return self.__parent__._cast(_2726.GuideDxfModel)

    @property
    def mass_disc(self: "CastSelf") -> "_2733.MassDisc":
        from mastapy._private.system_model.part_model import _2733

        return self.__parent__._cast(_2733.MassDisc)

    @property
    def measurement_component(self: "CastSelf") -> "_2734.MeasurementComponent":
        from mastapy._private.system_model.part_model import _2734

        return self.__parent__._cast(_2734.MeasurementComponent)

    @property
    def microphone(self: "CastSelf") -> "_2735.Microphone":
        from mastapy._private.system_model.part_model import _2735

        return self.__parent__._cast(_2735.Microphone)

    @property
    def microphone_array(self: "CastSelf") -> "_2736.MicrophoneArray":
        from mastapy._private.system_model.part_model import _2736

        return self.__parent__._cast(_2736.MicrophoneArray)

    @property
    def mountable_component(self: "CastSelf") -> "_2737.MountableComponent":
        from mastapy._private.system_model.part_model import _2737

        return self.__parent__._cast(_2737.MountableComponent)

    @property
    def oil_seal(self: "CastSelf") -> "_2739.OilSeal":
        from mastapy._private.system_model.part_model import _2739

        return self.__parent__._cast(_2739.OilSeal)

    @property
    def part(self: "CastSelf") -> "_2742.Part":
        from mastapy._private.system_model.part_model import _2742

        return self.__parent__._cast(_2742.Part)

    @property
    def planet_carrier(self: "CastSelf") -> "_2744.PlanetCarrier":
        from mastapy._private.system_model.part_model import _2744

        return self.__parent__._cast(_2744.PlanetCarrier)

    @property
    def point_load(self: "CastSelf") -> "_2746.PointLoad":
        from mastapy._private.system_model.part_model import _2746

        return self.__parent__._cast(_2746.PointLoad)

    @property
    def power_load(self: "CastSelf") -> "_2747.PowerLoad":
        from mastapy._private.system_model.part_model import _2747

        return self.__parent__._cast(_2747.PowerLoad)

    @property
    def root_assembly(self: "CastSelf") -> "_2750.RootAssembly":
        from mastapy._private.system_model.part_model import _2750

        return self.__parent__._cast(_2750.RootAssembly)

    @property
    def specialised_assembly(self: "CastSelf") -> "_2752.SpecialisedAssembly":
        from mastapy._private.system_model.part_model import _2752

        return self.__parent__._cast(_2752.SpecialisedAssembly)

    @property
    def unbalanced_mass(self: "CastSelf") -> "_2753.UnbalancedMass":
        from mastapy._private.system_model.part_model import _2753

        return self.__parent__._cast(_2753.UnbalancedMass)

    @property
    def virtual_component(self: "CastSelf") -> "_2755.VirtualComponent":
        from mastapy._private.system_model.part_model import _2755

        return self.__parent__._cast(_2755.VirtualComponent)

    @property
    def shaft(self: "CastSelf") -> "_2758.Shaft":
        from mastapy._private.system_model.part_model.shaft_model import _2758

        return self.__parent__._cast(_2758.Shaft)

    @property
    def agma_gleason_conical_gear(self: "CastSelf") -> "_2794.AGMAGleasonConicalGear":
        from mastapy._private.system_model.part_model.gears import _2794

        return self.__parent__._cast(_2794.AGMAGleasonConicalGear)

    @property
    def agma_gleason_conical_gear_set(
        self: "CastSelf",
    ) -> "_2795.AGMAGleasonConicalGearSet":
        from mastapy._private.system_model.part_model.gears import _2795

        return self.__parent__._cast(_2795.AGMAGleasonConicalGearSet)

    @property
    def bevel_differential_gear(self: "CastSelf") -> "_2796.BevelDifferentialGear":
        from mastapy._private.system_model.part_model.gears import _2796

        return self.__parent__._cast(_2796.BevelDifferentialGear)

    @property
    def bevel_differential_gear_set(
        self: "CastSelf",
    ) -> "_2797.BevelDifferentialGearSet":
        from mastapy._private.system_model.part_model.gears import _2797

        return self.__parent__._cast(_2797.BevelDifferentialGearSet)

    @property
    def bevel_differential_planet_gear(
        self: "CastSelf",
    ) -> "_2798.BevelDifferentialPlanetGear":
        from mastapy._private.system_model.part_model.gears import _2798

        return self.__parent__._cast(_2798.BevelDifferentialPlanetGear)

    @property
    def bevel_differential_sun_gear(
        self: "CastSelf",
    ) -> "_2799.BevelDifferentialSunGear":
        from mastapy._private.system_model.part_model.gears import _2799

        return self.__parent__._cast(_2799.BevelDifferentialSunGear)

    @property
    def bevel_gear(self: "CastSelf") -> "_2800.BevelGear":
        from mastapy._private.system_model.part_model.gears import _2800

        return self.__parent__._cast(_2800.BevelGear)

    @property
    def bevel_gear_set(self: "CastSelf") -> "_2801.BevelGearSet":
        from mastapy._private.system_model.part_model.gears import _2801

        return self.__parent__._cast(_2801.BevelGearSet)

    @property
    def concept_gear(self: "CastSelf") -> "_2802.ConceptGear":
        from mastapy._private.system_model.part_model.gears import _2802

        return self.__parent__._cast(_2802.ConceptGear)

    @property
    def concept_gear_set(self: "CastSelf") -> "_2803.ConceptGearSet":
        from mastapy._private.system_model.part_model.gears import _2803

        return self.__parent__._cast(_2803.ConceptGearSet)

    @property
    def conical_gear(self: "CastSelf") -> "_2804.ConicalGear":
        from mastapy._private.system_model.part_model.gears import _2804

        return self.__parent__._cast(_2804.ConicalGear)

    @property
    def conical_gear_set(self: "CastSelf") -> "_2805.ConicalGearSet":
        from mastapy._private.system_model.part_model.gears import _2805

        return self.__parent__._cast(_2805.ConicalGearSet)

    @property
    def cylindrical_gear(self: "CastSelf") -> "_2806.CylindricalGear":
        from mastapy._private.system_model.part_model.gears import _2806

        return self.__parent__._cast(_2806.CylindricalGear)

    @property
    def cylindrical_gear_set(self: "CastSelf") -> "_2807.CylindricalGearSet":
        from mastapy._private.system_model.part_model.gears import _2807

        return self.__parent__._cast(_2807.CylindricalGearSet)

    @property
    def cylindrical_planet_gear(self: "CastSelf") -> "_2808.CylindricalPlanetGear":
        from mastapy._private.system_model.part_model.gears import _2808

        return self.__parent__._cast(_2808.CylindricalPlanetGear)

    @property
    def face_gear(self: "CastSelf") -> "_2809.FaceGear":
        from mastapy._private.system_model.part_model.gears import _2809

        return self.__parent__._cast(_2809.FaceGear)

    @property
    def face_gear_set(self: "CastSelf") -> "_2810.FaceGearSet":
        from mastapy._private.system_model.part_model.gears import _2810

        return self.__parent__._cast(_2810.FaceGearSet)

    @property
    def gear(self: "CastSelf") -> "_2811.Gear":
        from mastapy._private.system_model.part_model.gears import _2811

        return self.__parent__._cast(_2811.Gear)

    @property
    def gear_set(self: "CastSelf") -> "_2813.GearSet":
        from mastapy._private.system_model.part_model.gears import _2813

        return self.__parent__._cast(_2813.GearSet)

    @property
    def hypoid_gear(self: "CastSelf") -> "_2815.HypoidGear":
        from mastapy._private.system_model.part_model.gears import _2815

        return self.__parent__._cast(_2815.HypoidGear)

    @property
    def hypoid_gear_set(self: "CastSelf") -> "_2816.HypoidGearSet":
        from mastapy._private.system_model.part_model.gears import _2816

        return self.__parent__._cast(_2816.HypoidGearSet)

    @property
    def klingelnberg_cyclo_palloid_conical_gear(
        self: "CastSelf",
    ) -> "_2817.KlingelnbergCycloPalloidConicalGear":
        from mastapy._private.system_model.part_model.gears import _2817

        return self.__parent__._cast(_2817.KlingelnbergCycloPalloidConicalGear)

    @property
    def klingelnberg_cyclo_palloid_conical_gear_set(
        self: "CastSelf",
    ) -> "_2818.KlingelnbergCycloPalloidConicalGearSet":
        from mastapy._private.system_model.part_model.gears import _2818

        return self.__parent__._cast(_2818.KlingelnbergCycloPalloidConicalGearSet)

    @property
    def klingelnberg_cyclo_palloid_hypoid_gear(
        self: "CastSelf",
    ) -> "_2819.KlingelnbergCycloPalloidHypoidGear":
        from mastapy._private.system_model.part_model.gears import _2819

        return self.__parent__._cast(_2819.KlingelnbergCycloPalloidHypoidGear)

    @property
    def klingelnberg_cyclo_palloid_hypoid_gear_set(
        self: "CastSelf",
    ) -> "_2820.KlingelnbergCycloPalloidHypoidGearSet":
        from mastapy._private.system_model.part_model.gears import _2820

        return self.__parent__._cast(_2820.KlingelnbergCycloPalloidHypoidGearSet)

    @property
    def klingelnberg_cyclo_palloid_spiral_bevel_gear(
        self: "CastSelf",
    ) -> "_2821.KlingelnbergCycloPalloidSpiralBevelGear":
        from mastapy._private.system_model.part_model.gears import _2821

        return self.__parent__._cast(_2821.KlingelnbergCycloPalloidSpiralBevelGear)

    @property
    def klingelnberg_cyclo_palloid_spiral_bevel_gear_set(
        self: "CastSelf",
    ) -> "_2822.KlingelnbergCycloPalloidSpiralBevelGearSet":
        from mastapy._private.system_model.part_model.gears import _2822

        return self.__parent__._cast(_2822.KlingelnbergCycloPalloidSpiralBevelGearSet)

    @property
    def planetary_gear_set(self: "CastSelf") -> "_2823.PlanetaryGearSet":
        from mastapy._private.system_model.part_model.gears import _2823

        return self.__parent__._cast(_2823.PlanetaryGearSet)

    @property
    def spiral_bevel_gear(self: "CastSelf") -> "_2825.SpiralBevelGear":
        from mastapy._private.system_model.part_model.gears import _2825

        return self.__parent__._cast(_2825.SpiralBevelGear)

    @property
    def spiral_bevel_gear_set(self: "CastSelf") -> "_2826.SpiralBevelGearSet":
        from mastapy._private.system_model.part_model.gears import _2826

        return self.__parent__._cast(_2826.SpiralBevelGearSet)

    @property
    def straight_bevel_diff_gear(self: "CastSelf") -> "_2827.StraightBevelDiffGear":
        from mastapy._private.system_model.part_model.gears import _2827

        return self.__parent__._cast(_2827.StraightBevelDiffGear)

    @property
    def straight_bevel_diff_gear_set(
        self: "CastSelf",
    ) -> "_2828.StraightBevelDiffGearSet":
        from mastapy._private.system_model.part_model.gears import _2828

        return self.__parent__._cast(_2828.StraightBevelDiffGearSet)

    @property
    def straight_bevel_gear(self: "CastSelf") -> "_2829.StraightBevelGear":
        from mastapy._private.system_model.part_model.gears import _2829

        return self.__parent__._cast(_2829.StraightBevelGear)

    @property
    def straight_bevel_gear_set(self: "CastSelf") -> "_2830.StraightBevelGearSet":
        from mastapy._private.system_model.part_model.gears import _2830

        return self.__parent__._cast(_2830.StraightBevelGearSet)

    @property
    def straight_bevel_planet_gear(self: "CastSelf") -> "_2831.StraightBevelPlanetGear":
        from mastapy._private.system_model.part_model.gears import _2831

        return self.__parent__._cast(_2831.StraightBevelPlanetGear)

    @property
    def straight_bevel_sun_gear(self: "CastSelf") -> "_2832.StraightBevelSunGear":
        from mastapy._private.system_model.part_model.gears import _2832

        return self.__parent__._cast(_2832.StraightBevelSunGear)

    @property
    def worm_gear(self: "CastSelf") -> "_2833.WormGear":
        from mastapy._private.system_model.part_model.gears import _2833

        return self.__parent__._cast(_2833.WormGear)

    @property
    def worm_gear_set(self: "CastSelf") -> "_2834.WormGearSet":
        from mastapy._private.system_model.part_model.gears import _2834

        return self.__parent__._cast(_2834.WormGearSet)

    @property
    def zerol_bevel_gear(self: "CastSelf") -> "_2835.ZerolBevelGear":
        from mastapy._private.system_model.part_model.gears import _2835

        return self.__parent__._cast(_2835.ZerolBevelGear)

    @property
    def zerol_bevel_gear_set(self: "CastSelf") -> "_2836.ZerolBevelGearSet":
        from mastapy._private.system_model.part_model.gears import _2836

        return self.__parent__._cast(_2836.ZerolBevelGearSet)

    @property
    def cycloidal_assembly(self: "CastSelf") -> "_2850.CycloidalAssembly":
        from mastapy._private.system_model.part_model.cycloidal import _2850

        return self.__parent__._cast(_2850.CycloidalAssembly)

    @property
    def cycloidal_disc(self: "CastSelf") -> "_2851.CycloidalDisc":
        from mastapy._private.system_model.part_model.cycloidal import _2851

        return self.__parent__._cast(_2851.CycloidalDisc)

    @property
    def ring_pins(self: "CastSelf") -> "_2852.RingPins":
        from mastapy._private.system_model.part_model.cycloidal import _2852

        return self.__parent__._cast(_2852.RingPins)

    @property
    def belt_drive(self: "CastSelf") -> "_2859.BeltDrive":
        from mastapy._private.system_model.part_model.couplings import _2859

        return self.__parent__._cast(_2859.BeltDrive)

    @property
    def clutch(self: "CastSelf") -> "_2861.Clutch":
        from mastapy._private.system_model.part_model.couplings import _2861

        return self.__parent__._cast(_2861.Clutch)

    @property
    def clutch_half(self: "CastSelf") -> "_2862.ClutchHalf":
        from mastapy._private.system_model.part_model.couplings import _2862

        return self.__parent__._cast(_2862.ClutchHalf)

    @property
    def concept_coupling(self: "CastSelf") -> "_2864.ConceptCoupling":
        from mastapy._private.system_model.part_model.couplings import _2864

        return self.__parent__._cast(_2864.ConceptCoupling)

    @property
    def concept_coupling_half(self: "CastSelf") -> "_2865.ConceptCouplingHalf":
        from mastapy._private.system_model.part_model.couplings import _2865

        return self.__parent__._cast(_2865.ConceptCouplingHalf)

    @property
    def coupling(self: "CastSelf") -> "_2867.Coupling":
        from mastapy._private.system_model.part_model.couplings import _2867

        return self.__parent__._cast(_2867.Coupling)

    @property
    def coupling_half(self: "CastSelf") -> "_2868.CouplingHalf":
        from mastapy._private.system_model.part_model.couplings import _2868

        return self.__parent__._cast(_2868.CouplingHalf)

    @property
    def cvt(self: "CastSelf") -> "_2870.CVT":
        from mastapy._private.system_model.part_model.couplings import _2870

        return self.__parent__._cast(_2870.CVT)

    @property
    def cvt_pulley(self: "CastSelf") -> "_2871.CVTPulley":
        from mastapy._private.system_model.part_model.couplings import _2871

        return self.__parent__._cast(_2871.CVTPulley)

    @property
    def part_to_part_shear_coupling(
        self: "CastSelf",
    ) -> "_2872.PartToPartShearCoupling":
        from mastapy._private.system_model.part_model.couplings import _2872

        return self.__parent__._cast(_2872.PartToPartShearCoupling)

    @property
    def part_to_part_shear_coupling_half(
        self: "CastSelf",
    ) -> "_2873.PartToPartShearCouplingHalf":
        from mastapy._private.system_model.part_model.couplings import _2873

        return self.__parent__._cast(_2873.PartToPartShearCouplingHalf)

    @property
    def pulley(self: "CastSelf") -> "_2875.Pulley":
        from mastapy._private.system_model.part_model.couplings import _2875

        return self.__parent__._cast(_2875.Pulley)

    @property
    def rolling_ring(self: "CastSelf") -> "_2882.RollingRing":
        from mastapy._private.system_model.part_model.couplings import _2882

        return self.__parent__._cast(_2882.RollingRing)

    @property
    def rolling_ring_assembly(self: "CastSelf") -> "_2883.RollingRingAssembly":
        from mastapy._private.system_model.part_model.couplings import _2883

        return self.__parent__._cast(_2883.RollingRingAssembly)

    @property
    def shaft_hub_connection(self: "CastSelf") -> "_2884.ShaftHubConnection":
        from mastapy._private.system_model.part_model.couplings import _2884

        return self.__parent__._cast(_2884.ShaftHubConnection)

    @property
    def spring_damper(self: "CastSelf") -> "_2890.SpringDamper":
        from mastapy._private.system_model.part_model.couplings import _2890

        return self.__parent__._cast(_2890.SpringDamper)

    @property
    def spring_damper_half(self: "CastSelf") -> "_2891.SpringDamperHalf":
        from mastapy._private.system_model.part_model.couplings import _2891

        return self.__parent__._cast(_2891.SpringDamperHalf)

    @property
    def synchroniser(self: "CastSelf") -> "_2892.Synchroniser":
        from mastapy._private.system_model.part_model.couplings import _2892

        return self.__parent__._cast(_2892.Synchroniser)

    @property
    def synchroniser_half(self: "CastSelf") -> "_2894.SynchroniserHalf":
        from mastapy._private.system_model.part_model.couplings import _2894

        return self.__parent__._cast(_2894.SynchroniserHalf)

    @property
    def synchroniser_part(self: "CastSelf") -> "_2895.SynchroniserPart":
        from mastapy._private.system_model.part_model.couplings import _2895

        return self.__parent__._cast(_2895.SynchroniserPart)

    @property
    def synchroniser_sleeve(self: "CastSelf") -> "_2896.SynchroniserSleeve":
        from mastapy._private.system_model.part_model.couplings import _2896

        return self.__parent__._cast(_2896.SynchroniserSleeve)

    @property
    def torque_converter(self: "CastSelf") -> "_2897.TorqueConverter":
        from mastapy._private.system_model.part_model.couplings import _2897

        return self.__parent__._cast(_2897.TorqueConverter)

    @property
    def torque_converter_pump(self: "CastSelf") -> "_2898.TorqueConverterPump":
        from mastapy._private.system_model.part_model.couplings import _2898

        return self.__parent__._cast(_2898.TorqueConverterPump)

    @property
    def torque_converter_turbine(self: "CastSelf") -> "_2900.TorqueConverterTurbine":
        from mastapy._private.system_model.part_model.couplings import _2900

        return self.__parent__._cast(_2900.TorqueConverterTurbine)

    @property
    def design_entity(self: "CastSelf") -> "DesignEntity":
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
class DesignEntity(_0.APIBase):
    """DesignEntity

    This is a mastapy class.
    """

    TYPE: ClassVar["Type"] = _DESIGN_ENTITY

    wrapped: "Any"

    def __post_init__(self: "Self") -> None:
        """Override of the post initialisation magic method."""
        if not hasattr(self.wrapped, "reference_count"):
            self.wrapped.reference_count = 0

        self.wrapped.reference_count += 1

    @property
    @exception_bridge
    def comment(self: "Self") -> "str":
        """str"""
        temp = pythonnet_property_get(self.wrapped, "Comment")

        if temp is None:
            return ""

        return temp

    @comment.setter
    @exception_bridge
    @enforce_parameter_types
    def comment(self: "Self", value: "str") -> None:
        pythonnet_property_set(
            self.wrapped, "Comment", str(value) if value is not None else ""
        )

    @property
    @exception_bridge
    def full_name_without_root_name(self: "Self") -> "str":
        """str

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "FullNameWithoutRootName")

        if temp is None:
            return ""

        return temp

    @property
    @exception_bridge
    def id(self: "Self") -> "str":
        """str

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "ID")

        if temp is None:
            return ""

        return temp

    @property
    @exception_bridge
    def icon(self: "Self") -> "Image":
        """Image

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "Icon")

        if temp is None:
            return None

        value = conversion.pn_to_mp_smt_bitmap(temp)

        if value is None:
            return None

        return value

    @property
    @exception_bridge
    def small_icon(self: "Self") -> "Image":
        """Image

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "SmallIcon")

        if temp is None:
            return None

        value = conversion.pn_to_mp_smt_bitmap(temp)

        if value is None:
            return None

        return value

    @property
    @exception_bridge
    def unique_name(self: "Self") -> "str":
        """str

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "UniqueName")

        if temp is None:
            return ""

        return temp

    @property
    @exception_bridge
    def design_properties(self: "Self") -> "_2448.Design":
        """mastapy.system_model.Design

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "DesignProperties")

        if temp is None:
            return None

        type_ = temp.GetType()
        return constructor.new(type_.Namespace, type_.Name)(temp)

    @property
    @exception_bridge
    def all_design_entities(self: "Self") -> "List[DesignEntity]":
        """List[mastapy.system_model.DesignEntity]

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "AllDesignEntities")

        if temp is None:
            return None

        value = conversion.pn_to_mp_objects_in_list(temp)

        if value is None:
            return None

        return value

    @property
    @exception_bridge
    def all_status_errors(self: "Self") -> "List[_2021.StatusItem]":
        """List[mastapy.utility.model_validation.StatusItem]

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "AllStatusErrors")

        if temp is None:
            return None

        value = conversion.pn_to_mp_objects_in_list(temp)

        if value is None:
            return None

        return value

    @property
    @exception_bridge
    def status(self: "Self") -> "_2020.Status":
        """mastapy.utility.model_validation.Status

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "Status")

        if temp is None:
            return None

        type_ = temp.GetType()
        return constructor.new(type_.Namespace, type_.Name)(temp)

    @property
    @exception_bridge
    def user_specified_data(self: "Self") -> "_1968.UserSpecifiedData":
        """mastapy.utility.scripting.UserSpecifiedData

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "UserSpecifiedData")

        if temp is None:
            return None

        type_ = temp.GetType()
        return constructor.new(type_.Namespace, type_.Name)(temp)

    @property
    @exception_bridge
    def report_names(self: "Self") -> "List[str]":
        """List[str]

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "ReportNames")

        if temp is None:
            return None

        value = conversion.pn_to_mp_objects_in_list(temp, str)

        if value is None:
            return None

        return value

    @exception_bridge
    def delete(self: "Self") -> None:
        """Method does not return."""
        pythonnet_method_call(self.wrapped, "Delete")

    @exception_bridge
    @enforce_parameter_types
    def output_default_report_to(self: "Self", file_path: "PathLike") -> None:
        """Method does not return.

        Args:
            file_path (PathLike)
        """
        file_path = str(file_path)
        pythonnet_method_call(self.wrapped, "OutputDefaultReportTo", file_path)

    @exception_bridge
    def get_default_report_with_encoded_images(self: "Self") -> "str":
        """str"""
        method_result = pythonnet_method_call(
            self.wrapped, "GetDefaultReportWithEncodedImages"
        )
        return method_result

    @exception_bridge
    @enforce_parameter_types
    def output_active_report_to(self: "Self", file_path: "PathLike") -> None:
        """Method does not return.

        Args:
            file_path (PathLike)
        """
        file_path = str(file_path)
        pythonnet_method_call(self.wrapped, "OutputActiveReportTo", file_path)

    @exception_bridge
    @enforce_parameter_types
    def output_active_report_as_text_to(self: "Self", file_path: "PathLike") -> None:
        """Method does not return.

        Args:
            file_path (PathLike)
        """
        file_path = str(file_path)
        pythonnet_method_call(self.wrapped, "OutputActiveReportAsTextTo", file_path)

    @exception_bridge
    def get_active_report_with_encoded_images(self: "Self") -> "str":
        """str"""
        method_result = pythonnet_method_call(
            self.wrapped, "GetActiveReportWithEncodedImages"
        )
        return method_result

    @exception_bridge
    @enforce_parameter_types
    def output_named_report_to(
        self: "Self", report_name: "str", file_path: "PathLike"
    ) -> None:
        """Method does not return.

        Args:
            report_name (str)
            file_path (PathLike)
        """
        report_name = str(report_name)
        file_path = str(file_path)
        pythonnet_method_call(
            self.wrapped,
            "OutputNamedReportTo",
            report_name if report_name else "",
            file_path,
        )

    @exception_bridge
    @enforce_parameter_types
    def output_named_report_as_masta_report(
        self: "Self", report_name: "str", file_path: "PathLike"
    ) -> None:
        """Method does not return.

        Args:
            report_name (str)
            file_path (PathLike)
        """
        report_name = str(report_name)
        file_path = str(file_path)
        pythonnet_method_call(
            self.wrapped,
            "OutputNamedReportAsMastaReport",
            report_name if report_name else "",
            file_path,
        )

    @exception_bridge
    @enforce_parameter_types
    def output_named_report_as_text_to(
        self: "Self", report_name: "str", file_path: "PathLike"
    ) -> None:
        """Method does not return.

        Args:
            report_name (str)
            file_path (PathLike)
        """
        report_name = str(report_name)
        file_path = str(file_path)
        pythonnet_method_call(
            self.wrapped,
            "OutputNamedReportAsTextTo",
            report_name if report_name else "",
            file_path,
        )

    @exception_bridge
    @enforce_parameter_types
    def get_named_report_with_encoded_images(self: "Self", report_name: "str") -> "str":
        """str

        Args:
            report_name (str)
        """
        report_name = str(report_name)
        method_result = pythonnet_method_call(
            self.wrapped,
            "GetNamedReportWithEncodedImages",
            report_name if report_name else "",
        )
        return method_result

    @property
    def cast_to(self: "Self") -> "_Cast_DesignEntity":
        """Cast to another type.

        Returns:
            _Cast_DesignEntity
        """
        return _Cast_DesignEntity(self)
