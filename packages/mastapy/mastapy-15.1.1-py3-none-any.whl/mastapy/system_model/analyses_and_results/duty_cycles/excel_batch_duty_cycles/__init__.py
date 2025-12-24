"""Subpackage."""

from typing import TYPE_CHECKING as __tc

if __tc:
    from mastapy._private.system_model.analyses_and_results.duty_cycles.excel_batch_duty_cycles._6905 import (
        ExcelBatchDutyCycleCreator,
    )
    from mastapy._private.system_model.analyses_and_results.duty_cycles.excel_batch_duty_cycles._6906 import (
        ExcelBatchDutyCycleSpectraCreatorDetails,
    )
    from mastapy._private.system_model.analyses_and_results.duty_cycles.excel_batch_duty_cycles._6907 import (
        ExcelFileDetails,
    )
    from mastapy._private.system_model.analyses_and_results.duty_cycles.excel_batch_duty_cycles._6908 import (
        ExcelSheet,
    )
    from mastapy._private.system_model.analyses_and_results.duty_cycles.excel_batch_duty_cycles._6909 import (
        ExcelSheetDesignStateSelector,
    )
    from mastapy._private.system_model.analyses_and_results.duty_cycles.excel_batch_duty_cycles._6910 import (
        MASTAFileDetails,
    )
else:
    import sys as __sys

    from lazy_imports import LazyImporter as __LazyImporter

    __import_structure = {
        "_private.system_model.analyses_and_results.duty_cycles.excel_batch_duty_cycles._6905": [
            "ExcelBatchDutyCycleCreator"
        ],
        "_private.system_model.analyses_and_results.duty_cycles.excel_batch_duty_cycles._6906": [
            "ExcelBatchDutyCycleSpectraCreatorDetails"
        ],
        "_private.system_model.analyses_and_results.duty_cycles.excel_batch_duty_cycles._6907": [
            "ExcelFileDetails"
        ],
        "_private.system_model.analyses_and_results.duty_cycles.excel_batch_duty_cycles._6908": [
            "ExcelSheet"
        ],
        "_private.system_model.analyses_and_results.duty_cycles.excel_batch_duty_cycles._6909": [
            "ExcelSheetDesignStateSelector"
        ],
        "_private.system_model.analyses_and_results.duty_cycles.excel_batch_duty_cycles._6910": [
            "MASTAFileDetails"
        ],
    }

    __sys.modules[__name__] = __LazyImporter(
        "mastapy",
        globals()["__file__"],
        __import_structure,
    )

__all__ = (
    "ExcelBatchDutyCycleCreator",
    "ExcelBatchDutyCycleSpectraCreatorDetails",
    "ExcelFileDetails",
    "ExcelSheet",
    "ExcelSheetDesignStateSelector",
    "MASTAFileDetails",
)
