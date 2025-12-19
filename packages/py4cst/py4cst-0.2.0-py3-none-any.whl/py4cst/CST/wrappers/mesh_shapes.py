'''This file is auto-generated. Do not edit.'''
from .. import IVBAProvider, VBAObjWrapper

class MeshShapes(VBAObjWrapper):


    def __init__(self, vbap: IVBAProvider) -> None:
        super().__init__(vbap, 'MeshShapes')
        self.set_save_history(False)

    def reset(self) -> None:
        """
        VBA Call
        --------
        MeshShapes.Reset()
        """
        self.cache_method('Reset')

    def delete(self, mesh_shape_name: str) -> None:
        """
        VBA Call
        --------
        MeshShapes.Delete(mesh_shape_name)
        """
        self.record_method('Delete', mesh_shape_name)

    def rename(self, old_mesh_shape_name: str, new_mesh_shape_name: str) -> None:
        """
        VBA Call
        --------
        MeshShapes.Rename(old_mesh_shape_name, new_mesh_shape_name)
        """
        self.record_method('Rename', old_mesh_shape_name, new_mesh_shape_name)

    def new_folder(self, name: str) -> None:
        """
        VBA Call
        --------
        MeshShapes.NewFolder(name)
        """
        self.record_method('NewFolder', name)

    def delete_folder(self, name: str) -> None:
        """
        VBA Call
        --------
        MeshShapes.DeleteFolder(name)
        """
        self.record_method('DeleteFolder', name)

    def rename_folder(self, old_name: str, new_name: str) -> None:
        """
        VBA Call
        --------
        MeshShapes.RenameFolder(old_name, new_name)
        """
        self.record_method('RenameFolder', old_name, new_name)

    def change_material(self, mesh_shape_name: str, material_name: str) -> None:
        """
        VBA Call
        --------
        MeshShapes.ChangeMaterial(mesh_shape_name, material_name)
        """
        self.record_method('ChangeMaterial', mesh_shape_name, material_name)

    def add_name(self, element_name: str) -> None:
        """
        VBA Call
        --------
        MeshShapes.AddName(element_name)
        """
        self.cache_method('AddName', element_name)

    def delete_multiple(self) -> None:
        """
        VBA Call
        --------
        MeshShapes.DeleteMultiple()
        """
        self.cache_method('DeleteMultiple')
        self.flush_cache('DeleteMultipleMeshShapes')

    def set_tolerance(self, value: float) -> None:
        """
        VBA Call
        --------
        MeshShapes.Tolerance(value)
        """
        self.cache_method('Tolerance', value)

    def resolve_intersections(self) -> None:
        """
        VBA Call
        --------
        MeshShapes.ResolveIntersections()
        """
        self.cache_method('ResolveIntersections')
        self.flush_cache('ResolveIntersections')

    def mesh_element_size(self, value: float) -> None:
        """
        VBA Call
        --------
        MeshShapes.MeshElementSize(value)
        """
        self.cache_method('MeshElementSize', value)

    def create_mesh_shapes_by_facetting(self) -> None:
        """
        VBA Call
        --------
        MeshShapes.CreateMeshShapesByFacetting()
        """
        self.cache_method('CreateMeshShapesByFacetting')
        self.flush_cache('CreateMeshShapesByFacetting')

    def create_mesh_shapes_by_remeshing(self) -> None:
        """
        VBA Call
        --------
        MeshShapes.CreateMeshShapesByRemeshing()
        """
        self.cache_method('CreateMeshShapesByRemeshing')
        self.flush_cache('CreateMeshShapesByRemeshing')

