from eggtools.attributes.EggAttribute import EggAttribute
from panda3d.egg import EggRenderMode

from eggtools.components.EggExceptions import EggAttributeInvalid

name2id = {
    "unspecified": EggRenderMode.VM_unspecified,
    "off": EggRenderMode.VM_hidden,
    "hidden": EggRenderMode.VM_hidden,
    "on": EggRenderMode.VM_normal,
    "normal": EggRenderMode.VM_normal,

}


def get_visibility_mode(visibility_name: str):
    return name2id.get(visibility_name.lower(), None)


class EggVisibilityAttribute(EggAttribute):
    def __init__(self, visibility_type, overwrite=False):
        if not isinstance(visibility_type, str):
            if visibility_type:
                visibility_type = "on"
            else:
                visibility_type = "off"
        self.overwrite = overwrite
        self.visibility_type = get_visibility_mode(visibility_type)
        if self.visibility_type is None:
            raise EggAttributeInvalid(self, visibility_type)

        super().__init__(entry_type = "Scalar", name = "visibility", contents = self.visibility_type)

    @staticmethod
    def get_visibility_modes():
        return name2id

    def _modify_polygon(self, egg_polygon, tref=None):
        target_nodes = self.target_nodes

        if target_nodes.check(egg_polygon.getName()):
            visbility_mode = egg_polygon.getVisibilityMode()
            if not visbility_mode:
                egg_polygon.setVisibilityMode(self.visibility_type)
            elif self.overwrite:
                if visbility_mode.getVisibilityMode() != self.visibility_type:
                    egg_polygon.setVisibilityMode(self.visibility_type)

    def _modify_node(self, egg_node):
        if self.target_nodes.check(egg_node.getName()):
            visbility_mode = egg_node.getVisibilityMode()
            if not visbility_mode:
                egg_node.setVisibilityMode(self.visibility_type)
            elif self.overwrite:
                if egg_node.getVisibilityMode() != self.visibility_type:
                    egg_node.setVisibilityMode(self.visibility_type)


class EggVisibility(EggVisibilityAttribute):
    def __init__(self, visibility_type, overwrite=False):
        super().__init__(visibility_type, overwrite)
