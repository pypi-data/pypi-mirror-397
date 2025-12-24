"""Subpackage."""

from typing import TYPE_CHECKING as __tc

if __tc:
    from mastapy._private.nodal_analysis.nodal_entities.external_force._177 import (
        ExternalForceEntity,
    )
    from mastapy._private.nodal_analysis.nodal_entities.external_force._178 import (
        ExternalForceLineContactEntity,
    )
    from mastapy._private.nodal_analysis.nodal_entities.external_force._179 import (
        ExternalForceSinglePointEntity,
    )
    from mastapy._private.nodal_analysis.nodal_entities.external_force._180 import (
        GearMeshBothFlankContacts,
    )
    from mastapy._private.nodal_analysis.nodal_entities.external_force._181 import (
        GearMeshDirectSingleFlankContact,
    )
else:
    import sys as __sys

    from lazy_imports import LazyImporter as __LazyImporter

    __import_structure = {
        "_private.nodal_analysis.nodal_entities.external_force._177": [
            "ExternalForceEntity"
        ],
        "_private.nodal_analysis.nodal_entities.external_force._178": [
            "ExternalForceLineContactEntity"
        ],
        "_private.nodal_analysis.nodal_entities.external_force._179": [
            "ExternalForceSinglePointEntity"
        ],
        "_private.nodal_analysis.nodal_entities.external_force._180": [
            "GearMeshBothFlankContacts"
        ],
        "_private.nodal_analysis.nodal_entities.external_force._181": [
            "GearMeshDirectSingleFlankContact"
        ],
    }

    __sys.modules[__name__] = __LazyImporter(
        "mastapy",
        globals()["__file__"],
        __import_structure,
    )

__all__ = (
    "ExternalForceEntity",
    "ExternalForceLineContactEntity",
    "ExternalForceSinglePointEntity",
    "GearMeshBothFlankContacts",
    "GearMeshDirectSingleFlankContact",
)
