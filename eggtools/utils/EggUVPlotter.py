import matplotlib.pyplot as plt
import numpy as np
from panda3d.egg import EggNode

from eggtools.components.EggContext import EggContext
from eggtools.components.points.PointData import PointData, PointHelper


class MatplotPlotter:

    def __init__(self):
        plt.grid(True)
        ax = plt.gca()
        ax.set_xlim([0, 1])
        ax.set_ylim([0, 1])

    def open_plot(self, title=""):
        """
        NOTE: This will freeze your code until the plot window is closed. Recommended to run this last!
        """
        plt.title(title)
        plt.show()

    def plot_eggnode_textures(self, ctx: EggContext, egg_node: EggNode):
        point_texture_lookup = ctx.points_by_textures(egg_node)
        for point_texture in point_texture_lookup.keys():
            point_datas = point_texture_lookup[point_texture]
            # Aggregate all the points into one PointData
            point_data = PointHelper.unify_point_datas(point_datas)
            self.plot_uvs(point_data)

    def plot_uvs(self, point_data, color="black", i: int = 0):
        """
        If "i" is non-zero, all the UVs will be duplicated, shifted by "i", then merged back into the u/v list.
        """
        x_list = []
        y_list = []
        for u, v in point_data.egg_vertex_uvs.values():
            x_list.append(u)
            y_list.append(v)

        # if the count is an odd number we need to add one more to make it balance
        if len(x_list) % 2:
            x_list.append(x_list[-1])
            y_list.append(y_list[-1])

        # This will duplicate the U/V entries, shift them by one, and then merge back in with the original list.
        # This is so that we can have fully connected lines with the points.
        if i:
            x_list_dupe = x_list[:]
            shifted_list = x_list_dupe[-i:] + x_list_dupe[:-i]
            x_list = x_list_dupe + shifted_list
            y_list_dupe = y_list[:]
            shifted_list = y_list_dupe[-i:] + y_list_dupe[:-i]
            y_list = y_list_dupe + shifted_list

        x_list_np = np.array(x_list)
        y_list_np = np.array(y_list)

        xx = np.vstack([x_list_np[0::2], x_list_np[1::2]])
        yy = np.vstack([y_list_np[0::2], y_list_np[1::2]])

        plt.plot(xx, yy, '-o', c = color)
