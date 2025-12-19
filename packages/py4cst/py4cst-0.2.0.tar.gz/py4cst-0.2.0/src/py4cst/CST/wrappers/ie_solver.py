'''This file is auto-generated. Do not edit.'''
from .. import IVBAProvider, VBAObjWrapper
from enum import Enum
from typing import Union

class IESolver(VBAObjWrapper):
    class Accuracy(Enum):
        CUSTOM = 'Custom'
        LOW = 'Low'
        MEDIUM = 'Medium'
        HIGH = 'High'

    class RealGroundModelType(Enum):
        AUTO = 'Auto'
        TYPE_1 = 'Type 1'
        TYPE_2 = 'Type 2'

    class PreconditionerType(Enum):
        AUTO = 'Auto'
        TYPE_1 = 'Type 1'
        TYPE_2 = 'Type 2'
        TYPE_3 = 'Type 3'

    class CmaAccuracy(Enum):
        DEFAULT = 'Default'
        CUSTOM = 'Custom'

    class CmaMem(Enum):
        CUSTOM = 'Custom'
        LOW = 'Low'
        MEDIUM = 'Medium'
        HIGH = 'High'

    def __init__(self, vbap: IVBAProvider) -> None:
        super().__init__(vbap, 'IESolver')
        self.set_save_history(False)

    def reset(self) -> None:
        """
        VBA Call
        --------
        IESolver.Reset()
        """
        self.record_method('Reset')

    def set_accuracy_setting(self, accuracy: Union[Accuracy, str]) -> None:
        """
        VBA Call
        --------
        IESolver.SetAccuracySetting(accuracy)
        """
        self.record_method('SetAccuracySetting', str(getattr(accuracy, 'value', accuracy)))

    def set_use_fast_frequency_sweep(self, flag: bool) -> None:
        """
        VBA Call
        --------
        IESolver.UseFastFrequencySweep(flag)
        """
        self.record_method('UseFastFrequencySweep', flag)

    def set_use_ie_ground_plane(self, flag: bool) -> None:
        """
        VBA Call
        --------
        IESolver.UseIEGroundPlane(flag)
        """
        self.record_method('UseIEGroundPlane', flag)

    def set_real_ground_material_name(self, name: str) -> None:
        """
        VBA Call
        --------
        IESolver.SetRealGroundMaterialName(name)
        """
        self.record_method('SetRealGroundMaterialName', name)

    def set_calc_farfield_in_real_ground(self, flag: bool) -> None:
        """
        VBA Call
        --------
        IESolver.CalcFarFieldInRealGround(flag)
        """
        self.record_method('CalcFarFieldInRealGround', flag)

    def set_real_ground_model_type(self, model_type: Union[RealGroundModelType, str]) -> None:
        """
        VBA Call
        --------
        IESolver.RealGroundModelType(model_type)
        """
        self.record_method('RealGroundModelType', str(getattr(model_type, 'value', model_type)))

    def set_preconditioner_type(self, preconditioner_type: Union[PreconditionerType, str]) -> None:
        """
        VBA Call
        --------
        IESolver.PreconditionerType(preconditioner_type)
        """
        self.record_method('PreconditionerType', str(getattr(preconditioner_type, 'value', preconditioner_type)))

    def set_low_frequency_stabilization(self, flag: bool) -> None:
        """
        VBA Call
        --------
        IESolver.LowFrequencyStabilization(flag)
        """
        self.record_method('LowFrequencyStabilization', flag)

    def set_low_frequency_stabilization_multilayer(self, flag: bool) -> None:
        """
        VBA Call
        --------
        IESolver.LowFrequencyStabilizationML(flag)
        """
        self.record_method('LowFrequencyStabilizationML', flag)

    def set_multilayer(self, flag: bool) -> None:
        """
        VBA Call
        --------
        IESolver.Multilayer(flag)
        """
        self.record_method('Multilayer', flag)

    def set_iterative_mom_accuracy_ie_solver(self, accuracy: float) -> None:
        """
        VBA Call
        --------
        IESolver.SetiMoMACC_I(accuracy)
        """
        self.record_method('SetiMoMACC_I', accuracy)

    def set_iterative_mom_accuracy_multilayer_solver(self, accuracy: float) -> None:
        """
        VBA Call
        --------
        IESolver.SetiMoMACC_M(accuracy)
        """
        self.record_method('SetiMoMACC_M', accuracy)

    def set_cfie_alpha(self, accuracy: float) -> None:
        """
        VBA Call
        --------
        IESolver.SetCFIEAlpha(accuracy)
        """
        self.record_method('SetCFIEAlpha', accuracy)

    def set_deembed_external_ports(self, flag: bool) -> None:
        """
        VBA Call
        --------
        IESolver.DeembedExternalPorts(flag)
        """
        self.record_method('DeembedExternalPorts', flag)

    def set_open_boundary_condition_in_xy_dir(self, flag: bool) -> None:
        """
        VBA Call
        --------
        IESolver.SetOpenBC_XY(flag)
        """
        self.record_method('SetOpenBC_XY', flag)

    def set_cma_mode_tracking(self, flag: bool) -> None:
        """
        VBA Call
        --------
        IESolver.ModeTrackingCMA(flag)
        """
        self.record_method('ModeTrackingCMA', flag)

    def set_cma_number_of_modes(self, number: int) -> None:
        """
        VBA Call
        --------
        IESolver.NumberOfModesCMA(number)
        """
        self.record_method('NumberOfModesCMA', number)

    def set_cma_start_frequency(self, freq: float) -> None:
        """
        VBA Call
        --------
        IESolver.StartFrequencyCMA(freq)
        """
        self.record_method('StartFrequencyCMA', freq)

    def set_cma_accuracy_setting(self, accuracy: Union[CmaAccuracy, str]) -> None:
        """
        VBA Call
        --------
        IESolver.SetAccuracySettingCMA(accuracy)
        """
        self.record_method('SetAccuracySettingCMA', str(getattr(accuracy, 'value', accuracy)))

    def set_cma_number_of_frequency_samples(self, number: int) -> None:
        """
        VBA Call
        --------
        IESolver.FrequencySamplesCMA(number)
        """
        self.record_method('FrequencySamplesCMA', number)

    def set_cma_mem_setting(self, mem: Union[CmaMem, str]) -> None:
        """
        VBA Call
        --------
        IESolver.SetMemSettingCMA(mem)
        """
        self.record_method('SetMemSettingCMA', str(getattr(mem, 'value', mem)))

    def set_cma_calculate_modal_weighting_coefficients(self, flag: bool) -> None:
        """
        VBA Call
        --------
        IESolver.CalculateModalWeightingCoefficientsCMA(flag)
        """
        self.record_method('CalculateModalWeightingCoefficientsCMA', flag)

