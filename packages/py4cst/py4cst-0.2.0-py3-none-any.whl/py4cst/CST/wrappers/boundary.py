'''This file is auto-generated. Do not edit.'''
from .. import IVBAProvider, VBATypeName, VBAObjWrapper
from enum import Enum
from typing import Union, Tuple

class Boundary(VBAObjWrapper):
    class BoundaryType(Enum):
        ELECTRIC = 'electric'
        MAGNETIC = 'magnetic'
        TANGENTIAL = 'tangential'
        NORMAL = 'normal'
        OPEN = 'open'
        EXPANDED_OPEN = 'expanded open'
        PERIODIC = 'periodic'
        CONDUCTING_WALL = 'conducting wall'
        UNIT_CELL = 'unit cell'

    class SymmetryType(Enum):
        ELECTRIC = 'electric'
        MAGNETIC = 'magnetic'
        NONE = 'none'

    class PotentialType(Enum):
        NONE = 'none'
        FIXED = 'fixed'
        FLOATING = 'floating'

    class ThermalBoundaryType(Enum):
        ISOTHERMAL = 'isothermal'
        ADIABATIC = 'adiabatic'
        OPEN = 'open'
        EXPANDED_OPEN = 'expanded open'

    class ThermalSymmetryType(Enum):
        ISOTHERMAL = 'isothermal'
        ADIABATIC = 'adiabatic'
        NONE = 'none'
        EXPANDED_OPEN = 'expanded open'

    class TemperatureType(Enum):
        NONE = 'none'
        FIXED = 'fixed'
        FLOATING = 'floating'

    class DistanceType(Enum):
        FRACTION = 'Fraction'
        ABSOLUTE = 'Absolute'

    class DistanceRefFreqType(Enum):
        CENTER = 'Center'
        CENTER_N_MONITORS = 'CenterNMonitors'
        USER = 'User'

    class Direction(Enum):
        OUTWARD = 'outward'
        INWARD = 'inward'

    def __init__(self, vbap: IVBAProvider) -> None:
        super().__init__(vbap, 'Boundary')
        self.set_save_history(False)

    def set_type_x_min(self, boundary_type: Union[BoundaryType, str]) -> None:
        """
        VBA Call
        --------
        Boundary.Xmin(boundary_type)
        """
        self.record_method('Xmin', str(getattr(boundary_type, 'value', boundary_type)))

    def set_type_x_max(self, boundary_type: Union[BoundaryType, str]) -> None:
        """
        VBA Call
        --------
        Boundary.Xmax(boundary_type)
        """
        self.record_method('Xmax', str(getattr(boundary_type, 'value', boundary_type)))

    def set_type_y_min(self, boundary_type: Union[BoundaryType, str]) -> None:
        """
        VBA Call
        --------
        Boundary.Ymin(boundary_type)
        """
        self.record_method('Ymin', str(getattr(boundary_type, 'value', boundary_type)))

    def set_type_y_max(self, boundary_type: Union[BoundaryType, str]) -> None:
        """
        VBA Call
        --------
        Boundary.Ymax(boundary_type)
        """
        self.record_method('Ymax', str(getattr(boundary_type, 'value', boundary_type)))

    def set_type_z_min(self, boundary_type: Union[BoundaryType, str]) -> None:
        """
        VBA Call
        --------
        Boundary.Zmin(boundary_type)
        """
        self.record_method('Zmin', str(getattr(boundary_type, 'value', boundary_type)))

    def set_type_z_max(self, boundary_type: Union[BoundaryType, str]) -> None:
        """
        VBA Call
        --------
        Boundary.Zmax(boundary_type)
        """
        self.record_method('Zmax', str(getattr(boundary_type, 'value', boundary_type)))

    def get_type_x_min(self) -> BoundaryType:
        """
        VBA Call
        --------
        Boundary.GetXmin()
        """
        __retval__ = self.query_method_str('GetXmin')
        return Boundary.BoundaryType(__retval__)

    def get_type_x_max(self) -> BoundaryType:
        """
        VBA Call
        --------
        Boundary.GetXmax()
        """
        __retval__ = self.query_method_str('GetXmax')
        return Boundary.BoundaryType(__retval__)

    def get_type_y_min(self) -> BoundaryType:
        """
        VBA Call
        --------
        Boundary.GetYmin()
        """
        __retval__ = self.query_method_str('GetYmin')
        return Boundary.BoundaryType(__retval__)

    def get_type_y_max(self) -> BoundaryType:
        """
        VBA Call
        --------
        Boundary.GetYmax()
        """
        __retval__ = self.query_method_str('GetYmax')
        return Boundary.BoundaryType(__retval__)

    def get_type_z_min(self) -> BoundaryType:
        """
        VBA Call
        --------
        Boundary.GetZmin()
        """
        __retval__ = self.query_method_str('GetZmin')
        return Boundary.BoundaryType(__retval__)

    def get_type_z_max(self) -> BoundaryType:
        """
        VBA Call
        --------
        Boundary.GetZmax()
        """
        __retval__ = self.query_method_str('GetZmax')
        return Boundary.BoundaryType(__retval__)

    def set_symmetry_x(self, symmetry_type: Union[SymmetryType, str]) -> None:
        """
        VBA Call
        --------
        Boundary.Xsymmetry(symmetry_type)
        """
        self.record_method('Xsymmetry', str(getattr(symmetry_type, 'value', symmetry_type)))

    def set_symmetry_y(self, symmetry_type: Union[SymmetryType, str]) -> None:
        """
        VBA Call
        --------
        Boundary.Ysymmetry(symmetry_type)
        """
        self.record_method('Ysymmetry', str(getattr(symmetry_type, 'value', symmetry_type)))

    def set_symmetry_z(self, symmetry_type: Union[SymmetryType, str]) -> None:
        """
        VBA Call
        --------
        Boundary.Zsymmetry(symmetry_type)
        """
        self.record_method('Zsymmetry', str(getattr(symmetry_type, 'value', symmetry_type)))

    def get_symmetry_x(self) -> SymmetryType:
        """
        VBA Call
        --------
        Boundary.GetXSymmetry()
        """
        __retval__ = self.query_method_str('GetXSymmetry')
        return Boundary.SymmetryType(__retval__)

    def get_symmetry_y(self) -> SymmetryType:
        """
        VBA Call
        --------
        Boundary.GetYSymmetry()
        """
        __retval__ = self.query_method_str('GetYSymmetry')
        return Boundary.SymmetryType(__retval__)

    def get_symmetry_z(self) -> SymmetryType:
        """
        VBA Call
        --------
        Boundary.GetZSymmetry()
        """
        __retval__ = self.query_method_str('GetZSymmetry')
        return Boundary.SymmetryType(__retval__)

    def set_apply_in_all_directions(self, flag: bool = True) -> None:
        """
        VBA Call
        --------
        Boundary.ApplyInAllDirections(flag)
        """
        self.record_method('ApplyInAllDirections', flag)

    def set_potential_type_x_min(self, potential_type: Union[PotentialType, str]) -> None:
        """
        VBA Call
        --------
        Boundary.XminPotentialType(potential_type)
        """
        self.record_method('XminPotentialType', str(getattr(potential_type, 'value', potential_type)))

    def set_potential_type_x_max(self, potential_type: Union[PotentialType, str]) -> None:
        """
        VBA Call
        --------
        Boundary.XmaxPotentialType(potential_type)
        """
        self.record_method('XmaxPotentialType', str(getattr(potential_type, 'value', potential_type)))

    def set_potential_type_y_min(self, potential_type: Union[PotentialType, str]) -> None:
        """
        VBA Call
        --------
        Boundary.YminPotentialType(potential_type)
        """
        self.record_method('YminPotentialType', str(getattr(potential_type, 'value', potential_type)))

    def set_potential_type_y_max(self, potential_type: Union[PotentialType, str]) -> None:
        """
        VBA Call
        --------
        Boundary.YmaxPotentialType(potential_type)
        """
        self.record_method('YmaxPotentialType', str(getattr(potential_type, 'value', potential_type)))

    def set_potential_type_z_min(self, potential_type: Union[PotentialType, str]) -> None:
        """
        VBA Call
        --------
        Boundary.ZminPotentialType(potential_type)
        """
        self.record_method('ZminPotentialType', str(getattr(potential_type, 'value', potential_type)))

    def set_potential_type_z_max(self, potential_type: Union[PotentialType, str]) -> None:
        """
        VBA Call
        --------
        Boundary.ZmaxPotentialType(potential_type)
        """
        self.record_method('ZmaxPotentialType', str(getattr(potential_type, 'value', potential_type)))

    def set_potential_x_min(self, potential: float) -> None:
        """
        VBA Call
        --------
        Boundary.XminPotential(potential)
        """
        self.record_method('XminPotential', potential)

    def set_potential_x_max(self, potential: float) -> None:
        """
        VBA Call
        --------
        Boundary.XmaxPotential(potential)
        """
        self.record_method('XmaxPotential', potential)

    def set_potential_y_min(self, potential: float) -> None:
        """
        VBA Call
        --------
        Boundary.YminPotential(potential)
        """
        self.record_method('YminPotential', potential)

    def set_potential_y_max(self, potential: float) -> None:
        """
        VBA Call
        --------
        Boundary.YmaxPotential(potential)
        """
        self.record_method('YmaxPotential', potential)

    def set_potential_z_min(self, potential: float) -> None:
        """
        VBA Call
        --------
        Boundary.ZminPotential(potential)
        """
        self.record_method('ZminPotential', potential)

    def set_potential_z_max(self, potential: float) -> None:
        """
        VBA Call
        --------
        Boundary.ZmaxPotential(potential)
        """
        self.record_method('ZmaxPotential', potential)

    def set_thermal_type_x_min(self, thermal_type: Union[ThermalBoundaryType, str]) -> None:
        """
        VBA Call
        --------
        Boundary.XminThermal(thermal_type)
        """
        self.record_method('XminThermal', str(getattr(thermal_type, 'value', thermal_type)))

    def set_thermal_type_x_max(self, thermal_type: Union[ThermalBoundaryType, str]) -> None:
        """
        VBA Call
        --------
        Boundary.XmaxThermal(thermal_type)
        """
        self.record_method('XmaxThermal', str(getattr(thermal_type, 'value', thermal_type)))

    def set_thermal_type_y_min(self, thermal_type: Union[ThermalBoundaryType, str]) -> None:
        """
        VBA Call
        --------
        Boundary.YminThermal(thermal_type)
        """
        self.record_method('YminThermal', str(getattr(thermal_type, 'value', thermal_type)))

    def set_thermal_type_y_max(self, thermal_type: Union[ThermalBoundaryType, str]) -> None:
        """
        VBA Call
        --------
        Boundary.YmaxThermal(thermal_type)
        """
        self.record_method('YmaxThermal', str(getattr(thermal_type, 'value', thermal_type)))

    def set_thermal_type_z_min(self, thermal_type: Union[ThermalBoundaryType, str]) -> None:
        """
        VBA Call
        --------
        Boundary.ZminThermal(thermal_type)
        """
        self.record_method('ZminThermal', str(getattr(thermal_type, 'value', thermal_type)))

    def set_thermal_type_z_max(self, thermal_type: Union[ThermalBoundaryType, str]) -> None:
        """
        VBA Call
        --------
        Boundary.ZmaxThermal(thermal_type)
        """
        self.record_method('ZmaxThermal', str(getattr(thermal_type, 'value', thermal_type)))

    def set_thermal_symmetry_x(self, symmetry_type: Union[ThermalSymmetryType, str]) -> None:
        """
        VBA Call
        --------
        Boundary.XsymmetryThermal(symmetry_type)
        """
        self.record_method('XsymmetryThermal', str(getattr(symmetry_type, 'value', symmetry_type)))

    def set_thermal_symmetry_y(self, symmetry_type: Union[ThermalSymmetryType, str]) -> None:
        """
        VBA Call
        --------
        Boundary.YsymmetryThermal(symmetry_type)
        """
        self.record_method('YsymmetryThermal', str(getattr(symmetry_type, 'value', symmetry_type)))

    def set_thermal_symmetry_z(self, symmetry_type: Union[ThermalSymmetryType, str]) -> None:
        """
        VBA Call
        --------
        Boundary.ZsymmetryThermal(symmetry_type)
        """
        self.record_method('ZsymmetryThermal', str(getattr(symmetry_type, 'value', symmetry_type)))

    def get_thermal_symmetry_x(self) -> ThermalSymmetryType:
        """
        VBA Call
        --------
        Boundary.GetXSymmetryThermal()
        """
        __retval__ = self.query_method_str('GetXSymmetryThermal')
        return Boundary.ThermalSymmetryType(__retval__)

    def get_thermal_symmetry_y(self) -> ThermalSymmetryType:
        """
        VBA Call
        --------
        Boundary.GetYSymmetryThermal()
        """
        __retval__ = self.query_method_str('GetYSymmetryThermal')
        return Boundary.ThermalSymmetryType(__retval__)

    def get_thermal_symmetry_z(self) -> ThermalSymmetryType:
        """
        VBA Call
        --------
        Boundary.GetZSymmetryThermal()
        """
        __retval__ = self.query_method_str('GetZSymmetryThermal')
        return Boundary.ThermalSymmetryType(__retval__)

    def set_temperature_type_x_min(self, temperature_type: Union[TemperatureType, str]) -> None:
        """
        VBA Call
        --------
        Boundary.XminTemperatureType(temperature_type)
        """
        self.record_method('XminTemperatureType', str(getattr(temperature_type, 'value', temperature_type)))

    def set_temperature_type_x_max(self, temperature_type: Union[TemperatureType, str]) -> None:
        """
        VBA Call
        --------
        Boundary.XmaxTemperatureType(temperature_type)
        """
        self.record_method('XmaxTemperatureType', str(getattr(temperature_type, 'value', temperature_type)))

    def set_temperature_type_y_min(self, temperature_type: Union[TemperatureType, str]) -> None:
        """
        VBA Call
        --------
        Boundary.YminTemperatureType(temperature_type)
        """
        self.record_method('YminTemperatureType', str(getattr(temperature_type, 'value', temperature_type)))

    def set_temperature_type_y_max(self, temperature_type: Union[TemperatureType, str]) -> None:
        """
        VBA Call
        --------
        Boundary.YmaxTemperatureType(temperature_type)
        """
        self.record_method('YmaxTemperatureType', str(getattr(temperature_type, 'value', temperature_type)))

    def set_temperature_type_z_min(self, temperature_type: Union[TemperatureType, str]) -> None:
        """
        VBA Call
        --------
        Boundary.ZminTemperatureType(temperature_type)
        """
        self.record_method('ZminTemperatureType', str(getattr(temperature_type, 'value', temperature_type)))

    def set_temperature_type_z_max(self, temperature_type: Union[TemperatureType, str]) -> None:
        """
        VBA Call
        --------
        Boundary.ZmaxTemperatureType(temperature_type)
        """
        self.record_method('ZmaxTemperatureType', str(getattr(temperature_type, 'value', temperature_type)))

    def set_temperature_x_min(self, temperature: float) -> None:
        """
        VBA Call
        --------
        Boundary.XminTemperature(temperature)
        """
        self.record_method('XminTemperature', temperature)

    def set_temperature_x_max(self, temperature: float) -> None:
        """
        VBA Call
        --------
        Boundary.XmaxTemperature(temperature)
        """
        self.record_method('XmaxTemperature', temperature)

    def set_temperature_y_min(self, temperature: float) -> None:
        """
        VBA Call
        --------
        Boundary.YminTemperature(temperature)
        """
        self.record_method('YminTemperature', temperature)

    def set_temperature_y_max(self, temperature: float) -> None:
        """
        VBA Call
        --------
        Boundary.YmaxTemperature(temperature)
        """
        self.record_method('YmaxTemperature', temperature)

    def set_temperature_z_min(self, temperature: float) -> None:
        """
        VBA Call
        --------
        Boundary.ZminTemperature(temperature)
        """
        self.record_method('ZminTemperature', temperature)

    def set_temperature_z_max(self, temperature: float) -> None:
        """
        VBA Call
        --------
        Boundary.ZmaxTemperature(temperature)
        """
        self.record_method('ZmaxTemperature', temperature)

    def get_calculation_box(self) -> Tuple:
        """
        VBA Call
        --------
        Boundary.GetCalculationBox(&x_min, &x_max, &y_min, &y_max, &z_min, &z_max)

        Returns
        -------
        (x_min, x_max, y_min, y_max, z_min, z_max)
        """
        return self.query_method_t('GetCalculationBox', None, VBATypeName.Double, VBATypeName.Double, VBATypeName.Double, VBATypeName.Double, VBATypeName.Double, VBATypeName.Double)

    def get_structure_box(self) -> Tuple:
        """
        VBA Call
        --------
        Boundary.GetStructureBox(&x_min, &x_max, &y_min, &y_max, &z_min, &z_max)

        Returns
        -------
        (x_min, x_max, y_min, y_max, z_min, z_max)
        """
        return self.query_method_t('GetStructureBox', None, VBATypeName.Double, VBATypeName.Double, VBATypeName.Double, VBATypeName.Double, VBATypeName.Double, VBATypeName.Double)

    def set_number_of_layers(self, count: int) -> None:
        """
        VBA Call
        --------
        Boundary.Layer(count)
        """
        self.record_method('Layer', count)

    def set_minimum_lines_distance(self, distance: float) -> None:
        """
        VBA Call
        --------
        Boundary.MinimumLinesDistance(distance)
        """
        self.record_method('MinimumLinesDistance', distance)

    def set_minimum_distance_type(self, distance_type: Union[DistanceType, str]) -> None:
        """
        VBA Call
        --------
        Boundary.MinimumDistanceType(distance_type)
        """
        self.record_method('MinimumDistanceType', str(getattr(distance_type, 'value', distance_type)))

    def set_absolute_distance(self, distance: float) -> None:
        """
        VBA Call
        --------
        Boundary.SetAbsoluteDistance(distance)
        """
        self.record_method('SetAbsoluteDistance', distance)

    def set_minimum_distance_reference_frequency_type(self, freq_type: Union[DistanceRefFreqType, str]) -> None:
        """
        VBA Call
        --------
        Boundary.MinimumDistanceReferenceFrequencyType(freq_type)
        """
        self.record_method('MinimumDistanceReferenceFrequencyType', str(getattr(freq_type, 'value', freq_type)))

    def set_minimum_distance_per_wavelength(self, distance: float) -> None:
        """
        VBA Call
        --------
        Boundary.MinimumDistancePerWavelength(distance)
        """
        self.record_method('MinimumDistancePerWavelength', distance)

    def set_frequency_for_minimum_distance(self, freq: float) -> None:
        """
        VBA Call
        --------
        Boundary.FrequencyForMinimumDistance(freq)
        """
        self.record_method('FrequencyForMinimumDistance', freq)

    def set_period_shift_x_deg(self, angle_deg: float) -> None:
        """
        VBA Call
        --------
        Boundary.XPeriodicShift(angle_deg)
        """
        self.record_method('XPeriodicShift', angle_deg)

    def set_period_shift_y_deg(self, angle_deg: float) -> None:
        """
        VBA Call
        --------
        Boundary.YPeriodicShift(angle_deg)
        """
        self.record_method('YPeriodicShift', angle_deg)

    def set_period_shift_z_deg(self, angle_deg: float) -> None:
        """
        VBA Call
        --------
        Boundary.ZPeriodicShift(angle_deg)
        """
        self.record_method('ZPeriodicShift', angle_deg)

    def set_periodic_use_constant_angles(self, flag: bool = True) -> None:
        """
        VBA Call
        --------
        Boundary.PeriodicUseConstantAngles(flag)
        """
        self.record_method('PeriodicUseConstantAngles', flag)

    def set_periodic_boundary_angles_deg(self, theta_deg: float, phi_deg: float) -> None:
        """
        VBA Call
        --------
        Boundary.SetPeriodicBoundaryAngles(theta_deg, phi_deg)
        """
        self.record_method('SetPeriodicBoundaryAngles', theta_deg, phi_deg)

    def set_periodic_boundary_angles_direction(self, direction: Union[Direction, str]) -> None:
        """
        VBA Call
        --------
        Boundary.SetPeriodicBoundaryAnglesDirection(direction)
        """
        self.record_method('SetPeriodicBoundaryAnglesDirection', str(getattr(direction, 'value', direction)))

    def get_unit_cell_scan_angle(self) -> Tuple:
        """
        VBA Call
        --------
        Boundary.GetUnitCellScanAngle(&theta, &phi, &dir)

        Returns
        -------
        (theta, phi, dir)
        """
        __retval__ = list(self.query_method_t('GetUnitCellScanAngle', None, VBATypeName.Double, VBATypeName.Double, VBATypeName.Long))
        dir_map = {0: Boundary.Direction.INWARD, 1: Boundary.Direction.OUTWARD}
        __retval__[2] = dir_map.get(__retval__[2])
        return tuple(__retval__)

    def get_unit_cells_distance_dir1(self) -> float:
        """
        VBA Call
        --------
        Boundary.UnitCellDs1()
        """
        return self.query_method_float('UnitCellDs1')

    def get_unit_cells_distance_dir2(self) -> float:
        """
        VBA Call
        --------
        Boundary.UnitCellDs2()
        """
        return self.query_method_float('UnitCellDs2')

    def get_unit_cells_angle_deg(self) -> float:
        """
        VBA Call
        --------
        Boundary.UnitCellAngle()
        """
        return self.query_method_float('UnitCellAngle')

    def set_unit_cells_origin(self, pos_dir1: float, pos_dir2: float) -> None:
        """
        VBA Call
        --------
        Boundary.UnitCellOrigin(pos_dir1, pos_dir2)
        """
        self.record_method('UnitCellOrigin', pos_dir1, pos_dir2)

    def set_unit_cells_fit_to_bounding_box(self, flag: bool = True) -> None:
        """
        VBA Call
        --------
        Boundary.UnitCellFitToBoundingBox(flag)
        """
        self.record_method('UnitCellFitToBoundingBox', flag)

