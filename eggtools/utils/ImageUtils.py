from PIL import Image
from panda3d.core import Filename
import os

from eggtools.components.points.PointData import PointData


def crop_image_to_box(point_data: PointData, filename_suffix="", repeat_image=True) -> Filename:
    # i need to change filename_suffix to something that continuously increments
    egg_texture = point_data.egg_texture
    tex_node_name = egg_texture.getName()
    tex_filename = egg_texture.getFilename()

    image_src = Image.open(Filename.toOsSpecific(tex_filename))
    src_width, src_height = image_src.size
    # Smallest res allowed is 1 pixel
    src_width = max(1, src_width)
    src_height = max(1, src_height)

    base_filename = point_data.egg_filename
    box_coords = point_data.get_bbox()
    xMin, yMin = box_coords[0]
    xMax, yMax = box_coords[1]

    image_kwargs = {}
    file_ext = tex_filename.getExtension().lower()

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

    image_cropped_name = tex_filename.getBasenameWoExtension() + f"_cropped_{tex_node_name}_{filename_suffix}"
    # At the very moment lets not try to merge node textures who share identical cropped textures
    image_cropped_filename = Filename.fromOsSpecific(
        os.path.join(
            base_filename.getDirname(),
            f"{image_cropped_name}.{file_ext}"

        )
    )
    crop_width, crop_height = image_cropped.size
    # Smallest res allowed is 1 pixel
    crop_width = max(1, crop_width)
    crop_height = max(1, crop_height)

    if file_ext == "png":
        image_kwargs['quality'] = 95  # intended
    elif file_ext == "jpg":
        # imageKwargs['subsampling'] = 0
        image_kwargs['quality'] = 'keep'

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

    image_cropped.save(
        Filename.toOsSpecific(image_cropped_filename),
        **image_kwargs
    )
    return image_cropped_filename


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
