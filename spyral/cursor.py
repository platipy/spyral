import pygame
import spyral
import re

cursors = [pygame.cursors.thickarrow_strings, 
           pygame.cursors.sizer_x_strings, 
           pygame.cursors.sizer_y_strings, 
           pygame.cursors.sizer_xy_strings]

class MonochromeCursor(object):
    def __init__(self, source):
        """
        source can be an XBM file, a sequence of strings, or an Image.
        """
        if isinstance(source, spyral.Image):
            pass
        elif isinstance(source, str):
            self.data = pygame.cursors.load_xbm(source, source)
        else:
            self.data = pygame.cursors.compile(source)

class ColorCursor(spyral.Sprite):
    pass

def set_cursor(cursor):
    pygame.mouse.set_cursor(*cursor.data)

# MonochromeCursor
# built-in cursors
# load XBM file
# use Image
#   - image width must be divisible by 8
#   - should be black and white
#       * parameter to control other colors (round up or down)

# ColorCursor
#   - hides cursor
#   - moves other cursor around screen    