"""
This attribute has little documentation in the Panda3D manual, so its effectiveness is unknown.

Possible related articles:
https://docs.panda3d.org/1.10/python/reference/panda3d.core.PolylightNode
https://docs.panda3d.org/1.10/python/reference/panda3d.core.PolylightEffect
"""

from eggtools.attributes.EggAttribute import EggAttribute


class EggPolylightAttribute(EggAttribute):
    def __init__(self, flag: bool = True):
        """
        <Scalar> polylight { 1 }
        """
        self.flag = bool(flag)
        super().__init__("Scalar", "polylight", self.flag)

    def _modify_polygon(self, egg_polygon, tref):
        pass

    def _modify_node(self, egg_node):
        if self.target_nodes.check(egg_node.getName()) and hasattr(egg_node, "set_polylight_flag"):
            egg_node.set_polylight_flag(self.flag)


class EggPolylight(EggPolylightAttribute):
    def __init__(self, flag: bool = True):
        super().__init__(flag)
