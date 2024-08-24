import copy
import shutil
import os

from panda3d.core import Filename, StringStream, LPoint2d
from panda3d.egg import EggTexture, EggData, EggPolygon

from eggtools.EggMan import EggMan
from eggtools.components.EggDataContext import EggDataContext
from eggtools.components.points.PointData import PointData

from eggtools.utils import ImageUtils


class Depalettizer:
    def __init__(self, file_list: list, padding_u=0.001, padding_v=0.001):
        self.eggman = EggMan(file_list)
        # Don't let these values be zero!
        self.padding_u = max(padding_u, 0.001)
        self.padding_v = max(padding_v, 0.001)

    def normalize_uvs(self, point_data: PointData):
        bbox = point_data.get_bbox()
        min_x, min_y = bbox[0]
        max_x, max_y = bbox[1]

        min_x += self.padding_u
        max_x -= self.padding_u
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

        # Problem: You cannot just add new textures to a texture collection or to polygons. You think it would be easy?
        # No, we need to effectively 'inject' these new texture headers into our working EggData.
        raw_data = []
        i = 0

        # Nodes will most likely contain numerous of textures. We can group related polygons by mutual textures.
        point_texture_lookup = ctx.points_by_textures(egg_node)

        # Focus on each texture.
        for point_texture in point_texture_lookup.keys():
            # Well, now we have PointDatas whose only differences are the different egg_vertex_uvs.
            # Let's aggregate them...
            point_vertexes = dict()
            point_datas = point_texture_lookup[point_texture]
            point_filename = None
            for pd in point_datas:
                point_vertexes = point_vertexes | pd.egg_vertex_uvs
                # I am aware that this variable will continuously get changed
                point_filename = pd.egg_filename

            # THIS is all of our aggregated point data. Don't mind the similar variable names here.
            point_data = PointData(point_filename, point_vertexes, point_texture)

            # Cross my fingers that this works babyy!!
            self.normalize_uvs(point_data)

            # Generates and writes out the new texture images.
            cropped_filename = ImageUtils.crop_image_to_box(point_data, str(i))
            # Generate a new EggTexture, only differences here is just the filename/paths.
            egg_texture_new = self.eggman.rebase_egg_texture(
                cropped_filename.getBasenameWoExtension(), cropped_filename, point_data.egg_texture
            )

            # Adding the new texture into our records.
            ctx.add_collect_texture(egg_texture_new)
            raw_data.append(egg_texture_new)

            # No, don't do this. Just adds redundant TRefs and causes issues.
            for child in egg_node.getChildren():
                if isinstance(child, EggPolygon):
                    if egg_texture_new not in ctx.get_used_node_textures(child):
                        child.clearTexture()
                        child.addTexture(egg_texture_new)

            # Strongly recommended to keep this on by default since the margining/texture filtering
            # may get a bit distracting
            if clamp_uvs:
                point_data.egg_texture.setWrapU(EggTexture.WM_clamp)
                point_data.egg_texture.setWrapV(EggTexture.WM_clamp)
            i += 1

        # This is weird, I know, but I have not been able to successfully export egg files *with*
        # the new texture headers. My current workaround is to generate a new EggData and append the existing EggData.
        eggstr = '\n'.join([str(elem) for elem in raw_data])
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
        ctx = self.eggman.egg_datas[egg_data]
        for egg_node in ctx.point_data.keys():
            # This is just a bandaid patch for now
            if ctx.configured:
                self.depalettize_node(egg_data, egg_node, clamp_uvs = clamp_uvs)

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
