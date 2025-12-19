'''This file is auto-generated. Do not edit.'''
from .. import IVBAProvider, VBAObjWrapper

class Units(VBAObjWrapper):


    def __init__(self, vbap: IVBAProvider) -> None:
        super().__init__(vbap, 'Units')
        self.set_save_history(False)

    def set_geometry_unit(self, unit: str) -> None:
        """
        VBA Call
        --------
        Units.Geometry(unit)
        """
        self.record_method('Geometry', unit)

    def get_geometry_unit(self) -> str:
        """
        VBA Call
        --------
        Units.GetGeometryUnit()
        """
        return self.query_method_str('GetGeometryUnit')

    def get_geometry_unit_to_si_factor(self) -> float:
        """
        VBA Call
        --------
        Units.GetGeometryUnitToSI()
        """
        return self.query_method_float('GetGeometryUnitToSI')

    def get_geometry_si_to_unit_factor(self) -> float:
        """
        VBA Call
        --------
        Units.GetGeometrySIToUnit()
        """
        return self.query_method_float('GetGeometrySIToUnit')

    def set_time_unit(self, unit: str) -> None:
        """
        VBA Call
        --------
        Units.Time(unit)
        """
        self.record_method('Time', unit)

    def get_time_unit(self) -> str:
        """
        VBA Call
        --------
        Units.GetTimeUnit()
        """
        return self.query_method_str('GetTimeUnit')

    def get_time_unit_to_si_factor(self) -> float:
        """
        VBA Call
        --------
        Units.GetTimeUnitToSI()
        """
        return self.query_method_float('GetTimeUnitToSI')

    def get_time_si_to_unit_factor(self) -> float:
        """
        VBA Call
        --------
        Units.GetTimeSIToUnit()
        """
        return self.query_method_float('GetTimeSIToUnit')

    def set_frequency_unit(self, unit: str) -> None:
        """
        VBA Call
        --------
        Units.Frequency(unit)
        """
        self.record_method('Frequency', unit)

    def get_frequency_unit(self) -> str:
        """
        VBA Call
        --------
        Units.GetFrequencyUnit()
        """
        return self.query_method_str('GetFrequencyUnit')

    def get_frequency_unit_to_si_factor(self) -> float:
        """
        VBA Call
        --------
        Units.GetFrequencyUnitToSI()
        """
        return self.query_method_float('GetFrequencyUnitToSI')

    def get_frequency_si_to_unit_factor(self) -> float:
        """
        VBA Call
        --------
        Units.GetFrequencySIToUnit()
        """
        return self.query_method_float('GetFrequencySIToUnit')

    def set_temperature_unit(self, unit: str) -> None:
        """
        VBA Call
        --------
        Units.TemperatureUnit(unit)
        """
        self.record_method('TemperatureUnit', unit)

    def get_temperature_unit(self) -> str:
        """
        VBA Call
        --------
        Units.GetTemperatureUnit()
        """
        return self.query_method_str('GetTemperatureUnit')

