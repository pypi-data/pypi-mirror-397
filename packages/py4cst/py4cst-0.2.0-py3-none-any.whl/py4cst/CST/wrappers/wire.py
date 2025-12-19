'''This file is auto-generated. Do not edit.'''
from .. import IVBAProvider, VBAObjWrapper
from enum import Enum
from typing import Union, Tuple

class Wire(VBAObjWrapper):
    class Type(Enum):
        BOND_WIRE = 'Bondwire'
        CURVE_WIRE = 'Curvewire'

    class BondWireType(Enum):
        SPLINE = 'Spline'
        JEDEC_4 = 'JEDEC4'
        JEDEC_5 = 'JEDEC5'

    class Termination(Enum):
        NATURAL = 'natural'
        ROUNDED = 'rounded'
        EXTENDED = 'extended'

    def __init__(self, vbap: IVBAProvider) -> None:
        super().__init__(vbap, 'Wire')
        self.set_save_history(False)

    def reset(self) -> None:
        """
        VBA Call
        --------
        Wire.Reset()
        """
        self.cache_method('Reset')

    def set_name(self, name: str) -> None:
        """
        VBA Call
        --------
        Wire.Name(name)
        """
        self.cache_method('Name', name)

    def set_folder_name(self, folder_name: str) -> None:
        """
        VBA Call
        --------
        Wire.Folder(folder_name)
        """
        self.cache_method('Folder', folder_name)

    def set_type(self, wire_type: Union[Type, str]) -> None:
        """
        VBA Call
        --------
        Wire.Type(wire_type)
        """
        self.cache_method('Type', str(getattr(wire_type, 'value', wire_type)))

    def set_bond_wire_type(self, bond_wire_type: Union[BondWireType, str]) -> None:
        """
        VBA Call
        --------
        Wire.BondWireType(bond_wire_type)
        """
        self.cache_method('BondWireType', str(getattr(bond_wire_type, 'value', bond_wire_type)))

    def set_height(self, height: float) -> None:
        """
        VBA Call
        --------
        Wire.Height(height)
        """
        self.cache_method('Height', height)

    def set_relative_center_position(self, pos: float) -> None:
        """
        VBA Call
        --------
        Wire.RelativeCenterPosition(pos)
        """
        self.cache_method('RelativeCenterPosition', pos)

    def set_point1(self, coords: Tuple[float, float, float]) -> None:
        """
        VBA Call
        --------
        Wire.Point1(coords[0], coords[1], coords[2], False)
        """
        self.cache_method('Point1', coords[0], coords[1], coords[2], False)

    def set_pick_as_point1(self) -> None:
        """
        VBA Call
        --------
        Wire.Point1(0, 0, 0, True)
        """
        self.cache_method('Point1', 0, 0, 0, True)

    def set_point2(self, coords: Tuple[float, float, float]) -> None:
        """
        VBA Call
        --------
        Wire.Point2(coords[0], coords[1], coords[2], False)
        """
        self.cache_method('Point2', coords[0], coords[1], coords[2], False)

    def set_pick_as_point2(self) -> None:
        """
        VBA Call
        --------
        Wire.Point2(0, 0, 0, True)
        """
        self.cache_method('Point2', 0, 0, 0, True)

    def set_alpha_angle_deg(self, angle_deg: float) -> None:
        """
        VBA Call
        --------
        Wire.Alpha(angle_deg)
        """
        self.cache_method('Alpha', angle_deg)

    def set_beta_angle_deg(self, angle_deg: float) -> None:
        """
        VBA Call
        --------
        Wire.Beta(angle_deg)
        """
        self.cache_method('Beta', angle_deg)

    def set_curve_name(self, name: str) -> None:
        """
        VBA Call
        --------
        Wire.Curve(name)
        """
        self.cache_method('Curve', name)

    def set_radius(self, radius: float) -> None:
        """
        VBA Call
        --------
        Wire.Radius(radius)
        """
        self.cache_method('Radius', radius)

    def set_solid_wire_model(self, flag: bool = True) -> None:
        """
        VBA Call
        --------
        Wire.SolidWireModel(flag)
        """
        self.cache_method('SolidWireModel', flag)

    def set_material(self, mat_name: str) -> None:
        """
        VBA Call
        --------
        Wire.Material(mat_name)
        """
        self.cache_method('Material', mat_name)

    def change_material(self, wire_name: str, material_name: str) -> None:
        """
        VBA Call
        --------
        Wire.ChangeMaterial(wire_name, material_name)
        """
        self.record_method('ChangeMaterial', wire_name, material_name)

    def set_termination(self, termination: Union[Termination, str]) -> None:
        """
        VBA Call
        --------
        Wire.Termination(termination)
        """
        self.cache_method('Termination', str(getattr(termination, 'value', termination)))

    def set_advanced_chain_selection(self, flag: bool = True) -> None:
        """
        VBA Call
        --------
        Wire.AdvancedChainSelection(flag)
        """
        self.cache_method('AdvancedChainSelection', flag)

    def create(self) -> None:
        """
        VBA Call
        --------
        Wire.Add()
        """
        self.cache_method('Add')
        self.flush_cache('Create Wire')

    def set_solid_name(self, name: str) -> None:
        """
        VBA Call
        --------
        Wire.SolidName(name)
        """
        self.cache_method('SolidName', name)

    def set_keep_wire_after_conversion(self, flag: bool = True) -> None:
        """
        VBA Call
        --------
        Wire.KeepWire(flag)
        """
        self.cache_method('KeepWire', flag)

    def convert_to_solid_shape(self) -> None:
        """
        VBA Call
        --------
        Wire.ConvertToSolidShape()
        """
        self.cache_method('ConvertToSolidShape')
        self.flush_cache('ConvertToSolidShape (Wire)')

    def delete(self, wire_name: str) -> None:
        """
        VBA Call
        --------
        Wire.Delete(wire_name)
        """
        self.record_method('Delete', wire_name)

    def rename(self, old_name: str, new_name: str) -> None:
        """
        VBA Call
        --------
        Wire.Rename(old_name, new_name)
        """
        self.record_method('Rename', old_name, new_name)

    def set_automesh_fixpoints(self, wire_name: str, flag: bool = True) -> None:
        """
        VBA Call
        --------
        Wire.SetAutomeshFixpoints(wire_name, flag)
        """
        self.record_method('SetAutomeshFixpoints', wire_name, flag)

    def set_priority(self, wire_name: str, priority: float) -> None:
        """
        VBA Call
        --------
        Wire.SetPriority(wire_name, priority)
        """
        self.record_method('SetPriority', wire_name, priority)

    def set_material_based_refinement(self, wire_name: str, flag: bool = True) -> None:
        """
        VBA Call
        --------
        Wire.SetMaterialBasedRefinement(wire_name, flag)
        """
        self.record_method('SetMaterialBasedRefinement', wire_name, flag)

    def set_mesh_stepwidth(self, wire_name: str, widths: Tuple[float, float, float]) -> None:
        """
        VBA Call
        --------
        Wire.SetMeshStepwidth(wire_name, widths[0], widths[1], widths[2])
        """
        self.record_method('SetMeshStepwidth', wire_name, widths[0], widths[1], widths[2])

    def set_mesh_stepwidth_tet(self, wire_name: str, step_width: float) -> None:
        """
        VBA Call
        --------
        Wire.SetMeshStepwidthTet(wire_name, step_width)
        """
        self.record_method('SetMeshStepwidthTet', wire_name, step_width)

    def set_mesh_stepwidth_srf(self, wire_name: str, step_width: float) -> None:
        """
        VBA Call
        --------
        Wire.SetMeshStepwidthSrf(wire_name, step_width)
        """
        self.record_method('SetMeshStepwidthSrf', wire_name, step_width)

    def set_mesh_extendwidth(self, widths: Tuple[float, float, float]) -> None:
        """
        VBA Call
        --------
        Wire.SetMeshExtendwidth(widths[0], widths[1], widths[2])
        """
        self.cache_method('SetMeshExtendwidth', widths[0], widths[1], widths[2])

    def set_mesh_refinement(self, active: bool, factor: float) -> None:
        """
        VBA Call
        --------
        Wire.SetMeshRefinement(active, factor)
        """
        self.cache_method('SetMeshRefinement', active, factor)

    def activate_mesh_refinement(self, factor: float) -> None:
        """
        VBA Call
        --------
        Wire.SetMeshRefinement(True, factor)
        """
        self.cache_method('SetMeshRefinement', True, factor)

    def deactivate_mesh_refinement(self) -> None:
        """
        VBA Call
        --------
        Wire.SetMeshRefinement(False, 1.0)
        """
        self.cache_method('SetMeshRefinement', False, 1.0)

    def set_mesh_volume_refinement(self, active: bool, factor: float) -> None:
        """
        VBA Call
        --------
        Wire.SetMeshVolumeRefinement(active, factor)
        """
        self.cache_method('SetMeshVolumeRefinement', active, factor)

    def activate_mesh_volume_refinement(self, factor: float) -> None:
        """
        VBA Call
        --------
        Wire.SetMeshVolumeRefinement(True, factor)
        """
        self.cache_method('SetMeshVolumeRefinement', True, factor)

    def deactivate_mesh_volume_refinement(self) -> None:
        """
        VBA Call
        --------
        Wire.SetMeshVolumeRefinement(False, 1.0)
        """
        self.cache_method('SetMeshVolumeRefinement', False, 1.0)

    def set_use_for_simulation(self, flag: bool = True) -> None:
        """
        VBA Call
        --------
        Wire.SetUseForSimulation(flag)
        """
        self.cache_method('SetUseForSimulation', flag)

    def get_length(self, wire_name: str) -> float:
        """
        VBA Call
        --------
        Wire.GetLength(wire_name)
        """
        return self.query_method_float('GetLength', wire_name)

    def get_grid_length(self, wire_name: str) -> float:
        """
        VBA Call
        --------
        Wire.GetGridLength(wire_name)
        """
        return self.query_method_float('GetGridLength', wire_name)

    def create_folder(self, name: str) -> None:
        """
        VBA Call
        --------
        Wire.NewFolder(name)
        """
        self.record_method('NewFolder', name)

    def delete_folder(self, name: str) -> None:
        """
        VBA Call
        --------
        Wire.DeleteFolder(name)
        """
        self.record_method('DeleteFolder', name)

    def rename_folder(self, old_name: str, new_name: str) -> None:
        """
        VBA Call
        --------
        Wire.RenameFolder(old_name, new_name)
        """
        self.record_method('RenameFolder', old_name, new_name)

    def does_folder_exist(self, name: str) -> bool:
        """
        VBA Call
        --------
        Wire.DoesFolderExist(name)
        """
        return self.query_method_bool('DoesFolderExist', name)

    def slice(self, name: str) -> None:
        """
        VBA Call
        --------
        Wire.Slice(name)
        """
        self.record_method('Slice', name)

    def slice_folder(self, name: str) -> None:
        """
        VBA Call
        --------
        Wire.SliceFolder(name)
        """
        self.record_method('SliceFolder', name)

