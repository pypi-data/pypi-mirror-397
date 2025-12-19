'''This file is auto-generated. Do not edit.'''
from .. import IVBAProvider, VBAObjWrapper
from enum import Enum
from typing import Union

class Cone(VBAObjWrapper):
    class Axis(Enum):
        X = 'x'
        Y = 'y'
        Z = 'z'

    def __init__(self, vbap: IVBAProvider) -> None:
        super().__init__(vbap, 'Cone')
        self.set_save_history(False)

    def reset(self) -> None:
        """
        VBA Call
        --------
        Cone.Reset()
        """
        self.cache_method('Reset')

    def set_name(self, name: str) -> None:
        """
        VBA Call
        --------
        Cone.Name(name)
        """
        self.cache_method('Name', name)

    def set_component(self, component_name: str) -> None:
        """
        VBA Call
        --------
        Cone.Component(component_name)
        """
        self.cache_method('Component', component_name)

    def set_material(self, mat_name: str) -> None:
        """
        VBA Call
        --------
        Cone.Material(mat_name)
        """
        self.cache_method('Material', mat_name)

    def create(self) -> None:
        """
        VBA Call
        --------
        Cone.Create()
        """
        self.cache_method('Create')
        self.flush_cache('Create Cone')

    def set_axis(self, axis: Union[Axis, str]) -> None:
        """
        VBA Call
        --------
        Cone.Axis(axis)
        """
        self.cache_method('Axis', str(getattr(axis, 'value', axis)))

    def set_top_radius(self, radius: float) -> None:
        """
        VBA Call
        --------
        Cone.Topradius(radius)
        """
        self.cache_method('Topradius', radius)

    def set_bottom_radius(self, radius: float) -> None:
        """
        VBA Call
        --------
        Cone.Bottomradius(radius)
        """
        self.cache_method('Bottomradius', radius)

    def set_x_center(self, center: float) -> None:
        """
        VBA Call
        --------
        Cone.Xcenter(center)
        """
        self.cache_method('Xcenter', center)

    def set_y_center(self, center: float) -> None:
        """
        VBA Call
        --------
        Cone.Ycenter(center)
        """
        self.cache_method('Ycenter', center)

    def set_z_center(self, center: float) -> None:
        """
        VBA Call
        --------
        Cone.Zcenter(center)
        """
        self.cache_method('Zcenter', center)

    def set_x_range(self, x_min: float, x_max: float) -> None:
        """
        VBA Call
        --------
        Cone.Xrange(x_min, x_max)
        """
        self.cache_method('Xrange', x_min, x_max)

    def set_y_range(self, y_min: float, y_max: float) -> None:
        """
        VBA Call
        --------
        Cone.Yrange(y_min, y_max)
        """
        self.cache_method('Yrange', y_min, y_max)

    def set_z_range(self, z_min: float, z_max: float) -> None:
        """
        VBA Call
        --------
        Cone.Zrange(z_min, z_max)
        """
        self.cache_method('Zrange', z_min, z_max)

    def set_num_segments(self, num_segments: int) -> None:
        """
        VBA Call
        --------
        Cone.Segments(num_segments)
        """
        self.cache_method('Segments', num_segments)

    def set_smooth_geometry(self) -> None:
        """
        VBA Call
        --------
        Cone.Segments(0)
        """
        self.cache_method('Segments', 0)

