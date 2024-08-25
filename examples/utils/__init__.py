import os
from panda3d.core import Filename

from eggtools.EggMan import EggMan

if not os.path.isfile('tests/models/test_grid_1.egg'):
    test_egg = Filename.fromOsSpecific('models/test_grid_1.egg')
else:
    test_egg = Filename.fromOsSpecific(os.path.join(os.getcwd(), 'tests/models/test_grid_1.egg'))

eggman = EggMan(
    egg_filepaths = [test_egg],
    search_paths = [
        os.path.join(os.getcwd(), "tests/maps"),
    ],
)
egg = eggman.get_egg_by_filename(test_egg)
ctx = eggman.egg_datas[egg]
eggman.fix_broken_texpaths(egg, try_names = False, try_absolute = True)
