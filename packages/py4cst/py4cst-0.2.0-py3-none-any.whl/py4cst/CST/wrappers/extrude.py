'''This file is auto-generated. Do not edit.'''
from .. import IVBAProvider, VBAObjWrapper
from enum import Enum
from typing import Union, Tuple

class Extrude(VBAObjWrapper):
    class Mode(Enum):
        POINT_LIST = 'pointlist'
        PICKS = 'picks'
        MULTIPLE_PICKS = 'multiplepicks'

    def __init__(self, vbap: IVBAProvider) -> None:
        super().__init__(vbap, 'Extrude')
        self.set_save_history(False)

    def reset(self) -> None:
        """
        VBA Call
        --------
        Extrude.Reset()
        """
        self.cache_method('Reset')

    def set_name(self, name: str) -> None:
        """
        VBA Call
        --------
        Extrude.Name(name)
        """
        self.cache_method('Name', name)

    def set_component(self, component_name: str) -> None:
        """
        VBA Call
        --------
        Extrude.Component(component_name)
        """
        self.cache_method('Component', component_name)

    def set_material(self, mat_name: str) -> None:
        """
        VBA Call
        --------
        Extrude.Material(mat_name)
        """
        self.cache_method('Material', mat_name)

    def set_mode(self, mode: Union[Mode, str]) -> None:
        """
        VBA Call
        --------
        Extrude.Mode(mode)
        """
        self.cache_method('Mode', str(getattr(mode, 'value', mode)))

    def set_height(self, height: float) -> None:
        """
        VBA Call
        --------
        Extrude.Height(height)
        """
        self.cache_method('Height', height)

    def set_origin(self, origin: Tuple[float, float, float]) -> None:
        """
        VBA Call
        --------
        Extrude.Origin(origin[0], origin[1], origin[2])
        """
        self.cache_method('Origin', origin[0], origin[1], origin[2])

    def set_u_vector(self, u: Tuple[float, float, float]) -> None:
        """
        VBA Call
        --------
        Extrude.Uvector(u[0], u[1], u[2])
        """
        self.cache_method('Uvector', u[0], u[1], u[2])

    def set_v_vector(self, v: Tuple[float, float, float]) -> None:
        """
        VBA Call
        --------
        Extrude.Vvector(v[0], v[1], v[2])
        """
        self.cache_method('Vvector', v[0], v[1], v[2])

    def set_first_point(self, uv: Tuple[float, float]) -> None:
        """
        VBA Call
        --------
        Extrude.Point(uv[0], uv[1])
        """
        self.cache_method('Point', uv[0], uv[1])

    def add_line_to(self, uv: Tuple[float, float]) -> None:
        """
        VBA Call
        --------
        Extrude.LineTo(uv[0], uv[1])
        """
        self.cache_method('LineTo', uv[0], uv[1])

    def add_line_relative(self, uv: Tuple[float, float]) -> None:
        """
        VBA Call
        --------
        Extrude.RLine(uv[0], uv[1])
        """
        self.cache_method('RLine', uv[0], uv[1])

    def set_taper(self, taper: float) -> None:
        """
        VBA Call
        --------
        Extrude.Taper(taper)
        """
        self.cache_method('Taper', taper)

    def set_twist_deg(self, angle_deg: float) -> None:
        """
        VBA Call
        --------
        Extrude.Twist(angle_deg)
        """
        self.cache_method('Twist', angle_deg)

    def set_use_picks_for_height(self, flag: bool = True) -> None:
        """
        VBA Call
        --------
        Extrude.UsePicksForHeight(flag)
        """
        self.cache_method('UsePicksForHeight', flag)

    def set_pick_height_determined_by_first_face(self, flag: bool = True) -> None:
        """
        VBA Call
        --------
        Extrude.PickHeightDeterminedByFirstFace(flag)
        """
        self.cache_method('PickHeightDeterminedByFirstFace', flag)

    def set_num_picked_faces(self, count: int) -> None:
        """
        VBA Call
        --------
        Extrude.NumberOfPickedFaces(count)
        """
        self.cache_method('NumberOfPickedFaces', count)

    def set_delete_base_face_solid(self, flag: bool = True) -> None:
        """
        VBA Call
        --------
        Extrude.DeleteBaseFaceSolid(flag)
        """
        self.cache_method('DeleteBaseFaceSolid', flag)

    def set_clear_picked_face(self, flag: bool = True) -> None:
        """
        VBA Call
        --------
        Extrude.ClearPickedFace(flag)
        """
        self.cache_method('ClearPickedFace', flag)

    def modify_height(self) -> None:
        """
        VBA Call
        --------
        Extrude.ModifyHeight()
        """
        self.cache_method('ModifyHeight')
        self.flush_cache('ModifyHeight (Extrude)')

    def set_simplify_active(self, flag: bool = True) -> None:
        """
        VBA Call
        --------
        Extrude.SetSimplifyActive(flag)
        """
        self.cache_method('SetSimplifyActive', flag)

    def set_simplify_min_points_arc(self, count: int) -> None:
        """
        VBA Call
        --------
        Extrude.SetSimplifyMinPointsArc(count)
        """
        self.cache_method('SetSimplifyMinPointsArc', count)

    def set_simplify_min_points_circle(self, count: int) -> None:
        """
        VBA Call
        --------
        Extrude.SetSimplifyMinPointsCircle(count)
        """
        self.cache_method('SetSimplifyMinPointsCircle', count)

    def set_simplify_angle_deg(self, angle_deg: float) -> None:
        """
        VBA Call
        --------
        Extrude.SetSimplifyAngle(angle_deg)
        """
        self.cache_method('SetSimplifyAngle', angle_deg)

    def set_simplify_adjacent_tol_deg(self, angle_deg: float) -> None:
        """
        VBA Call
        --------
        Extrude.SetSimplifyAdjacentTol(angle_deg)
        """
        self.cache_method('SetSimplifyAdjacentTol', angle_deg)

    def set_simplify_radius_tol(self, deviation: float) -> None:
        """
        VBA Call
        --------
        Extrude.SetSimplifyRadiusTol(deviation)
        """
        self.cache_method('SetSimplifyRadiusTol', deviation)

    def set_simplify_angle_tang_deg(self, angle_deg: float) -> None:
        """
        VBA Call
        --------
        Extrude.SetSimplifyAngleTang(angle_deg)
        """
        self.cache_method('SetSimplifyAngleTang', angle_deg)

    def set_simplify_edge_length(self, length: float) -> None:
        """
        VBA Call
        --------
        Extrude.SetSimplifyEdgeLength(length)
        """
        self.cache_method('SetSimplifyEdgeLength', length)

    def create(self) -> None:
        """
        VBA Call
        --------
        Extrude.Create()
        """
        self.cache_method('Create')
        self.flush_cache('Create Extrude')

