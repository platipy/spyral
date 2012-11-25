import pygame
import spyral

import pygame
import spyral

class _FontImage(spyral.Image):
    def __init__(self, surf):
        self._surf = surf
        self._name = None
        self._version = 1
        
class Font(object):
    """
    Loads a font from a TrueType Font file (.ttf), with size as the desired height in pixels.
    
    Currently, the use of system fonts is not supported.
    """
    def __init__(self, font_path, size, default_color):
        self.size = int(size)
        self.font = pygame.font.Font(font_path, size)
        self.default_color = spyral.color._determine(default_color)
        
    def render(self, text, color = None, underline = False, italic = False, bold = False):
        """
        Renders the text with this font and color (or the default
        color). Italic and bold are false italic and bold modes that
        may not look good for many fonts. It is preferable to load a
        bold or italic font where possible instead of using these
        options.
        
        Returns a spyral.Image of the rendered text.
        """
        if color is None:
            color = self.default_color
        else:
            color = spyral.color._determine(color)
        self.font.set_underline(underline)
        self.font.set_bold(bold)
        self.font.set_italic(italic)
        s1 = self.font.render(text, True, color).convert_alpha()
        s2 = pygame.Surface(s1.get_size(), pygame.SRCALPHA)
        s2.blit(s1, (0, 0))
        
        return _FontImage(s2.convert_alpha())

    def get_height(self):
        """
        Returns the average height in pixels for each glyph in the
        font.
        """
        return self.font.get_height()
        
    def get_ascent(self):
        """
        Return the height in pixels from the font baseline to the top
        of the font.
        """
        return self.font.get_ascent()
        
    def get_descent(self):
        """
        Return the height in pixels from the font baseline to the
        bottom of the font.
        """
        return self.font.get_descent()
        
    def get_linesize(self):
        """
        Returns the height in pixels for a line of text rendered with
        the font.
        """
        return self.font.get_linesize()
        
    def get_metrics(self, text):
        """
        Returns a list containing the font metrics for each character
        in the passed in string. The metrics is a tuple containing the
        minimum x offset, maximum x offset, minimum y offset, maximum
        y offset, and the advance offset of the character.
        """
        return self.font.get_metrics(text)
        
    def get_size(self, text):
        """
        Returns the size needed to render the text without actually
        rendering the text. Useful for word-wrapping. Remember to
        keep in mind font kerning may be used.
        """
        return self.font.size(text)