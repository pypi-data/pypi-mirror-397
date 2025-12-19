'''This file is auto-generated. Do not edit.'''
from .. import IVBAProvider, VBATypeName, VBAObjWrapper
from typing import Union, Tuple, Optional
from enum import Enum

class LumpedElement(VBAObjWrapper):
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
        super().__init__(vbap, 'LumpedElement')
        self.set_save_history(False)

    def reset(self) -> None:
        """
        VBA Call
        --------
        LumpedElement.Reset()
        """
        self.cache_method('Reset')

    def create(self) -> None:
        """
        VBA Call
        --------
        LumpedElement.Create()
        """
        self.cache_method('Create')
        self.flush_cache('Create LumpedElement')

    def create_multipin(self) -> None:
        """
        VBA Call
        --------
        LumpedElement.CreateMultipin()
        """
        self.cache_method('CreateMultipin')
        self.flush_cache('CreateMultipin LumpedElement')

    def modify(self) -> None:
        """
        VBA Call
        --------
        LumpedElement.Modify()
        """
        self.cache_method('Modify')
        self.flush_cache('Modify LumpedElement')

    def set_type(self, elem_type: Union[Type, str]) -> None:
        """
        VBA Call
        --------
        LumpedElement.SetType(elem_type)
        """
        self.cache_method('SetType', str(getattr(elem_type, 'value', elem_type)))

    def set_name(self, name: str) -> None:
        """
        VBA Call
        --------
        LumpedElement.SetName(name)
        """
        self.cache_method('SetName', name)

    def set_folder_name(self, folder_name: str) -> None:
        """
        VBA Call
        --------
        LumpedElement.Folder(folder_name)
        """
        self.cache_method('Folder', folder_name)

    def set_resistance(self, value: float) -> None:
        """
        VBA Call
        --------
        LumpedElement.SetR(value)
        """
        self.cache_method('SetR', value)

    def set_inductance(self, value: float) -> None:
        """
        VBA Call
        --------
        LumpedElement.SetL(value)
        """
        self.cache_method('SetL', value)

    def set_capacitance(self, value: float) -> None:
        """
        VBA Call
        --------
        LumpedElement.SetC(value)
        """
        self.cache_method('SetC', value)

    def set_blocking_conductivity(self, value: float) -> None:
        """
        VBA Call
        --------
        LumpedElement.SetGs(value)
        """
        self.cache_method('SetGs', value)

    def set_reverse_current(self, value: float) -> None:
        """
        VBA Call
        --------
        LumpedElement.SetI0(value)
        """
        self.cache_method('SetI0', value)

    def set_temperature_kelvin(self, value: float) -> None:
        """
        VBA Call
        --------
        LumpedElement.SetT(value)
        """
        self.cache_method('SetT', value)

    def set_temperature_celsius(self, value: float) -> None:
        """
        VBA Call
        --------
        LumpedElement.SetT(value-273.15)
        """
        self.cache_method('SetT', value-273.15)

    def set_temperature_fahrenheit(self, value: float) -> None:
        """
        VBA Call
        --------
        LumpedElement.SetT((value + 459.67)*(5/9))
        """
        self.cache_method('SetT', (value + 459.67)*(5/9))

    def set_point1(self, coords: Tuple[float, float, float]) -> None:
        """
        VBA Call
        --------
        LumpedElement.SetP1(False, coords[0], coords[1], coords[2])
        """
        self.cache_method('SetP1', False, coords[0], coords[1], coords[2])

    def set_pick_as_point1(self) -> None:
        """
        VBA Call
        --------
        LumpedElement.SetP1(True, 0, 0, 0)
        """
        self.cache_method('SetP1', True, 0, 0, 0)

    def set_point2(self, coords: Tuple[float, float, float]) -> None:
        """
        VBA Call
        --------
        LumpedElement.SetP2(False, coords[0], coords[1], coords[2])
        """
        self.cache_method('SetP2', False, coords[0], coords[1], coords[2])

    def set_pick_as_point2(self) -> None:
        """
        VBA Call
        --------
        LumpedElement.SetP2(True, 0, 0, 0)
        """
        self.cache_method('SetP2', True, 0, 0, 0)

    def get_coordinates(self, name: str) -> Optional[Tuple]:
        """
        VBA Call
        --------
        LumpedElement.GetCoordinates(name, &x0, &y0, &z0, &x1, &y1, &z1)

        Returns
        -------
        coordinates
            (x0, y0, z0, x1, y1, z1) *on success* | None
        """
        __retval__ = self.query_method_t('GetCoordinates', VBATypeName.Boolean, name, VBATypeName.Double, VBATypeName.Double, VBATypeName.Double, VBATypeName.Double, VBATypeName.Double, VBATypeName.Double)
        return None if not __retval__[0] else tuple(__retval__[1:])

    def get_properties(self, name: str) -> Optional[Tuple]:
        """
        VBA Call
        --------
        LumpedElement.GetProperties(name, &type, &r, &l, &c, &gs, &i0, &t, &radius)

        Returns
        -------
        properties
            (type, r, l, c, Gs, I0, T, radius) *on success* | None
        """
        __retval__ = self.query_method_t('GetProperties', VBATypeName.Boolean, name, VBATypeName.String, VBATypeName.Double, VBATypeName.Double, VBATypeName.Double, VBATypeName.Double, VBATypeName.Double, VBATypeName.Double, VBATypeName.Double)
        return None if not __retval__[0] else tuple(__retval__[1:])

    def set_circuit_file_name(self, file_name: str) -> None:
        """
        VBA Call
        --------
        LumpedElement.CircuitFileName(file_name)
        """
        self.cache_method('CircuitFileName', file_name)

    def set_use_relative_path(self, flag: bool) -> None:
        """
        VBA Call
        --------
        LumpedElement.UseRelativePath(flag)
        """
        self.cache_method('UseRelativePath', flag)

    def set_circuit_id(self, id: int) -> None:
        """
        VBA Call
        --------
        LumpedElement.CircuitId(id)
        """
        self.cache_method('CircuitId', id)

    def set_use_copy_only(self, flag: bool) -> None:
        """
        VBA Call
        --------
        LumpedElement.UseCopyOnly(flag)
        """
        self.cache_method('UseCopyOnly', flag)

    def set_invert(self, flag: bool) -> None:
        """
        VBA Call
        --------
        LumpedElement.SetInvert(flag)
        """
        self.cache_method('SetInvert', flag)

    def set_monitor(self, flag: bool) -> None:
        """
        VBA Call
        --------
        LumpedElement.SetMonitor(flag)
        """
        self.cache_method('SetMonitor', flag)

    def set_radius(self, radius: float) -> None:
        """
        VBA Call
        --------
        LumpedElement.SetRadius(radius)
        """
        self.cache_method('SetRadius', radius)

    def set_wire(self, wire: str) -> None:
        """
        VBA Call
        --------
        LumpedElement.Wire(wire)
        """
        self.cache_method('Wire', wire)

    def set_wire_end_to_end1(self) -> None:
        """
        VBA Call
        --------
        LumpedElement.Position('end1')
        """
        self.cache_method('Position', 'end1')

    def set_wire_end_to_end2(self) -> None:
        """
        VBA Call
        --------
        LumpedElement.Position('end2')
        """
        self.cache_method('Position', 'end2')

    def set_port_name(self, name: str) -> None:
        """
        VBA Call
        --------
        LumpedElement.PortName(name)
        """
        self.cache_method('PortName', name)

    def start_name_iteration(self) -> None:
        """
        VBA Call
        --------
        LumpedElement.StartLumpedElementNameIteration()
        """
        self.record_method('StartLumpedElementNameIteration')

    def connect_multipin_element_pin_to_sub_element(self, multipin_name: str, circuit_pin_name: str, multipin_sub_element_name: str) -> None:
        """
        VBA Call
        --------
        LumpedElement.ConnectMultipinElementPinToSubElement(multipin_name, circuit_pin_name, multipin_sub_element_name)
        """
        self.record_method('ConnectMultipinElementPinToSubElement', multipin_name, circuit_pin_name, multipin_sub_element_name)

    def connect_multipin_element_pin_to_short(self, multipin_name: str, circuit_pin_name: str) -> None:
        """
        VBA Call
        --------
        LumpedElement.ConnectMultipinElementPinToShort(multipin_name, circuit_pin_name)
        """
        self.record_method('ConnectMultipinElementPinToShort', multipin_name, circuit_pin_name)

    def connect_multipin_element_pin_to_open(self, multipin_name: str, circuit_pin_name: str) -> None:
        """
        VBA Call
        --------
        LumpedElement.ConnectMultipinElementPinToOpen(multipin_name, circuit_pin_name)
        """
        self.record_method('ConnectMultipinElementPinToOpen', multipin_name, circuit_pin_name)

    def get_next_name(self) -> None:
        """
        VBA Call
        --------
        LumpedElement.GetNextLumpedElementName()
        """
        self.record_method('GetNextLumpedElementName')

    def rename(self, old_name: str, new_name: str) -> None:
        """
        VBA Call
        --------
        LumpedElement.Rename(old_name, new_name)
        """
        self.record_method('Rename', old_name, new_name)

    def delete(self, name: str) -> None:
        """
        VBA Call
        --------
        LumpedElement.Delete(name)
        """
        self.record_method('Delete', name)

    def create_folder(self, name: str) -> None:
        """
        VBA Call
        --------
        LumpedElement.NewFolder(name)
        """
        self.record_method('NewFolder', name)

    def delete_folder(self, name: str) -> None:
        """
        VBA Call
        --------
        LumpedElement.DeleteFolder(name)
        """
        self.record_method('DeleteFolder', name)

    def rename_folder(self, old_name: str, new_name: str) -> None:
        """
        VBA Call
        --------
        LumpedElement.RenameFolder(old_name, new_name)
        """
        self.record_method('RenameFolder', old_name, new_name)

