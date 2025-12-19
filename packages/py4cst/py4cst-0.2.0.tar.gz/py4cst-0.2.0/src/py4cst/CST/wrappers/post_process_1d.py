'''This file is auto-generated. Do not edit.'''
from .. import IVBAProvider, VBAObjWrapper
from enum import Enum
from typing import Union

class PostProcess1D(VBAObjWrapper):
    class ApplyTarget(Enum):
        S_PARAMETER = 'S-parameter'
        PROBES = 'Probes'
        MONITORS = 'Monitors'

    class OperationType(Enum):
        TIME_WINDOW = 'Time Window'
        AR_FILTER = 'AR-Filter'
        PHASE_DEEMBEDDING = 'Phase Deembedding'
        RENORMALIZATION = 'Renormalization'
        VSWR = 'VSWR'
        YZ_MATRICES = 'YZ-matrices'
        EXCLUDE_PORT_MODES = 'Exclude Port Modes'

    def __init__(self, vbap: IVBAProvider) -> None:
        super().__init__(vbap, 'PostProcess1D')
        self.set_save_history(False)

    def reset(self) -> None:
        """
        VBA Call
        --------
        PostProcess1D.Reset()
        """
        self.record_method('Reset')

    def set_apply_target(self, apply_target: Union[ApplyTarget, str]) -> None:
        """
        VBA Call
        --------
        PostProcess1D.ApplyTo(apply_target)
        """
        self.record_method('ApplyTo', str(getattr(apply_target, 'value', apply_target)))

    def add_operation(self, operation_type: Union[OperationType, str]) -> None:
        """
        VBA Call
        --------
        PostProcess1D.AddOperation(operation_type)
        """
        self.record_method('AddOperation', str(getattr(operation_type, 'value', operation_type)))

    def set_deembed_distance(self, port_name: int, distance: float) -> None:
        """
        VBA Call
        --------
        PostProcess1D.SetDeembedDistance(port_name, distance)
        """
        self.record_method('SetDeembedDistance', port_name, distance)

    def set_renorm_impedance(self, port_name: int, mode_name: int, impedance: float) -> None:
        """
        VBA Call
        --------
        PostProcess1D.SetRenormImpedance(port_name, mode_name, impedance)
        """
        self.record_method('SetRenormImpedance', port_name, mode_name, impedance)

    def set_renorm_impedance_on_all_ports(self, impedance: float) -> None:
        """
        VBA Call
        --------
        PostProcess1D.SetRenormImpedanceOnAllPorts(impedance)
        """
        self.record_method('SetRenormImpedanceOnAllPorts', impedance)

    def reset_renorm_impedance_on_all_ports(self) -> None:
        """
        VBA Call
        --------
        PostProcess1D.SetUnnormImpedanceOnAllPorts()
        """
        self.record_method('SetUnnormImpedanceOnAllPorts')

    def set_consider_port_mode(self, port_name: int, mode_name: int, flag: bool = True) -> None:
        """
        VBA Call
        --------
        PostProcess1D.SetConsiderPortMode(port_name, mode_name, flag)
        """
        self.record_method('SetConsiderPortMode', port_name, mode_name, flag)

    def run(self) -> None:
        """
        VBA Call
        --------
        PostProcess1D.Run()
        """
        self.record_method('Run')

    def set_operation_active(self, operation_type: Union[OperationType, str], active: bool = True) -> None:
        """
        VBA Call
        --------
        PostProcess1D.ActivateOperation(operation_type, active)
        """
        self.record_method('ActivateOperation', str(getattr(operation_type, 'value', operation_type)), active)

