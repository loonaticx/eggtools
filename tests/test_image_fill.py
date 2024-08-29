import os

from panda3d.core import *

from eggtools.components.images import ImageUtils
from eggtools.components.images.ImageFill import FillTypes

if not os.path.isfile('tests/maps/test_uv_1.png'):
    test_image_1 = Filename.fromOsSpecific('maps/test_uv_1.png')
else:
    test_image_1 = Filename.fromOsSpecific(os.path.join(os.getcwd(), 'tests/maps/test_uv_1.png'))

from eggtools.components.images.ImageMarginer import *
from PIL import Image

test_image_1 = Image.open(Filename.toOsSpecific(test_image_1))
print(test_image_1.size)

# margin = MarginTypes.get(MarginMode.Inpaint)(
#     radius = 2
# )

fill_type = FillTypes.get(FillMode.Inpaint)(
    radius = 2
)

marginer = ImageMarginer(fill_type)


def try_different_margins(sample_image, margin_x, margin_y):
    for fill_type in FillTypes.values():
        image = marginer.create_margined_image(sample_image, fill_type(), margin_x, margin_y)
        if not image:
            print(f"something went wrong with {fill_type} -> {image}")
            continue
        image.show()


try_different_margins(test_image_1, 1024, 1024)

# image_margined = marginer.create_margined_image(2048, 2048)
# image_expanded = marginer.expand_image(test_image_1, 690, 1024)
# repeat_image = marginer.fill_repeat(image_expanded)
# repeat_image = marginer.fill_clamp(image_expanded)


# image_margined.show()

# image_expanded.show()
# image_cropped = ImageUtils.trim_transparency(image_expanded)
# image_cropped.show()

# image_expanded.show()
# margin_mask_test = marginer.make_margin_mask(test_image_1.size, image_expanded.size)

# margin_mask_test2 = marginer.make_margin_mask_from_alpha(image_expanded)
# margin_mask_test2.show()
# margin_mask_test.show()
# margin_image = marginer.create_margins(2, 2)
# margin_image.show()

# image_margined = marginer.fill_inpaint(image_expanded, margin_mask_test2)
# image_margined.show()
