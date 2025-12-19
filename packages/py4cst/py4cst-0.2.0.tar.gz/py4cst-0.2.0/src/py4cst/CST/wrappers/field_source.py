'''This file is auto-generated. Do not edit.'''
from .. import IVBAProvider, VBAObjWrapper
from enum import Enum
from typing import Union

class FieldSource(VBAObjWrapper):
    class AlignmentType(Enum):
        USER = 'user'
        CURRENT_WCS = 'currentwcs'
        SOURCE_FILE = 'sourcefile'

    class MultipoleCalcMode(Enum):
        AUTOMATIC = 'automatic'
        USER_DEFINED = 'user defined'
        AUTO_TRUNCATION = 'autotruncation'

    class SourceName(Enum):
        TEMPERATURE = 'Temperature'
        DISPLACEMENT = 'Displacement'
        FORCE_DENSITY = 'Force Density'
        NODAL_FORCES = 'Nodal Forces'
        THERMAL_LOSSES = 'Thermal Losses'

    class FieldMonitorName(Enum):
        INITIAL_SOLUTION = 'Initial Solution'
        STATIONARY_SOLUTION = 'Stationary Solution'

    class ImportSettingsKey(Enum):
        FORMAT_SOURCE = 'FormatSource'
        FORMAT_TARGET = 'FormatTarget'
        NASTRAN_FILENAME = 'NastranFilename'
        TEMPERATURE_FILENAME = 'TemperatureFilename'
        GEOMETRY_UNIT = 'GeometryUnit'
        TEMPERATURE_UNIT = 'TemperatureUnit'
        WORKING_DIR = 'WorkingDir'

    class ImportSettingFormatSource(Enum):
        ABAQUS = 'Abaqus'
        TET = 'Tet'
        HEX = 'Hex'
        CHT = 'CHT'

    def __init__(self, vbap: IVBAProvider) -> None:
        super().__init__(vbap, 'FieldSource')
        self.set_save_history(False)

    def reset(self) -> None:
        """
        VBA Call
        --------
        FieldSource.Reset()
        """
        self.record_method('Reset')

    def set_name(self, name: str) -> None:
        """
        VBA Call
        --------
        FieldSource.Name(name)
        """
        self.record_method('Name', name)

    def set_file_name(self, name: str) -> None:
        """
        VBA Call
        --------
        FieldSource.FileName(name)
        """
        self.record_method('FileName', name)

    def delete(self, name: str) -> None:
        """
        VBA Call
        --------
        FieldSource.Delete(name)
        """
        self.record_method('Delete', name)

    def set_id(self, id: int) -> None:
        """
        VBA Call
        --------
        FieldSource.Id(id)
        """
        self.record_method('Id', id)

    def get_next_id(self) -> int:
        """
        VBA Call
        --------
        FieldSource.GetNextId()
        """
        return self.query_method_int('GetNextId')

    def delete_all(self) -> None:
        """
        VBA Call
        --------
        FieldSource.DeleteAll()
        """
        self.record_method('DeleteAll')

    def rename(self, old_name: str, new_name: str) -> None:
        """
        VBA Call
        --------
        FieldSource.Rename(old_name, new_name)
        """
        self.record_method('Rename', old_name, new_name)

    def read_from_file(self) -> None:
        """
        VBA Call
        --------
        FieldSource.Read()
        """
        self.record_method('Read')

    def set_project_path(self, path: str) -> None:
        """
        VBA Call
        --------
        FieldSource.ProjectPath(path)
        """
        self.record_method('ProjectPath', path)

    def set_use_relative_path(self, flag: bool) -> None:
        """
        VBA Call
        --------
        FieldSource.UseRelativePath(flag)
        """
        self.record_method('UseRelativePath', flag)

    def set_result_subdir(self, path: str) -> None:
        """
        VBA Call
        --------
        FieldSource.ResultSubDirectory(path)
        """
        self.record_method('ResultSubDirectory', path)

    def set_source_name(self, field_type: Union[SourceName, str]) -> None:
        """
        VBA Call
        --------
        FieldSource.SourceName(field_type)
        """
        self.record_method('SourceName', str(getattr(field_type, 'value', field_type)))

    def set_field_monitor_name(self, name: Union[FieldMonitorName, str]) -> None:
        """
        VBA Call
        --------
        FieldSource.FieldMonitorName(name)
        """
        self.record_method('FieldMonitorName', str(getattr(name, 'value', name)))

    def set_import_setting(self, key: Union[ImportSettingsKey, str], value: str) -> None:
        """
        VBA Call
        --------
        FieldSource.ImportSettings(key, value)
        """
        self.record_method('ImportSettings', str(getattr(key, 'value', key)), value)

    def set_time_value(self, time: float) -> None:
        """
        VBA Call
        --------
        FieldSource.TimeValue(time)
        """
        self.record_method('TimeValue', time)

    def set_use_last_time_frame(self, flag: bool) -> None:
        """
        VBA Call
        --------
        FieldSource.UseLastTimeFrame(flag)
        """
        self.record_method('UseLastTimeFrame', flag)

    def set_use_copy_only(self, flag: bool) -> None:
        """
        VBA Call
        --------
        FieldSource.UseCopyOnly(flag)
        """
        self.record_method('UseCopyOnly', flag)

    def create_field_import(self) -> None:
        """
        VBA Call
        --------
        FieldSource.CreateFieldImport()
        """
        self.record_method('CreateFieldImport')

    def create_field_import_from_abaqus(self, name: str, dir: str, nastran_file_name: str, distribution_file_name: str, geom_unit: str, temp_unit: str) -> None:
        """
        VBA Call
        --------
        FieldSource.CreateFieldImportFromAbaqus(name, dir, nastran_file_name, distribution_file_name, geom_unit, temp_unit)
        """
        self.record_method('CreateFieldImportFromAbaqus', name, dir, nastran_file_name, distribution_file_name, geom_unit, temp_unit)

