"""Subpackage."""

from typing import TYPE_CHECKING as __tc

if __tc:
    from mastapy._private.gears.gear_designs.cylindrical.micro_geometry._1229 import (
        CylindricalGearBiasModification,
    )
    from mastapy._private.gears.gear_designs.cylindrical.micro_geometry._1230 import (
        CylindricalGearCommonFlankMicroGeometry,
    )
    from mastapy._private.gears.gear_designs.cylindrical.micro_geometry._1231 import (
        CylindricalGearFlankMicroGeometry,
    )
    from mastapy._private.gears.gear_designs.cylindrical.micro_geometry._1232 import (
        CylindricalGearLeadModification,
    )
    from mastapy._private.gears.gear_designs.cylindrical.micro_geometry._1233 import (
        CylindricalGearLeadModificationAtProfilePosition,
    )
    from mastapy._private.gears.gear_designs.cylindrical.micro_geometry._1234 import (
        CylindricalGearMeshMicroGeometry,
    )
    from mastapy._private.gears.gear_designs.cylindrical.micro_geometry._1235 import (
        CylindricalGearMeshMicroGeometryDutyCycle,
    )
    from mastapy._private.gears.gear_designs.cylindrical.micro_geometry._1236 import (
        CylindricalGearMicroGeometry,
    )
    from mastapy._private.gears.gear_designs.cylindrical.micro_geometry._1237 import (
        CylindricalGearMicroGeometryBase,
    )
    from mastapy._private.gears.gear_designs.cylindrical.micro_geometry._1238 import (
        CylindricalGearMicroGeometryDutyCycle,
    )
    from mastapy._private.gears.gear_designs.cylindrical.micro_geometry._1239 import (
        CylindricalGearMicroGeometryMap,
    )
    from mastapy._private.gears.gear_designs.cylindrical.micro_geometry._1240 import (
        CylindricalGearMicroGeometryPerTooth,
    )
    from mastapy._private.gears.gear_designs.cylindrical.micro_geometry._1241 import (
        CylindricalGearProfileModification,
    )
    from mastapy._private.gears.gear_designs.cylindrical.micro_geometry._1242 import (
        CylindricalGearProfileModificationAtFaceWidthPosition,
    )
    from mastapy._private.gears.gear_designs.cylindrical.micro_geometry._1243 import (
        CylindricalGearSetMicroGeometry,
    )
    from mastapy._private.gears.gear_designs.cylindrical.micro_geometry._1244 import (
        CylindricalGearSetMicroGeometryDutyCycle,
    )
    from mastapy._private.gears.gear_designs.cylindrical.micro_geometry._1245 import (
        CylindricalGearToothMicroGeometry,
    )
    from mastapy._private.gears.gear_designs.cylindrical.micro_geometry._1246 import (
        CylindricalGearTriangularEndModification,
    )
    from mastapy._private.gears.gear_designs.cylindrical.micro_geometry._1247 import (
        CylindricalGearTriangularEndModificationAtOrientation,
    )
    from mastapy._private.gears.gear_designs.cylindrical.micro_geometry._1248 import (
        DrawDefiningGearOrBoth,
    )
    from mastapy._private.gears.gear_designs.cylindrical.micro_geometry._1249 import (
        GearAlignment,
    )
    from mastapy._private.gears.gear_designs.cylindrical.micro_geometry._1250 import (
        LeadFormReliefWithDeviation,
    )
    from mastapy._private.gears.gear_designs.cylindrical.micro_geometry._1251 import (
        LeadModificationForCustomer102CAD,
    )
    from mastapy._private.gears.gear_designs.cylindrical.micro_geometry._1252 import (
        LeadReliefSpecificationForCustomer102,
    )
    from mastapy._private.gears.gear_designs.cylindrical.micro_geometry._1253 import (
        LeadReliefWithDeviation,
    )
    from mastapy._private.gears.gear_designs.cylindrical.micro_geometry._1254 import (
        LeadSlopeReliefWithDeviation,
    )
    from mastapy._private.gears.gear_designs.cylindrical.micro_geometry._1255 import (
        LinearCylindricalGearTriangularEndModification,
    )
    from mastapy._private.gears.gear_designs.cylindrical.micro_geometry._1256 import (
        MeasuredMapDataTypes,
    )
    from mastapy._private.gears.gear_designs.cylindrical.micro_geometry._1257 import (
        MeshAlignment,
    )
    from mastapy._private.gears.gear_designs.cylindrical.micro_geometry._1258 import (
        MeshedCylindricalGearFlankMicroGeometry,
    )
    from mastapy._private.gears.gear_designs.cylindrical.micro_geometry._1259 import (
        MeshedCylindricalGearMicroGeometry,
    )
    from mastapy._private.gears.gear_designs.cylindrical.micro_geometry._1260 import (
        MicroGeometryLeadToleranceChartView,
    )
    from mastapy._private.gears.gear_designs.cylindrical.micro_geometry._1261 import (
        MicroGeometryViewingOptions,
    )
    from mastapy._private.gears.gear_designs.cylindrical.micro_geometry._1262 import (
        ModificationForCustomer102CAD,
    )
    from mastapy._private.gears.gear_designs.cylindrical.micro_geometry._1263 import (
        ParabolicCylindricalGearTriangularEndModification,
    )
    from mastapy._private.gears.gear_designs.cylindrical.micro_geometry._1264 import (
        ProfileFormReliefWithDeviation,
    )
    from mastapy._private.gears.gear_designs.cylindrical.micro_geometry._1265 import (
        ProfileModificationForCustomer102CAD,
    )
    from mastapy._private.gears.gear_designs.cylindrical.micro_geometry._1266 import (
        ProfileReliefSpecificationForCustomer102,
    )
    from mastapy._private.gears.gear_designs.cylindrical.micro_geometry._1267 import (
        ProfileReliefWithDeviation,
    )
    from mastapy._private.gears.gear_designs.cylindrical.micro_geometry._1268 import (
        ProfileSlopeReliefWithDeviation,
    )
    from mastapy._private.gears.gear_designs.cylindrical.micro_geometry._1269 import (
        ReliefWithDeviation,
    )
    from mastapy._private.gears.gear_designs.cylindrical.micro_geometry._1270 import (
        SingleCylindricalGearTriangularEndModification,
    )
    from mastapy._private.gears.gear_designs.cylindrical.micro_geometry._1271 import (
        TotalLeadReliefWithDeviation,
    )
    from mastapy._private.gears.gear_designs.cylindrical.micro_geometry._1272 import (
        TotalProfileReliefWithDeviation,
    )
