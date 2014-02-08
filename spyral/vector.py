"""A vector is a class that behaves like a 2-tuple, but with convenient
methods."""

from __future__ import division
import math

class Vec2D(object):
    """
    Vec2D is a class that behaves like a 2-tuple, but with a number
    of convenient methods for vector calculation and manipulation.
    It can be created with two arguments for x,y, or by passing a
    2-tuple.

    In addition to the methods documented below, Vec2D supports
    the following:

    >>> from spyral import Vec2D
    >>> v1 = Vec2D(1,0)
    >>> v2 = Vec2D((0,1))    # Note 2-tuple argument!

    Tuple access, or x,y attribute access

    >>> v1.x
    1
    >>> v1.y
    0
    >>> v1[0]
    1
    >>> v1[1]
    0

    Addition, subtraction, and multiplication

    >>> v1 + v2
    Vec2D(1, 1)
    >>> v1 - v2
    Vec2D(1, -1)
    >>> 3 * v1
    Vec2D(3, 0)
    >>> (3, 4) * (v1+v2)
    Vec2D(3, 4)

    Compatibility with standard tuples

    >>> v1 + (1,1)
    Vec2D(2, 1)
    >>> (1,1) + v1
    Vec2D(2, 1)

    """
    __slots__ = ['x', 'y']

    def __init__(self, *args):
        if len(args) == 1:
            self.x, self.y = args[0]
        elif len(args) == 2:
            self.x, self.y = args[0], args[1]
        else:
            raise ValueError("Invalid Vec2D arguments")

    def __len__(self):
        return 2

    def __getitem__(self, key):
        if key == 0:
            return self.x
        if key == 1:
            return self.y
        raise IndexError("Invalid subscript %s" % (str(key)))

    def __repr__(self):
        return 'Vec2D(%s, %s)' % (str(self.x), str(self.y))

    def __eq__(self, o):
        try:
            return self.x == o[0] and self.y == o[1]
        except (IndexError, TypeError):
            return False

    def __ne__(self, o):
        return not self.__eq__(o)

    def __add__(self, o):
        try:
            return Vec2D(self.x + o[0], self.y + o[1])
        except (IndexError, TypeError):
            return NotImplemented

    __radd__ = __add__

    def __sub__(self, o):
        try:
            return Vec2D(self.x - o[0], self.y - o[1])
        except (IndexError, TypeError):
            print self, o
            return NotImplemented

    __isub__ = __sub__

    def __rsub__(self, o):
        try:
            return Vec2D(o[0] - self.x, o[1] - self.y)
        except (IndexError, TypeError):
            return NotImplemented

    def __mul__(self, o):
        try:
            return Vec2D(self.x * o[0], self.y * o[1])
        except (IndexError, TypeError):
            pass

        if isinstance(o, (int, long, float)):
            return Vec2D(self.x * o, self.y * o)

        return NotImplemented

    __rmul__ = __mul__
    __imul__ = __mul__

    def __div__(self, o):
        try:
            return Vec2D(self.x / o[0], self.y / o[1])
        except (IndexError, TypeError):
            pass

        if isinstance(o, (int, long, float)):
            return Vec2D(self.x / o, self.y / o)

    __truediv__ = __div__

    def __neg__(self):
        return (-self.x, -self.y)

    def __pos__(self):
        return self

    def get_length(self):
        """
        Return the length of this vector.

        :rtype: float
        """
        return math.sqrt(self.x * self.x + self.y * self.y)

    def get_length_squared(self):
        """
        Return the squared length of this vector.

        :rtype: int
        """
        return self.x * self.x + self.y * self.y

    def get_angle(self):
        """
        Return the angle this vector makes with the positive x axis.

        :rtype: float
        """
        return math.atan2(self.y, self.x)

    def perpendicular(self):
        """
        Returns a new :class:`Vec2D <spyral.Vec2D>` perpendicular to this one.

        :rtype: :class:`Vec2D <spyral.Vec2D>`
        """
        return Vec2D(-self.y, self.x)

    def dot(self, other):
        """
        Returns the `dot product <http://en.wikipedia.org/wiki/Dot_product>`_
        of this point with another.

        :param other: the other point
        :type other: 2-tuple or :class:`Vec2D <spyral.Vec2D>`
        :rtype: int
        """
        return self.x * other[0] + self.y * other[1]

    def distance(self, other):
        """
        Returns the distance from this :class:`Vec2D <spyral.Vec2D>` to the
        other point.

        :param other: the other point
        :type other: 2-tuple or :class:`Vec2D <spyral.Vec2D>`
        :rtype: float
        """
        return (other - self).get_length()

    def angle(self, other):
        """
        Returns the angle between this point and another point.

        :param other: the other point
        :type other: 2-tuple or :class:`Vec2D <spyral.Vec2D>`
        :rtype: float
        """
        x = self.x*other[1] - self.y*other[0]
        d = self.x*other[0] + self.y*other[1]
        return math.atan2(x, d)

    def projection(self, other):
        """
        Returns the
        `projection <http://en.wikipedia.org/wiki/Vector_projection>`_
        of this :class:`Vec2D <spyral.Vec2D>` onto another point.

        :param other: the other point
        :type other: 2-tuple or :class:`Vec2D <spyral.Vec2D>`
        :rtype: float
        """
        other = Vec2D(other)
        l2 = float(other.x*other.x + other.y*other.y)
        d = self.x*other.x + self.y*other.y
        return (d/l2)*other

    def rotated(self, angle, center=(0, 0)):
        """
        Returns a new vector from the old point rotated by `angle` radians about
        the optional `center`.

        :param angle: angle in radians.
        :type angle: float
        :param center: an optional center
        :type center: 2-tuple or :class:`Vec2D <spyral.Vec2D>`
        :rtype: :class:`Vec2D <spyral.Vec2D>`
        """
        p = self - center
        c = math.cos(angle)
        s = math.sin(angle)
        x = p.x*c - p.y*s
        y = p.x*s + p.y*c
        return Vec2D(x, y) + center

    def normalized(self):
        """
        Returns a new vector based on this one, normalized to length 1. That is,
        it keeps the same angle, but its length is now 1.

        :rtype: :class:`Vec2D <spyral.Vec2D>`
        """
        l = self.get_length()
        if self.get_length() == 0:
            return None
        return Vec2D(self.x/l, self.y/l)

    def floor(self):
        """
        Converts the components of this vector into ints, discarding anything
        past the decimal place.

        :returns: this :class:`Vec2D <spyral.Vec2D>`
        """
        self.x = int(self.x)
        self.y = int(self.y)
        return self

    def to_polar(self):
        """
        Returns `Vec2D(radius, theta)` for this vector, where `radius` is the
        length and `theta` is the angle.

        :rtype: :class:`Vec2D <spyral.Vec2D>`
        """
        return Vec2D(self.get_length(), self.get_angle())

    @staticmethod
    def from_polar(*args):
        """
        Takes in radius, theta or (radius, theta) and returns rectangular
        :class:`Vec2D <spyral.Vec2D>`.

        :rtype: :class:`Vec2D <spyral.Vec2D>`
        """
        v = Vec2D(*args)
        return Vec2D(v.x*math.cos(v.y), v.x*math.sin(v.y))

    def __hash__(self):
        return self.x + self.y
