'''This file is auto-generated. Do not edit.'''
from .. import IVBAProvider, VBAObjWrapper
from enum import Enum
from typing import Union

class MeshAdaption3D(VBAObjWrapper):
    class Type(Enum):
        E_STATIC = 'EStatic'
        M_STATIC = 'MStatic'
        J_STATIC = 'JStatic'
        LOW_FREQUENCY = 'LowFrequency'
        HIGH_FREQUENCY_HEX = 'HighFrequencyHex'
        HIGH_FREQUENCY_TET = 'HighFrequencyTet'
        TIME = 'Time'

    class Strategy(Enum):
        EXPERT_SYSTEM = 'ExpertSystem'
        ENERGY = 'Energy'

    class RefinementType(Enum):
        AUTOMATIC = 'Automatic'
        BISECTION = 'Bisection'

    class ErrorEstimatorType(Enum):
        AUTOMATIC = 'Automatic'

    def __init__(self, vbap: IVBAProvider) -> None:
        super().__init__(vbap, 'MeshAdaption3D')
        self.set_save_history(False)

    def set_error_limit(self, value: float) -> None:
        """
        VBA Call
        --------
        MeshAdaption3D.Errorlimit(value)
        """
        self.record_method('Errorlimit', value)

    def set_accuracy_factor(self, value: float) -> None:
        """
        VBA Call
        --------
        MeshAdaption3D.AccuracyFactor(value)
        """
        self.record_method('AccuracyFactor', value)

    def set_type(self, value: Union[Type, str]) -> None:
        """
        VBA Call
        --------
        MeshAdaption3D.SetType(value)
        """
        self.record_method('SetType', str(getattr(value, 'value', value)))

    def set_adaption_strategy(self, value: Union[Strategy, str]) -> None:
        """
        VBA Call
        --------
        MeshAdaption3D.SetAdaptionStrategy(value)
        """
        self.record_method('SetAdaptionStrategy', str(getattr(value, 'value', value)))

    def set_refinement_type(self, value: Union[RefinementType, str]) -> None:
        """
        VBA Call
        --------
        MeshAdaption3D.RefinementType(value)
        """
        self.record_method('RefinementType', str(getattr(value, 'value', value)))

    def set_error_estimator_type(self, value: Union[ErrorEstimatorType, str]) -> None:
        """
        VBA Call
        --------
        MeshAdaption3D.ErrorEstimatorType(value)
        """
        self.record_method('ErrorEstimatorType', str(getattr(value, 'value', value)))

    def set_min_number_of_passes(self, value: int) -> None:
        """
        VBA Call
        --------
        MeshAdaption3D.MinPasses(value)
        """
        self.record_method('MinPasses', value)

    def set_max_number_of_passes(self, value: int) -> None:
        """
        VBA Call
        --------
        MeshAdaption3D.MaxPasses(value)
        """
        self.record_method('MaxPasses', value)

    def set_cell_increase_factor(self, value: float) -> None:
        """
        VBA Call
        --------
        MeshAdaption3D.CellIncreaseFactor(value)
        """
        self.record_method('CellIncreaseFactor', value)

    def set_weight_e(self, value: float) -> None:
        """
        VBA Call
        --------
        MeshAdaption3D.WeightE(value)
        """
        self.record_method('WeightE', value)

    def set_weight_b(self, value: float) -> None:
        """
        VBA Call
        --------
        MeshAdaption3D.WeightB(value)
        """
        self.record_method('WeightB', value)

    def set_refine_x(self, flag: bool) -> None:
        """
        VBA Call
        --------
        MeshAdaption3D.RefineX(flag)
        """
        self.record_method('RefineX', flag)

    def set_refine_y(self, flag: bool) -> None:
        """
        VBA Call
        --------
        MeshAdaption3D.RefineY(flag)
        """
        self.record_method('RefineY', flag)

    def set_refine_z(self, flag: bool) -> None:
        """
        VBA Call
        --------
        MeshAdaption3D.RefineZ(flag)
        """
        self.record_method('RefineZ', flag)

    def set_max_delta_s(self, value: float) -> None:
        """
        VBA Call
        --------
        MeshAdaption3D.MaxDeltaS(value)
        """
        self.record_method('MaxDeltaS', value)

    def clear_stop_criteria(self) -> None:
        """
        VBA Call
        --------
        MeshAdaption3D.ClearStopCriteria()
        """
        self.record_method('ClearStopCriteria')

    def add_s_parameter_stop_criterion(self, auto_freq: bool, f_min: float, f_max: float, max_delta: float, num_checks: int, active: bool = True) -> None:
        """
        VBA Call
        --------
        MeshAdaption3D.AddSParameterStopCriterion(auto_freq, f_min, f_max, max_delta, num_checks, active)
        """
        self.record_method('AddSParameterStopCriterion', auto_freq, f_min, f_max, max_delta, num_checks, active)

    def add_0d_result_stop_criterion(self, result_name: str, max_delta: float, num_checks: int, active: bool = True) -> None:
        """
        VBA Call
        --------
        MeshAdaption3D.Add0DResultStopCriterion(result_name, max_delta, num_checks, active)
        """
        self.record_method('Add0DResultStopCriterion', result_name, max_delta, num_checks, active)

    def set_cell_increase_factor(self, result_name: str, max_delta: float, num_checks: int, active: bool = True, is_complex: bool = True) -> None:
        """
        VBA Call
        --------
        MeshAdaption3D.Add1DResultStopCriterion(result_name, max_delta, num_checks, active, is_complex)
        """
        self.record_method('Add1DResultStopCriterion', result_name, max_delta, num_checks, active, is_complex)

    def add_stop_criterion(self, group_name: str, threshold: float, num_checks: int, active: bool = True) -> None:
        """
        VBA Call
        --------
        MeshAdaption3D.AddStopCriterion(group_name, threshold, num_checks, active)
        """
        self.record_method('AddStopCriterion', group_name, threshold, num_checks, active)

    def remove_all_user_defined_stop_criteria(self) -> None:
        """
        VBA Call
        --------
        MeshAdaption3D.RemoveAllUserDefinedStopCriteria()
        """
        self.record_method('RemoveAllUserDefinedStopCriteria')

    def set_mesh_increment(self, value: float) -> None:
        """
        VBA Call
        --------
        MeshAdaption3D.MeshIncrement(value)
        """
        self.record_method('MeshIncrement', value)

    def set_frequency_range(self, f_min: float, f_max: float) -> None:
        """
        VBA Call
        --------
        MeshAdaption3D.SetFrequencyRange(False, f_min, f_max)
        """
        self.record_method('SetFrequencyRange', False, f_min, f_max)

    def set_frequency_range_auto(self) -> None:
        """
        VBA Call
        --------
        MeshAdaption3D.SetFrequencyRange(True, 0, 0)
        """
        self.record_method('SetFrequencyRange', True, 0, 0)

    def set_skipped_pulses(self, value: float) -> None:
        """
        VBA Call
        --------
        MeshAdaption3D.SkipPulses(value)
        """
        self.record_method('SkipPulses', value)

    def set_number_of_delta_s_checks(self, value: int) -> None:
        """
        VBA Call
        --------
        MeshAdaption3D.NumberOfDeltaSChecks(value)
        """
        self.record_method('NumberOfDeltaSChecks', value)

    def set_number_of_prop_const_checks(self, value: int) -> None:
        """
        VBA Call
        --------
        MeshAdaption3D.NumberOfPropConstChecks(value)
        """
        self.record_method('NumberOfPropConstChecks', value)

    def set_propagation_constant_accuracy(self, value: float) -> None:
        """
        VBA Call
        --------
        MeshAdaption3D.PropagationConstantAccuracy(value)
        """
        self.record_method('PropagationConstantAccuracy', value)

    def set_subsequent_checks_only_once(self, flag: bool) -> None:
        """
        VBA Call
        --------
        MeshAdaption3D.SubsequentChecksOnlyOnce(flag)
        """
        self.record_method('SubsequentChecksOnlyOnce', flag)

    def set_wavelength_based_refinement(self, flag: bool) -> None:
        """
        VBA Call
        --------
        MeshAdaption3D.WavelengthBasedRefinement(flag)
        """
        self.record_method('WavelengthBasedRefinement', flag)

    def set_min_accepted_cell_growth(self, value: float) -> None:
        """
        VBA Call
        --------
        MeshAdaption3D.MinimumAcceptedCellGrowth(value)
        """
        self.record_method('MinimumAcceptedCellGrowth', value)

    def set_ref_theta_factor(self, value: float) -> None:
        """
        VBA Call
        --------
        MeshAdaption3D.RefThetaFactor(value)
        """
        self.record_method('RefThetaFactor', value)

    def set_min_mesh_cell_growth(self, value: float) -> None:
        """
        VBA Call
        --------
        MeshAdaption3D.SetMinimumMeshCellGrowth(value)
        """
        self.record_method('SetMinimumMeshCellGrowth', value)

    def set_linear_growth_limitation(self, value: float) -> None:
        """
        VBA Call
        --------
        MeshAdaption3D.SetLinearGrowthLimitation(value)
        """
        self.record_method('SetLinearGrowthLimitation', value)

    def set_linear_growth_limitation(self, flag: bool) -> None:
        """
        VBA Call
        --------
        MeshAdaption3D.EnableLinearGrowthLimitation(flag)
        """
        self.record_method('EnableLinearGrowthLimitation', flag)

    def set_singular_edge_refinement(self, value: int) -> None:
        """
        VBA Call
        --------
        MeshAdaption3D.SingularEdgeRefinement(value)
        """
        self.record_method('SingularEdgeRefinement', value)

    def set_snap_to_geometry(self, flag: bool) -> None:
        """
        VBA Call
        --------
        MeshAdaption3D.SnapToGeometry(flag)
        """
        self.record_method('SnapToGeometry', flag)

    def set_inner_s_parameter_adaptation(self, flag: bool) -> None:
        """
        VBA Call
        --------
        MeshAdaption3D.EnableInnerSParameterAdaptation(flag)
        """
        self.record_method('EnableInnerSParameterAdaptation', flag)

    def set_port_propagation_constant_adaptation(self, flag: bool) -> None:
        """
        VBA Call
        --------
        MeshAdaption3D.EnablePortPropagationConstantAdaptation(flag)
        """
        self.record_method('EnablePortPropagationConstantAdaptation', flag)

