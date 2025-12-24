"""Subpackage."""

from typing import TYPE_CHECKING as __tc

if __tc:
    from mastapy._private.scripting._7959 import ApiEnumForAttribute
    from mastapy._private.scripting._7960 import ApiVersion
    from mastapy._private.scripting._7961 import SMTBitmap
    from mastapy._private.scripting._7963 import MastaPropertyAttribute
    from mastapy._private.scripting._7964 import PythonCommand
    from mastapy._private.scripting._7965 import ScriptingCommand
    from mastapy._private.scripting._7966 import ScriptingExecutionCommand
    from mastapy._private.scripting._7967 import ScriptingObjectCommand
    from mastapy._private.scripting._7968 import ApiVersioning
else:
    import sys as __sys

    from lazy_imports import LazyImporter as __LazyImporter

    __import_structure = {
        "_private.scripting._7959": ["ApiEnumForAttribute"],
        "_private.scripting._7960": ["ApiVersion"],
        "_private.scripting._7961": ["SMTBitmap"],
        "_private.scripting._7963": ["MastaPropertyAttribute"],
        "_private.scripting._7964": ["PythonCommand"],
        "_private.scripting._7965": ["ScriptingCommand"],
        "_private.scripting._7966": ["ScriptingExecutionCommand"],
        "_private.scripting._7967": ["ScriptingObjectCommand"],
        "_private.scripting._7968": ["ApiVersioning"],
    }

    __sys.modules[__name__] = __LazyImporter(
        "mastapy",
        globals()["__file__"],
        __import_structure,
    )

__all__ = (
    "ApiEnumForAttribute",
    "ApiVersion",
    "SMTBitmap",
    "MastaPropertyAttribute",
    "PythonCommand",
    "ScriptingCommand",
    "ScriptingExecutionCommand",
    "ScriptingObjectCommand",
    "ApiVersioning",
)
