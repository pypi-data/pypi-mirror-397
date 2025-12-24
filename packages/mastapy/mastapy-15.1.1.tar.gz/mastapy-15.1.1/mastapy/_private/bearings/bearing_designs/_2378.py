"""DetailedBearing"""

from __future__ import annotations

from typing import TYPE_CHECKING, ClassVar

from mastapy._private._internal.dataclasses import extended_dataclass
from mastapy._private._internal.exceptions import CastException
from mastapy._private._internal.python_net import python_net_import

from mastapy._private._internal import utility
from mastapy._private.bearings.bearing_designs import _2381

_DETAILED_BEARING = python_net_import(
    "SMT.MastaAPI.Bearings.BearingDesigns", "DetailedBearing"
)

if TYPE_CHECKING:
    from typing import Any, Type, TypeVar

    from mastapy._private.bearings.bearing_designs import _2377
    from mastapy._private.bearings.bearing_designs.fluid_film import (
        _2435,
        _2437,
        _2439,
        _2441,
        _2442,
        _2443,
    )
    from mastapy._private.bearings.bearing_designs.rolling import (
        _2382,
        _2383,
        _2384,
        _2385,
        _2386,
        _2387,
        _2389,
        _2395,
        _2396,
        _2397,
        _2401,
        _2406,
        _2407,
        _2408,
        _2409,
        _2412,
        _2414,
        _2417,
        _2418,
        _2419,
        _2420,
        _2421,
        _2422,
    )

    Self = TypeVar("Self", bound="DetailedBearing")
    CastSelf = TypeVar("CastSelf", bound="DetailedBearing._Cast_DetailedBearing")


__docformat__ = "restructuredtext en"
__all__ = ("DetailedBearing",)


