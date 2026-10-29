from eggtools.attributes.EggAttribute import EggAttribute


class EggDrawOrderAttribute(EggAttribute):
    """
    <Scalar> draw-order { draw_order }
    """

    def __init__(self, draw_order):
        self.draw_order = draw_order
        self.clear_draw_order = False
        if self.draw_order == "clear":
            self.clear_draw_order = True

        super().__init__(entry_type = "Scalar", name = "draw-order", contents = self.draw_order)

    def _modify_polygon(self, egg_polygon, tref=None):
        pass

    def _modify_node(self, egg_node):
        if not hasattr(egg_node, "clearDrawOrder") or hasattr(egg_node, "setDrawOrder"):
            return
        if self.target_nodes.check(egg_node.getName()):
            if self.clear_draw_order:
                egg_node.clearDrawOrder()
                return
            if not egg_node.hasDcsType():
                egg_node.setDrawOrder(int(self.draw_order))


class EggDrawOrder(EggDrawOrderAttribute):
    def __init__(self, draw_order):
        super().__init__(draw_order)
