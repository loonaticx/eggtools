from eggtools.attributes.EggAttribute import EggAttribute
from panda3d.egg import EggRenderMode, EggVertexPool

from eggtools.EggManConfig import DualConfig
from eggtools.components.EggExceptions import EggAttributeInvalid

name2id = {
    "unspecified": EggRenderMode.AM_unspecified,
    "off": EggRenderMode.AM_off,
    "on": EggRenderMode.AM_on,

    # Normal alpha blending
    "blend": EggRenderMode.AM_blend,

    # Alpha blending w/o depth write
    "blend_no_occlude": EggRenderMode.AM_blend_no_occlude,
    "blend-no-occlude": EggRenderMode.AM_blend_no_occlude,

    "ms": EggRenderMode.AM_ms,
    "multisample": EggRenderMode.AM_ms,
    "multisample_mask": EggRenderMode.AM_ms_mask,
    "ms_mask": EggRenderMode.AM_ms_mask,
    "binary": EggRenderMode.AM_binary,
    "dual": EggRenderMode.AM_dual,
    "premultiplied": EggRenderMode.AM_premultiplied,

}


def get_alpha_type(alpha_name: str):
    return name2id.get(alpha_name.lower(), None)


class EggAlphaAttribute(EggAttribute):
    def __init__(self, alpha_name, overwrite=False):
        """
        <Scalar> alpha { alpha_name }
        """
        # <Scalar> alpha { dual }
        self.alpha_name = alpha_name
        self.overwrite = overwrite
        self.alpha_mode = get_alpha_type(self.alpha_name)
        if self.alpha_mode is None:
            raise EggAttributeInvalid(self, self.alpha_name)
        super().__init__(entry_type = "Scalar", name = "alpha", contents = self.alpha_name)

    @staticmethod
    def get_attributes():
        return name2id

    def _modify_polygon(self, egg_polygon, tref):
        if not self.target_nodes:
            target_nodes = DualConfig
        else:
            target_nodes = self.target_nodes

        if target_nodes.check(tref.getName()):
            # We got ourselves a winner. Let's find the Group parent and add a dual attribute to it.
            alpha_mode = egg_polygon.determineAlphaMode()
            if not alpha_mode:
                egg_polygon.setAlphaMode(self.alpha_mode)
            elif self.overwrite:
                if alpha_mode.getAlphaMode() != self.alpha_mode:
                    egg_polygon.setAlphaMode(self.alpha_mode)

    def _modify_node(self, egg_node):
        if isinstance(egg_node, EggVertexPool):
            return
        if self.target_nodes.check(egg_node.getName()):
            # We got ourselves a winner. Let's find the Group parent and add a dual attribute to it.
            alpha_mode = egg_node.determineAlphaMode()
            if not alpha_mode and hasattr(egg_node, "setAlphaMode"):
                egg_node.setAlphaMode(self.alpha_mode)
            elif self.overwrite:
                if egg_node.getAlphaMode() != self.alpha_mode:
                    egg_node.setAlphaMode(self.alpha_mode)


class EggAlpha(EggAlphaAttribute):
    def __init__(self, alpha_name, overwrite=False):
        super().__init__(alpha_name, overwrite)
