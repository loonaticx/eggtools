from functools import cmp_to_key

from enum import Enum, auto


class PointEnum(Enum):
    U = auto()
    V = auto()


def bounding_box(points):
    """
    :returns: a list containing the bottom left and the top right points in the sequence

    ( [xMin, yMin], [xMax, yMax] )
    """
    x, y = points
    # Here, we use min and max four times over the collection of points
    bot_left_x = min(point for point in x)
    bot_left_y = min(point for point in y)
    top_right_x = max(point for point in x)
    top_right_y = max(point for point in y)

    return [(bot_left_x, bot_left_y), (top_right_x, top_right_y)]


def _cmp_points_u(coords_1, coords_2):
    u1, v1 = coords_1
    u2, v2 = coords_2
    if u1 > u2:
        return 1
    return -1


def _cmp_points_v(coords_1, coords_2):
    u1, v1 = coords_1
    u2, v2 = coords_2
    if v1 > v2:
        return 1
    return -1


sort_points_u = cmp_to_key(_cmp_points_u)
sort_points_v = cmp_to_key(_cmp_points_v)
