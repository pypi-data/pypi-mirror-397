'''This file is auto-generated. Do not edit.'''
from .. import IVBAProvider, VBAObjWrapper
from enum import Enum
from typing import Union, Optional

class EigenmodeSolver(VBAObjWrapper):
    class MethodType(Enum):
        AKS = 'AKS'
        JDM = 'JDM'
        JDM_LOW_MEMORY = 'JDM (low memory)'
        AUTOMATIC = 'Automatic'
        CLASSICAL_LOSSLESS = 'Classical (Lossless)'
        GENERAL_LOSSY = 'General (Lossy)'

    class MethodMesh(Enum):
        HEX = 'Hex'
        TET = 'Tet'

    class MeshType(Enum):
        HEXAHEDRAL_MESH = 'Hexahedral Mesh'
        TETRAHEDRAL_MESH = 'Tetrahedral Mesh'

    def __init__(self, vbap: IVBAProvider) -> None:
        super().__init__(vbap, 'EigenmodeSolver')
        self.set_save_history(False)

    def reset(self) -> None:
        """
        VBA Call
        --------
        EigenmodeSolver.Reset()
        """
        self.record_method('Reset')

    def start(self) -> bool:
        """
        VBA Call
        --------
        EigenmodeSolver.Start()
        """
        return self.query_method_bool('Start')

    def set_mesh_adaptation_hex(self, flag: bool = True) -> None:
        """
        VBA Call
        --------
        EigenmodeSolver.SetMeshAdaptationHex(flag)
        """
        self.record_method('SetMeshAdaptationHex', flag)

    def set_mesh_adaptation_tet(self, flag: bool = True) -> None:
        """
        VBA Call
        --------
        EigenmodeSolver.SetMeshAdaptationTet(flag)
        """
        self.record_method('SetMeshAdaptationTet', flag)

    def set_number_of_modes(self, number: int) -> None:
        """
        VBA Call
        --------
        EigenmodeSolver.SetNumberOfModes(number)
        """
        self.record_method('SetNumberOfModes', number)

    def set_calculate_modes_in_frequency_range(self, flag: bool = True) -> None:
        """
        VBA Call
        --------
        EigenmodeSolver.SetModesInFrequencyRange(flag)
        """
        self.record_method('SetModesInFrequencyRange', flag)

    def set_consider_static_modes(self, flag: bool = True) -> None:
        """
        VBA Call
        --------
        EigenmodeSolver.SetConsiderStaticModes(flag)
        """
        self.record_method('SetConsiderStaticModes', flag)

    def set_use_remote_calculation(self, flag: bool = True) -> None:
        """
        VBA Call
        --------
        EigenmodeSolver.SetRemoteCalculation(flag)
        """
        self.record_method('SetRemoteCalculation', flag)

    def set_method_type(self, method_type: Union[MethodType, str], mesh: Union[MethodMesh, str]) -> None:
        """
        VBA Call
        --------
        EigenmodeSolver.SetMethodType(method_type, mesh)
        """
        self.record_method('SetMethodType', str(getattr(method_type, 'value', method_type)), str(getattr(mesh, 'value', mesh)))

    def set_mesh_type(self, mesh_type: Union[MeshType, str]) -> None:
        """
        VBA Call
        --------
        EigenmodeSolver.SetMeshType(mesh_type)
        """
        self.record_method('SetMeshType', str(getattr(mesh_type, 'value', mesh_type)))

    def set_material_evaluation_frequency(self, freq: Optional[float]) -> None:
        """
        VBA Call
        --------
        EigenmodeSolver.SetMaterialEvaluationFrequency(freq is None, freq or 0.0)
        """
        self.record_method('SetMaterialEvaluationFrequency', freq is None, freq or 0.0)

    def set_frequency_target(self, freq: Optional[float]) -> None:
        """
        VBA Call
        --------
        EigenmodeSolver.SetFrequencyTarget(freq is None, freq or 0.0)
        """
        self.record_method('SetFrequencyTarget', freq is None, freq or 0.0)

    def set_lower_bound_for_q(self, q_min: Optional[float]) -> None:
        """
        VBA Call
        --------
        EigenmodeSolver.SetLowerBoundForQ(q_min is None, q_min or 0.0)
        """
        self.record_method('SetLowerBoundForQ', q_min is None, q_min or 0.0)

    def set_max_number_of_threads(self, number: int) -> None:
        """
        VBA Call
        --------
        EigenmodeSolver.SetMaxNumberOfThreads(number)
        """
        self.record_method('SetMaxNumberOfThreads', number)

    def set_use_parallelization(self, flag: bool = True) -> None:
        """
        VBA Call
        --------
        EigenmodeSolver.SetUseParallelization(flag)
        """
        self.record_method('SetUseParallelization', flag)

    def set_consider_losses_in_postprocessing_only(self, flag: bool = True) -> None:
        """
        VBA Call
        --------
        EigenmodeSolver.SetConsiderLossesInPostprocessingOnly(flag)
        """
        self.record_method('SetConsiderLossesInPostprocessingOnly', flag)

    def get_consider_losses_in_postprocessing_only(self) -> bool:
        """
        VBA Call
        --------
        EigenmodeSolver.GetConsiderLossesInPostprocessingOnly()
        """
        return self.query_method_bool('GetConsiderLossesInPostprocessingOnly')

    def set_minimum_q(self, min_q: float) -> None:
        """
        VBA Call
        --------
        EigenmodeSolver.SetMinimumQ(min_q)
        """
        self.record_method('SetMinimumQ', min_q)

    def set_calculate_external_q_factor(self, flag: bool = True) -> None:
        """
        VBA Call
        --------
        EigenmodeSolver.SetCalculateExternalQFactor(flag)
        """
        self.record_method('SetCalculateExternalQFactor', flag)

    def set_q_external_accuracy(self, accuracy: float) -> None:
        """
        VBA Call
        --------
        EigenmodeSolver.SetQExternalAccuracy(accuracy)
        """
        self.record_method('SetQExternalAccuracy', accuracy)

    def set_order_tet(self, order: int) -> None:
        """
        VBA Call
        --------
        EigenmodeSolver.SetOrderTet(order)
        """
        self.record_method('SetOrderTet', order)

    def set_store_results_in_cache(self, flag: bool = True) -> None:
        """
        VBA Call
        --------
        EigenmodeSolver.SetStoreResultsInCache(flag)
        """
        self.record_method('SetStoreResultsInCache', flag)

    def set_td_compatible_materials(self, flag: bool = True) -> None:
        """
        VBA Call
        --------
        EigenmodeSolver.SetTDCompatibleMaterials(flag)
        """
        self.record_method('SetTDCompatibleMaterials', flag)

    def set_calculate_thermal_losses(self, flag: bool = True) -> None:
        """
        VBA Call
        --------
        EigenmodeSolver.SetCalculateThermalLosses(flag)
        """
        self.record_method('SetCalculateThermalLosses', flag)

    def set_accuracy(self, accuracy: float) -> None:
        """
        VBA Call
        --------
        EigenmodeSolver.SetAccuracy(accuracy)
        """
        self.record_method('SetAccuracy', accuracy)

    def get_number_of_modes_calculated(self) -> int:
        """
        VBA Call
        --------
        EigenmodeSolver.GetNumberOfModesCalculated()
        """
        return self.query_method_int('GetNumberOfModesCalculated')

    def get_mode_frequency_in_hz(self, mode_number: int) -> float:
        """
        VBA Call
        --------
        EigenmodeSolver.GetModeFrequencyInHz(mode_number)
        """
        return self.query_method_float('GetModeFrequencyInHz', mode_number)

    def get_mode_rel_residual_norm(self, mode_number: int) -> float:
        """
        VBA Call
        --------
        EigenmodeSolver.GetModeRelResidualNorm(mode_number)
        """
        return self.query_method_float('GetModeRelResidualNorm', mode_number)

    def get_mode_q_factor(self, mode_number: int) -> float:
        """
        VBA Call
        --------
        EigenmodeSolver.GetModeQFactor(mode_number)
        """
        return self.query_method_float('GetModeQFactor', mode_number)

    def get_mode_external_q_factor(self, mode_number: int) -> float:
        """
        VBA Call
        --------
        EigenmodeSolver.GetModeExternalQFactor(mode_number)
        """
        return self.query_method_float('GetModeExternalQFactor', mode_number)

    def get_loaded_frequency_in_hz(self, mode_number: int) -> float:
        """
        VBA Call
        --------
        EigenmodeSolver.GetLoadedFrequencyInHz(mode_number)
        """
        return self.query_method_float('GetLoadedFrequencyInHz', mode_number)

    def get_number_of_sensitivity_design_parameters(self) -> int:
        """
        VBA Call
        --------
        EigenmodeSolver.GetNumberOfSensitivityDesignParameters()
        """
        return self.query_method_int('GetNumberOfSensitivityDesignParameters')

    def get_sensitivity_design_parameter(self, index: int) -> str:
        """
        VBA Call
        --------
        EigenmodeSolver.GetSensitivityDesignParameter(index+1)
        """
        return self.query_method_str('GetSensitivityDesignParameter', index+1)

    def get_frequency_sensitivity(self, param_name: str, mode_number: int) -> float:
        """
        VBA Call
        --------
        EigenmodeSolver.GetFrequencySensitivity(param_name, mode_number)
        """
        return self.query_method_float('GetFrequencySensitivity', param_name, mode_number)

    def get_q_factor_sensitivity(self, param_name: str, mode_number: int) -> float:
        """
        VBA Call
        --------
        EigenmodeSolver.GetQFactorSensitivity(param_name, mode_number)
        """
        return self.query_method_float('GetQFactorSensitivity', param_name, mode_number)

    def reset_force_calculation(self) -> None:
        """
        VBA Call
        --------
        EigenmodeSolver.ResetForceCalculation()
        """
        self.record_method('ResetForceCalculation')

    def calculate_lorentz_force_for_mode(self, mode_index: int) -> None:
        """
        VBA Call
        --------
        EigenmodeSolver.CalculateLorentzForceForMode(mode_index)
        """
        self.record_method('CalculateLorentzForceForMode', mode_index)

    def calculate_lorentz_force_for_all_modes(self) -> None:
        """
        VBA Call
        --------
        EigenmodeSolver.CalculateLorentzForceForAllModes()
        """
        self.record_method('CalculateLorentzForceForAllModes')

    def is_mode_selected_for_force_calculation(self, mode_index: int) -> bool:
        """
        VBA Call
        --------
        EigenmodeSolver.IsModeSelectedForForceCalculation(mode_index)
        """
        return self.query_method_bool('IsModeSelectedForForceCalculation', mode_index)

    def is_any_mode_selected_for_force_calculation(self) -> bool:
        """
        VBA Call
        --------
        EigenmodeSolver.IsAnyModeSelectedForForceCalculation()
        """
        return self.query_method_bool('IsAnyModeSelectedForForceCalculation')

    def start_force_calculation(self) -> bool:
        """
        VBA Call
        --------
        EigenmodeSolver.StartForceCalculation()
        """
        return self.query_method_bool('StartForceCalculation')

