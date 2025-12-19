'''This file is auto-generated. Do not edit.'''
from .. import IVBAProvider, VBAObjWrapper
from enum import Enum
from typing import Union, Tuple

class Rotate(VBAObjWrapper):
    class Mode(Enum):
        POINTLIST = 'pointlist'
        PICKS = 'picks'

    def __init__(self, vbap: IVBAProvider) -> None:
        super().__init__(vbap, 'Rotate')
        self.set_save_history(False)

    def reset(self) -> None:
        """
        VBA Call
        --------
        Rotate.Reset()
        """
        self.cache_method('Reset')

    def set_name(self, name: str) -> None:
        """
        VBA Call
        --------
        Rotate.Name(name)
        """
        self.cache_method('Name', name)

    def set_component(self, component_name: str) -> None:
        """
        VBA Call
        --------
        Rotate.Component(component_name)
        """
        self.cache_method('Component', component_name)

    def set_material(self, mat_name: str) -> None:
        """
        VBA Call
        --------
        Rotate.Material(mat_name)
        """
        self.cache_method('Material', mat_name)

    def set_mode(self, mode: Union[Mode, str]) -> None:
        """
        VBA Call
        --------
        Rotate.Mode(mode)
        """
        self.cache_method('Mode', str(getattr(mode, 'value', mode)))

    def set_start_angle_deg(self, angle_deg: float) -> None:
        """
        VBA Call
        --------
        Rotate.StartAngle(angle_deg)
        """
        self.cache_method('StartAngle', angle_deg)

    def set_angle_deg(self, angle_deg: float) -> None:
        """
        VBA Call
        --------
        Rotate.Angle(angle_deg)
        """
        self.cache_method('Angle', angle_deg)

    def set_height(self, height: float) -> None:
        """
        VBA Call
        --------
        Rotate.Height(height)
        """
        self.cache_method('Height', height)

    def set_origin(self, coords: Tuple[float, float, float]) -> None:
        """
        VBA Call
        --------
        Rotate.Origin(coords[0], coords[1], coords[2])
        """
        self.cache_method('Origin', coords[0], coords[1], coords[2])

    def set_r_vector(self, uvw: Tuple[float, float, float]) -> None:
        """
        VBA Call
        --------
        Rotate.Rvector(uvw[0], uvw[1], uvw[2])
        """
        self.cache_method('Rvector', uvw[0], uvw[1], uvw[2])

    def set_z_vector(self, uvw: Tuple[float, float, float]) -> None:
        """
        VBA Call
        --------
        Rotate.Zvector(uvw[0], uvw[1], uvw[2])
        """
        self.cache_method('Zvector', uvw[0], uvw[1], uvw[2])

    def set_first_point(self, uv: Tuple[float, float]) -> None:
        """
        VBA Call
        --------
        Rotate.Point(uv[0], uv[1])
        """
        self.cache_method('Point', uv[0], uv[1])

    def add_line_to(self, uv: Tuple[float, float]) -> None:
        """
        VBA Call
        --------
        Rotate.LineTo(uv[0], uv[1])
        """
        self.cache_method('LineTo', uv[0], uv[1])

    def add_line_relative(self, uv: Tuple[float, float]) -> None:
        """
        VBA Call
        --------
        Rotate.RLine(uv[0], uv[1])
        """
        self.cache_method('RLine', uv[0], uv[1])

    def set_radius_ratio(self, ratio: float) -> None:
        """
        VBA Call
        --------
        Rotate.RadiusRatio(ratio)
        """
        self.cache_method('RadiusRatio', ratio)

    def modify_angle(self) -> None:
        """
        VBA Call
        --------
        Rotate.ModifyAngle()
        """
        self.cache_method('ModifyAngle')
        self.flush_cache('ModifyAngle (Port)')

    def set_num_steps(self, count: int) -> None:
        """
        VBA Call
        --------
        Rotate.NSteps(count)
        """
        self.cache_method('NSteps', count)

    def set_split_closed_edges(self, flag: bool = True) -> None:
        """
        VBA Call
        --------
        Rotate.SplitClosedEdges(flag)
        """
        self.cache_method('SplitClosedEdges', flag)

    def set_segmented_profile(self, flag: bool = True) -> None:
        """
        VBA Call
        --------
        Rotate.SegmentedProfile(flag)
        """
        self.cache_method('SegmentedProfile', flag)

    def set_delete_base_face_solid(self, flag: bool = True) -> None:
        """
        VBA Call
        --------
        Rotate.DeleteBaseFaceSolid(flag)
        """
        self.cache_method('DeleteBaseFaceSolid', flag)

    def set_clear_picked_face(self, flag: bool = True) -> None:
        """
        VBA Call
        --------
        Rotate.ClearPickedFace(flag)
        """
        self.cache_method('ClearPickedFace', flag)

    def set_simplify_solid(self, flag: bool = True) -> None:
        """
        VBA Call
        --------
        Rotate.SimplifySolid(flag)
        """
        self.cache_method('SimplifySolid', flag)

    def set_use_advanced_segmented_rotation(self, flag: bool = True) -> None:
        """
        VBA Call
        --------
        Rotate.UseAdvancedSegmentedRotation(flag)
        """
        self.cache_method('UseAdvancedSegmentedRotation', flag)

    def set_simplify_active(self, flag: bool = True) -> None:
        """
        VBA Call
        --------
        Rotate.SetSimplifyActive(flag)
        """
        self.cache_method('SetSimplifyActive', flag)

    def set_simplify_min_points_arc(self, count: int) -> None:
        """
        VBA Call
        --------
        Rotate.SetSimplifyMinPointsArc(count)
        """
        self.cache_method('SetSimplifyMinPointsArc', count)

    def set_simplify_min_points_circle(self, count: int) -> None:
        """
        VBA Call
        --------
        Rotate.SetSimplifyMinPointsCircle(count)
        """
        self.cache_method('SetSimplifyMinPointsCircle', count)

    def set_simplify_angle_deg(self, angle_deg: float) -> None:
        """
        VBA Call
        --------
        Rotate.SetSimplifyAngle(angle_deg)
        """
        self.cache_method('SetSimplifyAngle', angle_deg)

    def set_simplify_adjacent_tol_deg(self, angle_deg: float) -> None:
        """
        VBA Call
        --------
        Rotate.SetSimplifyAdjacentTol(angle_deg)
        """
        self.cache_method('SetSimplifyAdjacentTol', angle_deg)

    def set_simplify_radius_tol(self, deviation: float) -> None:
        """
        VBA Call
        --------
        Rotate.SetSimplifyRadiusTol(deviation)
        """
        self.cache_method('SetSimplifyRadiusTol', deviation)

    def set_simplify_angle_tang_deg(self, angle_deg: float) -> None:
        """
        VBA Call
        --------
        Rotate.SetSimplifyAngleTang(angle_deg)
        """
        self.cache_method('SetSimplifyAngleTang', angle_deg)

    def set_simplify_edge_length(self, length: float) -> None:
        """
        VBA Call
        --------
        Rotate.SetSimplifyEdgeLength(length)
        """
        self.cache_method('SetSimplifyEdgeLength', length)

    def create(self) -> None:
        """
        VBA Call
        --------
        Rotate.Create()
        """
        self.cache_method('Create')
        self.flush_cache('Create Rotate')

