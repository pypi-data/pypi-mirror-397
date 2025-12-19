'''This file is auto-generated. Do not edit.'''
from .. import IVBAProvider, VBATypeName, VBAObjWrapper
from enum import Enum
from typing import Union, Tuple

class FDSolver(VBAObjWrapper):
    class ObcTypeHex(Enum):
        DEFAULT = 'Default'
        PML = 'PML'
        FREESPACE_SIBC = 'FreespaceSIBC'

    class ObcTypeTet(Enum):
        DEFAULT = 'Default'
        PML = 'PML'
        SIBC = 'SIBC'

    class ResetSampleIntervals(Enum):
        ALL = 'all'
        ADAPTATION = 'adaptation'
        SINGLE = 'single'
        INACTIVE = 'inactive'
        INFINITE = 'infinite'

    class SampleInterval(Enum):
        AUTOMATIC = 'Automatic'
        SINGLE = 'Single'
        EQUIDISTANT = 'Equidistant'
        LOGARITHMIC = 'Logarithmic'

    class InactiveSampleInterval(Enum):
        AUTOMATIC = 'Automatic'
        EQUIDISTANT = 'Equidistant'

    class FreqDistAdaptMode(Enum):
        LOCAL = 'Local'
        AS_A_WHOLE = 'As_A_Whole'
        DISTRIBUTED = 'Distributed'

    class SweepThresholdType(Enum):
        S_PARAMETERS = 'S-Parameters'
        PROBES = 'Probes'

    class Type(Enum):
        AUTO = 'Auto'
        ITERATIVE = 'Iterative'
        DIRECT = 'Direct'

    class MeshMethod(Enum):
        HEXAHEDRAL = 'Hexahedral'
        TETRAHEDRAL = 'Tetrahedral'
        SURFACE = 'Surface'

    class SweepMethod(Enum):
        GENERAL_PURPOSE = 'General purpose'
        FAST_REDUCED_ORDER_MODEL = 'Fast reduced order model'
        DISCRETE_SAMPLES_ONLY = 'Discrete samples only'

    class StimulationMode(Enum):
        ALL = 'All'
        ALL_FLOQUET = 'All+Floquet'
        PLANE_WAVE = 'Plane Wave'
        LIST = 'List'
        CMA = 'CMA'

    class ResultDataSamplingMode(Enum):
        AUTOMATIC = 'Automatic'
        FREQUENCY_LINEAR = 'Frequency (linear)'
        FREQUENCY_LOGARITHMIC = 'Frequency (logarithmic)'
        FREQUENCY_LOG_LINEAR = 'Frequency (log-linear)'

    class ExcitationPort(Enum):
        Z_MIN = 'zmin'
        Z_MAX = 'zmax'

    class ExcitationMode(Enum):
        _1 = '1'
        _1_3_4 = '1;3;4'
        TE_0_0 = 'TE(0,0)'
        TM_0_0 = 'TM(0,0)'
        LCP = 'LCP'
        RCP = 'RCP'

    class OrderTet(Enum):
        FIRST = 'First'
        SECOND = 'Second'
        THIRD = 'Third'

    class OrderSrf(Enum):
        FIRST = 'First'
        SECOND = 'Second'
        THIRD = 'Third'

    class NetworkComputingStrategy(Enum):
        RUN_REMOTE = 'RunRemote'
        SAMPLES = 'Samples'

    class MlfmmAccuracy(Enum):
        VERY_LOW_MEM = 'VeryLowMem'
        LOW_MEM = 'LowMem'
        DEFAULT = 'Default'
        HIGH_ACC = 'HighAcc'

    class RecordUnitCellScanFarfield(Enum):
        ON = 'on'
        OFF = 'off'
        AUTO = 'auto'

    def __init__(self, vbap: IVBAProvider) -> None:
        super().__init__(vbap, 'FDSolver')
        self.set_save_history(False)

    def reset(self) -> None:
        """
        VBA Call
        --------
        FDSolver.Reset()
        """
        self.record_method('Reset')

    def start(self) -> None:
        """
        VBA Call
        --------
        FDSolver.start()
        """
        self.record_method('start')

    def set_accelerated_restart(self, flag: bool) -> None:
        """
        VBA Call
        --------
        FDSolver.AcceleratedRestart(flag)
        """
        self.record_method('AcceleratedRestart', flag)

    def set_accuracy_tet(self, value: float) -> None:
        """
        VBA Call
        --------
        FDSolver.AccuracyTet(value)
        """
        self.record_method('AccuracyTet', value)

    def set_accuracy_srf(self, value: float) -> None:
        """
        VBA Call
        --------
        FDSolver.AccuracySrf(value)
        """
        self.record_method('AccuracySrf', value)

    def set_accuracy_hex(self, value: float) -> None:
        """
        VBA Call
        --------
        FDSolver.AccuracyHex(value)
        """
        self.record_method('AccuracyHex', value)

    def set_accuracy_rom(self, value: float) -> None:
        """
        VBA Call
        --------
        FDSolver.AccuracyROM(value)
        """
        self.record_method('AccuracyROM', value)

    def set_store_all_results(self, flag: bool) -> None:
        """
        VBA Call
        --------
        FDSolver.StoreAllResults(flag)
        """
        self.record_method('StoreAllResults', flag)

    def set_store_solution_coefficients(self, flag: bool) -> None:
        """
        VBA Call
        --------
        FDSolver.StoreSolutionCoefficients(flag)
        """
        self.record_method('StoreSolutionCoefficients', flag)

    def set_create_legacy_1d_signals(self, flag: bool) -> None:
        """
        VBA Call
        --------
        FDSolver.CreateLegacy1DSignals(flag)
        """
        self.record_method('CreateLegacy1DSignals', flag)

    def set_obc_type_hex(self, obc_type: Union[ObcTypeHex, str]) -> None:
        """
        VBA Call
        --------
        FDSolver.SetOpenBCTypeHex(obc_type)
        """
        self.record_method('SetOpenBCTypeHex', str(getattr(obc_type, 'value', obc_type)))

    def set_obc_type_tet(self, obc_type: Union[ObcTypeTet, str]) -> None:
        """
        VBA Call
        --------
        FDSolver.SetOpenBCTypeTet(obc_type)
        """
        self.record_method('SetOpenBCTypeTet', str(getattr(obc_type, 'value', obc_type)))

    def set_add_monitor_samples(self, flag: bool) -> None:
        """
        VBA Call
        --------
        FDSolver.AddMonitorSamples(flag)
        """
        self.record_method('AddMonitorSamples', flag)

    def set_max_number_of_frequency_samples(self, number: int) -> None:
        """
        VBA Call
        --------
        FDSolver.FrequencySamples(number)
        """
        self.record_method('FrequencySamples', number)

    def set_mesh_adaptation_hex(self, flag: bool) -> None:
        """
        VBA Call
        --------
        FDSolver.MeshAdaptionHex(flag)
        """
        self.record_method('MeshAdaptionHex', flag)

    def set_mesh_adaption_tet(self, flag: bool) -> None:
        """
        VBA Call
        --------
        FDSolver.MeshAdaptionTet(flag)
        """
        self.record_method('MeshAdaptionTet', flag)

    def reset_sample_intervals(self, key: Union[ResetSampleIntervals, str]) -> None:
        """
        VBA Call
        --------
        FDSolver.ResetSampleIntervals(key)
        """
        self.record_method('ResetSampleIntervals', str(getattr(key, 'value', key)))

    def set_use_helmholtz_equation(self, flag: bool) -> None:
        """
        VBA Call
        --------
        FDSolver.UseHelmholtzEquation(flag)
        """
        self.record_method('UseHelmholtzEquation', flag)

    def add_sample_interval(self, min: float, max: float, num_samples: int, key: Union[SampleInterval, str], adaptation: bool = False) -> None:
        """
        VBA Call
        --------
        FDSolver.AddSampleInterval(min, max, num_samples, key, adaptation)
        """
        self.record_method('AddSampleInterval', min, max, num_samples, str(getattr(key, 'value', key)), adaptation)

    def add_inactive_sample_interval(self, min: float, max: float, num_samples: int, key: Union[InactiveSampleInterval, str], adaptation: bool = False) -> None:
        """
        VBA Call
        --------
        FDSolver.AddInactiveSampleInterval(min, max, num_samples, key, adaptation)
        """
        self.record_method('AddInactiveSampleInterval', min, max, num_samples, str(getattr(key, 'value', key)), adaptation)

    def set_max_number_of_iterations(self, count: int) -> None:
        """
        VBA Call
        --------
        FDSolver.MaxIterations(count)
        """
        self.record_method('MaxIterations', count)

    def set_limit_iterations(self, flag: bool) -> None:
        """
        VBA Call
        --------
        FDSolver.LimitIterations(flag)
        """
        self.record_method('LimitIterations', flag)

    def set_modes_only(self, flag: bool) -> None:
        """
        VBA Call
        --------
        FDSolver.ModesOnly(flag)
        """
        self.record_method('ModesOnly', flag)

    def set_shield_all_ports(self, flag: bool) -> None:
        """
        VBA Call
        --------
        FDSolver.SetShieldAllPorts(flag)
        """
        self.record_method('SetShieldAllPorts', flag)

    def set_port_mesh_matches_3d_mesh_tet(self, flag: bool) -> None:
        """
        VBA Call
        --------
        FDSolver.SetPortMeshMatches3DMeshTet(flag)
        """
        self.record_method('SetPortMeshMatches3DMeshTet', flag)

    def set_allow_rom_port_mode_solver(self, flag: bool) -> None:
        """
        VBA Call
        --------
        FDSolver.SetAllowROMPortModeSolver(flag)
        """
        self.record_method('SetAllowROMPortModeSolver', flag)

    def set_allow_discrete_port_solver(self, flag: bool) -> None:
        """
        VBA Call
        --------
        FDSolver.SetAllowDiscretePortSolver(flag)
        """
        self.record_method('SetAllowDiscretePortSolver', flag)

    def set_use_rom_port_mode_solver_tet(self, general_purpose: bool, fast_reduced_order_model: bool) -> None:
        """
        VBA Call
        --------
        FDSolver.SetUseROMPortModeSolverTet(general_purpose, fast_reduced_order_model)
        """
        self.record_method('SetUseROMPortModeSolverTet', general_purpose, fast_reduced_order_model)

    def set_enable_native_single_ended(self, flag: bool) -> None:
        """
        VBA Call
        --------
        FDSolver.EnableNativeSingleEnded(flag)
        """
        self.record_method('EnableNativeSingleEnded', flag)

    def set_use_deembedded_fields(self, flag: bool) -> None:
        """
        VBA Call
        --------
        FDSolver.UseDeembeddedFields(flag)
        """
        self.record_method('UseDeembeddedFields', flag)

    def set_freq_dist_adapt_mode(self, mode: Union[FreqDistAdaptMode, str]) -> None:
        """
        VBA Call
        --------
        FDSolver.FreqDistAdaptMode(mode)
        """
        self.record_method('FreqDistAdaptMode', str(getattr(mode, 'value', mode)))

    def set_prefer_lean_output(self, flag: bool) -> None:
        """
        VBA Call
        --------
        FDSolver.SetPreferLeanOutput(flag)
        """
        self.record_method('SetPreferLeanOutput', flag)

    def set_use_imp_line_impedance_as_reference(self, flag: bool) -> None:
        """
        VBA Call
        --------
        FDSolver.SetUseImpLineImpedanceAsReference(flag)
        """
        self.record_method('SetUseImpLineImpedanceAsReference', flag)

    def set_use_orient_port_with_mask(self, flag: bool) -> None:
        """
        VBA Call
        --------
        FDSolver.SetUseOrientPortWithMask(flag)
        """
        self.record_method('SetUseOrientPortWithMask', flag)

    def set_consider_port_losses_tet(self, flag: bool) -> None:
        """
        VBA Call
        --------
        FDSolver.ConsiderPortLossesTet(flag)
        """
        self.record_method('ConsiderPortLossesTet', flag)

    def set_stop_sweep_if_criterion_met(self, flag: bool) -> None:
        """
        VBA Call
        --------
        FDSolver.SetStopSweepIfCriterionMet(flag)
        """
        self.record_method('SetStopSweepIfCriterionMet', flag)

    def set_sweep_threshold(self, type: Union[SweepThresholdType, str], threshold: float) -> None:
        """
        VBA Call
        --------
        FDSolver.SetSweepThreshold(type, threshold)
        """
        self.record_method('SetSweepThreshold', str(getattr(type, 'value', type)), threshold)

    def set_use_sweep_threshold(self, type: Union[SweepThresholdType, str], flag: bool) -> None:
        """
        VBA Call
        --------
        FDSolver.UseSweepThreshold(type, flag)
        """
        self.record_method('UseSweepThreshold', str(getattr(type, 'value', type)), flag)

    def set_type(self, solver_type: Union[Type, str]) -> None:
        """
        VBA Call
        --------
        FDSolver.Type(solver_type)
        """
        self.record_method('Type', str(getattr(solver_type, 'value', solver_type)))

    def set_store_results_in_cache(self, flag: bool) -> None:
        """
        VBA Call
        --------
        FDSolver.StoreResultsInCache(flag)
        """
        self.record_method('StoreResultsInCache', flag)

    def set_method(self, mesh_method: Union[MeshMethod, str], sweep_method: Union[SweepMethod, str]) -> None:
        """
        VBA Call
        --------
        FDSolver.SetMethod(mesh_method, sweep_method)
        """
        self.record_method('SetMethod', str(getattr(mesh_method, 'value', mesh_method)), str(getattr(sweep_method, 'value', sweep_method)))

    def set_auto_norm_impedance(self, flag: bool) -> None:
        """
        VBA Call
        --------
        FDSolver.AutoNormImpedance(flag)
        """
        self.record_method('AutoNormImpedance', flag)

    def set_norming_impedance(self, impedance: float) -> None:
        """
        VBA Call
        --------
        FDSolver.NormingImpedance(impedance)
        """
        self.record_method('NormingImpedance', impedance)

    def set_stimulation(self, port: str, mode: Union[StimulationMode, str]) -> None:
        """
        VBA Call
        --------
        FDSolver.Stimulation(port, mode)
        """
        self.record_method('Stimulation', port, str(getattr(mode, 'value', mode)))

    def set_number_of_sweep_error_checks(self, number: int) -> None:
        """
        VBA Call
        --------
        FDSolver.SweepErrorChecks(number)
        """
        self.record_method('SweepErrorChecks', number)

    def set_minimum_number_of_sweep_samples(self, number: int) -> None:
        """
        VBA Call
        --------
        FDSolver.SweepMinimumSamples(number)
        """
        self.record_method('SweepMinimumSamples', number)

    def set_sweep_consider_all(self, flag: bool) -> None:
        """
        VBA Call
        --------
        FDSolver.SweepConsiderAll(flag)
        """
        self.record_method('SweepConsiderAll', flag)

    def reset_sweep_consider_list(self) -> None:
        """
        VBA Call
        --------
        FDSolver.SweepConsiderReset()
        """
        self.record_method('SweepConsiderReset')

    def consider_sweep_s_param(self, port_out: int, mode_out: int, mode_in: int) -> None:
        """
        VBA Call
        --------
        FDSolver.SweepConsiderSPar(port_out, mode_out, mode_in)
        """
        self.record_method('SweepConsiderSPar', port_out, mode_out, mode_in)

    def set_minimum_number_of_result_data_samples(self, number: int) -> None:
        """
        VBA Call
        --------
        FDSolver.SetNumberOfResultDataSamples(number)
        """
        self.record_method('SetNumberOfResultDataSamples', number)

    def set_result_data_sampling_mode(self, mode: Union[ResultDataSamplingMode, str]) -> None:
        """
        VBA Call
        --------
        FDSolver.SetResultDataSamplingMode(mode)
        """
        self.record_method('SetResultDataSamplingMode', str(getattr(mode, 'value', mode)))

    def set_extrude_open_boundary_condition(self, flag: bool) -> None:
        """
        VBA Call
        --------
        FDSolver.ExtrudeOpenBC(flag)
        """
        self.record_method('ExtrudeOpenBC', flag)

    def set_td_compatible_materials(self, flag: bool) -> None:
        """
        VBA Call
        --------
        FDSolver.TDCompatibleMaterials(flag)
        """
        self.record_method('TDCompatibleMaterials', flag)

    def set_calculate_static_b_field(self, flag: bool) -> None:
        """
        VBA Call
        --------
        FDSolver.CalcStatBField(flag)
        """
        self.record_method('CalcStatBField', flag)

    def set_calculate_power_loss(self, flag: bool) -> None:
        """
        VBA Call
        --------
        FDSolver.CalcPowerLoss(flag)
        """
        self.record_method('CalcPowerLoss', flag)

    def set_calculate_power_loss_per_component(self, flag: bool) -> None:
        """
        VBA Call
        --------
        FDSolver.CalcPowerLossPerComponent(flag)
        """
        self.record_method('CalcPowerLossPerComponent', flag)

    def set_use_green_sandy_ferrite_model(self, flag: bool) -> None:
        """
        VBA Call
        --------
        FDSolver.SetUseGreenSandyFerriteModel(flag)
        """
        self.record_method('SetUseGreenSandyFerriteModel', flag)

    def set_green_sandy_threshold_h_field(self, threshold: float) -> None:
        """
        VBA Call
        --------
        FDSolver.SetGreenSandyThresholdH(threshold)
        """
        self.record_method('SetGreenSandyThresholdH', threshold)

    def reset_excitation_list(self) -> None:
        """
        VBA Call
        --------
        FDSolver.ResetExcitationList()
        """
        self.record_method('ResetExcitationList')

    def add_item_to_excitation_list(self, port: Union[ExcitationPort, str], mode: Union[ExcitationMode, str]) -> None:
        """
        VBA Call
        --------
        FDSolver.AddToExcitationList(port, mode)
        """
        self.record_method('AddToExcitationList', str(getattr(port, 'value', port)), str(getattr(mode, 'value', mode)))

    def set_use_parallelization(self, flag: bool) -> None:
        """
        VBA Call
        --------
        FDSolver.UseParallelization(flag)
        """
        self.record_method('UseParallelization', flag)

    def set_max_number_of_cpu_threads(self, number: int) -> None:
        """
        VBA Call
        --------
        FDSolver.MaxCPUs(number)
        """
        self.record_method('MaxCPUs', number)

    def set_max_number_of_cpu_devices(self, number: int) -> None:
        """
        VBA Call
        --------
        FDSolver.MaximumNumberOfCPUDevices(number)
        """
        self.record_method('MaximumNumberOfCPUDevices', number)

    def set_sweep_weight_evanescent(self, weight: float) -> None:
        """
        VBA Call
        --------
        FDSolver.SweepWeightEvanescent(weight)
        """
        self.record_method('SweepWeightEvanescent', weight)

    def set_low_frequency_stabilization(self, flag: bool) -> None:
        """
        VBA Call
        --------
        FDSolver.LowFrequencyStabilization(flag)
        """
        self.record_method('LowFrequencyStabilization', flag)

    def set_order_tet(self, order: Union[OrderTet, str]) -> None:
        """
        VBA Call
        --------
        FDSolver.OrderTet(order)
        """
        self.record_method('OrderTet', str(getattr(order, 'value', order)))

    def set_mixed_order_tet(self, flag: bool) -> None:
        """
        VBA Call
        --------
        FDSolver.MixedOrderTet(flag)
        """
        self.record_method('MixedOrderTet', flag)

    def set_order_srf(self, order: Union[OrderSrf, str]) -> None:
        """
        VBA Call
        --------
        FDSolver.OrderSrf(order)
        """
        self.record_method('OrderSrf', str(getattr(order, 'value', order)))

    def set_mixed_order_srf(self, flag: bool) -> None:
        """
        VBA Call
        --------
        FDSolver.MixedOrderSrf(flag)
        """
        self.record_method('MixedOrderSrf', flag)

    def set_use_distributed_computing(self, flag: bool) -> None:
        """
        VBA Call
        --------
        FDSolver.UseDistributedComputing(flag)
        """
        self.record_method('UseDistributedComputing', flag)

    def set_network_computing_strategy(self, strategy: str) -> None:
        """
        VBA Call
        --------
        FDSolver.NetworkComputingStrategy(strategy)
        """
        self.record_method('NetworkComputingStrategy', strategy)

    def set_network_computing_job_count(self, count: int) -> None:
        """
        VBA Call
        --------
        FDSolver.NetworkComputingJobCount(count)
        """
        self.record_method('NetworkComputingJobCount', count)

    def set_use_sensitivity_analysis(self, flag: bool) -> None:
        """
        VBA Call
        --------
        FDSolver.UseSensitivityAnalysis(flag)
        """
        self.record_method('UseSensitivityAnalysis', flag)

    def set_use_double_precision(self, flag: bool) -> None:
        """
        VBA Call
        --------
        FDSolver.UseDoublePrecision(flag)
        """
        self.record_method('UseDoublePrecision', flag)

    def set_preconditioner_accuracy_int_eq(self, tolerance: float) -> None:
        """
        VBA Call
        --------
        FDSolver.PreconditionerAccuracyIntEq(tolerance)
        """
        self.record_method('PreconditionerAccuracyIntEq', tolerance)

    def set_min_mlfmm_box_size(self, tolerance: float) -> None:
        """
        VBA Call
        --------
        FDSolver.MinMLFMMBoxSize(tolerance)
        """
        self.record_method('MinMLFMMBoxSize', tolerance)

    def set_mlfmm_accuracy(self, accuracy: Union[MlfmmAccuracy, str]) -> None:
        """
        VBA Call
        --------
        FDSolver.MLFMMAccuracy(accuracy)
        """
        self.record_method('MLFMMAccuracy', str(getattr(accuracy, 'value', accuracy)))

    def set_use_cfie_for_cpec_int_eq(self, flag: bool) -> None:
        """
        VBA Call
        --------
        FDSolver.UseCFIEForCPECIntEq(flag)
        """
        self.record_method('UseCFIEForCPECIntEq', flag)

    def set_use_fast_rcs_sweep_int_eq(self, flag: bool) -> None:
        """
        VBA Call
        --------
        FDSolver.UseFastRCSSweepIntEq(flag)
        """
        self.record_method('UseFastRCSSweepIntEq', flag)

    def set_mrcs_sweep_properties(self, phi_start: float, phi_end: float, num_phi_steps: int, theta_start: float, theta_end: float, num_theta_steps: int, e_inc_theta: float, e_inc_phi: float) -> None:
        """
        VBA Call
        --------
        FDSolver.SetMRCSSweepProperties(phi_start, phi_end, num_phi_steps, theta_start, theta_end, num_theta_steps, e_inc_theta, e_inc_phi)
        """
        self.record_method('SetMRCSSweepProperties', phi_start, phi_end, num_phi_steps, theta_start, theta_end, num_theta_steps, e_inc_theta, e_inc_phi)

    def get_rcs_sweep_properties(self) -> Tuple:
        """
        VBA Call
        --------
        FDSolver.GetRCSSweepProperties(&phi_start, &phi_end, &num_phi_steps, &theta_start, &theta_end, &num_theta_steps, &e_inc_theta, &e_inc_phi, &activation)

        Returns
        -------
        (phi_start, phi_end, num_phi_steps, theta_start, theta_end, num_theta_steps, e_inc_theta, e_inc_phi, activation)
        """
        return self.query_method_t('GetRCSSweepProperties', None, VBATypeName.Double, VBATypeName.Double, VBATypeName.Integer, VBATypeName.Double, VBATypeName.Double, VBATypeName.Integer, VBATypeName.Double, VBATypeName.Double, VBATypeName.Boolean)

    def set_calc_block_excitations_in_parallel(self, enable: bool, use_block: bool, max_parallel: int) -> None:
        """
        VBA Call
        --------
        FDSolver.SetCalcBlockExcitationsInParallel(enable, use_block, max_parallel)
        """
        self.record_method('SetCalcBlockExcitationsInParallel', enable, use_block, max_parallel)

    def set_write_3d_fields_for_farfield_calc(self, flag: bool) -> None:
        """
        VBA Call
        --------
        FDSolver.SetWrite3DFieldsForFarfieldCalc(flag)
        """
        self.record_method('SetWrite3DFieldsForFarfieldCalc', flag)

    def set_record_unit_cell_scan_farfield(self, key: Union[RecordUnitCellScanFarfield, str]) -> None:
        """
        VBA Call
        --------
        FDSolver.SetRecordUnitCellScanFarfield(key)
        """
        self.record_method('SetRecordUnitCellScanFarfield', str(getattr(key, 'value', key)))

    def set_consider_unit_cell_scan_farfield_symmetry(self, flag_theta: bool, flag_phi: bool) -> None:
        """
        VBA Call
        --------
        FDSolver.SetConsiderUnitCellScanFarfieldSymmetry(flag_theta, flag_phi)
        """
        self.record_method('SetConsiderUnitCellScanFarfieldSymmetry', flag_theta, flag_phi)

    def set_disable_result_templates_during_unit_cell_scan_angle_sweep(self, flag: bool) -> None:
        """
        VBA Call
        --------
        FDSolver.SetDisableResultTemplatesDuringUnitCellScanAngleSweep(flag)
        """
        self.record_method('SetDisableResultTemplatesDuringUnitCellScanAngleSweep', flag)

    def extract_unit_cell_scan_farfield(self, frequencies: list[float], names: list[str], anchor: int) -> None:
        """
        VBA Call
        --------
        FDSolver.ExtractUnitCellScanFarfield(';'.join(str(f) for f in frequencies), ';'.join(str(s) for s in names), anchor)
        """
        self.record_method('ExtractUnitCellScanFarfield', ';'.join(str(f) for f in frequencies), ';'.join(str(s) for s in names), anchor)

    def update_interpolation_settings(self, navigation_tree_path: str) -> None:
        """
        VBA Call
        --------
        FDSolver.UpdateInterpolationSettings(navigation_tree_path)
        """
        self.record_method('UpdateInterpolationSettings', navigation_tree_path)

    def export_mor_solution(self, frequency: float) -> None:
        """
        VBA Call
        --------
        FDSolver.ExportMORSolution(frequency)
        """
        self.record_method('ExportMORSolution', frequency)

    def set_force_recalculate_old_samples(self, flag: bool) -> None:
        """
        VBA Call
        --------
        FDSolver.ForceRecalculateOldSamples(flag)
        """
        self.record_method('ForceRecalculateOldSamples', flag)

    def set_allow_float_direct_solver(self, flag: bool) -> None:
        """
        VBA Call
        --------
        FDSolver.SetAllowFloatDirectSolver(flag)
        """
        self.record_method('SetAllowFloatDirectSolver', flag)

    def set_allow_change_settings_for_schematic(self, flag: bool) -> None:
        """
        VBA Call
        --------
        FDSolver.SetAllowChangeSettingsForSchematic(flag)
        """
        self.record_method('SetAllowChangeSettingsForSchematic', flag)

