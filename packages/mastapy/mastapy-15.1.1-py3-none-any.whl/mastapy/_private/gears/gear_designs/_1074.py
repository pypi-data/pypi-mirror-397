"""GearDesignComponent"""

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

from mastapy._private import _0
from mastapy._private._internal import constructor, conversion, utility

_GEAR_DESIGN_COMPONENT = python_net_import(
    "SMT.MastaAPI.Gears.GearDesigns", "GearDesignComponent"
)

if TYPE_CHECKING:
    from typing import Any, List, Type, TypeVar

    from mastapy._private._internal.typing import PathLike

    from mastapy._private.gears.gear_designs import _1073, _1075, _1076
    from mastapy._private.gears.gear_designs.agma_gleason_conical import (
        _1339,
        _1340,
        _1341,
        _1342,
    )
    from mastapy._private.gears.gear_designs.bevel import _1326, _1327, _1328, _1329
    from mastapy._private.gears.gear_designs.concept import _1322, _1323, _1324
    from mastapy._private.gears.gear_designs.conical import _1300, _1301, _1302, _1305
    from mastapy._private.gears.gear_designs.cylindrical import (
        _1144,
        _1150,
        _1160,
        _1173,
        _1174,
    )
    from mastapy._private.gears.gear_designs.face import (
        _1115,
        _1117,
        _1120,
        _1121,
        _1123,
    )
    from mastapy._private.gears.gear_designs.hypoid import _1111, _1112, _1113, _1114
    from mastapy._private.gears.gear_designs.klingelnberg_conical import (
        _1107,
        _1108,
        _1109,
        _1110,
    )
    from mastapy._private.gears.gear_designs.klingelnberg_hypoid import (
        _1103,
        _1104,
        _1105,
        _1106,
    )
    from mastapy._private.gears.gear_designs.klingelnberg_spiral_bevel import (
        _1099,
        _1100,
        _1101,
        _1102,
    )
    from mastapy._private.gears.gear_designs.spiral_bevel import (
        _1095,
        _1096,
        _1097,
        _1098,
    )
    from mastapy._private.gears.gear_designs.straight_bevel import (
        _1087,
        _1088,
        _1089,
        _1090,
    )
    from mastapy._private.gears.gear_designs.straight_bevel_diff import (
        _1091,
        _1092,
        _1093,
        _1094,
    )
    from mastapy._private.gears.gear_designs.worm import (
        _1082,
        _1083,
        _1084,
        _1085,
        _1086,
    )
    from mastapy._private.gears.gear_designs.zerol_bevel import (
        _1078,
        _1079,
        _1080,
        _1081,
    )
    from mastapy._private.utility.scripting import _1968

    Self = TypeVar("Self", bound="GearDesignComponent")
    CastSelf = TypeVar(
        "CastSelf", bound="GearDesignComponent._Cast_GearDesignComponent"
    )


__docformat__ = "restructuredtext en"
__all__ = ("GearDesignComponent",)


