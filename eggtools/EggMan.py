"""
EggMan: The docile robust egg manager for installing & maintaining models.

Allows you to do bulk/individual modifications to a set of egg files, including support for:
- Repathing textures, with support for auto-resolving broken texture paths
- Renaming TRefs to be something more appropriate and not like lambert69SG
- Removing defined UV names, which have a history of causing issues
- Removing Material/MRef data, since we don't have any use for them
- Renaming Group nodes
"""
from __future__ import annotations

import logging
from enum import Enum
from typing import Union, Dict, List
from typing import Optional

from ordered_set import OrderedSet
from panda3d.core import Filename
from panda3d.egg import *
import os
from pathlib import Path

from eggtools.components.EggExceptions import EggAccessViolation, EggImproperArgType
from eggtools.AttributeDefs import DefinedAttributes, ObjectTypeDefs
from eggtools.attributes.EggAttribute import EggAttribute
from eggtools.attributes.EggUVNameAttribute import EggUVNameAttribute
from eggtools.components.points.PointData import PointData
from eggtools.config.EggVariableConfig import GAMEASSETS_MAPS_PATH
from eggtools.utils.EggNameResolver import EggNameResolver
from eggtools.components.EggContext import EggContext
from eggtools.components.EggDataContext import EggDataContext

BASE_PATH = GAMEASSETS_MAPS_PATH


class EggGroupRenameType(str, Enum):
    RenamePrefixes = "rename_prefix"
    RenameSuffixes = "rename_suffix"
    ReplaceAll = "replace_all"


