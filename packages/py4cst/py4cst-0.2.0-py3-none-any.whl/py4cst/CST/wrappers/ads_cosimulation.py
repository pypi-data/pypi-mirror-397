'''This file is auto-generated. Do not edit.'''
from .. import IVBAProvider, VBAObjWrapper
from enum import Enum
from typing import Union

class ADSCosimulation(VBAObjWrapper):
    class SolverType(Enum):
        TRANSIENT = 'transient'
        FREQUENCY_DOMAIN = 'frequency domain'

    class ParamType(Enum):
        NONE = 'None'
        LENGTH = 'Length'
        TEMPERATURE = 'Temperature'
        VOLTAGE = 'Voltage'
        CURRENT = 'Current'
        RESISTANCE = 'Resistance'
        CONDUCTANCE = 'Conductance'
        CAPACITANCE = 'Capacitance'
        INDUCTANCE = 'Inductance'
        FREQUENCY = 'Frequency'
        TIME = 'Time'

    def __init__(self, vbap: IVBAProvider) -> None:
        super().__init__(vbap, 'ADSCosimulation')
        self.set_save_history(False)

    def set_cosimulation_enabled(self, flag: bool = True) -> None:
        """
        VBA Call
        --------
        ADSCosimulation.EnableCoSimulation(flag)
        """
        self.record_method('EnableCoSimulation', flag)

    def set_use_interpolation(self, flag: bool = True) -> None:
        """
        VBA Call
        --------
        ADSCosimulation.UseInterpolation(flag)
        """
        self.record_method('UseInterpolation', flag)

    def set_solver_type(self, solver_type: Union[SolverType, str]) -> None:
        """
        VBA Call
        --------
        ADSCosimulation.SolverType(solver_type)
        """
        self.record_method('SolverType', str(getattr(solver_type, 'value', solver_type)))

    def set_description(self, description: str) -> None:
        """
        VBA Call
        --------
        ADSCosimulation.Description(description)
        """
        self.record_method('Description', description)

    def set_parameter_info(self, param_name: str, use: bool, param_type: Union[ParamType, str], nominal_value: float, step_size: float) -> None:
        """
        VBA Call
        --------
        ADSCosimulation.ParameterInformation(param_name, use, param_type, nominal_value, step_size)
        """
        self.record_method('ParameterInformation', param_name, use, str(getattr(param_type, 'value', param_type)), nominal_value, step_size)

