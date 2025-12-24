"""Subpackage."""

from typing import TYPE_CHECKING as __tc

if __tc:
    from mastapy._private.system_model.analyses_and_results._2939 import (
        CompoundAnalysis,
    )
    from mastapy._private.system_model.analyses_and_results._2940 import (
        AnalysisCaseVariable,
    )
    from mastapy._private.system_model.analyses_and_results._2941 import (
        ConnectionAnalysis,
    )
    from mastapy._private.system_model.analyses_and_results._2942 import Context
    from mastapy._private.system_model.analyses_and_results._2943 import (
        DesignEntityAnalysis,
    )
    from mastapy._private.system_model.analyses_and_results._2944 import (
        DesignEntityGroupAnalysis,
    )
    from mastapy._private.system_model.analyses_and_results._2945 import (
        DesignEntitySingleContextAnalysis,
    )
    from mastapy._private.system_model.analyses_and_results._2949 import PartAnalysis
    from mastapy._private.system_model.analyses_and_results._2950 import (
        CompoundAdvancedSystemDeflection,
    )
    from mastapy._private.system_model.analyses_and_results._2951 import (
        CompoundAdvancedSystemDeflectionSubAnalysis,
    )
    from mastapy._private.system_model.analyses_and_results._2952 import (
        CompoundAdvancedTimeSteppingAnalysisForModulation,
    )
    from mastapy._private.system_model.analyses_and_results._2953 import (
        CompoundCriticalSpeedAnalysis,
    )
    from mastapy._private.system_model.analyses_and_results._2954 import (
        CompoundDynamicAnalysis,
    )
    from mastapy._private.system_model.analyses_and_results._2955 import (
        CompoundDynamicModelAtAStiffness,
    )
    from mastapy._private.system_model.analyses_and_results._2956 import (
        CompoundDynamicModelForHarmonicAnalysis,
    )
    from mastapy._private.system_model.analyses_and_results._2957 import (
        CompoundDynamicModelForModalAnalysis,
    )
    from mastapy._private.system_model.analyses_and_results._2958 import (
        CompoundDynamicModelForStabilityAnalysis,
    )
    from mastapy._private.system_model.analyses_and_results._2959 import (
        CompoundDynamicModelForSteadyStateSynchronousResponse,
    )
    from mastapy._private.system_model.analyses_and_results._2960 import (
        CompoundHarmonicAnalysis,
    )
    from mastapy._private.system_model.analyses_and_results._2961 import (
        CompoundHarmonicAnalysisForAdvancedTimeSteppingAnalysisForModulation,
    )
    from mastapy._private.system_model.analyses_and_results._2962 import (
        CompoundHarmonicAnalysisOfSingleExcitation,
    )
    from mastapy._private.system_model.analyses_and_results._2963 import (
        CompoundModalAnalysis,
    )
    from mastapy._private.system_model.analyses_and_results._2964 import (
        CompoundModalAnalysisAtASpeed,
    )
    from mastapy._private.system_model.analyses_and_results._2965 import (
        CompoundModalAnalysisAtAStiffness,
    )
    from mastapy._private.system_model.analyses_and_results._2966 import (
        CompoundModalAnalysisForHarmonicAnalysis,
    )
    from mastapy._private.system_model.analyses_and_results._2967 import (
        CompoundMultibodyDynamicsAnalysis,
    )
    from mastapy._private.system_model.analyses_and_results._2968 import (
        CompoundPowerFlow,
    )
    from mastapy._private.system_model.analyses_and_results._2969 import (
        CompoundStabilityAnalysis,
    )
    from mastapy._private.system_model.analyses_and_results._2970 import (
        CompoundSteadyStateSynchronousResponse,
    )
    from mastapy._private.system_model.analyses_and_results._2971 import (
        CompoundSteadyStateSynchronousResponseAtASpeed,
    )
    from mastapy._private.system_model.analyses_and_results._2972 import (
        CompoundSteadyStateSynchronousResponseOnAShaft,
    )
    from mastapy._private.system_model.analyses_and_results._2973 import (
        CompoundSystemDeflection,
    )
    from mastapy._private.system_model.analyses_and_results._2974 import (
        CompoundTorsionalSystemDeflection,
    )
    from mastapy._private.system_model.analyses_and_results._2975 import (
        TESetUpForDynamicAnalysisOptions,
    )
    from mastapy._private.system_model.analyses_and_results._2976 import TimeOptions
