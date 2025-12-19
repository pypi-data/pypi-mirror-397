'''This file is auto-generated. Do not edit.'''
from .. import IVBAProvider, VBATypeName, VBAObjWrapper
from enum import Enum
from typing import Union, Tuple

class Port(VBAObjWrapper):
    class Orientation(Enum):
        XMIN = 'xmin'
        XMAX = 'xmax'
        YMIN = 'ymin'
        YMAX = 'ymax'
        ZMIN = 'zmin'
        ZMAX = 'zmax'

    class Coordinates(Enum):
        FREE = 'Free'
        FULL = 'Full'
        PICKS = 'Picks'

    class Potential(Enum):
        POSITIVE = 'Positive'
        NEGATIVE = 'Negative'

    class BoundaryPosition(Enum):
        UMIN = 'Umin'
        UMAX = 'Umax'
        VMIN = 'Vmin'
        VMAX = 'Vmax'

    class Shield(Enum):
        NONE = 'none'
        PEC = 'PEC'
        PMC = 'PMC'

    class ModeType(Enum):
        TE = 'TE'
        TM = 'TM'
        TEM = 'TEM'
        QTEM = 'QTEM'
        UNDEF = 'UNDEF'
        DAMPED = 'DAMPED'
        PLANE_WAVE = 'PLANE WAVE'
        FLOQUET = 'FLOQUET'

    class FacePortType(Enum):
        UNKNOWN = 0
        RECTANGULAR = 1
        CYLINDRICAL = 2
        COAXIAL = 3

    class PortType(Enum):
        WAVEGUIDE = 'Waveguide'
        DISCRETE = 'Discrete'

    def __init__(self, vbap: IVBAProvider) -> None:
        super().__init__(vbap, 'Port')
        self.set_save_history(False)

    def reset(self) -> None:
        """
        VBA Call
        --------
        Port.Reset()
        """
        self.cache_method('Reset')

    def delete(self, port_number: int) -> None:
        """
        VBA Call
        --------
        Port.Delete(port_number)
        """
        self.record_method('Delete', port_number)

    def change_number(self, old_port_number: int, new_port_number: int) -> None:
        """
        VBA Call
        --------
        Port.Rename(old_port_number, new_port_number)
        """
        self.record_method('Rename', old_port_number, new_port_number)

    def change_label(self, port_number: int, label: str) -> None:
        """
        VBA Call
        --------
        Port.RenameLabel(port_number, label)
        """
        self.record_method('RenameLabel', port_number, label)

    def create(self) -> None:
        """
        VBA Call
        --------
        Port.Create()
        """
        self.cache_method('Create')
        self.flush_cache('Create Port')

    def modify(self) -> None:
        """
        VBA Call
        --------
        Port.Modify()
        """
        self.cache_method('Modify')
        self.flush_cache('Modify Port')

    def set_number(self, number: int) -> None:
        """
        VBA Call
        --------
        Port.PortNumber(number)
        """
        self.cache_method('PortNumber', number)

    def set_label(self, label: str) -> None:
        """
        VBA Call
        --------
        Port.Label(label)
        """
        self.cache_method('Label', label)

    def set_folder_name(self, folder_name: str) -> None:
        """
        VBA Call
        --------
        Port.Folder(folder_name)
        """
        self.cache_method('Folder', folder_name)

    def set_waveguide_monitor(self, flag: bool = True) -> None:
        """
        VBA Call
        --------
        Port.WaveguideMonitor(flag)
        """
        self.cache_method('WaveguideMonitor', flag)

    def set_number_of_modes(self, count: int) -> None:
        """
        VBA Call
        --------
        Port.NumberOfModes(count)
        """
        self.cache_method('NumberOfModes', count)

    def set_orientation(self, orientation: Union[Orientation, str]) -> None:
        """
        VBA Call
        --------
        Port.Orientation(orientation)
        """
        self.cache_method('Orientation', str(getattr(orientation, 'value', orientation)))

    def set_coordinates(self, coordinates: Union[Coordinates, str]) -> None:
        """
        VBA Call
        --------
        Port.Coordinates(coordinates)
        """
        self.cache_method('Coordinates', str(getattr(coordinates, 'value', coordinates)))

    def set_x_range(self, x_min: float, x_max: float) -> None:
        """
        VBA Call
        --------
        Port.Xrange(x_min, x_max)
        """
        self.cache_method('Xrange', x_min, x_max)

    def set_y_range(self, y_min: float, y_max: float) -> None:
        """
        VBA Call
        --------
        Port.Yrange(y_min, y_max)
        """
        self.cache_method('Yrange', y_min, y_max)

    def set_z_range(self, z_min: float, z_max: float) -> None:
        """
        VBA Call
        --------
        Port.Zrange(z_min, z_max)
        """
        self.cache_method('Zrange', z_min, z_max)

    def add_x_range(self, x_min: float, x_max: float) -> None:
        """
        VBA Call
        --------
        Port.XrangeAdd(x_min, x_max)
        """
        self.cache_method('XrangeAdd', x_min, x_max)

    def add_y_range(self, y_min: float, y_max: float) -> None:
        """
        VBA Call
        --------
        Port.YrangeAdd(y_min, y_max)
        """
        self.cache_method('YrangeAdd', y_min, y_max)

    def add_z_range(self, z_min: float, z_max: float) -> None:
        """
        VBA Call
        --------
        Port.ZrangeAdd(z_min, z_max)
        """
        self.cache_method('ZrangeAdd', z_min, z_max)

    def set_on_boundaries(self, flag: bool = True) -> None:
        """
        VBA Call
        --------
        Port.PortOnBound(flag)
        """
        self.cache_method('PortOnBound', flag)

    def set_clip_picked_port_to_boundaries(self, flag: bool = True) -> None:
        """
        VBA Call
        --------
        Port.ClipPickedPortToBound(flag)
        """
        self.cache_method('ClipPickedPortToBound', flag)

    def set_text_size(self, size: int) -> None:
        """
        VBA Call
        --------
        Port.TextSize(size)
        """
        self.cache_method('TextSize', size)

    def change_text_size(self, port_number: int, size: int) -> None:
        """
        VBA Call
        --------
        Port.ChangeTextSize(port_number, size)
        """
        self.cache_method('ChangeTextSize', port_number, size)

    def set_text_max_limit(self, flag: bool = True) -> None:
        """
        VBA Call
        --------
        Port.TextMaxLimit(flag)
        """
        self.cache_method('TextMaxLimit', flag)

    def set_reference_plane_distance(self, distance: float) -> None:
        """
        VBA Call
        --------
        Port.ReferencePlaneDistance(distance)
        """
        self.cache_method('ReferencePlaneDistance', distance)

    def add_potential_numerically(self, mode_set: int, potential: Union[Potential, str], uv_pos: Tuple[float, float]) -> None:
        """
        VBA Call
        --------
        Port.AddPotentialNumerically(mode_set, potential, uv_pos[0], uv_pos[1])
        """
        self.cache_method('AddPotentialNumerically', mode_set, str(getattr(potential, 'value', potential)), uv_pos[0], uv_pos[1])

    def add_potential_picked(self, mode_set: int, potential: Union[Potential, str], solid_name: str, face_id: int) -> None:
        """
        VBA Call
        --------
        Port.AddPotentialPicked(mode_set, potential, solid_name, face_id)
        """
        self.cache_method('AddPotentialPicked', mode_set, str(getattr(potential, 'value', potential)), solid_name, face_id)

    def add_potential_edge_picked(self, mode_set: int, potential: Union[Potential, str], solid_name: str, edge_id: int) -> None:
        """
        VBA Call
        --------
        Port.AddPotentialEdgePicked(mode_set, potential, solid_name, edge_id)
        """
        self.cache_method('AddPotentialEdgePicked', mode_set, str(getattr(potential, 'value', potential)), solid_name, edge_id)

    def set_adjust_polarization(self, flag: bool = True) -> None:
        """
        VBA Call
        --------
        Port.AdjustPolarization(flag)
        """
        self.cache_method('AdjustPolarization', flag)

    def set_polarization_angle_deg(self, angle_deg: float) -> None:
        """
        VBA Call
        --------
        Port.PolarizationAngle(angle_deg)
        """
        self.cache_method('PolarizationAngle', angle_deg)

    def set_port_impedance_and_calibration_evaluation(self, flag: bool = True) -> None:
        """
        VBA Call
        --------
        Port.PortImpedanceAndCalibration(flag)
        """
        self.cache_method('PortImpedanceAndCalibration', flag)

    def add_mode_line_by_point(self, line_number: int, start_coords: Tuple[float, float, float], end_coords: Tuple[float, float, float]) -> None:
        """
        VBA Call
        --------
        Port.AddModeLineByPoint(line_number, start_coords[0], start_coords[1], start_coords[2], end_coords[0], end_coords[1], end_coords[2])
        """
        self.cache_method('AddModeLineByPoint', line_number, start_coords[0], start_coords[1], start_coords[2], end_coords[0], end_coords[1], end_coords[2])

    def add_mode_line_by_face(self, line_number: int, start_coords: Tuple[float, float, float], solid_name: str, face_id: int, reverse: bool = False) -> None:
        """
        VBA Call
        --------
        Port.AddModeLineByFace(line_number, start_coords[0], start_coords[1], start_coords[2], solid_name, face_id, reverse)
        """
        self.cache_method('AddModeLineByFace', line_number, start_coords[0], start_coords[1], start_coords[2], solid_name, face_id, reverse)

    def add_mode_line_by_boundary(self, line_number: int, start_coords: Tuple[float, float, float], position: Union[BoundaryPosition, str], reverse: bool = False) -> None:
        """
        VBA Call
        --------
        Port.AddModeLineByBoundary(line_number, start_coords[0], start_coords[1], start_coords[2], position, reverse)
        """
        self.cache_method('AddModeLineByBoundary', line_number, start_coords[0], start_coords[1], start_coords[2], str(getattr(position, 'value', position)), reverse)

    def add_mode_line(self, mode_number: int, impedance_line_number: int, calibration_line_number: int, polarization_line_number: int) -> None:
        """
        VBA Call
        --------
        Port.AddModeLine(mode_number, impedance_line_number, calibration_line_number, polarization_line_number)
        """
        self.cache_method('AddModeLine', mode_number, impedance_line_number, calibration_line_number, polarization_line_number)

    def set_estimation(self, port_number: int, value: float) -> None:
        """
        VBA Call
        --------
        Port.SetEstimation(port_number, value)
        """
        self.cache_method('SetEstimation', port_number, value)

    def set_single_ended(self, flag: bool = True) -> None:
        """
        VBA Call
        --------
        Port.SingleEnded(flag)
        """
        self.cache_method('SingleEnded', flag)

    def set_shield(self, key: Union[Shield, str]) -> None:
        """
        VBA Call
        --------
        Port.Shield(key)
        """
        self.cache_method('Shield', str(getattr(key, 'value', key)))

    def get_frequency(self, port_number: int, mode_number: int) -> float:
        """
        VBA Call
        --------
        Port.GetFrequency(port_number, mode_number)
        """
        return self.query_method_float('GetFrequency', port_number, mode_number)

    def get_cutoff_frequency(self, port_number: int, mode_number: int) -> float:
        """
        VBA Call
        --------
        Port.GetFcutoff(port_number, mode_number)
        """
        return self.query_method_float('GetFcutoff', port_number, mode_number)

    def get_mode_type(self, port_number: int, mode_number: int) -> ModeType:
        """
        VBA Call
        --------
        Port.GetModeType(port_number, mode_number)
        """
        __retval__ = self.query_method_str('GetModeType', port_number, mode_number)
        return Port.ModeType(__retval__)

    def get_beta(self, port_number: int, mode_number: int) -> float:
        """
        VBA Call
        --------
        Port.GetBeta(port_number, mode_number)
        """
        return self.query_method_float('GetBeta', port_number, mode_number)

    def get_alpha(self, port_number: int, mode_number: int) -> float:
        """
        VBA Call
        --------
        Port.GetAlpha(port_number, mode_number)
        """
        return self.query_method_float('GetAlpha', port_number, mode_number)

    def get_accuracy(self, port_number: int, mode_number: int) -> float:
        """
        VBA Call
        --------
        Port.GetAccuracy(port_number, mode_number)
        """
        return self.query_method_float('GetAccuracy', port_number, mode_number)

    def get_wave_impedance(self, port_number: int, mode_number: int) -> float:
        """
        VBA Call
        --------
        Port.GetWaveImpedance(port_number, mode_number)
        """
        return self.query_method_float('GetWaveImpedance', port_number, mode_number)

    def get_line_impedance(self, port_number: int, mode_number: int) -> float:
        """
        VBA Call
        --------
        Port.GetLineImpedance(port_number, mode_number)
        """
        return self.query_method_float('GetLineImpedance', port_number, mode_number)

    def get_line_impedance_broad_by_index(self, port_number: int, mode_number: int, index: int) -> float:
        """
        VBA Call
        --------
        Port.GetLineImpedanceBroadByIndex(port_number, mode_number, index)
        """
        return self.query_method_float('GetLineImpedanceBroadByIndex', port_number, mode_number, index)

    def get_line_impedance_broad_by_frequency(self, port_number: int, mode_number: int, frequency: float) -> float:
        """
        VBA Call
        --------
        Port.GetLineImpedanceBroadByFreq(port_number, mode_number, frequency)
        """
        return self.query_method_float('GetLineImpedanceBroadByFreq', port_number, mode_number, frequency)

    def get_type(self, port_number: int) -> PortType:
        """
        VBA Call
        --------
        Port.GetType(port_number)
        """
        __retval__ = self.query_method_str('GetType', port_number)
        return Port.PortType(__retval__)

    def get_number_of_modes(self, port_number: int) -> int:
        """
        VBA Call
        --------
        Port.GetNumberOfModes(port_number)
        """
        return self.query_method_int('GetNumberOfModes', port_number)

    def get_port_mesh_location(self, port_number: int) -> Tuple:
        """
        VBA Call
        --------
        Port.GetPortMeshLocation(port_number, &orientation, &x_min, &x_max, &y_min, &y_max, &z_min, &z_max)

        Returns
        -------
        (orientation, x_min, x_max, y_min, y_max, z_min, z_max)
        """
        return self.query_method_t('GetPortMeshLocation', None, port_number, VBATypeName.Long, VBATypeName.Long, VBATypeName.Long, VBATypeName.Long, VBATypeName.Long, VBATypeName.Long, VBATypeName.Long)

    def get_port_mesh_coordinates(self, port_number: int) -> Tuple:
        """
        VBA Call
        --------
        Port.GetPortMeshCoordinates(port_number, &orientation, &x_min, &x_max, &y_min, &y_max, &z_min, &z_max)

        Returns
        -------
        (orientation, x_min, x_max, y_min, y_max, z_min, z_max)
        """
        return self.query_method_t('GetPortMeshCoordinates', None, port_number, VBATypeName.Long, VBATypeName.Double, VBATypeName.Double, VBATypeName.Double, VBATypeName.Double, VBATypeName.Double, VBATypeName.Double)

    def get_port_center_coordinates(self, port_number: int) -> Tuple:
        """
        VBA Call
        --------
        Port.GetPortCenterCoordinates(port_number, &x, &y, &z)

        Returns
        -------
        (x, y, z)
        """
        return self.query_method_t('GetPortCenterCoordinates', None, port_number, VBATypeName.Double, VBATypeName.Double, VBATypeName.Double)

    def get_face_port_type_and_size(self, port_number: int) -> Tuple:
        """
        VBA Call
        --------
        Port.GetFacePortTypeAndSize(port_number, &face_port_type, &size1, &size2)

        Returns
        -------
        (face_port_type, size1, size2)
        """
        return self.query_method_t('GetFacePortTypeAndSize', None, port_number, VBATypeName.Long, VBATypeName.Double, VBATypeName.Double)

    def get_label(self, port_number: int) -> str:
        """
        VBA Call
        --------
        Port.GetLabel(port_number)
        """
        return self.query_method_str('GetLabel', port_number)

