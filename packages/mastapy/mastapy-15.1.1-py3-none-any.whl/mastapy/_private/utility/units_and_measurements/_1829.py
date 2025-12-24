"""MeasurementBase"""

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
from mastapy._private._internal import constructor, conversion, utility
from mastapy._private._internal.implicit import list_with_selected_item, overridable
from mastapy._private.utility.units_and_measurements import _1834

_MEASUREMENT_BASE = python_net_import(
    "SMT.MastaAPI.Utility.UnitsAndMeasurements", "MeasurementBase"
)

if TYPE_CHECKING:
    from typing import Any, List, Tuple, Type, TypeVar, Union

    from mastapy._private._internal.typing import PathLike

    from mastapy._private.utility import _1821
    from mastapy._private.utility.units_and_measurements.measurements import (
        _1836,
        _1837,
        _1838,
        _1839,
        _1840,
        _1841,
        _1842,
        _1843,
        _1844,
        _1845,
        _1846,
        _1847,
        _1848,
        _1849,
        _1850,
        _1851,
        _1852,
        _1853,
        _1854,
        _1855,
        _1856,
        _1857,
        _1858,
        _1859,
        _1860,
        _1861,
        _1862,
        _1863,
        _1864,
        _1865,
        _1866,
        _1867,
        _1868,
        _1869,
        _1870,
        _1871,
        _1872,
        _1873,
        _1874,
        _1875,
        _1876,
        _1877,
        _1878,
        _1879,
        _1880,
        _1881,
        _1882,
        _1883,
        _1884,
        _1885,
        _1886,
        _1887,
        _1888,
        _1889,
        _1890,
        _1891,
        _1892,
        _1893,
        _1894,
        _1895,
        _1896,
        _1897,
        _1898,
        _1899,
        _1900,
        _1901,
        _1902,
        _1903,
        _1904,
        _1905,
        _1906,
        _1907,
        _1908,
        _1909,
        _1910,
        _1911,
        _1912,
        _1913,
        _1914,
        _1915,
        _1916,
        _1917,
        _1918,
        _1919,
        _1920,
        _1921,
        _1922,
        _1923,
        _1924,
        _1925,
        _1926,
        _1927,
        _1928,
        _1929,
        _1930,
        _1931,
        _1932,
        _1933,
        _1934,
        _1935,
        _1936,
        _1937,
        _1938,
        _1939,
        _1940,
        _1941,
        _1942,
        _1943,
        _1944,
        _1945,
        _1946,
        _1947,
        _1948,
        _1949,
        _1950,
        _1951,
        _1952,
        _1953,
        _1954,
        _1955,
        _1956,
        _1957,
        _1958,
        _1959,
        _1960,
        _1961,
        _1962,
        _1963,
        _1964,
        _1965,
    )

    Self = TypeVar("Self", bound="MeasurementBase")
    CastSelf = TypeVar("CastSelf", bound="MeasurementBase._Cast_MeasurementBase")


__docformat__ = "restructuredtext en"
__all__ = ("MeasurementBase",)


