import math as math

def sub(p1, p2):
    """ Computes p2-p1. """
    return (p1[0] - p2[0], p1[1] - p2[1])
    
def add(p1, p2):
    """ Computes p1 + p2. """
    return (p2[0] + p1[0], p2[1] + p1[1])
    
def angle(p):
    """ Calculates the angle that p makes with the x axis, in radians. """
    return math.atan2(p[1], p[0])
    
def dist(p1, p2):
    """ Calculates the distance between two points. """
    return math.hypot(*sub(p1,p2))
    
def rectangular(r, theta):
    """ Converts polar coordinates to rectangular. """
    return (r*math.cos(theta), r*math.sin(theta))
    
def polar(p):
    """ Converts rectangular coordinates to polar. Returns (r, theta). """
    return (dist(p, (0,0)), angle(p))

def scale(p, scale):
    """ Scales p by (scale_x, scale_y). """
    return (p[0] * scale[0], p[1] * scale[1])

def unscale(p, scale):
    """ Scales p by (1/scale_x, 1/scale_y). """
    return (p[0] / scale[0], p[1] / scale[1])

def dist2(p1, p2):
    """ Returns the square of a distance between two points"""
    x = sub(p1, p2)
    return x[0]**2 + x[1]**2
    
def rotate(p, angle, center = (0,0)):
    """ Rotates p around center by angle. """
    (r, theta) = sub(p, center)
    print theta
    theta += angle    
    return add(rectangular(r, theta), center)
    
def snap_to_grid(p, size):
    """
    Finds the nearest grid point to p. Allows a uniform size, or a tuple of
    sizes for each axis.

    snap_to_grid((x,y), 16)
    snap_to_grid((x,y), (16, 8))
    """
    try:
        return (int(round(p[0]/size[0])*size[0]),
                int(round(p[1]/size[1])*size[1]))
    except TypeError:
        return (int(round(p[0]/size)*size),
                int(round(p[1]/size)*size))    
    
def bounding_rect(l):
    """
    Computes a bounding rectangle from an iterable of tuples (x,y).
    """
    # This can be done faster.
    x = [x[0] for x in l]
    y = [y[1] for y in l]
    minx = max(0, min(x))
    miny = max(0, min(y))
    return pygame.Rect(minx, miny, max(x)-minx, max(y)-miny)