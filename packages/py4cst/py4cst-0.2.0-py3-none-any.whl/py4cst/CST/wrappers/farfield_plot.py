'''This file is auto-generated. Do not edit.'''
from .. import IVBAProvider, VBATypeName, VBAObjWrapper
from enum import Enum
from typing import Union, Tuple, Optional

class FarfieldPlot(VBAObjWrapper):
    class PlotType(Enum):
        POLAR = 'polar'
        CARTESIAN = 'cartesian'
        TWO_D = '2d'
        TWO_D_ORTHO = '2dortho'
        THREE_D = '3d'

    class AngleVariant(Enum):
        ANGLE_1 = 'angle1'
        ANGLE_2 = 'angle2'

    class AsciiVersion(Enum):
        V2009 = '2009'
        V2010 = '2010'

    class CoordSystem(Enum):
        SPHERICAL = 'spherical'
        LUDWIG_2_AE = 'ludwig2ae'
        LUDWIG_2_EA = 'ludwig2ea'
        LUDWIG_3 = 'ludwig3'

    class Polarization(Enum):
        LINEAR = 'linear'
        CIRCULAR = 'circular'
        SLANT = 'slant'
        ABS = 'abs'

    class Component(Enum):
        RADIAL = 'radial'
        COMP_1 = 'comp1'
        THETA = 'theta'
        AZIMUTH = 'azimuth'
        LEFT = 'left'
        ALPHA = 'alpha'
        HORIZONTAL = 'horizontal'
        CROSSPOLAR = 'crosspolar'
        COMP_2 = 'comp2'
        PHI = 'phi'
        ELEVATION = 'elevation'
        RIGHT = 'right'
        EPSILON = 'epsilon'
        VERTICAL = 'vertical'
        COPOLAR = 'copolar'

    class ComplexComponent(Enum):
        ABS = 'abs'
        PHASE = 'phase'
        RE = 're'
        IM = 'im'

    class TFType(Enum):
        TIME = 'time'
        FREQUENCY = 'frequency'
        DEFAULT = ''

    class ListFieldComponent(Enum):
        THETA = 'Point_T'
        PHI = 'Point_P'
        RADIUS = 'Point_R'

    class CutType(Enum):
        POLAR = 'polar'
        LATERAL = 'lateral'

    class PlotMode(Enum):
        DIRECTIVITY = 'directivity'
        GAIN = 'gain'
        REALIZED_GAIN = 'realized gain'
        EFIELD = 'efield'
        EPATTERN = 'epattern'
        HFIELD = 'hfield'
        PFIELD = 'pfield'
        RCS = 'rcs'
        RCS_UNITS = 'rcsunits'
        RCS_SW = 'rcssw'

    class SelComponent(Enum):
        ABS = 'Abs'
        AXIAL_RATIO = 'Axial Ratio'
        THETA = 'Theta'
        THETA_PHASE = 'Theta Phase'
        PHI = 'Phi'
        PHI_PHASE = 'Phi Phase'
        THETA_DIV_PHI = 'Theta/Phi'
        PHI_DIV_THETA = 'Phi/Theta'

    class UnitCode(Enum):
        V_MINUS_1 = '-1'
        V_0 = '0'
        V_60 = '60'
        V_120 = '120'
        V_MINUS_60 = '-60'

    class MaxRefMode(Enum):
        ABS = 'abs'
        PLOT = 'plot'

    class AxesType(Enum):
        XYZ = 'xyz'
        USER = 'user'
        MAIN_LOBE = 'mainlobe'
        CURRENT_WCS = 'currentwcs'

    class Axis(Enum):
        X = 'x'
        Y = 'y'
        Z = 'z'

    class AntennaType(Enum):
        UNKNOWN = 'unknown'
        ISOTROPIC = 'isotropic'
        ISOTROPIC_LINEAR = 'isotropic_linear'
        DIRECTIONAL_LINEAR = 'directional_linear'
        DIRECTIONAL_CIRCULAR = 'directional_circular'

    class PhaseCenterComponent(Enum):
        THETA = 'theta'
        PHI = 'phi'
        BORESIGHT = 'boresight'

    class PhaseCenterPlane(Enum):
        BOTH = 'both'
        E_PLANE = 'e-plane'
        H_PLANE = 'h-plane'

    class PhaseCenterMode(Enum):
        AVG = 'avg'
        EPLANE = 'eplane'
        HPLANE = 'hplane'

    class Origin(Enum):
        BOUNDING_BOX = 'bbox'
        ZERO = 'zero'
        FREE = 'free'

    def __init__(self, vbap: IVBAProvider) -> None:
        super().__init__(vbap, 'FarfieldPlot')
        self.set_save_history(False)

    def reset(self) -> None:
        """
        VBA Call
        --------
        FarfieldPlot.Reset()
        """
        self.record_method('Reset')

    def reset_plot(self) -> None:
        """
        VBA Call
        --------
        FarfieldPlot.ResetPlot()
        """
        self.record_method('ResetPlot')

    def set_plot_type(self, plot_type: Union[PlotType, str]) -> None:
        """
        VBA Call
        --------
        FarfieldPlot.Plottype(plot_type)
        """
        self.record_method('Plottype', str(getattr(plot_type, 'value', plot_type)))

    def vary_coord(self, angle_variant: Union[AngleVariant, str]) -> None:
        """
        VBA Call
        --------
        FarfieldPlot.Vary(angle_variant)
        """
        self.record_method('Vary', str(getattr(angle_variant, 'value', angle_variant)))

    def set_phi_deg(self, angle_deg: float) -> None:
        """
        VBA Call
        --------
        FarfieldPlot.Phi(angle_deg)
        """
        self.record_method('Phi', angle_deg)

    def set_theta_deg(self, angle_deg: float) -> None:
        """
        VBA Call
        --------
        FarfieldPlot.Theta(angle_deg)
        """
        self.record_method('Theta', angle_deg)

    def set_theta_step_deg(self, angle_deg: float) -> None:
        """
        VBA Call
        --------
        FarfieldPlot.Step(angle_deg)
        """
        self.record_method('Step', angle_deg)

    def set_phi_step_deg(self, angle_deg: float) -> None:
        """
        VBA Call
        --------
        FarfieldPlot.Step2(angle_deg)
        """
        self.record_method('Step2', angle_deg)

    def set_lock_steps(self, flag: bool = True) -> None:
        """
        VBA Call
        --------
        FarfieldPlot.SetLockSteps(flag)
        """
        self.record_method('SetLockSteps', flag)

    def set_plot_range_only(self, flag: bool = True) -> None:
        """
        VBA Call
        --------
        FarfieldPlot.SetPlotRangeOnly(flag)
        """
        self.record_method('SetPlotRangeOnly', flag)

    def set_theta_start_deg(self, angle_deg: float) -> None:
        """
        VBA Call
        --------
        FarfieldPlot.SetThetaStart(angle_deg)
        """
        self.record_method('SetThetaStart', angle_deg)

    def set_theta_end_deg(self, angle_deg: float) -> None:
        """
        VBA Call
        --------
        FarfieldPlot.SetThetaEnd(angle_deg)
        """
        self.record_method('SetThetaEnd', angle_deg)

    def set_phi_start_deg(self, angle_deg: float) -> None:
        """
        VBA Call
        --------
        FarfieldPlot.SetPhiStart(angle_deg)
        """
        self.record_method('SetPhiStart', angle_deg)

    def set_phi_end_deg(self, angle_deg: float) -> None:
        """
        VBA Call
        --------
        FarfieldPlot.SetPhiEnd(angle_deg)
        """
        self.record_method('SetPhiEnd', angle_deg)

    def set_use_farfield_approximation(self, flag: bool = True) -> None:
        """
        VBA Call
        --------
        FarfieldPlot.UseFarfieldApproximation(flag)
        """
        self.record_method('UseFarfieldApproximation', flag)

    def set_multipoles_max_number(self, max_num: int) -> None:
        """
        VBA Call
        --------
        FarfieldPlot.SetMultipolNumber(max_num)
        """
        self.record_method('SetMultipolNumber', max_num)

    def set_frequency(self, freq: float) -> None:
        """
        VBA Call
        --------
        FarfieldPlot.SetFrequency(freq)
        """
        self.record_method('SetFrequency', freq)

    def set_time(self, time: float) -> None:
        """
        VBA Call
        --------
        FarfieldPlot.SetTime(time)
        """
        self.record_method('SetTime', time)

    def set_time_domain_farfield(self, flag: bool = True) -> None:
        """
        VBA Call
        --------
        FarfieldPlot.SetTimeDomainFF(flag)
        """
        self.record_method('SetTimeDomainFF', flag)

    def set_num_movie_samples(self, num: int) -> None:
        """
        VBA Call
        --------
        FarfieldPlot.SetMovieSamples(num)
        """
        self.record_method('SetMovieSamples', num)

    def plot(self) -> None:
        """
        VBA Call
        --------
        FarfieldPlot.Plot()
        """
        self.record_method('Plot')

    def store_settings(self) -> None:
        """
        VBA Call
        --------
        FarfieldPlot.StoreSettings()
        """
        self.record_method('StoreSettings')

    def export_summary_as_ascii(self, file_name: str) -> None:
        """
        VBA Call
        --------
        FarfieldPlot.ASCIIExportSummary(file_name)
        """
        self.record_method('ASCIIExportSummary', file_name)

    def set_ascii_export_version(self, version: Union[AsciiVersion, str]) -> None:
        """
        VBA Call
        --------
        FarfieldPlot.ASCIIExportVersion(version)
        """
        self.record_method('ASCIIExportVersion', str(getattr(version, 'value', version)))

    def export_source_as_ascii(self, file_name: str) -> None:
        """
        VBA Call
        --------
        FarfieldPlot.ASCIIExportAsSource(file_name)
        """
        self.record_method('ASCIIExportAsSource', file_name)

    def export_broadband_source_as_ascii(self, file_name: str) -> None:
        """
        VBA Call
        --------
        FarfieldPlot.ASCIIExportAsBroadbandSource(file_name)
        """
        self.record_method('ASCIIExportAsBroadbandSource', file_name)

    def copy_farfield_to_1d_results(self, result_folder: str, result_name: str) -> None:
        """
        VBA Call
        --------
        FarfieldPlot.CopyFarfieldTo1DResults(result_folder, result_name)
        """
        self.record_method('CopyFarfieldTo1DResults', result_folder, result_name)

    def include_unit_cell_sidewalls(self, flag: bool = True) -> None:
        """
        VBA Call
        --------
        FarfieldPlot.IncludeUnitCellSidewalls(flag)
        """
        self.record_method('IncludeUnitCellSidewalls', flag)

    def calculate_point_deg(self, theta_deg: float, phi_deg: float, farfield_name: str, coord_system: Optional[Union[CoordSystem, str]] = None, polarization: Optional[Union[Polarization, str]] = None, component: Optional[Union[Component, str]] = None, complex_component: Optional[Union[ComplexComponent, str]] = None) -> float:
        """
        VBA Call
        --------
        FarfieldPlot.CalculatePoint(theta_deg, phi_deg, ' '.join(str(getattr(v, 'value', v)) for v in [coord_system, polarization, component, complex_component] if v is not None), farfield_name)
        """
        return self.query_method_float('CalculatePoint', theta_deg, phi_deg, ' '.join(str(getattr(v, 'value', v)) for v in [coord_system, polarization, component, complex_component] if v is not None), farfield_name)

    def calculate_point_no_approx_deg(self, theta_deg: float, phi_deg: float, radius: float, farfield_name: str, coord_system: Optional[Union[CoordSystem, str]] = None, polarization: Optional[Union[Polarization, str]] = None, component: Optional[Union[Component, str]] = None, complex_component: Optional[Union[ComplexComponent, str]] = None) -> float:
        """
        VBA Call
        --------
        FarfieldPlot.CalculatePointNoApprox(theta_deg, phi_deg, radius, ' '.join(str(getattr(v, 'value', v)) for v in [coord_system, polarization, component, complex_component] if v is not None), farfield_name)
        """
        return self.query_method_float('CalculatePointNoApprox', theta_deg, phi_deg, radius, ' '.join(str(getattr(v, 'value', v)) for v in [coord_system, polarization, component, complex_component] if v is not None), farfield_name)

    def add_list_eval_point_deg(self, polar_angle_deg: float, lateral_angle_deg: float, radius: float, coord_system: Union[CoordSystem, str], tf_type: Union[TFType, str], freq_or_time: float) -> None:
        """
        VBA Call
        --------
        FarfieldPlot.AddListEvaluationPoint(polar_angle_deg, lateral_angle_deg, radius, coord_system, tf_type, freq_or_time)
        """
        self.record_method('AddListEvaluationPoint', polar_angle_deg, lateral_angle_deg, radius, str(getattr(coord_system, 'value', coord_system)), str(getattr(tf_type, 'value', tf_type)), freq_or_time)

    def calculate_list(self, name: str = '') -> None:
        """
        VBA Call
        --------
        FarfieldPlot.CalculateList(name)
        """
        self.record_method('CalculateList', name)

    def get_list(self, field_component: Union[ListFieldComponent, str]) -> None:
        """
        VBA Call
        --------
        FarfieldPlot.GetList(field_component)
        """
        self.record_method('GetList', str(getattr(field_component, 'value', field_component)))

    def get_list_item(self, index: int, field_component: Union[ListFieldComponent, str]) -> None:
        """
        VBA Call
        --------
        FarfieldPlot.GetListItem(index, field_component)
        """
        self.record_method('GetListItem', index, str(getattr(field_component, 'value', field_component)))

    def clear_cuts(self) -> None:
        """
        VBA Call
        --------
        FarfieldPlot.ClearCuts()
        """
        self.record_method('ClearCuts')

    def add_cut_deg(self, cut_type: Union[CutType, str], const_angle_deg: float, step_deg: float) -> None:
        """
        VBA Call
        --------
        FarfieldPlot.AddCut(cut_type, const_angle_deg, step_deg)
        """
        self.record_method('AddCut', str(getattr(cut_type, 'value', cut_type)), const_angle_deg, step_deg)

    def set_color_by_value(self, flag: bool = True) -> None:
        """
        VBA Call
        --------
        FarfieldPlot.SetColorByValue(flag)
        """
        self.record_method('SetColorByValue', flag)

    def set_theta_360_deg(self, flag: bool = True) -> None:
        """
        VBA Call
        --------
        FarfieldPlot.SetTheta360(flag)
        """
        self.record_method('SetTheta360', flag)

    def set_draw_step_lines(self, flag: bool = True) -> None:
        """
        VBA Call
        --------
        FarfieldPlot.DrawStepLines(flag)
        """
        self.record_method('DrawStepLines', flag)

    def set_symmetric_range(self, flag: bool = True) -> None:
        """
        VBA Call
        --------
        FarfieldPlot.SymmetricRange(flag)
        """
        self.record_method('SymmetricRange', flag)

    def set_draw_iso_longitude_latitude_lines(self, flag: bool = True) -> None:
        """
        VBA Call
        --------
        FarfieldPlot.DrawIsoLongitudeLatitudeLines(flag)
        """
        self.record_method('DrawIsoLongitudeLatitudeLines', flag)

    def set_show_structure(self, flag: bool = True) -> None:
        """
        VBA Call
        --------
        FarfieldPlot.ShowStructure(flag)
        """
        self.record_method('ShowStructure', flag)

    def set_show_structure_profile(self, flag: bool = True) -> None:
        """
        VBA Call
        --------
        FarfieldPlot.ShowStructureProfile(flag)
        """
        self.record_method('ShowStructureProfile', flag)

    def set_structure_transparent(self, flag: bool = True) -> None:
        """
        VBA Call
        --------
        FarfieldPlot.SetStructureTransparent(flag)
        """
        self.record_method('SetStructureTransparent', flag)

    def set_farfield_transparent(self, flag: bool = True) -> None:
        """
        VBA Call
        --------
        FarfieldPlot.SetFarfieldTransparent(flag)
        """
        self.record_method('SetFarfieldTransparent', flag)

    def set_farfield_size(self, size: int) -> None:
        """
        VBA Call
        --------
        FarfieldPlot.FarfieldSize(size)
        """
        self.record_method('FarfieldSize', size)

    def set_plot_mode(self, plot_mode: Union[PlotMode, str]) -> None:
        """
        VBA Call
        --------
        FarfieldPlot.SetPlotMode(plot_mode)
        """
        self.record_method('SetPlotMode', str(getattr(plot_mode, 'value', plot_mode)))

    def get_plot_mode(self) -> str:
        """
        VBA Call
        --------
        FarfieldPlot.GetPlotMode()
        """
        return self.query_method_str('GetPlotMode')

    def select_component(self, sel_component: Union[SelComponent, str]) -> None:
        """
        VBA Call
        --------
        FarfieldPlot.SelectComponent(sel_component)
        """
        self.record_method('SelectComponent', str(getattr(sel_component, 'value', sel_component)))

    def enable_polar_extra_lines(self) -> None:
        """
        VBA Call
        --------
        FarfieldPlot.SetSpecials('enablepolarextralines')
        """
        self.record_method('SetSpecials', 'enablepolarextralines')

    def disable_polar_extra_lines(self) -> None:
        """
        VBA Call
        --------
        FarfieldPlot.SetSpecials('disablepolarextralines')
        """
        self.record_method('SetSpecials', 'disablepolarextralines')

    def show_total_radiated_power_linear(self) -> None:
        """
        VBA Call
        --------
        FarfieldPlot.SetSpecials('showtrp')
        """
        self.record_method('SetSpecials', 'showtrp')

    def show_total_radiated_power_logarithmic(self) -> None:
        """
        VBA Call
        --------
        FarfieldPlot.SetSpecials('showtrpdb')
        """
        self.record_method('SetSpecials', 'showtrpdb')

    def hide_total_radiated_power(self) -> None:
        """
        VBA Call
        --------
        FarfieldPlot.SetSpecials('showtrpoff')
        """
        self.record_method('SetSpecials', 'showtrpoff')

    def show_total_isotropic_sensitivity_linear(self) -> None:
        """
        VBA Call
        --------
        FarfieldPlot.SetSpecials('showtis')
        """
        self.record_method('SetSpecials', 'showtis')

    def show_total_isotropic_sensitivity_logarithmic(self) -> None:
        """
        VBA Call
        --------
        FarfieldPlot.SetSpecials('showtisdb')
        """
        self.record_method('SetSpecials', 'showtisdb')

    def hide_total_isotropic_sensitivity(self) -> None:
        """
        VBA Call
        --------
        FarfieldPlot.SetSpecials('showtisoff')
        """
        self.record_method('SetSpecials', 'showtisoff')

    def set_virtual_sphere_radius(self, radius: float) -> None:
        """
        VBA Call
        --------
        FarfieldPlot.Distance(radius)
        """
        self.record_method('Distance', radius)

    def set_scale_linear(self, flag: bool = True) -> None:
        """
        VBA Call
        --------
        FarfieldPlot.SetScaleLinear(flag)
        """
        self.record_method('SetScaleLinear', flag)

    def is_scale_linear(self) -> bool:
        """
        VBA Call
        --------
        FarfieldPlot.IsScaleLinear()
        """
        return self.query_method_bool('IsScaleLinear')

    def set_inverse_axial_ratio(self, flag: bool = True) -> None:
        """
        VBA Call
        --------
        FarfieldPlot.SetInverseAxialRatio(flag)
        """
        self.record_method('SetInverseAxialRatio', flag)

    def has_inverse_axial_ratio(self) -> bool:
        """
        VBA Call
        --------
        FarfieldPlot.IsInverseAxialRatio()
        """
        return self.query_method_bool('IsInverseAxialRatio')

    def set_log_plot_range(self, range_db: float) -> None:
        """
        VBA Call
        --------
        FarfieldPlot.SetLogRange(range_db)
        """
        self.record_method('SetLogRange', range_db)

    def set_log_plot_normalization(self, norm_db: float) -> None:
        """
        VBA Call
        --------
        FarfieldPlot.SetLogNorm(norm_db)
        """
        self.record_method('SetLogNorm', norm_db)

    def get_log_plot_range(self) -> float:
        """
        VBA Call
        --------
        FarfieldPlot.GetLogRange()
        """
        return self.query_method_float('GetLogRange')

    def set_main_lobe_threshold(self, threshold_db: float) -> None:
        """
        VBA Call
        --------
        FarfieldPlot.SetMainLobeThreshold(threshold_db)
        """
        self.record_method('SetMainLobeThreshold', threshold_db)

    def set_db_unit(self, unit_code: Union[UnitCode, str]) -> None:
        """
        VBA Call
        --------
        FarfieldPlot.DBUnit(unit_code)
        """
        self.record_method('DBUnit', str(getattr(unit_code, 'value', unit_code)))

    def set_max_reference_mode(self, max_ref_mode: Union[MaxRefMode, str]) -> None:
        """
        VBA Call
        --------
        FarfieldPlot.SetMaxReferenceMode(max_ref_mode)
        """
        self.record_method('SetMaxReferenceMode', str(getattr(max_ref_mode, 'value', max_ref_mode)))

    def enable_fixed_plot_maximum(self, flag: bool = True) -> None:
        """
        VBA Call
        --------
        FarfieldPlot.EnableFixPlotMaximum(flag)
        """
        self.record_method('EnableFixPlotMaximum', flag)

    def is_plot_maximum_fixed(self) -> bool:
        """
        VBA Call
        --------
        FarfieldPlot.IsPlotMaximumFixed()
        """
        return self.query_method_bool('IsPlotMaximumFixed')

    def set_fixed_plot_maximum(self, maximum: float) -> None:
        """
        VBA Call
        --------
        FarfieldPlot.SetFixPlotMaximumValue(maximum)
        """
        self.record_method('SetFixPlotMaximumValue', maximum)

    def get_fixed_plot_maximum(self) -> float:
        """
        VBA Call
        --------
        FarfieldPlot.GetFixPlotMaximumValue()
        """
        return self.query_method_float('GetFixPlotMaximumValue')

    def set_num_contour_values(self, num: int) -> None:
        """
        VBA Call
        --------
        FarfieldPlot.SetNumberOfContourValues(num)
        """
        self.record_method('SetNumberOfContourValues', num)

    def set_draw_countour_lines(self, flag: bool = True) -> None:
        """
        VBA Call
        --------
        FarfieldPlot.DrawContourLines(flag)
        """
        self.record_method('DrawContourLines', flag)

    def set_origin(self, origin: Union[Origin, str]) -> None:
        """
        VBA Call
        --------
        FarfieldPlot.Origin(origin)
        """
        self.record_method('Origin', str(getattr(origin, 'value', origin)))

    def set_user_origin(self, pos: Tuple[float, float, float]) -> None:
        """
        VBA Call
        --------
        FarfieldPlot.Userorigin(pos[0], pos[1], pos[2])
        """
        self.record_method('Userorigin', pos[0], pos[1], pos[2])

    def set_phi_start_axis(self, axis: Tuple[float, float, float]) -> None:
        """
        VBA Call
        --------
        FarfieldPlot.Phistart(axis[0], axis[1], axis[2])
        """
        self.record_method('Phistart', axis[0], axis[1], axis[2])

    def set_theta_start_axis(self, axis: Tuple[float, float, float]) -> None:
        """
        VBA Call
        --------
        FarfieldPlot.Thetastart(axis[0], axis[1], axis[2])
        """
        self.record_method('Thetastart', axis[0], axis[1], axis[2])

    def set_axes_type(self, axes_type: Union[AxesType, str]) -> None:
        """
        VBA Call
        --------
        FarfieldPlot.SetAxesType(axes_type)
        """
        self.record_method('SetAxesType', str(getattr(axes_type, 'value', axes_type)))

    def set_antenna_type(self, antenna_type: Union[AntennaType, str]) -> None:
        """
        VBA Call
        --------
        FarfieldPlot.SetAntennaType(antenna_type)
        """
        self.record_method('SetAntennaType', str(getattr(antenna_type, 'value', antenna_type)))

    def set_polarization_vector(self, vec: Tuple[float, float, float]) -> None:
        """
        VBA Call
        --------
        FarfieldPlot.PolarizationVector(vec[0], vec[1], vec[2])
        """
        self.record_method('PolarizationVector', vec[0], vec[1], vec[2])

    def set_coord_system(self, coord_system: Union[CoordSystem, str]) -> None:
        """
        VBA Call
        --------
        FarfieldPlot.SetCoordinateSystemType(coord_system)
        """
        self.record_method('SetCoordinateSystemType', str(getattr(coord_system, 'value', coord_system)))

    def set_automatic_coord_system(self, flag: bool = True) -> None:
        """
        VBA Call
        --------
        FarfieldPlot.SetAutomaticCoordinateSystem(flag)
        """
        self.record_method('SetAutomaticCoordinateSystem', flag)

    def set_polarization_type(self, polarization_type: Union[Polarization, str]) -> None:
        """
        VBA Call
        --------
        FarfieldPlot.SetPolarizationType(polarization_type)
        """
        self.record_method('SetPolarizationType', str(getattr(polarization_type, 'value', polarization_type)))

    def set_slant_angle_deg(self, angle_deg: float) -> None:
        """
        VBA Call
        --------
        FarfieldPlot.SlantAngle(angle_deg)
        """
        self.record_method('SlantAngle', angle_deg)

    def set_use_decoupling_plane(self, flag: bool = True) -> None:
        """
        VBA Call
        --------
        FarfieldPlot.UseDecouplingPlane(flag)
        """
        self.record_method('UseDecouplingPlane', flag)

    def set_decoupling_plane_axis(self, axis: Union[Axis, str]) -> None:
        """
        VBA Call
        --------
        FarfieldPlot.DecouplingPlaneAxis(axis)
        """
        self.record_method('DecouplingPlaneAxis', str(getattr(axis, 'value', axis)))

    def set_decoupling_plane_position(self, position: float) -> None:
        """
        VBA Call
        --------
        FarfieldPlot.DecouplingPlanePosition(position)
        """
        self.record_method('DecouplingPlanePosition', position)

    def use_user_defined_decoupling_plane(self, flag: bool = True) -> None:
        """
        VBA Call
        --------
        FarfieldPlot.SetUserDecouplingPlane(flag)
        """
        self.record_method('SetUserDecouplingPlane', flag)

    def get_max_value(self) -> float:
        """
        VBA Call
        --------
        FarfieldPlot.Getmax()
        """
        return self.query_method_float('Getmax')

    def get_min_value(self) -> float:
        """
        VBA Call
        --------
        FarfieldPlot.Getmin()
        """
        return self.query_method_float('Getmin')

    def get_mean_value(self) -> float:
        """
        VBA Call
        --------
        FarfieldPlot.GetMean()
        """
        return self.query_method_float('GetMean')

    def get_radiation_efficiency(self) -> float:
        """
        VBA Call
        --------
        FarfieldPlot.GetRadiationEfficiency()
        """
        return self.query_method_float('GetRadiationEfficiency')

    def get_total_efficiency(self) -> float:
        """
        VBA Call
        --------
        FarfieldPlot.GetTotalEfficiency()
        """
        return self.query_method_float('GetTotalEfficiency')

    def get_system_radiation_efficiency(self) -> float:
        """
        VBA Call
        --------
        FarfieldPlot.GetSystemRadiationEfficiency()
        """
        return self.query_method_float('GetSystemRadiationEfficiency')

    def get_system_total_efficiency(self) -> float:
        """
        VBA Call
        --------
        FarfieldPlot.GetSystemTotalEfficiency()
        """
        return self.query_method_float('GetSystemTotalEfficiency')

    def get_total_radiated_power(self) -> float:
        """
        VBA Call
        --------
        FarfieldPlot.GetTRP()
        """
        return self.query_method_float('GetTRP')

    def get_total_rcs(self) -> float:
        """
        VBA Call
        --------
        FarfieldPlot.GetTotalRCS()
        """
        return self.query_method_float('GetTotalRCS')

    def get_total_acs(self) -> float:
        """
        VBA Call
        --------
        FarfieldPlot.GetTotalACS()
        """
        return self.query_method_float('GetTotalACS')

    def get_main_lobe_angle_deg(self) -> float:
        """
        VBA Call
        --------
        FarfieldPlot.GetMainLobeDirection()
        """
        return self.query_method_float('GetMainLobeDirection')

    def get_main_lobe_vector(self) -> Tuple:
        """
        VBA Call
        --------
        FarfieldPlot.GetMainLobeVector(&x, &y, &z)

        Returns
        -------
        (x, y, z)
        """
        return self.query_method_t('GetMainLobeVector', None, VBATypeName.Double, VBATypeName.Double, VBATypeName.Double)

    def get_main_lobe_width_deg(self) -> float:
        """
        VBA Call
        --------
        FarfieldPlot.GetAngularWidthXdB()
        """
        return self.query_method_float('GetAngularWidthXdB')

    def get_side_lobe_suppression(self) -> float:
        """
        VBA Call
        --------
        FarfieldPlot.GetSideLobeSuppression()
        """
        return self.query_method_float('GetSideLobeSuppression')

    def get_side_lobe_level(self) -> float:
        """
        VBA Call
        --------
        FarfieldPlot.GetSideLobeLevel()
        """
        return self.query_method_float('GetSideLobeLevel')

    def get_front_to_back_ratio(self) -> float:
        """
        VBA Call
        --------
        FarfieldPlot.GetFrontToBackRatio()
        """
        return self.query_method_float('GetFrontToBackRatio')

    def set_phase_center_calculation(self, flag: bool = True) -> None:
        """
        VBA Call
        --------
        FarfieldPlot.EnablePhaseCenterCalculation(flag)
        """
        self.record_method('EnablePhaseCenterCalculation', flag)

    def set_phase_center_component(self, phase_center_component: Union[PhaseCenterComponent, str]) -> None:
        """
        VBA Call
        --------
        FarfieldPlot.SetPhaseCenterComponent(phase_center_component)
        """
        self.record_method('SetPhaseCenterComponent', str(getattr(phase_center_component, 'value', phase_center_component)))

    def set_phase_center_plane(self, phase_center_plane: Union[PhaseCenterPlane, str]) -> None:
        """
        VBA Call
        --------
        FarfieldPlot.SetPhaseCenterPlane(phase_center_plane)
        """
        self.record_method('SetPhaseCenterPlane', str(getattr(phase_center_plane, 'value', phase_center_plane)))

    def set_phase_center_angular_limit_deg(self, limit_deg: float) -> None:
        """
        VBA Call
        --------
        FarfieldPlot.SetPhaseCenterAngularLimit(limit_deg)
        """
        self.record_method('SetPhaseCenterAngularLimit', limit_deg)

    def set_show_phase_center(self, flag: bool = True) -> None:
        """
        VBA Call
        --------
        FarfieldPlot.ShowPhaseCenter(flag)
        """
        self.record_method('ShowPhaseCenter', flag)

    def get_phase_center_result(self, axis: Union[Axis, str], mode: Union[PhaseCenterMode, str]) -> None:
        """
        VBA Call
        --------
        FarfieldPlot.GetPhaseCenterResult(axis, mode)
        """
        self.record_method('GetPhaseCenterResult', str(getattr(axis, 'value', axis)), str(getattr(mode, 'value', mode)))

    def get_phase_center_result_expr(self) -> str:
        """
        VBA Call
        --------
        FarfieldPlot.GetPhaseCenterResultExpr()
        """
        return self.query_method_str('GetPhaseCenterResultExpr')

    def get_phase_center_result_expr_avg(self) -> str:
        """
        VBA Call
        --------
        FarfieldPlot.GetPhaseCenterResultExprAvg()
        """
        return self.query_method_str('GetPhaseCenterResultExprAvg')

    def get_phase_center_result_expr_e_plane(self) -> str:
        """
        VBA Call
        --------
        FarfieldPlot.GetPhaseCenterResultExprEPlane()
        """
        return self.query_method_str('GetPhaseCenterResultExprEPlane')

    def get_phase_center_result_expr_h_plane(self) -> str:
        """
        VBA Call
        --------
        FarfieldPlot.GetPhaseCenterResultExprHPlane()
        """
        return self.query_method_str('GetPhaseCenterResultExprHPlane')

