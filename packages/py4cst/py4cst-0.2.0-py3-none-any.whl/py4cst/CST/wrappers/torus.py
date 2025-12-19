'''This file is auto-generated. Do not edit.'''
from .. import IVBAProvider, VBAObjWrapper
from enum import Enum
from typing import Union

class Torus(VBAObjWrapper):
    class Axis(Enum):
        X = 'x'
        Y = 'y'
        Z = 'z'

    def __init__(self, vbap: IVBAProvider) -> None:
        super().__init__(vbap, 'Torus')
        self.set_save_history(False)

    def reset(self) -> None:
        """
        VBA Call
        --------
        Torus.Reset()
        """
        self.cache_method('Reset')

    def set_name(self, name: str) -> None:
        """
        VBA Call
        --------
        Torus.Name(name)
        """
        self.cache_method('Name', name)

    def set_component(self, component_name: str) -> None:
        """
        VBA Call
        --------
        Torus.Component(component_name)
        """
        self.cache_method('Component', component_name)

    def set_material(self, mat_name: str) -> None:
        """
        VBA Call
        --------
        Torus.Material(mat_name)
        """
        self.cache_method('Material', mat_name)

    def create(self) -> None:
        """
        VBA Call
        --------
        Torus.Create()
        """
        self.cache_method('Create')
        self.flush_cache('Create Torus')

    def set_axis(self, axis: Union[Axis, str]) -> None:
        """
        VBA Call
        --------
        Torus.Axis(axis)
        """
        self.cache_method('Axis', str(getattr(axis, 'value', axis)))

    def set_outer_radius(self, radius: float) -> None:
        """
        VBA Call
        --------
        Torus.Outerradius(radius)
        """
        self.cache_method('Outerradius', radius)

    def set_inner_radius(self, radius: float) -> None:
        """
        VBA Call
        --------
        Torus.Innerradius(radius)
        """
        self.cache_method('Innerradius', radius)

    def set_x_center(self, center: float) -> None:
        """
        VBA Call
        --------
        Torus.Xcenter(center)
        """
        self.cache_method('Xcenter', center)

    def set_y_center(self, center: float) -> None:
        """
        VBA Call
        --------
        Torus.Ycenter(center)
        """
        self.cache_method('Ycenter', center)

    def set_z_center(self, center: float) -> None:
        """
        VBA Call
        --------
        Torus.Zcenter(center)
        """
        self.cache_method('Zcenter', center)

    def set_num_segments(self, num_segments: int) -> None:
        """
        VBA Call
        --------
        Torus.Segments(num_segments)
        """
        self.cache_method('Segments', num_segments)

    def set_smooth_geometry(self) -> None:
        """
        VBA Call
        --------
        Torus.Segments(0)
        """
        self.cache_method('Segments', 0)