class EggMan(object):
    # This is used to quickly grab EggData via a texture name
    _egg_name_2_egg_data = dict()

    def __str__(self):
        out = f"Eggman ({id(self)})\n"
        for egg in self.egg_datas.keys():
            out += str(self.egg_datas[egg]) + "\n"
        return out

    def verify_integrity(func):
        """
        Watcher to ensure that no invalid egg inputs are given
        """

        def verify(self, egg_base: EggData, *args):
            if not isinstance(egg_base, EggData):
                raise EggImproperArgType(egg_base, EggData)

            if not self.egg_datas.get(egg_base):
                raise EggAccessViolation(egg_base, "Attempted to utilize non-existent EggData entry!")

            return func(self, egg_base, *args)

        return verify

    def __init__(self, egg_filepaths: list, search_paths: List[str] = None,
                 loglevel: logging = logging.WARNING) -> None:
        logging.basicConfig(level = loglevel)
        if not search_paths:
            search_paths = [BASE_PATH]
        self.NameResolver = EggNameResolver(search_paths, loglevel = loglevel)
        self.search_paths = self.NameResolver.search_paths

        # use egg_datas to work with registered eggs
        # filename is stored in EggContext.filename
        self.egg_datas = dict()  # { EggData : EggContext }
        self.defined_attributes = DefinedAttributes

        self.register_eggs(egg_filepaths)

    """
    Core
    """

    # region

    def register_eggs(self, egg_filepaths: List[Union[Filename, str]]) -> None:
        """
        Register Egg entries with EggMan through filepaths.
        """
        if not egg_filepaths:
            return
        for fp in egg_filepaths:
            if not isinstance(fp, Filename):
                fp = Filename.fromOsSpecific(fp)
            if fp.getExtension() not in ("egg", "pz"):  # pz: pzip
                print(f"{fp.getBasenameWoExtension()} does not have egg extension, not registering {fp.getFullpath()}")
                continue
            egg_data = EggDataContext()
            egg_data.read(fp)
            self.register_egg_data([egg_data])

    def register_egg_data(self, egg_datas: List[Union[EggData, EggDataContext]]) -> None:
        """
        Registers supplemented egg data into EggMan.
        """
        if not isinstance(egg_datas, list):
            egg_datas = [egg_datas]

        for egg_data in egg_datas:
            if self.egg_datas.get(egg_data):
                raise EggAccessViolation(egg_data, "Attempted to register the same EggData more than once!")
            egg_filepath = egg_data.getEggFilename()

            self.egg_datas[egg_data] = EggContext(egg_filepath)
            ctx = self.egg_datas[egg_data]

            if isinstance(egg_data, EggDataContext):
                egg_data.context = ctx

            # Populates this EggTextureCollection. Note that you will need to ensure that the texture collection
            # is recalled if any textures are added/deleted.
            ctx.egg_texture_collection.findUsedTextures(egg_data)
            self._traverse_egg(egg_data, ctx)
            self._egg_name_2_egg_data[egg_filepath.getBasename()] = egg_data
            if not egg_data.getChildren():
                logging.warning("Registering empty EggData!")
            if not ctx.filename:
                # Todo: better handling for egg files with no filename
                # Setting this to debug instead of warning, it should be a warning but we always seem to catch this
                logging.debug("EggData entry registered with no filename (use setEggFilename!)")

    def _register_egg_texture(self, ctx: EggContext, target_node: EggTexture) -> None:
        """
        Register an egg texture with the given EggContext. This is used when traversing down the egg.
        """
        ctx.add_collect_texture(target_node)
        uvName = target_node.getUvName()
        if uvName:
            uvAttr = EggUVNameAttribute(uvName)
            ctx.egg_attributes.add(uvAttr)

    def _traverse_egg(self, egg: Union[EggData, EggGroup], ctx: EggContext) -> None:
        """
        Traverses down an egg tree and records data mapped to the ctx key.

        :param EggData | EggGroup egg: Egg to traverse
        :param EggContext ctx: The original EggContext, required to keep things in order during recursion.
        """
        # we ask for ctx just to keep things in order
        for child in egg.getChildren():
            if isinstance(child, EggGroup):
                # print(f"ObjectTypes for {child.getName()} - {child.getObjectTypes()}")
                self._replace_object_types(ctx, child)
                ctx.egg_groups.add(child)
                self._traverse_egg(child, ctx)

            # <Material> { ... }
            if isinstance(child, EggMaterial):
                ctx.egg_materials.add(child)

            # <Texture> { blah.png }
            if isinstance(child, EggTexture):
                self._register_egg_texture(ctx, child)

            # <File> { filename.egg }
            if isinstance(child, EggExternalReference):
                ctx.egg_ext_file_refs.add(child)

            if isinstance(child, EggPolygon):
                # { EggGroupName { { Polygon_TREFNAME : { "vertexID" : [ U, V ] } } }
                # For now can we only use one tref for Polygon entries, even though having more is possible
                polyTexture = child.getTexture()
                # Even if the poly doesn't have a texture, we should still traverse it for now
                # let's not discriminate..
                # if not polyTexture:
                #     continue
                parent_node = child.getParent()

                vertex_uvs = {}
                # UV name attributes are handled separately since they are tangible
                for egg_vertex in child.getVertices():
                    u, v = [None, None]
                    if egg_vertex.hasUv():
                        u, v = egg_vertex.getUv()
                    vertex_uvs[egg_vertex] = [u, v]

                if not ctx.point_data.get(parent_node):
                    ctx.point_data[parent_node] = OrderedSet()

                # parent node should already have an entry.
                ctx.point_data[parent_node].add(
                    PointData(
                        egg_filename = ctx.filename,
                        egg_vertex_uvs = vertex_uvs,
                        egg_texture = polyTexture
                    )
                )

    # endregion

    """
    EggData Management
    """

    # region
    def merge_eggs(self, destination_egg: EggDataContext,
                   target_eggs: Union[List[EggDataContext], EggDataContext]) -> None:
        """
        Source egg(s) will be removed from egg datas and cannot be searched for anymore.

        Result will be the object passed through the destination_egg argument.
        """
        if not isinstance(target_eggs, list):
            target_eggs = [target_eggs]

        for sacrifice in target_eggs:
            ctx = self.egg_datas[sacrifice]
            # Remove old egg from dict
            del self._egg_name_2_egg_data[ctx.filename.getBasename()]
            destination_egg.merge(sacrifice)
            del self.egg_datas[sacrifice]

        self.mark_dirty(destination_egg)

    @verify_integrity
    def replace_eggdata(self, old_eggdata: EggDataContext, new_eggdata: EggDataContext):
        """
        Replaces a registered EggData entry with any unregistered EggData entry.
        Note: EggContext may be stale from this!

        :param new_eggdata: EggData that is currently *not* registered with EggMan yet.
        """
        """
        # Use case:
        newEggData = EggData()
        newEggData.read(...)
        # Example: Adding new data entries to the top of the egg file, rather than the bottom
        newEggData.merge(oldEggData)
        eggman.replace_eggdata(oldEggData, newEggData)
        """
        if old_eggdata is new_eggdata:
            # This would already raise an exception, but let's give a bit more of a clear reason.
            raise EggAccessViolation(new_eggdata, "Cannot replace EggData with itself!")

        ctx_old = self.egg_datas[old_eggdata]

        # Generate new EggData entry
        self.register_egg_data(new_eggdata)

        ctx_new = self.egg_datas[new_eggdata]
        ctx_new.merge_replace(ctx_old)
        ctx_new.egg_texture_collection.removeUnusedTextures(new_eggdata)

        # Swap locations of the old and new entry to preserve the index order.
        egg_indexes = list(self.egg_datas)
        old_eggdata_index = egg_indexes.index(old_eggdata)
        new_eggdata_index = egg_indexes.index(new_eggdata)

        eggdata = list(self.egg_datas.items())

        # Move old eggdata to the back of the dict so that it doesn't affect anyone else
        eggdata[old_eggdata_index], eggdata[new_eggdata_index] = eggdata[new_eggdata_index], eggdata[old_eggdata_index]

        # Convert back to dict
        self.egg_datas = dict(eggdata)

        # Remove old egg from dict
        del self._egg_name_2_egg_data[ctx_old.filename.getBasename()]
        del self.egg_datas[old_eggdata]
        ctx_old.destroy()
        del ctx_old

    # endregion

    """
    Egg Group Management
    """

    # region

    def strip_all_group_prefix(self, prefixes, recurse):
        for egg_data in self.egg_datas.keys():
            self.strip_group_prefix(egg_data, prefixes = prefixes, recurse = recurse)

    def strip_group_prefix(self, egg: EggNode, prefixes, recurse):
        """
        wrapper for rename_group_nodes
        """
        self.rename_group_nodes(
            egg,
            rename_type = EggGroupRenameType.RenamePrefixes,
            substrings = prefixes,
            recurse = recurse
        )

    def strip_all_group_suffix(self, suffixes, recurse):
        for egg_data in self.egg_datas.keys():
            self.strip_group_suffix(egg_data, suffixes = suffixes, recurse = recurse)

    def strip_group_suffix(self, egg: EggNode, suffixes, recurse):
        """
        wrapper for rename_group_nodes
        """
        self.rename_group_nodes(
            egg,
            rename_type = EggGroupRenameType.RenameSuffixes,
            substrings = suffixes,
            recurse = recurse
        )

    def rename_all_group_nodes(self, rename_type: EggGroupRenameType, substrings: list, recurse=True):
        for egg_data in self.egg_datas.keys():
            self.mark_dirty(egg_data)
            self.rename_group_nodes(egg_data, rename_type, substrings, recurse)

    def rename_group_nodes(self, egg: EggNode, rename_type: EggGroupRenameType, substrings: list, recurse: bool = True):
        """
        :param bool recurse: If true, will rename every nested group in the egg.
            False will only rename the highest layer.
        """

        def strip_group_prefix(egg: EggGroup, prefixes: list):
            # note: removeprefix exists in python 3.9
            name = egg.get_name()
            for prefix in prefixes:
                if name.startswith(prefix):
                    return name[len(prefix):]
            return name

        def strip_group_suffix(egg: EggGroup, suffixes: list):
            name = egg.get_name()
            for suffix in suffixes:
                if name.endswith(suffix):
                    return name.rstrip(suffix)
            return name

        def traverse_egg(egg: EggNode, ctx: EggContext):
            """
            Traverses down an egg tree and records data mapped to the ctx key.

            :param egg: Egg to traverse
            :type egg: EggData | EggGroup
            :param ctx: The original EggContext, required to keep things in order during recursion.
            :type ctx: EggContext
            """
            # we ask for ctx just to keep things in order
            for child in egg.getChildren():
                if isinstance(child, EggGroup):
                    if rename_type == EggGroupRenameType.RenamePrefixes:
                        child.set_name(strip_group_prefix(child, substrings))
                    elif rename_type == EggGroupRenameType.RenameSuffixes:
                        child.set_name(strip_group_suffix(child, substrings))
                    else:
                        # replace all
                        new_name = child.get_name().replace(substrings[0], substrings[1])
                        child.set_name(new_name)
                    if recurse:
                        traverse_egg(child, ctx)

        traverse_egg(egg, self.egg_datas[egg])

    # endregion

    """
    Egg Attribute Management
    """

    # region

    def apply_all_attributes(self, egg_attributes: Dict[EggAttribute] = None) -> None:
        """
        By default, will clear up all the defined UV names if applicable
        """
        for egg_data in self.egg_datas.keys():
            self.apply_attributes(egg_data, egg_attributes)

    @verify_integrity
    def apply_attributes(self, egg_base: EggData, egg_attributes: Dict[EggAttribute] = None) -> None:
        ctx = self.egg_datas.get(egg_base)

        if not egg_attributes:
            egg_attributes = dict()

        dirty = False

        for attribute in egg_attributes.keys():
            node_entries = egg_attributes[attribute]
            attribute.apply(egg_base, ctx, node_entries)
            dirty = True
        for attribute in ctx.egg_attributes:
            attribute.apply(egg_base, ctx)
            dirty = True
        if dirty:
            self.mark_dirty(egg_base)

    def _replace_object_types(self, ctx: EggContext, target_node: EggGroup) -> None:
        if not hasattr(target_node, "getObjectTypes"):
            return
        # Hack- Find egg data from ctx (reverse operation)
        egg_base = list(filter(lambda x: self.egg_datas[x] == ctx, self.egg_datas))[0]
        for object_type_name in target_node.getObjectTypes():
            object_type_def = ObjectTypeDefs.get(object_type_name, list())
            # If we don't have an <ObjectType> defined for this instance, just keep it on the egg file and move on.
            if not object_type_def:
                continue
            for attribute in object_type_def:
                # Apply EggAttribute equivalents defined for this object type
                attribute.apply(egg_base, ctx, node_entries = [target_node.getName()])
            target_node.removeObjectType(object_type_name)
            ctx.dirty = True

    # endregion

    """
    Texture Reference Methods
    """

    # region
    def rebase_egg_texture(self, tref: str, new_tex_path: str, old_egg_texture: EggTexture) -> EggTexture:
        """
        Generates a new EggTexture with a given tref + texpath while copying the attributes of the old EggTexture.

        :param str tref: TextureReference name
        :param str new_tex_path: New texture path for the EggTexture
        :param EggTexture old_egg_texture: EggTexture to inherit attributes from
        :return: EggTexture with modified tref/tex path
        :rtype: EggTexture
        """
        # lord, forgive me for my sins
        et = EggTexture(tref, new_tex_path)

        et.alpha_file_channel = old_egg_texture.alpha_file_channel
        et.alpha_filename = old_egg_texture.alpha_filename
        et.alpha_fullpath = old_egg_texture.alpha_fullpath
        et.alpha_scale = old_egg_texture.alpha_scale
        et.anisotropic_degree = old_egg_texture.anisotropic_degree
        et.border_color = old_egg_texture.border_color
        et.color = old_egg_texture.color
        et.compression_mode = old_egg_texture.compression_mode
        et.env_type = old_egg_texture.env_type
        et.format = old_egg_texture.format
        et.lod_bias = old_egg_texture.lod_bias
        et.magfilter = old_egg_texture.magfilter
        et.max_lod = old_egg_texture.max_lod
        et.min_lod = old_egg_texture.min_lod
        et.minfilter = old_egg_texture.minfilter
        # et.multitexture_sort = old_egg_texture.multitexture_sort
        et.multiview = old_egg_texture.multiview
        et.num_views = old_egg_texture.num_views
        et.priority = old_egg_texture.priority
        et.quality_level = old_egg_texture.quality_level
        et.read_mipmaps = old_egg_texture.read_mipmaps
        et.rgb_scale = old_egg_texture.rgb_scale
        et.saved_result = old_egg_texture.saved_result
        et.stage_name = old_egg_texture.stage_name
        et.tex_gen = old_egg_texture.tex_gen
        et.texture_type = old_egg_texture.texture_type
        et.uv_name = old_egg_texture.uv_name  # meh we dont like these but let's play fair now
        et.wrap_mode = old_egg_texture.wrap_mode
        et.wrap_u = old_egg_texture.wrap_u
        et.wrap_v = old_egg_texture.wrap_v

        # Inherited Attributes
        oldDepthOffset = old_egg_texture.getDepthOffset()
        if oldDepthOffset:
            et.setDepthOffset(oldDepthOffset)

        oldDepthWrite = old_egg_texture.getDepthWriteMode()
        if oldDepthWrite:
            et.setDepthWriteMode(oldDepthWrite)

        oldDepthTest = old_egg_texture.getDepthTestMode()
        if oldDepthTest:
            et.setDepthTestMode(oldDepthTest)

        oldAlphaMode = old_egg_texture.getAlphaMode()
        if oldAlphaMode:
            et.setAlphaMode(oldAlphaMode)

        oldDrawOrder = old_egg_texture.getDrawOrder()
        if oldDrawOrder:
            et.setDrawOrder(oldDrawOrder)

        return et

    def _replace_poly_tref(self,
                           egg_polygon: EggPolygon, new_tex: EggTexture, tex_to_replace: EggTexture,
                           replace_by_name: bool = True) -> None:
        """
        Low level method for replacing EggTextures associated with an EggPolygon.

        :param bool replace_by_name: Renames TRefs to the name of the texture (excluding extension)
        """
        poly_textures = egg_polygon.getTextures()
        new_textures = list()
        for texture_ref in range(len(poly_textures)):
            if replace_by_name:
                replace_by_name = poly_textures[texture_ref].getFilename() == tex_to_replace.getFilename()
            if poly_textures[texture_ref] == tex_to_replace or replace_by_name:
                new_textures.append(new_tex)
            else:
                new_textures.append(poly_textures[texture_ref])
        egg_polygon.clearTexture()
        for tex in new_textures:
            egg_polygon.add_texture(tex)

    def do_tex_replace(self, egg: EggData, new_tex: EggTexture, old_tex: EggTexture) -> None:
        """
        Base method used for replacing texture instances in an egg file.

        Recursively replaces an EggTexture with another in a EggData instance.
        """

        def traverse_egg(egg, ctx):
            """
            Traverses down an egg tree and records data mapped to the ctx key.

            :param egg: Egg to traverse
            :type egg: EggData | EggGroup
            :param ctx: The original EggContext, required to keep things in order during recursion.
            :type ctx: EggContext
            """
            # we ask for ctx just to keep things in order
            for child in egg.getChildren():
                if isinstance(child, EggGroupNode):
                    traverse_egg(child, ctx)
                if isinstance(child, EggPolygon):
                    self._replace_poly_tref(child, new_tex, old_tex)

        traverse_egg(egg, self.egg_datas[egg])

    def repath_egg_texture(self, egg: EggData, egg_texture: EggTexture, filename: Filename) -> None:
        """
        Repaths an EggTexture while *also* renaming the corresponding TRefs

        Todo: Since filename can be a filepath, we should have a relative mode.

        :param EggData egg: base egg file
        :param EggTexture egg_texture: texture to repath
        :param Filename filename: new filename for egg texture
        """
        self.mark_dirty(egg)

        test_tref = "test_tref"
        ctx = self.egg_datas[egg]
        # gotta iterate through the texture set to find our particular EggTexture
        for egg_tex in ctx.egg_textures:
            if egg_tex != egg_texture:
                continue
            temp_tex = EggTexture(egg_texture)
            temp_tex.assign(self.rebase_egg_texture(test_tref, filename, egg_tex))
            self.do_tex_replace(egg, new_tex = temp_tex, old_tex = egg_tex)
            egg_tex.setFilename(filename)
        self.rename_trefs(egg)

    def get_tref(self, egg: EggData, egg_texture: EggTexture) -> str:
        """
        Gets the name of the tref for the given EggTexture

        Example:
            <Texture> texture1 { ... }
            <TRef> { texture1 }
        will return 'texture1'
        """
        ctx = self.egg_datas[egg]
        # Ya I know, looks ugly, but don't blame me! There's no way to get the TRef from the Egg API!
        return repr(
            ctx.egg_texture_collection.findFilename(egg_texture.getFilename())
        ).replace("EggTexture ", "", 1)

    def _replace_tref(self, egg: EggData, old_tex: EggTexture, new_tex: EggTexture) -> None:
        ctx = self.egg_datas[egg]
        self.do_tex_replace(egg, new_tex, old_tex)
        old_tex.assign(new_tex)
        self.mark_dirty(ctx)

    def rename_trefs(self, egg: EggData) -> None:
        """
        Rename texture references (trefs)

        Example: texture1 is a tref
        <Texture> texture1 { ... }
        <TRef> texture1
        """
        ctx = self.egg_datas[egg]
        for egg_tex in ctx.egg_textures:
            self.mark_dirty(ctx)
            egg_fn = egg_tex.getFilename().getBasenameWoExtension()
            new_tex = self.rebase_egg_texture(egg_fn, egg_tex.getFullpath(), egg_tex)
            self.do_tex_replace(egg, new_tex, egg_tex)
            egg_tex.assign(new_tex)
        # Guarantees that each texture in the collection has a unique TRef name
        # Hmm, maybe we shouldn't put it here just yet. This leads ot .ref1.png files getting exported.
        # ctx.egg_texture_collection.uniquifyTrefs()

    def rename_all_trefs(self) -> None:
        """
        Renames all texture references (trefs) registered with EggMan.

        Example: texture1 is a tref
        <Texture> texture1 { ... }
        <TRef> texture1
        """
        for egg_data in self.egg_datas.keys():
            self.rename_trefs(egg_data)

    def get_current_textures(self, egg: EggData) -> List[EggTexture]:
        # workaround attempt
        ctx = self.egg_datas[egg]
        egg_textures = []
        for texture in ctx.egg_textures:
            egg_textures.append(texture)
        return egg_textures

    def get_texture_filepaths(self, egg: EggData) -> List[Filename]:
        ctx = self.egg_datas[egg]
        # test = list(lambda texname: texname.getFilename() for texname in ctx.egg_textures)
        return [texname.getFilename() for texname in ctx.egg_textures]

    def get_texture_basenames(self, egg: EggData, include_extension: bool = True) -> List[str]:
        ctx = self.egg_datas[egg]
        # test = list(lambda texname: texname.getFilename() for texname in ctx.egg_textures)
        if include_extension:
            return [texname.getFilename().getBasename() for texname in ctx.egg_textures]
        return [texname.getFilename().getBasenameWoExtension() for texname in ctx.egg_textures]

    def get_texture_by_name(self, egg: EggData, texture_name: str) -> EggTexture:
        """
        Ensure that texture_name is the Basename (.getBasename()))
        """
        ctx = self.egg_datas[egg]
        for egg_texture in ctx.egg_textures:
            if texture_name in egg_texture.getFilename().getBasename():
                return egg_texture

    def sort_trefs(self, egg: EggData = None, sortby: str = ""):
        # TODO, make sortby enums, just have like
        # { TCSort.TRefs: sortByTref }
        pass

    # endregion

    """
    Texture Access Methods
    """

    # region
    def get_tex_info(self, egg_texture: EggTexture) -> str:
        """
        Returns the anisotropic filtering degree that has been specified for this texture,
        or 0 if nothing has been specified.

        1 = Off
        """
        return f"Anisotropic Degree: {egg_texture.anisotropic_degree}\n" \
               f"Alpha File Channel: {egg_texture.alpha_file_channel}"

    # endregion

    """
    Egg Vertex Management
    """

    # region

    @verify_integrity
    def get_point_data(self, egg_data, egg_node) -> Optional[OrderedSet[PointData]]:
        """
        [
            [NodeID, NodeTex]
            NodeID --> [ EggVertex: { u, v } ]
            NodeTex --> EggTexture
        ]
        """
        ctx: EggContext = self.egg_datas[egg_data]
        point_data = ctx.point_data.get(egg_node)
        if point_data:
            return point_data
        for point_node in ctx.point_data.keys():
            if egg_node.getName() == point_node.getName():
                point_data = ctx.point_data[point_node]
                return point_data
        return None

    # endregion

    """
    Egg External File Methods
    """

    # region
    def get_all_egg_filenames(self, prepend_dir=".", as_filename_object: bool = False) -> \
            Union[List[Filename], List[str]]:
        filenames = list()
        for egg_data in self.egg_datas.keys():
            if as_filename_object:
                filenames.append(Filename.fromOsSpecific(os.path.join(prepend_dir, self.get_egg_filename(egg_data))))
            else:
                filenames.append(os.path.join(prepend_dir, self.get_egg_filename(egg_data)))
        return filenames

    def get_egg_filename(self, egg: EggData) -> Filename:
        """
        Get the Filename attribute from the given EggData object.
        """
        ctx = self.egg_datas[egg]
        return ctx.filename

    def get_egg_by_filename(self, filename: str) -> EggData:
        """
        Search for a specific egg data entry given a filename

        :param str filename: Must include extension at the end.
        """
        if hasattr(filename, 'getBasename'):
            filename = filename.getBasename()
        return self._egg_name_2_egg_data.get(filename)

    # endregion

    """
    EggMan Helper Methods
    """

    # region

    def mark_dirty(self, egg: Union[EggData, EggContext]) -> None:
        if isinstance(egg, EggContext):
            egg.dirty = True
        else:
            self.egg_datas[egg].dirty = True

    def resolve_egg_textures(self, egg: EggData, want_auto_resolve: bool = True, try_names: bool = True,
                             try_absolute=False) -> None:
        """
        Attempts to resolve 'invalid' texture paths in the EggData.
        If a file was successfully resolved, the EggTexture will be rebuilt to match the working file path.

        :param bool want_auto_resolve: Attempts to automatically resolve the file by performing a series of checks.

        :param bool try_names: Try resolving the EggTexture by searching for a different filename.
            Ideal for circumstances where image files have altered names but are still relevant to the file.
            Only effective if want_auto_resolve is True.

        :param bool try_absolute: Allow a file to have an absolute file path if an entry can be found.
            It is most effective for EggTextures that are meant to be short-lived and not retained during export.
            Not recommended to use absolute file paths for general use.
            Only effective if want_auto_resolve is True.
        """

        def auto_resolve(tex_path: str):
            """
            :return: new filename for setFilename
            """
            tex_file = Path(tex_path).name
            if try_names:
                tex_file = self.NameResolver.try_different_names(tex_file)
            if try_absolute:
                possible_path = self.NameResolver.try_searching_paths(tex_file)
                if possible_path:
                    self.mark_dirty(ctx)
                    return possible_path
            for search_path in self.NameResolver.search_paths:
                new_tex_file = Filename.fromOsSpecific(os.path.join(search_path, tex_file))
                if not os.path.isfile(new_tex_file):
                    continue
                logging.info(f"Rebasing texture path for {tex_file} to {search_path}")
                tex_path = os.path.relpath(
                    new_tex_file, os.path.dirname(os.path.abspath(ctx.filename))
                ).replace(os.sep, '/')
                logging.debug(f"new tex path--> {tex_path} ({search_path}")
                self.mark_dirty(ctx)
                return tex_path
            return tex_path

        ctx = self.egg_datas[egg]

        for egg_texture in ctx.egg_textures:
            fixed_path = os.path.abspath(os.path.join(os.path.dirname(ctx.filename), egg_texture.getFullpath()))
            # TODO: ensure_relative function
            try:
                rel_tex_path = os.path.relpath(
                    fixed_path, os.path.dirname(os.path.abspath(ctx.filename))
                ).replace(os.sep, '/')
            except ValueError:
                # An exception can be thrown if the relative texture is on a different drive (ie: google drive)
                rel_tex_path = ""

            ensure_test = rel_tex_path in str(egg_texture.getFilename())

            # EDGE CASE: what if file is using absolute filepath and checks the os.path.isfile check?
            # we still don't want to use absolute filepaths unless explicitly asked to do so.
            if not (os.path.isfile(fixed_path) and not os.path.isfile(os.path.abspath(egg_texture.getFullpath()))):
                # if relative (good), this should give is an invalid path.
                logging.debug(f"(path){os.path.abspath(egg_texture.getFullpath())}")
                if want_auto_resolve:
                    tref = repr(
                        ctx.egg_texture_collection.findFilename(egg_texture.getFilename())
                    ).replace("EggTexture ", "", 1)
                    egg_texture.assign(
                        self.rebase_egg_texture(tref, auto_resolve(egg_texture.getFullpath()), egg_texture)
                    )
                    if not os.path.isfile(egg_texture.getFilename()):
                        logging.warning(
                            f"Still couldn't find a texture after trying to auto resolve {egg_texture.getFilename()}"
                        )
                else:
                    logging.warning(f"Couldn't find texture {egg_texture.getFilename()}")

            elif os.path.isfile(fixed_path) and not ensure_test:
                # I haven't encountered this case yet
                logging.warning("ensure_test returned false")

                tref = repr(
                    ctx.egg_texture_collection.findFilename(egg_texture.getFilename())
                ).replace("EggTexture ", "", 1)
                egg_texture.assign(
                    self.rebase_egg_texture(tref, auto_resolve(egg_texture.getFullpath()), egg_texture)
                )
            else:
                logging.info(f"Found texture {egg_texture.getFilename()}")
                logging.debug(f"(filepath){os.path.abspath(egg_texture.getFullpath())}")
                logging.debug(f"(fixedpath){fixed_path}")

    @verify_integrity
    def use_absolute_texpaths(self, egg: EggData):
        ctx = self.egg_datas[egg]
        for egg_texture in ctx.egg_textures:
            filename = egg_texture.getFilename()
            if not filename.isFullyQualified():
                possible_path = self.NameResolver.try_searching_paths(filename.toOsSpecific())
                if os.path.isfile(possible_path):
                    self.repath_egg_texture(egg, egg_texture, possible_path)
        pass

    def resolve_external_refs(self, egg: EggData):
        ctx = self.egg_datas[egg]
        for external_ref in ctx.egg_ext_file_refs:
            # TODO, can copy what was done w/ ensuring texture
            pass

    # endregion
    """
    General Maintenance Methods
    """

    # region

    def remove_texture_duplicates(self, egg: EggData = None):
        if not egg:
            for egg_data in self.egg_datas.keys():
                egg_data.collapseEquivalentTextures()
        else:
            egg.collapseEquivalentTextures()

    def remove_timestamps(self, egg: EggData = None) -> None:
        if not egg:
            for egg_data in self.egg_datas.keys():
                self.remove_timestamp(egg_data)
        else:
            self.remove_timestamp(egg)

    def remove_timestamp(self, egg: EggData = None) -> None:
        ctx = self.egg_datas[egg]
        ctx.egg_timestamp_old = egg.getEggTimestamp()
        egg.setEggTimestamp(1)
        self.mark_dirty(egg)

    def fix_broken_texpaths(self, egg: EggData = None, try_names: bool = True, try_absolute: bool = False) -> None:
        """
        Fixes broken texture paths but does not change the name of the TRef.

        :param bool try_absolute: Allow a file to have an absolute file path if an entry can be found.
            It is most effective for EggTextures that are meant to be short-lived and not retained during export.
        """
        if not egg:
            # ok we'll just fix all of the ones we've registered then
            for egg_data in self.egg_datas.keys():
                self.resolve_egg_textures(egg_data, try_names = try_names, try_absolute = try_absolute)
        else:
            self.resolve_egg_textures(egg, try_names = try_names, try_absolute = try_absolute)

    def remove_egg_materials(self, egg: EggData) -> None:
        ctx = self.egg_datas[egg]
        for material in ctx.egg_materials:
            material.clearAmb()
            material.clearBase()
            material.clearDiff()
            material.clearEmit()
            material.clearIor()
            material.clearLocal()
            material.clearMetallic()
            material.clearRoughness()
            material.clearShininess()
            material.clearSpec()

        egg.collapseEquivalentMaterials()
        ctx.egg_materials = set()
        self.mark_dirty(ctx)

    def remove_all_egg_materials(self) -> None:
        for egg in self.egg_datas.keys():
            ctx = self.egg_datas[egg]
            for material in ctx.egg_materials:
                material.clearAmb()
                material.clearBase()
                material.clearDiff()
                material.clearEmit()
                material.clearIor()
                material.clearLocal()
                material.clearMetallic()
                material.clearRoughness()
                material.clearShininess()
                material.clearSpec()

            egg.collapseEquivalentMaterials()
            ctx.egg_materials = set()
            self.mark_dirty(ctx)

    def purge_all_comments(self, egg: EggData = None) -> None:
        if not egg:
            for egg_data in self.egg_datas.keys():
                self.purge_comments(egg_data)
        else:
            self.purge_comments(egg)

    def purge_comments(self, egg: EggData) -> None:
        # We can probably actually put EggComments anywhere in the egg file, but people mostly
        # put them in the beginning of the egg file not in a nested group.
        for child in egg.getChildren():
            if isinstance(child, EggComment):
                # idk how to completely get rid of Comments rn
                child.setComment("")
                self.mark_dirty(egg)
                # < Comment> { dfsjkofjhksdf }

    # endregion

    """
    Write/Output Methods
    """

    # region
    def write_all_eggs(self, custom_suffix="", dryrun=False):
        """
        Writes egg files through the EggData writeEgg method.

        Not always guaranteed to output changes made to the egg file, and will export floating point values
        up to the number defined in your Config file.
        """
        for egg_data in self.egg_datas.keys():
            self.write_egg(egg_data, custom_suffix = custom_suffix, dryrun = dryrun)

    def write_egg(self, egg, filename: Filename = None, custom_suffix="", dryrun=False):
        """
        Writes egg files through the EggData writeEgg method.

        Not always guaranteed to output changes made to the egg file, and will export floating point values
        up to the number defined in your Config file.
        """
        if not filename:
            filename = egg.egg_filename
        filename = Filename(filename.getFullpath() + custom_suffix)
        ctx = self.egg_datas[egg]
        if ctx.dirty:
            if not dryrun:
                # If we put uniquifyTRefs here, it will not generate .tref.png files.
                ctx.egg_texture_collection.uniquifyTrefs()
                if not ctx.egg_save_timestamp:
                    self.remove_timestamp(egg)
                # We get a PermissionDenied error once in a while with models that are not scoped to the target env.
                if not egg.writeEgg(filename + custom_suffix):
                    logging.error(f"something went wrong when trying to write {egg.egg_filename}")
            else:
                print(egg)
        else:
            logging.debug(f"{egg.egg_filename} was not dirty, not writing anything")

    def write_all_eggs_manually(self, custom_suffix="", dryrun=False):
        """
        Exports all of the Egg files in EggMan manually. This will guarantee that something does get exported.
        By default, floating point values will be truncated to .4f
        """
        # I don't think this is going to cause any visual dislocation issues. The precision comes from
        # a floating point error nonetheless. We are also talking about a 0.0000xxxxxx difference.
        for egg_data in self.egg_datas.keys():
            self.write_egg_manually(egg_data, custom_suffix = custom_suffix, dryrun = dryrun)

    def write_egg_manually(self, egg, filename="", custom_suffix="", dryrun=False):
        """
        Don't know why this currently happens, but there are instances where trying to save the egg a la writeEgg
        doesn't work. This is the alternative manual approach, where we just write out a string.

        Floating point values will be truncated to .4f
        """
        if not filename:
            filename = egg.egg_filename
        filename = Filename(filename.getFullpath() + custom_suffix)
        ctx = self.egg_datas[egg]
        if ctx.dirty:
            if not dryrun:
                # If we put uniquifyTRefs here, it will not generate .tref.png files.
                ctx.egg_texture_collection.uniquifyTrefs()
                if not ctx.egg_save_timestamp:
                    self.remove_timestamp(egg)
                # We get a PermissionDenied error once in a while with models that are not scoped to the target env.
                try:
                    with open(filename, "w") as egg_file:
                        logging.info(f"trying to write {filename}")
                        egg_file.write(str(egg))
                except Exception as e:
                    print(f"Failed to save file ({e})")
            else:
                print(egg)
        else:
            pass
            # logging.debug(f"not rewriting {filename}")

    @staticmethod
    def rewrite_egg_manually(eggfile):
        """
        Open, read, and re-write an egg file.

        Since we are doing the manual approach, floating point values will be .4f by default.
        """
        if isinstance(eggfile, EggData):
            egg_data = eggfile
            filename = egg_data.getFilename()
        else:
            egg_data = EggData()
            egg_data.read(eggfile)
            filename = eggfile
        try:
            with open(filename, "w") as egg_file:
                egg_file.write(str(egg_data))
        except Exception as e:
            print(f"Failed to save file ({e})")

    # endregion


"""
Test module
"""

if __name__ == "__main__":
    import os

    file_list = []

    target_path = os.getcwd()
    for dirpath, _, filenames in os.walk(os.path.join(target_path)):
        for file in filenames:
            if file.endswith(".egg"):
                print(f"adding file {file}")
                file_list.append(os.path.abspath(os.path.join(dirpath, file)))

    eggman = EggMan(file_list)
