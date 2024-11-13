from eggtools.attributes.EggAttribute import EggAttribute
from panda3d.egg import EggGroup

from eggtools.components.EggExceptions import EggAttributeInvalid

name2id = {
    "none": EggGroup.BT_none,
    "axis": EggGroup.BT_axis,
    "point": EggGroup.BT_point_camera_relative,
    "point_camera_relative": EggGroup.BT_point_camera_relative,
    "point_world_relative": EggGroup.BT_point_world_relative,
}


def get_billboard_type(billboard_name: str):
    return name2id.get(billboard_name.lower(), None)


class EggBillboardAttribute(EggAttribute):
    def __init__(self, billboard_type: str):
        self.billboard_type = billboard_type
        self.billboard_mode = get_billboard_type(billboard_type)
        if self.billboard_mode is None:  # 0 != None
            raise EggAttributeInvalid(self, self.billboard_type)
        super().__init__(entry_type = "Billboard", name = "", contents = billboard_type)

    @staticmethod
    def get_billboard_types():
        return name2id

    def _modify_polygon(self, egg_polygon, tref):
        pass

    def _modify_node(self, egg_node):
        if self.target_nodes.check(egg_node.getName()) and hasattr(egg_node, "getBillboardType"):
            if not egg_node.getBillboardType():
                egg_node.setBillboardType(self.billboard_mode)


class EggBillboard(EggBillboardAttribute):
    def __init__(self, billboard_type: str):
        super().__init__(billboard_type)
