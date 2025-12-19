'''This file is auto-generated. Do not edit.'''
from .. import IVBAProvider, VBAObjWrapper
from enum import Enum
from typing import Union

class Optimizer(VBAObjWrapper):
    class GoalType(Enum):
        PRIMARY_RESULT_1D = '1D Primary Result'
        PRIMARY_RESULT_1DC = '1DC Primary Result'
        RESULT_0D = '0D Result'
        RESULT_1D = '1D Result'
        RESULT_1DC = '1DC Result'

    class GoalSummaryType(Enum):
        SUM_ALL_GOALS = 'Sum_All_Goals'
        MAX_ALL_GOALS = 'Max_All_Goals'

    class GoalOperator(Enum):
        LESS_THAN = '<'
        GREATER_THAN = '>'
        EQUAL = '='
        MIN = 'min'
        MAX = 'max'
        MOVE_MIN = 'move min'
        MOVE_MAX = 'move max'

    class GoalNorm(Enum):
        MAX_DIFF = 'MaxDiff'
        MAX_DIFF_SQ = 'MaxDiffSq'
        SUM_DIFF = 'SumDiff'
        SUM_DIFF_SQ = 'SumDiffSq'
        DIFF = 'Diff'
        DIFF_SQ = 'DiffSq'

    class GoalScalarType(Enum):
        MAG_LIN = 'maglin'
        MAG_DB_10 = 'magdb10'
        MAG_DB_20 = 'magdb20'
        REAL = 'real'
        IMAG = 'imag'
        PHASE = 'phase'

    class GoalRangeType(Enum):
        TOTAL = 'total'
        RANGE = 'range'
        SINGLE = 'single'

    class OptimizerType(Enum):
        TRUST_REGION = 'Trust_Region'
        NELDER_MEAD_SIMPLEX = 'Nelder_Mead_Simplex'
        CMAES = 'CMAES'
        GENETIC_ALGORITHM = 'Genetic_Algorithm'
        PARTICLE_SWARM = 'Particle_Swarm'
        INTERPOLATED_NR_VARIABLE_METRIC = 'Interpolated_NR_VariableMetric'
        CLASSIC_POWELL = 'Classic Powell'

    class InterpolationType(Enum):
        SECOND_ORDER = 'Second_Order'

    class DistributionType(Enum):
        UNIFORM_RANDOM_NUMBERS = 'Uniform_Random_Numbers'
        LATIN_HYPER_CUBE = 'Latin_Hyper_Cube'
        NOISY_LATIN_HYPER_CUBE = 'Noisy_Latin_Hyper_Cube'
        CUBE_DISTRIBUTION = 'Cube_Distribution'

    class DataStorageStrategy(Enum):
        ALL = 'All'
        AUTOMATIC = 'Automatic'
        NONE = 'None'

    def __init__(self, vbap: IVBAProvider) -> None:
        super().__init__(vbap, 'Optimizer')
        self.set_save_history(False)

    def start(self) -> None:
        """
        VBA Call
        --------
        Optimizer.Start()
        """
        self.record_method('Start')

    def set_start_active_solver(self, flag: bool = True) -> None:
        """
        VBA Call
        --------
        Optimizer.StartActiveSolver(flag)
        """
        self.record_method('StartActiveSolver', flag)

    def init_parameter_list(self) -> None:
        """
        VBA Call
        --------
        Optimizer.InitParameterList()
        """
        self.record_method('InitParameterList')

    def reset_parameter_list(self) -> None:
        """
        VBA Call
        --------
        Optimizer.ResetParameterList()
        """
        self.record_method('ResetParameterList')

    def select_parameter(self, param_name: str, use_for_optimization: bool = True) -> None:
        """
        VBA Call
        --------
        Optimizer.SelectParameter(param_name, use_for_optimization)
        """
        self.record_method('SelectParameter', param_name, use_for_optimization)

    def set_parameter_init_value(self, value: float) -> None:
        """
        VBA Call
        --------
        Optimizer.SetParameterInit(value)
        """
        self.record_method('SetParameterInit', value)

    def set_parameter_min_value(self, value: float) -> None:
        """
        VBA Call
        --------
        Optimizer.SetParameterMin(value)
        """
        self.record_method('SetParameterMin', value)

    def set_parameter_max_value(self, value: float) -> None:
        """
        VBA Call
        --------
        Optimizer.SetParameterMax(value)
        """
        self.record_method('SetParameterMax', value)

    def set_parameter_number_of_anchors(self, number: int) -> None:
        """
        VBA Call
        --------
        Optimizer.SetParameterAnchors(number)
        """
        self.record_method('SetParameterAnchors', number)

    def set_min_max_auto(self, percentage: float) -> None:
        """
        VBA Call
        --------
        Optimizer.SetMinMaxAuto(percentage)
        """
        self.record_method('SetMinMaxAuto', percentage)

    def set_and_update_min_max_auto(self, percentage: float) -> None:
        """
        VBA Call
        --------
        Optimizer.SetAndUpdateMinMaxAuto(percentage)
        """
        self.record_method('SetAndUpdateMinMaxAuto', percentage)

    def set_always_start_from_current(self, flag: bool = True) -> None:
        """
        VBA Call
        --------
        Optimizer.SetAlwaysStartFromCurrent(flag)
        """
        self.record_method('SetAlwaysStartFromCurrent', flag)

    def set_use_data_of_previous_calculations(self, flag: bool = True) -> None:
        """
        VBA Call
        --------
        Optimizer.SetUseDataOfPreviousCalculations(flag)
        """
        self.record_method('SetUseDataOfPreviousCalculations', flag)

    def get_number_of_varying_parameters(self) -> int:
        """
        VBA Call
        --------
        Optimizer.GetNumberOfVaryingParameters()
        """
        return self.query_method_int('GetNumberOfVaryingParameters')

    def get_name_of_varying_parameter(self, index: int) -> str:
        """
        VBA Call
        --------
        Optimizer.GetNameOfVaryingParameter(index)
        """
        return self.query_method_str('GetNameOfVaryingParameter', index)

    def get_value_of_varying_parameter(self, index: int) -> float:
        """
        VBA Call
        --------
        Optimizer.GetValueOfVaryingParameter(index)
        """
        return self.query_method_float('GetValueOfVaryingParameter', index)

    def get_parameter_min_of_varying_parameter(self, index: int) -> float:
        """
        VBA Call
        --------
        Optimizer.GetParameterMinOfVaryingParameter(index)
        """
        return self.query_method_float('GetParameterMinOfVaryingParameter', index)

    def get_parameter_max_of_varying_parameter(self, index: int) -> float:
        """
        VBA Call
        --------
        Optimizer.GetParameterMaxOfVaryingParameter(index)
        """
        return self.query_method_float('GetParameterMaxOfVaryingParameter', index)

    def get_parameter_init_of_varying_parameter(self, index: int) -> float:
        """
        VBA Call
        --------
        Optimizer.GetParameterInitOfVaryingParameter(index)
        """
        return self.query_method_float('GetParameterInitOfVaryingParameter', index)

    def add_goal(self, goal_type: Union[GoalType, str]) -> int:
        """
        VBA Call
        --------
        Optimizer.AddGoal(goal_type)
        """
        return self.query_method_int('AddGoal', str(getattr(goal_type, 'value', goal_type)))

    def select_goal(self, id: int, use_for_optimization: bool = True) -> None:
        """
        VBA Call
        --------
        Optimizer.SelectGoal(id, use_for_optimization)
        """
        self.record_method('SelectGoal', id, use_for_optimization)

    def delete_goal(self, id: int) -> None:
        """
        VBA Call
        --------
        Optimizer.DeleteGoal(id)
        """
        self.record_method('DeleteGoal', id)

    def delete_all_goals(self) -> None:
        """
        VBA Call
        --------
        Optimizer.DeleteAllGoals()
        """
        self.record_method('DeleteAllGoals')

    def set_goal_summary_type(self, goal_summary_type: Union[GoalSummaryType, str]) -> None:
        """
        VBA Call
        --------
        Optimizer.SetGoalSummaryType(goal_summary_type)
        """
        self.record_method('SetGoalSummaryType', str(getattr(goal_summary_type, 'value', goal_summary_type)))

    def set_use_goal_for_optimization(self, flag: bool = True) -> None:
        """
        VBA Call
        --------
        Optimizer.SetGoalUseFlag(flag)
        """
        self.record_method('SetGoalUseFlag', flag)

    def set_goal_operator(self, operator_type: Union[GoalOperator, str]) -> None:
        """
        VBA Call
        --------
        Optimizer.SetGoalOperator(operator_type)
        """
        self.record_method('SetGoalOperator', str(getattr(operator_type, 'value', operator_type)))

    def set_goal_target(self, value: float) -> None:
        """
        VBA Call
        --------
        Optimizer.SetGoalTarget(value)
        """
        self.record_method('SetGoalTarget', value)

    def set_goal_norm_new(self, norm: Union[GoalNorm, str]) -> None:
        """
        VBA Call
        --------
        Optimizer.SetGoalNormNew(norm)
        """
        self.record_method('SetGoalNormNew', str(getattr(norm, 'value', norm)))

    def set_goal_weight(self, value: float) -> None:
        """
        VBA Call
        --------
        Optimizer.SetGoalWeight(value)
        """
        self.record_method('SetGoalWeight', value)

    def set_goal_scalar_type(self, scalar_type: Union[GoalScalarType, str]) -> None:
        """
        VBA Call
        --------
        Optimizer.SetGoalScalarType(scalar_type)
        """
        self.record_method('SetGoalScalarType', str(getattr(scalar_type, 'value', scalar_type)))

    def set_goal_1d_result_name(self, name: str) -> None:
        """
        VBA Call
        --------
        Optimizer.SetGoal1DResultName(name)
        """
        self.record_method('SetGoal1DResultName', name)

    def set_goal_1dc_result_name(self, name: str) -> None:
        """
        VBA Call
        --------
        Optimizer.SetGoal1DCResultName(name)
        """
        self.record_method('SetGoal1DCResultName', name)

    def set_goal_template_based_0d_result_name(self, name: str) -> None:
        """
        VBA Call
        --------
        Optimizer.SetGoalTemplateBased0DResultName(name)
        """
        self.record_method('SetGoalTemplateBased0DResultName', name)

    def set_goal_template_based_1d_result_name(self, name: str) -> None:
        """
        VBA Call
        --------
        Optimizer.SetGoalTemplateBased1DResultName(name)
        """
        self.record_method('SetGoalTemplateBased1DResultName', name)

    def set_goal_template_based_1dc_result_name(self, name: str) -> None:
        """
        VBA Call
        --------
        Optimizer.SetGoalTemplateBased1DCResultName(name)
        """
        self.record_method('SetGoalTemplateBased1DCResultName', name)

    def set_goal_range(self, min_value: float, max_value: float) -> None:
        """
        VBA Call
        --------
        Optimizer.SetGoalRange(min_value, max_value)
        """
        self.record_method('SetGoalRange', min_value, max_value)

    def set_goal_range_type(self, range_type: Union[GoalRangeType, str]) -> None:
        """
        VBA Call
        --------
        Optimizer.SetGoalRangeType(range_type)
        """
        self.record_method('SetGoalRangeType', str(getattr(range_type, 'value', range_type)))

    def set_use_slope(self, flag: bool = True) -> None:
        """
        VBA Call
        --------
        Optimizer.UseSlope(flag)
        """
        self.record_method('UseSlope', flag)

    def set_goal_target_max(self, value: float) -> None:
        """
        VBA Call
        --------
        Optimizer.SetGoalTargetMax(value)
        """
        self.record_method('SetGoalTargetMax', value)

    def set_optimizer_type(self, optimizer_type: Union[OptimizerType, str]) -> None:
        """
        VBA Call
        --------
        Optimizer.SetOptimizerType(optimizer_type)
        """
        self.record_method('SetOptimizerType', str(getattr(optimizer_type, 'value', optimizer_type)))

    def set_use_interpolation(self, interpolation: Union[InterpolationType, str], optimizer_type: Union[OptimizerType, str]) -> None:
        """
        VBA Call
        --------
        Optimizer.SetUseInterpolation(interpolation, optimizer_type)
        """
        self.record_method('SetUseInterpolation', str(getattr(interpolation, 'value', interpolation)), str(getattr(optimizer_type, 'value', optimizer_type)))

    def set_generation_size(self, optimizer_type: Union[OptimizerType, str], size: float) -> None:
        """
        VBA Call
        --------
        Optimizer.SetGenerationSize(optimizer_type, size)
        """
        self.record_method('SetGenerationSize', str(getattr(optimizer_type, 'value', optimizer_type)), size)

    def set_max_number_of_iterations(self, optimizer_type: Union[OptimizerType, str], number: int) -> None:
        """
        VBA Call
        --------
        Optimizer.SetMaxIt(optimizer_type, number)
        """
        self.record_method('SetMaxIt', str(getattr(optimizer_type, 'value', optimizer_type)), number)

    def set_initial_distribution(self, optimizer_type: Union[OptimizerType, str], distribution: Union[DistributionType, str]) -> None:
        """
        VBA Call
        --------
        Optimizer.SetInitialDistribution(optimizer_type, distribution)
        """
        self.record_method('SetInitialDistribution', str(getattr(optimizer_type, 'value', optimizer_type)), str(getattr(distribution, 'value', distribution)))

    def set_goal_function_level(self, optimizer_type: Union[OptimizerType, str], level: float) -> None:
        """
        VBA Call
        --------
        Optimizer.SetGoalFunctionLevel(optimizer_type, level)
        """
        self.record_method('SetGoalFunctionLevel', str(getattr(optimizer_type, 'value', optimizer_type)), level)

    def set_mutation_rate(self, optimizer_type: Union[OptimizerType, str], rate: float) -> None:
        """
        VBA Call
        --------
        Optimizer.SetMutationRate(optimizer_type, rate)
        """
        self.record_method('SetMutationRate', str(getattr(optimizer_type, 'value', optimizer_type)), rate)

    def set_min_simplex_size(self, value: float) -> None:
        """
        VBA Call
        --------
        Optimizer.SetMinSimplexSize(value)
        """
        self.record_method('SetMinSimplexSize', value)

    def set_use_max_number_of_evaluations(self, optimizer_type: Union[OptimizerType, str], flag: bool = True) -> None:
        """
        VBA Call
        --------
        Optimizer.SetUseMaxEval(optimizer_type, flag)
        """
        self.record_method('SetUseMaxEval', str(getattr(optimizer_type, 'value', optimizer_type)), flag)

    def set_max_number_of_evaluations(self, optimizer_type: Union[OptimizerType, str], number: int) -> None:
        """
        VBA Call
        --------
        Optimizer.SetMaxEval(optimizer_type, number)
        """
        self.record_method('SetMaxEval', str(getattr(optimizer_type, 'value', optimizer_type)), number)

    def set_use_pre_def_point_in_init_distribution(self, optimizer_type: Union[OptimizerType, str], flag: bool = True) -> None:
        """
        VBA Call
        --------
        Optimizer.SetUsePreDefPointInInitDistribution(optimizer_type, flag)
        """
        self.record_method('SetUsePreDefPointInInitDistribution', str(getattr(optimizer_type, 'value', optimizer_type)), flag)

    def set_number_of_refinements(self, number: int) -> None:
        """
        VBA Call
        --------
        Optimizer.SetNumRefinements(number)
        """
        self.record_method('SetNumRefinements', number)

    def set_domain_accuracy(self, optimizer_type: Union[OptimizerType, str], accuracy: float) -> None:
        """
        VBA Call
        --------
        Optimizer.SetDomainAccuracy(optimizer_type, accuracy)
        """
        self.record_method('SetDomainAccuracy', str(getattr(optimizer_type, 'value', optimizer_type)), accuracy)

    def set_sigma(self, optimizer_type: Union[OptimizerType, str], sigma: float) -> None:
        """
        VBA Call
        --------
        Optimizer.SetSigma(optimizer_type, sigma)
        """
        self.record_method('SetSigma', str(getattr(optimizer_type, 'value', optimizer_type)), sigma)

    def set_accuracy(self, optimizer_type: Union[OptimizerType, str], accuracy: float) -> None:
        """
        VBA Call
        --------
        Optimizer.SetAccuracy(optimizer_type, accuracy)
        """
        self.record_method('SetAccuracy', str(getattr(optimizer_type, 'value', optimizer_type)), accuracy)

    def set_data_storage_strategy(self, strategy: Union[DataStorageStrategy, str]) -> None:
        """
        VBA Call
        --------
        Optimizer.SetDataStorageStrategy(strategy)
        """
        self.record_method('SetDataStorageStrategy', str(getattr(strategy, 'value', strategy)))

    def set_move_mesh(self, flag: bool = True) -> None:
        """
        VBA Call
        --------
        Optimizer.SetOptionMoveMesh(flag)
        """
        self.record_method('SetOptionMoveMesh', flag)

