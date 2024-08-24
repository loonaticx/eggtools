import os

from panda3d.core import *

if not os.path.isfile('tests/models/test_grid_1.egg'):
    test_egg = Filename.fromOsSpecific('models/test_grid_1.egg')
else:
    test_egg = Filename.fromOsSpecific(os.path.join(os.getcwd(), 'tests/models/test_grid_1.egg'))

from eggtools.utils.EggDepalettizer import Depalettizer

depal = Depalettizer([test_egg])

eggdatas_prior = depal.eggman.egg_datas
for eggdata_prior in eggdatas_prior.keys():
    ctx_prior = depal.eggman.egg_datas[eggdata_prior]
    print("--- old ---")
    print(ctx_prior.egg_texture_collection.getTextures())
    print(ctx_prior.filename)
    print(ctx_prior.filename.getFullpath())
    print(ctx_prior.dirty)

depal.depalettize_all()

eggdatas_after = depal.eggman.egg_datas
for eggdata_after in eggdatas_after.keys():
    ctx_after = depal.eggman.egg_datas[eggdata_after]
    print("--- new ---")
    print(ctx_after.egg_texture_collection.getTextures())
    print(ctx_after.filename)
    print(ctx_after.filename.getFullpath())
    print(ctx_after.dirty)
    depal.eggman.write_egg_manually(eggdata_after, custom_suffix = "crop.egg")
