"""Subpackage."""

from typing import TYPE_CHECKING as __tc

if __tc:
    from mastapy._private.nodal_analysis.geometry_modeller_link._236 import (
        BaseGeometryModellerDimension,
    )
    from mastapy._private.nodal_analysis.geometry_modeller_link._237 import (
        GearTipRadiusClashTest,
    )
    from mastapy._private.nodal_analysis.geometry_modeller_link._238 import (
        GeometryModellerAngleDimension,
    )
    from mastapy._private.nodal_analysis.geometry_modeller_link._239 import (
        GeometryModellerCountDimension,
    )
    from mastapy._private.nodal_analysis.geometry_modeller_link._240 import (
        GeometryModellerDesignInformation,
    )
    from mastapy._private.nodal_analysis.geometry_modeller_link._241 import (
        GeometryModellerDimension,
    )
    from mastapy._private.nodal_analysis.geometry_modeller_link._242 import (
        GeometryModellerDimensions,
    )
    from mastapy._private.nodal_analysis.geometry_modeller_link._243 import (
        GeometryModellerDimensionType,
    )
    from mastapy._private.nodal_analysis.geometry_modeller_link._244 import (
        GeometryModellerLengthDimension,
    )
    from mastapy._private.nodal_analysis.geometry_modeller_link._245 import (
        GeometryModellerSettings,
    )
    from mastapy._private.nodal_analysis.geometry_modeller_link._246 import (
        GeometryModellerUnitlessDimension,
    )
    from mastapy._private.nodal_analysis.geometry_modeller_link._247 import (
        GeometryTypeForComponentImport,
    )
    from mastapy._private.nodal_analysis.geometry_modeller_link._248 import MeshRequest
    from mastapy._private.nodal_analysis.geometry_modeller_link._249 import (
        MeshRequestResult,
    )
    from mastapy._private.nodal_analysis.geometry_modeller_link._250 import (
        ProfileFromImport,
    )
    from mastapy._private.nodal_analysis.geometry_modeller_link._251 import (
        RepositionComponentDetails,
    )
else:
    import sys as __sys

    from lazy_imports import LazyImporter as __LazyImporter

    __import_structure = {
        "_private.nodal_analysis.geometry_modeller_link._236": [
            "BaseGeometryModellerDimension"
        ],
        "_private.nodal_analysis.geometry_modeller_link._237": [
            "GearTipRadiusClashTest"
        ],
        "_private.nodal_analysis.geometry_modeller_link._238": [
            "GeometryModellerAngleDimension"
        ],
        "_private.nodal_analysis.geometry_modeller_link._239": [
            "GeometryModellerCountDimension"
        ],
        "_private.nodal_analysis.geometry_modeller_link._240": [
            "GeometryModellerDesignInformation"
        ],
        "_private.nodal_analysis.geometry_modeller_link._241": [
            "GeometryModellerDimension"
        ],
        "_private.nodal_analysis.geometry_modeller_link._242": [
            "GeometryModellerDimensions"
        ],
        "_private.nodal_analysis.geometry_modeller_link._243": [
            "GeometryModellerDimensionType"
        ],
        "_private.nodal_analysis.geometry_modeller_link._244": [
            "GeometryModellerLengthDimension"
        ],
        "_private.nodal_analysis.geometry_modeller_link._245": [
            "GeometryModellerSettings"
        ],
        "_private.nodal_analysis.geometry_modeller_link._246": [
            "GeometryModellerUnitlessDimension"
        ],
        "_private.nodal_analysis.geometry_modeller_link._247": [
            "GeometryTypeForComponentImport"
        ],
        "_private.nodal_analysis.geometry_modeller_link._248": ["MeshRequest"],
        "_private.nodal_analysis.geometry_modeller_link._249": ["MeshRequestResult"],
        "_private.nodal_analysis.geometry_modeller_link._250": ["ProfileFromImport"],
        "_private.nodal_analysis.geometry_modeller_link._251": [
            "RepositionComponentDetails"
        ],
    }

    __sys.modules[__name__] = __LazyImporter(
        "mastapy",
        globals()["__file__"],
        __import_structure,
    )

__all__ = (
    "BaseGeometryModellerDimension",
    "GearTipRadiusClashTest",
    "GeometryModellerAngleDimension",
    "GeometryModellerCountDimension",
    "GeometryModellerDesignInformation",
    "GeometryModellerDimension",
    "GeometryModellerDimensions",
    "GeometryModellerDimensionType",
    "GeometryModellerLengthDimension",
    "GeometryModellerSettings",
    "GeometryModellerUnitlessDimension",
    "GeometryTypeForComponentImport",
    "MeshRequest",
    "MeshRequestResult",
    "ProfileFromImport",
    "RepositionComponentDetails",
)
