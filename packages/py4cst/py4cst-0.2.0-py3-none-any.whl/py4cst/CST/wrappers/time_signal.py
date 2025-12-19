'''This file is auto-generated. Do not edit.'''
from .. import IVBAProvider, VBAObjWrapper
from enum import Enum
from typing import Union

class TimeSignal(VBAObjWrapper):
    class SignalType(Enum):
        GAUSSIAN = 'Gaussian'
        RECTANGULAR = 'Rectangular'
        SINE_STEP = 'Sine step'
        SINE = 'Sine'
        SMOOTH_STEP = 'Smooth step'
        CONSTANT = 'Constant'
        DOUBLE_EXPONENTIAL = 'Double exponential'
        IMPULSE = 'Impulse'
        USER = 'User'
        IMPORT = 'Import'

    class ProblemType(Enum):
        HIGH_FREQUENCY = 'High Frequency'
        LOW_FREQUENCY = 'Low Frequency'

    def __init__(self, vbap: IVBAProvider) -> None:
        super().__init__(vbap, 'TimeSignal')
        self.set_save_history(False)

    def reset(self) -> None:
        """
        VBA Call
        --------
        TimeSignal.Reset()
        """
        self.cache_method('Reset')

    def set_name(self, name: str) -> None:
        """
        VBA Call
        --------
        TimeSignal.Name(name)
        """
        self.cache_method('Name', name)

    def set_id(self, id: int) -> None:
        """
        VBA Call
        --------
        TimeSignal.Id(id)
        """
        self.cache_method('Id', id)

    def rename(self, old_name: str, new_name: str, problem_type: Union[ProblemType, str]) -> None:
        """
        VBA Call
        --------
        TimeSignal.Rename(old_name, new_name, problem_type)
        """
        self.record_method('Rename', old_name, new_name, str(getattr(problem_type, 'value', problem_type)))

    def delete(self, name: str, problem_type: Union[ProblemType, str]) -> None:
        """
        VBA Call
        --------
        TimeSignal.Delete(name, problem_type)
        """
        self.record_method('Delete', name, str(getattr(problem_type, 'value', problem_type)))

    def create(self) -> None:
        """
        VBA Call
        --------
        TimeSignal.Create()
        """
        self.cache_method('Create')
        self.flush_cache('Create TimeSignal')

    def set_file_name(self, file_name: str) -> None:
        """
        VBA Call
        --------
        TimeSignal.FileName(file_name)
        """
        self.cache_method('FileName', file_name)

    def set_use_copy_only(self, flag: bool = True) -> None:
        """
        VBA Call
        --------
        TimeSignal.UseCopyOnly(flag)
        """
        self.cache_method('UseCopyOnly', flag)

    def set_f_min(self, value: float) -> None:
        """
        VBA Call
        --------
        TimeSignal.Fmin(value)
        """
        self.cache_method('Fmin', value)

    def set_f_max(self, value: float) -> None:
        """
        VBA Call
        --------
        TimeSignal.Fmax(value)
        """
        self.cache_method('Fmax', value)

    def set_total_time(self, time: float) -> None:
        """
        VBA Call
        --------
        TimeSignal.Ttotal(time)
        """
        self.cache_method('Ttotal', time)

    def set_rise_time(self, time: float) -> None:
        """
        VBA Call
        --------
        TimeSignal.Trise(time)
        """
        self.cache_method('Trise', time)

    def set_hold_time(self, time: float) -> None:
        """
        VBA Call
        --------
        TimeSignal.Thold(time)
        """
        self.cache_method('Thold', time)

    def set_fall_time(self, time: float) -> None:
        """
        VBA Call
        --------
        TimeSignal.Tfall(time)
        """
        self.cache_method('Tfall', time)

    def set_vertical_offset(self, offset: float) -> None:
        """
        VBA Call
        --------
        TimeSignal.Voffset(offset)
        """
        self.cache_method('Voffset', offset)

    def set_amplitude_rise_percent(self, percent: float) -> None:
        """
        VBA Call
        --------
        TimeSignal.AmplitudeRisePercent(percent)
        """
        self.cache_method('AmplitudeRisePercent', percent)

    def set_rise_factor(self, factor: float) -> None:
        """
        VBA Call
        --------
        TimeSignal.RiseFactor(factor)
        """
        self.cache_method('RiseFactor', factor)

    def set_chirp_rate(self, rate: float) -> None:
        """
        VBA Call
        --------
        TimeSignal.ChirpRate(rate)
        """
        self.cache_method('ChirpRate', rate)

    def set_frequency(self, frequency: float) -> None:
        """
        VBA Call
        --------
        TimeSignal.Frequency(frequency)
        """
        self.cache_method('Frequency', frequency)

    def set_phase(self, phase: float) -> None:
        """
        VBA Call
        --------
        TimeSignal.Phase(phase)
        """
        self.cache_method('Phase', phase)

    def set_amplitude(self, amplitude: float) -> None:
        """
        VBA Call
        --------
        TimeSignal.Amplitude(amplitude)
        """
        self.cache_method('Amplitude', amplitude)

    def set_start_amplitude(self, amplitude: float) -> None:
        """
        VBA Call
        --------
        TimeSignal.StartAmplitude(amplitude)
        """
        self.cache_method('StartAmplitude', amplitude)

    def set_end_amplitude(self, amplitude: float) -> None:
        """
        VBA Call
        --------
        TimeSignal.EndAmplitude(amplitude)
        """
        self.cache_method('EndAmplitude', amplitude)

    def set_signal_type(self, signal_type: Union[SignalType, str]) -> None:
        """
        VBA Call
        --------
        TimeSignal.SignalType(signal_type)
        """
        self.cache_method('SignalType', str(getattr(signal_type, 'value', signal_type)))

    def set_min_number_of_user_signal_samples(self, number: int) -> None:
        """
        VBA Call
        --------
        TimeSignal.MinUserSignalSamples(number)
        """
        self.cache_method('MinUserSignalSamples', number)

    def set_periodic(self, flag: bool = True) -> None:
        """
        VBA Call
        --------
        TimeSignal.Periodic(flag)
        """
        self.cache_method('Periodic', flag)

    def set_problem_type(self, problem_type: Union[ProblemType, str]) -> None:
        """
        VBA Call
        --------
        TimeSignal.ProblemType(problem_type)
        """
        self.cache_method('ProblemType', str(getattr(problem_type, 'value', problem_type)))

    def set_excitation_signal_as_reference(self, signal_name: str, problem_type: Union[ProblemType, str]) -> None:
        """
        VBA Call
        --------
        TimeSignal.ExcitationSignalAsReference(signal_name, problem_type)
        """
        self.cache_method('ExcitationSignalAsReference', signal_name, str(getattr(problem_type, 'value', problem_type)))

    def resample_excitation_signal(self, signal_name: str, t_min: float, t_max: float, t_step: float, problem_type: Union[ProblemType, str]) -> None:
        """
        VBA Call
        --------
        TimeSignal.ExcitationSignalResample(signal_name, t_min, t_max, t_step, problem_type)
        """
        self.cache_method('ExcitationSignalResample', signal_name, t_min, t_max, t_step, str(getattr(problem_type, 'value', problem_type)))

    def get_next_id(self) -> int:
        """
        VBA Call
        --------
        TimeSignal.GetNextId()
        """
        return self.query_method_int('GetNextId')

