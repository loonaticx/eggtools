"""
To promote static typing
"""
from enum import IntEnum


class EggEnum(IntEnum):
    pass


# region Group Enums

from panda3d.egg import EggGroup as EG


class EggGroupEnum(EggEnum):
    pass


class BillboardType(EggGroupEnum):
    NoType = EG.BTNone
    Axis = EG.BTAxis
    PointCameraRelative = EG.BTPointCameraRelative
    PointWorldRelative = EG.BTPointWorldRelative


class BlendMode(EggGroupEnum):
    Unspecified = EG.BMUnspecified
    NoType = EG.BMNone
    Add = EG.BMAdd
    Subtract = EG.BMSubtract
    InvSubtract = EG.BMInvSubtract
    Min = EG.BMMin
    Max = EG.BMMax


class CollisionSolidType(EggGroupEnum):
    NoType = EG.CSTNone

    # The geometry represents an infinite plane.
    # The first polygon found in the group will define the plane.
    Plane = EG.CSTPlane

    # The geometry represents a single polygon.
    # The first polygon is used.
    Polygon = EG.CSTPolygon

    # The geometry represents a complex shape made up of several polygons.
    # This collision type should not be overused, as it provides the least optimization benefit.
    Polyset = EG.CSTPolyset

    # The geometry represents a sphere.
    # The vertices in the group are averaged together to determine the sphere’s center and radius.
    Sphere = EG.CSTSphere

    # The geometry represents a tube.
    # This is a cylinder-like shape with hemispherical endcaps;
    # it is sometimes called a capsule or a lozenge in other packages.
    # The smallest tube shape that will fit around the vertices is used.
    Tube = EG.CSTTube

    # The geometry represents an inverse sphere.
    # This is the same as Sphere, with the normal inverted, so that the solid part of an inverse sphere is the
    # entire world outside of it.
    # Note that an inverse sphere is in infinitely large solid with a finite hole cut into it.
    InvSphere = EG.CSTInvSphere

    # The geometry represents a box.
    # The smallest axis-alligned box that will fit around the vertices is used.
    Box = EG.CSTBox

    FloorMesh = EG.CSTFloorMesh


class CollisionFlagType(EggGroupEnum):
    NoType = EG.CFNone

    # Each group descended from this node that contains geometry will define a new collision object of the given type.
    # The event name, if any, will also be inherited from the top node and shared among all the collision objects.
    # This option will soon be the default; it is suggested that it is always specified for most compatibility.
    Descend = EG.CFDescend

    # Throws the name of the <Collide> entry, or the name of the surface if the <Collide> entry has no name,
    # as an event whenever an avatar strikes the solid.
    # This is the default if the <Collide> entry has a name.
    Event = EG.CFEvent

    # Don’t discard the visible geometry after using it to define a collision surface;
    # create both an invisible collision surface and the visible geometry.
    Keep = EG.CFKeep

    Solid = EG.CFSolid

    Center = EG.CFCenter

    Turnstile = EG.CFTurnstile

    # Stores a special effective normal with the collision solid that points up,
    # regardless of the actual shape or orientation of the solid.
    # This can be used to allow an avatar to stand on a sloping surface without having a tendency to slide downward.
    Level = EG.CFLevel

    # Rather than being a solid collision surface, the defined surface represents a boundary.
    # The name of the surface will be thrown as an event when an avatar crosses into the interior,
    # and name-out will be thrown when an avatar exits.
    Intangible = EG.CFIntangible


class DartType(EggGroupEnum):
    NoType = EG.DTNone
    Structured = EG.DTStructured
    Sync = EG.DTSync
    NoSync = EG.DTNosync
    Default = EG.DTDefault


class DynamicCoordinateType(EggGroupEnum):
    """
    The dynamic coordinate system (DCS) attribute is used to indicate nodes that should not be flattened out of the
    hierarchy during the conversion process.

    Unlike the Model attribute, DCS goes one step further and indicates that the node’s
    transform is important and should be preserved.

    Notouch is even stronger, and means not to do any flattening below the node at all.
    """
    Unspecified = EG.DCUnspecified  # 0
    NoType = EG.DCNone  # 16
    Local = EG.DCLocal  # 32
    Net = EG.DCNet  # 48
    NoTouch = EG.DCNoTouch  # 64
    Default = EG.DCDefault  # 80


class TriangulateType(EggGroupEnum):
    Polygon = EG.TPolygon
    Convex = EG.TConvex
    Composite = EG.TComposite
    Recurse = EG.TRecurse
    FlatShaded = EG.TFlatShaded


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

    # Normal alpha blending
    Blend = ERM.AMBlend

    # Alpha blending w/o depth write
    BlendNoOcclude = ERM.AMBlendNoOcclude

    Binary = ERM.AMBinary
    Dual = ERM.AMDual

    Multisample = ERM.AMMs
    MultisampleMask = ERM.AMMsMask

    Premultiplied = ERM.AMPremultiplied


class DepthTestMode(EggRenderEnum):
    Unspecified = ERM.DTMUnspecified
    Off = ERM.DTMOff
    On = ERM.DTMOn


class DepthWriteMode(EggRenderEnum):
    Unspecified = ERM.DWMUnspecified
    Off = ERM.DWMOff
    On = ERM.DWMOn


class RenderVisibilityMode(EggRenderEnum):
    Unspecified = ERM.VMUnspecified
    Hidden = ERM.VMHidden
    Normal = ERM.VMNormal

# endregion
