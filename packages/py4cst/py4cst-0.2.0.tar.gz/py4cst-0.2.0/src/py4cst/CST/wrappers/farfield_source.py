'''This file is auto-generated. Do not edit.'''
from .. import IVBAProvider, VBAObjWrapper
from enum import Enum
from typing import Union, Tuple

class FarfieldSource(VBAObjWrapper):
    class AlignmentType(Enum):
        USER = 'user'
        CURRENT_WCS = 'currentwcs'
        SOURCE_FILE = 'sourcefile'

    class MultipoleCalcMode(Enum):
        AUTOMATIC = 'automatic'
        USER_DEFINED = 'user defined'
        AUTO_TRUNCATION = 'autotruncation'

    def __init__(self, vbap: IVBAProvider) -> None:
        super().__init__(vbap, 'FarfieldSource')
        self.set_save_history(False)

    def reset(self) -> None:
        """
        VBA Call
        --------
        FarfieldSource.Reset()
        """
        self.cache_method('Reset')

    def set_name(self, name: str) -> None:
        """
        VBA Call
        --------
        FarfieldSource.Name(name)
        """
        self.cache_method('Name', name)

    def set_id(self, id: int) -> None:
        """
        VBA Call
        --------
        FarfieldSource.Id(id)
        """
        self.cache_method('Id', id)

    def set_position(self, pos: Tuple[float, float, float]) -> None:
        """
        VBA Call
        --------
        FarfieldSource.SetPosition(pos[0], pos[1], pos[2])
        """
        self.cache_method('SetPosition', pos[0], pos[1], pos[2])

    def set_phi0_vec(self, vec: Tuple[float, float, float]) -> None:
        """
        VBA Call
        --------
        FarfieldSource.SetPhi0XYZ(vec[0], vec[1], vec[2])
        """
        self.cache_method('SetPhi0XYZ', vec[0], vec[1], vec[2])

    def set_theta0_vec(self, vec: Tuple[float, float, float]) -> None:
        """
        VBA Call
        --------
        FarfieldSource.SetTheta0XYZ(vec[0], vec[1], vec[2])
        """
        self.cache_method('SetTheta0XYZ', vec[0], vec[1], vec[2])

    def import_from_file(self, file_path: str) -> None:
        """
        VBA Call
        --------
        FarfieldSource.Import(file_path)
        """
        self.cache_method('Import', file_path)

    def set_use_copy_only(self, flag: bool = True) -> None:
        """
        VBA Call
        --------
        FarfieldSource.UseCopyOnly(flag)
        """
        self.cache_method('UseCopyOnly', flag)

    def set_use_multipole_ffs(self, flag: bool = True) -> None:
        """
        VBA Call
        --------
        FarfieldSource.UseMultipoleFFS(flag)
        """
        self.cache_method('UseMultipoleFFS', flag)

    def set_alignment_type(self, alignment_type: Union[AlignmentType, str]) -> None:
        """
        VBA Call
        --------
        FarfieldSource.SetAlignmentType(alignment_type)
        """
        self.cache_method('SetAlignmentType', str(getattr(alignment_type, 'value', alignment_type)))

    def set_multipole_degree(self, degree: int) -> None:
        """
        VBA Call
        --------
        FarfieldSource.SetMultipoleDegree(degree)
        """
        self.cache_method('SetMultipoleDegree', degree)

    def set_multipole_calc_mode(self, mode: Union[MultipoleCalcMode, str]) -> None:
        """
        VBA Call
        --------
        FarfieldSource.SetMultipoleCalcMode(mode)
        """
        self.cache_method('SetMultipoleCalcMode', str(getattr(mode, 'value', mode)))

    def store(self) -> None:
        """
        VBA Call
        --------
        FarfieldSource.Store()
        """
        self.cache_method('Store')
        self.flush_cache('Store FarfieldSource')

    def delete(self) -> None:
        """
        VBA Call
        --------
        FarfieldSource.Delete()
        """
        self.record_method('Delete')

    def delete_all(self) -> None:
        """
        VBA Call
        --------
        FarfieldSource.DeleteAll()
        """
        self.record_method('DeleteAll')

    def get_next_id(self) -> int:
        """
        VBA Call
        --------
        FarfieldSource.GetNextId()
        """
        return self.query_method_int('GetNextId')

