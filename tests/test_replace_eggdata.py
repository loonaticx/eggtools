import os

from panda3d.core import Filename
from panda3d.egg import EggData

from eggtools.EggMan import EggMan

if not os.path.isfile('tests/coll_test.egg'):
    test_egg = Filename.fromOsSpecific('coll_test.egg')
else:
    test_egg = Filename.fromOsSpecific(os.path.join(os.getcwd(), 'tests/coll_test.egg'))

eggman = EggMan([test_egg])
egg = eggman.get_egg_by_filename("coll_test.egg")
ctx = eggman.egg_datas[egg]


def try_replace_with_self():
    eggman.replace_eggdata(egg, egg)


# Should return with an error
try:
    try_replace_with_self()
except Exception as e:
    print(e)

eggman.replace_eggdata(egg, EggData())

print(eggman.egg_datas)
