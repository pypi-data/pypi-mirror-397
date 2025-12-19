'''This file is auto-generated. Do not edit.'''
from .. import IVBAProvider, VBAObjWrapper
from enum import Enum
from typing import Union

class TraceFromCurve(VBAObjWrapper):
    class GapType(Enum):
        ROUNDED = 0
        EXTENDED = 1
        NATURAL = 2

    def __init__(self, vbap: IVBAProvider) -> None:
        super().__init__(vbap, 'TraceFromCurve')
        self.set_save_history(False)

    def reset(self) -> None:
        """
        VBA Call
        --------
        TraceFromCurve.Reset()
        """
        self.cache_method('Reset')

    def set_name(self, name: str) -> None:
        """
        VBA Call
        --------
        TraceFromCurve.Name(name)
        """
        self.cache_method('Name', name)

    def set_component(self, component_name: str) -> None:
        """
        VBA Call
        --------
        TraceFromCurve.Component(component_name)
        """
        self.cache_method('Component', component_name)

    def set_material(self, mat_name: str) -> None:
        """
        VBA Call
        --------
        TraceFromCurve.Material(mat_name)
        """
        self.cache_method('Material', mat_name)

    def set_curve(self, curve_name: str) -> None:
        """
        VBA Call
        --------
        TraceFromCurve.Curve(curve_name)
        """
        self.cache_method('Curve', curve_name)

    def set_thickness(self, thickness: float) -> None:
        """
        VBA Call
        --------
        TraceFromCurve.Thickness(thickness)
        """
        self.cache_method('Thickness', thickness)

    def set_width(self, width: float) -> None:
        """
        VBA Call
        --------
        TraceFromCurve.Width(width)
        """
        self.cache_method('Width', width)

    def set_start_round(self, flag: bool = True) -> None:
        """
        VBA Call
        --------
        TraceFromCurve.RoundStart(flag)
        """
        self.cache_method('RoundStart', flag)

    def set_end_round(self, flag: bool = True) -> None:
        """
        VBA Call
        --------
        TraceFromCurve.RoundEnd(flag)
        """
        self.cache_method('RoundEnd', flag)

    def set_gap_type(self, gap_type: Union[GapType, int]) -> None:
        """
        VBA Call
        --------
        TraceFromCurve.GapType(gap_type)
        """
        self.cache_method('GapType', int(getattr(gap_type, 'value', gap_type)))

    def create(self) -> None:
        """
        VBA Call
        --------
        TraceFromCurve.Create()
        """
        self.cache_method('Create')
        self.flush_cache('Create TraceFromCurve')

