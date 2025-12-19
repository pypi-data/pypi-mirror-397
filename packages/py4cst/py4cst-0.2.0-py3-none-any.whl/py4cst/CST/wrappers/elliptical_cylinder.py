'''This file is auto-generated. Do not edit.'''
from .. import IVBAProvider, VBAObjWrapper
from enum import Enum
from typing import Union

class ECylinder(VBAObjWrapper):
    class Axis(Enum):
        X = 'x'
        Y = 'y'
        Z = 'z'

    def __init__(self, vbap: IVBAProvider) -> None:
        super().__init__(vbap, 'ECylinder')
        self.set_save_history(False)

    def reset(self) -> None:
        """
        VBA Call
        --------
        ECylinder.Reset()
        """
        self.cache_method('Reset')

    def set_name(self, name: str) -> None:
        """
        VBA Call
        --------
        ECylinder.Name(name)
        """
        self.cache_method('Name', name)

    def set_component(self, component_name: str) -> None:
        """
        VBA Call
        --------
        ECylinder.Component(component_name)
        """
        self.cache_method('Component', component_name)

    def set_material(self, mat_name: str) -> None:
        """
        VBA Call
        --------
        ECylinder.Material(mat_name)
        """
        self.cache_method('Material', mat_name)

    def create(self) -> None:
        """
        VBA Call
        --------
        ECylinder.Create()
        """
        self.cache_method('Create')
        self.flush_cache('Create ECylinder')

    def set_axis(self, axis: Union[Axis, str]) -> None:
        """
        VBA Call
        --------
        ECylinder.Axis(axis)
        """
        self.cache_method('Axis', str(getattr(axis, 'value', axis)))

    def set_x_radius(self, radius: float) -> None:
        """
        VBA Call
        --------
        ECylinder.Xradius(radius)
        """
        self.cache_method('Xradius', radius)

    def set_y_radius(self, radius: float) -> None:
        """
        VBA Call
        --------
        ECylinder.Yradius(radius)
        """
        self.cache_method('Yradius', radius)

    def set_z_radius(self, radius: float) -> None:
        """
        VBA Call
        --------
        ECylinder.Zradius(radius)
        """
        self.cache_method('Zradius', radius)

    def set_x_center(self, center: float) -> None:
        """
        VBA Call
        --------
        ECylinder.Xcenter(center)
        """
        self.cache_method('Xcenter', center)

    def set_y_center(self, center: float) -> None:
        """
        VBA Call
        --------
        ECylinder.Ycenter(center)
        """
        self.cache_method('Ycenter', center)

    def set_z_center(self, center: float) -> None:
        """
        VBA Call
        --------
        ECylinder.Zcenter(center)
        """
        self.cache_method('Zcenter', center)

    def set_x_range(self, x_min: float, x_max: float) -> None:
        """
        VBA Call
        --------
        ECylinder.Xrange(x_min, x_max)
        """
        self.cache_method('Xrange', x_min, x_max)

    def set_y_range(self, y_min: float, y_max: float) -> None:
        """
        VBA Call
        --------
        ECylinder.Yrange(y_min, y_max)
        """
        self.cache_method('Yrange', y_min, y_max)

    def set_z_range(self, z_min: float, z_max: float) -> None:
        """
        VBA Call
        --------
        ECylinder.Zrange(z_min, z_max)
        """
        self.cache_method('Zrange', z_min, z_max)

    def set_num_segments(self, num_segments: int) -> None:
        """
        VBA Call
        --------
        ECylinder.Segments(num_segments)
        """
        self.cache_method('Segments', num_segments)

    def set_smooth_geometry(self) -> None:
        """
        VBA Call
        --------
        ECylinder.Segments(0)
        """
        self.cache_method('Segments', 0)

