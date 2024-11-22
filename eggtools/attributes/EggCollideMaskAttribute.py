from eggtools.attributes.EggAttribute import EggAttribute
from eggtools.components.EggExceptions import EggAttributeInvalid

name2type = {
    'both': ['collide-mask', [True, True]],
    'from': ['from-collide-mask', [True, False]],
    'into': ['into-collide-mask', [False, True]],
    'to': ['into-collide-mask', [False, True]],

}


def get_collide_mask(collide_mask_name: str):
    return name2type.get(collide_mask_name.lower(), [None, None])


class EggCollideMaskAttribute(EggAttribute):
    def __init__(self, value, side='both'):
        # side = from, into, both
        self.value = value
        self.side = side
        name = get_collide_mask(side)[0]
        if name is None:
            raise EggAttributeInvalid(self, side)
        super().__init__(entry_type = "Scalar", name = name, contents = self.value)

    @staticmethod
    def get_collide_masks():
        return name2type

    def _modify_polygon(self, egg_polygon, tref=None):
        pass

    def _modify_node(self, egg_node):
        if self.target_nodes.check(egg_node.getName()) and hasattr(egg_node, "setFromCollideMask"):
            collide_from, collide_to = name2type[self.side][1]
            # Make it a bit prettier
            if all([collide_from, collide_to]):
                egg_node.setCollideMask(self.value)
                return
            if collide_from:
                egg_node.setFromCollideMask(self.value)
            if collide_to:
                egg_node.setIntoCollideMask(self.value)


class EggCollideMask(EggCollideMaskAttribute):
    def __init__(self, value, side='both'):
        super().__init__(value, side)
