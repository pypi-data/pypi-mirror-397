'''This file is auto-generated. Do not edit.'''
from .. import IVBAProvider, VBAObjWrapper

class Brick(VBAObjWrapper):


    def __init__(self, vbap: IVBAProvider) -> None:
        super().__init__(vbap, 'Brick')
        self.set_save_history(False)

    def reset(self) -> None:
        """
        VBA Call
        --------
        Brick.Reset()
        """
        self.cache_method('Reset')

    def set_name(self, name: str) -> None:
        """
        VBA Call
        --------
        Brick.Name(name)
        """
        self.cache_method('Name', name)

    def set_component(self, component_name: str) -> None:
        """
        VBA Call
        --------
        Brick.Component(component_name)
        """
        self.cache_method('Component', component_name)

    def set_material(self, mat_name: str) -> None:
        """
        VBA Call
        --------
        Brick.Material(mat_name)
        """
        self.cache_method('Material', mat_name)

    def set_x_range(self, x_min: float, x_max: float) -> None:
        """
        VBA Call
        --------
        Brick.Xrange(x_min, x_max)
        """
        self.cache_method('Xrange', x_min, x_max)

    def set_y_range(self, y_min: float, y_max: float) -> None:
        """
        VBA Call
        --------
        Brick.Yrange(y_min, y_max)
        """
        self.cache_method('Yrange', y_min, y_max)

    def set_z_range(self, z_min: float, z_max: float) -> None:
        """
        VBA Call
        --------
        Brick.Zrange(z_min, z_max)
        """
        self.cache_method('Zrange', z_min, z_max)

    def create(self) -> None:
        """
        VBA Call
        --------
        Brick.Create()
        """
        self.cache_method('Create')
        self.flush_cache('Create Brick')

