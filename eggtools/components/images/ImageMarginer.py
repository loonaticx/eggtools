from enum import Enum, auto
import numpy as np
import cv2 as cv

from PIL import Image, ImageDraw, ImageOps


# can maybe make custom dataclasses for the magrins to configure certain values
class MarginMode(Enum):
    Repeat = auto()
    Inpaint = auto()
    Solid = auto()


class ImageMarginer:
    def __init__(self, source_image: Image, margin_mode: MarginMode = MarginMode.Inpaint):
        # get source image
        self.source_image = source_image
        self.margin_mode = margin_mode
        # todo: convert method args into class variables.. maybe?

    def create_margined_image(self, margin_x, margin_y) -> Image:
        margin_func = {
            MarginMode.Inpaint: self.fill_inpaint,
            MarginMode.Solid: self.fill_solid,
        }
        margin_op = margin_func.get(self.margin_mode)
        if not margin_op:
            return

        op_kwargs = {}
        expanded_image = self.expand_image(self.source_image, margin_x, margin_y)
        # margin_mask = self.make_margin_mask(self.source_image.size, expanded_image.size)
        margin_mask = self.make_margin_mask_from_alpha(expanded_image)
        op_kwargs["image"] = expanded_image
        op_kwargs["image_mask"] = margin_mask
        return margin_op(**op_kwargs)

    def expand_image(self, image: Image, margin_x, margin_y) -> Image:
        # generates a new image
        # https://www.geeksforgeeks.org/convert-opencv-image-to-pil-image-in-python/
        # https://stackoverflow.com/questions/14134892/convert-image-from-pil-to-opencv-format
        # https://www.geeksforgeeks.org/add-padding-to-the-image-with-python-pillow/
        image_width, image_height = image.size
        new_image_width = image_width + margin_x
        new_image_height = image_height + margin_y
        new_image = Image.new("RGBA", (new_image_width, new_image_height))
        # image.paste(new_image, (margin_x, margin_y, image_width - margin_x, image_height - margin_y))
        c_image = image.copy()
        x_offset = (new_image_width - image.width) // 2
        y_offset = (new_image_height - image_height) // 2
        new_image.paste(c_image, (x_offset, y_offset))
        # new_image.paste(c_image, (int(margin_x / 2), (int(margin_y / 2))))
        # new_image.paste(c_image, (margin_x, margin_y, image_width - margin_x, image_height - margin_y))

        return new_image

    def make_margin_mask_from_alpha(self, image_to_mask) -> Image:
        r, g, b, a = image_to_mask.split()
        return ImageOps.invert(a.convert("L"))

        base_mask_image = Image.new("RGBA", image_to_mask.size, "WHITE")
        # base_mask_image = Image.alpha_composite(base_mask_image, image_to_mask.getchannel('A'))
        # mask = ImageOps.invert(image_to_mask.convert('La'))
        base_mask_image.putalpha(ImageOps.invert(image_to_mask.getchannel('A')))
        base_mask_image = base_mask_image.convert("L")
        return base_mask_image

    def make_margin_mask(self, source_img_size, mask_img_size) -> Image:
        """
        different ways we can do this
        have a bounding box margin mask with a threshold value (("margins"))

        have a transparent background and then mask by what is and isnt transparent

        """
        # future arg: mask type (black-white, white-black, transparency, etc)
        source_width, source_height = source_img_size
        dest_width, dest_height = mask_img_size
        margin_x = dest_width - source_width
        margin_y = dest_height - source_height

        # make a mask
        # i dont want to use 1 bit pixels due to transparency
        new_image_mask = Image.new("L", (dest_width, dest_height), color = "white")
        used_bounds = ImageDraw.Draw(new_image_mask)
        # https://docs.opencv.org/4.x/df/d3d/tutorial_py_inpainting.html
        """
        [(x0, y0), (x1, y1)]
        or
        [x0, y0, x1, y1]
        upper left corner, lower right corner
        """
        print(f"xmargin - {margin_x}")
        print(f"dest_width- {dest_width}")
        print(f"source_width- {source_width}")
        print(f"source_width - abs(source_width - margin_x) - {source_width - abs(source_width - margin_x)}")
        used_bounds.rectangle(
            [int(margin_x / 2), int(margin_y / 2), int(dest_width - margin_x / 2), int(dest_height - margin_y / 2)],
            # [(margin_x, source_height-abs(source_height - margin_y)), (source_width- abs(source_width - margin_x),
            # margin_y)],
            fill = "Black"
        )
        return new_image_mask

    """
    fill methods
    """

    def fill_solid(self, image: Image, *args, **kwargs):
        # mask = self.make_margin_mask_from_alpha(image)
        # new_image = mask.convert("RGBA")
        # r, g, b, a = image.split()
        base_mask_image = Image.new("RGBA", image.size, "WHITE")
        new_image = base_mask_image.paste(base_mask_image)
        # base_mask_image = Image.alpha_composite(base_mask_image, a)
        # base_mask_image = Image.alpha_composite(base_mask_image, image_to_mask.getchannel('A'))
        # mask = ImageOps.invert(image_to_mask.convert('La'))
        # base_mask_image.putalpha(ImageOps.invert(image.getchannel('A')))
        return image

    def fill_inpaint(self, image: Image, image_mask: Image, inpaint_radius=0, inpaint_method=cv.INPAINT_TELEA, *args):
        # inpaint radius: higher takes longer
        # https://docs.opencv.org/4.x/d7/d8b/group__photo__inpaint.html
        # mask currentlly required but we can have it do it automatically based off transparency or something
        # ^ actually would be good for _a.rgb files
        # ensure there is already transparency
        # opencv uses bgr instead of rgb
        image = cv.cvtColor(np.array(image), cv.COLOR_RGB2BGR)
        # COLOR_RGB2GRAY

        # Color convert
        image_mask = np.array(image_mask)
        image_mask = image_mask[:, :].copy()
        # image_mask = cv.cvtColor(
        #     image_mask,
        #     cv.COLOR_RGB2GRAY
        # )

        mask = np.uint8(image_mask)
        new_image = cv.inpaint(image, mask, inpaint_radius, inpaint_method)
        # convert it to PIL
        new_image = cv.cvtColor(new_image, cv.COLOR_BGR2RGB)
        new_image = Image.fromarray(new_image)
        return new_image
