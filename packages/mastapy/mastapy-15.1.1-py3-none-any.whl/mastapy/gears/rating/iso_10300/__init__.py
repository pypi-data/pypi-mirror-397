"""Subpackage."""

from typing import TYPE_CHECKING as __tc

if __tc:
    from mastapy._private.gears.rating.iso_10300._533 import (
        GeneralLoadFactorCalculationMethod,
    )
    from mastapy._private.gears.rating.iso_10300._534 import Iso10300FinishingMethods
    from mastapy._private.gears.rating.iso_10300._535 import (
        ISO10300MeshSingleFlankRating,
    )
    from mastapy._private.gears.rating.iso_10300._536 import (
        ISO10300MeshSingleFlankRatingBevelMethodB2,
    )
    from mastapy._private.gears.rating.iso_10300._537 import (
        ISO10300MeshSingleFlankRatingHypoidMethodB2,
    )
    from mastapy._private.gears.rating.iso_10300._538 import (
        ISO10300MeshSingleFlankRatingMethodB1,
    )
    from mastapy._private.gears.rating.iso_10300._539 import (
        ISO10300MeshSingleFlankRatingMethodB2,
    )
    from mastapy._private.gears.rating.iso_10300._540 import ISO10300RateableMesh
    from mastapy._private.gears.rating.iso_10300._541 import ISO10300RatingMethod
    from mastapy._private.gears.rating.iso_10300._542 import ISO10300SingleFlankRating
    from mastapy._private.gears.rating.iso_10300._543 import (
        ISO10300SingleFlankRatingBevelMethodB2,
    )
    from mastapy._private.gears.rating.iso_10300._544 import (
        ISO10300SingleFlankRatingHypoidMethodB2,
    )
    from mastapy._private.gears.rating.iso_10300._545 import (
        ISO10300SingleFlankRatingMethodB1,
    )
    from mastapy._private.gears.rating.iso_10300._546 import (
        ISO10300SingleFlankRatingMethodB2,
    )
    from mastapy._private.gears.rating.iso_10300._547 import (
        MountingConditionsOfPinionAndWheel,
    )
    from mastapy._private.gears.rating.iso_10300._548 import (
        PittingFactorCalculationMethod,
    )
    from mastapy._private.gears.rating.iso_10300._549 import ProfileCrowningSetting
    from mastapy._private.gears.rating.iso_10300._550 import (
        VerificationOfContactPattern,
    )
else:
    import sys as __sys

    from lazy_imports import LazyImporter as __LazyImporter

    __import_structure = {
        "_private.gears.rating.iso_10300._533": ["GeneralLoadFactorCalculationMethod"],
        "_private.gears.rating.iso_10300._534": ["Iso10300FinishingMethods"],
        "_private.gears.rating.iso_10300._535": ["ISO10300MeshSingleFlankRating"],
        "_private.gears.rating.iso_10300._536": [
            "ISO10300MeshSingleFlankRatingBevelMethodB2"
        ],
        "_private.gears.rating.iso_10300._537": [
            "ISO10300MeshSingleFlankRatingHypoidMethodB2"
        ],
        "_private.gears.rating.iso_10300._538": [
            "ISO10300MeshSingleFlankRatingMethodB1"
        ],
        "_private.gears.rating.iso_10300._539": [
            "ISO10300MeshSingleFlankRatingMethodB2"
        ],
        "_private.gears.rating.iso_10300._540": ["ISO10300RateableMesh"],
        "_private.gears.rating.iso_10300._541": ["ISO10300RatingMethod"],
        "_private.gears.rating.iso_10300._542": ["ISO10300SingleFlankRating"],
        "_private.gears.rating.iso_10300._543": [
            "ISO10300SingleFlankRatingBevelMethodB2"
        ],
        "_private.gears.rating.iso_10300._544": [
            "ISO10300SingleFlankRatingHypoidMethodB2"
        ],
        "_private.gears.rating.iso_10300._545": ["ISO10300SingleFlankRatingMethodB1"],
        "_private.gears.rating.iso_10300._546": ["ISO10300SingleFlankRatingMethodB2"],
        "_private.gears.rating.iso_10300._547": ["MountingConditionsOfPinionAndWheel"],
        "_private.gears.rating.iso_10300._548": ["PittingFactorCalculationMethod"],
        "_private.gears.rating.iso_10300._549": ["ProfileCrowningSetting"],
        "_private.gears.rating.iso_10300._550": ["VerificationOfContactPattern"],
    }

    __sys.modules[__name__] = __LazyImporter(
        "mastapy",
        globals()["__file__"],
        __import_structure,
    )

__all__ = (
    "GeneralLoadFactorCalculationMethod",
    "Iso10300FinishingMethods",
    "ISO10300MeshSingleFlankRating",
    "ISO10300MeshSingleFlankRatingBevelMethodB2",
    "ISO10300MeshSingleFlankRatingHypoidMethodB2",
    "ISO10300MeshSingleFlankRatingMethodB1",
    "ISO10300MeshSingleFlankRatingMethodB2",
    "ISO10300RateableMesh",
    "ISO10300RatingMethod",
    "ISO10300SingleFlankRating",
    "ISO10300SingleFlankRatingBevelMethodB2",
    "ISO10300SingleFlankRatingHypoidMethodB2",
    "ISO10300SingleFlankRatingMethodB1",
    "ISO10300SingleFlankRatingMethodB2",
    "MountingConditionsOfPinionAndWheel",
    "PittingFactorCalculationMethod",
    "ProfileCrowningSetting",
    "VerificationOfContactPattern",
)
