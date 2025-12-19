'''This file is auto-generated. Do not edit.'''
from .. import IVBAProvider, VBAObjWrapper
from enum import Enum
from typing import Union, Tuple

class Pick(VBAObjWrapper):
    class PickType(Enum):
        END_POINT = 'EndPoint'

    def __init__(self, vbap: IVBAProvider) -> None:
        super().__init__(vbap, 'Pick')
        self.set_save_history(False)

    def add_edge(self, uvw1: Tuple[int, int, int], uvw2: Tuple[int, int, int]) -> None:
        """
        VBA Call
        --------
        Pick.AddEdge(uvw1[0], uvw1[1], uvw1[2], uvw2[0], uvw2[1], uvw2[2])
        """
        self.record_method('AddEdge', uvw1[0], uvw1[1], uvw1[2], uvw2[0], uvw2[1], uvw2[2])

    def delete_edge(self, index: int) -> None:
        """
        VBA Call
        --------
        Pick.DeleteEdge(index)
        """
        self.record_method('DeleteEdge', index)

    def add_mean_edge(self, indices: list[int]) -> None:
        """
        VBA Call
        --------
        Pick.MeanEdge(','.join(str(i) for i in indices))
        """
        self.record_method('MeanEdge', ','.join(str(i) for i in indices))

    def move_edge(self, index: int, delta: Tuple[float, float, float], keep_original: bool = False) -> None:
        """
        VBA Call
        --------
        Pick.MoveEdge(index, delta[0], delta[1], delta[2], keep_original)
        """
        self.record_method('MoveEdge', index, delta[0], delta[1], delta[2], keep_original)

    def move_edge_in_plane(self, index: int, offset: float, keep_original: bool = False) -> None:
        """
        VBA Call
        --------
        Pick.MoveEdgeInPlane(index, offset, keep_original)
        """
        self.record_method('MoveEdgeInPlane', index, offset, keep_original)

    def pick_edge_from_picked_points(self, index1: int, index2: int) -> None:
        """
        VBA Call
        --------
        Pick.PickEdgeFromPickedPoints(index1, index2)
        """
        self.record_method('PickEdgeFromPickedPoints', index1, index2)

    def clear_all_picks(self) -> None:
        """
        VBA Call
        --------
        Pick.ClearAllPicks()
        """
        self.record_method('ClearAllPicks')

    def write_next_pick_to_database(self, id: int) -> None:
        """
        VBA Call
        --------
        Pick.NextPickToDataBase(id)
        """
        self.record_method('NextPickToDataBase', id)

    def snap_last_point_to_drawplane(self) -> None:
        """
        VBA Call
        --------
        Pick.SnapLastPointToDrawplane()
        """
        self.record_method('SnapLastPointToDrawplane')

    def pick_point_from_id_on(self, name: str, pick_type: Union[PickType, str], id: int) -> None:
        """
        VBA Call
        --------
        Pick.PickPointFromIdOn(name, pick_type, id)
        """
        self.record_method('PickPointFromIdOn', name, str(getattr(pick_type, 'value', pick_type)), id)

    def pick_point_from_point_on(self, name: str, pick_type: Union[PickType, str], coords: Tuple[float, float, float]) -> None:
        """
        VBA Call
        --------
        Pick.PickPointFromPointOn(name, pick_type, coords[0], coords[1], coords[2])
        """
        self.record_method('PickPointFromPointOn', name, str(getattr(pick_type, 'value', pick_type)), coords[0], coords[1], coords[2])

    def pick_edge_from_id_on(self, name: str, edge_id: int, vertex_id: int) -> None:
        """
        VBA Call
        --------
        Pick.PickEdgeFromIdOn(name, edge_id, vertex_id)
        """
        self.record_method('PickEdgeFromIdOn', name, edge_id, vertex_id)

    def pick_edge_from_point_on(self, name: str, coords: Tuple[float, float, float]) -> None:
        """
        VBA Call
        --------
        Pick.PickEdgeFromPointOn(name, coords[0], coords[1], coords[2])
        """
        self.record_method('PickEdgeFromPointOn', name, coords[0], coords[1], coords[2])

    def pick_face_from_id_on(self, name: str, face_id: int) -> None:
        """
        VBA Call
        --------
        Pick.PickFaceFromIdOn(name, face_id)
        """
        self.record_method('PickFaceFromIdOn', name, face_id)

    def pick_face_from_point_on(self, name: str, coords: Tuple[float, float, float]) -> None:
        """
        VBA Call
        --------
        Pick.PickFaceFromPointOn(name, coords[0], coords[1], coords[2])
        """
        self.record_method('PickFaceFromPointOn', name, coords[0], coords[1], coords[2])

    def pick_dangling_edge_chain_from_id(self, shape_name: str, id: int) -> None:
        """
        VBA Call
        --------
        Pick.PickDanglingEdgeChainFromId(shape_name, id)
        """
        self.record_method('PickDanglingEdgeChainFromId', shape_name, id)

    def pick_edge_from_id(self, shape_name: str, edge_id: int, vertex_id: int) -> None:
        """
        VBA Call
        --------
        Pick.PickEdgeFromId(shape_name, edge_id, vertex_id)
        """
        self.record_method('PickEdgeFromId', shape_name, edge_id, vertex_id)

    def pick_edge_from_point(self, shape_name: str, coords: Tuple[float, float, float]) -> None:
        """
        VBA Call
        --------
        Pick.PickEdgeFromPoint(shape_name, coords[0], coords[1], coords[2])
        """
        self.record_method('PickEdgeFromPoint', shape_name, coords[0], coords[1], coords[2])

    def pick_solid_edge_chain_from_id(self, shape_name: str, edge_id: int, face_id: int) -> None:
        """
        VBA Call
        --------
        Pick.PickSolidEdgeChainFromId(shape_name, edge_id, face_id)
        """
        self.record_method('PickSolidEdgeChainFromId', shape_name, edge_id, face_id)

    def pick_face_chain_from_id(self, shape_name: str, face_id: int) -> None:
        """
        VBA Call
        --------
        Pick.PickFaceChainFromId(shape_name, face_id)
        """
        self.record_method('PickFaceChainFromId', shape_name, face_id)

    def pick_face_from_id(self, shape_name: str, id: int) -> None:
        """
        VBA Call
        --------
        Pick.PickFaceFromId(shape_name, id)
        """
        self.record_method('PickFaceFromId', shape_name, id)

    def pick_face_from_point(self, shape_name: str, coords: Tuple[float, float, float]) -> None:
        """
        VBA Call
        --------
        Pick.PickFaceFromPoint(shape_name, coords[0], coords[1], coords[2])
        """
        self.record_method('PickFaceFromPoint', shape_name, coords[0], coords[1], coords[2])

    def change_face_id(self, shape_name: str, change_statement: str, version_number: str) -> None:
        """
        VBA Call
        --------
        Pick.ChangeFaceId(shape_name, change_statement, version_number)
        """
        self.record_method('ChangeFaceId', shape_name, change_statement, version_number)

    def change_edge_id(self, shape_name: str, change_statement: str, version_number: str) -> None:
        """
        VBA Call
        --------
        Pick.ChangeEdgeId(shape_name, change_statement, version_number)
        """
        self.record_method('ChangeEdgeId', shape_name, change_statement, version_number)

    def change_vertex_id(self, shape_name: str, change_statement: str, version_number: str) -> None:
        """
        VBA Call
        --------
        Pick.ChangeVertexId(shape_name, change_statement, version_number)
        """
        self.record_method('ChangeVertexId', shape_name, change_statement, version_number)

    def delete_face(self, index: int) -> None:
        """
        VBA Call
        --------
        Pick.DeleteFace(index)
        """
        self.record_method('DeleteFace', index)

    def delete_point(self, index: int) -> None:
        """
        VBA Call
        --------
        Pick.DeletePoint(index)
        """
        self.record_method('DeletePoint', index)

    def add_mean_point(self, indices: str) -> None:
        """
        VBA Call
        --------
        Pick.MeanPoint(indices)
        """
        self.record_method('MeanPoint', indices)

    def add_mean_from_last_two_points(self) -> None:
        """
        VBA Call
        --------
        Pick.MeanLastTwoPoints()
        """
        self.record_method('MeanLastTwoPoints')

    def move_point(self, index: int, delta: Tuple[float, float, float], keep_original: bool = False) -> None:
        """
        VBA Call
        --------
        Pick.MovePoint(index, delta[0], delta[1], delta[2], keep_original)
        """
        self.record_method('MovePoint', index, delta[0], delta[1], delta[2], keep_original)

    def pick_point_from_coordinates(self, coords: Tuple[float, float, float]) -> None:
        """
        VBA Call
        --------
        Pick.PickPointFromCoordinates(coords[0], coords[1], coords[2])
        """
        self.record_method('PickPointFromCoordinates', coords[0], coords[1], coords[2])

    def get_edge_id_from_point(self, shape_name: str, coords: Tuple[float, float, float]) -> int:
        """
        VBA Call
        --------
        Pick.GetEdgeIdFromPoint(shape_name, coords[0], coords[1], coords[2])
        """
        return self.query_method_int('GetEdgeIdFromPoint', shape_name, coords[0], coords[1], coords[2])

    def get_face_id_from_point(self, shape_name: str, coords: Tuple[float, float, float]) -> int:
        """
        VBA Call
        --------
        Pick.GetFaceIdFromPoint(shape_name, coords[0], coords[1], coords[2])
        """
        return self.query_method_int('GetFaceIdFromPoint', shape_name, coords[0], coords[1], coords[2])

    def get_number_of_picked_points(self) -> int:
        """
        VBA Call
        --------
        Pick.GetNumberOfPickedPoints()
        """
        return self.query_method_int('GetNumberOfPickedPoints')

    def get_number_of_picked_edges(self) -> int:
        """
        VBA Call
        --------
        Pick.GetNumberOfPickedEdges()
        """
        return self.query_method_int('GetNumberOfPickedEdges')

    def get_number_of_picked_faces(self) -> int:
        """
        VBA Call
        --------
        Pick.GetNumberOfPickedFaces()
        """
        return self.query_method_int('GetNumberOfPickedFaces')

