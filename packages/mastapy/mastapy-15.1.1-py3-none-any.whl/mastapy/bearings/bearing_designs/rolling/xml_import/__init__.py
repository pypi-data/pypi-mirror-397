"""Subpackage."""

from typing import TYPE_CHECKING as __tc

if __tc:
    from mastapy._private.bearings.bearing_designs.rolling.xml_import._2424 import (
        AbstractXmlVariableAssignment,
    )
    from mastapy._private.bearings.bearing_designs.rolling.xml_import._2425 import (
        BearingImportFile,
    )
    from mastapy._private.bearings.bearing_designs.rolling.xml_import._2426 import (
        RollingBearingImporter,
    )
    from mastapy._private.bearings.bearing_designs.rolling.xml_import._2427 import (
        XmlBearingTypeMapping,
    )
    from mastapy._private.bearings.bearing_designs.rolling.xml_import._2428 import (
        XMLVariableAssignment,
    )
else:
    import sys as __sys

    from lazy_imports import LazyImporter as __LazyImporter

    __import_structure = {
        "_private.bearings.bearing_designs.rolling.xml_import._2424": [
            "AbstractXmlVariableAssignment"
        ],
        "_private.bearings.bearing_designs.rolling.xml_import._2425": [
            "BearingImportFile"
        ],
        "_private.bearings.bearing_designs.rolling.xml_import._2426": [
            "RollingBearingImporter"
        ],
        "_private.bearings.bearing_designs.rolling.xml_import._2427": [
            "XmlBearingTypeMapping"
        ],
        "_private.bearings.bearing_designs.rolling.xml_import._2428": [
            "XMLVariableAssignment"
        ],
    }

    __sys.modules[__name__] = __LazyImporter(
        "mastapy",
        globals()["__file__"],
        __import_structure,
    )

__all__ = (
    "AbstractXmlVariableAssignment",
    "BearingImportFile",
    "RollingBearingImporter",
    "XmlBearingTypeMapping",
    "XMLVariableAssignment",
)
