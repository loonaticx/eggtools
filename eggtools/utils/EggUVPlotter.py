import matplotlib.pyplot as plt
import numpy as np
from panda3d.egg import EggNode

from eggtools.components.EggContext import EggContext
from eggtools.components.points.PointData import PointData, PointHelper
from eggtools.components.points.PointUtils import PointEnum


class MatplotPlotter:

    def __init__(self):
        plt.grid(True)
        ax = plt.gca()
        ax.set_xlim([0, 1])
        ax.set_ylim([0, 1])
        self.line_style = 'solid'
        self.plot_type = "plot"  # or "scatter"

    def open_plot(self, title=""):
        """
        NOTE: This will freeze your code until the plot window is closed. Recommended to run this last!
        """
        plt.title(title)
        plt.show()

    def plot_eggnode_textures(self, ctx: EggContext, egg_nodes: list[EggNode] | EggNode, plot_kwargs=None, i: int = 0,
                              sortby: PointEnum | None = None):
        if plot_kwargs is None:
            plot_kwargs = {}
        if not isinstance(egg_nodes, list):
            egg_nodes = [egg_nodes]
        for egg_node in egg_nodes:
            fig, ax = plt.subplots()
            point_texture_lookup = ctx.points_by_textures(egg_node)
            for point_texture in point_texture_lookup.keys():
                point_datas = point_texture_lookup[point_texture]
                # Aggregate all the points into one PointData
                point_data = PointHelper.unify_point_datas(point_datas)
                # point_data.sort_test()
                # point_data=point_data
                self.plot_uvs(
                    ax = ax,
                    coordlist = point_data.get_coords(sort_by = sortby),
                    plot_kwargs = plot_kwargs,
                    i = i
                )

    def plot_uvs(self,
                 ax, coordlist: list = None,
                 point_data: PointData = None, plot_kwargs: dict = None,
                 i: int = 0,
                 plot_args: str = ""):
        """
        If "i" is non-zero, all the UVs will be duplicated, shifted by "i", then merged back into the u/v list.
        """
        if not plot_kwargs:
            plot_kwargs = dict()

        if point_data:
            coords = list(point_data.egg_vertex_uvs.values())
        elif coordlist:
            coords = coordlist
        else:
            return

        args = plot_args
        if self.line_style and "-" not in args:
            args += "-"

        args += "o"

        x_list = []
        y_list = []
        for u, v in coords:
            x_list.append(u)
            y_list.append(v)

        # if the count is an odd number we need to add one more to make it balance
        if len(x_list) % 2:
            x_list.append(x_list[-1])
            y_list.append(y_list[-1])

        # This will duplicate the U/V entries, shift them by one, and then merge back in with the original list.
        # This is so that we can have fully connected lines with the points.
        if i:
            # note: use np.roll instead
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


        # https://matplotlib.org/stable/gallery/lines_bars_and_markers/multicolored_line.html

        if plot_kwargs.get("c"):
            plot_kwargs["c"] = np.linspace(0, 1, len(x_list))

        if self.plot_type == "fill":
            plt.fill(xx, yy, args, **plot_kwargs)

        if self.plot_type == "plot":
            ax.plot(xx, yy, args, **plot_kwargs)

        elif self.plot_type == "scatter":
            plt.scatter(xx, yy, **plot_kwargs)

        else:
            pass
