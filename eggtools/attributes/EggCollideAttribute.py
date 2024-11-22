from panda3d.egg import EggGroup, EggVertexPool, EggPolygon

from eggtools.attributes.EggAttribute import EggAttribute
from eggtools.components.EggEnums import CollisionFlagType, CollisionSolidType
from eggtools.components.EggExceptions import EggAttributeInvalid

# Collision Solids, see EggEnums for usage information
cs2type = {
    'none': CollisionSolidType.NoType,
    'plane': CollisionSolidType.Plane,
    'polygon': CollisionSolidType.Polygon,
    'polyset': CollisionSolidType.Polyset,
    'sphere': CollisionSolidType.Sphere,
    'tube': CollisionSolidType.Tube,
    'inv_sphere': CollisionSolidType.InvSphere,
    'invsphere': CollisionSolidType.InvSphere,
    'box': CollisionSolidType.Box,
    'floor_mesh': CollisionSolidType.FloorMesh,
}


def get_collision_solid(cs_name: str):
    return cs2type.get(cs_name.lower(), None)


# Collision Flags, see EggEnums for usage information

flags2type = {
    'none': CollisionFlagType.NoType,
    'descend': CollisionFlagType.Descend,
    'event': CollisionFlagType.Event,
    'keep': CollisionFlagType.Keep,
    'solid': CollisionFlagType.Solid,
    'center': CollisionFlagType.Center,
    'turnstile': CollisionFlagType.Turnstile,
    'level': CollisionFlagType.Level,
    'intangible': CollisionFlagType.Intangible,
}


def get_collision_flag(cf_name: str):
    return flags2type.get(cf_name.lower(), None)


class EggCollideAttribute(EggAttribute):
    def __init__(self, csname, flags, name='', preserve_uv_data=True):
        # <Collide> name { type [flags] }
        self.cstype = get_collision_solid(csname)
        if self.cstype is None:
            raise EggAttributeInvalid(self, csname)
        self.flags = list()

        # Make sure flags is not empty & it's a proper list.
        if flags and not isinstance(flags, list):
            flags = [flags]

        #  Using <Collide> without 'descend' is deprecated, add it on:
        if 'descend' not in flags:
            flags.append('descend')

        for flag_entry in flags:
            flag_value = get_collision_flag(flag_entry)
            if flag_value is None:
                raise EggAttributeInvalid(self, flag_entry)
            self.flags.append(flag_value)

        self.preserve_uv_data = preserve_uv_data

        super().__init__(entry_type = "Collide", name = name,
                         contents = csname + (' ' if flags else '') + ' '.join(flags))

    @staticmethod
    def get_collision_solids():
        return cs2type

    @staticmethod
    def get_collision_flags():
        return flags2type

    def _modify_polygon(self, egg_polygon, tref=None):
        # print(egg_polygon.hasColor())
        pass

    def _modify_node(self, egg_node):
        if self.target_nodes.check(egg_node.getName()) and hasattr(egg_node, "setCollideFlags"):
            # We must aggregate all the collision bits
            collisionFlag = 0
            for flag in self.flags:
                collisionFlag |= flag
            egg_node.setCollideFlags(collisionFlag)
            egg_node.setCollisionName(self.name)
            egg_node.setCsType(self.cstype)
            if not self.preserve_uv_data:
                self.remove_uv_data(egg_node)

    def remove_uv_data(self, egg_node):
        """
        Removes UV data and textures/materials associated with the node's polygons.
        """
        if isinstance(egg_node, EggGroup):
            for child in egg_node.getChildren():
                self.remove_uv_data(child)

        if isinstance(egg_node, EggVertexPool):
            for vpoolchild in egg_node:  # should only contain EggVertexes
                vpoolchild.clear_uv()

        if isinstance(egg_node, EggPolygon):
            if "keep" not in self.flags:
                egg_node.clear_texture()
                egg_node.clear_material()


class EggCollide(EggCollideAttribute):
    def __init__(self, csname, flags, name='', preserve_uv_data=True):
        super().__init__(csname, flags, name, preserve_uv_data = preserve_uv_data)
