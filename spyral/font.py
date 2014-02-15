"""
This module defines Font objects, used for rendering text into Images.
"""

import pygame
from spyral import Image, Vec2D

class _FontImage(Image):
    """
    A wrapper for Images that came from rendering a font. This is necessary
    since the rendering returns a surface, which the Image API is built to hide.

    :param surf: The pygame Surface that will be stored in this _FontImage.
    :type surf: :class:`pygame.Surface`
    """
    def __init__(self, surf):
        self._surf = surf
        self._name = None
        self._version = 1

class Font(object):
    """
    Font objects are how you get text onto the screen. They are loaded from
    TrueType Font files (\*.ttf); system fonts are not supported for asthetic
    reasons. If you need direction on what the different size-related
    properties of a Font object, check out the Font example.

    :param str font_path: The location of the \*.ttf file.
    :param int size: The size of the font; font sizes refer to the height of the
                     font in pixels.
    :param color: A three-tuple of RGB values ranging from 0-255. Defaults to
                  black ``(0, 0, 0)``.
    :type color: A three-tuple.
    """
    def __init__(self, font_path, size, default_color=(0, 0, 0)):
        self.size = int(size)
        self.font = pygame.font.Font(font_path, size)
        self.default_color = default_color

    def render(self, text, color=None, underline=False,
               italic=False, bold=False):
        """
        Renders the given *text*. Italicizing and bolding are artificially
        added, and may not look good for many fonts. It is preferable to load a
        bold or italic font where possible instead of using these options.

        :param str text: The text to render. Some characters might not be able
                         to be rendered (e.g., "\\\\n").
        :param color: A three-tuple of RGB values ranging from 0-255. Defaults
                      to the default Font color.
        :type color: A three-tuple.
        :param bool underline: Whether to underline this text. Note that the
                               line will always be 1 pixel wide, no matter the
                               font size.
        :param bool italic: Whether to artificially italicize this font by
                            angling it.
        :param bool bold: Whether to artificially embolden this font by
                          stretching it.
        :rtype: :class:`Image <spyral.Image>`
        """
        if color is None:
            color = self.default_color
        self.font.set_underline(underline)
        self.font.set_bold(bold)
        self.font.set_italic(italic)
        text_surface = self.font.render(text, True, color).convert_alpha()
        background_surface = pygame.Surface(text_surface.get_size(), pygame.SRCALPHA)
        background_surface.blit(text_surface, (0, 0))

        return _FontImage(background_surface.convert_alpha())

    def _get_height(self):
        return self.font.get_height()
    #: The average height in pixels for each glyph in the font. Read-only.
    height = property(_get_height)

    def _get_ascent(self):
        return self.font.get_ascent()
    #: The height in pixels from the font baseline to the top of the font.
    #: Read-only.
    ascent = property(_get_ascent)

    def _get_descent(self):
        return self.font.get_descent()
    #: The height in pixels from the font baseline to the bottom of the font.
    #: Read-only.
    descent = property(_get_descent)

    def _get_linesize(self):
        return self.font.get_linesize()
    #: The height in pixels for a line of text rendered with the font.
    #: Read-only.
    linesize = property(_get_linesize)

    def get_metrics(self, text):
        """
        Returns a list containing the font metrics for each character
        in the text. The metrics is a tuple containing the
        minimum x offset, maximum x offset, minimum y offset, maximum
        y offset, and the advance offset of the character. ``[(minx, maxx, miny,
        maxy, advance), (minx, maxx, miny, maxy, advance), ...]``

        :param str text: The text to gather metrics on.
        :rtype: `list` of tuples.
        """
        return self.font.get_metrics(text)

    def get_size(self, text):
        """
        Returns the size needed to render the text without actually
        rendering the text. Useful for word-wrapping. Remember to
        keep in mind font kerning may be used.

        :param str text: The text to get the size of.
        :returns: The size (width and height) of the text as it would be
                  rendered.
        :rtype: :class:`Vec2D <spyral.Vec2D>`
        """
        return Vec2D(self.font.size(text))
