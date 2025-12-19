'''This file is auto-generated. Do not edit.'''
from .. import IVBAProvider, VBAObjWrapper
from enum import Enum
from typing import Union, Tuple

class Mesh(VBAObjWrapper):
    class MeshType(Enum):
        PBA = 'PBA'
        STAIRCASE = 'Staircase'
        TETRAHEDRAL = 'Tetrahedral'
        SURFACE = 'Surface'
        SURFACE_ML = 'SurfaceML'

    class PbaType(Enum):
        PBA = 'PBA'
        FAST_PBA = 'Fast PBA'

    class ParallelMesherType(Enum):
        HEX = 'Hex'
        TET = 'Tet'

    class ParallelMesherMode(Enum):
        MAXIMUM = 'maximum'
        USER_DEFINED = 'user-defined'
        NONE = 'none'

    class AutomeshRefineDielectrics(Enum):
        NONE = 'None'
        WAVE = 'Wave'
        STATIC = 'Static'

    class SurfaceMeshMethod(Enum):
        GENERAL = 'General'
        FAST = 'Fast'

    class SurfaceToleranceType(Enum):
        RELATIVE = 'Relative'
        ABSOLUTE = 'Absolute'

    class VolumeMeshMethod(Enum):
        DELAUNAY = 'Delaunay'
        ADVANCING_FRONT = 'Advancing Front'

    class PickType(Enum):
        MIDPOINT = 'Midpoint'
        FACECENTER = 'Facecenter'
        CENTERPOINT = 'Centerpoint'
        ENDPOINT = 'Endpoint'
        CIRCLE_ENDPOINT = 'CircleEndpoint'
        CIRCLEPOINT = 'Circlepoint'

    class SpatialVariation(Enum):
        NONE = 'none'
        SPHERICAL = 'spherical'
        CURVE = 'curve'

    def __init__(self, vbap: IVBAProvider) -> None:
        super().__init__(vbap, 'Mesh')
        self.set_save_history(False)

    def set_mesh_type(self, mesh_type: Union[MeshType, str]) -> None:
        """
        VBA Call
        --------
        Mesh.MeshType(mesh_type)
        """
        self.record_method('MeshType', str(getattr(mesh_type, 'value', mesh_type)))

    def set_creator(self, creator: str) -> None:
        """
        VBA Call
        --------
        Mesh.SetCreator(creator)
        """
        self.record_method('SetCreator', creator)

    def set_connectivity_check(self, flag: bool = True) -> None:
        """
        VBA Call
        --------
        Mesh.ConnectivityCheck(flag)
        """
        self.record_method('ConnectivityCheck', flag)

    def set_cad_processing_method(self, method: str, undocumented_param: int = -1) -> None:
        """
        VBA Call
        --------
        Mesh.SetCADProcessingMethod(method, undocumented_param)
        """
        self.record_method('SetCADProcessingMethod', method, undocumented_param)

    def set_gpu_for_matrix_calculation_disabled(self, flag: bool = True) -> None:
        """
        VBA Call
        --------
        Mesh.SetGPUForMatrixCalculationDisabled(flag)
        """
        self.record_method('SetGPUForMatrixCalculationDisabled', flag)

    def set_tst_version(self, version: str) -> None:
        """
        VBA Call
        --------
        Mesh.TSTVersion(version)
        """
        self.record_method('TSTVersion', version)

    def set_pba_version(self, version: str) -> None:
        """
        VBA Call
        --------
        Mesh.PBAVersion(version)
        """
        self.record_method('PBAVersion', version)

    def set_pba_type(self, pba_type: Union[PbaType, str]) -> None:
        """
        VBA Call
        --------
        Mesh.PBAType(pba_type)
        """
        self.record_method('PBAType', str(getattr(pba_type, 'value', pba_type)))

    def set_automatic_pba_type(self, flag: bool = True) -> None:
        """
        VBA Call
        --------
        Mesh.AutomaticPBAType(flag)
        """
        self.record_method('AutomaticPBAType', flag)

    def set_number_of_lines_per_wavelength(self, number: int) -> None:
        """
        VBA Call
        --------
        Mesh.LinesPerWavelength(number)
        """
        self.record_method('LinesPerWavelength', number)

    def set_min_number_of_steps(self, number: int) -> None:
        """
        VBA Call
        --------
        Mesh.MinimumStepNumber(number)
        """
        self.record_method('MinimumStepNumber', number)

    def set_ratio_limit(self, value: float) -> None:
        """
        VBA Call
        --------
        Mesh.RatioLimit(value)
        """
        self.record_method('RatioLimit', value)

    def set_use_ratio_limit(self, flag: bool = True) -> None:
        """
        VBA Call
        --------
        Mesh.UseRatioLimit(flag)
        """
        self.record_method('UseRatioLimit', flag)

    def set_smallest_mesh_step(self, value: float) -> None:
        """
        VBA Call
        --------
        Mesh.SmallestMeshStep(value)
        """
        self.record_method('SmallestMeshStep', value)

    def set_steps_per_wavelength_tet(self, value: float) -> None:
        """
        VBA Call
        --------
        Mesh.StepsPerWavelengthTet(value)
        """
        self.record_method('StepsPerWavelengthTet', value)

    def set_steps_per_wavelength_srf(self, value: float) -> None:
        """
        VBA Call
        --------
        Mesh.StepsPerWavelengthSrf(value)
        """
        self.record_method('StepsPerWavelengthSrf', value)

    def set_steps_per_wavelength_srf_ml(self, value: float) -> None:
        """
        VBA Call
        --------
        Mesh.StepsPerWavelengthSrfML(value)
        """
        self.record_method('StepsPerWavelengthSrfML', value)

    def set_minimum_step_number_tet(self, value: float) -> None:
        """
        VBA Call
        --------
        Mesh.MinimumStepNumberTet(value)
        """
        self.record_method('MinimumStepNumberTet', value)

    def set_minimum_step_number_srf(self, value: float) -> None:
        """
        VBA Call
        --------
        Mesh.MinimumStepNumberSrf(value)
        """
        self.record_method('MinimumStepNumberSrf', value)

    def set_minimum_step_number_srf_ml(self, value: float) -> None:
        """
        VBA Call
        --------
        Mesh.MinimumStepNumberSrfML(value)
        """
        self.record_method('MinimumStepNumberSrfML', value)

    def set_automesh(self, flag: bool = True) -> None:
        """
        VBA Call
        --------
        Mesh.Automesh(flag)
        """
        self.record_method('Automesh', flag)

    def set_material_refinement_tet(self, flag: bool = True) -> None:
        """
        VBA Call
        --------
        Mesh.MaterialRefinementTet(flag)
        """
        self.record_method('MaterialRefinementTet', flag)

    def set_equilibrate_mesh(self, flag: bool = True) -> None:
        """
        VBA Call
        --------
        Mesh.EquilibrateMesh(flag)
        """
        self.record_method('EquilibrateMesh', flag)

    def set_equilibrate_mesh_ratio(self, value: float) -> None:
        """
        VBA Call
        --------
        Mesh.EquilibrateMeshRatio(value)
        """
        self.record_method('EquilibrateMeshRatio', value)

    def set_use_cell_aspect_ratio(self, flag: bool = True) -> None:
        """
        VBA Call
        --------
        Mesh.UseCellAspectRatio(flag)
        """
        self.record_method('UseCellAspectRatio', flag)

    def set_cell_aspect_ratio(self, value: float) -> None:
        """
        VBA Call
        --------
        Mesh.CellAspectRatio(value)
        """
        self.record_method('CellAspectRatio', value)

    def set_use_pec_edge_model(self, flag: bool = True) -> None:
        """
        VBA Call
        --------
        Mesh.UsePecEdgeModel(flag)
        """
        self.record_method('UsePecEdgeModel', flag)

    def set_point_acc_enhancement(self, value: float) -> None:
        """
        VBA Call
        --------
        Mesh.PointAccEnhancement(value)
        """
        self.record_method('PointAccEnhancement', value)

    def set_fast_pba_accuracy(self, value: float) -> None:
        """
        VBA Call
        --------
        Mesh.FastPBAAccuracy(value)
        """
        self.record_method('FastPBAAccuracy', value)

    def set_fast_pba_gap_detection(self, flag: bool = True) -> None:
        """
        VBA Call
        --------
        Mesh.FastPBAGapDetection(flag)
        """
        self.record_method('FastPBAGapDetection', flag)

    def set_fast_pba_gap_tolerance(self, value: float) -> None:
        """
        VBA Call
        --------
        Mesh.FPBAGapTolerance(value)
        """
        self.record_method('FPBAGapTolerance', value)

    def set_area_fill_limit(self, value: float) -> None:
        """
        VBA Call
        --------
        Mesh.AreaFillLimit(value)
        """
        self.record_method('AreaFillLimit', value)

    def set_convert_geometry_data_after_meshing(self, flag: bool = True) -> None:
        """
        VBA Call
        --------
        Mesh.ConvertGeometryDataAfterMeshing(flag)
        """
        self.record_method('ConvertGeometryDataAfterMeshing', flag)

    def set_consider_space_for_lower_mesh_limit(self, flag: bool = True) -> None:
        """
        VBA Call
        --------
        Mesh.ConsiderSpaceForLowerMeshLimit(flag)
        """
        self.record_method('ConsiderSpaceForLowerMeshLimit', flag)

    def set_ratio_limit_governs_local_refinement(self, flag: bool = True) -> None:
        """
        VBA Call
        --------
        Mesh.RatioLimitGovernsLocalRefinement(flag)
        """
        self.record_method('RatioLimitGovernsLocalRefinement', flag)

    def update(self) -> None:
        """
        VBA Call
        --------
        Mesh.Update()
        """
        self.record_method('Update')

    def force_update(self) -> None:
        """
        VBA Call
        --------
        Mesh.ForceUpdate()
        """
        self.record_method('ForceUpdate')

    def calculate_matrices(self) -> None:
        """
        VBA Call
        --------
        Mesh.CalculateMatrices()
        """
        self.record_method('CalculateMatrices')

    def set_view_mesh_mode(self, flag: bool = True) -> None:
        """
        VBA Call
        --------
        Mesh.ViewMeshMode(flag)
        """
        self.record_method('ViewMeshMode', flag)

    def set_small_feature_size(self, value: float) -> None:
        """
        VBA Call
        --------
        Mesh.SmallFeatureSize(value)
        """
        self.record_method('SmallFeatureSize', value)

    def set_parallel_mesher_mode(self, mesher_type: Union[ParallelMesherType, str], mesher_mode: Union[ParallelMesherMode, str]) -> None:
        """
        VBA Call
        --------
        Mesh.SetParallelMesherMode(mesher_type, mesher_mode)
        """
        self.record_method('SetParallelMesherMode', str(getattr(mesher_type, 'value', mesher_type)), str(getattr(mesher_mode, 'value', mesher_mode)))

    def set_max_number_of_parallel_mesher_threads(self, mesher_type: Union[ParallelMesherType, str], number: int) -> None:
        """
        VBA Call
        --------
        Mesh.SetMaxParallelMesherThreads(mesher_type, number)
        """
        self.record_method('SetMaxParallelMesherThreads', str(getattr(mesher_type, 'value', mesher_type)), number)

    def set_automesh_straight_lines(self, flag: bool = True) -> None:
        """
        VBA Call
        --------
        Mesh.AutomeshStraightLines(flag)
        """
        self.record_method('AutomeshStraightLines', flag)

    def set_automesh_elliptical_lines(self, flag: bool = True) -> None:
        """
        VBA Call
        --------
        Mesh.AutomeshEllipticalLines(flag)
        """
        self.record_method('AutomeshEllipticalLines', flag)

    def set_automesh_at_wire_end_points(self, flag: bool = True) -> None:
        """
        VBA Call
        --------
        Mesh.AutomeshAtWireEndPoints(flag)
        """
        self.record_method('AutomeshAtWireEndPoints', flag)

    def set_automesh_at_probe_points(self, flag: bool = True) -> None:
        """
        VBA Call
        --------
        Mesh.AutomeshAtProbePoints(flag)
        """
        self.record_method('AutomeshAtProbePoints', flag)

    def set_automesh_limit_shape_faces(self, flag: bool = True) -> None:
        """
        VBA Call
        --------
        Mesh.AutoMeshLimitShapeFaces(flag)
        """
        self.record_method('AutoMeshLimitShapeFaces', flag)

    def set_automesh_number_of_shape_faces(self, number: int) -> None:
        """
        VBA Call
        --------
        Mesh.AutoMeshNumberOfShapeFaces(number)
        """
        self.record_method('AutoMeshNumberOfShapeFaces', number)

    def set_merge_thin_pec_layer_fixpoints(self, flag: bool = True) -> None:
        """
        VBA Call
        --------
        Mesh.MergeThinPECLayerFixpoints(flag)
        """
        self.record_method('MergeThinPECLayerFixpoints', flag)

    def set_automesh_fixpoints_for_background(self, flag: bool = True) -> None:
        """
        VBA Call
        --------
        Mesh.AutomeshFixpointsForBackground(flag)
        """
        self.record_method('AutomeshFixpointsForBackground', flag)

    def enable_automesh_refine_at_pec_lines(self, factor: int) -> None:
        """
        VBA Call
        --------
        Mesh.AutomeshRefineAtPecLines(True, factor)
        """
        self.record_method('AutomeshRefineAtPecLines', True, factor)

    def disable_automesh_refine_at_pec_lines(self) -> None:
        """
        VBA Call
        --------
        Mesh.AutomeshRefineAtPecLines(False, 0)
        """
        self.record_method('AutomeshRefineAtPecLines', False, 0)

    def set_automesh_refine_pec_along_axes_only(self, flag: bool = True) -> None:
        """
        VBA Call
        --------
        Mesh.AutomeshRefinePecAlongAxesOnly(flag)
        """
        self.record_method('AutomeshRefinePecAlongAxesOnly', flag)

    def set_automesh_refine_dielectrics_type(self, dielectrics_type: Union[AutomeshRefineDielectrics, str]) -> None:
        """
        VBA Call
        --------
        Mesh.SetAutomeshRefineDielectricsType(dielectrics_type)
        """
        self.record_method('SetAutomeshRefineDielectricsType', str(getattr(dielectrics_type, 'value', dielectrics_type)))

    def set_surface_mesh_geometry_accuracy(self, value: float) -> None:
        """
        VBA Call
        --------
        Mesh.SurfaceMeshGeometryAccuracy(value)
        """
        self.record_method('SurfaceMeshGeometryAccuracy', value)

    def set_surface_mesh_method(self, method: Union[SurfaceMeshMethod, str]) -> None:
        """
        VBA Call
        --------
        Mesh.SurfaceMeshMethod(method)
        """
        self.record_method('SurfaceMeshMethod', str(getattr(method, 'value', method)))

    def set_surface_tolerance(self, value: float) -> None:
        """
        VBA Call
        --------
        Mesh.SurfaceTolerance(value)
        """
        self.record_method('SurfaceTolerance', value)

    def set_surface_tolerance_type(self, surface_tolerance_type: Union[SurfaceToleranceType, str]) -> None:
        """
        VBA Call
        --------
        Mesh.SurfaceToleranceType(surface_tolerance_type)
        """
        self.record_method('SurfaceToleranceType', str(getattr(surface_tolerance_type, 'value', surface_tolerance_type)))

    def set_normal_tolerance(self, value: float) -> None:
        """
        VBA Call
        --------
        Mesh.NormalTolerance(value)
        """
        self.record_method('NormalTolerance', value)

    def set_anisotropic_curvature_refinement_fsm(self, flag: bool = True) -> None:
        """
        VBA Call
        --------
        Mesh.AnisotropicCurvatureRefinementFSM(flag)
        """
        self.record_method('AnisotropicCurvatureRefinementFSM', flag)

    def set_surface_mesh_enrichment(self, level: int) -> None:
        """
        VBA Call
        --------
        Mesh.SurfaceMeshEnrichment(level)
        """
        self.record_method('SurfaceMeshEnrichment', level)

    def set_surface_optimization(self, flag: bool = True) -> None:
        """
        VBA Call
        --------
        Mesh.SurfaceOptimization(flag)
        """
        self.record_method('SurfaceOptimization', flag)

    def set_surface_smoothing(self, flag: bool = True) -> None:
        """
        VBA Call
        --------
        Mesh.SurfaceSmoothing(flag)
        """
        self.record_method('SurfaceSmoothing', flag)

    def set_curvature_refinement_factor(self, value: float) -> None:
        """
        VBA Call
        --------
        Mesh.CurvatureRefinementFactor(value)
        """
        self.record_method('CurvatureRefinementFactor', value)

    def set_min_curvature_refinement(self, value: float) -> None:
        """
        VBA Call
        --------
        Mesh.MinimumCurvatureRefinement(value)
        """
        self.record_method('MinimumCurvatureRefinement', value)

    def set_anisotropic_curvature_refinement(self, flag: bool = True) -> None:
        """
        VBA Call
        --------
        Mesh.AnisotropicCurvatureRefinement(flag)
        """
        self.record_method('AnisotropicCurvatureRefinement', flag)

    def set_volume_optimization(self, flag: bool = True) -> None:
        """
        VBA Call
        --------
        Mesh.VolumeOptimization(flag)
        """
        self.record_method('VolumeOptimization', flag)

    def set_volume_smoothing(self, flag: bool = True) -> None:
        """
        VBA Call
        --------
        Mesh.VolumeSmoothing(flag)
        """
        self.record_method('VolumeSmoothing', flag)

    def set_density_transitions(self, value: float) -> None:
        """
        VBA Call
        --------
        Mesh.DensityTransitions(value)
        """
        self.record_method('DensityTransitions', value)

    def set_volume_mesh_method(self, method: Union[VolumeMeshMethod, str]) -> None:
        """
        VBA Call
        --------
        Mesh.VolumeMeshMethod(method)
        """
        self.record_method('VolumeMeshMethod', str(getattr(method, 'value', method)))

    def set_delaunay_optimization_level(self, value: int) -> None:
        """
        VBA Call
        --------
        Mesh.DelaunayOptimizationLevel(value)
        """
        self.record_method('DelaunayOptimizationLevel', value)

    def set_delaunay_propagation_factor(self, value: float) -> None:
        """
        VBA Call
        --------
        Mesh.DelaunayPropagationFactor(value)
        """
        self.record_method('DelaunayPropagationFactor', value)

    def snap_to_surface_mesh(self, file_path_in: str, file_path_out: str) -> None:
        """
        VBA Call
        --------
        Mesh.SnapToSurfaceMesh(file_path_in, file_path_out)
        """
        self.record_method('SnapToSurfaceMesh', file_path_in, file_path_out)

    def set_self_intersecting_check(self, flag: bool = True) -> None:
        """
        VBA Call
        --------
        Mesh.SelfIntersectingCheck(flag)
        """
        self.record_method('SelfIntersectingCheck', flag)

    def find_fixpoint_from_position(self, coords: Tuple[float, float, float]) -> int:
        """
        VBA Call
        --------
        Mesh.FindFixpointFromPosition(coords[0], coords[1], coords[2])
        """
        return self.query_method_int('FindFixpointFromPosition', coords[0], coords[1], coords[2])

    def add_fixpoint(self, coords: Tuple[float, float, float]) -> None:
        """
        VBA Call
        --------
        Mesh.AddFixpoint(coords[0], coords[1], coords[2])
        """
        self.record_method('AddFixpoint', coords[0], coords[1], coords[2])

    def add_fixpoint_relative(self, ref_fixpoint_id: int, coords: Tuple[float, float, float]) -> None:
        """
        VBA Call
        --------
        Mesh.RelativeAddFixpoint(ref_fixpoint_id, coords[0], coords[1], coords[2])
        """
        self.record_method('RelativeAddFixpoint', ref_fixpoint_id, coords[0], coords[1], coords[2])

    def delete_fixpoint(self, fixpoint_id: int) -> None:
        """
        VBA Call
        --------
        Mesh.DeleteFixpoint(fixpoint_id)
        """
        self.record_method('DeleteFixpoint', fixpoint_id)

    def add_intermediate_fixpoint(self, id1: int, id2: int, number_of_points: int) -> None:
        """
        VBA Call
        --------
        Mesh.AddIntermediateFixpoint(id1, id2, number_of_points)
        """
        self.record_method('AddIntermediateFixpoint', id1, id2, number_of_points)

    def add_automesh_fixpoint(self, use_xyz: Tuple[bool, bool, bool], coords: Tuple[float, float, float]) -> None:
        """
        VBA Call
        --------
        Mesh.AddAutomeshFixpoint(use_xyz[0], use_xyz[1], use_xyz[2], coords[0], coords[1], coords[2])
        """
        self.record_method('AddAutomeshFixpoint', use_xyz[0], use_xyz[1], use_xyz[2], coords[0], coords[1], coords[2])

    def delete_automesh_fixpoint(self, coords: Tuple[float, float, float]) -> None:
        """
        VBA Call
        --------
        Mesh.DeleteAutomeshFixpoint(coords[0], coords[1], coords[2])
        """
        self.record_method('DeleteAutomeshFixpoint', coords[0], coords[1], coords[2])

    def modify_automesh_fixpoint_from_id(self, use_xyz: Tuple[bool, bool, bool], fixpoint_id: int) -> None:
        """
        VBA Call
        --------
        Mesh.ModifyAutomeshFixpointFromId(use_xyz[0], use_xyz[1], use_xyz[2], fixpoint_id)
        """
        self.record_method('ModifyAutomeshFixpointFromId', use_xyz[0], use_xyz[1], use_xyz[2], fixpoint_id)

    def add_automesh_fixpoint_from_id(self, use_xyz: Tuple[bool, bool, bool], pick_type: Union[PickType, str], solid_name: str, pick_id: int, face_id: int, number: int) -> None:
        """
        VBA Call
        --------
        Mesh.AddAutomeshFixpointFromId(use_xyz[0], use_xyz[1], use_xyz[2], pick_type, solid_name, pick_id, face_id, number)
        """
        self.record_method('AddAutomeshFixpointFromId', use_xyz[0], use_xyz[1], use_xyz[2], str(getattr(pick_type, 'value', pick_type)), solid_name, pick_id, face_id, number)

    def delete_automesh_fixpoint_from_id(self, fixpoint_id: int) -> None:
        """
        VBA Call
        --------
        Mesh.DeleteAutomeshFixpointFromId(fixpoint_id)
        """
        self.record_method('DeleteAutomeshFixpointFromId', fixpoint_id)

    def clear_spatial_variation(self) -> None:
        """
        VBA Call
        --------
        Mesh.ClearSpatialVariation()
        """
        self.record_method('ClearSpatialVariation')

    def clear_spatial_variation_for_shape(self, solid_name: str) -> None:
        """
        VBA Call
        --------
        Mesh.ClearSpatialVariationForShape(solid_name)
        """
        self.record_method('ClearSpatialVariationForShape', solid_name)

    def set_spatial_variation_type_for_shape(self, solid_name: str, var_type: Union[SpatialVariation, str]) -> None:
        """
        VBA Call
        --------
        Mesh.SetSpatialVariationTypeForShape(solid_name, var_type)
        """
        self.record_method('SetSpatialVariationTypeForShape', solid_name, str(getattr(var_type, 'value', var_type)))

    def get_mesh_type(self) -> str:
        """
        VBA Call
        --------
        Mesh.GetMeshType()
        """
        return self.query_method_str('GetMeshType')

    def is_fpba_used(self) -> bool:
        """
        VBA Call
        --------
        Mesh.IsFPBAUsed()
        """
        return self.query_method_bool('IsFPBAUsed')

    def is_fpba_gap_detection_active(self) -> bool:
        """
        VBA Call
        --------
        Mesh.IsFastPBAGapDetection()
        """
        return self.query_method_bool('IsFastPBAGapDetection')

    def get_fpba_gap_tolerance(self) -> float:
        """
        VBA Call
        --------
        Mesh.GetFPBAGapTolerance()
        """
        return self.query_method_float('GetFPBAGapTolerance')

    def get_area_fill_limit(self) -> float:
        """
        VBA Call
        --------
        Mesh.GetAreaFillLimit()
        """
        return self.query_method_float('GetAreaFillLimit')

    def get_min_edge_length(self) -> float:
        """
        VBA Call
        --------
        Mesh.GetMinimumEdgeLength()
        """
        return self.query_method_float('GetMinimumEdgeLength')

    def get_max_edge_length(self) -> float:
        """
        VBA Call
        --------
        Mesh.GetMaximumEdgeLength()
        """
        return self.query_method_float('GetMaximumEdgeLength')

    def get_surface_mesh_area(self) -> float:
        """
        VBA Call
        --------
        Mesh.GetSurfaceMeshArea()
        """
        return self.query_method_float('GetSurfaceMeshArea')

    def get_number_of_mesh_cells(self) -> int:
        """
        VBA Call
        --------
        Mesh.GetNumberOfMeshCells()
        """
        return self.query_method_int('GetNumberOfMeshCells')

    def get_number_of_mesh_cells_metrics(self) -> int:
        """
        VBA Call
        --------
        Mesh.GetNumberOfMeshCellsMetrics()
        """
        return self.query_method_int('GetNumberOfMeshCellsMetrics')

    def get_parallel_mesher_mode(self) -> str:
        """
        VBA Call
        --------
        Mesh.GetParallelMesherMode()
        """
        return self.query_method_str('GetParallelMesherMode')

    def get_max_parallel_mesher_threads(self) -> int:
        """
        VBA Call
        --------
        Mesh.GetMaxParallelMesherThreads()
        """
        return self.query_method_int('GetMaxParallelMesherThreads')

