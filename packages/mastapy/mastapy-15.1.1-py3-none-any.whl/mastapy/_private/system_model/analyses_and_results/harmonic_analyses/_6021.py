"""AbstractPeriodicExcitationDetail"""

from __future__ import annotations

from typing import TYPE_CHECKING, ClassVar

from mastapy._private._internal.dataclasses import extended_dataclass
from mastapy._private._internal.exception_bridge import exception_bridge
from mastapy._private._internal.exceptions import CastException
from mastapy._private._internal.python_net import (
    python_net_import,
    pythonnet_property_get,
)

from mastapy._private import _0
from mastapy._private._internal import constructor, utility

_ABSTRACT_PERIODIC_EXCITATION_DETAIL = python_net_import(
    "SMT.MastaAPI.SystemModel.AnalysesAndResults.HarmonicAnalyses",
    "AbstractPeriodicExcitationDetail",
)

if TYPE_CHECKING:
    from typing import Any, Type, TypeVar

    from mastapy._private.electric_machines.harmonic_load_data import _1591
    from mastapy._private.system_model.analyses_and_results.harmonic_analyses import (
        _6076,
        _6077,
        _6078,
        _6079,
        _6080,
        _6081,
        _6082,
        _6083,
        _6084,
        _6085,
        _6086,
        _6087,
        _6097,
        _6099,
        _6100,
        _6102,
        _6140,
        _6157,
        _6183,
    )
    from mastapy._private.system_model.analyses_and_results.harmonic_analyses.transfer_path_analyses import (
        _6201,
    )

    Self = TypeVar("Self", bound="AbstractPeriodicExcitationDetail")
    CastSelf = TypeVar(
        "CastSelf",
        bound="AbstractPeriodicExcitationDetail._Cast_AbstractPeriodicExcitationDetail",
    )


__docformat__ = "restructuredtext en"
__all__ = ("AbstractPeriodicExcitationDetail",)


