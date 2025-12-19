'''This file is auto-generated. Do not edit.'''
from .. import IVBAProvider, VBATypeName, VBAObjWrapper
from typing import Union, Tuple, Optional
from enum import Enum

class DiscretePort(VBAObjWrapper):
    class PortType(Enum):
        S_PARAMETER = 'Sparameter'
        VOLTAGE = 'Voltage'
        CURRENT = 'Current'

    def __init__(self, vbap: IVBAProvider) -> None:
        super().__init__(vbap, 'DiscretePort')
        self.set_save_history(False)

    def reset(self) -> None:
        """
        VBA Call
        --------
        DiscretePort.Reset()
        """
        self.cache_method('Reset')

    def create(self) -> None:
        """
        VBA Call
        --------
        DiscretePort.Create()
        """
        self.cache_method('Create')
        self.flush_cache('Create DiscretePort')

    def modify(self) -> None:
        """
        VBA Call
        --------
        DiscretePort.Modify()
        """
        self.cache_method('Modify')
        self.flush_cache('Modify DiscretePort')

    def set_number(self, number: int) -> None:
        """
        VBA Call
        --------
        DiscretePort.PortNumber(number)
        """
        self.cache_method('PortNumber', number)

    def set_label(self, label: str) -> None:
        """
        VBA Call
        --------
        DiscretePort.Label(label)
        """
        self.cache_method('Label', label)

    def set_type(self, port_type: Union[PortType, str]) -> None:
        """
        VBA Call
        --------
        DiscretePort.Type(port_type)
        """
        self.cache_method('Type', str(getattr(port_type, 'value', port_type)))

    def set_impedance(self, impedance: float) -> None:
        """
        VBA Call
        --------
        DiscretePort.Impedance(impedance)
        """
        self.cache_method('Impedance', impedance)

    def set_voltage(self, voltage: float) -> None:
        """
        VBA Call
        --------
        DiscretePort.Voltage(voltage)
        """
        self.cache_method('Voltage', voltage)

    def set_voltage_port_impedance(self, impedance: float) -> None:
        """
        VBA Call
        --------
        DiscretePort.VoltagePortImpedance(impedance)
        """
        self.cache_method('VoltagePortImpedance', impedance)

    def set_current(self, current: float) -> None:
        """
        VBA Call
        --------
        DiscretePort.Current(current)
        """
        self.cache_method('Current', current)

    def set_current_port_admittance(self, admittance: float) -> None:
        """
        VBA Call
        --------
        DiscretePort.CurrentPortAdmittance(admittance)
        """
        self.cache_method('CurrentPortAdmittance', admittance)

    def set_radius(self, radius: float) -> None:
        """
        VBA Call
        --------
        DiscretePort.Radius(radius)
        """
        self.cache_method('Radius', radius)

    def set_point1(self, coords: Tuple[float, float, float]) -> None:
        """
        VBA Call
        --------
        DiscretePort.SetP1(False, coords[0], coords[1], coords[2])
        """
        self.cache_method('SetP1', False, coords[0], coords[1], coords[2])

    def set_pick_as_point1(self) -> None:
        """
        VBA Call
        --------
        DiscretePort.SetP1(True, 0, 0, 0)
        """
        self.cache_method('SetP1', True, 0, 0, 0)

    def set_point2(self, coords: Tuple[float, float, float]) -> None:
        """
        VBA Call
        --------
        DiscretePort.SetP2(False, coords[0], coords[1], coords[2])
        """
        self.cache_method('SetP2', False, coords[0], coords[1], coords[2])

    def set_pick_as_point2(self) -> None:
        """
        VBA Call
        --------
        DiscretePort.SetP2(True, 0, 0, 0)
        """
        self.cache_method('SetP2', True, 0, 0, 0)

    def set_invert_direction(self, flag: bool = True) -> None:
        """
        VBA Call
        --------
        DiscretePort.InvertDirection(flag)
        """
        self.cache_method('InvertDirection', flag)

    def set_local_coordinates(self, flag: bool = True) -> None:
        """
        VBA Call
        --------
        DiscretePort.LocalCoordinates(flag)
        """
        self.cache_method('LocalCoordinates', flag)

    def set_monitor(self, flag: bool = True) -> None:
        """
        VBA Call
        --------
        DiscretePort.Monitor(flag)
        """
        self.cache_method('Monitor', flag)

    def set_wire(self, wire_name: str) -> None:
        """
        VBA Call
        --------
        DiscretePort.Wire(wire_name)
        """
        self.cache_method('Wire', wire_name)

    def set_wire_end_to_end1(self) -> None:
        """
        VBA Call
        --------
        DiscretePort.Position('end1')
        """
        self.cache_method('Position', 'end1')

    def set_wire_end_to_end2(self) -> None:
        """
        VBA Call
        --------
        DiscretePort.Position('end2')
        """
        self.cache_method('Position', 'end2')

    def set_lumped_element_name(self, name: str) -> None:
        """
        VBA Call
        --------
        DiscretePort.LumpedElementName(name)
        """
        self.cache_method('LumpedElementName', name)

    def set_delete_lumped_element(self, flag: bool = True) -> None:
        """
        VBA Call
        --------
        DiscretePort.DeleteLumpedElement(flag)
        """
        self.cache_method('DeleteLumpedElement', flag)

    def get_element_dir_index(self, port_number: int) -> Tuple:
        """
        VBA Call
        --------
        DiscretePort.GetElementDirIndex(port_number, &dir, &index)

        Returns
        -------
        (dir, index)
        """
        return self.query_method_t('GetElementDirIndex', None, port_number, VBATypeName.Long, VBATypeName.Long)

    def get_element_second_index(self, port_number: int) -> int:
        """
        VBA Call
        --------
        DiscretePort.GetElement2ndIndex(port_number, &index)

        Returns
        -------
        index
        """
        __retval__ = self.query_method_t('GetElement2ndIndex', None, port_number, VBATypeName.Long)
        return __retval__[0]

    def get_length(self, port_number: int) -> float:
        """
        VBA Call
        --------
        DiscretePort.GetLength(port_number)
        """
        return self.query_method_float('GetLength', port_number)

    def get_grid_length(self, port_number: int) -> float:
        """
        VBA Call
        --------
        DiscretePort.GetGridLength(port_number)
        """
        return self.query_method_float('GetGridLength', port_number)

    def get_coordinates(self, port_number: int) -> Optional[Tuple]:
        """
        VBA Call
        --------
        DiscretePort.GetCoordinates(port_number, &x0, &y0, &z0, &x1, &y1, &z1)

        Returns
        -------
        coordinates
            (x0, y0, z0, x1, y1, z1) *on success* | None
        """
        __retval__ = self.query_method_t('GetCoordinates', VBATypeName.Boolean, port_number, VBATypeName.Double, VBATypeName.Double, VBATypeName.Double, VBATypeName.Double, VBATypeName.Double, VBATypeName.Double)
        return None if not __retval__[0] else tuple(__retval__[1:])

    def get_properties(self, port_number: int) -> Optional[Tuple]:
        """
        VBA Call
        --------
        DiscretePort.GetProperties(port_number, &type, &impedance, &current, &voltage, &voltage_port_impedance, &radius, &monitor)

        Returns
        -------
        coordinates
            (x0, y0, z0, x1, y1, z1) *on success* | None
        """
        __retval__ = list(self.query_method_t('GetProperties', VBATypeName.Boolean, port_number, VBATypeName.String, VBATypeName.Double, VBATypeName.Double, VBATypeName.Double, VBATypeName.Double, VBATypeName.Double, VBATypeName.Boolean))
        __retval__[1] = DiscretePort.PortType(__retval__[1])
        return None if not __retval__[0] else tuple(__retval__[1:])

    def delete(self, port_number: int) -> None:
        """
        VBA Call
        --------
        DiscretePort.Delete(port_number)
        """
        self.record_method('Delete', port_number)

