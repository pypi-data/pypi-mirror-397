'''This file is auto-generated. Do not edit.'''
from .. import IVBAProvider, VBATypeName, VBAObjWrapper
from typing import Tuple, Optional

class Anchorpoint(VBAObjWrapper):


    def __init__(self, vbap: IVBAProvider) -> None:
        super().__init__(vbap, 'Anchorpoint')
        self.set_save_history(False)

    def store(self, name: str) -> None:
        """
        VBA Call
        --------
        Anchorpoint.Store(name)
        """
        self.record_method('Store', name)

    def define(self, name: str, pos: Tuple[float, float, float], normal: Tuple[float, float, float], u_vector: Tuple[float, float, float]) -> None:
        """
        VBA Call
        --------
        Anchorpoint.Define(name, pos[0], pos[1], pos[2], normal[0], normal[1], normal[2], u_vector[0], u_vector[1], u_vector[2])
        """
        self.record_method('Define', name, pos[0], pos[1], pos[2], normal[0], normal[1], normal[2], u_vector[0], u_vector[1], u_vector[2])

    def restore(self, name: str) -> None:
        """
        VBA Call
        --------
        Anchorpoint.Restore(name)
        """
        self.record_method('Restore', name)

    def delete(self, name: str) -> None:
        """
        VBA Call
        --------
        Anchorpoint.Delete(name)
        """
        self.record_method('Delete', name)

    def rename(self, old_name: str, new_name: str) -> None:
        """
        VBA Call
        --------
        Anchorpoint.Rename(old_name, new_name)
        """
        self.record_method('Rename', old_name, new_name)

    def create_folder(self, name: str) -> None:
        """
        VBA Call
        --------
        Anchorpoint.NewFolder(name)
        """
        self.record_method('NewFolder', name)

    def delete_folder(self, name: str) -> None:
        """
        VBA Call
        --------
        Anchorpoint.DeleteFolder(name)
        """
        self.record_method('DeleteFolder', name)

    def rename_folder(self, old_name: str, new_name: str) -> None:
        """
        VBA Call
        --------
        Anchorpoint.RenameFolder(old_name, new_name)
        """
        self.record_method('RenameFolder', old_name, new_name)

    def does_exist(self, name: str) -> bool:
        """
        VBA Call
        --------
        Anchorpoint.DoesExist(name)
        """
        return self.query_method_bool('DoesExist', name)

    def get_origin(self, name: str) -> Optional[Tuple]:
        """
        VBA Call
        --------
        Anchorpoint.GetOrigin(name, &x, &y, &z)

        Returns
        -------
        origin
            (x, y, z) *on success* | None
        """
        __retval__ = self.query_method_t('GetOrigin', VBATypeName.Boolean, name, VBATypeName.Double, VBATypeName.Double, VBATypeName.Double)
        return None if not __retval__[0] else tuple(__retval__[1:])

    def get_normal(self, name: str) -> Optional[Tuple]:
        """
        VBA Call
        --------
        Anchorpoint.GetNormal(name, &x, &y, &z)

        Returns
        -------
        normal
            (x, y, z) *on success* | None
        """
        __retval__ = self.query_method_t('GetNormal', VBATypeName.Boolean, name, VBATypeName.Double, VBATypeName.Double, VBATypeName.Double)
        return None if not __retval__[0] else tuple(__retval__[1:])

    def get_u_vector(self, name: str) -> Optional[Tuple]:
        """
        VBA Call
        --------
        Anchorpoint.GetUVector(name, &x, &y, &z)

        Returns
        -------
        u_vector
            (x, y, z) *on success* | None
        """
        __retval__ = self.query_method_t('GetUVector', VBATypeName.Boolean, name, VBATypeName.Double, VBATypeName.Double, VBATypeName.Double)
        return None if not __retval__[0] else tuple(__retval__[1:])

