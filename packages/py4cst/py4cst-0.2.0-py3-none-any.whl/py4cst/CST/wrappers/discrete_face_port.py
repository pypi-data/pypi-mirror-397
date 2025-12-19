'''This file is auto-generated. Do not edit.'''
from .. import IVBAProvider, VBATypeName, VBAObjWrapper
from .port import Port
from enum import Enum
from typing import Union, Tuple

class DiscreteFacePort(VBAObjWrapper):
    class PortType(Enum):
        SPARAMETER = 'Sparameter'
        VOLTAGE = 'Voltage'
        CURRENT = 'Current'

    class FaceType(Enum):
        LINEAR = 'Linear'
        CURVED = 'Curved'

    def __init__(self, vbap: IVBAProvider) -> None:
        super().__init__(vbap, 'DiscreteFacePort')
        self.set_save_history(False)

    def reset(self) -> None:
        """
        VBA Call
        --------
        DiscreteFacePort.Reset()
        """
        self.cache_method('Reset')

    def create(self) -> None:
        """
        VBA Call
        --------
        DiscreteFacePort.Create()
        """
        self.cache_method('Create')
        self.flush_cache('Create DiscreteFacePort')

    def modify(self) -> None:
        """
        VBA Call
        --------
        DiscreteFacePort.Modify()
        """
        self.cache_method('Modify')
        self.flush_cache('Modify DiscreteFacePort')

    def set_number(self, number: int) -> None:
        """
        VBA Call
        --------
        DiscreteFacePort.PortNumber(number)
        """
        self.cache_method('PortNumber', number)

    def set_label(self, label: str) -> None:
        """
        VBA Call
        --------
        DiscreteFacePort.Label(label)
        """
        self.cache_method('Label', label)

    def set_type(self, port_type: Union[PortType, str]) -> None:
        """
        VBA Call
        --------
        DiscreteFacePort.Type(port_type)
        """
        self.cache_method('Type', str(getattr(port_type, 'value', port_type)))

    def set_impedance(self, impedance: float) -> None:
        """
        VBA Call
        --------
        DiscreteFacePort.Impedance(impedance)
        """
        self.cache_method('Impedance', impedance)

    def set_voltage_amplitude(self, amplitude: float) -> None:
        """
        VBA Call
        --------
        DiscreteFacePort.VoltageAmplitude(amplitude)
        """
        self.cache_method('VoltageAmplitude', amplitude)

    def set_voltage_port_impedance(self, impedance: float) -> None:
        """
        VBA Call
        --------
        DiscreteFacePort.VoltagePortImpedance(impedance)
        """
        self.cache_method('VoltagePortImpedance', impedance)

    def set_current_amplitude(self, amplitude: float) -> None:
        """
        VBA Call
        --------
        DiscreteFacePort.CurrentAmplitude(amplitude)
        """
        self.cache_method('CurrentAmplitude', amplitude)

    def set_current_port_admittance(self, admittance: float) -> None:
        """
        VBA Call
        --------
        DiscreteFacePort.CurrentPortAdmittance(admittance)
        """
        self.cache_method('CurrentPortAdmittance', admittance)

    def set_point1(self, coords: Tuple[float, float, float]) -> None:
        """
        VBA Call
        --------
        DiscreteFacePort.SetP1(False, coords[0], coords[1], coords[2])
        """
        self.cache_method('SetP1', False, coords[0], coords[1], coords[2])

    def set_pick_as_point1(self) -> None:
        """
        VBA Call
        --------
        DiscreteFacePort.SetP1(True, 0, 0, 0)
        """
        self.cache_method('SetP1', True, 0, 0, 0)

    def set_point2(self, coords: Tuple[float, float, float]) -> None:
        """
        VBA Call
        --------
        DiscreteFacePort.SetP2(False, coords[0], coords[1], coords[2])
        """
        self.cache_method('SetP2', False, coords[0], coords[1], coords[2])

    def set_pick_as_point2(self) -> None:
        """
        VBA Call
        --------
        DiscreteFacePort.SetP2(True, 0, 0, 0)
        """
        self.cache_method('SetP2', True, 0, 0, 0)

    def set_invert_direction(self, flag: bool = True) -> None:
        """
        VBA Call
        --------
        DiscreteFacePort.InvertDirection(flag)
        """
        self.cache_method('InvertDirection', flag)

    def set_local_coordinates(self, flag: bool = True) -> None:
        """
        VBA Call
        --------
        DiscreteFacePort.LocalCoordinates(flag)
        """
        self.cache_method('LocalCoordinates', flag)

    def set_center_edge(self, flag: bool = True) -> None:
        """
        VBA Call
        --------
        DiscreteFacePort.CenterEdge(flag)
        """
        self.cache_method('CenterEdge', flag)

    def set_use_projection(self, flag: bool = True) -> None:
        """
        VBA Call
        --------
        DiscreteFacePort.UseProjection(flag)
        """
        self.cache_method('UseProjection', flag)

    def set_reverse_projection(self, flag: bool = True) -> None:
        """
        VBA Call
        --------
        DiscreteFacePort.ReverseProjection(flag)
        """
        self.cache_method('ReverseProjection', flag)

    def set_lumped_element_name(self, name: str) -> None:
        """
        VBA Call
        --------
        DiscreteFacePort.LumpedElementName(name)
        """
        self.cache_method('LumpedElementName', name)

    def set_delete_lumped_element(self, flag: bool = True) -> None:
        """
        VBA Call
        --------
        DiscreteFacePort.DeleteLumpedElement(flag)
        """
        self.cache_method('DeleteLumpedElement', flag)

    def set_monitor(self, flag: bool = True) -> None:
        """
        VBA Call
        --------
        DiscreteFacePort.Monitor(flag)
        """
        self.cache_method('Monitor', flag)

    def set_allow_full_size(self, flag: bool = True) -> None:
        """
        VBA Call
        --------
        DiscreteFacePort.AllowFullSize(flag)
        """
        self.cache_method('AllowFullSize', flag)

    def set_face_type(self, face_type: Union[FaceType, str]) -> None:
        """
        VBA Call
        --------
        DiscreteFacePort.FaceType(face_type)
        """
        self.cache_method('FaceType', str(getattr(face_type, 'value', face_type)))

    def get_properties(self) -> Tuple:
        """
        VBA Call
        --------
        DiscreteFacePort.GetProperties(&port_type)

        Returns
        -------
        (VBA return value, port_type)
        """
        __retval__ = list(self.query_method_t('GetProperties', VBATypeName.String, VBATypeName.String))
        __retval__[0] = DiscreteFacePort.PortType(__retval__[0])
        __retval__[1] = DiscreteFacePort.PortType(__retval__[1])
        return tuple(__retval__)

    def delete(self, port_number: int) -> None:
        """
        VBA Call
        --------
        Port.Delete(port_number)
        """
        Port(self.vbap).record_method('Delete', port_number)

