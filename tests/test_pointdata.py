import os

from panda3d.core import *

from eggtools.EggMan import EggMan
from eggtools.components.EggContext import EggContext

if not os.path.isfile('tests/test_tiles.egg'):
    test_egg = Filename.fromOsSpecific('test_tiles.egg')
else:
    test_egg = Filename.fromOsSpecific(os.path.join(os.getcwd(), 'tests/test_tiles.egg'))

eggman = EggMan([test_egg])

egg_data = eggman.get_egg_by_filename(test_egg)
ctx: EggContext = eggman.egg_datas[egg_data]

for node in ctx.egg_groups:
    point_datas = eggman.get_point_data(egg_data, node)
    if point_datas:
        print(f"++ {node.getName()} has {len(point_datas)} entries")
    else:
        print(f"-- {node.getName()} does not have data --> {point_datas}")
        continue

    for point_data in point_datas:
        print(f"bbox - {point_data.get_bbox()}")
