"""A module for manipulating Images, which are specially wrapped Pygame
surfaces.
"""

import pygame
import spyral
import copy

def _new_spyral_surface(size):
    """
    Internal method for creating a new Spyral-compliant Pygame surface.
    """
    return pygame.Surface((int(size[0]),
                           int(size[1])),
                          pygame.SRCALPHA, 32).convert_alpha()

def from_sequence(images, orientation="right", padding=0):
    """
    A function that returns a new Image from a list of images by
    placing them next to each other.

    :param images: A list of images to lay out.
    :type images: List of :class:`Image <spyral.Image>`
    :param str orientation: Either 'left', 'right', 'above', 'below', or
                            'square' (square images will be placed in a grid
                            shape, like a chess board).
    :param padding: The padding between each image. Can be specified as a
                    scalar number (for constant padding between all images)
                    or a list (for different paddings between each image).
    :type padding: int or a list of ints.
    :returns: A new :class:`Image <spyral.Image>`
    """
    if orientation == 'square':
        length = int(math.ceil(math.sqrt(len(images))))
        max_height = 0
        for index, image in enumerate(images):
            if index % length == 0:
                x = 0
                y += max_height
                max_height = 0
            else:
                x += image.width
                max_height = max(max_height, image.height)
            sequence.append((image, (x, y)))
    else:
        if orientation in ('left', 'right'):
            selector = spyral.Vec2D(1, 0)
        else:
            selector = spyral.Vec2D(0, 1)

        if orientation in ('left', 'above'):
            reversed(images)

        if type(padding) in (float, int, long):
            padding = [padding] * len(images)
        else:
            padding = list(padding)
            padding.append(0)
        base = spyral.Vec2D(0, 0)
        sequence = []
        for image, padding in zip(images, padding):
            sequence.append((image, base))
            base = base + selector * (image.size + (padding, padding))
    return from_conglomerate(sequence)

def from_conglomerate(sequence):
    """
    A function that generates a new image from a sequence of
    (image, position) pairs. These images will be placed onto a singe image
    large enough to hold all of them. More explicit and less convenient than
    :func:`from_seqeuence <spyral.image.from_sequence>`.

    :param sequence: A list of (image, position) pairs, where the positions
                     are :class:`Vec2D <spyral.Vec2D>` s.
    :type sequence: List of image, position pairs.
    :returns: A new :class:`Image <spyral.Image>`
    """
    width, height = 0, 0
    for image, (x, y) in sequence:
        width = max(width, x+image.width)
        height = max(height, y+image.height)
    new = Image(size=(width, height))
    for image, (x, y) in sequence:
        new.draw_image(image, (x, y))
    return new

def render_nine_slice(image, size):
    """
    Creates a new image by dividing the given image into a 3x3 grid, and stretching
    the sides and center while leaving the corners the same size. This is ideal
    for buttons and other rectangular shapes.

    :param image: The image to stretch.
    :type image: :class:`Image <spyral.Image>`
    :param size: The new (width, height) of this image.
    :type size: :class:`Vec2D <spyral.Vec2D>`
    :returns: A new :class:`Image <spyral.Image>` similar to the old one.
    """
    bs = spyral.Vec2D(size)
    bw = size[0]
    bh = size[1]
    ps = image.size / 3
    pw = int(ps[0])
    ph = int(ps[1])
    surf = image._surf
    # Hack: If we don't make it one px large things get cut
    image = spyral.Image(size=bs + (1, 1))
    s = image._surf
    # should probably fix the math instead, but it works for now

    topleft = surf.subsurface(pygame.Rect((0, 0), ps))
    left = surf.subsurface(pygame.Rect((0, ph), ps))
    bottomleft = surf.subsurface(pygame.Rect((0, 2*ph), ps))
    top = surf.subsurface(pygame.Rect((pw, 0), ps))
    mid = surf.subsurface(pygame.Rect((pw, ph), ps))
    bottom = surf.subsurface(pygame.Rect((pw, 2*ph), ps))
    topright = surf.subsurface(pygame.Rect((2*pw, 0), ps))
    right = surf.subsurface(pygame.Rect((2*pw, ph), ps))
    bottomright = surf.subsurface(pygame.Rect((2*pw, 2*ph), ps))

    # corners
    s.blit(topleft, (0, 0))
    s.blit(topright, (bw - pw, 0))
    s.blit(bottomleft, (0, bh - ph))
    s.blit(bottomright, bs - ps)

    # left and right border
    for y in range(ph, bh - ph - ph, ph):
        s.blit(left, (0, y))
        s.blit(right, (bw - pw, y))
    s.blit(left, (0, bh - ph - ph))
    s.blit(right, (bw - pw, bh - ph - ph))
    # top and bottom border
    for x in range(pw, bw - pw - pw, pw):
        s.blit(top, (x, 0))
        s.blit(bottom, (x, bh - ph))
    s.blit(top, (bw - pw - pw, 0))
    s.blit(bottom, (bw - pw - pw, bh - ph))

    # center
    for x in range(pw, bw - pw - pw, pw):
        for y in range(ph, bh - ph - ph, ph):
            s.blit(mid, (x, y))

    for x in range(pw, bw - pw - pw, pw):
        s.blit(mid, (x, bh - ph - ph))
    for y in range(ph, bh - ph - ph, ph):
        s.blit(mid, (bw - pw - pw, y))
    s.blit(mid, (bw - pw - pw, bh - ph - ph))
    return image

