import spyral

def anchor_offset(anchor, width, height):
    w = width
    h = height
    a = anchor
    if a == 'topleft':
        offset = (0, 0)
    elif a == 'topright':
        offset = (w, 0)
    elif a == 'midtop':
        offset = (w / 2., 0)
    elif a == 'bottomleft':
        offset = (0, h)
    elif a == 'bottomright':
        offset = (w, h)
    elif a == 'midbottom':
        offset = (w / 2., h)
    elif a == 'midleft':
        offset = (0, h / 2.)
    elif a == 'midright':
        offset = (w, h / 2.)
    elif a == 'center':
        offset = (w / 2., h / 2.)
    else:
        offset = a * spyral.Vec2D(-1, -1)
    return spyral.Vec2D(offset)