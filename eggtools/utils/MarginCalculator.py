class MarginCalculator:
    """
    common variables
    margin_u || margin_v: value between [0, 1]
    margin_u = float(margin_x / 100)

    margin_x || margin_y: outside area, value between 0 < x < image_width || image_height
    margin_x = image_width - used_width


    used_width || used_height: inside area
    used_width = image_width - margin_x

    image_width = margin_x + used_width

    """

    def __init__(self):
        pass

    @staticmethod
    def get_margined_by_ratio(image_width, image_height, margin_u: float, margin_v: float):
        """
        margin_u: 0-1
        margin_v: 0-1
        """
        used_width = image_width - abs(image_width * margin_u)
        margin_x = image_width - used_width
        used_height = image_height - abs(image_height * margin_v)
        margin_y = image_height - used_height
        return [[round(margin_x), round(margin_y)], [round(used_width), round(used_height)]]

    @staticmethod
    def get_margined_by_px(image_width, image_height, margin_x, margin_y):
        # can make something for shrinking vs expanding image
        used_width = image_width - margin_x
        used_height = image_height - margin_y
        pass

    @staticmethod
    def expand_image(image_width, image_height, new_image_width, new_image_height):
        # expands the image -- does not rescale the image but instead applies margining till the new size is reached
        # we will infer that the image width/height is equal to the used width/height
        used_width = image_width
        used_height = image_height

        # find margins
        margin_x = new_image_width - used_width
        margin_y = new_image_height - used_height

        # new image diffs
        image_size_gain = 100 * (new_image_width / image_width)

        return [[margin_x, margin_y], [image_size_gain]]
