'''This file is auto-generated. Do not edit.'''
from .. import IVBAProvider, VBAObjWrapper
from enum import Enum
from typing import Union

class Arc(VBAObjWrapper):
    class Orientation(Enum):
        CLOCKWISE = 'Clockwise'
        COUNTER_CLOCKWISE = 'CounterClockwise'

    def __init__(self, vbap: IVBAProvider) -> None:
        super().__init__(vbap, 'Arc')
        self.set_save_history(False)

    def reset(self) -> None:
        """
        VBA Call
        --------
        Arc.Reset()
        """
        self.cache_method('Reset')

    def set_name(self, arc_name: str) -> None:
        """
        VBA Call
        --------
        Arc.Name(arc_name)
        """
        self.cache_method('Name', arc_name)

    def set_curve(self, curve_name: str) -> None:
        """
        VBA Call
        --------
        Arc.Curve(curve_name)
        """
        self.cache_method('Curve', curve_name)

    def set_orientation(self, orientation: Union[Orientation, str]) -> None:
        """
        VBA Call
        --------
        Arc.Orientation(orientation)
        """
        self.cache_method('Orientation', str(getattr(orientation, 'value', orientation)))

    def set_center_x(self, x: float) -> None:
        """
        VBA Call
        --------
        Arc.Xcenter(x)
        """
        self.cache_method('Xcenter', x)

    def set_center_y(self, y: float) -> None:
        """
        VBA Call
        --------
        Arc.Ycenter(y)
        """
        self.cache_method('Ycenter', y)

    def set_start_point_x(self, x: float) -> None:
        """
        VBA Call
        --------
        Arc.X1(x)
        """
        self.cache_method('X1', x)

    def set_start_point_y(self, y: float) -> None:
        """
        VBA Call
        --------
        Arc.Y1(y)
        """
        self.cache_method('Y1', y)

    def set_end_point_x(self, x: float) -> None:
        """
        VBA Call
        --------
        Arc.X2(x)
        """
        self.cache_method('X2', x)

    def set_end_point_y(self, y: float) -> None:
        """
        VBA Call
        --------
        Arc.Y2(y)
        """
        self.cache_method('Y2', y)

    def set_angle_deg(self, angle_deg: float) -> None:
        """
        VBA Call
        --------
        Arc.Angle(angle_deg)
        """
        self.cache_method('Angle', angle_deg)

    def set_use_angle(self, flag: bool = True) -> None:
        """
        VBA Call
        --------
        Arc.UseAngle(flag)
        """
        self.cache_method('UseAngle', flag)

    def set_number_of_segments(self, num: int) -> None:
        """
        VBA Call
        --------
        Arc.Segments(num)
        """
        self.cache_method('Segments', num)

    def set_infinite_number_of_segments(self) -> None:
        """
        VBA Call
        --------
        Arc.Segments(0)
        """
        self.cache_method('Segments', 0)

    def create(self) -> None:
        """
        VBA Call
        --------
        Arc.Create()
        """
        self.cache_method('Create')
        self.flush_cache('Create Arc')

