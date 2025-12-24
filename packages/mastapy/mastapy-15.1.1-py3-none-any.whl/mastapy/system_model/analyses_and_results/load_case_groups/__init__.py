"""Subpackage."""

from typing import TYPE_CHECKING as __tc

if __tc:
    from mastapy._private.system_model.analyses_and_results.load_case_groups._6000 import (
        AbstractDesignStateLoadCaseGroup,
    )
    from mastapy._private.system_model.analyses_and_results.load_case_groups._6001 import (
        AbstractLoadCaseGroup,
    )
    from mastapy._private.system_model.analyses_and_results.load_case_groups._6002 import (
        AbstractStaticLoadCaseGroup,
    )
    from mastapy._private.system_model.analyses_and_results.load_case_groups._6003 import (
        ClutchEngagementStatus,
    )
    from mastapy._private.system_model.analyses_and_results.load_case_groups._6004 import (
        ConceptSynchroGearEngagementStatus,
    )
    from mastapy._private.system_model.analyses_and_results.load_case_groups._6005 import (
        DesignState,
    )
    from mastapy._private.system_model.analyses_and_results.load_case_groups._6006 import (
        DutyCycle,
    )
    from mastapy._private.system_model.analyses_and_results.load_case_groups._6007 import (
        GenericClutchEngagementStatus,
    )
    from mastapy._private.system_model.analyses_and_results.load_case_groups._6008 import (
        LoadCaseGroupHistograms,
    )
    from mastapy._private.system_model.analyses_and_results.load_case_groups._6009 import (
        SubGroupInSingleDesignState,
    )
    from mastapy._private.system_model.analyses_and_results.load_case_groups._6010 import (
        SystemOptimisationGearSet,
    )
    from mastapy._private.system_model.analyses_and_results.load_case_groups._6011 import (
        SystemOptimiserGearSetOptimisation,
    )
    from mastapy._private.system_model.analyses_and_results.load_case_groups._6012 import (
        SystemOptimiserTargets,
    )
    from mastapy._private.system_model.analyses_and_results.load_case_groups._6013 import (
        TimeSeriesLoadCaseGroup,
    )
else:
    import sys as __sys

    from lazy_imports import LazyImporter as __LazyImporter

    __import_structure = {
        "_private.system_model.analyses_and_results.load_case_groups._6000": [
            "AbstractDesignStateLoadCaseGroup"
        ],
        "_private.system_model.analyses_and_results.load_case_groups._6001": [
            "AbstractLoadCaseGroup"
        ],
        "_private.system_model.analyses_and_results.load_case_groups._6002": [
            "AbstractStaticLoadCaseGroup"
        ],
        "_private.system_model.analyses_and_results.load_case_groups._6003": [
            "ClutchEngagementStatus"
        ],
        "_private.system_model.analyses_and_results.load_case_groups._6004": [
            "ConceptSynchroGearEngagementStatus"
        ],
        "_private.system_model.analyses_and_results.load_case_groups._6005": [
            "DesignState"
        ],
        "_private.system_model.analyses_and_results.load_case_groups._6006": [
            "DutyCycle"
        ],
        "_private.system_model.analyses_and_results.load_case_groups._6007": [
            "GenericClutchEngagementStatus"
        ],
        "_private.system_model.analyses_and_results.load_case_groups._6008": [
            "LoadCaseGroupHistograms"
        ],
        "_private.system_model.analyses_and_results.load_case_groups._6009": [
            "SubGroupInSingleDesignState"
        ],
        "_private.system_model.analyses_and_results.load_case_groups._6010": [
            "SystemOptimisationGearSet"
        ],
        "_private.system_model.analyses_and_results.load_case_groups._6011": [
            "SystemOptimiserGearSetOptimisation"
        ],
        "_private.system_model.analyses_and_results.load_case_groups._6012": [
            "SystemOptimiserTargets"
        ],
        "_private.system_model.analyses_and_results.load_case_groups._6013": [
            "TimeSeriesLoadCaseGroup"
        ],
    }

    __sys.modules[__name__] = __LazyImporter(
        "mastapy",
        globals()["__file__"],
        __import_structure,
    )

__all__ = (
    "AbstractDesignStateLoadCaseGroup",
    "AbstractLoadCaseGroup",
    "AbstractStaticLoadCaseGroup",
    "ClutchEngagementStatus",
    "ConceptSynchroGearEngagementStatus",
    "DesignState",
    "DutyCycle",
    "GenericClutchEngagementStatus",
    "LoadCaseGroupHistograms",
    "SubGroupInSingleDesignState",
    "SystemOptimisationGearSet",
    "SystemOptimiserGearSetOptimisation",
    "SystemOptimiserTargets",
    "TimeSeriesLoadCaseGroup",
)
