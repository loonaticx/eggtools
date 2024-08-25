from . import *

# Plot tool
from eggtools.utils.EggUVPlotter import MatplotPlotter

plotter = MatplotPlotter()

# first element is the group node, followed by its children, which will also be plotted (will not do any grandchildren)
testnode = list(ctx.egg_groups)[0]

# This gets all the points registered and ready but does not visually show the graph
plotter.plot_eggnode_textures(ctx, testnode)

# Need to run this to actually show the graph
# When the plot graph opens, it will halt any more code execution until after the plot window is closed.
plotter.open_plot(ctx.filename.getBasenameWoExtension())
