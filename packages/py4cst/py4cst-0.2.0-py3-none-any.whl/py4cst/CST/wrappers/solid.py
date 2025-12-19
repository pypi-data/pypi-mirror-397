'''This file is auto-generated. Do not edit.'''
from .. import IVBAProvider, VBAObjWrapper
from enum import Enum
from typing import Union, Tuple

class Solid(VBAObjWrapper):
    class Key(Enum):
        INSIDE = 'Inside'
        OUTSIDE = 'Outside'
        CENTERED = 'Centered'

    class MeshApproximation(Enum):
        PBA = 'PBA'
        STAIRCASE = 'Staircase'

    def __init__(self, vbap: IVBAProvider) -> None:
        super().__init__(vbap, 'Solid')
        self.set_save_history(False)

    def delete(self, solid_name: str) -> None:
        """
        VBA Call
        --------
        Solid.Delete(solid_name)
        """
        self.record_method('Delete', solid_name)

    def rename(self, old_name: str, new_name: str) -> None:
        """
        VBA Call
        --------
        Solid.Rename(old_name, new_name)
        """
        self.record_method('Rename', old_name, new_name)

    def change_component(self, solid_name: str, component_name: str) -> None:
        """
        VBA Call
        --------
        Solid.ChangeComponent(solid_name, component_name)
        """
        self.record_method('ChangeComponent', solid_name, component_name)

    def change_material(self, solid_name: str, material_name: str) -> None:
        """
        VBA Call
        --------
        Solid.ChangeMaterial(solid_name, material_name)
        """
        self.record_method('ChangeMaterial', solid_name, material_name)

    def set_use_individual_color(self, flag: bool = True) -> None:
        """
        VBA Call
        --------
        Solid.SetUseIndividualColor(flag)
        """
        self.record_method('SetUseIndividualColor', flag)

    def change_individual_color(self, solid_name: str, rgb: Tuple[float, float, float]) -> None:
        """
        VBA Call
        --------
        Solid.ChangeIndividualColor(solid_name, rgb[0], rgb[1], rgb[2])
        """
        self.record_method('ChangeIndividualColor', solid_name, rgb[0], rgb[1], rgb[2])

    def set_fast_model_update(self, flag: bool = True) -> None:
        """
        VBA Call
        --------
        Solid.FastModelUpdate(flag)
        """
        self.record_method('FastModelUpdate', flag)

    def perform_add_operation(self, solid1_name: str, solid2_name: str) -> None:
        """
        VBA Call
        --------
        Solid.Add(solid1_name, solid2_name)
        """
        self.record_method('Add', solid1_name, solid2_name)

    def perform_insert_operation(self, solid1_name: str, solid2_name: str) -> None:
        """
        VBA Call
        --------
        Solid.Insert(solid1_name, solid2_name)

        Description
        --------
        Insert solid2 into solid1.
        """
        self.record_method('Insert', solid1_name, solid2_name)

    def perform_intersect_operation(self, solid1_name: str, solid2_name: str) -> None:
        """
        VBA Call
        --------
        Solid.Intersect(solid1_name, solid2_name)
        """
        self.record_method('Intersect', solid1_name, solid2_name)

    def perform_subtract_operation(self, solid1_name: str, solid2_name: str) -> None:
        """
        VBA Call
        --------
        Solid.Subtract(solid1_name, solid2_name)

        Description
        --------
        Subtract solid2 from solid1.
        """
        self.record_method('Subtract', solid1_name, solid2_name)

    def merge_materials_of_component(self, component_or_solid_name: str) -> None:
        """
        VBA Call
        --------
        Solid.MergeMaterialsOfComponent(component_or_solid_name)
        """
        self.record_method('MergeMaterialsOfComponent', component_or_solid_name)

    def set_shape_visualization_accuracy2(self, acc: int) -> None:
        """
        VBA Call
        --------
        Solid.ShapeVisualizationAccuracy2(acc)
        """
        self.record_method('ShapeVisualizationAccuracy2', acc)

    def set_shape_visualization_offset(self, offset: int) -> None:
        """
        VBA Call
        --------
        Solid.ShapeVisualizationOffset(offset)
        """
        self.record_method('ShapeVisualizationOffset', offset)

    def attach_active_wcs(self, solid_name: str) -> None:
        """
        VBA Call
        --------
        Solid.AttachActiveWCS(solid_name)
        """
        self.record_method('AttachActiveWCS', solid_name)

    def blend_edge(self, radius: float) -> None:
        """
        VBA Call
        --------
        Solid.BlendEdge(radius)
        """
        self.record_method('BlendEdge', radius)

    def chamfer_edge1_deg(self, depth: float, angle_deg: float, face_id: int) -> None:
        """
        VBA Call
        --------
        Solid.ChamferEdge(depth, angle_deg, False, face_id)
        """
        self.record_method('ChamferEdge', depth, angle_deg, False, face_id)

    def chamfer_edge2_deg(self, depth: float, angle_deg: float, face_id: int) -> None:
        """
        VBA Call
        --------
        Solid.ChamferEdge(depth, angle_deg, True, face_id)
        """
        self.record_method('ChamferEdge', depth, angle_deg, True, face_id)

    def slice_shape(self, solid_name: str, component_name: str) -> None:
        """
        VBA Call
        --------
        Solid.SliceShape(solid_name, component_name)
        """
        self.record_method('SliceShape', solid_name, component_name)

    def split_shape(self, solid_name: str, component_name: str) -> None:
        """
        VBA Call
        --------
        Solid.SplitShape(solid_name, component_name)
        """
        self.record_method('SplitShape', solid_name, component_name)

    def thicken_sheet_advanced(self, solid_name: str, key: Union[Key, str], thickness: float, clear_picks: bool = False) -> None:
        """
        VBA Call
        --------
        Solid.ThickenSheetAdvanced(solid_name, key, thickness, clear_picks)
        """
        self.record_method('ThickenSheetAdvanced', solid_name, str(getattr(key, 'value', key)), thickness, clear_picks)

    def shell_advanced(self, solid_name: str, key: Union[Key, str], thickness: float, clear_picks: bool = False) -> None:
        """
        VBA Call
        --------
        Solid.ShellAdvanced(solid_name, key, thickness, clear_picks)
        """
        self.record_method('ShellAdvanced', solid_name, str(getattr(key, 'value', key)), thickness, clear_picks)

    def fillup_space_advanced(self, solid_name: str, component_name: str, material_name: str) -> None:
        """
        VBA Call
        --------
        Solid.FillupSpaceAdvanced(solid_name, component_name, material_name)
        """
        self.record_method('FillupSpaceAdvanced', solid_name, component_name, material_name)

    def move_selected_face(self, delta: Tuple[float, float, float]) -> None:
        """
        VBA Call
        --------
        Solid.MoveSelectedFace(delta[0], delta[1], delta[2])
        """
        self.record_method('MoveSelectedFace', delta[0], delta[1], delta[2])

    def move_selected_planar_face(self, offset: float) -> None:
        """
        VBA Call
        --------
        Solid.MoveSelectedPlanarFace(offset)
        """
        self.record_method('MoveSelectedPlanarFace', offset)

    def offset_selected_faces(self, offset: float) -> None:
        """
        VBA Call
        --------
        Solid.OffsetSelectedFaces(offset)
        """
        self.record_method('OffsetSelectedFaces', offset)

    def remove_selected_faces(self) -> None:
        """
        VBA Call
        --------
        Solid.RemoveSelectedFaces()
        """
        self.record_method('RemoveSelectedFaces')

    def set_selected_face_radius(self, radius: float) -> None:
        """
        VBA Call
        --------
        Solid.SelectedFaceRadius(radius)
        """
        self.record_method('SelectedFaceRadius', radius)

    def set_mesh_step_width(self, solid_name: str, delta: Tuple[float, float, float]) -> None:
        """
        VBA Call
        --------
        Solid.SetMeshStepWidth(solid_name, delta[0], delta[1], delta[2])
        """
        self.record_method('SetMeshStepWidth', solid_name, delta[0], delta[1], delta[2])

    def set_mesh_extend_width(self, solid_name: str, delta: Tuple[float, float, float]) -> None:
        """
        VBA Call
        --------
        Solid.SetMeshExtendwidth(solid_name, delta[0], delta[1], delta[2])
        """
        self.record_method('SetMeshExtendwidth', solid_name, delta[0], delta[1], delta[2])

    def set_automesh_fixpoints(self, solid_name: str, flag: bool = True) -> None:
        """
        VBA Call
        --------
        Solid.SetAutomeshFixpoints(solid_name, flag)
        """
        self.record_method('SetAutomeshFixpoints', solid_name, flag)

    def set_material_based_refinement(self, solid_name: str, flag: bool = True) -> None:
        """
        VBA Call
        --------
        Solid.SetMaterialBasedRefinement(solid_name, flag)
        """
        self.record_method('SetMaterialBasedRefinement', solid_name, flag)

    def set_mesh_properties(self, solid_name: str, approx: Union[MeshApproximation, str], default_type: bool = False) -> None:
        """
        VBA Call
        --------
        Solid.SetMeshProperties(solid_name, approx, default_type)
        """
        self.record_method('SetMeshProperties', solid_name, str(getattr(approx, 'value', approx)), default_type)

    def set_use_for_simulation(self, solid_name: str, flag: bool = True) -> None:
        """
        VBA Call
        --------
        Solid.SetUseForSimulation(solid_name, flag)
        """
        self.record_method('SetUseForSimulation', solid_name, flag)

    def set_use_thin_sheet_mesh_for_shape(self, solid_name: str, flag: bool = True) -> None:
        """
        VBA Call
        --------
        Solid.SetUseThinSheetMeshForShape(solid_name, flag)
        """
        self.record_method('SetUseThinSheetMeshForShape', solid_name, flag)

    def set_mesh_refinement(self, solid_name: str, edge_refinement: bool, edge_refinement_factor: float, volume_refinement: bool, volume_refinement_factor: float) -> None:
        """
        VBA Call
        --------
        Solid.SetMeshRefinement(solid_name, edge_refinement, edge_refinement_factor, volume_refinement, volume_refinement_factor)
        """
        self.record_method('SetMeshRefinement', solid_name, edge_refinement, edge_refinement_factor, volume_refinement, volume_refinement_factor)

