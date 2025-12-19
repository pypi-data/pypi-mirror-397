'''This file is auto-generated. Do not edit.'''
from .. import IVBAProvider, VBATypeName, VBAObjWrapper
from typing import Union, Tuple, Optional
from enum import Enum

class WCS(VBAObjWrapper):
    class Mode(Enum):
        GLOBAL = 'global'
        LOCAL = 'local'

    class AlignMode(Enum):
        POINT = 'Point'
        THREE_POINTS = '3Points'
        EDGE = 'Edge'
        EDGE_CENTER = 'EdgeCenter'
        ROTATION_EDGE = 'RotationEdge'
        FACE = 'Face'
        EDGE_AND_FACE = 'EdgeAndFace'

    class Axis(Enum):
        U = 'u'
        V = 'v'
        W = 'w'

    def __init__(self, vbap: IVBAProvider) -> None:
        super().__init__(vbap, 'WCS')
        self.set_save_history(False)

    def set_mode(self, mode: Union[Mode, str]) -> None:
        """
        VBA Call
        --------
        WCS.ActivateWCS(mode)
        """
        self.record_method('ActivateWCS', str(getattr(mode, 'value', mode)))

    def store(self, name: str) -> None:
        """
        VBA Call
        --------
        WCS.Store(name)
        """
        self.record_method('Store', name)

    def restore(self, name: str) -> None:
        """
        VBA Call
        --------
        WCS.Restore(name)
        """
        self.record_method('Restore', name)

    def delete(self, name: str) -> None:
        """
        VBA Call
        --------
        WCS.Delete(name)
        """
        self.record_method('Delete', name)

    def rename(self, old_name: str, new_name: str) -> None:
        """
        VBA Call
        --------
        WCS.Rename(old_name, new_name)
        """
        self.record_method('Rename', old_name, new_name)

    def set_normal(self, coords: Tuple[float, float, float]) -> None:
        """
        VBA Call
        --------
        WCS.SetNormal(coords[0], coords[1], coords[2])
        """
        self.record_method('SetNormal', coords[0], coords[1], coords[2])

    def set_origin(self, coords: Tuple[float, float, float]) -> None:
        """
        VBA Call
        --------
        WCS.SetOrigin(coords[0], coords[1], coords[2])
        """
        self.record_method('SetOrigin', coords[0], coords[1], coords[2])

    def set_u_vector(self, coords: Tuple[float, float, float]) -> None:
        """
        VBA Call
        --------
        WCS.SetUVector(coords[0], coords[1], coords[2])
        """
        self.record_method('SetUVector', coords[0], coords[1], coords[2])

    def align_wcs_with_selected(self, mode: Union[AlignMode, str]) -> None:
        """
        VBA Call
        --------
        WCS.AlignWCSWithSelected(mode)
        """
        self.record_method('AlignWCSWithSelected', str(getattr(mode, 'value', mode)))

    def rotate_wcs_deg(self, axis: Union[Axis, str], angle_deg: float) -> None:
        """
        VBA Call
        --------
        WCS.RotateWCS(axis, angle_deg)
        """
        self.record_method('RotateWCS', str(getattr(axis, 'value', axis)), angle_deg)

    def move_wcs(self, mode: Union[Mode, str], delta: Tuple[float, float, float]) -> None:
        """
        VBA Call
        --------
        WCS.MoveWCS(mode, delta[0], delta[1], delta[2])
        """
        self.record_method('MoveWCS', str(getattr(mode, 'value', mode)), delta[0], delta[1], delta[2])

    def align_wcs_with_global_coordinates(self) -> None:
        """
        VBA Call
        --------
        WCS.AlignWCSWithGlobalCoordinates()
        """
        self.record_method('AlignWCSWithGlobalCoordinates')

    def set_workplane_size(self, size: float) -> None:
        """
        VBA Call
        --------
        WCS.SetWorkplaneSize(size)
        """
        self.record_method('SetWorkplaneSize', size)

    def set_workplane_raster(self, raster_size: float) -> None:
        """
        VBA Call
        --------
        WCS.SetWorkplaneRaster(raster_size)
        """
        self.record_method('SetWorkplaneRaster', raster_size)

    def set_workplane_snap(self, flag: bool = True) -> None:
        """
        VBA Call
        --------
        WCS.SetWorkplaneSnap(flag)
        """
        self.record_method('SetWorkplaneSnap', flag)

    def set_workplane_autoadjust(self, flag: bool = True) -> None:
        """
        VBA Call
        --------
        WCS.SetWorkplaneAutoadjust(flag)
        """
        self.record_method('SetWorkplaneAutoadjust', flag)

    def set_workplane_snap_autoadjust(self, flag: bool = True) -> None:
        """
        VBA Call
        --------
        WCS.SetWorkplaneSnapAutoadjust(flag)
        """
        self.record_method('SetWorkplaneSnapAutoadjust', flag)

    def set_workplane_autosnap_factor(self, factor: float) -> None:
        """
        VBA Call
        --------
        WCS.SetWorkplaneAutosnapFactor(factor)
        """
        self.record_method('SetWorkplaneAutosnapFactor', factor)

    def set_workplane_snap_raster(self, raster_size: float) -> None:
        """
        VBA Call
        --------
        WCS.SetWorkplaneSnapRaster(raster_size)
        """
        self.record_method('SetWorkplaneSnapRaster', raster_size)

    def get_mode(self) -> Mode:
        """
        VBA Call
        --------
        WCS.IsWCSActive()
        """
        __retval__ = self.query_method_str('IsWCSActive')
        return WCS.Mode(__retval__)

    def does_exist(self, wcs_name: str) -> bool:
        """
        VBA Call
        --------
        WCS.DoesExist(wcs_name)
        """
        return self.query_method_bool('DoesExist', wcs_name)

    def get_origin(self, wcs_name: str) -> Optional[Tuple]:
        """
        VBA Call
        --------
        WCS.GetOrigin(wcs_name, &x, &y, &z)

        Returns
        -------
        coordinates
            (x, y, z) *on success* | None
        """
        __retval__ = self.query_method_t('GetOrigin', VBATypeName.Boolean, wcs_name, VBATypeName.Double, VBATypeName.Double, VBATypeName.Double)
        return None if not __retval__[0] else tuple(__retval__[1:])

    def get_normal(self, wcs_name: str) -> Optional[Tuple]:
        """
        VBA Call
        --------
        WCS.GetNormal(wcs_name, &x, &y, &z)

        Returns
        -------
        coordinates
            (x, y, z) *on success* | None
        """
        __retval__ = self.query_method_t('GetNormal', VBATypeName.Boolean, wcs_name, VBATypeName.Double, VBATypeName.Double, VBATypeName.Double)
        return None if not __retval__[0] else tuple(__retval__[1:])

    def get_u_vector(self, wcs_name: str) -> Optional[Tuple]:
        """
        VBA Call
        --------
        WCS.GetUVector(wcs_name, &x, &y, &z)

        Returns
        -------
        coordinates
            (x, y, z) *on success* | None
        """
        __retval__ = self.query_method_t('GetUVector', VBATypeName.Boolean, wcs_name, VBATypeName.Double, VBATypeName.Double, VBATypeName.Double)
        return None if not __retval__[0] else tuple(__retval__[1:])

    def get_affine_matrix_uvw_to_xyz(self, wcs_name: str) -> Optional[Tuple]:
        """
        VBA Call
        --------
        WCS.GetAffineMatrixUVW2XYZ(wcs_name, &ux, &uy, &uz, &vx, &vy, &vz, &wx, &wy, &wz)

        Returns
        -------
        coordinates
            (ux, uy, uz, vx, vy, vz, wx, wy, wz) *on success* | None
        """
        __retval__ = self.query_method_t('GetAffineMatrixUVW2XYZ', VBATypeName.Boolean, wcs_name, VBATypeName.Double, VBATypeName.Double, VBATypeName.Double, VBATypeName.Double, VBATypeName.Double, VBATypeName.Double, VBATypeName.Double, VBATypeName.Double, VBATypeName.Double)
        return None if not __retval__[0] else tuple(__retval__[1:])

    def get_affine_matrix_xyz_to_uvw(self, wcs_name: str) -> Optional[Tuple]:
        """
        VBA Call
        --------
        WCS.GetAffineMatrixXYZ2UVW(wcs_name, &ux, &uy, &uz, &vx, &vy, &vz, &wx, &wy, &wz)

        Returns
        -------
        coordinates
            (ux, uy, uz, vx, vy, vz, wx, wy, wz) *on success* | None
        """
        __retval__ = self.query_method_t('GetAffineMatrixXYZ2UVW', VBATypeName.Boolean, wcs_name, VBATypeName.Double, VBATypeName.Double, VBATypeName.Double, VBATypeName.Double, VBATypeName.Double, VBATypeName.Double, VBATypeName.Double, VBATypeName.Double, VBATypeName.Double)
        return None if not __retval__[0] else tuple(__retval__[1:])

    def get_wcs_point_from_global(self, wcs_name: str, x: float, y: float, z: float) -> Optional[Tuple]:
        """
        VBA Call
        --------
        WCS.GetWCSPointFromGlobal(wcs_name, &u, &v, &w, x, y, z)

        Returns
        -------
        coordinates
            (u, v, w) *on success* | None
        """
        __retval__ = self.query_method_t('GetWCSPointFromGlobal', VBATypeName.Boolean, wcs_name, VBATypeName.Double, VBATypeName.Double, VBATypeName.Double, x, y, z)
        return None if not __retval__[0] else tuple(__retval__[1:])

    def get_global_point_from_wcs(self, wcs_name: str, u: float, v: float, w: float) -> Optional[Tuple]:
        """
        VBA Call
        --------
        WCS.GetGlobalPointFromWCS(wcs_name, &x, &y, &z, u, v, w)

        Returns
        -------
        coordinates
            (x, y, z) *on success* | None
        """
        __retval__ = self.query_method_t('GetGlobalPointFromWCS', VBATypeName.Boolean, wcs_name, VBATypeName.Double, VBATypeName.Double, VBATypeName.Double, u, v, w)
        return None if not __retval__[0] else tuple(__retval__[1:])

