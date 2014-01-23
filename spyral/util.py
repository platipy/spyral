import spyral
import math
import pygame

def anchor_offset(anchor, width, height):
    """
    Given an `anchor` position (either a string or a 2-tuple position), finds the
    correct offset in a rectangle of size (`width`, `height`). If the `anchor` is
    a 2-tuple (or Vec2D), then it TODO: What does it do?.
    
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

def compute_layer(layers, layer):
    """
    Computes the numerical index of `layer` in `layers`, taking
    :above and :below specifiers into account.
    """
    # This should be optimized at some point.
    if type(layer) in (int, long, float):
        return layer
    try:
        s = layer.split(':')
        layer = s[0]
        offset = 0
        if len(s) > 1:
            mod = s[1]
            if mod == 'above':
                offset = 0.5
            if mod == 'below':
                offset = -0.5
        layer = layers.index(layer) + offset
    except ValueError:
        layer = len(layers)
    return layer

@spyral.memoize._ImageMemoize
def scale_surface(s, target_size):
    """
    Internal method to scale a surface `s` by a float `factor`. Uses memoization
    to improve performance.
    """
    new_size = (int(math.ceil(target_size[0])),
                int(math.ceil(target_size[1])))
    if new_size == s.get_size():
        return s
    t = pygame.transform.smoothscale(s,
                               new_size,
                               pygame.Surface(new_size, pygame.SRCALPHA).convert_alpha())
    return t

class _Blit(object):
    """
    An internal class to represent a drawable `surface` with additional data (e.g.
    `rect` representing its location on screen, whether it's `static`).
    """
    __slots__ = ['surface', 'position', 'rect', 'area', 'layer', 'flags', 'static', 'clipping', 'final_size']
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
        self.position = self.position * scale
        self.final_size = self.final_size * scale
        self.area = spyral.Rect(self.area.topleft * scale, self.area.size * scale)

    def clip(self, rect):
        self.area = self.area.clip(spyral.Rect(rect))

    def finalize(self):
        self.surface = scale_surface(self.surface, self.final_size)
        self.surface = self.surface.subsurface(self.area._to_pygame())
        self.rect = pygame.Rect((self.position[0], self.position[1]), self.surface.get_size())

class _CollisionBox(object):
    """
    An internal class to represent a drawable `surface` with additional data (e.g.
    `rect` representing its location on screen, whether it's `static`).
    """
    __slots__ = ['position', 'rect', 'area']
    def __init__(self, position, area):
        self.position = position # coordinates to draw at
        self.area = area         # portion of the surface to be drawn to screen
        # Rect is only for finalized sprites
        self.rect = None

    def apply_scale(self, scale):
        self.position = self.position * scale
        self.area = spyral.Rect(self.area.topleft * scale, self.area.size * scale)

    def clip(self, rect):
        self.area = self.area.clip(spyral.Rect(rect))

    def finalize(self):
        self.rect = spyral.Rect(self.position, self.area.size)
        