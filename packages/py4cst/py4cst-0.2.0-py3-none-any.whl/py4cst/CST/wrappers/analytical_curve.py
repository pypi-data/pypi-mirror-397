'''This file is auto-generated. Do not edit.'''
from .. import IVBAProvider, VBAObjWrapper

class AnalyticalCurve(VBAObjWrapper):


    def __init__(self, vbap: IVBAProvider) -> None:
        super().__init__(vbap, 'AnalyticalCurve')
        self.set_save_history(False)

    def reset(self) -> None:
        """
        VBA Call
        --------
        AnalyticalCurve.Reset()
        """
        self.cache_method('Reset')

    def set_name(self, analytical_curve_name: str) -> None:
        """
        VBA Call
        --------
        AnalyticalCurve.Name(analytical_curve_name)
        """
        self.cache_method('Name', analytical_curve_name)

    def set_curve(self, curve_name: str) -> None:
        """
        VBA Call
        --------
        AnalyticalCurve.Curve(curve_name)
        """
        self.cache_method('Curve', curve_name)

    def set_law_x(self, law: str) -> None:
        """
        VBA Call
        --------
        AnalyticalCurve.LawX(law)
        """
        self.cache_method('LawX', law)

    def set_law_y(self, law: str) -> None:
        """
        VBA Call
        --------
        AnalyticalCurve.LawY(law)
        """
        self.cache_method('LawY', law)

    def set_law_z(self, law: str) -> None:
        """
        VBA Call
        --------
        AnalyticalCurve.LawZ(law)
        """
        self.cache_method('LawZ', law)

    def set_parameter_range(self, min: float, max: float) -> None:
        """
        VBA Call
        --------
        AnalyticalCurve.ParameterRange(min, max)
        """
        self.cache_method('ParameterRange', min, max)

    def create(self) -> None:
        """
        VBA Call
        --------
        AnalyticalCurve.Create()
        """
        self.cache_method('Create')
        self.flush_cache('Create AnalyticalCurve')

