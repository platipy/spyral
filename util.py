import pygame as _pygame

def new_surface(size, size2 = None):
    """ returns a Surface guaranteed to work with APH, which has an alpha
    channel and a 32-bit color depth.
    new_surface((width,height)) or new_surface(width, height) """
    if size2 is None:
        return _pygame.Surface((int(size[0]), int(size[1])), _pygame.SRCALPHA, 32)
    return _pygame.Surface((int(size), int(size2)), _pygame.SRCALPHA, 32)
    
def bounding_rect(l):
    """ Computes a bounding rectangle from an iterable of tuples (x,y). """
    # This can be done faster.
    x = [x[0] for x in l]
    y = [y[1] for y in l]
    minx = max(0, min(x))
    miny = max(0, min(y))
    return _pygame.Rect(minx, miny, max(x)-minx, max(y)-miny)