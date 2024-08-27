import logging

from PIL import Image, ImageChops
from panda3d.core import Filename
import os

from eggtools.components.points.PointData import PointData
from eggtools.utils.MarginCalculator import MarginCalculator


def crop_image_to_box(
        point_data: PointData, repeat_image=True,
        margin_u=0., margin_v=0.) -> Image:
    # i need to change filename_suffix to something that continuously increments
    egg_texture = point_data.egg_texture
    tex_node_name = egg_texture.getName()
    tex_filename = egg_texture.getFilename()

    image_filepath = Filename.toOsSpecific(tex_filename)
    if not os.path.isfile(image_filepath):
        logging.warning(f"Can't find image file {image_filepath} to work with! Skipping crop for TRef {tex_node_name}")
        return Filename()
    image_src = Image.open(image_filepath)
    src_width, src_height = image_src.size
    # Smallest res allowed is 1 pixel
    src_width = max(1, src_width)
    src_height = max(1, src_height)

    base_filename = point_data.egg_filename
    box_coords = point_data.get_bbox()
    xMin, yMin = box_coords[0]
    xMax, yMax = box_coords[1]

    # Cropped out area, we should keep note of this new image size.
    crop_x1 = max(1, src_width * xMin)  # Right
    crop_y1 = max(1, abs(src_height - (src_height * yMax)))  # Top
    crop_x2 = max(1, src_width * xMax)  # Left
    crop_y2 = max(1, abs(src_height - (src_height * yMin)))  # Bottom

    # nitpicky image edge cases
    if abs(crop_y2 - crop_y1) < 1:
        crop_y2 += crop_y1
    if abs(crop_x2 - crop_x1) < 1:
        crop_x2 += crop_x1

    crop_bounds = (
        crop_x1, crop_y1,
        crop_x2, crop_y2
    )

    try:
        # Sometimes we end up catching stragglers that aren't palettized, which make a fuss
        # Coordinate 'lower' is less than 'upper'
        # Note: This may be a cause of bad image outputs.
        image_cropped = image_src.crop(crop_bounds)
    except:
        return

    crop_width, crop_height = image_cropped.size
    # Smallest res allowed is 1 pixel
    crop_width = max(1, crop_width)
    crop_height = max(1, crop_height)

    # This is a little bit different than the ImageMarginer's repeat option.
    # This is an obligation for images that have a repeating texture, which need to conform to the new UVs.
    if repeat_image:
        if crop_height > src_height or crop_width > src_width:
            # The cropped image's width/height is larger than the source, we need to repeat it
            image_crop_copy = image_cropped.copy()
            pixel_height = 0
            pixel_width = 0

            while pixel_height < crop_height:
                image_crop_copy.paste(image_src, (0, pixel_height, src_width, pixel_height + src_height))
                pixel_height += src_height

            while pixel_width < crop_width:
                image_crop_copy.paste(image_src, (pixel_width, 0, pixel_width + src_width, src_height))
                pixel_width += src_width

            image_cropped = image_crop_copy

    return image_cropped


## we can migrate functions below somewhere else
def crop_images_to_box(point_datas, repeat_image=True):
    i = 0
    for point_data in point_datas:
        crop_image_to_box(point_data, str(i), repeat_image)
        i += 1


# idk if i want this in eggman..., do i?
# well, we kind of have to since pointdata requires eggdata.. and yeah
def crop_images_to_box_eggnodes(point_datas, repeat_image=True):
    i = 0
    for point_data in point_datas:
        crop_image_to_box(point_data, str(i), repeat_image)
        i += 1


#####

def trim_transparency(image: Image):
    bg = Image.new(image.mode, image.size)
    diff = ImageChops.difference(image, bg)
    bbox = diff.getbbox()
    if bbox:
        return image.crop(bbox)
