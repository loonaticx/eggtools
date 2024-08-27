from enum import Enum, auto
from dataclasses import dataclass

import cv2 as cv
from PIL import Image


class MarginType:
    # def __hash__(self):
    #     return hash(f"{__class__.__name__}")
    #
    # def __repr__(self):
    #     return __class__.__name__
    #
    # def __str__(self):
    #     return __class__.__name__

    def __init__(self):
        pass


class UnknownMargin:
    def __init__(self, *args, **kwargs):
        pass


@dataclass
class InpaintMargin(MarginType):

    @property
    def methods(self):
        # API: https://docs.opencv.org/4.x/d7/d8b/group__photo__inpaint.html
        # Guide: https://docs.opencv.org/4.x/df/d3d/tutorial_py_inpainting.html
        return [
            cv.INPAINT_TELEA,
            cv.INPAINT_NS
        ]

    # inpaint radius: higher takes longer
    radius: int = 0
    method = cv.INPAINT_TELEA


# can maybe make custom dataclasses for the magrins to configure certain values

@dataclass
class InnerMarginType(MarginType):
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

    resample = 0


"""
inner margin considerations:
PIL.ImageOps.pad

"""


@dataclass
class SolidMargin(MarginType):
    color: str = "BLACK"


@dataclass
class RepeatMargin(MarginType):
    pass


@dataclass
class ClampMargin(MarginType):
    # idk if this is worth the effort but
    # https://pillow.readthedocs.io/en/stable/reference/Image.html#PIL.Image.Image.getpixel
    pass


class MarginMode(Enum):
    Unknown = UnknownMargin
    Repeat = RepeatMargin
    Inpaint = InpaintMargin
    Solid = SolidMargin
    Clamp = ClampMargin


MarginTypes = dict((margin, margin.value) for margin in MarginMode)

if __name__ == "__main__":
    myMargin = MarginTypes.get(MarginMode.Unknown)(
        color = "White"
    )

    test = ClampMargin()
    print(test.__class__.__name__)


    def test_func_1():
        print(f"F!")


    def test_func_2():
        print("F2")


    testDict = {
        MarginMode.Solid: test_func_1,
        SolidMargin: test_func_2
    }

    testMargin = MarginMode.Solid
    print(testMargin)
    testMargin = MarginTypes.get(testMargin)()
    print(type(testMargin))
    print(testMargin)
    print(testDict.get(type(testMargin)))
    print(testDict)

    # testDict.get(testMargin)()

    # myMargin = MarginTypes[MarginMode.Unknown](color="White")
    # print(myMargin.color)

    # testMargin = MarginMode.Solid
    # testMargin = MarginTypes.get(testMargin)()
    # testMargin.color = "White"
    # testMarginTwo = MarginMode.Solid("Test")
