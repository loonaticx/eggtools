"""
Indexed geometry is a way to reduce the amount of data that needs to be stored in a model.
In a non-indexed model, each vertex is stored as a unique point in space.
In an indexed model, each vertex is stored only once, and then referenced by a list of indices.
This can save a lot of memory, especially for models with many polygons.

This attribute has little documentation in the Panda3D manual, so its effectiveness is unknown.

Read more: https://observablehq.com/@cse4413msstate/basic-modelling-indexed-geometry

"""

from eggtools.attributes.EggAttribute import EggAttribute


class EggIndexAttribute(EggAttribute):

    def __init__(self, flag: bool = True):
        """
        Geometry at this node and below will be generated as indexed geometry.
        """
        self.flag = bool(flag)
        super().__init__("Scalar", "indexed", self.flag)

    def _modify_polygon(self, egg_polygon, tref):
        pass

    def _modify_node(self, egg_node):
        if self.target_nodes.check(egg_node.getName()) and hasattr(egg_node, "set_indexed_flag"):
            egg_node.set_indexed_flag(self.flag)


class EggIndex(EggIndexAttribute):
    def __init__(self, flag: bool = True):
        super().__init__(flag)
