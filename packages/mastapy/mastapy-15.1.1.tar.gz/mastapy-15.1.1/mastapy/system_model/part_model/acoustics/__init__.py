"""Subpackage."""

from typing import TYPE_CHECKING as __tc

if __tc:
    from mastapy._private.system_model.part_model.acoustics._2910 import (
        AcousticAnalysisOptions,
    )
    from mastapy._private.system_model.part_model.acoustics._2911 import (
        AcousticAnalysisSetup,
    )
    from mastapy._private.system_model.part_model.acoustics._2912 import (
        AcousticAnalysisSetupCacheReporting,
    )
    from mastapy._private.system_model.part_model.acoustics._2913 import (
        AcousticAnalysisSetupCollection,
    )
    from mastapy._private.system_model.part_model.acoustics._2914 import (
        AcousticEnvelopeType,
    )
    from mastapy._private.system_model.part_model.acoustics._2915 import (
        AcousticInputSurfaceOptions,
    )
    from mastapy._private.system_model.part_model.acoustics._2916 import (
        CacheMemoryEstimates,
    )
    from mastapy._private.system_model.part_model.acoustics._2917 import (
        CylindricalEnvelopeTypes,
    )
    from mastapy._private.system_model.part_model.acoustics._2918 import (
        FEPartInputSurfaceOptions,
    )
    from mastapy._private.system_model.part_model.acoustics._2919 import (
        FESurfaceSelectionForAcousticEnvelope,
    )
    from mastapy._private.system_model.part_model.acoustics._2920 import HoleInFaceGroup
    from mastapy._private.system_model.part_model.acoustics._2921 import (
        HemisphericalEnvelopeType,
    )
    from mastapy._private.system_model.part_model.acoustics._2922 import (
        MeshedReflectingPlane,
    )
    from mastapy._private.system_model.part_model.acoustics._2923 import (
        MeshedResultPlane,
    )
    from mastapy._private.system_model.part_model.acoustics._2924 import (
        MeshedResultSphere,
    )
    from mastapy._private.system_model.part_model.acoustics._2925 import (
        MeshedResultSurface,
    )
    from mastapy._private.system_model.part_model.acoustics._2926 import (
        MeshedResultSurfaceBase,
    )
    from mastapy._private.system_model.part_model.acoustics._2927 import (
        MicrophoneArrayDesign,
    )
    from mastapy._private.system_model.part_model.acoustics._2928 import (
        PartSelectionForAcousticEnvelope,
    )
    from mastapy._private.system_model.part_model.acoustics._2929 import PlaneShape
    from mastapy._private.system_model.part_model.acoustics._2930 import (
        ReflectingPlaneCollection,
    )
    from mastapy._private.system_model.part_model.acoustics._2931 import (
        ReflectingPlaneOptions,
    )
    from mastapy._private.system_model.part_model.acoustics._2932 import (
        ResultPlaneOptions,
    )
    from mastapy._private.system_model.part_model.acoustics._2933 import (
        ResultSphereOptions,
    )
    from mastapy._private.system_model.part_model.acoustics._2934 import (
        ResultSurfaceCollection,
    )
    from mastapy._private.system_model.part_model.acoustics._2935 import (
        ResultSurfaceOptions,
    )
    from mastapy._private.system_model.part_model.acoustics._2936 import (
        RightParallelepipedEnvelopeTypes,
    )
    from mastapy._private.system_model.part_model.acoustics._2937 import (
        SphericalEnvelopeCentreDefinition,
    )
    from mastapy._private.system_model.part_model.acoustics._2938 import (
        SphericalEnvelopeType,
    )
