"""When they have no other home, functions and classes are added here.
Eventually, they should be refactored to a more permanent home."""

import spyral
import math
import pygame

def _anchor_offset(anchor, width, height):
    """
    Given an `anchor` position (either a string or a 2-tuple position), finds
    the correct offset in a rectangle of size (`width`, `height`). If the
    `anchor` is a 2-tuple (or Vec2D), then it multiplies both components by -1.

    >>> anchor_offset("topleft", 100, 100)
    Vec2D(0,0)
    >>> anchor_offset("bottomright", 100, 100)
    Vec2D(100,100)
    >>> anchor_offset("center", 100, 100)
    Vec2D(50,50)
    >>> anchor_offset((10, 10), 100, 100)
    Vec2D(-10,-10)

    For a complete list of the anchor positions, see `Anchor Offset Lists`_.

    :param anchor: The (possibly named) position to offset by.
    :type anchor: string or :class:`Vec2D <spyral.Vec2D>`
    :param width: the width of the rectangle to offset in.
    :type width: int
    :param height: the height of the rectangle to offset in.
    :type height: int
    :rtype: :class:`Vec2D <spyral.Vec2D>`
    """
    w = width
    h = height
    a = anchor
    if a == 'topleft':
        offset = (0, 0)
    elif a == 'topright':
        offset = (w, 0)
    elif a == 'midtop':
        offset = (w / 2., 0)
    elif a == 'bottomleft':
        offset = (0, h)
    elif a == 'bottomright':
        offset = (w, h)
    elif a == 'midbottom':
        offset = (w / 2., h)
    elif a == 'midleft':
        offset = (0, h / 2.)
    elif a == 'midright':
        offset = (w, h / 2.)
    elif a == 'center':
        offset = (w / 2., h / 2.)
    else:
        offset = a * spyral.Vec2D(-1, -1)
    return spyral.Vec2D(offset)

@spyral.memoize._ImageMemoize
def scale_surface(s, target_size):
    """
    Internal method to scale a surface `s` by a float `factor`. Uses memoization
    to improve performance.

    :param target_size: The end size of the surface
    :type target_size: :class:`Vec2D <spyral.Vec2D>`
    :returns: A new surface, or the original (both pygame surfaces).
    """
    new_size = (int(math.ceil(target_size[0])),
                int(math.ceil(target_size[1])))
    if new_size == s.get_size():
        return s
    t = pygame.transform.smoothscale(s, new_size,
                                     spyral.image._new_spyral_surface(new_size))
    return t

class _Blit(object):
    """
    An internal class to represent a drawable `surface` with additional data
    (e.g. `rect` representing its location on screen, whether it's `static`).

    .. attribute::surface

        The internal Pygame source surface use to render this blit.

    .. attribute::position

        The current position of this Blit (:class:`Vec2D <spyral.Vec2D>`).

    .. attribute::area

        The portion of the surface to be drawn to the screen
        (:class:`Rect <spyral.Rect>`).

    .. attribute::layer

        The layer of this blit within the scene (`str).

    .. attribute::flags

        Any drawing flags (presently unused).

    .. attribute::static

        Whether this Blit is static.

    .. attribute::final_size

        The final size, set seperately to defer scaling.

    .. attribute::rect

        A rect representing the final position and size of this blit
        (:class:`Rect <spyral.Rect>`).

    """
    __slots__ = ['surface', 'position', 'rect', 'area', 'layer',
                 'flags', 'static', 'clipping', 'final_size']
    def __init__(self, surface, position, area, layer, flags, static):
        self.surface = surface   # pygame surface
        self.position = position # coordinates to draw at
        self.area = area         # portion of the surface to be drawn to screen
        self.layer = layer       # layer in scene
        self.flags = flags       # any drawing flags (currently unusued)
        self.static = static     # static blits haven't changed

        # Final size of the surface, the scaling will happen late
        self.final_size = spyral.Vec2D(surface.get_size())
        # Rect is only for finalized sprites
        self.rect = None

    def apply_scale(self, scale):
        """
        Applies the scaling factor to this blit.

        :param scale: The scaling factor
        :type scale: :class:`Vec2D <spyral.Vec2D>`
        """
        self.position = self.position * scale
        self.final_size = self.final_size * scale
        self.area = spyral.Rect(self.area.topleft * scale,
                                self.area.size * scale)

    def clip(self, rect):
        """
        Applies any necessary cropping to this blit

        :param rect: The new maximal size of the blit.
        :type rect: :class:`Rect <spyral.Rect>`
        """
        self.area = self.area.clip(spyral.Rect(rect))

    def finalize(self):
        """
        Performs all the final calculations for this blit and calculates the
        rect.
        """
        self.surface = scale_surface(self.surface, self.final_size)
        self.surface = self.surface.subsurface(self.area._to_pygame())
        self.rect = pygame.Rect((self.position[0], self.position[1]),
                                self.surface.get_size())

class _CollisionBox(object):
    """
    An internal class for managing the collidable area for a sprite or view.
    In many ways, this is a reduced form of a _Blit.

    .. attribute::position

        The current position of this CollisionBox
        (:class:`Vec2D <spyral.Vec2D>`).

    .. attribute::area

        The current offset and size of this CollisionBox.
        (:class:`Rect <spyral.Rect>`).

    .. attribute::rect

        A rect representing the final position and size of this CollisionBox.
        (:class:`Rect <spyral.Rect>`).

    """
    __slots__ = ['position', 'rect', 'area']
    def __init__(self, position, area):
        self.position = position
        self.area = area
        self.rect = None

    def apply_scale(self, scale):
        self.position = self.position * scale
        self.area = spyral.Rect(self.area.topleft * scale,
                                self.area.size * scale)

    def clip(self, rect):
        self.area = self.area.clip(spyral.Rect(rect))

    def finalize(self):
        self.rect = spyral.Rect(self.position, self.area.size)
        