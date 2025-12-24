"""GenericMatrix"""

from __future__ import annotations

from typing import TYPE_CHECKING, ClassVar, Generic, TypeVar

from mastapy._private._internal.dataclasses import extended_dataclass
from mastapy._private._internal.exception_bridge import exception_bridge
from mastapy._private._internal.exceptions import CastException
from mastapy._private._internal.python_net import (
    python_net_import,
    pythonnet_method_call,
    pythonnet_property_get,
)
from mastapy._private._internal.type_enforcement import enforce_parameter_types

from mastapy._private import _0
from mastapy._private._internal import conversion, utility

_GENERIC_MATRIX = python_net_import("SMT.MastaAPI.MathUtility", "GenericMatrix")

if TYPE_CHECKING:
    from typing import Any, List, Type

    from mastapy._private.math_utility import (
        _1705,
        _1707,
        _1708,
        _1709,
        _1721,
        _1740,
        _1741,
        _1742,
        _1747,
        _1751,
    )

    Self = TypeVar("Self", bound="GenericMatrix")
    CastSelf = TypeVar("CastSelf", bound="GenericMatrix._Cast_GenericMatrix")

TElement = TypeVar("TElement", bound="object")
TMatrix = TypeVar("TMatrix", bound="GenericMatrix")

__docformat__ = "restructuredtext en"
__all__ = ("GenericMatrix",)


@extended_dataclass(frozen=True, slots=True, weakref_slot=True)
class _Cast_GenericMatrix:
    """Special nested class for casting GenericMatrix to subclasses."""

    __parent__: "GenericMatrix"

    @property
    def complex_matrix(self: "CastSelf") -> "_1705.ComplexMatrix":
        from mastapy._private.math_utility import _1705

        return self.__parent__._cast(_1705.ComplexMatrix)

    @property
    def complex_vector(self: "CastSelf") -> "_1707.ComplexVector":
        from mastapy._private.math_utility import _1707

        return self.__parent__._cast(_1707.ComplexVector)

    @property
    def complex_vector_3d(self: "CastSelf") -> "_1708.ComplexVector3D":
        from mastapy._private.math_utility import _1708

        return self.__parent__._cast(_1708.ComplexVector3D)

    @property
    def complex_vector_6d(self: "CastSelf") -> "_1709.ComplexVector6D":
        from mastapy._private.math_utility import _1709

        return self.__parent__._cast(_1709.ComplexVector6D)

    @property
    def euler_parameters(self: "CastSelf") -> "_1721.EulerParameters":
        from mastapy._private.math_utility import _1721

        return self.__parent__._cast(_1721.EulerParameters)

    @property
    def quaternion(self: "CastSelf") -> "_1740.Quaternion":
        from mastapy._private.math_utility import _1740

        return self.__parent__._cast(_1740.Quaternion)

    @property
    def real_matrix(self: "CastSelf") -> "_1741.RealMatrix":
        from mastapy._private.math_utility import _1741

        return self.__parent__._cast(_1741.RealMatrix)

    @property
    def real_vector(self: "CastSelf") -> "_1742.RealVector":
        from mastapy._private.math_utility import _1742

        return self.__parent__._cast(_1742.RealVector)

    @property
    def square_matrix(self: "CastSelf") -> "_1747.SquareMatrix":
        from mastapy._private.math_utility import _1747

        return self.__parent__._cast(_1747.SquareMatrix)

    @property
    def vector_6d(self: "CastSelf") -> "_1751.Vector6D":
        from mastapy._private.math_utility import _1751

        return self.__parent__._cast(_1751.Vector6D)

    @property
    def generic_matrix(self: "CastSelf") -> "GenericMatrix":
        return self.__parent__

    def __getattr__(self: "CastSelf", name: str) -> "Any":
        try:
            return self.__getattribute__(name)
        except AttributeError:
            class_name = utility.camel(name)
            raise CastException(
                f'Detected an invalid cast. Cannot cast to type "{class_name}"'
            ) from None


@extended_dataclass(frozen=True, slots=True, weakref_slot=True, eq=False)
class GenericMatrix(_0.APIBase, Generic[TElement, TMatrix]):
    """GenericMatrix

    This is a mastapy class.

    Generic Types:
        TElement
        TMatrix
    """

    TYPE: ClassVar["Type"] = _GENERIC_MATRIX

    wrapped: "Any"

    def __post_init__(self: "Self") -> None:
        """Override of the post initialisation magic method."""
        if not hasattr(self.wrapped, "reference_count"):
            self.wrapped.reference_count = 0

        self.wrapped.reference_count += 1

    @property
    @exception_bridge
    def number_of_columns(self: "Self") -> "int":
        """int

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "NumberOfColumns")

        if temp is None:
            return 0

        return temp

    @property
    @exception_bridge
    def number_of_entries(self: "Self") -> "int":
        """int

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "NumberOfEntries")

        if temp is None:
            return 0

        return temp

    @property
    @exception_bridge
    def number_of_rows(self: "Self") -> "int":
        """int

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "NumberOfRows")

        if temp is None:
            return 0

        return temp

    @property
    @exception_bridge
    def data(self: "Self") -> "List[TElement]":
        """List[TElement]

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "Data")

        if temp is None:
            return None

        value = conversion.pn_to_mp_objects_in_list(temp)

        if value is None:
            return None

        return value

    @exception_bridge
    @enforce_parameter_types
    def get_column_at(self: "Self", index: "int") -> "List[TElement]":
        """List[TElement]

        Args:
            index (int)
        """
        index = int(index)
        return conversion.pn_to_mp_objects_in_list(
            pythonnet_method_call(self.wrapped, "GetColumnAt", index if index else 0)
        )

    @exception_bridge
    @enforce_parameter_types
    def get_row_at(self: "Self", row_index: "int") -> "List[TElement]":
        """List[TElement]

        Args:
            row_index (int)
        """
        row_index = int(row_index)
        return conversion.pn_to_mp_objects_in_list(
            pythonnet_method_call(
                self.wrapped, "GetRowAt", row_index if row_index else 0
            )
        )

    @property
    def cast_to(self: "Self") -> "_Cast_GenericMatrix":
        """Cast to another type.

        Returns:
            _Cast_GenericMatrix
        """
        return _Cast_GenericMatrix(self)
