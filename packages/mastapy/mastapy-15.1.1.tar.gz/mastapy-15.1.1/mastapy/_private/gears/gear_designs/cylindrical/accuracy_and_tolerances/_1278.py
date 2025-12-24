"""CylindricalAccuracyGrader"""

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
from mastapy._private.gears.gear_designs.cylindrical.accuracy_and_tolerances import (
    _1279,
)

_CYLINDRICAL_ACCURACY_GRADER = python_net_import(
    "SMT.MastaAPI.Gears.GearDesigns.Cylindrical.AccuracyAndTolerances",
    "CylindricalAccuracyGrader",
)

if TYPE_CHECKING:
    from typing import Any, Type, TypeVar

    from mastapy._private.gears.gear_designs.cylindrical.accuracy_and_tolerances import (
        _1273,
        _1274,
        _1276,
        _1277,
        _1280,
        _1281,
        _1286,
        _1287,
        _1288,
    )

    Self = TypeVar("Self", bound="CylindricalAccuracyGrader")
    CastSelf = TypeVar(
        "CastSelf", bound="CylindricalAccuracyGrader._Cast_CylindricalAccuracyGrader"
    )


__docformat__ = "restructuredtext en"
__all__ = ("CylindricalAccuracyGrader",)


@extended_dataclass(frozen=True, slots=True, weakref_slot=True)
class _Cast_CylindricalAccuracyGrader:
    """Special nested class for casting CylindricalAccuracyGrader to subclasses."""

    __parent__: "CylindricalAccuracyGrader"

    @property
    def cylindrical_accuracy_grader_base(
        self: "CastSelf",
    ) -> "_1279.CylindricalAccuracyGraderBase":
        return self.__parent__._cast(_1279.CylindricalAccuracyGraderBase)

    @property
    def agma2000a88_accuracy_grader(
        self: "CastSelf",
    ) -> "_1273.AGMA2000A88AccuracyGrader":
        from mastapy._private.gears.gear_designs.cylindrical.accuracy_and_tolerances import (
            _1273,
        )

        return self.__parent__._cast(_1273.AGMA2000A88AccuracyGrader)

    @property
    def agma20151a01_accuracy_grader(
        self: "CastSelf",
    ) -> "_1274.AGMA20151A01AccuracyGrader":
        from mastapy._private.gears.gear_designs.cylindrical.accuracy_and_tolerances import (
            _1274,
        )

        return self.__parent__._cast(_1274.AGMA20151A01AccuracyGrader)

    @property
    def agmaiso13281b14_accuracy_grader(
        self: "CastSelf",
    ) -> "_1276.AGMAISO13281B14AccuracyGrader":
        from mastapy._private.gears.gear_designs.cylindrical.accuracy_and_tolerances import (
            _1276,
        )

        return self.__parent__._cast(_1276.AGMAISO13281B14AccuracyGrader)

    @property
    def customer_102agma2000_accuracy_grader(
        self: "CastSelf",
    ) -> "_1277.Customer102AGMA2000AccuracyGrader":
        from mastapy._private.gears.gear_designs.cylindrical.accuracy_and_tolerances import (
            _1277,
        )

        return self.__parent__._cast(_1277.Customer102AGMA2000AccuracyGrader)

    @property
    def cylindrical_accuracy_grader_with_profile_form_and_slope(
        self: "CastSelf",
    ) -> "_1280.CylindricalAccuracyGraderWithProfileFormAndSlope":
        from mastapy._private.gears.gear_designs.cylindrical.accuracy_and_tolerances import (
            _1280,
        )

        return self.__parent__._cast(
            _1280.CylindricalAccuracyGraderWithProfileFormAndSlope
        )

    @property
    def iso132811995_accuracy_grader(
        self: "CastSelf",
    ) -> "_1286.ISO132811995AccuracyGrader":
        from mastapy._private.gears.gear_designs.cylindrical.accuracy_and_tolerances import (
            _1286,
        )

        return self.__parent__._cast(_1286.ISO132811995AccuracyGrader)

    @property
    def iso132812013_accuracy_grader(
        self: "CastSelf",
    ) -> "_1287.ISO132812013AccuracyGrader":
        from mastapy._private.gears.gear_designs.cylindrical.accuracy_and_tolerances import (
            _1287,
        )

        return self.__parent__._cast(_1287.ISO132812013AccuracyGrader)

    @property
    def iso1328_accuracy_grader_common(
        self: "CastSelf",
    ) -> "_1288.ISO1328AccuracyGraderCommon":
        from mastapy._private.gears.gear_designs.cylindrical.accuracy_and_tolerances import (
            _1288,
        )

        return self.__parent__._cast(_1288.ISO1328AccuracyGraderCommon)

    @property
    def cylindrical_accuracy_grader(self: "CastSelf") -> "CylindricalAccuracyGrader":
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
class CylindricalAccuracyGrader(_1279.CylindricalAccuracyGraderBase):
    """CylindricalAccuracyGrader

    This is a mastapy class.
    """

    TYPE: ClassVar["Type"] = _CYLINDRICAL_ACCURACY_GRADER

    wrapped: "Any"

    def __post_init__(self: "Self") -> None:
        """Override of the post initialisation magic method."""
        if not hasattr(self.wrapped, "reference_count"):
            self.wrapped.reference_count = 0

        self.wrapped.reference_count += 1

    @property
    @exception_bridge
    def tolerance_standard(self: "Self") -> "str":
        """str

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "ToleranceStandard")

        if temp is None:
            return ""

        return temp

    @property
    @exception_bridge
    def accuracy_grades(self: "Self") -> "_1281.CylindricalAccuracyGrades":
        """mastapy.gears.gear_designs.cylindrical.accuracy_and_tolerances.CylindricalAccuracyGrades

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "AccuracyGrades")

        if temp is None:
            return None

        type_ = temp.GetType()
        return constructor.new(type_.Namespace, type_.Name)(temp)

    @property
    def cast_to(self: "Self") -> "_Cast_CylindricalAccuracyGrader":
        """Cast to another type.

        Returns:
            _Cast_CylindricalAccuracyGrader
        """
        return _Cast_CylindricalAccuracyGrader(self)
