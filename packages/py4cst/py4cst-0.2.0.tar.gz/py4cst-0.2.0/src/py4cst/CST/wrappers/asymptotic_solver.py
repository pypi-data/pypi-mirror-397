'''This file is auto-generated. Do not edit.'''
from .. import IVBAProvider, VBAObjWrapper
from enum import Enum
from typing import Union
import cmath

class AsymptoticSolver(VBAObjWrapper):
    class SolverType(Enum):
        SBR = 'SBR'
        SBR_RAYTUBES = 'SBR_RAYTUBES'

    class SolverMode(Enum):
        MONOSTATIC_SCATTERING = 'MONOSTATIC_SCATTERING'
        BISTATIC_SCATTERING = 'BISTATIC_SCATTERING'
        FIELD_SOURCES = 'FIELD_SOURCES'
        RANGE_PROFILES = 'RANGE_PROFILES'

    class AccuracyLevel(Enum):
        LOW = 'LOW'
        MEDIUM = 'MEDIUM'
        HIGH = 'HIGH'
        CUSTOM = 'CUSTOM'

    class RangeProfilesWindow(Enum):
        RECTANGULAR = 'RECTANGULAR'
        HANNING = 'HANNING'
        HAMMING = 'HAMMING'
        BLACKMAN = 'BLACKMAN'

    class RangeProfilesMode(Enum):
        RANGE_EXTEND = 'RANGE_EXTEND'
        BANDWIDTH = 'BANDWIDTH'

    class AngleSweep(Enum):
        POINT = 'POINT'
        THETA = 'THETA'
        PHI = 'PHI'
        BOTH = 'BOTH'

    def __init__(self, vbap: IVBAProvider) -> None:
        super().__init__(vbap, 'AsymptoticSolver')
        self.set_save_history(False)

    def set_solver_type(self, solver_type: Union[SolverType, str]) -> None:
        """
        VBA Call
        --------
        AsymptoticSolver.SetSolverType(solver_type)
        """
        self.record_method('SetSolverType', str(getattr(solver_type, 'value', solver_type)))

    def set_solver_mode(self, solver_mode: Union[SolverMode, str]) -> None:
        """
        VBA Call
        --------
        AsymptoticSolver.SetSolverMode(solver_mode)
        """
        self.record_method('SetSolverMode', str(getattr(solver_mode, 'value', solver_mode)))

    def set_accuracy_level(self, accuracy_level: Union[AccuracyLevel, str]) -> None:
        """
        VBA Call
        --------
        AsymptoticSolver.SetAccuracyLevel(accuracy_level)
        """
        self.record_method('SetAccuracyLevel', str(getattr(accuracy_level, 'value', accuracy_level)))

    def set_solver_store_results_as_tables_only(self, flag: bool = True) -> None:
        """
        VBA Call
        --------
        AsymptoticSolver.SetSolverStoreResultsAsTablesOnly(flag)
        """
        self.record_method('SetSolverStoreResultsAsTablesOnly', flag)

    def set_calculate_rcs_map_for_1d_sweeps(self, flag: bool = True) -> None:
        """
        VBA Call
        --------
        AsymptoticSolver.CalculateRCSMapFor1DSweeps(flag)
        """
        self.record_method('CalculateRCSMapFor1DSweeps', flag)

    def set_calculate_monitors(self, flag: bool = True) -> None:
        """
        VBA Call
        --------
        AsymptoticSolver.Set('CalculateMonitors', flag)
        """
        self.record_method('Set', 'CalculateMonitors', flag)

    def reset_polarizations(self) -> None:
        """
        VBA Call
        --------
        AsymptoticSolver.ResetPolarizations()
        """
        self.record_method('ResetPolarizations')

    def add_horizontal_polarization(self, value: float) -> None:
        """
        VBA Call
        --------
        AsymptoticSolver.AddHorizontalPolarization(value)
        """
        self.record_method('AddHorizontalPolarization', value)

    def add_vertical_polarization(self, value: float) -> None:
        """
        VBA Call
        --------
        AsymptoticSolver.AddVerticalPolarization(value)
        """
        self.record_method('AddVerticalPolarization', value)

    def add_lhc_polarization(self, value: float) -> None:
        """
        VBA Call
        --------
        AsymptoticSolver.AddLHCPolarization(value)
        """
        self.record_method('AddLHCPolarization', value)

    def add_rhc_polarization(self, value: float) -> None:
        """
        VBA Call
        --------
        AsymptoticSolver.AddRHCPolarization(value)
        """
        self.record_method('AddRHCPolarization', value)

    def add_custom_polarization(self, theta: complex, phi: complex) -> None:
        """
        VBA Call
        --------
        AsymptoticSolver.AddCustomPolarization(real(theta), imag(theta), real(phi), imag(phi))
        """
        self.record_method('AddCustomPolarization', theta.real, theta.imag, phi.real, phi.imag)

    def set_solver_maximum_number_of_reflections(self, number: int) -> None:
        """
        VBA Call
        --------
        AsymptoticSolver.SetSolverMaximumNumberOfReflections(number)
        """
        self.record_method('SetSolverMaximumNumberOfReflections', number)

    def set_solver_range_profiles_center_frequency(self, freq: float) -> None:
        """
        VBA Call
        --------
        AsymptoticSolver.SetSolverRangeProfilesCenterFrequency(freq)
        """
        self.record_method('SetSolverRangeProfilesCenterFrequency', freq)

    def set_solver_range_profiles_automatic(self, flag: bool = True) -> None:
        """
        VBA Call
        --------
        AsymptoticSolver.SetSolverRangeProfilesAutomatic(flag)
        """
        self.record_method('SetSolverRangeProfilesAutomatic', flag)

    def set_solver_range_profiles_number_of_samples(self, number: int) -> None:
        """
        VBA Call
        --------
        AsymptoticSolver.SetSolverRangeProfilesNumberOfSamples(number)
        """
        self.record_method('SetSolverRangeProfilesNumberOfSamples', number)

    def set_solver_range_profiles_window_function(self, window: Union[RangeProfilesWindow, str]) -> None:
        """
        VBA Call
        --------
        AsymptoticSolver.SetSolverRangeProfilesWindowFunction(window)
        """
        self.record_method('SetSolverRangeProfilesWindowFunction', str(getattr(window, 'value', window)))

    def set_solver_range_profiles_spec_mode(self, mode: Union[RangeProfilesMode, str]) -> None:
        """
        VBA Call
        --------
        AsymptoticSolver.SetSolverRangeProfilesSpecMode(mode)
        """
        self.record_method('SetSolverRangeProfilesSpecMode', str(getattr(mode, 'value', mode)))

    def set_solver_range_profiles_range_extend(self, ext: float) -> None:
        """
        VBA Call
        --------
        AsymptoticSolver.SetSolverRangeProfilesRangeExtend(ext)
        """
        self.record_method('SetSolverRangeProfilesRangeExtend', ext)

    def set_solver_range_profiles_bandwidth(self, bw: float) -> None:
        """
        VBA Call
        --------
        AsymptoticSolver.SetSolverRangeProfilesBandwidth(bw)
        """
        self.record_method('SetSolverRangeProfilesBandwidth', bw)

    def reset_frequency_list(self) -> None:
        """
        VBA Call
        --------
        AsymptoticSolver.ResetFrequencyList()
        """
        self.record_method('ResetFrequencyList')

    def add_frequency_sweep(self, f_min: float, f_max: float, f_step: float) -> None:
        """
        VBA Call
        --------
        AsymptoticSolver.AddFrequencySweep(f_min, f_max, f_step)
        """
        self.record_method('AddFrequencySweep', f_min, f_max, f_step)

    def reset_excitation_angle_list(self) -> None:
        """
        VBA Call
        --------
        AsymptoticSolver.ResetExcitationAngleList()
        """
        self.record_method('ResetExcitationAngleList')

    def add_excitation_angle_sweep_deg(self, angle_sweep_type: Union[AngleSweep, str], theta_min: float, theta_max: float, theta_step: float, phi_min: float, phi_max: float, phi_step: float) -> None:
        """
        VBA Call
        --------
        AsymptoticSolver.AddExcitationAngleSweep(angle_sweep_type, theta_min, theta_max, theta_step, phi_min, phi_max, phi_step)
        """
        self.record_method('AddExcitationAngleSweep', str(getattr(angle_sweep_type, 'value', angle_sweep_type)), theta_min, theta_max, theta_step, phi_min, phi_max, phi_step)

    def add_excitation_angle_sweep_with_rays_deg(self, angle_sweep_type: Union[AngleSweep, str], theta_min: float, theta_max: float, theta_step: float, phi_min: float, phi_max: float, phi_step: float) -> None:
        """
        VBA Call
        --------
        AsymptoticSolver.AddExcitationAngleSweepWithRays(angle_sweep_type, theta_min, theta_max, theta_step, phi_min, phi_max, phi_step)
        """
        self.record_method('AddExcitationAngleSweepWithRays', str(getattr(angle_sweep_type, 'value', angle_sweep_type)), theta_min, theta_max, theta_step, phi_min, phi_max, phi_step)

    def reset_field_sources(self) -> None:
        """
        VBA Call
        --------
        AsymptoticSolver.ResetFieldSources()
        """
        self.record_method('ResetFieldSources')

    def set_field_source_active(self, field_source_name: str, flag: bool = True) -> None:
        """
        VBA Call
        --------
        AsymptoticSolver.SetFieldSourceActive(field_source_name, flag)
        """
        self.record_method('SetFieldSourceActive', field_source_name, flag)

    def set_field_source_phasor(self, field_source_name: str, phasor: complex) -> None:
        """
        VBA Call
        --------
        AsymptoticSolver.SetFieldSourcePhasor(field_source_name, abs(phasor), angle(phasor))
        """
        self.record_method('SetFieldSourcePhasor', field_source_name, abs(phasor), cmath.phase(phasor))

    def set_field_source_store_rays(self, field_source_name: str, flag: bool = True) -> None:
        """
        VBA Call
        --------
        AsymptoticSolver.SetFieldSourceRays(field_source_name, flag)
        """
        self.record_method('SetFieldSourceRays', field_source_name, flag)

    def set_simultaneous_field_source_excitation(self, flag: bool = True) -> None:
        """
        VBA Call
        --------
        AsymptoticSolver.SimultaneousFieldSourceExcitation(flag)
        """
        self.record_method('SimultaneousFieldSourceExcitation', flag)

    def set_calculate_s_params(self, flag: bool = True) -> None:
        """
        VBA Call
        --------
        AsymptoticSolver.Set('CalculateSParameters', flag)
        """
        self.record_method('Set', 'CalculateSParameters', flag)

    def reset_observation_angle_list(self) -> None:
        """
        VBA Call
        --------
        AsymptoticSolver.ResetObservationAngleList()
        """
        self.record_method('ResetObservationAngleList')

    def add_observation_angle_sweep_deg(self, angle_sweep_type: Union[AngleSweep, str], theta_min: float, theta_max: float, theta_step: float, phi_min: float, phi_max: float, phi_step: float) -> None:
        """
        VBA Call
        --------
        AsymptoticSolver.AddObservationAngleSweep(angle_sweep_type, theta_min, theta_max, theta_step, phi_min, phi_max, phi_step)
        """
        self.record_method('AddObservationAngleSweep', str(getattr(angle_sweep_type, 'value', angle_sweep_type)), theta_min, theta_max, theta_step, phi_min, phi_max, phi_step)

    def add_observation_angle_sweep_with_rays_deg(self, angle_sweep_type: Union[AngleSweep, str], theta_min: float, theta_max: float, theta_step: float, phi_min: float, phi_max: float, phi_step: float) -> None:
        """
        VBA Call
        --------
        AsymptoticSolver.AddObservationAngleSweepWithRays(angle_sweep_type, theta_min, theta_max, theta_step, phi_min, phi_max, phi_step)
        """
        self.record_method('AddObservationAngleSweepWithRays', str(getattr(angle_sweep_type, 'value', angle_sweep_type)), theta_min, theta_max, theta_step, phi_min, phi_max, phi_step)

    def set_use_parallelization(self, flag: bool = True) -> None:
        """
        VBA Call
        --------
        AsymptoticSolver.UseParallelization(flag)
        """
        self.record_method('UseParallelization', flag)

    def set_maximum_number_of_threads(self, number: int) -> None:
        """
        VBA Call
        --------
        AsymptoticSolver.MaximumNumberOfThreads(number)
        """
        self.record_method('MaximumNumberOfThreads', number)

    def set_remote_calculation(self, flag: bool = True) -> None:
        """
        VBA Call
        --------
        AsymptoticSolver.RemoteCalculation(flag)
        """
        self.record_method('RemoteCalculation', flag)

    def set_distributed_computing(self, flag: bool = True) -> None:
        """
        VBA Call
        --------
        AsymptoticSolver.DistributedComputing(flag)
        """
        self.record_method('DistributedComputing', flag)

    def set_number_of_distributed_computing_nodes(self, number: int) -> None:
        """
        VBA Call
        --------
        AsymptoticSolver.DistributedComputingNodes(number)
        """
        self.record_method('DistributedComputingNodes', number)

    def start(self) -> bool:
        """
        VBA Call
        --------
        AsymptoticSolver.Start()
        """
        __retval__ = self.query_method_int('Start')
        return bool(__retval__)

