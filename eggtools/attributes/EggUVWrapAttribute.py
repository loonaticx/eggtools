"""
UV Wrap mode for an EggNode that has a texture.

Note: If an EggNode is being modified by this attribute, keep in mind that
all of its textures will be modified. Any nodes that use the same texture will also get the modification

This is because the UV wrap mode is assigned in the Texture header.
"""

from panda3d.egg import EggTexture

from eggtools.attributes.EggAttribute import EggAttribute
from eggtools.components.EggEnums import TextureWrapMode

name2id = {
    # note: setting to unspecified will just not set/define anything
    "unspecified": TextureWrapMode.Unspecified,  # 0
    "clamp": TextureWrapMode.Clamp,
    "repeat": TextureWrapMode.Repeat,
    "mirror": TextureWrapMode.Mirror,
    "mirror_once": TextureWrapMode.MirrorOnce,
    "border_color": TextureWrapMode.BorderColor
}


def get_wm_type(wm_name: str):
    if not wm_name:
        return None
    return name2id.get(wm_name.lower(), None)


class EggUVWrapAttribute(EggAttribute):

    # note: there's some determineWrapX methods in EggTexture, which says it tries to
    # determine the appropriate wrap in X direction. could we use this to our advantage?
    def __init__(self, wrap_u=None, wrap_v=None, wrap_w=None, border_color=None):
        """
        <Scalar> wrapX { wm_type }
        """
        self.wrap_u = get_wm_type(wrap_u)
        self.wrap_v = get_wm_type(wrap_v)
        self.wrap_w = get_wm_type(wrap_w)
        self.border_color = border_color
        # cant pretty define this for now
        super().__init__(entry_type = "Scalar", name = "wrap", contents = "")

    @staticmethod
    def get_attributes():
        return name2id

    def _modify_polygon(self, egg_polygon, tref=None):
        pass

    def _modify_node(self, egg_node):
        if isinstance(egg_node, EggTexture):
            egg_texture = egg_node
            wrap_u: EggTexture.WrapMode = egg_texture.getWrapU()
            wrap_v: EggTexture.WrapMode = egg_texture.getWrapV()
            wrap_w: EggTexture.WrapMode = egg_texture.getWrapW()
            if self.wrap_u is not None:
                egg_texture.setWrapU(self.wrap_u)
            if self.wrap_v is not None:
                egg_texture.setWrapV(self.wrap_v)
            if self.wrap_w is not None:
                egg_texture.setWrapW(self.wrap_w)
            if self.border_color:
                egg_texture.setBorderColor(self.border_color)


class EggUVWrap(EggUVWrapAttribute):
    def __init__(self, wrap_u=None, wrap_v=None, wrap_w=None, border_color=None):
        super().__init__(wrap_u, wrap_v, wrap_w, border_color)
