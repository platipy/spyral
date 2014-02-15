"""
Rects are a convenience class for managing rectangular regions.
"""

import pygame
import spyral

class Rect(object):
    """
    Rect represents a rectangle and provides some useful features. Rects can 
    be specified 3 ways in the constructor:

    #. Four numbers, ``x``, ``y``, ``width``, ``height``
    #. Two tuples, ``(x, y)`` and `(width, height)`
    #. Another rect, which is copied

    >>> rect1 = spyral.Rect(10, 10, 64, 64)               # Method 1
    >>> rect2 = spyral.Rect((10, 10), (64, 64))           # Method 2
    >>> rect3 = spyral.Rect(rect1.topleft, rect1.size)    # Method 2
    >>> rect4 = spyral.Rect(rect3)                        # Method 3

    Rects support all the usual :ref:`anchor points <ref.anchors>` as
    attributes, so you can both get ``rect.center`` and assign to it.
    Rects also support attributes of ``right``, ``left``, ``top``, ``bottom``,
    ``x``, and ``y``.

    >>> rect1.x
    10
    >>> rect1.centerx
    42.0
    >>> rect1.width
    64
    >>> rect1.topleft
    Vec2D(10, 10)
    >>> rect1.bottomright
    Vec2D(74, 74)
    >>> rect1.center
    Vec2D(42.0, 42.0)
    >>> rect1.size
    Vec2D(64, 64)

    """
    def __init__(self, *args):
        if len(args) == 1:
            r = args[0]
            self._x, self._y = r.x, r.y
            self._w, self._h = r.w, r.h
        elif len(args) == 2:
            self._x, self._y = args[0]
            self._w, self._h = args[1]
        elif len(args) == 4:
            self.left, self.top, self.width, self.height = args
        else:
            raise ValueError("You done goofed.")

    def __getattr__(self, name):
        v = spyral.Vec2D
        if name == "right":
            return self._x + self._w
        if name == "left" or name == "x":
            return self._x
        if name == "top" or name == "y":
            return self._y
        if name == "bottom":
            return self._y + self._h
        if name == "topright":
            return v(self._x + self._w, self._y)
        if name == "bottomleft":
            return v(self._x, self._y + self._h)
        if name == "topleft" or name == "pos":
            return v(self._x, self._y)
        if name == "bottomright":
            return v(self._x + self._w, self._y + self._h)
        if name == "centerx":
            return self._x + self._w / 2.
        if name == "centery":
            return self._y + self._h / 2.
        if name == "center":
            return v(self._x + self._w / 2., self._y + self._h / 2.)
        if name == "midleft":
            return v(self._x, self._y + self._h / 2.)
        if name == "midright":
            return v(self._x + self._w, self._y + self._h / 2.)
        if name == "midtop":
            return v(self._x + self._w / 2., self._y)
        if name == "midbottom":
            return v(self._x + self._w / 2., self._y + self._h)
        if name == "size":
            return v(self._w, self._h)
        if name == "width" or name == "w":
            return self._w
        if name == "height" or name == "h":
            return self._h

        raise AttributeError("type object 'rect' "
                             "has no attribute '%s'" % name)

    def __setattr__(self, name, val):
        # This could use _a lot_ more error checking
        if name[0] == "_":
            self.__dict__[name] = int(val)
            return
        if name == "right":
            self._x = val - self._w
        elif name == "left":
            self._x = val
        elif name == "top":
            self._y = val
        elif name == "bottom":
            self._y = val - self._h
        elif name == "topleft" or name == "pos":
            self._x, self._y = val
        elif name == "topright":
            self._x = val[0] - self._w
            self._y = val[1]
        elif name == "bottomleft":
            self._x = val[0]
            self._y = val[1] - self._h
        elif name == "bottomright":
            self._x = val[0] - self._w
            self._y = val[0] - self._h
        elif name == "width" or name == "w":
            self._w = val
        elif name == "height" or name == "h":
            self._h = val
        elif name == "size":
            self._w, self._h = val
        elif name == "centerx":
            self._x = val - self._w / 2.
        elif name == "centery":
            self._y = val - self._h / 2.
        elif name == "center":
            self._x = val[0] - self._w / 2.
            self._y = val[1] - self._h / 2.
        elif name == "midtop":
            self._x = val[0] - self._w / 2.
            self._y = val[1]
        elif name == "midleft":
            self._x = val[0]
            self._y = val[1] - self._h / 2.
        elif name == "midbottom":
            self._x = val[0] - self._w / 2.
            self._y = val[1] - self._h
        elif name == "midright":
            self._x = val[0] - self._w
            self._y = val[1] - self._h / 2.
        else:
            raise AttributeError("You done goofed!")

    def copy(self):
        """
        Returns a copy of this rect

        :returns: A new :class:`Rect <spyral.Rect>`
        """
        return Rect(self._x, self._y, self._w, self._h)

    def move(self, x, y):
        """
        Returns a copy of this rect offset by *x* and *y*.

        :param float x: The horizontal offset.
        :param float y: The vertical offset.
        :returns: A new :class:`Rect <spyral.Rect>`
        """
        return Rect(x, y, self._w, self._h)

    def move_ip(self, x, y):
        """
        Moves this rect by *x* and *y*.

        :param float x: The horizontal offset.
        :param float y: The vertical offset.
        """
        self._x, self._y = self._x + x, self._y + y

    def inflate(self, width, height):
        """
        Returns a copy of this rect inflated by *width* and *height*.

        :param float width: The amount to add horizontally.
        :param float height: The amount to add vertically.
        :returns: A new :class:`Rect <spyral.Rect>`
        """
        c = self.center
        n = self.copy()
        n.size = (self._w + width, self._h + height)
        n.center = c
        return n

    def inflate_ip(self, width, height):
        """
        Inflates this rect by *width*, *height*.

        :param float width: The amount to add horizontally.
        :param float height: The amount to add vertically.
        """
        c = self.center
        self.size = (self._w + width, self._h + height)
        self.center = c

    def union(self, other):
        """
        Returns a new rect which represents the union of this rect
        with other -- in other words, a new rect is created that can fit both
        original rects.

        :param other: The other Rect.
        :type other: :class:`Rect <spyral.Rect>`
        :returns: A new :class:`Rect <spyral.Rect>`
        """
        top = min(self.top, other.top)
        left = min(self.left, other.left)
        bottom = max(self.bottom, other.bottom)
        right = max(self.right, other.right)
        return Rect((left, top), (right - left, bottom - top))

    def union_ip(self, other):
        """
        Modifies this rect to be the union of it and the other -- in other
        words, this rect will expand to include the other rect.

        :param other: The other Rect.
        :type other: :class:`Rect <spyral.Rect>`
        """
        top = min(self.top, other.top)
        left = min(self.left, other.left)
        bottom = max(self.bottom, other.bottom)
        right = max(self.right, other.right)
        self.top, self.left = top, left
        self.bottom, self.right = bottom, right

    # @test: Rect(10,10,50,50).clip(Rect(0,0,20,20)) -> Rect(10,10,10,10)
    def clip(self, other):
        """
        Returns a Rect which is cropped to be completely inside of other.
        If the other does not overlap with this rect, a rect of size 0 is
        returned.

        :param other: The other Rect.
        :type other: :class:`Rect <spyral.Rect>`
        :returns: A new :class:`Rect <spyral.Rect>`
        """
        B = other
        A = self
        try:
            B._x
        except TypeError:
            B = Rect(B)

        if A._x >= B._x and A._x < (B._x + B._w):
            x = A._x
        elif B._x >= A._x and B._x < (A._x + A._w):
            x = B._x
        else:
            return Rect(A._x, A._y, 0, 0)

        if ((A._x + A._w) > B._x) and ((A._x + A._w) <= (B._x + B._w)):
            w = A._x + A._w - x
        elif ((B._x + B._w) > A._x) and ((B._x + B._w) <= (A._x + A._w)):
            w = B._x + B._w - x
        else:
            return Rect(A._x, A._y, 0, 0)

        if A._y >= B._y and A._y < (B._y + B._h):
            y = A._y
        elif B._y >= A._y and B._y < (A._y + A._h):
            y = B._y
        else:
            return Rect(A._x, A._y, 0, 0)

        if ((A._y + A._h) > B._y) and ((A._y + A._h) <= (B._y + B._h)):
            h = A._y + A._h - y
        elif ((B._y + B._h) > A._y) and ((B._y + B._h) <= (A._y + A._h)):
            h = B._y + B._h - y
        else:
            return Rect(A._x, A._y, 0, 0)

        return Rect(x, y, w, h)

    def clip_ip(self, other):
        """
        Modifies this rect to be cropped completely inside of other.
        If the other does not overlap with this rect, this rect will have a size
        of 0.

        :param other: The other Rect.
        :type other: :class:`Rect <spyral.Rect>`
        """
        new_rect = self.clip(other)
        self.topleft, self.size = new_rect.topleft, new_rect.size

    def contains(self, other):
        """
        Returns `True` if the other rect is contained inside this rect.

        :param other: The other Rect.
        :type other: :class:`Rect <spyral.Rect>`
        :returns: A `bool` indicating whether this rect is contained within
                  another.
        """
        return (other.collide_point(self.topleft) and
                other.collide_point(self.bottomright))

    def collide_rect(self, other):
        """
        Returns `True` if this rect collides with the other rect.

        :param other: The other Rect.
        :type other: :class:`Rect <spyral.Rect>`
        :returns: A `bool` indicating whether this rect is contained within
                  another.
        """
        return (self.clip(other).size != (0, 0) or
                other.clip(self).size != (0, 0))

    def collide_point(self, point):
        """
        :param point: The point.
        :type point: :class:`Vec2D <spyral.Vec2D>`
        :returns: A `bool` indicating whether the point is contained within this
                  rect.
        """
        # This could probably be optimized as well
        return point[0] > self.left and point[0] < self.right and \
            point[1] > self.top and point[1] < self.bottom

    def _to_pygame(self):
        """
        Internal method for creating a Pygame compatible rect from this rect.

        :returns: A :class:`pygame.Rect`
        """
        return pygame.Rect(((self.left, self.top), (self.width, self.height)))

    def __str__(self):
        return ''.join(['<rect(',
                        str(self._x),
                        ',',
                        str(self._y),
                        ',',
                        str(self._w),
                        ',',
                        str(self._h),
                        ')>'])

    def __repr__(self):
        return self.__str__()
