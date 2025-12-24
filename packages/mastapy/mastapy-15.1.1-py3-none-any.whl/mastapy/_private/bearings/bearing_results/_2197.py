"""LoadedNonLinearBearingResults"""

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
from mastapy._private.bearings.bearing_results import _2189

_LOADED_NON_LINEAR_BEARING_RESULTS = python_net_import(
    "SMT.MastaAPI.Bearings.BearingResults", "LoadedNonLinearBearingResults"
)

if TYPE_CHECKING:
    from typing import Any, Type, TypeVar

    from mastapy._private.bearings import _2112
    from mastapy._private.bearings.bearing_results import _2191, _2192, _2193, _2194
    from mastapy._private.bearings.bearing_results.fluid_film import (
        _2366,
        _2367,
        _2368,
        _2369,
        _2371,
        _2374,
        _2375,
    )
    from mastapy._private.bearings.bearing_results.rolling import (
        _2225,
        _2228,
        _2231,
        _2236,
        _2239,
        _2244,
        _2247,
        _2251,
        _2254,
        _2259,
        _2263,
        _2266,
        _2272,
        _2276,
        _2279,
        _2283,
        _2286,
        _2291,
        _2294,
        _2297,
        _2300,
    )
    from mastapy._private.materials.efficiency import _407, _408

    Self = TypeVar("Self", bound="LoadedNonLinearBearingResults")
    CastSelf = TypeVar(
        "CastSelf",
        bound="LoadedNonLinearBearingResults._Cast_LoadedNonLinearBearingResults",
    )


__docformat__ = "restructuredtext en"
__all__ = ("LoadedNonLinearBearingResults",)


