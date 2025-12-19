'''This file is auto-generated. Do not edit.'''
from .. import IVBAProvider, VBATypeName, VBAObjWrapper
from typing import Union, Tuple, Optional
from enum import Enum

class FloquetPort(VBAObjWrapper):
    class Position(Enum):
        Z_MIN = 'zmin'
        Z_MAX = 'zmax'

    class ModeType(Enum):
        TE = 'TE'
        TM = 'TM'
        LCP = 'LCP'
        RCP = 'RCP'

    class SortCode(Enum):
        PLUS_BETA_PW = '+beta/pw'
        PLUS_BETA = '+beta'
        MINUS_BETA = '-beta'
        PLUS_ALPHA = '+alpha'
        MINUS_ALPHA = '-alpha'
        PLUS_TE = '+te'
        MINUS_TE = '-te'
        PLUS_TM = '+tm'
        MINUS_TM = '-tm'
        PLUS_ORDER_X = '+orderx'
        MINUS_ORDER_X = '-orderx'
        PLUS_ORDER_Y = '+ordery'
        MINUS_ORDER_Y = '-ordery'

    def __init__(self, vbap: IVBAProvider) -> None:
        super().__init__(vbap, 'FloquetPort')
        self.set_save_history(False)

    def reset(self) -> None:
        """
        VBA Call
        --------
        FloquetPort.Reset()
        """
        self.record_method('Reset')

    def prepare_port(self, position: Union[Position, str]) -> None:
        """
        VBA Call
        --------
        FloquetPort.Port(position)
        """
        self.record_method('Port', str(getattr(position, 'value', position)))

    def add_mode(self, mode_type: Union[ModeType, str], order_x: int, order_y_prime: int) -> None:
        """
        VBA Call
        --------
        FloquetPort.AddMode(mode_type, order_x, order_y_prime)
        """
        self.record_method('AddMode', str(getattr(mode_type, 'value', mode_type)), order_x, order_y_prime)

    def set_use_circular_polarization(self, flag: bool) -> None:
        """
        VBA Call
        --------
        FloquetPort.SetUseCircularPolarization(flag)
        """
        self.record_method('SetUseCircularPolarization', flag)

    def set_polarization_independent_of_phi_deg(self, alignment_angle: float) -> None:
        """
        VBA Call
        --------
        FloquetPort.SetPolarizationIndependentOfScanAnglePhi(alignment_angle, True)
        """
        self.record_method('SetPolarizationIndependentOfScanAnglePhi', alignment_angle, True)

    def set_polarization_independent_of_phi_rad(self, alignment_angle: float) -> None:
        """
        VBA Call
        --------
        FloquetPort.set_polarization_independent_of_phi_rad(alignment_angle)
        """
        self.record_method('set_polarization_independent_of_phi_rad', alignment_angle)

    def set_polarization_dependent_of_phi(self) -> None:
        """
        VBA Call
        --------
        FloquetPort.SetPolarizationIndependentOfScanAnglePhi(0, False)
        """
        self.record_method('SetPolarizationIndependentOfScanAnglePhi', 0, False)

    def set_dialog_frequency(self, frequency: float) -> None:
        """
        VBA Call
        --------
        FloquetPort.SetDialogFrequency(frequency)
        """
        self.record_method('SetDialogFrequency', frequency)

    def set_dialog_media_factor(self, frequency: float) -> None:
        """
        VBA Call
        --------
        FloquetPort.SetDialogMediaFactor(frequency)
        """
        self.record_method('SetDialogMediaFactor', frequency)

    def set_dialog_theta_deg(self, angle: float) -> None:
        """
        VBA Call
        --------
        FloquetPort.SetDialogTheta(angle)
        """
        self.record_method('SetDialogTheta', angle)

    def set_dialog_phi_deg(self, angle: float) -> None:
        """
        VBA Call
        --------
        FloquetPort.SetDialogPhi(angle)
        """
        self.record_method('SetDialogPhi', angle)

    def set_dialog_phi_rad(self, angle: float) -> None:
        """
        VBA Call
        --------
        FloquetPort.set_dialog_phi_rad(angle)
        """
        self.record_method('set_dialog_phi_rad', angle)

    def set_dialog_max_order_x(self, order: int) -> None:
        """
        VBA Call
        --------
        FloquetPort.SetDialogMaxOrderX(order)
        """
        self.record_method('SetDialogMaxOrderX', order)

    def set_dialog_max_order_y_prime(self, order: int) -> None:
        """
        VBA Call
        --------
        FloquetPort.SetDialogMaxOrderYPrime(order)
        """
        self.record_method('SetDialogMaxOrderYPrime', order)

    def set_customized_list_flag(self, flag: bool) -> None:
        """
        VBA Call
        --------
        FloquetPort.SetCustomizedListFlag(flag)
        """
        self.record_method('SetCustomizedListFlag', flag)

    def set_number_of_modes_considered(self, number: int) -> None:
        """
        VBA Call
        --------
        FloquetPort.SetNumberOfModesConsidered(number)
        """
        self.record_method('SetNumberOfModesConsidered', number)

    def set_sort_code(self, code: Union[SortCode, str]) -> None:
        """
        VBA Call
        --------
        FloquetPort.SetSortCode(code)
        """
        self.record_method('SetSortCode', str(getattr(code, 'value', code)))

    def set_distance_to_reference_plane(self, distance: float) -> None:
        """
        VBA Call
        --------
        FloquetPort.SetDistanceToReferencePlane(distance)
        """
        self.record_method('SetDistanceToReferencePlane', distance)

    def get_number_of_modes(self) -> int:
        """
        VBA Call
        --------
        FloquetPort.GetNumberOfModes()
        """
        return self.query_method_int('GetNumberOfModes')

    def reset_mode_iterator(self) -> bool:
        """
        VBA Call
        --------
        FloquetPort.FirstMode()
        """
        return self.query_method_bool('FirstMode')

    def get_mode(self) -> Optional[Tuple]:
        """
        VBA Call
        --------
        FloquetPort.GetMode(&mode_type, &order_x, &order_y_prime)

        Returns
        -------
        mode
            (mode_type, order_x, order_y_prime) *on success* | None
        """
        __retval__ = self.query_method_t('GetMode', VBATypeName.Boolean, VBATypeName.String, VBATypeName.Integer, VBATypeName.Integer)
        return None if not __retval__[0] else tuple(__retval__[1:])

    def advance_mode_iterator(self) -> bool:
        """
        VBA Call
        --------
        FloquetPort.NextMode()
        """
        return self.query_method_bool('NextMode')

    def get_number_of_modes_considered(self) -> int:
        """
        VBA Call
        --------
        FloquetPort.GetNumberOfModesConsidered()
        """
        return self.query_method_int('GetNumberOfModesConsidered')

    def is_port_at_z_min(self) -> bool:
        """
        VBA Call
        --------
        FloquetPort.IsPortAtZmin()
        """
        return self.query_method_bool('IsPortAtZmin')

    def is_port_at_z_max(self) -> bool:
        """
        VBA Call
        --------
        FloquetPort.IsPortAtZmax()
        """
        return self.query_method_bool('IsPortAtZmax')

    def get_mode_name_by_number(self, number: int) -> Optional[str]:
        """
        VBA Call
        --------
        FloquetPort.GetModeNameByNumber(&name, number)

        Returns
        -------
        name
            name *on success* | None
        """
        __retval__ = self.query_method_t('GetModeNameByNumber', VBATypeName.Boolean, VBATypeName.String, number)
        return None if not __retval__[0] else __retval__[1]

    def get_mode_number_by_name(self, name: str) -> Optional[int]:
        """
        VBA Call
        --------
        FloquetPort.GetModeNumberByName(&number, name)

        Returns
        -------
        mode_number
            number *on success* | None
        """
        __retval__ = self.query_method_t('GetModeNumberByName', VBATypeName.Boolean, VBATypeName.Long, name)
        return None if not __retval__[0] else __retval__[1]

    def set_force_legacy_phase_reference(self, flag: bool) -> None:
        """
        VBA Call
        --------
        FloquetPort.ForceLegacyPhaseReference(flag)
        """
        self.record_method('ForceLegacyPhaseReference', flag)

