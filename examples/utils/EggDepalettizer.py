from . import *

# test_egg defined in __init__

from eggtools.utils.EggDepalettizer import Depalettizer

# padding_u and padding_v should be between 0 and 1
depal = Depalettizer([test_egg], padding_u = 0.001, padding_v = 0.001, eggman = eggman)

depal.depalettize_all()

for eggdata in depal.eggman.egg_datas.keys():
    depal.eggman.write_egg_manually(eggdata, custom_suffix = "crop3.egg")
