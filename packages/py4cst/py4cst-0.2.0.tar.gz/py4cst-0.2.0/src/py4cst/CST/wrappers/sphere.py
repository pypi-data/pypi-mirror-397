'''This file is auto-generated. Do not edit.'''
from .. import IVBAProvider, VBAObjWrapper
from enum import Enum
from typing import Union, Tuple

class Sphere(VBAObjWrapper):
    class Axis(Enum):
        X = 'x'
        Y = 'y'
        Z = 'z'

    def __init__(self, vbap: IVBAProvider) -> None:
        super().__init__(vbap, 'Sphere')
        self.set_save_history(False)

    def reset(self) -> None:
        """
        VBA Call
        --------
        Sphere.Reset()
        """
        self.cache_method('Reset')

    def set_name(self, name: str) -> None:
        """
        VBA Call
        --------
        Sphere.Name(name)
        """
        self.cache_method('Name', name)

    def set_component(self, component_name: str) -> None:
        """
        VBA Call
        --------
        Sphere.Component(component_name)
        """
        self.cache_method('Component', component_name)

    def set_material(self, mat_name: str) -> None:
        """
        VBA Call
        --------
        Sphere.Material(mat_name)
        """
        self.cache_method('Material', mat_name)

    def create(self) -> None:
        """
        VBA Call
        --------
        Sphere.Create()
        """
        self.cache_method('Create')
        self.flush_cache('Create Sphere')

    def set_axis(self, axis: Union[Axis, str]) -> None:
        """
        VBA Call
        --------
        Sphere.Axis(axis)
        """
        self.cache_method('Axis', str(getattr(axis, 'value', axis)))

    def set_center_radius(self, radius: float) -> None:
        """
        VBA Call
        --------
        Sphere.CenterRadius(radius)
        """
        self.cache_method('CenterRadius', radius)

    def set_top_radius(self, radius: float) -> None:
        """
        VBA Call
        --------
        Sphere.TopRadius(radius)
        """
        self.cache_method('TopRadius', radius)

    def set_bottom_radius(self, radius: float) -> None:
        """
        VBA Call
        --------
        Sphere.BottomRadius(radius)
        """
        self.cache_method('BottomRadius', radius)

    def set_center(self, coords: Tuple[float, float, float]) -> None:
        """
        VBA Call
        --------
        Sphere.Center(coords[0], coords[1], coords[2])
        """
        self.cache_method('Center', coords[0], coords[1], coords[2])

    def set_num_segments(self, num_segments: int) -> None:
        """
        VBA Call
        --------
        Sphere.Segments(num_segments)
        """
        self.cache_method('Segments', num_segments)

    def set_smooth_geometry(self) -> None:
        """
        VBA Call
        --------
        Sphere.Segments(0)
        """
        self.cache_method('Segments', 0)

