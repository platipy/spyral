import spyral

def anchor_offset(anchor, width, height):
    """
    Given an `anchor` position (either a string or a 2-tuple position), finds the
    correct offset in a rectangle of size (`width`, `height`). If the `anchor` is
    a 2-tuple (or Vec2D), then it TODO: What does it do?.
    
    >>> anchor_offset("topleft", 100, 100)
    Vec2D(0,0)
    >>> anchor_offset("bottomright", 100, 100)
    Vec2D(100,100)
    >>> anchor_offset("center", 100, 100)
    Vec2D(50,50)
    >>> anchor_offset((10, 10), 100, 100)
    Vec2D(-10,-10)
    
    For a complete list of the anchor positions, see `Anchor Offset Lists`_.
    
    :param anchor: The (possibly named) position to offset by.
    :type anchor: string or :class:`Vec2D <spyral.Vec2D>`
    :param width: the width of the rectangle to offset in.
    :type width: int
    :param height: the height of the rectangle to offset in. 
    :type height: int
    """
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