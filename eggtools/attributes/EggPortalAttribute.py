"""
This attribute has little documentation in the Panda3D manual, so its effectiveness is unknown.

More Information:
https://docs.panda3d.org/1.10/python/programming/render-attributes/occlusion-culling/portal-culling
https://docs.panda3d.org/1.10/python/reference/panda3d.core.PortalNode
"""

from eggtools.attributes.EggAttribute import EggAttribute


class EggPortalAttribute(EggAttribute):
    def __init__(self, flag: bool = True):
        """
        A portal is a window in 3D space that allows objects in one cell (the “out” cell)
        to be seen from another cell (the “in” cell).

        <Scalar> portal { 1 }
        """
        self.flag = bool(flag)
        super().__init__("Scalar", "portal", self.flag)

    def _modify_polygon(self, egg_polygon, tref):
        pass

    def _modify_node(self, egg_node):
        if self.target_nodes.check(egg_node.getName()) and hasattr(egg_node, "set_portal_flag"):
            egg_node.set_portal_flag(self.flag)


class EggPortal(EggPortalAttribute):
    def __init__(self, flag: bool = True):
        super().__init__(flag)
