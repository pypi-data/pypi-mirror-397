'''This file is auto-generated. Do not edit.'''
from .. import IVBAProvider, VBAObjWrapper
from enum import Enum
from typing import Union

class Background(VBAObjWrapper):
    class MaterialType(Enum):
        NORMAL = 'normal'
        PEC = 'pec'

    class ThermalType(Enum):
        NORMAL = 'normal'
        PTC = 'ptc'

    def __init__(self, vbap: IVBAProvider) -> None:
        super().__init__(vbap, 'Background')
        self.set_save_history(False)

    def reset(self) -> None:
        """
        VBA Call
        --------
        Background.Reset()
        """
        self.record_method('Reset')

    def set_type(self, material_type: Union[MaterialType, str]) -> None:
        """
        VBA Call
        --------
        Background.Type(material_type)
        """
        self.record_method('Type', str(getattr(material_type, 'value', material_type)))

    def set_permitivity(self, epsilon: float) -> None:
        """
        VBA Call
        --------
        Background.Epsilon(epsilon)
        """
        self.record_method('Epsilon', epsilon)

    def set_permeability(self, mu: float) -> None:
        """
        VBA Call
        --------
        Background.Mu(mu)
        """
        self.record_method('Mu', mu)

    def set_conductivity(self, sigma: float) -> None:
        """
        VBA Call
        --------
        Background.ElConductivity(sigma)
        """
        self.record_method('ElConductivity', sigma)

    def set_space_x_min(self, value: float) -> None:
        """
        VBA Call
        --------
        Background.XminSpace(value)
        """
        self.record_method('XminSpace', value)

    def set_space_x_max(self, value: float) -> None:
        """
        VBA Call
        --------
        Background.XmaxSpace(value)
        """
        self.record_method('XmaxSpace', value)

    def set_space_y_min(self, value: float) -> None:
        """
        VBA Call
        --------
        Background.YminSpace(value)
        """
        self.record_method('YminSpace', value)

    def set_space_y_max(self, value: float) -> None:
        """
        VBA Call
        --------
        Background.YmaxSpace(value)
        """
        self.record_method('YmaxSpace', value)

    def set_space_z_min(self, value: float) -> None:
        """
        VBA Call
        --------
        Background.ZminSpace(value)
        """
        self.record_method('ZminSpace', value)

    def set_space_z_max(self, value: float) -> None:
        """
        VBA Call
        --------
        Background.ZmaxSpace(value)
        """
        self.record_method('ZmaxSpace', value)

    def set_thermal_type(self, thermal_type: Union[ThermalType, str]) -> None:
        """
        VBA Call
        --------
        Background.ThermalType(thermal_type)
        """
        self.record_method('ThermalType', str(getattr(thermal_type, 'value', thermal_type)))

    def set_thermal_conductivity(self, value: float) -> None:
        """
        VBA Call
        --------
        Background.ThermalConductivity(value)
        """
        self.record_method('ThermalConductivity', value)

    def set_apply_in_all_directions(self, flag: bool = True) -> None:
        """
        VBA Call
        --------
        Background.ApplyInAllDirections(flag)
        """
        self.record_method('ApplyInAllDirections', flag)

