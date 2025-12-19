'''This file is auto-generated. Do not edit.'''
from .. import IVBAProvider, VBAObjWrapper

class STL(VBAObjWrapper):


    def __init__(self, vbap: IVBAProvider) -> None:
        super().__init__(vbap, 'STL')
        self.set_save_history(False)

    def reset(self) -> None:
        """
        VBA Call
        --------
        STL.Reset()
        """
        self.record_method('Reset')

    def set_file_name(self, file_name: str) -> None:
        """
        VBA Call
        --------
        STL.FileName(file_name)
        """
        self.record_method('FileName', file_name)

    def set_name(self, name: str) -> None:
        """
        VBA Call
        --------
        STL.Name(name)
        """
        self.record_method('Name', name)

    def set_component(self, name: str) -> None:
        """
        VBA Call
        --------
        STL.Component(name)
        """
        self.record_method('Component', name)

    def set_scale_to_unit(self, flag: bool = True) -> None:
        """
        VBA Call
        --------
        STL.ScaleToUnit(flag)
        """
        self.record_method('ScaleToUnit', flag)

    def set_import_file_units(self, units: str) -> None:
        """
        VBA Call
        --------
        STL.ImportFileUnits(units)
        """
        self.record_method('ImportFileUnits', units)

    def set_export_from_active_coordinate_system(self, flag: bool = True) -> None:
        """
        VBA Call
        --------
        STL.ExportFromActiveCoordinateSystem(flag)
        """
        self.record_method('ExportFromActiveCoordinateSystem', flag)

    def set_import_to_active_coordinate_system(self, flag: bool = True) -> None:
        """
        VBA Call
        --------
        STL.ImportToActiveCoordinateSystem(flag)
        """
        self.record_method('ImportToActiveCoordinateSystem', flag)

    def set_export_file_units(self, units: str) -> None:
        """
        VBA Call
        --------
        STL.ExportFileUnits(units)
        """
        self.record_method('ExportFileUnits', units)

    def set_normal_tolerance(self, tolerance: float) -> None:
        """
        VBA Call
        --------
        STL.NormalTolerance(tolerance)
        """
        self.record_method('NormalTolerance', tolerance)

    def set_surface_tolerance(self, tolerance: float) -> None:
        """
        VBA Call
        --------
        STL.SurfaceTolerance(tolerance)
        """
        self.record_method('SurfaceTolerance', tolerance)

    def read(self) -> None:
        """
        VBA Call
        --------
        STL.Read()
        """
        self.record_method('Read')

    def write(self) -> None:
        """
        VBA Call
        --------
        STL.Write()
        """
        self.record_method('Write')

