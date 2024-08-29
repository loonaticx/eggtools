from . import *

# Plot tool
from eggtools.utils.EggUVPlotter import MatplotPlotter

plotter = MatplotPlotter()

from eggtools.utils.EggDepalettizer import Depalettizer

padding = 0.02
# padding_u and padding_v should be between 0 and 1
depal = Depalettizer([test_egg], padding_u = padding, padding_v = padding, eggman = eggman)

# depal.depalettize_all(clamp_uvs = False)

for eggdata in eggman.egg_datas.keys():
    ctx = eggman.egg_datas[eggdata]

# first element is the group node, followed by its children, which will also be plotted (will not do any grandchildren)
testnode = list(ctx.egg_groups)[0]
plotter.plot_type = "plot"

kwargs = {}
import numpy as np


# This gets all the points registered and ready but does not visually show the graph
plotter.plot_eggnode_textures(ctx, testnode, i = 1, plot_kwargs = kwargs)


# Need to run this to actually show the graph
# When the plot graph opens, it will halt any more code execution until after the plot window is closed.
plotter.open_plot(ctx.filename.getBasenameWoExtension())
