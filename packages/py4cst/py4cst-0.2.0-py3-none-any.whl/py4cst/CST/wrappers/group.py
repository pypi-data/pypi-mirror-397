'''This file is auto-generated. Do not edit.'''
from .. import IVBAProvider, VBAObjWrapper
from enum import Enum
from typing import Union

class Group(VBAObjWrapper):
    class Type(Enum):
        NORMAL = 'normal'
        MESH = 'mesh'

    def __init__(self, vbap: IVBAProvider) -> None:
        super().__init__(vbap, 'Group')
        self.set_save_history(False)

    def create(self, name: str, group_type: Union[Type, str]) -> None:
        """
        VBA Call
        --------
        Group.Add(name, group_type)
        """
        self.record_method('Add', name, str(getattr(group_type, 'value', group_type)))

    def delete(self, name: str) -> None:
        """
        VBA Call
        --------
        Group.Delete(name)
        """
        self.record_method('Delete', name)

    def rename(self, old_name: str, new_name: str) -> None:
        """
        VBA Call
        --------
        Group.Rename(old_name, new_name)
        """
        self.record_method('Rename', old_name, new_name)

    def add_item(self, item_name: str, group_name: str) -> None:
        """
        VBA Call
        --------
        Group.AddItem(item_name, group_name)
        """
        self.record_method('AddItem', item_name, group_name)

    def remove_item(self, item_name: str, group_name: str) -> None:
        """
        VBA Call
        --------
        Group.RemoveItem(item_name, group_name)
        """
        self.record_method('RemoveItem', item_name, group_name)

    def create_folder(self, name: str) -> None:
        """
        VBA Call
        --------
        Group.NewFolder(name)
        """
        self.record_method('NewFolder', name)

    def rename_folder(self, old_name: str, new_name: str) -> None:
        """
        VBA Call
        --------
        Group.RenameFolder(old_name, new_name)
        """
        self.record_method('RenameFolder', old_name, new_name)

    def delete_folder(self, name: str) -> None:
        """
        VBA Call
        --------
        Group.DeleteFolder(name)
        """
        self.record_method('DeleteFolder', name)

    def reset(self) -> None:
        """
        VBA Call
        --------
        Group.Reset()
        """
        self.record_method('Reset')

