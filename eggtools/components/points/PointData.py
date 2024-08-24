from dataclasses import dataclass
from panda3d.core import Filename
from panda3d.egg import EggTexture
from . import PointUtils


@dataclass
class PointData:
    """
    Generated from EggPolygon instances.
    """
    """
    [
        [NodeID, NodeTex]
        NodeID --> [ EggVertex: { u, v } ]
        NodeTex --> EggTexture
    ]
    """

    def __hash__(self):
        return hash(id(self))

    egg_filename: Filename
    egg_vertex_uvs: dict  # aka "point_data"
    egg_texture: EggTexture

    def get_bounding_volume(self):
        return self.get_bbox()

    def get_bbox(self):
        """
        xMin, xMax = bbox[0]
        yMin, yMax = bbox[1]
        """
        allX = []
        allY = []
        for coords in self.egg_vertex_uvs.values():
            u, v = coords
            allX.append(u)
            allY.append(v)
        return PointUtils.bounding_box([allX, allY])
