'''This file is auto-generated. Do not edit.'''
from .. import IVBAProvider, VBAObjWrapper
from enum import Enum
from typing import Union

class ParameterSweep(VBAObjWrapper):
    class SimulationType(Enum):
        TRANSIENT = 'Transient'
        PORT_MODES_ONLY = 'Calculate port modes only'
        EIGENMODE = 'Eigenmode'
        FREQUENCY = 'Frequency'
        TLM = 'TLM'
        ASYMTOTIC = 'Asymtotic'
        E_STATIC = 'E-Static'
        ELECTROQUASISTATIC = 'Electroquasistatic'
        TRANSIENT_ELECTROQUASISTATIC = 'Transient Electroquasistatic'
        M_STATIC = 'M-Static'
        TRANSIENT_MAGNETOQUASISTATIC = 'Transient Magnetoquasistatic'
        J_STATIC = 'J-Static'
        LOW_FREQUENCY = 'Low Frequency'
        THERMAL = 'Thermal'
        TRANSIENT_THERMAL = 'Transient Thermal'
        STRUCTURAL_MECHANICS = 'Structural Mechanics'
        PIC = 'PIC'
        PARTICLE_TRACKING = 'Particle Tracking'

    def __init__(self, vbap: IVBAProvider) -> None:
        super().__init__(vbap, 'ParameterSweep')
        self.set_save_history(False)

    def set_simulation_type(self, sim_type: Union[SimulationType, str]) -> None:
        """
        VBA Call
        --------
        ParameterSweep.SetSimulationType(sim_type)
        """
        self.record_method('SetSimulationType', str(getattr(sim_type, 'value', sim_type)))

    def add_sequence(self, name: str) -> None:
        """
        VBA Call
        --------
        ParameterSweep.AddSequence(name)
        """
        self.record_method('AddSequence', name)

    def delete_sequence(self, name: str) -> None:
        """
        VBA Call
        --------
        ParameterSweep.DeleteSequence(name)
        """
        self.record_method('DeleteSequence', name)

    def set_sequence_enabled(self, name: str, flag: bool = True) -> None:
        """
        VBA Call
        --------
        ParameterSweep.EnableSequence(name, flag)
        """
        self.record_method('EnableSequence', name, flag)

    def delete_all_sequences(self) -> None:
        """
        VBA Call
        --------
        ParameterSweep.DeleteAllSequences()
        """
        self.record_method('DeleteAllSequences')

    def rename_sequence(self, old_name: str, new_name: str) -> None:
        """
        VBA Call
        --------
        ParameterSweep.RenameSequence(old_name, new_name)
        """
        self.record_method('RenameSequence', old_name, new_name)

    def add_parameter_samples_lin(self, seq_name: str, param_name: str, lower_bound: float, upper_bound: float, num_steps: int) -> None:
        """
        VBA Call
        --------
        ParameterSweep.AddParameter_Samples(seq_name, param_name, lower_bound, upper_bound, num_steps, False)
        """
        self.record_method('AddParameter_Samples', seq_name, param_name, lower_bound, upper_bound, num_steps, False)

    def add_parameter_samples_log(self, seq_name: str, param_name: str, lower_bound: float, upper_bound: float, num_steps: int) -> None:
        """
        VBA Call
        --------
        ParameterSweep.AddParameter_Samples(seq_name, param_name, lower_bound, upper_bound, num_steps, True)
        """
        self.record_method('AddParameter_Samples', seq_name, param_name, lower_bound, upper_bound, num_steps, True)

    def add_parameter_step_width(self, seq_name: str, param_name: str, lower_bound: float, upper_bound: float, width: float) -> None:
        """
        VBA Call
        --------
        ParameterSweep.AddParameter_Stepwidth(seq_name, param_name, lower_bound, upper_bound, width)
        """
        self.record_method('AddParameter_Stepwidth', seq_name, param_name, lower_bound, upper_bound, width)

    def add_parameter_arbitrary_points(self, seq_name: str, param_name: str, points: list[float]) -> None:
        """
        VBA Call
        --------
        ParameterSweep.AddParameter_ArbitraryPoints(seq_name, param_name, ';'.join(str(p) for p in points))
        """
        self.record_method('AddParameter_ArbitraryPoints', seq_name, param_name, ';'.join(str(p) for p in points))

    def delete_parameter(self, seq_name: str, param_name: str) -> None:
        """
        VBA Call
        --------
        ParameterSweep.DeleteParameter(seq_name, param_name)
        """
        self.record_method('DeleteParameter', seq_name, param_name)

    def start(self) -> None:
        """
        VBA Call
        --------
        ParameterSweep.Start()
        """
        self.record_method('Start')

    def set_use_distributed_computing(self, flag: bool = True) -> None:
        """
        VBA Call
        --------
        ParameterSweep.UseDistributedComputing(flag)
        """
        self.record_method('UseDistributedComputing', flag)

