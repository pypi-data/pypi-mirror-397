'''This file is auto-generated. Do not edit.'''
from .. import IVBAProvider, VBAObjWrapper
from enum import Enum
from typing import Union

class MeshSettings(VBAObjWrapper):
    class MeshType(Enum):
        HEX = 'Hex'
        HEX_TLM = 'HexTLM'
        TET = 'Tet'
        UNSTR = 'Unstr'
        ALL = 'All'

    def __init__(self, vbap: IVBAProvider) -> None:
        super().__init__(vbap, 'MeshSettings')
        self.set_save_history(False)

    def set_mesh_type(self, mesh_type: Union[MeshType, str]) -> None:
        """
        VBA Call
        --------
        MeshSettings.SetMeshType(mesh_type)
        """
        self.record_method('SetMeshType', str(getattr(mesh_type, 'value', mesh_type)))

    def set_version(self, version: int) -> None:
        """
        VBA Call
        --------
        MeshSettings.Set('Version', version)
        """
        self.record_method('Set', 'Version', version)

    def set_steps_per_wave_near(self, steps: float) -> None:
        """
        VBA Call
        --------
        MeshSettings.Set('StepsPerWaveNear', steps)
        """
        self.record_method('Set', 'StepsPerWaveNear', steps)

    def set_steps_per_wave_far(self, steps: float) -> None:
        """
        VBA Call
        --------
        MeshSettings.Set('StepsPerWaveFar', steps)
        """
        self.record_method('Set', 'StepsPerWaveFar', steps)

    def set_wavelength_refinement_same_as_near(self, flag: bool) -> None:
        """
        VBA Call
        --------
        MeshSettings.Set('WavelengthRefinementSameAsNear', 1 if flag else 0)
        """
        self.record_method('Set', 'WavelengthRefinementSameAsNear', 1 if flag else 0)

    def set_steps_per_box_near(self, steps: float) -> None:
        """
        VBA Call
        --------
        MeshSettings.Set('StepsPerBoxNear', steps)
        """
        self.record_method('Set', 'StepsPerBoxNear', steps)

    def set_steps_per_box_far(self, steps: float) -> None:
        """
        VBA Call
        --------
        MeshSettings.Set('StepsPerBoxFar', steps)
        """
        self.record_method('Set', 'StepsPerBoxFar', steps)

    def set_max_step_near(self, step: float) -> None:
        """
        VBA Call
        --------
        MeshSettings.Set('MaxStepNear', step)
        """
        self.record_method('Set', 'MaxStepNear', step)

    def set_max_step_far(self, step: float) -> None:
        """
        VBA Call
        --------
        MeshSettings.Set('MaxStepFar', step)
        """
        self.record_method('Set', 'MaxStepFar', step)

    def set_model_box_descr_near(self, descr: str) -> None:
        """
        VBA Call
        --------
        MeshSettings.Set('ModelBoxDescrNear', descr)
        """
        self.record_method('Set', 'ModelBoxDescrNear', descr)

    def set_model_box_descr_far(self, descr: str) -> None:
        """
        VBA Call
        --------
        MeshSettings.Set('ModelBoxDescrFar', descr)
        """
        self.record_method('Set', 'ModelBoxDescrFar', descr)

    def set_use_max_step_absolute(self, flag: bool) -> None:
        """
        VBA Call
        --------
        MeshSettings.Set('UseMaxStepAbsolute', 1 if flag else 0)
        """
        self.record_method('Set', 'UseMaxStepAbsolute', 1 if flag else 0)

    def set_geometry_refinement_same_as_near(self, flag: bool) -> None:
        """
        VBA Call
        --------
        MeshSettings.Set('GeometryRefinementSameAsNear', 1 if flag else 0)
        """
        self.record_method('Set', 'GeometryRefinementSameAsNear', 1 if flag else 0)

    def set_use_ratio_limit_geometry(self, flag: bool) -> None:
        """
        VBA Call
        --------
        MeshSettings.Set('UseRatioLimitGeometry', 1 if flag else 0)
        """
        self.record_method('Set', 'UseRatioLimitGeometry', 1 if flag else 0)

    def set_ratio_limit_geometry(self, limit: float) -> None:
        """
        VBA Call
        --------
        MeshSettings.Set('RatioLimitGeometry', limit)
        """
        self.record_method('Set', 'RatioLimitGeometry', limit)

    def set_min_step_geometry_x(self, step: float) -> None:
        """
        VBA Call
        --------
        MeshSettings.Set('MinStepGeometryX', step)
        """
        self.record_method('Set', 'MinStepGeometryX', step)

    def set_min_step_geometry_y(self, step: float) -> None:
        """
        VBA Call
        --------
        MeshSettings.Set('MinStepGeometryY', step)
        """
        self.record_method('Set', 'MinStepGeometryY', step)

    def set_min_step_geometry_z(self, step: float) -> None:
        """
        VBA Call
        --------
        MeshSettings.Set('MinStepGeometryZ', step)
        """
        self.record_method('Set', 'MinStepGeometryZ', step)

    def set_use_same_min_step_geometry(self, flag: bool) -> None:
        """
        VBA Call
        --------
        MeshSettings.Set('UseSameMinStepGeometryXYZ', 1 if flag else 0)
        """
        self.record_method('Set', 'UseSameMinStepGeometryXYZ', 1 if flag else 0)

    def set_plane_merge_version(self, version: str) -> None:
        """
        VBA Call
        --------
        MeshSettings.Set('PlaneMergeVersion', version)
        """
        self.record_method('Set', 'PlaneMergeVersion', version)

    def set_face_refinement_on(self, flag: bool) -> None:
        """
        VBA Call
        --------
        MeshSettings.Set('FaceRefinementOn', 1 if flag else 0)
        """
        self.record_method('Set', 'FaceRefinementOn', 1 if flag else 0)

    def set_face_refinement_policy(self, value: float) -> None:
        """
        VBA Call
        --------
        MeshSettings.Set('FaceRefinementPolicy', value)
        """
        self.record_method('Set', 'FaceRefinementPolicy', value)

    def set_face_refinement_ratio(self, value: float) -> None:
        """
        VBA Call
        --------
        MeshSettings.Set('FaceRefinementRatio', value)
        """
        self.record_method('Set', 'FaceRefinementRatio', value)

    def set_face_refinement_step(self, value: float) -> None:
        """
        VBA Call
        --------
        MeshSettings.Set('FaceRefinementStep', value)
        """
        self.record_method('Set', 'FaceRefinementStep', value)

    def set_face_refinement_number_of_steps(self, number: int) -> None:
        """
        VBA Call
        --------
        MeshSettings.Set('FaceRefinementNSteps', number)
        """
        self.record_method('Set', 'FaceRefinementNSteps', number)

    def set_face_refinement_number_of_buffer_lines(self, number: int) -> None:
        """
        VBA Call
        --------
        MeshSettings.Set('FaceRefinementBufferLines', number)
        """
        self.record_method('Set', 'FaceRefinementBufferLines', number)

    def set_ellipse_refinement_on(self, flag: bool) -> None:
        """
        VBA Call
        --------
        MeshSettings.Set('EllipseRefinementOn', 1 if flag else 0)
        """
        self.record_method('Set', 'EllipseRefinementOn', 1 if flag else 0)

    def set_ellipse_refinement_policy(self, value: int) -> None:
        """
        VBA Call
        --------
        MeshSettings.Set('EllipseRefinementPolicy', value)
        """
        self.record_method('Set', 'EllipseRefinementPolicy', value)

    def set_ellipse_refinement_ratio(self, value: float) -> None:
        """
        VBA Call
        --------
        MeshSettings.Set('EllipseRefinementRatio', value)
        """
        self.record_method('Set', 'EllipseRefinementRatio', value)

    def set_ellipse_refinement_step(self, value: float) -> None:
        """
        VBA Call
        --------
        MeshSettings.Set('EllipseRefinementStep', value)
        """
        self.record_method('Set', 'EllipseRefinementStep', value)

    def set_ellipse_refinement_number_of_steps(self, number: int) -> None:
        """
        VBA Call
        --------
        MeshSettings.Set('EllipseRefinementNSteps', number)
        """
        self.record_method('Set', 'EllipseRefinementNSteps', number)

    def set_edge_refinement_on(self, flag: bool) -> None:
        """
        VBA Call
        --------
        MeshSettings.Set('EdgeRefinementOn', 1 if flag else 0)
        """
        self.record_method('Set', 'EdgeRefinementOn', 1 if flag else 0)

    def set_edge_refinement_policy(self, value: int) -> None:
        """
        VBA Call
        --------
        MeshSettings.Set('EdgeRefinementPolicy', value)
        """
        self.record_method('Set', 'EdgeRefinementPolicy', value)

    def set_edge_refinement_ratio(self, value: float) -> None:
        """
        VBA Call
        --------
        MeshSettings.Set('EdgeRefinementRatio', value)
        """
        self.record_method('Set', 'EdgeRefinementRatio', value)

    def set_edge_refinement_step(self, value: float) -> None:
        """
        VBA Call
        --------
        MeshSettings.Set('EdgeRefinementStep', value)
        """
        self.record_method('Set', 'EdgeRefinementStep', value)

    def set_edge_refinement_number_of_buffer_lines(self, number: int) -> None:
        """
        VBA Call
        --------
        MeshSettings.Set('EdgeRefinementBufferLines', number)
        """
        self.record_method('Set', 'EdgeRefinementBufferLines', number)

    def set_refine_edge_material_global(self, flag: bool) -> None:
        """
        VBA Call
        --------
        MeshSettings.Set('RefineEdgeMaterialGlobal', 1 if flag else 0)
        """
        self.record_method('Set', 'RefineEdgeMaterialGlobal', 1 if flag else 0)

    def set_refine_axial_edge_global(self, flag: bool) -> None:
        """
        VBA Call
        --------
        MeshSettings.Set('RefineAxialEdgeGlobal', 1 if flag else 0)
        """
        self.record_method('Set', 'RefineAxialEdgeGlobal', 1 if flag else 0)

    def set_number_of_buffer_lines_near(self, number: int) -> None:
        """
        VBA Call
        --------
        MeshSettings.Set('BufferLinesNear', number)
        """
        self.record_method('Set', 'BufferLinesNear', number)

    def set_use_dielectrics(self, flag: bool) -> None:
        """
        VBA Call
        --------
        MeshSettings.Set('UseDielectrics', 1 if flag else 0)
        """
        self.record_method('Set', 'UseDielectrics', 1 if flag else 0)

    def set_equilibrate_on(self, flag: bool) -> None:
        """
        VBA Call
        --------
        MeshSettings.Set('EquilibrateOn', 1 if flag else 0)
        """
        self.record_method('Set', 'EquilibrateOn', 1 if flag else 0)

    def set_equilibrate(self, value: float) -> None:
        """
        VBA Call
        --------
        MeshSettings.Set('Equilibrate', value)
        """
        self.record_method('Set', 'Equilibrate', value)

    def set_ignore_thin_panel_material(self, flag: bool) -> None:
        """
        VBA Call
        --------
        MeshSettings.Set('IgnoreThinPanelMaterial', 1 if flag else 0)
        """
        self.record_method('Set', 'IgnoreThinPanelMaterial', 1 if flag else 0)

    def set_snap_to_axial_edges(self, flag: bool) -> None:
        """
        VBA Call
        --------
        MeshSettings.Set('SnapToAxialEdges', 1 if flag else 0)
        """
        self.record_method('Set', 'SnapToAxialEdges', 1 if flag else 0)

    def set_snap_to_planes(self, flag: bool) -> None:
        """
        VBA Call
        --------
        MeshSettings.Set('SnapToPlanes', 1 if flag else 0)
        """
        self.record_method('Set', 'SnapToPlanes', 1 if flag else 0)

    def set_snap_to_spheres(self, flag: bool) -> None:
        """
        VBA Call
        --------
        MeshSettings.Set('SnapToSpheres', 1 if flag else 0)
        """
        self.record_method('Set', 'SnapToSpheres', 1 if flag else 0)

    def set_snap_to_ellipses(self, flag: bool) -> None:
        """
        VBA Call
        --------
        MeshSettings.Set('SnapToEllipses', 1 if flag else 0)
        """
        self.record_method('Set', 'SnapToEllipses', 1 if flag else 0)

    def set_snap_to_cylinders(self, flag: bool) -> None:
        """
        VBA Call
        --------
        MeshSettings.Set('SnapToCylinders', 1 if flag else 0)
        """
        self.record_method('Set', 'SnapToCylinders', 1 if flag else 0)

    def set_snap_to_cylinder_centers(self, flag: bool) -> None:
        """
        VBA Call
        --------
        MeshSettings.Set('SnapToCylinderCenters', 1 if flag else 0)
        """
        self.record_method('Set', 'SnapToCylinderCenters', 1 if flag else 0)

    def set_phase_error_near(self, error: float) -> None:
        """
        VBA Call
        --------
        MeshSettings.Set('PhaseErrorNear', error)
        """
        self.record_method('Set', 'PhaseErrorNear', error)

    def set_phase_error_far(self, error: float) -> None:
        """
        VBA Call
        --------
        MeshSettings.Set('PhaseErrorFar', error)
        """
        self.record_method('Set', 'PhaseErrorFar', error)

    def set_cells_per_wavelength_policy(self, policy: str) -> None:
        """
        VBA Call
        --------
        MeshSettings.Set('CellsPerWavelengthPolicy', policy)
        """
        self.record_method('Set', 'CellsPerWavelengthPolicy', policy)

    def set_min_step(self, step: float) -> None:
        """
        VBA Call
        --------
        MeshSettings.Set('MinStep', step)
        """
        self.record_method('Set', 'MinStep', step)

    def set_method(self, method: str) -> None:
        """
        VBA Call
        --------
        MeshSettings.Set('Method', method)
        """
        self.record_method('Set', 'Method', method)

    def set_curvature_order(self, order: int) -> None:
        """
        VBA Call
        --------
        MeshSettings.Set('CurvatureOrder', order)
        """
        self.record_method('Set', 'CurvatureOrder', order)

    def set_curvature_order_policy(self, policy: str) -> None:
        """
        VBA Call
        --------
        MeshSettings.Set('CurvatureOrderPolicy', policy)
        """
        self.record_method('Set', 'CurvatureOrderPolicy', policy)

    def set_curv_refinement_control(self, value: str) -> None:
        """
        VBA Call
        --------
        MeshSettings.Set('CurvRefinementControl', value)
        """
        self.record_method('Set', 'CurvRefinementControl', value)

    def set_normal_tolerance(self, value: float) -> None:
        """
        VBA Call
        --------
        MeshSettings.Set('NormalTolerance', value)
        """
        self.record_method('Set', 'NormalTolerance', value)

    def set_srf_mesh_gradation(self, value: float) -> None:
        """
        VBA Call
        --------
        MeshSettings.Set('SrfMeshGradation', value)
        """
        self.record_method('Set', 'SrfMeshGradation', value)

    def set_srf_mesh_optimization(self, flag: bool) -> None:
        """
        VBA Call
        --------
        MeshSettings.Set('SrfMeshOptimization', 1 if flag else 0)
        """
        self.record_method('Set', 'SrfMeshOptimization', 1 if flag else 0)

    def set_use_materials(self, flag: bool) -> None:
        """
        VBA Call
        --------
        MeshSettings.Set('UseMaterials', 1 if flag else 0)
        """
        self.record_method('Set', 'UseMaterials', 1 if flag else 0)

    def set_move_mesh(self, flag: bool) -> None:
        """
        VBA Call
        --------
        MeshSettings.Set('MoveMesh', 1 if flag else 0)
        """
        self.record_method('Set', 'MoveMesh', 1 if flag else 0)

    def set_automatic_edge_refinement(self, flag: bool) -> None:
        """
        VBA Call
        --------
        MeshSettings.Set('AutomaticEdgeRefinement', 1 if flag else 0)
        """
        self.record_method('Set', 'AutomaticEdgeRefinement', 1 if flag else 0)

    def set_use_aniso_curve_refinement(self, flag: bool) -> None:
        """
        VBA Call
        --------
        MeshSettings.Set('UseAnisoCurveRefinement', 1 if flag else 0)
        """
        self.record_method('Set', 'UseAnisoCurveRefinement', 1 if flag else 0)

    def set_use_same_srf_and_vol_mesh_gradation(self, flag: bool) -> None:
        """
        VBA Call
        --------
        MeshSettings.Set('UseSameSrfAndVolMeshGradation', 1 if flag else 0)
        """
        self.record_method('Set', 'UseSameSrfAndVolMeshGradation', 1 if flag else 0)

    def set_vol_mesh_gradation(self, value: float) -> None:
        """
        VBA Call
        --------
        MeshSettings.Set('VolMeshGradation', value)
        """
        self.record_method('Set', 'VolMeshGradation', value)

    def set_vol_mesh_optimization(self, flag: bool) -> None:
        """
        VBA Call
        --------
        MeshSettings.Set('VolMeshOptimization', 1 if flag else 0)
        """
        self.record_method('Set', 'VolMeshOptimization', 1 if flag else 0)

    def set_small_feature_size(self, value: float) -> None:
        """
        VBA Call
        --------
        MeshSettings.Set('SmallFeatureSize', value)
        """
        self.record_method('Set', 'SmallFeatureSize', value)

    def set_coincidence_tolerance(self, value: float) -> None:
        """
        VBA Call
        --------
        MeshSettings.Set('CoincidenceTolerance', value)
        """
        self.record_method('Set', 'CoincidenceTolerance', value)

    def set_self_intersection_check(self, flag: bool) -> None:
        """
        VBA Call
        --------
        MeshSettings.Set('SelfIntersectionCheck', 1 if flag else 0)
        """
        self.record_method('Set', 'SelfIntersectionCheck', 1 if flag else 0)

    def set_optimize_for_planar_structures(self, flag: bool) -> None:
        """
        VBA Call
        --------
        MeshSettings.Set('OptimizeForPlanarStructures', 1 if flag else 0)
        """
        self.record_method('Set', 'OptimizeForPlanarStructures', 1 if flag else 0)

