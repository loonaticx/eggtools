def bounding_box(points):
    """returns a list containing the bottom left and the top right
    points in the sequence
    Here, we use min and max four times over the collection of points
    """
    x, y = points
    bot_left_x = min(point for point in x)
    bot_left_y = min(point for point in y)
    top_right_x = max(point for point in x)
    top_right_y = max(point for point in y)

    return [(bot_left_x, bot_left_y), (top_right_x, top_right_y)]