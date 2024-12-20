from eggtools.attributes.EggAttribute import EggAttribute
from panda3d.egg import EggRenderMode

from eggtools.components.EggEnums import DepthWriteMode
from eggtools.components.EggExceptions import EggAttributeInvalid

name2id = {
    "unspecified": DepthWriteMode.Unspecified,  # 0
    "off": DepthWriteMode.Off,  # 1
    "on": DepthWriteMode.On,  # 2
}


def get_depth_write_mode(depth_write_name: str):
    return name2id.get(depth_write_name.lower(), None)


class EggDepthWriteAttribute(EggAttribute):
    def __init__(self, depth_type, overwrite=False):
        self.overwrite = overwrite
        if not isinstance(depth_type, str):
            if depth_type:
                depth_type = "on"
            else:
                depth_type = "off"
        self.depth_type = get_depth_write_mode(depth_type)
        if self.depth_type is None:
            raise EggAttributeInvalid(self, depth_type)
        super().__init__(entry_type = "Scalar", name = "depth-write", contents = depth_type)

    @staticmethod
    def get_depth_write_modes():
        return name2id

    def _modify_polygon(self, egg_polygon, tref=None):
        target_nodes = self.target_nodes

        if target_nodes.check(egg_polygon.getName()):
            # getDepthWrite is for EggRenderMode
            depth_write_mode = egg_polygon.getDepthWriteMode()
            if not depth_write_mode:
                egg_polygon.setDepthWriteMode(self.depth_type)
            elif self.overwrite:
                if depth_write_mode.getDepthWriteMode() != self.depth_type:
                    egg_polygon.setDepthWriteMode(self.depth_type)

    def _modify_node(self, egg_node):
        if self.target_nodes.check(egg_node.getName()) and \
                hasattr(egg_node, "determineDepthWriteMode") and \
                hasattr(egg_node, "setDepthWriteMode"):
            # First, check if we HAVE a render mode in the first place:
            render_mode: EggRenderMode = egg_node.determineDepthWriteMode()

            # If we do not have a render node, then we do not have a depth-write value.
            if not render_mode:
                # Generate our initial <Scalar> depth-write {} value:
                # This will also generate our missing render mode.
                egg_node.setDepthWriteMode(self.depth_type)

            # If we already have a render mode, that means there may be a depth-write value already set!
            # If we already have a depth-write attribute, forcibly change it if overwrite is enabled.
            elif self.overwrite:
                if render_mode.getDepthWriteMode() != self.depth_type:
                    render_mode.setDepthWriteMode(self.depth_type)


class EggDepthWrite(EggDepthWriteAttribute):
    def __init__(self, depth_type, overwrite=False):
        super().__init__(depth_type, overwrite)
