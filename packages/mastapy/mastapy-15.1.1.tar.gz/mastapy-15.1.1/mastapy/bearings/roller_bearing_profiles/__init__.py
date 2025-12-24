"""Subpackage."""

from typing import TYPE_CHECKING as __tc

if __tc:
    from mastapy._private.bearings.roller_bearing_profiles._2164 import ProfileDataToUse
    from mastapy._private.bearings.roller_bearing_profiles._2165 import ProfileSet
    from mastapy._private.bearings.roller_bearing_profiles._2166 import ProfileToFit
    from mastapy._private.bearings.roller_bearing_profiles._2167 import (
        RollerBearingConicalProfile,
    )
    from mastapy._private.bearings.roller_bearing_profiles._2168 import (
        RollerBearingCrownedProfile,
    )
    from mastapy._private.bearings.roller_bearing_profiles._2169 import (
        RollerBearingDinLundbergProfile,
    )
    from mastapy._private.bearings.roller_bearing_profiles._2170 import (
        RollerBearingFlatProfile,
    )
    from mastapy._private.bearings.roller_bearing_profiles._2171 import (
        RollerBearingFujiwaraKawaseProfile,
    )
    from mastapy._private.bearings.roller_bearing_profiles._2172 import (
        RollerBearingJohnsGoharProfile,
    )
    from mastapy._private.bearings.roller_bearing_profiles._2173 import (
        RollerBearingLoadDependentProfile,
    )
    from mastapy._private.bearings.roller_bearing_profiles._2174 import (
        RollerBearingLundbergProfile,
    )
    from mastapy._private.bearings.roller_bearing_profiles._2175 import (
        RollerBearingProfile,
    )
    from mastapy._private.bearings.roller_bearing_profiles._2176 import (
        RollerBearingTangentialCrownedProfile,
    )
    from mastapy._private.bearings.roller_bearing_profiles._2177 import (
        RollerBearingUserSpecifiedProfile,
    )
    from mastapy._private.bearings.roller_bearing_profiles._2178 import (
        RollerRaceProfilePoint,
    )
    from mastapy._private.bearings.roller_bearing_profiles._2179 import (
        UserSpecifiedProfilePoint,
    )
    from mastapy._private.bearings.roller_bearing_profiles._2180 import (
        UserSpecifiedRollerRaceProfilePoint,
    )
else:
    import sys as __sys

    from lazy_imports import LazyImporter as __LazyImporter

    __import_structure = {
        "_private.bearings.roller_bearing_profiles._2164": ["ProfileDataToUse"],
        "_private.bearings.roller_bearing_profiles._2165": ["ProfileSet"],
        "_private.bearings.roller_bearing_profiles._2166": ["ProfileToFit"],
        "_private.bearings.roller_bearing_profiles._2167": [
            "RollerBearingConicalProfile"
        ],
        "_private.bearings.roller_bearing_profiles._2168": [
            "RollerBearingCrownedProfile"
        ],
        "_private.bearings.roller_bearing_profiles._2169": [
            "RollerBearingDinLundbergProfile"
        ],
        "_private.bearings.roller_bearing_profiles._2170": ["RollerBearingFlatProfile"],
        "_private.bearings.roller_bearing_profiles._2171": [
            "RollerBearingFujiwaraKawaseProfile"
        ],
        "_private.bearings.roller_bearing_profiles._2172": [
            "RollerBearingJohnsGoharProfile"
        ],
        "_private.bearings.roller_bearing_profiles._2173": [
            "RollerBearingLoadDependentProfile"
        ],
        "_private.bearings.roller_bearing_profiles._2174": [
            "RollerBearingLundbergProfile"
        ],
        "_private.bearings.roller_bearing_profiles._2175": ["RollerBearingProfile"],
        "_private.bearings.roller_bearing_profiles._2176": [
            "RollerBearingTangentialCrownedProfile"
        ],
        "_private.bearings.roller_bearing_profiles._2177": [
            "RollerBearingUserSpecifiedProfile"
        ],
        "_private.bearings.roller_bearing_profiles._2178": ["RollerRaceProfilePoint"],
        "_private.bearings.roller_bearing_profiles._2179": [
            "UserSpecifiedProfilePoint"
        ],
        "_private.bearings.roller_bearing_profiles._2180": [
            "UserSpecifiedRollerRaceProfilePoint"
        ],
    }

    __sys.modules[__name__] = __LazyImporter(
        "mastapy",
        globals()["__file__"],
        __import_structure,
    )

__all__ = (
    "ProfileDataToUse",
    "ProfileSet",
    "ProfileToFit",
    "RollerBearingConicalProfile",
    "RollerBearingCrownedProfile",
    "RollerBearingDinLundbergProfile",
    "RollerBearingFlatProfile",
    "RollerBearingFujiwaraKawaseProfile",
    "RollerBearingJohnsGoharProfile",
    "RollerBearingLoadDependentProfile",
    "RollerBearingLundbergProfile",
    "RollerBearingProfile",
    "RollerBearingTangentialCrownedProfile",
    "RollerBearingUserSpecifiedProfile",
    "RollerRaceProfilePoint",
    "UserSpecifiedProfilePoint",
    "UserSpecifiedRollerRaceProfilePoint",
)