else:
    import sys as __sys

    from lazy_imports import LazyImporter as __LazyImporter

    __import_structure = {
        "_private.system_model.analyses_and_results._2939": ["CompoundAnalysis"],
        "_private.system_model.analyses_and_results._2940": ["AnalysisCaseVariable"],
        "_private.system_model.analyses_and_results._2941": ["ConnectionAnalysis"],
        "_private.system_model.analyses_and_results._2942": ["Context"],
        "_private.system_model.analyses_and_results._2943": ["DesignEntityAnalysis"],
        "_private.system_model.analyses_and_results._2944": [
            "DesignEntityGroupAnalysis"
        ],
        "_private.system_model.analyses_and_results._2945": [
            "DesignEntitySingleContextAnalysis"
        ],
        "_private.system_model.analyses_and_results._2949": ["PartAnalysis"],
        "_private.system_model.analyses_and_results._2950": [
            "CompoundAdvancedSystemDeflection"
        ],
        "_private.system_model.analyses_and_results._2951": [
            "CompoundAdvancedSystemDeflectionSubAnalysis"
        ],
        "_private.system_model.analyses_and_results._2952": [
            "CompoundAdvancedTimeSteppingAnalysisForModulation"
        ],
        "_private.system_model.analyses_and_results._2953": [
            "CompoundCriticalSpeedAnalysis"
        ],
        "_private.system_model.analyses_and_results._2954": ["CompoundDynamicAnalysis"],
        "_private.system_model.analyses_and_results._2955": [
            "CompoundDynamicModelAtAStiffness"
        ],
        "_private.system_model.analyses_and_results._2956": [
            "CompoundDynamicModelForHarmonicAnalysis"
        ],
        "_private.system_model.analyses_and_results._2957": [
            "CompoundDynamicModelForModalAnalysis"
        ],
        "_private.system_model.analyses_and_results._2958": [
            "CompoundDynamicModelForStabilityAnalysis"
        ],
        "_private.system_model.analyses_and_results._2959": [
            "CompoundDynamicModelForSteadyStateSynchronousResponse"
        ],
        "_private.system_model.analyses_and_results._2960": [
            "CompoundHarmonicAnalysis"
        ],
        "_private.system_model.analyses_and_results._2961": [
            "CompoundHarmonicAnalysisForAdvancedTimeSteppingAnalysisForModulation"
        ],
        "_private.system_model.analyses_and_results._2962": [
            "CompoundHarmonicAnalysisOfSingleExcitation"
        ],
        "_private.system_model.analyses_and_results._2963": ["CompoundModalAnalysis"],
        "_private.system_model.analyses_and_results._2964": [
            "CompoundModalAnalysisAtASpeed"
        ],
        "_private.system_model.analyses_and_results._2965": [
            "CompoundModalAnalysisAtAStiffness"
        ],
        "_private.system_model.analyses_and_results._2966": [
            "CompoundModalAnalysisForHarmonicAnalysis"
        ],
        "_private.system_model.analyses_and_results._2967": [
            "CompoundMultibodyDynamicsAnalysis"
        ],
        "_private.system_model.analyses_and_results._2968": ["CompoundPowerFlow"],
        "_private.system_model.analyses_and_results._2969": [
            "CompoundStabilityAnalysis"
        ],
        "_private.system_model.analyses_and_results._2970": [
            "CompoundSteadyStateSynchronousResponse"
        ],
        "_private.system_model.analyses_and_results._2971": [
            "CompoundSteadyStateSynchronousResponseAtASpeed"
        ],
        "_private.system_model.analyses_and_results._2972": [
            "CompoundSteadyStateSynchronousResponseOnAShaft"
        ],
        "_private.system_model.analyses_and_results._2973": [
            "CompoundSystemDeflection"
        ],
        "_private.system_model.analyses_and_results._2974": [
            "CompoundTorsionalSystemDeflection"
        ],
        "_private.system_model.analyses_and_results._2975": [
            "TESetUpForDynamicAnalysisOptions"
        ],
        "_private.system_model.analyses_and_results._2976": ["TimeOptions"],
    }

    __sys.modules[__name__] = __LazyImporter(
        "mastapy",
        globals()["__file__"],
        __import_structure,
    )

__all__ = (
    "CompoundAnalysis",
    "AnalysisCaseVariable",
    "ConnectionAnalysis",
    "Context",
    "DesignEntityAnalysis",
    "DesignEntityGroupAnalysis",
    "DesignEntitySingleContextAnalysis",
    "PartAnalysis",
    "CompoundAdvancedSystemDeflection",
    "CompoundAdvancedSystemDeflectionSubAnalysis",
    "CompoundAdvancedTimeSteppingAnalysisForModulation",
    "CompoundCriticalSpeedAnalysis",
    "CompoundDynamicAnalysis",
    "CompoundDynamicModelAtAStiffness",
    "CompoundDynamicModelForHarmonicAnalysis",
    "CompoundDynamicModelForModalAnalysis",
    "CompoundDynamicModelForStabilityAnalysis",
    "CompoundDynamicModelForSteadyStateSynchronousResponse",
    "CompoundHarmonicAnalysis",
    "CompoundHarmonicAnalysisForAdvancedTimeSteppingAnalysisForModulation",
    "CompoundHarmonicAnalysisOfSingleExcitation",
    "CompoundModalAnalysis",
    "CompoundModalAnalysisAtASpeed",
    "CompoundModalAnalysisAtAStiffness",
    "CompoundModalAnalysisForHarmonicAnalysis",
    "CompoundMultibodyDynamicsAnalysis",
    "CompoundPowerFlow",
    "CompoundStabilityAnalysis",
    "CompoundSteadyStateSynchronousResponse",
    "CompoundSteadyStateSynchronousResponseAtASpeed",
    "CompoundSteadyStateSynchronousResponseOnAShaft",
    "CompoundSystemDeflection",
    "CompoundTorsionalSystemDeflection",
    "TESetUpForDynamicAnalysisOptions",
    "TimeOptions",
)