@extended_dataclass(frozen=True, slots=True, weakref_slot=True)
class _Cast_MeasurementBase:
    """Special nested class for casting MeasurementBase to subclasses."""

    __parent__: "MeasurementBase"

    @property
    def acceleration(self: "CastSelf") -> "_1836.Acceleration":
        from mastapy._private.utility.units_and_measurements.measurements import _1836

        return self.__parent__._cast(_1836.Acceleration)

    @property
    def angle(self: "CastSelf") -> "_1837.Angle":
        from mastapy._private.utility.units_and_measurements.measurements import _1837

        return self.__parent__._cast(_1837.Angle)

    @property
    def angle_per_unit_temperature(self: "CastSelf") -> "_1838.AnglePerUnitTemperature":
        from mastapy._private.utility.units_and_measurements.measurements import _1838

        return self.__parent__._cast(_1838.AnglePerUnitTemperature)

    @property
    def angle_small(self: "CastSelf") -> "_1839.AngleSmall":
        from mastapy._private.utility.units_and_measurements.measurements import _1839

        return self.__parent__._cast(_1839.AngleSmall)

    @property
    def angle_very_small(self: "CastSelf") -> "_1840.AngleVerySmall":
        from mastapy._private.utility.units_and_measurements.measurements import _1840

        return self.__parent__._cast(_1840.AngleVerySmall)

    @property
    def angular_acceleration(self: "CastSelf") -> "_1841.AngularAcceleration":
        from mastapy._private.utility.units_and_measurements.measurements import _1841

        return self.__parent__._cast(_1841.AngularAcceleration)

    @property
    def angular_compliance(self: "CastSelf") -> "_1842.AngularCompliance":
        from mastapy._private.utility.units_and_measurements.measurements import _1842

        return self.__parent__._cast(_1842.AngularCompliance)

    @property
    def angular_jerk(self: "CastSelf") -> "_1843.AngularJerk":
        from mastapy._private.utility.units_and_measurements.measurements import _1843

        return self.__parent__._cast(_1843.AngularJerk)

    @property
    def angular_stiffness(self: "CastSelf") -> "_1844.AngularStiffness":
        from mastapy._private.utility.units_and_measurements.measurements import _1844

        return self.__parent__._cast(_1844.AngularStiffness)

    @property
    def angular_velocity(self: "CastSelf") -> "_1845.AngularVelocity":
        from mastapy._private.utility.units_and_measurements.measurements import _1845

        return self.__parent__._cast(_1845.AngularVelocity)

    @property
    def area(self: "CastSelf") -> "_1846.Area":
        from mastapy._private.utility.units_and_measurements.measurements import _1846

        return self.__parent__._cast(_1846.Area)

    @property
    def area_small(self: "CastSelf") -> "_1847.AreaSmall":
        from mastapy._private.utility.units_and_measurements.measurements import _1847

        return self.__parent__._cast(_1847.AreaSmall)

    @property
    def carbon_emission_factor(self: "CastSelf") -> "_1848.CarbonEmissionFactor":
        from mastapy._private.utility.units_and_measurements.measurements import _1848

        return self.__parent__._cast(_1848.CarbonEmissionFactor)

    @property
    def current_density(self: "CastSelf") -> "_1849.CurrentDensity":
        from mastapy._private.utility.units_and_measurements.measurements import _1849

        return self.__parent__._cast(_1849.CurrentDensity)

    @property
    def current_per_length(self: "CastSelf") -> "_1850.CurrentPerLength":
        from mastapy._private.utility.units_and_measurements.measurements import _1850

        return self.__parent__._cast(_1850.CurrentPerLength)

    @property
    def cycles(self: "CastSelf") -> "_1851.Cycles":
        from mastapy._private.utility.units_and_measurements.measurements import _1851

        return self.__parent__._cast(_1851.Cycles)

    @property
    def damage(self: "CastSelf") -> "_1852.Damage":
        from mastapy._private.utility.units_and_measurements.measurements import _1852

        return self.__parent__._cast(_1852.Damage)

    @property
    def damage_rate(self: "CastSelf") -> "_1853.DamageRate":
        from mastapy._private.utility.units_and_measurements.measurements import _1853

        return self.__parent__._cast(_1853.DamageRate)

    @property
    def data_size(self: "CastSelf") -> "_1854.DataSize":
        from mastapy._private.utility.units_and_measurements.measurements import _1854

        return self.__parent__._cast(_1854.DataSize)

    @property
    def decibel(self: "CastSelf") -> "_1855.Decibel":
        from mastapy._private.utility.units_and_measurements.measurements import _1855

        return self.__parent__._cast(_1855.Decibel)

    @property
    def density(self: "CastSelf") -> "_1856.Density":
        from mastapy._private.utility.units_and_measurements.measurements import _1856

        return self.__parent__._cast(_1856.Density)

    @property
    def electrical_resistance(self: "CastSelf") -> "_1857.ElectricalResistance":
        from mastapy._private.utility.units_and_measurements.measurements import _1857

        return self.__parent__._cast(_1857.ElectricalResistance)

    @property
    def electrical_resistivity(self: "CastSelf") -> "_1858.ElectricalResistivity":
        from mastapy._private.utility.units_and_measurements.measurements import _1858

        return self.__parent__._cast(_1858.ElectricalResistivity)

    @property
    def electric_current(self: "CastSelf") -> "_1859.ElectricCurrent":
        from mastapy._private.utility.units_and_measurements.measurements import _1859

        return self.__parent__._cast(_1859.ElectricCurrent)

    @property
    def energy(self: "CastSelf") -> "_1860.Energy":
        from mastapy._private.utility.units_and_measurements.measurements import _1860

        return self.__parent__._cast(_1860.Energy)

    @property
    def energy_per_unit_area(self: "CastSelf") -> "_1861.EnergyPerUnitArea":
        from mastapy._private.utility.units_and_measurements.measurements import _1861

        return self.__parent__._cast(_1861.EnergyPerUnitArea)

    @property
    def energy_per_unit_area_small(self: "CastSelf") -> "_1862.EnergyPerUnitAreaSmall":
        from mastapy._private.utility.units_and_measurements.measurements import _1862

        return self.__parent__._cast(_1862.EnergyPerUnitAreaSmall)

    @property
    def energy_small(self: "CastSelf") -> "_1863.EnergySmall":
        from mastapy._private.utility.units_and_measurements.measurements import _1863

        return self.__parent__._cast(_1863.EnergySmall)

    @property
    def enum(self: "CastSelf") -> "_1864.Enum":
        from mastapy._private.utility.units_and_measurements.measurements import _1864

        return self.__parent__._cast(_1864.Enum)

    @property
    def flow_rate(self: "CastSelf") -> "_1865.FlowRate":
        from mastapy._private.utility.units_and_measurements.measurements import _1865

        return self.__parent__._cast(_1865.FlowRate)

    @property
    def flow_resistance(self: "CastSelf") -> "_1866.FlowResistance":
        from mastapy._private.utility.units_and_measurements.measurements import _1866

        return self.__parent__._cast(_1866.FlowResistance)

    @property
    def force(self: "CastSelf") -> "_1867.Force":
        from mastapy._private.utility.units_and_measurements.measurements import _1867

        return self.__parent__._cast(_1867.Force)

    @property
    def force_per_unit_length(self: "CastSelf") -> "_1868.ForcePerUnitLength":
        from mastapy._private.utility.units_and_measurements.measurements import _1868

        return self.__parent__._cast(_1868.ForcePerUnitLength)

    @property
    def force_per_unit_pressure(self: "CastSelf") -> "_1869.ForcePerUnitPressure":
        from mastapy._private.utility.units_and_measurements.measurements import _1869

        return self.__parent__._cast(_1869.ForcePerUnitPressure)

    @property
    def force_per_unit_temperature(self: "CastSelf") -> "_1870.ForcePerUnitTemperature":
        from mastapy._private.utility.units_and_measurements.measurements import _1870

        return self.__parent__._cast(_1870.ForcePerUnitTemperature)

    @property
    def fraction_measurement_base(self: "CastSelf") -> "_1871.FractionMeasurementBase":
        from mastapy._private.utility.units_and_measurements.measurements import _1871

        return self.__parent__._cast(_1871.FractionMeasurementBase)

    @property
    def fraction_per_temperature(self: "CastSelf") -> "_1872.FractionPerTemperature":
        from mastapy._private.utility.units_and_measurements.measurements import _1872

        return self.__parent__._cast(_1872.FractionPerTemperature)

    @property
    def frequency(self: "CastSelf") -> "_1873.Frequency":
        from mastapy._private.utility.units_and_measurements.measurements import _1873

        return self.__parent__._cast(_1873.Frequency)

    @property
    def fuel_consumption_engine(self: "CastSelf") -> "_1874.FuelConsumptionEngine":
        from mastapy._private.utility.units_and_measurements.measurements import _1874

        return self.__parent__._cast(_1874.FuelConsumptionEngine)

    @property
    def fuel_efficiency_vehicle(self: "CastSelf") -> "_1875.FuelEfficiencyVehicle":
        from mastapy._private.utility.units_and_measurements.measurements import _1875

        return self.__parent__._cast(_1875.FuelEfficiencyVehicle)

    @property
    def gradient(self: "CastSelf") -> "_1876.Gradient":
        from mastapy._private.utility.units_and_measurements.measurements import _1876

        return self.__parent__._cast(_1876.Gradient)

    @property
    def heat_conductivity(self: "CastSelf") -> "_1877.HeatConductivity":
        from mastapy._private.utility.units_and_measurements.measurements import _1877

        return self.__parent__._cast(_1877.HeatConductivity)

    @property
    def heat_transfer(self: "CastSelf") -> "_1878.HeatTransfer":
        from mastapy._private.utility.units_and_measurements.measurements import _1878

        return self.__parent__._cast(_1878.HeatTransfer)

    @property
    def heat_transfer_coefficient_for_plastic_gear_tooth(
        self: "CastSelf",
    ) -> "_1879.HeatTransferCoefficientForPlasticGearTooth":
        from mastapy._private.utility.units_and_measurements.measurements import _1879

        return self.__parent__._cast(_1879.HeatTransferCoefficientForPlasticGearTooth)

    @property
    def heat_transfer_resistance(self: "CastSelf") -> "_1880.HeatTransferResistance":
        from mastapy._private.utility.units_and_measurements.measurements import _1880

        return self.__parent__._cast(_1880.HeatTransferResistance)

    @property
    def impulse(self: "CastSelf") -> "_1881.Impulse":
        from mastapy._private.utility.units_and_measurements.measurements import _1881

        return self.__parent__._cast(_1881.Impulse)

    @property
    def index(self: "CastSelf") -> "_1882.Index":
        from mastapy._private.utility.units_and_measurements.measurements import _1882

        return self.__parent__._cast(_1882.Index)

    @property
    def inductance(self: "CastSelf") -> "_1883.Inductance":
        from mastapy._private.utility.units_and_measurements.measurements import _1883

        return self.__parent__._cast(_1883.Inductance)

    @property
    def integer(self: "CastSelf") -> "_1884.Integer":
        from mastapy._private.utility.units_and_measurements.measurements import _1884

        return self.__parent__._cast(_1884.Integer)

    @property
    def inverse_short_length(self: "CastSelf") -> "_1885.InverseShortLength":
        from mastapy._private.utility.units_and_measurements.measurements import _1885

        return self.__parent__._cast(_1885.InverseShortLength)

    @property
    def inverse_short_time(self: "CastSelf") -> "_1886.InverseShortTime":
        from mastapy._private.utility.units_and_measurements.measurements import _1886

        return self.__parent__._cast(_1886.InverseShortTime)

    @property
    def jerk(self: "CastSelf") -> "_1887.Jerk":
        from mastapy._private.utility.units_and_measurements.measurements import _1887

        return self.__parent__._cast(_1887.Jerk)

    @property
    def kinematic_viscosity(self: "CastSelf") -> "_1888.KinematicViscosity":
        from mastapy._private.utility.units_and_measurements.measurements import _1888

        return self.__parent__._cast(_1888.KinematicViscosity)

    @property
    def length_long(self: "CastSelf") -> "_1889.LengthLong":
        from mastapy._private.utility.units_and_measurements.measurements import _1889

        return self.__parent__._cast(_1889.LengthLong)

    @property
    def length_medium(self: "CastSelf") -> "_1890.LengthMedium":
        from mastapy._private.utility.units_and_measurements.measurements import _1890

        return self.__parent__._cast(_1890.LengthMedium)

    @property
    def length_per_unit_temperature(
        self: "CastSelf",
    ) -> "_1891.LengthPerUnitTemperature":
        from mastapy._private.utility.units_and_measurements.measurements import _1891

        return self.__parent__._cast(_1891.LengthPerUnitTemperature)

    @property
    def length_short(self: "CastSelf") -> "_1892.LengthShort":
        from mastapy._private.utility.units_and_measurements.measurements import _1892

        return self.__parent__._cast(_1892.LengthShort)

    @property
    def length_to_the_fourth(self: "CastSelf") -> "_1893.LengthToTheFourth":
        from mastapy._private.utility.units_and_measurements.measurements import _1893

        return self.__parent__._cast(_1893.LengthToTheFourth)

    @property
    def length_very_long(self: "CastSelf") -> "_1894.LengthVeryLong":
        from mastapy._private.utility.units_and_measurements.measurements import _1894

        return self.__parent__._cast(_1894.LengthVeryLong)

    @property
    def length_very_short(self: "CastSelf") -> "_1895.LengthVeryShort":
        from mastapy._private.utility.units_and_measurements.measurements import _1895

        return self.__parent__._cast(_1895.LengthVeryShort)

    @property
    def length_very_short_per_length_short(
        self: "CastSelf",
    ) -> "_1896.LengthVeryShortPerLengthShort":
        from mastapy._private.utility.units_and_measurements.measurements import _1896

        return self.__parent__._cast(_1896.LengthVeryShortPerLengthShort)

    @property
    def linear_angular_damping(self: "CastSelf") -> "_1897.LinearAngularDamping":
        from mastapy._private.utility.units_and_measurements.measurements import _1897

        return self.__parent__._cast(_1897.LinearAngularDamping)

    @property
    def linear_angular_stiffness_cross_term(
        self: "CastSelf",
    ) -> "_1898.LinearAngularStiffnessCrossTerm":
        from mastapy._private.utility.units_and_measurements.measurements import _1898

        return self.__parent__._cast(_1898.LinearAngularStiffnessCrossTerm)

    @property
    def linear_damping(self: "CastSelf") -> "_1899.LinearDamping":
        from mastapy._private.utility.units_and_measurements.measurements import _1899

        return self.__parent__._cast(_1899.LinearDamping)

    @property
    def linear_flexibility(self: "CastSelf") -> "_1900.LinearFlexibility":
        from mastapy._private.utility.units_and_measurements.measurements import _1900

        return self.__parent__._cast(_1900.LinearFlexibility)

    @property
    def linear_stiffness(self: "CastSelf") -> "_1901.LinearStiffness":
        from mastapy._private.utility.units_and_measurements.measurements import _1901

        return self.__parent__._cast(_1901.LinearStiffness)

    @property
    def magnetic_field_strength(self: "CastSelf") -> "_1902.MagneticFieldStrength":
        from mastapy._private.utility.units_and_measurements.measurements import _1902

        return self.__parent__._cast(_1902.MagneticFieldStrength)

    @property
    def magnetic_flux(self: "CastSelf") -> "_1903.MagneticFlux":
        from mastapy._private.utility.units_and_measurements.measurements import _1903

        return self.__parent__._cast(_1903.MagneticFlux)

    @property
    def magnetic_flux_density(self: "CastSelf") -> "_1904.MagneticFluxDensity":
        from mastapy._private.utility.units_and_measurements.measurements import _1904

        return self.__parent__._cast(_1904.MagneticFluxDensity)

    @property
    def magnetic_vector_potential(self: "CastSelf") -> "_1905.MagneticVectorPotential":
        from mastapy._private.utility.units_and_measurements.measurements import _1905

        return self.__parent__._cast(_1905.MagneticVectorPotential)

    @property
    def magnetomotive_force(self: "CastSelf") -> "_1906.MagnetomotiveForce":
        from mastapy._private.utility.units_and_measurements.measurements import _1906

        return self.__parent__._cast(_1906.MagnetomotiveForce)

    @property
    def mass(self: "CastSelf") -> "_1907.Mass":
        from mastapy._private.utility.units_and_measurements.measurements import _1907

        return self.__parent__._cast(_1907.Mass)

    @property
    def mass_per_unit_length(self: "CastSelf") -> "_1908.MassPerUnitLength":
        from mastapy._private.utility.units_and_measurements.measurements import _1908

        return self.__parent__._cast(_1908.MassPerUnitLength)

    @property
    def mass_per_unit_time(self: "CastSelf") -> "_1909.MassPerUnitTime":
        from mastapy._private.utility.units_and_measurements.measurements import _1909

        return self.__parent__._cast(_1909.MassPerUnitTime)

    @property
    def moment_of_inertia(self: "CastSelf") -> "_1910.MomentOfInertia":
        from mastapy._private.utility.units_and_measurements.measurements import _1910

        return self.__parent__._cast(_1910.MomentOfInertia)

    @property
    def moment_of_inertia_per_unit_length(
        self: "CastSelf",
    ) -> "_1911.MomentOfInertiaPerUnitLength":
        from mastapy._private.utility.units_and_measurements.measurements import _1911

        return self.__parent__._cast(_1911.MomentOfInertiaPerUnitLength)

    @property
    def moment_per_unit_pressure(self: "CastSelf") -> "_1912.MomentPerUnitPressure":
        from mastapy._private.utility.units_and_measurements.measurements import _1912

        return self.__parent__._cast(_1912.MomentPerUnitPressure)

    @property
    def number(self: "CastSelf") -> "_1913.Number":
        from mastapy._private.utility.units_and_measurements.measurements import _1913

        return self.__parent__._cast(_1913.Number)

    @property
    def percentage(self: "CastSelf") -> "_1914.Percentage":
        from mastapy._private.utility.units_and_measurements.measurements import _1914

        return self.__parent__._cast(_1914.Percentage)

    @property
    def power(self: "CastSelf") -> "_1915.Power":
        from mastapy._private.utility.units_and_measurements.measurements import _1915

        return self.__parent__._cast(_1915.Power)

    @property
    def power_per_small_area(self: "CastSelf") -> "_1916.PowerPerSmallArea":
        from mastapy._private.utility.units_and_measurements.measurements import _1916

        return self.__parent__._cast(_1916.PowerPerSmallArea)

    @property
    def power_per_unit_time(self: "CastSelf") -> "_1917.PowerPerUnitTime":
        from mastapy._private.utility.units_and_measurements.measurements import _1917

        return self.__parent__._cast(_1917.PowerPerUnitTime)

    @property
    def power_small(self: "CastSelf") -> "_1918.PowerSmall":
        from mastapy._private.utility.units_and_measurements.measurements import _1918

        return self.__parent__._cast(_1918.PowerSmall)

    @property
    def power_small_per_area(self: "CastSelf") -> "_1919.PowerSmallPerArea":
        from mastapy._private.utility.units_and_measurements.measurements import _1919

        return self.__parent__._cast(_1919.PowerSmallPerArea)

    @property
    def power_small_per_mass(self: "CastSelf") -> "_1920.PowerSmallPerMass":
        from mastapy._private.utility.units_and_measurements.measurements import _1920

        return self.__parent__._cast(_1920.PowerSmallPerMass)

    @property
    def power_small_per_unit_area_per_unit_time(
        self: "CastSelf",
    ) -> "_1921.PowerSmallPerUnitAreaPerUnitTime":
        from mastapy._private.utility.units_and_measurements.measurements import _1921

        return self.__parent__._cast(_1921.PowerSmallPerUnitAreaPerUnitTime)

    @property
    def power_small_per_unit_time(self: "CastSelf") -> "_1922.PowerSmallPerUnitTime":
        from mastapy._private.utility.units_and_measurements.measurements import _1922

        return self.__parent__._cast(_1922.PowerSmallPerUnitTime)

    @property
    def power_small_per_volume(self: "CastSelf") -> "_1923.PowerSmallPerVolume":
        from mastapy._private.utility.units_and_measurements.measurements import _1923

        return self.__parent__._cast(_1923.PowerSmallPerVolume)

    @property
    def pressure(self: "CastSelf") -> "_1924.Pressure":
        from mastapy._private.utility.units_and_measurements.measurements import _1924

        return self.__parent__._cast(_1924.Pressure)

    @property
    def pressure_per_unit_time(self: "CastSelf") -> "_1925.PressurePerUnitTime":
        from mastapy._private.utility.units_and_measurements.measurements import _1925

        return self.__parent__._cast(_1925.PressurePerUnitTime)

    @property
    def pressure_small(self: "CastSelf") -> "_1926.PressureSmall":
        from mastapy._private.utility.units_and_measurements.measurements import _1926

        return self.__parent__._cast(_1926.PressureSmall)

    @property
    def pressure_velocity_product(self: "CastSelf") -> "_1927.PressureVelocityProduct":
        from mastapy._private.utility.units_and_measurements.measurements import _1927

        return self.__parent__._cast(_1927.PressureVelocityProduct)

    @property
    def pressure_viscosity_coefficient(
        self: "CastSelf",
    ) -> "_1928.PressureViscosityCoefficient":
        from mastapy._private.utility.units_and_measurements.measurements import _1928

        return self.__parent__._cast(_1928.PressureViscosityCoefficient)

    @property
    def price(self: "CastSelf") -> "_1929.Price":
        from mastapy._private.utility.units_and_measurements.measurements import _1929

        return self.__parent__._cast(_1929.Price)

    @property
    def price_per_unit_mass(self: "CastSelf") -> "_1930.PricePerUnitMass":
        from mastapy._private.utility.units_and_measurements.measurements import _1930

        return self.__parent__._cast(_1930.PricePerUnitMass)

    @property
    def quadratic_angular_damping(self: "CastSelf") -> "_1931.QuadraticAngularDamping":
        from mastapy._private.utility.units_and_measurements.measurements import _1931

        return self.__parent__._cast(_1931.QuadraticAngularDamping)

    @property
    def quadratic_drag(self: "CastSelf") -> "_1932.QuadraticDrag":
        from mastapy._private.utility.units_and_measurements.measurements import _1932

        return self.__parent__._cast(_1932.QuadraticDrag)

    @property
    def rescaled_measurement(self: "CastSelf") -> "_1933.RescaledMeasurement":
        from mastapy._private.utility.units_and_measurements.measurements import _1933

        return self.__parent__._cast(_1933.RescaledMeasurement)

    @property
    def rotatum(self: "CastSelf") -> "_1934.Rotatum":
        from mastapy._private.utility.units_and_measurements.measurements import _1934

        return self.__parent__._cast(_1934.Rotatum)

    @property
    def safety_factor(self: "CastSelf") -> "_1935.SafetyFactor":
        from mastapy._private.utility.units_and_measurements.measurements import _1935

        return self.__parent__._cast(_1935.SafetyFactor)

    @property
    def specific_acoustic_impedance(
        self: "CastSelf",
    ) -> "_1936.SpecificAcousticImpedance":
        from mastapy._private.utility.units_and_measurements.measurements import _1936

        return self.__parent__._cast(_1936.SpecificAcousticImpedance)

    @property
    def specific_heat(self: "CastSelf") -> "_1937.SpecificHeat":
        from mastapy._private.utility.units_and_measurements.measurements import _1937

        return self.__parent__._cast(_1937.SpecificHeat)

    @property
    def square_root_of_unit_force_per_unit_area(
        self: "CastSelf",
    ) -> "_1938.SquareRootOfUnitForcePerUnitArea":
        from mastapy._private.utility.units_and_measurements.measurements import _1938

        return self.__parent__._cast(_1938.SquareRootOfUnitForcePerUnitArea)

    @property
    def stiffness_per_unit_face_width(
        self: "CastSelf",
    ) -> "_1939.StiffnessPerUnitFaceWidth":
        from mastapy._private.utility.units_and_measurements.measurements import _1939

        return self.__parent__._cast(_1939.StiffnessPerUnitFaceWidth)

    @property
    def stress(self: "CastSelf") -> "_1940.Stress":
        from mastapy._private.utility.units_and_measurements.measurements import _1940

        return self.__parent__._cast(_1940.Stress)

    @property
    def temperature(self: "CastSelf") -> "_1941.Temperature":
        from mastapy._private.utility.units_and_measurements.measurements import _1941

        return self.__parent__._cast(_1941.Temperature)

    @property
    def temperature_difference(self: "CastSelf") -> "_1942.TemperatureDifference":
        from mastapy._private.utility.units_and_measurements.measurements import _1942

        return self.__parent__._cast(_1942.TemperatureDifference)

    @property
    def temperature_per_unit_time(self: "CastSelf") -> "_1943.TemperaturePerUnitTime":
        from mastapy._private.utility.units_and_measurements.measurements import _1943

        return self.__parent__._cast(_1943.TemperaturePerUnitTime)

    @property
    def text(self: "CastSelf") -> "_1944.Text":
        from mastapy._private.utility.units_and_measurements.measurements import _1944

        return self.__parent__._cast(_1944.Text)

    @property
    def thermal_contact_coefficient(
        self: "CastSelf",
    ) -> "_1945.ThermalContactCoefficient":
        from mastapy._private.utility.units_and_measurements.measurements import _1945

        return self.__parent__._cast(_1945.ThermalContactCoefficient)

    @property
    def thermal_expansion_coefficient(
        self: "CastSelf",
    ) -> "_1946.ThermalExpansionCoefficient":
        from mastapy._private.utility.units_and_measurements.measurements import _1946

        return self.__parent__._cast(_1946.ThermalExpansionCoefficient)

    @property
    def thermal_resistance(self: "CastSelf") -> "_1947.ThermalResistance":
        from mastapy._private.utility.units_and_measurements.measurements import _1947

        return self.__parent__._cast(_1947.ThermalResistance)

    @property
    def thermo_elastic_factor(self: "CastSelf") -> "_1948.ThermoElasticFactor":
        from mastapy._private.utility.units_and_measurements.measurements import _1948

        return self.__parent__._cast(_1948.ThermoElasticFactor)

    @property
    def time(self: "CastSelf") -> "_1949.Time":
        from mastapy._private.utility.units_and_measurements.measurements import _1949

        return self.__parent__._cast(_1949.Time)

    @property
    def time_short(self: "CastSelf") -> "_1950.TimeShort":
        from mastapy._private.utility.units_and_measurements.measurements import _1950

        return self.__parent__._cast(_1950.TimeShort)

    @property
    def time_very_short(self: "CastSelf") -> "_1951.TimeVeryShort":
        from mastapy._private.utility.units_and_measurements.measurements import _1951

        return self.__parent__._cast(_1951.TimeVeryShort)

    @property
    def torque(self: "CastSelf") -> "_1952.Torque":
        from mastapy._private.utility.units_and_measurements.measurements import _1952

        return self.__parent__._cast(_1952.Torque)

    @property
    def torque_converter_inverse_k(self: "CastSelf") -> "_1953.TorqueConverterInverseK":
        from mastapy._private.utility.units_and_measurements.measurements import _1953

        return self.__parent__._cast(_1953.TorqueConverterInverseK)

    @property
    def torque_converter_k(self: "CastSelf") -> "_1954.TorqueConverterK":
        from mastapy._private.utility.units_and_measurements.measurements import _1954

        return self.__parent__._cast(_1954.TorqueConverterK)

    @property
    def torque_per_current(self: "CastSelf") -> "_1955.TorquePerCurrent":
        from mastapy._private.utility.units_and_measurements.measurements import _1955

        return self.__parent__._cast(_1955.TorquePerCurrent)

    @property
    def torque_per_square_root_of_power(
        self: "CastSelf",
    ) -> "_1956.TorquePerSquareRootOfPower":
        from mastapy._private.utility.units_and_measurements.measurements import _1956

        return self.__parent__._cast(_1956.TorquePerSquareRootOfPower)

    @property
    def torque_per_unit_temperature(
        self: "CastSelf",
    ) -> "_1957.TorquePerUnitTemperature":
        from mastapy._private.utility.units_and_measurements.measurements import _1957

        return self.__parent__._cast(_1957.TorquePerUnitTemperature)

    @property
    def velocity(self: "CastSelf") -> "_1958.Velocity":
        from mastapy._private.utility.units_and_measurements.measurements import _1958

        return self.__parent__._cast(_1958.Velocity)

    @property
    def velocity_small(self: "CastSelf") -> "_1959.VelocitySmall":
        from mastapy._private.utility.units_and_measurements.measurements import _1959

        return self.__parent__._cast(_1959.VelocitySmall)

    @property
    def viscosity(self: "CastSelf") -> "_1960.Viscosity":
        from mastapy._private.utility.units_and_measurements.measurements import _1960

        return self.__parent__._cast(_1960.Viscosity)

    @property
    def voltage(self: "CastSelf") -> "_1961.Voltage":
        from mastapy._private.utility.units_and_measurements.measurements import _1961

        return self.__parent__._cast(_1961.Voltage)

    @property
    def voltage_per_angular_velocity(
        self: "CastSelf",
    ) -> "_1962.VoltagePerAngularVelocity":
        from mastapy._private.utility.units_and_measurements.measurements import _1962

        return self.__parent__._cast(_1962.VoltagePerAngularVelocity)

    @property
    def volume(self: "CastSelf") -> "_1963.Volume":
        from mastapy._private.utility.units_and_measurements.measurements import _1963

        return self.__parent__._cast(_1963.Volume)

    @property
    def wear_coefficient(self: "CastSelf") -> "_1964.WearCoefficient":
        from mastapy._private.utility.units_and_measurements.measurements import _1964

        return self.__parent__._cast(_1964.WearCoefficient)

    @property
    def yank(self: "CastSelf") -> "_1965.Yank":
        from mastapy._private.utility.units_and_measurements.measurements import _1965

        return self.__parent__._cast(_1965.Yank)

    @property
    def measurement_base(self: "CastSelf") -> "MeasurementBase":
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
class MeasurementBase(_0.APIBase):
    """MeasurementBase

    This is a mastapy class.
    """

    TYPE: ClassVar["Type"] = _MEASUREMENT_BASE

    wrapped: "Any"

    def __post_init__(self: "Self") -> None:
        """Override of the post initialisation magic method."""
        if not hasattr(self.wrapped, "reference_count"):
            self.wrapped.reference_count = 0

        self.wrapped.reference_count += 1

    @property
    @exception_bridge
    def absolute_tolerance(self: "Self") -> "overridable.Overridable_float":
        """Overridable[float]"""
        temp = pythonnet_property_get(self.wrapped, "AbsoluteTolerance")

        if temp is None:
            return 0.0

        return constructor.new_from_mastapy(
            "mastapy._private._internal.implicit.overridable", "Overridable_float"
        )(temp)

    @absolute_tolerance.setter
    @exception_bridge
    @enforce_parameter_types
    def absolute_tolerance(
        self: "Self", value: "Union[float, Tuple[float, bool]]"
    ) -> None:
        wrapper_type = overridable.Overridable_float.wrapper_type()
        enclosed_type = overridable.Overridable_float.implicit_type()
        value, is_overridden = _unpack_overridable(value)
        value = wrapper_type[enclosed_type](
            enclosed_type(value) if value is not None else 0.0, is_overridden
        )
        pythonnet_property_set(self.wrapped, "AbsoluteTolerance", value)

    @property
    @exception_bridge
    def default_unit(
        self: "Self",
    ) -> "list_with_selected_item.ListWithSelectedItem_Unit":
        """ListWithSelectedItem[mastapy.utility.units_and_measurements.Unit]"""
        temp = pythonnet_property_get(self.wrapped, "DefaultUnit")

        if temp is None:
            return None

        selected_value = temp.SelectedValue

        if selected_value is None:
            return ListWithSelectedItem_None(temp)

        return constructor.new_from_mastapy(
            "mastapy._private._internal.implicit.list_with_selected_item",
            "ListWithSelectedItem_Unit",
        )(temp)

    @default_unit.setter
    @exception_bridge
    @enforce_parameter_types
    def default_unit(self: "Self", value: "_1834.Unit") -> None:
        generic_type = list_with_selected_item.ListWithSelectedItem_Unit.implicit_type()
        value = promote_to_list_with_selected_item(value)
        value = conversion.mp_to_pn_smt_list_with_selected_item(
            self, value, generic_type
        )
        pythonnet_property_set(self.wrapped, "DefaultUnit", value)

    @property
    @exception_bridge
    def name(self: "Self") -> "str":
        """str

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "Name")

        if temp is None:
            return ""

        return temp

    @property
    @exception_bridge
    def percentage_tolerance(self: "Self") -> "overridable.Overridable_float":
        """Overridable[float]"""
        temp = pythonnet_property_get(self.wrapped, "PercentageTolerance")

        if temp is None:
            return 0.0

        return constructor.new_from_mastapy(
            "mastapy._private._internal.implicit.overridable", "Overridable_float"
        )(temp)

    @percentage_tolerance.setter
    @exception_bridge
    @enforce_parameter_types
    def percentage_tolerance(
        self: "Self", value: "Union[float, Tuple[float, bool]]"
    ) -> None:
        wrapper_type = overridable.Overridable_float.wrapper_type()
        enclosed_type = overridable.Overridable_float.implicit_type()
        value, is_overridden = _unpack_overridable(value)
        value = wrapper_type[enclosed_type](
            enclosed_type(value) if value is not None else 0.0, is_overridden
        )
        pythonnet_property_set(self.wrapped, "PercentageTolerance", value)

    @property
    @exception_bridge
    def rounding_digits(self: "Self") -> "int":
        """int"""
        temp = pythonnet_property_get(self.wrapped, "RoundingDigits")

        if temp is None:
            return 0

        return temp

    @rounding_digits.setter
    @exception_bridge
    @enforce_parameter_types
    def rounding_digits(self: "Self", value: "int") -> None:
        pythonnet_property_set(
            self.wrapped, "RoundingDigits", int(value) if value is not None else 0
        )

    @property
    @exception_bridge
    def rounding_method(self: "Self") -> "_1821.RoundingMethods":
        """mastapy.utility.RoundingMethods"""
        temp = pythonnet_property_get(self.wrapped, "RoundingMethod")

        if temp is None:
            return None

        value = conversion.pn_to_mp_enum(temp, "SMT.MastaAPI.Utility.RoundingMethods")

        if value is None:
            return None

        return constructor.new_from_mastapy(
            "mastapy._private.utility._1821", "RoundingMethods"
        )(value)

    @rounding_method.setter
    @exception_bridge
    @enforce_parameter_types
    def rounding_method(self: "Self", value: "_1821.RoundingMethods") -> None:
        value = conversion.mp_to_pn_enum(value, "SMT.MastaAPI.Utility.RoundingMethods")
        pythonnet_property_set(self.wrapped, "RoundingMethod", value)

    @property
    @exception_bridge
    def current_unit(self: "Self") -> "_1834.Unit":
        """mastapy.utility.units_and_measurements.Unit

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "CurrentUnit")

        if temp is None:
            return None

        type_ = temp.GetType()
        return constructor.new(type_.Namespace, type_.Name)(temp)

    @property
    @exception_bridge
    def available_units(self: "Self") -> "List[_1834.Unit]":
        """List[mastapy.utility.units_and_measurements.Unit]

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "AvailableUnits")

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
    def cast_to(self: "Self") -> "_Cast_MeasurementBase":
        """Cast to another type.

        Returns:
            _Cast_MeasurementBase
        """
        return _Cast_MeasurementBase(self)
