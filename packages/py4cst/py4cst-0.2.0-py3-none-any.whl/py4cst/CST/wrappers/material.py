'''This file is auto-generated. Do not edit.'''
from .. import IVBAProvider, VBATypeName, VBAObjWrapper
from typing import Union, Tuple, Optional
from enum import Enum

class Material(VBAObjWrapper):
    class Type(Enum):
        PEC = 'PEC'
        NORMAL = 'Normal'
        ANISOTROPIC = 'Anisotropic'
        LOSSY_METAL = 'Lossy Metal'
        CORRUGATED_WALL = 'Corrugated wall'
        OHMIC_SHEET = 'Ohmic sheet'
        TENSOR_FORMULA = 'Tensor formula'
        NONLINEAR = 'Nonlinear'

    class RefCoordSystem(Enum):
        GLOBAL = 'Global'
        SOLID = 'Solid'

    class CoordSystem(Enum):
        CARTESIAN = 'Cartesian'
        CYLINDRICAL = 'Cylindrical'
        SPHERICAL = 'Spherical'

    class TabSurfImpModel(Enum):
        OPAQUE = 'Opaque'
        TRANSPARENT = 'Transparent'

    class DispFitSchemeTabSI(Enum):
        NTH_ORDER = 'Nth Order'

    class EntryBlock(Enum):
        UU = 'uu'
        VU = 'vu'
        UV = 'uv'
        VV = 'vv'

    class TangentDeltaModel(Enum):
        CONST_SIGMA = 'ConstSigma'
        CONST_TAN_D = 'ConstTanD'

    class ConstTangentDeltaStrategy(Enum):
        AUTOMATIC_ORDER = 'AutomaticOrder'
        USER_DEFINED_ORDER = 'UserDefinedOrder'
        DJORDJEVIC_SARKAR = 'DjordjevicSarkar'

    class DispModelEps(Enum):
        NONE = 'None'
        DEBYE_1ST = 'Debye1st'
        DEBYE_2ND = 'Debye2nd'
        DRUDE = 'Drude'
        LORENTZ = 'Lorentz'
        GENERAL_1ST = 'General1st'
        GENERAL_2ND = 'General2nd'
        GENERAL = 'General'
        NON_LINEAR_2ND = 'NonLinear2nd'
        NON_LINEAR_3RD = 'NonLinear3rd'
        NON_LINEAR_KERR = 'NonLinearKerr'
        NON_LINEAR_RAMAN = 'NonLinearRaman'

    class DispModelMu(Enum):
        NONE = 'None'
        DEBYE_1ST = 'Debye1st'
        DEBYE_2ND = 'Debye2nd'
        DRUDE = 'Drude'
        LORENTZ = 'Lorentz'
        GYROTROPIC = 'Gyrotropic'
        GENERALIZED_DEBYE = 'GeneralizedDebye'
        GENERAL_1ST = 'General1st'
        GENERAL_2ND = 'General2nd'
        NON_LINEAR_2ND = 'NonLinear2nd'
        NON_LINEAR_3RD = 'NonLinear3rd'
        NON_LINEAR_KERR = 'NonLinearKerr'
        NON_LINEAR_RAMAN = 'NonLinearRaman'

    class DispersiveFittingFormat(Enum):
        REAL_IMAG = 'Real_Imag'
        REAL_TAND = 'Real_Tand'

    class DispersiveFittingScheme(Enum):
        CONDUCTIVITY = 'Conductivity'
        FIRST_ORDER = '1st Order'
        SECOND_ORDER = '2nd Order'
        NTH_ORDER = 'Nth Order'

    class Direction(Enum):
        X = 'x'
        Y = 'y'
        Z = 'z'

    class SpatiallyVarMatProp(Enum):
        EPS = 'eps'
        MU = 'mu'
        SIGMA = 'sigma'
        SIGMA_M = 'sigmam'

    class SpatiallyVarMatModel(Enum):
        CONSTANT = 'Constant'
        LUNEBURG = 'Luneburg'
        POWER_LAW = 'PowerLaw'
        GRADED_INDEX = 'GradedIndex'

    class SpatiallyVarMatParam(Enum):
        VALUE_CONSTANT = 'value_constant'
        VALUE_CENTER = 'value_center'
        VALUE_SURFACE = 'value_surface'
        VALUE_AXIS = 'value_axis'
        VALUE_CLADDING = 'value_cladding'
        VALUE_PROFILE = 'value_profile'
        VALUE_GRADIENT = 'value_gradient'

    class SpaceMapMatProp(Enum):
        EPS = 'eps'
        MU = 'mu'
        SIGMA = 'sigma'
        SIGMA_M = 'sigmam'
        EPS_INFINITY = 'epsinfinity'
        MU_INFINITY = 'muinfinity'
        DISP_COEFF0_EPS = 'dispcoeff0eps'
        DISP_COEFF0_MU = 'dispcoeff0mu'
        DISP_COEFF1_EPS = 'dispcoeff1eps'
        DISP_COEFF1_MU = 'dispcoeff1mu'
        DISP_COEFF2_EPS = 'dispcoeff2eps'
        DISP_COEFF2_MU = 'dispcoeff2mu'
        DISP_COEFF3_EPS = 'dispcoeff3eps'
        DISP_COEFF3_MU = 'dispcoeff3mu'
        DISP_COEFF4_EPS = 'dispcoeff4eps'
        DISP_COEFF4_MU = 'dispcoeff4mu'

    class SpaceMapMatModel(Enum):
        CONSTANT_3D = '3DConstant'
        DEFAULT_3D = '3DDefault'
        IMPORT_HEX_3D = '3DImportHex'
        IMPORT_TET_3D = '3DImportTet'

    class SpaceMapMatParam(Enum):
        VALUE_CONSTANT = 'value_constant'
        VALUE_DEFAULT = 'value_default'
        MAP_FILENAME = 'map_filename'
        SLIMMESH_FILENAME = 'slimmesh_filename'

    class GeneralizedDebyeNonLinDep(Enum):
        NONE = 'None'
        BH_CURVE = 'BHCurve'
        TAB_MU_DIFF_CURVE = 'TabMuDiffCurve'

    class CoatingTypeDef(Enum):
        PERFECT_ABSORBER = 'PERFECT_ABSORBER'
        SURFACE_IMPEDANCE_TABLE = 'SURFACE_IMPEDANCE_TABLE'
        REFLECTION_FACTOR_TABLE = 'REFLECTION_FACTOR_TABLE'
        REFLECTION_TRANSMISSION_FACTOR_TABLE = 'REFLECTION_TRANSMISSION_FACTOR_TABLE'

    class ParticleProp(Enum):
        NONE = 'None'
        SECONDARY_EMISSION = 'SecondaryEmission'
        SHEET_TRANSPARENCY = 'SheetTransparency'

    class SeModel(Enum):
        NONE = 'None'
        FURMAN = 'Furman'
        IMPORT = 'Import'
        VAUGHAN = 'Vaughan'

    class IonSeeModel(Enum):
        NONE = 'None'
        ION_IMPORT = 'Ion Import'

    class ParticleTransparencySettings(Enum):
        SCALAR = 'Scalar'
        IMPORT = 'Import'

    class ThermalType(Enum):
        PTC = 'PTC'
        NORMAL = 'Normal'
        ANISOTROPIC = 'Anisotropic'

    class SpecificHeatUnit(Enum):
        J_K_KG = 'J/K/kg'
        KJ_K_KG = 'kJ/K/kg'

    class MechanicsType(Enum):
        UNUSED = 'Unused'
        ISOTROPIC = 'Isotropic'

    class FlowResPressureLossTypeUVW(Enum):
        BLOCKED = 'Blocked'
        COEFFICIENT = 'Coefficient'
        CURVE = 'Curve'

    class FlowResPressureLossTypeSheet(Enum):
        BLOCKED = 'Blocked'
        COEFFICIENT = 'Coefficient'
        CURVE = 'Curve'
        PERFORATION = 'Perforation'
        FREE_AREA_RATIO = 'FreeAreaRatio'

    class FlowResShapeType(Enum):
        HEXAGON = 'Hexagon'
        CIRCLE = 'Circle'
        SQUARE = 'Square'

    class TensorFormulaFor(Enum):
        EPSILON_R = 'epsilon_r'
        MU_R = 'mu_r'

    class Species(Enum):
        ELECTRON = 'electron'
        HOLE = 'hole'

    def __init__(self, vbap: IVBAProvider) -> None:
        super().__init__(vbap, 'Material')
        self.set_save_history(False)

    def reset(self) -> None:
        """
        VBA Call
        --------
        Material.Reset()
        """
        self.cache_method('Reset')

    def create(self) -> None:
        """
        VBA Call
        --------
        Material.Create()
        """
        self.cache_method('Create')
        self.flush_cache('Create Material')

    def set_name(self, name: str) -> None:
        """
        VBA Call
        --------
        Material.Name(name)
        """
        self.cache_method('Name', name)

    def set_folder_name(self, folder_name: str) -> None:
        """
        VBA Call
        --------
        Material.Folder(folder_name)
        """
        self.cache_method('Folder', folder_name)

    def set_type(self, mat_type: Union[Type, str]) -> None:
        """
        VBA Call
        --------
        Material.Type(mat_type)
        """
        self.cache_method('Type', str(getattr(mat_type, 'value', mat_type)))

    def set_frequency_unit(self, unit: str) -> None:
        """
        VBA Call
        --------
        Material.MaterialUnit('Frequency', unit)
        """
        self.cache_method('MaterialUnit', 'Frequency', unit)

    def set_geometry_unit(self, unit: str) -> None:
        """
        VBA Call
        --------
        Material.MaterialUnit('Geometry', unit)
        """
        self.cache_method('MaterialUnit', 'Geometry', unit)

    def set_time_unit(self, unit: str) -> None:
        """
        VBA Call
        --------
        Material.MaterialUnit('Time', unit)
        """
        self.cache_method('MaterialUnit', 'Time', unit)

    def set_temperature_unit(self, unit: str) -> None:
        """
        VBA Call
        --------
        Material.MaterialUnit('Temperature', unit)
        """
        self.cache_method('MaterialUnit', 'Temperature', unit)

    def delete(self, mat_name: str) -> None:
        """
        VBA Call
        --------
        Material.Delete(mat_name)
        """
        self.record_method('Delete', mat_name)

    def rename(self, old_name: str, new_name: str) -> None:
        """
        VBA Call
        --------
        Material.Rename(old_name, new_name)
        """
        self.record_method('Rename', old_name, new_name)

    def create_folder(self, name: str) -> None:
        """
        VBA Call
        --------
        Material.NewFolder(name)
        """
        self.record_method('NewFolder', name)

    def delete_folder(self, name: str) -> None:
        """
        VBA Call
        --------
        Material.DeleteFolder(name)
        """
        self.record_method('DeleteFolder', name)

    def rename_folder(self, old_name: str, new_name: str) -> None:
        """
        VBA Call
        --------
        Material.RenameFolder(old_name, new_name)
        """
        self.record_method('RenameFolder', old_name, new_name)

    def set_color_rgb(self, r: float, g: float, b: float) -> None:
        """
        VBA Call
        --------
        Material.Colour(r, g, b)
        """
        self.cache_method('Colour', r, g, b)
        self.flush_cache('ChangeColour (Material)')

    def set_transparency(self, transparency: float) -> None:
        """
        VBA Call
        --------
        Material.Transparency(transparency)
        """
        self.cache_method('Transparency', transparency)

    def set_color_alpha(self, alpha: float) -> None:
        """
        VBA Call
        --------
        Material.Transparency(1.0 - alpha)
        """
        self.cache_method('Transparency', 1.0 - alpha)

    def set_wireframe(self, flag: bool) -> None:
        """
        VBA Call
        --------
        Material.Wireframe(flag)
        """
        self.cache_method('Wireframe', flag)

    def set_reflection(self, flag: bool) -> None:
        """
        VBA Call
        --------
        Material.Reflection(flag)
        """
        self.cache_method('Reflection', flag)

    def set_allow_outlines(self, flag: bool) -> None:
        """
        VBA Call
        --------
        Material.Allowoutline(flag)
        """
        self.cache_method('Allowoutline', flag)

    def set_transparent_solid_outlines(self, flag: bool) -> None:
        """
        VBA Call
        --------
        Material.Transparentoutline(flag)
        """
        self.cache_method('Transparentoutline', flag)

    def change_appearance(self) -> None:
        """
        VBA Call
        --------
        Material.ChangeColour()
        """
        self.cache_method('ChangeColour')
        self.flush_cache('ChangeColour (Material)')

    def set_rel_permitivity(self, epsilon: float) -> None:
        """
        VBA Call
        --------
        Material.Epsilon(epsilon)
        """
        self.cache_method('Epsilon', epsilon)

    def set_rel_permitivity_x(self, epsilon: float) -> None:
        """
        VBA Call
        --------
        Material.EpsilonX(epsilon)
        """
        self.cache_method('EpsilonX', epsilon)

    def set_rel_permitivity_y(self, epsilon: float) -> None:
        """
        VBA Call
        --------
        Material.EpsilonY(epsilon)
        """
        self.cache_method('EpsilonY', epsilon)

    def set_rel_permitivity_z(self, epsilon: float) -> None:
        """
        VBA Call
        --------
        Material.EpsilonZ(epsilon)
        """
        self.cache_method('EpsilonZ', epsilon)

    def set_rel_permeability(self, mu: float) -> None:
        """
        VBA Call
        --------
        Material.Mu(mu)
        """
        self.cache_method('Mu', mu)

    def set_rel_permeability_x(self, mu: float) -> None:
        """
        VBA Call
        --------
        Material.MuX(mu)
        """
        self.cache_method('MuX', mu)

    def set_rel_permeability_y(self, mu: float) -> None:
        """
        VBA Call
        --------
        Material.MuY(mu)
        """
        self.cache_method('MuY', mu)

    def set_rel_permeability_z(self, mu: float) -> None:
        """
        VBA Call
        --------
        Material.MuZ(mu)
        """
        self.cache_method('MuZ', mu)

    def set_material_density(self, rho_kg_per_m3: float) -> None:
        """
        VBA Call
        --------
        Material.Rho(rho_kg_per_m3)
        """
        self.cache_method('Rho', rho_kg_per_m3)

    def add_coated_material(self, mat_name: str, thickness: float) -> None:
        """
        VBA Call
        --------
        Material.AddCoatedMaterial(mat_name, thickness)
        """
        self.cache_method('AddCoatedMaterial', mat_name, thickness)

    def set_reference_coord_system(self, name: Union[RefCoordSystem, str]) -> None:
        """
        VBA Call
        --------
        Material.ReferenceCoordSystem(name)
        """
        self.cache_method('ReferenceCoordSystem', str(getattr(name, 'value', name)))

    def set_coord_system_type(self, name: Union[CoordSystem, str]) -> None:
        """
        VBA Call
        --------
        Material.CoordSystemType(name)
        """
        self.cache_method('CoordSystemType', str(getattr(name, 'value', name)))

    def set_corrugation(self, depth: float, gap_width: float, tooth_width: float) -> None:
        """
        VBA Call
        --------
        Material.Corrugation(depth, gap_width, tooth_width)
        """
        self.cache_method('Corrugation', depth, gap_width, tooth_width)

    def set_ohmic_sheet_impedance(self, impedance: complex) -> None:
        """
        VBA Call
        --------
        Material.OhmicSheetImpedance(real(impedance), imag(impedance))
        """
        self.cache_method('OhmicSheetImpedance', impedance.real, impedance.imag)

    def set_ohmic_sheet_frequency(self, frequency: float) -> None:
        """
        VBA Call
        --------
        Material.OhmicSheetFreq(frequency)
        """
        self.cache_method('OhmicSheetFreq', frequency)

    def set_tabulated_surface_impedance_model(self, model: Union[TabSurfImpModel, str]) -> None:
        """
        VBA Call
        --------
        Material.SetTabulatedSurfaceImpedanceModel(model)
        """
        self.cache_method('SetTabulatedSurfaceImpedanceModel', str(getattr(model, 'value', model)))

    def add_tabulated_surface_impedance_fitting_value(self, frequency: float, impedance: complex, weight: float) -> None:
        """
        VBA Call
        --------
        Material.AddTabulatedSurfaceImpedanceFittingValue(frequency, real(impedance), imag(impedance), weight)
        """
        self.record_method('AddTabulatedSurfaceImpedanceFittingValue', frequency, impedance.real, impedance.imag, weight)

    def add_tabulated_surface_impedance_value(self, frequency: float, impedance: complex) -> None:
        """
        VBA Call
        --------
        Material.AddTabulatedSurfaceImpedanceValue(frequency, real(impedance), imag(impedance))
        """
        self.record_method('AddTabulatedSurfaceImpedanceValue', frequency, impedance.real, impedance.imag)

    def set_dispersive_fitting_scheme_tab_surf_imp(self, scheme: Union[DispFitSchemeTabSI, str]) -> None:
        """
        VBA Call
        --------
        Material.DispersiveFittingSchemeTabSI(scheme)
        """
        self.cache_method('DispersiveFittingSchemeTabSI', str(getattr(scheme, 'value', scheme)))

    def set_max_order_nth_model_fit_tab_surf_imp(self, order: int) -> None:
        """
        VBA Call
        --------
        Material.MaximalOrderNthModelFitTabSI(order)
        """
        self.cache_method('MaximalOrderNthModelFitTabSI', order)

    def set_use_only_data_in_sim_freq_range_nth_model_tab_surf_imp(self, flag: bool) -> None:
        """
        VBA Call
        --------
        Material.UseOnlyDataInSimFreqRangeNthModelTabSI(flag)
        """
        self.cache_method('UseOnlyDataInSimFreqRangeNthModelTabSI', flag)

    def set_error_limit_nth_model_fit_tab_surf_imp(self, limit: float) -> None:
        """
        VBA Call
        --------
        Material.ErrorLimitNthModelFitTabSI(limit)
        """
        self.cache_method('ErrorLimitNthModelFitTabSI', limit)

    def set_as_tabulated_compact_model(self, flag: bool) -> None:
        """
        VBA Call
        --------
        Material.TabulatedCompactModel(flag)
        """
        self.cache_method('TabulatedCompactModel', flag)

    def reset_tabulated_compact_model_list(self) -> None:
        """
        VBA Call
        --------
        Material.ResetTabulatedCompactModelList()
        """
        self.record_method('ResetTabulatedCompactModelList')

    def set_tabulated_compact_model_impedance(self, imp_p1: float, imp_p2: float) -> None:
        """
        VBA Call
        --------
        Material.SetTabulatedCompactModelImpedance(imp_p1, imp_p2)
        """
        self.cache_method('SetTabulatedCompactModelImpedance', imp_p1, imp_p2)

    def set_symm_tabulated_compact_model_impedance(self, imp_p: float) -> None:
        """
        VBA Call
        --------
        Material.SetSymmTabulatedCompactModelImpedance(imp_p)
        """
        self.cache_method('SetSymmTabulatedCompactModelImpedance', imp_p)

    def add_tabulated_compact_model_item(self, frequency: float, s11: complex, s21: complex, s12: complex, s22: complex, weight: float) -> None:
        """
        VBA Call
        --------
        Material.AddTabulatedCompactModelItem(frequency, real(s11), imag(s11), real(s21), imag(s21), real(s12), imag(s12), real(s22), imag(s22), weight)
        """
        self.record_method('AddTabulatedCompactModelItem', frequency, s11.real, s11.imag, s21.real, s21.imag, s12.real, s12.imag, s22.real, s22.imag, weight)

    def add_symm_tabulated_compact_model_item(self, frequency: float, s11: complex, s21: complex, weight: float) -> None:
        """
        VBA Call
        --------
        Material.AddSymmTabulatedCompactModelItem(frequency, real(s11), imag(s11), real(s21), imag(s21), weight)
        """
        self.record_method('AddSymmTabulatedCompactModelItem', frequency, s11.real, s11.imag, s21.real, s21.imag, weight)

    def set_tabulated_compact_model_anisotropic(self, flag: bool) -> None:
        """
        VBA Call
        --------
        Material.TabulatedCompactModelAnisotropic(flag)
        """
        self.cache_method('TabulatedCompactModelAnisotropic', flag)

    def add_aniso_tabulated_compact_model_item(self, entry_block: Union[EntryBlock, str], frequency: float, s11: complex, s21: complex, s12: complex, s22: complex, weight: float) -> None:
        """
        VBA Call
        --------
        Material.AddAnisoTabulatedCompactModelItem(entry_block, frequency, real(s11), imag(s11), real(s21), imag(s21), real(s12), imag(s12), real(s22), imag(s22), weight)
        """
        self.record_method('AddAnisoTabulatedCompactModelItem', str(getattr(entry_block, 'value', entry_block)), frequency, s11.real, s11.imag, s21.real, s21.imag, s12.real, s12.imag, s22.real, s22.imag, weight)

    def add_aniso_symm_tabulated_compact_model_item(self, entry_block: Union[EntryBlock, str], frequency: float, s11: complex, s21: complex, weight: float) -> None:
        """
        VBA Call
        --------
        Material.AddAnisoSymmTabulatedCompactModelItem(entry_block, frequency, real(s11), imag(s11), real(s21), imag(s21), weight)
        """
        self.record_method('AddAnisoSymmTabulatedCompactModelItem', str(getattr(entry_block, 'value', entry_block)), frequency, s11.real, s11.imag, s21.real, s21.imag, weight)

    def set_max_order_fit_tabulated_compact_model(self, order: int) -> None:
        """
        VBA Call
        --------
        Material.MaximalOrderFitTabulatedCompactModel(order)
        """
        self.cache_method('MaximalOrderFitTabulatedCompactModel', order)

    def set_use_only_data_in_sim_freq_range_tabulated_compact_model(self, flag: bool) -> None:
        """
        VBA Call
        --------
        Material.UseOnlyDataInSimFreqRangeTabulatedCompactModel(flag)
        """
        self.cache_method('UseOnlyDataInSimFreqRangeTabulatedCompactModel', flag)

    def set_error_limit_fit_tabulated_compact_model(self, limit: float) -> None:
        """
        VBA Call
        --------
        Material.ErrorLimitFitTabulatedCompactModel(limit)
        """
        self.cache_method('ErrorLimitFitTabulatedCompactModel', limit)

    def set_thickness(self, thickness: float) -> None:
        """
        VBA Call
        --------
        Material.Thickness(thickness)
        """
        self.cache_method('Thickness', thickness)

    def set_lossy_metal_surf_imp_roughness(self, roughness: float) -> None:
        """
        VBA Call
        --------
        Material.LossyMetalSIRoughness(roughness)
        """
        self.cache_method('LossyMetalSIRoughness', roughness)

    def set_el_conductivity(self, sigma: float) -> None:
        """
        VBA Call
        --------
        Material.Sigma(sigma)
        """
        self.cache_method('Sigma', sigma)

    def set_el_conductivity_x(self, sigma: float) -> None:
        """
        VBA Call
        --------
        Material.SigmaX(sigma)
        """
        self.cache_method('SigmaX', sigma)

    def set_el_conductivity_y(self, sigma: float) -> None:
        """
        VBA Call
        --------
        Material.SigmaY(sigma)
        """
        self.cache_method('SigmaY', sigma)

    def set_el_conductivity_z(self, sigma: float) -> None:
        """
        VBA Call
        --------
        Material.SigmaZ(sigma)
        """
        self.cache_method('SigmaZ', sigma)

    def set_el_parametric_conductivity(self, flag: bool) -> None:
        """
        VBA Call
        --------
        Material.SetElParametricConductivity(flag)
        """
        self.cache_method('SetElParametricConductivity', flag)

    def add_je_value(self, dj: float, de: float) -> None:
        """
        VBA Call
        --------
        Material.AddJEValue(dj, de)
        """
        self.cache_method('AddJEValue', dj, de)

    def reset_je_list(self) -> None:
        """
        VBA Call
        --------
        Material.ResetJEList()
        """
        self.record_method('ResetJEList')

    def reset_el_time_dependent_conductivity_curve(self) -> None:
        """
        VBA Call
        --------
        Material.ResetElTimeDepCond()
        """
        self.cache_method('ResetElTimeDepCond')

    def add_el_time_dependent_conductivity_value(self, d_time: float, d_cond: float) -> None:
        """
        VBA Call
        --------
        Material.AddElTimeDepCondValue(d_time, d_cond)
        """
        self.cache_method('AddElTimeDepCondValue', d_time, d_cond)

    def add_el_time_dependent_conductivity_aniso_value(self, d_time: float, d_cond: Tuple[float, float, float]) -> None:
        """
        VBA Call
        --------
        Material.AddElTimeDepCondAnisoValue(d_time, d_cond[0], d_cond[1], d_cond[2])
        """
        self.cache_method('AddElTimeDepCondAnisoValue', d_time, d_cond[0], d_cond[1], d_cond[2])

    def load_el_time_dependent_conductivity_from_file(self, file_path: str, time_unit: str) -> None:
        """
        VBA Call
        --------
        Material.LoadElTimeDepConductivity(file_path, time_unit)
        """
        self.cache_method('LoadElTimeDepConductivity', file_path, time_unit)

    def set_el_tangent_delta(self, tan_d: float) -> None:
        """
        VBA Call
        --------
        Material.TanD(tan_d)
        """
        self.cache_method('TanD', tan_d)

    def set_el_tangent_delta_x(self, tan_d: float) -> None:
        """
        VBA Call
        --------
        Material.TanDX(tan_d)
        """
        self.cache_method('TanDX', tan_d)

    def set_el_tangent_delta_y(self, tan_d: float) -> None:
        """
        VBA Call
        --------
        Material.TanDY(tan_d)
        """
        self.cache_method('TanDY', tan_d)

    def set_el_tangent_delta_z(self, tan_d: float) -> None:
        """
        VBA Call
        --------
        Material.TanDZ(tan_d)
        """
        self.cache_method('TanDZ', tan_d)

    def set_el_tangent_delta_given(self, flag: bool) -> None:
        """
        VBA Call
        --------
        Material.TanDGiven(flag)
        """
        self.cache_method('TanDGiven', flag)

    def set_el_tangent_delta_frequency(self, frequency: float) -> None:
        """
        VBA Call
        --------
        Material.TanDFreq(frequency)
        """
        self.cache_method('TanDFreq', frequency)

    def set_el_tangent_delta_model(self, model: Union[TangentDeltaModel, str]) -> None:
        """
        VBA Call
        --------
        Material.TanDModel(model)
        """
        self.cache_method('TanDModel', str(getattr(model, 'value', model)))

    def set_el_const_tangent_delta_strategy_eps(self, strategy: Union[ConstTangentDeltaStrategy, str]) -> None:
        """
        VBA Call
        --------
        Material.SetConstTanDStrategyEps(strategy)
        """
        self.cache_method('SetConstTanDStrategyEps', str(getattr(strategy, 'value', strategy)))

    def set_el_const_tangent_delta_model_order_eps(self, order: int) -> None:
        """
        VBA Call
        --------
        Material.ConstTanDModelOrderEps(order)
        """
        self.cache_method('ConstTanDModelOrderEps', order)

    def set_djordjevic_sarkar_upper_freq_eps(self, frequency: float) -> None:
        """
        VBA Call
        --------
        Material.DjordjevicSarkarUpperFreqEps(frequency)
        """
        self.cache_method('DjordjevicSarkarUpperFreqEps', frequency)

    def set_mag_conductivity(self, sigma: float) -> None:
        """
        VBA Call
        --------
        Material.SigmaM(sigma)
        """
        self.cache_method('SigmaM', sigma)

    def set_mag_conductivity_x(self, sigma: float) -> None:
        """
        VBA Call
        --------
        Material.SigmaMX(sigma)
        """
        self.cache_method('SigmaMX', sigma)

    def set_mag_conductivity_y(self, sigma: float) -> None:
        """
        VBA Call
        --------
        Material.SigmaMY(sigma)
        """
        self.cache_method('SigmaMY', sigma)

    def set_mag_conductivity_z(self, sigma: float) -> None:
        """
        VBA Call
        --------
        Material.SigmaMZ(sigma)
        """
        self.cache_method('SigmaMZ', sigma)

    def set_mag_parametric_conductivity(self, flag: bool) -> None:
        """
        VBA Call
        --------
        Material.SetMagParametricConductivity(flag)
        """
        self.cache_method('SetMagParametricConductivity', flag)

    def reset_mag_time_dependent_conductivity_curve(self) -> None:
        """
        VBA Call
        --------
        Material.ResetMagTimeDepCond()
        """
        self.record_method('ResetMagTimeDepCond')

    def add_mag_time_dependent_conductivity_value(self, d_time: float, d_cond: float) -> None:
        """
        VBA Call
        --------
        Material.AddMagTimeDepCondValue(d_time, d_cond)
        """
        self.cache_method('AddMagTimeDepCondValue', d_time, d_cond)

    def add_mag_time_dependent_conductivity_aniso_value(self, d_time: float, d_cond: Tuple[float, float, float]) -> None:
        """
        VBA Call
        --------
        Material.AddMagTimeDepCondAnisoValue(d_time, d_cond[0], d_cond[1], d_cond[2])
        """
        self.cache_method('AddMagTimeDepCondAnisoValue', d_time, d_cond[0], d_cond[1], d_cond[2])

    def load_mag_time_dependent_conductivity_from_file(self, file_path: str, time_unit: str) -> None:
        """
        VBA Call
        --------
        Material.LoadMagTimeDepConductivity(file_path, time_unit)
        """
        self.cache_method('LoadMagTimeDepConductivity', file_path, time_unit)

    def set_mag_tangent_delta(self, tan_d: float) -> None:
        """
        VBA Call
        --------
        Material.TanDM(tan_d)
        """
        self.cache_method('TanDM', tan_d)

    def set_mag_tangent_delta_x(self, tan_d: float) -> None:
        """
        VBA Call
        --------
        Material.TanDMX(tan_d)
        """
        self.cache_method('TanDMX', tan_d)

    def set_mag_tangent_delta_y(self, tan_d: float) -> None:
        """
        VBA Call
        --------
        Material.TanDMY(tan_d)
        """
        self.cache_method('TanDMY', tan_d)

    def set_mag_tangent_delta_z(self, tan_d: float) -> None:
        """
        VBA Call
        --------
        Material.TanDMZ(tan_d)
        """
        self.cache_method('TanDMZ', tan_d)

    def set_mag_tangent_delta_given(self, flag: bool) -> None:
        """
        VBA Call
        --------
        Material.TanDMGiven(flag)
        """
        self.cache_method('TanDMGiven', flag)

    def set_mag_tangent_delta_frequency(self, frequency: float) -> None:
        """
        VBA Call
        --------
        Material.TanDMFreq(frequency)
        """
        self.cache_method('TanDMFreq', frequency)

    def set_mag_tangent_delta_model(self, model: Union[TangentDeltaModel, str]) -> None:
        """
        VBA Call
        --------
        Material.TanDMModel(model)
        """
        self.cache_method('TanDMModel', str(getattr(model, 'value', model)))

    def set_mag_const_tangent_delta_strategy_mu(self, strategy: Union[ConstTangentDeltaStrategy, str]) -> None:
        """
        VBA Call
        --------
        Material.SetConstTanDStrategyMu(strategy)
        """
        self.cache_method('SetConstTanDStrategyMu', str(getattr(strategy, 'value', strategy)))

    def set_mag_const_tangent_delta_model_order_mu(self, order: int) -> None:
        """
        VBA Call
        --------
        Material.ConstTanDModelOrderMu(order)
        """
        self.cache_method('ConstTanDModelOrderMu', order)

    def set_djordjevic_sarkar_upper_freq_mu(self, frequency: float) -> None:
        """
        VBA Call
        --------
        Material.DjordjevicSarkarUpperFreqMu(frequency)
        """
        self.cache_method('DjordjevicSarkarUpperFreqMu', frequency)

    def set_disp_model_esp(self, model: Union[DispModelEps, str]) -> None:
        """
        VBA Call
        --------
        Material.DispModelEps(model)
        """
        self.cache_method('DispModelEps', str(getattr(model, 'value', model)))

    def set_disp_model_mu(self, model: Union[DispModelMu, str]) -> None:
        """
        VBA Call
        --------
        Material.DispModelMu(model)
        """
        self.cache_method('DispModelMu', str(getattr(model, 'value', model)))

    def set_eps_infinity(self, eps: float) -> None:
        """
        VBA Call
        --------
        Material.EpsInfinity(eps)
        """
        self.cache_method('EpsInfinity', eps)

    def set_eps_infinity_x(self, eps: float) -> None:
        """
        VBA Call
        --------
        Material.EpsInfinityX(eps)
        """
        self.cache_method('EpsInfinityX', eps)

    def set_eps_infinity_y(self, eps: float) -> None:
        """
        VBA Call
        --------
        Material.EpsInfinityY(eps)
        """
        self.cache_method('EpsInfinityY', eps)

    def set_eps_infinity_z(self, eps: float) -> None:
        """
        VBA Call
        --------
        Material.EpsInfinityZ(eps)
        """
        self.cache_method('EpsInfinityZ', eps)

    def set_disp_coeff0_eps(self, eps: float) -> None:
        """
        VBA Call
        --------
        Material.DispCoeff0Eps(eps)
        """
        self.cache_method('DispCoeff0Eps', eps)

    def set_disp_coeff0_eps_x(self, eps: float) -> None:
        """
        VBA Call
        --------
        Material.DispCoeff0EpsX(eps)
        """
        self.cache_method('DispCoeff0EpsX', eps)

    def set_disp_coeff0_eps_y(self, eps: float) -> None:
        """
        VBA Call
        --------
        Material.DispCoeff0EpsY(eps)
        """
        self.cache_method('DispCoeff0EpsY', eps)

    def set_disp_coeff0_eps_z(self, eps: float) -> None:
        """
        VBA Call
        --------
        Material.DispCoeff0EpsZ(eps)
        """
        self.cache_method('DispCoeff0EpsZ', eps)

    def set_disp_coeff1_eps(self, eps: float) -> None:
        """
        VBA Call
        --------
        Material.DispCoeff1Eps(eps)
        """
        self.cache_method('DispCoeff1Eps', eps)

    def set_disp_coeff1_eps_x(self, eps: float) -> None:
        """
        VBA Call
        --------
        Material.DispCoeff1EpsX(eps)
        """
        self.cache_method('DispCoeff1EpsX', eps)

    def set_disp_coeff1_eps_y(self, eps: float) -> None:
        """
        VBA Call
        --------
        Material.DispCoeff1EpsY(eps)
        """
        self.cache_method('DispCoeff1EpsY', eps)

    def set_disp_coeff1_eps_z(self, eps: float) -> None:
        """
        VBA Call
        --------
        Material.DispCoeff1EpsZ(eps)
        """
        self.cache_method('DispCoeff1EpsZ', eps)

    def set_disp_coeff2_eps(self, eps: float) -> None:
        """
        VBA Call
        --------
        Material.DispCoeff2Eps(eps)
        """
        self.cache_method('DispCoeff2Eps', eps)

    def set_disp_coeff2_eps_x(self, eps: float) -> None:
        """
        VBA Call
        --------
        Material.DispCoeff2EpsX(eps)
        """
        self.cache_method('DispCoeff2EpsX', eps)

    def set_disp_coeff2_eps_y(self, eps: float) -> None:
        """
        VBA Call
        --------
        Material.DispCoeff2EpsY(eps)
        """
        self.cache_method('DispCoeff2EpsY', eps)

    def set_disp_coeff2_eps_z(self, eps: float) -> None:
        """
        VBA Call
        --------
        Material.DispCoeff2EpsZ(eps)
        """
        self.cache_method('DispCoeff2EpsZ', eps)

    def set_disp_coeff3_eps(self, eps: float) -> None:
        """
        VBA Call
        --------
        Material.DispCoeff3Eps(eps)
        """
        self.cache_method('DispCoeff3Eps', eps)

    def set_disp_coeff3_eps_x(self, eps: float) -> None:
        """
        VBA Call
        --------
        Material.DispCoeff3EpsX(eps)
        """
        self.cache_method('DispCoeff3EpsX', eps)

    def set_disp_coeff3_eps_y(self, eps: float) -> None:
        """
        VBA Call
        --------
        Material.DispCoeff3EpsY(eps)
        """
        self.cache_method('DispCoeff3EpsY', eps)

    def set_disp_coeff3_eps_z(self, eps: float) -> None:
        """
        VBA Call
        --------
        Material.DispCoeff3EpsZ(eps)
        """
        self.cache_method('DispCoeff3EpsZ', eps)

    def set_disp_coeff4_eps(self, eps: float) -> None:
        """
        VBA Call
        --------
        Material.DispCoeff4Eps(eps)
        """
        self.cache_method('DispCoeff4Eps', eps)

    def set_disp_coeff4_eps_x(self, eps: float) -> None:
        """
        VBA Call
        --------
        Material.DispCoeff4EpsX(eps)
        """
        self.cache_method('DispCoeff4EpsX', eps)

    def set_disp_coeff4_eps_y(self, eps: float) -> None:
        """
        VBA Call
        --------
        Material.DispCoeff4EpsY(eps)
        """
        self.cache_method('DispCoeff4EpsY', eps)

    def set_disp_coeff4_eps_z(self, eps: float) -> None:
        """
        VBA Call
        --------
        Material.DispCoeff4EpsZ(eps)
        """
        self.cache_method('DispCoeff4EpsZ', eps)

    def add_disp_eps_pole_1st_order(self, alpha0: float, beta0: float) -> None:
        """
        VBA Call
        --------
        Material.AddDispEpsPole1stOrder(alpha0, beta0)
        """
        self.cache_method('AddDispEpsPole1stOrder', alpha0, beta0)

    def add_disp_eps_pole_1st_order_x(self, alpha0: float, beta0: float) -> None:
        """
        VBA Call
        --------
        Material.AddDispEpsPole1stOrderX(alpha0, beta0)
        """
        self.cache_method('AddDispEpsPole1stOrderX', alpha0, beta0)

    def add_disp_eps_pole_1st_order_y(self, alpha0: float, beta0: float) -> None:
        """
        VBA Call
        --------
        Material.AddDispEpsPole1stOrderY(alpha0, beta0)
        """
        self.cache_method('AddDispEpsPole1stOrderY', alpha0, beta0)

    def add_disp_eps_pole_1st_order_z(self, alpha0: float, beta0: float) -> None:
        """
        VBA Call
        --------
        Material.AddDispEpsPole1stOrderZ(alpha0, beta0)
        """
        self.cache_method('AddDispEpsPole1stOrderZ', alpha0, beta0)

    def add_disp_eps_pole_2nd_order(self, alpha0: float, alpha1: float, beta0: float, beta1: float) -> None:
        """
        VBA Call
        --------
        Material.AddDispEpsPole2ndOrder(alpha0, alpha1, beta0, beta1)
        """
        self.cache_method('AddDispEpsPole2ndOrder', alpha0, alpha1, beta0, beta1)

    def add_disp_eps_pole_2nd_order_x(self, alpha0: float, alpha1: float, beta0: float, beta1: float) -> None:
        """
        VBA Call
        --------
        Material.AddDispEpsPole2ndOrderX(alpha0, alpha1, beta0, beta1)
        """
        self.cache_method('AddDispEpsPole2ndOrderX', alpha0, alpha1, beta0, beta1)

    def add_disp_eps_pole_2nd_order_y(self, alpha0: float, alpha1: float, beta0: float, beta1: float) -> None:
        """
        VBA Call
        --------
        Material.AddDispEpsPole2ndOrderY(alpha0, alpha1, beta0, beta1)
        """
        self.cache_method('AddDispEpsPole2ndOrderY', alpha0, alpha1, beta0, beta1)

    def add_disp_eps_pole_2nd_order_z(self, alpha0: float, alpha1: float, beta0: float, beta1: float) -> None:
        """
        VBA Call
        --------
        Material.AddDispEpsPole2ndOrderZ(alpha0, alpha1, beta0, beta1)
        """
        self.cache_method('AddDispEpsPole2ndOrderZ', alpha0, alpha1, beta0, beta1)

    def add_disp_mu_pole_1st_order(self, alpha0: float, beta0: float) -> None:
        """
        VBA Call
        --------
        Material.AddDispMuPole1stOrder(alpha0, beta0)
        """
        self.cache_method('AddDispMuPole1stOrder', alpha0, beta0)

    def add_disp_mu_pole_1st_order_x(self, alpha0: float, beta0: float) -> None:
        """
        VBA Call
        --------
        Material.AddDispMuPole1stOrderX(alpha0, beta0)
        """
        self.cache_method('AddDispMuPole1stOrderX', alpha0, beta0)

    def add_disp_mu_pole_1st_order_y(self, alpha0: float, beta0: float) -> None:
        """
        VBA Call
        --------
        Material.AddDispMuPole1stOrderY(alpha0, beta0)
        """
        self.cache_method('AddDispMuPole1stOrderY', alpha0, beta0)

    def add_disp_mu_pole_1st_order_z(self, alpha0: float, beta0: float) -> None:
        """
        VBA Call
        --------
        Material.AddDispMuPole1stOrderZ(alpha0, beta0)
        """
        self.cache_method('AddDispMuPole1stOrderZ', alpha0, beta0)

    def add_disp_mu_pole_2nd_order(self, alpha0: float, alpha1: float, beta0: float, beta1: float) -> None:
        """
        VBA Call
        --------
        Material.AddDispMuPole2ndOrder(alpha0, alpha1, beta0, beta1)
        """
        self.cache_method('AddDispMuPole2ndOrder', alpha0, alpha1, beta0, beta1)

    def add_disp_mu_pole_2nd_order_x(self, alpha0: float, alpha1: float, beta0: float, beta1: float) -> None:
        """
        VBA Call
        --------
        Material.AddDispMuPole2ndOrderX(alpha0, alpha1, beta0, beta1)
        """
        self.cache_method('AddDispMuPole2ndOrderX', alpha0, alpha1, beta0, beta1)

    def add_disp_mu_pole_2nd_order_y(self, alpha0: float, alpha1: float, beta0: float, beta1: float) -> None:
        """
        VBA Call
        --------
        Material.AddDispMuPole2ndOrderY(alpha0, alpha1, beta0, beta1)
        """
        self.cache_method('AddDispMuPole2ndOrderY', alpha0, alpha1, beta0, beta1)

    def add_disp_mu_pole_2nd_order_z(self, alpha0: float, alpha1: float, beta0: float, beta1: float) -> None:
        """
        VBA Call
        --------
        Material.AddDispMuPole2ndOrderZ(alpha0, alpha1, beta0, beta1)
        """
        self.cache_method('AddDispMuPole2ndOrderZ', alpha0, alpha1, beta0, beta1)

    def set_mu_infinity(self, mu: float) -> None:
        """
        VBA Call
        --------
        Material.MuInfinity(mu)
        """
        self.cache_method('MuInfinity', mu)

    def set_mu_infinity_x(self, mu: float) -> None:
        """
        VBA Call
        --------
        Material.MuInfinityX(mu)
        """
        self.cache_method('MuInfinityX', mu)

    def set_mu_infinity_y(self, mu: float) -> None:
        """
        VBA Call
        --------
        Material.MuInfinityY(mu)
        """
        self.cache_method('MuInfinityY', mu)

    def set_mu_infinity_z(self, mu: float) -> None:
        """
        VBA Call
        --------
        Material.MuInfinityZ(mu)
        """
        self.cache_method('MuInfinityZ', mu)

    def set_disp_coeff0_mu(self, mu: float) -> None:
        """
        VBA Call
        --------
        Material.DispCoeff0Mu(mu)
        """
        self.cache_method('DispCoeff0Mu', mu)

    def set_disp_coeff0_mu_x(self, mu: float) -> None:
        """
        VBA Call
        --------
        Material.DispCoeff0MuX(mu)
        """
        self.cache_method('DispCoeff0MuX', mu)

    def set_disp_coeff0_mu_y(self, mu: float) -> None:
        """
        VBA Call
        --------
        Material.DispCoeff0MuY(mu)
        """
        self.cache_method('DispCoeff0MuY', mu)

    def set_disp_coeff0_mu_z(self, mu: float) -> None:
        """
        VBA Call
        --------
        Material.DispCoeff0MuZ(mu)
        """
        self.cache_method('DispCoeff0MuZ', mu)

    def set_disp_coeff1_mu(self, mu: float) -> None:
        """
        VBA Call
        --------
        Material.DispCoeff1Mu(mu)
        """
        self.cache_method('DispCoeff1Mu', mu)

    def set_disp_coeff1_mu_x(self, mu: float) -> None:
        """
        VBA Call
        --------
        Material.DispCoeff1MuX(mu)
        """
        self.cache_method('DispCoeff1MuX', mu)

    def set_disp_coeff1_mu_y(self, mu: float) -> None:
        """
        VBA Call
        --------
        Material.DispCoeff1MuY(mu)
        """
        self.cache_method('DispCoeff1MuY', mu)

    def set_disp_coeff1_mu_z(self, mu: float) -> None:
        """
        VBA Call
        --------
        Material.DispCoeff1MuZ(mu)
        """
        self.cache_method('DispCoeff1MuZ', mu)

    def set_disp_coeff2_mu(self, mu: float) -> None:
        """
        VBA Call
        --------
        Material.DispCoeff2Mu(mu)
        """
        self.cache_method('DispCoeff2Mu', mu)

    def set_disp_coeff2_mu_x(self, mu: float) -> None:
        """
        VBA Call
        --------
        Material.DispCoeff2MuX(mu)
        """
        self.cache_method('DispCoeff2MuX', mu)

    def set_disp_coeff2_mu_y(self, mu: float) -> None:
        """
        VBA Call
        --------
        Material.DispCoeff2MuY(mu)
        """
        self.cache_method('DispCoeff2MuY', mu)

    def set_disp_coeff2_mu_z(self, mu: float) -> None:
        """
        VBA Call
        --------
        Material.DispCoeff2MuZ(mu)
        """
        self.cache_method('DispCoeff2MuZ', mu)

    def set_disp_coeff3_mu(self, mu: float) -> None:
        """
        VBA Call
        --------
        Material.DispCoeff3Mu(mu)
        """
        self.cache_method('DispCoeff3Mu', mu)

    def set_disp_coeff3_mu_x(self, mu: float) -> None:
        """
        VBA Call
        --------
        Material.DispCoeff3MuX(mu)
        """
        self.cache_method('DispCoeff3MuX', mu)

    def set_disp_coeff3_mu_y(self, mu: float) -> None:
        """
        VBA Call
        --------
        Material.DispCoeff3MuY(mu)
        """
        self.cache_method('DispCoeff3MuY', mu)

    def set_disp_coeff3_mu_z(self, mu: float) -> None:
        """
        VBA Call
        --------
        Material.DispCoeff3MuZ(mu)
        """
        self.cache_method('DispCoeff3MuZ', mu)

    def set_disp_coeff4_mu(self, mu: float) -> None:
        """
        VBA Call
        --------
        Material.DispCoeff4Mu(mu)
        """
        self.cache_method('DispCoeff4Mu', mu)

    def set_disp_coeff4_mu_x(self, mu: float) -> None:
        """
        VBA Call
        --------
        Material.DispCoeff4MuX(mu)
        """
        self.cache_method('DispCoeff4MuX', mu)

    def set_disp_coeff4_mu_y(self, mu: float) -> None:
        """
        VBA Call
        --------
        Material.DispCoeff4MuY(mu)
        """
        self.cache_method('DispCoeff4MuY', mu)

    def set_disp_coeff4_mu_z(self, mu: float) -> None:
        """
        VBA Call
        --------
        Material.DispCoeff4MuZ(mu)
        """
        self.cache_method('DispCoeff4MuZ', mu)

    def set_use_si_unit_system(self, flag: bool) -> None:
        """
        VBA Call
        --------
        Material.UseSISystem(flag)
        """
        self.cache_method('UseSISystem', flag)

    def set_gyro_mu_frequency(self, frequency: float) -> None:
        """
        VBA Call
        --------
        Material.GyroMuFreq(frequency)
        """
        self.cache_method('GyroMuFreq', frequency)

    def set_magnetostatic_dep_source_field(self, source_field: str) -> None:
        """
        VBA Call
        --------
        Material.SetMagnetostaticDepSourceField(source_field)
        """
        self.cache_method('SetMagnetostaticDepSourceField', source_field)

    def set_dispersive_fitting_format_eps(self, format: Union[DispersiveFittingFormat, str]) -> None:
        """
        VBA Call
        --------
        Material.DispersiveFittingFormatEps(format)
        """
        self.cache_method('DispersiveFittingFormatEps', str(getattr(format, 'value', format)))

    def set_dispersive_fitting_format_mu(self, format: Union[DispersiveFittingFormat, str]) -> None:
        """
        VBA Call
        --------
        Material.DispersiveFittingFormatMu(format)
        """
        self.cache_method('DispersiveFittingFormatMu', str(getattr(format, 'value', format)))

    def add_dispersion_fitting_value_eps(self, d_freq: float, d_val: complex, d_weight: float) -> None:
        """
        VBA Call
        --------
        Material.AddDispersionFittingValueEps(d_freq, real(d_val), imag(d_val), d_weight)
        """
        self.cache_method('AddDispersionFittingValueEps', d_freq, d_val.real, d_val.imag, d_weight)

    def add_dispersion_fitting_value_mu(self, d_freq: float, d_val: complex, d_weight: float) -> None:
        """
        VBA Call
        --------
        Material.AddDispersionFittingValueMu(d_freq, real(d_val), imag(d_val), d_weight)
        """
        self.cache_method('AddDispersionFittingValueMu', d_freq, d_val.real, d_val.imag, d_weight)

    def add_dispersion_fitting_value_xyz_eps(self, d_freq: float, d_val: Tuple[complex, complex, complex], d_weight: float) -> None:
        """
        VBA Call
        --------
        Material.AddDispersionFittingValueXYZEps(d_freq, real(d_val[0]), imag(d_val[0]), real(d_val[1]), imag(d_val[1]), real(d_val[2]), imag(d_val[2]), d_weight)
        """
        self.cache_method('AddDispersionFittingValueXYZEps', d_freq, d_val[0].real, d_val[0].imag, d_val[1].real, d_val[1].imag, d_val[2].real, d_val[2].imag, d_weight)

    def add_dispersion_fitting_value_xyz_mu(self, d_freq: float, d_val: Tuple[complex, complex, complex], d_weight: float) -> None:
        """
        VBA Call
        --------
        Material.AddDispersionFittingValueXYZMu(d_freq, real(d_val[0]), imag(d_val[0]), real(d_val[1]), imag(d_val[1]), real(d_val[2]), imag(d_val[2]), d_weight)
        """
        self.cache_method('AddDispersionFittingValueXYZMu', d_freq, d_val[0].real, d_val[0].imag, d_val[1].real, d_val[1].imag, d_val[2].real, d_val[2].imag, d_weight)

    def set_dispersive_fitting_scheme_eps(self, scheme: Union[DispersiveFittingScheme, str]) -> None:
        """
        VBA Call
        --------
        Material.DispersiveFittingSchemeEps(scheme)
        """
        self.cache_method('DispersiveFittingSchemeEps', str(getattr(scheme, 'value', scheme)))

    def set_dispersive_fitting_scheme_mu(self, scheme: Union[DispersiveFittingScheme, str]) -> None:
        """
        VBA Call
        --------
        Material.DispersiveFittingSchemeMu(scheme)
        """
        self.cache_method('DispersiveFittingSchemeMu', str(getattr(scheme, 'value', scheme)))

    def set_max_order_nth_model_fit_eps(self, order: int) -> None:
        """
        VBA Call
        --------
        Material.MaximalOrderNthModelFitEps(order)
        """
        self.cache_method('MaximalOrderNthModelFitEps', order)

    def set_max_order_nth_model_fit_mu(self, order: int) -> None:
        """
        VBA Call
        --------
        Material.MaximalOrderNthModelFitMu(order)
        """
        self.cache_method('MaximalOrderNthModelFitMu', order)

    def set_error_limit_nth_model_fit_esp(self, limit: float) -> None:
        """
        VBA Call
        --------
        Material.ErrorLimitNthModelFitEps(limit)
        """
        self.cache_method('ErrorLimitNthModelFitEps', limit)

    def set_error_limit_nth_model_fit_mu(self, limit: float) -> None:
        """
        VBA Call
        --------
        Material.ErrorLimitNthModelFitMu(limit)
        """
        self.cache_method('ErrorLimitNthModelFitMu', limit)

    def set_use_only_data_in_sim_freq_range_nth_model_eps(self, flag: bool) -> None:
        """
        VBA Call
        --------
        Material.UseOnlyDataInSimFreqRangeNthModelEps(flag)
        """
        self.cache_method('UseOnlyDataInSimFreqRangeNthModelEps', flag)

    def set_use_only_data_in_sim_freq_range_nth_model_mu(self, flag: bool) -> None:
        """
        VBA Call
        --------
        Material.UseOnlyDataInSimFreqRangeNthModelMu(flag)
        """
        self.cache_method('UseOnlyDataInSimFreqRangeNthModelMu', flag)

    def set_use_general_dispersion_eps(self, flag: bool) -> None:
        """
        VBA Call
        --------
        Material.UseGeneralDispersionEps(flag)
        """
        self.cache_method('UseGeneralDispersionEps', flag)

    def set_use_general_dispersion_mu(self, flag: bool) -> None:
        """
        VBA Call
        --------
        Material.UseGeneralDispersionMu(flag)
        """
        self.cache_method('UseGeneralDispersionMu', flag)

    def set_tensor_formula_for(self, key: Union[TensorFormulaFor, str]) -> None:
        """
        VBA Call
        --------
        Material.TensorFormulaFor(key)
        """
        self.cache_method('TensorFormulaFor', str(getattr(key, 'value', key)))

    def set_tensor_formula_real(self, row: int, column: int, formula: str) -> None:
        """
        VBA Call
        --------
        Material.TensorFormulaReal(row, column, formula)
        """
        self.cache_method('TensorFormulaReal', row, column, formula)

    def set_tensor_formula_imag(self, row: int, column: int, formula: str) -> None:
        """
        VBA Call
        --------
        Material.TensorFormulaImag(row, column, formula)
        """
        self.cache_method('TensorFormulaImag', row, column, formula)

    def set_tensor_alignment(self, w: Tuple[float, float, float]) -> None:
        """
        VBA Call
        --------
        Material.TensorAlignment(w[0], w[1], w[2])
        """
        self.cache_method('TensorAlignment', w[0], w[1], w[2])

    def set_tensor_alignment2(self, u: Tuple[float, float, float], v: Tuple[float, float, float]) -> None:
        """
        VBA Call
        --------
        Material.TensorAlignment2(u[0], u[1], u[2], v[0], v[1], v[2])
        """
        self.cache_method('TensorAlignment2', u[0], u[1], u[2], v[0], v[1], v[2])

    def reset_spatially_varying_material_parameter(self, prop: Union[SpatiallyVarMatProp, str]) -> None:
        """
        VBA Call
        --------
        Material.ResetSpatiallyVaryingMaterialParameter(prop)
        """
        self.cache_method('ResetSpatiallyVaryingMaterialParameter', str(getattr(prop, 'value', prop)))

    def set_spatially_varying_material_model(self, prop: Union[SpatiallyVarMatProp, str], model: Union[SpatiallyVarMatModel, str]) -> None:
        """
        VBA Call
        --------
        Material.SpatiallyVaryingMaterialModel(prop, model)
        """
        self.cache_method('SpatiallyVaryingMaterialModel', str(getattr(prop, 'value', prop)), str(getattr(model, 'value', model)))

    def set_spatially_varying_material_model_aniso(self, prop: Union[SpatiallyVarMatProp, str], direction: Union[Direction, str], model: Union[SpatiallyVarMatModel, str]) -> None:
        """
        VBA Call
        --------
        Material.SpatiallyVaryingMaterialModelAniso(prop, direction, model)
        """
        self.cache_method('SpatiallyVaryingMaterialModelAniso', str(getattr(prop, 'value', prop)), str(getattr(direction, 'value', direction)), str(getattr(model, 'value', model)))

    def add_spatially_varying_material_parameter(self, prop: Union[SpatiallyVarMatProp, str], param: Union[SpatiallyVarMatParam, str], value: float) -> None:
        """
        VBA Call
        --------
        Material.AddSpatiallyVaryingMaterialParameter(prop, param, value)
        """
        self.cache_method('AddSpatiallyVaryingMaterialParameter', str(getattr(prop, 'value', prop)), str(getattr(param, 'value', param)), value)

    def add_spatially_varying_material_parameter_aniso(self, prop: Union[SpatiallyVarMatProp, str], direction: Union[Direction, str], param: Union[SpatiallyVarMatParam, str], value: float) -> None:
        """
        VBA Call
        --------
        Material.AddSpatiallyVaryingMaterialParameterAniso(prop, direction, param, value)
        """
        self.cache_method('AddSpatiallyVaryingMaterialParameterAniso', str(getattr(prop, 'value', prop)), str(getattr(direction, 'value', direction)), str(getattr(param, 'value', param)), value)

    def reset_space_map_based_material(self, prop: Union[SpaceMapMatProp, str]) -> None:
        """
        VBA Call
        --------
        Material.ResetSpaceMapBasedMaterial(prop)
        """
        self.cache_method('ResetSpaceMapBasedMaterial', str(getattr(prop, 'value', prop)))

    def set_space_map_based_operator(self, prop: Union[SpaceMapMatProp, str], model: Union[SpaceMapMatModel, str]) -> None:
        """
        VBA Call
        --------
        Material.SpaceMapBasedOperator(prop, model)
        """
        self.cache_method('SpaceMapBasedOperator', str(getattr(prop, 'value', prop)), str(getattr(model, 'value', model)))

    def set_space_map_based_operator_aniso(self, prop: Union[SpaceMapMatProp, str], direction: Union[Direction, str], model: Union[SpaceMapMatModel, str]) -> None:
        """
        VBA Call
        --------
        Material.SpaceMapBasedOperatorAniso(prop, direction, model)
        """
        self.cache_method('SpaceMapBasedOperatorAniso', str(getattr(prop, 'value', prop)), str(getattr(direction, 'value', direction)), str(getattr(model, 'value', model)))

    def add_space_map_based_material_string_parameter(self, prop: Union[SpaceMapMatProp, str], param: Union[SpaceMapMatParam, str], value: str) -> None:
        """
        VBA Call
        --------
        Material.AddSpaceMapBasedMaterialStringParameter(prop, param, value)
        """
        self.cache_method('AddSpaceMapBasedMaterialStringParameter', str(getattr(prop, 'value', prop)), str(getattr(param, 'value', param)), value)

    def add_space_map_based_material_double_parameter(self, prop: Union[SpaceMapMatProp, str], param: Union[SpaceMapMatParam, str], value: float) -> None:
        """
        VBA Call
        --------
        Material.AddSpaceMapBasedMaterialDoubleParameter(prop, param, value)
        """
        self.cache_method('AddSpaceMapBasedMaterialDoubleParameter', str(getattr(prop, 'value', prop)), str(getattr(param, 'value', param)), value)

    def add_space_map_based_material_string_parameter_aniso(self, prop: Union[SpaceMapMatProp, str], direction: Union[Direction, str], param: Union[SpaceMapMatParam, str], value: str) -> None:
        """
        VBA Call
        --------
        Material.AddSpaceMapBasedMaterialStringParameterAniso(prop, direction, param, value)
        """
        self.cache_method('AddSpaceMapBasedMaterialStringParameterAniso', str(getattr(prop, 'value', prop)), str(getattr(direction, 'value', direction)), str(getattr(param, 'value', param)), value)

    def add_space_map_based_material_double_parameter_aniso(self, prop: Union[SpaceMapMatProp, str], direction: Union[Direction, str], param: Union[SpaceMapMatParam, str], value: float) -> None:
        """
        VBA Call
        --------
        Material.AddSpaceMapBasedMaterialDoubleParameterAniso(prop, direction, param, value)
        """
        self.cache_method('AddSpaceMapBasedMaterialDoubleParameterAniso', str(getattr(prop, 'value', prop)), str(getattr(direction, 'value', direction)), str(getattr(param, 'value', param)), value)

    def convert_material_field(self, file_path_in: str, file_path_out: str) -> None:
        """
        VBA Call
        --------
        Material.ConvertMaterialField(file_path_in, file_path_out)
        """
        self.cache_method('ConvertMaterialField', file_path_in, file_path_out)

    def reset_tab_mu_differential(self) -> None:
        """
        VBA Call
        --------
        Material.ResetTabMuDifferential()
        """
        self.cache_method('ResetTabMuDifferential')

    def add_tab_mu_differential(self, h_field: float, mu_diff: float) -> None:
        """
        VBA Call
        --------
        Material.AddTabMuDifferential(h_field, mu_diff)
        """
        self.cache_method('AddTabMuDifferential', h_field, mu_diff)

    def set_generalized_debye_non_lin_dependency(self, dependency: Union[GeneralizedDebyeNonLinDep, str]) -> None:
        """
        VBA Call
        --------
        Material.GeneralizedDebyeNonLinDependency(dependency)
        """
        self.cache_method('GeneralizedDebyeNonLinDependency', str(getattr(dependency, 'value', dependency)))

    def set_magnetostatic_dep_source_field(self, source_field: str) -> None:
        """
        VBA Call
        --------
        Material.SetMagnetostaticDepSourceField(source_field)
        """
        self.cache_method('SetMagnetostaticDepSourceField', source_field)

    def set_coating_type_definition(self, prop: Union[CoatingTypeDef, str]) -> None:
        """
        VBA Call
        --------
        Material.SetCoatingTypeDefinition(prop)
        """
        self.cache_method('SetCoatingTypeDefinition', str(getattr(prop, 'value', prop)))

    def add_tabulated_surface_impedance_deg(self, frequency: float, angle: float, z_te: complex, z_tm: complex) -> None:
        """
        VBA Call
        --------
        Material.AddTabulatedSurfaceImpedance(frequency, angle, real(z_te), imag(z_te), real(z_tm), imag(z_tm))
        """
        self.cache_method('AddTabulatedSurfaceImpedance', frequency, angle, z_te.real, z_te.imag, z_tm.real, z_tm.imag)

    def add_tabulated_reflection_factor_deg(self, frequency: float, angle: float, r_te: complex, r_tm: complex) -> None:
        """
        VBA Call
        --------
        Material.AddTabulatedReflectionFactor(frequency, angle, real(r_te), imag(r_te), real(r_tm), imag(r_tm))
        """
        self.cache_method('AddTabulatedReflectionFactor', frequency, angle, r_te.real, r_te.imag, r_tm.real, r_tm.imag)

    def add_tabulated_reflection_transmission_factor_deg(self, frequency: float, angle: float, r_te: complex, r_tm: complex, t_te: complex, t_tm: complex) -> None:
        """
        VBA Call
        --------
        Material.AddTabulatedReflectionTransmissionFactor(frequency, angle, real(r_te), imag(r_te), real(r_tm), imag(r_tm), real(t_te), imag(t_te), real(t_tm), imag(t_tm))
        """
        self.cache_method('AddTabulatedReflectionTransmissionFactor', frequency, angle, r_te.real, r_te.imag, r_tm.real, r_tm.imag, t_te.real, t_te.imag, t_tm.real, t_tm.imag)

    def add_temperature_dep_eps(self, d_temperature: float, d_value: float) -> None:
        """
        VBA Call
        --------
        Material.AddTemperatureDepEps(d_temperature, d_value)
        """
        self.cache_method('AddTemperatureDepEps', d_temperature, d_value)

    def reset_temperature_dep_eps(self) -> None:
        """
        VBA Call
        --------
        Material.ResetTemperatureDepEps()
        """
        self.cache_method('ResetTemperatureDepEps')

    def add_temperature_dep_mu(self, d_temperature: float, d_value: float) -> None:
        """
        VBA Call
        --------
        Material.AddTemperatureDepMu(d_temperature, d_value)
        """
        self.cache_method('AddTemperatureDepMu', d_temperature, d_value)

    def reset_temperature_dep_mu(self) -> None:
        """
        VBA Call
        --------
        Material.ResetTemperatureDepMu()
        """
        self.cache_method('ResetTemperatureDepMu')

    def add_temperature_dep_sigma(self, d_temperature: float, d_value: float) -> None:
        """
        VBA Call
        --------
        Material.AddTemperatureDepSigma(d_temperature, d_value)
        """
        self.cache_method('AddTemperatureDepSigma', d_temperature, d_value)

    def reset_temperature_dep_sigma(self) -> None:
        """
        VBA Call
        --------
        Material.ResetTemperatureDepSigma()
        """
        self.cache_method('ResetTemperatureDepSigma')

    def set_temperature_dep_source_field(self, field_name: str) -> None:
        """
        VBA Call
        --------
        Material.SetTemperatureDepSourceField(field_name)
        """
        self.cache_method('SetTemperatureDepSourceField', field_name)

    def add_hb_value(self, h_value: float, b_value: float) -> None:
        """
        VBA Call
        --------
        Material.AddHBValue(h_value, b_value)
        """
        self.cache_method('AddHBValue', h_value, b_value)

    def reset_hb_list(self) -> None:
        """
        VBA Call
        --------
        Material.ResetHBList()
        """
        self.cache_method('ResetHBList')

    def set_use_nl_anisotropy(self, flag: bool) -> None:
        """
        VBA Call
        --------
        Material.NLAnisotropy(flag)
        """
        self.cache_method('NLAnisotropy', flag)

    def set_nla_stacking_factor(self, factor: float) -> None:
        """
        VBA Call
        --------
        Material.NLAStackingFactor(factor)
        """
        self.cache_method('NLAStackingFactor', factor)

    def set_nla_direction_x(self, dir: float) -> None:
        """
        VBA Call
        --------
        Material.NLADirectionX(dir)
        """
        self.cache_method('NLADirectionX', dir)

    def set_nla_direction_y(self, dir: float) -> None:
        """
        VBA Call
        --------
        Material.NLADirectionY(dir)
        """
        self.cache_method('NLADirectionY', dir)

    def set_nla_direction_z(self, dir: float) -> None:
        """
        VBA Call
        --------
        Material.NLADirectionZ(dir)
        """
        self.cache_method('NLADirectionZ', dir)

    def set_particle_property(self, prop: Union[ParticleProp, str]) -> None:
        """
        VBA Call
        --------
        Material.ParticleProperty(prop)
        """
        self.cache_method('ParticleProperty', str(getattr(prop, 'value', prop)))

    def set_se_model(self, model: Union[SeModel, str]) -> None:
        """
        VBA Call
        --------
        Material.SeModel(model)
        """
        self.cache_method('SeModel', str(getattr(model, 'value', model)))

    def set_se_max_number_of_generations(self, number: int) -> None:
        """
        VBA Call
        --------
        Material.SeMaxGenerations(number)
        """
        self.cache_method('SeMaxGenerations', number)

    def set_se_max_number_of_secondaries(self, number: int) -> None:
        """
        VBA Call
        --------
        Material.SeMaxSecondaries(number)
        """
        self.cache_method('SeMaxSecondaries', number)

    def set_se_ts_param_t1(self, value: float) -> None:
        """
        VBA Call
        --------
        Material.SeTsParam_T1(value)
        """
        self.cache_method('SeTsParam_T1', value)

    def set_se_ts_param_t2(self, value: float) -> None:
        """
        VBA Call
        --------
        Material.SeTsParam_T2(value)
        """
        self.cache_method('SeTsParam_T2', value)

    def set_se_ts_param_t3(self, value: float) -> None:
        """
        VBA Call
        --------
        Material.SeTsParam_T3(value)
        """
        self.cache_method('SeTsParam_T3', value)

    def set_se_ts_param_t4(self, value: float) -> None:
        """
        VBA Call
        --------
        Material.SeTsParam_T4(value)
        """
        self.cache_method('SeTsParam_T4', value)

    def set_se_ts_param_sey(self, value: float) -> None:
        """
        VBA Call
        --------
        Material.SeTsParam_SEY(value)
        """
        self.cache_method('SeTsParam_SEY', value)

    def set_se_ts_param_energy(self, value: float) -> None:
        """
        VBA Call
        --------
        Material.SeTsParam_Energy(value)
        """
        self.cache_method('SeTsParam_Energy', value)

    def set_se_ts_param_s(self, value: float) -> None:
        """
        VBA Call
        --------
        Material.SeTsParam_S(value)
        """
        self.cache_method('SeTsParam_S', value)

    def set_se_ts_param_pn(self, n: int, value: float) -> None:
        """
        VBA Call
        --------
        Material.SeTsParam_PN(n, value)
        """
        self.cache_method('SeTsParam_PN', n, value)

    def set_se_ts_param_epsn(self, n: int, value: float) -> None:
        """
        VBA Call
        --------
        Material.SeTsParam_EpsN(n, value)
        """
        self.cache_method('SeTsParam_EpsN', n, value)

    def set_se_rd_param_r(self, value: float) -> None:
        """
        VBA Call
        --------
        Material.SeRdParam_R(value)
        """
        self.cache_method('SeRdParam_R', value)

    def set_se_rd_param_r1(self, value: float) -> None:
        """
        VBA Call
        --------
        Material.SeRdParam_R1(value)
        """
        self.cache_method('SeRdParam_R1', value)

    def set_se_rd_param_r2(self, value: float) -> None:
        """
        VBA Call
        --------
        Material.SeRdParam_R2(value)
        """
        self.cache_method('SeRdParam_R2', value)

    def set_se_rd_param_q(self, value: float) -> None:
        """
        VBA Call
        --------
        Material.SeRdParam_Q(value)
        """
        self.cache_method('SeRdParam_Q', value)

    def set_se_rd_param_p1_inf(self, value: float) -> None:
        """
        VBA Call
        --------
        Material.SeRdParam_P1Inf(value)
        """
        self.cache_method('SeRdParam_P1Inf', value)

    def set_se_rd_param_energy(self, value: float) -> None:
        """
        VBA Call
        --------
        Material.SeRdParam_Energy(value)
        """
        self.cache_method('SeRdParam_Energy', value)

    def set_se_bs_param_sigma(self, value: float) -> None:
        """
        VBA Call
        --------
        Material.SeBsParam_Sigma(value)
        """
        self.cache_method('SeBsParam_Sigma', value)

    def set_se_bs_param_e1(self, value: float) -> None:
        """
        VBA Call
        --------
        Material.SeBsParam_E1(value)
        """
        self.cache_method('SeBsParam_E1', value)

    def set_se_bs_param_e2(self, value: float) -> None:
        """
        VBA Call
        --------
        Material.SeBsParam_E2(value)
        """
        self.cache_method('SeBsParam_E2', value)

    def set_se_bs_param_p1_hat(self, value: float) -> None:
        """
        VBA Call
        --------
        Material.SeBsParam_P1Hat(value)
        """
        self.cache_method('SeBsParam_P1Hat', value)

    def set_se_bs_param_p1_inf(self, value: float) -> None:
        """
        VBA Call
        --------
        Material.SeBsParam_P1Inf(value)
        """
        self.cache_method('SeBsParam_P1Inf', value)

    def set_se_bs_param_energy(self, value: float) -> None:
        """
        VBA Call
        --------
        Material.SeBsParam_Energy(value)
        """
        self.cache_method('SeBsParam_Energy', value)

    def set_se_bs_param_p(self, value: float) -> None:
        """
        VBA Call
        --------
        Material.SeBsParam_P(value)
        """
        self.cache_method('SeBsParam_P', value)

    def set_se_bs_param_w(self, value: float) -> None:
        """
        VBA Call
        --------
        Material.SeBsParam_W(value)
        """
        self.cache_method('SeBsParam_W', value)

    def enable_se_plot_1d_deg(self, angle: float, energy: float) -> None:
        """
        VBA Call
        --------
        Material.SePlot1D(True, angle, energy)
        """
        self.cache_method('SePlot1D', True, angle, energy)

    def disable_se_plot_1d_deg(self) -> None:
        """
        VBA Call
        --------
        Material.SePlot1D(False, 0, 0)
        """
        self.cache_method('SePlot1D', False, 0, 0)

    def setup_se_vaughan(self, energy_max: float, se_yield_max: float, energy_threshold: float, smoothness: float, temperature: float) -> None:
        """
        VBA Call
        --------
        Material.SeVaughan(energy_max, se_yield_max, energy_threshold, smoothness, temperature)
        """
        self.cache_method('SeVaughan', energy_max, se_yield_max, energy_threshold, smoothness, temperature)

    def set_se_import_settings(self, file_name: str, temperature: float) -> None:
        """
        VBA Call
        --------
        Material.SeImportSettings(file_name, temperature)
        """
        self.cache_method('SeImportSettings', file_name, temperature)

    def set_se_import_data(self, energy: float, sey: float) -> None:
        """
        VBA Call
        --------
        Material.SeImportData(energy, sey)
        """
        self.cache_method('SeImportData', energy, sey)

    def set_ion_see_model(self, model: Union[IonSeeModel, str]) -> None:
        """
        VBA Call
        --------
        Material.IonSEEModel(model)
        """
        self.cache_method('IonSEEModel', str(getattr(model, 'value', model)))

    def set_ion_see_import_settings(self, file_name: str, temperature: float) -> None:
        """
        VBA Call
        --------
        Material.IonSEEImportSettings(file_name, temperature)
        """
        self.cache_method('IonSEEImportSettings', file_name, temperature)

    def set_ion_see_import_data(self, energy: float, sey: float) -> None:
        """
        VBA Call
        --------
        Material.IonSEEImportData(energy, sey)
        """
        self.cache_method('IonSEEImportData', energy, sey)

    def set_particle_transparency_settings(self, type: Union[ParticleTransparencySettings, str], percent: float, file_name: str) -> None:
        """
        VBA Call
        --------
        Material.ParticleTransparencySettings(type, percent, file_name)
        """
        self.cache_method('ParticleTransparencySettings', str(getattr(type, 'value', type)), percent, file_name)

    def set_particle_transparency_import_data(self, energy: float, transparency: float) -> None:
        """
        VBA Call
        --------
        Material.ParticleTransparencyImportData(energy, transparency)
        """
        self.cache_method('ParticleTransparencyImportData', energy, transparency)

    def set_energy_step_for_sey_plots(self, step: float) -> None:
        """
        VBA Call
        --------
        Material.SetEnergyStepForSEYPlots(step)
        """
        self.cache_method('SetEnergyStepForSEYPlots', step)

    def set_special_disp_param_for_pic(self, esp_inf: float, relax_freq: float, reson_freq: float, reson_width: float, lorentz_weight: float) -> None:
        """
        VBA Call
        --------
        Material.SpecialDispParamForPIC(esp_inf, relax_freq, reson_freq, reson_width, lorentz_weight)
        """
        self.cache_method('SpecialDispParamForPIC', esp_inf, relax_freq, reson_freq, reson_width, lorentz_weight)

    def set_special_disp_param_visual(self, max_freq: float, prop_dist: float) -> None:
        """
        VBA Call
        --------
        Material.SpecialDispParamVisual(max_freq, prop_dist)
        """
        self.cache_method('SpecialDispParamVisual', max_freq, prop_dist)

    def set_thermal_type(self, thermal_type: str) -> None:
        """
        VBA Call
        --------
        Material.ThermalType(thermal_type)
        """
        self.cache_method('ThermalType', thermal_type)

    def set_thermal_conductivity(self, value: float) -> None:
        """
        VBA Call
        --------
        Material.ThermalConductivity(value)
        """
        self.cache_method('ThermalConductivity', value)

    def set_thermal_conductivity_x(self, value: float) -> None:
        """
        VBA Call
        --------
        Material.ThermalConductivityX(value)
        """
        self.cache_method('ThermalConductivityX', value)

    def set_thermal_conductivity_y(self, value: float) -> None:
        """
        VBA Call
        --------
        Material.ThermalConductivityY(value)
        """
        self.cache_method('ThermalConductivityY', value)

    def set_thermal_conductivity_z(self, value: float) -> None:
        """
        VBA Call
        --------
        Material.ThermalConductivityZ(value)
        """
        self.cache_method('ThermalConductivityZ', value)

    def set_specific_heat(self, value: float, unit: Union[SpecificHeatUnit, str]) -> None:
        """
        VBA Call
        --------
        Material.SpecificHeat(value, unit)
        """
        self.cache_method('SpecificHeat', value, str(getattr(unit, 'value', unit)))

    def set_blood_flow(self, value: float) -> None:
        """
        VBA Call
        --------
        Material.BloodFlow(value)
        """
        self.cache_method('BloodFlow', value)

    def set_metabolic_rate(self, value: float) -> None:
        """
        VBA Call
        --------
        Material.MetabolicRate(value)
        """
        self.cache_method('MetabolicRate', value)

    def set_voxel_convection(self, value: float) -> None:
        """
        VBA Call
        --------
        Material.VoxelConvection(value)
        """
        self.cache_method('VoxelConvection', value)

    def set_dynamic_viscosity(self, value: float) -> None:
        """
        VBA Call
        --------
        Material.DynamicViscosity(value)
        """
        self.cache_method('DynamicViscosity', value)

    def set_emissivity(self, value: float) -> None:
        """
        VBA Call
        --------
        Material.Emissivity(value)
        """
        self.cache_method('Emissivity', value)

    def reset_nl_thermal_cond(self) -> None:
        """
        VBA Call
        --------
        Material.ResetNLThermalCond()
        """
        self.cache_method('ResetNLThermalCond')

    def add_nl_thermal_cond(self, temperature: float, value: float) -> None:
        """
        VBA Call
        --------
        Material.AddNLThermalCond(temperature, value)
        """
        self.cache_method('AddNLThermalCond', temperature, value)

    def add_nl_thermal_cond_aniso(self, temperature: float, value_x: float, value_y: float, value_z: float) -> None:
        """
        VBA Call
        --------
        Material.AddNLThermalCondAniso(temperature, value_x, value_y, value_z)
        """
        self.cache_method('AddNLThermalCondAniso', temperature, value_x, value_y, value_z)

    def reset_nl_heat_cap(self) -> None:
        """
        VBA Call
        --------
        Material.ResetNLHeatCap()
        """
        self.cache_method('ResetNLHeatCap')

    def add_nl_specific_heat(self, temperature: float, value: float, unit: str) -> None:
        """
        VBA Call
        --------
        Material.AddNLSpecificHeat(temperature, value, unit)
        """
        self.cache_method('AddNLSpecificHeat', temperature, value, unit)

    def reset_nl_blook_flow(self) -> None:
        """
        VBA Call
        --------
        Material.ResetNLBloodFlow()
        """
        self.cache_method('ResetNLBloodFlow')

    def add_nl_blood_flow_min_temperature(self, value: float) -> None:
        """
        VBA Call
        --------
        Material.SetNLBloodFlowMinTemperature(value)
        """
        self.cache_method('SetNLBloodFlowMinTemperature', value)

    def add_nl_blood_flow_basal_value(self, value: float) -> None:
        """
        VBA Call
        --------
        Material.SetNLBloodFlowBasalValue(value)
        """
        self.cache_method('SetNLBloodFlowBasalValue', value)

    def add_nl_blood_flow_local_vasodilation_param(self, value: float) -> None:
        """
        VBA Call
        --------
        Material.SetNLBloodFlowLocalVasodilationParam(value)
        """
        self.cache_method('SetNLBloodFlowLocalVasodilationParam', value)

    def add_nl_blood_flow_max_multiplier(self, value: float) -> None:
        """
        VBA Call
        --------
        Material.SetNLBloodFlowMaxMultiplier(value)
        """
        self.cache_method('SetNLBloodFlowMaxMultiplier', value)

    def add_nl_dynamic_viscosity(self, temperature: float, value: float) -> None:
        """
        VBA Call
        --------
        Material.AddNLDynamicViscosity(temperature, value)
        """
        self.cache_method('AddNLDynamicViscosity', temperature, value)

    def set_mechanics_type(self, mechanics_type: Union[MechanicsType, str]) -> None:
        """
        VBA Call
        --------
        Material.MechanicsType(mechanics_type)
        """
        self.cache_method('MechanicsType', str(getattr(mechanics_type, 'value', mechanics_type)))

    def set_youngs_modulus(self, value: float) -> None:
        """
        VBA Call
        --------
        Material.YoungsModulus(value)
        """
        self.cache_method('YoungsModulus', value)

    def set_poisson_ratio(self, value: float) -> None:
        """
        VBA Call
        --------
        Material.PoissonsRatio(value)
        """
        self.cache_method('PoissonsRatio', value)

    def set_thermal_expansion_rate(self, value: float) -> None:
        """
        VBA Call
        --------
        Material.ThermalExpansionRate(value)
        """
        self.cache_method('ThermalExpansionRate', value)

    def reset_temp_dep_youngs_modulus(self) -> None:
        """
        VBA Call
        --------
        Material.ResetTempDepYoungsModulus()
        """
        self.cache_method('ResetTempDepYoungsModulus')

    def add_temp_dep_youngs_modulus(self, temperature: float, value: float) -> None:
        """
        VBA Call
        --------
        Material.AddTempDepYoungsModulus(temperature, value)
        """
        self.cache_method('AddTempDepYoungsModulus', temperature, value)

    def set_intrinsic_carrier_density(self, value: float) -> None:
        """
        VBA Call
        --------
        Material.IntrinsicCarrierDensity(value)
        """
        self.cache_method('IntrinsicCarrierDensity', value)

    def set_lattice_scattering(self, species: Union[Species, str], mobility: float, exponent: float) -> None:
        """
        VBA Call
        --------
        Material.LatticeScattering(species, mobility, exponent)
        """
        self.cache_method('LatticeScattering', str(getattr(species, 'value', species)), mobility, exponent)

    def set_effective_mass_for_conductivity(self, species: Union[Species, str], effective_mass: float) -> None:
        """
        VBA Call
        --------
        Material.EffectiveMassForConductivity(species, effective_mass)
        """
        self.cache_method('EffectiveMassForConductivity', str(getattr(species, 'value', species)), effective_mass)

    def enable_auger_recombination(self, gamma_electron: float, gamma_hole: float) -> None:
        """
        VBA Call
        --------
        Material.AugerRecombination(True, gamma_electron, gamma_hole)
        """
        self.cache_method('AugerRecombination', True, gamma_electron, gamma_hole)

    def disable_auger_recombination(self) -> None:
        """
        VBA Call
        --------
        Material.AugerRecombination(False, 0, 0)
        """
        self.cache_method('AugerRecombination', False, 0, 0)

    def enable_band_to_band_recombination(self, rate: float) -> None:
        """
        VBA Call
        --------
        Material.BandToBandRecombination(True, rate)
        """
        self.cache_method('BandToBandRecombination', True, rate)

    def disable_band_to_band_recombination(self) -> None:
        """
        VBA Call
        --------
        Material.BandToBandRecombination(False, 0)
        """
        self.cache_method('BandToBandRecombination', False, 0)

    def enable_impact_ionization(self, electron_ionization_rate: float, electron_exponent: float, electron_critical_field: float, hole_ionization_rate: float, hole_exponent: float, hole_critical_field: float) -> None:
        """
        VBA Call
        --------
        Material.ImpactIonization(True, electron_ionization_rate, electron_exponent, electron_critical_field, hole_ionization_rate, hole_exponent, hole_critical_field)
        """
        self.cache_method('ImpactIonization', True, electron_ionization_rate, electron_exponent, electron_critical_field, hole_ionization_rate, hole_exponent, hole_critical_field)

    def disable_impact_ionization(self) -> None:
        """
        VBA Call
        --------
        Material.ImpactIonization(False, 0, 0, 0, 0, 0, 0)
        """
        self.cache_method('ImpactIonization', False, 0, 0, 0, 0, 0, 0)

    def enable_optically_induced_carrier_generation(self, quantum_efficiency: float) -> None:
        """
        VBA Call
        --------
        Material.OpticallyInducedCarrierGeneration(True, quantum_efficiency)
        """
        self.cache_method('OpticallyInducedCarrierGeneration', True, quantum_efficiency)

    def disable_optically_induced_carrier_generation(self) -> None:
        """
        VBA Call
        --------
        Material.OpticallyInducedCarrierGeneration(False, 0)
        """
        self.cache_method('OpticallyInducedCarrierGeneration', False, 0)

    def enable_srh_recombination(self, trap_energy_level: float, electron_lifetime: float, electron_reference_density: float, hole_lifetime: float, hole_reference_density: float) -> None:
        """
        VBA Call
        --------
        Material.SRHRecombination(True, trap_energy_level, electron_lifetime, electron_reference_density, hole_lifetime, hole_reference_density)
        """
        self.cache_method('SRHRecombination', True, trap_energy_level, electron_lifetime, electron_reference_density, hole_lifetime, hole_reference_density)

    def disable_srh_recombination(self) -> None:
        """
        VBA Call
        --------
        Material.SRHRecombination(False, 0, 0, 0, 0, 0)
        """
        self.cache_method('SRHRecombination', False, 0, 0, 0, 0, 0)

    def set_flow_res_pressure_loss_type_u(self, value: Union[FlowResPressureLossTypeUVW, str]) -> None:
        """
        VBA Call
        --------
        Material.FlowResPressureLossTypeU(value)
        """
        self.cache_method('FlowResPressureLossTypeU', str(getattr(value, 'value', value)))

    def set_flow_res_pressure_loss_type_v(self, value: Union[FlowResPressureLossTypeUVW, str]) -> None:
        """
        VBA Call
        --------
        Material.FlowResPressureLossTypeV(value)
        """
        self.cache_method('FlowResPressureLossTypeV', str(getattr(value, 'value', value)))

    def set_flow_res_pressure_loss_type_w(self, value: Union[FlowResPressureLossTypeUVW, str]) -> None:
        """
        VBA Call
        --------
        Material.FlowResPressureLossTypeW(value)
        """
        self.cache_method('FlowResPressureLossTypeW', str(getattr(value, 'value', value)))

    def set_flow_res_loss_coefficient_u(self, value: float) -> None:
        """
        VBA Call
        --------
        Material.FlowResLossCoefficientU(value)
        """
        self.cache_method('FlowResLossCoefficientU', value)

    def set_flow_res_loss_coefficient_v(self, value: float) -> None:
        """
        VBA Call
        --------
        Material.FlowResLossCoefficientV(value)
        """
        self.cache_method('FlowResLossCoefficientV', value)

    def set_flow_res_loss_coefficient_w(self, value: float) -> None:
        """
        VBA Call
        --------
        Material.FlowResLossCoefficientW(value)
        """
        self.cache_method('FlowResLossCoefficientW', value)

    def set_flow_res_pressure_loss_type_sheet(self, value: Union[FlowResPressureLossTypeSheet, str]) -> None:
        """
        VBA Call
        --------
        Material.FlowResPressureLossTypeSheet(value)
        """
        self.cache_method('FlowResPressureLossTypeSheet', str(getattr(value, 'value', value)))

    def set_flow_res_loss_coefficient_sheet(self, value: float) -> None:
        """
        VBA Call
        --------
        Material.FlowResLossCoefficientSheet(value)
        """
        self.cache_method('FlowResLossCoefficientSheet', value)

    def set_flow_res_free_area_ratio(self, value: float) -> None:
        """
        VBA Call
        --------
        Material.FlowResFreeAreaRatio(value)
        """
        self.cache_method('FlowResFreeAreaRatio', value)

    def set_flow_res_shape_type(self, value: Union[FlowResShapeType, str]) -> None:
        """
        VBA Call
        --------
        Material.FlowResShapeType(value)
        """
        self.cache_method('FlowResShapeType', str(getattr(value, 'value', value)))

    def set_flow_res_shape_size(self, value: float) -> None:
        """
        VBA Call
        --------
        Material.FlowResShapeSize(value)
        """
        self.cache_method('FlowResShapeSize', value)

    def set_flow_res_shape_u_pitch(self, value: float) -> None:
        """
        VBA Call
        --------
        Material.FlowResShapeUPitch(value)
        """
        self.cache_method('FlowResShapeUPitch', value)

    def set_flow_res_shape_v_pitch(self, value: float) -> None:
        """
        VBA Call
        --------
        Material.FlowResShapeVPitch(value)
        """
        self.cache_method('FlowResShapeVPitch', value)

    def get_number_of_materials(self) -> int:
        """
        VBA Call
        --------
        Material.GetNumberOfMaterials()
        """
        return self.query_method_int('GetNumberOfMaterials')

    def get_name_of_material_from_index(self) -> str:
        """
        VBA Call
        --------
        Material.GetNameOfMaterialFromIndex()
        """
        return self.query_method_str('GetNameOfMaterialFromIndex')

    def is_background_material(self, material_name: str) -> bool:
        """
        VBA Call
        --------
        Material.IsBackgroundMaterial(material_name)
        """
        return self.query_method_bool('IsBackgroundMaterial', material_name)

    def get_type_of_background_material(self) -> Type:
        """
        VBA Call
        --------
        Material.GetTypeOfBackgroundMaterial()
        """
        __retval__ = self.query_method_str('GetTypeOfBackgroundMaterial')
        return Material.Type(__retval__)

    def get_type_of_material(self, material_name: str) -> Type:
        """
        VBA Call
        --------
        Material.GetTypeOfMaterial(material_name)
        """
        __retval__ = self.query_method_str('GetTypeOfMaterial', material_name)
        return Material.Type(__retval__)

    def get_color_rgb(self, material_name: str) -> Optional[Tuple]:
        """
        VBA Call
        --------
        Material.GetColour(material_name, &r, &g, &b)

        Returns
        -------
        Color
            (r, g, b) *on success* | None
        """
        __retval__ = self.query_method_t('GetColour', VBATypeName.Boolean, material_name, VBATypeName.Double, VBATypeName.Double, VBATypeName.Double)
        return None if not __retval__[0] else tuple(__retval__[1:])

    def get_epsilon(self, material_name: str) -> Optional[Tuple]:
        """
        VBA Call
        --------
        Material.GetEpsilon(material_name, &eps_x, &eps_y, &eps_z)

        Returns
        -------
        Epsilon
            (x, y, z) *on success* | None
        """
        __retval__ = self.query_method_t('GetEpsilon', VBATypeName.Boolean, material_name, VBATypeName.Double, VBATypeName.Double, VBATypeName.Double)
        return None if not __retval__[0] else tuple(__retval__[1:])

    def get_mu(self, material_name: str) -> Optional[Tuple]:
        """
        VBA Call
        --------
        Material.GetMu(material_name, &mu_x, &mu_y, &mu_z)

        Returns
        -------
        Mu
            (x, y, z) *on success* | None
        """
        __retval__ = self.query_method_t('GetMu', VBATypeName.Boolean, material_name, VBATypeName.Double, VBATypeName.Double, VBATypeName.Double)
        return None if not __retval__[0] else tuple(__retval__[1:])

    def get_el_sigma(self, material_name: str) -> Optional[Tuple]:
        """
        VBA Call
        --------
        Material.GetSigma(material_name, &sigma_x, &sigma_y, &sigma_z)

        Returns
        -------
        Sigma - electric
            (x, y, z) *on success* | None
        """
        __retval__ = self.query_method_t('GetSigma', VBATypeName.Boolean, material_name, VBATypeName.Double, VBATypeName.Double, VBATypeName.Double)
        return None if not __retval__[0] else tuple(__retval__[1:])

    def get_mag_sigma(self, material_name: str) -> Optional[Tuple]:
        """
        VBA Call
        --------
        Material.GetSigmaM(material_name, &sigma_x, &sigma_y, &sigma_z)

        Returns
        -------
        Sigma - magnetic
            (x, y, z) *on success* | None
        """
        __retval__ = self.query_method_t('GetSigmaM', VBATypeName.Boolean, material_name, VBATypeName.Double, VBATypeName.Double, VBATypeName.Double)
        return None if not __retval__[0] else tuple(__retval__[1:])

    def get_corrugation(self, material_name: str) -> Optional[Tuple]:
        """
        VBA Call
        --------
        Material.GetCorrugation(material_name, &depth, &gap_width, &tooth_width)

        Returns
        -------
        Corrugation
            (depth, gap_width, tooth_width) *on success* | None
        """
        __retval__ = self.query_method_t('GetCorrugation', VBATypeName.Boolean, material_name, VBATypeName.Double, VBATypeName.Double, VBATypeName.Double)
        return None if not __retval__[0] else tuple(__retval__[1:])

    def get_ohmic_sheet_impedance(self, material_name: str) -> Optional[complex]:
        """
        VBA Call
        --------
        Material.GetOhmicSheetImpedance(material_name, &re, &im)

        Returns
        -------
        Impedance
            complex(re, im) *on success* | None
        """
        __retval__ = self.query_method_t('GetOhmicSheetImpedance', VBATypeName.Boolean, material_name, VBATypeName.Double, VBATypeName.Double)
        return None if not __retval__[0] else complex(__retval__[1], __retval__[2])

    def get_rho(self, material_name: str) -> Optional[float]:
        """
        VBA Call
        --------
        Material.GetRho(material_name, &value)

        Returns
        -------
        Rho
            value *on success* | None
        """
        __retval__ = self.query_method_t('GetRho', VBATypeName.Boolean, material_name, VBATypeName.Double)
        return None if not __retval__[0] else __retval__[1]

    def get_dynamic_viscosity(self, material_name: str) -> Optional[float]:
        """
        VBA Call
        --------
        Material.GetDynamicViscosity(material_name, &value)

        Returns
        -------
        Dynamic viscosity
            value *on success* | None
        """
        __retval__ = self.query_method_t('GetDynamicViscosity', VBATypeName.Boolean, material_name, VBATypeName.Double)
        return None if not __retval__[0] else __retval__[1]

    def get_emissivity(self, material_name: str) -> Optional[float]:
        """
        VBA Call
        --------
        Material.GetEmissivity(material_name, &value)

        Returns
        -------
        Emissivity
            value *on success* | None
        """
        __retval__ = self.query_method_t('GetEmissivity', VBATypeName.Boolean, material_name, VBATypeName.Double)
        return None if not __retval__[0] else __retval__[1]

    def get_thermal_conductivity(self, material_name: str) -> Optional[Tuple]:
        """
        VBA Call
        --------
        Material.GetThermalConductivity(material_name, &x, &y, &z)

        Returns
        -------
        Thermal conductivity
            (x, y, z) *on success* | None
        """
        __retval__ = self.query_method_t('GetThermalConductivity', VBATypeName.Boolean, material_name, VBATypeName.Double, VBATypeName.Double, VBATypeName.Double)
        return None if not __retval__[0] else tuple(__retval__[1:])

    def get_specific_heat(self, material_name: str) -> Optional[float]:
        """
        VBA Call
        --------
        Material.GetSpecificHeat(material_name, &value)

        Returns
        -------
        Specific heat
            value *on success* | None
        """
        __retval__ = self.query_method_t('GetSpecificHeat', VBATypeName.Boolean, material_name, VBATypeName.Double)
        return None if not __retval__[0] else __retval__[1]

    def get_heat_capacity(self, material_name: str) -> Optional[float]:
        """
        VBA Call
        --------
        Material.GetHeatCapacity(material_name, &value)

        Returns
        -------
        Heat capacity
            value *on success* | None
        """
        __retval__ = self.query_method_t('GetHeatCapacity', VBATypeName.Boolean, material_name, VBATypeName.Double)
        return None if not __retval__[0] else __retval__[1]

    def get_blood_flow(self, material_name: str) -> Optional[float]:
        """
        VBA Call
        --------
        Material.GetBloodFlow(material_name, &value)

        Returns
        -------
        Blood flow
            value *on success* | None
        """
        __retval__ = self.query_method_t('GetBloodFlow', VBATypeName.Boolean, material_name, VBATypeName.Double)
        return None if not __retval__[0] else __retval__[1]

    def get_metabolic_rate(self, material_name: str) -> Optional[float]:
        """
        VBA Call
        --------
        Material.GetMetabolicRate(material_name, &value)

        Returns
        -------
        Metabolic rate
            value *on success* | None
        """
        __retval__ = self.query_method_t('GetMetabolicRate', VBATypeName.Boolean, material_name, VBATypeName.Double)
        return None if not __retval__[0] else __retval__[1]

    def get_voxel_convection(self, material_name: str) -> Optional[float]:
        """
        VBA Call
        --------
        Material.GetVoxelConvection(material_name, &value)

        Returns
        -------
        Voxel convection
            value *on success* | None
        """
        __retval__ = self.query_method_t('GetVoxelConvection', VBATypeName.Boolean, material_name, VBATypeName.Double)
        return None if not __retval__[0] else __retval__[1]

    def exists(self, material_name: str) -> bool:
        """
        VBA Call
        --------
        Material.Exists(material_name)
        """
        return self.query_method_bool('Exists', material_name)

    def change_background_material(self) -> None:
        """
        VBA Call
        --------
        Material.ChangeBackgroundMaterial()
        """
        self.cache_method('ChangeBackgroundMaterial')
        self.flush_cache('ChangeBackgroundMaterial (Material)')

    def set_use_emissivity(self, flag: bool) -> None:
        """
        VBA Call
        --------
        Material.UseEmissivity(flag)
        """
        self.cache_method('UseEmissivity', flag)

