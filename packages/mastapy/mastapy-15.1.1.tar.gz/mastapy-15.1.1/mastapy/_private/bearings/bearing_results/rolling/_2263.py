"""LoadedNeedleRollerBearingResults"""

from __future__ import annotations

from typing import TYPE_CHECKING, ClassVar

from mastapy._private._internal.dataclasses import extended_dataclass
from mastapy._private._internal.exceptions import CastException
from mastapy._private._internal.python_net import python_net_import

from mastapy._private._internal import utility
from mastapy._private.bearings.bearing_results.rolling import _2251

_LOADED_NEEDLE_ROLLER_BEARING_RESULTS = python_net_import(
    "SMT.MastaAPI.Bearings.BearingResults.Rolling", "LoadedNeedleRollerBearingResults"
)

if TYPE_CHECKING:
    from typing import Any, Type, TypeVar

    from mastapy._private.bearings import _2112
    from mastapy._private.bearings.bearing_results import _2189, _2194, _2197
    from mastapy._private.bearings.bearing_results.rolling import _2266, _2272, _2276

    Self = TypeVar("Self", bound="LoadedNeedleRollerBearingResults")
    CastSelf = TypeVar(
        "CastSelf",
        bound="LoadedNeedleRollerBearingResults._Cast_LoadedNeedleRollerBearingResults",
    )


__docformat__ = "restructuredtext en"
__all__ = ("LoadedNeedleRollerBearingResults",)


@extended_dataclass(frozen=True, slots=True, weakref_slot=True)
class _Cast_LoadedNeedleRollerBearingResults:
    """Special nested class for casting LoadedNeedleRollerBearingResults to subclasses."""

    __parent__: "LoadedNeedleRollerBearingResults"

    @property
    def loaded_cylindrical_roller_bearing_results(
        self: "CastSelf",
    ) -> "_2251.LoadedCylindricalRollerBearingResults":
        return self.__parent__._cast(_2251.LoadedCylindricalRollerBearingResults)

    @property
    def loaded_non_barrel_roller_bearing_results(
        self: "CastSelf",
    ) -> "_2266.LoadedNonBarrelRollerBearingResults":
        from mastapy._private.bearings.bearing_results.rolling import _2266

        return self.__parent__._cast(_2266.LoadedNonBarrelRollerBearingResults)

    @property
    def loaded_roller_bearing_results(
        self: "CastSelf",
    ) -> "_2272.LoadedRollerBearingResults":
        from mastapy._private.bearings.bearing_results.rolling import _2272

        return self.__parent__._cast(_2272.LoadedRollerBearingResults)

    @property
    def loaded_rolling_bearing_results(
        self: "CastSelf",
    ) -> "_2276.LoadedRollingBearingResults":
        from mastapy._private.bearings.bearing_results.rolling import _2276

        return self.__parent__._cast(_2276.LoadedRollingBearingResults)

    @property
    def loaded_detailed_bearing_results(
        self: "CastSelf",
    ) -> "_2194.LoadedDetailedBearingResults":
        from mastapy._private.bearings.bearing_results import _2194

        return self.__parent__._cast(_2194.LoadedDetailedBearingResults)

    @property
    def loaded_non_linear_bearing_results(
        self: "CastSelf",
    ) -> "_2197.LoadedNonLinearBearingResults":
        from mastapy._private.bearings.bearing_results import _2197

        return self.__parent__._cast(_2197.LoadedNonLinearBearingResults)

    @property
    def loaded_bearing_results(self: "CastSelf") -> "_2189.LoadedBearingResults":
        from mastapy._private.bearings.bearing_results import _2189

        return self.__parent__._cast(_2189.LoadedBearingResults)

    @property
    def bearing_load_case_results_lightweight(
        self: "CastSelf",
    ) -> "_2112.BearingLoadCaseResultsLightweight":
        from mastapy._private.bearings import _2112

        return self.__parent__._cast(_2112.BearingLoadCaseResultsLightweight)

    @property
    def loaded_needle_roller_bearing_results(
        self: "CastSelf",
    ) -> "LoadedNeedleRollerBearingResults":
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
class LoadedNeedleRollerBearingResults(_2251.LoadedCylindricalRollerBearingResults):
    """LoadedNeedleRollerBearingResults

    This is a mastapy class.
    """

    TYPE: ClassVar["Type"] = _LOADED_NEEDLE_ROLLER_BEARING_RESULTS

    wrapped: "Any"

    def __post_init__(self: "Self") -> None:
        """Override of the post initialisation magic method."""
        if not hasattr(self.wrapped, "reference_count"):
            self.wrapped.reference_count = 0

        self.wrapped.reference_count += 1

    @property
    def cast_to(self: "Self") -> "_Cast_LoadedNeedleRollerBearingResults":
        """Cast to another type.

        Returns:
            _Cast_LoadedNeedleRollerBearingResults
        """
        return _Cast_LoadedNeedleRollerBearingResults(self)