else:
    import sys as __sys

    from lazy_imports import LazyImporter as __LazyImporter

    __import_structure = {
        "_private.system_model.part_model.acoustics._2910": ["AcousticAnalysisOptions"],
        "_private.system_model.part_model.acoustics._2911": ["AcousticAnalysisSetup"],
        "_private.system_model.part_model.acoustics._2912": [
            "AcousticAnalysisSetupCacheReporting"
        ],
        "_private.system_model.part_model.acoustics._2913": [
            "AcousticAnalysisSetupCollection"
        ],
        "_private.system_model.part_model.acoustics._2914": ["AcousticEnvelopeType"],
        "_private.system_model.part_model.acoustics._2915": [
            "AcousticInputSurfaceOptions"
        ],
        "_private.system_model.part_model.acoustics._2916": ["CacheMemoryEstimates"],
        "_private.system_model.part_model.acoustics._2917": [
            "CylindricalEnvelopeTypes"
        ],
        "_private.system_model.part_model.acoustics._2918": [
            "FEPartInputSurfaceOptions"
        ],
        "_private.system_model.part_model.acoustics._2919": [
            "FESurfaceSelectionForAcousticEnvelope"
        ],
        "_private.system_model.part_model.acoustics._2920": ["HoleInFaceGroup"],
        "_private.system_model.part_model.acoustics._2921": [
            "HemisphericalEnvelopeType"
        ],
        "_private.system_model.part_model.acoustics._2922": ["MeshedReflectingPlane"],
        "_private.system_model.part_model.acoustics._2923": ["MeshedResultPlane"],
        "_private.system_model.part_model.acoustics._2924": ["MeshedResultSphere"],
        "_private.system_model.part_model.acoustics._2925": ["MeshedResultSurface"],
        "_private.system_model.part_model.acoustics._2926": ["MeshedResultSurfaceBase"],
        "_private.system_model.part_model.acoustics._2927": ["MicrophoneArrayDesign"],
        "_private.system_model.part_model.acoustics._2928": [
            "PartSelectionForAcousticEnvelope"
        ],
        "_private.system_model.part_model.acoustics._2929": ["PlaneShape"],
        "_private.system_model.part_model.acoustics._2930": [
            "ReflectingPlaneCollection"
        ],
        "_private.system_model.part_model.acoustics._2931": ["ReflectingPlaneOptions"],
        "_private.system_model.part_model.acoustics._2932": ["ResultPlaneOptions"],
        "_private.system_model.part_model.acoustics._2933": ["ResultSphereOptions"],
        "_private.system_model.part_model.acoustics._2934": ["ResultSurfaceCollection"],
        "_private.system_model.part_model.acoustics._2935": ["ResultSurfaceOptions"],
        "_private.system_model.part_model.acoustics._2936": [
            "RightParallelepipedEnvelopeTypes"
        ],
        "_private.system_model.part_model.acoustics._2937": [
            "SphericalEnvelopeCentreDefinition"
        ],
        "_private.system_model.part_model.acoustics._2938": ["SphericalEnvelopeType"],
    }

    __sys.modules[__name__] = __LazyImporter(
        "mastapy",
        globals()["__file__"],
        __import_structure,
    )

__all__ = (
    "AcousticAnalysisOptions",
    "AcousticAnalysisSetup",
    "AcousticAnalysisSetupCacheReporting",
    "AcousticAnalysisSetupCollection",
    "AcousticEnvelopeType",
    "AcousticInputSurfaceOptions",
    "CacheMemoryEstimates",
    "CylindricalEnvelopeTypes",
    "FEPartInputSurfaceOptions",
    "FESurfaceSelectionForAcousticEnvelope",
    "HoleInFaceGroup",
    "HemisphericalEnvelopeType",
    "MeshedReflectingPlane",
    "MeshedResultPlane",
    "MeshedResultSphere",
    "MeshedResultSurface",
    "MeshedResultSurfaceBase",
    "MicrophoneArrayDesign",
    "PartSelectionForAcousticEnvelope",
    "PlaneShape",
    "ReflectingPlaneCollection",
    "ReflectingPlaneOptions",
    "ResultPlaneOptions",
    "ResultSphereOptions",
    "ResultSurfaceCollection",
    "ResultSurfaceOptions",
    "RightParallelepipedEnvelopeTypes",
    "SphericalEnvelopeCentreDefinition",
    "SphericalEnvelopeType",
)