else:
    import sys as __sys

    from lazy_imports import LazyImporter as __LazyImporter

    __import_structure = {
        "_private.gears.gear_designs.cylindrical.micro_geometry._1229": [
            "CylindricalGearBiasModification"
        ],
        "_private.gears.gear_designs.cylindrical.micro_geometry._1230": [
            "CylindricalGearCommonFlankMicroGeometry"
        ],
        "_private.gears.gear_designs.cylindrical.micro_geometry._1231": [
            "CylindricalGearFlankMicroGeometry"
        ],
        "_private.gears.gear_designs.cylindrical.micro_geometry._1232": [
            "CylindricalGearLeadModification"
        ],
        "_private.gears.gear_designs.cylindrical.micro_geometry._1233": [
            "CylindricalGearLeadModificationAtProfilePosition"
        ],
        "_private.gears.gear_designs.cylindrical.micro_geometry._1234": [
            "CylindricalGearMeshMicroGeometry"
        ],
        "_private.gears.gear_designs.cylindrical.micro_geometry._1235": [
            "CylindricalGearMeshMicroGeometryDutyCycle"
        ],
        "_private.gears.gear_designs.cylindrical.micro_geometry._1236": [
            "CylindricalGearMicroGeometry"
        ],
        "_private.gears.gear_designs.cylindrical.micro_geometry._1237": [
            "CylindricalGearMicroGeometryBase"
        ],
        "_private.gears.gear_designs.cylindrical.micro_geometry._1238": [
            "CylindricalGearMicroGeometryDutyCycle"
        ],
        "_private.gears.gear_designs.cylindrical.micro_geometry._1239": [
            "CylindricalGearMicroGeometryMap"
        ],
        "_private.gears.gear_designs.cylindrical.micro_geometry._1240": [
            "CylindricalGearMicroGeometryPerTooth"
        ],
        "_private.gears.gear_designs.cylindrical.micro_geometry._1241": [
            "CylindricalGearProfileModification"
        ],
        "_private.gears.gear_designs.cylindrical.micro_geometry._1242": [
            "CylindricalGearProfileModificationAtFaceWidthPosition"
        ],
        "_private.gears.gear_designs.cylindrical.micro_geometry._1243": [
            "CylindricalGearSetMicroGeometry"
        ],
        "_private.gears.gear_designs.cylindrical.micro_geometry._1244": [
            "CylindricalGearSetMicroGeometryDutyCycle"
        ],
        "_private.gears.gear_designs.cylindrical.micro_geometry._1245": [
            "CylindricalGearToothMicroGeometry"
        ],
        "_private.gears.gear_designs.cylindrical.micro_geometry._1246": [
            "CylindricalGearTriangularEndModification"
        ],
        "_private.gears.gear_designs.cylindrical.micro_geometry._1247": [
            "CylindricalGearTriangularEndModificationAtOrientation"
        ],
        "_private.gears.gear_designs.cylindrical.micro_geometry._1248": [
            "DrawDefiningGearOrBoth"
        ],
        "_private.gears.gear_designs.cylindrical.micro_geometry._1249": [
            "GearAlignment"
        ],
        "_private.gears.gear_designs.cylindrical.micro_geometry._1250": [
            "LeadFormReliefWithDeviation"
        ],
        "_private.gears.gear_designs.cylindrical.micro_geometry._1251": [
            "LeadModificationForCustomer102CAD"
        ],
        "_private.gears.gear_designs.cylindrical.micro_geometry._1252": [
            "LeadReliefSpecificationForCustomer102"
        ],
        "_private.gears.gear_designs.cylindrical.micro_geometry._1253": [
            "LeadReliefWithDeviation"
        ],
        "_private.gears.gear_designs.cylindrical.micro_geometry._1254": [
            "LeadSlopeReliefWithDeviation"
        ],
        "_private.gears.gear_designs.cylindrical.micro_geometry._1255": [
            "LinearCylindricalGearTriangularEndModification"
        ],
        "_private.gears.gear_designs.cylindrical.micro_geometry._1256": [
            "MeasuredMapDataTypes"
        ],
        "_private.gears.gear_designs.cylindrical.micro_geometry._1257": [
            "MeshAlignment"
        ],
        "_private.gears.gear_designs.cylindrical.micro_geometry._1258": [
            "MeshedCylindricalGearFlankMicroGeometry"
        ],
        "_private.gears.gear_designs.cylindrical.micro_geometry._1259": [
            "MeshedCylindricalGearMicroGeometry"
        ],
        "_private.gears.gear_designs.cylindrical.micro_geometry._1260": [
            "MicroGeometryLeadToleranceChartView"
        ],
        "_private.gears.gear_designs.cylindrical.micro_geometry._1261": [
            "MicroGeometryViewingOptions"
        ],
        "_private.gears.gear_designs.cylindrical.micro_geometry._1262": [
            "ModificationForCustomer102CAD"
        ],
        "_private.gears.gear_designs.cylindrical.micro_geometry._1263": [
            "ParabolicCylindricalGearTriangularEndModification"
        ],
        "_private.gears.gear_designs.cylindrical.micro_geometry._1264": [
            "ProfileFormReliefWithDeviation"
        ],
        "_private.gears.gear_designs.cylindrical.micro_geometry._1265": [
            "ProfileModificationForCustomer102CAD"
        ],
        "_private.gears.gear_designs.cylindrical.micro_geometry._1266": [
            "ProfileReliefSpecificationForCustomer102"
        ],
        "_private.gears.gear_designs.cylindrical.micro_geometry._1267": [
            "ProfileReliefWithDeviation"
        ],
        "_private.gears.gear_designs.cylindrical.micro_geometry._1268": [
            "ProfileSlopeReliefWithDeviation"
        ],
        "_private.gears.gear_designs.cylindrical.micro_geometry._1269": [
            "ReliefWithDeviation"
        ],
        "_private.gears.gear_designs.cylindrical.micro_geometry._1270": [
            "SingleCylindricalGearTriangularEndModification"
        ],
        "_private.gears.gear_designs.cylindrical.micro_geometry._1271": [
            "TotalLeadReliefWithDeviation"
        ],
        "_private.gears.gear_designs.cylindrical.micro_geometry._1272": [
            "TotalProfileReliefWithDeviation"
        ],
    }

    __sys.modules[__name__] = __LazyImporter(
        "mastapy",
        globals()["__file__"],
        __import_structure,
    )