@extended_dataclass(frozen=True, slots=True, weakref_slot=True)
class _Cast_GearDesignComponent:
    """Special nested class for casting GearDesignComponent to subclasses."""

    __parent__: "GearDesignComponent"

    @property
    def gear_design(self: "CastSelf") -> "_1073.GearDesign":
        from mastapy._private.gears.gear_designs import _1073

        return self.__parent__._cast(_1073.GearDesign)

    @property
    def gear_mesh_design(self: "CastSelf") -> "_1075.GearMeshDesign":
        from mastapy._private.gears.gear_designs import _1075

        return self.__parent__._cast(_1075.GearMeshDesign)

    @property
    def gear_set_design(self: "CastSelf") -> "_1076.GearSetDesign":
        from mastapy._private.gears.gear_designs import _1076

        return self.__parent__._cast(_1076.GearSetDesign)

    @property
    def zerol_bevel_gear_design(self: "CastSelf") -> "_1078.ZerolBevelGearDesign":
        from mastapy._private.gears.gear_designs.zerol_bevel import _1078

        return self.__parent__._cast(_1078.ZerolBevelGearDesign)

    @property
    def zerol_bevel_gear_mesh_design(
        self: "CastSelf",
    ) -> "_1079.ZerolBevelGearMeshDesign":
        from mastapy._private.gears.gear_designs.zerol_bevel import _1079

        return self.__parent__._cast(_1079.ZerolBevelGearMeshDesign)

    @property
    def zerol_bevel_gear_set_design(
        self: "CastSelf",
    ) -> "_1080.ZerolBevelGearSetDesign":
        from mastapy._private.gears.gear_designs.zerol_bevel import _1080

        return self.__parent__._cast(_1080.ZerolBevelGearSetDesign)

    @property
    def zerol_bevel_meshed_gear_design(
        self: "CastSelf",
    ) -> "_1081.ZerolBevelMeshedGearDesign":
        from mastapy._private.gears.gear_designs.zerol_bevel import _1081

        return self.__parent__._cast(_1081.ZerolBevelMeshedGearDesign)

    @property
    def worm_design(self: "CastSelf") -> "_1082.WormDesign":
        from mastapy._private.gears.gear_designs.worm import _1082

        return self.__parent__._cast(_1082.WormDesign)

    @property
    def worm_gear_design(self: "CastSelf") -> "_1083.WormGearDesign":
        from mastapy._private.gears.gear_designs.worm import _1083

        return self.__parent__._cast(_1083.WormGearDesign)

    @property
    def worm_gear_mesh_design(self: "CastSelf") -> "_1084.WormGearMeshDesign":
        from mastapy._private.gears.gear_designs.worm import _1084

        return self.__parent__._cast(_1084.WormGearMeshDesign)

    @property
    def worm_gear_set_design(self: "CastSelf") -> "_1085.WormGearSetDesign":
        from mastapy._private.gears.gear_designs.worm import _1085

        return self.__parent__._cast(_1085.WormGearSetDesign)

    @property
    def worm_wheel_design(self: "CastSelf") -> "_1086.WormWheelDesign":
        from mastapy._private.gears.gear_designs.worm import _1086

        return self.__parent__._cast(_1086.WormWheelDesign)

    @property
    def straight_bevel_gear_design(self: "CastSelf") -> "_1087.StraightBevelGearDesign":
        from mastapy._private.gears.gear_designs.straight_bevel import _1087

        return self.__parent__._cast(_1087.StraightBevelGearDesign)

    @property
    def straight_bevel_gear_mesh_design(
        self: "CastSelf",
    ) -> "_1088.StraightBevelGearMeshDesign":
        from mastapy._private.gears.gear_designs.straight_bevel import _1088

        return self.__parent__._cast(_1088.StraightBevelGearMeshDesign)

    @property
    def straight_bevel_gear_set_design(
        self: "CastSelf",
    ) -> "_1089.StraightBevelGearSetDesign":
        from mastapy._private.gears.gear_designs.straight_bevel import _1089

        return self.__parent__._cast(_1089.StraightBevelGearSetDesign)

    @property
    def straight_bevel_meshed_gear_design(
        self: "CastSelf",
    ) -> "_1090.StraightBevelMeshedGearDesign":
        from mastapy._private.gears.gear_designs.straight_bevel import _1090

        return self.__parent__._cast(_1090.StraightBevelMeshedGearDesign)

    @property
    def straight_bevel_diff_gear_design(
        self: "CastSelf",
    ) -> "_1091.StraightBevelDiffGearDesign":
        from mastapy._private.gears.gear_designs.straight_bevel_diff import _1091

        return self.__parent__._cast(_1091.StraightBevelDiffGearDesign)

    @property
    def straight_bevel_diff_gear_mesh_design(
        self: "CastSelf",
    ) -> "_1092.StraightBevelDiffGearMeshDesign":
        from mastapy._private.gears.gear_designs.straight_bevel_diff import _1092

        return self.__parent__._cast(_1092.StraightBevelDiffGearMeshDesign)

    @property
    def straight_bevel_diff_gear_set_design(
        self: "CastSelf",
    ) -> "_1093.StraightBevelDiffGearSetDesign":
        from mastapy._private.gears.gear_designs.straight_bevel_diff import _1093

        return self.__parent__._cast(_1093.StraightBevelDiffGearSetDesign)

    @property
    def straight_bevel_diff_meshed_gear_design(
        self: "CastSelf",
    ) -> "_1094.StraightBevelDiffMeshedGearDesign":
        from mastapy._private.gears.gear_designs.straight_bevel_diff import _1094

        return self.__parent__._cast(_1094.StraightBevelDiffMeshedGearDesign)

    @property
    def spiral_bevel_gear_design(self: "CastSelf") -> "_1095.SpiralBevelGearDesign":
        from mastapy._private.gears.gear_designs.spiral_bevel import _1095

        return self.__parent__._cast(_1095.SpiralBevelGearDesign)

    @property
    def spiral_bevel_gear_mesh_design(
        self: "CastSelf",
    ) -> "_1096.SpiralBevelGearMeshDesign":
        from mastapy._private.gears.gear_designs.spiral_bevel import _1096

        return self.__parent__._cast(_1096.SpiralBevelGearMeshDesign)

    @property
    def spiral_bevel_gear_set_design(
        self: "CastSelf",
    ) -> "_1097.SpiralBevelGearSetDesign":
        from mastapy._private.gears.gear_designs.spiral_bevel import _1097

        return self.__parent__._cast(_1097.SpiralBevelGearSetDesign)

    @property
    def spiral_bevel_meshed_gear_design(
        self: "CastSelf",
    ) -> "_1098.SpiralBevelMeshedGearDesign":
        from mastapy._private.gears.gear_designs.spiral_bevel import _1098

        return self.__parent__._cast(_1098.SpiralBevelMeshedGearDesign)

    @property
    def klingelnberg_cyclo_palloid_spiral_bevel_gear_design(
        self: "CastSelf",
    ) -> "_1099.KlingelnbergCycloPalloidSpiralBevelGearDesign":
        from mastapy._private.gears.gear_designs.klingelnberg_spiral_bevel import _1099

        return self.__parent__._cast(
            _1099.KlingelnbergCycloPalloidSpiralBevelGearDesign
        )

    @property
    def klingelnberg_cyclo_palloid_spiral_bevel_gear_mesh_design(
        self: "CastSelf",
    ) -> "_1100.KlingelnbergCycloPalloidSpiralBevelGearMeshDesign":
        from mastapy._private.gears.gear_designs.klingelnberg_spiral_bevel import _1100

        return self.__parent__._cast(
            _1100.KlingelnbergCycloPalloidSpiralBevelGearMeshDesign
        )

    @property
    def klingelnberg_cyclo_palloid_spiral_bevel_gear_set_design(
        self: "CastSelf",
    ) -> "_1101.KlingelnbergCycloPalloidSpiralBevelGearSetDesign":
        from mastapy._private.gears.gear_designs.klingelnberg_spiral_bevel import _1101

        return self.__parent__._cast(
            _1101.KlingelnbergCycloPalloidSpiralBevelGearSetDesign
        )

    @property
    def klingelnberg_cyclo_palloid_spiral_bevel_meshed_gear_design(
        self: "CastSelf",
    ) -> "_1102.KlingelnbergCycloPalloidSpiralBevelMeshedGearDesign":
        from mastapy._private.gears.gear_designs.klingelnberg_spiral_bevel import _1102

        return self.__parent__._cast(
            _1102.KlingelnbergCycloPalloidSpiralBevelMeshedGearDesign
        )

    @property
    def klingelnberg_cyclo_palloid_hypoid_gear_design(
        self: "CastSelf",
    ) -> "_1103.KlingelnbergCycloPalloidHypoidGearDesign":
        from mastapy._private.gears.gear_designs.klingelnberg_hypoid import _1103

        return self.__parent__._cast(_1103.KlingelnbergCycloPalloidHypoidGearDesign)

    @property
    def klingelnberg_cyclo_palloid_hypoid_gear_mesh_design(
        self: "CastSelf",
    ) -> "_1104.KlingelnbergCycloPalloidHypoidGearMeshDesign":
        from mastapy._private.gears.gear_designs.klingelnberg_hypoid import _1104

        return self.__parent__._cast(_1104.KlingelnbergCycloPalloidHypoidGearMeshDesign)

    @property
    def klingelnberg_cyclo_palloid_hypoid_gear_set_design(
        self: "CastSelf",
    ) -> "_1105.KlingelnbergCycloPalloidHypoidGearSetDesign":
        from mastapy._private.gears.gear_designs.klingelnberg_hypoid import _1105

        return self.__parent__._cast(_1105.KlingelnbergCycloPalloidHypoidGearSetDesign)

    @property
    def klingelnberg_cyclo_palloid_hypoid_meshed_gear_design(
        self: "CastSelf",
    ) -> "_1106.KlingelnbergCycloPalloidHypoidMeshedGearDesign":
        from mastapy._private.gears.gear_designs.klingelnberg_hypoid import _1106

        return self.__parent__._cast(
            _1106.KlingelnbergCycloPalloidHypoidMeshedGearDesign
        )

    @property
    def klingelnberg_conical_gear_design(
        self: "CastSelf",
    ) -> "_1107.KlingelnbergConicalGearDesign":
        from mastapy._private.gears.gear_designs.klingelnberg_conical import _1107

        return self.__parent__._cast(_1107.KlingelnbergConicalGearDesign)

    @property
    def klingelnberg_conical_gear_mesh_design(
        self: "CastSelf",
    ) -> "_1108.KlingelnbergConicalGearMeshDesign":
        from mastapy._private.gears.gear_designs.klingelnberg_conical import _1108

        return self.__parent__._cast(_1108.KlingelnbergConicalGearMeshDesign)

    @property
    def klingelnberg_conical_gear_set_design(
        self: "CastSelf",
    ) -> "_1109.KlingelnbergConicalGearSetDesign":
        from mastapy._private.gears.gear_designs.klingelnberg_conical import _1109

        return self.__parent__._cast(_1109.KlingelnbergConicalGearSetDesign)

    @property
    def klingelnberg_conical_meshed_gear_design(
        self: "CastSelf",
    ) -> "_1110.KlingelnbergConicalMeshedGearDesign":
        from mastapy._private.gears.gear_designs.klingelnberg_conical import _1110

        return self.__parent__._cast(_1110.KlingelnbergConicalMeshedGearDesign)

    @property
    def hypoid_gear_design(self: "CastSelf") -> "_1111.HypoidGearDesign":
        from mastapy._private.gears.gear_designs.hypoid import _1111

        return self.__parent__._cast(_1111.HypoidGearDesign)

    @property
    def hypoid_gear_mesh_design(self: "CastSelf") -> "_1112.HypoidGearMeshDesign":
        from mastapy._private.gears.gear_designs.hypoid import _1112

        return self.__parent__._cast(_1112.HypoidGearMeshDesign)

    @property
    def hypoid_gear_set_design(self: "CastSelf") -> "_1113.HypoidGearSetDesign":
        from mastapy._private.gears.gear_designs.hypoid import _1113

        return self.__parent__._cast(_1113.HypoidGearSetDesign)

    @property
    def hypoid_meshed_gear_design(self: "CastSelf") -> "_1114.HypoidMeshedGearDesign":
        from mastapy._private.gears.gear_designs.hypoid import _1114

        return self.__parent__._cast(_1114.HypoidMeshedGearDesign)

    @property
    def face_gear_design(self: "CastSelf") -> "_1115.FaceGearDesign":
        from mastapy._private.gears.gear_designs.face import _1115

        return self.__parent__._cast(_1115.FaceGearDesign)

    @property
    def face_gear_mesh_design(self: "CastSelf") -> "_1117.FaceGearMeshDesign":
        from mastapy._private.gears.gear_designs.face import _1117

        return self.__parent__._cast(_1117.FaceGearMeshDesign)

    @property
    def face_gear_pinion_design(self: "CastSelf") -> "_1120.FaceGearPinionDesign":
        from mastapy._private.gears.gear_designs.face import _1120

        return self.__parent__._cast(_1120.FaceGearPinionDesign)

    @property
    def face_gear_set_design(self: "CastSelf") -> "_1121.FaceGearSetDesign":
        from mastapy._private.gears.gear_designs.face import _1121

        return self.__parent__._cast(_1121.FaceGearSetDesign)

    @property
    def face_gear_wheel_design(self: "CastSelf") -> "_1123.FaceGearWheelDesign":
        from mastapy._private.gears.gear_designs.face import _1123

        return self.__parent__._cast(_1123.FaceGearWheelDesign)

    @property
    def cylindrical_gear_design(self: "CastSelf") -> "_1144.CylindricalGearDesign":
        from mastapy._private.gears.gear_designs.cylindrical import _1144

        return self.__parent__._cast(_1144.CylindricalGearDesign)

    @property
    def cylindrical_gear_mesh_design(
        self: "CastSelf",
    ) -> "_1150.CylindricalGearMeshDesign":
        from mastapy._private.gears.gear_designs.cylindrical import _1150

        return self.__parent__._cast(_1150.CylindricalGearMeshDesign)

    @property
    def cylindrical_gear_set_design(
        self: "CastSelf",
    ) -> "_1160.CylindricalGearSetDesign":
        from mastapy._private.gears.gear_designs.cylindrical import _1160

        return self.__parent__._cast(_1160.CylindricalGearSetDesign)

    @property
    def cylindrical_planetary_gear_set_design(
        self: "CastSelf",
    ) -> "_1173.CylindricalPlanetaryGearSetDesign":
        from mastapy._private.gears.gear_designs.cylindrical import _1173

        return self.__parent__._cast(_1173.CylindricalPlanetaryGearSetDesign)

    @property
    def cylindrical_planet_gear_design(
        self: "CastSelf",
    ) -> "_1174.CylindricalPlanetGearDesign":
        from mastapy._private.gears.gear_designs.cylindrical import _1174

        return self.__parent__._cast(_1174.CylindricalPlanetGearDesign)

    @property
    def conical_gear_design(self: "CastSelf") -> "_1300.ConicalGearDesign":
        from mastapy._private.gears.gear_designs.conical import _1300

        return self.__parent__._cast(_1300.ConicalGearDesign)

    @property
    def conical_gear_mesh_design(self: "CastSelf") -> "_1301.ConicalGearMeshDesign":
        from mastapy._private.gears.gear_designs.conical import _1301

        return self.__parent__._cast(_1301.ConicalGearMeshDesign)

    @property
    def conical_gear_set_design(self: "CastSelf") -> "_1302.ConicalGearSetDesign":
        from mastapy._private.gears.gear_designs.conical import _1302

        return self.__parent__._cast(_1302.ConicalGearSetDesign)

    @property
    def conical_meshed_gear_design(self: "CastSelf") -> "_1305.ConicalMeshedGearDesign":
        from mastapy._private.gears.gear_designs.conical import _1305

        return self.__parent__._cast(_1305.ConicalMeshedGearDesign)

    @property
    def concept_gear_design(self: "CastSelf") -> "_1322.ConceptGearDesign":
        from mastapy._private.gears.gear_designs.concept import _1322

        return self.__parent__._cast(_1322.ConceptGearDesign)

    @property
    def concept_gear_mesh_design(self: "CastSelf") -> "_1323.ConceptGearMeshDesign":
        from mastapy._private.gears.gear_designs.concept import _1323

        return self.__parent__._cast(_1323.ConceptGearMeshDesign)

    @property
    def concept_gear_set_design(self: "CastSelf") -> "_1324.ConceptGearSetDesign":
        from mastapy._private.gears.gear_designs.concept import _1324

        return self.__parent__._cast(_1324.ConceptGearSetDesign)

    @property
    def bevel_gear_design(self: "CastSelf") -> "_1326.BevelGearDesign":
        from mastapy._private.gears.gear_designs.bevel import _1326

        return self.__parent__._cast(_1326.BevelGearDesign)

    @property
    def bevel_gear_mesh_design(self: "CastSelf") -> "_1327.BevelGearMeshDesign":
        from mastapy._private.gears.gear_designs.bevel import _1327

        return self.__parent__._cast(_1327.BevelGearMeshDesign)

    @property
    def bevel_gear_set_design(self: "CastSelf") -> "_1328.BevelGearSetDesign":
        from mastapy._private.gears.gear_designs.bevel import _1328

        return self.__parent__._cast(_1328.BevelGearSetDesign)

    @property
    def bevel_meshed_gear_design(self: "CastSelf") -> "_1329.BevelMeshedGearDesign":
        from mastapy._private.gears.gear_designs.bevel import _1329

        return self.__parent__._cast(_1329.BevelMeshedGearDesign)

    @property
    def agma_gleason_conical_gear_design(
        self: "CastSelf",
    ) -> "_1339.AGMAGleasonConicalGearDesign":
        from mastapy._private.gears.gear_designs.agma_gleason_conical import _1339

        return self.__parent__._cast(_1339.AGMAGleasonConicalGearDesign)

    @property
    def agma_gleason_conical_gear_mesh_design(
        self: "CastSelf",
    ) -> "_1340.AGMAGleasonConicalGearMeshDesign":
        from mastapy._private.gears.gear_designs.agma_gleason_conical import _1340

        return self.__parent__._cast(_1340.AGMAGleasonConicalGearMeshDesign)

    @property
    def agma_gleason_conical_gear_set_design(
        self: "CastSelf",
    ) -> "_1341.AGMAGleasonConicalGearSetDesign":
        from mastapy._private.gears.gear_designs.agma_gleason_conical import _1341

        return self.__parent__._cast(_1341.AGMAGleasonConicalGearSetDesign)

    @property
    def agma_gleason_conical_meshed_gear_design(
        self: "CastSelf",
    ) -> "_1342.AGMAGleasonConicalMeshedGearDesign":
        from mastapy._private.gears.gear_designs.agma_gleason_conical import _1342

        return self.__parent__._cast(_1342.AGMAGleasonConicalMeshedGearDesign)

    @property
    def gear_design_component(self: "CastSelf") -> "GearDesignComponent":
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
class GearDesignComponent(_0.APIBase):
    """GearDesignComponent

    This is a mastapy class.
    """

    TYPE: ClassVar["Type"] = _GEAR_DESIGN_COMPONENT

    wrapped: "Any"

    def __post_init__(self: "Self") -> None:
        """Override of the post initialisation magic method."""
        if not hasattr(self.wrapped, "reference_count"):
            self.wrapped.reference_count = 0

        self.wrapped.reference_count += 1

    @property
    @exception_bridge
    def name(self: "Self") -> "str":
        """str"""
        temp = pythonnet_property_get(self.wrapped, "Name")

        if temp is None:
            return ""

        return temp

    @name.setter
    @exception_bridge
    @enforce_parameter_types
    def name(self: "Self", value: "str") -> None:
        pythonnet_property_set(
            self.wrapped, "Name", str(value) if value is not None else ""
        )

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
    def dispose(self: "Self") -> None:
        """Method does not return."""
        pythonnet_method_call(self.wrapped, "Dispose")

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

    def __enter__(self: "Self") -> None:
        return self

    def __exit__(
        self: "Self", exception_type: "Any", exception_value: "Any", traceback: "Any"
    ) -> None:
        self.dispose()

    @property
    def cast_to(self: "Self") -> "_Cast_GearDesignComponent":
        """Cast to another type.

        Returns:
            _Cast_GearDesignComponent
        """
        return _Cast_GearDesignComponent(self)
