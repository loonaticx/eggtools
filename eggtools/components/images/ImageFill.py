from enum import Enum
import cv2
import cv2 as cv
import numpy as np
from PIL import Image

from eggtools.components.images import ImageUtils


class FillType:
    def __hash__(self):
        return hash(f"{__class__.__name__}")

    def __repr__(self):
        return __class__.__name__

    def __str__(self):
        return __class__.__name__

    def __init__(self):
        pass

    def fill_image(self, image: Image) -> Image:
        pass


class UnknownFill:
    """
    Not an actual FillType
    """

    def __init__(self, *args, **kwargs):
        super().__init__()

    def fill_image(self, image: Image) -> Image:
        return image


class InpaintFill(FillType):

    @property
    def methods(self):
        # API: https://docs.opencv.org/4.x/d7/d8b/group__photo__inpaint.html
        # Guide: https://docs.opencv.org/4.x/df/d3d/tutorial_py_inpainting.html
        return [
            cv.INPAINT_TELEA,
            cv.INPAINT_NS
        ]

    def __init__(self, radius: int = 0, method=cv2.INPAINT_TELEA):
        """
        :param int radius: The higher the radius, the smoother that the background fill will be.
            NOTE: Computation time significantly increases with the radius value
        """
        super().__init__()
        self.radius = radius
        self.method = method

    def fill_image(self, image: Image):
        # opencv uses bgr instead of rgb
        image_conv = cv.cvtColor(np.array(image), cv.COLOR_RGB2BGR)

        # Grab image mask based off the alphas of the image-- this will be the newly generated outer area.
        image_mask = ImageUtils.get_alpha_mask(image)

        # Color convert
        image_mask = np.array(image_mask)
        image_mask = image_mask[:, :].copy()

        mask = np.uint8(image_mask)
        new_image = cv.inpaint(image_conv, mask, self.radius, self.method)

        # convert it to PIL
        new_image = cv.cvtColor(new_image, cv.COLOR_BGR2RGB)
        new_image = Image.fromarray(new_image)
        return new_image


class SolidFill(FillType):

    def __init__(self, color: str = "BLACK"):
        super().__init__()
        self.color = color

    def fill_image(self, image: Image):
        color = self.color
        filled_image = Image.new("RGBA", image.size, color)

        # Composite the original image over the new solid color background
        new_image = Image.alpha_composite(filled_image, image)

        # Convert the result back to RGB if you don't need the alpha channel anymore
        new_image = new_image.convert("RGB")

        return new_image


class RepeatFill(FillType):
    def __init__(self):
        super().__init__()

    def fill_image(self, image: Image):
        image_width, image_height = image.size
        image_result = image.copy()

        # Trim out the transparency that was generated for our extended image
        image_cropped = ImageUtils.trim_transparency(image)
        cropped_width, cropped_height = image_cropped.size
        # We're going to take this image pattern and use it to fill in the transparent areas we've just created
        pattern_width, pattern_height = image_cropped.size

        # Calculate the starting position to center the image
        start_x = (image_width // 2) - (cropped_width // 2)
        start_y = (image_height // 2) - (cropped_height // 2)

        # Calculate the number of tiles in each direction
        x_tiles = (image_width // cropped_width) + 2
        y_tiles = (image_height // cropped_height) + 2

        # Tile the image centered on the canvas
        for i in range(-x_tiles // 2, x_tiles // 2 + 1):
            for j in range(-y_tiles // 2, y_tiles // 2 + 1):
                x = start_x + i * cropped_width
                y = start_y + j * cropped_height
                # Check if the image is within the canvas bounds
                if x < image_width and y < image_height and (x + cropped_width) > 0 and (y + cropped_height) > 0:
                    # Paste the image
                    image_result.paste(image_cropped, (x, y))

        return image_result


class ClampFill(FillType):
    def __init__(self):
        super().__init__()

    def fill_image(self, image: Image):
        # Canvas.
        canvas = image.copy()
        canvas_size = canvas.size
        canvas_width, canvas_height = canvas_size

        # Trim out the transparency that was generated for our extended image
        image_cropped = ImageUtils.trim_transparency(image)
        cropped_width, cropped_height = image_cropped.size
        original_width = cropped_width
        original_height = cropped_height
        original_image = image_cropped

        # Calculate the position to center the image
        center_x = (canvas_width - original_width) // 2
        center_y = (canvas_height - original_height) // 2

        # Paste the original image in the center of the canvas
        canvas.paste(original_image, (center_x, center_y))

        # Extend the edge pixels horizontally
        for x in range(center_x):
            left_column = original_image.crop((0, 0, 1, original_height))
            canvas.paste(left_column, (x, center_y))

        for x in range(center_x + original_width, canvas_width):
            right_column = original_image.crop((original_width - 1, 0, original_width, original_height))
            canvas.paste(right_column, (x, center_y))

        # Extend the edge pixels vertically
        for y in range(center_y):
            top_row = original_image.crop((0, 0, original_width, 1))
            canvas.paste(top_row, (center_x, y))

        for y in range(center_y + original_height, canvas_height):
            bottom_row = original_image.crop((0, original_height - 1, original_width, original_height))
            canvas.paste(bottom_row, (center_x, y))

        # dude i LOVE computer graphics SO MUCH I LOVE FILLING EDGES YEAH!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

        # Fill the corners with the corner pixels
        top_left_corner = original_image.crop((
            0, 0, 1, 1
        )).resize((
            center_x, center_y
        ))
        canvas.paste(
            top_left_corner, (0, 0)
        )

        top_right_corner = original_image.crop((
            original_width - 1, 0, original_width, 1
        )).resize((
            canvas_width - (center_x + original_width), center_y
        ))
        canvas.paste(
            top_right_corner, (center_x + original_width, 0)
        )

        bottom_left_corner = original_image.crop((
            0, original_height - 1, 1, original_height
        )).resize((
            center_x, canvas_height - (center_y + original_height)
        ))
        canvas.paste(
            bottom_left_corner, (0, center_y + original_height)
        )

        bottom_right_corner = original_image.crop((
            original_width - 1, original_height - 1, original_width, original_height
        )).resize((
            canvas_width - (center_x + original_width),
            canvas_height - (center_y + original_height)
        ))
        canvas.paste(
            bottom_right_corner,
            (center_x + original_width, center_y + original_height)
        )

        return canvas


"""
inner margin considerations:
PIL.ImageOps.pad
"""


class InnerFillType(FillType):
    # migrate this somewhere else sometime
    """
    Inner margins use image resampling
    """

    @property
    def resampling_modes(self):
        # https://pillow.readthedocs.io/en/stable/reference/Image.html#PIL.Image.Image.resize
        # https://pillow.readthedocs.io/en/stable/reference/Image.html#resampling-filters
        return [
            Image.Resampling.NEAREST,
            Image.Resampling.BOX,
            Image.Resampling.BILINEAR,
            Image.Resampling.HAMMING,
            Image.Resampling.BICUBIC,
            Image.Resampling.LANCZOS,

        ]

    def __init__(self, resample_mode: Image.Resampling = Image.Resampling.BICUBIC):
        super().__init__()
        self.resample_mode = resample_mode

    def fill_image(self, image: Image):
        pass


class FillMode(Enum):
    Unknown = UnknownFill
    Repeat = RepeatFill
    Inpaint = InpaintFill
    Solid = SolidFill
    Clamp = ClampFill


FillTypes = dict((fill_mode, fill_mode.value) for fill_mode in FillMode)
