"""Subpackage."""

from typing import TYPE_CHECKING as __tc

if __tc:
    from mastapy._private.fe_tools.vfx_tools.vfx_enums._1386 import ProSolveEigenmethod
    from mastapy._private.fe_tools.vfx_tools.vfx_enums._1387 import ProSolveMpcType
    from mastapy._private.fe_tools.vfx_tools.vfx_enums._1388 import ProSolveSolverType
else:
    import sys as __sys

    from lazy_imports import LazyImporter as __LazyImporter

    __import_structure = {
        "_private.fe_tools.vfx_tools.vfx_enums._1386": ["ProSolveEigenmethod"],
        "_private.fe_tools.vfx_tools.vfx_enums._1387": ["ProSolveMpcType"],
        "_private.fe_tools.vfx_tools.vfx_enums._1388": ["ProSolveSolverType"],
    }

    __sys.modules[__name__] = __LazyImporter(
        "mastapy",
        globals()["__file__"],
        __import_structure,
    )

__all__ = (
    "ProSolveEigenmethod",
    "ProSolveMpcType",
    "ProSolveSolverType",
)
