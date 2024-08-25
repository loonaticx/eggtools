from panda3d.core import Filename, StringStream, LPoint2d
from panda3d.egg import EggTexture, EggData, EggPolygon, EggNode

from eggtools.EggMan import EggMan
from eggtools.components.EggDataContext import EggDataContext
from eggtools.components.points.PointData import PointData, PointHelper

from eggtools.utils import ImageUtils


class Depalettizer:
    def __init__(self, file_list: list, padding_u=0.001, padding_v=0.001, eggman: EggMan = None):
        """
        By default, padding is equivalent to 1% of the texture size [0-1]
        (meaning that the uv would effectively be 99% of its normalized scale)
        """
        self.eggman = eggman
        if not self.eggman:
            self.eggman = EggMan(file_list)
        # Padding must be a non-zero value.
        self.padding_u = max(padding_u, 0.00000000001)
        self.padding_v = max(padding_v, 0.00000000001)

        # Problem: You cannot just add new textures to a texture collection or to polygons. You think it would be easy?
        # No, we need to effectively 'inject' these new texture headers into our working EggData.
        self.raw_data = []

    def normalize_uvs(self, point_data: PointData):
        bbox = point_data.get_bbox()
        min_x, min_y = bbox[0]
        max_x, max_y = bbox[1]

        min_x -= self.padding_u
        max_x += self.padding_u
        min_y -= self.padding_v
        max_y += self.padding_v

        # Reference: https://stackoverflow.com/a/2450158
        # https://www.albany.edu/faculty/jmower/geog/gog530Python/src/NormalizingCoordinatesManual.html

        for vertex, uv_coordinates in point_data.egg_vertex_uvs.items():
            xVal, yVal = uv_coordinates
            newX = xVal - ((max_x + min_x) / 2)
            newX /= max_x - min_x
            newX += 0.5
            newY = yVal - ((max_y + min_y) / 2)
            newY /= max_y - min_y
            newY += 0.5
            vertex.set_uv(LPoint2d(newX, newY))

    def depalettize_node(self, egg_data: EggDataContext, egg_node: EggNode, clamp_uvs=True):
        """
        Depalettizes an EggNode completely.

        WILL affect model/egg data

        :param bool clamp_uvs: Sets the UV wrap mode to clamp. Strongly recommended due to padding artifacts.
        """
        ctx = self.eggman.egg_datas[egg_data]

        i = 0

        # Nodes will most likely contain numerous of textures. We can group related polygons by mutual textures.
        point_texture_lookup = ctx.points_by_textures(egg_node)

        # Focus on each texture.
        for point_texture in point_texture_lookup.keys():
            # Well, now we have PointDatas whose only differences are the different egg_vertex_uvs.
            # Let's aggregate them...
            point_datas = point_texture_lookup[point_texture]

            # THIS is all of our aggregated point data. Don't mind the similar variable names here.
            point_data = PointHelper.unify_point_datas(point_datas)

            # Generates and writes out the new texture images.
            # If we can't create a cropped image let's bounce before something explodes for now
            cropped_filename = ImageUtils.crop_image_to_box(point_data, f"{egg_node.getName()}_{i}")

            if not cropped_filename:
                continue

            # Cross my fingers that this works babyy!!
            self.normalize_uvs(point_data)

            # Generate a new EggTexture, only differences here is just the filename/paths.
            egg_texture_new = self.eggman.rebase_egg_texture(
                cropped_filename.getBasenameWoExtension(), cropped_filename, point_data.egg_texture
            )

            recorded_texture = ctx.egg_texture_collection.findFilename(egg_texture_new.getFilename())

            if not recorded_texture:
                # Adding the new texture into our records.
                ctx.add_collect_texture(egg_texture_new)
                self.raw_data.append(egg_texture_new)
                recorded_texture = egg_texture_new

            for child in egg_node.getChildren():
                if isinstance(child, EggPolygon):
                    if recorded_texture not in ctx.get_used_node_textures(child):
                        child.clearTexture()
                        child.addTexture(recorded_texture)

            # Strongly recommended to keep this on by default since the margining/texture filtering
            # may get a bit distracting
            if clamp_uvs:
                point_data.egg_texture.setWrapU(EggTexture.WM_clamp)
                point_data.egg_texture.setWrapV(EggTexture.WM_clamp)
            i += 1

    def append_new_eggdata(self, egg_data):
        # This will lead to redundant texture entries, but it's ok for now, because they get cleaned up
        # later down the line anyway

        # This is weird, I know, but I have not been able to successfully export egg files *with*
        # the new texture headers. My current workaround is to generate a new EggData and append the existing EggData.
        eggstr = '\n'.join([str(elem) for elem in self.raw_data])
        data_stream = StringStream(bytes(eggstr, encoding = 'utf-8'))
        egg_data_new = EggDataContext()
        egg_data_new.read(data_stream)

        # We want to merge the main egg data with the new egg data because we want those TRef headers
        # on the top of the file.
        egg_data_new.merge(egg_data)
        self.eggman.replace_eggdata(egg_data, egg_data_new)
        ctx = self.eggman.egg_datas[egg_data_new]
        ctx.egg_generated = True

    def depalettize_egg(self, egg_data, clamp_uvs=True):
        """
        Depalettizes an Egg file (EggData) completely.

        :param bool clamp_uvs: Sets the UV wrap mode to clamp. Strongly recommended due to padding artifacts.
        """
        self.raw_data = []
        ctx = self.eggman.egg_datas[egg_data]
        for egg_node in ctx.point_data.keys():
            if ctx.configured:
                self.depalettize_node(egg_data, egg_node, clamp_uvs = clamp_uvs)
                # ctx.merge_replace(new_ctx)
        self.append_new_eggdata(egg_data)

    def depalettize_all(self, clamp_uvs=True):
        """
        Depalettizes all Egg files registered in EggMan.
        """
        # Take a snapshot, we do not want to traverse any new registries into EggMan.
        # can't use a deep copy here..
        context_snapshot = [*self.eggman.egg_datas.keys()]
        for egg_data in context_snapshot:
            ctx = self.eggman.egg_datas.get(egg_data)
            if ctx and not ctx.egg_generated:
                self.depalettize_egg(egg_data, clamp_uvs)

        self.eggman.remove_texture_duplicates()
