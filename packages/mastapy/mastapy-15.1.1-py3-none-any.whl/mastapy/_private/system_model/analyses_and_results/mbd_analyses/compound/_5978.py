"""StraightBevelDiffGearSetCompoundMultibodyDynamicsAnalysis"""

from __future__ import annotations

from typing import TYPE_CHECKING, ClassVar

from mastapy._private._internal.dataclasses import extended_dataclass
from mastapy._private._internal.exception_bridge import exception_bridge
from mastapy._private._internal.exceptions import CastException
from mastapy._private._internal.python_net import (
    python_net_import,
    pythonnet_property_get,
)

from mastapy._private._internal import constructor, conversion, utility
from mastapy._private.system_model.analyses_and_results.mbd_analyses.compound import (
    _5887,
)

_STRAIGHT_BEVEL_DIFF_GEAR_SET_COMPOUND_MULTIBODY_DYNAMICS_ANALYSIS = python_net_import(
    "SMT.MastaAPI.SystemModel.AnalysesAndResults.MBDAnalyses.Compound",
    "StraightBevelDiffGearSetCompoundMultibodyDynamicsAnalysis",
)

if TYPE_CHECKING:
    from typing import Any, List, Type, TypeVar

    from mastapy._private.system_model.analyses_and_results import _2943
    from mastapy._private.system_model.analyses_and_results.analysis_cases import (
        _7939,
        _7942,
    )
    from mastapy._private.system_model.analyses_and_results.mbd_analyses import _5837
    from mastapy._private.system_model.analyses_and_results.mbd_analyses.compound import (
        _5869,
        _5875,
        _5903,
        _5929,
        _5950,
        _5969,
        _5976,
        _5977,
    )
    from mastapy._private.system_model.part_model.gears import _2828

    Self = TypeVar(
        "Self", bound="StraightBevelDiffGearSetCompoundMultibodyDynamicsAnalysis"
    )
    CastSelf = TypeVar(
        "CastSelf",
        bound="StraightBevelDiffGearSetCompoundMultibodyDynamicsAnalysis._Cast_StraightBevelDiffGearSetCompoundMultibodyDynamicsAnalysis",
    )


__docformat__ = "restructuredtext en"
__all__ = ("StraightBevelDiffGearSetCompoundMultibodyDynamicsAnalysis",)


