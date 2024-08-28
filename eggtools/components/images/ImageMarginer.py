from PIL import Image

from eggtools.components.images import ImageUtils
from eggtools.components.images.ImageFill import FillMode, FillType, FillTypes, \
    ClampFill, RepeatFill, UnknownFill, SolidFill
from eggtools.components.points import PointUtils


class ImageMarginer:
    margin_x = 0.001
    margin_y = 0.001

    def _get_fill_type(self, fill_type):
        if isinstance(fill_type, FillMode):
            fill_type = fill_type.value()
        elif not isinstance(fill_type, FillType):
            # Maybe still a fill mode
            fill_type = FillTypes.get(fill_type, UnknownFill)()
        return fill_type

    def __init__(self, fill_type: FillMode | FillType | None = SolidFill):
        self.fill_type = self._get_fill_type(fill_type)

    @staticmethod
    def expand_image(source_image: Image, margin_x, margin_y) -> Image:
        """
        The newly created space is transparent. Use a fill method to fill it in.

        xxxxxxxxxx
        x--------x
        x--------x
        xxxxxxxxxx

        :returns: Expanded image in RGBA format

        """

        # generates a new image
        # https://www.geeksforgeeks.org/convert-opencv-image-to-pil-image-in-python/
        # https://stackoverflow.com/questions/14134892/convert-image-from-pil-to-opencv-format
        # https://www.geeksforgeeks.org/add-padding-to-the-image-with-python-pillow/
        image_width, image_height = source_image.size
        new_image_width = int(image_width + margin_x)
        new_image_height = int(image_height + margin_y)
        new_image = Image.new("RGBA", (new_image_width, new_image_height))
        c_image = source_image.copy()
        x_offset = (new_image_width - source_image.width) // 2
        y_offset = (new_image_height - image_height) // 2
        new_image.paste(c_image, (x_offset, y_offset))

        return new_image

    def create_margined_image(self, source_image: Image, fill_type: FillMode | FillType | None,
                              margin_x=None,  margin_y=None) -> Image:
        if not margin_x:
            margin_x = self.margin_x

        if not margin_y:
            margin_y = self.margin_y

        fill_type = self._get_fill_type(fill_type)
        if not fill_type:
            fill_type = self.fill_type

        expanded_image = ImageMarginer.expand_image(source_image, margin_x, margin_y)
        return fill_type.fill_image(image=expanded_image)
