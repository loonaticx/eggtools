import os

from panda3d.core import *

from eggtools.EggMan import EggMan
from eggtools.components.EggContext import EggContext

from eggtools.components.images import ImageUtils

if not os.path.isfile('tests/test_tiles.egg'):
    test_egg = Filename.fromOsSpecific('test_tiles.egg')
else:
    test_egg = Filename.fromOsSpecific(os.path.join(os.getcwd(), 'tests/test_tiles.egg'))

eggman = EggMan([test_egg])

egg_data = eggman.get_egg_by_filename(test_egg)
ctx: EggContext = eggman.egg_datas[egg_data]

for node in ctx.egg_groups:
    point_datas = eggman.get_point_data(egg_data, node)
    if not point_datas:
        continue

    i = 0
    print(f"+++ point_data traversal for {node.getName()} +++")
    for point_data in point_datas:
        print(f"--- run {i} ---")
        cropped_file = ImageUtils.crop_image_to_box(point_data, str(i))
        bbox = point_data.get_bbox()
        xmin, ymin = bbox[0]
        xmax, ymax = bbox[1]
        print(f"bbox - {point_data.get_bbox()} | dim: ({xmax - xmin}, {ymax - ymin})")
        print(f"pointdata_filename - {point_data.egg_filename}")
        print(f"cropped_file - {cropped_file}")
        i += 1
    print()
