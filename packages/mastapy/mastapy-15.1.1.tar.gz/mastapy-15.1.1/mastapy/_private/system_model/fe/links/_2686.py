"""FELink"""

from __future__ import annotations

from typing import TYPE_CHECKING, ClassVar

from mastapy._private._internal.dataclasses import extended_dataclass
from mastapy._private._internal.exception_bridge import exception_bridge
from mastapy._private._internal.exceptions import CastException
from mastapy._private._internal.list_with_selected_item import (
    promote_to_list_with_selected_item,
)
from mastapy._private._internal.overridable_constructor import _unpack_overridable
from mastapy._private._internal.python_net import (
    python_net_import,
    pythonnet_method_call,
    pythonnet_property_get,
    pythonnet_property_set,
)
from mastapy._private._internal.sentinels import ListWithSelectedItem_None
from mastapy._private._internal.type_enforcement import enforce_parameter_types

from mastapy._private import _0
from mastapy._private._internal import (
    constructor,
    conversion,
    enum_with_selected_value_runtime,
    overridable_enum_runtime,
    utility,
)
from mastapy._private._internal.implicit import (
    enum_with_selected_value,
    list_with_selected_item,
    overridable,
)
from mastapy._private.nodal_analysis.dev_tools_analyses import _301
from mastapy._private.system_model.fe import _2622, _2647, _2663, _2668

_FE_LINK = python_net_import("SMT.MastaAPI.SystemModel.FE.Links", "FELink")

if TYPE_CHECKING:
    from collections import OrderedDict
    from typing import Any, List, Tuple, Type, TypeVar, Union

    from mastapy._private._internal.typing import PathLike

    from mastapy._private.materials import _371
    from mastapy._private.system_model.connections_and_sockets import _2555
    from mastapy._private.system_model.fe import _2662
    from mastapy._private.system_model.fe.links import (
        _2687,
        _2689,
        _2690,
        _2691,
        _2692,
        _2693,
        _2694,
        _2695,
        _2696,
        _2697,
        _2698,
        _2699,
        _2700,
        _2701,
    )
    from mastapy._private.system_model.part_model import _2737

    Self = TypeVar("Self", bound="FELink")
    CastSelf = TypeVar("CastSelf", bound="FELink._Cast_FELink")


__docformat__ = "restructuredtext en"
__all__ = ("FELink",)


