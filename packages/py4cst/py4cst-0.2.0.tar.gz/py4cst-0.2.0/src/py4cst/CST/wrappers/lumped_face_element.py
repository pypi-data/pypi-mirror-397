'''This file is auto-generated. Do not edit.'''
from .. import IVBAProvider, VBAObjWrapper
from enum import Enum
from typing import Union, Tuple

class LumpedFaceElement(VBAObjWrapper):
    class Type(Enum):
        RLC_PARALLEL = 'rlcparallel'
        RLC_SERIAL = 'rlcserial'
        DIODE = 'diode'
        SPICE_CIRCUIT = 'spicecircuit'
        TOUCHSTONE = 'touchstone'
        MULTIPIN_GROUP_ITEM = 'multipingroupitem'
        MULTIPIN_GROUP_SPICE = 'multipingroupspice'
        MULTIPIN_GROUP_TOUCHSTONE = 'multipingrouptouchstone'

    def __init__(self, vbap: IVBAProvider) -> None:
        super().__init__(vbap, 'LumpedFaceElement')
        self.set_save_history(False)

    def reset(self) -> None:
        """
        VBA Call
        --------
        LumpedFaceElement.Reset()
        """
        self.cache_method('Reset')

    def create(self) -> None:
        """
        VBA Call
        --------
        LumpedFaceElement.Create()
        """
        self.cache_method('Create')
        self.flush_cache('Create LumpedFaceElement')

    def modify(self) -> None:
        """
        VBA Call
        --------
        LumpedFaceElement.Modify()
        """
        self.cache_method('Modify')
        self.flush_cache('Modify LumpedFaceElement')

    def set_type(self, elem_type: Union[Type, str]) -> None:
        """
        VBA Call
        --------
        LumpedFaceElement.SetType(elem_type)
        """
        self.cache_method('SetType', str(getattr(elem_type, 'value', elem_type)))

    def set_name(self, name: str) -> None:
        """
        VBA Call
        --------
        LumpedFaceElement.SetName(name)
        """
        self.cache_method('SetName', name)

    def set_folder_name(self, folder_name: str) -> None:
        """
        VBA Call
        --------
        LumpedFaceElement.Folder(folder_name)
        """
        self.cache_method('Folder', folder_name)

    def set_resistance(self, value: float) -> None:
        """
        VBA Call
        --------
        LumpedFaceElement.SetR(value)
        """
        self.cache_method('SetR', value)

    def set_inductance(self, value: float) -> None:
        """
        VBA Call
        --------
        LumpedFaceElement.SetL(value)
        """
        self.cache_method('SetL', value)

    def set_capacitance(self, value: float) -> None:
        """
        VBA Call
        --------
        LumpedFaceElement.SetC(value)
        """
        self.cache_method('SetC', value)

    def set_blocking_conductivity(self, value: float) -> None:
        """
        VBA Call
        --------
        LumpedFaceElement.SetGs(value)
        """
        self.cache_method('SetGs', value)

    def set_reverse_current(self, value: float) -> None:
        """
        VBA Call
        --------
        LumpedFaceElement.SetI0(value)
        """
        self.cache_method('SetI0', value)

    def set_temperature_kelvin(self, value: float) -> None:
        """
        VBA Call
        --------
        LumpedFaceElement.SetT(value)
        """
        self.cache_method('SetT', value)

    def set_temperature_celsius(self, value: float) -> None:
        """
        VBA Call
        --------
        LumpedFaceElement.SetT(value-273.15)
        """
        self.cache_method('SetT', value-273.15)

    def set_temperature_fahrenheit(self, value: float) -> None:
        """
        VBA Call
        --------
        LumpedFaceElement.SetT((value + 459.67)*(5/9))
        """
        self.cache_method('SetT', (value + 459.67)*(5/9))

    def set_point1(self, coords: Tuple[float, float, float]) -> None:
        """
        VBA Call
        --------
        LumpedFaceElement.SetP1(False, coords[0], coords[1], coords[2])
        """
        self.cache_method('SetP1', False, coords[0], coords[1], coords[2])

    def set_pick_as_point1(self) -> None:
        """
        VBA Call
        --------
        LumpedFaceElement.SetP1(True, 0, 0, 0)
        """
        self.cache_method('SetP1', True, 0, 0, 0)

    def set_point2(self, coords: Tuple[float, float, float]) -> None:
        """
        VBA Call
        --------
        LumpedFaceElement.SetP2(False, coords[0], coords[1], coords[2])
        """
        self.cache_method('SetP2', False, coords[0], coords[1], coords[2])

    def set_pick_as_point2(self) -> None:
        """
        VBA Call
        --------
        LumpedFaceElement.SetP2(True, 0, 0, 0)
        """
        self.cache_method('SetP2', True, 0, 0, 0)

    def set_circuit_file_name(self, file_name: str) -> None:
        """
        VBA Call
        --------
        LumpedFaceElement.CircuitFileName(file_name)
        """
        self.cache_method('CircuitFileName', file_name)

    def set_use_relative_path(self, flag: bool) -> None:
        """
        VBA Call
        --------
        LumpedFaceElement.UseRelativePath(flag)
        """
        self.cache_method('UseRelativePath', flag)

    def set_circuit_id(self, id: int) -> None:
        """
        VBA Call
        --------
        LumpedFaceElement.CircuitId(id)
        """
        self.cache_method('CircuitId', id)

    def set_use_copy_only(self, flag: bool) -> None:
        """
        VBA Call
        --------
        LumpedFaceElement.UseCopyOnly(flag)
        """
        self.cache_method('UseCopyOnly', flag)

    def set_invert(self, flag: bool) -> None:
        """
        VBA Call
        --------
        LumpedFaceElement.SetInvert(flag)
        """
        self.cache_method('SetInvert', flag)

    def set_monitor(self, flag: bool) -> None:
        """
        VBA Call
        --------
        LumpedFaceElement.SetMonitor(flag)
        """
        self.cache_method('SetMonitor', flag)

    def set_use_projection(self, flag: bool) -> None:
        """
        VBA Call
        --------
        LumpedFaceElement.UseProjection(flag)
        """
        self.cache_method('UseProjection', flag)

    def set_reverse_projection(self, flag: bool) -> None:
        """
        VBA Call
        --------
        LumpedFaceElement.ReverseProjection(flag)
        """
        self.cache_method('ReverseProjection', flag)

    def set_port_name(self, name: str) -> None:
        """
        VBA Call
        --------
        LumpedFaceElement.PortName(name)
        """
        self.cache_method('PortName', name)

    def set_delete_port(self, flag: bool) -> None:
        """
        VBA Call
        --------
        LumpedFaceElement.DeletePort(flag)
        """
        self.record_method('DeletePort', flag)

    def rename(self, old_name: str, new_name: str) -> None:
        """
        VBA Call
        --------
        LumpedFaceElement.Rename(old_name, new_name)
        """
        self.record_method('Rename', old_name, new_name)

    def delete(self, name: str) -> None:
        """
        VBA Call
        --------
        LumpedFaceElement.Delete(name)
        """
        self.record_method('Delete', name)

    def create_folder(self, name: str) -> None:
        """
        VBA Call
        --------
        LumpedFaceElement.NewFolder(name)
        """
        self.record_method('NewFolder', name)

    def delete_folder(self, name: str) -> None:
        """
        VBA Call
        --------
        LumpedFaceElement.DeleteFolder(name)
        """
        self.record_method('DeleteFolder', name)

    def rename_folder(self, old_name: str, new_name: str) -> None:
        """
        VBA Call
        --------
        LumpedFaceElement.RenameFolder(old_name, new_name)
        """
        self.record_method('RenameFolder', old_name, new_name)

