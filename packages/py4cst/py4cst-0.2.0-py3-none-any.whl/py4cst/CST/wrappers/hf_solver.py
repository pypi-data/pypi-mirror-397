'''This file is auto-generated. Do not edit.'''
from .. import IVBAProvider, VBAObjWrapper
from ..frequency_range_list import FrequencyRangeList
from enum import Enum
from typing import Union

class Solver(VBAObjWrapper):
    class PmlType(Enum):
        CONV_PML = 'ConvPML'
        GTPML = 'GTPML'

    class UpdateSchema(Enum):
        GAP = 'Gap'
        DISTRIBUTED = 'Distributed'

    class SuppressTss(Enum):
        TRUE = 'True'
        ALL = 'All'
        FALSE = 'False'
        NONE = 'None'
        RESET = 'Reset'
        PORTS = 'Ports'
        LUMPED_ELEMENTS = 'LumpedElements'
        PROBES = 'Probes'
        UI_MONITORS = 'UIMonitors'

    class Excitation(Enum):
        PORT_MODE = 'portmode'
        PLANE_WAVE = 'planewave'
        FIELD_SOURCE = 'fieldsource'
        FARFIELD_SOURCE = 'farfieldsource'

    class SimultExcitOffset(Enum):
        TIME_SHIFT = 'Timeshift'
        PHASE_SHIFT = 'Phaseshift'

    class Absorb(Enum):
        AUTOMATIC = 'Automatic'
        ACTIVATE = 'Activate'
        DEACTIVATE = 'Deactivate'

    class ExcitationType(Enum):
        AUTOMATIC = 'Automatic'
        STANDARD = 'Standard'
        BROADBAND = 'Broadband'

    class DecompositionType(Enum):
        AUTOMATIC = 'Automatic'
        STANDARD = 'Standard'
        BROADBAND = 'Broadband'

    class Window(Enum):
        RECTANGULAR = 'Rectangular'
        COSINE = 'Cosine'

    class HftdDispUpdateScheme(Enum):
        STANDARD = 'Standard'
        GENERALIZED = 'Generalized'
        AUTOMATIC = 'Automatic'

    class SubcycleState(Enum):
        AUTOMATIC = 'Automatic'
        ACTIVATE = 'Activate'
        DEACTIVATE = 'Deactivate'

    def __init__(self, vbap: IVBAProvider) -> None:
        super().__init__(vbap, 'Solver')
        self.set_save_history(False)

    def set_time_between_updates(self, value: int) -> None:
        """
        VBA Call
        --------
        Solver.TimeBetweenUpdates(value)
        """
        self.record_method('TimeBetweenUpdates', value)

    def set_frequency_range(self, min_freq: float, max_freq: float) -> None:
        """
        VBA Call
        --------
        Solver.FrequencyRange(min_freq, max_freq)
        """
        self.record_method('FrequencyRange', min_freq, max_freq)

    def calculate_zy_matrices(self) -> None:
        """
        VBA Call
        --------
        Solver.CalculateZandYMatrices()
        """
        self.record_method('CalculateZandYMatrices')

    def calculate_vswr(self) -> None:
        """
        VBA Call
        --------
        Solver.CalculateVSWR()
        """
        self.record_method('CalculateVSWR')

    def set_pba_fill_limit(self, percentage: float) -> None:
        """
        VBA Call
        --------
        Solver.PBAFillLimit(percentage)
        """
        self.record_method('PBAFillLimit', percentage)

    def set_use_split_components(self, flag: bool) -> None:
        """
        VBA Call
        --------
        Solver.UseSplitComponents(flag)
        """
        self.record_method('UseSplitComponents', flag)

    def set_always_exclude_pec(self, flag: bool) -> None:
        """
        VBA Call
        --------
        Solver.AlwaysExcludePec(flag)
        """
        self.record_method('AlwaysExcludePec', flag)

    def set_mpi_parallelization(self, flag: bool) -> None:
        """
        VBA Call
        --------
        Solver.MPIParallelization(flag)
        """
        self.record_method('MPIParallelization', flag)

    def get_min_frequency(self) -> float:
        """
        VBA Call
        --------
        Solver.GetFmin()
        """
        return self.query_method_float('GetFmin')

    def get_max_frequency(self) -> float:
        """
        VBA Call
        --------
        Solver.GetFmax()
        """
        return self.query_method_float('GetFmax')

    def get_number_of_frequency_samples(self) -> int:
        """
        VBA Call
        --------
        Solver.GetNFsamples()
        """
        return self.query_method_int('GetNFsamples')

    def get_number_of_ports(self) -> int:
        """
        VBA Call
        --------
        Solver.GetNumberOfPorts()
        """
        return self.query_method_int('GetNumberOfPorts')

    def are_ports_subsequently_named(self) -> bool:
        """
        VBA Call
        --------
        Solver.ArePortsSubsequentlyNamed()
        """
        return self.query_method_bool('ArePortsSubsequentlyNamed')

    def get_stimulation_port(self) -> int:
        """
        VBA Call
        --------
        Solver.GetStimulationPort()
        """
        return self.query_method_int('GetStimulationPort')

    def get_stimulation_mode(self) -> int:
        """
        VBA Call
        --------
        Solver.GetStimulationMode()
        """
        return self.query_method_int('GetStimulationMode')

    def get_total_simulation_time(self) -> int:
        """
        VBA Call
        --------
        Solver.GetTotalSimulationTime()
        """
        return self.query_method_int('GetTotalSimulationTime')

    def get_matrix_calculation_time(self) -> int:
        """
        VBA Call
        --------
        Solver.GetMatrixCalculationTime()
        """
        return self.query_method_int('GetMatrixCalculationTime')

    def get_last_solver_time(self) -> int:
        """
        VBA Call
        --------
        Solver.GetLastSolverTime()
        """
        return self.query_method_int('GetLastSolverTime')

    def start(self) -> None:
        """
        VBA Call
        --------
        Solver.Start()
        """
        self.record_method('Start')

    def set_normalize_impedances_automatically(self, flag: bool) -> None:
        """
        VBA Call
        --------
        Solver.AutoNormImpedance(flag)
        """
        self.record_method('AutoNormImpedance', flag)

    def set_norming_impedance(self, impedance: float) -> None:
        """
        VBA Call
        --------
        Solver.NormingImpedance(impedance)
        """
        self.record_method('NormingImpedance', impedance)

    def set_mesh_adaptation(self, flag: bool) -> None:
        """
        VBA Call
        --------
        Solver.MeshAdaption(flag)
        """
        self.record_method('MeshAdaption', flag)

    def set_use_distributed_computing(self, flag: bool) -> None:
        """
        VBA Call
        --------
        Solver.UseDistributedComputing(flag)
        """
        self.record_method('UseDistributedComputing', flag)

    def set_distribute_matrix_calculation(self, flag: bool) -> None:
        """
        VBA Call
        --------
        Solver.DistributeMatrixCalculation(flag)
        """
        self.record_method('DistributeMatrixCalculation', flag)

    def set_use_hardware_acceleration(self, flag: bool) -> None:
        """
        VBA Call
        --------
        Solver.HardwareAcceleration(flag)
        """
        self.record_method('HardwareAcceleration', flag)

    def set_store_td_results_in_cache(self, flag: bool) -> None:
        """
        VBA Call
        --------
        Solver.StoreTDResultsInCache(flag)
        """
        self.record_method('StoreTDResultsInCache', flag)

    def set_number_of_frequency_samples(self, num_samples: int) -> None:
        """
        VBA Call
        --------
        Solver.FrequencySamples(num_samples)
        """
        self.record_method('FrequencySamples', num_samples)

    def set_number_of_log_frequency_samples(self, num_samples: int) -> None:
        """
        VBA Call
        --------
        Solver.FrequencyLogSamples(num_samples)
        """
        self.record_method('FrequencyLogSamples', num_samples)

    def set_consider_two_port_reciprocity(self, flag: bool) -> None:
        """
        VBA Call
        --------
        Solver.ConsiderTwoPortReciprocity(flag)
        """
        self.record_method('ConsiderTwoPortReciprocity', flag)

    def set_energy_balance_limit(self, limit: float) -> None:
        """
        VBA Call
        --------
        Solver.EnergyBalanceLimit(limit)
        """
        self.record_method('EnergyBalanceLimit', limit)

    def set_time_step_stability_factor(self, factor: float) -> None:
        """
        VBA Call
        --------
        Solver.TimeStepStabilityFactor(factor)
        """
        self.record_method('TimeStepStabilityFactor', factor)

    def set_normalize_to_reference_signal(self, flag: bool) -> None:
        """
        VBA Call
        --------
        Solver.NormalizeToReferenceSignal(flag)
        """
        self.record_method('NormalizeToReferenceSignal', flag)

    def set_normalize_to_default_signal_when_in_use(self, flag: bool) -> None:
        """
        VBA Call
        --------
        Solver.NormalizeToDefaultSignalWhenInUse(flag)
        """
        self.record_method('NormalizeToDefaultSignalWhenInUse', flag)

    def set_detect_identical_ports_automatically(self, flag: bool) -> None:
        """
        VBA Call
        --------
        Solver.AutoDetectIdenticalPorts(flag)
        """
        self.record_method('AutoDetectIdenticalPorts', flag)

    def set_sample_time_signal_automatically(self, flag: bool) -> None:
        """
        VBA Call
        --------
        Solver.AutomaticTimeSignalSampling(flag)
        """
        self.record_method('AutomaticTimeSignalSampling', flag)

    def set_consider_excitation_for_freq_sampling_rate(self, flag: bool) -> None:
        """
        VBA Call
        --------
        Solver.ConsiderExcitationForFreqSamplingRate(flag)
        """
        self.record_method('ConsiderExcitationForFreqSamplingRate', flag)

    def set_perform_tdr_computation(self, flag: bool) -> None:
        """
        VBA Call
        --------
        Solver.TDRComputation(flag)
        """
        self.record_method('TDRComputation', flag)

    def set_shift_tdr_50_percent(self, flag: bool) -> None:
        """
        VBA Call
        --------
        Solver.TDRShift50Percent(flag)
        """
        self.record_method('TDRShift50Percent', flag)

    def set_perform_tdr_reflection_computation(self, flag: bool) -> None:
        """
        VBA Call
        --------
        Solver.TDRReflection(flag)
        """
        self.record_method('TDRReflection', flag)

    def set_use_broadband_phase_shift(self, flag: bool) -> None:
        """
        VBA Call
        --------
        Solver.UseBroadBandPhaseShift(flag)
        """
        self.record_method('UseBroadBandPhaseShift', flag)

    def set_broadband_phase_shift_lower_bound_factor(self, value: float) -> None:
        """
        VBA Call
        --------
        Solver.SetBroadBandPhaseShiftLowerBoundFac(value)
        """
        self.record_method('SetBroadBandPhaseShiftLowerBoundFac', value)

    def set_sparam_adjustment(self, flag: bool) -> None:
        """
        VBA Call
        --------
        Solver.SParaAdjustment(flag)
        """
        self.record_method('SParaAdjustment', flag)

    def set_prepare_farfields(self, flag: bool) -> None:
        """
        VBA Call
        --------
        Solver.PrepareFarfields(flag)
        """
        self.record_method('PrepareFarfields', flag)

    def set_monitor_farfields_near_to_model(self, flag: bool) -> None:
        """
        VBA Call
        --------
        Solver.MonitorFarFieldsNearToModel(flag)
        """
        self.record_method('MonitorFarFieldsNearToModel', flag)

    def set_dump_solver_matrices(self, flag: bool) -> None:
        """
        VBA Call
        --------
        Solver.MatrixDump(flag)
        """
        self.record_method('MatrixDump', flag)

    def set_restart_after_instability_abort(self, flag: bool) -> None:
        """
        VBA Call
        --------
        Solver.RestartAfterInstabilityAbort(flag)
        """
        self.record_method('RestartAfterInstabilityAbort', flag)

    def set_max_number_of_threads(self, num_threads: int) -> None:
        """
        VBA Call
        --------
        Solver.MaximumNumberOfThreads(num_threads)
        """
        self.record_method('MaximumNumberOfThreads', num_threads)

    def set_pml_type(self, pml_type: Union[PmlType, str]) -> None:
        """
        VBA Call
        --------
        Solver.SetPMLType(pml_type)
        """
        self.record_method('SetPMLType', str(getattr(pml_type, 'value', pml_type)))

    def set_update_schema_discrete_items(self, schema: Union[UpdateSchema, str]) -> None:
        """
        VBA Call
        --------
        Solver.DiscreteItemUpdate(schema)
        """
        self.record_method('DiscreteItemUpdate', str(getattr(schema, 'value', schema)))

    def set_update_schema_discrete_items_edge(self, schema: Union[UpdateSchema, str]) -> None:
        """
        VBA Call
        --------
        Solver.DiscreteItemEdgeUpdate(schema)
        """
        self.record_method('DiscreteItemEdgeUpdate', str(getattr(schema, 'value', schema)))

    def set_update_schema_discrete_items_face(self, schema: Union[UpdateSchema, str]) -> None:
        """
        VBA Call
        --------
        Solver.DiscreteItemFaceUpdate(schema)
        """
        self.record_method('DiscreteItemFaceUpdate', str(getattr(schema, 'value', schema)))

    def get_update_schema_discrete_items(self) -> str:
        """
        VBA Call
        --------
        Solver.GetDiscreteItemUpdate()
        """
        return self.query_method_str('GetDiscreteItemUpdate')

    def get_update_schema_discrete_items_edge(self) -> str:
        """
        VBA Call
        --------
        Solver.GetDiscreteItemEdgeUpdate()
        """
        return self.query_method_str('GetDiscreteItemEdgeUpdate')

    def get_update_schema_discrete_items_face(self) -> str:
        """
        VBA Call
        --------
        Solver.GetDiscreteItemFaceUpdate()
        """
        return self.query_method_str('GetDiscreteItemFaceUpdate')

    def suppress_time_signal_storage(self, key: Union[SuppressTss, str]) -> None:
        """
        VBA Call
        --------
        Solver.SuppressTimeSignalStorage(key)
        """
        self.record_method('SuppressTimeSignalStorage', str(getattr(key, 'value', key)))

    def set_calculate_modes_only(self, flag: bool) -> None:
        """
        VBA Call
        --------
        Solver.CalculateModesOnly(flag)
        """
        self.record_method('CalculateModesOnly', flag)

    def set_stimulation_mode(self, mode_number: int) -> None:
        """
        VBA Call
        --------
        Solver.StimulationMode(mode_number)
        """
        self.record_method('StimulationMode', mode_number)

    def set_stimulation_by_all_ports(self) -> None:
        """
        VBA Call
        --------
        Solver.StimulationPort('All')
        """
        self.record_method('StimulationPort', 'All')

    def set_stimulation_by_selected_port(self) -> None:
        """
        VBA Call
        --------
        Solver.StimulationPort('Selected')
        """
        self.record_method('StimulationPort', 'Selected')

    def set_stimulation_by_plane_wave(self) -> None:
        """
        VBA Call
        --------
        Solver.StimulationPort('Plane Wave')
        """
        self.record_method('StimulationPort', 'Plane Wave')

    def set_stimulation_by_port(self, port_number: int) -> None:
        """
        VBA Call
        --------
        Solver.StimulationPort(port_number)
        """
        self.record_method('StimulationPort', port_number)

    def reset_excitation_modes(self) -> None:
        """
        VBA Call
        --------
        Solver.ResetExcitationModes()
        """
        self.record_method('ResetExcitationModes')

    def set_excitation_port_mode(self, port: int, mode: int, amplitude: float, phase: float, signal: str, active: bool) -> None:
        """
        VBA Call
        --------
        Solver.ExcitationPortMode(port, mode, amplitude, phase, signal, active)
        """
        self.record_method('ExcitationPortMode', port, mode, amplitude, phase, signal, active)

    def set_excitation_field_source(self, name: str, amplitude: float, phase: float, signal: str, active: bool) -> None:
        """
        VBA Call
        --------
        Solver.ExcitationFieldSource(name, amplitude, phase, signal, active)
        """
        self.record_method('ExcitationFieldSource', name, amplitude, phase, signal, active)

    def define_excitation(self, excitation: Union[Excitation, str], name: int, mode: int, amplitude: float, phase_or_time: float, signal_name: str, active: bool) -> None:
        """
        VBA Call
        --------
        Solver.DefineExcitation(excitation, name, mode, amplitude, phase_or_time, signal_name, active)
        """
        self.record_method('DefineExcitation', str(getattr(excitation, 'value', excitation)), name, mode, amplitude, phase_or_time, signal_name, active)

    def define_excitation_settings(self, excitation: Union[Excitation, str], name: int, mode: int, amplitude: float, phase_or_time: float, signal_name: str, accuracy: float, f_min: float, f_max: float, active: bool) -> None:
        """
        VBA Call
        --------
        Solver.DefineExcitationSettings(excitation, name, mode, amplitude, phase_or_time, signal_name, accuracy, f_min, f_max, active)
        """
        self.record_method('DefineExcitationSettings', str(getattr(excitation, 'value', excitation)), name, mode, amplitude, phase_or_time, signal_name, accuracy, f_min, f_max, active)

    def set_phase_ref_frequency(self, frequency: float) -> None:
        """
        VBA Call
        --------
        Solver.PhaseRefFrequency(frequency)
        """
        self.record_method('PhaseRefFrequency', frequency)

    def set_s_param_port_excitation(self, flag: bool) -> None:
        """
        VBA Call
        --------
        Solver.SParameterPortExcitation(flag)
        """
        self.record_method('SParameterPortExcitation', flag)

    def set_simultaneous_excitation(self, flag: bool) -> None:
        """
        VBA Call
        --------
        Solver.SimultaneousExcitation(flag)
        """
        self.record_method('SimultaneousExcitation', flag)

    def set_simultaneous_excitation_auto_label(self, flag: bool) -> None:
        """
        VBA Call
        --------
        Solver.SetSimultaneousExcitAutoLabel(flag)
        """
        self.record_method('SetSimultaneousExcitAutoLabel', flag)

    def set_simultaneous_excitation_label(self, label: str) -> None:
        """
        VBA Call
        --------
        Solver.SetSimultaneousExcitationLabel(label)
        """
        self.record_method('SetSimultaneousExcitationLabel', label)

    def set_simultaneous_excitation_offset(self, offset: Union[SimultExcitOffset, str]) -> None:
        """
        VBA Call
        --------
        Solver.SetSimultaneousExcitationOffset(offset)
        """
        self.record_method('SetSimultaneousExcitationOffset', str(getattr(offset, 'value', offset)))

    def set_excitation_selection_show_additional_settings(self, flag: bool) -> None:
        """
        VBA Call
        --------
        Solver.ExcitationSelectionShowAdditionalSettings(flag)
        """
        self.record_method('ExcitationSelectionShowAdditionalSettings', flag)

    def set_superimpose_plw_excitation(self, flag: bool) -> None:
        """
        VBA Call
        --------
        Solver.SuperimposePLWExcitation(flag)
        """
        self.record_method('SuperimposePLWExcitation', flag)

    def set_show_excitation_list_accuracy(self, flag: bool) -> None:
        """
        VBA Call
        --------
        Solver.ShowExcitationListAccuracy(flag)
        """
        self.record_method('ShowExcitationListAccuracy', flag)

    def set_show_excitation_list_monitor_freq_interval(self, flag: bool) -> None:
        """
        VBA Call
        --------
        Solver.ShowExcitationListMonitorFreqInterval(flag)
        """
        self.record_method('ShowExcitationListMonitorFreqInterval', flag)

    def set_use_s_param_symmetries(self, flag: bool) -> None:
        """
        VBA Call
        --------
        Solver.SParaSymmetry(flag)
        """
        self.record_method('SParaSymmetry', flag)

    def reset_s_param_symmetries(self) -> None:
        """
        VBA Call
        --------
        Solver.ResetSParaSymm()
        """
        self.record_method('ResetSParaSymm')

    def define_new_s_param_symmetries(self) -> None:
        """
        VBA Call
        --------
        Solver.DefSParaSymm()
        """
        self.record_method('DefSParaSymm')

    def add_s_param(self, port_num1: int, port_num2: int) -> None:
        """
        VBA Call
        --------
        Solver.SPara(port_num1, port_num2)
        """
        self.record_method('SPara', port_num1, port_num2)

    def set_waveguide_port_generalized(self, flag: bool) -> None:
        """
        VBA Call
        --------
        Solver.WaveguidePortGeneralized(flag)
        """
        self.record_method('WaveguidePortGeneralized', flag)

    def set_waveguide_port_mode_tracking(self, flag: bool) -> None:
        """
        VBA Call
        --------
        Solver.WaveguidePortModeTracking(flag)
        """
        self.record_method('WaveguidePortModeTracking', flag)

    def set_absorb_unconsidered_mode_fields(self, key: Union[Absorb, str]) -> None:
        """
        VBA Call
        --------
        Solver.AbsorbUnconsideredModeFields(key)
        """
        self.record_method('AbsorbUnconsideredModeFields', str(getattr(key, 'value', key)))

    def set_full_deembedding(self, flag: bool) -> None:
        """
        VBA Call
        --------
        Solver.FullDeembedding(flag)
        """
        self.record_method('FullDeembedding', flag)

    def set_number_of_samples_full_deembedding(self, number: int) -> None:
        """
        VBA Call
        --------
        Solver.SetSamplesFullDeembedding(number)
        """
        self.record_method('SetSamplesFullDeembedding', number)

    def set_consider_dispersive_behavior_full_deembedding(self, flag: bool) -> None:
        """
        VBA Call
        --------
        Solver.DispEpsFullDeembedding(flag)
        """
        self.record_method('DispEpsFullDeembedding', flag)

    def set_waveguide_port_broadband(self, flag: bool) -> None:
        """
        VBA Call
        --------
        Solver.WaveguidePortBroadband(flag)
        """
        self.record_method('WaveguidePortBroadband', flag)

    def set_mode_freq_factor(self, factor: float) -> None:
        """
        VBA Call
        --------
        Solver.SetModeFreqFactor(factor)
        """
        self.record_method('SetModeFreqFactor', factor)

    def set_scale_te_tm_mode_to_center_frequency(self, flag: bool) -> None:
        """
        VBA Call
        --------
        Solver.ScaleTETMModeToCenterFrequency(flag)
        """
        self.record_method('ScaleTETMModeToCenterFrequency', flag)

    def set_waveguide_port_excitation_type(self, excitation_type: Union[ExcitationType, str]) -> None:
        """
        VBA Call
        --------
        Solver.WaveguidePortExcitationType(excitation_type)
        """
        self.record_method('WaveguidePortExcitationType', str(getattr(excitation_type, 'value', excitation_type)))

    def set_waveguide_port_decomposition_type(self, decomposition_type: Union[DecompositionType, str]) -> None:
        """
        VBA Call
        --------
        Solver.WaveguidePortDecompositionType(decomposition_type)
        """
        self.record_method('WaveguidePortDecompositionType', str(getattr(decomposition_type, 'value', decomposition_type)))

    def set_voltage_waveguide_port(self, port_name: int, value: float) -> None:
        """
        VBA Call
        --------
        Solver.SetVoltageWaveguidePort(port_name, value, True)
        """
        self.record_method('SetVoltageWaveguidePort', port_name, value, True)

    def unset_voltage_waveguide_port(self, port_name: int) -> None:
        """
        VBA Call
        --------
        Solver.SetVoltageWaveguidePort(port_name, 0.0, False)
        """
        self.record_method('SetVoltageWaveguidePort', port_name, 0.0, False)

    def set_adaptive_port_meshing(self, flag: bool) -> None:
        """
        VBA Call
        --------
        Solver.AdaptivePortMeshing(flag)
        """
        self.record_method('AdaptivePortMeshing', flag)

    def set_adaptive_port_meshing_accuracy(self, accuracy_percent: int) -> None:
        """
        VBA Call
        --------
        Solver.AccuracyAdaptivePortMeshing(accuracy_percent)
        """
        self.record_method('AccuracyAdaptivePortMeshing', accuracy_percent)

    def set_adaptive_port_meshing_number_of_passes(self, number: int) -> None:
        """
        VBA Call
        --------
        Solver.PassesAdaptivePortMeshing(number)
        """
        self.record_method('PassesAdaptivePortMeshing', number)

    def set_number_of_pulse_widths(self, number: int) -> None:
        """
        VBA Call
        --------
        Solver.NumberOfPulseWidths(number)
        """
        self.record_method('NumberOfPulseWidths', number)

    def enable_steady_state_monitor(self, accuracy_dB: float) -> None:
        """
        VBA Call
        --------
        Solver.SteadyStateLimit(accuracy_dB)
        """
        self.record_method('SteadyStateLimit', accuracy_dB)

    def disable_steady_state_monitor(self) -> None:
        """
        VBA Call
        --------
        Solver.SteadyStateLimit('No Check')
        """
        self.record_method('SteadyStateLimit', 'No Check')

    def add_stop_criterion(self, group_name: str, threshold: float, num_checks: int, active: bool) -> None:
        """
        VBA Call
        --------
        Solver.AddStopCriterion(group_name, threshold, num_checks, active)
        """
        self.record_method('AddStopCriterion', group_name, threshold, num_checks, active)

    def add_stop_criterion_with_target_frequency(self, group_name: str, threshold: float, num_checks: int, target_frequency_ranges: FrequencyRangeList, active: bool) -> None:
        """
        VBA Call
        --------
        Solver.AddStopCriterionWithTargetFrequency(group_name, threshold, num_checks, active, str(target_frequency_ranges))
        """
        self.record_method('AddStopCriterionWithTargetFrequency', group_name, threshold, num_checks, active, str(target_frequency_ranges))

    def set_stop_criteria_show_excitation(self, flag: bool) -> None:
        """
        VBA Call
        --------
        Solver.StopCriteriaShowExcitation(flag)
        """
        self.record_method('StopCriteriaShowExcitation', flag)

    def set_use_ar_filter(self, flag: bool) -> None:
        """
        VBA Call
        --------
        Solver.UseArfilter(flag)
        """
        self.record_method('UseArfilter', flag)

    def set_ar_max_energy_deviation(self, limit: float) -> None:
        """
        VBA Call
        --------
        Solver.ArMaxEnergyDeviation(limit)
        """
        self.record_method('ArMaxEnergyDeviation', limit)

    def set_ar_number_of_pulses_to_skip(self, number: int) -> None:
        """
        VBA Call
        --------
        Solver.ArPulseSkip(number)
        """
        self.record_method('ArPulseSkip', number)

    def start_ar_filter(self) -> None:
        """
        VBA Call
        --------
        Solver.StartArFilter()
        """
        self.record_method('StartArFilter')

    def set_time_window(self, window: Union[Window, str], smoothness_percent: int, enabled_on_transient_sim: bool) -> None:
        """
        VBA Call
        --------
        Solver.SetTimeWindow(window, smoothness_percent, enabled_on_transient_sim)
        """
        self.record_method('SetTimeWindow', str(getattr(window, 'value', window)), smoothness_percent, enabled_on_transient_sim)

    def set_surface_impedance_order(self, order: int) -> None:
        """
        VBA Call
        --------
        Solver.SurfaceImpedanceOrder(order)
        """
        self.record_method('SurfaceImpedanceOrder', order)

    def set_activate_power_loss_1d_monitor(self, flag: bool) -> None:
        """
        VBA Call
        --------
        Solver.ActivatePowerLoss1DMonitor(flag)
        """
        self.record_method('ActivatePowerLoss1DMonitor', flag)

    def set_power_loss_1d_monitor_per_solid(self, flag: bool) -> None:
        """
        VBA Call
        --------
        Solver.PowerLoss1DMonitorPerSolid(flag)
        """
        self.record_method('PowerLoss1DMonitorPerSolid', flag)

    def set_use_3d_field_monitor_for_power_loss_1d_monitor(self, flag: bool) -> None:
        """
        VBA Call
        --------
        Solver.Use3DFieldMonitorForPowerLoss1DMonitor(flag)
        """
        self.record_method('Use3DFieldMonitorForPowerLoss1DMonitor', flag)

    def set_use_farfield_monitor_for_power_loss_1d_monitor(self, flag: bool) -> None:
        """
        VBA Call
        --------
        Solver.UseFarFieldMonitorForPowerLoss1DMonitor(flag)
        """
        self.record_method('UseFarFieldMonitorForPowerLoss1DMonitor', flag)

    def set_use_extra_freq_for_power_loss_1d_monitor(self, flag: bool) -> None:
        """
        VBA Call
        --------
        Solver.UseExtraFreqForPowerLoss1DMonitor(flag)
        """
        self.record_method('UseExtraFreqForPowerLoss1DMonitor', flag)

    def reset_power_loss_1d_monitor_extra_freqs(self) -> None:
        """
        VBA Call
        --------
        Solver.ResetPowerLoss1DMonitorExtraFreq()
        """
        self.record_method('ResetPowerLoss1DMonitorExtraFreq')

    def add_power_loss_1d_monitor_extra_freq(self, freq: float) -> None:
        """
        VBA Call
        --------
        Solver.AddPowerLoss1DMonitorExtraFreq(freq)
        """
        self.record_method('AddPowerLoss1DMonitorExtraFreq', freq)

    def set_time_power_loss_si_material_monitor(self, flag: bool) -> None:
        """
        VBA Call
        --------
        Solver.SetTimePowerLossSIMaterialMonitor(flag)
        """
        self.record_method('SetTimePowerLossSIMaterialMonitor', flag)

    def activate_timer_power_loss_si_material_monitor(self, t_start: float, t_step: float) -> None:
        """
        VBA Call
        --------
        Solver.ActivateTimePowerLossSIMaterialMonitor(t_start, t_step, 0.0, False)
        """
        self.record_method('ActivateTimePowerLossSIMaterialMonitor', t_start, t_step, 0.0, False)

    def activate_timer_power_loss_si_material_monitor_lim(self, t_start: float, t_step: float, t_end: float) -> None:
        """
        VBA Call
        --------
        Solver.ActivateTimePowerLossSIMaterialMonitor(t_start, t_step, t_end, True)
        """
        self.record_method('ActivateTimePowerLossSIMaterialMonitor', t_start, t_step, t_end, True)

    def set_time_power_loss_si_material_monitor_average(self, flag: bool) -> None:
        """
        VBA Call
        --------
        Solver.SetTimePowerLossSIMaterialMonitorAverage(flag)
        """
        self.record_method('SetTimePowerLossSIMaterialMonitorAverage', flag)

    def set_time_power_loss_si_material_monitor_average_rep_period(self, period: float) -> None:
        """
        VBA Call
        --------
        Solver.SetTimePowerLossSIMaterialMonitorAverageRepPeriod(period)
        """
        self.record_method('SetTimePowerLossSIMaterialMonitorAverageRepPeriod', period)

    def set_time_power_loss_si_material_monitor_per_solid(self, flag: bool) -> None:
        """
        VBA Call
        --------
        Solver.TimePowerLossSIMaterialMonitorPerSolid(flag)
        """
        self.record_method('TimePowerLossSIMaterialMonitorPerSolid', flag)

    def set_disp_non_linear_material_monitor(self, flag: bool) -> None:
        """
        VBA Call
        --------
        Solver.SetDispNonLinearMaterialMonitor(flag)
        """
        self.record_method('SetDispNonLinearMaterialMonitor', flag)

    def activate_disp_non_linear_material_monitor(self, t_start: float, t_step: float) -> None:
        """
        VBA Call
        --------
        Solver.ActivateDispNonLinearMaterialMonitor(t_start, t_step, 0.0, False)
        """
        self.record_method('ActivateDispNonLinearMaterialMonitor', t_start, t_step, 0.0, False)

    def activate_disp_non_linear_material_monitor_lim(self, t_start: float, t_step: float, t_end: float) -> None:
        """
        VBA Call
        --------
        Solver.ActivateDispNonLinearMaterialMonitor(t_start, t_step, t_end, True)
        """
        self.record_method('ActivateDispNonLinearMaterialMonitor', t_start, t_step, t_end, True)

    def set_activate_space_material_3d_monitor(self, flag: bool) -> None:
        """
        VBA Call
        --------
        Solver.ActivateSpaceMaterial3DMonitor(flag)
        """
        self.record_method('ActivateSpaceMaterial3DMonitor', flag)

    def set_use_3d_field_monitor_for_space_material_3d_monitor(self, flag: bool) -> None:
        """
        VBA Call
        --------
        Solver.Use3DFieldMonitorForSpaceMaterial3DMonitor(flag)
        """
        self.record_method('Use3DFieldMonitorForSpaceMaterial3DMonitor', flag)

    def set_use_extra_freq_for_space_material_3d_monitor(self, flag: bool) -> None:
        """
        VBA Call
        --------
        Solver.UseExtraFreqForSpaceMaterial3DMonitor(flag)
        """
        self.record_method('UseExtraFreqForSpaceMaterial3DMonitor', flag)

    def reset_space_material_3d_monitor_extra_freqs(self) -> None:
        """
        VBA Call
        --------
        Solver.ResetSpaceMaterial3DMonitorExtraFreq()
        """
        self.record_method('ResetSpaceMaterial3DMonitorExtraFreq')

    def add_space_material_3d_monitor_extra_freq(self, freq: float) -> None:
        """
        VBA Call
        --------
        Solver.AddSpaceMaterial3DMonitorExtraFreq(freq)
        """
        self.record_method('AddSpaceMaterial3DMonitorExtraFreq', freq)

    def set_hftd_disp_update_scheme(self, scheme: Union[HftdDispUpdateScheme, str]) -> None:
        """
        VBA Call
        --------
        Solver.SetHFTDDispUpdateScheme(scheme)
        """
        self.record_method('SetHFTDDispUpdateScheme', str(getattr(scheme, 'value', scheme)))

    def set_use_tst_at_port(self, flag: bool) -> None:
        """
        VBA Call
        --------
        Solver.UseTSTAtPort(flag)
        """
        self.record_method('UseTSTAtPort', flag)

    def set_sybcycle_state(self, state: Union[SubcycleState, str]) -> None:
        """
        VBA Call
        --------
        Solver.SetSubcycleState(state)
        """
        self.record_method('SetSubcycleState', str(getattr(state, 'value', state)))

    def set_simplified_pba_method(self, flag: bool) -> None:
        """
        VBA Call
        --------
        Solver.SimplifiedPBAMethod(flag)
        """
        self.record_method('SimplifiedPBAMethod', flag)

    def set_aks_penalty_factor(self, factor: float) -> None:
        """
        VBA Call
        --------
        Solver.AKSPenaltyFactor(factor)
        """
        self.record_method('AKSPenaltyFactor', factor)

    def set_aks_estimation(self, factor: float) -> None:
        """
        VBA Call
        --------
        Solver.AKSEstimation(factor)
        """
        self.record_method('AKSEstimation', factor)

    def set_aks_number_of_iterations(self, number: int) -> None:
        """
        VBA Call
        --------
        Solver.AKSIterations(number)
        """
        self.record_method('AKSIterations', number)

    def set_aks_accuracy(self, accuracy: float) -> None:
        """
        VBA Call
        --------
        Solver.AKSAccuracy(accuracy)
        """
        self.record_method('AKSAccuracy', accuracy)

    def reset_aks(self) -> None:
        """
        VBA Call
        --------
        Solver.AKSReset()
        """
        self.record_method('AKSReset')

    def start_aks(self) -> None:
        """
        VBA Call
        --------
        Solver.AKSStart()
        """
        self.record_method('AKSStart')

    def set_aks_number_of_estimation_cycles(self, number: int) -> None:
        """
        VBA Call
        --------
        Solver.AKSEstimationCycles(number)
        """
        self.record_method('AKSEstimationCycles', number)

    def set_aks_automatic_estimation(self, flag: bool) -> None:
        """
        VBA Call
        --------
        Solver.AKSAutomaticEstimation(flag)
        """
        self.record_method('AKSAutomaticEstimation', flag)

    def set_aks_number_of_check_modes(self, number: int) -> None:
        """
        VBA Call
        --------
        Solver.AKSCheckModes(number)
        """
        self.record_method('AKSCheckModes', number)

    def set_aks_maximum_df(self, delta_frequency: float) -> None:
        """
        VBA Call
        --------
        Solver.AKSMaximumDF(delta_frequency)
        """
        self.record_method('AKSMaximumDF', delta_frequency)

    def set_aks_max_number_of_passes(self, number: int) -> None:
        """
        VBA Call
        --------
        Solver.AKSMaximumPasses(number)
        """
        self.record_method('AKSMaximumPasses', number)

    def set_aks_mesh_increment(self, inc: int) -> None:
        """
        VBA Call
        --------
        Solver.AKSMeshIncrement(inc)
        """
        self.record_method('AKSMeshIncrement', inc)

    def set_aks_min_number_of_passes(self, number: int) -> None:
        """
        VBA Call
        --------
        Solver.AKSMinimumPasses(number)
        """
        self.record_method('AKSMinimumPasses', number)

    def get_aks_number_of_modes(self) -> int:
        """
        VBA Call
        --------
        Solver.AKSGetNumberOfModes()
        """
        return self.query_method_int('AKSGetNumberOfModes')

