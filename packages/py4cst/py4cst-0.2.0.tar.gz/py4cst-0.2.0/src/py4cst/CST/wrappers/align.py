'''This file is auto-generated. Do not edit.'''
from .. import IVBAProvider, VBAObjWrapper
from enum import Enum
from typing import Union

class Align(VBAObjWrapper):
    class AlignWhat(Enum):
        SHAPE = 'Shape'
        SUBPROJECT = 'Subproject'
        PART = 'Part'
        MIXED = 'Mixed'

    class AlignHow(Enum):
        FACES = 'Faces'
        ROTATE = 'Rotate'
        ROTATE_BY_DEGREE = 'RotateByDegree'

    class PickWhat(Enum):
        SOURCE_PLANE = 'SourcePlane'
        TARGET_PLANE = 'TargetPlane'
        ZERO_ANGLE = 'ZeroAngle'
        FINAL_ANGLE = 'FinalAngle'

    class PickKind(Enum):
        FACE = 'Face'
        EDGE = 'Edge'
        POINT = 'Point'

    class NumericalValue(Enum):
        ANGLE = 'Angle'

    def __init__(self, vbap: IVBAProvider) -> None:
        super().__init__(vbap, 'Align')
        self.set_save_history(False)

    def reset(self) -> None:
        """
        VBA Call
        --------
        Align.Reset()
        """
        self.record_method('Reset')

    def set_name(self, name: str) -> None:
        """
        VBA Call
        --------
        Align.Name(name)
        """
        self.record_method('Name', name)

    def add_name(self, name: str) -> None:
        """
        VBA Call
        --------
        Align.AddName(name)
        """
        self.record_method('AddName', name)

    def align(self, what: Union[AlignWhat, str], how: Union[AlignHow, str]) -> None:
        """
        VBA Call
        --------
        Align.Align(what, how)
        """
        self.record_method('Align', str(getattr(what, 'value', what)), str(getattr(how, 'value', how)))

    def set_kind_of_pick_for(self, what: Union[PickWhat, str], kind: Union[PickKind, str]) -> None:
        """
        VBA Call
        --------
        Align.SetKindOfPickFor(what, kind)
        """
        self.record_method('SetKindOfPickFor', str(getattr(what, 'value', what)), str(getattr(kind, 'value', kind)))

    def set_name_to_step(self, what: Union[PickWhat, str], name: str) -> None:
        """
        VBA Call
        --------
        Align.SetNameToStep(what, name)
        """
        self.record_method('SetNameToStep', str(getattr(what, 'value', what)), name)

    def set_numerical_value(self, what: Union[NumericalValue, str], value: float) -> None:
        """
        VBA Call
        --------
        Align.SetNumericalValue(what, value)
        """
        self.record_method('SetNumericalValue', str(getattr(what, 'value', what)), value)

    def set_opposite_face_orientation(self, flag: bool = True) -> None:
        """
        VBA Call
        --------
        Align.SetOppositeFaceOrientation(flag)
        """
        self.record_method('SetOppositeFaceOrientation', flag)

    def set_clear_subproject_import_info(self, flag: bool = True) -> None:
        """
        VBA Call
        --------
        Align.ClearSubProjectImportInfo(flag)
        """
        self.record_method('ClearSubProjectImportInfo', flag)

