from eggtools.attributes.EggAttribute import EggAttribute

from eggtools.components.EggEnums import DynamicCoordinateType
from eggtools.components.EggExceptions import EggAttributeInvalid

name2id = {
    "unspecified": DynamicCoordinateType.Unspecified,
    "none": DynamicCoordinateType.NoType,
    "local": DynamicCoordinateType.Local,
    "net": DynamicCoordinateType.Net,
    "no_touch": DynamicCoordinateType.NoTouch,
    "no-touch": DynamicCoordinateType.NoTouch,
    "notouch": DynamicCoordinateType.NoTouch,
    "default": DynamicCoordinateType.Default,
}


def get_dcs_type(dcs_name: str):
    return name2id.get(dcs_name.lower(), None)


class EggDCSAttribute(EggAttribute):
    def __init__(self, dcs_type):
        # <DCS> { boolean-value }
        # or
        # <DCS> { dcs-type }
        # https://loonaticx.github.io/panda3d-egg-bible/home/syntax/general.html#dcs-attributes
        if type(dcs_type) is bool or type(dcs_type) is int:
            if dcs_type:
                # True/1
                dcs_type = "default"
            else:
                # False/0
                dcs_type = "none"
        self.dcs_type = dcs_type
        self.dcs_mode = get_dcs_type(self.dcs_type)
        if self.dcs_mode is None:
            raise EggAttributeInvalid(self, self.dcs_type)
        super().__init__(entry_type = "DCS", name = "", contents = self.dcs_type)

    @staticmethod
    def get_dcs_types():
        return name2id

    def _modify_polygon(self, egg_polygon, tref):
        pass

    def _modify_node(self, egg_node):
        if not hasattr(egg_node, "hasDcsType"):
            return
        # 'panda3d.egg.EggVertexPool' object has no attribute 'hasDcsType'
        if self.target_nodes.check(egg_node.getName()):
            if not egg_node.hasDcsType():
                egg_node.setDcsType(self.dcs_mode)
        pass


class EggDCS(EggDCSAttribute):
    def __init__(self, dcs_type):
        super().__init__(dcs_type)