@extended_dataclass(frozen=True, slots=True, weakref_slot=True)
class _Cast_StraightBevelDiffGearSetCompoundMultibodyDynamicsAnalysis:
    """Special nested class for casting StraightBevelDiffGearSetCompoundMultibodyDynamicsAnalysis to subclasses."""

    __parent__: "StraightBevelDiffGearSetCompoundMultibodyDynamicsAnalysis"

    @property
    def bevel_gear_set_compound_multibody_dynamics_analysis(
        self: "CastSelf",
    ) -> "_5887.BevelGearSetCompoundMultibodyDynamicsAnalysis":
        return self.__parent__._cast(
            _5887.BevelGearSetCompoundMultibodyDynamicsAnalysis
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
    def gear_set_compound_multibody_dynamics_analysis(
        self: "CastSelf",
    ) -> "_5929.GearSetCompoundMultibodyDynamicsAnalysis":
        from mastapy._private.system_model.analyses_and_results.mbd_analyses.compound import (
            _5929,
        )

        return self.__parent__._cast(_5929.GearSetCompoundMultibodyDynamicsAnalysis)

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
    def part_compound_multibody_dynamics_analysis(
        self: "CastSelf",
    ) -> "_5950.PartCompoundMultibodyDynamicsAnalysis":
        from mastapy._private.system_model.analyses_and_results.mbd_analyses.compound import (
            _5950,
        )

        return self.__parent__._cast(_5950.PartCompoundMultibodyDynamicsAnalysis)

    @property
    def part_compound_analysis(self: "CastSelf") -> "_7942.PartCompoundAnalysis":
        from mastapy._private.system_model.analyses_and_results.analysis_cases import (
            _7942,
        )

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
    def straight_bevel_diff_gear_set_compound_multibody_dynamics_analysis(
        self: "CastSelf",
    ) -> "StraightBevelDiffGearSetCompoundMultibodyDynamicsAnalysis":
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
class StraightBevelDiffGearSetCompoundMultibodyDynamicsAnalysis(
    _5887.BevelGearSetCompoundMultibodyDynamicsAnalysis
):
    """StraightBevelDiffGearSetCompoundMultibodyDynamicsAnalysis

    This is a mastapy class.
    """

    TYPE: ClassVar["Type"] = (
        _STRAIGHT_BEVEL_DIFF_GEAR_SET_COMPOUND_MULTIBODY_DYNAMICS_ANALYSIS
    )

    wrapped: "Any"

    def __post_init__(self: "Self") -> None:
        """Override of the post initialisation magic method."""
        if not hasattr(self.wrapped, "reference_count"):
            self.wrapped.reference_count = 0

        self.wrapped.reference_count += 1

    @property
    @exception_bridge
    def component_design(self: "Self") -> "_2828.StraightBevelDiffGearSet":
        """mastapy.system_model.part_model.gears.StraightBevelDiffGearSet

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
    def assembly_design(self: "Self") -> "_2828.StraightBevelDiffGearSet":
        """mastapy.system_model.part_model.gears.StraightBevelDiffGearSet

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "AssemblyDesign")

        if temp is None:
            return None

        type_ = temp.GetType()
        return constructor.new(type_.Namespace, type_.Name)(temp)

    @property
    @exception_bridge
    def assembly_analysis_cases_ready(
        self: "Self",
    ) -> "List[_5837.StraightBevelDiffGearSetMultibodyDynamicsAnalysis]":
        """List[mastapy.system_model.analyses_and_results.mbd_analyses.StraightBevelDiffGearSetMultibodyDynamicsAnalysis]

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "AssemblyAnalysisCasesReady")

        if temp is None:
            return None

        value = conversion.pn_to_mp_objects_in_list(temp)

        if value is None:
            return None

        return value

    @property
    @exception_bridge
    def straight_bevel_diff_gears_compound_multibody_dynamics_analysis(
        self: "Self",
    ) -> "List[_5976.StraightBevelDiffGearCompoundMultibodyDynamicsAnalysis]":
        """List[mastapy.system_model.analyses_and_results.mbd_analyses.compound.StraightBevelDiffGearCompoundMultibodyDynamicsAnalysis]

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(
            self.wrapped, "StraightBevelDiffGearsCompoundMultibodyDynamicsAnalysis"
        )

        if temp is None:
            return None

        value = conversion.pn_to_mp_objects_in_list(temp)

        if value is None:
            return None

        return value

    @property
    @exception_bridge
    def straight_bevel_diff_meshes_compound_multibody_dynamics_analysis(
        self: "Self",
    ) -> "List[_5977.StraightBevelDiffGearMeshCompoundMultibodyDynamicsAnalysis]":
        """List[mastapy.system_model.analyses_and_results.mbd_analyses.compound.StraightBevelDiffGearMeshCompoundMultibodyDynamicsAnalysis]

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(
            self.wrapped, "StraightBevelDiffMeshesCompoundMultibodyDynamicsAnalysis"
        )

        if temp is None:
            return None

        value = conversion.pn_to_mp_objects_in_list(temp)

        if value is None:
            return None

        return value

    @property
    @exception_bridge
    def assembly_analysis_cases(
        self: "Self",
    ) -> "List[_5837.StraightBevelDiffGearSetMultibodyDynamicsAnalysis]":
        """List[mastapy.system_model.analyses_and_results.mbd_analyses.StraightBevelDiffGearSetMultibodyDynamicsAnalysis]

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "AssemblyAnalysisCases")

        if temp is None:
            return None

        value = conversion.pn_to_mp_objects_in_list(temp)

        if value is None:
            return None

        return value

    @property
    def cast_to(
        self: "Self",
    ) -> "_Cast_StraightBevelDiffGearSetCompoundMultibodyDynamicsAnalysis":
        """Cast to another type.

        Returns:
            _Cast_StraightBevelDiffGearSetCompoundMultibodyDynamicsAnalysis
        """
        return _Cast_StraightBevelDiffGearSetCompoundMultibodyDynamicsAnalysis(self)
