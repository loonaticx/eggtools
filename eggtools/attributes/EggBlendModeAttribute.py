from eggtools.attributes.EggAttribute import EggAttribute
from eggtools.components.EggEnums import BlendMode
from eggtools.components.EggExceptions import EggAttributeInvalid

name2id = {
    "unspecified": BlendMode.Unspecified,
    "none": BlendMode.NoType,
    "add": BlendMode.Add,
    "subtract": BlendMode.Subtract,
    "inv_subtract": BlendMode.InvSubtract,
    "inv-subtract": BlendMode.InvSubtract,
    "invsubtract": BlendMode.InvSubtract,
    "invsub": BlendMode.InvSubtract,
    "min": BlendMode.Min,
    "max": BlendMode.Max
}


def get_blend_mode(mode: str):
    return name2id.get(mode.lower(), None)


class EggBlendModeAttribute(EggAttribute):
    def __init__(self, mode: str):
        """
        <Scalar> blend { mode }
        """
        self.mode = get_blend_mode(mode)
        if self.mode is None:
            raise EggAttributeInvalid(self, mode)
        super().__init__("Scalar", "blend", self.mode)

    @staticmethod
    def get_blend_modes():
        return name2id

    def _modify_polygon(self, egg_polygon, tref):
        if self.target_nodes.check(tref.getName()):
            # Do something here for TRefs #
            pass

    def _modify_node(self, egg_node):
        if self.target_nodes.check(egg_node.getName()) and hasattr(egg_node, "set_blend_mode"):
            egg_node.set_blend_mode(self.mode)


class EggBlendMode(EggBlendModeAttribute):
    def __init__(self, mode: str):
        super().__init__(mode)