@extended_dataclass(frozen=True, slots=True, weakref_slot=True)
class _Cast_DetailedBearing:
    """Special nested class for casting DetailedBearing to subclasses."""

    __parent__: "DetailedBearing"

    @property
    def non_linear_bearing(self: "CastSelf") -> "_2381.NonLinearBearing":
        return self.__parent__._cast(_2381.NonLinearBearing)

    @property
    def bearing_design(self: "CastSelf") -> "_2377.BearingDesign":
        from mastapy._private.bearings.bearing_designs import _2377

        return self.__parent__._cast(_2377.BearingDesign)

    @property
    def angular_contact_ball_bearing(
        self: "CastSelf",
    ) -> "_2382.AngularContactBallBearing":
        from mastapy._private.bearings.bearing_designs.rolling import _2382

        return self.__parent__._cast(_2382.AngularContactBallBearing)

    @property
    def angular_contact_thrust_ball_bearing(
        self: "CastSelf",
    ) -> "_2383.AngularContactThrustBallBearing":
        from mastapy._private.bearings.bearing_designs.rolling import _2383

        return self.__parent__._cast(_2383.AngularContactThrustBallBearing)

    @property
    def asymmetric_spherical_roller_bearing(
        self: "CastSelf",
    ) -> "_2384.AsymmetricSphericalRollerBearing":
        from mastapy._private.bearings.bearing_designs.rolling import _2384

        return self.__parent__._cast(_2384.AsymmetricSphericalRollerBearing)

    @property
    def axial_thrust_cylindrical_roller_bearing(
        self: "CastSelf",
    ) -> "_2385.AxialThrustCylindricalRollerBearing":
        from mastapy._private.bearings.bearing_designs.rolling import _2385

        return self.__parent__._cast(_2385.AxialThrustCylindricalRollerBearing)

    @property
    def axial_thrust_needle_roller_bearing(
        self: "CastSelf",
    ) -> "_2386.AxialThrustNeedleRollerBearing":
        from mastapy._private.bearings.bearing_designs.rolling import _2386

        return self.__parent__._cast(_2386.AxialThrustNeedleRollerBearing)

    @property
    def ball_bearing(self: "CastSelf") -> "_2387.BallBearing":
        from mastapy._private.bearings.bearing_designs.rolling import _2387

        return self.__parent__._cast(_2387.BallBearing)

    @property
    def barrel_roller_bearing(self: "CastSelf") -> "_2389.BarrelRollerBearing":
        from mastapy._private.bearings.bearing_designs.rolling import _2389

        return self.__parent__._cast(_2389.BarrelRollerBearing)

    @property
    def crossed_roller_bearing(self: "CastSelf") -> "_2395.CrossedRollerBearing":
        from mastapy._private.bearings.bearing_designs.rolling import _2395

        return self.__parent__._cast(_2395.CrossedRollerBearing)

    @property
    def cylindrical_roller_bearing(
        self: "CastSelf",
    ) -> "_2396.CylindricalRollerBearing":
        from mastapy._private.bearings.bearing_designs.rolling import _2396

        return self.__parent__._cast(_2396.CylindricalRollerBearing)

    @property
    def deep_groove_ball_bearing(self: "CastSelf") -> "_2397.DeepGrooveBallBearing":
        from mastapy._private.bearings.bearing_designs.rolling import _2397

        return self.__parent__._cast(_2397.DeepGrooveBallBearing)

    @property
    def four_point_contact_ball_bearing(
        self: "CastSelf",
    ) -> "_2401.FourPointContactBallBearing":
        from mastapy._private.bearings.bearing_designs.rolling import _2401

        return self.__parent__._cast(_2401.FourPointContactBallBearing)

    @property
    def multi_point_contact_ball_bearing(
        self: "CastSelf",
    ) -> "_2406.MultiPointContactBallBearing":
        from mastapy._private.bearings.bearing_designs.rolling import _2406

        return self.__parent__._cast(_2406.MultiPointContactBallBearing)

    @property
    def needle_roller_bearing(self: "CastSelf") -> "_2407.NeedleRollerBearing":
        from mastapy._private.bearings.bearing_designs.rolling import _2407

        return self.__parent__._cast(_2407.NeedleRollerBearing)

    @property
    def non_barrel_roller_bearing(self: "CastSelf") -> "_2408.NonBarrelRollerBearing":
        from mastapy._private.bearings.bearing_designs.rolling import _2408

        return self.__parent__._cast(_2408.NonBarrelRollerBearing)

    @property
    def roller_bearing(self: "CastSelf") -> "_2409.RollerBearing":
        from mastapy._private.bearings.bearing_designs.rolling import _2409

        return self.__parent__._cast(_2409.RollerBearing)

    @property
    def rolling_bearing(self: "CastSelf") -> "_2412.RollingBearing":
        from mastapy._private.bearings.bearing_designs.rolling import _2412

        return self.__parent__._cast(_2412.RollingBearing)

    @property
    def self_aligning_ball_bearing(self: "CastSelf") -> "_2414.SelfAligningBallBearing":
        from mastapy._private.bearings.bearing_designs.rolling import _2414

        return self.__parent__._cast(_2414.SelfAligningBallBearing)

    @property
    def spherical_roller_bearing(self: "CastSelf") -> "_2417.SphericalRollerBearing":
        from mastapy._private.bearings.bearing_designs.rolling import _2417

        return self.__parent__._cast(_2417.SphericalRollerBearing)

    @property
    def spherical_roller_thrust_bearing(
        self: "CastSelf",
    ) -> "_2418.SphericalRollerThrustBearing":
        from mastapy._private.bearings.bearing_designs.rolling import _2418

        return self.__parent__._cast(_2418.SphericalRollerThrustBearing)

    @property
    def taper_roller_bearing(self: "CastSelf") -> "_2419.TaperRollerBearing":
        from mastapy._private.bearings.bearing_designs.rolling import _2419

        return self.__parent__._cast(_2419.TaperRollerBearing)

    @property
    def three_point_contact_ball_bearing(
        self: "CastSelf",
    ) -> "_2420.ThreePointContactBallBearing":
        from mastapy._private.bearings.bearing_designs.rolling import _2420

        return self.__parent__._cast(_2420.ThreePointContactBallBearing)

    @property
    def thrust_ball_bearing(self: "CastSelf") -> "_2421.ThrustBallBearing":
        from mastapy._private.bearings.bearing_designs.rolling import _2421

        return self.__parent__._cast(_2421.ThrustBallBearing)

    @property
    def toroidal_roller_bearing(self: "CastSelf") -> "_2422.ToroidalRollerBearing":
        from mastapy._private.bearings.bearing_designs.rolling import _2422

        return self.__parent__._cast(_2422.ToroidalRollerBearing)

    @property
    def pad_fluid_film_bearing(self: "CastSelf") -> "_2435.PadFluidFilmBearing":
        from mastapy._private.bearings.bearing_designs.fluid_film import _2435

        return self.__parent__._cast(_2435.PadFluidFilmBearing)

    @property
    def plain_grease_filled_journal_bearing(
        self: "CastSelf",
    ) -> "_2437.PlainGreaseFilledJournalBearing":
        from mastapy._private.bearings.bearing_designs.fluid_film import _2437

        return self.__parent__._cast(_2437.PlainGreaseFilledJournalBearing)

    @property
    def plain_journal_bearing(self: "CastSelf") -> "_2439.PlainJournalBearing":
        from mastapy._private.bearings.bearing_designs.fluid_film import _2439

        return self.__parent__._cast(_2439.PlainJournalBearing)

    @property
    def plain_oil_fed_journal_bearing(
        self: "CastSelf",
    ) -> "_2441.PlainOilFedJournalBearing":
        from mastapy._private.bearings.bearing_designs.fluid_film import _2441

        return self.__parent__._cast(_2441.PlainOilFedJournalBearing)

    @property
    def tilting_pad_journal_bearing(
        self: "CastSelf",
    ) -> "_2442.TiltingPadJournalBearing":
        from mastapy._private.bearings.bearing_designs.fluid_film import _2442

        return self.__parent__._cast(_2442.TiltingPadJournalBearing)

    @property
    def tilting_pad_thrust_bearing(self: "CastSelf") -> "_2443.TiltingPadThrustBearing":
        from mastapy._private.bearings.bearing_designs.fluid_film import _2443

        return self.__parent__._cast(_2443.TiltingPadThrustBearing)

    @property
    def detailed_bearing(self: "CastSelf") -> "DetailedBearing":
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
class DetailedBearing(_2381.NonLinearBearing):
    """DetailedBearing

    This is a mastapy class.
    """

    TYPE: ClassVar["Type"] = _DETAILED_BEARING

    wrapped: "Any"

    def __post_init__(self: "Self") -> None:
        """Override of the post initialisation magic method."""
        if not hasattr(self.wrapped, "reference_count"):
            self.wrapped.reference_count = 0

        self.wrapped.reference_count += 1

    @property
    def cast_to(self: "Self") -> "_Cast_DetailedBearing":
        """Cast to another type.

        Returns:
            _Cast_DetailedBearing
        """
        return _Cast_DetailedBearing(self)
