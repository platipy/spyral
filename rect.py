class Rect(object):
    def __init__(self, *args):
        # Again with the weird non-pythonic mess
        if len(args) == 1: # copy another rect
            return args[0].copy()
        elif len(args) == 2:
            self._x, self._y = args[0]
            self._w, self._h = args[1]
        elif len(args) == 4:
            self.left, self.top, self.width, self.height = args
        else:
            raise ValueError("You done goofed.")
            
    def __getattr__(self, name):
        if name == "right":
            return self._x + self._w
        if name == "left" or name == "x":
            return self._x
        if name == "top" or name == "y":
            return self._y
        if name == "bottom":
            return self._y + self._h
        if name == "topright":
            return (self._x + self._w, self._y)
        if name == "bottomleft":
            return (self._x, self._y + self._h)
        if name == "topleft":
            return (self._x, self._y)
        if name == "bottomright":
            return (self._x + self._w, self._y + self._h)
        if name == "centerx":
            return (self._x + self._w / 2.)
        if name == "centery":
            return (self._y + self._h / 2.)
        if name == "center":
            return (self._x + self._w / 2., self._y + self._h / 2.)
        if name == "midleft":
            return (self._x, self._y + self._h / 2.)
        if name == "midright":
            return (self._x + self._w, self._y + self._h / 2.)
        if name == "midtop":
            return (self._x + self._w / 2., self._y)
        if name == "midbottom":
            return (self._x + self._w / 2., self._y + self._h)
        if name == "size":
            return (self._w, self._h)
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
        return Rect(self._x, self._y, self._w, self._h)
        
    def move(self, x, y):
        return Rect(x, y, self._w, self._h)
        
    def move_ip(self, x, y):
        self._x, self._y = x,y
        
    def inflate(self, x, y):
        c = self.center
        n = self.copy()
        n.size = (self._w + x, self._h + y)
        n.center = c
        return n
        
    def inflate_ip(self, x, y):
        c = self.center
        self.size = (self._w + x, self._h + y)
        self.center = c
        
    def clip(self, B):
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
        elif ((B._x + B._w) < A._x) and ((B._x + B._w) <= A._x + A._w):
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
        if self.clip(r).size == r.size:
            return True
        return False
        
    def collide_rect(self, r):
        # Probably write a better optimized version of this later
        if self.clip(r).size == (0,0) and r.clip(self).size == (0,0):
            return True
        return False
        
    def collide_point(self, point):
        # This could probably be optimized as well
        return point[0] > self.left and point[0] < self.right and \
            point[1] > self.top and point[1] < self.bottom
        
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