from eggtools.attributes.EggAttribute import EggAttribute


# More information, check here:
# https://docs.panda3d.org/1.10/python/programming/rendering-process/controlling-render-order

class EggBinAttribute(EggAttribute):
    """
    Built-in Cull Bins:
    ------------------------------------------
    | Bin Name     | Sort | Type             |
    |----------------------------------------|
    | background   | 10   | BT_fixed         |
    | opaque       | 20   | BT_state_sorted  |
    | transparent  | 30   | BT_back_to_front |
    | fixed        | 40   | BT_fixed         |
    | opaque       | 50   | BT_unsorted      |
    ------------------------------------------
    """

    def __init__(self, bin_name):
        """
        <Scalar> bin { bin_name }
        """
        # if bin_name is None, that means we clear the bin
        super().__init__(entry_type = "Scalar", name = "bin", contents = bin_name)

    def _modify_polygon(self, egg_polygon, tref):
        pass

    def _modify_node(self, egg_node):
        if self.target_nodes.check(egg_node.getName()):
            # We can assume if they have a getter then they should have a setter, and a clear-er...
            if not hasattr(egg_node, "getBin"):
                return
            if not self.contents:
                egg_node.clearBin()
                return
            bin_name = egg_node.getBin()
            if not bin_name:
                egg_node.setBin(self.contents)


class EggBin(EggBinAttribute):
    def __init__(self, bin_name):
        super().__init__(bin_name)
