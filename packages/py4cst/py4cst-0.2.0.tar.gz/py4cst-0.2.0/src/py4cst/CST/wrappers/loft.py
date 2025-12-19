'''This file is auto-generated. Do not edit.'''
from .. import IVBAProvider, VBAObjWrapper

class Loft(VBAObjWrapper):


    def __init__(self, vbap: IVBAProvider) -> None:
        super().__init__(vbap, 'Loft')
        self.set_save_history(False)

    def reset(self) -> None:
        """
        VBA Call
        --------
        Loft.Reset()
        """
        self.cache_method('Reset')

    def set_name(self, name: str) -> None:
        """
        VBA Call
        --------
        Loft.Name(name)
        """
        self.cache_method('Name', name)

    def set_component(self, component_name: str) -> None:
        """
        VBA Call
        --------
        Loft.Component(component_name)
        """
        self.cache_method('Component', component_name)

    def set_material(self, mat_name: str) -> None:
        """
        VBA Call
        --------
        Loft.Material(mat_name)
        """
        self.cache_method('Material', mat_name)

    def set_tangency(self, tang: float) -> None:
        """
        VBA Call
        --------
        Loft.Tangency(tang)
        """
        self.cache_method('Tangency', tang)

    def create(self) -> None:
        """
        VBA Call
        --------
        Loft.CreateNew()
        """
        self.cache_method('CreateNew')

