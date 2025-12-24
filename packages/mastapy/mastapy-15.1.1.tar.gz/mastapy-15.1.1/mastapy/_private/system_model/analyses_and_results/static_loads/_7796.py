"""ElectricMachineHarmonicLoadDataFromMASTA"""

from __future__ import annotations

from typing import TYPE_CHECKING, ClassVar

from mastapy._private._internal.dataclasses import extended_dataclass
from mastapy._private._internal.exception_bridge import exception_bridge
from mastapy._private._internal.exceptions import CastException
from mastapy._private._internal.python_net import (
    python_net_import,
    pythonnet_property_get,
)

from mastapy._private._internal import utility
from mastapy._private.system_model.analyses_and_results.static_loads import _7792

_ELECTRIC_MACHINE_HARMONIC_LOAD_DATA_FROM_MASTA = python_net_import(
    "SMT.MastaAPI.SystemModel.AnalysesAndResults.StaticLoads",
    "ElectricMachineHarmonicLoadDataFromMASTA",
)

if TYPE_CHECKING:
    from typing import Any, Type, TypeVar

    from mastapy._private.electric_machines.harmonic_load_data import (
        _1589,
        _1591,
        _1595,
    )

    Self = TypeVar("Self", bound="ElectricMachineHarmonicLoadDataFromMASTA")
    CastSelf = TypeVar(
        "CastSelf",
        bound="ElectricMachineHarmonicLoadDataFromMASTA._Cast_ElectricMachineHarmonicLoadDataFromMASTA",
    )


__docformat__ = "restructuredtext en"
__all__ = ("ElectricMachineHarmonicLoadDataFromMASTA",)


@extended_dataclass(frozen=True, slots=True, weakref_slot=True)
class _Cast_ElectricMachineHarmonicLoadDataFromMASTA:
    """Special nested class for casting ElectricMachineHarmonicLoadDataFromMASTA to subclasses."""

    __parent__: "ElectricMachineHarmonicLoadDataFromMASTA"

    @property
    def electric_machine_harmonic_load_data(
        self: "CastSelf",
    ) -> "_7792.ElectricMachineHarmonicLoadData":
        return self.__parent__._cast(_7792.ElectricMachineHarmonicLoadData)

    @property
    def electric_machine_harmonic_load_data_base(
        self: "CastSelf",
    ) -> "_1589.ElectricMachineHarmonicLoadDataBase":
        from mastapy._private.electric_machines.harmonic_load_data import _1589

        return self.__parent__._cast(_1589.ElectricMachineHarmonicLoadDataBase)

    @property
    def speed_dependent_harmonic_load_data(
        self: "CastSelf",
    ) -> "_1595.SpeedDependentHarmonicLoadData":
        from mastapy._private.electric_machines.harmonic_load_data import _1595

        return self.__parent__._cast(_1595.SpeedDependentHarmonicLoadData)

    @property
    def harmonic_load_data_base(self: "CastSelf") -> "_1591.HarmonicLoadDataBase":
        from mastapy._private.electric_machines.harmonic_load_data import _1591

        return self.__parent__._cast(_1591.HarmonicLoadDataBase)

    @property
    def electric_machine_harmonic_load_data_from_masta(
        self: "CastSelf",
    ) -> "ElectricMachineHarmonicLoadDataFromMASTA":
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
class ElectricMachineHarmonicLoadDataFromMASTA(_7792.ElectricMachineHarmonicLoadData):
    """ElectricMachineHarmonicLoadDataFromMASTA

    This is a mastapy class.
    """

    TYPE: ClassVar["Type"] = _ELECTRIC_MACHINE_HARMONIC_LOAD_DATA_FROM_MASTA

    wrapped: "Any"

    def __post_init__(self: "Self") -> None:
        """Override of the post initialisation magic method."""
        if not hasattr(self.wrapped, "reference_count"):
            self.wrapped.reference_count = 0

        self.wrapped.reference_count += 1

    @property
    @exception_bridge
    def electric_machine_name(self: "Self") -> "str":
        """str

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "ElectricMachineName")

        if temp is None:
            return ""

        return temp

    @property
    @exception_bridge
    def electric_machine_setup(self: "Self") -> "str":
        """str

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "ElectricMachineSetup")

        if temp is None:
            return ""

        return temp

    @property
    @exception_bridge
    def electromagnetic_load_case(self: "Self") -> "str":
        """str

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "ElectromagneticLoadCase")

        if temp is None:
            return ""

        return temp

    @property
    def cast_to(self: "Self") -> "_Cast_ElectricMachineHarmonicLoadDataFromMASTA":
        """Cast to another type.

        Returns:
            _Cast_ElectricMachineHarmonicLoadDataFromMASTA
        """
        return _Cast_ElectricMachineHarmonicLoadDataFromMASTA(self)
