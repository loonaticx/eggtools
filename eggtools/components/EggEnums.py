"""
To promote static typing
"""
from enum import Enum


class EggEnum(Enum):
    pass


# region Group Enums

from panda3d.egg import EggGroup as EG


class EggGroupEnum(EggEnum):
    pass


class DartType(EggGroupEnum):
    NoType = EG.DTNone
    Structured = EG.DTStructured
    Sync = EG.DTSync
    NoSync = EG.DTNosync
    Default = EG.DTDefault


# endregion

# region Texture Enums

from panda3d.egg import EggTexture as ET


class EggTextureEnum(EggEnum):
    pass


class TextureWrapMode(EggTextureEnum):
    BorderColor = ET.WMBorderColor
    Clamp = ET.WMClamp
    Mirror = ET.WMMirror
    MirrorOnce = ET.WMMirrorOnce
    Repeat = ET.WMRepeat
    Unspecified = ET.WMUnspecified


# endregion

# region Render Mode Enums

from panda3d.egg import EggRenderMode as ERM


class EggRenderEnum(EggEnum):
    pass


class RenderAlphaMode(EggRenderEnum):
    Unspecified = ERM.AMUnspecified
    Off = ERM.AMOff
    On = ERM.AMOn

    Blend = ERM.AMBlend
    BlendNoOcclude = ERM.AMBlendNoOcclude

    Binary = ERM.AMBinary
    Dual = ERM.AMDual

    Multisample = ERM.AMMs
    MultisampleMask = ERM.AMMsMask

    Premultiplied = ERM.AMPremultiplied


class RenderVisibilityMode(EggRenderEnum):
    Unspecified = ERM.VMUnspecified
    Hidden = ERM.VMHidden
    Normal = ERM.VMNormal

# endregion
