'''This file is auto-generated. Do not edit.'''
from .. import IVBAProvider, VBAObjWrapper
from enum import Enum
from typing import Union, Tuple

class Transform(VBAObjWrapper):
    class What(Enum):
        SHAPE = 'Shape'
        ANCHORPOINT = 'Anchorpoint'
        FACE = 'Face'
        MESHSHAPE = 'Meshshape'
        PROBE = 'Probe'
        VOXELDATA = 'Voxeldata'
        MIXED = 'mixed'
        FFS = 'FFS'
        HF_3D_MONITOR = 'HF3DMonitor'
        PORT = 'Port'
        LUMPED_ELEMENT = 'Lumpedelement'
        CURRENT_DISTRIBUTION = 'Currentdistribution'
        COIL = 'Coil'
        CURRENT_MONITOR = 'currentmonitor'
        CURRENT_WIRE = 'currentwire'
        VOLTAGE_MONITOR = 'voltagemonitor'
        VOLTAGE_WIRE = 'voltagewire'

    class How(Enum):
        TRANSLATE = 'Translate'
        ROTATE = 'Rotate'
        SCALE = 'Scale'
        MIRROR = 'Mirror'
        MATRIX = 'Matrix'
        LOCAL_TO_GLOBAL = 'LocalToGlobal'
        GLOBAL_TO_LOCAL = 'GlobalToLocal'

    class Origin(Enum):
        SHAPE_CENTER = 'ShapeCenter'
        COMMON_CENTER = 'CommonCenter'
        FREE = 'Free'

    def __init__(self, vbap: IVBAProvider) -> None:
        super().__init__(vbap, 'Transform')
        self.set_save_history(False)

    def reset(self) -> None:
        """
        VBA Call
        --------
        Transform.Reset()
        """
        self.cache_method('Reset')

    def set_name(self, name: str) -> None:
        """
        VBA Call
        --------
        Transform.Name(name)
        """
        self.cache_method('Name', name)

    def add_name(self, name: str) -> None:
        """
        VBA Call
        --------
        Transform.AddName(name)
        """
        self.cache_method('AddName', name)

    def translate_curve(self) -> None:
        """
        VBA Call
        --------
        Transform.TranslateCurve()
        """
        self.cache_method('TranslateCurve')
        self.flush_cache('Transform: TranslateCurve')

    def scale_curve(self) -> None:
        """
        VBA Call
        --------
        Transform.ScaleCurve()
        """
        self.cache_method('ScaleCurve')
        self.flush_cache('Transform: ScaleCurve')

    def rotate_curve(self) -> None:
        """
        VBA Call
        --------
        Transform.RotateCurve()
        """
        self.cache_method('RotateCurve')
        self.flush_cache('Transform: RotateCurve')

    def mirror_curve(self) -> None:
        """
        VBA Call
        --------
        Transform.MirrorCurve()
        """
        self.cache_method('MirrorCurve')
        self.flush_cache('Transform: MirrorCurve')

    def translate_wire(self) -> None:
        """
        VBA Call
        --------
        Transform.TranslateWire()
        """
        self.cache_method('TranslateWire')
        self.flush_cache('Transform: TranslateWire')

    def scale_wire(self) -> None:
        """
        VBA Call
        --------
        Transform.ScaleWire()
        """
        self.cache_method('ScaleWire')
        self.flush_cache('Transform: ScaleWire')

    def rotate_wire(self) -> None:
        """
        VBA Call
        --------
        Transform.RotateWire()
        """
        self.cache_method('RotateWire')
        self.flush_cache('Transform: RotateWire')

    def mirror_wire(self) -> None:
        """
        VBA Call
        --------
        Transform.MirrorWire()
        """
        self.cache_method('MirrorWire')
        self.flush_cache('Transform: MirrorWire')

    def translate_coil(self) -> None:
        """
        VBA Call
        --------
        Transform.TranslateCoil()
        """
        self.cache_method('TranslateCoil')
        self.flush_cache('Transform: TranslateCoil')

    def scale_coil(self) -> None:
        """
        VBA Call
        --------
        Transform.ScaleCoil()
        """
        self.cache_method('ScaleCoil')
        self.flush_cache('Transform: ScaleCoil')

    def rotate_coil(self) -> None:
        """
        VBA Call
        --------
        Transform.RotateCoil()
        """
        self.cache_method('RotateCoil')
        self.flush_cache('Transform: RotateCoil')

    def mirror_coil(self) -> None:
        """
        VBA Call
        --------
        Transform.MirrorCoil()
        """
        self.cache_method('MirrorCoil')
        self.flush_cache('Transform: MirrorCoil')

    def transform(self, what: Union[What, str], how: Union[How, str]) -> None:
        """
        VBA Call
        --------
        Transform.Transform(what, how)
        """
        self.cache_method('Transform', str(getattr(what, 'value', what)), str(getattr(how, 'value', how)))
        self.flush_cache('Transform')

    def set_use_picked_points(self, flag: bool = True) -> None:
        """
        VBA Call
        --------
        Transform.UsePickedPoints(flag)
        """
        self.cache_method('UsePickedPoints', flag)

    def set_invert_picked_points(self, flag: bool = True) -> None:
        """
        VBA Call
        --------
        Transform.InvertPickedPoints(flag)
        """
        self.cache_method('InvertPickedPoints', flag)

    def set_multiple_objects(self, flag: bool = True) -> None:
        """
        VBA Call
        --------
        Transform.MultipleObjects(flag)
        """
        self.cache_method('MultipleObjects', flag)

    def set_group_objects(self, flag: bool = True) -> None:
        """
        VBA Call
        --------
        Transform.GroupObjects(flag)
        """
        self.cache_method('GroupObjects', flag)

    def set_origin(self, key: Union[Origin, str]) -> None:
        """
        VBA Call
        --------
        Transform.Origin(key)
        """
        self.cache_method('Origin', str(getattr(key, 'value', key)))

    def set_center(self, uvw: Tuple[float, float, float]) -> None:
        """
        VBA Call
        --------
        Transform.Center(uvw[0], uvw[1], uvw[2])
        """
        self.cache_method('Center', uvw[0], uvw[1], uvw[2])

    def set_vector(self, uvw: Tuple[float, float, float]) -> None:
        """
        VBA Call
        --------
        Transform.Vector(uvw[0], uvw[1], uvw[2])
        """
        self.cache_method('Vector', uvw[0], uvw[1], uvw[2])

    def set_scale_factor(self, uvw_factors: Tuple[float, float, float]) -> None:
        """
        VBA Call
        --------
        Transform.ScaleFactor(uvw_factors[0], uvw_factors[1], uvw_factors[2])
        """
        self.cache_method('ScaleFactor', uvw_factors[0], uvw_factors[1], uvw_factors[2])

    def set_angle(self, uvw_angles: Tuple[float, float, float]) -> None:
        """
        VBA Call
        --------
        Transform.Angle(uvw_angles[0], uvw_angles[1], uvw_angles[2])
        """
        self.cache_method('Angle', uvw_angles[0], uvw_angles[1], uvw_angles[2])

    def set_plane_normal(self, uvw_normal: Tuple[float, float, float]) -> None:
        """
        VBA Call
        --------
        Transform.PlaneNormal(uvw_normal[0], uvw_normal[1], uvw_normal[2])
        """
        self.cache_method('PlaneNormal', uvw_normal[0], uvw_normal[1], uvw_normal[2])

    def set_matrix(self, c11: float, c12: float, c13: float, c21: float, c22: float, c23: float, c31: float, c32: float, c33: float) -> None:
        """
        VBA Call
        --------
        Transform.Matrix(c11, c12, c13, c21, c22, c23, c31, c32, c33)
        """
        self.cache_method('Matrix', c11, c12, c13, c21, c22, c23, c31, c32, c33)

    def set_number_of_repetitions(self, count: int) -> None:
        """
        VBA Call
        --------
        Transform.Repetitions(count)
        """
        self.cache_method('Repetitions', count)

    def set_component(self, name: str) -> None:
        """
        VBA Call
        --------
        Transform.Component(name)
        """
        self.cache_method('Component', name)

    def set_material(self, name: str) -> None:
        """
        VBA Call
        --------
        Transform.Material(name)
        """
        self.cache_method('Material', name)

    def set_multiple_selection(self, flag: bool = True) -> None:
        """
        VBA Call
        --------
        Transform.MultipleSelection(flag)
        """
        self.cache_method('MultipleSelection', flag)

    def set_destination(self, destination: str) -> None:
        """
        VBA Call
        --------
        Transform.Destination(destination)
        """
        self.cache_method('Destination', destination)

    def set_auto_destination(self, flag: bool = True) -> None:
        """
        VBA Call
        --------
        Transform.AutoDestination(flag)
        """
        self.cache_method('AutoDestination', flag)

    def set_touch(self, flag: bool = True) -> None:
        """
        VBA Call
        --------
        Transform.Touch(flag)
        """
        self.cache_method('Touch', flag)

    def add_name_to_active_touch_set(self, name: str) -> None:
        """
        VBA Call
        --------
        Transform.AddNameToActiveTouchSet(name)
        """
        self.cache_method('AddNameToActiveTouchSet', name)

    def add_name_to_passive_touch_set(self, name: str) -> None:
        """
        VBA Call
        --------
        Transform.AddNameToPassiveTouchSet(name)
        """
        self.cache_method('AddNameToPassiveTouchSet', name)

    def set_touch_tolerance(self, tolerance: float) -> None:
        """
        VBA Call
        --------
        Transform.TouchTolerance(tolerance)
        """
        self.cache_method('TouchTolerance', tolerance)

    def set_touch_max_num_iterations(self, count: int) -> None:
        """
        VBA Call
        --------
        Transform.TouchMaxIterations(count)
        """
        self.cache_method('TouchMaxIterations', count)

    def set_touch_heuristic(self, flag: bool = True) -> None:
        """
        VBA Call
        --------
        Transform.TouchHeuristic(flag)
        """
        self.cache_method('TouchHeuristic', flag)

    def set_touch_offset(self, offset: float) -> None:
        """
        VBA Call
        --------
        Transform.TouchOffset(offset)
        """
        self.cache_method('TouchOffset', offset)

