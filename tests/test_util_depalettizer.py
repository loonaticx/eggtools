import os

from panda3d.core import *

from eggtools.EggMan import EggMan

model_filename = "test_grid_1.egg"
base_dir = "tests"

if not os.path.isfile(f'{base_dir}/models/{model_filename}'):
    test_egg = Filename.fromOsSpecific(f'models/{model_filename}')
else:
    test_egg = Filename.fromOsSpecific(os.path.join(os.getcwd(), f'{base_dir}/models/{model_filename}'))

eggman = EggMan(
    egg_filepaths = [test_egg],
    search_paths = [
        os.path.join(os.getcwd(), f"{base_dir}/maps"),
    ],
)
egg = eggman.get_egg_by_filename(test_egg)
ctx = eggman.egg_datas[egg]
eggman.fix_broken_texpaths(egg, try_names = False, try_absolute = True)


from eggtools.utils.EggDepalettizer import Depalettizer

# 0.05 - [8, 8] | 0.001 - [0, 0] | 0.06 - [10, 10]
depal = Depalettizer([test_egg], padding_u=0.001, padding_v = 0.001, eggman=eggman)

verbose_logging = True

eggdatas_prior = depal.eggman.egg_datas
for eggdata_prior in eggdatas_prior.keys():
    ctx_prior = depal.eggman.egg_datas[eggdata_prior]
    if verbose_logging:
        print("--- old ---")
        print(ctx_prior.egg_texture_collection.getTextures())
        print(ctx_prior.filename)
        print(ctx_prior.filename.getFullpath())
        print(ctx_prior.dirty)

depal.depalettize_all()

eggdatas_after = depal.eggman.egg_datas
for eggdata_after in eggdatas_after.keys():
    ctx_after = depal.eggman.egg_datas[eggdata_after]
    if verbose_logging:
        print("--- new ---")
        print(ctx_after.egg_texture_collection.getTextures())
        print(ctx_after.filename)
        print(ctx_after.filename.getFullpath())
        print(ctx_after.dirty)
    depal.eggman.write_egg_manually(eggdata_after, custom_suffix = "crop3.egg")

