import pygame
import spyral

class Rect(object):
    """
    Rect represents a rectangle and provides some useful features.
    
    Rects can be specified 3 ways in the constructor
    
    * Another rect, which is copied
    * Two tuples, `(x, y)` and `(width, height)`
    * Four numbers, `x`, `y`, `width`, `height`
    
    Rects support all the usual :ref:`anchor points <anchors>` as 
    attributes, so you can both get `rect.center` and assign to it.
    Rects also support attributes of `right`, `left`, `top`, `bottom`,
    `x`, and `y`.
    """
    def __init__(self, *args):
        if len(args) == 1:
            r = args[0]
            self._x, self._y = r.x, r.y
            self._w, self._h = r.w, r.h
        elif len(args) == 2:
            self._x, self._y = args[0]
            self._w, self._h = args[1]
        elif len(args) == 4:
            self.left, self.top, self.width, self.height = args
        else:
            raise ValueError("You done goofed.")
                
    def __getattr__(self, name):
        v = spyral.Vec2D
        if name == "right":
            return self._x + self._w
        if name == "left" or name == "x":
            return self._x
        if name == "top" or name == "y":
            return self._y
        if name == "bottom":
            return self._y + self._h
        if name == "topright":
            return v(self._x + self._w, self._y)
        if name == "bottomleft":
            return v(self._x, self._y + self._h)
        if name == "topleft" or name == "pos":
            return v(self._x, self._y)
        if name == "bottomright":
            return v(self._x + self._w, self._y + self._h)
        if name == "centerx":
            return (self._x + self._w / 2.)
        if name == "centery":
            return (self._y + self._h / 2.)
        if name == "center":
            return v(self._x + self._w / 2., self._y + self._h / 2.)
        if name == "midleft":
            return v(self._x, self._y + self._h / 2.)
        if name == "midright":
            return v(self._x + self._w, self._y + self._h / 2.)
        if name == "midtop":
            return v(self._x + self._w / 2., self._y)
        if name == "midbottom":
            return v(self._x + self._w / 2., self._y + self._h)
        if name == "size":
            return v(self._w, self._h)
        if name == "width" or name == "w":
            return self._w
        if name == "height" or name == "h":
            return self._h
            
        raise AttributeError("type object 'rect' has no attribute '" + name + "'")
            
    def __setattr__(self, name, val):
        # This could use _a lot_ more error checking
        if name[0] == "_":
            self.__dict__[name] = int(val)
            return
        if name == "right":
            self._x = val - self._w
        elif name == "left":
            self._x = val
        elif name == "top":
            self._y = val
        elif name == "bottom":
            self._y = val - self._h
        elif name == "topleft":
            self._x, self._y = val
        elif name == "topright":
            self._x = val[0] - self._w
            self._y = val[1]
        elif name == "bottomleft":
            self._x = val[0]
            self._y = val[1] - self._h
        elif name == "bottomright":
            self._x = val[0] - self._w
            self._y = val[0] - self._h
        elif name == "width" or name == "w":
            self._w = val
        elif name == "height" or name == "h":
            self._h = val
        elif name == "size":
            self._w, self._h = val
        elif name == "centerx":
            self._x = val - self._w / 2.
        elif name == "centery":
            self._y = val - self._h / 2.
        elif name == "center":
            self._x = val[0] - self._w / 2.
            self._y = val[1] - self._h / 2.
        elif name == "midtop":
            self._x = val[0] - self._w / 2.
            self._y = val[1]
        elif name == "midleft":
            self._x = val[0]
            self._y = val[1] - self._h / 2.
        elif name == "midbottom":
            self._x = val[0] - self._w / 2.
            self._y = val[1] - self._h
        elif name == "midright":
            self._x = val[0] - self._w
            self._y = val[1] - self._h / 2.
        else:
            raise AttributeError("You done goofed!")
            
    def copy(self):
        """
        Returns a copy of this rect
        """
        return Rect(self._x, self._y, self._w, self._h)
        
    def move(self, x, y):
        """
        Returns a copy of this rect offset by *x* and *y*.
        """
        return Rect(x, y, self._w, self._h)
        
    def move_ip(self, x, y):
        """
        Moves this rect by *x* and *y*.
        """
        self._x, self._y = self._x + x, self._y + y
        
    def inflate(self, width, height):
        """
        Returns a copy of this rect inflated by *width* and *height*.
        """
        c = self.center
        n = self.copy()
        n.size = (self._w + width, self._h + height)
        n.center = c
        return n
        
    def inflate_ip(self, width, height):
        """
        Inflates this rect by *width*, *height*.
        """
        c = self.center
        self.size = (self._w + width, self._h + height)
        self.center = c
        
    def union(self, other):
        """
        Returns a new rect which represents the union of this rect
        with other.
        """
        top = min(self.top, other.top)
        left = min(self.left, other.left)
        bottom = max(self.bottom, other.bottom)
        right = max(self.right, other.right)
        return Rect((left, top), (right - left, bottom - top))

    # @test: Rect(10,10,50,50).clip(Rect(0,0,20,20)) -> Rect(10,10,10,10)
    def clip(self, r):
        """
        Returns a Rect which is cropped to be completely inside of r.
        If the r does not overlap with this rect, 0 is returned.
        """
        B = r
        A = self
        try:
            B._x
        except TypeError:
            B = Rect(B)
            
        if A._x >= B._x and A._x < (B._x + B._w):
            x = A._x
        elif B._x >= A._x and B._x < (A._x + A._w):
            x = B._x
        else:
            return Rect(A._x, A._y, 0, 0)
            
        if ((A._x + A._w) > B._x) and ((A._x + A._w) <= (B._x + B._w)):
            w = A._x + A._w - x
        elif ((B._x + B._w) > A._x) and ((B._x + B._w) <= (A._x + A._w)):
            w = B._x + B._w - x
        else:
            return Rect(A._x, A._y, 0, 0)
            
        if A._y >= B._y and A._y < (B._y + B._h):
            y = A._y
        elif B._y >= A._y and B._y < (A._y + A._h):
            y = B._y
        else:
            return Rect(A._x, A._y, 0, 0)
            
        if ((A._y + A._h) > B._y) and ((A._y + A._h) <= (B._y + B._h)):
            h = A._y + A._h - y
        elif ((B._y + B._h) > A._y) and ((B._y + B._h) <= (A._y + A._h)):
            h = B._y + B._h - y
        else:
            return Rect(A._x, A._y, 0, 0)
        
        return Rect(x, y, w, h)
        
    def contains(self, r):
        """
        Returns True if the rect r is contained inside this rect
        """
        return r.collide_point(self.topleft) and r.collide_point(self.bottomright)
        
    def collide_rect(self, r):
        """
        Returns true if this rect collides with rect r.
        """
        return self.clip(r).size != (0,0) or r.clip(self).size != (0,0)
        
    def collide_point(self, point):
        """
        Returns true if this rect collides with point
        """
        # This could probably be optimized as well
        return point[0] > self.left and point[0] < self.right and \
            point[1] > self.top and point[1] < self.bottom

    def _to_pygame(self):
        return pygame.Rect(((self.left, self.top), (self.width, self.height)))
        
    def __str__(self):
        return ''.join(['<rect(',
                        str(self._x),
                        ',',
                        str(self._y),
                        ',',
                        str(self._w),
                        ',',
                        str(self._h),
                        ')>'])
    def __repr__(self):
        return self.__str__()