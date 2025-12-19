'''This file is auto-generated. Do not edit.'''
from .. import IVBAProvider, VBAObjWrapper

class AnalyticalFace(VBAObjWrapper):


    def __init__(self, vbap: IVBAProvider) -> None:
        super().__init__(vbap, 'AnalyticalFace')
        self.set_save_history(False)

    def reset(self) -> None:
        """
        VBA Call
        --------
        AnalyticalFace.Reset()
        """
        self.cache_method('Reset')

    def set_name(self, name: str) -> None:
        """
        VBA Call
        --------
        AnalyticalFace.Name(name)
        """
        self.cache_method('Name', name)

    def set_component(self, component_name: str) -> None:
        """
        VBA Call
        --------
        AnalyticalFace.Component(component_name)
        """
        self.cache_method('Component', component_name)

    def set_material(self, mat_name: str) -> None:
        """
        VBA Call
        --------
        AnalyticalFace.Material(mat_name)
        """
        self.cache_method('Material', mat_name)

    def set_law_x(self, expr: str) -> None:
        """
        VBA Call
        --------
        AnalyticalFace.LawX(expr)
        """
        self.cache_method('LawX', expr)

    def set_law_y(self, expr: str) -> None:
        """
        VBA Call
        --------
        AnalyticalFace.LawY(expr)
        """
        self.cache_method('LawY', expr)

    def set_law_z(self, expr: str) -> None:
        """
        VBA Call
        --------
        AnalyticalFace.LawZ(expr)
        """
        self.cache_method('LawZ', expr)

    def set_param_range_u(self, u_min: float, u_max: float) -> None:
        """
        VBA Call
        --------
        AnalyticalFace.ParameterRangeU(u_min, u_max)
        """
        self.cache_method('ParameterRangeU', u_min, u_max)

    def set_param_range_v(self, v_min: float, v_max: float) -> None:
        """
        VBA Call
        --------
        AnalyticalFace.ParameterRangeV(v_min, v_max)
        """
        self.cache_method('ParameterRangeV', v_min, v_max)

    def create(self) -> None:
        """
        VBA Call
        --------
        AnalyticalFace.Create()
        """
        self.cache_method('Create')
        self.flush_cache('Create AnalyticalFace')

