import math

class Vec2D(object):
    __slots__ = ['x', 'y']
    
    def __init__(self, *args):
        """
        Accepts either x and y as a tuple, or two arguments, x and y.
        """
        if len(args) == 1:
            self.x, self.y = args[0]
        elif len(args) == 2:
            self.x, self.y = args[0], args[1]
        else:
            raise ValueError("Invalid Vec2D arguments")
            
    def __len__(self):
        return 2
        
    def __getitem__(self, key):
        if key == 0:
            return self.x
        if key == 1:
            return self.y
        raise IndexError("Invalid subscript %s" % (str(key)))
        
    def __repr__(self):
        return 'Vec2D(%s, %s)' % (str(self.x), str(self.y))
        
    def __eq__(self, o):
        try:
            return self.x == o[0] and self.y == o[1]
        except (IndexError, TypeError):
            return False
    
    def __neq__(self, o):
        try:
            return self.x != o[0] or self.y != o[1]
        except (IndexError, TypeError):
            return True
    
    def __add__(self, o):
        try:
            return Vec2D(self.x + o[0], self.y + o[1])
        except (IndexError, TypeError):
            return NotImplemented
    
    __radd__ = __add__
    
    def __sub__(self, o):
        try:
            return Vec2D(self.x - o[0], self.y - o[1])
        except (IndexError, TypeError):
            return NotImplemented
            
    __isub__ = __sub__

    def __rsub__(self, o):
        try:
            return Vec2D(o[0] - self.x, o[1] - self.y)
        except (IndexError, TypeError):
            return NotImplemented
            
    def __mul__(self, o):
        try:
            return Vec2D(self.x * o[0], self.y * o[0])
        except (IndexError, TypeError):
            pass
        
        if isinstance(o, (int, long, float)):
            return Vec2D(self.x * o, self.y * o)
            
        return NotImplemented
        
    __rmul__ = __mul__
    __imul__ = __mul__
            
    def get_length(self):
        return math.sqrt(self.x * self.x + self.y * self.y)
            
    def rotated(self, angle, center = (0, 0)):
        """
        Rotates by *angle* radians about the optional center
        """
        p = self - center
        c = math.cos(angle)
        s = math.sin(angle)
        x = p.x*c - p.y*s
        y = p.x*s + p.y*c
        return Vec2D(x, y) + center
        
    def normalized(self):
        """
        Returns this vector normalized to length 1.
        """
        l = self.get_length()
        if self.get_length() == 0:
            return None
        return Vec2D(self.x/l, self.y/l)
        
    def distance(self, other):
        """
        Returns the distance from this point to the other point.
        """
        return (other - self).get_length()
