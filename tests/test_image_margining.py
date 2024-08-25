import os

from panda3d.core import *

if not os.path.isfile('tests/maps/test_grid_1.png'):
    test_image_1 = Filename.fromOsSpecific('maps/test_grid_1.png')
else:
    test_image_1 = Filename.fromOsSpecific(os.path.join(os.getcwd(), 'tests/maps/test_grid_1.png'))

from eggtools.components.images.ImageMarginer import *
from PIL import Image

test_image_1 = Image.open(Filename.toOsSpecific(test_image_1))
print(test_image_1.size)
marginer = ImageMarginer(test_image_1, MarginMode.Inpaint)
image_margined = marginer.create_margined_image(2, 2)
# image_expanded = marginer.expand_image(test_image_1, 1024, 1024)
# image_expanded.show()
# margin_mask_test = marginer.make_margin_mask(test_image_1.size, image_expanded.size)

# margin_mask_test2 = marginer.make_margin_mask_from_alpha(image_expanded)
# margin_mask_test2.show()
# margin_mask_test.show()
# margin_image = marginer.create_margins(2, 2)
# margin_image.show()

# image_margined = marginer.fill_inpaint(image_expanded, margin_mask_test2)
image_margined.show()
