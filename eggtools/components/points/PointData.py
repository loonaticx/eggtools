from dataclasses import dataclass
from panda3d.core import Filename
from panda3d.egg import EggTexture
from . import PointUtils


@dataclass
class PointData:
    """
    Used with EggPolygon instances to keep a reference of the origin egg file, the corresponding TRef used
    on the polygon, and the collection of EggVertices that make up the polygon.

    Note: Not intended to be used for polygons that have more than one TRef entry, such as used in multitexturing.
    """

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

    """
    Debug Methods
    """

    def print_uvs(self, multiplier=1):
        for u, v in self.egg_vertex_uvs.values():
            print(f"u: {u * multiplier} v: {v * multiplier}")


class PointHelper:
    @staticmethod
    def unify_point_datas(point_datas) -> PointData:
        """
        Takes the vertex_uv properties of all the provided PointDatas and aggregates them into one
        """
        point_vertexes = dict()
        for pd in point_datas:
            point_vertexes = point_vertexes | pd.egg_vertex_uvs
        point_filename = point_datas[0].egg_filename
        point_texture = point_datas[0].egg_texture
        return PointData(point_filename, point_vertexes, point_texture)
