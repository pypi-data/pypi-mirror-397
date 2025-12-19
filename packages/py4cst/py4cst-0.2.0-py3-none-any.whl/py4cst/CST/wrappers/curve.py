'''This file is auto-generated. Do not edit.'''
from .. import IVBAProvider, VBATypeName, VBAObjWrapper
from typing import Union, Tuple, Optional
from enum import Enum

class Curve(VBAObjWrapper):
    class IterationType(Enum):
        ALL = 'all'
        OPEN = 'open'
        CLOSED = 'closed'

    def __init__(self, vbap: IVBAProvider) -> None:
        super().__init__(vbap, 'Curve')
        self.set_save_history(False)

    def new_curve(self, name: str) -> None:
        """
        VBA Call
        --------
        Curve.NewCurve(name)
        """
        self.record_method('NewCurve', name)

    def delete_curve(self, name: str) -> None:
        """
        VBA Call
        --------
        Curve.DeleteCurve(name)
        """
        self.record_method('DeleteCurve', name)

    def rename_curve(self, old_name: str, new_name: str) -> None:
        """
        VBA Call
        --------
        Curve.RenameCurve(old_name, new_name)
        """
        self.record_method('RenameCurve', old_name, new_name)

    def delete_curve_item(self, curve_name: str, item_name: str) -> None:
        """
        VBA Call
        --------
        Curve.DeleteCurveItem(curve_name, item_name)
        """
        self.record_method('DeleteCurveItem', curve_name, item_name)

    def rename_curve_item(self, curve_name: str, old_item_name: str, new_item_name: str) -> None:
        """
        VBA Call
        --------
        Curve.RenameCurveItem(curve_name, old_item_name, new_item_name)
        """
        self.record_method('RenameCurveItem', curve_name, old_item_name, new_item_name)

    def delete_curve_item_segment(self, curve_name: str, edge_id: int) -> None:
        """
        VBA Call
        --------
        Curve.DeleteCurveItemSegment(curve_name, edge_id)
        """
        self.record_method('DeleteCurveItemSegment', curve_name, edge_id)

    def move_curve_item(self, item_name: str, old_curve_name: str, new_curve_name: str) -> None:
        """
        VBA Call
        --------
        Curve.MoveCurveItem(item_name, old_curve_name, new_curve_name)
        """
        self.record_method('MoveCurveItem', item_name, old_curve_name, new_curve_name)

    def start_curve_name_iteration(self, it_type: Union[IterationType, str]) -> None:
        """
        VBA Call
        --------
        Curve.StartCurveNameIteration(it_type)
        """
        self.record_method('StartCurveNameIteration', str(getattr(it_type, 'value', it_type)))

    def get_next_curve_name(self) -> str:
        """
        VBA Call
        --------
        Curve.GetNextCurveName()
        """
        return self.query_method_str('GetNextCurveName')

    def get_point_coordinates(self, item_name: str, pid: str) -> Optional[Tuple]:
        """
        VBA Call
        --------
        Curve.GetPointCoordinates(item_name, pid, &x, &y, &z)

        Returns
        -------
        coordinates
            (x, y, z) *on success* | None
        """
        __retval__ = self.query_method_t('GetPointCoordinates', VBATypeName.Boolean, item_name, pid, VBATypeName.Double, VBATypeName.Double, VBATypeName.Double)
        return None if not __retval__[0] else tuple(__retval__[1:])

    def get_number_of_points(self) -> int:
        """
        VBA Call
        --------
        Curve.GetNumberOfPoints()
        """
        return self.query_method_int('GetNumberOfPoints')

    def is_closed(self, item_name: str) -> bool:
        """
        VBA Call
        --------
        Curve.IsClosed(item_name)
        """
        return self.query_method_bool('IsClosed', item_name)

