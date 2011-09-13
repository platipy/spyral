import math as _math

def sub(p1, p2):
    return (p1[0] - p2[0], p1[1] - p2[1])
    
def add(p1, p2):
    return (p2[0] + p1[0], p2[1] + p1[1])
    
def angle(p):
    return _math.atan2(p[1], p[0])
    
def dist(p1, p2):
    return _math.hypot(*sub(p1,p2))
    
def rectangular(r, theta):
    return (r*_math.cos(theta), r*_math.sin(theta))

def scale(p, scale):
    return (p[0] * scale[0], p[1] * scale[1])

def unscale(p, scale):
    return (p[0] / scale[0], p[1] / scale[1])

def round_pos(t):
    return (_math.floor(t[0]), _math.ceil(t[1]))