@extended_dataclass(frozen=True, slots=True, weakref_slot=True)
class _Cast_FELink:
    """Special nested class for casting FELink to subclasses."""

    __parent__: "FELink"

    @property
    def electric_machine_stator_fe_link(
        self: "CastSelf",
    ) -> "_2687.ElectricMachineStatorFELink":
        from mastapy._private.system_model.fe.links import _2687

        return self.__parent__._cast(_2687.ElectricMachineStatorFELink)

    @property
    def gear_mesh_fe_link(self: "CastSelf") -> "_2690.GearMeshFELink":
        from mastapy._private.system_model.fe.links import _2690

        return self.__parent__._cast(_2690.GearMeshFELink)

    @property
    def gear_with_duplicated_meshes_fe_link(
        self: "CastSelf",
    ) -> "_2691.GearWithDuplicatedMeshesFELink":
        from mastapy._private.system_model.fe.links import _2691

        return self.__parent__._cast(_2691.GearWithDuplicatedMeshesFELink)

    @property
    def multi_angle_connection_fe_link(
        self: "CastSelf",
    ) -> "_2692.MultiAngleConnectionFELink":
        from mastapy._private.system_model.fe.links import _2692

        return self.__parent__._cast(_2692.MultiAngleConnectionFELink)

    @property
    def multi_node_connector_fe_link(
        self: "CastSelf",
    ) -> "_2693.MultiNodeConnectorFELink":
        from mastapy._private.system_model.fe.links import _2693

        return self.__parent__._cast(_2693.MultiNodeConnectorFELink)

    @property
    def multi_node_fe_link(self: "CastSelf") -> "_2694.MultiNodeFELink":
        from mastapy._private.system_model.fe.links import _2694

        return self.__parent__._cast(_2694.MultiNodeFELink)

    @property
    def planetary_connector_multi_node_fe_link(
        self: "CastSelf",
    ) -> "_2695.PlanetaryConnectorMultiNodeFELink":
        from mastapy._private.system_model.fe.links import _2695

        return self.__parent__._cast(_2695.PlanetaryConnectorMultiNodeFELink)

    @property
    def planet_based_fe_link(self: "CastSelf") -> "_2696.PlanetBasedFELink":
        from mastapy._private.system_model.fe.links import _2696

        return self.__parent__._cast(_2696.PlanetBasedFELink)

    @property
    def planet_carrier_fe_link(self: "CastSelf") -> "_2697.PlanetCarrierFELink":
        from mastapy._private.system_model.fe.links import _2697

        return self.__parent__._cast(_2697.PlanetCarrierFELink)

    @property
    def point_load_fe_link(self: "CastSelf") -> "_2698.PointLoadFELink":
        from mastapy._private.system_model.fe.links import _2698

        return self.__parent__._cast(_2698.PointLoadFELink)

    @property
    def rolling_ring_connection_fe_link(
        self: "CastSelf",
    ) -> "_2699.RollingRingConnectionFELink":
        from mastapy._private.system_model.fe.links import _2699

        return self.__parent__._cast(_2699.RollingRingConnectionFELink)

    @property
    def shaft_hub_connection_fe_link(
        self: "CastSelf",
    ) -> "_2700.ShaftHubConnectionFELink":
        from mastapy._private.system_model.fe.links import _2700

        return self.__parent__._cast(_2700.ShaftHubConnectionFELink)

    @property
    def single_node_fe_link(self: "CastSelf") -> "_2701.SingleNodeFELink":
        from mastapy._private.system_model.fe.links import _2701

        return self.__parent__._cast(_2701.SingleNodeFELink)

    @property
    def fe_link(self: "CastSelf") -> "FELink":
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
class FELink(_0.APIBase):
    """FELink

    This is a mastapy class.
    """

    TYPE: ClassVar["Type"] = _FE_LINK

    wrapped: "Any"

    def __post_init__(self: "Self") -> None:
        """Override of the post initialisation magic method."""
        if not hasattr(self.wrapped, "reference_count"):
            self.wrapped.reference_count = 0

        self.wrapped.reference_count += 1

    @property
    @exception_bridge
    def angle_of_centre_of_connection_patch(
        self: "Self",
    ) -> "overridable.Overridable_float":
        """Overridable[float]"""
        temp = pythonnet_property_get(self.wrapped, "AngleOfCentreOfConnectionPatch")

        if temp is None:
            return 0.0

        return constructor.new_from_mastapy(
            "mastapy._private._internal.implicit.overridable", "Overridable_float"
        )(temp)

    @angle_of_centre_of_connection_patch.setter
    @exception_bridge
    @enforce_parameter_types
    def angle_of_centre_of_connection_patch(
        self: "Self", value: "Union[float, Tuple[float, bool]]"
    ) -> None:
        wrapper_type = overridable.Overridable_float.wrapper_type()
        enclosed_type = overridable.Overridable_float.implicit_type()
        value, is_overridden = _unpack_overridable(value)
        value = wrapper_type[enclosed_type](
            enclosed_type(value) if value is not None else 0.0, is_overridden
        )
        pythonnet_property_set(self.wrapped, "AngleOfCentreOfConnectionPatch", value)

    @property
    @exception_bridge
    def bearing_node_link_option(
        self: "Self",
    ) -> "enum_with_selected_value.EnumWithSelectedValue_BearingNodeOption":
        """EnumWithSelectedValue[mastapy.system_model.fe.BearingNodeOption]"""
        temp = pythonnet_property_get(self.wrapped, "BearingNodeLinkOption")

        if temp is None:
            return None

        value = enum_with_selected_value.EnumWithSelectedValue_BearingNodeOption.wrapped_type()
        return enum_with_selected_value_runtime.create(temp, value)

    @bearing_node_link_option.setter
    @exception_bridge
    @enforce_parameter_types
    def bearing_node_link_option(
        self: "Self", value: "_2622.BearingNodeOption"
    ) -> None:
        wrapper_type = enum_with_selected_value_runtime.ENUM_WITH_SELECTED_VALUE
        enclosed_type = enum_with_selected_value.EnumWithSelectedValue_BearingNodeOption.implicit_type()
        value = conversion.mp_to_pn_enum(value, enclosed_type)
        value = wrapper_type[enclosed_type](value)
        pythonnet_property_set(self.wrapped, "BearingNodeLinkOption", value)

    @property
    @exception_bridge
    def bearing_ring_in_fe(self: "Self") -> "overridable.Overridable_bool":
        """Overridable[bool]"""
        temp = pythonnet_property_get(self.wrapped, "BearingRingInFE")

        if temp is None:
            return False

        return constructor.new_from_mastapy(
            "mastapy._private._internal.implicit.overridable", "Overridable_bool"
        )(temp)

    @bearing_ring_in_fe.setter
    @exception_bridge
    @enforce_parameter_types
    def bearing_ring_in_fe(
        self: "Self", value: "Union[bool, Tuple[bool, bool]]"
    ) -> None:
        wrapper_type = overridable.Overridable_bool.wrapper_type()
        enclosed_type = overridable.Overridable_bool.implicit_type()
        value, is_overridden = _unpack_overridable(value)
        value = wrapper_type[enclosed_type](
            enclosed_type(value) if value is not None else False, is_overridden
        )
        pythonnet_property_set(self.wrapped, "BearingRingInFE", value)

    @property
    @exception_bridge
    def component_name(self: "Self") -> "str":
        """str

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "ComponentName")

        if temp is None:
            return ""

        return temp

    @property
    @exception_bridge
    def connect_to_midside_nodes(self: "Self") -> "bool":
        """bool"""
        temp = pythonnet_property_get(self.wrapped, "ConnectToMidsideNodes")

        if temp is None:
            return False

        return temp

    @connect_to_midside_nodes.setter
    @exception_bridge
    @enforce_parameter_types
    def connect_to_midside_nodes(self: "Self", value: "bool") -> None:
        pythonnet_property_set(
            self.wrapped,
            "ConnectToMidsideNodes",
            bool(value) if value is not None else False,
        )

    @property
    @exception_bridge
    def connection(self: "Self") -> "str":
        """str

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "Connection")

        if temp is None:
            return ""

        return temp

    @property
    @exception_bridge
    def coupling_type(self: "Self") -> "overridable.Overridable_RigidCouplingType":
        """Overridable[mastapy.nodal_analysis.dev_tools_analyses.RigidCouplingType]"""
        temp = pythonnet_property_get(self.wrapped, "CouplingType")

        if temp is None:
            return None

        value = overridable.Overridable_RigidCouplingType.wrapped_type()
        return overridable_enum_runtime.create(temp, value)

    @coupling_type.setter
    @exception_bridge
    @enforce_parameter_types
    def coupling_type(
        self: "Self",
        value: "Union[_301.RigidCouplingType, Tuple[_301.RigidCouplingType, bool]]",
    ) -> None:
        wrapper_type = overridable.Overridable_RigidCouplingType.wrapper_type()
        enclosed_type = overridable.Overridable_RigidCouplingType.implicit_type()
        value, is_overridden = _unpack_overridable(value)
        value = conversion.mp_to_pn_enum(value, enclosed_type)
        value = wrapper_type[enclosed_type](
            value if value is not None else None, is_overridden
        )
        pythonnet_property_set(self.wrapped, "CouplingType", value)

    @property
    @exception_bridge
    def external_node_ids(self: "Self") -> "str":
        """str

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "ExternalNodeIDs")

        if temp is None:
            return ""

        return temp

    @property
    @exception_bridge
    def has_teeth(self: "Self") -> "bool":
        """bool"""
        temp = pythonnet_property_get(self.wrapped, "HasTeeth")

        if temp is None:
            return False

        return temp

    @has_teeth.setter
    @exception_bridge
    @enforce_parameter_types
    def has_teeth(self: "Self", value: "bool") -> None:
        pythonnet_property_set(
            self.wrapped, "HasTeeth", bool(value) if value is not None else False
        )

    @property
    @exception_bridge
    def link_node_source(
        self: "Self",
    ) -> "enum_with_selected_value.EnumWithSelectedValue_LinkNodeSource":
        """EnumWithSelectedValue[mastapy.system_model.fe.LinkNodeSource]"""
        temp = pythonnet_property_get(self.wrapped, "LinkNodeSource")

        if temp is None:
            return None

        value = (
            enum_with_selected_value.EnumWithSelectedValue_LinkNodeSource.wrapped_type()
        )
        return enum_with_selected_value_runtime.create(temp, value)

    @link_node_source.setter
    @exception_bridge
    @enforce_parameter_types
    def link_node_source(self: "Self", value: "_2663.LinkNodeSource") -> None:
        wrapper_type = enum_with_selected_value_runtime.ENUM_WITH_SELECTED_VALUE
        enclosed_type = enum_with_selected_value.EnumWithSelectedValue_LinkNodeSource.implicit_type()
        value = conversion.mp_to_pn_enum(value, enclosed_type)
        value = wrapper_type[enclosed_type](value)
        pythonnet_property_set(self.wrapped, "LinkNodeSource", value)

    @property
    @exception_bridge
    def link_to_get_nodes_from(
        self: "Self",
    ) -> "list_with_selected_item.ListWithSelectedItem_FELink":
        """ListWithSelectedItem[mastapy.system_model.fe.links.FELink]"""
        temp = pythonnet_property_get(self.wrapped, "LinkToGetNodesFrom")

        if temp is None:
            return None

        selected_value = temp.SelectedValue

        if selected_value is None:
            return ListWithSelectedItem_None(temp)

        return constructor.new_from_mastapy(
            "mastapy._private._internal.implicit.list_with_selected_item",
            "ListWithSelectedItem_FELink",
        )(temp)

    @link_to_get_nodes_from.setter
    @exception_bridge
    @enforce_parameter_types
    def link_to_get_nodes_from(self: "Self", value: "FELink") -> None:
        generic_type = (
            list_with_selected_item.ListWithSelectedItem_FELink.implicit_type()
        )
        value = promote_to_list_with_selected_item(value)
        value = conversion.mp_to_pn_smt_list_with_selected_item(
            self, value, generic_type
        )
        pythonnet_property_set(self.wrapped, "LinkToGetNodesFrom", value)

    @property
    @exception_bridge
    def node_cone_search_angle(self: "Self") -> "overridable.Overridable_float":
        """Overridable[float]"""
        temp = pythonnet_property_get(self.wrapped, "NodeConeSearchAngle")

        if temp is None:
            return 0.0

        return constructor.new_from_mastapy(
            "mastapy._private._internal.implicit.overridable", "Overridable_float"
        )(temp)

    @node_cone_search_angle.setter
    @exception_bridge
    @enforce_parameter_types
    def node_cone_search_angle(
        self: "Self", value: "Union[float, Tuple[float, bool]]"
    ) -> None:
        wrapper_type = overridable.Overridable_float.wrapper_type()
        enclosed_type = overridable.Overridable_float.implicit_type()
        value, is_overridden = _unpack_overridable(value)
        value = wrapper_type[enclosed_type](
            enclosed_type(value) if value is not None else 0.0, is_overridden
        )
        pythonnet_property_set(self.wrapped, "NodeConeSearchAngle", value)

    @property
    @exception_bridge
    def node_cylinder_search_axial_offset(
        self: "Self",
    ) -> "overridable.Overridable_float":
        """Overridable[float]"""
        temp = pythonnet_property_get(self.wrapped, "NodeCylinderSearchAxialOffset")

        if temp is None:
            return 0.0

        return constructor.new_from_mastapy(
            "mastapy._private._internal.implicit.overridable", "Overridable_float"
        )(temp)

    @node_cylinder_search_axial_offset.setter
    @exception_bridge
    @enforce_parameter_types
    def node_cylinder_search_axial_offset(
        self: "Self", value: "Union[float, Tuple[float, bool]]"
    ) -> None:
        wrapper_type = overridable.Overridable_float.wrapper_type()
        enclosed_type = overridable.Overridable_float.implicit_type()
        value, is_overridden = _unpack_overridable(value)
        value = wrapper_type[enclosed_type](
            enclosed_type(value) if value is not None else 0.0, is_overridden
        )
        pythonnet_property_set(self.wrapped, "NodeCylinderSearchAxialOffset", value)

    @property
    @exception_bridge
    def node_cylinder_search_diameter(self: "Self") -> "overridable.Overridable_float":
        """Overridable[float]"""
        temp = pythonnet_property_get(self.wrapped, "NodeCylinderSearchDiameter")

        if temp is None:
            return 0.0

        return constructor.new_from_mastapy(
            "mastapy._private._internal.implicit.overridable", "Overridable_float"
        )(temp)

    @node_cylinder_search_diameter.setter
    @exception_bridge
    @enforce_parameter_types
    def node_cylinder_search_diameter(
        self: "Self", value: "Union[float, Tuple[float, bool]]"
    ) -> None:
        wrapper_type = overridable.Overridable_float.wrapper_type()
        enclosed_type = overridable.Overridable_float.implicit_type()
        value, is_overridden = _unpack_overridable(value)
        value = wrapper_type[enclosed_type](
            enclosed_type(value) if value is not None else 0.0, is_overridden
        )
        pythonnet_property_set(self.wrapped, "NodeCylinderSearchDiameter", value)

    @property
    @exception_bridge
    def node_cylinder_search_length(self: "Self") -> "overridable.Overridable_float":
        """Overridable[float]"""
        temp = pythonnet_property_get(self.wrapped, "NodeCylinderSearchLength")

        if temp is None:
            return 0.0

        return constructor.new_from_mastapy(
            "mastapy._private._internal.implicit.overridable", "Overridable_float"
        )(temp)

    @node_cylinder_search_length.setter
    @exception_bridge
    @enforce_parameter_types
    def node_cylinder_search_length(
        self: "Self", value: "Union[float, Tuple[float, bool]]"
    ) -> None:
        wrapper_type = overridable.Overridable_float.wrapper_type()
        enclosed_type = overridable.Overridable_float.implicit_type()
        value, is_overridden = _unpack_overridable(value)
        value = wrapper_type[enclosed_type](
            enclosed_type(value) if value is not None else 0.0, is_overridden
        )
        pythonnet_property_set(self.wrapped, "NodeCylinderSearchLength", value)

    @property
    @exception_bridge
    def node_search_cylinder_thickness(self: "Self") -> "overridable.Overridable_float":
        """Overridable[float]"""
        temp = pythonnet_property_get(self.wrapped, "NodeSearchCylinderThickness")

        if temp is None:
            return 0.0

        return constructor.new_from_mastapy(
            "mastapy._private._internal.implicit.overridable", "Overridable_float"
        )(temp)

    @node_search_cylinder_thickness.setter
    @exception_bridge
    @enforce_parameter_types
    def node_search_cylinder_thickness(
        self: "Self", value: "Union[float, Tuple[float, bool]]"
    ) -> None:
        wrapper_type = overridable.Overridable_float.wrapper_type()
        enclosed_type = overridable.Overridable_float.implicit_type()
        value, is_overridden = _unpack_overridable(value)
        value = wrapper_type[enclosed_type](
            enclosed_type(value) if value is not None else 0.0, is_overridden
        )
        pythonnet_property_set(self.wrapped, "NodeSearchCylinderThickness", value)

    @property
    @exception_bridge
    def node_selection_depth(
        self: "Self",
    ) -> "overridable.Overridable_NodeSelectionDepthOption":
        """Overridable[mastapy.system_model.fe.NodeSelectionDepthOption]"""
        temp = pythonnet_property_get(self.wrapped, "NodeSelectionDepth")

        if temp is None:
            return None

        value = overridable.Overridable_NodeSelectionDepthOption.wrapped_type()
        return overridable_enum_runtime.create(temp, value)

    @node_selection_depth.setter
    @exception_bridge
    @enforce_parameter_types
    def node_selection_depth(
        self: "Self",
        value: "Union[_2668.NodeSelectionDepthOption, Tuple[_2668.NodeSelectionDepthOption, bool]]",
    ) -> None:
        wrapper_type = overridable.Overridable_NodeSelectionDepthOption.wrapper_type()
        enclosed_type = overridable.Overridable_NodeSelectionDepthOption.implicit_type()
        value, is_overridden = _unpack_overridable(value)
        value = conversion.mp_to_pn_enum(value, enclosed_type)
        value = wrapper_type[enclosed_type](
            value if value is not None else None, is_overridden
        )
        pythonnet_property_set(self.wrapped, "NodeSelectionDepth", value)

    @property
    @exception_bridge
    def number_of_axial_nodes(self: "Self") -> "int":
        """int"""
        temp = pythonnet_property_get(self.wrapped, "NumberOfAxialNodes")

        if temp is None:
            return 0

        return temp

    @number_of_axial_nodes.setter
    @exception_bridge
    @enforce_parameter_types
    def number_of_axial_nodes(self: "Self", value: "int") -> None:
        pythonnet_property_set(
            self.wrapped, "NumberOfAxialNodes", int(value) if value is not None else 0
        )

    @property
    @exception_bridge
    def number_of_nodes_in_full_fe_mesh(self: "Self") -> "int":
        """int

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "NumberOfNodesInFullFEMesh")

        if temp is None:
            return 0

        return temp

    @property
    @exception_bridge
    def number_of_nodes_in_ring(self: "Self") -> "overridable.Overridable_int":
        """Overridable[int]"""
        temp = pythonnet_property_get(self.wrapped, "NumberOfNodesInRing")

        if temp is None:
            return 0

        return constructor.new_from_mastapy(
            "mastapy._private._internal.implicit.overridable", "Overridable_int"
        )(temp)

    @number_of_nodes_in_ring.setter
    @exception_bridge
    @enforce_parameter_types
    def number_of_nodes_in_ring(
        self: "Self", value: "Union[int, Tuple[int, bool]]"
    ) -> None:
        wrapper_type = overridable.Overridable_int.wrapper_type()
        enclosed_type = overridable.Overridable_int.implicit_type()
        value, is_overridden = _unpack_overridable(value)
        value = wrapper_type[enclosed_type](
            enclosed_type(value) if value is not None else 0, is_overridden
        )
        pythonnet_property_set(self.wrapped, "NumberOfNodesInRing", value)

    @property
    @exception_bridge
    def span_of_patch(self: "Self") -> "overridable.Overridable_float":
        """Overridable[float]"""
        temp = pythonnet_property_get(self.wrapped, "SpanOfPatch")

        if temp is None:
            return 0.0

        return constructor.new_from_mastapy(
            "mastapy._private._internal.implicit.overridable", "Overridable_float"
        )(temp)

    @span_of_patch.setter
    @exception_bridge
    @enforce_parameter_types
    def span_of_patch(self: "Self", value: "Union[float, Tuple[float, bool]]") -> None:
        wrapper_type = overridable.Overridable_float.wrapper_type()
        enclosed_type = overridable.Overridable_float.implicit_type()
        value, is_overridden = _unpack_overridable(value)
        value = wrapper_type[enclosed_type](
            enclosed_type(value) if value is not None else 0.0, is_overridden
        )
        pythonnet_property_set(self.wrapped, "SpanOfPatch", value)

    @property
    @exception_bridge
    def support_material_id(
        self: "Self",
    ) -> "list_with_selected_item.ListWithSelectedItem_int":
        """ListWithSelectedItem[int]"""
        temp = pythonnet_property_get(self.wrapped, "SupportMaterialID")

        if temp is None:
            return 0

        selected_value = temp.SelectedValue

        if selected_value is None:
            return ListWithSelectedItem_None(temp)

        return constructor.new_from_mastapy(
            "mastapy._private._internal.implicit.list_with_selected_item",
            "ListWithSelectedItem_int",
        )(temp)

    @support_material_id.setter
    @exception_bridge
    @enforce_parameter_types
    def support_material_id(self: "Self", value: "int") -> None:
        generic_type = list_with_selected_item.ListWithSelectedItem_int.implicit_type()
        value = promote_to_list_with_selected_item(value)
        value = conversion.mp_to_pn_smt_list_with_selected_item(
            self, value, generic_type
        )
        pythonnet_property_set(self.wrapped, "SupportMaterialID", value)

    @property
    @exception_bridge
    def width_of_axial_patch(self: "Self") -> "overridable.Overridable_float":
        """Overridable[float]"""
        temp = pythonnet_property_get(self.wrapped, "WidthOfAxialPatch")

        if temp is None:
            return 0.0

        return constructor.new_from_mastapy(
            "mastapy._private._internal.implicit.overridable", "Overridable_float"
        )(temp)

    @width_of_axial_patch.setter
    @exception_bridge
    @enforce_parameter_types
    def width_of_axial_patch(
        self: "Self", value: "Union[float, Tuple[float, bool]]"
    ) -> None:
        wrapper_type = overridable.Overridable_float.wrapper_type()
        enclosed_type = overridable.Overridable_float.implicit_type()
        value, is_overridden = _unpack_overridable(value)
        value = wrapper_type[enclosed_type](
            enclosed_type(value) if value is not None else 0.0, is_overridden
        )
        pythonnet_property_set(self.wrapped, "WidthOfAxialPatch", value)

    @property
    @exception_bridge
    def alignment_in_component_coordinate_system(
        self: "Self",
    ) -> "_2662.LinkComponentAxialPositionErrorReporter":
        """mastapy.system_model.fe.LinkComponentAxialPositionErrorReporter

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(
            self.wrapped, "AlignmentInComponentCoordinateSystem"
        )

        if temp is None:
            return None

        type_ = temp.GetType()
        return constructor.new(type_.Namespace, type_.Name)(temp)

    @property
    @exception_bridge
    def alignment_in_fe_coordinate_system(
        self: "Self",
    ) -> "_2662.LinkComponentAxialPositionErrorReporter":
        """mastapy.system_model.fe.LinkComponentAxialPositionErrorReporter

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "AlignmentInFECoordinateSystem")

        if temp is None:
            return None

        type_ = temp.GetType()
        return constructor.new(type_.Namespace, type_.Name)(temp)

    @property
    @exception_bridge
    def alignment_in_world_coordinate_system(
        self: "Self",
    ) -> "_2662.LinkComponentAxialPositionErrorReporter":
        """mastapy.system_model.fe.LinkComponentAxialPositionErrorReporter

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "AlignmentInWorldCoordinateSystem")

        if temp is None:
            return None

        type_ = temp.GetType()
        return constructor.new(type_.Namespace, type_.Name)(temp)

    @property
    @exception_bridge
    def component(self: "Self") -> "_2737.MountableComponent":
        """mastapy.system_model.part_model.MountableComponent

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "Component")

        if temp is None:
            return None

        type_ = temp.GetType()
        return constructor.new(type_.Namespace, type_.Name)(temp)

    @property
    @exception_bridge
    def shape_connection_settings(
        self: "Self",
    ) -> "_2689.FlexibleInterpolationDefinitionSettings":
        """mastapy.system_model.fe.links.FlexibleInterpolationDefinitionSettings

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "ShapeConnectionSettings")

        if temp is None:
            return None

        type_ = temp.GetType()
        return constructor.new(type_.Namespace, type_.Name)(temp)

    @property
    @exception_bridge
    def socket(self: "Self") -> "_2555.Socket":
        """mastapy.system_model.connections_and_sockets.Socket

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "Socket")

        if temp is None:
            return None

        type_ = temp.GetType()
        return constructor.new(type_.Namespace, type_.Name)(temp)

    @property
    @exception_bridge
    def support_material(self: "Self") -> "_371.Material":
        """mastapy.materials.Material

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "SupportMaterial")

        if temp is None:
            return None

        type_ = temp.GetType()
        return constructor.new(type_.Namespace, type_.Name)(temp)

    @property
    @exception_bridge
    def nodes(self: "Self") -> "List[_2647.FESubstructureNode]":
        """List[mastapy.system_model.fe.FESubstructureNode]

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "Nodes")

        if temp is None:
            return None

        value = conversion.pn_to_mp_objects_in_list(temp)

        if value is None:
            return None

        return value

    @property
    @exception_bridge
    def report_names(self: "Self") -> "List[str]":
        """List[str]

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "ReportNames")

        if temp is None:
            return None

        value = conversion.pn_to_mp_objects_in_list(temp, str)

        if value is None:
            return None

        return value

    @exception_bridge
    def nodes_grouped_by_angle(
        self: "Self",
    ) -> "OrderedDict[float, List[_2647.FESubstructureNode]]":
        """OrderedDict[float, List[mastapy.system_model.fe.FESubstructureNode]]"""
        return conversion.pn_to_mp_objects_in_list_in_ordered_dict(
            pythonnet_method_call(self.wrapped, "NodesGroupedByAngle"), float
        )

    @exception_bridge
    @enforce_parameter_types
    def add_or_replace_node(self: "Self", node: "_2647.FESubstructureNode") -> None:
        """Method does not return.

        Args:
            node (mastapy.system_model.fe.FESubstructureNode)
        """
        pythonnet_method_call(
            self.wrapped, "AddOrReplaceNode", node.wrapped if node else None
        )

    @exception_bridge
    def remove_all_nodes(self: "Self") -> None:
        """Method does not return."""
        pythonnet_method_call(self.wrapped, "RemoveAllNodes")

    @exception_bridge
    @enforce_parameter_types
    def output_default_report_to(self: "Self", file_path: "PathLike") -> None:
        """Method does not return.

        Args:
            file_path (PathLike)
        """
        file_path = str(file_path)
        pythonnet_method_call(self.wrapped, "OutputDefaultReportTo", file_path)

    @exception_bridge
    def get_default_report_with_encoded_images(self: "Self") -> "str":
        """str"""
        method_result = pythonnet_method_call(
            self.wrapped, "GetDefaultReportWithEncodedImages"
        )
        return method_result

    @exception_bridge
    @enforce_parameter_types
    def output_active_report_to(self: "Self", file_path: "PathLike") -> None:
        """Method does not return.

        Args:
            file_path (PathLike)
        """
        file_path = str(file_path)
        pythonnet_method_call(self.wrapped, "OutputActiveReportTo", file_path)

    @exception_bridge
    @enforce_parameter_types
    def output_active_report_as_text_to(self: "Self", file_path: "PathLike") -> None:
        """Method does not return.

        Args:
            file_path (PathLike)
        """
        file_path = str(file_path)
        pythonnet_method_call(self.wrapped, "OutputActiveReportAsTextTo", file_path)

    @exception_bridge
    def get_active_report_with_encoded_images(self: "Self") -> "str":
        """str"""
        method_result = pythonnet_method_call(
            self.wrapped, "GetActiveReportWithEncodedImages"
        )
        return method_result

    @exception_bridge
    @enforce_parameter_types
    def output_named_report_to(
        self: "Self", report_name: "str", file_path: "PathLike"
    ) -> None:
        """Method does not return.

        Args:
            report_name (str)
            file_path (PathLike)
        """
        report_name = str(report_name)
        file_path = str(file_path)
        pythonnet_method_call(
            self.wrapped,
            "OutputNamedReportTo",
            report_name if report_name else "",
            file_path,
        )

    @exception_bridge
    @enforce_parameter_types
    def output_named_report_as_masta_report(
        self: "Self", report_name: "str", file_path: "PathLike"
    ) -> None:
        """Method does not return.

        Args:
            report_name (str)
            file_path (PathLike)
        """
        report_name = str(report_name)
        file_path = str(file_path)
        pythonnet_method_call(
            self.wrapped,
            "OutputNamedReportAsMastaReport",
            report_name if report_name else "",
            file_path,
        )

    @exception_bridge
    @enforce_parameter_types
    def output_named_report_as_text_to(
        self: "Self", report_name: "str", file_path: "PathLike"
    ) -> None:
        """Method does not return.

        Args:
            report_name (str)
            file_path (PathLike)
        """
        report_name = str(report_name)
        file_path = str(file_path)
        pythonnet_method_call(
            self.wrapped,
            "OutputNamedReportAsTextTo",
            report_name if report_name else "",
            file_path,
        )

    @exception_bridge
    @enforce_parameter_types
    def get_named_report_with_encoded_images(self: "Self", report_name: "str") -> "str":
        """str

        Args:
            report_name (str)
        """
        report_name = str(report_name)
        method_result = pythonnet_method_call(
            self.wrapped,
            "GetNamedReportWithEncodedImages",
            report_name if report_name else "",
        )
        return method_result

    @property
    def cast_to(self: "Self") -> "_Cast_FELink":
        """Cast to another type.

        Returns:
            _Cast_FELink
        """
        return _Cast_FELink(self)
