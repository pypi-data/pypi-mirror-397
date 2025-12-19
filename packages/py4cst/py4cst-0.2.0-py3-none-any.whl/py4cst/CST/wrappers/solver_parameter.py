'''This file is auto-generated. Do not edit.'''
from .. import IVBAProvider, VBAObjWrapper
from enum import Enum
from typing import Union

class SolverParameter(VBAObjWrapper):
    class SolverType(Enum):
        TRANSIENT = 'Transient solver'
        FREQ_DOMAIN = 'Frequency domain solver'
        ASYMPTOTIC = 'Asymptotic solver'
        EIGENMODE = 'Eigenmode solver'
        ELECTROSTATICS = 'Electrostatics solver'
        MAGNETOSTATIC = 'Magnetostatic solver'
        LF_FREQ_DOMAIN = 'LF Frequency domain solver'
        LF_FREQ_DOMAIN_EQS = 'LF Frequency domain solver (EQS)'
        STATIONARY_CURRENT = 'Stationary current solver'
        PARTICLE_TRACKING = 'Particle tracking solver'
        PIC = 'PIC solver'
        THERMAL = 'Thermal solver'
        INTEGRAL_EQUATION = 'Integral equation solver'
        MULTILAYER = 'Multilayer solver'
        LF_TIME_DOMAIN_MQS = 'LF Time domain solver (MQS)'
        LF_TIME_DOMAIN_EQS = 'LF Time domain solver (EQS)'
        THERMAL_TRANSIENT = 'Thermal transient solver'
        STRUCTURAL_MECHANICS = 'Structural mechanics solver'
        WAKEFIELD = 'Wakefield solver'

    class MeshType(Enum):
        HEXAHEDRAL = 'Hexahedral'
        TETRAHEDRAL = 'Tetrahedral'
        SURFACE = 'Surface'

    def __init__(self, vbap: IVBAProvider) -> None:
        super().__init__(vbap, 'SolverParameter')
        self.set_save_history(False)

    def set_solver_type(self, solver_type: Union[SolverType, str], mesh_type: Union[MeshType, str]) -> None:
        """
        VBA Call
        --------
        SolverParameter.SolverType(solver_type, mesh_type)
        """
        self.record_method('SolverType', str(getattr(solver_type, 'value', solver_type)), str(getattr(mesh_type, 'value', mesh_type)))

    def set_ignore_lossy_metals(self, flag: bool = True) -> None:
        """
        VBA Call
        --------
        SolverParameter.IgnoreLossyMetals(flag)
        """
        self.record_method('IgnoreLossyMetals', flag)

    def set_ignore_lossy_dielectrics(self, flag: bool = True) -> None:
        """
        VBA Call
        --------
        SolverParameter.IgnoreLossyDielectrics(flag)
        """
        self.record_method('IgnoreLossyDielectrics', flag)

    def set_ignore_lossy_metals_for_wires(self, flag: bool = True) -> None:
        """
        VBA Call
        --------
        SolverParameter.IgnoreLossyMetalsForWires(flag)
        """
        self.record_method('IgnoreLossyMetalsForWires', flag)

    def set_ignore_nonlinear_materials(self, flag: bool = True) -> None:
        """
        VBA Call
        --------
        SolverParameter.IgnoreNonlinearMaterials(flag)
        """
        self.record_method('IgnoreNonlinearMaterials', flag)

    def set_use_thin_wire_model(self, flag: bool = True) -> None:
        """
        VBA Call
        --------
        SolverParameter.UseThinWireModel(flag)
        """
        self.record_method('UseThinWireModel', flag)

    def set_use_zero_wire_radius(self, flag: bool = True) -> None:
        """
        VBA Call
        --------
        SolverParameter.UseZeroWireRadius(flag)
        """
        self.record_method('UseZeroWireRadius', flag)

