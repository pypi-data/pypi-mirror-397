'''This file is auto-generated. Do not edit.'''
from .. import IVBAProvider, VBAObjWrapper
from enum import Enum
from typing import Union, Tuple

class Monitor(VBAObjWrapper):
    class FieldType(Enum):
        E_FIELD = 'Efield'
        H_FIELD = 'Hfield'
        POWER_FLOW = 'Powerflow'
        CURRENT = 'Current'
        POWER_LOSS = 'Powerloss'
        E_ENERGY = 'Eenergy'
        H_ENERGY = 'Henergy'
        FARFIELD = 'Farfield'
        FIELD_SOURCE = 'Fieldsource'
        SPACE_CHARGE = 'Spacecharge'
        PARTICLE_CURRENT_DENSITY = 'Particlecurrentdensity'

    class Dimension(Enum):
        PLANE = 'plane'
        VOLUME = 'volume'

    class Direction(Enum):
        X = 'x'
        Y = 'y'
        Z = 'z'

    class Domain(Enum):
        FREQUENCY = 'frequency'
        TIME = 'time'
        STATIC = 'static'

    class Accuracy(Enum):
        LOW = '1e-3'
        MEDIUM = '1e-4'
        HIGH = '1e-5'

    class Origin(Enum):
        BOUNDING_BOX = 'bbox'
        ZERO = 'zero'
        FREE = 'free'

    class SamplingStrategy(Enum):
        FREQUENCIES = 'Frequencies'
        STEPS = 'Steps'
        LINEAR = 'Linear'
        LOGARITHMIC = 'Logarithmic'

    def __init__(self, vbap: IVBAProvider) -> None:
        super().__init__(vbap, 'Monitor')
        self.set_save_history(False)

    def reset(self) -> None:
        """
        VBA Call
        --------
        Monitor.Reset()
        """
        self.record_method('Reset')

    def set_name(self, name: str) -> None:
        """
        VBA Call
        --------
        Monitor.Name(name)
        """
        self.cache_method('Name', name)

    def rename(self, old_name: str, new_name: str) -> None:
        """
        VBA Call
        --------
        Monitor.Rename(old_name, new_name)
        """
        self.record_method('Rename', old_name, new_name)

    def delete(self, name: str) -> None:
        """
        VBA Call
        --------
        Monitor.Delete(name)
        """
        self.record_method('Delete', name)

    def create(self) -> None:
        """
        VBA Call
        --------
        Monitor.Create()
        """
        self.cache_method('Create')
        self.flush_cache('Create Monitor')

    def set_field_type(self, field_type: Union[FieldType, str]) -> None:
        """
        VBA Call
        --------
        Monitor.FieldType(field_type)
        """
        self.cache_method('FieldType', str(getattr(field_type, 'value', field_type)))

    def set_dimension(self, dimension: Union[Dimension, str]) -> None:
        """
        VBA Call
        --------
        Monitor.Dimension(dimension)
        """
        self.cache_method('Dimension', str(getattr(dimension, 'value', dimension)))

    def set_plane_normal(self, direction: Union[Direction, str]) -> None:
        """
        VBA Call
        --------
        Monitor.PlaneNormal(direction)
        """
        self.cache_method('PlaneNormal', str(getattr(direction, 'value', direction)))

    def set_plane_position(self, position: float) -> None:
        """
        VBA Call
        --------
        Monitor.PlanePosition(position)
        """
        self.cache_method('PlanePosition', position)

    def set_domain(self, domain: Union[Domain, str]) -> None:
        """
        VBA Call
        --------
        Monitor.Domain(domain)
        """
        self.cache_method('Domain', str(getattr(domain, 'value', domain)))

    def set_frequency(self, frequency: float) -> None:
        """
        VBA Call
        --------
        Monitor.Frequency(frequency)
        """
        self.cache_method('Frequency', frequency)

    def set_time_start(self, start: float) -> None:
        """
        VBA Call
        --------
        Monitor.Tstart(start)
        """
        self.cache_method('Tstart', start)

    def set_time_step(self, step: float) -> None:
        """
        VBA Call
        --------
        Monitor.Tstep(step)
        """
        self.cache_method('Tstep', step)

    def set_time_end(self, end: float) -> None:
        """
        VBA Call
        --------
        Monitor.Tend(end)
        """
        self.cache_method('Tend', end)

    def set_use_time_end(self, flag: bool) -> None:
        """
        VBA Call
        --------
        Monitor.UseTend(flag)
        """
        self.cache_method('UseTend', flag)

    def set_average_over_time(self, flag: bool) -> None:
        """
        VBA Call
        --------
        Monitor.TimeAverage(flag)
        """
        self.cache_method('TimeAverage', flag)

    def set_repetition_period(self, period: float) -> None:
        """
        VBA Call
        --------
        Monitor.RepetitionPeriod(period)
        """
        self.cache_method('RepetitionPeriod', period)

    def set_automatic_order(self, flag: bool) -> None:
        """
        VBA Call
        --------
        Monitor.AutomaticOrder(flag)
        """
        self.cache_method('AutomaticOrder', flag)

    def set_max_order(self, order: int) -> None:
        """
        VBA Call
        --------
        Monitor.MaxOrder(order)
        """
        self.cache_method('MaxOrder', order)

    def set_number_of_frequency_samples(self, number: int) -> None:
        """
        VBA Call
        --------
        Monitor.FrequencySamples(number)
        """
        self.cache_method('FrequencySamples', number)

    def set_compute_transient_farfield(self, flag: bool) -> None:
        """
        VBA Call
        --------
        Monitor.TransientFarfield(flag)
        """
        self.cache_method('TransientFarfield', flag)

    def set_accuracy(self, accuracy: str) -> None:
        """
        VBA Call
        --------
        Monitor.Accuracy(accuracy)
        """
        self.cache_method('Accuracy', accuracy)

    def set_origin(self, origin: Union[Origin, str]) -> None:
        """
        VBA Call
        --------
        Monitor.Origin(origin)
        """
        self.cache_method('Origin', str(getattr(origin, 'value', origin)))

    def set_user_origin(self, coords: Tuple[float, float, float]) -> None:
        """
        VBA Call
        --------
        Monitor.UserOrigin(coords[0], coords[1], coords[2])
        """
        self.cache_method('UserOrigin', coords[0], coords[1], coords[2])

    def set_frequency_range(self, min: float, max: float) -> None:
        """
        VBA Call
        --------
        Monitor.FrequencyRange(min, max)
        """
        self.cache_method('FrequencyRange', min, max)

    def set_number_of_samples(self, number: int) -> None:
        """
        VBA Call
        --------
        Monitor.Samples(number)
        """
        self.cache_method('Samples', number)

    def set_sampling_strategy(self, strategy: str) -> None:
        """
        VBA Call
        --------
        Monitor.SamplingStrategy(strategy)
        """
        self.cache_method('SamplingStrategy', strategy)

    def set_monitor_value(self, value: float) -> None:
        """
        VBA Call
        --------
        Monitor.MonitorValue(value)
        """
        self.cache_method('MonitorValue', value)

    def set_monitor_value_list(self, frequencies: list[float]) -> None:
        """
        VBA Call
        --------
        Monitor.MonitorValueList(';'.join(str(f) for f in frequencies))
        """
        self.cache_method('MonitorValueList', ';'.join(str(f) for f in frequencies))

    def set_sampling_step(self, step: float) -> None:
        """
        VBA Call
        --------
        Monitor.SampleStep(step)
        """
        self.cache_method('SampleStep', step)

    def set_monitor_value_range(self, min: float, max: float) -> None:
        """
        VBA Call
        --------
        Monitor.MonitorValueRange(min, max)
        """
        self.cache_method('MonitorValueRange', min, max)

    def set_use_subvolume(self, flag: bool) -> None:
        """
        VBA Call
        --------
        Monitor.UseSubvolume(flag)
        """
        self.cache_method('UseSubvolume', flag)

    def set_subvolume(self, min: Tuple[float, float, float], max: Tuple[float, float, float]) -> None:
        """
        VBA Call
        --------
        Monitor.SetSubvolume(min[0], min[1], min[2], max[0], max[1], max[2])
        """
        self.cache_method('SetSubvolume', min[0], min[1], min[2], max[0], max[1], max[2])

    def set_invert_orientation(self, flag: bool) -> None:
        """
        VBA Call
        --------
        Monitor.InvertOrientation(flag)
        """
        self.cache_method('InvertOrientation', flag)

    def set_export_farfield_source(self, flag: bool) -> None:
        """
        VBA Call
        --------
        Monitor.ExportFarfieldSource(flag)
        """
        self.cache_method('ExportFarfieldSource', flag)

    def enable_nearfield_calculation(self, flag: bool) -> None:
        """
        VBA Call
        --------
        Monitor.EnableNearfieldCalculation(flag)
        """
        self.cache_method('EnableNearfieldCalculation', flag)

    def create_using_arbitrary_values(self, frequencies: list[float]) -> None:
        """
        VBA Call
        --------
        Monitor.CreateUsingArbitraryValues(';'.join(str(f) for f in frequencies))
        """
        self.cache_method('CreateUsingArbitraryValues', ';'.join(str(f) for f in frequencies))
        self.flush_cache('Create Monitor')

    def create_using_linear_samples(self, min: float, max: float, num_samples: int) -> None:
        """
        VBA Call
        --------
        Monitor.CreateUsingLinearSamples(min, max, num_samples)
        """
        self.cache_method('CreateUsingLinearSamples', min, max, num_samples)
        self.flush_cache('Create Monitor')

    def create_using_linear_step(self, min: float, max: float, step: float) -> None:
        """
        VBA Call
        --------
        Monitor.CreateUsingLinearStep(min, max, step)
        """
        self.cache_method('CreateUsingLinearStep', min, max, step)
        self.flush_cache('Create Monitor')

    def create_using_log_samples(self, min: float, max: float, num_samples: int) -> None:
        """
        VBA Call
        --------
        Monitor.CreateUsingLogSamples(min, max, num_samples)
        """
        self.cache_method('CreateUsingLogSamples', min, max, num_samples)
        self.flush_cache('Create Monitor')

    def export(self, excitation_name: str, file_path: str, flag: bool) -> None:
        """
        VBA Call
        --------
        Monitor.Export(excitation_name, file_path, flag)
        """
        self.cache_method('Export', excitation_name, file_path, flag)
        self.flush_cache('Export Monitor')

    def set_subvolume_sampling(self, factor_xyz: Tuple[float, float, float]) -> None:
        """
        VBA Call
        --------
        Monitor.SetSubVolumeSampling(factor_xyz[0], factor_xyz[1], factor_xyz[2])
        """
        self.cache_method('SetSubVolumeSampling', factor_xyz[0], factor_xyz[1], factor_xyz[2])

    def change_subvolume_sampling(self, monitor_name: str, factor_xyz: Tuple[float, float, float]) -> None:
        """
        VBA Call
        --------
        Monitor.ChangeSubVolumeSampling(monitor_name, factor_xyz[0], factor_xyz[1], factor_xyz[2])
        """
        self.record_method('ChangeSubVolumeSampling', monitor_name, factor_xyz[0], factor_xyz[1], factor_xyz[2])

    def change_subvolume_sampling_to_history(self, monitor_name: str, factor_xyz: Tuple[float, float, float]) -> None:
        """
        VBA Call
        --------
        Monitor.ChangeSubVolumeSamplingToHistory(monitor_name, factor_xyz[0], factor_xyz[1], factor_xyz[2])
        """
        self.record_method('ChangeSubVolumeSamplingToHistory', monitor_name, factor_xyz[0], factor_xyz[1], factor_xyz[2])

    def get_number_of_monitors(self) -> int:
        """
        VBA Call
        --------
        Monitor.GetNumberOfMonitors()
        """
        return self.query_method_int('GetNumberOfMonitors')

    def get_monitor_name_from_index(self, index: int) -> str:
        """
        VBA Call
        --------
        Monitor.GetMonitorNameFromIndex(index)
        """
        return self.query_method_str('GetMonitorNameFromIndex', index)

    def get_monitor_type_from_index(self, index: int) -> FieldType:
        """
        VBA Call
        --------
        Monitor.GetMonitorTypeFromIndex(index)
        """
        __retval__ = self.query_method_str('GetMonitorTypeFromIndex', index)
        return Monitor.FieldType(__retval__)

    def get_monitor_domain_from_index(self, index: int) -> Domain:
        """
        VBA Call
        --------
        Monitor.GetMonitorDomainFromIndex(index)
        """
        __retval__ = self.query_method_str('GetMonitorDomainFromIndex', index)
        return Monitor.Domain(__retval__)

    def get_monitor_frequency_from_index(self, index: int) -> float:
        """
        VBA Call
        --------
        Monitor.GetMonitorFrequencyFromIndex(index)
        """
        return self.query_method_float('GetMonitorFrequencyFromIndex', index)

    def get_monitor_time_start_from_index(self, index: int) -> float:
        """
        VBA Call
        --------
        Monitor.GetMonitorTstartFromIndex(index)
        """
        return self.query_method_float('GetMonitorTstartFromIndex', index)

    def get_monitor_time_step_from_index(self, index: int) -> float:
        """
        VBA Call
        --------
        Monitor.GetMonitorTstepFromIndex(index)
        """
        return self.query_method_float('GetMonitorTstepFromIndex', index)

    def get_monitor_time_end_from_index(self, index: int) -> float:
        """
        VBA Call
        --------
        Monitor.GetMonitorTendFromIndex(index)
        """
        return self.query_method_float('GetMonitorTendFromIndex', index)

