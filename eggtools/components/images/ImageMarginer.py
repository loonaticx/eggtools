import numpy as np
import cv2 as cv

from PIL import Image, ImageDraw, ImageOps

from eggtools.components.images import ImageUtils
from eggtools.components.images.MarginMode import MarginMode, MarginType, SolidMargin, InpaintMargin, MarginTypes, \
    ClampMargin, RepeatMargin
from eggtools.components.points import PointUtils


class ImageMarginer:
    def __init__(self, source_image: Image, margin_type: MarginType):
        # MarginTypes.get(testMargin)()
        if not isinstance(margin_type, MarginType):
            # Maybe still a margin mode
            margin_type = MarginTypes.get(margin_type)()
        # get source image
        self.source_image = source_image
        self.margin_type = margin_type

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
        new_image_width = image_width + margin_x
        new_image_height = image_height + margin_y
        new_image = Image.new("RGBA", (new_image_width, new_image_height))
        c_image = source_image.copy()
        x_offset = (new_image_width - source_image.width) // 2
        y_offset = (new_image_height - image_height) // 2
        new_image.paste(c_image, (x_offset, y_offset))

        return new_image

    @staticmethod
    def make_margin_mask_from_alpha(image_to_mask) -> Image:
        r, g, b, a = image_to_mask.split()
        return ImageOps.invert(a.convert("L"))

    def create_margined_image(self, margin_x, margin_y) -> Image:
        # i need to do something about margin_type, it's not really good that is just a class var
        # especially if we're anticipatingon passing it around...
        margin_func = {
            # MarginMode.Inpaint: self.fill_inpaint,
            # MarginMode.Solid: self.fill_solid,
            SolidMargin: self.fill_solid,
            InpaintMargin: self.fill_inpaint,
            ClampMargin: self.fill_clamp,
            RepeatMargin: self.fill_repeat,

        }
        margin_op = margin_func.get(type(self.margin_type))
        if not margin_op:
            return

        op_kwargs = {}
        expanded_image = ImageMarginer.expand_image(self.source_image, margin_x, margin_y)
        margin_mask = ImageMarginer.make_margin_mask_from_alpha(expanded_image)
        op_kwargs["image"] = expanded_image
        # currently only used for one instance (inpaint)
        op_kwargs["image_mask"] = margin_mask
        return margin_op(**op_kwargs)

    """
    fill methods
    """

    def fill_clamp(self, image: Image, **kwargs):
        margin_type = self.margin_type
        if not isinstance(self.margin_type, ClampMargin):
            # throw warning here :|
            margin_type = ClampMargin()

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

    def fill_solid(self, image: Image, **kwargs):
        margin_type = self.margin_type
        if not isinstance(self.margin_type, SolidMargin):
            # throw a note that we're using default solid margin
            margin_type = SolidMargin()

        color = margin_type.color
        filled_image = Image.new("RGBA", image.size, color)

        # Composite the original image over the new solid color background
        new_image = Image.alpha_composite(filled_image, image)

        # Convert the result back to RGB if you don't need the alpha channel anymore
        new_image = new_image.convert("RGB")

        # mask = self.make_margin_mask_from_alpha(image)
        # new_image = mask.convert("RGBA")
        # r, g, b, a = image.split()
        # base_mask_image = Image.new("RGBA", image.size, "WHITE")
        # new_image = base_mask_image.paste(base_mask_image)
        # base_mask_image = Image.alpha_composite(base_mask_image, a)
        # base_mask_image = Image.alpha_composite(base_mask_image, image_to_mask.getchannel('A'))
        # mask = ImageOps.invert(image_to_mask.convert('La'))
        # base_mask_image.putalpha(ImageOps.invert(image.getchannel('A')))

        return new_image

    def fill_repeat(self, image: Image, **kwargs):
        margin_type = self.margin_type
        if not isinstance(self.margin_type, RepeatMargin):
            # throw warning here :|
            margin_type = RepeatMargin()

        image_width, image_height = image.size
        image_result = image.copy()

        # Trim out the transparency that was generated for our extended image
        image_cropped = ImageUtils.trim_transparency(image)
        cropped_width, cropped_height = image_cropped.size
        # We're going to take this image pattern and use it to fill in the transparent areas we've just created
        pattern_width, pattern_height = image_cropped.size

        # Note:
        # Something different about this is that we need to tile our pattern

        # pixel_height = 0
        pixel_width = 0

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

        # while pixel_width < image_width:
        #     pixel_height = 0
        #     while pixel_height < image_height:
        #         print(f"Iter ({pixel_width} - {pixel_height})")
        #         image_result.paste(image_cropped, (pixel_width, pixel_height, pattern_width, pixel_height +
        #         pattern_height))
        #         pixel_height += pattern_height
        #         image_result.paste(image_cropped, (pixel_width, pixel_height, pixel_width + pattern_width,
        #         pattern_height))
        #     pixel_width += pattern_width

        # while pixel_width < image_width:
        #     print(f"Iter {pixel_width}")
        #     image_result.paste(image_cropped, (pixel_width, 0, pixel_width + pattern_width, pattern_height))
        #     pixel_width += pattern_width

        return image_result

    def fill_inpaint(self, image: Image, image_mask: Image, **kwargs):
        margin_type = self.margin_type
        if not isinstance(self.margin_type, InpaintMargin):
            # throw warning here :|
            margin_type = InpaintMargin()

        # note: wouldbe good to throw a warning above a certain radii since it can get hella slow
        inpaint_radius = margin_type.radius
        inpaint_method = margin_type.method
        # higher radius = smoother
        # mask currently required but we can have it do it automatically based off transparency or something
        # ^ actually would be good for _a.rgb files
        # ensure there is already transparency
        # opencv uses bgr instead of rgb
        image = cv.cvtColor(np.array(image), cv.COLOR_RGB2BGR)
        # COLOR_RGB2GRAY

        # Color convert
        image_mask = np.array(image_mask)
        image_mask = image_mask[:, :].copy()

        mask = np.uint8(image_mask)
        new_image = cv.inpaint(image, mask, inpaint_radius, inpaint_method)
        # convert it to PIL
        new_image = cv.cvtColor(new_image, cv.COLOR_BGR2RGB)
        new_image = Image.fromarray(new_image)
        return new_image
