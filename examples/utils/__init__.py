import os
from panda3d.core import Filename

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
