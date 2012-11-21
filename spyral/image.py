import pygame
import spyral
import copy

class Image(object):
    """
    The image is the basic drawable item in spyral. They can be created
    either by loading from common file formats, or by creating a new
    image and using some of the draw methods. Images are not drawn on
    their own, they are placed as the *image* attribute on Sprites to
    be drawn.

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
            self._surf = Image._new_spyral_surface(size)
            self._name = None
        else:
            self._surf = pygame.image.load(filename).convert_alpha()
            self._name = filename
        self._version = 1
    
    def get_width(self):
        return self._surf.get_width()
        
    def get_height(self):
        return self._surf.get_height()
        
    def get_size(self):
        """
        Returns the (width, height) of the image.
        """
        return spyral.Vec2D(self._surf.get_size())
    
    def fill(self, color):
        """
        Fills the entire image with the specified color.
        """
        color = spyral.color._determine(color)
        self._surf.fill(color)
        self._version += 1
        spyral.camera._scale.clear(self._surf)
        
    def draw_rect(self, color, position, size, border_width = 0, anchor= 'topleft'):
        """
        Draws a rectangle on this image. position = (x, y) specifies 
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
        self._version += 1
        spyral.camera._scale.clear(self._surf)
        
    def draw_lines(self, color, points, width = 1, closed = False):
        """
        Draws a series of connected lines on a image, with the
        vertices specified by points. This does not draw any sort of
        end caps on lines.
        
        If closed is True, the first and last point will be connected.
        If closed is True and width is 0, the shape will be filled.
        """
        color = spyral.color._determine(color)
        if width == 1:
            pygame.draw.aalines(self._surf, color, closed, points)
        else:
            pygame.draw.lines(self._surf, color, closed, points, width)
        self._version += 1
        spyral.camera._scale.clear(self._surf)
    
    def draw_circle(self, color, position, radius, width = 0, anchor= 'topleft'):
        """
        Draws a circle on this image. position = (x, y) specifies
        the center of the circle, and radius the radius. If width is
        0, the circle is filled. The anchor parameter is an :ref:`anchor 
        position <anchors>`.
        """
        color = spyral.color._determine(color)
        offset = self._calculate_offset(anchor)
        pygame.draw.circle(self._surf, color, position + offset, radius, width)
        self._version += 1
        spyral.camera._scale.clear(self._surf)
        
    def draw_ellipse(self, color, position, size, border_width = 0, anchor= 'topleft'):
        """
        Draws an ellipse on this image. position = (x, y) specifies 
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
        self._version += 1
        spyral.camera._scale.clear(self._surf)
    
    def draw_point(self, color, position, anchor= 'topleft'):
        """
        Draws a point on this image. position = (x, y) specifies
        the position of the point. The anchor parameter is an :ref:`anchor 
        position <anchors>`.
        """
        color = spyral.color._determine(color)
        offset = self._calculate_offset(anchor)
        self._surf.set_at(position + offset, color)
        self._version += 1
        spyral.camera._scale.clear(self._surf)
    
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
        self._version += 1
        spyral.camera._scale.clear(self._surf)
        
    def draw_image(self, image, position = (0, 0), anchor= 'topleft'):
        """
        Draws another image onto this one at the specified position. The anchor 
        parameter is an :ref:`anchor position <anchors>`.
        """
        offset = self._calculate_offset(anchor, image._surf.get_size())
        self._surf.blit(image._surf, position + offset)
        self._version += 1
        spyral.camera._scale.clear(self._surf)
        
    @classmethod
    def from_sequence(self, images, orientation = None, padding=0):
        """
        Static class method that returns a new Image from a list of *images* by placing them next to each other. *orientation* can be either 'left', 'right', 'above', 'below', or 'square' (square images will be placed in a grid shape, like a chess board). Optionally, the parameter *padding* can be specified as a number (for constant padding between all images) or a list (for different paddings between each image).
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
                    x += image.get_width()
                    max_height = max(max_height, image.get_height())
                sequence.append((image, (x, y)))
        else:
            if orientation in ('left', 'right'):
                selector = spyral.Vec2D(1,0)
            else:
                selector = spyral.Vec2D(0,1)

            if orientation in ('left', 'above'):
                reversed(images)

            if type(padding) in (float, int, long):
                padding = [padding] * len(images)
            else:
                padding = list(padding)
                padding.append(0)
            base = spyral.Vec2D(0,0)
            sequence = []
            for image, padding in zip(images, padding):
                sequence.append((image, base))
                base = base + selector * (image.get_size() + (padding, padding))
        return Image.from_conglomerate(sequence)
    @classmethod
    def from_conglomerate(self, sequence):
        """
        Generates a new image from a *sequence* of (image, position) pairs. These images will be placed onto a singe image large enough to hold all of them.
        """
        width, height = 0, 0
        for image, (x, y) in sequence:
            width = max(width, x+image.get_width())
            height = max(height, y+image.get_height())
        new = Image(size=(width, height))
        for image, (x, y) in sequence:
            new.draw_image(image, (x,y))
        return new
    def rotate(self, angle):
        """
        Rotates the image by *angle* degrees clockwise. This may change
        the image dimensions if the angle is not a multiple of 90.
        
        Successive rotations degrate image quality. Save a copy of the
        original if you plan to do many rotations.
        """
        self._surf = pygame.transform.rotate(self._surf, angle).convert_alpha()
        self._version += 1
        
    def scale(self, size):
        """
        Scales the image to the destination size.
        """
        self._surf = pygame.transform.smoothscale(self._surf, size).convert_alpha()
        self._version += 1
        
    def flip(self, xbool, ybool):
        """
        Flips the image horizontally, vertically, or both.
        """
        self._version += 1
        self._surf = pygame.transform.flip(self._surf, xbool, ybool).convert_alpha()
        
    def copy(self):
        """
        Returns a copy of this image that can be changed while preserving the
        original.
        """
        new = copy.copy(self)
        new._surf = self._surf.copy()
        return new
    
    @classmethod
    def _new_spyral_surface(self, size):
        return pygame.Surface((int(size[0]), int(size[1])), pygame.SRCALPHA, 32).convert_alpha()
        
    def crop(self, position, size):
        """
        Removes the edges of an image, keeping the internal rectangle specified
        by position and size.
        """
        new = Image._new_spyral_surface(size)
        new.blit(self._surf, (0,0), (position, size))
        self._surf = new
        self._version += 1
        
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
