'''This file is auto-generated. Do not edit.'''
from .. import IVBAProvider, VBAObjWrapper
from enum import Enum
from typing import Union

class LayerStacking(VBAObjWrapper):
    class Direction(Enum):
        X = 'x'
        Y = 'y'
        Z = 'z'

    def __init__(self, vbap: IVBAProvider) -> None:
        super().__init__(vbap, 'LayerStacking')
        self.set_save_history(False)

    def reset(self) -> None:
        """
        VBA Call
        --------
        LayerStacking.Reset()
        """
        self.record_method('Reset')

    def set_layer_stacking_active(self, flag: bool) -> None:
        """
        VBA Call
        --------
        LayerStacking.LayerStackingActive(flag)
        """
        self.record_method('LayerStackingActive', flag)

    def set_background_items_align_value(self, value: float) -> None:
        """
        VBA Call
        --------
        LayerStacking.AlignValueBackgroundItems(value)
        """
        self.record_method('AlignValueBackgroundItems', value)

    def set_background_items_normal(self, direction: Union[Direction, str]) -> None:
        """
        VBA Call
        --------
        LayerStacking.NormalBackgroundItems(direction)
        """
        self.record_method('NormalBackgroundItems', str(getattr(direction, 'value', direction)))

    def set_invert_direction(self, flag: bool) -> None:
        """
        VBA Call
        --------
        LayerStacking.InvertDirection(flag)
        """
        self.record_method('InvertDirection', flag)

    def set_fix_traversal(self, flag: bool) -> None:
        """
        VBA Call
        --------
        LayerStacking.FixTransversal(flag)
        """
        self.record_method('FixTransversal', flag)

    def add_item(self, index: int, height: float, material_name: str) -> None:
        """
        VBA Call
        --------
        LayerStacking.AddItem(index, height, material_name)
        """
        self.record_method('AddItem', index, height, material_name)