@extended_dataclass(frozen=True, slots=True, weakref_slot=True)
class _Cast_AbstractPeriodicExcitationDetail:
    """Special nested class for casting AbstractPeriodicExcitationDetail to subclasses."""

    __parent__: "AbstractPeriodicExcitationDetail"

    @property
    def electric_machine_periodic_excitation_detail(
        self: "CastSelf",
    ) -> "_6076.ElectricMachinePeriodicExcitationDetail":
        from mastapy._private.system_model.analyses_and_results.harmonic_analyses import (
            _6076,
        )

        return self.__parent__._cast(_6076.ElectricMachinePeriodicExcitationDetail)

    @property
    def electric_machine_rotor_x_force_periodic_excitation_detail(
        self: "CastSelf",
    ) -> "_6077.ElectricMachineRotorXForcePeriodicExcitationDetail":
        from mastapy._private.system_model.analyses_and_results.harmonic_analyses import (
            _6077,
        )

        return self.__parent__._cast(
            _6077.ElectricMachineRotorXForcePeriodicExcitationDetail
        )

    @property
    def electric_machine_rotor_x_moment_periodic_excitation_detail(
        self: "CastSelf",
    ) -> "_6078.ElectricMachineRotorXMomentPeriodicExcitationDetail":
        from mastapy._private.system_model.analyses_and_results.harmonic_analyses import (
            _6078,
        )

        return self.__parent__._cast(
            _6078.ElectricMachineRotorXMomentPeriodicExcitationDetail
        )

    @property
    def electric_machine_rotor_y_force_periodic_excitation_detail(
        self: "CastSelf",
    ) -> "_6079.ElectricMachineRotorYForcePeriodicExcitationDetail":
        from mastapy._private.system_model.analyses_and_results.harmonic_analyses import (
            _6079,
        )

        return self.__parent__._cast(
            _6079.ElectricMachineRotorYForcePeriodicExcitationDetail
        )

    @property
    def electric_machine_rotor_y_moment_periodic_excitation_detail(
        self: "CastSelf",
    ) -> "_6080.ElectricMachineRotorYMomentPeriodicExcitationDetail":
        from mastapy._private.system_model.analyses_and_results.harmonic_analyses import (
            _6080,
        )

        return self.__parent__._cast(
            _6080.ElectricMachineRotorYMomentPeriodicExcitationDetail
        )

    @property
    def electric_machine_rotor_z_force_periodic_excitation_detail(
        self: "CastSelf",
    ) -> "_6081.ElectricMachineRotorZForcePeriodicExcitationDetail":
        from mastapy._private.system_model.analyses_and_results.harmonic_analyses import (
            _6081,
        )

        return self.__parent__._cast(
            _6081.ElectricMachineRotorZForcePeriodicExcitationDetail
        )

    @property
    def electric_machine_stator_tooth_axial_loads_excitation_detail(
        self: "CastSelf",
    ) -> "_6082.ElectricMachineStatorToothAxialLoadsExcitationDetail":
        from mastapy._private.system_model.analyses_and_results.harmonic_analyses import (
            _6082,
        )

        return self.__parent__._cast(
            _6082.ElectricMachineStatorToothAxialLoadsExcitationDetail
        )

    @property
    def electric_machine_stator_tooth_loads_excitation_detail(
        self: "CastSelf",
    ) -> "_6083.ElectricMachineStatorToothLoadsExcitationDetail":
        from mastapy._private.system_model.analyses_and_results.harmonic_analyses import (
            _6083,
        )

        return self.__parent__._cast(
            _6083.ElectricMachineStatorToothLoadsExcitationDetail
        )

    @property
    def electric_machine_stator_tooth_moments_excitation_detail(
        self: "CastSelf",
    ) -> "_6084.ElectricMachineStatorToothMomentsExcitationDetail":
        from mastapy._private.system_model.analyses_and_results.harmonic_analyses import (
            _6084,
        )

        return self.__parent__._cast(
            _6084.ElectricMachineStatorToothMomentsExcitationDetail
        )

    @property
    def electric_machine_stator_tooth_radial_loads_excitation_detail(
        self: "CastSelf",
    ) -> "_6085.ElectricMachineStatorToothRadialLoadsExcitationDetail":
        from mastapy._private.system_model.analyses_and_results.harmonic_analyses import (
            _6085,
        )

        return self.__parent__._cast(
            _6085.ElectricMachineStatorToothRadialLoadsExcitationDetail
        )

    @property
    def electric_machine_stator_tooth_tangential_loads_excitation_detail(
        self: "CastSelf",
    ) -> "_6086.ElectricMachineStatorToothTangentialLoadsExcitationDetail":
        from mastapy._private.system_model.analyses_and_results.harmonic_analyses import (
            _6086,
        )

        return self.__parent__._cast(
            _6086.ElectricMachineStatorToothTangentialLoadsExcitationDetail
        )

    @property
    def electric_machine_torque_ripple_periodic_excitation_detail(
        self: "CastSelf",
    ) -> "_6087.ElectricMachineTorqueRipplePeriodicExcitationDetail":
        from mastapy._private.system_model.analyses_and_results.harmonic_analyses import (
            _6087,
        )

        return self.__parent__._cast(
            _6087.ElectricMachineTorqueRipplePeriodicExcitationDetail
        )

    @property
    def gear_mesh_excitation_detail(
        self: "CastSelf",
    ) -> "_6097.GearMeshExcitationDetail":
        from mastapy._private.system_model.analyses_and_results.harmonic_analyses import (
            _6097,
        )

        return self.__parent__._cast(_6097.GearMeshExcitationDetail)

    @property
    def gear_mesh_misalignment_excitation_detail(
        self: "CastSelf",
    ) -> "_6099.GearMeshMisalignmentExcitationDetail":
        from mastapy._private.system_model.analyses_and_results.harmonic_analyses import (
            _6099,
        )

        return self.__parent__._cast(_6099.GearMeshMisalignmentExcitationDetail)

    @property
    def gear_mesh_te_excitation_detail(
        self: "CastSelf",
    ) -> "_6100.GearMeshTEExcitationDetail":
        from mastapy._private.system_model.analyses_and_results.harmonic_analyses import (
            _6100,
        )

        return self.__parent__._cast(_6100.GearMeshTEExcitationDetail)

    @property
    def general_periodic_excitation_detail(
        self: "CastSelf",
    ) -> "_6102.GeneralPeriodicExcitationDetail":
        from mastapy._private.system_model.analyses_and_results.harmonic_analyses import (
            _6102,
        )

        return self.__parent__._cast(_6102.GeneralPeriodicExcitationDetail)

    @property
    def periodic_excitation_with_reference_shaft(
        self: "CastSelf",
    ) -> "_6140.PeriodicExcitationWithReferenceShaft":
        from mastapy._private.system_model.analyses_and_results.harmonic_analyses import (
            _6140,
        )

        return self.__parent__._cast(_6140.PeriodicExcitationWithReferenceShaft)

    @property
    def single_node_periodic_excitation_with_reference_shaft(
        self: "CastSelf",
    ) -> "_6157.SingleNodePeriodicExcitationWithReferenceShaft":
        from mastapy._private.system_model.analyses_and_results.harmonic_analyses import (
            _6157,
        )

        return self.__parent__._cast(
            _6157.SingleNodePeriodicExcitationWithReferenceShaft
        )

    @property
    def unbalanced_mass_excitation_detail(
        self: "CastSelf",
    ) -> "_6183.UnbalancedMassExcitationDetail":
        from mastapy._private.system_model.analyses_and_results.harmonic_analyses import (
            _6183,
        )

        return self.__parent__._cast(_6183.UnbalancedMassExcitationDetail)

    @property
    def transfer_path_node_single_degreeof_freedom_excitation(
        self: "CastSelf",
    ) -> "_6201.TransferPathNodeSingleDegreeofFreedomExcitation":
        from mastapy._private.system_model.analyses_and_results.harmonic_analyses.transfer_path_analyses import (
            _6201,
        )

        return self.__parent__._cast(
            _6201.TransferPathNodeSingleDegreeofFreedomExcitation
        )

    @property
    def abstract_periodic_excitation_detail(
        self: "CastSelf",
    ) -> "AbstractPeriodicExcitationDetail":
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
class AbstractPeriodicExcitationDetail(_0.APIBase):
    """AbstractPeriodicExcitationDetail

    This is a mastapy class.
    """

    TYPE: ClassVar["Type"] = _ABSTRACT_PERIODIC_EXCITATION_DETAIL

    wrapped: "Any"

    def __post_init__(self: "Self") -> None:
        """Override of the post initialisation magic method."""
        if not hasattr(self.wrapped, "reference_count"):
            self.wrapped.reference_count = 0

        self.wrapped.reference_count += 1

    @property
    @exception_bridge
    def harmonic_load_data(self: "Self") -> "_1591.HarmonicLoadDataBase":
        """mastapy.electric_machines.harmonic_load_data.HarmonicLoadDataBase

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "HarmonicLoadData")

        if temp is None:
            return None

        type_ = temp.GetType()
        return constructor.new(type_.Namespace, type_.Name)(temp)

    @property
    def cast_to(self: "Self") -> "_Cast_AbstractPeriodicExcitationDetail":
        """Cast to another type.

        Returns:
            _Cast_AbstractPeriodicExcitationDetail
        """
        return _Cast_AbstractPeriodicExcitationDetail(self)
