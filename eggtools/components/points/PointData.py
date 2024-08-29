from dataclasses import dataclass
from typing import Optional

from panda3d.core import Filename
from panda3d.egg import EggTexture
from . import PointUtils
from .PointUtils import PointEnum


@dataclass
class PointData:
    """
    Used with EggPolygon instances to keep a reference of the origin egg file, the corresponding TRef used
    on the polygon, and the collection of EggVertices that make up the polygon.

    Note: Not intended to be used for polygons that have more than one TRef entry, such as used in multitexturing.
    """

    def __str__(self):
        return f"PointData: {len(self.egg_vertex_uvs.keys())} vertexes registered"

    def __hash__(self):
        return hash(id(self))

    egg_filename: Filename

    # The *actual* point data:
    egg_vertex_uvs: dict  # { EggVertex: [u, v] }

    egg_texture: EggTexture

    # Conventional shortcut method
    def get_bounding_volume(self):
        return self.get_bbox()

    def get_bbox(self):
        """
        Reports the bounding box of the egg_vertex_uvs entries.

        :returns: ( [xMin, yMin], [xMax, yMax] )
        """
        allX = []
        allY = []
        for coords in self.egg_vertex_uvs.values():
            u, v = coords
            allX.append(u)
            allY.append(v)
        return PointUtils.bounding_box([allX, allY])

    def get_all_vertices(self):
        verts = list(self.egg_vertex_uvs.keys())
        Vx = []
        Vy = []
        Vz = []
        # according to CNC machines, they call the 4th dimension the A-axis
        Va = []
        for egg_vertex in verts:
            x, y, z, a = egg_vertex.getPos4()
            Vx.append(x)
            Vy.append(y)
            Vz.append(z)
            Va.append(a)
        return Vx, Vy, Vz, Va

    def get_coords(self, sort_by: PointEnum = None):
        # note: yes it is possible ican do this better with numpy
        # but numpy is only used for matplotlib rn
        coords = list(self.egg_vertex_uvs.values())
        if sort_by == PointEnum.U:
            coords.sort(key = PointUtils.sort_points_u)
        elif sort_by == PointEnum.V:
            coords.sort(key = PointUtils.sort_points_v)
        return coords

    """
    Debug Methods
    """

    def print_uvs(self, multiplier=1):
        for u, v in self.egg_vertex_uvs.values():
            print(f"u: {u * multiplier} v: {v * multiplier}")


class PointHelper:
    @staticmethod
    def unify_point_datas(point_datas) -> Optional[PointData]:
        """
        Takes the vertex_uv properties of all the provided PointDatas and aggregates them into one
        """
        point_vertexes = dict()
        if not point_datas:
            return None

        for pd in point_datas:
            # for python 3.8 compatibility
            # https://peps.python.org/pep-0584/
            # unsupported operand type(s) for |: 'dict' and 'dict'
            # point_vertexes = point_vertexes | pd.egg_vertex_uvs
            point_vertexes = {**point_vertexes, **pd.egg_vertex_uvs}
        point_filename = point_datas[0].egg_filename
        point_texture = point_datas[0].egg_texture
        return PointData(point_filename, point_vertexes, point_texture)
