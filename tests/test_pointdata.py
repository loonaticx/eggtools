import os

from panda3d.core import *

from eggtools.EggMan import EggMan
from eggtools.components.EggContext import EggContext
from eggtools.components.points.PointData import PointHelper

if not os.path.isfile('tests/models/test_grid_1.egg'):
    test_egg = Filename.fromOsSpecific('models/test_grid_1.egg')
else:
    test_egg = Filename.fromOsSpecific(os.path.join(os.getcwd(), 'tests/models/test_grid_1.egg'))

eggman = EggMan([test_egg])

egg_data = eggman.get_egg_by_filename(test_egg)
ctx: EggContext = eggman.egg_datas[egg_data]

for node in ctx.egg_groups:
    # to test this
    ctx.points_by_textures(node)

    point_datas = eggman.get_point_data(egg_data, node)
    unify_test = PointHelper.unify_point_datas(point_datas)

    if point_datas:
        print(f"++ {node.getName()} has {len(point_datas)} entries")
    else:
        print(f"-- {node.getName()} does not have data --> {point_datas}")
        continue

    for point_data in point_datas:
        print(f"bbox - {point_data.get_bbox()}")
