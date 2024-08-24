from ordered_set import OrderedSet
from panda3d.core import Filename
from panda3d.egg import EggTextureCollection, EggTexture, EggNode

from eggtools.components.EggDataContext import EggDataContext

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from eggtools.components.points.PointData import PointData


class EggContext:
    """
    Holds iterable attributes for an EggData object
    """

    @property
    def filename(self) -> Filename:
        return self._filename

    @filename.setter
    def filename(self, filename: Filename):
        if filename and not isinstance(filename, Filename):
            filename = Filename.fromOsSpecific(filename)
        # Set the variable in EggContext FIRST to prevent a circular call loop
        self._filename = filename
        loopback = self.egg_data_loopback
        if isinstance(loopback, EggDataContext) and loopback.egg_filename is not self._filename:
            loopback.filename = self._filename
        # For now we only have one important consideration for if a context is configured.
        # This isn't the strongest logic, but it will do for now.
        self.configured = not self._filename.empty()

    # Holds the intended filename out of the egg.
    # *Should* be in sync with whatever the value is in EggData
    _filename: Filename

    def __hash__(self):
        return hash(str(self))

    def __init__(self, filename: Filename):
        # Don't completely rely on this being the source EggData object. This is meant for synchronization uses.
        self.egg_data_loopback: EggDataContext | None = None

        # If egg has been altered in memory, it is considered dirty and subject to overwrite what's on the disk.
        self.dirty = False

        self.egg_textures = set()
        self.egg_texture_collection = EggTextureCollection()
        self.egg_materials = set()
        self.egg_attributes = set()
        self.egg_timestamp_old: int | bool = False
        self.egg_save_timestamp = False
        self.egg_ext_file_refs = set()
        self.egg_groups = set()

        # True if the corresponding egg data was created during code execution.
        # More specifically used for flagging not-iter-safe eggs during an EggMan traversal.
        self.egg_generated = False

        # Context is considered "configured" if it went through EggMan's traversal without running into any
        # critical issues, such as a missing filename.
        # This just indicates that the EggContext setup and ready for action.
        self.configured = False

        self.point_data: dict[EggNode, OrderedSet[PointData]] = dict()
        # { EggNode : [PointData] }

        self.filename = filename

    def add_collect_texture(self, egg_texture: EggTexture):
        """
        Currently a convenience method to handle managing both the texture set and TextureCollection object.
        """
        self.egg_textures.add(egg_texture)
        self.egg_texture_collection.addTexture(egg_texture)
        self.dirty = True

    def get_used_node_textures(self, egg_node: EggNode) -> list:
        # Gotta make another one of these since the class one includes every texture registered already
        texcollection = EggTextureCollection()
        texcollection.findUsedTextures(egg_node)
        return texcollection.getTextures()

    def points_by_textures(self, egg_node: EggNode):
        point_datas = self.point_data[egg_node]
        node_textures = dict()
        for egg_texture in self.get_used_node_textures(egg_node):
            node_textures[egg_texture] = []

        for point_data in point_datas:
            point_texture = point_data.egg_texture
            if not point_texture:
                continue
            # BETTER NOT DESYNC FOOL
            node_textures[point_texture].append(point_data)

        return node_textures

    def merge_replace(self, ctx_other, prioritize_other=False):
        if ctx_other.filename:
            if not self.filename:
                self.filename = ctx_other.filename
            elif prioritize_other:
                self.filename = ctx_other.filename
        # TODO: merging sets, EggTextureCollections, etc.

        self.dirty = True

    def destroy(self):
        # Goobye
        self.egg_data_loopback = None
        self.dirty = False
        self.egg_textures = set()
        self.egg_texture_collection = EggTextureCollection()
        self.egg_materials = set()
        self.egg_attributes = set()
        self.egg_timestamp_old = False
        self.egg_save_timestamp = False
        self.egg_ext_file_refs = set()
        self.egg_groups = set()
        self.egg_generated = False
        self.point_data = dict()
        self.filename = Filename()
