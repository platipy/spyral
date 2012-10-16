import pygame
import spyral
import copy

class Image(object):
    """
    The image is the basic drawable item in spyral. They can be created
    either by loading from common file formats, or by creating a new
    image and using some of the draw methods.

    | *size*: If *size* is passed, creates a new blank image of
      that size to draw on. Size should be an iterable with two
      elements
    | *filename*: If *filename* is set, the file with that name
      is loaded.
    """
    
    def __init__(self, filename = None, size = None):
        if size is not None and filename is not None:
            raise ValueError("Must specify exactly one of size and filename.")
        if size is None and filename is None:
            raise ValueError("Must specify exactly one of size and filename.")
            
        if size is not None:
            self._surf = pygame.Surface((int(size[0]), int(size[1])), pygame.SRCALPHA, 32)
            self._name = None
        else:
            self._surf = pygame.image.load(filename).convert_alpha()
            self._name = filename
    
    def get_width(self):
        return self._surf.get_width()
        
    def get_height(self):
        return self._surf.get_height()
        
    def get_size(self):
        """
        Returns the (width, height) of the image.
        """
        return self._surf.get_size()
    
    def fill(self, color):
        """
        Fills the entire surface with the specified color.
        """
        color = spyral.color._determine(color)
        self._surf.fill(color)
        
    def draw_rect(self, color, position, size, border_width = 0, anchor= 'topleft'):
        """
        Draws a rectangle on this surface. position = (x, y) specifies 
        the top-left corner, and size = (width, height) specifies the
        width and height of the rectangle. border_width specifies the
        width of the border to draw. If it is 0, the rectangle is
        filled with the color specified. The anchor parameter is an :ref:`anchor 
        position <anchors>`.
        """
        # We'll try to make sure that everything is okay later
        
        color = spyral.color._determine(color)
        offset = self._calculate_offset(anchor, size)
        pygame.draw.rect(self._surf, color, (position + offset, size), border_width)
        
    def draw_lines(self, color, points, width = 1, closed = False):
        """
        Draws a series of connected lines on a surface, with the
        vertices specified by points. This does not draw any sort of
        end caps on lines.
        
        If closed is True, the first and last point will be connected.
        If closed is True and width is 0, the shape will be filled.
        """
        color = spyral.color._determine(color)
        pygame.draw.aalines(self._surf, color, closed, points)
    
    def draw_circle(self, color, position, radius, width = 0, anchor= 'topleft'):
        """
        Draws a circle on this surface. position = (x, y) specifies
        the center of the circle, and radius the radius. If width is
        0, the circle is filled. The anchor parameter is an :ref:`anchor 
        position <anchors>`.
        """
        color = spyral.color._determine(color)
        offset = self._calculate_offset(anchor)
        pygame.draw.circle(self._surf, color, position + offset, radius, width)
        
    def draw_ellipse(self, color, position, size, border_width = 0, anchor= 'topleft'):
        """
        Draws an ellipse on this surface. position = (x, y) specifies 
        the top-left corner, and size = (width, height) specifies the
        width and height of the ellipse. border_width specifies the
        width of the border to draw. If it is 0, the ellipse is
        filled with the color specified. The anchor parameter is an :ref:`anchor 
        position <anchors>`.
        """
        # We'll try to make sure that everything is okay later
        
        color = spyral.color._determine(color)
        offset = self._calculate_offset(anchor, size)
        pygame.draw.ellipse(self._surf, color, (position + offset, size), border_width)
    
    def draw_point(self, color, position, anchor= 'topleft'):
        """
        Draws a point on this surface. position = (x, y) specifies
        the position of the point. The anchor parameter is an :ref:`anchor 
        position <anchors>`.
        """
        color = spyral.color._determine(color)
        offset = self._calculate_offset(anchor)
        self._surf.set_at(position + offset, color)
    
    def draw_arc(self, color, position, size, start_angle, end_angle, border_width = 0, anchor = 'topleft'):
        """
        Draws an elliptical arc on this surface. position = (x, y) specifies 
        the top-left corner, and size = (width, height) specifies the
        width and height of the ellipse. The start_angle and end_angle specify
        the range of the arc to draw. border_width specifies the
        width of the border to draw. If it is 0, the ellipse is
        filled with the color specified. The anchor parameter is an :ref:`anchor 
        position <anchors>`.
        """
        color = spyral.color._determine(color)
        offset = self._calculate_offset(anchor, size)
        pygame.draw.arc(self._surf, color, (position + offset, size), start_angle, end_angle, border_width)
        
    def draw_image(self, image, position = (0, 0), anchor= 'topleft'):
        """
        Draws another image onto this one at the specified position. The anchor 
        parameter is an :ref:`anchor position <anchors>`.
        """
        offset = self._calculate_offset(anchor, image._surf.get_size())
        self._surf.blit(image._surf, position + offset)
        
    def rotate(self, angle):
        """
        Rotates the image by *angle* degrees clockwise. This may change
        the image dimensions if the angle is not a multiple of 90.
        
        Successive rotations degrate image quality. Save a copy of the
        original if you plan to do many rotations.
        """
        self._surf = pygame.transform.rotate(self._surf, angle).convert_alpha()
        
    def scale(self, size):
        """
        Scales the image to the destination size.
        """
        self._surf = pygame.transform.smoothscale(self._surf, size).convert_alpha()
        
    def flip(self, xbool, ybool):
        """
        Flips the image horizontally, vertically, or both.
        """
        self._surf = pygame.transform.flip(self._surf, xbool, ybool).convert_alpha()
        
    def copy(self):
        """
        Returns a copy of this image that can be changed while preserving the
        original.
        """
        new = copy.copy(self)
        new._surf = self._surf.copy()
        return new
        
    def crop(self, position, size):
        """
        Removes the edges of an image, keeping the internal rectangle specified
        by position and size.
        """
        new = pygame.Surface((int(size[0]), int(size[1])), pygame.SRCALPHA, 32)
        new.blit(self._surf, (0,0), (position, size))
        self._surf = new
        
    def _calculate_offset(self, anchor_type, size = (0,0)):
        w, h = self._surf.get_size()
        w2, h2 = size
        a = anchor_type

        if a == 'topleft':
            return spyral.Vec2D(0, 0)
        elif a == 'topright':
            return spyral.Vec2D(w - w2, 0)
        elif a == 'midtop':
            return spyral.Vec2D( (w - w2) / 2., 0)
        elif a == 'bottomleft':
            return spyral.Vec2D(0, h - h2)
        elif a == 'bottomright':
            return spyral.Vec2D(w - w2, h - h2)
        elif a == 'midbottom':
            return spyral.Vec2D((w - w2) / 2., h - h2)
        elif a == 'midleft':
            return spyral.Vec2D(0, (h - h2) / 2.)
        elif a == 'midright':
            return spyral.Vec2D(w - w2, (h - h2) / 2.)
        elif a == 'center':
            return spyral.Vec2D((w - w2) / 2., (h - h2) / 2.)
        else:
            return spyral.Vec2D(a) - spyral.Vec2D(w2, h2)