class Image(object):
    """
    The image is the basic drawable item in spyral. They can be created
    either by loading from common file formats, or by creating a new
    image and using some of the draw methods. Images are not drawn on
    their own, they are placed as the *image* attribute on Sprites to
    be drawn.

    Almost all of the methods of an Image instance return the Image itself,
    enabling commands to be chained in a
    `fluent interface <http://en.wikipedia.org/wiki/Fluent_interface>`_.

    :param size: If size is passed, creates a new blank image of that size to
                 draw on. If you do not specify a size, you *must* pass in a
                 filename.
    :type size: :class:`Vec2D <spyral.Vec2D>`
    :param str filename:  If filename is set, the file with that name is loaded.
                          The appendix has a list of the 
                          :ref:`valid image formats<ref.image_formats>`. If you do
                          not specify a filename, you *must* pass in a size.

    """

    def __init__(self, filename=None, size=None):
        if size is not None and filename is not None:
            raise ValueError("Must specify exactly one of size and filename. See http://platipy.org/en/latest/spyral_docs.html#spyral.image.Image")
        if size is None and filename is None:
            raise ValueError("Must specify exactly one of size and filename. See http://platipy.org/en/latest/spyral_docs.html#spyral.image.Image")

        if size is not None:
            self._surf = _new_spyral_surface(size)
            self._name = None
        else:
            self._surf = pygame.image.load(filename).convert_alpha()
            self._name = filename
        self._version = 1

    def _get_width(self):
        return self._surf.get_width()

    #: The width of this image in pixels (int). Read-only.
    width = property(_get_width)

    def _get_height(self):
        return self._surf.get_height()

    #: The height of this image in pixels (int). Read-only.
    height = property(_get_height)

    def _get_size(self):
        return spyral.Vec2D(self._surf.get_size())

    #: The (width, height) of the image (:class:`Vec2D <spyral.Vec2D`).
    #: Read-only.
    size = property(_get_size)

    def fill(self, color):
        """
        Fills the entire image with the specified color.

        :param color: a three-tuple of RGB values ranging from 0-255. Example:
                      (255, 128, 0) is orange.
        :type color: a three-tuple of ints.
        :returns: This image.
        """
        self._surf.fill(color)
        self._version += 1
        spyral.util.scale_surface.clear(self._surf)
        return self

    def draw_rect(self, color, position, size=None,
                  border_width=0, anchor='topleft'):
        """
        Draws a rectangle on this image.

        :param color: a three-tuple of RGB values ranging from 0-255. Example:
                      (255, 128, 0) is orange.
        :type color: a three-tuple of ints.
        :param position: The starting position of the rect (top-left corner). If
                         position is a Rect, then size should be `None`.
        :type position: :class:`Vec2D <spyral.Vec2D>` or
                        :class:`Rect <spyral.Rect>`
        :param size: The size of the rectangle; should not be given if position
                     is a rect.
        :type size: :class:`Vec2D <spyral.Vec2D>`
        :param int border_width: The width of the border to draw. If it is 0,
                                 the rectangle is filled with the color
                                 specified.
        :param str anchor: The anchor parameter is an
                           :ref:`anchor position <ref.anchors>`.
        :returns: This image.
        """
        if size is None:
            rect = spyral.Rect(position)
        else:
            rect = spyral.Rect(position, size)
        offset = self._calculate_offset(anchor, rect.size)
        pygame.draw.rect(self._surf, color,
                             (rect.pos + offset, rect.size), border_width)
        self._version += 1
        spyral.util.scale_surface.clear(self._surf)
        return self

    def draw_lines(self, color, points, width=1, closed=False):
        """
        Draws a series of connected lines on a image, with the
        vertices specified by points. This does not draw any sort of
        end caps on lines.

        :param color: a three-tuple of RGB values ranging from 0-255. Example:
                      (255, 128, 0) is orange.
        :type color: a three-tuple of ints.
        :param points: A list of points that will be connected, one to another.
        :type points: A list of :class:`Vec2D <spyral.Vec2D>` s.
        :param int width: The width of the lines.
        :param bool closed: If closed is True, the first and last point will be
                            connected. If closed is True and width is 0, the
                            shape will be filled.
        :returns: This image.
        """
        if width == 1:
            pygame.draw.aalines(self._surf, color, closed, points)
        else:
            pygame.draw.lines(self._surf, color, closed, points, width)
        self._version += 1
        spyral.util.scale_surface.clear(self._surf)
        return self

    def draw_circle(self, color, position, radius, width=0, anchor='topleft'):
        """
        Draws a circle on this image.

        :param color: a three-tuple of RGB values ranging from 0-255. Example:
                      (255, 128, 0) is orange.
        :type color: a three-tuple of ints.
        :param position: The center of this circle
        :type position: :class:`Vec2D <spyral.Vec2D>`
        :param int radius: The radius of this circle
        :param int width: The width of the circle. If it is 0, the circle is
                          filled with the color specified.
        :param str anchor: The anchor parameter is an
                           :ref:`anchor position <ref.anchors>`.
        :returns: This image.
        """
        offset = self._calculate_offset(anchor)
        pygame.draw.circle(self._surf, color, (position + offset).floor(),
                           radius, width)
        self._version += 1
        spyral.util.scale_surface.clear(self._surf)
        return self

    def draw_ellipse(self, color, position, size=None,
                     border_width=0, anchor='topleft'):
        """
        Draws an ellipse on this image.

        :param color: a three-tuple of RGB values ranging from 0-255. Example:
                      (255, 128, 0) is orange.
        :type color: a three-tuple of ints.
        :param position: The starting position of the ellipse (top-left corner).
                         If position is a Rect, then size should be `None`.
        :type position: :class:`Vec2D <spyral.Vec2D>` or
                        :class:`Rect <spyral.Rect>`
        :param size: The size of the ellipse; should not be given if position is
                     a rect.
        :type size: :class:`Vec2D <spyral.Vec2D>`
        :param int border_width: The width of the ellipse. If it is 0, the
                          ellipse is filled with the color specified.
        :param str anchor: The anchor parameter is an
                           :ref:`anchor position <ref.anchors>`.
        :returns: This image.
        """
        if size is None:
            rect = spyral.Rect(position)
        else:
            rect = spyral.Rect(position, size)
        offset = self._calculate_offset(anchor, rect.size)
        pygame.draw.ellipse(self._surf, color,
                            (rect.pos + offset, rect.size), border_width)
        self._version += 1
        spyral.util.scale_surface.clear(self._surf)
        return self

    def draw_point(self, color, position, anchor='topleft'):
        """
        Draws a point on this image.

        :param color: a three-tuple of RGB values ranging from 0-255. Example:
                      (255, 128, 0) is orange.
        :type color: a three-tuple of ints.
        :param position: The position of this point.
        :type position: :class:`Vec2D <spyral.Vec2D>`
        :param str anchor: The anchor parameter is an
                           :ref:`anchor position <ref.anchors>`.
        :returns: This image.
        """
        offset = self._calculate_offset(anchor)
        self._surf.set_at(position + offset, color)
        self._version += 1
        spyral.util.scale_surface.clear(self._surf)
        return self

    def draw_arc(self, color, start_angle, end_angle,
                 position, size=None, border_width=0, anchor='topleft'):
        """
        Draws an elliptical arc on this image.

        :param color: a three-tuple of RGB values ranging from 0-255. Example:
                      (255, 128, 0) is orange.
        :type color: a three-tuple of ints.
        :param float start_angle: The starting angle, in radians, of the arc.
        :param float end_angle: The ending angle, in radians, of the arc.
        :param position: The starting position of the ellipse (top-left corner).
                         If position is a Rect, then size should be `None`.
        :type position: :class:`Vec2D <spyral.Vec2D>` or
                        :class:`Rect <spyral.Rect>`
        :param size: The size of the ellipse; should not be given if position is
                     a rect.
        :type size: :class:`Vec2D <spyral.Vec2D>`
        :param int border_width: The width of the ellipse. If it is 0, the
                          ellipse is filled with the color specified.
        :param str anchor: The anchor parameter is an
                           :ref:`anchor position <ref.anchors>`.
        :returns: This image.
        """
        if size is None:
            rect = spyral.Rect(position)
        else:
            rect = spyral.Rect(position, size)
        offset = self._calculate_offset(anchor, rect.size)
        pygame.draw.arc(self._surf, color, (rect.pos + offset, rect.size),
                        start_angle, end_angle, border_width)
        self._version += 1
        spyral.util.scale_surface.clear(self._surf)
        return self

    def draw_image(self, image, position=(0, 0), anchor='topleft'):
        """
        Draws another image over this one.

        :param image: The image to overlay on top of this one.
        :type image: :class:`Image <spyral.Image>`
        :param position: The position of this image.
        :type position: :class:`Vec2D <spyral.Vec2D>`
        :param str anchor: The anchor parameter is an
                           :ref:`anchor position <ref.anchors>`.
        :returns: This image.
        """
        offset = self._calculate_offset(anchor, image._surf.get_size())
        self._surf.blit(image._surf, position + offset)
        self._version += 1
        spyral.util.scale_surface.clear(self._surf)
        return self

    def rotate(self, angle):
        """
        Rotates the image by angle degrees clockwise. This may change the image
        dimensions if the angle is not a multiple of 90.

        Successive rotations degrate image quality. Save a copy of the
        original if you plan to do many rotations.

        :param float angle: The number of degrees to rotate.
        :returns: This image.
        """
        self._surf = pygame.transform.rotate(self._surf, angle).convert_alpha()
        self._version += 1
        return self

    def scale(self, size):
        """
        Scales the image to the destination size.

        :param size: The new size of the image.
        :type size: :class:`Vec2D <spyral.Vec2D>`
        :returns: This image.
        """
        self._surf = pygame.transform.smoothscale(self._surf,
                                                  size).convert_alpha()
        self._version += 1
        return self

    def flip(self, flip_x=True, flip_y=True):
        """
        Flips the image horizontally, vertically, or both.

        :param bool flip_x: whether to flip horizontally.
        :param bool flip_y: whether to flip vertically.
        :returns: This image.
        """
        self._version += 1
        self._surf = pygame.transform.flip(self._surf,
                                           flip_x, flip_y).convert_alpha()
        return self

    def copy(self):
        """
        Returns a copy of this image that can be changed while preserving the
        original.

        :returns: A new image.
        """
        new = copy.copy(self)
        new._surf = self._surf.copy()
        return new

    def crop(self, position, size=None):
        """
        Removes the edges of an image, keeping the internal rectangle specified
        by position and size.

        :param position: The upperleft corner of the internal rectangle that
                         will be preserved.
        :type position: a :class:`Vec2D <spyral.Vec2D>` or a
                        :class:`Rect <spyral.Rect>`.
        :param size: The size of the internal rectangle to preserve. If a Rect
                     was passed in for position, this should be None.
        :type size: :class:`Vec2D <spyral.Vec2D>` or None.
        :returns: This image.
        """
        if size is None:
            rect = spyral.Rect(position)
        else:
            rect = spyral.Rect(position, size)
        new = _new_spyral_surface(size)
        new.blit(self._surf, (0, 0), (rect.pos, rect.size))
        self._surf = new
        self._version += 1
        return self

    def _calculate_offset(self, anchor_type, size=(0, 0)):
        """
        Internal method for calculating the offset associated with an
        anchor type.

        :param anchor_type: A string indicating the position of the anchor,
                            taken from :ref:`anchor position <ref.anchors>`. A
                            numerical offset can also be specified.
        :type anchor_type: str or a :class:`Vec2D <spyral.Vec2D>`.
        :param size: The size of the region to offset in.
        :type size: :class:`Vec2D <spyral.Vec2D>`.
        """
        w, h = self._surf.get_size()
        w2, h2 = size

        if anchor_type == 'topleft':
            return spyral.Vec2D(0, 0)
        elif anchor_type == 'topright':
            return spyral.Vec2D(w - w2, 0)
        elif anchor_type == 'midtop':
            return spyral.Vec2D((w - w2) / 2., 0)
        elif anchor_type == 'bottomleft':
            return spyral.Vec2D(0, h - h2)
        elif anchor_type == 'bottomright':
            return spyral.Vec2D(w - w2, h - h2)
        elif anchor_type == 'midbottom':
            return spyral.Vec2D((w - w2) / 2., h - h2)
        elif anchor_type == 'midleft':
            return spyral.Vec2D(0, (h - h2) / 2.)
        elif anchor_type == 'midright':
            return spyral.Vec2D(w - w2, (h - h2) / 2.)
        elif anchor_type == 'center':
            return spyral.Vec2D((w - w2) / 2., (h - h2) / 2.)
        else:
            return spyral.Vec2D(anchor_type) - spyral.Vec2D(w2, h2)
