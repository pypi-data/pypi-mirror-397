'''This file is auto-generated. Do not edit.'''
from .. import IVBAProvider, VBATypeName, VBAObjWrapper
from enum import Enum
from typing import Union, Tuple

class PlaneWave(VBAObjWrapper):
    class PolarizationType(Enum):
        LINEAR = 'Linear'
        CIRCULAR = 'Circular'
        ELLIPTICAL = 'Elliptical'

    class CircularDirection(Enum):
        LEFT = 'Left'
        RIGHT = 'Right'

    class Direction(Enum):
        X = 'x'
        Y = 'y'
        Z = 'z'

    def __init__(self, vbap: IVBAProvider) -> None:
        super().__init__(vbap, 'PlaneWave')
        self.set_save_history(False)

    def reset(self) -> None:
        """
        VBA Call
        --------
        PlaneWave.Reset()
        """
        self.record_method('Reset')

    def store(self) -> None:
        """
        VBA Call
        --------
        PlaneWave.Store()
        """
        self.record_method('Store')

    def delete(self) -> None:
        """
        VBA Call
        --------
        PlaneWave.Delete()
        """
        self.record_method('Delete')

    def set_normal_vector(self, coords: Tuple[float, float, float]) -> None:
        """
        VBA Call
        --------
        PlaneWave.Normal(coords[0], coords[1], coords[2])
        """
        self.record_method('Normal', coords[0], coords[1], coords[2])

    def set_e_vector(self, coords: Tuple[float, float, float]) -> None:
        """
        VBA Call
        --------
        PlaneWave.EVector(coords[0], coords[1], coords[2])
        """
        self.record_method('EVector', coords[0], coords[1], coords[2])

    def set_polarization(self, polarization_type: Union[PolarizationType, str]) -> None:
        """
        VBA Call
        --------
        PlaneWave.Polarization(polarization_type)
        """
        self.record_method('Polarization', str(getattr(polarization_type, 'value', polarization_type)))

    def set_reference_frequency(self, frequency: float) -> None:
        """
        VBA Call
        --------
        PlaneWave.ReferenceFrequency(frequency)
        """
        self.record_method('ReferenceFrequency', frequency)

    def set_phase_difference_deg(self, angle: float) -> None:
        """
        VBA Call
        --------
        PlaneWave.PhaseDifference(angle)
        """
        self.record_method('PhaseDifference', angle)

    def set_circular_direction(self, direction: Union[CircularDirection, str]) -> None:
        """
        VBA Call
        --------
        PlaneWave.CircularDirection(direction)
        """
        self.record_method('CircularDirection', str(getattr(direction, 'value', direction)))

    def set_axial_ratio(self, ratio: float) -> None:
        """
        VBA Call
        --------
        PlaneWave.AxialRatio(ratio)
        """
        self.record_method('AxialRatio', ratio)

    def set_use_custom_decoupling_plane(self, flag: bool = True) -> None:
        """
        VBA Call
        --------
        PlaneWave.SetUserDecouplingPlane(flag)
        """
        self.record_method('SetUserDecouplingPlane', flag)

    def set_custom_decoupling_plane(self, direction: Union[Direction, str], position: float) -> None:
        """
        VBA Call
        --------
        PlaneWave.DecouplingPlane(direction, position)
        """
        self.record_method('DecouplingPlane', str(getattr(direction, 'value', direction)), position)

    def get_normal_vector(self) -> Tuple:
        """
        VBA Call
        --------
        PlaneWave.GetNormal(&x, &y, &z)

        Returns
        -------
        (x, y, z)
        """
        return self.query_method_t('GetNormal', None, VBATypeName.Double, VBATypeName.Double, VBATypeName.Double)

    def get_e_vector(self) -> Tuple:
        """
        VBA Call
        --------
        PlaneWave.GetEVector(&x, &y, &z)

        Returns
        -------
        (x, y, z)
        """
        return self.query_method_t('GetEVector', None, VBATypeName.Double, VBATypeName.Double, VBATypeName.Double)

    def get_polarization_type(self) -> PolarizationType:
        """
        VBA Call
        --------
        PlaneWave.GetPolarizationType()
        """
        __retval__ = self.query_method_str('GetPolarizationType')
        return PlaneWave.PolarizationType(__retval__)

    def get_circular_direction(self) -> CircularDirection:
        """
        VBA Call
        --------
        PlaneWave.GetCircularDirection()
        """
        __retval__ = self.query_method_str('GetCircularDirection')
        return PlaneWave.CircularDirection(__retval__)

    def get_reference_frequency(self) -> float:
        """
        VBA Call
        --------
        PlaneWave.GetReferenceFrequency()
        """
        return self.query_method_float('GetReferenceFrequency')

    def get_phase_difference_deg(self) -> float:
        """
        VBA Call
        --------
        PlaneWave.GetPhaseDifference()
        """
        return self.query_method_float('GetPhaseDifference')

    def get_axial_ratio(self) -> float:
        """
        VBA Call
        --------
        PlaneWave.GetAxialRatio()
        """
        return self.query_method_float('GetAxialRatio')