__all__ = (
    "CylindricalGearBiasModification",
    "CylindricalGearCommonFlankMicroGeometry",
    "CylindricalGearFlankMicroGeometry",
    "CylindricalGearLeadModification",
    "CylindricalGearLeadModificationAtProfilePosition",
    "CylindricalGearMeshMicroGeometry",
    "CylindricalGearMeshMicroGeometryDutyCycle",
    "CylindricalGearMicroGeometry",
    "CylindricalGearMicroGeometryBase",
    "CylindricalGearMicroGeometryDutyCycle",
    "CylindricalGearMicroGeometryMap",
    "CylindricalGearMicroGeometryPerTooth",
    "CylindricalGearProfileModification",
    "CylindricalGearProfileModificationAtFaceWidthPosition",
    "CylindricalGearSetMicroGeometry",
    "CylindricalGearSetMicroGeometryDutyCycle",
    "CylindricalGearToothMicroGeometry",
    "CylindricalGearTriangularEndModification",
    "CylindricalGearTriangularEndModificationAtOrientation",
    "DrawDefiningGearOrBoth",
    "GearAlignment",
    "LeadFormReliefWithDeviation",
    "LeadModificationForCustomer102CAD",
    "LeadReliefSpecificationForCustomer102",
    "LeadReliefWithDeviation",
    "LeadSlopeReliefWithDeviation",
    "LinearCylindricalGearTriangularEndModification",
    "MeasuredMapDataTypes",
    "MeshAlignment",
    "MeshedCylindricalGearFlankMicroGeometry",
    "MeshedCylindricalGearMicroGeometry",
    "MicroGeometryLeadToleranceChartView",
    "MicroGeometryViewingOptions",
    "ModificationForCustomer102CAD",
    "ParabolicCylindricalGearTriangularEndModification",
    "ProfileFormReliefWithDeviation",
    "ProfileModificationForCustomer102CAD",
    "ProfileReliefSpecificationForCustomer102",
    "ProfileReliefWithDeviation",
    "ProfileSlopeReliefWithDeviation",
    "ReliefWithDeviation",
    "SingleCylindricalGearTriangularEndModification",
    "TotalLeadReliefWithDeviation",
    "TotalProfileReliefWithDeviation",
)
