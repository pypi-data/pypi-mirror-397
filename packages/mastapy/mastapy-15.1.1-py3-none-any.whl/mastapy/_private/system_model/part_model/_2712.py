"""BoltedJoint"""

from __future__ import annotations

from typing import TYPE_CHECKING, ClassVar

from mastapy._private._internal.dataclasses import extended_dataclass
from mastapy._private._internal.exception_bridge import exception_bridge
from mastapy._private._internal.exceptions import CastException
from mastapy._private._internal.python_net import (
    python_net_import,
    pythonnet_property_get,
)

from mastapy._private._internal import constructor, utility
from mastapy._private.system_model.part_model import _2752

_BOLTED_JOINT = python_net_import("SMT.MastaAPI.SystemModel.PartModel", "BoltedJoint")

if TYPE_CHECKING:
    from typing import Any, Type, TypeVar

    from mastapy._private.bolts import _1690
    from mastapy._private.system_model import _2451
    from mastapy._private.system_model.part_model import _2703, _2742

    Self = TypeVar("Self", bound="BoltedJoint")
    CastSelf = TypeVar("CastSelf", bound="BoltedJoint._Cast_BoltedJoint")


__docformat__ = "restructuredtext en"
__all__ = ("BoltedJoint",)


@extended_dataclass(frozen=True, slots=True, weakref_slot=True)
class _Cast_BoltedJoint:
    """Special nested class for casting BoltedJoint to subclasses."""

    __parent__: "BoltedJoint"

    @property
    def specialised_assembly(self: "CastSelf") -> "_2752.SpecialisedAssembly":
        return self.__parent__._cast(_2752.SpecialisedAssembly)

    @property
    def abstract_assembly(self: "CastSelf") -> "_2703.AbstractAssembly":
        from mastapy._private.system_model.part_model import _2703

        return self.__parent__._cast(_2703.AbstractAssembly)

    @property
    def part(self: "CastSelf") -> "_2742.Part":
        from mastapy._private.system_model.part_model import _2742

        return self.__parent__._cast(_2742.Part)

    @property
    def design_entity(self: "CastSelf") -> "_2451.DesignEntity":
        from mastapy._private.system_model import _2451

        return self.__parent__._cast(_2451.DesignEntity)

    @property
    def bolted_joint(self: "CastSelf") -> "BoltedJoint":
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
class BoltedJoint(_2752.SpecialisedAssembly):
    """BoltedJoint

    This is a mastapy class.
    """

    TYPE: ClassVar["Type"] = _BOLTED_JOINT

    wrapped: "Any"

    def __post_init__(self: "Self") -> None:
        """Override of the post initialisation magic method."""
        if not hasattr(self.wrapped, "reference_count"):
            self.wrapped.reference_count = 0

        self.wrapped.reference_count += 1

    @property
    @exception_bridge
    def detailed_bolted_joint(self: "Self") -> "_1690.DetailedBoltedJointDesign":
        """mastapy.bolts.DetailedBoltedJointDesign

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "DetailedBoltedJoint")

        if temp is None:
            return None

        type_ = temp.GetType()
        return constructor.new(type_.Namespace, type_.Name)(temp)

    @property
    def cast_to(self: "Self") -> "_Cast_BoltedJoint":
        """Cast to another type.

        Returns:
            _Cast_BoltedJoint
        """
        return _Cast_BoltedJoint(self)