@extended_dataclass(frozen=True, slots=True, weakref_slot=True)
class _Cast_LoadedNonLinearBearingResults:
    """Special nested class for casting LoadedNonLinearBearingResults to subclasses."""

    __parent__: "LoadedNonLinearBearingResults"

    @property
    def loaded_bearing_results(self: "CastSelf") -> "_2189.LoadedBearingResults":
        return self.__parent__._cast(_2189.LoadedBearingResults)

    @property
    def bearing_load_case_results_lightweight(
        self: "CastSelf",
    ) -> "_2112.BearingLoadCaseResultsLightweight":
        from mastapy._private.bearings import _2112

        return self.__parent__._cast(_2112.BearingLoadCaseResultsLightweight)

    @property
    def loaded_concept_axial_clearance_bearing_results(
        self: "CastSelf",
    ) -> "_2191.LoadedConceptAxialClearanceBearingResults":
        from mastapy._private.bearings.bearing_results import _2191

        return self.__parent__._cast(_2191.LoadedConceptAxialClearanceBearingResults)

    @property
    def loaded_concept_clearance_bearing_results(
        self: "CastSelf",
    ) -> "_2192.LoadedConceptClearanceBearingResults":
        from mastapy._private.bearings.bearing_results import _2192

        return self.__parent__._cast(_2192.LoadedConceptClearanceBearingResults)

    @property
    def loaded_concept_radial_clearance_bearing_results(
        self: "CastSelf",
    ) -> "_2193.LoadedConceptRadialClearanceBearingResults":
        from mastapy._private.bearings.bearing_results import _2193

        return self.__parent__._cast(_2193.LoadedConceptRadialClearanceBearingResults)

    @property
    def loaded_detailed_bearing_results(
        self: "CastSelf",
    ) -> "_2194.LoadedDetailedBearingResults":
        from mastapy._private.bearings.bearing_results import _2194

        return self.__parent__._cast(_2194.LoadedDetailedBearingResults)

    @property
    def loaded_angular_contact_ball_bearing_results(
        self: "CastSelf",
    ) -> "_2225.LoadedAngularContactBallBearingResults":
        from mastapy._private.bearings.bearing_results.rolling import _2225

        return self.__parent__._cast(_2225.LoadedAngularContactBallBearingResults)

    @property
    def loaded_angular_contact_thrust_ball_bearing_results(
        self: "CastSelf",
    ) -> "_2228.LoadedAngularContactThrustBallBearingResults":
        from mastapy._private.bearings.bearing_results.rolling import _2228

        return self.__parent__._cast(_2228.LoadedAngularContactThrustBallBearingResults)

    @property
    def loaded_asymmetric_spherical_roller_bearing_results(
        self: "CastSelf",
    ) -> "_2231.LoadedAsymmetricSphericalRollerBearingResults":
        from mastapy._private.bearings.bearing_results.rolling import _2231

        return self.__parent__._cast(
            _2231.LoadedAsymmetricSphericalRollerBearingResults
        )

    @property
    def loaded_axial_thrust_cylindrical_roller_bearing_results(
        self: "CastSelf",
    ) -> "_2236.LoadedAxialThrustCylindricalRollerBearingResults":
        from mastapy._private.bearings.bearing_results.rolling import _2236

        return self.__parent__._cast(
            _2236.LoadedAxialThrustCylindricalRollerBearingResults
        )

    @property
    def loaded_axial_thrust_needle_roller_bearing_results(
        self: "CastSelf",
    ) -> "_2239.LoadedAxialThrustNeedleRollerBearingResults":
        from mastapy._private.bearings.bearing_results.rolling import _2239

        return self.__parent__._cast(_2239.LoadedAxialThrustNeedleRollerBearingResults)

    @property
    def loaded_ball_bearing_results(
        self: "CastSelf",
    ) -> "_2244.LoadedBallBearingResults":
        from mastapy._private.bearings.bearing_results.rolling import _2244

        return self.__parent__._cast(_2244.LoadedBallBearingResults)

    @property
    def loaded_crossed_roller_bearing_results(
        self: "CastSelf",
    ) -> "_2247.LoadedCrossedRollerBearingResults":
        from mastapy._private.bearings.bearing_results.rolling import _2247

        return self.__parent__._cast(_2247.LoadedCrossedRollerBearingResults)

    @property
    def loaded_cylindrical_roller_bearing_results(
        self: "CastSelf",
    ) -> "_2251.LoadedCylindricalRollerBearingResults":
        from mastapy._private.bearings.bearing_results.rolling import _2251

        return self.__parent__._cast(_2251.LoadedCylindricalRollerBearingResults)

    @property
    def loaded_deep_groove_ball_bearing_results(
        self: "CastSelf",
    ) -> "_2254.LoadedDeepGrooveBallBearingResults":
        from mastapy._private.bearings.bearing_results.rolling import _2254

        return self.__parent__._cast(_2254.LoadedDeepGrooveBallBearingResults)

    @property
    def loaded_four_point_contact_ball_bearing_results(
        self: "CastSelf",
    ) -> "_2259.LoadedFourPointContactBallBearingResults":
        from mastapy._private.bearings.bearing_results.rolling import _2259

        return self.__parent__._cast(_2259.LoadedFourPointContactBallBearingResults)

    @property
    def loaded_needle_roller_bearing_results(
        self: "CastSelf",
    ) -> "_2263.LoadedNeedleRollerBearingResults":
        from mastapy._private.bearings.bearing_results.rolling import _2263

        return self.__parent__._cast(_2263.LoadedNeedleRollerBearingResults)

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
    def loaded_self_aligning_ball_bearing_results(
        self: "CastSelf",
    ) -> "_2279.LoadedSelfAligningBallBearingResults":
        from mastapy._private.bearings.bearing_results.rolling import _2279

        return self.__parent__._cast(_2279.LoadedSelfAligningBallBearingResults)

    @property
    def loaded_spherical_roller_radial_bearing_results(
        self: "CastSelf",
    ) -> "_2283.LoadedSphericalRollerRadialBearingResults":
        from mastapy._private.bearings.bearing_results.rolling import _2283

        return self.__parent__._cast(_2283.LoadedSphericalRollerRadialBearingResults)

    @property
    def loaded_spherical_roller_thrust_bearing_results(
        self: "CastSelf",
    ) -> "_2286.LoadedSphericalRollerThrustBearingResults":
        from mastapy._private.bearings.bearing_results.rolling import _2286

        return self.__parent__._cast(_2286.LoadedSphericalRollerThrustBearingResults)

    @property
    def loaded_taper_roller_bearing_results(
        self: "CastSelf",
    ) -> "_2291.LoadedTaperRollerBearingResults":
        from mastapy._private.bearings.bearing_results.rolling import _2291

        return self.__parent__._cast(_2291.LoadedTaperRollerBearingResults)

    @property
    def loaded_three_point_contact_ball_bearing_results(
        self: "CastSelf",
    ) -> "_2294.LoadedThreePointContactBallBearingResults":
        from mastapy._private.bearings.bearing_results.rolling import _2294

        return self.__parent__._cast(_2294.LoadedThreePointContactBallBearingResults)

    @property
    def loaded_thrust_ball_bearing_results(
        self: "CastSelf",
    ) -> "_2297.LoadedThrustBallBearingResults":
        from mastapy._private.bearings.bearing_results.rolling import _2297

        return self.__parent__._cast(_2297.LoadedThrustBallBearingResults)

    @property
    def loaded_toroidal_roller_bearing_results(
        self: "CastSelf",
    ) -> "_2300.LoadedToroidalRollerBearingResults":
        from mastapy._private.bearings.bearing_results.rolling import _2300

        return self.__parent__._cast(_2300.LoadedToroidalRollerBearingResults)

    @property
    def loaded_fluid_film_bearing_results(
        self: "CastSelf",
    ) -> "_2366.LoadedFluidFilmBearingResults":
        from mastapy._private.bearings.bearing_results.fluid_film import _2366

        return self.__parent__._cast(_2366.LoadedFluidFilmBearingResults)

    @property
    def loaded_grease_filled_journal_bearing_results(
        self: "CastSelf",
    ) -> "_2367.LoadedGreaseFilledJournalBearingResults":
        from mastapy._private.bearings.bearing_results.fluid_film import _2367

        return self.__parent__._cast(_2367.LoadedGreaseFilledJournalBearingResults)

    @property
    def loaded_pad_fluid_film_bearing_results(
        self: "CastSelf",
    ) -> "_2368.LoadedPadFluidFilmBearingResults":
        from mastapy._private.bearings.bearing_results.fluid_film import _2368

        return self.__parent__._cast(_2368.LoadedPadFluidFilmBearingResults)

    @property
    def loaded_plain_journal_bearing_results(
        self: "CastSelf",
    ) -> "_2369.LoadedPlainJournalBearingResults":
        from mastapy._private.bearings.bearing_results.fluid_film import _2369

        return self.__parent__._cast(_2369.LoadedPlainJournalBearingResults)

    @property
    def loaded_plain_oil_fed_journal_bearing(
        self: "CastSelf",
    ) -> "_2371.LoadedPlainOilFedJournalBearing":
        from mastapy._private.bearings.bearing_results.fluid_film import _2371

        return self.__parent__._cast(_2371.LoadedPlainOilFedJournalBearing)

    @property
    def loaded_tilting_pad_journal_bearing_results(
        self: "CastSelf",
    ) -> "_2374.LoadedTiltingPadJournalBearingResults":
        from mastapy._private.bearings.bearing_results.fluid_film import _2374

        return self.__parent__._cast(_2374.LoadedTiltingPadJournalBearingResults)

    @property
    def loaded_tilting_pad_thrust_bearing_results(
        self: "CastSelf",
    ) -> "_2375.LoadedTiltingPadThrustBearingResults":
        from mastapy._private.bearings.bearing_results.fluid_film import _2375

        return self.__parent__._cast(_2375.LoadedTiltingPadThrustBearingResults)

    @property
    def loaded_non_linear_bearing_results(
        self: "CastSelf",
    ) -> "LoadedNonLinearBearingResults":
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
class LoadedNonLinearBearingResults(_2189.LoadedBearingResults):
    """LoadedNonLinearBearingResults

    This is a mastapy class.
    """

    TYPE: ClassVar["Type"] = _LOADED_NON_LINEAR_BEARING_RESULTS

    wrapped: "Any"

    def __post_init__(self: "Self") -> None:
        """Override of the post initialisation magic method."""
        if not hasattr(self.wrapped, "reference_count"):
            self.wrapped.reference_count = 0

        self.wrapped.reference_count += 1

    @property
    @exception_bridge
    def power_loss(self: "Self") -> "_407.PowerLoss":
        """mastapy.materials.efficiency.PowerLoss

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "PowerLoss")

        if temp is None:
            return None

        type_ = temp.GetType()
        return constructor.new(type_.Namespace, type_.Name)(temp)

    @property
    @exception_bridge
    def resistive_torque(self: "Self") -> "_408.ResistiveTorque":
        """mastapy.materials.efficiency.ResistiveTorque

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "ResistiveTorque")

        if temp is None:
            return None

        type_ = temp.GetType()
        return constructor.new(type_.Namespace, type_.Name)(temp)

    @property
    def cast_to(self: "Self") -> "_Cast_LoadedNonLinearBearingResults":
        """Cast to another type.

        Returns:
            _Cast_LoadedNonLinearBearingResults
        """
        return _Cast_LoadedNonLinearBearingResults(self)
